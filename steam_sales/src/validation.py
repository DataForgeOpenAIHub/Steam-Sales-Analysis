from datetime import datetime
from typing import Dict, List, Optional

from dateutil import parser
from pydantic import BaseModel, Field, HttpUrl, field_validator


# Game ID Details
class GameMetaData(BaseModel):
    appid: int = Field(..., description="The application ID")
    name: str = Field(..., max_length=255, description="The name of the game")


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
class PCRequirements(BaseModel):
    minimum: Optional[Dict] = Field(..., description="")
    recommended: Optional[Dict] = Field(..., description="")


class Game(BaseModel):
    type: str = Field(..., description="Type of the game")
    name: str = Field(..., description="Name of the game")
    appid: int = Field(..., description="Application ID of the game")
    required_age: Optional[int | str] = Field(..., description="Minimum required age to play the game.")
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
    pc_requirements: PCRequirements = Field(..., description="PC system requirements for the game")
    developers: Optional[List[str]] = Field(default=[], description="List of developers who worked on the game")
    publishers: List[str] = Field(..., description="List of publishers responsible for distributing the game")
    pc_platform: bool = Field(..., description="Indicates if the game is available on PC platforms")
    metacritic: Optional[int] = Field(..., description="Metacritic score of the game, if available")
    categories: Optional[list] = Field(default=[], description="Categories or genres of the game")
    genres: Optional[list] = Field(default=[], description="Genres the game belongs to")
    recommendations: int = Field(..., description="Number of recommendations from Steam users")
    achievements: int = Field(..., description="Total number of attainable achievements")
    release_date: Optional[datetime] = Field(..., description="Date when the game was released")
    coming_soon: bool = Field(..., description="Indicates if the game release is upcoming")

    @field_validator("release_date", mode="before")
    def validate_release_date(cls, v):
        if isinstance(v, str):
            try:
                parsed_date = parser.parse(v)
                return parsed_date
            except ValueError as e:
                print(f"Error parsing date '{v}': {e}")
                return None

        if v is not None and not isinstance(v, str):
            raise ValueError("date must be a string or an integer")

        return v


class GameList(BaseModel):
    games: List[Game] = Field(..., description="The list of Steam games")
