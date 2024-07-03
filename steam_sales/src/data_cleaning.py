from settings import config


def print_steam_links(df):
    """
    Prints the Steam links for each game in the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing game information.

    Returns:
        None
    """
    url_base = f"{config.STEAM_BASE_SEARCH_URL}/app/"

    for _, row in df.iterrows():
        appid = row["appid"]
        name = row["name"]

        print(name + ":", url_base + str(appid))
