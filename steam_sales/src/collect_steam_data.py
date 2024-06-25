import datetime as dt
import os
import statistics
import time
from multiprocessing import Pool, cpu_count

from bs4 import BeautifulSoup
from collect_metadata import get_request
from crud import bulk_ingest_steam_data
from db import get_db
from settings import Path, config, get_logger
from sqlalchemy import text
from validation import Game, GameList

logger = get_logger(__name__)


def parse_steam_request(appid: int):
    url = f"{config.STEAM_BASE_SEARCH_URL}/api/appdetails/"
    parameters = {"appids": appid}

    json_data = get_request(url, parameters=parameters)
    if json_data:
        json_app_data = json_data[str(appid)]

        if json_app_data["success"]:
            data = json_app_data["data"]
            return data

    return None


def parse_html_to_dict(html_content: str):
    soup = BeautifulSoup(html_content, "lxml")
    plain_text = soup.get_text(separator="\n", strip=True)
    lines = plain_text.split("\n")
    requirements_dict = {}

    for i in range(0, len(lines) - 1, 2):
        requirements_dict[lines[i]] = lines[i + 1]

    return requirements_dict


def requirements_parser(requirements: dict):
    requirements_dict = {"minimum": None, "recommended": None}

    if "minimum" in requirements:
        requirements_dict["minimum"] = parse_html_to_dict(requirements["minimum"])

    if "recommended" in requirements:
        requirements_dict["recommended"] = parse_html_to_dict(requirements["recommended"])

    return requirements_dict


def text_parser(text: str):
    if text:
        soup = BeautifulSoup(text, "lxml")
        plain_text = soup.get_text(separator="\n", strip=True)
        return plain_text

    return None


def parse_game_data(data: dict):
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
    except Exception as e:
        logger.error(f"Error parsing game data for `{data.get('steam_appid', 'unknown')}`: {str(e)}")

    return None


def fetch_and_process_app_data(app_id_list):
    app_data = []
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(parse_steam_request, app_id_list)
        app_data.extend(filter(None, results))

    final_app_data = [game for game in (parse_game_data(data) for data in app_data) if game is not None]

    return GameList(games=final_app_data)


def main():
    db = get_db()
    with open(os.path.join(Path.sql_queries, "steam_appid_dup.sql"), "r") as f:
        query = text(f.read())

    result = db.execute(query)
    app_id_list = [row[0] for row in result.fetchall()]
    logger.info(f"{len(app_id_list)} ID's found")

    batch_size = 5
    num_batches = (len(app_id_list) + batch_size - 1) // batch_size
    current_batch = 0

    batch_times = []

    for i in range(0, len(app_id_list), batch_size):
        start_time = time.time()

        current_batch += 1
        batch = app_id_list[i : i + batch_size]
        app_data = fetch_and_process_app_data(batch)

        bulk_ingest_steam_data(app_data, db)

        end_time = time.time()
        time_taken = end_time - start_time
        batch_times.append(time_taken)
        mean_time = statistics.mean(batch_times)
        est_remaining = (num_batches - i - 2) * mean_time
        remaining_td = dt.timedelta(seconds=round(est_remaining))
        time_td = dt.timedelta(seconds=round(time_taken))

        logger.info(f"Batch {current_batch} of {num_batches} completed. Time taken: {time_td} -> ETA: {remaining_td}")


if __name__ == "__main__":
    main()
