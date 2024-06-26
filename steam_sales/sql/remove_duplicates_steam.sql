WITH CTE AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY appid
            ORDER BY appid
        ) AS row_num
    FROM steam_games_raw
)
DELETE FROM steam_games_raw
WHERE appid IN (
        SELECT appid
        FROM CTE
        WHERE row_num > 1
    );