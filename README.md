# SQL Stock Market Analysis (Jan 2015 – Jul 2018)

A comprehensive data engineering, technical strategy, and corporate action analysis of six major National Stock Exchange (NSE) stocks using **MySQL 8.0** and **SQL Window Functions**.

---

## Executive Summary

This project analyzes **889 trading days** (January 1, 2015 to July 31, 2018) across six leading Indian NSE stocks:
- **Auto Sector:** Bajaj Auto, Eicher Motors, Hero Motocorp, TVS Motors
- **IT Sector:** Infosys, TCS (Tata Consultancy Services)

Using advanced SQL techniques—including sliding frame window aggregations (`AVG() OVER`), CTE pipelines, `ROW_NUMBER()`, `LAG()`, and conditional aggregation—we built a complete moving average technical trading system and uncovered critical corporate action **"Data Traps"**.

### Primary Discoveries:
1. **The Corporate Action Data Trap:** Unadjusted raw stock price data incorrectly identifies **TCS (-23.8%)** and **Infosys (-30.9%)** as bottom-tier market losers due to 1:1 bonus share issues (splits) on May 31, 2018 (TCS -50.4%) and June 15, 2015 (Infosys -49.9%).
2. **True Adjusted Growth:** Normalizing pre-event price series reveals that TCS generated **+52.4%** and Infosys generated **+38.2%** actual capital returns over the 3.5-year period.
3. **Top Market Leaders:** **TVS Motors (+86.9%)** and **Eicher Motors (+82.6%)** led the market in total returns.
4. **Signal Distortion:** The artificial -50.4% price cliff on TCS triggered a **fake Death Cross ('Sell') signal on 2018-06-05**. Normalizing price data completely eliminates this false signal, confirming TCS remained in an uninterrupted **'Buy' trend from 2018-04-20 onwards**.

---

## Project Structure

```text
SQL Stock Market Analysis/
├── app.py                             # Interactive Web Dashboard Flask Backend API
├── 01_create_database.sql             # Database creation & character encoding setup
├── 02_create_tables.sql               # Table schemas for all 6 stock datasets
├── 03_load_data.sql                   # CSV import, STR_TO_DATE transformation & NULL handling
├── 04_stock_market_analysis.sql       # Unified master SQL analysis script (Tasks 1 to 13 + Stretch)
├── build_insights_pdf.py              # Python script to compile PDF report & Matplotlib charts
├── generate_all_charts.py             # Standalone visualization generator for all 8 project charts
├── Stock_Market_Analysis_Insights.pdf # Professional insights PDF report
├── chart1_normalized_performance.png  # Chart 1: Six-Stock Normalized Trajectory (Rebased to 100)
├── chart2_bajaj_ma.png                # Chart 2: Bajaj Auto Price & Moving Averages (MA20 vs MA50)
├── chart3_bajaj_signals.png           # Chart 3: Bajaj Auto Golden/Death Cross Crossover Signals
├── chart4_pct_returns.png             # Chart 4: Total Returns Across All 6 Stocks (Unadjusted vs Adjusted)
├── chart5_signal_counts.png           # Chart 5: Buy vs Sell Signal Frequencies Across All 6 Stocks
├── chart6_worst_daily_movements.png   # Chart 6: Single Worst Daily Price Movement per Stock
├── chart7_tcs_adjusted.png            # Chart 7: TCS Unadjusted vs Adjusted Trajectory & Data Trap
├── chart8_infosys_adjusted.png        # Chart 8: Infosys Unadjusted vs Adjusted Trajectory & Data Trap
├── templates/index.html               # Web Dashboard Interactive HTML Interface
├── static/css/dashboard.css           # Glassmorphism Dark Mode Dashboard UI Styles
├── static/js/dashboard.js             # Interactive Query Studio & Chart Gallery JS Logic
└── README.md                          # Project documentation & presentation guide
```

---

## 🚀 Interactive Web Dashboard & SQL Studio

You can launch the **Interactive Web Dashboard** locally:

```bash
# 1. Run the Flask Web App
python app.py

# 2. Open your web browser and navigate to:
http://127.0.0.1:5000
```

