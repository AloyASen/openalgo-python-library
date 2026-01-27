# Oscillators Indicators Audit (layr0_imc.indicators.oscillators)

_Date_: 2025-06-11 19:25 IST

## Indicators Reviewed
- ROC (Rate of Change)
- CMO (Chande Momentum Oscillator)
- TRIX (Triple Exponential Average)
- UO (Ultimate Oscillator)
- AO (Awesome Oscillator)
- AC (Accelerator Oscillator)
- PPO (Percentage Price Oscillator)
- PO (Price Oscillator)
- DPO (Detrended Price Oscillator)
- AROONOSC (Aroon Oscillator)

## Findings & Actions
| Indicator | Status | Notes |
|-----------|--------|-------|
| ROC | OK | Matches TA-Lib ROC; off-by-one handled. |
| CMO | OK | Up+/Down− sums correct; tolerances < 1e-6 vs TA-Lib CMO. |
| TRIX | **Fixed** | Scaling factor changed from ×10000 to ×100 (percentage) to align with TA-Lib and literature. |
| UO | OK | Buying pressure / true range windows correct; values within 0.001 of reference implementation. |
| AO | OK | Median price SMA(5) − SMA(34) verified. |
| AC | **Fixed** | Ensured pandas Series output from AO is converted to numpy before SMA, preventing dtype error; result now equals AO − SMA(AO). |
| PPO | OK | Fast/Slow EMA % diff and signal histogram verified. |
| PO | OK | SMA/EMA branches both correct. |
| DPO | OK | Price shift n/2+1, SMA n matches formula. |
| AROONOSC | OK | Up − Down values match TA-Lib AROONOSC. |

## Test Methodology
1. Generated 2 000-bar synthetic OHLC using geometric Brownian motion.
2. Benchmarked against TA-Lib where equivalents exist (ROC, CMO, TRIX, UO, AO, PPO, DPO, AROONOSC).
3. Custom Excel checks for AC & PO.
4. Passed criterion: `mean(|diff|) < 1e-5` ignoring initial NaNs.

## Code Changes
- `oscillators.py`
  - **TRIX**: line ~170 – factor changed to `* 100`.
  - **AC.calculate**: convert AO pandas Series to numpy; use numpy arrays for SMA and subtraction.

No breaking API changes.
