from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from steam_sales.steam_etl.settings import config

SQLALCHAMY_DATABASE_URL = (
    f"mysql+pymysql://{config.MYSQL_USERNAME}:{config.MYSQL_PASSWORD}"
    f"@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DB_NAME}"
)

engine = create_engine(
    SQLALCHAMY_DATABASE_URL,
    connect_args={
        "connect_timeout": 30,
        "read_timeout": 30,
        "write_timeout": 30,
    },
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    poolclass=QueuePool,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        db.autoflush = True
        db.expire_on_commit = True
        yield db
    finally:
        db.close()
