import time
import warnings

import requests
import typer
from crud import bulk_ingest_meta_data, log_last_run_time
from db import get_db
from requests.exceptions import RequestException, SSLError
from settings import config, get_logger
from tqdm import tqdm
from typer import Typer
from typing_extensions import Annotated
from validation import GameMetaDataList, LastRun

warnings.filterwarnings("ignore")

logger = get_logger(__file__)
app = Typer(name="SteamSpy Metadata Collector")


def get_request(url: str, parameters=None, max_retries=4):
    """
    Sends a GET request to the specified URL with optional parameters.

    Args:
        url (str): The URL to send the request to.
        parameters (dict, optional): The parameters to include in the request. Defaults to None.
        max_retries (int, optional): The maximum number of retries in case of failures. Defaults to 4.

    Returns:
        dict or None: The JSON response if the request is successful, None otherwise.
    """

    try_count = 0
    wait_time = 4

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
        wait_time *= 4

    logger.error(f"Failed to retrieve data from {url}?appids={parameters['appids']} after {max_retries} retries.")

    return None


@app.command(name="fetch_metadata", help="Fetch and ingest metadata from SteamSpy Database")
def main(max_pages: Annotated[int, typer.Option(help="Number of pages to fetch from.")] = 100):
    """
    Fetches game metadata from SteamSpy API and stores it in a database.

    Args:
        max_pages (int, optional): Number of pages to fetch from. Defaults to 100.
    """
    url = config.STEAMSPY_BASE_URL
    db = get_db()

    for i in tqdm(range(max_pages)):
        parameters = {"request": "all", "page": i}
        json_data = get_request(url, parameters)

        if json_data is None:
            continue

        games = GameMetaDataList(games=json_data.values())
        bulk_ingest_meta_data(games, db)

    db.close()

    last_run = LastRun(scraper="meta")
    log_last_run_time(last_run, db)


if __name__ == "__main__":
    app()
