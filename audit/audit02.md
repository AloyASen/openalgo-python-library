### layr0-IMC Indicators Performance Audit (NumPy/Numba) — Audit 02

This follow-up audit reflects recent refactors and optimizations. It validates progress and lists the remaining high-value improvements. References use module paths like `layr0-IMC/indicators/*` and utilities in `layr0-IMC/indicators/utils.py`.

### What’s improved since Audit 01
- **JIT shim available**: `layr0-IMC/numba_shim.py` provides cached, fastmath-enabled `jit/njit/prange` defaults.
- **Base rolling-window fix**: `BaseIndicator.rolling_window()` no longer attempts Numba on `as_strided`, preventing unsupported-call failures. A safe `rolling_window_numba()` exists.
- **O(n) utility kernels added** (Numba, cached):
  - Rolling extrema: `utils.highest`, `utils.lowest` (deque-based)
  - Rolling averages/variance: `utils.sma`, `utils.stdev`, `utils.rolling_variance`, `utils.rolling_sum`
  - ATR variants: `utils.true_range`, `utils.atr_wilder`, `utils.atr_sma`
  - EMA variants: `utils.ema`, `utils.ema_wilder`
  - Indicator-specific: `utils.vwma_optimized`, `utils.cmo_optimized`, `utils.kama_optimized`

These utilities enable broad O(n) refactors and reduce duplication.

### Remaining opportunities (highest impact first)
- **Adopt the JIT shim everywhere**
  - Many modules still use `from numba import jit`. Switch to `from layr0-IMC.numba_shim import jit` (and `njit/prange`) across `trend.py`, `oscillators.py`, `volatility.py`, etc., to standardize `fastmath=True, cache=True`.

- **Replace slice-in-loop rolling logic with O(n) utils**
  - **Volatility**:
    - `BollingerBands`: compute middle with `utils.sma`, and bands from `utils.stdev` (drop per-window mean/variance loops).
    - `Donchian`: use `utils.highest/lowest` instead of window `.max()/.min()` per step.
    - `CHOP`: compute `TR` once; maintain ATR with `utils.rolling_sum(TR, period)` and range with deque-based highest/lowest. Avoid repeated `np.sum` and `np.max/min` windows.
    - `RVI (Relative Volatility Index)`: replace internal `_calculate_stdev` with `utils.stdev`; keep RSI-on-STDDEV code.
    - `UlcerIndex`: current version reduced complexity but still loops inner windows. Implement deque-based rolling max of close and maintain a rolling sum of squared drawdowns to achieve true O(n).
  - **Trend**:
    - `VWMA`: use `utils.vwma_optimized` (prefix-sum O(n)) instead of nested window sums.
    - `KAMA`: use `utils.kama_optimized` (O(n) rolling volatility); remove nested volatility loops.
    - `Ichimoku`: compute Tenkan/Kijun/Senkou B using `utils.highest/lowest` for range halves (replace per-window `.max()/.min()`).
  - **Oscillators**:
    - `AROONOSC`: determine positions using deque-based rolling extrema (or track index of max/min) rather than window scans.
    - `AO`/`AC`, `PO`/`DPO`, `KST`: use `utils.sma` (and `utils.ema` where appropriate) + `utils.roc` to avoid window averages recomputation.

- **Consolidate duplicated kernels**
  - **EMA and ATR** implementations exist in many classes. Replace with `utils.ema`/`utils.ema_wilder` and `utils.atr_wilder`/`utils.atr_sma` to reduce compile count and ensure consistent numerics.

- **Keep dtype/contiguity guarantees**
  - Continue using `BaseIndicator.validate_input` to provide `float64` C-contiguous arrays; avoid redundant conversions down-stream.

### Correctness and API notes
- **NaN seeding**: Preserve first-valid index behavior (typically at `period-1`) when switching to utils, so visual alignment remains unchanged.
- **Interface stability**: Keep aliases in `__init__.py` while consolidating internal implementations to a single source of truth.

### Suggested file-level actions (quick map)
- `volatility.py`: Bollinger, STDDEV, RVI, Donchian, CHOP, UlcerIndex → replace per-window logic with `utils.stdev`, `utils.highest/lowest`, `utils.rolling_sum`, `utils.atr_*`.
- `trend.py`: VWMA → `utils.vwma_optimized`; KAMA → `utils.kama_optimized`; Ichimoku ranges → `utils.highest/lowest`.
- `oscillators.py`: AO/AC/PO/DPO/KST/AROONOSC → use `utils.sma/ema/roc` and deque-based ranges.
- Across all: switch `numba.jit` to `layr0-IMC.numba_shim.jit` and remove duplicated EMA/ATR kernels.

### Expected impact
- O(n) conversions on remaining hotspots typically yield 5–20× speedups on long series (larger gains for big `period`), with lower memory churn.
- Kernel consolidation reduces JIT warm-up and improves cache reuse; consistent math across indicators.

### Final summary
- Great progress: unsafe `as_strided` JIT path fixed; a strong set of O(n) kernels exist in `utils.py`.
- Next steps: systematically replace slice-in-loop patterns with those utils, adopt the shim JIT everywhere, and deduplicate EMA/ATR implementations.
- Target biggest wins first: `Bollinger/STDDEV/RVI`, `Donchian/Ichimoku/AROON`, `VWMA/KAMA`, `CHOP/UlcerIndex`.


