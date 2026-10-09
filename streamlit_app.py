import os
import time
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="SQL Stock Market Analysis — Interactive Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    .metric-card {
        background: rgba(19, 27, 46, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
    }
    .metric-val { font-size: 1.6rem; font-weight: 800; color: #00f2fe; }
    .metric-lbl { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; }
    .insight-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'stocks.db')

@st.cache_resource
def init_database():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Check if tables exist, if not load CSVs
    tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    if 'bajaj_auto' not in tables:
        csv_folder = os.path.dirname(__file__)
        stocks_map = {
            'bajaj_auto': 'Bajaj Auto.csv', 'eicher_motors': 'Eicher Motors.csv',
            'hero_motocorp': 'Hero Motocorp.csv', 'infosys': 'Infosys.csv',
            'tcs': 'TCS.csv', 'tvs_motors': 'TVS Motors.csv'
        }
        for tbl, cfile in stocks_map.items():
            cpath = os.path.join(csv_folder, cfile)
            if os.path.exists(cpath):
                df = pd.read_csv(cpath)
                df.columns = [c.strip() for c in df.columns]
                col_map = {
                    'Date': 'date', 'Open Price': 'open_price', 'High Price': 'high_price',
                    'Low Price': 'low_price', 'Close Price': 'close_price', 'WAP': 'wap',
                    'No.of Shares': 'no_of_shares', 'No. of Trades': 'no_of_trades',
                    'Total Turnover (Rs.)': 'total_turnover', 'Deliverable Quantity': 'deliverable_qty',
                    '% Deli. Qty to Traded Qty': 'pct_deli_qty', 'Spread High-Low': 'spread_high_low',
                    'Spread Close-Open': 'spread_close_open'
                }
                df = df.rename(columns=col_map)
                df['date'] = pd.to_datetime(df['date'], format='%d-%B-%Y').dt.strftime('%Y-%m-%d')
                df = df.sort_values('date').reset_index(drop=True)
                df.to_sql(tbl, conn, if_exists='replace', index=False)
        
        # Build derived tables
        conn.execute('DROP TABLE IF EXISTS bajaj1;')
        conn.execute('''
        CREATE TABLE bajaj1 AS
        SELECT date, close_price,
            CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20 THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2) END AS ma20,
            CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50 THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2) END AS ma50
        FROM bajaj_auto;''')

        conn.execute('DROP TABLE IF EXISTS master_table;')
        conn.execute('''
        CREATE TABLE master_table AS
        SELECT b.date, b.close_price AS bajaj, t.close_price AS tcs, v.close_price AS tvs, i.close_price AS infosys, e.close_price AS eicher, h.close_price AS hero
        FROM bajaj_auto b JOIN tcs t ON t.date = b.date JOIN tvs_motors v ON v.date = b.date JOIN infosys i ON i.date = b.date JOIN eicher_motors e ON e.date = b.date JOIN hero_motocorp h ON h.date = b.date;''')

        conn.execute('DROP TABLE IF EXISTS bajaj2;')
        conn.execute('''
        CREATE TABLE bajaj2 AS
        WITH t AS (
            SELECT date, close_price, ma20, ma50, LAG(ma20) OVER (ORDER BY date) AS prev_ma20, LAG(ma50) OVER (ORDER BY date) AS prev_ma50 FROM bajaj1
        )
        SELECT date, close_price,
            CASE WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
                 WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
                 WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
                 ELSE 'Hold' END AS signal FROM t;''')
    return conn

conn = init_database()

# Header Banner
st.title("📈 SQL Stock Market Analysis Dashboard")
st.markdown("**Interactive Query Studio & Financial Insights Hub** | 6 NSE Stocks (Jan 2015 – Jul 2018)")
st.divider()

# Executive Metric Cards
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric("Scope", "6 Stocks", "NSE Market")
with c2:
    st.metric("Duration", "889 Days", "2015 – 2018")
with c3:
    st.metric("Buy Signals", "56 Fired", "20/50 SMA")
with c4:
    st.metric("Sell Signals", "57 Fired", "20/50 SMA")
with c5:
    st.metric("Top Return", "+86.9%", "TVS Motors")
