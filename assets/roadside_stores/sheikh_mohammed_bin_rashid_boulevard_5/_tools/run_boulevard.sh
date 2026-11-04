#!/usr/bin/env bash
# Usage: ./run_boulevard.sh [NN ...]   -> build, validate (fresh process + GLB re-import), render 4 views (sequential).
# Uses the premium_commercial_17 validate_asset.py / render_asset.py READ-ONLY (they take the asset folder as argument).
cd "$(dirname "$0")"
PY="${PY:-python3.11}"
P17T=../../premium_commercial_17/_tools
NUMS="${@:-01 02 03 04 05}"
for n in $NUMS; do
  script=$(ls build_${n}_*.py)
  f=$(ls -d ../${n}_*/ 2>/dev/null | head -1); f=${f%/}
  [ -z "$f" ] && f=../$(basename $script .py | sed "s/^build_//")
  $PY $script > /tmp/bv_build_$n.log 2>&1
  f=$(ls -d ../${n}_*/ | head -1); f=${f%/}
  b=$(basename $script .py | sed "s/^build_${n}_//")
  cp /tmp/bv_build_$n.log $f/lod/build_log.txt
  grep BUILD_OK $f/lod/build_log.txt || { echo "BUILD_FAIL $n"; continue; }
  $PY $P17T/validate_asset.py $(realpath $f) $b 2>&1 | grep VALIDATION
  rm -f $f/renders/*_lowres.jpg $f/renders/render_report.json
  $PY $P17T/render_asset.py $(realpath $f) $b > /tmp/bv_render_$n.log 2>&1
  echo "RENDER_DONE $n $(grep -c '^RENDERED' /tmp/bv_render_$n.log)/4"
done
