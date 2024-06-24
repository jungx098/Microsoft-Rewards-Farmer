import json
import logging
import random
import time
from datetime import date, timedelta

import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.browser import Browser
from src.utils import Utils


class Searches:
    searchIdx = 0
    searchMax = 200
    searchTerms: list[str] = []

    def __init__(self, browser: Browser):
        self.browser = browser
        self.webdriver = browser.webdriver

    def getGoogleTrends(self, wordsCount: int) -> list:
        # Function to retrieve Google Trends search terms
        Searches.searchMax = max(Searches.searchMax, wordsCount * 2)

        if len(Searches.searchTerms) < Searches.searchIdx + wordsCount:
            Searches.searchIdx = 0
            Searches.searchTerms = []

        i = 0
        while len(Searches.searchTerms) < Searches.searchMax:
            i += 1
            # Fetching daily trends from Google Trends API
            r = requests.get(
                f'https://trends.google.com/trends/api/dailytrends?hl={self.browser.localeLang}&ed={(date.today() - timedelta(days=i)).strftime("%Y%m%d")}&geo={self.browser.localeGeo}&ns=15'
            )
            trends = json.loads(r.text[6:])
            for topic in trends["default"]["trendingSearchesDays"][0][
                "trendingSearches"
            ]:
                Searches.searchTerms.append(topic["title"]["query"].lower())
                Searches.searchTerms.extend(
                    relatedTopic["query"].lower()
                    for relatedTopic in topic["relatedQueries"]
                )
            Searches.searchTerms = list(set(Searches.searchTerms))

        start = Searches.searchIdx
        end = min(len(Searches.searchTerms), Searches.searchIdx + wordsCount)
        Searches.searchIdx = end

        return Searches.searchTerms[start:end]

    def getRelatedTerms(self, word: str) -> list:
        # Function to retrieve related terms from Bing API
        try:
            r = requests.get(
                f"https://api.bing.com/osjson.aspx?query={word}",
                headers={"User-agent": self.browser.userAgent},
                timeout=60,
            )
            result = set(r.json()[1])
            result.discard(word)
            return list(result)
        except Exception:  # pylint: disable=broad-except
            return []

    def bingSearches(self, numberOfSearches: int, pointsCounter: int = 0):
        # Function to perform Bing searches
        logging.info(
            "[BING] %s Search Start - Reward Count: %d Points: %d",
            self.browser.browserType.capitalize(),
            numberOfSearches,
            pointsCounter,
        )

        # 3 more search counts to compensate potential reward failures.
        search_terms = self.getGoogleTrends(numberOfSearches + 3)
        self.webdriver.get("https://bing.com")

        i = 0
        reward_cnt = 0
        while reward_cnt < numberOfSearches and i < len(search_terms):
            word = search_terms[i]
            i = i + 1
            logging.info(
                "[BING] Iteration: %d/%d Progress: %d/%d Word: %s",
                i,
                len(search_terms),
                reward_cnt,
                numberOfSearches,
                word,
            )
            points = self.bingSearch(word)
            if points <= pointsCounter:
                relatedTerms = self.getRelatedTerms(word)
                retryMax = min(3, len(relatedTerms))
                for retry in range(retryMax):
                    logging.warning(
                        "[BING] Possible blockage. Refreshing the page.",
                    )
                    self.webdriver.refresh()

                    term = relatedTerms[retry]
                    logging.info(
                        "[BING] Retry: %d/%d Word: %s (points: %d)",
                        retry + 1,
                        retryMax,
                        term,
                        points,
                    )
                    points = self.bingSearch(term)
                    if not points <= pointsCounter:
                        break
            if points > pointsCounter:
                pointsCounter = points
                reward_cnt += 1
            elif points == pointsCounter:
                logging.warning("[BING] No point gained (points: %d).", points)
            else:
                logging.warning(
                    "[BING] Invalid point returned (points: %d).",
                    points,
                )
                break

        logging.info(
            "[BING] %s Search Done - Iteration: %d/%d Progress: %d/%d Points: %d",
            self.browser.browserType.capitalize(),
            i,
            len(search_terms),
            reward_cnt,
            numberOfSearches,
            pointsCounter,
        )

        return pointsCounter

    def bingSearch(self, word: str):
        # Function to perform a single Bing search
        i = 0

        while True:
            try:
                self.browser.utils.waitUntilClickable(By.ID, "sb_form_q")
                searchbar = self.webdriver.find_element(By.ID, "sb_form_q")
                searchbar.clear()
                searchbar.send_keys(word)
                searchbar.submit()
                time.sleep(Utils.randomSeconds(100, 180))

                # Scroll down after the search (adjust the number of scrolls as needed)
                for _ in range(3):  # Scroll down 3 times
                    self.webdriver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    time.sleep(
                        Utils.randomSeconds(7, 10)
                    )  # Random wait between scrolls

                return self.browser.utils.getBingAccountPoints()
            except TimeoutException:
                if i == 5:
                    logging.info("[BING] " + "TIMED OUT GETTING NEW PROXY")
                    self.webdriver.proxy = self.browser.giveMeProxy()
                elif i == 10:
                    logging.error(
                        "[BING] "
                        + "Cancelling mobile searches due to too many retries."
                    )
                    return self.browser.utils.getBingAccountPoints()
                self.browser.utils.tryDismissAllMessages()
                logging.error("[BING] " + "Timeout, retrying in 5~ seconds...")
                time.sleep(Utils.randomSeconds(7, 15))
                i += 1
                continue
