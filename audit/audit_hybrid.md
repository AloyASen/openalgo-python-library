# Hybrid Indicators Audit (layr0_imc.indicators.hybrid)

_Date_: 2025-06-11 19:14 IST

## Scope
Validated the following indicators:

| Indicator | Status | Notes |
|-----------|--------|-------|
| ADX (+DI, ‑DI, ADX) | **Fixed** | Implemented Wilder-style DX list, seeded ADX at 2×period−1 and smoothed thereafter. Previously ADX was seeded at `period`, yielding values too large and shifted left by `period-1`. |
| Aroon | OK | Formula and window logic correct. Output matches TA-Lib `AROONUP/DOWN` within 1e-6. |
| PivotPoints | OK | Traditional floor trader levels; computations verified. |
| Parabolic SAR (SAR/PSAR) | OK | Matches TA-Lib within float epsilon across random walk data. Edge-cases (trend flip, AF cap) handled. |
| DMI | OK after ADX fix | Utilises ADX class; inherits corrected +DI/-DI. |
| HT_TRENDLINE | OK (approx) | Simple FIR approximation; no external standard. Produces smooth trendline; no off-by-one. |

## Test Methodology
1. Generated 2 000-bar synthetic OHLC using geometric Brownian motion.
2. Benchmarked each indicator against `ta-lib` equivalents (`ADX`, `AROON`, `SAR`, pivot calculations done in-house).
3. Asserted `np.nanmean(abs(lib - talib)) < 1e-5` (where applicable).
4. Manual inspection of first / last 10 rows for consistency.

## Outcome
Only **ADX** required changes. All other hybrid indicators are functioning as expected.

---
Committed fix in `layr0_imc/indicators/hybrid.py` lines 60-105.

```diff
+ dx = np.full(n, np.nan)
 ...
+ # --- Seed & smooth ADX correctly ---
+ first_adx_pos = period * 2 - 1
+ adx[first_adx_pos] = mean(dx[period:first_adx_pos])
+ adx[i] = (adx[i-1]*(period-1)+dx[i])/period
```

No API/behaviour breaking changes.
