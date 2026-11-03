#!/usr/bin/env bash
# Rebuild all three roadside store prototypes from scratch and render their inspection sets.
# Requires a Python 3.11 environment with: bpy==4.5.15 pillow numpy arabic-reshaper python-bidi
#   python3.11 -m venv venv && venv/bin/pip install bpy==4.5.15 pillow numpy arabic-reshaper python-bidi
# Usage: PY=venv/bin/python ./run_all.sh        (NO_RENDER=1 skips the Cycles renders)
set -euo pipefail
cd "$(dirname "$0")"
PY="${PY:-python}"
for spec in "enoc build_enoc.py enoc_service_station" \
            "starbucks build_starbucks.py starbucks_drive_thru" \
            "zoom build_zoom.py zoom_convenience_store"; do
  set -- $spec
  dir="../$1"
  rm -rf "$dir/source/textures" "$dir/renders"
  mkdir -p "$dir/source"
  "$PY" "$2" > "$dir/source/build_log.txt" 2>&1
  grep -E "^STATS|^EXPORT" "$dir/source/build_log.txt" | cut -c1-200
  if [ "${NO_RENDER:-0}" != "1" ]; then
    "$PY" render_previews.py "$dir" "$3" > "$dir/source/render_log.txt" 2>&1
    grep -E "^RENDERED|^TRIS" "$dir/source/render_log.txt"
  fi
done
"$PY" measure.py
