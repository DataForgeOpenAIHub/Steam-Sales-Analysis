SELECT appid
FROM steamspy_games_metadata
WHERE appid NOT IN (
        SELECT appid
        FROM steamspy_games_raw
    );