import { execSync } from 'child_process';
import { performance } from 'perf_hooks';
import { existsSync, readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const TARGET_DIR = resolve(__dirname, '../target');
const CMD = `node ${TARGET_DIR}/index.js ${TARGET_DIR}/docs ${TARGET_DIR}/output.json`;
const RUNS = 5;

// ── Sanity check ────────────────────────────────────────────────────────────
try {
  execSync(CMD, { stdio: 'pipe' });
} catch (e) {
  console.error('Sanity check failed (script crashed):');
  console.error(e.stderr?.toString() ?? e.message);
  process.exit(1);
}

const out = JSON.parse(readFileSync(`${TARGET_DIR}/output.json`, 'utf8'));
if (!out || out.total !== 200) {
  console.error(`Sanity check failed: expected total=200, got total=${out?.total}`);
  process.exit(1);
}

// ── Timed runs ───────────────────────────────────────────────────────────────
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
