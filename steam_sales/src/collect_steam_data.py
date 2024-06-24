from collect_metadata import get_request
from rich.pretty import pretty_repr
from settings import config, get_logger
from validation import Game

logger = get_logger(__name__)


def steam_request(appid: int):
    url = f"{config.STEAM_BASE_SEARCH_URL}/api/appdetails/"
    parameters = {"appids": appid}

    json_data = get_request(url, parameters=parameters)
    json_app_data = json_data[str(appid)]

    if json_app_data["success"]:
        data = json_app_data["data"]
        return data

    return None


def parse_game_data(data: dict):
    game_data = {
        "appid": data["steam_appid"],
        "name": data["name"],
        "type": data["type"],
        "required_age": data["required_age"],
        "is_free": data["is_free"],
        "controller_support": data.get("controller_support", None),
        "dlc": data.get("dlc", []),
        "detailed_description": data["detailed_description"],
        "short_description": data["short_description"],
        "about_the_game": data["about_the_game"],
        "supported_languages": data["supported_languages"],
        "reviews": data["reviews"],
        "header_image": data["header_image"],
        "capsule_image": data["capsule_image"],
        "website": data["website"],
        "pc_requirements": data["pc_requirements"],
        "mac_requirements": data["mac_requirements"],
        "linux_requirements": data["linux_requirements"],
        "developers": data["developers"],
        "publishers": data["publishers"],
        "platforms": data["platforms"],
        "metacritic": data["metacritic"]["score"],
        "categories": data["categories"],
        "genres": data["genres"],
        "recommendations": data["recommendations"]["total"],
        "achievements": data["achievements"]["total"],
        "release_date": data["release_date"],
    }

    return Game(**game_data)


if __name__ == "__main__":
    appid = 1172470
    data = steam_request(appid)
    game_data = parse_game_data(data)
    logger.info(pretty_repr(game_data))
