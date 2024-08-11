from typing import Annotated

import typer
from steam_sales.steam_etl import SteamDataClean, SteamSpyFetcher, SteamSpyMetadataFetcher, SteamStoreFetcher

app = typer.Typer(name="steamstore", help="CLI for Steam Store Data Ingestion ETL Pipeline")


@app.command(
    name="fetch_steamspy_metadata",
    help="Fetch metadata from SteamSpy Database and ingest metadata into Custom Database",
)
def fetch_steamspy_metadata(max_pages: Annotated[int, typer.Option(help="Number of pages to fetch from.")] = 100):
    """
    Fetches game metadata from SteamSpy API and stores it in a database.

    Parameters:
        - max_pages (int, optional): Number of pages to fetch from. Defaults to 100.
    """
    fetcher = SteamSpyMetadataFetcher(max_pages=max_pages)
    fetcher.run()
    typer.echo("SteamSpy metadata fetched successfully.", color=typer.colors.GREEN)


@app.command(name="fetch_steamspy_data", help="Fetch from SteamSpy Database and ingest data into Custom Database")
def fetch_steamspy_data(
    batch_size: Annotated[int, typer.Option(help="Number of records to process in each batch.")] = 1000,
):
    """
    Fetches SteamSpy data using the specified batch size.

    Parameters:
        - batch_size (int): The number of records to fetch in each batch. Defaults to 1000.
    """
    fetcher = SteamSpyFetcher(batch_size=batch_size)
    fetcher.run()
    typer.echo("SteamSpy data fetched successfully.", color=typer.colors.GREEN)


@app.command(name="fetch_steamstore_data", help="Fetch from Steam Store Database and ingest data into Custom Database")
def fetch_steamstore_data(
    batch_size: Annotated[int, typer.Option(help="Number of app IDs to process in each batch.")] = 5,
    bulk_factor: Annotated[
        int, typer.Option(help="Factor to determine when to perform a bulk insert (batch_size * bulk_factor).")
    ] = 10,
    reverse: Annotated[bool, typer.Option(help="Process app IDs in reverse order.")] = False,
):
    """
    This command fetches unique app IDs from the Steam Store Database, processes the data in batches,
    and ingests the data into the database. The process is designed to handle large datasets efficiently
    by using batch processing and bulk insertion methods.

    Parameters:
        - batch_size (int): The number of app IDs to process in each batch. Default is 5.
        - bulk_factor (int): Determines when to perform a bulk insert. Data is ingested in bulk when the
        number of processed games reaches batch_size * bulk_factor. Default is 10.
        - reverse (bool): If set to True, the app IDs are processed in reverse order. Default is False.
    """
    fetcher = SteamStoreFetcher(batch_size=batch_size, bulk_factor=bulk_factor, reverse=reverse)
    fetcher.run()
    typer.echo("SteamStore data fetched successfully.", color=typer.colors.GREEN)


@app.command(name="clean_steam_data", help="Clean the Steam Data and ingest into the Custom Database")
def clean_steam_data(
    batch_size: Annotated[int, typer.Option(help="Number of records to process in each batch.")] = 1000,
):
    """
    Cleans the Steam data by running the SteamDataClean class with the specified batch size.

    Parameters:
        - batch_size (int): The number of records to process in each batch. Default is 1000.
    """
    cleaner = SteamDataClean(batch_size=batch_size)
    cleaner.ingest()
    typer.echo("Steam data cleaned successfully.", color=typer.colors.GREEN)


if __name__ == "__main__":
    app()
