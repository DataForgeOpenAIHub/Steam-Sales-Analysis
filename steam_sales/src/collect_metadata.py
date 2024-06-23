import time
import requests
from requests.exceptions import SSLError, RequestException
from settings import config, get_logger
from validation import GameMetaDataList
from crud import bulk_ingest_meta_data
from db import get_db


logger = get_logger(__file__)


def get_request(url: str, parameters=None, max_retries=5):
    try_count = 0
    while try_count < max_retries:
        try:
            response = requests.get(url=url, params=parameters)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning(f"Rate limited. Waiting for {response.headers['Retry-After']} seconds...")
                time.sleep(int(response.headers["Retry-After"]) + 1)
            else:
                logger.error(f"Error: Request failed with status code {response.status_code}")
                return None
        except SSLError as e:
            logger.error(f"SSL Error: {e}")
        except RequestException as e:
            logger.exception(f"Request Exception: {e}")

        try_count += 1
        logger.info(f"Retrying ({try_count}/{max_retries})...")
        time.sleep(5)

    logger.info(f"Failed to retrieve data from {url} after {max_retries} retries.")
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
