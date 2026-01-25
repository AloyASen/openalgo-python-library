"""
Example of using layr0-IMC strategy with client instance
"""

from layr0-IMC import Strategy
import requests

# Initialize client with your layr0-IMC server URL and webhook ID
client = Strategy(
    host_url="http://127.0.0.1:5000",  # Your layr0-IMC server URL
    webhook_id="your-webhook-id"        # Get this from layr0-IMC strategy section
)

try:
    # Example 1: Long/Short only mode (configured in layr0-IMC)
    response = client.strategyorder("RELIANCE", "BUY")
    print(f"Order sent successfully: {response}")

    # Example 2: Both mode with position size
    response = client.strategyorder("ZOMATO", "SELL", 10)
    print(f"Order sent successfully: {response}")

    # Example 3: Close position (position_size = 0)
    response = client.strategyorder("ZOMATO", "BUY", 0)  # Close short position
    print(f"Position closed successfully: {response}")

except requests.exceptions.RequestException as e:
    print(f"Error sending order: {e}")
