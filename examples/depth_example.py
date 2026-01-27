"""
layr0_imc WebSocket Market Depth Example

Verbose levels:
  - verbose=False (default): Silent mode - no SDK output, only your prints
  - verbose=True or 1: Basic info - connection, auth, subscription status
  - verbose=2: Full debug - all market data updates from SDK (includes depth table)
"""

from layr0_imc import api
import time

# Initialize feed client with explicit parameters
# Set verbose=True for basic logging, verbose=2 for full debug
client = api(
    api_key="918d504f250e6f7d6b533b245a46009d3f3b8cad8e6314c8b45ae8a35b972d8a",  # Replace with your API key
    host="http://127.0.0.1:5000",  # Replace with your API host
    ws_url="ws://127.0.0.1:8765",  # Explicit WebSocket URL (can be different from REST API host)
    verbose=False  # Silent mode (default) - set to True or 2 for debugging
)

# MCX instruments for testing
instruments_list = [
    {"exchange": "MCX", "symbol": "GOLDPETAL30MAY25FUT"}
]

def on_data_received(data):
    print("Market Depth Update:")
    print(data)

# Connect and subscribe
client.connect()
client.subscribe_depth(instruments_list, on_data_received=on_data_received)

# Poll Market Depth data a few times
for i in range(100):
    print(f"\nPoll {i+1}:")
    print(client.get_depth())
    time.sleep(0.5)

# Cleanup
client.unsubscribe_depth(instruments_list)
client.disconnect()
