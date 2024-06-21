import argparse
import csv
import datetime as dt
import os
import statistics
import time

import numpy as np
import pandas as pd

from id_collection import get_request


def get_index(download_path: str, index_filename: str):
    try:
        rel_path = os.path.join(download_path, index_filename)

        with open(rel_path, "r") as f:
            index = int(f.readline())

    except FileNotFoundError:
        index = 0

    return index


def prepare_data_file(download_path: str, filename: str, index: int, columns: list):
    if index == 0:
        rel_path = os.path.join(download_path, filename)

        with open(rel_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()


def parse_steam_request(appid: int, name: str):

    url = "http://store.steampowered.com/api/appdetails/"
    parameters = {"appids": appid}

    json_data = get_request(url, parameters=parameters)
    json_app_data = json_data[str(appid)]

    if json_app_data["success"]:
        data = json_app_data["data"]
    else:
        data = {"name": name, "steam_appid": appid}

    return data


def get_app_data(start: int, stop: int, parser, pause: int):
    app_data = []

    for index, row in app_list[start:stop].iterrows():
        print("Current index: {}".format(index), end="\r")

        appid = row["appid"]
        name = row["name"]

        data = parser(appid, name)
        app_data.append(data)

        time.sleep(pause)

    return app_data


def process_batches(
    parser, app_list, download_path, data_filename, index_filename, columns, begin=0, end=-1, batchsize=100, pause=1
):
    print("Starting at index {}:\n".format(begin))

    if end == -1:
        end = len(app_list) + 1

    batches = np.arange(begin, end, batchsize)
    batches = np.append(batches, end)

    apps_written = 0
    batch_times = []

    for i in range(len(batches) - 1):
        start_time = time.time()

        start = batches[i]
        stop = batches[i + 1]

        app_data = get_app_data(start, stop, parser, pause)

        if app_data:
            rel_path = os.path.join(download_path, data_filename)

            with open(rel_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")

                for j in range(3, 0, -1):
                    print("\rAbout to write data, don't stop script! ({})".format(j), end="")
                    time.sleep(0.5)

                writer.writerows(app_data)
                print("\rExported lines {}-{} to {}.".format(start, stop - 1, data_filename), end=" ")

            apps_written += len(app_data)

            idx_path = os.path.join(download_path, index_filename)

            with open(idx_path, "w") as f:
                index = stop
                print(index, file=f)

            end_time = time.time()
            time_taken = end_time - start_time

            batch_times.append(time_taken)
            mean_time = statistics.mean(batch_times)

            est_remaining = (len(batches) - i - 2) * mean_time

            remaining_td = dt.timedelta(seconds=round(est_remaining))
            time_td = dt.timedelta(seconds=round(time_taken))
            mean_td = dt.timedelta(seconds=round(mean_time))

            print("Batch {} time: {} (avg: {}, remaining: {})".format(i, time_td, mean_td, remaining_td))

    print("\nProcessing batches complete. {} apps written".format(apps_written))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Steam app data.")
    parser.add_argument("--num_records", type=int, default=0, help="Number of records to scrape (0 for all).")
    args = parser.parse_args()

    num_records = args.num_records

    download_path = "./data/download"
    steam_app_data = "steam_app_data.csv"
    steam_index = "steam_index.txt"
    app_list = pd.read_csv("./data/download/app_list.csv")

    steam_columns = [
        "type",
        "name",
        "steam_appid",
        "required_age",
        "is_free",
        "controller_support",
        "dlc",
        "detailed_description",
        "about_the_game",
        "short_description",
        "fullgame",
        "supported_languages",
        "header_image",
        "website",
        "pc_requirements",
        "mac_requirements",
        "linux_requirements",
        "legal_notice",
        "drm_notice",
        "ext_user_account_notice",
        "developers",
        "publishers",
        "demos",
        "price_overview",
        "packages",
        "package_groups",
        "platforms",
        "metacritic",
        "reviews",
        "categories",
        "genres",
        "screenshots",
        "movies",
        "recommendations",
        "achievements",
        "release_date",
        "support_info",
        "background",
        "content_descriptors",
    ]

    index = get_index(download_path, steam_index)
    end = -1 if num_records == 0 else index + num_records

    prepare_data_file(download_path, steam_app_data, index, steam_columns)

    process_batches(
        parser=parse_steam_request,
        app_list=app_list,
        download_path=download_path,
        data_filename=steam_app_data,
        index_filename=steam_index,
        columns=steam_columns,
        begin=index,
        end=end,
        batchsize=5,
    )
