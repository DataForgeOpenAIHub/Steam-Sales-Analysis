from sqlalchemy.orm import Session

from steam_sales.steam_etl import model
from steam_sales.steam_etl.settings import get_logger
from steam_sales.steam_etl.validation import CleanList, GameDetailsList, GameList, GameMetaDataList, LastRun

logger = get_logger(__name__)


def remove_duplicates_meta(all_data: GameMetaDataList, unique_games: list = []) -> GameMetaDataList:
    """
    Removes duplicates from the given list of game metadata.

    Args:
        all_data (GameMetaDataList): The list of game metadata to remove duplicates from.
        unique_games (list, optional): A list of unique game appids. Defaults to an empty list.

    Returns:
        GameMetaDataList: A new list of game metadata without duplicates.
    """
    seen_appids = set(unique_games)
    unique_games = []

    for game in all_data.games:
        if game.appid not in seen_appids:
            seen_appids.add(game.appid)
            unique_games.append(game)

    return GameMetaDataList(games=unique_games)


def bulk_ingest_meta_data(requests: GameMetaDataList, db: Session):
    """
    Bulk ingests game metadata into the database.

    Args:
        requests (GameMetaDataList): A list of game metadata requests.
        db (Session): The database session.

    Returns:
        List[GameMeta]: A list of newly added game metadata documents.
    """
    new_docs = []

    games_in_db = db.query(model.GameMeta.appid).all()
    games_in_db = [doc[0] for doc in games_in_db]

    requests = remove_duplicates_meta(requests, games_in_db)

    for np in requests.games:
        new_post = model.GameMeta(**np.model_dump())
        new_docs.append(new_post)

    db.bulk_save_objects(new_docs)
    db.commit()
    return len(new_docs)


def bulk_ingest_steamspy_data(requests: GameDetailsList, db: Session):
    """
    Bulk ingests SteamSpy data into the database.

    Args:
        requests (GameDetailsList): A list of game details to be ingested.
        db (Session): The database session.

    Returns:
        List[GameDetails]: The list of newly added game details documents.
    """
    new_docs = []

    for np in requests.games:
        new_post = model.GameDetails(**np.model_dump())
        new_docs.append(new_post)

    db.bulk_save_objects(new_docs)
    db.commit()

    return len(new_docs)


def bulk_ingest_steam_data(requests: GameList, db: Session):
    """
    Bulk ingests Steam data into the database.

    Args:
        requests (GameList): A list of game requests.
        db (Session): The database session.

    Returns:
        List[Game]: A list of newly added game documents.

    Raises:
        Exception: If there is an error during the bulk ingestion process.
    """
    try:
        new_docs = []

        for np in requests.games:
            if game_exists(np.appid, db):
                continue

            new_post = model.Game(**np.model_dump())
            new_docs.append(new_post)

        db.bulk_save_objects(new_docs)
        db.commit()

        # logger.info(f"Successfully added '{len(new_docs)}' documents to the database")
        return len(new_docs)
    except Exception as e:
        logger.error(f"Failed to bulk ingest data: {e}")
        return 0


def game_exists(appid: str, db: Session):
    """
    Check if a game with the given appid exists in the database.

    Args:
        appid (str): The appid of the game to check.
        db (Session): The database session.

    Returns:
        bool: True if the game exists in the database, False otherwise.
    """
    blog = db.query(model.Game).filter(model.Game.appid == appid).first()
    if blog:
        logger.warning(
            f"Document with the id '{appid}' already exists. Requesting the data from the Steam API skipped.",
        )
        return True
    return False


def bulk_ingest_clean_data(requests: CleanList, db: Session):
    """
    Bulk ingests clean data into the database.

    Args:
        requests (CleanList): A list of clean data requests.
        db (Session): The database session.

    Returns:
        List[CleanData]: A list of newly added clean data documents.
    """
    new_docs = []

    for np in requests.games:
        new_post = model.CleanData(**np.model_dump())
        new_docs.append(new_post)

    db.bulk_save_objects(new_docs)
    db.commit()

    # logger.info(f"Successfully added '{len(new_docs)}' documents to the database")
    return new_docs


def log_last_run_time(log: LastRun, db: Session):
    """
    Log the last run time for a scraper.

    Args:
        log (LastRun): The last run time log.
        db (Session): The database session.
    """
    entry = db.query(model.LastRun).filter(model.LastRun.scraper == log.scraper)
    if not entry.first():
        new_entry = model.LastRun(**log.model_dump())
        db.add(new_entry)
    else:
        entry.update(log.model_dump())

    db.commit()
    logger.info(f"Updated last run time to '{log.last_run}' for worker '{log.scraper}'")


def flag_faulty_appid(appid: int, db: Session):
    """
    Flag an appid as faulty in the database.

    Args:
        appid (int): The appid to flag as faulty.
        db (Session): The database session.
    """
    entry = db.query(model.GameMeta).filter(model.GameMeta.appid == appid)
    if entry.first():
        entry.update({"dne": True})
    db.commit()
    logger.info(f"Flagged app ID '{appid}' as faulty")
