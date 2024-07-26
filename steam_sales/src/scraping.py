import os
import time
import warnings
from abc import ABC, abstractmethod
from multiprocessing import Pool, cpu_count

import requests
from crud import bulk_ingest_meta_data, bulk_ingest_steamspy_data, log_last_run_time
from db import get_db
from requests.exceptions import RequestException, SSLError
from settings import Path, config, get_logger
from sqlalchemy import text
from tqdm import tqdm
from validation import GameDetails, GameDetailsList, GameMetaDataList, LastRun

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

    def get_sql_query(self, file_name: str):
        with open(os.path.join(Path.sql_queries, file_name), "r") as f:
            query = text(f.read())
        return query

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


class SteamSpyFetcher(BaseFetcher):
    def __init__(self, batch_size: int = 1000):
        super().__init__()

        self.url = config.STEAMSPY_BASE_URL
        self.batch_size = batch_size

    def parse_steamspy_request(self, appid: int):
        """
        Parses the SteamSpy request for a specific app ID.

        Args:
            appid (int): The ID of the app to retrieve details for.

        Returns:
            GameDetails: An instance of the GameDetails class containing the parsed data.
        """
        url = config.STEAMSPY_BASE_URL
        parameters = {"request": "appdetails", "appid": appid}
        json_data = self.get_request(url, parameters)

        return GameDetails(**json_data)

    def fetch_and_process_app_data(self, app_id_list):
        """
        Fetches and processes app data for a given list of app IDs.

        Args:
            app_id_list (list): A list of app IDs to fetch data for.

        Returns:
            GameDetailsList: A list of game details objects containing the fetched app data.
        """

        app_data = []
        with Pool(processes=cpu_count()) as pool:
            results = pool.map(self.parse_steamspy_request, app_id_list)
            app_data.extend(filter(None, results))

        return GameDetailsList(games=app_data)

    def run(self):
        """
        Collects SteamSpy data for a list of app IDs in batches and ingests the data into a database.

        Args:
            batch_size (int, optional): The number of app IDs to process in each batch. Defaults to 1000.
        """
        db = get_db()
        query = self.get_sql_query("steamspy_appid_dup.sql")

        result = db.execute(query)
        app_id_list = [row[0] for row in result.fetchall()]
        logger.info(f"{len(app_id_list)} ID's found")

        for i in tqdm(range(0, len(app_id_list), self.batch_size)):
            batch = app_id_list[i : i + self.batch_size]
            app_data = self.fetch_and_process_app_data(batch)

            bulk_ingest_steamspy_data(app_data, db)

        db.close()


if __name__ == "__main__":
    scraper = SteamSpyMetadataFetcher(max_pages=4)
    scraper.run()
