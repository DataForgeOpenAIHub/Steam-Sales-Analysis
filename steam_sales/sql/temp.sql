SELECT DISTINCT appid
FROM steamspy_games_metadata
WHERE appid NOT IN (
        SELECT appid
        FROM temp
    )
ORDER BY appid ASC;