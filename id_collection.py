import os
import time
import pandas as pd
import requests
from requests.exceptions import SSLError, RequestException


def get_request(url: str, parameters=None, max_retries=5):
    try_count = 0
    while try_count < max_retries:
        try:
            response = requests.get(url=url, params=parameters)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"Rate limited. Waiting for {response.headers['Retry-After']} seconds...")
                time.sleep(int(response.headers["Retry-After"]) + 1)
            else:
                print(f"Error: Request failed with status code {response.status_code}")
                return None
        except SSLError as e:
            print(f"SSL Error: {e}")
        except RequestException as e:
            print(f"Request Exception: {e}")

        try_count += 1
        print(f"Retrying ({try_count}/{max_retries})...")
        time.sleep(5)

    print(f"Failed to retrieve data from {url} after {max_retries} retries.")
    return None


if __name__ == "__main__":
    url = "https://steamspy.com/api.php"
    app_id_path = "./data/download/app_list.csv"

    os.makedirs(os.path.dirname(app_id_path), exist_ok=True)

    if os.path.exists(app_id_path):
        existing_data = pd.read_csv(app_id_path)
        existing_appids = set(existing_data["appid"])
        print("Existing data loaded.")
    else:
        existing_data = pd.DataFrame()
        existing_appids = set()
        print("No existing data found, creating new file.")

    all_data = []
    new_data_count = 0

    max_pages = 75
    for i in range(max_pages):
        parameters = {"request": "all", "page": i}
        json_data = get_request(url, parameters)

        if json_data is None:
            print(f"Page {i+1} data fetch failed or empty.")
            continue

        steamspy_data = pd.DataFrame.from_dict(json_data, orient="index")
        app_list = steamspy_data[["appid", "name"]]

        new_data = app_list[~app_list["appid"].isin(existing_appids)]

        if not new_data.empty:
            new_data_count += len(new_data)
            all_data.append(new_data)

        print(f"\rPage {i+1}/{max_pages} data fetched ", end="")

    print("\n")

    if all_data:
        new_data_combined = pd.concat(all_data)
        updated_data = pd.concat([existing_data, new_data_combined]).sort_values("appid").reset_index(drop=True)

        updated_data.to_csv(app_id_path, header=True, index=False)
        print(f"All new data appended and sorted to {app_id_path}")
        print(f"Number of new entries added: {new_data_count}")
    else:
        print("No new data to append.")

    # app_list_df = pd.read_csv(app_id_path)
    # print(app_list_df.head())

# main()
