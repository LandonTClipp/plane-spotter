import datetime
import pytest
from unittest import mock

from freezegun import freeze_time
from plane_spotter.adsb import ADSBExchange
from plane_spotter.geolocator import Airport, Geolocator
from plane_spotter.notification import plane_landed_message, plane_stationed_at_message
from plane_spotter.scripts.notify import _main_loop, AirportDiscovery
from pytest_httpserver import HTTPServer

from tests.conftest import write_airport_csv

EXAMPLE_ADSB = {
    "hex": "a835af",
    "type": "adsb_icao",
    "flight": "N628TS  ",
    "r": "N628TS",
    "t": "GLF6",
    "dbFlags": 8,
    "alt_baro": "ground",
    "gs": 0,
    "true_heading": 171.56,
    "squawk": "1034",
    "emergency": "none",
    "category": "A3",
    "lat": 37.730289,
    "lon": -122.214091,
    "nic": 8,
    "rc": 186,
    "seen_pos": 60.179,
    "version": 2,
    "sil_type": "perhour",
    "mlat": [],
    "tisb": [],
    "messages": 9811372,
    "seen": 60,
    "rssi": -5.7,
    "ctime": 1671668713823,
}


@pytest.fixture
def geolocator(airport_csv_path) -> Geolocator:
    write_airport_csv(airport_csv_path)
    return Geolocator(airport_code_file=airport_csv_path)


@pytest.fixture
def adsb_exchange(httpserver: HTTPServer) -> ADSBExchange:
    return ADSBExchange(
        key="foo", hostname="localhost", port=httpserver.port, https=False
    )


def aero_b_ranch_airport() -> Airport:
    return Airport(ident="00AA", name="Aero B Ranch Airport", iso_region="US-KS")


def test_main_loop_not_near_any_known_airport(
    notification_stub, adsb_exchange, geolocator, httpserver: HTTPServer, log
):
    httpserver.expect_request("/v2/hex/BADC0DE/").respond_with_json(
        {
            "alt_baro": "ground",
            "lat": 37.730289,
            "lon": -122.214091,
        }
    )

    _main_loop(
        adsb_backend=adsb_exchange,
        geolocator=geolocator,
        notification_backend=notification_stub,
        search_radius=100,
        icao_hex_id="BADC0DE",
        loop_interval=0,
        num_loops=1,
    )
    assert {"event": "not near any known airport", "level": "info"} in log.events
    assert notification_stub.send.not_called()


@freeze_time("2022-01-01")
def test_main_loop_airplane_starts_at_airport(
    notification_stub,
    adsb_exchange: ADSBExchange,
    geolocator: Geolocator,
    httpserver: HTTPServer,
    log,
):
    now = datetime.datetime.now(datetime.timezone.utc)
    httpserver.expect_request("/v2/hex/BADC0DE/").respond_with_json(
        {
            "alt_baro": "ground",
            "lat": 38.704022,
            "lon": -101.473911,
        }
    ),

    _main_loop(
        adsb_backend=adsb_exchange,
        geolocator=geolocator,
        notification_backend=notification_stub,
        search_radius=100,
        icao_hex_id="BADC0DE",
        loop_interval=0,
        num_loops=1,
    )
    assert {
        "event": "discovered first airport aircraft has landed at",
        "level": "info",
    } in log.events
    message = plane_stationed_at_message(
        airport=AirportDiscovery(airport=aero_b_ranch_airport(), discovery_time=now)
    )
    notification_stub.send.assert_called_once_with(
        message=message,
        log=mock.ANY,
    )


@freeze_time("2022-01-01")
def test_main_loop_airplane_starts_in_air_then_lands(
    notification_stub, geolocator, httpserver: HTTPServer, log
):
    now = datetime.datetime.now(datetime.timezone.utc)
    adsb = ADSBExchange(
        key="foo", hostname="localhost", port=httpserver.port, https=False
    )

    httpserver.expect_ordered_request("/v2/hex/BADC0DE/").respond_with_json(
        {
            "alt_baro": 43000,
            "lat": 38.704022,
            "lon": -101.473911,
        }
    )
    httpserver.expect_ordered_request("/v2/hex/BADC0DE/").respond_with_json(
        {
            "alt_baro": "ground",
            "lat": 38.704022,
            "lon": -101.473911,
        }
    )

    _main_loop(
        adsb_backend=adsb,
        geolocator=geolocator,
        notification_backend=notification_stub,
        search_radius=100,
        icao_hex_id="BADC0DE",
        loop_interval=0,
        num_loops=2,
    )
    assert {
        "event": "aircraft is still in flight. Unknown last landed airport.",
        "level": "info",
    } in log.events
    assert {"event": "airplane landed at airport", "level": "info"} in log.events

    landed_message = plane_landed_message(
        source=AirportDiscovery(airport=Airport(), discovery_time=now, unknown=True),
        destination=AirportDiscovery(
            airport=aero_b_ranch_airport(),
            discovery_time=now,
        ),
        hashtags=["#elonjet"],
    )
    notification_stub.send.assert_called_once_with(message=landed_message, log=mock.ANY)
