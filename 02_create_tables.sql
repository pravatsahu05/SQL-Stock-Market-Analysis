-- ============================================================================
-- PROJECT: SQL Stock Market Analysis
-- FILE 2: 02_create_tables.sql
-- PURPOSE: Define table schemas for all six NSE stock datasets
-- ENGINE: MySQL 8.0+
-- ============================================================================

USE stock_market_analysis;

-- ----------------------------------------------------------------------------
-- TABLE 1: bajaj_auto
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS bajaj_auto;
CREATE TABLE bajaj_auto (
    `date` DATE PRIMARY KEY,
    `open_price` DECIMAL(12,2),
    `high_price` DECIMAL(12,2),
    `low_price` DECIMAL(12,2),
    `close_price` DECIMAL(12,2),
    `wap` DECIMAL(16,4),
    `no_of_shares` BIGINT,
    `no_of_trades` BIGINT,
    `total_turnover` DECIMAL(20,2),
    `deliverable_qty` BIGINT NULL,
    `pct_deli_qty` DECIMAL(6,2) NULL,
    `spread_high_low` DECIMAL(12,2),
    `spread_close_open` DECIMAL(12,2)
);

-- ----------------------------------------------------------------------------
-- TABLE 2: eicher_motors
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS eicher_motors;
CREATE TABLE eicher_motors (
    `date` DATE PRIMARY KEY,
    `open_price` DECIMAL(12,2),
    `high_price` DECIMAL(12,2),
    `low_price` DECIMAL(12,2),
    `close_price` DECIMAL(12,2),
    `wap` DECIMAL(16,4),
    `no_of_shares` BIGINT,
    `no_of_trades` BIGINT,
    `total_turnover` DECIMAL(20,2),
    `deliverable_qty` BIGINT NULL,
    `pct_deli_qty` DECIMAL(6,2) NULL,
    `spread_high_low` DECIMAL(12,2),
    `spread_close_open` DECIMAL(12,2)
);

-- ----------------------------------------------------------------------------
-- TABLE 3: hero_motocorp
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS hero_motocorp;
CREATE TABLE hero_motocorp (
    `date` DATE PRIMARY KEY,
    `open_price` DECIMAL(12,2),
    `high_price` DECIMAL(12,2),
    `low_price` DECIMAL(12,2),
    `close_price` DECIMAL(12,2),
    `wap` DECIMAL(16,4),
    `no_of_shares` BIGINT,
    `no_of_trades` BIGINT,
    `total_turnover` DECIMAL(20,2),
    `deliverable_qty` BIGINT NULL,
    `pct_deli_qty` DECIMAL(6,2) NULL,
    `spread_high_low` DECIMAL(12,2),
    `spread_close_open` DECIMAL(12,2)
);

-- ----------------------------------------------------------------------------
-- TABLE 4: infosys
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS infosys;
CREATE TABLE infosys (
    `date` DATE PRIMARY KEY,
    `open_price` DECIMAL(12,2),
    `high_price` DECIMAL(12,2),
    `low_price` DECIMAL(12,2),
    `close_price` DECIMAL(12,2),
    `wap` DECIMAL(16,4),
    `no_of_shares` BIGINT,
    `no_of_trades` BIGINT,
    `total_turnover` DECIMAL(20,2),
    `deliverable_qty` BIGINT NULL,
    `pct_deli_qty` DECIMAL(6,2) NULL,
    `spread_high_low` DECIMAL(12,2),
    `spread_close_open` DECIMAL(12,2)
);

-- ----------------------------------------------------------------------------
-- TABLE 5: tcs
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS tcs;
CREATE TABLE tcs (
    `date` DATE PRIMARY KEY,
    `open_price` DECIMAL(12,2),
    `high_price` DECIMAL(12,2),
    `low_price` DECIMAL(12,2),
    `close_price` DECIMAL(12,2),
    `wap` DECIMAL(16,4),
    `no_of_shares` BIGINT,
    `no_of_trades` BIGINT,
    `total_turnover` DECIMAL(20,2),
    `deliverable_qty` BIGINT NULL,
    `pct_deli_qty` DECIMAL(6,2) NULL,
    `spread_high_low` DECIMAL(12,2),
    `spread_close_open` DECIMAL(12,2)
);

-- ----------------------------------------------------------------------------
-- TABLE 6: tvs_motors
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS tvs_motors;
CREATE TABLE tvs_motors (
    `date` DATE PRIMARY KEY,
    `open_price` DECIMAL(12,2),
    `high_price` DECIMAL(12,2),
    `low_price` DECIMAL(12,2),
    `close_price` DECIMAL(12,2),
    `wap` DECIMAL(16,4),
    `no_of_shares` BIGINT,
    `no_of_trades` BIGINT,
    `total_turnover` DECIMAL(20,2),
    `deliverable_qty` BIGINT NULL,
    `pct_deli_qty` DECIMAL(6,2) NULL,
    `spread_high_low` DECIMAL(12,2),
    `spread_close_open` DECIMAL(12,2)
);

-- Verification Query: List all created tables in the active database
SHOW TABLES;
