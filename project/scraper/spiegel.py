from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service

from sys import platform
import pandas as pd
import re
import os
import time

from scraper.config import SPIEGEL_LOG_DIR


class SpiegelScraper:
    def __init__(self, run_config: dict):
        """
        SpiegelScraper: An object for scraping SpiegelDebatten

        Input: 
          run_config(dict): Config for the scraping run, see run-configs directory for examples

        Returns:
          SpiegelScraper instance. To start scraping, call the .run() function 
        """
        # user credentials
        self.mail = run_config["user"]["mail"]
        self.password = run_config["user"]["password"]
        self.log_path = SPIEGEL_LOG_DIR + \
            run_config["log"]["fileName"] + ".txt"

        # resolve searchterms
        self.search_queue = run_config["searchTerms"]


        # data
        self.data = []
        # set downloadpath
        options = Options()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference(
            "browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir",
                               f"{os.getcwd()}\data\Spiegel")
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk", "application/x-ndjson,application/json")

        # instantiating firefox with proper service
        if platform == "linux" or platform == "linux2":
            self.driver = webdriver.Firefox(options=options,
                                            service=Service("./scraper/driver/geckodriver-v0.36.0-linux64.tar.gz"))
        else:
            self.driver = webdriver.Firefox(options=options)

    def run(self, continued = False):
        if not continued:
            self.login()

        for search_term in self.search_queue:
            self.search(search_term)
            self.scroll(3, 300, 2)
            time.sleep(10)
            debates_urls = self.fetch_debates()

            for url in debates_urls:
                self.driver.get(url)
                self.scroll(3, 300, 2)
                debate = self.get_current_debate()
                self.click_read_further(debate)

                debate_json = self.parse_debate(debate)
                self.data.append(debate_json)
            
            # navigate back home after scraping all debates
            self.driver.get("https://www.spiegel.de/debatten/")
            self.search_queue.pop(0)

    def login(self):
        time.sleep(2)
        self.driver.get("https://www.spiegel.de")

        WebDriverWait(self.driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[id^='sp_message_iframe']"))
        )
        # Now inside the iframe – wait for the consent button to be clickable
        accept_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((
                By.XPATH, "//button[normalize-space()='Einwilligen und weiter' or normalize-space()='Consent and continue']"
            ))
        )
        accept_button.click()

        self.driver.get("https://www.spiegel.de/debatten/")
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'a[title="Jetzt anmelden"]'))).click()

        # login routine
        email_field = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#username")))
        email_field.send_keys(self.mail + Keys.ENTER)

        password_field = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#password")))
        password_field.send_keys(self.password + Keys.ENTER)

        # accept cookie consent (again)
        WebDriverWait(self.driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[id^='sp_message_iframe']"))
        )
        # Now inside the iframe – wait for the consent button to be clickable
        accept_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((
                By.XPATH, "//button[normalize-space()='Einwilligen und weiter' or normalize-space()='Consent and continue']"
            ))
        )
        accept_button.click()
        # switch out of iframe content
        self.driver.switch_to.default_content()

        # click the cross on the subscription banner
        close_banner = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'button[onClick="atExperienceInteractAndClose()"]')
            )
        )
        close_banner.click()

    def search(self, text):
        search = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')))
        search.clear()
        search.send_keys(text + Keys.ENTER)

    def fetch_debates(self):
        # get unique urls (hence converting to set and back to list)
        return list(set([el.get_attribute("href") for el in self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="/debatten/debatte"]')]))

    def get_current_debate(self):
        return WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#debate")))

    def click_read_further(self, debate):
        # click read_further on every debate article
        spans = debate.find_elements(By.CSS_SELECTOR, "span")
        weiterlesen = [el for el in spans if bool(
            re.findall("Weiterlesen", el.get_attribute("innerHTML")))]
        for el in weiterlesen:
            el.click()
    
    def scroll(self, times, offset = 300, sleep = 1, sleep_after = 0):
        for _ in range(times):
            time.sleep(sleep)
            ActionChains(self.driver).scroll_by_amount(0, offset).perform()
            time.sleep(sleep_after)

    def parse_comment(self, comment):
        com_el = comment.text.split("\n")
        extracted = {}
        candidate_username = com_el.pop(0)
        if candidate_username == "Empfehlung":
            extracted["user_name"] = com_el.pop(0)
        else:
            extracted["user_name"] = candidate_username
        extracted["user_points"] = com_el.pop(0)
        extracted["vote_yes"] = com_el.pop(0) == "Ja"
        extracted["posted_since"] = com_el.pop(0)
        extracted["text"] = ""
        next_el = ""
        while (not next_el == "Weniger anzeigen") and (not next_el == "Weiterlesen"):
            if len(com_el) > 1:
                extracted["text"] += com_el.pop(0)
                next_el = com_el[0]
            else:
                break
        # avoid double quotes in comments
        extracted["text"] = re.sub('"', "'", extracted["text"])
        return extracted

    def parse_debate(self, debate):
        deb_el = debate.text.split("\n")

        extracted = {}
        extracted["date"] = deb_el.pop(0)
        extracted["status"] = deb_el.pop(0)
        extracted["title"] = deb_el.pop(0)
        extracted["related"] = self.parse_related(debate)

        # extract keywords
        extracted["keywords"] = []
        next_el = ""
        while not len(re.findall("\d", next_el)):
            extracted["keywords"].append(deb_el.pop(0))
            next_el = deb_el[0]

        extracted["num_votes"] = deb_el.pop(0)
        extracted["num_comments"] = deb_el.pop(0)

        deb_el.pop(0)
        deb_el.pop(0)
        extracted["votes_yes"] = deb_el.pop(0)
        deb_el.pop(0)
        extracted["votes_no"] = deb_el.pop(0)

        comment_area = debate.find_element(By.CSS_SELECTOR, "#debate-content")
        if comment_area:
            comments = comment_area.find_elements(By.CSS_SELECTOR, "ul")
        else:
            extracted["comments"] = None
            return extracted
        
        # check whether the comment section is split into
        # two columns for now only scrape comments, when there is this layout
        if len(comments) > 1:
            yes_comments = comments[0].find_elements(
                By.CSS_SELECTOR, '*[data-testid="list-item"]')
            no_comments = comments[1].find_elements(
                By.CSS_SELECTOR, '*[data-testid="list-item"]')

            extracted["comments"] = [
                self.parse_comment(com) for com in yes_comments]
            extracted["comments"].extend(
                [self.parse_comment(com) for com in no_comments])
            return extracted
        else:
            extracted["comments"] = None
            return extracted

    @classmethod
    def debate_dict_to_dataframe(cls, debate):
        comments = pd.DataFrame(debate["comments"])
        debate["keywords"] = ",".join(debate["keywords"])
        debate.pop("comments")
        debate = pd.DataFrame(debate, index=range(len(comments)))
        return comments.join(debate)
    
    @classmethod
    def editors_note_given(cls, debate):
        child_elements = debate.find_elements(By.CSS_SELECTOR, ":scope > *")
        # there are two possible sections: related articles and editors note
        candidate_1 = child_elements[1]
        candidate_2 = child_elements[2]
        
        is_in_1 = "Anmerkung der Redaktion" in candidate_1.text
        is_in_2 = "Anmerkung der Redaktion" in candidate_2.text

        return is_in_1 or is_in_2

    def parse_related(self, debate):
        child_elements = debate.find_elements(By.CSS_SELECTOR, ":scope > *")
        # there are two possible sections: related articles and editors note
        candidate_1 = child_elements[1]
        candidate_2 = child_elements[2]
        
        # first identify the first candidate as editors note or related articels
        is_articles_1 = "Artikel zur Debatte" in candidate_1.text
        is_editors_note_1 = "Anmerkung der Redaktion" in candidate_1.text

        related = {}
        # since editor notes are always named last,
        # the second candidate must be the comment section
        # and does not has to be parsed
        if is_editors_note_1:
            related["editors_note"] = self.parse_editors_note(candidate_1)
        
        # if candidate 1 is related articles
        # then check if editors note was given
        elif is_articles_1:
            articles = candidate_1.find_elements(By.CSS_SELECTOR, "a")
            related["related_articles"] = [self.parse_related_articles(art) for art in articles]
            is_editors_note_2 = "Anmerkung der Redaktion" in candidate_2.text
            if is_editors_note_2:
                related["editors_note"] = self.parse_editors_note(candidate_2)
        
        return related


    def parse_editors_note(self, editors_element):
        # fetch children and go into the text section
        text_scection = editors_element.find_elements(By.CSS_SELECTOR, ":scope > *")[1]
        # fetch text and return it
        return text_scection.text

    def parse_related_articles(self, article):
        extracted = {}
        article_text_els = article.text.split("\n")
        extracted["date_published"] = article_text_els[2]
        extracted["title"] = article_text_els[3]
        extracted["link"] = article.get_attribute("href")

        return extracted