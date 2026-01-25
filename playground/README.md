# ADX Testing Playground

This folder contains scripts to test the ADX indicator with real market data using the layr0-IMC API.

## Files

- `test_adx_real_data.py` - Main test script using real market data
- `compare_indicators.py` - Compare ADX with other indicators 
- `adx_results.csv` - Output file with calculated results (generated after running tests)

## Setup

1. Make sure your layr0-IMC server is running locally on `http://127.0.0.1:5001`
2. Update the API key in the test scripts with your actual key
3. Run the test script:

```bash
cd playground
python test_adx_real_data.py
```

## What the test does

1. **Fetches real data** from NSE for RELIANCE stock
2. **Calculates ADX** using our fixed implementation
3. **Analyzes results** including:
   - Number of valid vs NaN values
   - ADX statistics (min/max/mean)
   - First and last calculated values
   - High ADX periods (strong trends)
4. **Saves results** to CSV for further analysis
5. **Fallback testing** with sample data if API fails

## Expected Results

- **Valid ADX values**: Should start appearing after ~26 data points (2 * period - 1)
- **NaN values**: First 25-26 values should be NaN (normal warm-up period)
- **ADX range**: Typically 0-100, with >25 indicating strong trend
- **No errors**: Should run without the previous NaN issues

## Troubleshooting

If you get connection errors:
1. Check if layr0-IMC server is running
2. Verify your API key
3. Update the host URL if needed
4. The script will automatically fall back to sample data testing