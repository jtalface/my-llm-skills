---
name: autoresearch
description: "Universal optimization scaffold using the Karpathy autoresearch technique. Invoke with /autoresearch [goal] [target path] to autonomously optimize anything: website load time, script runtime, API latency, build time, bundle size, etc. Analyzes the target, generates a fixed benchmark harness, scaffolds the full project structure (benchmark, program.md, results.tsv), runs a baseline, then loops forever — modify, benchmark, keep or revert — until manually stopped. ALWAYS trigger when the user says /autoresearch, \"autonomously optimize\", \"run autoresearch on\", or \"apply autoresearch to\" anything."
---

# autoresearch — universal optimization scaffold

Applies the Karpathy autoresearch technique to **any optimization goal**: reads the target, designs a benchmark harness, scaffolds the full project structure, runs a baseline, then enters an autonomous experiment loop that modifies → benchmarks → keeps or reverts, forever, until manually interrupted.

## Trigger

Invoke this skill when the user says any of:
- `/autoresearch <goal description> [<target path>]`
- "run autoresearch on X"
- "autonomously optimize X"
- "apply autoresearch to X"
- "set up an autoresearch loop for X"

## Core pattern (from Karpathy)

The autoresearch pattern has four components:
1. **Fixed benchmark harness** — immutable file that defines the metric. NEVER modified by the agent.
2. **Mutable target** — the files the agent freely edits to improve the metric.
3. **`program.md`** — agent instructions written by the human, read by the AI.
4. **`results.tsv`** — audit trail of every experiment (untracked by git).

The loop: `modify → benchmark → if improved: keep commit / else: git reset → log → repeat`

---

## EXECUTION — follow these phases in order

### PHASE 1: Parse the invocation

Extract from the user's message:
- `GOAL` — the optimization objective (e.g. "optimize load time", "speed up runtime", "reduce bundle size", "improve API latency")
- `TARGET_PATH` — path to the thing being optimized (directory, file, or project root). If not provided, ask the user for it before proceeding.

Derive:
- `TARGET_NAME` — basename of TARGET_PATH (e.g. `my-site`, `process-data`)
- `SCAFFOLD_DIR` — sibling directory: `{parent of TARGET_PATH}/{TARGET_NAME}-autoresearch/`
- `DATE_TAG` — today's date as `{mon}{day}` (e.g. `jun26`)

---

### PHASE 2: Analyze the target

Read the target to understand what you're working with. Use your file/bash tools:

1. List all files in TARGET_PATH (excluding `node_modules/`, `.git/`, build outputs, `__pycache__/`).
2. Read the key files: entry points, configuration, main source files, any existing benchmark/test scripts.
3. Determine:
   - **Tech stack** (Node.js, Python, browser app, Go, shell, etc.)
   - **What produces the measurable output** (a server, a script, a build command)
   - **What the agent can freely modify** (source files, config, assets)
   - **What must remain functionally correct** (the thing must still work after each change)
   - **Rough baseline** (if you can estimate or quickly run the current metric, do it)

---

### PHASE 3: Design the benchmark harness

Based on the goal and stack, choose:

#### A. What metric to measure (single scalar, lower = better)

| Goal type | Metric | How to measure |
|-----------|--------|----------------|
| Website / web app load time | `load_time_ms` | Puppeteer: `loadEventEnd - startTime`, median of 5 runs, cache disabled |
| Website LCP / FCP | `lcp_ms` / `fcp_ms` | Puppeteer PerformanceObserver |
| Website bundle / transfer size | `bundle_kb` | Sum of response sizes, or output file size |
| Script / CLI runtime | `runtime_ms` | `performance.now()` wrapper or Python `timeit`, median of 5 runs |
| API endpoint latency | `p50_ms` | `autocannon` 5s load test, or fetch loop |
| Build / compile time | `build_time_ms` | Time the build command, median of 3 runs |
| Database query | `query_ms` | Timed query loop, median of 10 runs |
| Custom / inferred | Infer from GOAL | Design a harness that isolates the bottleneck |

