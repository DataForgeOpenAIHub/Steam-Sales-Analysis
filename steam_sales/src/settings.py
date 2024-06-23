import logging
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.logging import RichHandler
from pprint import pprint


class Path:
    curr_file_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(curr_file_dir)
    root_dir = os.path.dirname(package_dir)

    env_file = os.path.join(root_dir, ".env")
    data_dir = os.path.join(root_dir, "data")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.env_file, extra="ignore", env_file_encoding="utf-8")

    # Database configuration
    MYSQL_USERNAME: str = Field()
    MYSQL_PASSWORD: str = Field()
    MYSQL_HOST: str = Field()
    MYSQL_PORT: str = Field()
    MYSQL_DB_NAME: str = Field()

    STEAMSPY_BASE_URL: str = "https://steamspy.com/api.php"
    STEAM_BASE_SEARCH_URL: str = "http://store.steampowered.com"


def get_logger(name):
    # Create a logger
    logger = logging.getLogger(name)

    # Set the logging level (adjust as needed)
    logger.setLevel(logging.DEBUG)

    # Create a console handler and set the level
    ch = RichHandler()
    ch.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)
    return logger


def get_settings():
    return Settings()


config = get_settings()

# pprint(Path.__dict__)
# pprint(config.model_dump())
