"""
Example of fetching 5-minute historical data from layr0-IMC
"""

from layr0-IMC import api
from datetime import datetime, timedelta
import pandas as pd

# Format floats to 2 decimal places
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# Initialize the API client
client = api(
    api_key="38f99d7d226cc0c3baa19dcacf0b1f049d2f68371da1dda2c97b1b63a3a9ca2e",
    host="http://127.0.0.1:5000"
)

# Set the date range (last 7 days)
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

print(f"Fetching 5-minute data for SBIN from {start_date} to {end_date}")

# Get 5-minute historical data
df = client.history(
    symbol="SBIN",
    exchange="NSE",
    interval="D",
    start_date=start_date,
    end_date=end_date
)

if isinstance(df, pd.DataFrame):
    # Print basic information
    print("\nData Overview:")
    print(f"Total Candles: {len(df)}")
    print(f"Date Range: {df.index[0]} to {df.index[-1]}")
    
    # Print first few candles
    print("\nFirst 5 candles:")
    print(df.head().to_string())
    
    # Print last few candles
    print("\nLast 5 candles:")
    print(df.tail().to_string())
    
    # Print basic statistics
    print("\nBasic Statistics:")
    print(df.describe().to_string())
    
    # Calculate some basic indicators
    df['change%'] = df['close'].pct_change() * 100
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['Volume_MA'] = df['volume'].rolling(window=20).mean()
    
    print("\nLast 5 candles with indicators:")
    cols = ['open', 'high', 'low', 'close', 'volume', 'change%', 'SMA_20', 'Volume_MA']
    print(df[cols].tail().to_string())
    
else:
    print("Error fetching data:", df.get('message', 'Unknown error'))
