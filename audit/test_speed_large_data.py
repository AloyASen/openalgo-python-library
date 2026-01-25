#!/usr/bin/env python3
"""
layr0-IMC Technical Indicators - Large Data Speed Test
====================================================

Comprehensive speed testing on HDFCBANK.csv (~924K records)
Tests all 104 indicators for first run (cold) and second run (warm) performance.

This test measures:
1. Cold start performance (first run with Numba compilation)
2. Warm performance (second run with compiled code)
3. Memory usage and efficiency
4. Real-world large dataset performance
"""

import pandas as pd
import numpy as np
import time
import psutil
import os
import sys
from datetime import datetime
import gc

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from layr0-IMC import ta
    print("[SUCCESS] layr0-IMC imported successfully")
except ImportError as e:
    print(f"[ERROR] Error importing layr0-IMC: {e}")
    sys.exit(1)

class LargeDataSpeedTest:
    def __init__(self, data_file):
        self.data_file = data_file
        self.results = {}
        self.data = None
        self.high = None
        self.low = None
        self.close = None
        self.open_prices = None
        self.volume = None
        
        # All 104 indicators with EXACT parameter signatures
        self.indicators = [
            # Trend Indicators (19)
            ("sma", "SMA", {"data": "close", "period": 20}),
            ("ema", "EMA", {"data": "close", "period": 20}),
            ("wma", "WMA", {"data": "close", "period": 20}),
            ("dema", "DEMA", {"data": "close", "period": 20}),
            ("tema", "TEMA", {"data": "close", "period": 20}),
            ("hma", "HMA", {"data": "close", "period": 20}),
            ("vwma", "VWMA", {"data": "close", "volume": "volume", "period": 20}),
            ("alma", "ALMA", {"data": "close", "period": 21, "offset": 0.85, "sigma": 6.0}),
            ("kama", "KAMA", {"data": "close", "length": 10, "fast_length": 2, "slow_length": 30}),
            ("zlema", "ZLEMA", {"data": "close", "period": 20}),
            ("t3", "T3", {"data": "close", "period": 21, "v_factor": 0.7}),
            ("frama", "FRAMA", {"high": "high", "low": "low", "period": 26}),
            ("trima", "TRIMA", {"data": "close", "period": 20}),
            ("mcginley", "MCGINLEY", {"data": "close", "period": 14}),
            ("vidya", "VIDYA", {"data": "close", "period": 14, "alpha": 0.2}),
            ("supertrend", "SUPERTREND", {"high": "high", "low": "low", "close": "close", "period": 10, "multiplier": 3.0}),
            ("ichimoku", "ICHIMOKU", {"high": "high", "low": "low", "close": "close", "conversion_periods": 9, "base_periods": 26, "lagging_span2_periods": 52, "displacement": 26}),
            ("alligator", "ALLIGATOR", {"data": "close", "jaw_period": 13, "jaw_shift": 8, "teeth_period": 8, "teeth_shift": 5, "lips_period": 5, "lips_shift": 3}),
            ("ma_envelopes", "MA_ENVELOPES", {"data": "close", "period": 20, "percentage": 2.5, "ma_type": "SMA"}),
            
            # Momentum Indicators (9)
            ("rsi", "RSI", {"data": "close", "period": 14}),
            ("macd", "MACD", {"data": "close", "fast_period": 12, "slow_period": 26, "signal_period": 9}),
            ("po", "PO", {"data": "close", "fast_period": 10, "slow_period": 20, "ma_type": "SMA"}),
            ("ppo", "PPO", {"data": "close", "fast_period": 12, "slow_period": 26, "signal_period": 9}),
            ("cmo", "CMO", {"data": "close", "period": 14}),
            ("crsi", "CRSI", {"data": "close", "lenrsi": 3, "lenupdown": 2, "lenroc": 100}),
            ("rvi", "RVI", {"open_prices": "open", "high": "high", "low": "low", "close": "close", "period": 10}),
            ("tsi", "TSI", {"data": "close", "long_period": 25, "short_period": 13, "signal_period": 13}),
            ("coppock", "COPPOCK", {"data": "close", "wma_length": 10, "long_roc_length": 14, "short_roc_length": 11}),
            
            # Oscillators (18)
            ("roc", "ROC", {"data": "close", "length": 12}),
            ("trix", "TRIX", {"data": "close", "length": 18}),
            ("ultimate_oscillator", "UO", {"high": "high", "low": "low", "close": "close", "period1": 7, "period2": 14, "period3": 28}),
            ("awesome_oscillator", "AO", {"high": "high", "low": "low", "fast_period": 5, "slow_period": 34}),
            ("accelerator_oscillator", "AC", {"high": "high", "low": "low", "period": 5}),
            ("dpo", "DPO", {"data": "close", "period": 21, "is_centered": False}),
            ("aroon_oscillator", "AROON_OSC", {"high": "high", "low": "low", "period": 25}),
            ("stochrsi", "STOCHRSI", {"data": "close", "rsi_period": 14, "stoch_period": 14, "k_period": 3, "d_period": 3}),
            ("cho", "CHO", {"high": "high", "low": "low", "close": "close", "volume": "volume", "fast_period": 3, "slow_period": 10}),
            ("chop", "CHOP", {"high": "high", "low": "low", "close": "close", "period": 14}),
            ("kst", "KST", {"data": "close", "roclen1": 10, "roclen2": 15, "roclen3": 20, "roclen4": 30, "smalen1": 10, "smalen2": 10, "smalen3": 10, "smalen4": 15, "siglen": 9}),
            ("stc", "STC", {"data": "close", "fast_length": 23, "slow_length": 50, "cycle_length": 10, "d1_length": 3, "d2_length": 3}),
            ("vi", "VI", {"high": "high", "low": "low", "close": "close", "period": 14}),
            ("gator_oscillator", "GATOR", {"high": "high", "low": "low", "jaw_period": 13, "teeth_period": 8, "lips_period": 5}),
            ("fisher", "FISHER", {"high": "high", "low": "low", "length": 9}),
            ("stochastic", "STOCHASTIC", {"high": "high", "low": "low", "close": "close", "k_period": 14, "d_period": 3}),
            ("cci", "CCI", {"high": "high", "low": "low", "close": "close", "period": 20}),
            ("williams_r", "WILLIAMS_R", {"high": "high", "low": "low", "close": "close", "period": 14}),
            
            # Volatility Indicators (15)
            ("atr", "ATR", {"high": "high", "low": "low", "close": "close", "period": 14}),
            ("bbands", "BBANDS", {"data": "close", "period": 20, "std_dev": 2.0}),
            ("keltner", "KELTNER", {"high": "high", "low": "low", "close": "close", "ema_period": 20, "atr_period": 10, "multiplier": 2.0}),
            ("donchian", "DONCHIAN", {"high": "high", "low": "low", "period": 20}),
            ("chaikin", "CHAIKIN", {"high": "high", "low": "low", "ema_period": 10, "roc_period": 10}),
            ("natr", "NATR", {"high": "high", "low": "low", "close": "close", "period": 14}),
            ("true_range", "TR", {"high": "high", "low": "low", "close": "close"}),
            ("massindex", "MASSINDEX", {"high": "high", "low": "low", "length": 10}),
            ("bbpercent", "BB%B", {"data": "close", "period": 20, "std_dev": 2.0}),
            ("bbwidth", "BBW", {"data": "close", "period": 20, "std_dev": 2.0}),
            ("chandelier_exit", "CE", {"high": "high", "low": "low", "close": "close", "period": 22, "multiplier": 3.0}),
            ("hv", "HV", {"close": "close", "length": 10, "annual": 365, "per": 1}),
            ("ulcerindex", "UI", {"data": "close", "length": 14, "smooth_length": 14, "signal_length": 52, "signal_type": "SMA", "return_signal": False}),
            ("starc", "STARC", {"high": "high", "low": "low", "close": "close", "ma_period": 5, "atr_period": 15, "multiplier": 1.33}),
            ("stdev", "STDEV", {"data": "close", "period": 20}),
            
            # Volume Indicators (15)
            ("obv", "OBV", {"close": "close", "volume": "volume"}),
            ("vwap", "VWAP", {"high": "high", "low": "low", "close": "close", "volume": "volume", "anchor": "Session", "source": "hlc3"}),
            ("mfi", "MFI", {"high": "high", "low": "low", "close": "close", "volume": "volume", "period": 14}),
            ("adl", "ADL", {"high": "high", "low": "low", "close": "close", "volume": "volume"}),
            ("cmf", "CMF", {"high": "high", "low": "low", "close": "close", "volume": "volume", "period": 20}),
            ("emv", "EMV", {"high": "high", "low": "low", "volume": "volume", "length": 14, "divisor": 10000}),
            ("force_index", "FI", {"close": "close", "volume": "volume", "length": 13}),
            ("nvi", "NVI", {"close": "close", "volume": "volume"}),
            ("pvi", "PVI", {"close": "close", "volume": "volume", "initial_value": 100.0}),
            ("volosc", "VO", {"volume": "volume", "short_length": 5, "long_length": 10}),
            ("vroc", "VROC", {"volume": "volume", "period": 25}),
            ("kvo", "KVO", {"high": "high", "low": "low", "close": "close", "volume": "volume", "trig_len": 34, "fast_x": 55, "slow_x": 89}),
            ("pvt", "PVT", {"close": "close", "volume": "volume"}),
            ("rvol", "RVOL", {"volume": "volume", "period": 20}),
            ("bop", "BOP", {"open_prices": "open", "high": "high", "low": "low", "close": "close"}),
            
            # Statistical Indicators (8)
            ("linreg", "LR", {"data": "close", "period": 14}),
            ("lrslope", "LRS", {"data": "close", "period": 100, "interval": 1}),
            ("correlation", "CORR", {"data1": "high", "data2": "low", "period": 20}),
            ("beta", "BETA", {"asset": "close", "market": "close", "period": 252}),
            ("variance", "VAR", {"data": "close", "lookback": 20, "mode": "PR", "ema_period": 20}),
            ("tsf", "TSF", {"data": "close", "period": 14}),
            ("median", "MEDIAN", {"data": "close", "period": 3}),
            ("mode", "MODE", {"data": "close", "period": 20, "bins": 10}),
            
            # Hybrid Indicators (9)
            ("adx", "ADX", {"high": "high", "low": "low", "close": "close", "period": 14}),
            ("aroon", "AROON", {"high": "high", "low": "low", "period": 25}),
            ("pivot_points", "PIVOT", {"high": "high", "low": "low", "close": "close"}),
            ("dmi", "DMI", {"high": "high", "low": "low", "close": "close", "period": 14}),
            ("ckstop", "CKSTOP", {"high": "high", "low": "low", "close": "close", "p": 10, "x": 1.0, "q": 9}),
            ("fractals", "FRACTALS", {"high": "high", "low": "low", "periods": 2}),
            ("rwi", "RWI", {"high": "high", "low": "low", "close": "close", "period": 14}),
            ("psar", "PSAR", {"high": "high", "low": "low", "acceleration": 0.02, "maximum": 0.2}),
            ("elderray", "ELDERRAY", {"high": "high", "low": "low", "close": "close", "period": 13}),
            
            # Utility Functions (11)
            ("crossover", "CROSSOVER", {"series1": "close", "series2": "open"}),
            ("crossunder", "CROSSUNDER", {"series1": "close", "series2": "open"}),
            ("highest", "HIGHEST", {"data": "high", "period": 20}),
            ("lowest", "LOWEST", {"data": "low", "period": 20}),
            ("change", "CHANGE", {"data": "close", "length": 1}),
            ("exrem", "EXREM", {"primary": "close", "secondary": "open"}),
            ("flip", "FLIP", {"primary": "close", "secondary": "open"}),
            ("valuewhen", "VALUEWHEN", {"expr": "close", "array": "high", "n": 1}),
            ("rising", "RISING", {"data": "close", "length": 5}),
            ("falling", "FALLING", {"data": "close", "length": 5}),
            ("cross", "CROSS", {"series1": "close", "series2": "open"}),
        ]
        
    def load_data(self):
        """Load and prepare the large HDFCBANK dataset"""
        print(f"[LOADING] Data from: {self.data_file}")
        
        try:
            # Read the CSV file
            df = pd.read_csv(self.data_file)
            print(f"[SUCCESS] Data loaded successfully: {len(df):,} records")
            
            # Display data info
            print(f"[INFO] Dataset info:")
            print(f"   - Columns: {list(df.columns)}")
            print(f"   - Shape: {df.shape}")
            print(f"   - Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            # Prepare the data arrays
            self.data = df
            
            # Handle different possible column names
            if 'CLOSE' in df.columns:
                self.close = df['CLOSE'].values.astype(np.float64)
                self.high = df['HIGH'].values.astype(np.float64)
                self.low = df['LOW'].values.astype(np.float64)
                self.open_prices = df['OPEN'].values.astype(np.float64)
                self.volume = df['VOLUME'].values.astype(np.float64)
            elif 'Close' in df.columns:
                self.close = df['Close'].values.astype(np.float64)
                self.high = df['High'].values.astype(np.float64)
                self.low = df['Low'].values.astype(np.float64)
                self.open_prices = df['Open'].values.astype(np.float64)
                self.volume = df['Volume'].values.astype(np.float64)
            else:
                # Try lowercase
                self.close = df['close'].values.astype(np.float64)
                self.high = df['high'].values.astype(np.float64)
                self.low = df['low'].values.astype(np.float64)
                self.open_prices = df['open'].values.astype(np.float64)
                self.volume = df['volume'].values.astype(np.float64)
            
            print(f"[SUCCESS] Data arrays prepared:")
            print(f"   - Close range: {self.close.min():.2f} - {self.close.max():.2f}")
            print(f"   - Volume range: {self.volume.min():,.0f} - {self.volume.max():,.0f}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error loading data: {e}")
            return False
    
    def get_memory_usage(self):
        """Get current memory usage"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024**2  # MB
    
    def prepare_parameters(self, params):
        """Convert parameter references to actual data arrays"""
        prepared = {}
        data_map = {
            "close": self.close,
            "high": self.high,
            "low": self.low,
            "open": self.open_prices,
            "volume": self.volume
        }
        
        for key, value in params.items():
            if value in data_map:
                prepared[key] = data_map[value]
            else:
                prepared[key] = value
        
        return prepared
    
    def test_indicator(self, func_name, display_name, params):
        """Test a single indicator for cold and warm performance"""
        print(f"\n[TEST] Testing {display_name} ({func_name})...")
        
        try:
            # Get the function
            func = getattr(ta, func_name)
            
            # Prepare parameters
            test_params = self.prepare_parameters(params)
            
            # Memory before
            mem_before = self.get_memory_usage()
            
            # Cold run (first time - includes Numba compilation)
            gc.collect()  # Clean up before test
            start_time = time.perf_counter()
            
            result1 = func(**test_params)
            
            cold_time = time.perf_counter() - start_time
            
            # Memory after cold run
            mem_after_cold = self.get_memory_usage()
            
            # Warm run (second time - compiled code)
            gc.collect()
            start_time = time.perf_counter()
            
            result2 = func(**test_params)
            
            warm_time = time.perf_counter() - start_time
            
            # Memory after warm run
            mem_after_warm = self.get_memory_usage()
            
            # Verify results are identical
            if isinstance(result1, tuple):
                results_match = all(np.allclose(r1, r2, equal_nan=True) for r1, r2 in zip(result1, result2))
                result_shape = tuple(r.shape if hasattr(r, 'shape') else len(r) for r in result1)
                result_type = f"Tuple[{len(result1)}]"
            else:
                results_match = np.allclose(result1, result2, equal_nan=True)
                result_shape = result1.shape if hasattr(result1, 'shape') else len(result1)
                result_type = "Array"
            
            # Calculate speedup
            speedup = cold_time / warm_time if warm_time > 0 else float('inf')
            
            # Store results
            self.results[func_name] = {
                'display_name': display_name,
                'cold_time': cold_time,
                'warm_time': warm_time,
                'speedup': speedup,
                'memory_cold': mem_after_cold - mem_before,
                'memory_warm': mem_after_warm - mem_after_cold,
                'result_shape': result_shape,
                'result_type': result_type,
                'results_match': results_match,
                'status': 'SUCCESS'
            }
            
            print(f"   [OK] {display_name}: Cold={cold_time*1000:.2f}ms, Warm={warm_time*1000:.2f}ms, Speedup={speedup:.1f}x")
            
        except Exception as e:
            print(f"   [ERROR] {display_name}: ERROR - {str(e)}")
            self.results[func_name] = {
                'display_name': display_name,
                'cold_time': 0,
                'warm_time': 0,
                'speedup': 0,
                'memory_cold': 0,
                'memory_warm': 0,
                'result_shape': None,
                'result_type': None,
                'results_match': False,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def run_speed_test(self):
        """Run complete speed test on all indicators"""
        print("[START] Starting Large Data Speed Test")
        print("=" * 60)
        
        if not self.load_data():
            return False
        
        print(f"\n[INFO] Testing {len(self.indicators)} indicators on {len(self.close):,} data points")
        print(f"[MEMORY] Initial memory usage: {self.get_memory_usage():.2f} MB")
        
        start_total = time.perf_counter()
        
        # Test each indicator
        for i, (func_name, display_name, params) in enumerate(self.indicators, 1):
            print(f"\n[{i:3d}/{len(self.indicators)}]", end="")
            self.test_indicator(func_name, display_name, params)
        
        total_time = time.perf_counter() - start_total
        
        # Generate comprehensive report
        self.generate_speed_report(total_time)
        
        return True
    
    def generate_speed_report(self, total_time):
        """Generate detailed speed test report"""
        print("\n" + "=" * 80)
        print("[RESULTS] LARGE DATA SPEED TEST RESULTS")
        print("=" * 80)
        
        # Summary statistics
        successful = [r for r in self.results.values() if r['status'] == 'SUCCESS']
        failed = [r for r in self.results.values() if r['status'] == 'ERROR']
        
        print(f"\n[SUMMARY] TEST SUMMARY")
        print(f"   - Total Indicators: {len(self.results)}")
        print(f"   - Successful: {len(successful)} ({len(successful)/len(self.results)*100:.1f}%)")
        print(f"   - Failed: {len(failed)} ({len(failed)/len(self.results)*100:.1f}%)")
        print(f"   - Data Points: {len(self.close):,}")
        print(f"   - Total Test Time: {total_time:.2f} seconds")
        print(f"   - Final Memory Usage: {self.get_memory_usage():.2f} MB")
        
        if successful:
            # Performance statistics
            cold_times = [r['cold_time'] for r in successful]
            warm_times = [r['warm_time'] for r in successful]
            speedups = [r['speedup'] for r in successful if r['speedup'] != float('inf')]
            
            print(f"\n[PERFORMANCE] PERFORMANCE METRICS")
            print(f"   [COLD] Cold Start Performance (includes Numba compilation):")
            print(f"      - Average: {np.mean(cold_times)*1000:.2f} ms")
            print(f"      - Median:  {np.median(cold_times)*1000:.2f} ms")
            print(f"      - Min:     {np.min(cold_times)*1000:.2f} ms")
            print(f"      - Max:     {np.max(cold_times)*1000:.2f} ms")
            
            print(f"\n   [WARM] Warm Performance (compiled code):")
            print(f"      - Average: {np.mean(warm_times)*1000:.2f} ms")
            print(f"      - Median:  {np.median(warm_times)*1000:.2f} ms")
            print(f"      - Min:     {np.min(warm_times)*1000:.2f} ms")
            print(f"      - Max:     {np.max(warm_times)*1000:.2f} ms")
            
            print(f"\n   [SPEEDUP] Speedup (Warm vs Cold):")
            print(f"      - Average: {np.mean(speedups):.1f}x faster")
            print(f"      - Median:  {np.median(speedups):.1f}x faster")
            print(f"      - Min:     {np.min(speedups):.1f}x faster")
            print(f"      - Max:     {np.max(speedups):.1f}x faster")
        
        # Top 10 fastest (warm)
        if successful:
            print(f"\n[FASTEST] TOP 10 FASTEST INDICATORS (Warm Performance)")
            fastest = sorted(successful, key=lambda x: x['warm_time'])[:10]
            for i, result in enumerate(fastest, 1):
                print(f"   {i:2d}. {result['display_name']:<15} {result['warm_time']*1000:6.2f} ms")
        
        # Top 10 slowest (warm)
        if successful:
            print(f"\n[SLOWEST] TOP 10 SLOWEST INDICATORS (Warm Performance)")
            slowest = sorted(successful, key=lambda x: x['warm_time'], reverse=True)[:10]
            for i, result in enumerate(slowest, 1):
                print(f"   {i:2d}. {result['display_name']:<15} {result['warm_time']*1000:6.2f} ms")
        
        # Detailed results table
        print(f"\n[DETAILED] DETAILED RESULTS")
        print("=" * 120)
        print(f"{'Indicator':<15} {'Status':<8} {'Cold (ms)':<10} {'Warm (ms)':<10} {'Speedup':<8} {'Shape':<20} {'Type':<12}")
        print("-" * 120)
        
        for func_name in sorted(self.results.keys()):
            result = self.results[func_name]
            if result['status'] == 'SUCCESS':
                print(f"{result['display_name']:<15} {'[OK]':<8} {result['cold_time']*1000:>8.2f} {result['warm_time']*1000:>8.2f} "
                      f"{result['speedup']:>6.1f}x {str(result['result_shape']):<20} {result['result_type']:<12}")
            else:
                print(f"{result['display_name']:<15} {'[ERR]':<8} {'ERROR':<10} {'ERROR':<10} {'N/A':<8} {'N/A':<20} {'N/A':<12}")
        
        # Error details
        if failed:
            print(f"\n[ERRORS] ERROR DETAILS")
            print("-" * 80)
            for result in failed:
                print(f"   - {result['display_name']}: {result.get('error', 'Unknown error')}")
        
        # Performance categories
        if successful:
            print(f"\n[CATEGORIES] PERFORMANCE CATEGORIES (Warm Performance)")
            print("-" * 60)
            ultra_fast = [r for r in successful if r['warm_time'] < 0.001]  # < 1ms
            fast = [r for r in successful if 0.001 <= r['warm_time'] < 0.01]  # 1-10ms  
            medium = [r for r in successful if 0.01 <= r['warm_time'] < 0.1]  # 10-100ms
            slow = [r for r in successful if r['warm_time'] >= 0.1]  # > 100ms
            
            print(f"   [ULTRA] Ultra Fast (< 1ms):    {len(ultra_fast):3d} indicators")
            print(f"   [FAST] Fast (1-10ms):         {len(fast):3d} indicators") 
            print(f"   [MED] Medium (10-100ms):     {len(medium):3d} indicators")
            print(f"   [SLOW] Slow (> 100ms):        {len(slow):3d} indicators")
        
        # Optimized indicators performance
        self.report_optimized_indicators_performance(successful)
        
    def report_optimized_indicators_performance(self, successful):
        """Report performance of optimized high priority indicators"""
        print(f"\n[OPTIMIZED] HIGH PRIORITY OPTIMIZED INDICATORS")
        print("-" * 70)
        
        # Expected performance before optimization (from audit04.md)
        optimized_indicators = {
            'variance': {'name': 'VAR (Variance)', 'baseline_warm': 24.55},
            'vi': {'name': 'VI (Vortex Indicator)', 'baseline_warm': 5.78}, 
            'ulcerindex': {'name': 'UI (Ulcer Index)', 'baseline_warm': 5.35}
        }
        
        print(f"   These indicators were optimized from O(N*period) to O(N) complexity:")
        print(f"   {'Indicator':<20} {'Before (s)':<12} {'After (s)':<12} {'Improvement':<12}")
        print(f"   {'-'*60}")
        
        total_improvement = 1.0
        optimized_count = 0
        
        for func_name, info in optimized_indicators.items():
            result = None
            for r in successful:
                if func_name in self.results and self.results[func_name]['display_name'] == info['name']:
                    result = r
                    break
            
            if result:
                current_time = result['warm_time']
                baseline_time = info['baseline_warm']
                improvement = baseline_time / current_time if current_time > 0 else float('inf')
                
                total_improvement *= improvement
                optimized_count += 1
                
                print(f"   {info['name']:<20} {baseline_time:<12.2f} {current_time:<12.4f} {improvement:<12.1f}x")
            else:
                print(f"   {info['name']:<20} {info['baseline_warm']:<12.2f} {'ERROR':<12} {'N/A':<12}")
        
        if optimized_count > 0:
            geometric_mean = total_improvement ** (1.0 / optimized_count)
            print(f"\n   [SUMMARY] Optimization Results:")
            print(f"      - Successfully optimized: {optimized_count}/3 indicators")
            print(f"      - Geometric mean speedup: {geometric_mean:.1f}x faster")
            print(f"      - Performance improvement: {(1 - 1/geometric_mean)*100:.1f}% reduction in execution time")
            
            if geometric_mean >= 10:
                print(f"      - [EXCELLENT] Achieved 10x+ speedup target!")
            elif geometric_mean >= 5:
                print(f"      - [GOOD] Achieved significant speedup!")
            else:
                print(f"      - [MODERATE] Some improvement achieved.")
        else:
            print(f"   [WARNING] No optimized indicators found in test results")
        
        # Save results to file
        self.save_results_to_file()
        
        print(f"\n[SUCCESS] Speed test completed successfully!")
        print(f"[ACHIEVEMENT] {len(successful)}/{len(self.results)} indicators working on {len(self.close):,} data points")
        
    def save_results_to_file(self):
        """Save detailed results to CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit/LARGE_DATA_SPEED_TEST_{timestamp}.csv"
        
        # Prepare data for CSV
        csv_data = []
        for func_name, result in self.results.items():
            csv_data.append({
                'function_name': func_name,
                'display_name': result['display_name'],
                'status': result['status'],
                'cold_time_ms': result['cold_time'] * 1000 if result['cold_time'] else 0,
                'warm_time_ms': result['warm_time'] * 1000 if result['warm_time'] else 0,
                'speedup': result['speedup'] if result['speedup'] != float('inf') else 999,
                'result_shape': str(result['result_shape']),
                'result_type': result['result_type'],
                'results_match': result['results_match'],
                'memory_cold_mb': result['memory_cold'],
                'memory_warm_mb': result['memory_warm'],
                'error': result.get('error', '')
            })
        
        # Save to CSV
        df_results = pd.DataFrame(csv_data)
        df_results.to_csv(filename, index=False)
        print(f"[SAVED] Detailed results saved to: {filename}")

def main():
    """Main function to run the speed test"""
    print("[SPEED TEST] layr0-IMC Large Data Speed Test")
    print("=" * 50)
    
    # Check if data file exists
    data_file = "audit/data/HDFCBANK.csv"
    if not os.path.exists(data_file):
        print(f"[ERROR] Data file not found: {data_file}")
        print("Please ensure HDFCBANK.csv is in the audit/data/ folder")
        return False
    
    # Run the speed test
    test = LargeDataSpeedTest(data_file)
    success = test.run_speed_test()
    
    if success:
        print("\n[SUCCESS] Large data speed test completed successfully!")
        return True
    else:
        print("\n[FAILED] Speed test failed!")
        return False

if __name__ == "__main__":
    main()