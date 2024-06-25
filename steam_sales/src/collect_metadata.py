import time

import requests
from crud import bulk_ingest_meta_data
from db import get_db
from requests.exceptions import RequestException, SSLError
from settings import config, get_logger
from validation import GameMetaDataList

logger = get_logger(__file__)


def get_request(url: str, parameters=None, max_retries=4):
    try_count = 0
    wait_time = 1  # Initial wait time in seconds

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
        wait_time *= 4  # Exponential backoff

    logger.error(f"Failed to retrieve data from {url}, params={parameters} after {max_retries} retries.")

    return None


def main():
    url = config.STEAMSPY_BASE_URL
    db = get_db()

    max_pages = 100
    for i in range(max_pages):
        parameters = {"request": "all", "page": i}
        json_data = get_request(url, parameters)

        if json_data is None:
            break

        games = GameMetaDataList(games=json_data.values())
        bulk_ingest_meta_data(games, db)


if __name__ == "__main__":
    main()
