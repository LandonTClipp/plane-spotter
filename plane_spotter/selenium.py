import pathlib
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import structlog
from structlog import get_logger

logger: structlog.stdlib.BoundLogger = get_logger(__name__)


def adsb_exchange_screenshot(icao_hex: str, screenshot_path: pathlib.Path) -> None:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(f"https://globe.adsbexchange.com/?icao={icao_hex.lower()}")
        driver.set_window_size(1000, 1000)
        driver.save_screenshot(screenshot_path)
    finally:
        driver.quit()
