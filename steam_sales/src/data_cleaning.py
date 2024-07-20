import json
import os
import warnings
from ast import literal_eval

import dateparser
import numpy as np
import pandas as pd
import tqdm
from bs4 import BeautifulSoup
from crud import bulk_ingest_clean_data
from db import get_db
from settings import Path, get_logger
from sqlalchemy import text
from validation import Clean, CleanList

warnings.filterwarnings("ignore")

logger = get_logger(__file__)


# class CleanerBase:
def fetch_data(source: str):
    """
    Fetches data from a specified source and returns it as a pandas DataFrame.

    Parameters:
    source (str): The name of the source file containing the SQL query.

    Returns:
    pandas.DataFrame: The fetched data as a DataFrame.

    """
    db = get_db()

    with open(os.path.join(Path.sql_queries, source), "r") as f:
        query = text(f.read())

    result = db.execute(query)
    data = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(data, columns=columns)

    db.close()

    return df


def process_null(df):
    """
    Process null values in a DataFrame by replacing specific values with None.

    Args:
        df (pandas.DataFrame): The DataFrame to process.

    Returns:
        pandas.DataFrame: The processed DataFrame with null values replaced.

    """
    df = df.copy()

    convert_to_none = ["", " ", "None", "none", "null", "N/a", "n/a", "N/A", "NA", '["none"]', '["null"]', "{}"]
    df.replace(convert_to_none, None, inplace=True)

    return df


def process_age(df):
    """
    Process the 'required_age' column in the given DataFrame.

    Parameters:
    df (DataFrame): The input DataFrame containing the 'required_age' column.

    Returns:
    DataFrame: A copy of the input DataFrame with the 'required_age' column processed.

    """
    df = df.copy()
    cut_points = [-1, 0, 3, 7, 12, 16, 1000]
    categories = [0, 3, 7, 12, 16, 18]

    df = df[df["required_age"].notna()]
    df["required_age"] = pd.cut(df["required_age"], bins=cut_points, labels=categories)

    return df


def process_platforms(df):
    """
    Process the platforms column in the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the platforms column.

    Returns:
        pandas.DataFrame: The DataFrame with the platforms column processed.
    """
    df = df.copy()

    def parse_platforms(x):
        """
        Parse the platforms from the given JSON string.

        Args:
            x (str): The JSON string representing the platforms.

        Returns:
            str: The parsed platforms separated by semicolons.
        """
        d = json.loads(x)

        return ";".join(platform for platform in d.keys() if d[platform])

    df["platform"] = df["platform"].apply(parse_platforms)

    return df


def process_language(df):
    """
    Process the language data in the given DataFrame.

    Parameters:
    df (DataFrame): The input DataFrame containing the language data.

    Returns:
    DataFrame: The processed DataFrame with the language data cleaned.

    """
    df = df.copy()

    df = df.dropna(subset=["supported_languages"])

    df["english"] = df["supported_languages"].apply(lambda x: 1 if "english" in x.lower() else 0)
    df = df.drop("supported_languages", axis=1)

    return df


def process_developers_and_publishers(df):
    """
    Process the developers and publishers columns in the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the developers and publishers columns.

    Returns:
        pandas.DataFrame: The processed DataFrame with the developers and publishers columns transformed.

    """
    pattern = r'(?i)\["(n/a|na|null)"\]'

    df = df[
        (df["developers"].notna())
        & (df["publishers"].notna() & (df["publishers"] != '[""]') & (df["publishers"] != '[" "]'))
    ]
    df = df[~df["developers"].str.contains(pattern, na=False)]
    df = df[~df["publishers"].str.contains(pattern, na=False)]

    df = df[~df["developers"].str.contains(";", na=False)]
    df = df[~df["publishers"].str.contains(";", na=False)]

    def safe_literal_eval(val):
        try:
            result = literal_eval(val)
            if isinstance(result, list):
                return ";".join(filter(None, result))
        except (ValueError, SyntaxError):
            return ""

        return val

    df["developer"] = df["developers"].apply(safe_literal_eval)
    df["publisher"] = df["publishers"].apply(safe_literal_eval)

    df = df.drop(["developers", "publishers"], axis=1)

    return df