### Dashboard Features:
1. **Interactive SQL Query Studio**: Select any of the project tasks (Tasks 1 to 13 + Stretch Challenge) or type your own custom SQL query to execute in real-time against `stocks.db`. View tabular results with search, execution timer, row count, and CSV export.
2. **Chart & Insights Gallery**: View all 8 high-resolution visual graphs. Each chart is paired with **Key Business Insights**, **Strategic Recommendations**, and **Methodological Risk & Caveats**.

---

## Database Setup & Data Import Guide

### 1. Prerequisites
- **MySQL 8.0+** or **MySQL Workbench**
- (Optional) **Python 3.10+** with `pandas`, `matplotlib`, and `reportlab` for generating visual charts and PDF reports.

### 2. Execution Steps in MySQL
Open MySQL Workbench and run the SQL scripts in numerical order:

```sql
-- Step 1: Create Database
SOURCE d:/Coding Programs/SQL Stock Market Analysis/01_create_database.sql;

-- Step 2: Create Schemas
SOURCE d:/Coding Programs/SQL Stock Market Analysis/02_create_tables.sql;

-- Step 3: Enable Local Infile & Load Data
SET GLOBAL local_infile = 1;
SOURCE d:/Coding Programs/SQL Stock Market Analysis/03_load_data.sql;

-- Step 4: Run Complete Analysis Pipeline
SOURCE d:/Coding Programs/SQL Stock Market Analysis/04_stock_market_analysis.sql;
```

---

## Quantitative Validation Audit Table

Every task in this project has been strictly validated against the official *Student Guide* checkpoints:

| Task # | Goal / Objective | Guide Checkpoint Expectation | Our Executed SQL Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| **Task 1** | History of `bajaj_auto` | 889 trading days, 2015-01-01 to 2018-07-31 | 889 days \| 2015-01-01 to 2018-07-31 | **MATCH** |
| **Task 2** | Eicher's Top 5 Closes | Top close > ₹32,000, all in same month | Top: ₹32,786.40 (07-Sep-2017) \| All 5 in Sep 2017 | **MATCH** |
| **Task 3** | TCS Year by Year | 2016 average equals exactly 2419.00 | 2015: 2537.39 \| 2016: **2419.00** \| 2017: 2475.36 \| 2018: 2729.12 | **MATCH** |
| **Task 4** | Find the Holes | 6 total NULL rows across 2 distinct dates | 6 rows total \| Dates: **2015-12-09** (4 stocks) & **2017-08-31** (2 stocks) | **MATCH** |
| **Task 5** | Moving Averages (`bajaj1`) | First ma20 on 2015-01-29 (2415.53), first ma50 on 2015-03-13 (2283.80) | ma20: **2415.53** \| ma50: **2283.80** \| 2018-07-31 ma20: **2918.51** | **MATCH** |
| **Task 6** | Master Table | 889 rows, 7 cols (2018-07-31: bajaj 2700.70, tvs 517.45) | 889 rows \| bajaj: **2700.70**, tvs: **517.45** | **MATCH** |
| **Task 7** | Golden Cross (`bajaj2`) | First Buy on 2015-05-18, First Sell on 2015-08-24 | First Buy: **2015-05-18** \| First Sell: **2015-08-24** | **MATCH** |
| **Task 8** | Bajaj Signal Counts | 3 rows (Buy, Hold, Sell) summing to 889 | **12 Buy, 866 Hold, 11 Sell** (Total: 889) | **MATCH** |
| **Task 9** | Single Day Signal | Signal for Bajaj on 2018-06-21 | **Buy** | **MATCH** |
| **Task 10** | All 6 Stocks in One Query | 6 rows, 5 cols; 56 Buys and 57 Sells total | 6 rows \| Total Buys: **56**, Total Sells: **57** | **MATCH** |
| **Task 11** | Who Went Up? | TVS top at +86.9%, 2 stocks negative | TVS: **+86.9%**, Eicher: **+82.6%**, TCS: **-23.8%**, Infosys: **-30.9%** | **MATCH** |
| **Task 12** | Data Trap (Worst Day) | Worst single day per stock; 2 wildly worse (-50%) | TCS: **-50.4%** (31-May-2018), Infosys: **-49.9%** (15-Jun-2015) | **MATCH** |
| **Task 13** | Fix It (Bonus Adjustment) | TCS & Infosys adjusted % changes | TCS: **+52.4%** (was -23.8%), Infosys: **+38.2%** (was -30.9%) | **MATCH** |

