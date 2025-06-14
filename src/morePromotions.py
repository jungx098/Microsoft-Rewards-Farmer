import logging

from selenium.webdriver.common.by import By

from src.browser import Browser

from .activities import Activities

logger = logging.getLogger(__name__)


class MorePromotions:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.activities = Activities(browser)

    def completeMorePromotions(self):
        # Function to complete More Promotions
        logging.info("[MORE PROMOS] " + "Trying to complete More Promotions...")
        self.browser.utils.goHome()

        # Get morePromotions data from the dashboard
        morePromotions = self.browser.utils.getDashboardData()["morePromotions"]

        for promotion in morePromotions:
            logger.info(
                'Promotion %d: "%s" %s (%s) DONE(%d) POINT(%d)',
                morePromotions.index(promotion) + 1,
                promotion["title"],
                promotion["description"],
                promotion["promotionType"],
                promotion["complete"],
                promotion["pointProgressMax"],
            )

        # Obtain elementSize
        cards = self.browser.webdriver.find_elements(By.XPATH, '//*[@id="more-activities"]/div/mee-card')
        num_cards = len(cards)
        logger.info("Total mee-card count: %d", num_cards)

        for i in range(1, num_cards + 1):
            try:
                element = self.browser.webdriver.find_element(
                    By.XPATH,
                    f'//*[@id="more-activities"]/div/mee-card[{i}]/div/card-content/mee-rewards-more-activities-card-item/div/a',
                )
                logger.info(
                    "Card %d: %s", i, element.accessible_name)

                # Sequtial search for the promotion for the current card
                promotion = None
                for promo in morePromotions:
                    if promo["title"] in element.accessible_name:
                        promotion = promo
                        logger.info("Promotion found: %s", promotion["title"])
                        break

                if promotion is None:
                    logger.warning(
                        "No promotion found for card %d with title: %s", i, element.accessible_name)
                    continue

            except Exception as e:
                logger.error("%s: No Element Found for mee-card[%d]", type(e).__name__, i)

        i = 0
        for promotion in morePromotions:
            try:
                i += 1
                logger.info(
                    '%d: "%s" %s (%s) DONE(%d) POINT(%d)',
                    i,
                    promotion["title"],
                    promotion["description"],
                    promotion["promotionType"],
                    promotion["complete"],
                    promotion["pointProgressMax"],
                )

                # Find corresponding cardId
                cardId = -1

                for j in range(1, num_cards + 1):
                    try:
                        # Try to find the element by cardId
                        element = self.browser.webdriver.find_element(
                            By.XPATH,
                            f'//*[@id="more-activities"]/div/mee-card[{j}]/div/card-content/mee-rewards-more-activities-card-item/div/a',
                        )
                        if promotion["title"] in element.accessible_name:
                            cardId = j
                            break
                    except Exception:
                        # If not found, continue to the next index
                        continue

                if cardId == -1:
                    logger.warning(
                        "Card ID not found for promotion: %s", promotion["title"]
                    )
                    continue

                # Log the found cardId
                logger.info("Card ID: %d", cardId)

                # Skip Windows search
                if promotion["title"] == "Windows search":
                    continue
                if promotion["title"] == "Bing app search":
                    continue

                if (
                    promotion["complete"] is False
                    and promotion["pointProgressMax"] != 0
                ):
                    # Open the activity for the promotion
                    self.activities.openMorePromotionsActivity(cardId)
                    if promotion["promotionType"] == "urlreward":
                        # Complete search for URL reward
                        link = ". " if promotion["title"][-1].isalnum() else " "
                        self.activities.completeSearch(
                            promotion["title"] + link + promotion["description"]
                        )
                    elif (
                        promotion["promotionType"] == "quiz"
                        and promotion["pointProgress"] == 0
                    ):
                        # Complete different types of quizzes based on point progress max
                        if promotion["pointProgressMax"] == 10:
                            self.activities.completeABC()
                        elif promotion["pointProgressMax"] in [30, 40]:
                            self.activities.completeQuiz()
                        elif promotion["pointProgressMax"] == 50:
                            self.activities.completeThisOrThat()
                    else:
                        # Default to completing search
                        link = ". " if promotion["title"][-1].isalnum() else " "
                        self.activities.completeSearch(
                            promotion["title"] + link + promotion["description"]
                        )
            except Exception:  # pylint: disable=broad-except
                # Reset tabs in case of an exception
                self.browser.utils.resetTabs()
        logging.info("[MORE PROMOS] Completed More Promotions successfully !")