If the goal mentions multiple metrics, pick ONE as the primary optimization target. Others can be logged as secondary.

#### B. What language/runtime for the harness

- Website (any stack) → `benchmark.mjs` using Puppeteer (ESM, Node.js)
- Node.js script → `benchmark.mjs` using Node timing
- Python script → `benchmark.py` using `timeit` / `subprocess`
- API / server → `benchmark.mjs` using `autocannon` or fetch loop
- Build system → `benchmark.sh` timing the build command
- General → `benchmark.sh` using `date +%s%N` timing

#### C. Harness requirements (always enforce these)

- Outputs **exactly one primary metric line**: `{metric_name}: {value}` (e.g. `load_time_ms: 312.4`)
- Outputs a second line with raw runs: `all_runs: [v1, v2, v3, ...]`
- Runs N ≥ 3 times and reports the **median** (reduces noise)
- Includes a **sanity check**: verify the target is still working (HTTP 200, correct output, file exists, etc.). If the sanity check fails, print an error and `exit 1`.
- Exit code 0 on success, non-zero on failure
- Fully self-contained — no CLI arguments needed (hardcode the URL, path, command)
- Prints nothing extra that would confuse `grep "^{metric_name}:"`

Write this as `SCAFFOLD_DIR/benchmark.{ext}`. This file is NEVER modified.

#### Benchmark templates

**Puppeteer (websites) — `benchmark.mjs`:**
```js
import puppeteer from 'puppeteer';

const URL = 'http://localhost:{PORT}';
const RUNS = 5;

async function run() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu', '--disable-extensions']
  });

  // Sanity check
  const check = await browser.newPage();
  const res = await check.goto(URL, { waitUntil: 'domcontentloaded' });
  if (!res || res.status() >= 400) {
    console.error(`Sanity check failed: HTTP ${res?.status()}`);
    await browser.close();
    process.exit(1);
  }
  await check.close();

  const times = [];
  for (let i = 0; i < RUNS; i++) {
    const page = await browser.newPage();
    await page.setCacheEnabled(false);
    await page.goto(URL, { waitUntil: 'load' });
    const t = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      return nav.loadEventEnd - nav.startTime;
    });
    times.push(t);
    await page.close();
  }

  await browser.close();
  times.sort((a, b) => a - b);
  const median = times[Math.floor(times.length / 2)];
  console.log(`load_time_ms: ${median.toFixed(1)}`);
  console.log(`all_runs: [${times.map(t => t.toFixed(1)).join(', ')}]`);
}

run().catch(e => { console.error(e); process.exit(1); });
```

**Python script timing — `benchmark.py`:**
```python
import subprocess, sys, time, statistics, os

TARGET = [sys.executable, '{path/to/script.py}']  # adjust as needed
ARGS   = []  # additional args if needed
RUNS   = 5

# Sanity check: script must exit 0
result = subprocess.run(TARGET + ARGS, capture_output=True)
if result.returncode != 0:
    print(f"Sanity check failed:\n{result.stderr.decode()}", file=sys.stderr)
    sys.exit(1)

times = []
for _ in range(RUNS):
    t0 = time.perf_counter()
    subprocess.run(TARGET + ARGS, capture_output=True)
    times.append((time.perf_counter() - t0) * 1000)

times.sort()
median = times[len(times) // 2]
print(f"runtime_ms: {median:.1f}")
print(f"all_runs: [{', '.join(f'{t:.1f}' for t in times)}]")
```

