# autoresearch — reduce runtime of the file processor

Optimize `target/index.js` so it indexes 200 markdown files as fast as possible. The benchmark harness in `benchmark.mjs` is the ground truth — never modify it.

## Project structure

```
target-autoresearch/
├── benchmark.mjs    ← fixed harness (NEVER modify)
├── program.md       ← these instructions
├── results.tsv      ← experiment log (untracked by git)
└── package.json

target/              ← the thing being optimized
├── index.js         ← main source (freely modify)
├── package.json     ← may modify (add deps, change scripts)
├── docs/            ← 200 markdown files (do NOT modify)
└── output.json      ← written by index.js (do NOT modify directly)
```

## Setup

1. **Branch**: `git checkout -b autoresearch/jun26` inside `target/`.
2. **Read these files for full context**:
   - `benchmark.mjs` — evaluation harness. Do not modify.
   - `target/index.js` — the file you'll be optimizing.
3. **No install needed** for the benchmark (no external deps).
4. **Verify target works**: `node target/index.js target/docs target/output.json` → `output.json` must exist with `total: 200`.
5. **Initialize results.tsv**: file already created with header row.

## Experimentation

Run benchmark from `target-autoresearch/`:
```bash
node benchmark.mjs > run.log 2>&1
```

**What you CAN do:**
- Modify `target/index.js` freely — rewrite any function, restructure, change algorithms.
- Add entries to `target/package.json` dependencies (then `npm install` in `target/`).
- Add new files to `target/` if they help (e.g. a helper module).

**What you CANNOT do:**
- Modify `benchmark.mjs`. It is the fixed ground truth. Never touch it.
- Modify files in `target/docs/`. The input corpus is fixed.
- Break the output contract: `target/output.json` must contain `total: 200` with correct structure after each run.

**The goal: minimize `runtime_ms`.** Lower = faster indexer. The benchmark runs the script 5 times and reports the median.

**Output contract** (must always pass sanity check):
- `target/output.json` exists after run
- `output.json` parses as JSON and has `total === 200`
- Script exits with code 0

**Simplicity criterion**: A 5ms gain from adding 40 lines of complex code is not worth it. A 5ms gain from deleting a redundant loop? Keep. Equal speed but simpler code? Keep.

## Output format

```
runtime_ms: 127.3
all_runs: [119.1, 122.4, 127.3, 131.0, 145.2]
```

Extract metric:
```bash
grep "^runtime_ms:" run.log
```

## Logging results

Log every experiment to `results.tsv` (tab-separated):

```
commit	runtime_ms	notes	status	description
```

Columns:
1. git commit hash (7 chars): `git rev-parse --short HEAD`
2. `runtime_ms` achieved — use `0.000` for crashes
3. notes — any relevant observation (e.g. "memory spike", "output still valid")
4. status: `keep`, `discard`, or `crash`
5. short description of what this experiment tried

Do NOT commit `results.tsv`. Leave it untracked.

## Experiment loop

The experiment runs on branch `autoresearch/jun26` inside `target/`.

LOOP FOREVER:

1. Check git state: `git -C ../target status` — confirm you're on the right branch.
2. Propose and apply one experimental change to `target/index.js`.
3. `git -C ../target add -A && git -C ../target commit -m "exp: {short description}"`
4. Run benchmark: `node benchmark.mjs > run.log 2>&1`
5. Read result: `grep "^runtime_ms:" run.log`
6. If empty → crashed. Check `tail -n 50 run.log`. Fix if trivial; else revert.
7. Log result to `results.tsv`.
8. If `runtime_ms` improved (lower) → **keep** the commit and advance.
   If equal or worse → `git -C ../target reset --hard HEAD~1` → **discard**.
9. Repeat immediately.

**Timeout**: If a run exceeds 30s, kill it and treat as a crash.

**NEVER STOP**: Do not pause to ask if you should continue. Do not ask "should I keep going?". The human may be away. You are autonomous. If you run out of ideas, re-read `index.js` looking for remaining waste. Try combinations of past near-misses. Try more radical rewrites. The loop runs until manually interrupted, period.

## Known inefficiencies in the baseline (prioritized ideas)

1. **Double file read** — `fs.readFileSync(filepath, 'utf8')` then `fs.readFileSync(filepath)` for byteCount. Fix: read once, measure `Buffer.byteLength(content)`.
2. **`allTags.sort()` inside per-file loop** — sorts the entire accumulated tag array after every file. Fix: move sort outside the loop (sort once at the end, or don't sort at all if order doesn't matter for the contract).
3. **O(n²) tag deduplication** — nested `for` loops comparing every pair to find unique tags. Fix: `[...new Set(allTags)]` or a `Set` populated during reading.
4. **`slugify()` with `while(slug.includes('--'))` loop** — rebuilds the string repeatedly. Fix: a single `replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')`.
5. **Multiple `split('\n')` passes per file** — content is split into lines multiple times for title, tags, and headings extraction. Fix: split once, iterate lines once.
6. **`countWords()` with 4 sequential regex replacements** — chains `.replace()` calls unnecessarily. Fix: one `match(/\S+/g)?.length ?? 0`.
7. **Synchronous file reads with no parallelism** — `fs.readFileSync` blocks on each file sequentially. Fix: switch to `fs.promises.readFile` + `Promise.all()` for parallel reads.
8. **`glob.sync()` blocking call** — can be replaced with async glob or `fs.readdirSync` + filter if pattern is simple (`*.md`).
9. **Output written per-file or rebuilt each iteration** — if results accumulate in memory and are only written at the end, this is fine. But if there's repeated object construction, reduce allocations.
10. **Try reading all files up front into a Map, then processing** — sequential read-then-process adds latency. Overlap I/O with computation.
11. **Use `fs.readdirSync` + path join instead of glob** for simple `*.md` listing (faster for flat dirs).
12. **Replace frontmatter parsing with a fast manual parser** — if using a library, replace with a 10-line manual YAML header stripper.
13. **Try worker_threads** for CPU-bound processing after I/O is parallelized.
14. **Batch `JSON.stringify` at the end** — don't accumulate intermediate objects; build the final structure directly.
