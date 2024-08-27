# Steam Sales Analysis

![banner](assets/imgs/steam_logo_banner.jpg)

## Overview
Welcome to **Steam Sales Analysis** – an innovative project designed to harness the power of data for insights into the gaming world. We have meticulously crafted an ETL (Extract, Transform, Load) pipeline that covers every essential step: data retrieval, processing, validation, and ingestion. By leveraging the robust Steamspy and Steam APIs, we collect comprehensive game-related metadata, details, and sales figures.

But we don’t stop there. The culmination of this data journey sees the information elegantly loaded into a MySQL database hosted on Aiven Cloud. From this solid foundation, we take it a step further: the data is analyzed and visualized through dynamic and interactive Tableau dashboards. This transforms raw numbers into actionable insights, offering a clear window into gaming trends and sales performance. Join us as we dive deep into the data and bring the world of gaming to life!

# `steamstore` CLI
![Steamstore ETL Pipeline](assets/imgs/steamstore-etl.drawio.png)

## Setup
### Installing the package
For general use, setting up the environment and dependencies is straightforward:

```bash
# Install the python distribution from PyPI
pip install steamstore-etl
```

### Setting up the environment variables
- Create an `.env` file in a directory.
```ini
# Database configuration
MYSQL_USERNAME=<your_mysql_username>
MYSQL_PASSWORD=<your_mysql_password>
MYSQL_HOST=<your_mysql_host>
MYSQL_PORT=<your_mysql_port>
MYSQL_DB_NAME=<your_mysql_db_name>
```
- Open a terminal at the specified location

   #### For Ubuntu (or other Unix-like systems)

   1. **Load `.env` Variables into the Terminal**

      To load the variables from the `.env` file into your current terminal session, you can use the `export` command along with the `dotenv` command if you have the `dotenv` utility installed. 

      **Using `export` directly (manual method):**

      ```bash
      export $(grep -v '^#' .env | xargs)
      ```

      - `grep -v '^#' .env` removes any comments from the file.
      - `xargs` converts the output into environment variable export commands.

      **Using `dotenv` (requires installation):**

      If you prefer a tool, you can use `dotenv`:

      - Install `dotenv` if you don't have it:

      ```bash
      sudo apt-get install python3-dotenv
      ```

      - Then, use the following command to load the `.env` file:

      ```bash
      dotenv
      ```

      **Using `source` (not typical for `.env` but useful for `.sh` files):**

      If your `.env` file is simple, you can use `source` directly (this method assumes no special parsing is needed):

      ```bash
      source .env
      ```

      Note that `source` works well if your `.env` file only contains simple `KEY=VALUE` pairs.

   2. **Verify the Variables**

      After loading, you can check that the environment variables are set:

      ```bash
      echo $MYSQL_USERNAME
      ```

   #### For Windows

   1. **Load `.env` Variables into PowerShell**

      You can use a PowerShell script to load the variables from the `.env` file.

      **Create a PowerShell script (e.g., `load_env.ps1`):**

      ```powershell
      Get-Content .env | ForEach-Object {
         if ($_ -match "^(.*?)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], [System.EnvironmentVariableTarget]::Process)
         }
      }
      ```

      - This script reads each line from the `.env` file and sets it as an environment variable for the current PowerShell session.

      **Run the script:**

      ```powershell
      .\load_env.ps1
      ```

      **Verify the Variables:**

      ```powershell
      echo $env:MYSQL_USERNAME
      ```

   2. **Load `.env` Variables into Command Prompt**

      The Command Prompt does not have built-in support for `.env` files. You can use a batch script to achieve this.

      **Create a batch script (e.g., `load_env.bat`):**

      ```batch
      @echo off
      for /f "tokens=1,2 delims==" %%A in (.env) do set %%A=%%B
      ```

      **Run the batch script:**

      ```batch
      load_env.bat
      ```

      **Verify the Variables:**

      ```batch
      echo %MYSQL_USERNAME%
      ```

## CLI for Steam Store Data Ingestion ETL Pipeline

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
     
# Setup Instructions
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

