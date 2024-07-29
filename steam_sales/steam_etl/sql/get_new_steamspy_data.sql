SELECT r.*
FROM SteamSales.steamspy_games_raw AS r
    INNER JOIN SteamSales.steamspy_games_metadata AS m ON m.appid = r.appid
    LEFT JOIN SteamSales.clean_game_data AS c ON r.appid = c.appid
WHERE m.date_added >= (
        SELECT DATE_SUB(last_run, INTERVAL 1 DAY)
        FROM last_run
        WHERE scraper = 'meta'
    )
    AND c.appid IS NULL;