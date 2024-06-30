import os
import warnings
from multiprocessing import Pool, cpu_count

from collect_metadata import get_request
from crud import bulk_ingest_steamspy_data
from db import get_db
from settings import Path, config, get_logger
from sqlalchemy import text
from tqdm import tqdm
from validation import GameDetails, GameDetailsList

warnings.filterwarnings("ignore")

logger = get_logger(__file__)


def parse_steamspy_request(appid: int):
    """
    Parses the SteamSpy request for a specific app ID.

    Args:
        appid (int): The ID of the app to retrieve details for.

    Returns:
        GameDetails: An instance of the GameDetails class containing the parsed data.
    """
    url = config.STEAMSPY_BASE_URL
    parameters = {"request": "appdetails", "appid": appid}
    json_data = get_request(url, parameters)

    return GameDetails(**json_data)


def fetch_and_process_app_data(app_id_list):
    """
    Fetches and processes app data for a given list of app IDs.

    Args:
        app_id_list (list): A list of app IDs to fetch data for.

    Returns:
        GameDetailsList: A list of game details objects containing the fetched app data.
    """

    app_data = []
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(parse_steamspy_request, app_id_list)
        app_data.extend(filter(None, results))

    return GameDetailsList(games=app_data)


def main():
    db = get_db()
    with open(os.path.join(Path.sql_queries, "steamspy_appid_dup.sql"), "r") as f:
        query = text(f.read())

    result = db.execute(query)
    app_id_list = [row[0] for row in result.fetchall()]
    logger.info(f"{len(app_id_list)} ID's found")

    batch_size = 1000
    current_batch = 0

    for i in tqdm(range(0, len(app_id_list), batch_size)):
        current_batch += 1
        batch = app_id_list[i : i + batch_size]
        app_data = fetch_and_process_app_data(batch)

        bulk_ingest_steamspy_data(app_data, db)

    db.close()


if __name__ == "__main__":
    main()
