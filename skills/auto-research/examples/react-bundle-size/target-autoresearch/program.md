# autoresearch — reduce production bundle size

Minimize the total uncompressed JS+CSS bundle size (in KB) of the React/Vite app in `../target/`. The agent edits source files and Vite config; the benchmark builds and measures `dist/assets/*.{js,css}`.

## Project structure

```
target-autoresearch/
├── benchmark.sh    ← fixed harness (never modify)
├── program.md      ← agent instructions
├── results.tsv     ← experiment log (untracked)
└── .gitignore

target/
├── package.json
├── vite.config.js
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── index.css
│   └── components/
│       ├── Charts.jsx
│       ├── Dashboard.jsx
│       ├── Header.jsx
│       └── DataTable.jsx
```

## Setup

1. Branch: `autoresearch/jun26`
2. Install deps: `npm install` from `../target/`
3. Verify: `npm run build` completes with no errors
4. Initialize results.tsv with just the header row

## Experimentation

Run benchmark from `target-autoresearch/`:
```bash
bash benchmark.sh > run.log 2>&1
grep "^bundle_kb:" run.log
```

**What you CAN do:**
- Edit any file in `src/` (App.jsx, components/*.jsx, index.css, main.jsx)
- Edit `package.json` (add/remove/replace dependencies)
- Edit `vite.config.js` (enable chunking, tree-shaking, minification)
- Run `npm install` / `npm remove` after changing package.json
- Replace heavy deps with lighter alternatives or native browser APIs

**What you CANNOT do:**
- Modify `benchmark.sh` — it is the fixed ground truth
- Break the app's visual output (Dashboard, Charts, DataTable must render)
- Remove the core React/Vite setup

**The goal: minimize `bundle_kb`.** Lower = less total JS+CSS delivered to users.

**Functional correctness** is a hard constraint. The build must succeed and index.html must exist.

**Simplicity criterion**: Prefer removing code over adding it. Native JS over library imports.

## Output format

```
bundle_kb: 542.3
all_runs: [542.3]
```

## Logging results

Tab-separated, NOT comma-separated:
```
commit	bundle_kb	notes	status	description
```

Status: `keep`, `discard`, or `crash`.

## Ideas to try (prioritized)

1. Replace `moment` with native `Intl.DateTimeFormat` / `Date.toLocaleDateString()` everywhere (~300KB saving)
2. Replace `lodash` full import with lodash-es named imports (tree-shakeable), or replace with native JS array methods
3. Remove `axios` entirely, delete all imports (it's not actually used for HTTP calls, just imported)
4. Replace `uuid` with `crypto.randomUUID()` (built-in, zero bundle cost)
5. Remove unused `date-fns` from package.json (it's declared but never imported)
6. Enable Vite manual chunking to split react-chartjs-2 into a separate async chunk
7. Replace `lodash` entirely with native equivalents (_.sample → random array pick, _.random → Math.random, etc.)
8. Add `build.minify: 'esbuild'` and `build.cssMinify: true` to vite.config.js
9. Use `React.lazy()` + `Suspense` to lazy-load Charts component
10. Remove `classnames` package if unused
