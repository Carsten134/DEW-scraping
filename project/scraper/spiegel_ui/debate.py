import re
from selenium.webdriver.common.by import By

from scraper.spiegel_ui.base import SpiegelUIComponent
from scraper.spiegel_ui.comment import SpiegelComment
from scraper.spiegel_ui.related import SpiegelRelatedSection

class SpiegelDebate(SpiegelUIComponent):
    def to_dict(self):
        deb_el = self.raw.text.split("\n")

        extracted = {}
        extracted["date"] = deb_el.pop(0)
        extracted["status"] = deb_el.pop(0)
        extracted["title"] = deb_el.pop(0)
        
        # parse related section
        child_elements = self.raw.find_elements(By.CSS_SELECTOR, ":scope > *")
        # there are two possible sections: related articles and editors note
        candidate_1 = child_elements[1]
        candidate_2 = child_elements[2]
        extracted["related"] = SpiegelRelatedSection([candidate_1, candidate_2]).to_dict()

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

        comment_area = self.raw.find_element(By.CSS_SELECTOR, "#debate-content")
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
                SpiegelComment(com).to_dict() for com in yes_comments]
            extracted["comments"].extend(
                [SpiegelComment(com).to_dict() for com in no_comments])
            return extracted
        else:
            extracted["comments"] = None
            return extracted