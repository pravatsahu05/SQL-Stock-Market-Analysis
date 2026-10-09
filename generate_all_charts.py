import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

os_dir = r'd:\Coding Programs\SQL Stock Market Analysis'
csv_folder = r'C:\Users\Pravat\Downloads'
db_path = os.path.join(os_dir, 'stocks.db')

conn = sqlite3.connect(db_path)

# Ensure base stock tables are loaded
stocks_map = {
    'bajaj_auto': 'Bajaj Auto.csv',
    'eicher_motors': 'Eicher Motors.csv',
    'hero_motocorp': 'Hero Motocorp.csv',
    'infosys': 'Infosys.csv',
    'tcs': 'TCS.csv',
    'tvs_motors': 'TVS Motors.csv'
}

for table_name, csv_name in stocks_map.items():
    csv_path = os.path.join(csv_folder, csv_name)
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
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
        df.to_sql(table_name, conn, if_exists='replace', index=False)

# Build helper tables in SQLite
conn.execute('DROP TABLE IF EXISTS bajaj1;')
conn.execute('''
CREATE TABLE bajaj1 AS
SELECT
    date,
    close_price,
    CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20 
         THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
    END AS ma20,
    CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50 
         THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2)
    END AS ma50
FROM bajaj_auto;
''')

conn.execute('DROP TABLE IF EXISTS master_table;')
conn.execute('''
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
''')

conn.execute('DROP TABLE IF EXISTS bajaj2;')
conn.execute('''
CREATE TABLE bajaj2 AS
WITH t AS (
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
FROM t;
''')

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#bdc3c7'
plt.rcParams['axes.linewidth'] = 0.8

PRIMARY = '#1a2a3a'
SECONDARY = '#2980b9'
ACCENT_GREEN = '#27ae60'
ACCENT_RED = '#c0392b'

# ----------------------------------------------------------------------------
# Chart 1: Six-stock Normalized Performance (Rebased to 100 on 2015-01-01)
# ----------------------------------------------------------------------------
df_master = pd.read_sql_query('SELECT * FROM master_table ORDER BY date', conn)
df_master['date'] = pd.to_datetime(df_master['date'])

fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
for col in ['bajaj', 'tcs', 'tvs', 'infosys', 'eicher', 'hero']:
    norm = (df_master[col] / df_master[col].iloc[0]) * 100
    ax.plot(df_master['date'], norm, label=col.upper(), linewidth=1.5)

ax.axhline(100, color='black', linestyle='--', linewidth=1, alpha=0.7)
ax.set_title('Chart 1: Six-Stock Normalized Performance Trajectory (Rebased to 100 on Jan 2015)', fontsize=12, fontweight='bold', pad=15)
ax.set_ylabel('Rebased Index (Base = 100)', fontsize=10, fontweight='bold')
ax.legend(loc='upper left', frameon=True, facecolor='white', ncol=3)
plt.tight_layout()
plt.savefig(os.path.join(os_dir, 'chart1_normalized_performance.png'))
plt.close()

# ----------------------------------------------------------------------------
# Chart 2: Bajaj Close Price + MA20 + MA50
# ----------------------------------------------------------------------------
df_b1 = pd.read_sql_query('SELECT * FROM bajaj1 ORDER BY date', conn)
df_b1['date'] = pd.to_datetime(df_b1['date'])

fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
ax.plot(df_b1['date'], df_b1['close_price'], label='Bajaj Close Price', color='#7f8c8d', alpha=0.5, linewidth=1)
ax.plot(df_b1['date'], df_b1['ma20'], label='20-Day SMA (ma20)', color=SECONDARY, linewidth=1.5)
ax.plot(df_b1['date'], df_b1['ma50'], label='50-Day SMA (ma50)', color='#d35400', linewidth=1.5)

ax.set_title('Chart 2: Bajaj Auto Close Price & Sliding Moving Averages (MA20 vs MA50)', fontsize=12, fontweight='bold', pad=15)
ax.set_ylabel('Price (₹)', fontsize=10, fontweight='bold')
ax.legend(loc='upper left', frameon=True, facecolor='white')
plt.tight_layout()
plt.savefig(os.path.join(os_dir, 'chart2_bajaj_ma.png'))
plt.close()

# ----------------------------------------------------------------------------
# Chart 3: Bajaj Buy/Sell Signal Crossover Chart
# ----------------------------------------------------------------------------
df_b2 = pd.read_sql_query('SELECT * FROM bajaj2 ORDER BY date', conn)
df_b2['date'] = pd.to_datetime(df_b2['date'])

fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
ax.plot(df_b1['date'], df_b1['ma20'], label='20-Day SMA', color=SECONDARY, linewidth=1.5)
ax.plot(df_b1['date'], df_b1['ma50'], label='50-Day SMA', color='#d35400', linewidth=1.5)

buys = df_b2[df_b2['signal'] == 'Buy']
sells = df_b2[df_b2['signal'] == 'Sell']

ax.scatter(buys['date'], buys['close_price'], marker='^', color=ACCENT_GREEN, s=90, label='Golden Cross (Buy)', zorder=5)
ax.scatter(sells['date'], sells['close_price'], marker='v', color=ACCENT_RED, s=90, label='Death Cross (Sell)', zorder=5)

ax.set_title('Chart 3: Bajaj Auto Golden Cross & Death Cross Technical Crossover Signals', fontsize=12, fontweight='bold', pad=15)
ax.set_ylabel('Price (₹)', fontsize=10, fontweight='bold')
ax.legend(loc='upper left', frameon=True, facecolor='white')
plt.tight_layout()
plt.savefig(os.path.join(os_dir, 'chart3_bajaj_signals.png'))
plt.close()

# ----------------------------------------------------------------------------
# Chart 4: Stock Percentage Returns (Unadjusted vs Adjusted Bar Chart)
# ----------------------------------------------------------------------------
stocks = ['TVS Motors', 'Eicher Motors', 'TCS', 'Infosys', 'Bajaj Auto', 'Hero Motocorp']
unadj_returns = [86.9, 82.6, -23.8, -30.9, 10.0, 6.0]
adj_returns = [86.9, 82.6, 52.4, 38.2, 10.0, 6.0]

x = np.arange(len(stocks))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)
rects1 = ax.bar(x - width/2, unadj_returns, width, label='Unadjusted Return (%)', color='#e74c3c')
rects2 = ax.bar(x + width/2, adj_returns, width, label='Corporate-Adjusted Return (%)', color='#2ecc71')

ax.set_ylabel('Percentage Change (%)', fontsize=10, fontweight='bold')
ax.set_title('Chart 4: Total Percentage Returns Across All Six NSE Stocks (2015-2018)', fontsize=12, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(stocks, fontsize=9, fontweight='bold')
ax.legend(frameon=True, facecolor='white')
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')

for rect in rects1:
    h = rect.get_height()
    ax.annotate(f'{h:.1f}%', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3 if h >= 0 else -12),
                textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

for rect in rects2:
    h = rect.get_height()
    ax.annotate(f'{h:.1f}%', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3 if h >= 0 else -12),
                textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(os_dir, 'chart4_pct_returns.png'))
plt.close()

# ----------------------------------------------------------------------------
# Chart 5: Buy vs Sell Signal Counts Across All Six Stocks
# ----------------------------------------------------------------------------
df_sig_all = pd.DataFrame({
    'Stock': ['Bajaj Auto', 'Eicher Motors', 'Hero Motocorp', 'Infosys', 'TCS', 'TVS Motors'],
    'Buys': [12, 6, 9, 9, 12, 8],
    'Sells': [11, 7, 9, 9, 13, 8]
})

fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
x = np.arange(len(df_sig_all['Stock']))
rects1 = ax.bar(x - width/2, df_sig_all['Buys'], width, label='Buy Signals', color='#27ae60')
rects2 = ax.bar(x + width/2, df_sig_all['Sells'], width, label='Sell Signals', color='#c0392b')

ax.set_ylabel('Number of Fired Signals', fontsize=10, fontweight='bold')
ax.set_title('Chart 5: Total Buy vs Sell Signal Frequencies Across All Six Stocks', fontsize=12, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(df_sig_all['Stock'], fontsize=9, fontweight='bold')
ax.legend(frameon=True, facecolor='white')

for rect in rects1:
    h = rect.get_height()
    ax.annotate(f'{h}', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                textcoords='offset points', ha='center', fontsize=8.5, fontweight='bold')

for rect in rects2:
    h = rect.get_height()
    ax.annotate(f'{h}', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                textcoords='offset points', ha='center', fontsize=8.5, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(os_dir, 'chart5_signal_counts.png'))
plt.close()

# ----------------------------------------------------------------------------
# Chart 6: Worst Daily Movements per Stock (Highlighting Data Traps)
# ----------------------------------------------------------------------------
worst_moves = pd.DataFrame({
    'Stock': ['TCS', 'Infosys', 'TVS Motors', 'Eicher Motors', 'Bajaj Auto', 'Hero Motocorp'],
    'Pct_Move': [-50.4, -49.9, -9.7, -9.3, -9.1, -6.2],
    'Category': ['Data Trap (1:1 Bonus)', 'Data Trap (1:1 Bonus)', 'Normal Trading', 'Normal Trading', 'Normal Trading', 'Normal Trading']
})

fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
colors_bar = ['#e74c3c' if 'Data Trap' in c else '#3498db' for c in worst_moves['Category']]
bars = ax.bar(worst_moves['Stock'], worst_moves['Pct_Move'], color=colors_bar, width=0.55)

ax.set_ylabel('Single-Day Return (%)', fontsize=10, fontweight='bold')
ax.set_title('Chart 6: Single Worst Daily Price Movement per Stock (Uncovering Corporate Actions)', fontsize=12, fontweight='bold', pad=15)
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')

for bar in bars:
    h = bar.get_height()
    ax.annotate(f'{h:.1f}%', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, -12),
                textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(os_dir, 'chart6_worst_daily_movements.png'))
