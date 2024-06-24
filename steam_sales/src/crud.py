from typing import List

import model
from settings import get_logger
from sqlalchemy.orm import Session
from validation import GameDetailsList, GameMetaDataList

logger = get_logger(__file__)


def remove_duplicates_meta(all_data: GameMetaDataList, unique_games: list = []) -> GameMetaDataList:
    seen_appids = set(unique_games)
    unique_games = []

    for game in all_data.games:
        if game.appid not in seen_appids:
            seen_appids.add(game.appid)
            unique_games.append(game)

    return GameMetaDataList(games=unique_games)


def bulk_ingest_meta_data(requests: GameMetaDataList, db: Session):
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


def bulk_ingest_data(requests: GameDetailsList, db: Session):
    new_docs = []

    for np in requests.games:
        new_post = model.GameDetails(**np.model_dump())
        new_docs.append(new_post)

    db.bulk_save_objects(new_docs)
    db.commit()

    logger.info(f"Successfully added '{len(new_docs)}' documents to the database")
    return new_docs


# def document_exists(appid: str, db: Session):
#     blog = db.query(model.GameMeta).filter(model.GameMeta.appid == appid).first()
#     if blog:
#         logger.error(
#             f"Document with the id '{appid}' already exists",
#         )
#         return True
#     return False