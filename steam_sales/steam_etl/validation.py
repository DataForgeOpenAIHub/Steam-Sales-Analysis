import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, HttpUrl, field_validator

from steam_sales.steam_etl.settings import get_logger

logger = get_logger(__file__)


# Game ID Details
def get_current_utc_time():
    return datetime.now(timezone.utc)


class GameMetaData(BaseModel):
    appid: int = Field(..., description="The application ID")
    name: str = Field(..., max_length=255, description="The name of the game")
    date_added: Optional[datetime] = Field(
        ..., default_factory=get_current_utc_time, description="Date the appid was added"
    )
    dne: Optional[bool] = Field(False, description="Flag App ID does not exist in database")


class GameMetaDataList(BaseModel):
    games: List[GameMetaData] = Field(..., description="The list of games")


# SteamSpy Game Details
class GameDetails(BaseModel):
    appid: int = Field(..., description="The application ID")
    name: str = Field(..., max_length=255, description="The name of the game")
    developer: str = Field(..., max_length=255, description="The developer of the game")
    publisher: str = Field(..., max_length=255, description="The publisher of the game")
    score_rank: str = Field("", max_length=255, description="The score rank of the game")
    positive: int = Field(..., description="The number of positive reviews")
    negative: int = Field(..., description="The number of negative reviews")
    userscore: float = Field(..., description="The user score of the game")
    owners: str = Field(..., description="The range of owners of the game")
    average_forever: int = Field(..., description="The average playtime forever in minutes")
    average_2weeks: int = Field(..., description="The average playtime in the last 2 weeks in minutes")
    median_forever: int = Field(..., description="The median playtime forever in minutes")
    median_2weeks: int = Field(..., description="The median playtime in the last 2 weeks in minutes")
    price: Optional[int] = Field(None, description="The current price of the game in cents")
    initialprice: Optional[int] = Field(None, description="The initial price of the game in cents")
    discount: Optional[str] = Field(None, max_length=255, description="The discount on the game")
    ccu: int = Field(..., description="The current concurrent users")
    languages: Optional[str] = Field(None, description="The supported languages")
    genre: str = Field(..., description="The genre of the game")
    tags: Optional[Dict[str, int]] = Field(None, description="The tags associated with the game")

    @field_validator("tags", mode="before")
    def validate_tags(cls, v):
        if v == []:
            return None

        if v is not None and not isinstance(v, dict):
            raise ValueError("tags must be a dictionary or None")

        return v

    @field_validator("score_rank", mode="before")
    def validate_score_rank(cls, v):
        if isinstance(v, int):
            return str(v)

        if v is not None and not isinstance(v, str):
            raise ValueError("score_rank must be a string or an integer")

        return v


class GameDetailsList(BaseModel):
    games: List[GameDetails] = Field(..., description="The list of SteamSpy games")


# Steam Game Details
class Game(BaseModel):
    type: str = Field(..., description="Type of the game")
    name: str = Field(..., description="Name of the game")
    appid: int = Field(..., description="Application ID of the game")
    required_age: Optional[Union[int, str]] = Field(..., description="Minimum required age to play the game.")
    is_free: bool = Field(..., description="Indicates if the game is free to play")
    controller_support: Optional[str] = Field(..., description="Type of controller support for the game, if available")
    dlc: Optional[List[int]] = Field(
        ..., description="List of downloadable content IDs associated with the game, if any"
    )
    detailed_description: Optional[str] = Field(default=None, description="Detailed description of the game")
    about_the_game: Optional[str] = Field(default=None, description="Brief description about the game")
    short_description: Optional[str] = Field(default=None, description="Short description of the game")
    supported_languages: Optional[str] = Field(default=None, description="Languages supported by the game")
    reviews: Optional[str] = Field(..., description="Reviews or critical acclaim summary of the game")
    header_image: HttpUrl = Field(..., description="URL to the header image of the game")
    capsule_image: HttpUrl = Field(..., description="URL to the capsule (thumbnail) image of the game")
    website: Optional[HttpUrl | str] = Field(..., description="Official website of the game")
    requirements: Optional[Dict] = Field(..., description="PC system requirements for the game")
    developers: Optional[List[str]] = Field(default=[], description="List of developers who worked on the game")
    publishers: List[str] = Field(..., description="List of publishers responsible for distributing the game")
    price_overview: Optional[Dict] = Field(..., description="Price overview of the game with currency")
    platform: Optional[dict] = Field(..., description="Indicates if the game is available on PC platforms")
    metacritic: Optional[int] = Field(..., description="Metacritic score of the game, if available")
    categories: Optional[list] = Field(default=[], description="Categories or genres of the game")
    genres: Optional[list] = Field(default=[], description="Genres the game belongs to")
    recommendations: int = Field(..., description="Number of recommendations from Steam users")
    achievements: int = Field(..., description="Total number of attainable achievements")
    release_date: Optional[str] = Field(..., description="Date when the game was released")
    coming_soon: bool = Field(..., description="Indicates if the game release is upcoming")

    @field_validator("required_age", mode="before")
    def validate_required_age(cls, v):
        if isinstance(v, str):
            match = re.search(r"\d+", v)
            if match:
                v = int(match.group())
            else:
                raise ValueError(f"Invalid value for required_age: {v}")

        elif not isinstance(v, int):
            raise ValueError(f"Invalid value type for required_age: {type(v)}")

        return v

    @field_validator("requirements", mode="before")
    def validate_requirements(cls, v):
        if isinstance(v, list):
            return {}
        else:
            return v