plt.close()

# ----------------------------------------------------------------------------
# Chart 7: Adjusted vs Unadjusted TCS Price Trajectory
# ----------------------------------------------------------------------------
df_tcs = pd.read_sql_query('SELECT date, close_price FROM tcs ORDER BY date', conn)
df_tcs['date'] = pd.to_datetime(df_tcs['date'])
df_tcs['adj_close'] = np.where(df_tcs['date'] < pd.to_datetime('2018-05-31'), df_tcs['close_price'] / 2.0, df_tcs['close_price'])

fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
ax.plot(df_tcs['date'], df_tcs['close_price'], label='Unadjusted Price (Unadjusted -50.4% Cliff)', color='#e74c3c', linestyle='--', linewidth=1.5)
ax.plot(df_tcs['date'], df_tcs['adj_close'], label='Adjusted Price (1:1 Bonus Adjusted)', color='#27ae60', linewidth=2)

ax.annotate('1:1 Bonus Issue\n(May 31, 2018)', xy=(pd.to_datetime('2018-05-31'), 1744.8), xytext=(pd.to_datetime('2017-06-01'), 1200),
            arrowprops=dict(facecolor='#c0392b', shrink=0.05, width=1.5, headwidth=8),
            fontsize=9, fontweight='bold', color='#c0392b',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fadbd8', edgecolor='#e74c3c'))

ax.set_title('Chart 7: TCS Unadjusted vs Adjusted Price Trajectory (Resolving the May 2018 Data Trap)', fontsize=12, fontweight='bold', pad=15)
ax.set_ylabel('Price (₹)', fontsize=10, fontweight='bold')
ax.legend(loc='upper left', frameon=True, facecolor='white')
plt.tight_layout()
plt.savefig(os.path.join(os_dir, 'chart7_tcs_adjusted.png'))
plt.close()

# ----------------------------------------------------------------------------
# Chart 8: Adjusted vs Unadjusted Infosys Price Trajectory
# ----------------------------------------------------------------------------
df_inf = pd.read_sql_query('SELECT date, close_price FROM infosys ORDER BY date', conn)
df_inf['date'] = pd.to_datetime(df_inf['date'])
df_inf['adj_close'] = np.where(df_inf['date'] < pd.to_datetime('2015-06-15'), df_inf['close_price'] / 2.0, df_inf['close_price'])

fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
ax.plot(df_inf['date'], df_inf['close_price'], label='Unadjusted Price (-49.9% Cliff on Jun 15, 2015)', color='#e74c3c', linestyle='--', linewidth=1.5)
ax.plot(df_inf['date'], df_inf['adj_close'], label='Adjusted Price (1:1 Bonus Adjusted)', color='#27ae60', linewidth=2)

ax.annotate('1:1 Bonus Issue\n(June 15, 2015)', xy=(pd.to_datetime('2015-06-15'), 991.1), xytext=(pd.to_datetime('2016-01-01'), 1600),
            arrowprops=dict(facecolor='#c0392b', shrink=0.05, width=1.5, headwidth=8),
            fontsize=9, fontweight='bold', color='#c0392b',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fadbd8', edgecolor='#e74c3c'))

ax.set_title('Chart 8: Infosys Unadjusted vs Adjusted Price Trajectory (Resolving June 2015 Data Trap)', fontsize=12, fontweight='bold', pad=15)
ax.set_ylabel('Price (₹)', fontsize=10, fontweight='bold')
ax.legend(loc='upper right', frameon=True, facecolor='white')
plt.tight_layout()
plt.savefig(os.path.join(os_dir, 'chart8_infosys_adjusted.png'))
plt.close()

print('All 8 charts generated successfully!')
conn.close()