**Shell command timing — `benchmark.sh`:**
```bash
#!/usr/bin/env bash
set -euo pipefail

TARGET_CMD="{command to benchmark}"
RUNS=5
TIMES=()

# Sanity check
eval "$TARGET_CMD" > /dev/null 2>&1 || { echo "Sanity check failed" >&2; exit 1; }

for i in $(seq 1 $RUNS); do
  START=$(date +%s%N)
  eval "$TARGET_CMD" > /dev/null 2>&1
  END=$(date +%s%N)
  TIMES+=( $(( (END - START) / 1000000 )) )
done

IFS=$'\n' SORTED=($(sort -n <<< "${TIMES[*]}")); unset IFS
N=${#SORTED[@]}
MEDIAN=${SORTED[$((N / 2))]}

echo "runtime_ms: $MEDIAN"
echo "all_runs: [$(IFS=', '; echo "${SORTED[*]}")]"
```

**Node.js script timing — `benchmark.mjs`:**
```js
import { execSync } from 'child_process';
import { performance } from 'perf_hooks';

const CMD = 'node {path/to/script.js}';
const RUNS = 5;

// Sanity check
try { execSync(CMD, { stdio: 'pipe' }); }
catch (e) { console.error('Sanity check failed:', e.stderr?.toString()); process.exit(1); }

const times = [];
for (let i = 0; i < RUNS; i++) {
  const t0 = performance.now();
  execSync(CMD, { stdio: 'pipe' });
  times.push(performance.now() - t0);
}

times.sort((a, b) => a - b);
const median = times[Math.floor(times.length / 2)];
console.log(`runtime_ms: ${median.toFixed(1)}`);
console.log(`all_runs: [${times.map(t => t.toFixed(1)).join(', ')}]`);
```

Adapt whichever template fits the goal. Fill in the hardcoded values (PORT, path, command).

---

### PHASE 4: Scaffold the project

Create `SCAFFOLD_DIR/` with the following files:

#### 4a. `benchmark.{ext}` — the fixed harness (already designed in Phase 3)

#### 4b. `package.json` (if Node.js harness)
```json
{
  "name": "{TARGET_NAME}-autoresearch",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "benchmark": "node benchmark.mjs"
  },
  "dependencies": {
    "puppeteer": "^24.0.0"
  }
}
```
Adjust dependencies to match what the harness actually imports.

#### 4c. `requirements.txt` (if Python harness)
Only include packages the benchmark actually uses (usually none beyond stdlib).

#### 4d. `results.tsv` — just the header row
```
commit	{metric_name}	{secondary_metric_or_notes}	status	description
```
Leave untracked by git.

#### 4e. `.gitignore`
```
node_modules/
run.log
results.tsv
.cache/
__pycache__/
*.pyc
```

#### 4f. `program.md` — the agent instructions

Write a `program.md` tailored to this specific goal. It MUST contain:

```markdown
# autoresearch — {GOAL}

{One sentence: what this is, what the agent optimizes, what it's not allowed to touch.}

## Project structure

\`\`\`
{TARGET_NAME}-autoresearch/
├── benchmark.{ext}    ← fixed harness (never modify)
├── program.md         ← agent instructions (human edits this)
├── results.tsv        ← experiment log (untracked)
└── {dep file}

{TARGET_NAME}/         ← the thing being optimized
├── {key files}
└── ...
\`\`\`

## Setup

To set up a new experiment:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `{DATE_TAG}`). Branch `autoresearch/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from main/master.
3. **Read the in-scope files**: Read these for full context:
   - `benchmark.{ext}` — evaluation harness and metric definition. Do not modify.
   - {list of key mutable files to read}
4. **Install benchmark deps**: `{install command}` from `{SCAFFOLD_DIR}/`.
5. **Verify the target works**: {how to confirm the target runs and produces valid output}.
6. **Initialize results.tsv**: Create with just the header row. Baseline recorded after first run.
7. **Confirm and go.**

## Experimentation

