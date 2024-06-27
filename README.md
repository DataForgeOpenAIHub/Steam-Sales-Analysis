# Steam Sales Analysis

## Overview
Welcome to **Steam Sales Analysis** – an innovative project designed to harness the power of data for insights into the gaming world. We have meticulously crafted an ETL (Extract, Transform, Load) pipeline that covers every essential step: data retrieval, processing, validation, and ingestion. By leveraging the robust Steamspy and Steam APIs, we collect comprehensive game-related metadata, details, and sales figures. 

But we don’t stop there. The culmination of this data journey sees the information elegantly loaded into a MySQL database hosted on Aiven Cloud. From this solid foundation, we take it a step further: the data is analyzed and visualized through dynamic and interactive Tableau dashboards. This transforms raw numbers into actionable insights, offering a clear window into gaming trends and sales performance. Join us as we dive deep into the data and bring the world of gaming to life!

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
This repository is licensed under the `MIT License` License. See the [LICENSE](LICENSE) file for details.

#### Disclaimer

<sub>
The content and code provided in this repository are for educational and demonstrative purposes only. The project may contain experimental features, and the code might not be optimized for production environments. The authors and contributors are not liable for any misuse, damages, or risks associated with the direct or indirect use of this code. Users are strictly advised to review, test, and completely modify the code to suit their specific use cases and requirements. By using any part of this project, you agree to these terms.
</sub>