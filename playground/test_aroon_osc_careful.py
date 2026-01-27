#!/usr/bin/env python
"""Careful test of Aroon Oscillator"""

import sys
import os

# Add the parent directory to path to use our current testing version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layr0_imc import ta
import numpy as np

def test_aroon_oscillator_careful():
    """Careful test to verify Aroon Oscillator = Aroon Up - Aroon Down"""
    
    print("Careful Aroon Oscillator Test")
    print("=" * 35)
    
    # Create test data with known patterns
    np.random.seed(42)
    n = 50
    
    # Create uptrend data
    base_price = 100
    trend = np.linspace(0, 0.2, n)
    noise = np.random.normal(0, 0.01, n)
    prices = base_price * np.exp(np.cumsum(trend + noise))
    
    high = prices * (1 + np.random.uniform(0.001, 0.02, n))
    low = prices * (1 - np.random.uniform(0.001, 0.02, n))
    
    print(f"Generated {n} test data points")
    print(f"Price range: {prices.min():.2f} - {prices.max():.2f}")
    
    # Test with same period for both calculations
    period = 14
    
    # Calculate Aroon components
    aroon_up, aroon_down = ta.aroon(high, low, period)
    
    # Calculate Aroon Oscillator directly  
    aroon_osc = ta.aroon_oscillator(high, low, period)
    
    # Calculate manually
    manual_osc = aroon_up - aroon_down
    
    print(f"\nUsing period={period} for all calculations")
    
    # Find valid data
    valid_mask = ~(np.isnan(aroon_up) | np.isnan(aroon_down) | np.isnan(aroon_osc))
    valid_count = valid_mask.sum()
    
    print(f"Valid data points: {valid_count}/{n}")
    
    if valid_count > 0:
        # Calculate differences
        differences = np.abs(aroon_osc[valid_mask] - manual_osc[valid_mask])
        max_diff = differences.max()
        mean_diff = differences.mean()
        
        print(f"Max difference: {max_diff:.10f}")
        print(f"Mean difference: {mean_diff:.10f}")
        
        if max_diff < 1e-10:
            print("PERFECT MATCH - Aroon Oscillator is correctly calculated!")
        elif max_diff < 0.01:
            print("GOOD MATCH - Small floating point differences")
        else:
            print("MISMATCH FOUND - Need to investigate")
            
            # Show problematic cases
            problem_indices = np.where(differences > 0.01)[0]
            if len(problem_indices) > 0:
                print(f"\nProblematic cases (diff > 0.01):")
                for idx in problem_indices[:5]:  # Show first 5
                    actual_idx = np.where(valid_mask)[0][idx]
                    print(f"  Index {actual_idx}: Up={aroon_up[actual_idx]:.4f}, Down={aroon_down[actual_idx]:.4f}")
                    print(f"    Direct Osc={aroon_osc[actual_idx]:.4f}, Manual={manual_osc[actual_idx]:.4f}, Diff={differences[idx]:.4f}")
        
        # Show sample results
        print(f"\nSample results (first 5 valid):")
        valid_indices = np.where(valid_mask)[0]
        for i in range(min(5, len(valid_indices))):
            idx = valid_indices[i]
            print(f"  Index {idx}: Up={aroon_up[idx]:.2f}, Down={aroon_down[idx]:.2f}, Osc={aroon_osc[idx]:.2f}")
    
    else:
        print("No valid data points found!")
    
    return max_diff < 0.01 if valid_count > 0 else False

if __name__ == "__main__":
    success = test_aroon_oscillator_careful()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
