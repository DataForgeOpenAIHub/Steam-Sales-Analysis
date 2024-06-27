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
    pc_requirements = Column(JSON, nullable=False)
    developers = Column(JSON, nullable=False)
    publishers = Column(JSON, nullable=False)
    pc_platform = Column(Boolean, nullable=False)
    metacritic = Column(Integer, nullable=True)
    categories = Column(JSON, nullable=False)
    genres = Column(JSON, nullable=False)
    recommendations = Column(Integer, nullable=True)
    achievements = Column(Integer, nullable=False)
    release_date = Column(DateTime, nullable=True)
    coming_soon = Column(Boolean, nullable=True)


Base.metadata.create_all(engine)