Run benchmark from `{SCAFFOLD_DIR}/`:
\`\`\`bash
{benchmark run command} > run.log 2>&1
\`\`\`

**What you CAN do:**
- {exhaustive list of files and types of changes the agent is allowed to make}

**What you CANNOT do:**
- Modify `benchmark.{ext}`. It is the fixed ground truth metric. Do not touch it.
- {other hard constraints: must preserve functionality, must not crash, etc.}

**The goal: minimize `{metric_name}`.** {One sentence on why lower is better and what it measures.}

**Visual / functional quality** is a hard constraint. {If applicable: describe what "still works" means. The output must be correct, the page must still function, etc.}

**Simplicity criterion**: All else equal, simpler is better. A small improvement from adding 40 lines of hacky code is usually not worth it. A similar improvement from deleting code? Always keep. Equal metric but simpler code? Keep.

**First run**: Always establish baseline first — run the benchmark against the unmodified target.

## Output format

\`\`\`
{metric_name}: {example_value}
all_runs: [{example_values}]
\`\`\`

Extract metric:
\`\`\`bash
grep "^{metric_name}:" run.log
\`\`\`

## Logging results

Log every experiment to `results.tsv` (tab-separated, NOT comma-separated):

\`\`\`
commit	{metric_name}	{secondary_column}	status	description
\`\`\`

Columns:
1. git commit hash (short, 7 chars)
2. `{metric_name}` achieved — use `0.000` for crashes
3. {secondary metric description, e.g. transfer size, or notes}
4. status: `keep`, `discard`, or `crash`
5. short description of what this experiment tried

Do NOT commit `results.tsv`. Leave it untracked.

## Experiment loop

The experiment runs on branch `autoresearch/{DATE_TAG}`.

LOOP FOREVER:

1. Check git state: confirm you're on the right branch and know the current commit.
2. Propose and apply one experimental change to the mutable target files.
3. `git add -A && git commit -m "{short description}"`
4. {Any required setup step: restart server, rebuild, clear cache, etc.}
5. Run benchmark: `{benchmark command} > run.log 2>&1`
6. Read result: `grep "^{metric_name}:" run.log`
7. If grep returns empty → crashed. Run `tail -n 50 run.log` to diagnose. Fix if trivial. If the idea is fundamentally broken, skip it.
8. Log result to `results.tsv`.
9. If `{metric_name}` improved (lower) → **keep** the commit and advance.
   If equal or worse → `git reset --hard HEAD~1` → **discard**.
10. Repeat immediately.

**Timeout**: If a run exceeds {timeout, e.g. 2 minutes for web, 30s for scripts}, kill it and treat as a crash.

**NEVER STOP**: Once the loop has begun, do NOT pause to ask the human if you should continue. Do NOT ask "should I keep going?" or "is this a good stopping point?". The human may be asleep. You are autonomous. If you run out of ideas, think harder: re-read the target files for obvious waste, try combinations of past near-misses, try more radical changes. The loop runs until manually interrupted, period.

## Ideas to try (non-exhaustive, prioritized)

{ORDERED LIST of optimization ideas specific to this goal type and tech stack.
Start with highest-impact, lowest-risk. End with more speculative/structural changes.
Be specific: not "optimize images" but "convert PNGs to WebP at quality 80 using sharp or cwebp".
Include at least 10 ideas.}
```

---

### PHASE 5: Initialize and install

```bash
# Create SCAFFOLD_DIR
mkdir -p {SCAFFOLD_DIR}
cd {SCAFFOLD_DIR}

# Install benchmark deps
npm install      # for Node.js harness
# or: pip install -r requirements.txt
# or: chmod +x benchmark.sh

# Initialize git if needed
# If TARGET_PATH is already inside a git repo, just create a branch:
git -C {TARGET_REPO_ROOT} checkout -b autoresearch/{DATE_TAG}
# If not in a git repo at all, init one:
git -C {TARGET_PATH} init && git -C {TARGET_PATH} add -A && git -C {TARGET_PATH} commit -m "initial state"
git -C {TARGET_PATH} checkout -b autoresearch/{DATE_TAG}
```

---

### PHASE 6: Run baseline

