# Autoresearch Scorecard — python-data-pipeline
**Date:** 2026-06-26  
**Goal:** Minimize `runtime_ms` for `target/process.py` (100,000-row sales CSV → output.json)  
**Benchmark:** median of 5 subprocess runs via `autoresearch/benchmark.py`

---

## Results Summary

| # | Experiment | runtime_ms | vs Baseline | vs Prev | Status |
|---|-----------|-----------|-------------|---------|--------|
| 0 | Baseline (unoptimized) | 558.1 | — | — | keep |
| 1 | Pandas vectorized ops | 548.4 | −1.7% | −1.7% | keep |
| 2 | Optimized stdlib — single pass | 190.1 | −65.9% | −65.4% | keep |
| 3 | `csv.reader` + positional indexing | 138.5 | −75.2% | −27.1% | keep |
| 4 | `capitalize()` + product cache + `defaultdict` | **118.6** | **−78.7%** | −14.4% | **keep (best)** |
| 5 | Welford's online variance in hot loop | 134.9 | −75.8% | +13.7% | discard |

**Best result: 118.6ms — 4.7× faster than baseline (558.1ms)**

---

## Experiment Details

### Exp 1 — Pandas vectorized ops (548.4ms, −1.7%)
**What:** Replaced all stdlib loops with `pandas.read_csv` + `groupby` aggregations.  
**Why it barely helped:** `import pandas` costs ~410ms per subprocess invocation. The actual data processing dropped from ~550ms to ~130ms, but the import tax almost entirely cancelled that gain.  
**Lesson:** Pandas is the wrong tool when the script is invoked as a subprocess — startup cost dominates.

### Exp 2 — Optimized stdlib, single CSV pass (190.1ms, −65.9%)
**What:** Eliminated 3 redundant CSV re-reads (the original read the file 4× total). Replaced O(n²) list-scan deduplication with set-based accumulators. Replaced bubble sort with `sorted()`. All aggregations done in one pass with dict accumulators.  
**Why it helped so much:** Removed 3 full file scans (300k+ extra rows processed) and dropped the O(n²) dedup loops. Python startup + stdlib import is only ~8ms vs 410ms for pandas.

### Exp 3 — `csv.reader` + positional indexing (138.5ms, −27.1%)
**What:** Replaced `csv.DictReader` with `csv.reader` and accessed fields by column index. Stored region accumulator as a `list` instead of a `dict`.  
**Why it helped:** `DictReader` creates a new `dict` object for every row (100k dicts × 8 keys = 800k key lookups and allocs). Direct positional access eliminates that overhead entirely.

### Exp 4 — String op cache + `capitalize()` + `defaultdict` (118.6ms, −14.4%) ✅ FINAL
**What:** Three micro-optimizations compounded:
- `str.capitalize()` (1 call) replaced the `[0].upper() + [1:].lower()` pattern (3 string objects per row × 200k rows)
- Product name `.title()` results cached in a dict — many rows share the same product string, so the title-casing is computed once per unique product rather than once per row
- `defaultdict` replaced manual `if key not in` guards throughout  

**Why it helped:** Profile showed string method calls accounted for ~22ms (14% of runtime). Caching `.title()` and reducing `.upper()/.lower()` calls to a single `.capitalize()` shaved ~20ms off the hot loop.

### Exp 5 — Welford's online variance (134.9ms, DISCARDED)
**What:** Moved variance computation into the main loop using Welford's algorithm (streaming mean + M2 accumulator), eliminating the post-processing `sum(genexpr)` over each category's revenue list. Also tracked min/max incrementally.  
**Why it regressed:** Welford's requires 3 extra floating-point operations and 3 extra list-element assignments per row in the hot loop (~100k iterations). The post-processing variance genexpr it replaced only ran over ~5 categories × 20k items = ~100k iterations total — the same work, but in a tighter, simpler loop. Moving it into the hot loop added branching and attribute access overhead that outweighed the savings.

---

## Key Insights

1. **Import cost matters for subprocess-invoked scripts.** pandas shaved ~420ms off processing time but added 410ms of import overhead — nearly a wash. Always profile with `subprocess` timing, not in-process.

2. **Eliminate algorithmic waste before micro-optimizing.** The biggest win (Exp 2, −65.9%) came from removing 3 redundant file reads and an O(n²) dedup loop — structural fixes, not tuning.

3. **Per-row object allocation is expensive at 100k rows.** Switching from `DictReader` (creates a dict per row) to `reader` (list per row, accessed by index) saved 27% on its own.

4. **String method call volume adds up.** 200k `.upper()` + 200k `.lower()` calls across a hot loop cost ~14ms. Caching repeated `.title()` calls and using `.capitalize()` cut that to near-zero.

5. **Online algorithms don't always win.** Welford's is great for infinite streams; for a bounded 100k-row file with only ~5 categories, a two-pass approach (accumulate list → compute stats) is faster because the post-pass is cache-warm and tight.

---

## Final State

**Winning file:** `target/process.py` (Exp 4 version)  
**Benchmark harness:** `autoresearch/benchmark.py` (fixed, not modified)  
**Full run log:** `autoresearch/results.tsv`
