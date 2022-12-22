from pathlib import Path
import pytest
import structlog
from textwrap import dedent
from unittest.mock import Mock

from plane_spotter.adsb import ADSBExchange
from plane_spotter.notification import NotificationBackend


logger = structlog.get_logger(__name__)


class NotificationStub(NotificationBackend):
    def __init__(self):
        pass

    def send(self, message: str, log: structlog.stdlib.BoundLogger = logger):
        pass


DEFAULT_AIRPORT_CSV = dedent(
    """\
        ident,type,name,elevation_ft,continent,iso_country,iso_region,municipality,gps_code,iata_code,local_code,coordinates
        00AA,small_airport,Aero B Ranch Airport,3435,NA,US,US-KS,Leoti,00AA,,00AA,"38.704022, -101.473911"
        00AK,small_airport,Lowell Field,450,NA,US,US-AK,Anchor Point,00AK,,00AK,"59.94919968, -151.695999146"
        """
)


@pytest.fixture
def adsb_stub():
    return Mock(spec=ADSBExchange(key="foo", hostname="bar"))


@pytest.fixture
def notification_stub():
    return Mock(spec=NotificationStub())


@pytest.fixture
def airport_csv_path(tmp_path: Path) -> Path:
    return tmp_path.joinpath("airport.csv")


def write_airport_csv(
    path: Path,
    text: str = DEFAULT_AIRPORT_CSV,
) -> None:
    path.write_text(text)
