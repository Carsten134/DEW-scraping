from selenium.webdriver.common.by import By

from scraper.spiegel_ui.base import SpiegelUIComponent
from scraper.spiegel_ui.editors_note import SpiegelEditorsNote
from scraper.spiegel_ui.related_article import SpiegelRelatedArticle

class SpiegelRelatedSection(SpiegelUIComponent):    
    def to_dict(self):
        candidate_1 = self.raw[0]
        candidate_2 = self.raw[1]
        
        # first identify the first candidate as editors note or related articels
        is_articles_1 = "Artikel zur Debatte" in candidate_1.text
        is_editors_note_1 = "Anmerkung der Redaktion" in candidate_1.text

        related = {}
        # since editor notes are always named last,
        # the second candidate must be the comment section
        # and does not has to be parsed
        if is_editors_note_1:
            related["editors_note"] = SpiegelEditorsNote(candidate_1).to_dict()
        
        # if candidate 1 is related articles
        # then check if editors note was given
        elif is_articles_1:
            articles = candidate_1.find_elements(By.CSS_SELECTOR, "a")
            related["related_articles"] = [SpiegelRelatedArticle(art).to_dict() for art in articles]
            is_editors_note_2 = "Anmerkung der Redaktion" in candidate_2.text
            if is_editors_note_2:
                related["editors_note"] = SpiegelEditorsNote(candidate_2).to_dict()
        
        return related