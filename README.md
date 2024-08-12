# Steam Sales Analysis

![banner](assets/imgs/steam_logo.jpg)

## Overview
Welcome to **Steam Sales Analysis** – an innovative project designed to harness the power of data for insights into the gaming world. We have meticulously crafted an ETL (Extract, Transform, Load) pipeline that covers every essential step: data retrieval, processing, validation, and ingestion. By leveraging the robust Steamspy and Steam APIs, we collect comprehensive game-related metadata, details, and sales figures.

But we don’t stop there. The culmination of this data journey sees the information elegantly loaded into a MySQL database hosted on Aiven Cloud. From this solid foundation, we take it a step further: the data is analyzed and visualized through dynamic and interactive Tableau dashboards. This transforms raw numbers into actionable insights, offering a clear window into gaming trends and sales performance. Join us as we dive deep into the data and bring the world of gaming to life!

# Setup Instructions

## General Use Case

For general use, setting up the environment and dependencies is straightforward:
1. **Clone the repository**:
   ```bash
   git clone https://github.com/DataForgeOpenAIHub/Steam-Sales-Analysis.git
   cd steam-sales-analysis
   ```
2. **Install the package**:
   ```bash
   pip install .
   ```

3. **Configuration**:
   - Create an `.env` file in the root directory of the repository.
   - Add the following variables to the `.env` file:
     ```ini
     # Database configuration
     MYSQL_USERNAME=<your_mysql_username>
     MYSQL_PASSWORD=<your_mysql_password>
     MYSQL_HOST=<your_mysql_host>
     MYSQL_PORT=<your_mysql_port>
     MYSQL_DB_NAME=<your_mysql_db_name>
     ```

## Development Setup

For development purposes, you might need to have additional dependencies and tools:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DataForgeOpenAIHub/Steam-Sales-Analysis.git
   cd steam-sales-analysis
   ```

2. **Create a virtual environment**:
   - Using `venv`:
     ```bash
     python -m venv game
     source game/bin/activate  # On Windows use `game\Scripts\activate`
     ```
   - Using `conda`:
     ```bash
     conda env create -f environment.yml
     conda activate game
     ```

3. **Install dependencies**:
   - Install general dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Install development dependencies:
     ```bash
     pip install -r dev-requirements.txt
     ```

4. **Configuration**:
   - Create an `.env` file in the root directory of the repository.
   - Add the following variables to the `.env` file:
     ```ini
     # Database configuration
     MYSQL_USERNAME=<your_mysql_username>
     MYSQL_PASSWORD=<your_mysql_password>
     MYSQL_HOST=<your_mysql_host>
     MYSQL_PORT=<your_mysql_port>
     MYSQL_DB_NAME=<your_mysql_db_name>
     ```

# `steamstore` CLI

CLI for Steam Store Data Ingestion ETL Pipeline

**Usage**:

```console
$ steamstore [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

**Commands**:

- `clean_steam_data`: Clean the Steam Data and ingest into the Custom Database
- `fetch_steamspy_data`: Fetch from SteamSpy Database and ingest data into Custom Database
- `fetch_steamspy_metadata`: Fetch metadata from SteamSpy Database and ingest metadata into Custom Database
- `fetch_steamstore_data`: Fetch from Steam Store Database and ingest data into Custom Database

## Detailed Command Usage
### `steamstore clean_steam_data`

Clean the Steam Data and ingest into the Custom Database

**Usage**:

```console
$ steamstore clean_steam_data [OPTIONS]
```

**Options**:

- `--batch-size INTEGER`: Number of records to process in each batch.  [default: 1000]
- `--help`: Show this message and exit.

### `steamstore fetch_steamspy_data`

Fetch from SteamSpy Database and ingest data into Custom Database

**Usage**:

```console
$ steamstore fetch_steamspy_data [OPTIONS]
```

**Options**:

- `--batch-size INTEGER`: Number of records to process in each batch.  [default: 1000]
- `--help`: Show this message and exit.

### `steamstore fetch_steamspy_metadata`

Fetch metadata from SteamSpy Database and ingest metadata into Custom Database

**Usage**:

```console
$ steamstore fetch_steamspy_metadata [OPTIONS]
```

**Options**:

- `--max-pages INTEGER`: Number of pages to fetch from.  [default: 100]
- `--help`: Show this message and exit.

### `steamstore fetch_steamstore_data`

Fetch from Steam Store Database and ingest data into Custom Database

**Usage**:

```console
$ steamstore fetch_steamstore_data [OPTIONS]
```

**Options**:

- `--batch-size INTEGER`: Number of app IDs to process in each batch.  [default: 5]
- `--bulk-factor INTEGER`: Factor to determine when to perform a bulk insert (batch_size * bulk_factor).  [default: 10]
- `--reverse / --no-reverse`: Process app IDs in reverse order.  [default: no-reverse]
- `--help`: Show this message and exit.

## Database Integration

The project connects to a MySQL database hosted on `Aiven Cloud` using the credentials provided in the `.env` file. Ensure that the database is properly set up and accessible with the provided credentials.

## Running Individual Parts of the ETL Pipeline
To execute the ETL pipeline, use the following commands:

1. **To collect metadata:**
   ```bash
   steamstore fetch_steamspy_metadata
   ```

2. **To collect SteamSpy data:**
   ```bash
   steamstore fetch_steamspy_data --batch-size 1000
   ```

3. **To collect Steam data:**
   ```bash
   steamstore fetch_steamstore_data --batch-size 5 --bulk-factor 10
   ```

4. **To clean Steam data:**
   ```bash
   steamstore clean_steam_data --batch-size 1000
   ```

This will start the process of retrieving data from the Steamspy and Steam APIs, processing and validating it, and then loading it into the MySQL database.

## References:

### API Used:

- [Steamspy API](https://steamspy.com/api.php)
- [Steam Store API - InternalSteamWebAPI](https://github.com/Revadike/InternalSteamWebAPI/wiki)
- [Steam Web API Documentation](https://steamapi.xpaw.me/#)
- [RJackson/StorefrontAPI Documentation](https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI)
- [Steamworks Web API Reference](https://partner.steamgames.com/doc/webapi)

### Repository

- [Nik Davis's Steam Data Science Project](https://github.com/nik-davis/steam-data-science-project)

---

#### LICENSE

This repository is licensed under the `MIT License`. See the [LICENSE](LICENSE) file for details.

#### Disclaimer

<sub>
The content and code provided in this repository are for educational and demonstrative purposes only. The project may contain experimental features, and the code might not be optimized for production environments. The authors and contributors are not liable for any misuse, damages, or risks associated with the direct or indirect use of this code. Users are strictly advised to review, test, and completely modify the code to suit their specific use cases and requirements. By using any part of this project, you agree to these terms.
</sub>

