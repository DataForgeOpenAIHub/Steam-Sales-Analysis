# Steam Sales Analysis

## Overview
The Steam Sales Analysis project involves creating an ETL (Extract, Transform, Load) data pipeline that encompasses data retrieval, processing, validation, and ingestion operations. We call the Steamspy and Steam APIs to collect game-related metadata, details, and sales data. Finally, the data is loaded into a MySQL database hosted on Aiven Cloud.

## Setup Instructions

### Using pip
1. **Create a virtual environment:**
   ```bash
   python -m venv game
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

2. **Install dependencies:**
   ```bash
   pip install -r dev-requirements.txt
   ```

### Using conda
1. **Create a conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate game
   ```

### Configuration
1. **Create an `.env` file** in the root directory of the repository.
2. **Add the following variables to the `.env` file:**
   ```ini
   # Database configuration
   MYSQL_USERNAME=<your_mysql_username>
   MYSQL_PASSWORD=<your_mysql_password>
   MYSQL_HOST=<your_mysql_host>
   MYSQL_PORT=<your_mysql_port>
   MYSQL_DB_NAME=<your_mysql_db_name>
   ```

## Database Integration
The project connects to a MySQL database hosted on Aiven Cloud using the credentials provided in the `.env` file. Ensure that the database is properly set up and accessible with the provided credentials.

## Running the ETL Pipeline
To execute the ETL pipeline, use the following command:
1. To collect metadata
    ```bash
    python steam_sales/src/collect_metadata.py
    ```
2. To collect steamspy data
    ```bash
    python steam_sales/src/collect_steamspy_data.py
    ```
3. To collect steam metadata
    ```bash
    python steam_sales/src/collect_steam_data.py
    ```

This will start the process of retrieving data from the Steamspy and Steam APIs, processing and validating it, and then loading it into the MySQL database.