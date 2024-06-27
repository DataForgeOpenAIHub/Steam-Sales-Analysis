SELECT DISTINCT appid
FROM steamspy_games_metadata
WHERE appid NOT IN (
        SELECT appid
        FROM steam_games_raw
    )
ORDER BY
    appid ASC;