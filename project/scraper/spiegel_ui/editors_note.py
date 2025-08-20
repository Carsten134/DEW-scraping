from selenium.webdriver.common.by import By

from scraper.spiegel_ui.base import SpiegelUIComponent

class SpiegelEditorsNote(SpiegelUIComponent):
    def parse_editors_note(self):
        # fetch children and go into the text section
        text_scection = self.raw.find_elements(By.CSS_SELECTOR, ":scope > *")[1]
        # fetch text and return it
        return text_scection.text
