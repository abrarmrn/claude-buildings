#!/usr/bin/env bash
# Usage: ./run_batch.sh <folder>:<base> ...   -> rebuild, validate, render (sequential). Logs in <folder>/renders/.
cd "$(dirname "$0")"
PY="${PY:-/home/user/bpyenv/bin/python}"
for item in "$@"; do
  f="${item%%:*}"; b="${item##*:}"
  n=$(echo "$f" | cut -c1-2)
  script=$(ls build_${n}_*.py)
  $PY $script > ../$f/lod/build_log.txt 2>&1; grep BUILD_OK ../$f/lod/build_log.txt || { echo "BUILD_FAIL $f"; continue; }
  $PY validate_asset.py ../$f $b 2>&1 | grep VALIDATION
  rm -f ../$f/renders/*_lowres.jpg ../$f/renders/render_report.json
  $PY render_asset.py ../$f $b > ../$f/renders/render_log.txt 2>&1
  echo "RENDER_DONE $f $(grep -c '^RENDERED' ../$f/renders/render_log.txt)/4"
done
