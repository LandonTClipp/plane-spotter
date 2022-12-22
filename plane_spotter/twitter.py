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
        dry_run: bool = True,
        log=logger,
    ):
        self._email = email
        self._password = password
        self._log = log.bind(class_name="TwitterSelenium")
        self._phone_number = phone_number
        self._username = username
        self._sleep_interval = sleep_interval
        self._dry_run = dry_run

    def __enter__(self):
        if self._dry_run:
            self._log.info("dry run of __enter__ method")
            return

        self._log.info("starting chromedriver")
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")
        options.add_argument("--incognito")
        self.webdriver = webdriver.Chrome(options=options)
        self._log.info("chrome driver started")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._dry_run:
            self._log.info("dry run of __exit__ method")
            return
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

    def login(self, log: structlog.stdlib.BoundLogger = logger):
        if self._dry_run:
            log.info("dry run of login method")
            return
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

        log.info("submitting password")
        password = self._wait_until_clickable(
            By.XPATH,
            "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input",
        )
        password.send_keys(self._password)
        password.send_keys(Keys.RETURN)

        log.info("login successful")

    def send(self, message: str, log=logger):
        """
        Submits a tweet. Chrome driver must be instantiated and login flow must be complete.
        """
        if self._dry_run:
            log.info("dry run of send method")
            log.info("would have sent message:")
            log.info(message)
            return

        log.info("Writing text")
        text_field_box = self._wait_until_clickable(By.CLASS_NAME, "DraftEditor-root")
        text_field_box.click()

        text_field = self._wait_until_clickable(
            By.CLASS_NAME, "public-DraftEditorPlaceholder-root"
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