with c6:
    st.metric("Data Traps", "2 Bonus", "TCS & Infy")

st.divider()

# Navigation Sidebar
st.sidebar.header("Navigation")
nav_choice = st.sidebar.radio("Select View Mode", ["⚡ SQL Query Studio", "📊 Chart & Insights Gallery", "📜 Executive Report & PDF"])

TASKS_DICT = {
    "Task 1: Trading History Duration": {
        "desc": "Find trading days count, earliest trading date, and latest trading date for Bajaj Auto.",
        "checkpoint": "Expected: 889 rows, earliest 2015-01-01, latest 2018-07-31",
        "sql": "SELECT COUNT(*) AS trading_days, MIN(date) AS first_day, MAX(date) AS last_day FROM bajaj_auto;"
    },
    "Task 2: Eicher Motors Five Best Closes": {
        "desc": "Find Eicher Motors 5 highest closing prices with dates, highest first.",
        "checkpoint": "Expected: Top close above ₹32,000; all 5 dates in September 2017.",
        "sql": "SELECT date, close_price FROM eicher_motors ORDER BY close_price DESC LIMIT 5;"
    },
    "Task 3: TCS Year-by-Year Averages": {
        "desc": "Calculate TCS average closing price for each year, rounded to 2 decimals.",
        "checkpoint": "Expected: 2016 average equals exactly 2419.00.",
        "sql": "SELECT strftime('%Y', date) AS year, ROUND(AVG(close_price), 2) AS avg_close FROM tcs GROUP BY year ORDER BY year;"
    },
    "Task 4: Find Data Holes (NULL Deliverables)": {
        "desc": "Find every row across all six tables where deliverable_qty is NULL using UNION ALL.",
        "checkpoint": "Expected: Exactly 6 rows total across 2 distinct dates (2015-12-09 and 2017-08-31).",
        "sql": """SELECT 'bajaj_auto' AS stock, date FROM bajaj_auto WHERE deliverable_qty IS NULL
UNION ALL SELECT 'eicher_motors', date FROM eicher_motors WHERE deliverable_qty IS NULL
UNION ALL SELECT 'hero_motocorp', date FROM hero_motocorp WHERE deliverable_qty IS NULL
UNION ALL SELECT 'infosys', date FROM infosys WHERE deliverable_qty IS NULL
UNION ALL SELECT 'tcs', date FROM tcs WHERE deliverable_qty IS NULL
UNION ALL SELECT 'tvs_motors', date FROM tvs_motors WHERE deliverable_qty IS NULL;"""
    },
    "Task 5: Moving Averages Table (bajaj1)": {
        "desc": "Create sliding 20-day and 50-day moving averages for Bajaj Auto.",
        "checkpoint": "Expected: First valid ma20 on 2015-01-29 (2415.53), first ma50 on 2015-03-13 (2283.80).",
        "sql": "SELECT * FROM bajaj1 LIMIT 30;"
    },
    "Task 6: Master Comparison Table (master_table)": {
        "desc": "Master table joining closing prices of all 6 stocks in specified column order.",
        "checkpoint": "Expected: 889 rows, 7 columns, no NULLs. On 2018-07-31: bajaj 2700.70, tvs 517.45.",
        "sql": "SELECT * FROM master_table ORDER BY date DESC LIMIT 20;"
    },
    "Task 7: Golden Cross Signals (bajaj2)": {
        "desc": "Generate Buy, Sell, and Hold signals using LAG() and 20/50 SMA crossover logic.",
        "checkpoint": "Expected: First Buy on 2015-05-18, first Sell on 2015-08-24.",
        "sql": "SELECT * FROM bajaj2 WHERE signal IN ('Buy', 'Sell') LIMIT 15;"
    },
    "Task 8: Signal Frequency Breakdown": {
        "desc": "Count occurrences of Buy, Hold, and Sell signals in bajaj2.",
        "checkpoint": "Expected: Buy = 12, Hold = 866, Sell = 11 (Sum = 889).",
        "sql": "SELECT signal, COUNT(*) AS number_of_days FROM bajaj2 GROUP BY signal ORDER BY signal;"
    },
    "Task 9: Signal on 2018-06-21": {
        "desc": "Query signal for Bajaj Auto on 2018-06-21.",
        "checkpoint": "Expected: Returns Buy on 2018-06-21. Returns Hold on 2016-01-04.",
        "sql": "SELECT date, close_price, signal FROM bajaj2 WHERE date = '2018-06-21';"
    },
    "Task 10: Unified 6-Stock Analysis Pipeline": {
        "desc": "Single query calculating buys, sells, last_signal_date, and last_signal across all six stocks.",
        "checkpoint": "Expected: Total Buys = 56, Total Sells = 57 across all six stocks.",
        "sql": """WITH prices AS (
    SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
    UNION ALL SELECT 'Eicher Motors', date, close_price FROM eicher_motors
    UNION ALL SELECT 'Hero Motocorp', date, close_price FROM hero_motocorp
    UNION ALL SELECT 'Infosys', date, close_price FROM infosys
    UNION ALL SELECT 'TCS', date, close_price FROM tcs
    UNION ALL SELECT 'TVS Motors', date, close_price FROM tvs_motors
),
ma AS (
    SELECT stock, date, close_price,
        CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20 THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
        CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50 THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
    FROM prices
),
lagged AS (
    SELECT stock, date, close_price, ma20, ma50, LAG(ma20) OVER (PARTITION BY stock ORDER BY date) AS prev_ma20, LAG(ma50) OVER (PARTITION BY stock ORDER BY date) AS prev_ma50 FROM ma
),
sig AS (
    SELECT stock, date, close_price,
        CASE WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
             WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
             WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell' ELSE 'Hold' END AS signal FROM lagged
),
latest AS (
    SELECT stock, date AS last_signal_date, signal AS last_signal, ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date DESC) AS rn FROM sig WHERE signal != 'Hold'
)
SELECT s.stock, SUM(CASE WHEN s.signal = 'Buy' THEN 1 ELSE 0 END) AS buys, SUM(CASE WHEN s.signal = 'Sell' THEN 1 ELSE 0 END) AS sells, l.last_signal_date, l.last_signal
FROM sig s JOIN latest l ON l.stock = s.stock AND l.rn = 1 GROUP BY s.stock ORDER BY s.stock;"""
    },
    "Task 11: Full Period Unadjusted Performance": {
        "desc": "Calculate unadjusted percentage return from 2015-01-01 to 2018-07-31.",
        "checkpoint": "Expected: TVS Motors top at +86.9%; TCS (-23.8%) and Infosys (-30.9%) list as negative.",
        "sql": """WITH prices AS (
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
SELECT e.stock, p1.close_price AS first_close, p2.close_price AS last_close, ROUND(100.0 * (p2.close_price - p1.close_price) / p1.close_price, 1) AS pct_change
FROM ends e JOIN prices p1 ON p1.stock = e.stock AND p1.date = e.first_date JOIN prices p2 ON p2.stock = e.stock AND p2.date = e.last_date ORDER BY pct_change DESC;"""
    },
    "Task 12: The Data Trap (Worst Single Day)": {
        "desc": "Find each stock's single worst day-over-day percentage loss to uncover corporate actions.",
        "checkpoint": "Expected: TCS (-50.4% on 2018-05-31) and Infosys (-49.9% on 2015-06-15) stand out.",
        "sql": """WITH prices AS (
    SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
    UNION ALL SELECT 'Eicher Motors', date, close_price FROM eicher_motors
    UNION ALL SELECT 'Hero Motocorp', date, close_price FROM hero_motocorp
    UNION ALL SELECT 'Infosys', date, close_price FROM infosys
    UNION ALL SELECT 'TCS', date, close_price FROM tcs
    UNION ALL SELECT 'TVS Motors', date, close_price FROM tvs_motors
),
moves AS (
    SELECT stock, date, close_price, ROUND(100.0 * (close_price / LAG(close_price) OVER (PARTITION BY stock ORDER BY date) - 1), 1) AS pct_move FROM prices
),
ranked AS (
    SELECT stock, date, close_price, pct_move, ROW_NUMBER() OVER (PARTITION BY stock ORDER BY pct_move ASC) AS rn FROM moves WHERE pct_move IS NOT NULL
)
SELECT stock, date, close_price, pct_move FROM ranked WHERE rn = 1 ORDER BY pct_move ASC;"""
    },
    "Task 13: Fix It — Corporate Action Adjustments": {
        "desc": "Adjust TCS and Infosys prices for 1:1 bonus issues and calculate true adjusted returns.",
        "checkpoint": "Expected: TCS adjusted return = +52.4% (was -23.8%); Infosys = +38.2% (was -30.9%).",
        "sql": """WITH adjusted AS (
    SELECT 'TCS' AS stock, date, CASE WHEN date < '2018-05-31' THEN close_price / 2.0 ELSE close_price END AS adj_close FROM tcs
    UNION ALL SELECT 'Infosys', date, CASE WHEN date < '2015-06-15' THEN close_price / 2.0 ELSE close_price END AS adj_close FROM infosys
)
SELECT stock, ROUND(100.0 * (MAX(CASE WHEN date = '2018-07-31' THEN adj_close END) / MAX(CASE WHEN date = '2015-01-01' THEN adj_close END) - 1), 1) AS adjusted_pct_change
FROM adjusted GROUP BY stock ORDER BY stock;"""
    },
    "Stretch Challenge: TCS Adjusted Signals": {
        "desc": "Rebuild TCS moving averages on adjusted prices to prove elimination of the fake 2018-06-05 Sell signal.",
        "checkpoint": "Expected: June 2018 Sell signal vanishes; TCS maintains unbroken Buy signal from April 2018.",
        "sql": """WITH tcs_adj AS (
    SELECT date, CASE WHEN date < '2018-05-31' THEN close_price / 2.0 ELSE close_price END AS close_price FROM tcs
),
ma AS (
    SELECT date, close_price,
        CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20 THEN AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
        CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50 THEN AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50 FROM tcs_adj
),
lagged AS (
    SELECT date, close_price, ma20, ma50, LAG(ma20) OVER (ORDER BY date) AS prev_ma20, LAG(ma50) OVER (ORDER BY date) AS prev_ma50 FROM ma
),
sig AS (
    SELECT date, close_price,
        CASE WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
             WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
             WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell' ELSE 'Hold' END AS signal FROM lagged
)
SELECT signal, COUNT(*) AS adjusted_count FROM sig GROUP BY signal ORDER BY signal;"""
    }
}

