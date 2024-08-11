# `steamstore`

CLI for Steam Store Data Ingestion ETL Pipeline

**Usage**:

```console
$ steamstore [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `clean_steam_data`: Clean the Steam Data and ingest into the...
* `fetch_steamspy_data`: Fetch from SteamSpy Database and ingest...
* `fetch_steamspy_metadata`: Fetch metadata from SteamSpy Database and...
* `fetch_steamstore_data`: Fetch from Steam Store Database and ingest...

## `steamstore clean_steam_data`

Clean the Steam Data and ingest into the Custom Database

**Usage**:

```console
$ steamstore clean_steam_data [OPTIONS]
```

**Options**:

* `--batch-size INTEGER`: Number of records to process in each batch.  [default: 1000]
* `--help`: Show this message and exit.

## `steamstore fetch_steamspy_data`

Fetch from SteamSpy Database and ingest data into Custom Database

**Usage**:

```console
$ steamstore fetch_steamspy_data [OPTIONS]
```

**Options**:

* `--batch-size INTEGER`: Number of records to process in each batch.  [default: 1000]
* `--help`: Show this message and exit.

## `steamstore fetch_steamspy_metadata`

Fetch metadata from SteamSpy Database and ingest metadata into Custom Database

**Usage**:

```console
$ steamstore fetch_steamspy_metadata [OPTIONS]
```

**Options**:

* `--max-pages INTEGER`: Number of pages to fetch from.  [default: 100]
* `--help`: Show this message and exit.

## `steamstore fetch_steamstore_data`

Fetch from Steam Store Database and ingest data into Custom Database

**Usage**:

```console
$ steamstore fetch_steamstore_data [OPTIONS]
```

**Options**:

* `--batch-size INTEGER`: Number of app IDs to process in each batch.  [default: 5]
* `--bulk-factor INTEGER`: Factor to determine when to perform a bulk insert (batch_size * bulk_factor).  [default: 10]
* `--reverse / --no-reverse`: Process app IDs in reverse order.  [default: no-reverse]
* `--help`: Show this message and exit.
