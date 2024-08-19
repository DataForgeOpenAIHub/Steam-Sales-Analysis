import os
import time
import warnings
from abc import ABC, abstractmethod
from multiprocessing import Pool, cpu_count

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, SSLError
from sqlalchemy import text
from tqdm import tqdm

from steam_sales.steam_etl.crud import (
    bulk_ingest_meta_data,
    bulk_ingest_steam_data,
    bulk_ingest_steamspy_data,
    flag_faulty_appid,
)
from steam_sales.steam_etl.db import get_db
from steam_sales.steam_etl.settings import Path, config, get_logger
from steam_sales.steam_etl.utils import log_last_run
from steam_sales.steam_etl.validation import Game, GameDetails, GameDetailsList, GameList, GameMetaDataList

warnings.filterwarnings("ignore")


class BaseFetcher(ABC):
    def __init__(self):
        self.base_logger = get_logger(name="BaseFetcher")

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
        headers = {"User-Agent": "YourCustomUserAgent/1.0", "DNT": "1"}
        while try_count < max_retries:
            try:
                response = requests.get(url=url, params=parameters, headers=headers)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", wait_time))
                    self.base_logger.warning(f"Rate limited. Waiting for {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    self.base_logger.info(f"Error: Request failed with status code {response.status_code}")
                    return None
            except SSLError as e:
                self.base_logger.error(f"SSL Error: {e}")
            except RequestException:
                self.base_logger.exception("Request Exception: No response from server")

            try_count += 1
            self.base_logger.info(f"Retrying ({try_count}/{max_retries}) in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time *= exponential_multiplier

        self.base_logger.error(
            f"Failed to retrieve data from {url}?appids={parameters['appids']} after {max_retries} retries."
        )

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
        self.logger = get_logger(name="SteamSpyMetadataFetcher")

        self.max_pages = max_pages
        self.url = config.STEAMSPY_BASE_URL

    @log_last_run(scraper_name="meta")
    def run(self):
        """
        Fetches game metadata from SteamSpy API and stores it in a database.
        """
        new_docs_added = 0
        with get_db() as db:
            for i in tqdm(range(self.max_pages)):
                parameters = {"request": "all", "page": i}
                json_data = self.get_request(self.url, parameters)

                if json_data is None:
                    continue

                games = GameMetaDataList(games=json_data.values())
                new_docs_added += bulk_ingest_meta_data(games, db)

        self.logger.info(f"Successfully added {new_docs_added} documents to the 'steamspy_games_metadata' table")


class SteamSpyFetcher(BaseFetcher):
    def __init__(self, batch_size: int = 1000):
        super().__init__()
        self.logger = get_logger(name="SteamSpyFetcher")

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

    @log_last_run(scraper_name="steamspy")
    def run(self):
        """
        Collects SteamSpy data for a list of app IDs in batches and ingests the data into a database.

        Args:
            batch_size (int, optional): The number of app IDs to process in each batch. Defaults to 1000.
        """
        new_docs_added = 0

        with get_db() as db:
            query = self.get_sql_query("steamspy_appid_dup.sql")

            result = db.execute(query)
            app_id_list = [row[0] for row in result.fetchall()]
            self.logger.info(f"{len(app_id_list)} ID's found")

            for i in tqdm(range(0, len(app_id_list), self.batch_size)):
                batch = app_id_list[i : i + self.batch_size]
                app_data = self.fetch_and_process_app_data(batch)

                new_docs_added += bulk_ingest_steamspy_data(app_data, db)

        self.logger.info(f"Successfully added {new_docs_added} documents to the 'steamspy_games_raw' table")


class SteamStoreFetcher(BaseFetcher):
    def __init__(self, batch_size: int = 5, bulk_factor: int = 10, reverse: bool = False):
        super().__init__()
        self.logger = get_logger(name="SteamStoreFetcher")

        self.url = config.STEAM_BASE_SEARCH_URL
        self.batch_size = batch_size
        self.bulk_factor = bulk_factor
        self.reverse = reverse

    def parse_steam_request(self, appid: int):
        """
        Parse the Steam request for a given appid.

        Args:
            appid (int): The ID of the Steam application.

        Returns:
            dict: The data retrieved from the Steam request, or None if the request fails.
        """
        url = f"{self.url}/api/appdetails/"
        parameters = {"appids": appid}

        json_data = self.get_request(url, parameters=parameters)

        if json_data:
            resp = json_data[str(appid)]
            if resp["success"]:
                data = resp["data"]
                data = self.parse_game_data(data)

                if data and appid == data.appid:
                    return data

            self.logger.error(f"Could not find data for appid {appid} in Steam Store Database")

            with get_db() as db:
                flag_faulty_appid(appid, db)

        return None

    def parse_html_to_dict(self, html_content: str):
        """
        Parses the HTML content and converts it into a dictionary.

        Args:
            html_content (str): The HTML content to be parsed.

        Returns:
            dict: A dictionary containing the parsed data, where each key represents a line of text and its
            corresponding value.
        """
        soup = BeautifulSoup(html_content, "lxml")
        plain_text = soup.get_text(separator="\n", strip=True)
        lines = plain_text.split("\n")
        requirements_dict = {}

        for i in range(0, len(lines) - 1, 2):
            requirements_dict[lines[i]] = lines[i + 1]

        return requirements_dict

    def text_parser(self, text: str):
        """
        Parses the given HTML text using BeautifulSoup and returns the plain text.

        Args:
            text (str): The HTML text to be parsed.

        Returns:
            str: The plain text extracted from the HTML.

        """
        if text:
            soup = BeautifulSoup(text, "lxml")
            plain_text = soup.get_text(separator="\n", strip=True)
            return plain_text

        return None

    def parse_game_data(self, data: dict):
        """
        Parses the Steam game data and returns a Game object.

        Args:
            data (dict): The Steam game data to be parsed.

        Returns:
            Game: A Game object containing the parsed data, or None if the data is invalid.
        """
        try:
            game_data = {
                "appid": data["steam_appid"],
                "name": data["name"],
                "type": data["type"],
                "required_age": data["required_age"],
                "is_free": data["is_free"],
                "controller_support": data.get("controller_support", None),
                "dlc": data.get("dlc", []),
                "detailed_description": self.text_parser(data.get("detailed_description", None)),
                "short_description": self.text_parser(data.get("short_description", None)),
                "about_the_game": self.text_parser(data.get("about_the_game", None)),
                "supported_languages": self.text_parser(data.get("supported_languages", None)),
                "reviews": self.text_parser(data.get("reviews", None)),
                "header_image": data["header_image"],
                "capsule_image": data["capsule_image"],
                "website": data.get("website", ""),
                "requirements": data["pc_requirements"],
                "developers": data.get("developers", None),
                "publishers": data["publishers"],
                "price_overview": data.get("price_overview", None),
                "platform": data["platforms"],
                "metacritic": data.get("metacritic", {}).get("score", 0),
                "categories": data.get("categories", None),
                "genres": data.get("genres", None),
                "recommendations": data.get("recommendations", {}).get("total", 0),
                "achievements": data.get("achievements", {}).get("total", 0),
                "release_date": data["release_date"]["date"],
                "coming_soon": data["release_date"]["coming_soon"],
            }

            return Game(**game_data)
        except KeyError as ke:
            self.logger.error(f"KeyError parsing game data for `{data['steam_appid']}`: Missing key {ke}")

        return None

    def fetch_and_process_app_data(self, batch_list: list):
        """
        Fetches and processes app data for a given list of app IDs.

        Args:
            app_id_list (list): A list of app IDs to fetch data for.

        Returns:
            GameList: A GameList object containing the processed app data.
        """
        app_data = []
        if batch_list:
            with Pool(processes=cpu_count()) as pool:
                results = pool.map(self.parse_steam_request, batch_list)
                app_data.extend(filter(None, results))

            return app_data
        return None

    @log_last_run(scraper_name="steam")
    def run(self):
        """
        This command fetches unique app IDs from the Steam Store Database, processes the data in batches,
        and ingests the data into the database. The process is designed to handle large datasets efficiently
        by using batch processing and bulk insertion methods.

        Parameters:
        - batch_size (int): The number of app IDs to process in each batch. Default is 5.
        - bulk_factor (int): Determines when to perform a bulk insert. Data is ingested in bulk when the
        number of processed games reaches batch_size * bulk_factor. Default is 10.
        - reverse (bool): If set to True, the app IDs are processed in reverse order. Default is False.
        """
        new_docs_added = 0

        # Create a database session
        with get_db() as db:

            # Query unique appids from the database
            query = self.get_sql_query("steam_appid_dup.sql")

            result = db.execute(query)
            app_id_list = [row[0] for row in result.fetchall()]

            if self.reverse:
                app_id_list.reverse()

            self.logger.info(f"{len(app_id_list)} ID's found")

            # Get the list of games batch them and insert into db
            games = GameList(games=[])

            for i in tqdm(range(0, len(app_id_list), self.batch_size)):
                batch = app_id_list[i : i + self.batch_size]
                app_data = self.fetch_and_process_app_data(batch)

                if app_data:
                    games.games.extend(app_data)

                if games.get_num_games() >= self.batch_size * self.bulk_factor:
                    new_docs_added += bulk_ingest_steam_data(games, db)
                    games.games = []

            # Additional check to process remaining records
            if games.get_num_games() > 0:
                new_docs_added += bulk_ingest_steam_data(games, db)

        self.logger.info(f"Successfully added {new_docs_added} documents to the 'steam_games_raw' table")


if __name__ == "__main__":
    fetcher = SteamSpyMetadataFetcher(max_pages=100)
    fetcher.run()

    fetcher = SteamSpyFetcher()
    fetcher.run()

    fetcher = SteamStoreFetcher()
    fetcher.run()
