from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scraper.autocorrect.specifications.base import PageSpecification
import re


class OnXHome(PageSpecification):
    def is_satisfied(self):
        # checks if current url contains the home page url
        home_sub_str = re.findall(
            "^https://x.com/home", self.candidate_driver.current_url)
        return len(home_sub_str) > 0


class OnXSearch(PageSpecification):
    def is_satisfied(self):
        # checks current url for search url substring
        search_sub_str = re.findall(
            "^https://x.com/search", self.candidate_driver.current_url)
        return bool(len(search_sub_str))


class PostsVisible(PageSpecification):
    def is_satisfied(self):
        try:
            # wait until posts are loaded
            WebDriverWait(self.candidate_driver, 10)\
                .until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'article')))
            return True
        except TimeoutException:
            # check why the posts are not visible
            return False


class NoSearchResultsExist(PageSpecification):
    def is_satisfied(self):
        no_results_sub = re.findall(
            "No results for", self.candidate_driver.page_source)
        return len(no_results_sub) > 0


class SomethingWentWrong(PageSpecification):
    def is_satisfied(self):
        failed = re.findall("Something went wrong. Try reloading.",
                            self.candidate_driver.page_source)
        return len(failed) > 0
