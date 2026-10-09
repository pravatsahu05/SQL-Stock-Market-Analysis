-- ============================================================================
-- STOCK MARKET ANALYSIS IN SQL
-- Six NSE Stocks: Bajaj Auto, Eicher Motors, Hero Motocorp, Infosys, TCS, TVS Motors
-- Time Period: January 2015 to July 2018 (889 Trading Days)
-- Author: Pravat
-- Database Engine: MySQL 8.0 / SQLite 3
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PART 1: GET TO KNOW THE DATA
-- ----------------------------------------------------------------------------

-- TASK 1: How much history do we have?
-- Goal: Return trading days count, earliest date, and latest date for bajaj_auto.
SELECT 
    COUNT(*) AS trading_days,
    MIN(date) AS first_day,
    MAX(date) AS last_day
FROM bajaj_auto;

-- TASK 2: Eicher's five best closes
-- Goal: Return date and close_price of Eicher Motors' 5 highest closing prices.
SELECT 
    date, 
    close_price
FROM eicher_motors
ORDER BY close_price DESC
LIMIT 5;

-- TASK 3: TCS, year by year
-- Goal: Return each year and TCS's average closing price, rounded to 2 decimals.
-- Note: Uses strftime('%Y', date) for SQLite / YEAR(date) for MySQL.
SELECT 
    strftime('%Y', date) AS year,
    ROUND(AVG(close_price), 2) AS avg_close
FROM tcs
GROUP BY year
ORDER BY year;

-- TASK 4: Find the holes
-- Goal: Identify rows where deliverable_qty is NULL across all six tables.
SELECT 'bajaj_auto' AS stock, date FROM bajaj_auto WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'eicher_motors' AS stock, date FROM eicher_motors WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'hero_motocorp' AS stock, date FROM hero_motocorp WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'infosys' AS stock, date FROM infosys WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'tcs' AS stock, date FROM tcs WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'tvs_motors' AS stock, date FROM tvs_motors WHERE deliverable_qty IS NULL;


-- ----------------------------------------------------------------------------
-- PART 2: THE ASSIGNMENT
-- ----------------------------------------------------------------------------

-- TASK 5: Moving averages (Bajaj Auto)
-- Goal: Create table bajaj1 with date, close_price, ma20, ma50.
-- Nullify partial window averages (rows 1-19 for ma20, rows 1-49 for ma50).
DROP TABLE IF EXISTS bajaj1;
CREATE TABLE bajaj1 AS
SELECT
    date,
    close_price,
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20 
        THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
    END AS ma20,
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50 
        THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2)
    END AS ma50
FROM bajaj_auto;

-- TASK 6: Master table
-- Goal: Create master_table with date and closing prices of all 6 stocks.
DROP TABLE IF EXISTS master_table;
CREATE TABLE master_table AS
SELECT
    b.date,
    b.close_price AS bajaj,
    t.close_price AS tcs,
    v.close_price AS tvs,
    i.close_price AS infosys,
    e.close_price AS eicher,
    h.close_price AS hero
FROM bajaj_auto b
JOIN tcs t ON t.date = b.date
JOIN tvs_motors v ON v.date = b.date
JOIN infosys i ON i.date = b.date
JOIN eicher_motors e ON e.date = b.date
JOIN hero_motocorp h ON h.date = b.date;

-- TASK 7: Golden cross signals (Bajaj Auto)
-- Goal: Create table bajaj2 with date, close_price, and signal ('Buy', 'Sell', 'Hold').
DROP TABLE IF EXISTS bajaj2;
CREATE TABLE bajaj2 AS
WITH t AS (
    SELECT 
        date, 
        close_price, 
        ma20, 
        ma50,
        LAG(ma20) OVER (ORDER BY date) AS prev_ma20,
        LAG(ma50) OVER (ORDER BY date) AS prev_ma50
    FROM bajaj1
)
SELECT 
    date, 
    close_price,
    CASE
        WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
        WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
        WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
        ELSE 'Hold'
    END AS signal
FROM t;

-- TASK 8: How often did it trigger?
-- Goal: Count occurrences of each signal in bajaj2.
SELECT 
    signal, 
    COUNT(*) AS count
FROM bajaj2
GROUP BY signal
ORDER BY signal;

-- TASK 9: Signal on a given day
-- Goal: Return the signal for Bajaj Auto on 2018-06-21.
SELECT 
    date,
    close_price,
    signal
FROM bajaj2
WHERE date = '2018-06-21';

-- MySQL Function Skeleton for Task 9 (Run in MySQL workbench):
/*
DELIMITER $$
CREATE FUNCTION bajaj_signal(d DATE)
RETURNS VARCHAR(4) DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE s VARCHAR(4);
    SELECT `signal` INTO s FROM bajaj2 WHERE `date` = d;
    RETURN IFNULL(s, 'NULL');
END $$
DELIMITER ;

SELECT bajaj_signal('2018-06-21');
*/

