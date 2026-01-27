#!/usr/bin/env python3
"""
layr0_imc Optimized Indicators Performance Test
=============================================

Tests the three High Priority optimized indicators (VAR, VI, UI) 
with 1 million random data points to measure performance improvements.

Optimizations Applied:
- VAR: O(N*period) -> O(N) rolling variance using cumulative sums
- VI: O(N*period) -> O(N) rolling sums for VMP, VMM, STR calculations  
- UI: O(N*period) -> O(N) rolling max and optimized rolling averages
"""

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
    from layr0_imc import ta
    print("[SUCCESS] layr0_imc imported successfully")
except ImportError as e:
    print(f"[ERROR] Error importing layr0_imc: {e}")
    sys.exit(1)

class OptimizedIndicatorTest:
    def __init__(self, data_size=1_000_000):
        self.data_size = data_size
        self.results = {}
        
        # Generate 1 million random data points
        print(f"[GENERATING] Creating {data_size:,} random data points...")
        np.random.seed(42)  # For reproducible results
        
        # Generate realistic price data with trend and volatility
        base_price = 100.0
        trend = np.cumsum(np.random.normal(0, 0.02, data_size))
        noise = np.random.normal(0, 2.0, data_size)
        
        self.close = base_price + trend + noise
        self.close = np.abs(self.close)  # Ensure positive prices
        
        # Generate OHLV data
        spread = np.random.uniform(0.5, 3.0, data_size)
        self.high = self.close + spread * np.random.uniform(0, 1, data_size)
        self.low = self.close - spread * np.random.uniform(0, 1, data_size)
        self.open_prices = self.close + np.random.normal(0, 0.5, data_size)
        self.volume = np.random.uniform(1000, 100000, data_size)
        
        print(f"[SUCCESS] Generated {data_size:,} data points")
        print(f"   - Close range: {self.close.min():.2f} - {self.close.max():.2f}")
        print(f"   - Data memory: {self.close.nbytes * 5 / 1024**2:.2f} MB")
        
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024**2
    
    def test_indicator(self, name, func, params, iterations=3):
        """Test an indicator multiple times for consistent results"""
        print(f"\n[TEST] Testing {name}...")
        
        try:
            times = []
            results = []
            
            for i in range(iterations):
                gc.collect()  # Clean memory before each test
                
                start_time = time.perf_counter()
                result = func(**params)
                end_time = time.perf_counter()
                
                execution_time = end_time - start_time
                times.append(execution_time)
                results.append(result)
                
                print(f"   Run {i+1}: {execution_time:.4f} seconds")
            
            # Calculate statistics
            avg_time = np.mean(times)
            min_time = np.min(times)
            max_time = np.max(times)
            std_time = np.std(times)
            
            # Verify results are consistent
            if isinstance(results[0], tuple):
                consistent = all(
                    all(np.allclose(r1[j], r2[j], equal_nan=True) for j in range(len(r1)))
                    for r1, r2 in zip(results[:-1], results[1:])
                )
                result_shape = tuple(r.shape if hasattr(r, 'shape') else len(r) for r in results[0])
            else:
                consistent = all(
                    np.allclose(r1, r2, equal_nan=True) 
                    for r1, r2 in zip(results[:-1], results[1:])
                )
                result_shape = results[0].shape if hasattr(results[0], 'shape') else len(results[0])
            
            self.results[name] = {
                'avg_time': avg_time,
                'min_time': min_time, 
                'max_time': max_time,
                'std_time': std_time,
                'result_shape': result_shape,
                'consistent': consistent,
                'status': 'SUCCESS'
            }
            
            print(f"   [OK] Average: {avg_time:.4f}s, Min: {min_time:.4f}s, Max: {max_time:.4f}s")
            print(f"   [OK] Shape: {result_shape}, Consistent: {consistent}")
            
        except Exception as e:
            print(f"   [ERROR] {name}: {str(e)}")
            self.results[name] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def run_optimized_test(self):
        """Test the three optimized high priority indicators"""
        print("=" * 80)
        print(f"[START] OPTIMIZED INDICATORS PERFORMANCE TEST")
        print(f"[DATA] Testing on {self.data_size:,} data points")
        print(f"[MEMORY] Initial memory: {self.get_memory_usage():.2f} MB")
        print("=" * 80)
        
        # Test 1: VAR (Variance) - Previously 24.55 seconds  
        print("\n[1/3] Testing VAR (Variance) - O(N) rolling variance optimization")
        self.test_indicator(
            "VAR",
            ta.variance,
            {
                "data": self.close,
                "lookback": 20,
                "mode": "PR", 
                "ema_period": 20,
                "filter_lookback": 20,
                "ema_length": 14
            }
        )
        
        # Test 2: VI (Vortex Indicator) - Previously 5.78 seconds
        print("\n[2/3] Testing VI (Vortex Indicator) - O(N) rolling sums optimization")
        self.test_indicator(
            "VI", 
            ta.vi,
            {
                "high": self.high,
                "low": self.low,
                "close": self.close,
                "period": 14
            }
        )
        
        # Test 3: UI (Ulcer Index) - Previously 5.35 seconds
        print("\n[3/3] Testing UI (Ulcer Index) - O(N) rolling max optimization")
        self.test_indicator(
            "UI",
            ta.ulcerindex,
            {
                "data": self.close,
                "length": 14,
                "smooth_length": 14,
                "signal_length": 52,
                "signal_type": "SMA",
                "return_signal": False
            }
        )
        
        # Generate report
        self.generate_optimization_report()
        
    def generate_optimization_report(self):
        """Generate optimization performance report"""
        print("\n" + "=" * 80)
        print("[RESULTS] OPTIMIZATION PERFORMANCE REPORT")
        print("=" * 80)
        
        # Expected performance from audit report (for 924K records)
        baseline_times = {
            "VAR": 24.55,  # Original warm time in seconds
            "VI": 5.78,
            "UI": 5.35
        }
        
        # Scale baseline times to 1M records (approximately)
        scale_factor = self.data_size / 924_219
        scaled_baseline = {k: v * scale_factor for k, v in baseline_times.items()}
        
        print(f"\n[DATASET] Performance Test Dataset:")
        print(f"   - Data points: {self.data_size:,}")
        print(f"   - Memory usage: {self.get_memory_usage():.2f} MB")
        print(f"   - Baseline scale factor: {scale_factor:.2f}x (vs 924K records)")
        
        print(f"\n[EXPECTED] Expected Performance (scaled from audit):")
        for name, time_val in scaled_baseline.items():
            print(f"   - {name}: {time_val:.2f} seconds (before optimization)")
        
        print(f"\n[ACTUAL] Actual Performance (after optimization):")
        
        successful = [name for name, result in self.results.items() if result['status'] == 'SUCCESS']
        failed = [name for name, result in self.results.items() if result['status'] == 'ERROR']
        
        # Performance summary table
        print(f"\n{'Indicator':<12} {'Status':<8} {'Time (s)':<10} {'Expected (s)':<12} {'Speedup':<10} {'Shape':<15}")
        print("-" * 75)
        
        total_speedup = 1.0
        speedup_count = 0
        
        for name in ['VAR', 'VI', 'UI']:
            if name in self.results:
                result = self.results[name]
                if result['status'] == 'SUCCESS':
                    actual_time = result['avg_time']
                    expected_time = scaled_baseline[name]
                    speedup = expected_time / actual_time if actual_time > 0 else float('inf')
                    
                    total_speedup *= speedup
                    speedup_count += 1
                    
                    print(f"{name:<12} {'[OK]':<8} {actual_time:<10.4f} {expected_time:<12.2f} {speedup:<10.1f}x {str(result['result_shape']):<15}")
                else:
                    print(f"{name:<12} {'[ERROR]':<8} {'N/A':<10} {scaled_baseline[name]:<12.2f} {'N/A':<10} {'N/A':<15}")
        
        if speedup_count > 0:
            geometric_mean_speedup = total_speedup ** (1.0 / speedup_count)
            print(f"\n[OPTIMIZATION] Overall Performance Improvement:")
            print(f"   - Successful optimizations: {len(successful)}/3")
            print(f"   - Geometric mean speedup: {geometric_mean_speedup:.1f}x faster")
            print(f"   - Time reduction: {(1 - 1/geometric_mean_speedup)*100:.1f}% faster")
        
        # Individual results
        print(f"\n[DETAILED] Detailed Results:")
        for name, result in self.results.items():
            if result['status'] == 'SUCCESS':
                print(f"\n   {name} (SUCCESS):")
                print(f"      - Average time: {result['avg_time']:.4f} seconds")
                print(f"      - Min time: {result['min_time']:.4f} seconds") 
                print(f"      - Max time: {result['max_time']:.4f} seconds")
                print(f"      - Std deviation: {result['std_time']:.4f} seconds")
                print(f"      - Result shape: {result['result_shape']}")
                print(f"      - Results consistent: {result['consistent']}")
            else:
                print(f"\n   {name} (ERROR): {result.get('error', 'Unknown error')}")
        
        # Save results to file
        self.save_optimization_results()
        
        print(f"\n[SUCCESS] Optimization test completed!")
        print(f"[ACHIEVEMENT] Successfully tested {len(successful)}/3 optimized indicators")
    
    def save_optimization_results(self):
        """Save optimization results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit/OPTIMIZED_INDICATORS_TEST_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("layr0_imc Optimized Indicators Performance Test Results\n")
            f.write("=" * 60 + "\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data Points: {self.data_size:,}\n")
            f.write(f"Memory Usage: {self.get_memory_usage():.2f} MB\n\n")
            
            for name, result in self.results.items():
                f.write(f"{name}:\n")
                if result['status'] == 'SUCCESS':
                    f.write(f"  Status: SUCCESS\n")
                    f.write(f"  Average Time: {result['avg_time']:.6f} seconds\n")
                    f.write(f"  Min Time: {result['min_time']:.6f} seconds\n")
                    f.write(f"  Max Time: {result['max_time']:.6f} seconds\n")
                    f.write(f"  Std Deviation: {result['std_time']:.6f} seconds\n")
                    f.write(f"  Result Shape: {result['result_shape']}\n")
                    f.write(f"  Consistent: {result['consistent']}\n")
                else:
                    f.write(f"  Status: ERROR\n")
                    f.write(f"  Error: {result.get('error', 'Unknown')}\n")
                f.write("\n")
        
        print(f"[SAVED] Results saved to: {filename}")

def main():
    """Main function to run the optimization test"""
    print("[OPTIMIZATION TEST] layr0_imc Optimized Indicators Performance Test")
    print("=" * 70)
    
    # Run the optimization test with 1 million data points
    test = OptimizedIndicatorTest(data_size=1_000_000)
    test.run_optimized_test()
    
    print("\n[SUCCESS] Optimization performance test completed!")

if __name__ == "__main__":
    main()
