import logging
import urllib.parse
from datetime import datetime

from src.browser import Browser

from .activities import Activities


class DailySet:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.webdriver = browser.webdriver
        self.activities = Activities(browser)

    def completeDailySet(self):
        # Function to complete the Daily Set
        logging.info("[DAILY SET] " + "Trying to complete the Daily Set...")
        self.browser.utils.goHome()
        data = self.browser.utils.getDashboardData()["dailySetPromotions"]
        todayDate = datetime.now().strftime("%m/%d/%Y")
        for activity in data.get(todayDate, []):
            try:
                logging.info(
                    f"[DAILY SET] Processing activity: {activity.get('title', 'unknown')}"
                )
                logging.info(
                    f"[DAILY SET] Activity complete status: {activity.get('complete', 'unknown')}"
                )
                logging.info(
                    f"[DAILY SET] Activity promotion type: {activity.get('promotionType', 'unknown')}"
                )
                logging.info(
                    f"[DAILY SET] Activity point progress: {activity.get('pointProgress', 'unknown')}/{activity.get('pointProgressMax', 'unknown')}"
                )

                if activity["complete"] is True:
                    logging.info(
                        "[DAILY SET] Activity already completed, skipping: %s",
                        activity.get("title", "unknown"),
                    )
                    continue

                if activity["complete"] is False:
                    cardId = int(activity["offerId"][-1:])
                    # Open the Daily Set activity
                    self.activities.openDailySetActivity(cardId)
                    if activity["promotionType"] == "urlreward":
                        logging.info(f"[DAILY SET] Completing search of card {cardId}")
                        # Complete search for URL reward
                        self.activities.completeSearch()
                    if activity["promotionType"] == "quiz":
                        logging.info(
                            f"[DAILY SET] pointProgress / pointProgressMax: {activity['pointProgress']} / {activity['pointProgressMax']}"
                        )
                        if (
                            activity["pointProgressMax"] == 50
                            and activity["pointProgress"] == 0
                        ):
                            logging.info(
                                "[DAILY SET] "
                                + f"Completing This or That of card {cardId}"
                            )
                            # Complete This or That for a specific point progress max
                            self.activities.completeThisOrThat()
                        elif (
                            activity["pointProgressMax"] in [40, 30]
                        ):
                            logging.info(
                                f"[DAILY SET] Completing 30-40 pt quiz of card {cardId}"
                            )
                            # Complete quiz for specific point progress max
                            self.activities.completeQuiz()
                        elif (
                            activity["pointProgressMax"] == 10
                            and activity["pointProgress"] == 0
                        ):
                            logging.info(
                                f"[DAILY SET] Completing 10 pt quiz of card {cardId}"
                            )
                            # Extract and parse search URL for additional checks
                            searchUrl = urllib.parse.unquote(
                                urllib.parse.parse_qs(
                                    urllib.parse.urlparse(
                                        activity["destinationUrl"]
                                    ).query
                                )["ru"][0]
                            )
                            searchUrlQueries = urllib.parse.parse_qs(
                                urllib.parse.urlparse(searchUrl).query
                            )
                            filters = {}
                            for filterEl in searchUrlQueries["filters"][0].split(" "):
                                filterEl = filterEl.split(":", 1)
                                filters[filterEl[0]] = filterEl[1]
                            if "PollScenarioId" in filters:
                                logging.info(
                                    f"[DAILY SET] Completing poll of card {cardId}"
                                )
                                # Complete survey for a specific scenario
                                self.activities.completeSurvey()
                            else:
                                logging.info(
                                    f"[DAILY SET] Completing 10 pt quiz of card {cardId}"
                                )
                                try:
                                    # Try completing ABC activity
                                    self.activities.completeABC()
                                except Exception:  # pylint: disable=broad-except
                                    # Default to completing quiz
                                    self.activities.completeQuiz()
            except Exception:  # pylint: disable=broad-except
                # Reset tabs in case of an exception
                logging.exception(
                    "[DAILY SET] An error occurred while completing activity '%s'. Skipping to next.",
                    activity.get("title", "Unknown"),
                )
                self.browser.utils.resetTabs()
        logging.info("[DAILY SET] Completed the Daily Set successfully !")