-- TASK 10: All six stocks in one query
-- Goal: Single CTE pipeline returning buys, sells, last_signal_date, last_signal for all 6 stocks.
WITH prices AS (
    SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
    UNION ALL SELECT 'Eicher Motors' AS stock, date, close_price FROM eicher_motors
    UNION ALL SELECT 'Hero Motocorp' AS stock, date, close_price FROM hero_motocorp
    UNION ALL SELECT 'Infosys' AS stock, date, close_price FROM infosys
    UNION ALL SELECT 'TCS' AS stock, date, close_price FROM tcs
    UNION ALL SELECT 'TVS Motors' AS stock, date, close_price FROM tvs_motors
),
ma AS (
    SELECT 
        stock, date, close_price,
        CASE 
            WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20 
            THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
        END AS ma20,
        CASE 
            WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50 
            THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW)
        END AS ma50
    FROM prices
),
lagged AS (
    SELECT 
        stock, date, close_price, ma20, ma50,
        LAG(ma20) OVER (PARTITION BY stock ORDER BY date) AS prev_ma20,
        LAG(ma50) OVER (PARTITION BY stock ORDER BY date) AS prev_ma50
    FROM ma
),
sig AS (
    SELECT 
        stock, date, close_price,
        CASE
            WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
            WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
            WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
            ELSE 'Hold'
        END AS signal
    FROM lagged
),
latest AS (
    SELECT 
        stock, date AS last_signal_date, signal AS last_signal,
        ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date DESC) AS rn
    FROM sig
    WHERE signal != 'Hold'
)
SELECT 
    s.stock,
    SUM(CASE WHEN s.signal = 'Buy' THEN 1 ELSE 0 END) AS buys,
    SUM(CASE WHEN s.signal = 'Sell' THEN 1 ELSE 0 END) AS sells,
    l.last_signal_date,
    l.last_signal
FROM sig s
JOIN latest l ON l.stock = s.stock AND l.rn = 1
GROUP BY s.stock
ORDER BY s.stock;


-- ----------------------------------------------------------------------------
-- PART 3: QUESTION THE RESULT
-- ----------------------------------------------------------------------------

-- TASK 11: Who went up?
-- Goal: Calculate overall % price change from 2015-01-01 to 2018-07-31 for each stock.
WITH prices AS (
    SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
    UNION ALL SELECT 'Eicher Motors' AS stock, date, close_price FROM eicher_motors
    UNION ALL SELECT 'Hero Motocorp' AS stock, date, close_price FROM hero_motocorp
    UNION ALL SELECT 'Infosys' AS stock, date, close_price FROM infosys
    UNION ALL SELECT 'TCS' AS stock, date, close_price FROM tcs
    UNION ALL SELECT 'TVS Motors' AS stock, date, close_price FROM tvs_motors
),
ends AS (
    SELECT stock, MIN(date) AS first_date, MAX(date) AS last_date 
    FROM prices 
    GROUP BY stock
)
SELECT 
    e.stock, 
    p1.close_price AS first_close, 
    p2.close_price AS last_close,
    ROUND(100.0 * (p2.close_price - p1.close_price) / p1.close_price, 1) AS pct_change
FROM ends e
JOIN prices p1 ON p1.stock = e.stock AND p1.date = e.first_date
JOIN prices p2 ON p2.stock = e.stock AND p2.date = e.last_date
ORDER BY pct_change DESC;

-- TASK 12: The data trap
-- Goal: Find each stock's single worst day-over-day % change to identify corporate action cliffs.
WITH prices AS (
    SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
    UNION ALL SELECT 'Eicher Motors' AS stock, date, close_price FROM eicher_motors
    UNION ALL SELECT 'Hero Motocorp' AS stock, date, close_price FROM hero_motocorp
    UNION ALL SELECT 'Infosys' AS stock, date, close_price FROM infosys
    UNION ALL SELECT 'TCS' AS stock, date, close_price FROM tcs
    UNION ALL SELECT 'TVS Motors' AS stock, date, close_price FROM tvs_motors
),
moves AS (
    SELECT 
        stock, date, close_price,
        ROUND(100.0 * (close_price / LAG(close_price) OVER (PARTITION BY stock ORDER BY date) - 1), 1) AS pct_move
    FROM prices
),
ranked AS (
    SELECT 
        stock, date, close_price, pct_move,
        ROW_NUMBER() OVER (PARTITION BY stock ORDER BY pct_move ASC) AS rn
    FROM moves
    WHERE pct_move IS NOT NULL
)
SELECT 
    stock, 
    date, 
    close_price, 
    pct_move
FROM ranked
WHERE rn = 1
ORDER BY pct_move ASC;

-- TASK 13: Fix it
-- Goal: Adjust TCS and Infosys prices for 1:1 bonus issues/splits and calculate adjusted % change.
WITH adjusted AS (
    SELECT 
        'TCS' AS stock, date,
        CASE WHEN date < '2018-05-31' THEN close_price / 2.0 ELSE close_price END AS adj_close
    FROM tcs
    UNION ALL
    SELECT 
        'Infosys' AS stock, date,
        CASE WHEN date < '2015-06-15' THEN close_price / 2.0 ELSE close_price END AS adj_close
    FROM infosys
)
SELECT 
    stock,
    ROUND(100.0 * (MAX(CASE WHEN date = '2018-07-31' THEN adj_close END) / MAX(CASE WHEN date = '2015-01-01' THEN adj_close END) - 1), 1) AS adjusted_pct_change
FROM adjusted
GROUP BY stock
ORDER BY stock;
