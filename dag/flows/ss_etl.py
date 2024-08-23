from prefect import flow, task

from steam_sales.steam_etl import SteamDataClean, SteamSpyFetcher, SteamSpyMetadataFetcher, SteamStoreFetcher


@task(name="Fetch & Update Metadata")
def update_metadata():
    fetcher = SteamSpyMetadataFetcher()
    fetcher.run()
    return 0


@task(name="Fetch & Update SteamSpy data")
def update_steamspy_data():
    fetcher = SteamSpyFetcher()
    fetcher.run()


@task(name="Fetch & Update SteamStore data")
def update_steamstore_data():
    fetcher = SteamStoreFetcher()
    fetcher.run()


@task(name="Clean New Steamstore database")
def clean_steamstore_data():
    cleaner = SteamDataClean()
    cleaner.ingest()


@flow(name="Steam ETL Pipeline", log_prints=True)
def steam_etl():
    update_metadata()
    update_steamspy_data()
    update_steamstore_data()
    clean_steamstore_data()


if __name__ == "__main__":
    steam_etl.serve(name="steam_etl")
