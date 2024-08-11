import os
import re
from functools import wraps

from sqlalchemy import text

from steam_sales.steam_etl.crud import log_last_run_time
from steam_sales.steam_etl.db import get_db
from steam_sales.steam_etl.settings import Path, config
from steam_sales.steam_etl.validation import LastRun


def print_steam_links(df):
    """
    Prints the Steam links for each game in the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing game information.

    Returns:
        None
    """
    url_base = f"{config.STEAM_BASE_SEARCH_URL}/app/"

    for _, row in df.iterrows():
        appid = row["appid"]
        name = row["name"]

        print(name + ":", url_base + str(appid))


def check_na(df, column):
    """
    Checks the number of values in a specified column of a DataFrame that match the pattern 'n/a', 'na', or 'null'.

    Args:
        df (pandas.DataFrame): The DataFrame to check.
        column (str): The name of the column to check.

    Returns:
        pandas.DataFrame: A DataFrame containing the rows where the specified column has a value matching the pattern.

    """
    pattern = re.compile(r"(?i)\b(n/a|na|null)\b")

    def is_na_like(value):
        return bool(pattern.fullmatch(str(value).strip()))

    count = df[column].apply(is_na_like).sum()

    print(f'The number of values like "n/a" in column "{column}" is: {count}')
    filtered_rows = df[df[column].apply(is_na_like)]

    return filtered_rows


def get_sql_query(file_name: str):
    """
    Retrieves an SQL query from a file.

    Args:
        file_name (str): The name of the file containing the SQL query.

    Returns:
        sqlalchemy.sql.text.TextClause: The SQL query as a SQLAlchemy TextClause object.
    """
    with open(os.path.join(Path.sql_queries, file_name), "r") as f:
        query = text(f.read())
    return query


def log_last_run(scraper_name):
    """
    Decorator function that logs the last run time of a function.
    Args:
        scraper_name (str): The name of the scraper.
    Returns:
        function: The decorated function.
    Example:
        @log_last_run("my_scraper")
        def scrape_data():
            # Function implementation
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            with get_db() as db:
                last_run = LastRun(scraper=scraper_name)
                log_last_run_time(last_run, db)

            return result

        return wrapper

    return decorator
