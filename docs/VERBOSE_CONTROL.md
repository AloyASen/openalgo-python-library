# layr0-IMC WebSocket Verbose Control

## Overview

The `verbose` parameter controls SDK logging output for WebSocket feed operations (LTP, Quote, Depth).

| Level | Value | Output |
|-------|-------|--------|
| Silent | `False` or `0` | Errors only (default) |
| Basic | `True` or `1` | Connection, auth, subscription status |
| Debug | `2` | All market data updates |

## Usage

```python
from layr0-IMC import api

# Silent mode (default) - no SDK output
client = api(api_key="...", host="...", ws_url="...", verbose=False)

# Basic logging - connection/subscription info
client = api(api_key="...", host="...", ws_url="...", verbose=True)

# Full debug - all data updates
client = api(api_key="...", host="...", ws_url="...", verbose=2)
```

## Test Example

```python
"""
Test verbose control in layr0-IMC WebSocket Feed
"""
from layr0-IMC import api
import time

# Change this to test different levels: False, True, 1, 2
VERBOSE_LEVEL = True

client = api(
    api_key="your_api_key_here",
    host="http://127.0.0.1:5000",
    ws_url="ws://127.0.0.1:8765",
    verbose=VERBOSE_LEVEL
)

instruments_list = [
    {"exchange": "NSE_INDEX", "symbol": "NIFTY"},
    {"exchange": "NSE", "symbol": "INFY"}
]

def on_data_received(data):
    # Your callback - always prints regardless of verbose
    print(f"MY CALLBACK: {data['symbol']} LTP: {data['data'].get('ltp')}")

# Connect and subscribe
print(f"\n=== Testing with verbose={VERBOSE_LEVEL} ===\n")
client.connect()
client.subscribe_quote(instruments_list, on_data_received=on_data_received)

# Poll a few times
for i in range(5):
    print(f"\n--- Poll {i+1} ---")
    quotes = client.get_quotes()
    for exch, symbols in quotes.get('quote', {}).items():
        for sym, data in symbols.items():
            print(f"  {exch}:{sym} = {data.get('ltp')}")
    time.sleep(1)

# Cleanup
client.unsubscribe_quote(instruments_list)
client.disconnect()
```

## Expected Output

### verbose=False (Silent)
```
=== Testing with verbose=False ===

MY CALLBACK: NIFTY LTP: 26008.5

--- Poll 1 ---
  NSE_INDEX:NIFTY = 26008.5
  NSE:INFY = 1531.0
```

### verbose=True (Basic)
```
=== Testing with verbose=True ===

[WS]    Connected to ws://127.0.0.1:8765
[AUTH]  Authenticating with API key: bf1267a1...7cf9169f
[AUTH]  Success | Broker: upstox | User: rajandran
[SUB]   Subscribing NSE_INDEX:NIFTY Quote...
[SUB]   NSE_INDEX:NIFTY | Mode: Quote | Status: success
[SUB]   Subscribing NSE:INFY Quote...
[SUB]   NSE:INFY | Mode: Quote | Status: success
MY CALLBACK: NIFTY LTP: 26008.5

--- Poll 1 ---
  NSE_INDEX:NIFTY = 26008.5
  NSE:INFY = 1531.0
```

### verbose=2 (Full Debug)
```
=== Testing with verbose=2 ===

[WS]    Connected to ws://127.0.0.1:8765
[AUTH]  Authenticating with API key: bf1267a1...7cf9169f
[AUTH]  Success | Broker: upstox | User: rajandran
[AUTH]  Full response: {'type': 'auth', 'status': 'success', ...}
[SUB]   Subscribing NSE_INDEX:NIFTY Quote...
[SUB]   NSE_INDEX:NIFTY | Mode: Quote | Status: success
[SUB]   Full response: {'type': 'subscribe', ...}
[QUOTE] NSE_INDEX:NIFTY      | O: 25998.5    H: 26025.5    L: 25924.15   C: 26008.5    LTP: 26008.5
MY CALLBACK: NIFTY LTP: 26008.5
[QUOTE] NSE:INFY             | O: 1549.0     H: 1550.6     L: 1525.9     C: 1531.0     LTP: 1531.0

--- Poll 1 ---
  NSE_INDEX:NIFTY = 26008.5
  NSE:INFY = 1531.0
```

## Log Categories

| Category | Description |
|----------|-------------|
| `[WS]` | WebSocket connection events |
| `[AUTH]` | Authentication status |
| `[SUB]` | Subscription requests and responses |
| `[UNSUB]` | Unsubscription events |
| `[LTP]` | LTP data updates (verbose=2) |
| `[QUOTE]` | Quote data updates (verbose=2) |
| `[DEPTH]` | Market depth updates (verbose=2) |
| `[ERROR]` | Error messages (always shown) |
