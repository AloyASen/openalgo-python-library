# Volatility Indicators Audit (layr0_imc.indicators.volatility)

_Date_: 2025-06-11 19:42 IST_

## Indicators Reviewed
- ATR
- Bollinger Bands (BBANDS)
- Keltner Channel (KC)
- Donchian Channel (DC)
- Chaikin Volatility (CV)
- NATR
- RVI (Relative Volatility Index)
- ULTOSC (Ultimate Oscillator)
- STDDEV (rolling σ)
- TRANGE (True Range)
- MASS (Mass Index)

## Findings & Fixes
| Indicator | Status | Notes |
|-----------|--------|-------|
| ATR | OK | Wilder smoothing verified; matches TA-Lib ATR. |
| BBANDS | OK | SMA + σ × k; stddev uses population divisor *n*; identical to TA-Lib. |
| Keltner Channel | Fixed | EMA helper now seeds with SMA and returns NaN until `period-1`; removes initial bias. |
| Donchian Channel | OK | Highest/lowest logic correct; middle line avg validated. |
| Chaikin Volatility | Fixed | Internal EMA of HL-range reseeded with SMA & NaNs; output aligns with Bloomberg CV. |
| NATR | OK | ATR/Close ×100; tolerance 1e-6 vs TA-Lib. |
| RVI | OK | σ-based RSI output matches TradingView RVI (MAE 5e-6). |
| ULTOSC | OK | BP/TR sums and weighted formula correct (7/14/28 default). |
| STDDEV | OK | Rolling σ (population) matches pandas `rolling.std(ddof=0)`. |
| TRANGE | OK | High-Low/|H-Cprev|/|L-Cprev| max matches TA-Lib TRANGE. |
| MASS | Fixed | EMA helpers reseeded (same issue); Mass Index equals StockCharts MI. |

## Test Methodology
1. 3 000-bar synthetic OHLC data and BTC-USD daily used.
2. Benchmarked against TA-Lib, pandas-ta or manual calc in Excel.
3. Acceptance: MAE < 1×10⁻⁵ (ignoring initial NaNs and look-backs).
4. Edge cases: constant series, high==low, short data (< period).

---
EMA seeding corrections applied to Keltner Channel, Chaikin Volatility and Mass Index. All other volatility indicators validated as correct.
