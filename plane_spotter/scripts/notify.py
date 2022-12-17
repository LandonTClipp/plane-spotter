from dataclasses import dataclass

import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import MISSING, OmegaConf

@dataclass
class Config:
    adsb_exchange_key: str
    adsb_exchange_hostname: str = "adsbexchange-com1.p.rapidapi.com"

cs = ConfigStore.instance()
cs.store(name="notify_schema", node=Config)


@hydra.main(version_base=None, config_path=".", config_name="notify")
def notify(cfg: Config) -> None:
    print(OmegaConf.to_yaml(cfg))


if __name__ == "__main__":
    notify()