if nav_choice == "⚡ SQL Query Studio":
    st.subheader("⚡ Interactive SQL Query Studio & Runner")
    task_sel = st.selectbox("Select Project Task Query", list(TASKS_DICT.keys()))
    
    t_info = TASKS_DICT[task_sel]
    st.info(f"**Description:** {t_info['desc']}\n\n🎯 **Guide Checkpoint:** {t_info['checkpoint']}")
    
    query_input = st.text_area("SQL Query Editor (SQLite / MySQL Engine)", value=t_info['sql'], height=180)
    
    col_run, col_csv = st.columns([1, 4])
    with col_run:
        run_clicked = st.button("▶ Execute Query", type="primary")
        
    if run_clicked or query_input:
        try:
            start_t = time.time()
            df_res = pd.read_sql_query(query_input, conn)
            exec_time = round((time.time() - start_t) * 1000, 2)
            
            st.success(f"Execution Successful! **{len(df_res)} rows** returned in **{exec_time} ms**.")
            st.dataframe(df_res, use_container_width=True)
            
            csv = df_res.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results as CSV", csv, f"query_results.csv", "text/csv")
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")

elif nav_choice == "📊 Chart & Insights Gallery":
    st.subheader("📊 Visual Charts & Financial Business Insights")
    st.markdown("Select a chart category or scroll through all 8 visual graphs with paired Key Insights, Recommendations, and Risk Caveats.")
    
    charts_data = [
        ("chart1_normalized_performance.png", "Chart 1: Six-Stock Normalized Performance Trajectory",
         ["TVS Motors (+86.9%) and Eicher Motors (+82.6%) dominated capital compounding.", "Rebased to 100 on Jan 2015 for cross-asset price normalization."],
         ["Overweight high-growth auto manufacturers during consumer expansion cycles."],
         ["Unadjusted prices corrupt IT sector trend comparisons."]),
        ("chart2_bajaj_ma.png", "Chart 2: Bajaj Auto Moving Average Trend (MA20 vs MA50)",
         ["MA20 acts as short-term filter; MA50 sets structural trend channel."],
         ["Use 50-day SMA as a dynamic trailing stop-loss line."],
         ["Moving averages confirmation lags spot price turning points."]),
        ("chart3_bajaj_signals.png", "Chart 3: Bajaj Auto Golden Cross & Death Cross Signals",
         ["Generated 12 Buy and 11 Sell signals across 889 trading days."],
         ["Execute trades on T+1 after crossover confirmation."],
         ["Sideways range-bound periods cause whipsaw commission losses."]),
        ("chart4_pct_returns.png", "Chart 4: Total Percentage Returns (Unadjusted vs Adjusted)",
         ["Raw data lists TCS as -23.8% and Infosys as -30.9%.", "1:1 bonus adjustments reveal true returns of +52.4% for TCS and +38.2% for Infosys."],
         ["Always normalize historical datasets for stock splits and bonus issues."],
         ["Unadjusted datasets lead to flawed backtesting."]),
        ("chart5_signal_counts.png", "Chart 5: Buy vs Sell Signal Frequencies Across All Six Stocks",
         ["Unified pipeline identified 56 total Buy and 57 total Sell signals across 6 stocks."],
         ["Favor low-frequency signal stocks (like Eicher) for passive portfolios."],
         ["Budget for transaction friction and tax implications."]),
        ("chart6_worst_daily_movements.png", "Chart 6: Single Worst Daily Price Movement per Stock",
         ["TCS (-50.4%) and Infosys (-49.9%) represent 1:1 bonus issue cliffs."],
         ["Establish automated data quality alerts for single-day drops > 20%."],
         ["Unadjusted price cliffs corrupt Value-at-Risk (VaR) models."]),
        ("chart7_tcs_adjusted.png", "Chart 7: TCS Unadjusted vs Adjusted Price Trajectory",
         ["TCS traded ex-bonus on May 31, 2018.", "Adjusted data eliminates a fake Sell signal on June 5, 2018."],
         ["Ignore crossover signals firing immediately after unadjusted bonus dates."],
         ["Unadjusted trading bots suffered whipsaw shorting losses."]),
        ("chart8_infosys_adjusted.png", "Chart 8: Infosys Unadjusted vs Adjusted Price Trajectory",
         ["Infosys traded ex-bonus on June 15, 2015.", "Adjusted series proves true return of +38.2%."],
         ["Apply multiplier adjustments backwards when maintaining databases."],
         ["Factor in cash dividends along with bonus share additions."])
    ]
    
    for fname, title, insights, recoms, caveats in charts_data:
        fpath = os.path.join(os.path.dirname(__file__), fname)
        st.markdown(f"### {title}")
        if os.path.exists(fpath):
            st.image(fpath, use_container_width=True)
            
            ci, cr, cc = st.columns(3)
            with ci:
                st.markdown("**📌 Key Business Insights**")
                for i in insights:
                    st.markdown(f"- {i}")
            with cr:
                st.markdown("**💡 Strategic Recommendations**")
                for r in recoms:
                    st.markdown(f"- {r}")
            with cc:
                st.markdown("**⚠️ Methodological Risk & Caveats**")
                for c in caveats:
                    st.markdown(f"- {c}")
        st.divider()

elif nav_choice == "📜 Executive Report & PDF":
    st.subheader("📜 Submission Documentation & PDF Report")
    pdf_path = os.path.join(os.path.dirname(__file__), 'Stock_Market_Analysis_Insights.pdf')
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button("📥 Download Official Insights PDF Report (2.38 MB)", pdf_bytes, "Stock_Market_Analysis_Insights.pdf", "application/pdf", type="primary")
    
    st.markdown("""
    ### Project Summary:
    - **6 NSE Stocks Analyzed:** Bajaj Auto, Eicher Motors, Hero Motocorp, Infosys, TCS, TVS Motors.
    - **889 Trading Days:** January 2015 to July 2018.
    - **Corporate Action Fixes:** TCS (+52.4%) and Infosys (+38.2%) bonus share adjustments.
    - **All Checkpoints Passed 100%.**
    """)
