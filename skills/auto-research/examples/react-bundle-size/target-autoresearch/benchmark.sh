#!/usr/bin/env bash
# FIXED HARNESS — DO NOT MODIFY
set -euo pipefail

TARGET_DIR="$(cd "$(dirname "$0")/../target" && pwd)"
OUT_DIR="/tmp/target-dist"

# Build to writable /tmp to avoid mounted FS permission issues
cd "$TARGET_DIR"
rm -rf "$OUT_DIR"
npx vite build --outDir "$OUT_DIR" --emptyOutDir 2>/dev/null

# Sanity check: index.html must exist
if [ ! -f "$OUT_DIR/index.html" ]; then
  echo "Sanity check failed: dist/index.html not found" >&2
  exit 1
fi

# Measure total JS + CSS bundle size in KB (uncompressed)
TOTAL_BYTES=$(find "$OUT_DIR/assets" \( -name "*.js" -o -name "*.css" \) | xargs wc -c | awk '/total/{print $1; found=1} !found && /^[[:space:]]*[0-9]+ [^t]/{last=$1} END{if(!found) print last}')
BUNDLE_KB=$(echo "scale=1; $TOTAL_BYTES / 1024" | bc)

echo "bundle_kb: $BUNDLE_KB"
echo "all_runs: [$BUNDLE_KB]"
