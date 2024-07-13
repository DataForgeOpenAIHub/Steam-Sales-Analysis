from db import Base, engine
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.mysql import JSON, LONGTEXT


class GameDetails(Base):
    __tablename__ = "steamspy_games_raw"

    appid = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    developer = Column(String(255), nullable=False)
    publisher = Column(String(255), nullable=False)
    score_rank = Column(String(255))
    positive = Column(Integer, nullable=False)
    negative = Column(Integer, nullable=False)
    userscore = Column(Float, nullable=False)
    owners = Column(Text, nullable=False)
    average_forever = Column(Integer, nullable=False)
    average_2weeks = Column(Integer, nullable=False)
    median_forever = Column(Integer, nullable=False)
    median_2weeks = Column(Integer, nullable=False)
    price = Column(Integer, nullable=True)
    initialprice = Column(Integer, nullable=True)
    discount = Column(String(255), nullable=True)
    ccu = Column(Integer, nullable=False)
    languages = Column(Text, nullable=True)
    genre = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)


class GameMeta(Base):
    __tablename__ = "steamspy_games_metadata"

    appid = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    date_added = Column(DateTime, nullable=False)


class Game(Base):
    __tablename__ = "steam_games_raw"

    type = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    appid = Column(Integer, primary_key=True, nullable=False)
    required_age = Column(Integer, nullable=True)
    is_free = Column(Boolean, nullable=False)
    controller_support = Column(String(255))
    dlc = Column(JSON, nullable=True)
    detailed_description = Column(LONGTEXT, nullable=True)
    about_the_game = Column(LONGTEXT, nullable=True)
    short_description = Column(LONGTEXT, nullable=True)
    supported_languages = Column(Text, nullable=True)
    reviews = Column(Text, nullable=True)
    header_image = Column(Text, nullable=False)
    capsule_image = Column(Text, nullable=False)
    website = Column(Text, default="")
    requirements = Column(JSON, nullable=True)
    developers = Column(JSON, nullable=False)
    publishers = Column(JSON, nullable=False)
    price_overview = Column(JSON, nullable=True)
    platform = Column(JSON, nullable=True)
    metacritic = Column(Integer, nullable=True)
    categories = Column(JSON, nullable=False)
    genres = Column(JSON, nullable=False)
    recommendations = Column(Integer, nullable=True)
    achievements = Column(Integer, nullable=False)
    release_date = Column(Text, nullable=True)
    coming_soon = Column(Boolean, nullable=True)


class CleanData(Base):
    __tablenale__ = "clean_game_data"

    type = Column(Text, nullable=False)
    name = Column(String(255), nullable=False)
    appid = Column(Integer, primary_key=True, nullable=False)
    required_age = Column(Integer, nullable=False)
    controller_support = Column(Integer, nullable=False)
    dlc = Column(Integer, nullable=False)
    requirements = Column(Text, nullable=False)
    platform = Column(String(255), nullable=False)
    metacritic = Column(Integer, nullable=False)
    categories = Column(String(255), nullable=False)
    genres = Column(String(255), nullable=False)
    recommendations = Column(Integer, nullable=False)
    achievements = Column(Integer, nullable=False)
    release_date = Column(DateTime, nullable=True)
    coming_soon = Column(Integer, nullable=False)
    english = Column(Integer, nullable=False)
    developer = Column(String(255), nullable=False)
    publisher = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    year = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)
    day = Column(Integer, nullable=True)
    positive_ratings = Column(Integer, nullable=False)
    negative_ratings = Column(Integer, nullable=False)
    owners_in_millions = Column(String(255), nullable=False)
    average_forever = Column(Integer, nullable=False)
    median_forever = Column(Integer, nullable=False)
    languages = Column(Text, nullable=False)
    steamspy_tags = Column(JSON, nullable=False)


Base.metadata.create_all(engine)