def process_price(df):
    """
    Process the price data in the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the price data.

    Returns:
        pandas.DataFrame: The DataFrame with processed price data.
    """
    df = df.copy()
    currency_rates = {"EUR": 1.08, "TWD": 0.03, "SGD": 0.74, "BRL": 0.18, "AUD": 0.67}

    def parse_price(x):
        """
        Parses the price information from a string representation.

        Parameters:
        x (str): The string representation of the price.

        Returns:
        dict: A dictionary containing the parsed price information. The dictionary has two keys:
              - 'currency': The currency of the price.
              - 'initial': The initial price value.
        """
        if x is not None:
            return literal_eval(x)
        else:
            return {"currency": "USD", "initial": -1}

    def convert_to_usd(price, currency, rates):
        """
        Converts the given price from the specified currency to USD using the provided exchange rates.

        Parameters:
        price (float): The price to be converted.
        currency (str): The currency of the price.
        rates (dict): A dictionary containing exchange rates for different currencies.

        Returns:
        float: The converted price in USD.
        """
        if currency == "USD":
            return price

        currency_rate = rates[currency]
        return price * currency_rate

    df["price_overview"] = df["price_overview"].apply(parse_price)

    df["currency"] = df["price_overview"].apply(lambda x: x["currency"])
    df["price"] = df["price_overview"].apply(lambda x: x["initial"])

    df.loc[df["is_free"] == 1, "price"] = 0
    df.loc[df["price"] > 0, "price"] /= 100

    df["price"] = df.apply(lambda x: convert_to_usd(x["price"], x["currency"], currency_rates), axis=1)

    df = df.drop(["is_free", "currency", "price_overview"], axis=1)

    return df


def process_categories_and_genres(df):
    """
    Process the categories and genres columns of the given DataFrame.

    Parameters:
    df (DataFrame): The input DataFrame containing the 'categories' and 'genres' columns.

    Returns:
    DataFrame: The processed DataFrame with the 'categories' and 'genres' columns modified.
    """
    df = df.copy()
    df = df[(df["categories"].notna()) & (df["genres"].notna())]

    for col in ["categories", "genres"]:
        df[col] = df[col].apply(lambda x: ";".join(item["description"] for item in literal_eval(x)))

    return df


def process_controller(df):
    """
    Process the controller support column in the given DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the controller support column.

    Returns:
    pandas.DataFrame: The DataFrame with the controller support column processed.
    """
    df = df.copy()
    df["controller_support"] = df["controller_support"].apply(lambda x: 1 if x == "full" else 0)

    return df


def process_dlc(df):
    """
    Process the 'dlc' column in the given DataFrame by converting the values to the number of DLCs available for each
    game.

    Args:
        df (DataFrame): The input DataFrame containing the 'dlc' column.

    Returns:
        DataFrame: A copy of the input DataFrame with the 'dlc' column transformed to the number of DLCs.

    """
    df = df.copy()

    def parse_list(x):
        """
        Parses a string representation of a list and returns the length of the list.

        Parameters:
        x (str): A string representation of a list.

        Returns:
        int: The length of the list.

        """
        lst = literal_eval(x)
        return len(lst)

    df["dlc"] = df["dlc"].apply(parse_list)

    return df


def process_requirement(df):
    """
    Process the requirements column of the given DataFrame.

    Parameters:
    df (DataFrame): The input DataFrame containing the requirements column.

    Returns:
    DataFrame: A copy of the input DataFrame with the requirements column processed.

    """
    df = df.copy()
    df["requirements"] = df["requirements"].apply(
        lambda x: BeautifulSoup(x, "lxml").get_text() if x else "Not available"
    )

    return df


def process_date(df):
    """
    Process the release date column in the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the release date column.

    Returns:
        pandas.DataFrame: The DataFrame with the release date column processed.

    """
    df = df.copy()

    def parse_date(date_string):
        """
        Parses a date string and returns a pandas datetime object.

        Parameters:
        date_string (str): The date string to be parsed.

        Returns:
        pd.Timestamp: A pandas datetime object representing the parsed date.

        """
        if isinstance(date_string, str):
            try:
                date_obj = dateparser.parse(date_string)
                return pd.to_datetime(date_obj)

            except:
                date_str = date_string.replace(" ", "")
                date_str = dateparser.parse(date_str)

                return pd.to_datetime(date_str)

        return pd.NaT

    df["release_date"] = df["release_date"].apply(parse_date)

    return df


def process_descriptions(df):
    """
    Process the descriptions of a DataFrame by combining multiple columns and performing some cleaning.

    Args:
        df (pandas.DataFrame): The DataFrame containing the columns to be processed.

    Returns:
        pandas.DataFrame: The processed DataFrame with unnecessary columns dropped.
    """
    df = df.copy()

    df["description"] = (
        df["detailed_description"].fillna("")
        + " "
        + df["about_the_game"].fillna("")
        + " "
        + df["short_description"].fillna("")
        + " Website: "
        + df["website"].fillna("Not available")
        + " Game Image: "
        + df["header_image"].fillna("Not available")
    )
    df["description"] = df["description"].replace("", "Not available")
    df = df.drop(["detailed_description", "about_the_game", "short_description", "website", "header_image"], axis=1)

    return df


def misc(df):
    """
    Perform miscellaneous data cleaning operations on the given DataFrame.

    Parameters:
    df (pandas.DataFrame): The input DataFrame to be cleaned.

    Returns:
    pandas.DataFrame: The cleaned DataFrame.
    """
    df = df.copy()
    col_to_drop = ["capsule_image", "reviews", "type"]

    df["year"] = df["release_date"].dt.year.astype("Int16")
    df["month"] = df["release_date"].dt.month.astype("Int16")
    df["day"] = df["release_date"].dt.day.astype("Int16")

    df = df.drop(col_to_drop, axis=1)

    return df


