import contextlib
import logging
import time
import urllib.parse

from selenium.webdriver.common.by import By

from src.browser import Browser

logger = logging.getLogger(__name__)


class Login:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.webdriver = browser.webdriver
        self.utils = browser.utils

    def login(self):
        logger.info("Logging-in...")
        self.webdriver.get(
            "https://rewards.bing.com/Signin/"
        )  # changed site to allow bypassing when M$ blocks access to login.live.com randomly

        retry = 0
        alreadyLoggedIn = False
        while retry < 3:
            try:
                self.utils.waitUntilVisible(
                    By.CSS_SELECTOR, 'html[data-role-name="RewardsPortal"]', 5
                )
                alreadyLoggedIn = True
                logger.info("Already Logged-in!")
                break
            except Exception:  # pylint: disable=broad-except
                try:
                    self.utils.waitUntilVisible(By.ID, "usernameEntry", 10)
                    logger.info("Found usernameEntry!")
                    break
                except Exception:  # pylint: disable=broad-except
                    if self.utils.tryDismissAllMessages():
                        logger.info("All Messages Dismissed!")
                        retry += 1
                        continue

        if retry == 3:
            return "Verify"

        if not alreadyLoggedIn:
            if isLocked := self.executeLogin():
                return "Locked"
        self.utils.tryDismissCookieBanner()

        logger.info("Logged-in !")

        self.utils.goHome()
        points = self.utils.getAccountPoints()

        logger.info("Ensuring you are logged into Bing...")
        self.checkBingLogin()
        logger.info("Logged-in successfully !")
        return points

    def executeLogin(self):
        email_field = self.utils.waitUntilVisible(By.ID, "usernameEntry", 10)
        logger.info("Entering email...")
        email_field.click()

        while True:
            email_field.send_keys(self.browser.username)
            time.sleep(3)
            if email_field.get_attribute("value") == self.browser.username:
                self.utils.waitUntilClickable(
                    By.CSS_SELECTOR, "[data-testid='primaryButton']"
                ).click()
                break

            email_field.clear()
            time.sleep(3)

        try:
            self.enterPassword(self.browser.password)
        except Exception:  # pylint: disable=broad-except
            logger.error("2FA Code required !")
            with contextlib.suppress(Exception):
                code = self.webdriver.find_element(
                    By.ID, "idRemoteNGC_DisplaySign"
                ).get_attribute("innerHTML")
                logger.error(f"2FA code: {code}")
            logger.info("Press enter when confirmed on your device...")
            input()

        try:
            self.utils.waitUntilVisible(By.NAME, "iProofEmail", 0.5)
            logger.error("Needs you to prove email")
            logger.info("Press enter when confirmed...")
            input()
        except Exception:
            logger.info("No email proof, all clear")

        # Wait until the user is redirected to the rewards.bing.com page
        retry = 3
        while not (
            urllib.parse.urlparse(self.webdriver.current_url).path == "/"
            and urllib.parse.urlparse(self.webdriver.current_url).hostname
            == "rewards.bing.com"
        ):
            retry -= 1
            if retry <= 0:
                logger.error("Login failed!")
                return True
            self.utils.tryDismissAllMessages()
            time.sleep(1)

        self.utils.waitUntilVisible(
            By.CSS_SELECTOR, 'html[data-role-name="RewardsPortal"]', 10
        )

    def enterPassword(self, password):
        self.utils.waitUntilClickable(By.NAME, "passwd", 10)

        logger.info("Writing password...")

        password_field = self.webdriver.find_element(By.NAME, "passwd")

        while True:
            password_field.send_keys(password)
            time.sleep(3)
            if password_field.get_attribute("value") == password:
                self.utils.waitUntilClickable(
                    By.CSS_SELECTOR, "[data-testid='primaryButton']"
                ).click()
                break

            password_field.clear()
            time.sleep(3)
        time.sleep(3)

    def checkBingLogin(self, timeout_sec=60):
        self.webdriver.get(
            "https://www.bing.com/fd/auth/signin?action=interactive&provider=windows_live_id&return_url=https%3A%2F%2Fwww.bing.com%2F"
        )

        timeout = time.time() + timeout_sec
        while time.time() < timeout:
            currentUrl = urllib.parse.urlparse(self.webdriver.current_url)
            if currentUrl.hostname == "www.bing.com" and currentUrl.path == "/":
                time.sleep(3)
                self.utils.tryDismissBingCookieBanner()
                with contextlib.suppress(Exception):
                    if self.utils.checkBingLogin():
                        return
            time.sleep(1)
        raise TimeoutError("Timed out waiting for Bing login to complete.")