```bash
{start the target if needed, e.g.: cd {TARGET_PATH} && node server.js &}
cd {SCAFFOLD_DIR}
{benchmark run command} > run.log 2>&1
grep "^{metric_name}:" run.log
```

Parse the baseline value. Log it to `results.tsv`:
```
{short_commit_hash}	{baseline_value}	{secondary}	keep	baseline (unoptimized)
```

Print a summary to the user:
```
✓ Scaffold created: {SCAFFOLD_DIR}
✓ Baseline: {metric_name} = {value}
↻ Starting experiment loop...
```

---

### PHASE 7: Autonomous experiment loop

Repeat until the user manually stops:

1. **Propose** the next experiment idea.
   - Track what you've tried. Don't repeat failures.
   - Work from the ideas list in `program.md` but adapt based on what's worked so far.
   - If ideas are exhausted, re-read the target files looking for new inefficiencies.
   - Escalate from low-hanging fruit → structural changes → speculative ideas.

2. **Apply** the change using your file editing tools. Make focused, atomic changes — one idea per commit.

3. **Commit**: `git add -A && git commit -m "exp: {short description}"`

4. **Setup** (if required): restart server, rebuild, etc.

5. **Benchmark**: `{benchmark command} > run.log 2>&1`

6. **Parse**:
   ```bash
   grep "^{metric_name}:" run.log
   ```
   Empty → crash. Read `tail -n 50 run.log`. Fix trivially or revert and skip.

7. **Decide**:
   - New value < current best → **KEEP**. Update best. Mark `keep` in tsv.
   - New value ≥ current best → **DISCARD**. `git reset --hard HEAD~1`. Mark `discard` in tsv.
   - Crash → **DISCARD** + fix. Mark `crash` in tsv. Revert if the commit broke anything.

8. **Log** every experiment to `results.tsv` — even discards and crashes.

9. **Repeat immediately.** No pauses. No questions.

---

## Goal-type-specific guidance

### Website performance

**Common mutable files**: `public/index.html`, `public/style.css`, `public/app.js`, `public/images/*`, `server.js`, `{framework config}`

**Benchmark**: Puppeteer, 5 runs, median `load_time_ms`. Port must be hardcoded.

**Setup**: Target server must be running before benchmarking. Restart after `server.js` changes. Static file changes are picked up automatically.

**Ideas to try (in priority order)**:
1. Convert PNG/JPG images to WebP at quality 80 (use `sharp` or `cwebp`)
2. Resize images to actual display dimensions (not 2000px originals)
3. Enable gzip/brotli compression on the server (Express: `compression` middleware)
4. Move render-blocking JS to end of `<body>` with `defer` attribute
5. Replace heavy libraries with native equivalents (e.g. lodash → native JS)
6. Replace `@import` Google Fonts with `<link rel="preconnect">` + `<link>` in `<head>`
7. Add `loading="lazy"` to below-the-fold images
8. Add cache headers for static assets (`Cache-Control: max-age=31536000`)
9. Inline critical CSS, defer the rest
10. Minify CSS (remove comments, whitespace)
11. Minify JS (remove comments, whitespace, console.logs)
12. Remove unused CSS rules
13. Use `srcset` and `sizes` for responsive images
14. Add `<link rel="preload">` for hero image with `fetchpriority="high"`
15. Convert icon fonts to inline SVG
16. Use AVIF instead of WebP if sharp supports it
17. Split and defer non-critical CSS
18. Add `dns-prefetch` for third-party domains
19. HTTP/2 push (if server supports it)
20. Move to a CDN for static assets (last resort; simulate with aggressive caching)

**Constraints**: The page must still be visually correct and functionally complete. All required sections must exist. Broken layout or missing content = discard even if metric improved.

---

### Python script / data pipeline

**Benchmark**: Python subprocess timing, 5 runs, median `runtime_ms`.