def process_col_rows(df):
    """
    Process the given DataFrame by dropping unnecessary columns and rows.

    Args:
        df (pandas.DataFrame): The DataFrame to be processed.

    Returns:
        pandas.DataFrame: The processed DataFrame.
    """
    df = df.copy()
    col_to_drop = [
        "score_rank",
        "userscore",
        "genre",
        "developer",
        "publisher",
        "price",
        "initialprice",
        "discount",
        "average_2weeks",
        "median_2weeks",
        "ccu",
    ]

    # Drop missing games
    df = df.dropna(subset=["name"])
    df = df.drop(col_to_drop, axis=1)

    return df


def process_owners(df):
    """
    Process the 'owners' column in the given DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the 'owners' column.

    Returns:
    pandas.DataFrame: The DataFrame with the 'owners' column processed.

    """
    df = df.copy()
    df["owners"] = (
        df["owners"]
        .apply(lambda x: tuple(map(lambda x: int(x) / 1000000, x.replace(",", "").split(" .. "))))
        .apply(lambda x: f"{x[0]} - {x[1]}")
    )

    return df


def process_tag_lang(df):
    """
    Process the dataframe by dropping rows with missing values in the 'languages' and 'tags' columns.

    Args:
        df (pandas.DataFrame): The input dataframe.

    Returns:
        pandas.DataFrame: The processed dataframe with missing values dropped.

    """
    df = df.copy()
    df = df.dropna(subset=["languages", "tags"])

    return df


def rename(df):
    """
    Renames the columns of the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame to be renamed.

    Returns:
        pandas.DataFrame: The renamed DataFrame.
    """
    df = df.copy()
    df = df.rename(
        {
            "tags": "steamspy_tags",
            "positive": "positive_ratings",
            "negative": "negative_ratings",
            "owners": "owners_in_millions",
        },
        axis=1,
    )

    return df


def process_with_progress(df, process_functions, df_name):
    """
    Process the DataFrame with the given list of functions, showing progress.

    Args:
        df (pandas.DataFrame): The DataFrame to be processed.
        process_functions (list): A list of functions to apply to the DataFrame.
        df_name (str): The name of the DataFrame being processed.

    Returns:
        pandas.DataFrame: The processed DataFrame.
    """
    for func in tqdm.tqdm(process_functions, desc=f"Processing {df_name} DataFrame"):
        df = func(df)

    return df


def process_steamspy(df):
    """
    Process the given DataFrame by applying a series of cleaning operations.

    Args:
        df (pandas.DataFrame): The DataFrame to be processed.

    Returns:
        pandas.DataFrame: The processed DataFrame.
    """
    process_functions = [process_null, process_col_rows, process_owners, process_tag_lang, rename]

    return process_with_progress(df, process_functions, "SteamSpy")


def process_steam(df):
    """
    Process the given DataFrame by applying a series of cleaning operations.

    Args:
        df (pandas.DataFrame): The DataFrame to be processed.

    Returns:
        pandas.DataFrame: The processed DataFrame.
    """
    process_functions = [
        process_null,
        process_age,
        process_platforms,
        process_language,
        process_developers_and_publishers,
        process_price,
        process_categories_and_genres,
        process_controller,
        process_dlc,
        process_requirement,
        process_date,
        process_descriptions,
        misc,
    ]

    return process_with_progress(df, process_functions, "Steam")


def main():
    steam_data = fetch_data("get_new_steam_data.sql")
    steamspy_data = fetch_data("get_new_steamspy_data.sql")
    # steam_data = fetch_data("get_all_steam_data.sql")
    # steamspy_data = fetch_data("get_all_steamspy_data.sql")
    logger.info(
        f"{steam_data.shape[0]} new data found in Steam table and {steamspy_data.shape[0]} new data found in SteamSpy "
        "table"
    )

    clean_steam_data = process_steam(steam_data)
    clean_steamspy_data = process_steamspy(steamspy_data)

    logger.info(f"Clean steam data shape: {clean_steam_data.shape}")
    logger.info(f"Clean steamspy data shape: {clean_steamspy_data.shape}")

    clean_steamspy_data_filtered = clean_steamspy_data.drop(columns=["name"])
    clean_game_df = pd.merge(clean_steam_data, clean_steamspy_data_filtered, on="appid")
    logger.info(f"Clean game data shape: {clean_game_df.shape}")

    db = get_db()

    batch_size = 1000
    clean_game_df_chunks = np.array_split(clean_game_df, len(clean_game_df) // batch_size + 1)

    for chunk in tqdm.tqdm(clean_game_df_chunks, desc="Batch progress"):
        bulk_data = CleanList(games=[])
        for i in range(chunk.shape[0]):
            data = chunk.iloc[i].to_dict()
            bulk_data.games.append(Clean(**data))

        bulk_ingest_clean_data(bulk_data, db)

    logger.info("Game data has been written to the database.")

    db.close()


if __name__ == "__main__":
    main()
