"""
I noticed the SpiegelScraper-file becoming very long and complicated,
with most of the code being dedicated to extracting data from the dom and 
handling edge cases when doing so.

This is why I will now introduce SpigelUIComponents. These are classes specifically
designed to fetch data from the spiegel website, such that navigation and interaction is seperate concern from 
fetching data.
"""


class SpiegelUIComponent:
    """
    Abstract class for fetching data from the spiegel website.
    """

    def __init__(self, raw):
        self.raw = raw

    def to_dict(self) -> dict:
        raise NotImplementedError()
