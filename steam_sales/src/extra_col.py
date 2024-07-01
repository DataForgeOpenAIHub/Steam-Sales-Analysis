import os
import warnings
from multiprocessing import Pool, cpu_count

import typer
from collect_metadata import get_request
from crud import bulk_ingest_steam_data, bulk_ingest_temp_data
from db import get_db
from settings import Path, config, get_logger
from sqlalchemy import text
from tqdm import tqdm
from typing_extensions import Annotated
from validation import Game, GameList, TempDetails, TempDetailsList

warnings.filterwarnings("ignore")

logger = get_logger(__file__)
app = typer.Typer(name="Steam Data Collector")


def parse_steam_request(appid: int):
    """
    Parse the Steam request for a given appid.

    Args:
        appid (int): The ID of the Steam application.

    Returns:
        dict: The data retrieved from the Steam request, or None if the request fails.
    """
    url = f"{config.STEAM_BASE_SEARCH_URL}/api/appdetails/"
    parameters = {"appids": appid}

    json_data = get_request(url, parameters=parameters)

    if json_data:
        resp = json_data[str(appid)]
        if resp["success"]:
            data = resp["data"]
            data = parse_game_data(data)

            if data and appid == data.appid:
                return data

        logger.error(f"Could not find data for appid {appid} in Steam Store Database")
    return None


def parse_game_data(data: dict):
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
            "requirements": data["pc_requirements"],
            "platform": data["platforms"],
            "release_date": data["release_date"]["date"],
        }
        logger.info(game_data)
        logger.info(TempDetails(**game_data))
        return TempDetails(**game_data)
    except KeyError as ke:
        logger.error(f"KeyError parsing game data for `{data['steam_appid']}`: Missing key {ke}")

    return None


def fetch_and_process_app_data(batch_list):
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
            results = pool.map(parse_steam_request, batch_list)
            app_data.extend(filter(None, results))

        return app_data
    return None


@app.command(name="fetch_ingest_data", help="Fetch and ingest data from Steam Store Database")
def main(
    batch_size: Annotated[int, typer.Option(help="Number of app IDs to process in each batch.")] = 5,
    bulk_factor: Annotated[
        int, typer.Option(help="Factor to determine when to perform a bulk insert (batch_size * bulk_factor).")
    ] = 10,
    reverse: Annotated[bool, typer.Option(help="Process app IDs in reverse order.")] = False,
):
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
    # Create a database session
    db = get_db()

    # Query unique appids from the database
    with open(os.path.join(Path.sql_queries, "temp.sql"), "r") as f:
        query = text(f.read())

    result = db.execute(query)
    app_id_list = [row[0] for row in result.fetchall()]

    if reverse:
        app_id_list.reverse()

    logger.info(f"{len(app_id_list)} ID's found")

    # Get the list of games batch them and insert into db
    games = TempDetailsList(games=[])

    for i in tqdm(range(0, len(app_id_list), batch_size)):
        batch = app_id_list[i : i + batch_size]
        app_data = fetch_and_process_app_data(batch)

        if app_data:
            games.games.extend(app_data)

        if games.get_num_games() >= batch_size * bulk_factor:
            bulk_ingest_temp_data(games, db)
            games.games = []

    db.close()


if __name__ == "__main__":
    app()
