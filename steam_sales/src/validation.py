from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, HttpUrl

from datetime import datetime


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
    games: List[GameDetails] = Field(..., description="The list of games")


# # Steam Game Details
# class PCRequirements(BaseModel):
#     os: str
#     processor: str
#     memory: str
#     graphics: str
#     directx: str = Field(None, alias="DirectX")
#     storage: str
#     sound_card: str = Field(None, alias="Sound Card")


class PCRequirements(BaseModel):
    minimum: Optional[str]
    recommended: Optional[str]


class ReleaseDate(BaseModel):
    coming_soon: bool
    date: Optional[datetime]

    @field_validator("date", mode="before")
    def validate_release_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%b %d, %Y")
        if v is not None and not isinstance(v, str):
            raise ValueError("date must be a string or an integer")
        return v


class Game(BaseModel):
    type: str
    name: str
    appid: int
    required_age: int
    is_free: bool
    controller_support: Optional[str]
    dlc: Optional[List[int]]
    detailed_description: str
    about_the_game: str
    short_description: str
    supported_languages: str
    header_image: HttpUrl
    capsule_image: HttpUrl
    website: HttpUrl
    pc_requirements: PCRequirements
    mac_requirements: PCRequirements = None
    linux_requirements: PCRequirements = None
    developers: List[str]
    publishers: List[str]
    platforms: Dict[str, bool]
    metacritic: int
    categories: list
    genres: list
    recommendations: int
    achievements: int
    release_date: ReleaseDate
