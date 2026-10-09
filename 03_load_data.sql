-- ============================================================================
-- PROJECT: SQL Stock Market Analysis
-- FILE 3: 03_load_data.sql
-- PURPOSE: Import raw CSV files into MySQL tables and transform date/empty values
-- ENGINE: MySQL 8.0+
-- ============================================================================

USE stock_market_analysis;

-- Important Setup Step for MySQL Workbench:
-- Enable local infile loading on the server:
-- SET GLOBAL local_infile = 1;

-- ----------------------------------------------------------------------------
-- 1. LOAD BAJAJ AUTO
-- ----------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:/Users/Pravat/Downloads/Bajaj Auto.csv' 
INTO TABLE bajaj_auto
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
    open_price = NULLIF(@o,''), 
    high_price = NULLIF(@h,''), 
    low_price = NULLIF(@l,''),
    close_price = NULLIF(@c,''), 
    wap = NULLIF(@w,''), 
    no_of_shares = NULLIF(@s,''),
    no_of_trades = NULLIF(@tr,''), 
    total_turnover = NULLIF(@to,''),
    deliverable_qty = NULLIF(@dq,''), 
    pct_deli_qty = NULLIF(@pd,''),
    spread_high_low = NULLIF(@shl,''), 
    spread_close_open = NULLIF(TRIM(@sco),'');

-- ----------------------------------------------------------------------------
-- 2. LOAD EICHER MOTORS
-- ----------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:/Users/Pravat/Downloads/Eicher Motors.csv' 
INTO TABLE eicher_motors
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
    open_price = NULLIF(@o,''), 
    high_price = NULLIF(@h,''), 
    low_price = NULLIF(@l,''),
    close_price = NULLIF(@c,''), 
    wap = NULLIF(@w,''), 
    no_of_shares = NULLIF(@s,''),
    no_of_trades = NULLIF(@tr,''), 
    total_turnover = NULLIF(@to,''),
    deliverable_qty = NULLIF(@dq,''), 
    pct_deli_qty = NULLIF(@pd,''),
    spread_high_low = NULLIF(@shl,''), 
    spread_close_open = NULLIF(TRIM(@sco),'');

-- ----------------------------------------------------------------------------
-- 3. LOAD HERO MOTOCORP
-- ----------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:/Users/Pravat/Downloads/Hero Motocorp.csv' 
INTO TABLE hero_motocorp
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
    open_price = NULLIF(@o,''), 
    high_price = NULLIF(@h,''), 
    low_price = NULLIF(@l,''),
    close_price = NULLIF(@c,''), 
    wap = NULLIF(@w,''), 
    no_of_shares = NULLIF(@s,''),
    no_of_trades = NULLIF(@tr,''), 
    total_turnover = NULLIF(@to,''),
    deliverable_qty = NULLIF(@dq,''), 
    pct_deli_qty = NULLIF(@pd,''),
    spread_high_low = NULLIF(@shl,''), 
    spread_close_open = NULLIF(TRIM(@sco),'');

-- ----------------------------------------------------------------------------
-- 4. LOAD INFOSYS
-- ----------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:/Users/Pravat/Downloads/Infosys.csv' 
INTO TABLE infosys
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
    open_price = NULLIF(@o,''), 
    high_price = NULLIF(@h,''), 
    low_price = NULLIF(@l,''),
    close_price = NULLIF(@c,''), 
    wap = NULLIF(@w,''), 
    no_of_shares = NULLIF(@s,''),
    no_of_trades = NULLIF(@tr,''), 
    total_turnover = NULLIF(@to,''),
    deliverable_qty = NULLIF(@dq,''), 
    pct_deli_qty = NULLIF(@pd,''),
    spread_high_low = NULLIF(@shl,''), 
    spread_close_open = NULLIF(TRIM(@sco),'');

-- ----------------------------------------------------------------------------
-- 5. LOAD TCS
-- ----------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:/Users/Pravat/Downloads/TCS.csv' 
INTO TABLE tcs
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
    open_price = NULLIF(@o,''), 
    high_price = NULLIF(@h,''), 
    low_price = NULLIF(@l,''),
    close_price = NULLIF(@c,''), 
    wap = NULLIF(@w,''), 
    no_of_shares = NULLIF(@s,''),
    no_of_trades = NULLIF(@tr,''), 
    total_turnover = NULLIF(@to,''),
    deliverable_qty = NULLIF(@dq,''), 
    pct_deli_qty = NULLIF(@pd,''),
    spread_high_low = NULLIF(@shl,''), 
    spread_close_open = NULLIF(TRIM(@sco),'');

-- ----------------------------------------------------------------------------
-- 6. LOAD TVS MOTORS
-- ----------------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'C:/Users/Pravat/Downloads/TVS Motors.csv' 
INTO TABLE tvs_motors
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
    open_price = NULLIF(@o,''), 
    high_price = NULLIF(@h,''), 
    low_price = NULLIF(@l,''),
    close_price = NULLIF(@c,''), 
    wap = NULLIF(@w,''), 
    no_of_shares = NULLIF(@s,''),
    no_of_trades = NULLIF(@tr,''), 
    total_turnover = NULLIF(@to,''),
    deliverable_qty = NULLIF(@dq,''), 
    pct_deli_qty = NULLIF(@pd,''),
    spread_high_low = NULLIF(@shl,''), 
    spread_close_open = NULLIF(TRIM(@sco),'');

-- ----------------------------------------------------------------------------
-- VERIFICATION: Check row counts across all loaded tables (Expected: 889 each)
-- ----------------------------------------------------------------------------
SELECT 'bajaj_auto' AS table_name, COUNT(*) AS total_rows, MIN(date) AS min_date, MAX(date) AS max_date FROM bajaj_auto
UNION ALL
SELECT 'eicher_motors', COUNT(*), MIN(date), MAX(date) FROM eicher_motors
UNION ALL
SELECT 'hero_motocorp', COUNT(*), MIN(date), MAX(date) FROM hero_motocorp
UNION ALL
SELECT 'infosys', COUNT(*), MIN(date), MAX(date) FROM infosys
UNION ALL
SELECT 'tcs', COUNT(*), MIN(date), MAX(date) FROM tcs
UNION ALL
SELECT 'tvs_motors', COUNT(*), MIN(date), MAX(date) FROM tvs_motors;
