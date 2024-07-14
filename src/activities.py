import logging
import random
import time
from typing import Optional

from selenium.webdriver.common.by import By

from src.browser import Browser
from src.utils import Utils

logger = logging.getLogger(__name__)


class Activities:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.webdriver = browser.webdriver

    def openDailySetActivity(self, cardId: int):
        # Open the Daily Set activity for the given cardId
        self.webdriver.find_element(
            By.XPATH,
            f'//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[{cardId}]/div/card-content/mee-rewards-daily-set-item-content/div/a',
        ).click()
        self.browser.utils.switchToNewTab(8)

    def openMorePromotionsActivity(self, cardId: int):
        # Open the More Promotions activity for the given cardId
        self.webdriver.find_element(
            By.XPATH,
            f'//*[@id="more-activities"]/div/mee-card[{cardId}]/div/card-content/mee-rewards-more-activities-card-item/div/a',
        ).click()
        self.browser.utils.switchToNewTab(8)

    def completeSearch(self, search_hint: Optional[str] = None):
        # Check search box element value. If this element was empty, Bing might
        # want to fill the box.
        search: Optional[str] = None
        try:
            search_box = self.webdriver.find_element(By.ID, "sb_form_q")
            search = search_box.get_attribute("value")
            logger.info("sb_form_q Value: %s", search)
        except Exception as e:
            logger.error("%s: No Element Found for sb_form_q", type(e).__name__)

        if search_hint and search == "":
            search_hint = search_hint.lower()

            if "convert your money" in search_hint:
                search_samples = [
                    "USD 100 to KRW",
                    "KRW 1000 to USD",
                    "USD 1000 to YEN",
                    "1000 USD to EURO?",
                ]

                search = random.choice(search_samples)
            elif "cook tonight" in search_hint:
                search_samples = [
                    "Pizza near me",
                    "Burrito near me",
                    "Bagel near me",
                    "Hawaiian Pizza Recipe",
                    "Juicy Lucy Recipe",
                ]

                search = random.choice(search_samples)
            elif "new recipe" in search_hint:
                search_samples = [
                    "Hawaiian Pizza Recipe",
                    "Juicy Lucy Recipe",
                ]

                search = random.choice(search_samples)
            else:
                logger.warning("Not Implemented Yet: %s", search_hint)

                search_samples = [
                    "USD 100 to KRW",
                    "KRW 1000 to USD",
                    "USD 1000 to YEN",
                    "1000 USD to EURO?",
                    "AUS to ICN flight",
                    "AUS to SFO flight",
                    "SFO to HND flight",
                    "Pizza near me",
                    "Burrito near me",
                    "Bagel near me",
                    "Hawaiian Pizza Recipe",
                    "Juicy Lucy Recipe",
                ]

                search = random.choice(search_samples)

            try:
                logger.info("Search: %s", search)
                element = self.browser.utils.waitUntilClickable(
                    By.ID, "sb_form_q", timeToWait=20
                )

                element.click()
                element.send_keys(search)

                time.sleep(random.randint(5, 10))
                element.submit()
            except Exception as e:
                logger.error("%s: Search Error", type(e).__name__)

        # Simulate completing a search activity
        time.sleep(Utils.randomSeconds(10, 15))

        self.browser.utils.closeCurrentTab()

    def completeSurvey(self):
        # Simulate completing a survey activity
        self.webdriver.find_element(By.ID, f"btoption{random.randint(0, 1)}").click()
        time.sleep(Utils.randomSeconds(10, 15))
        self.browser.utils.closeCurrentTab()

    def completeQuiz(self):
        # Simulate completing a quiz activity
        if not self.browser.utils.waitUntilQuizLoads():
            self.browser.utils.resetTabs()
            return
        self.webdriver.find_element(By.XPATH, '//*[@id="rqStartQuiz"]').click()
        self.browser.utils.waitUntilVisible(
            By.XPATH, '//*[@id="currentQuestionContainer"]/div/div[1]', 5
        )
        time.sleep(Utils.randomSeconds(10, 15))
        numberOfQuestions = self.webdriver.execute_script(
            "return _w.rewardsQuizRenderInfo.maxQuestions"
        )
        numberOfOptions = self.webdriver.execute_script(
            "return _w.rewardsQuizRenderInfo.numberOfOptions"
        )
        for question in range(numberOfQuestions):
            if numberOfOptions == 8:
                answers = []
                for i in range(numberOfOptions):
                    isCorrectOption = self.webdriver.find_element(
                        By.ID, f"rqAnswerOption{i}"
                    ).get_attribute("iscorrectoption")
                    if isCorrectOption and isCorrectOption.lower() == "true":
                        answers.append(f"rqAnswerOption{i}")
                for answer in answers:
                    self.webdriver.find_element(By.ID, answer).click()
                    time.sleep(Utils.randomSeconds(10, 15))
                    if not self.browser.utils.waitUntilQuestionRefresh():
                        self.browser.utils.resetTabs()
                        return
            elif numberOfOptions in [2, 3, 4]:
                correctOption = self.webdriver.execute_script(
                    "return _w.rewardsQuizRenderInfo.correctAnswer"
                )
                for i in range(numberOfOptions):
                    if (
                        self.webdriver.find_element(
                            By.ID, f"rqAnswerOption{i}"
                        ).get_attribute("data-option")
                        == correctOption
                    ):
                        self.webdriver.find_element(By.ID, f"rqAnswerOption{i}").click()
                        time.sleep(Utils.randomSeconds(10, 15))
                        if not self.browser.utils.waitUntilQuestionRefresh():
                            self.browser.utils.resetTabs()
                            return
                        break
            if question + 1 != numberOfQuestions:
                time.sleep(Utils.randomSeconds(10, 15))
        time.sleep(Utils.randomSeconds(10, 15))
        self.browser.utils.closeCurrentTab()

    def completeABC(self):
        # Simulate completing an ABC activity
        counter = self.webdriver.find_element(
            By.XPATH, '//*[@id="QuestionPane0"]/div[2]'
        ).text[:-1][1:]
        numberOfQuestions = max(int(s) for s in counter.split() if s.isdigit())
        for question in range(numberOfQuestions):
            self.webdriver.find_element(
                By.ID, f"questionOptionChoice{question}{random.randint(0, 2)}"
            ).click()
            time.sleep(Utils.randomSeconds(10, 15))
            self.webdriver.find_element(By.ID, f"nextQuestionbtn{question}").click()
            time.sleep(Utils.randomSeconds(10, 15))
        time.sleep(Utils.randomSeconds(1, 7))
        self.browser.utils.closeCurrentTab()

    def completeThisOrThat(self):
        # Simulate completing a This or That activity
        if not self.browser.utils.waitUntilQuizLoads():
            self.browser.utils.resetTabs()
            return
        self.webdriver.find_element(By.XPATH, '//*[@id="rqStartQuiz"]').click()
        self.browser.utils.waitUntilVisible(
            By.XPATH, '//*[@id="currentQuestionContainer"]/div/div[1]', 10
        )
        time.sleep(Utils.randomSeconds(10, 15))
        for _ in range(10):
            correctAnswerCode = self.webdriver.execute_script(
                "return _w.rewardsQuizRenderInfo.correctAnswer"
            )
            answer1, answer1Code = self.getAnswerAndCode("rqAnswerOption0")
            answer2, answer2Code = self.getAnswerAndCode("rqAnswerOption1")
            if answer1Code == correctAnswerCode:
                answer1.click()
                time.sleep(Utils.randomSeconds(10, 15))
            elif answer2Code == correctAnswerCode:
                answer2.click()
                time.sleep(Utils.randomSeconds(10, 15))

        time.sleep(Utils.randomSeconds(10, 15))
        self.browser.utils.closeCurrentTab()

    def getAnswerAndCode(self, answerId: str) -> tuple:
        # Helper function to get answer element and its code
        answerEncodeKey = self.webdriver.execute_script("return _G.IG")
        answer = self.webdriver.find_element(By.ID, answerId)
        answerTitle = answer.get_attribute("data-option")
        if answerTitle is not None:
            return (
                answer,
                self.browser.utils.getAnswerCode(answerEncodeKey, answerTitle),
            )
        else:
            return (answer, None)