---

## Detailed Task Implementations

### Task 5: Moving Averages Calculation (`bajaj1`)
Sliding 20-day and 50-day moving averages are computed using `AVG() OVER (ORDER BY date ROWS BETWEEN n PRECEDING AND CURRENT ROW)`. Partial windows are kept `NULL` via `CASE WHEN ROW_NUMBER() >= n`:

```sql
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
```

---

### Task 7: Golden Cross Signal Generation (`bajaj2`)
Crossover signals are generated by comparing today's moving averages (`ma20`, `ma50`) against yesterday's moving averages (`prev_ma20`, `prev_ma50`) retrieved using `LAG()` inside a CTE:

```sql
DROP TABLE IF EXISTS bajaj2;
CREATE TABLE bajaj2 AS
WITH t AS (
    SELECT 
        date, close_price, ma20, ma50,
        LAG(ma20) OVER (ORDER BY date) AS prev_ma20,
        LAG(ma50) OVER (ORDER BY date) AS prev_ma50
    FROM bajaj1
)
SELECT 
    date, close_price,
    CASE
        WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
        WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
        WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
        ELSE 'Hold'
    END AS signal
FROM t;
```

---

### Task 10: Unified 6-Stock Analysis Pipeline
Single query calculating buy/sell counts and latest signal for all six stocks simultaneously using CTE chaining and `ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date DESC)`:

```sql
WITH prices AS (
    SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
    UNION ALL SELECT 'Eicher Motors', date, close_price FROM eicher_motors
    UNION ALL SELECT 'Hero Motocorp', date, close_price FROM hero_motocorp
    UNION ALL SELECT 'Infosys', date, close_price FROM infosys
    UNION ALL SELECT 'TCS', date, close_price FROM tcs
    UNION ALL SELECT 'TVS Motors', date, close_price FROM tvs_motors
),
ma AS (
    SELECT stock, date, close_price,
        CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20 
             THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
        CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50 
             THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
    FROM prices
),
lagged AS (
    SELECT stock, date, close_price, ma20, ma50,
        LAG(ma20) OVER (PARTITION BY stock ORDER BY date) AS prev_ma20,
        LAG(ma50) OVER (PARTITION BY stock ORDER BY date) AS prev_ma50
    FROM ma
),
sig AS (
    SELECT stock, date, close_price,
        CASE
            WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
            WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
            WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
            ELSE 'Hold'
        END AS signal
    FROM lagged
),
latest AS (
    SELECT stock, date AS last_signal_date, signal AS last_signal,
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
```

---

### Task 13: Corporate Action Adjustment (`adjusted`)
Adjusting TCS (1:1 bonus on 2018-05-31) and Infosys (1:1 bonus on 2015-06-15) pre-event prices by dividing by 2:

```sql
WITH adjusted AS (
    SELECT 'TCS' AS stock, date,
        CASE WHEN date < '2018-05-31' THEN close_price / 2.0 ELSE close_price END AS adj_close
    FROM tcs
    UNION ALL
    SELECT 'Infosys' AS stock, date,
        CASE WHEN date < '2015-06-15' THEN close_price / 2.0 ELSE close_price END AS adj_close
    FROM infosys
)
SELECT 
    stock,
    ROUND(100.0 * (MAX(CASE WHEN date = '2018-07-31' THEN adj_close END) / MAX(CASE WHEN date = '2015-01-01' THEN adj_close END) - 1), 1) AS adjusted_pct_change
FROM adjusted
GROUP BY stock
ORDER BY stock;
```

---

## Methodological Limitations & Real-World Investor Caveats

1. **Moving Average Lag:** SMA indicators Confirmation-based rather than predictive. A Golden Cross fires 2–4 weeks *after* a trend reversal starts, missing exact bottoms and tops.
2. **Sideways Whipsaws:** During horizontal consolidation, moving averages cross repeatedly, producing rapid Buy/Sell signal flips that erode capital via transaction costs.
3. **Missing Real-World Factors:** Raw daily closing prices exclude:
   - **Cash Dividends:** Understates total return on high-dividend yield stocks.
   - **Transaction Costs & STT:** Brokerage, taxes, and slippage reduce net profits on 113 total trade executions.
   - **Benchmark Indices:** Alpha must be evaluated against the Nifty 50 or Sensex index.
