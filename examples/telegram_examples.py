"""
layr0_imc Telegram Notification API Examples

This file demonstrates how to use the Telegram notification API to send
custom alerts to Telegram users.

Prerequisites:
1. Telegram Bot must be running in layr0_imc settings
2. User must be linked using /link command in Telegram
3. Username must be your layr0_imc login username (NOT Telegram username)
"""

import layr0_imc

# Initialize the API client
# Replace with your actual API key and host
api = layr0_imc.api(
    api_key="your_api_key_here",
    host="http://127.0.0.1:5000"
)

# Replace with your layr0_imc login username
# NOTE: This is NOT your @telegram_username, it's the username you use to login to layr0_imc
USERNAME = "your_layr0_imc_username"

print("=" * 80)
print("layr0_imc Telegram Notification API Examples")
print("=" * 80)

# ============================================================================
# Example 1: Basic Notification
# ============================================================================
print("\n1. Basic Notification")
print("-" * 80)

result = api.telegram(
    username=USERNAME,
    message="NIFTY crossed 24000! Consider taking profit on long positions."
)

if result.get('status') == 'success':
    print("✅ Notification sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 2: High Priority Urgent Alert
# ============================================================================
print("\n2. High Priority Urgent Alert")
print("-" * 80)

result = api.telegram(
    username=USERNAME,
    message="🚨 URGENT: Stop loss hit on BANKNIFTY position!",
    priority=10
)

if result.get('status') == 'success':
    print("✅ Urgent alert sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 3: Multi-line Daily Trading Summary
# ============================================================================
print("\n3. Multi-line Daily Trading Summary")
print("-" * 80)

summary_message = """📊 Daily Trading Summary
─────────────────────
✅ Winning Trades: 8
❌ Losing Trades: 2
💰 Net P&L: +₹15,450
📈 Win Rate: 80%

🎯 Great day! Keep it up!"""

result = api.telegram(
    username=USERNAME,
    message=summary_message,
    priority=5
)

if result.get('status') == 'success':
    print("✅ Daily summary sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 4: Price Alert Notification
# ============================================================================
print("\n4. Price Alert Notification")
print("-" * 80)

result = api.telegram(
    username=USERNAME,
    message="🔔 Price Alert: RELIANCE reached target price ₹2,850",
    priority=8
)

if result.get('status') == 'success':
    print("✅ Price alert sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 5: Strategy Signal Alert
# ============================================================================
print("\n5. Strategy Signal Alert")
print("-" * 80)

signal_message = """📈 BUY Signal: RSI oversold on NIFTY 24000 CE
Entry: ₹145.50
Target: ₹165.00
SL: ₹138.00"""

result = api.telegram(
    username=USERNAME,
    message=signal_message,
    priority=9
)

if result.get('status') == 'success':
    print("✅ Strategy signal sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 6: Risk Management Alert
# ============================================================================
print("\n6. Risk Management Alert")
print("-" * 80)

risk_message = """⚠️ Risk Alert: Daily loss limit reached (-₹25,000)
No new positions recommended."""

result = api.telegram(
    username=USERNAME,
    message=risk_message,
    priority=10
)

if result.get('status') == 'success':
    print("✅ Risk alert sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 7: Market Update Notification
# ============================================================================
print("\n7. Market Update Notification")
print("-" * 80)

market_update = """📰 Market Update: FII bought ₹2,500 crores today
Market sentiment: Bullish
NIFTY support: 23,800"""

result = api.telegram(
    username=USERNAME,
    message=market_update,
    priority=5
)

if result.get('status') == 'success':
    print("✅ Market update sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 8: Trade Execution Confirmation
# ============================================================================
print("\n8. Trade Execution Confirmation")
print("-" * 80)

order_confirmation = """✅ Order Executed
Symbol: BANKNIFTY 48000 CE
Action: BUY
Qty: 30
Price: ₹245.75
Total: ₹7,372.50"""

result = api.telegram(
    username=USERNAME,
    message=order_confirmation,
    priority=7
)

if result.get('status') == 'success':
    print("✅ Order confirmation sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 9: Technical Indicator Alert
# ============================================================================
print("\n9. Technical Indicator Alert")
print("-" * 80)

technical_alert = """📊 Technical Alert: NIFTY
• RSI: 72 (Overbought)
• MACD: Bearish Crossover
• Support: 23,850
• Resistance: 24,150

Consider booking profits."""

result = api.telegram(
    username=USERNAME,
    message=technical_alert,
    priority=8
)

if result.get('status') == 'success':
    print("✅ Technical alert sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 10: Integration with Trading Strategy
# ============================================================================
print("\n10. Integration with Trading Strategy")
print("-" * 80)

# Simulate a trading scenario
current_price = 24150
target_price = 24200
symbol = "NIFTY"

if current_price >= target_price:
    result = api.telegram(
        username=USERNAME,
        message=f"🎯 {symbol} reached target price: ₹{current_price}",
        priority=9
    )

    if result.get('status') == 'success':
        print("✅ Target price alert sent successfully!")
    else:
        print(f"❌ Error: {result.get('message')}")
else:
    print(f"Price {current_price} has not reached target {target_price} yet.")

# ============================================================================
# Example 11: Position Update Alert
# ============================================================================
print("\n11. Position Update Alert")
print("-" * 80)

position_update = """📍 Position Update
Symbol: NIFTY 24000 PE
Entry: ₹120.50
Current: ₹145.75
P&L: +₹1,893.75 (+21%)
Status: In Profit"""

result = api.telegram(
    username=USERNAME,
    message=position_update,
    priority=6
)

if result.get('status') == 'success':
    print("✅ Position update sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

# ============================================================================
# Example 12: Weekly Performance Report
# ============================================================================
print("\n12. Weekly Performance Report")
print("-" * 80)

weekly_report = """📈 Weekly Trading Report
Week: Nov 18-22, 2024
─────────────────────
Total Trades: 45
Winners: 32
Losers: 13
Win Rate: 71.1%

Gross P&L: +₹78,450
Max Drawdown: -₹8,200
Best Trade: +₹12,300
Worst Trade: -₹3,100

Strategy Performance:
• Iron Condor: +₹45,200
• Straddle: +₹22,100
• Directional: +₹11,150

🎯 Another profitable week!"""

result = api.telegram(
    username=USERNAME,
    message=weekly_report,
    priority=5
)

if result.get('status') == 'success':
    print("✅ Weekly report sent successfully!")
else:
    print(f"❌ Error: {result.get('message')}")

print("\n" + "=" * 80)
print("Examples completed!")
print("=" * 80)
print("\nNote: Make sure to:")
print("1. Replace USERNAME with your layr0_imc login username")
print("2. Replace api_key with your actual API key")
print("3. Ensure Telegram bot is running in layr0_imc settings")
print("4. Ensure you've linked your account using /link command in Telegram")
print("=" * 80)
