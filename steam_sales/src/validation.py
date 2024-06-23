from pydantic import BaseModel, Field
from typing import Dict, List


class GameMetaData(BaseModel):
    appid: int = Field(..., description="The application ID")
    name: str = Field(..., max_length=255, description="The name of the game")


class GameMetaDataList(BaseModel):
    games: List[GameMetaData] = Field(..., description="The list of games")


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
    price: int = Field(..., description="The current price of the game in cents")
    initialprice: int = Field(..., description="The initial price of the game in cents")
    discount: str = Field(..., max_length=255, description="The discount on the game")
    ccu: int = Field(..., description="The current concurrent users")
    languages: str = Field(..., description="The supported languages")
    genre: str = Field(..., description="The genre of the game")
    tags: Dict[str, int] = Field(..., description="The tags associated with the game")


class GameDetailsList(BaseModel):
    games: List[GameDetails] = Field(..., description="The list of games")
