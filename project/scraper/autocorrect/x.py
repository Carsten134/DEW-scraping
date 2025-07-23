"""
Autocorrections for the XScraper object
"""
from functools import wraps
from selenium.webdriver import Firefox
import time

from scraper.autocorrect.specifications.base import AndSpecification, OrSpecification
from scraper.autocorrect.specifications import x as XSpec


def search_autocorrect(search):
    @wraps(search)
    def wrapped_search(self, text):
        # checking conditions ---------------------------------------------
        init_conditions = OrSpecification([XSpec.OnXSearch(self.driver),
                                           XSpec.OnXHome(self.driver)])
        valid_start = init_conditions.validate()
        if not valid_start:
            raise RuntimeError("Error in search, driver not on valid page")

        # -----------------------------------------------------------------

        search(self, text)

        # validate the answer and activate fallbacks if necessary ---------
        no_posts = not XSpec.PostsVisible(self.driver).is_satisfied()
        if no_posts:
            # no posts are visible... so check the reason why:
            not_found = XSpec.NoSearchResultsExist(self.driver).is_satisfied()
            if not_found:
                # for now just print a simple warning in this case
                self._log(f"WARNING: Search {text} found no results")

            something_went_wrong = XSpec.SomethingWentWrong(self.driver).is_satisfied()
            if something_went_wrong:
                feedback = fallback429(self.driver,
                                       self.run_config["fallbacks"]["429"]["secWaiting"],
                                       self.run_config["fallbacks"]["429"]["tries"])

                if feedback == "not found":
                    self._log(f"WARNING: Search {text} found no results")

                elif feedback == "not fixed":
                    raise RuntimeError(
                        f"Something went wrong on search {text}, check the browser and logfile {self.log_path} for more info.")

    return wrapped_search


def fallback429(driver: Firefox, waiting_time: float, tries: float):
    for _ in range(tries):
        time.sleep(waiting_time)
        driver.refresh()

        # wait until the window has refreshed
        time.sleep(2)
        if XSpec.SomethingWentWrong(driver).is_satisfied():
            continue

        posts = XSpec.PostsVisible(driver).is_satisfied()
        if posts:
            return "fixed"

        if not posts and XSpec.NoSearchResultsExist(driver).is_satisfied():
            return "not found"

    return "not fixed"
