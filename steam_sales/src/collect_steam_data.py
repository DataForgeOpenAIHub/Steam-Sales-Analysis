import os
import warnings
from multiprocessing import Pool, cpu_count

from bs4 import BeautifulSoup
from collect_metadata import get_request
from crud import bulk_ingest_steam_data
from db import get_db
from settings import Path, config, get_logger
from sqlalchemy import text
from tqdm import tqdm
from validation import Game, GameList

warnings.filterwarnings("ignore")

logger = get_logger(__file__)


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

    resp = json_data[str(appid)]
    if resp["success"]:
        data = resp["data"]
        data = parse_game_data(data)

        if data and appid == data.appid:
            return data

    logger.error(f"Could not find data for appid {appid} in Steam Store Database")
    return None


def parse_html_to_dict(html_content: str):
    """
    Parses the HTML content and converts it into a dictionary.

    Args:
        html_content (str): The HTML content to be parsed.

    Returns:
        dict: A dictionary containing the parsed data, where each key represents a line of text and its corresponding
        value.
    """
    soup = BeautifulSoup(html_content, "lxml")
    plain_text = soup.get_text(separator="\n", strip=True)
    lines = plain_text.split("\n")
    requirements_dict = {}

    for i in range(0, len(lines) - 1, 2):
        requirements_dict[lines[i]] = lines[i + 1]

    return requirements_dict


def requirements_parser(requirements: dict):
    """
    Parses the requirements dictionary and returns a dictionary with minimum and recommended requirements.

    Args:
        requirements (dict): A dictionary containing the minimum and recommended requirements.

    Returns:
        dict: A dictionary with minimum and recommended requirements parsed from the input dictionary.
    """

    requirements_dict = {"minimum": None, "recommended": None}

    if "minimum" in requirements:
        requirements_dict["minimum"] = parse_html_to_dict(requirements["minimum"])

    if "recommended" in requirements:
        requirements_dict["recommended"] = parse_html_to_dict(requirements["recommended"])

    return requirements_dict


def text_parser(text: str):
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
            "name": data["name"],
            "type": data["type"],
            "required_age": data["required_age"],
            "is_free": data["is_free"],
            "controller_support": data.get("controller_support", None),
            "dlc": data.get("dlc", []),
            "detailed_description": text_parser(data.get("detailed_description", None)),
            "short_description": text_parser(data.get("short_description", None)),
            "about_the_game": text_parser(data.get("about_the_game", None)),
            "supported_languages": text_parser(data.get("supported_languages", None)),
            "reviews": text_parser(data.get("reviews", None)),
            "header_image": data["header_image"],
            "capsule_image": data["capsule_image"],
            "website": data.get("website", ""),
            "pc_requirements": requirements_parser(data["pc_requirements"]),
            "developers": data.get("developers", None),
            "publishers": data["publishers"],
            "pc_platform": data["platforms"]["windows"],
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


def main():
    db = get_db()
    with open(os.path.join(Path.sql_queries, "steam_appid_dup.sql"), "r") as f:
        query = text(f.read())

    result = db.execute(query)
    app_id_list = [row[0] for row in result.fetchall()]
    logger.info(f"{len(app_id_list)} ID's found")

    batch_size = 5
    current_batch = 0

    games = GameList(games=[])

    for i in tqdm(range(0, len(app_id_list), batch_size)):
        current_batch += 1
        batch = app_id_list[i : i + batch_size]
        app_data = fetch_and_process_app_data(batch)

        if app_data:
            games.games.extend(app_data)

        if games.get_num_games() >= batch_size * 10:
            bulk_ingest_steam_data(games, db)
            games.games = []


if __name__ == "__main__":
    main()
