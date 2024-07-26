import time
import warnings
from abc import ABC, abstractmethod

import requests
from crud import bulk_ingest_meta_data, log_last_run_time
from db import get_db
from requests.exceptions import RequestException, SSLError
from settings import config, get_logger
from tqdm import tqdm
from validation import GameMetaDataList, LastRun

logger = get_logger(__file__)
warnings.filterwarnings("ignore")


class BaseFetcher(ABC):
    def __init__(self):
        pass

    def get_request(self, url: str, parameters=None, max_retries=4, wait_time=4, exponential_multiplier=4):
        """
        Sends a GET request to the specified URL with optional parameters.

        Args:
            url (str): The URL to send the request to.
            parameters (dict, optional): The parameters to include in the request. Defaults to None.
            max_retries (int, optional): The maximum number of retries in case of failures. Defaults to 4.
            wait_time (int, optional): The initial wait time between retries. Defaults to 4.
            exponential_multiplier (int, optional): The multiplier for increasing wait time between retries. Defaults
            to 4.

        Returns:
            dict or None: The JSON response if the request is successful, None otherwise.
        """

        try_count = 0

        while try_count < max_retries:
            try:
                response = requests.get(url=url, params=parameters)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", wait_time))
                    logger.warning(f"Rate limited. Waiting for {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    logger.info(f"Error: Request failed with status code {response.status_code}")
                    return None
            except SSLError as e:
                logger.error(f"SSL Error: {e}")
            except RequestException as e:
                logger.exception(f"Request Exception: {e}")

            try_count += 1
            logger.info(f"Retrying ({try_count}/{max_retries}) in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time *= exponential_multiplier

        logger.error(f"Failed to retrieve data from {url}?appids={parameters['appids']} after {max_retries} retries.")

        return None

    @abstractmethod
    def run(self):
        pass


class SteamSpyMetadataFetcher(BaseFetcher):
    def __init__(self, max_pages: int = 100):
        super().__init__()

        self.max_pages = max_pages
        self.url = config.STEAMSPY_BASE_URL

    def run(self):
        """
        Fetches game metadata from SteamSpy API and stores it in a database.
        """
        db = get_db()
        for i in tqdm(range(self.max_pages)):
            parameters = {"request": "all", "page": i}
            json_data = self.get_request(self.url, parameters)

            if json_data is None:
                continue

            games = GameMetaDataList(games=json_data.values())
            bulk_ingest_meta_data(games, db)

        last_run = LastRun(scraper="meta")
        log_last_run_time(last_run, db)

        db.close()


if __name__ == "__main__":
    scraper = SteamSpyMetadataFetcher(max_pages=4)
    scraper.run()
