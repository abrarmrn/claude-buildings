#!/usr/bin/env bash
# Usage: ./run_batch.sh <folder>:<base> ...   -> (re)build if needed, validate, render (sequential). Logs in <folder>/renders/.
# The build is skipped when <base>.blend is newer than its build script and the shared kit files.
cd "$(dirname "$0")"
PY="${PY:-/home/user/bpyenv/bin/python}"
for item in "$@"; do
  f="${item%%:*}"; b="${item##*:}"
  n=$(echo "$f" | cut -c1-2)
  script=$(ls build_${n}_*.py)
  blend="../$f/$b.blend"
  if [ ! -f "$blend" ] || [ -n "$(find $script pk_*.py -newer "$blend" 2>/dev/null)" ] || ! grep -q BUILD_OK ../$f/lod/build_log.txt 2>/dev/null; then
    $PY $script > ../$f/lod/build_log.txt 2>&1
  fi
  grep BUILD_OK ../$f/lod/build_log.txt || { echo "BUILD_FAIL $f"; continue; }
  $PY validate_asset.py ../$f $b 2>&1 | grep VALIDATION
  rm -f ../$f/renders/*_lowres.jpg ../$f/renders/render_report.json
  $PY render_asset.py ../$f $b > ../$f/renders/render_log.txt 2>&1
  echo "RENDER_DONE $f $(grep -c '^RENDERED' ../$f/renders/render_log.txt)/4"
done
