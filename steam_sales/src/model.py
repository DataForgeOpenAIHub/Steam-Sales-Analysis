from db import Base, engine
from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.dialects.mysql import JSON


class GameDetails(Base):
    __tablename__ = "steamspy_games_raw"

    id = Column(Integer, primary_key=True, autoincrement=True)
    appid = Column(Integer, unique=True, nullable=False)
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    appid = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)


Base.metadata.create_all(engine)