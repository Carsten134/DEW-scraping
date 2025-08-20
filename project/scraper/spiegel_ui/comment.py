import re

from scraper.spiegel_ui.base import SpiegelUIComponent


class SpiegelComment(SpiegelUIComponent):
    def to_dict(self):
        com_el = self.raw.text.split("\n")
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