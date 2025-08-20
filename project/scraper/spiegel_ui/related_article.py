from scraper.spiegel_ui.base import SpiegelUIComponent

class SpiegelRelatedArticle(SpiegelUIComponent):
    def to_dict(self):
        extracted = {}
        article_text_els = self.raw.text.split("\n")
        extracted["date_published"] = article_text_els[2]
        extracted["title"] = article_text_els[3]
        extracted["link"] = self.raw.get_attribute("href")

        return extracted