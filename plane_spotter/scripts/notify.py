from dataclasses import asdict, dataclass, field
import datetime
import json
import os
from textwrap import dedent
import time
from typing import Any

import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import MISSING, OmegaConf
from structlog import get_logger

from plane_spotter.adsb import ADSBExchange
from plane_spotter.geolocator import Geolocator
from plane_spotter.notification import NotificationBackend
from plane_spotter.package import airport_code_path
from plane_spotter.twitter import TwitterSelenium as _TwitterSelenium


@dataclass
class ADSBExchangeConfig:
    api_key: str = MISSING
    api_hostname: str = MISSING
    driver: str = "adsbexchange"


@dataclass
class TwitterBase:
    key_id: str = MISSING
    key_secret: str = MISSING
    driver: str = MISSING


@dataclass
class TwitterAPI(TwitterBase):
    key_id: str = MISSING
    key_secret: str = MISSING
    driver: str = "twitter_api"


@dataclass
class TwitterSelenium(TwitterBase):
    driver: str = "twitter_selenium"
    key_id: str = MISSING
    username: str = MISSING
    phone_number: str | None = None
    key_secret: str = MISSING


@dataclass
class Airplane:
    registration: str | None = MISSING
    icao_hex_id: str | None = MISSING


@dataclass
class Config:
    defaults: list[Any] = field(default_factory=lambda: defaults)
    search_radius: int = 1000
    adsb_backend: Any = MISSING
    airplane: Airplane = MISSING
    notification_backend: Any = MISSING


defaults: list[Any] = []

cs = ConfigStore.instance()
cs.store(group="adsb_backend", name="adsbexchange_schema", node=ADSBExchangeConfig)
cs.store(group="notification_backend", name="twitter_api_schema", node=TwitterAPI)
cs.store(
    group="notification_backend", name="twitter_selenium_schema", node=TwitterSelenium
)
cs.store(name="config_schema", node=Config)
cs.store(name="airplane_schema", node=Airplane)


logger = get_logger(__name__)


def _main_loop(
    adsb_backend: ADSBExchange,
    geolocator: Geolocator,
    notification_backend: NotificationBackend,
    cfg: Config,
    loop_interval: int = 120,
    num_loops: int = -1,
    log=logger,
):
    """
    This is the main loop for discovering ADS-B data and notifying the backend.

    num_loops if set to a non-positive number will loop only that number of times.
    If it's set to zero or a negative number, it will loop infinitely.
    """
    last_known_ident = None
    cur_loop = 0

    while (cur_loop < num_loops) or num_loops <= 0:
        response = adsb_backend.aircraft_last_position_by_hex_id(
            hex_id=cfg.airplane.icao_hex_id
        ).json()
        lat = response["lat"]
        lon = response["lon"]
        log.info(f"Plane last known location", lat=lat, lon=lon)

        nearest_airport = geolocator.lookup_airport(
            coordinates=(lat, lon), max_distance=cfg.search_radius
        )
        if nearest_airport is None:
            log.info("not near any known airport")
            continue

        log.info("Nearest airport info:")
        log.info("\n" + json.dumps(asdict(nearest_airport), indent=4) + "\n")

        ident = nearest_airport.ident
        name = nearest_airport.name
        if ident != last_known_ident:
            log.info("airplane spotted near new airport")
            now = datetime.datetime.now(datetime.timezone.utc)
            message = dedent(
                f"""\
            Airplane spotted near {name} at {now}
            
            Ident: {nearest_airport.ident}
            Country: {nearest_airport.iso_country}
            ISO Region: {nearest_airport.iso_region}
            Municipality: {nearest_airport.municipality}
            Distance To Airport (Km): {nearest_airport.distance_to_coordinates}
            """
            )
            notification_backend.send(message=message, log=log)
            last_known_ident = ident
        else:
            log.info("airplane hasn't moved")

        time.sleep(loop_interval)
        if num_loops > 0:
            cur_loop += 1


@hydra.main(
    version_base=None,
    config_path=os.environ.get("PLANE_NOTIFY_CONFIG_PATH", "config"),
    config_name="notify",
)
def notify(cfg: Config) -> None:
    missing_keys = OmegaConf.missing_keys(cfg)
    if missing_keys:
        raise RuntimeError(f"Got missing keys in config:\n{missing_keys}")

    log = logger.bind(
        adsb_backend=cfg.adsb_backend.driver,
        notification_backend=cfg.notification_backend.driver,
    )
    log.info("starting")

    notification_backend: NotificationBackend
    geolocator = Geolocator(airport_code_file=airport_code_path())

    log.info("instantiating ADS-B backend")
    if cfg.adsb_backend["driver"] == "adsbexchange":
        adsb_backend = ADSBExchange(
            key=cfg.adsb_backend["api_key"], hostname=cfg.adsb_backend["api_hostname"]
        )
    else:
        raise ValueError(f"backend not known: {cfg.adsb_backend['driver']}")

    log.info("instantiating notification backend")

    if cfg.notification_backend.driver == "twitter_selenium":
        twitter_selenium = _TwitterSelenium(
            email=cfg.notification_backend.key_id,
            password=cfg.notification_backend.key_secret,
            phone_number=cfg.notification_backend.phone_number,
            username=cfg.notification_backend.username,
        )
        notification_backend = twitter_selenium
    else:
        raise ValueError(f"backend not known: {cfg.notification_backend.driver}")

    with twitter_selenium:
        twitter_selenium.login()
        _main_loop(
            adsb_backend=adsb_backend,
            geolocator=geolocator,
            notification_backend=notification_backend,
            cfg=cfg,
        )


if __name__ == "__main__":
    notify()
