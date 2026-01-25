### layr0-IMC Indicators Performance Audit (NumPy/Numba) — Audit 01

This document summarizes a code-level audit of the technical indicators library with a focus on NumPy/Numba efficiency and speed optimizations. It references functions and classes as implemented under `layr0-IMC/indicators/*` and utility kernels in `layr0-IMC/indicators/utils.py`, and aligns the exposed API with `docs/FUNCTION_ABBREVIATIONS_LIST.md`.

### Scope
- Reviewed core modules: `trend.py`, `oscillators.py`, `volatility.py`, `momentum.py`, `statistics.py`, `hybrid.py`, `utils.py`, `base.py`, and interface in `__init__.py`.
- Assessed: JIT usage, algorithmic complexity, array handling, duplication of kernels (EMA/ATR/SMA/STDDEV), and correctness implications.

### Framework-level improvements (global)
- **Adopt a single JIT entrypoint**: Replace direct `from numba import jit` with the project’s `layr0-IMC.numba_shim.jit` (inherits `nopython=True`, `fastmath=True`, `cache=True`). Reduces warm-up latency, enables SIMD, and ensures consistent defaults across modules.
- **Unify shared kernels**: Centralize common kernels (EMA, ATR variants, rolling SMA, rolling STDDEV) in `layr0-IMC/indicators/utils.py` and reuse everywhere to minimize compilation count and ensure consistent numerics.
- **Fix unsupported Numba call**: `BaseIndicator.rolling_window()` uses `np.lib.stride_tricks.as_strided` under `@jit(nopython=True)` which Numba does not support. Either remove Numba for this function or implement a supported approach. Leaving as-is risks runtime failure if invoked.
- **Prefer O(n) rolling algorithms** over per-step slicing. Slice-based implementations are O(n×period) and allocate views repeatedly.

### Rolling-window hotspots to convert to O(n)
Convert slice-in-loop patterns to O(n) implementations using monotonic deques (for rolling min/max), rolling sums (for mean/variance), prefix sums (for weighted sums), or Welford/Chan variance.

- **Rolling min/max via deque**:
  - `utils.highest`, `utils.lowest`
  - `trend.Ichimoku` (Tenkan/Kijun/Senkou B)
  - `volatility.Donchian`
  - `oscillators.AROONOSC` (positions for up/down)
  - `momentum.WilliamsR`, `oscillators.Stochastic` (%K range)
  - `oscillators.StochRSI` (RSI high/low range)
  - `momentum.Fisher` (window min/max)
  - `volatility.CHOP` (window high/low for denominator)

- **Rolling SMA/STDDEV/VAR via O(n)**:
  - `volatility.BollingerBands`, `volatility.STDDEV`, `__init__.py` utility `stdev`
  - `volatility.RVI` (STDDEV then RSI)
  - `volatility.BBPercent`, `volatility.BBWidth`
  - Use rolling sums and (optionally) rolling sum-of-squares or Welford/Chan for variance; avoid `np.mean(window)` per step.

- **VWMA via prefix sums**:
  - `trend.VWMA` currently loops each window. Use prefix sums for `price*volume` and `volume` to compute VWMA in O(n).

- **CMO rolling sums**:
  - `oscillators.CMO`, `trend.VIDYA` (embedded CMO): maintain rolling sums of up/down changes instead of re-summing `period` elements per step.

- **KAMA rolling volatility**:
  - `trend.KAMA` computes volatility with nested loops; maintain a rolling sum of absolute diffs (`|diff|`) by adding new and removing old values.

- **Ulcer Index complexity reduction**:
  - `volatility.UlcerIndex` is currently O(n×period²) due to nested max-in-subwindow per step. Use a deque-based rolling max of `close` to get `MaxClose`, compute per-point drawdown, and keep a rolling sum of squared drawdowns to get the average in O(n).

- **CHOP ATR sum**:
  - `volatility.CHOP` recalculates ATR sums with window slices. Compute a single TR series, maintain a rolling sum for ATR, and use deque-based high/low range; avoid per-step `np.sum(window)` and `np.max/min(window)`.

