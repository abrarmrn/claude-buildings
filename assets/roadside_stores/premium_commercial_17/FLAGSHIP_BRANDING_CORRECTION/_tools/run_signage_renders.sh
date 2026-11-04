#!/bin/bash
# Renders all targeted signage views (after) + the before view from the pre-correction .blend files.
# ORIG_DIR must hold <NN_folder>/<base>.blend copies of the pre-correction files (e.g. from git history).
cd "$(dirname "$0")"
ORIG_DIR=${ORIG_DIR:?set ORIG_DIR}
OUT=../renders
mkdir -p $OUT
declare -A F=([01]=01_mercedes_showroom/mercedes_showroom [02]=02_bmw_showroom/bmw_showroom [03]=03_porsche_showroom/porsche_showroom [04]=04_ford_showroom/ford_showroom [05]=05_samsung_flagship/samsung_flagship [06]=06_apple_flagship/apple_flagship [07]=07_xiaomi_flagship/xiaomi_flagship)
for n in 01 02 03 04 05 06 07; do
  for v in front_day front_night road; do python3.11 render_signage.py $n $v 2>&1 | grep -E "RENDERED|Error"; done
  python3.11 render_signage.py $n front_day --blend $ORIG_DIR/${F[$n]}.blend --out $OUT/${n}_before_front_day.jpg 2>&1 | grep -E "RENDERED|Error"
  [ $n == 03 ] && python3.11 render_signage.py 03 detail_day 2>&1 | grep -E "RENDERED|Error"
done
echo ALLDONE
