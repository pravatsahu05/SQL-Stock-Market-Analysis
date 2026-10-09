import os
import time
import sqlite3
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')

DB_PATH = os.path.join(os.path.dirname(__file__), 'stocks.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Task Metadata Dictionary
TASKS_METADATA = {
    'task1': {
        'id': 'task1',
        'number': 1,
        'title': 'Task 1: Trading History Duration',
        'category': 'Part 1: Understand Data',
        'description': 'Find trading days count, earliest trading date, and latest trading date for Bajaj Auto.',
        'checkpoint': 'Expected: 889 rows, earliest 2015-01-01, latest 2018-07-31',
        'sql': """SELECT 
    COUNT(*) AS trading_days,
    MIN(date) AS first_day,
    MAX(date) AS last_day
FROM bajaj_auto;"""
    },
    'task2': {
        'id': 'task2',
        'number': 2,
        'title': "Task 2: Eicher Motors' Five Best Closes",
        'category': 'Part 1: Understand Data',
        'description': "Find Eicher Motors' 5 highest closing prices with dates, highest first.",
        'checkpoint': 'Expected: Top close above ₹32,000; all 5 dates in September 2017.',
        'sql': """SELECT 
    date, 
    close_price
FROM eicher_motors
ORDER BY close_price DESC
LIMIT 5;"""
    },
    'task3': {
        'id': 'task3',
        'number': 3,
        'title': 'Task 3: TCS Year-by-Year Averages',
        'category': 'Part 1: Understand Data',
        'description': "Calculate TCS's average closing price for each year, rounded to 2 decimals, oldest first.",
        'checkpoint': 'Expected: 2016 average equals exactly 2419.00.',
        'sql': """SELECT 
    strftime('%Y', date) AS year,
    ROUND(AVG(close_price), 2) AS avg_close
FROM tcs
GROUP BY year
ORDER BY year;"""
    },
    'task4': {
        'id': 'task4',
        'number': 4,
        'title': 'Task 4: Find Data Holes (NULL Deliverables)',
        'category': 'Part 1: Understand Data',
        'description': 'Across all six tables, return the stock name and date of every row where deliverable_qty is NULL.',
        'checkpoint': 'Expected: Exactly 6 rows total across 2 distinct dates (2015-12-09 and 2017-08-31).',
        'sql': """SELECT 'bajaj_auto' AS stock, date FROM bajaj_auto WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'eicher_motors' AS stock, date FROM eicher_motors WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'hero_motocorp' AS stock, date FROM hero_motocorp WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'infosys' AS stock, date FROM infosys WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'tcs' AS stock, date FROM tcs WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'tvs_motors' AS stock, date FROM tvs_motors WHERE deliverable_qty IS NULL;"""
    },
    'task5': {
        'id': 'task5',
        'number': 5,
        'title': 'Task 5: Moving Averages Table (bajaj1)',
        'category': 'Part 2: The Assignment',
        'description': 'Create table bajaj1 with 20-day and 50-day moving averages, nullifying incomplete windows.',
        'checkpoint': 'Expected: 889 rows, first valid ma20 on 2015-01-29 (2415.53), first ma50 on 2015-03-13 (2283.80).',
        'sql': """SELECT
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
FROM bajaj_auto
LIMIT 50;"""
    },
    'task6': {
        'id': 'task6',
        'number': 6,
        'title': 'Task 6: Master Comparison Table (master_table)',
        'category': 'Part 2: The Assignment',
        'description': 'Create master_table joining closing prices of all 6 stocks on date in exact specified column order.',
        'checkpoint': 'Expected: 889 rows, 7 columns, no NULLs. On 2018-07-31: bajaj 2700.70, tvs 517.45.',
        'sql': """SELECT
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
JOIN hero_motocorp h ON h.date = b.date
ORDER BY b.date DESC
LIMIT 20;"""
    },
    'task7': {
        'id': 'task7',
        'number': 7,
        'title': 'Task 7: Golden Cross Signals (bajaj2)',
        'category': 'Part 2: The Assignment',
        'description': 'Generate Buy, Sell, and Hold signals using LAG() and 20/50 SMA crossover logic.',
        'checkpoint': 'Expected: First Buy on 2015-05-18, first Sell on 2015-08-24.',
        'sql': """WITH t AS (
    SELECT date, close_price, ma20, ma50,
           LAG(ma20) OVER (ORDER BY date) AS prev_ma20,
           LAG(ma50) OVER (ORDER BY date) AS prev_ma50
    FROM bajaj1
)
SELECT date, close_price,
    CASE
        WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
        WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
        WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
        ELSE 'Hold'
    END AS signal
FROM t
WHERE signal IN ('Buy', 'Sell')
LIMIT 15;"""
    },
    'task8': {
        'id': 'task8',
        'number': 8,
        'title': 'Task 8: Signal Frequency Breakdown',
        'category': 'Part 2: The Assignment',
        'description': 'Count occurrences of Buy, Hold, and Sell signals in bajaj2.',
        'checkpoint': 'Expected: Buy = 12, Hold = 866, Sell = 11 (Sum = 889).',
        'sql': """SELECT 
    signal, 
    COUNT(*) AS number_of_days
FROM bajaj2
GROUP BY signal
ORDER BY signal;"""
    },
    'task9': {
        'id': 'task9',
        'number': 9,
        'title': 'Task 9: Signal on 2018-06-21',
        'category': 'Part 2: The Assignment',
        'description': 'Return the signal for Bajaj Auto on 2018-06-21.',
        'checkpoint': 'Expected: Returns Buy on 2018-06-21. Returns Hold on 2016-01-04.',
        'sql': """SELECT 
    date,
    close_price,
    signal
FROM bajaj2
WHERE date = '2018-06-21';"""
    },
    'task10': {
        'id': 'task10',
        'number': 10,
        'title': 'Task 10: Unified 6-Stock Analysis Pipeline',
        'category': 'Part 2: The Assignment',
        'description': 'Single query calculating buys, sells, last_signal_date, and last_signal across all six stocks.',
        'checkpoint': 'Expected: Total Buys = 56, Total Sells = 57 across all six stocks.',
        'sql': """WITH prices AS (
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
    FROM sig WHERE signal != 'Hold'
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
ORDER BY s.stock;"""
    },
    'task11': {
        'id': 'task11',
        'number': 11,
        'title': 'Task 11: Full Period Unadjusted Performance',
        'category': 'Part 3: Question The Result',
        'description': 'Calculate unadjusted percentage return from 2015-01-01 to 2018-07-31 for all six stocks.',
        'checkpoint': 'Expected: TVS Motors top at +86.9%; TCS (-23.8%) and Infosys (-30.9%) list as negative.',
        'sql': """WITH prices AS (
    SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
    UNION ALL SELECT 'Eicher Motors', date, close_price FROM eicher_motors
    UNION ALL SELECT 'Hero Motocorp', date, close_price FROM hero_motocorp
    UNION ALL SELECT 'Infosys', date, close_price FROM infosys
    UNION ALL SELECT 'TCS', date, close_price FROM tcs
    UNION ALL SELECT 'TVS Motors', date, close_price FROM tvs_motors
),
ends AS (
    SELECT stock, MIN(date) AS first_date, MAX(date) AS last_date FROM prices GROUP BY stock
)
SELECT 
    e.stock, 
    p1.close_price AS first_close, 
    p2.close_price AS last_close,
    ROUND(100.0 * (p2.close_price - p1.close_price) / p1.close_price, 1) AS pct_change
FROM ends e
JOIN prices p1 ON p1.stock = e.stock AND p1.date = e.first_date
JOIN prices p2 ON p2.stock = e.stock AND p2.date = e.last_date
ORDER BY pct_change DESC;"""
    },
    'task12': {
        'id': 'task12',
        'number': 12,
        'title': 'Task 12: The Data Trap (Worst Single Day)',
        'category': 'Part 3: Question The Result',
        'description': 'Find each stock\'s single worst day-over-day percentage loss to uncover corporate actions.',
        'checkpoint': 'Expected: TCS (-50.4% on 2018-05-31) and Infosys (-49.9% on 2015-06-15) stand out.',
        'sql': """WITH prices AS (
    SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
    UNION ALL SELECT 'Eicher Motors', date, close_price FROM eicher_motors
    UNION ALL SELECT 'Hero Motocorp', date, close_price FROM hero_motocorp
    UNION ALL SELECT 'Infosys', date, close_price FROM infosys
    UNION ALL SELECT 'TCS', date, close_price FROM tcs
    UNION ALL SELECT 'TVS Motors', date, close_price FROM tvs_motors
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
    FROM moves WHERE pct_move IS NOT NULL
)
SELECT stock, date, close_price, pct_move
FROM ranked WHERE rn = 1 ORDER BY pct_move ASC;"""
    },
    'task13': {
        'id': 'task13',
        'number': 13,
        'title': 'Task 13: Fix It — Corporate Action Adjustments',
        'category': 'Part 3: Question The Result',
        'description': 'Adjust TCS and Infosys prices for 1:1 bonus issues and calculate true adjusted returns.',
        'checkpoint': 'Expected: TCS adjusted return = +52.4% (was -23.8%); Infosys = +38.2% (was -30.9%).',
        'sql': """WITH adjusted AS (
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
GROUP BY stock ORDER BY stock;"""
    },
    'stretch': {
        'id': 'stretch',
        'number': 14,
        'title': 'Stretch Challenge: TCS Adjusted Signal Re-Analysis',
        'category': 'Stretch Challenge',
        'description': 'Rebuild TCS moving averages on adjusted prices to prove elimination of the fake 2018-06-05 Sell signal.',
        'checkpoint': 'Expected: June 2018 Sell signal vanishes; TCS maintains unbroken Buy signal from April 2018.',
        'sql': """WITH tcs_adj AS (
    SELECT date, CASE WHEN date < '2018-05-31' THEN close_price / 2.0 ELSE close_price END AS close_price FROM tcs
),
ma AS (
    SELECT date, close_price,
        CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20 THEN AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
        CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50 THEN AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
    FROM tcs_adj
),
lagged AS (
    SELECT date, close_price, ma20, ma50,
        LAG(ma20) OVER (ORDER BY date) AS prev_ma20,
        LAG(ma50) OVER (ORDER BY date) AS prev_ma50
    FROM ma
),
sig AS (
    SELECT date, close_price,
        CASE
            WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
            WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
            WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
            ELSE 'Hold'
        END AS signal
    FROM lagged
)
SELECT signal, COUNT(*) AS adjusted_count FROM sig GROUP BY signal ORDER BY signal;"""
    }
}

# Detailed Insights & Recommendations for all 8 Charts
CHARTS_INSIGHTS = {
    'chart1': {
        'id': 'chart1',
        'title': 'Chart 1: Six-Stock Normalized Performance Trajectory',
        'filename': 'chart1_normalized_performance.png',
        'category': 'Comparative Trend Analysis',
        'insights': [
            'TVS Motors and Eicher Motors dominated long-term capital compounding, outperforming all other stocks by a massive margin.',
            'TVS Motors surged from an initial index level of 100 on Jan 1, 2015 to 186.9 on July 31, 2018 (+86.9%).',
            'Eicher Motors followed closely, climbing to 182.6 (+82.6%) due to strong Royal Enfield market expansion.',
            'Unadjusted IT stocks (TCS and Infosys) display an apparent sharp plunge due to 1:1 bonus share splits rather than business deterioration.'
        ],
        'recommendations': [
            'Strategic Allocation: Overweight high-growth auto manufacturers (TVS & Eicher) during multi-year consumer expansion cycles.',
            'Benchmark Relative Alpha: Use normalized performance rebasing to compare assets across vastly different nominal price ranges (e.g., Eicher at ₹27,000 vs TVS at ₹500).'
        ],
        'caveats': [
            'Unadjusted raw price series distort performance rankings for stocks undergoing corporate actions.',
            'Does not account for cash dividend reinvestments.'
        ]
    },
    'chart2': {
        'id': 'chart2',
        'title': 'Chart 2: Bajaj Auto Moving Average Trend (MA20 vs MA50)',
        'filename': 'chart2_bajaj_ma.png',
        'category': 'Technical Indicators',
        'insights': [
            'The 20-day Simple Moving Average (ma20) acts as a responsive short-term trend filter, while the 50-day SMA (ma50) establishes the medium-term baseline.',
            'Bajaj Auto demonstrated a steady, upward-sloping channel over the 3.5-year period (+10.0% total gain).',
            'Incomplete initial windows (rows 1-19 for ma20, rows 1-49 for ma50) were cleanly set to NULL to prevent premature false signals.'
        ],
        'recommendations': [
            'Trend Confirmation: Wait for both MA20 and MA50 to slope in the same direction before scaling into leveraged positions.',
            'Support/Resistance: Use the 50-day SMA as a dynamic trailing stop-loss line during sustained uptrends.'
        ],
        'caveats': [
            'Moving averages lag price action by 20 to 50 trading days, confirmation occurs after momentum has already begun.'
        ]
    },
    'chart3': {
        'id': 'chart3',
        'title': 'Chart 3: Bajaj Auto Golden Cross & Death Cross Signals',
        'filename': 'chart3_bajaj_signals.png',
        'category': 'Crossover Strategy',
        'insights': [
            'Over 889 trading days, Bajaj Auto generated 12 Golden Cross (Buy) signals and 11 Death Cross (Sell) signals (866 Hold days).',
            'First Buy signal triggered on 2015-05-18 (Close ₹2,221.95); first Sell triggered on 2015-08-24 (Close ₹2,188.45).',
            'The latest signal fired was a **Buy on 2018-06-21** (Close ₹2,832.95).'
        ],
        'recommendations': [
            'Systematic Execution: Execute signals strictly on the day after crossover confirmation to eliminate emotional bias.',
            'Filter Consolidation: Implement a secondary volatility filter (e.g. ATR or ADX) to ignore crossovers occurring inside tight trading ranges.'
        ],
        'caveats': [
            'Sideways Whipsawing: During horizontal range-bound periods (e.g. late 2015), rapid signal flipping generates friction losses.'
        ]
    },
    'chart4': {
        'id': 'chart4',
        'title': 'Chart 4: Total Returns (Unadjusted vs Corporate-Adjusted)',
        'filename': 'chart4_pct_returns.png',
        'category': 'Corporate Actions',
        'insights': [
            'Raw unadjusted data lists TCS as -23.8% and Infosys as -30.9% (ranking #5 and #6 as bottom losers).',
            'Corporate action price adjustment (halving pre-event historical prices for 1:1 bonus issues) flips TCS to **+52.4%** and Infosys to **+38.2%**!',
            'Auto stocks (TVS +86.9%, Eicher +82.6%, Bajaj +10.0%, Hero +6.0%) required no bonus adjustments over this timeframe.'
        ],
        'recommendations': [
            'Mandatory Data Normalization: Always audit and adjust historical datasets for stock splits and bonus issues before evaluating performance.',
            'Portfolio Re-ranking: Re-evaluating IT sector holdings post-adjustment proves technology was a core wealth creator rather than a destroyer.'
        ],
        'caveats': [
            'Unadjusted historical data leads to flawed backtesting and inaccurate automated trading algorithm behavior.'
        ]
    },
    'chart5': {
        'id': 'chart5',
        'title': 'Chart 5: Buy vs Sell Signal Frequencies Across All Six Stocks',
        'filename': 'chart5_signal_counts.png',
        'category': 'Strategy Audit',
        'insights': [
            'Across all six stocks, the single unified SQL CTE pipeline identified **56 total Buy signals** and **57 total Sell signals**.',
            'TCS and Bajaj Auto generated the highest signal activity (12 & 12 Buys), reflecting frequent trend transitions.',
            'Eicher Motors generated the fewest signals (6 Buys, 7 Sells), confirming a strong, persistent long-term bull trend.'
        ],
        'recommendations': [
            'Turnover Management: Select lower-frequency signal stocks (like Eicher) for passive long-term accounts to minimize transaction friction.',
            'Execution Friction Budgeting: Factor in brokerage fees, STT, and slippage across the 113 total trades executed.'
        ],
        'caveats': [
            'High signal count does not equal higher profitability; range-bound stocks fire redundant signals.'
        ]
    },
    'chart6': {
        'id': 'chart6',
        'title': 'Chart 6: Single Worst Daily Price Movement per Stock',
        'filename': 'chart6_worst_daily_movements.png',
        'category': 'Risk Management & Data Quality',
        'insights': [
            'Four stocks experienced normal worst single-day market drawdowns ranging between -6.2% (Hero) and -9.7% (TVS).',
            'TCS (-50.4% on 2018-05-31) and Infosys (-49.9% on 2015-06-15) stand out as extreme single-day anomaly cliffs.',
            'These extreme cliffs represent 1:1 bonus share issues (share counts doubled while price halved).'
        ],
        'recommendations': [
            'Anomaly Detection: Set automated data quality alert thresholds for single-day drops exceeding -20% to flag corporate events.',
            'Risk Management: Distinguish technical share splits from fundamental corporate solvency crises.'
        ],
        'caveats': [
            'Raw price changes without split adjustments severely corrupt risk models such as Value-at-Risk (VaR).'
        ]
    },
    'chart7': {
        'id': 'chart7',
        'title': 'Chart 7: TCS Unadjusted vs Adjusted Price Trajectory',
        'filename': 'chart7_tcs_adjusted.png',
        'category': 'Deep Dive: TCS Data Trap',
        'insights': [
            'On May 31, 2018, TCS traded ex-bonus for its 1:1 bonus issue, causing nominal price to drop overnight from ₹3,517.75 to ₹1,744.80.',
            'Adjusting pre-event prices reveals an uninterrupted, powerful multi-year bull run climbing from ₹1,274.10 to ₹1,941.25 (+52.4%).',
            'Stretch Analysis Proof: The unadjusted price cliff triggered a **fake Death Cross (Sell) signal on 2018-06-05**. Adjusted data proves TCS remained in a strong **Buy trend from April 2018 onwards**.'
        ],
        'recommendations': [
            'Signal Filtering: Never execute crossover signals that fire immediately following unadjusted corporate action dates.',
            'Long-Term Holding: Retain core compounder positions when price drops are driven purely by share splits.'
        ],
        'caveats': [
            'Unadjusted technical trading bots would have suffered immediate whipsaw loss by shorting TCS right before a major 2018 rally.'
        ]
    },
    'chart8': {
        'id': 'chart8',
        'title': 'Chart 8: Infosys Unadjusted vs Adjusted Price Trajectory',
        'filename': 'chart8_infosys_adjusted.png',
        'category': 'Deep Dive: Infosys Data Trap',
        'insights': [
            'On June 15, 2015, Infosys traded ex-bonus for its 1:1 bonus share issue, dropping price from ₹1,976.65 to ₹991.10.',
            'Adjusting historical prices before June 15, 2015 (dividing by 2) transforms start price to ₹987.90, proving a solid +38.2% total gain.',
            'Latest signal for Infosys fired as **Buy on 2018-05-07**.'
        ],
        'recommendations': [
            'Historical Data Normalization: Apply multiplier adjustments backwards from current date when maintaining price databases.',
            'Total Return Strategy: Factor in both bonus shares and regular dividend yield when evaluating large-cap IT assets.'
        ],
        'caveats': [
            'Multiple historical splits (e.g. 2014 & 2015) require compound multiplier adjustments for multi-decade studies.'
        ]
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(list(TASKS_METADATA.values()))

@app.route('/api/query/<task_id>', methods=['GET'])
def execute_task_query(task_id):
    if task_id not in TASKS_METADATA:
        return jsonify({'error': 'Task not found'}), 404
    
    meta = TASKS_METADATA[task_id]
    sql = meta['sql']
    
    start_time = time.time()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        
        columns = [description[0] for description in cursor.description]
        rows = [list(row) for row in cursor.fetchall()]
        conn.close()
        
        exec_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            'success': True,
            'metadata': meta,
            'columns': columns,
            'rows': rows,
            'count': len(rows),
            'execution_time_ms': exec_time
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'metadata': meta
        }), 500

@app.route('/api/custom_query', methods=['POST'])
def execute_custom_query():
    data = request.get_json() or {}
    sql = data.get('sql', '').strip()
    
    if not sql:
        return jsonify({'error': 'No SQL query provided'}), 400
    
    # Basic safety check: allow SELECT and WITH queries
    first_word = sql.split()[0].upper() if sql.split() else ''
    if first_word not in ['SELECT', 'WITH', 'PRAGMA', 'EXPLAIN']:
        return jsonify({'error': 'Only SELECT / WITH read queries are allowed in custom query mode'}), 403

    start_time = time.time()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        
        columns = [description[0] for description in cursor.description] if cursor.description else []
        rows = [list(row) for row in cursor.fetchall()] if cursor.description else []
        conn.close()
        
        exec_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            'success': True,
            'columns': columns,
            'rows': rows,
            'count': len(rows),
            'execution_time_ms': exec_time
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chart_insights', methods=['GET'])
def get_chart_insights():
    return jsonify(CHARTS_INSIGHTS)

if __name__ == '__main__':
    print('Starting SQL Stock Market Analysis Web Dashboard on http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=True)