class GameList(BaseModel):
    games: List[Game] = Field(..., description="The list of Steam games")

    def get_num_games(self):
        return len(self.games)


# # Clean Data Details
class Clean(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the game")
    appid: int = Field(..., description="Application ID of the game")
    required_age: int = Field(..., description="Minimum required age to play the game.")
    controller_support: int = Field(..., description="Type of controller support for the game, if available")
    dlc: int = Field(..., description="List of downloadable content IDs associated with the game, if any")
    requirements: str = Field(..., description="PC system requirements for the game")
    platform: str = Field(..., description="Indicates if the game is available on PC platforms")
    metacritic: int = Field(..., description="Metacritic score of the game, if available")
    categories: str = Field(..., description="Categories or genres of the game")
    genres: str = Field(..., description="Genres the game belongs to")
    recommendations: int = Field(..., description="Number of recommendations from Steam users")
    achievements: int = Field(..., description="Total number of attainable achievements")
    release_date: Optional[datetime] = Field(None, description="Date when the game was released")
    coming_soon: int = Field(..., description="Indicates if the game release is upcoming")
    english: int = Field(..., description="Indicates if the game supports English language")
    developer: str = Field(..., description="Developer of the game")
    publisher: str = Field(..., description="Publisher of the game")
    price: float = Field(..., description="Current price of the game")
    description: str = Field(..., description="Description of the game")
    website: Optional[HttpUrl | str] = Field(..., description="Official website of the game")
    header_image: HttpUrl = Field(..., description="URL to the header image of the game")
    year: Optional[int] = Field(None, description="Year of the game release")
    month: Optional[int] = Field(None, description="Month of the game release")
    day: Optional[int] = Field(None, description="Day of the game release")
    positive_ratings: int = Field(..., description="Number of positive ratings")
    negative_ratings: int = Field(..., description="Number of negative ratings")
    owners_in_millions: str = Field(..., description="Number of owners in millions")
    average_forever: int = Field(..., description="Average playtime forever in minutes")
    median_forever: int = Field(..., description="Median playtime forever in minutes")
    languages: str = Field(..., description="Supported languages")
    steamspy_tags: Dict[str, int] = Field(..., description="Tags associated with the game")

    @field_validator("steamspy_tags", mode="before")
    def validate_steamspy_tags(cls, v):
        if isinstance(v, str):
            v = eval(v)

        return v

    @field_validator("release_date", mode="before")
    def validate_release_date(cls, v):
        if pd.isna(v):
            return None
        elif isinstance(v, datetime):
            return v
        else:
            return None

    @field_validator("day", "month", "year", mode="before")
    def validate_release_date_components(cls, v):
        if isinstance(v, int):
            return v
        else:
            return None


class CleanList(BaseModel):
    games: List[Clean] = Field(..., description="The list of Steam games")


class LastRun(BaseModel):
    scraper: str = Field(..., description="Script executed")
    last_run: Optional[datetime] = Field(default_factory=get_current_utc_time, description="Last run time")

    @field_validator("scraper", mode="before")
    def validate_scraper(cls, v):
        allowed = ["meta", "steamspy", "steam", "cleaner"]
        if isinstance(v, str):
            if v in allowed:
                return v.lower()

        raise ValueError(f"Invalid value for scraper: {v}. Allowed types are {allowed}")
