DELETE FROM SteamSales.steam_games_raw
WHERE id NOT IN (
        SELECT *
        FROM (
                SELECT MIN(id)
                FROM SteamSales.steam_games_raw
                GROUP BY appid
            ) AS temp_table
    );