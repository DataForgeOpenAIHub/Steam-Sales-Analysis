import model
from settings import get_logger
from sqlalchemy.orm import Session
from validation import CleanList, GameDetailsList, GameList, GameMetaDataList

logger = get_logger(__file__)


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

    logger.info(f"Successfully added '{len(new_docs)}' documents to the database")
    return new_docs


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

    logger.info(f"Successfully added '{len(new_docs)}' documents to the database")
    return new_docs


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

        logger.info(f"Successfully added '{len(new_docs)}' documents to the database")
        return new_docs
    except Exception as e:
        logger.error(f"Failed to bulk ingest data: {e}")
        return


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
    new_docs = []

    for np in requests.games:
        new_post = model.CleanData(**np.model_dump())
        new_docs.append(new_post)

    db.bulk_save_objects(new_docs)
    db.commit()

    logger.info(f"Successfully added '{len(new_docs)}' documents to the database")
    return new_docs
