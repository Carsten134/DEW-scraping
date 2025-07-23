import pandas as pd
import os
import re
from urllib.parse import unquote

from loaders.config import X_JSON_RETRIEVAL


class XDataLoader:
    def __init__(self, dir):
        self.raw_data = pd.DataFrame()
        self.processed_data = pd.DataFrame()
        self.fetch_from_dir(dir)

    def fetch_from_dir(self, dir: str) -> None:
        """
        Fetch all .ndjsons from the download dir
        """
        first = True
        for file in os.listdir(dir):
            # only fetch .ndjson files
            if not file.endswith(".ndjson"):
                continue

            # if first only fetch dataframe
            if first:
                self.raw_data = pd.read_json("/".join([dir, file]), lines=True)
                first = False
                continue

            # ...else concatinate existsing with fetched dataframe
            self.raw_data = pd.concat(
                [self.raw_data, pd.read_json("/".join([dir, file]), lines=True)])

        self.raw_data.reset_index(inplace=True)

    def process_raw_data(self) -> None:
        """
        Processes the fetched raw data. Only call if data was fetched from dir.
        """
        # special case to warn user if data wasn't fetched yet
        if self.raw_data.empty:
            raise RuntimeError(
                "Tried to process data from XDataLoader instance, that had no raw data. Fetch first with `.fetch_from_dir('*your dir')`")

        self.processed_data = self.raw_data.copy()

        # extract all the relevant information from the
        for col in X_JSON_RETRIEVAL:
            self.processed_data[col] = self.processed_data.apply(
                lambda row: XDataLoader._retrieve_if_there(row["data"], X_JSON_RETRIEVAL[col]), axis=1)

        # extract search query
        self.processed_data["source_search_query"] = self.processed_data.apply(
            lambda row: XDataLoader._retrieve_search_query_from_url(row["source_platform_url"]), axis=1)

        # drop unwanted columns
        self.processed_data.drop(columns=["id", "index", "nav_index", "item_id", "timestamp_collected",
                                 "source_platform", "source_platform_url", "source_url", "user_agent", "data"], inplace=True)

    def save_to_csv(self, dir) -> None:
        # include user warning
        if self.processed_data.empty:
            raise RuntimeError(
                "Tried to save processed data in XDataLoader instance but data was not processed yet.")

        self.processed_data.to_csv(dir)

    @classmethod
    def _retrieve_if_there(cls, data: dict, keys: list[str]):
        temp = data
        for key in keys:
            if key in temp:
                temp = temp[key]
            else:
                return None
        return temp

    @classmethod
    def _retrieve_search_query_from_url(cls, url):
        candidate = re.findall(r"https://x.com/search\?q=(.+)&", url)
        if candidate:
            return unquote(candidate[0])
