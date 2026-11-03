#!/usr/bin/env bash
# Sequential render worker. Queue file lines: <folder>:<basename>. Appending new lines while it runs is fine.
# Usage: QDIR=/path/to/state PY=python ./render_worker.sh      (create $QDIR/render_stop to finish when the queue is empty)
cd "$(dirname "$0")"
PY="${PY:-python}"; QDIR="${QDIR:-.}"
Q="$QDIR/render_queue.txt"; D="$QDIR/render_done.txt"; touch "$Q" "$D"
while pgrep -f "render_store.py" > /dev/null; do sleep 5; done      # let any manual render finish first
while true; do
  next=$(grep -vxFf "$D" "$Q" | head -1)
  if [ -z "$next" ]; then
    [ -f "$QDIR/render_stop" ] && break
    sleep 8; continue
  fi
  f="${next%%:*}"; b="${next##*:}"
  mkdir -p "../$f/renders"
  "$PY" render_store.py "../$f" "$b" > "../$f/renders/render_log.txt" 2>&1
  echo "$next" >> "$D"
  echo "WORKER_DONE $next $(grep -c RENDERED ../$f/renders/render_log.txt)/4"
done
