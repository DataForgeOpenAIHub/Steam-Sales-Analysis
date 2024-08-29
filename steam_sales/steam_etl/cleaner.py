import json
import warnings
from abc import ABC, abstractmethod
from ast import literal_eval

import dateparser
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from tqdm import tqdm

from steam_sales.steam_etl.crud import bulk_ingest_clean_data
from steam_sales.steam_etl.db import get_db
from steam_sales.steam_etl.settings import get_logger
from steam_sales.steam_etl.utils import get_sql_query
from steam_sales.steam_etl.validation import Clean, CleanList

warnings.filterwarnings("ignore")


class BaseCleaner(ABC):
    """
    Base class for common data cleaning methods.
    """

    def __init__(self):
        pass

    def fetch_data(self, source: str) -> pd.DataFrame:
        """
        Fetches data from the specified source and returns it as a pandas DataFrame.

        Parameters:
        - source (str): The source from which to fetch the data.

        Returns:
        - df (pd.DataFrame): The fetched data as a pandas DataFrame.
        """
        with get_db() as db:
            query = get_sql_query(source)
            result = db.execute(query)
            data = result.fetchall()
            columns = result.keys()

        df = pd.DataFrame(data, columns=columns)
        return df

    def process_null(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process null values in the given DataFrame by replacing specific values with None.

        Args:
            df (pd.DataFrame): The DataFrame to process.

        Returns:
            pd.DataFrame: The processed DataFrame with null values replaced.
        """
        convert_to_none = ["", " ", "None", "none", "null", "N/a", "n/a", "N/A", "NA", '["none"]', '["null"]', "{}"]
        df.replace(convert_to_none, None, inplace=True)
        return df

    def safe_literal_eval(self, val):
        """
        Safely evaluates a string representation of a Python literal.

        Args:
            val (str): The string representation of the Python literal.

        Returns:
            str: If the evaluation is successful and the result is a list, a semicolon-separated string of non-empty
            elements.
                 If the evaluation fails, an empty string is returned.
                 If the evaluation is successful and the result is not a list, the original value is returned.
        """
        try:
            result = literal_eval(val)
            if isinstance(result, list):
                return ";".join(filter(None, result))
        except (ValueError, SyntaxError):
            return ""
        return val

    def process_with_progress(self, df: pd.DataFrame, process_functions: list, df_name: str) -> pd.DataFrame:
        """
        Process the given DataFrame using a list of process functions and display a progress bar.

        Args:
            df (pd.DataFrame): The DataFrame to be processed.
            process_functions (list): A list of functions to be applied to the DataFrame.
            df_name (str): The name of the DataFrame.

        Returns:
            pd.DataFrame: The processed DataFrame.
        """
        for func in tqdm(process_functions, desc=f"Processing {df_name} DataFrame"):
            df = func(df)
        return df

    @abstractmethod
    def process(self):
        """
        This method is responsible for executing the cleaning process.
        It performs the necessary data cleaning operations on the dataset.

        This method is currently unimplemented.
        """
        pass

    @abstractmethod
    def run(self):
        """
        This method is responsible for executing the cleaning process.
        It performs the necessary data cleaning operations on the dataset.

        This method is currently unimplemented.
        """
        pass


class SteamSpyCleaner(BaseCleaner):
    """
    Class for cleaning SteamSpy data.
    """

    def __init__(self):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)

        self.col_to_drop = [
            "score_rank",  # too many missing values
            "userscore",  # too little variance (most have 0)
            "genre",
            "developer",
            "publisher",
            "price",
            "initialprice",
            "discount",  # provided by Steam data
            "average_2weeks",
            "median_2weeks",
            "ccu",  # not interested in temporally specific columns
        ]

    def process_col_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        df.dropna(subset=["name", "languages", "tags"], inplace=True)
        df.drop(columns=self.col_to_drop, inplace=True)
        return df

    def process_owners(self, df):
        """
        Process the 'owners' column in the given DataFrame.

        This function converts the 'owners' column values from a string format
        to a formatted range string. The original values are assumed to be in the
        format 'x .. y', where x and y are numbers representing the range of owners.

        Parameters:
        - df (pandas.DataFrame): The DataFrame containing the 'owners' column.

        Returns:
        - df (pandas.DataFrame): The DataFrame with the 'owners' column processed.

        Example:
        >>> df = pd.DataFrame({'owners': ['0 .. 1', '1 .. 10', '10 .. 100']})
        >>> processed_df = process_owners(df)
        >>> print(processed_df)
              owners
        0     0 - 1
        1    1 - 10
        2  10 - 100
        """

        df["owners"] = (
            df["owners"]
            .apply(lambda x: tuple(map(lambda x: int(x) / 1000000, x.replace(",", "").split(" .. "))))
            .apply(lambda x: f"{x[0]} - {x[1]}")
        )
        return df

    def rename(self, df):
        df.rename(
            columns={
                "tags": "steamspy_tags",
                "positive": "positive_ratings",
                "negative": "negative_ratings",
                "owners": "owners_in_millions",
            },
            inplace=True,
        )
        return df

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        process_functions = [self.process_null, self.process_col_rows, self.process_owners, self.rename]
        return self.process_with_progress(df, process_functions, "SteamSpy")

    def run(self):
        steamspy_df = self.fetch_data("get_new_steamspy_data.sql")
        # steamspy_df = self.fetch_data("get_all_steamspy_data.sql")
        self.logger.info(f"{steamspy_df.shape[0]} new records found")
        cleaned_steamspy_df = self.process(steamspy_df)
        cleaned_steamspy_df.drop(columns=["name"], inplace=True)
        self.logger.info(f"Clean steamspy data shape: {cleaned_steamspy_df.shape}")
        return cleaned_steamspy_df


class SteamStoreCleaner(BaseCleaner):
    """
    Class for cleaning Steam data.
    """

    def __init__(self):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)

        self.currency_rates = {"EUR": 1.08, "TWD": 0.03, "SGD": 0.74, "BRL": 0.18, "AUD": 0.67}

    def process_age(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the 'required_age' column in the given DataFrame by categorizing the age groups.

        Args:
            df (pd.DataFrame): The DataFrame containing the 'required_age' column.

        Returns:
            pd.DataFrame: The DataFrame with the 'required_age' column categorized.
        """
        cut_points = [-1, 0, 3, 7, 12, 16, 1000]
        categories = [0, 3, 7, 12, 16, 18]
        df = df[df["required_age"].notna()]
        df["required_age"] = pd.cut(df["required_age"], bins=cut_points, labels=categories)
        return df

    @staticmethod
    def parse_platforms(x):
        d = json.loads(x)
        return ";".join(platform for platform in d.keys() if d[platform])

    def process_platforms(self, df: pd.DataFrame) -> pd.DataFrame:
        df["platform"] = df["platform"].apply(self.parse_platforms)
        return df

    def process_language(self, df: pd.DataFrame) -> pd.DataFrame:
        df.dropna(subset=["supported_languages"], inplace=True)
        df["english"] = df["supported_languages"].apply(lambda x: 1 if "english" in x.lower() else 0)
        df.drop("supported_languages", axis=1, inplace=True)
        return df

    def process_developers_and_publishers(self, df: pd.DataFrame) -> pd.DataFrame:
        pattern = r'(?i)\["(n/a|na|null)"\]'
        df = df[
            (df["developers"].notna())
            & (df["publishers"].notna() & (df["publishers"] != '[""]') & (df["publishers"] != '[" "]'))
        ]
        df = df[~df["developers"].str.contains(pattern, na=False)]
        df = df[~df["publishers"].str.contains(pattern, na=False)]
        df = df[~df["developers"].str.contains(";", na=False)]
        df = df[~df["publishers"].str.contains(";", na=False)]
        df["developer"] = df["developers"].apply(self.safe_literal_eval)
        df["publisher"] = df["publishers"].apply(self.safe_literal_eval)
        df.drop(columns=["developers", "publishers"], inplace=True)
        return df

    @staticmethod
    def parse_price(x):
        if x is not None:
            return literal_eval(x)
        else:
            return {"currency": "USD", "initial": -1}

    @staticmethod
    def convert_to_usd(price, currency, rates):
        if currency == "USD":
            return price
        currency_rate = rates[currency]
        return price * currency_rate

    def process_price(self, df: pd.DataFrame) -> pd.DataFrame:
        df["price_overview"] = df["price_overview"].apply(self.parse_price)
        df["currency"] = df["price_overview"].apply(lambda x: x["currency"])
        df["price"] = df["price_overview"].apply(lambda x: x["initial"])
        df.loc[df["is_free"] == 1, "price"] = 0
        df.loc[df["price"] > 0, "price"] /= 100
        df["price"] = df.apply(lambda x: self.convert_to_usd(x["price"], x["currency"], self.currency_rates), axis=1)
        df.drop(columns=["is_free", "currency", "price_overview"], inplace=True)
        return df

    @staticmethod
    def translate(text):
        try:
            lang = GoogleTranslator(source="auto", target="en").translate(text)
            return lang
        except Exception:
            return text

    def process_categories_and_genres(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[(df["categories"].notna()) & (df["genres"].notna())]
        for col in ["categories", "genres"]:
            df[col] = df[col].apply(lambda x: ";".join(item["description"] for item in literal_eval(x)))
        df.loc[df["english"] == 0, "genres"] = df.loc[df["english"] == 0, "genres"].apply(self.translate)
        df.loc[df["english"] == 0, "categories"] = df.loc[df["english"] == 0, "categories"].apply(self.translate)
        return df

    def process_controller(self, df: pd.DataFrame) -> pd.DataFrame:
        df["controller_support"] = df["controller_support"].apply(lambda x: 1 if x == "full" else 0)
        return df

    @staticmethod
    def parse_list(x):
        lst = literal_eval(x)
        return len(lst)

    def process_dlc(self, df: pd.DataFrame) -> pd.DataFrame:
        df["dlc"] = df["dlc"].apply(self.parse_list)
        return df

    def process_requirement(self, df: pd.DataFrame) -> pd.DataFrame:
        df["requirements"] = df["requirements"].apply(
            lambda x: BeautifulSoup(x, "lxml").get_text() if x else "Not available"
        )
        return df

    @staticmethod
    def parse_date(date_string):
        if isinstance(date_string, str):
            try:
                date_obj = dateparser.parse(date_string)
                return pd.to_datetime(date_obj)
            except:
                date_str = date_string.replace(" ", "")
                date_str = dateparser.parse(date_str)
                return pd.to_datetime(date_str)
        return pd.NaT

    def process_date(self, df: pd.DataFrame) -> pd.DataFrame:
        df["release_date"] = df["release_date"].apply(self.parse_date)
        return df

    def process_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        # Fill missing values in the specified columns
        df["detailed_description"] = df["detailed_description"].fillna("")
        df["about_the_game"] = df["about_the_game"].fillna("")
        df["short_description"] = df["short_description"].fillna("")
        df["website"] = df["website"].fillna("Not available")
        df["header_image"] = df["header_image"].fillna("Not available")

        # Concatenate the columns into the 'description' column using f-strings
        df["description"] = df.apply(
            lambda row: (
                f"{row['detailed_description']} {row['about_the_game']} {row['short_description']}"
                # f"Website: {row['website']} Game Image: {row['header_image']}"
            ),
            axis=1,
        ).replace("", "Not available")

        df.drop(
            columns=["detailed_description", "about_the_game", "short_description"],  # , "website", "header_image"],
            inplace=True,
        )
        return df

    def misc(self, df: pd.DataFrame) -> pd.DataFrame:
        col_to_drop = ["capsule_image", "reviews"]
        df["year"] = df["release_date"].dt.year.astype("Int16")
        df["month"] = df["release_date"].dt.month.astype("Int16")
        df["day"] = df["release_date"].dt.day.astype("Int16")
        df.drop(columns=col_to_drop, inplace=True)
        return df

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        process_functions = [
            self.process_null,
            self.process_age,
            self.process_platforms,
            self.process_language,
            self.process_developers_and_publishers,
            self.process_price,
            self.process_categories_and_genres,
            self.process_controller,
            self.process_dlc,
            self.process_requirement,
            self.process_date,
            self.process_descriptions,
            self.misc,
        ]
        return self.process_with_progress(df, process_functions, "Steam Store")

    def run(self):
        steam_df = self.fetch_data("get_new_steam_data.sql")
        # steam_df = self.fetch_data("get_all_steam_data.sql")
        self.logger.info(f"{steam_df.shape[0]} new records found")
        cleaned_steam_df = self.process(steam_df)
        self.logger.info(f"Clean steam data shape: {cleaned_steam_df.shape}")
        return cleaned_steam_df


class SteamDataClean:
    def __init__(self, batch_size: int = 1000):

        self.batch_size = batch_size
        self.logger = get_logger(self.__class__.__name__)

    def merge(self):
        steamspy_cleaner = SteamSpyCleaner()
        steam_cleaner = SteamStoreCleaner()

        steamspy_df = steamspy_cleaner.run()
        steam_df = steam_cleaner.run()

        merged_df = pd.merge(steamspy_df, steam_df, on="appid")
        self.logger.info(f"Merged data shape: {merged_df.shape}")
        return merged_df

    def ingest(self):
        merged_df = self.merge()

        merged_df = np.array_split(merged_df, len(merged_df) // self.batch_size + 1)

        with get_db() as db:
            for chunk in tqdm(merged_df, desc="Batch progress"):
                bulk_data = CleanList(games=[])
                for i in range(chunk.shape[0]):
                    data = chunk.iloc[i].to_dict()
                    bulk_data.games.append(Clean(**data))

                bulk_ingest_clean_data(bulk_data, db)

        self.logger.info("Game data has been written to the database.")


if __name__ == "__main__":
    cleaner = SteamDataClean()
    cleaner.ingest()
