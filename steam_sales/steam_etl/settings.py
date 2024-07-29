import logging
import logging.handlers
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.logging import RichHandler


class Path:
    curr_file_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(curr_file_dir)
    root_dir = os.path.dirname(package_dir)

    env_file = os.path.join(root_dir, ".env")
    sql_queries = os.path.join(curr_file_dir, "sql")
    log_file = os.path.join(root_dir, "logs")

    if not os.path.exists(log_file):
        os.mkdir(log_file)


class Settings(BaseSettings):
    if os.path.exists(Path.env_file):
        model_config = SettingsConfigDict(env_file=Path.env_file, extra="ignore", env_file_encoding="utf-8")
    else:
        model_config = SettingsConfigDict(extra="ignore")

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
    ch = RichHandler(rich_tracebacks=True)
    ch.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter("'%(name)s' - %(message)s")
    ch.setFormatter(formatter)

    # Create a file handler and set the level
    fh = logging.handlers.RotatingFileHandler(
        os.path.join(Path.log_file, "steam-data.log"), maxBytes=5 * 1024 * 1024, backupCount=3
    )
    fh.setLevel(logging.ERROR)

    # Create a formatter and add it to both handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


def get_settings():
    return Settings()


config = get_settings()

# from pprint import pprint

# pprint(Path.__dict__)
# pprint(config.model_dump())
