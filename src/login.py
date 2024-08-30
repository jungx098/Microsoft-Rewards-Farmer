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
        alreadyLoggedIn = False
        while True:
            try:
                self.utils.waitUntilVisible(
                    By.CSS_SELECTOR, 'html[data-role-name="RewardsPortal"]', 1
                )
                alreadyLoggedIn = True
                logger.info("Already Logged-in!")
                break
            except Exception:  # pylint: disable=broad-except
                try:
                    self.utils.waitUntilVisible(By.ID, "i0116", 10)
                    logger.info("Found i0116!")
                    break
                except Exception:  # pylint: disable=broad-except
                    if self.utils.tryDismissAllMessages():
                        logger.info("All Messages Dismissed!")
                        continue

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
        self.utils.waitUntilVisible(By.ID, "i0116", 10)
        logger.info("Entering email...")
        self.utils.waitUntilClickable(By.NAME, "loginfmt", 10)
        email_field = self.webdriver.find_element(By.NAME, "loginfmt")

        while True:
            email_field.send_keys(self.browser.username)
            time.sleep(3)
            if email_field.get_attribute("value") == self.browser.username:
                self.webdriver.find_element(By.ID, "idSIButton9").click()
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
            self.utils.waitUntilVisible(
                By.NAME, 'iProofEmail', 0.5
            )
            logger.error('Needs you to prove email')
            logger.info('Press enter when confirmed...')
            input()
        except Exception:
            logger.info('No email proof, all clear')

        while not (
            urllib.parse.urlparse(self.webdriver.current_url).path == "/"
            and urllib.parse.urlparse(self.webdriver.current_url).hostname
            == "account.microsoft.com"
        ):
            if urllib.parse.urlparse(self.webdriver.current_url).hostname == "rewards.bing.com":
                self.webdriver.get("https://account.microsoft.com")

            if "Abuse" in str(self.webdriver.current_url):
                logger.error(f"{self.browser.username} is locked")
                return True
            self.utils.tryDismissAllMessages()
            time.sleep(1)

        self.utils.waitUntilVisible(
            By.CSS_SELECTOR, 'html[data-role-name="MeePortal"]', 10
        )

    def enterPassword(self, password):
        self.utils.waitUntilClickable(By.NAME, "passwd", 10)
        self.utils.waitUntilClickable(By.ID, "idSIButton9", 10)

        logger.info("Writing password...")

        password_field = self.webdriver.find_element(By.NAME, "passwd")

        while True:
            password_field.send_keys(password)
            time.sleep(3)
            if password_field.get_attribute("value") == password:
                self.webdriver.find_element(By.ID, "idSIButton9").click()
                break

            password_field.clear()
            time.sleep(3)
        time.sleep(3)

    def checkBingLogin(self):
        self.webdriver.get(
            "https://www.bing.com/fd/auth/signin?action=interactive&provider=windows_live_id&return_url=https%3A%2F%2Fwww.bing.com%2F"
        )
        while True:
            currentUrl = urllib.parse.urlparse(self.webdriver.current_url)
            if currentUrl.hostname == "www.bing.com" and currentUrl.path == "/":
                time.sleep(3)
                self.utils.tryDismissBingCookieBanner()
                with contextlib.suppress(Exception):
                    if self.utils.checkBingLogin():
                        return
            time.sleep(1)
