-- ============================================================================
-- PROJECT: SQL Stock Market Analysis
-- FILE 1: 01_create_database.sql
-- PURPOSE: Create and select the database environment in MySQL
-- ENGINE: MySQL 8.0+
-- ============================================================================

-- Step 1: Drop the database if it already exists to ensure a clean setup
DROP DATABASE IF EXISTS stock_market_analysis;

-- Step 2: Create a fresh database with standard UTF-8 character encoding
CREATE DATABASE stock_market_analysis
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- Step 3: Select the database for subsequent table creation and queries
USE stock_market_analysis;

-- Verification query
SELECT DATABASE() AS current_active_database;
