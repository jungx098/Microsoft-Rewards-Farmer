import json
import logging
from pathlib import Path

from selenium.webdriver.common.by import By

from src.browser import Browser

from .activities import Activities

logger = logging.getLogger(__name__)


class ExploreOnBing:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.activities = Activities(browser)

    def completeExploreOnBing(self):
        # Function to complete More Promotions
        logging.info("[EXPLORE ON BING] " + "Trying to complete Explore on Bing...")
        self.browser.utils.goHome()

        # Get morePromotions data from the dashboard
        # Note: no explorerOnBing entry in the dictionary.
        dashboardData = self.browser.utils.getDashboardData()

        # Save dashboard data to a file
        dashboardDataFile = Path("dashboard_data.json")
        with open(dashboardDataFile, "w", encoding="utf-8") as f:
            json.dump(dashboardData, f, indent=4)
        logging.info("Dashboard data saved to %s", dashboardDataFile)

        # List all dictionary keys
        for key in dashboardData.keys():
            logger.info("Key: %s", key)

        # List all id
        cards = self.browser.webdriver.find_elements(
            By.XPATH, '//*[@id="more-activities"]/div/mee-card'
        )
        num_cards = len(cards)
        logger.info("Total mee-card count: %d", num_cards)

        # Dump cards to a file
        cardsFile = Path("cards.json")
        with open(cardsFile, "w", encoding="utf-8") as f:
            json.dump([card.get_attribute("id") for card in cards], f, indent=4)
        logging.info("Cards saved to %s", cardsFile)

        # Find all elements that have an 'id' attribute
        elements_with_id = self.browser.webdriver.find_elements(By.XPATH, "//*[@id]")

        # Extract and print their IDs
        ids = [elem.get_attribute("id") for elem in elements_with_id]
        print("Element IDs:", ids)

        # Dump ids to a file
        idsFile = Path("ids.json")
        with open(idsFile, "w", encoding="utf-8") as f:
            json.dump(ids, f, indent=4)
        logging.info("IDs saved to %s", idsFile)

        logging.info("[EXPLORE ON BING] Done!")
