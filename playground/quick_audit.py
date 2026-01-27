#!/usr/bin/env python3
"""
Quick Speed Audit for Key layr0_imc Technical Indicators
Tests a representative sample of indicators to verify functionality and performance
"""

import numpy as np
import pandas as pd
import time
import sys
import os
from datetime import datetime

# Add the parent directory to Python path to import layr0_imc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layr0_imc import ta

def generate_realistic_data(size: int) -> dict:
    """Generate realistic OHLCV data for testing"""
    np.random.seed(42)  # For reproducible results
    
    base_price = 100.0
    base_volume = 1000000
    
    data = {
        'open': [],
        'high': [],
        'low': [],
        'close': [],
        'volume': []
    }
    
    for i in range(size):
        # Generate price with trend and noise
        trend = 0.0001 * np.sin(i / 100)  # Long-term sine wave trend
        noise = np.random.normal(0, 0.02)  # 2% daily volatility
        
        if i == 0:
            close = base_price
            open_price = base_price
        else:
            daily_return = trend + noise
            open_price = data['close'][-1]
            close = open_price * (1 + daily_return)
        
        # Generate realistic OHLC from close
        daily_range = abs(np.random.normal(0, 0.015)) * close
        high = close + daily_range * np.random.uniform(0.2, 0.8)
        low = close - daily_range * np.random.uniform(0.2, 0.8)
        
        # Ensure OHLC consistency
        high = max(high, close, open_price)
        low = min(low, close, open_price)
        
        # Generate volume with some correlation to price movement
        volume_base = base_volume * (0.5 + np.random.uniform(0, 1))
        price_change = abs((close - open_price) / open_price)
        volume_mult = 1 + price_change * 2  # Higher volume on bigger moves
        volume = int(volume_base * volume_mult)
        
        data['open'].append(open_price)
        data['high'].append(high)
        data['low'].append(low)
        data['close'].append(close)
        data['volume'].append(volume)
    
    return {k: np.array(v) for k, v in data.items()}

def benchmark_indicator(name: str, func, data: dict) -> tuple:
    """Benchmark a single indicator"""
    try:
        start_time = time.perf_counter()
        result = func(data)
        end_time = time.perf_counter()
        
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Validate result
        if result is None:
            return execution_time, False, "Returned None"
        
        # Handle tuple results (like MACD, Stochastic, etc.)
        if isinstance(result, tuple):
            for i, r in enumerate(result):
                if r is None:
                    return execution_time, False, f"Tuple element {i} is None"
                if hasattr(r, '__len__') and len(r) == 0:
                    return execution_time, False, f"Tuple element {i} is empty"
        else:
            if hasattr(result, '__len__') and len(result) == 0:
                return execution_time, False, "Result is empty"
        
        return execution_time, True, "OK"
        
    except Exception as e:
        return 0, False, str(e)

def main():
    """Main execution function"""
    
    # Key representative indicators from each category
    indicators = {
        # Trend Indicators
        'sma': lambda data: ta.sma(data['close'], period=20),
        'ema': lambda data: ta.ema(data['close'], period=20),
        'supertrend': lambda data: ta.supertrend(data['high'], data['low'], data['close']),
        
        # Momentum Indicators
        'rsi': lambda data: ta.rsi(data['close']),
        'macd': lambda data: ta.macd(data['close']),
        'stochastic': lambda data: ta.stochastic(data['high'], data['low'], data['close']),
        
        # Volume Indicators
        'obv': lambda data: ta.obv(data['close'], data['volume']),
        'vwap': lambda data: ta.vwap(data['high'], data['low'], data['close'], data['volume']),
        'kvo': lambda data: ta.kvo(data['high'], data['low'], data['close'], data['volume']),
        
        # Volatility Indicators
        'bbands': lambda data: ta.bbands(data['close']),
        'atr': lambda data: ta.atr(data['high'], data['low'], data['close']),
        
        # Statistical Indicators
        'lrslope': lambda data: ta.lrslope(data['close']),
        'correlation': lambda data: ta.correlation(data['close'], data['high'], period=20),
        
        # Hybrid Indicators
        'adx': lambda data: ta.adx(data['high'], data['low'], data['close']),

    }
    
    print("layr0_imc Quick Speed Audit")
    print("=" * 50)
    print(f"Testing {len(indicators)} representative indicators")
    print()
    
    dataset_sizes = [1000, 10000, 100000]
    results = {}
    
    for size in dataset_sizes:
        print(f"Testing with {size:,} data points...")
        data = generate_realistic_data(size)
        
        size_results = {}
        successful_tests = 0
        total_time = 0
        
        for i, (name, func) in enumerate(indicators.items(), 1):
            print(f"  [{i:2d}/{len(indicators)}] Testing {name}...", end=" ", flush=True)
            
            exec_time, success, message = benchmark_indicator(name, func, data)
            total_time += exec_time
            
            if success:
                successful_tests += 1
                size_results[name] = exec_time
                print(f"{exec_time:.3f}ms OK")
            else:
                size_results[name] = None
                print(f"ERROR: {message}")
        
        results[size] = size_results
        
        print(f"  Success Rate: {successful_tests}/{len(indicators)} ({successful_tests/len(indicators)*100:.1f}%)")
        print(f"  Total Time: {total_time/1000:.3f}s")
        print(f"  Average Time: {total_time/len(indicators):.2f}ms per indicator")
        print()
    
    # Generate simple report
    print("Performance Summary:")
    print("-" * 70)
    print(f"{'Indicator':<15} {'1K (ms)':<10} {'10K (ms)':<10} {'100K (ms)':<10} {'Scaling':<10}")
    print("-" * 70)
    
    for name in indicators.keys():
        times = []
        for size in dataset_sizes:
            if results[size][name] is not None:
                times.append(results[size][name])
            else:
                times.append(-1)
        
        scaling = "N/A"
        if times[0] > 0 and times[-1] > 0:
            scaling = f"{times[-1]/times[0]:.1f}x"
        
        time_strs = []
        for t in times:
            if t > 0:
                time_strs.append(f"{t:.3f}")
            else:
                time_strs.append("ERROR")
        
        print(f"{name:<15} {time_strs[0]:<10} {time_strs[1]:<10} {time_strs[2]:<10} {scaling:<10}")
    
    print()
    print("Quick audit completed!")

if __name__ == "__main__":
    main()
