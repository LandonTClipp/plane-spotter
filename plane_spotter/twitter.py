import pathlib
import time

import selenium
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import structlog
from structlog import get_logger

from plane_spotter.notification import NotificationBackend

logger: structlog.stdlib.BoundLogger = get_logger(__name__)


class TwitterSelenium(NotificationBackend):
    def __init__(
        self,
        email: str,
        password: str,
        phone_number: str | None = None,
        username: str | None = None,
        sleep_interval: int = 5,
        log=logger,
    ):
        self._email = email
        self._password = password
        self._log = log
        self._phone_number = phone_number
        self._username = username
        self._sleep_interval = sleep_interval

    def __enter__(self):
        self._log.info("starting chromedriver")
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")
        options.add_argument("--incognito")
        self.webdriver = webdriver.Chrome(options=options)
        self._log.info("chrome driver started")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.webdriver.quit()
        self.webdriver = None

    def _sleep(self, log=logger):
        log.info("sleeping...")
        time.sleep(self._sleep_interval)

    def _wait(self) -> WebDriverWait:
        return WebDriverWait(self.webdriver, self._sleep_interval)

    def _wait_until_clickable(self, by: By, value: str):
        return self._wait().until(
            expected_conditions.element_to_be_clickable((by, value))
        )

    def unusual_activity_challenge(self, log=logger):
        """
        Twitter sometimes says:

            There was unusual login activity on your account.
            To help keep your account safe, please enter your phone number
            or username to verify it's you.

        """
        log.info("checking for unusual activity challenge prompt")
        try:
            phone_or_username_field = self._wait_until_clickable(
                By.XPATH,
                "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input",
            )
            log.info("unusual activity challenge exists")
            phone_or_username_field.send_keys(
                self._username if self._username is not None else self._phone_number
            )
            phone_or_username_field.send_keys(Keys.RETURN)
        except selenium.common.exceptions.NoSuchElementException:
            log.info("unusual activity challenge not present")
            return
        except selenium.common.exceptions.TimeoutException:
            log.info("unusual activity challenge timed out")
            return

    def login(self, log: structlog.stdlib.BoundLogger = logger):
        log.info("going to login page")
        self.webdriver.get("https://twitter.com/login")

        email = self._wait_until_clickable(
            by=By.XPATH,
            value="/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input",
        )
        log.info("sending email to twitter")
        email.send_keys(self._email)
        email.send_keys(Keys.RETURN)

        self.unusual_activity_challenge(log=log)

        password_xpath_1 = "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input"
        password_xpath_2 = "/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input"

        log.info("getting password input")

        password = self._get_password([password_xpath_1, password_xpath_2])
        if password is None:
            raise RuntimeError("Failed to get password element, check xpaths")

        log.info("submitting password")
        password.send_keys(self._password)
        password.send_keys(Keys.RETURN)

        log.info("login successful")

    def send(self, message: str, log=logger):
        """
        Submits a tweet. Chrome driver must be instantiated and login flow must be complete.
        """
        log.info("Writing text")
        text_field_box = WebDriverWait(self.webdriver, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.CLASS_NAME, "DraftEditor-root")
            )
        )
        text_field_box.click()

        text_field = self._wait().until(
            expected_conditions.element_to_be_clickable(
                (By.CLASS_NAME, "public-DraftEditorPlaceholder-root")
            )
        )

        ActionChains(self.webdriver).move_to_element(text_field).send_keys(
            message
        ).perform()

        log.info("clicking Tweet button")
        tweet_button = self._wait().until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "div[data-testid='tweetButtonInline']",
                )
            )
        )
        tweet_button.click()

        log.info("tweet successful")
        self._sleep()

    def _get_password(self, xpaths: list):
        for path in xpaths:
            try:
                return self._get_password_element(path)
            except selenium.common.exceptions.TimeoutException:
                continue
            except selenium.common.exceptions.NoSuchElementException:
                continue

        return None

    def _get_password_element(self, xpath: str):
        return self._wait_until_clickable(By.XPATH, xpath)
