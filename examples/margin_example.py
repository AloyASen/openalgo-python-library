#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenAlgo Margin Calculation Examples

This script demonstrates how to use the margin() function to calculate
margin requirements for single and multiple positions.
"""

from openalgo import api

# Initialize the API client
client = api(api_key="your_api_key_here", host="http://127.0.0.1:5000")

def test_single_stock_margin():
    """Example: Calculate margin for a single stock purchase"""
    print("\n=== Single Stock Margin Calculation ===")

    result = client.margin(positions=[{
        "symbol": "SBIN",
        "exchange": "NSE",
        "action": "BUY",
        "product": "CNC",  # Cash and Carry (Delivery)
        "pricetype": "LIMIT",
        "quantity": "10",
        "price": "750.50"
    }])

    if result['status'] == 'success':
        print(f"Total Margin Required: ₹{result['data']['total_margin_required']}")
        if 'span_margin' in result['data']:
            print(f"SPAN Margin: ₹{result['data']['span_margin']}")
        if 'exposure_margin' in result['data']:
            print(f"Exposure Margin: ₹{result['data']['exposure_margin']}")
    else:
        print(f"Error: {result['message']}")

def test_futures_margin():
    """Example: Calculate margin for futures trading"""
    print("\n=== Futures Margin Calculation ===")

    result = client.margin(positions=[{
        "symbol": "NIFTY30DEC25FUT",
        "exchange": "NFO",
        "action": "BUY",
        "product": "NRML",  # Normal (F&O - Carry Forward)
        "pricetype": "LIMIT",
        "quantity": "75",  # NIFTY lot size
        "price": "26050.00"
    }])

    if result['status'] == 'success':
        print(f"Total Margin Required: ₹{result['data']['total_margin_required']}")
        if 'span_margin' in result['data']:
            print(f"SPAN Margin: ₹{result['data']['span_margin']}")
        if 'exposure_margin' in result['data']:
            print(f"Exposure Margin: ₹{result['data']['exposure_margin']}")
    else:
        print(f"Error: {result['message']}")

def test_options_spread():
    """Example: Calculate margin for an options spread (Short Straddle)"""
    print("\n=== Options Spread Margin Calculation (Short Straddle) ===")

    result = client.margin(positions=[
        {
            "symbol": "NIFTY30DEC2526000CE",
            "exchange": "NFO",
            "action": "SELL",  # Selling Call
            "product": "NRML",
            "pricetype": "LIMIT",
            "quantity": "75",
            "price": "150.00"
        },
        {
            "symbol": "NIFTY30DEC2526000PE",
            "exchange": "NFO",
            "action": "SELL",  # Selling Put
            "product": "NRML",
            "pricetype": "LIMIT",
            "quantity": "75",
            "price": "125.00"
        }
    ])

    if result['status'] == 'success':
        print(f"Total Margin Required: ₹{result['data']['total_margin_required']}")
        print("Note: Margin benefit applied for hedged positions")
        if 'span_margin' in result['data']:
            print(f"SPAN Margin: ₹{result['data']['span_margin']}")
        if 'exposure_margin' in result['data']:
            print(f"Exposure Margin: ₹{result['data']['exposure_margin']}")
    else:
        print(f"Error: {result['message']}")

def test_iron_condor():
    """Example: Calculate margin for Iron Condor strategy (4 legs)"""
    print("\n=== Iron Condor Strategy Margin Calculation ===")

    result = client.margin(positions=[
        {
            "symbol": "NIFTY30DEC2526500CE",  # Sell higher Call
            "exchange": "NFO",
            "action": "SELL",
            "product": "NRML",
            "pricetype": "LIMIT",
            "quantity": "75",
            "price": "50.00"
        },
        {
            "symbol": "NIFTY30DEC2527000CE",  # Buy even higher Call
            "exchange": "NFO",
            "action": "BUY",
            "product": "NRML",
            "pricetype": "LIMIT",
            "quantity": "75",
            "price": "25.00"
        },
        {
            "symbol": "NIFTY30DEC2525500PE",  # Sell lower Put
            "exchange": "NFO",
            "action": "SELL",
            "product": "NRML",
            "pricetype": "LIMIT",
            "quantity": "75",
            "price": "45.00"
        },
        {
            "symbol": "NIFTY30DEC2525000PE",  # Buy even lower Put
            "exchange": "NFO",
            "action": "BUY",
            "product": "NRML",
            "pricetype": "LIMIT",
            "quantity": "75",
            "price": "20.00"
        }
    ])

    if result['status'] == 'success':
        print(f"Total Margin Required: ₹{result['data']['total_margin_required']}")
        print("Note: Significant margin benefit for this hedged strategy")
        if 'span_margin' in result['data']:
            print(f"SPAN Margin: ₹{result['data']['span_margin']}")
        if 'exposure_margin' in result['data']:
            print(f"Exposure Margin: ₹{result['data']['exposure_margin']}")
    else:
        print(f"Error: {result['message']}")

def test_intraday_margin():
    """Example: Calculate margin for intraday trading with MIS product"""
    print("\n=== Intraday (MIS) Margin Calculation ===")

    result = client.margin(positions=[{
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "action": "BUY",
        "product": "MIS",  # Margin Intraday Square-off
        "pricetype": "MARKET",
        "quantity": "100"
        # price is "0" by default for MARKET orders
    }])

    if result['status'] == 'success':
        print(f"Total Margin Required: ₹{result['data']['total_margin_required']}")
        print("Note: MIS provides leverage, requiring less margin than CNC")
        if 'span_margin' in result['data']:
            print(f"SPAN Margin: ₹{result['data']['span_margin']}")
        if 'exposure_margin' in result['data']:
            print(f"Exposure Margin: ₹{result['data']['exposure_margin']}")
    else:
        print(f"Error: {result['message']}")

def test_stop_loss_order():
    """Example: Calculate margin for a stop-loss order"""
    print("\n=== Stop Loss Order Margin Calculation ===")

    result = client.margin(positions=[{
        "symbol": "BANKNIFTY30DEC2548000CE",
        "exchange": "NFO",
        "action": "BUY",
        "product": "MIS",
        "pricetype": "SL",  # Stop Loss Limit
        "quantity": "35",  # BANKNIFTY lot size
        "price": "300.00",
        "trigger_price": "295.00"
    }])

    if result['status'] == 'success':
        print(f"Total Margin Required: ₹{result['data']['total_margin_required']}")
        if 'span_margin' in result['data']:
            print(f"SPAN Margin: ₹{result['data']['span_margin']}")
        if 'exposure_margin' in result['data']:
            print(f"Exposure Margin: ₹{result['data']['exposure_margin']}")
    else:
        print(f"Error: {result['message']}")

def main():
    """Run all margin calculation examples"""
    print("=" * 60)
    print("OpenAlgo Margin Calculator Examples")
    print("=" * 60)

    # Run examples
    test_single_stock_margin()
    test_futures_margin()
    test_options_spread()
    test_iron_condor()
    test_intraday_margin()
    test_stop_loss_order()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()