**Ideas to try (in priority order)**:
1. Profile with `cProfile` to find the hotspot (do this in the first experiment to guide all others)
2. Replace slow loops with vectorized NumPy operations
3. Cache expensive computations (memoize, write to disk)
4. Use generators instead of building full lists
5. Use faster I/O (binary formats vs CSV, `orjson` vs `json`)
6. Parallelize with `multiprocessing.Pool` or `concurrent.futures`
7. Use more efficient data structures (`deque`, `set` instead of `list` for lookups)
8. Pre-compile regexes
9. Use `__slots__` on hot classes
10. Profile memory: reduce allocations in hot loops
11. Replace Python loops with `map`/`filter`/list comprehensions
12. Use `functools.lru_cache` for repeated pure calls
13. Try PyPy (if compatible)
14. Reduce I/O: read files once, batch writes

---

### Node.js script / CLI

**Benchmark**: Node.js `execSync` timing, 5 runs, median `runtime_ms`.

**Ideas to try (in priority order)**:
1. Profile with `--prof` or `clinic.js` to find hotspot
2. Replace synchronous I/O with async (if bottleneck is I/O)
3. Cache parsed results to disk (avoid re-parsing on each run)
4. Use streams instead of reading entire files into memory
5. Replace slow regex with simpler string ops
6. Reduce `require`/`import` overhead (lazy-load heavy modules)
7. Use faster JSON parser (`fast-json-parse`, `simdjson`)
8. Reduce allocations in hot loops (object pooling, Buffer reuse)
9. Use native Node addons for CPU-intensive work
10. Parallelize with `worker_threads`

---

### API / server latency

**Benchmark**: `autocannon` or fetch loop, 5-10s, p50 `latency_ms`.

```js
// package.json dep: "autocannon": "^7.0.0"
import autocannon from 'autocannon';
const result = await autocannon({ url: 'http://localhost:{PORT}/{endpoint}', duration: 5, connections: 10 });
console.log(`p50_ms: ${result.latency.p50.toFixed(1)}`);
console.log(`all_runs: [p50=${result.latency.p50.toFixed(1)}, p99=${result.latency.p99.toFixed(1)}]`);
```

**Ideas to try (in priority order)**:
1. Add response caching (in-memory LRU, Redis)
2. Add database query result caching
3. Use database indexes on filtered/sorted columns
4. Replace N+1 queries with bulk queries / JOIN
5. Enable HTTP keep-alive / connection pooling
6. Add gzip/brotli response compression
7. Reduce JSON serialization cost (avoid serializing unused fields)
8. Use streaming responses for large payloads
9. Move heavy computation off the request path (background job)
10. Add ETags / conditional GET for cacheable resources

---

### Build system

**Benchmark**: Shell timing of build command, 3 runs, median `build_time_ms`.

**Ideas to try (in priority order)**:
1. Enable persistent caching (`cache: { type: 'filesystem' }` in webpack)
2. Use `swc` or `esbuild` instead of Babel for transpilation
3. Enable parallel workers (`thread-loader`, `HappyPack`)
4. Reduce entry points / split config
5. Exclude `node_modules` from unnecessary transforms
6. Use `resolve.alias` to skip redundant lookups
7. Minimize what's watched in watch mode
8. Profile build with `speed-measure-webpack-plugin`
9. Remove source maps in production
10. Tree-shake aggressively

---

## Notes for the executing agent

- **Always read `program.md` first** before starting the loop. It has the final word on constraints.
- **Never modify `benchmark.{ext}`** under any circumstances.
- **Be atomic**: one idea per commit. This makes reverts clean and the log readable.
- **Compound wins**: after establishing a strong baseline via several keeps, try combining multiple past near-misses.
- **When in doubt, keep it simple**: complexity is a cost. A 1% gain that adds 30 lines of unmaintainable code is usually not worth it.
- **The metric is the metric**: don't argue with it. If the benchmark says it regressed, revert — even if you think it should be faster.
