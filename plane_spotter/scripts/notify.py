from dataclasses import dataclass, field
import json
from typing import Any

import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import MISSING, OmegaConf
from structlog import get_logger

from plane_spotter.adsb import ADSB, ADSBExchange
from plane_spotter.geolocator import Geolocator
from plane_spotter.notification import NotificationBackend, TwitterClient
from plane_spotter.package import airport_code_path

@dataclass
class ADSBExchangeConfig:
    api_key: str = MISSING
    api_hostname: str = MISSING
    driver: str = "adsbexchange"

@dataclass
class Twitter:
    key_id: str = MISSING
    key_secret: str = MISSING
    driver: str = "twitter"


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
    


defaults = [
    {"notification_backend": "twitter"},
    {"adsb_backend": "adsbexchange"},    
]

cs = ConfigStore.instance()
cs.store(group="adsb_backend", name="adsbexchange_schema", node=ADSBExchangeConfig)
cs.store(group="notification_backend", name="twitter_schema", node=Twitter)
cs.store(name="config_schema", node=Config)
cs.store(name="airplane_schema", node=Airplane)


logger = get_logger(__name__)


@hydra.main(version_base=None, config_path="config", config_name="notify")
def notify(cfg: Config) -> None:
    print(OmegaConf.to_yaml(cfg))
    missing_keys = OmegaConf.missing_keys(cfg)
    if missing_keys:
        raise RuntimeError(f"Got missing keys in config:\n{missing_keys}")

    log = logger.bind(
        adsb_backend=cfg.adsb_backend.driver,
        notification_backend=cfg.notification_backend.driver,
    )
    log.info("starting")

    adsb_backend: ADSB
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
    if cfg.notification_backend == "twitter":
        notification_backend = TwitterClient()

    response = adsb_backend.aircraft_last_position_by_hex_id(
        hex_id=cfg.airplane["icao_hex_id"]
    ).json()
    lat = response["lat"]
    lon = response["lon"]
    log.info(f"Plane last known location", lat=lat, lon=lon)

    nearest_airport = geolocator.lookup_airport(
        coordinates=(lat, lon), max_distance=cfg.search_radius
    )
    if nearest_airport is None:
        log.info("not near any known airport")
        return

    log.info("Nearest airport info:")
    log.info("\n" + json.dumps(nearest_airport, indent=4) + "\n")


if __name__ == "__main__":
    notify()