### Numba usage and parallelism
- **Parallel only after O(n)**: Apply `prange` only to loops with independent iterations and O(1) work. First convert to O(n); parallelizing O(n×period) slices rarely helps and can be slower.
- **Fastmath and caching**: The shim’s `fastmath=True` and `cache=True` are beneficial globally. Keep arrays `float64` and C-contiguous; optionally consider an expert toggle to compute in `float32` for memory/speed trade-offs.
- **Reduce kernel duplication**: Each unique kernel signature compiles separately. Consolidating EMA/ATR/SMA reduces compile overhead and memory.

### Memory and API hygiene
- **Contiguity/dtype**: `BaseIndicator.validate_input` already returns `float64` NumPy arrays; avoid redundant conversions in helper paths to prevent extra allocations.
- **Avoid per-iteration slicing**: Even in Numba, `x[i-p+1:i+1]` incurs overhead. The O(n) approaches eliminate this and reduce heap pressure.
- **Pandas boundaries**: Converting back to `pd.Series` is fine for ergonomics; document that high-throughput pipelines should supply NumPy arrays to minimize overhead.

### Duplicate logic to consolidate
- **ATR variants**: Implement two utilities in `utils.py` and reuse: (1) Wilder’s smoothing, (2) SMA-based ATR. Replace ad-hoc re-implementations in `trend._calculate_atr`, `volatility.ATR`, `volatility.STARC`, `volatility.ChandelierExit`, etc.
- **EMA kernels**: Consolidate multiple EMA variants across `trend`, `momentum`, `oscillators`, `volatility` into one or two shared kernels (seeded with SMA vs immediate start) in `utils.py`.
- **SMA kernels**: Standardize on a rolling-sum SMA. Replace slice-mean implementations in classes that currently recompute windows.

### Correctness and maintenance notes
- **NaN seeding semantics**: Preserve first-valid index behavior (typically at `period-1`) when refactoring to O(n). Many indicators rely on NaN seeds for alignment with charting expectations.
- **As-strided JIT**: Ensure `BaseIndicator.rolling_window()` no longer uses Numba with `as_strided` or provide a pure-NumPy path without JIT to avoid runtime errors.
- **Abbreviation coverage**: Public methods in `layr0-IMC/indicators/__init__.py` and aliases (e.g., `psar`/`parabolic_sar`, `bbpercent`, `bbwidth`, `ulcerindex`, `rwi`) align with `docs/FUNCTION_ABBREVIATIONS_LIST.md`. Keep a single canonical implementation per indicator and provide aliases only at the interface level.

### Expected performance impact (typical ranges)
- **O(n) rolling conversions**: ~5–30× improvement on long series depending on `period` and indicator (e.g., `Donchian`, `Aroon`, `Ichimoku`, `Bollinger`, `STDDEV`, `RVI`, `CMO`, `KAMA`, `VWMA`, `UlcerIndex`, `CHOP`).
- **Kernel consolidation + caching**: ~1.5–3× reduction in warm-up time and lower peak memory; improved numerical consistency across indicators.
- **Stability**: Removing the unsupported `as_strided` JIT path avoids potential runtime failures.

### Actionable checklist
- **JIT shim**: Use `layr0-IMC.numba_shim.jit` (and `njit/prange` from the same module) everywhere.
- **Refactor rolling windows**: Replace window slicing with O(n) algorithms: deque min/max, rolling sums, Welford variance, prefix sums.
- **Consolidate kernels**: Single `ema`, two `atr` variants, rolling `sma/stddev` in `utils.py` and reuse.
- **Optimize heavy indicators**: Prioritize `UlcerIndex`, `CHOP`, `VWMA`, `KAMA`, `CMO`, `Bollinger/STDDEV`, `Donchian`, `Aroon`, `Ichimoku`.
- **Preserve NaN/edge semantics**: Keep index alignment and NaN seeds identical to current outputs.

### Final summary
- **Unify Numba entrypoints and shared kernels** for consistent, cached, SIMD-enabled performance.
- **Eliminate O(n×period) patterns** by adopting O(n) rolling algorithms using deques and rolling sums.
- **Consolidate duplicated EMA/ATR/SMA/STDDEV code** into `utils.py` to reduce compile overhead and drift.
- **Fix `as_strided` under JIT** in `BaseIndicator.rolling_window()` to prevent unsupported Numba calls.
- **Expect major speedups** on long series (often 5–30×) for range-based indicators, with lower memory and more consistent results.


