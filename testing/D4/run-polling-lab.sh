#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
umask 077
root="$(cd "$(dirname "$0")/../.." && pwd)"
run_dir="$root/work/d4/d4-polling-$(date -u +%Y%m%dT%H%M%S)-$$"
mkdir -p "$run_dir"
python3 "$root/testing/D4/generate-continuation-admission.py" --check
printf 'D4 polling campaign: %s\n' "$run_dir"
bash "$root/testing/D4/build-lab.sh" "$run_dir"
docker version --format '{{.Server.Version}}' > "$run_dir/docker-version.txt"
docker compose version --short > "$run_dir/compose-version.txt"
docker image inspect postgres@sha256:0ea6700a3b4f0ae6ce746519073558aed4d88a79d8d07622a9a644946c7319c4 --format '{{json .Id}} {{json .RepoDigests}}' >> "$run_dir/images.txt"
# Two bounded independent groups; every case still owns a distinct Compose project.
# The final aggregate is reconstructed from immutable per-case reports after both exit.
python3 "$root/testing/D4/lab-scenarios.py" "$run_dir" --scenarios S01 S02 S03 S04 S05 > "$run_dir/regression.log" 2>&1 &
regression_pid=$!
python3 "$root/testing/D4/lab-scenarios.py" "$run_dir" --scenarios S06 S07 S08 S09 S10 S11 S12 > "$run_dir/long-running.log" 2>&1 &
long_running_pid=$!
campaign_failed=0
wait "$regression_pid" || campaign_failed=1
wait "$long_running_pid" || campaign_failed=1
python3 - "$run_dir" <<'PY'
import json,sys
from pathlib import Path
run=Path(sys.argv[1]);results=[]
for i in range(1,13):
 p=run/('S%02d'%i)/'result.json'
 if p.exists():results.append(json.loads(p.read_text()))
(run/'scenario-results.json').write_text(json.dumps(results,indent=2)+'\n')
if len(results)!=12 or any(r['status']!='PASS' for r in results):raise SystemExit(1)
PY
if [[ "$campaign_failed" != 0 ]];then exit 1;fi
printf '%s\n' "$run_dir" > "$root/work/d4/latest-polling-lab-success.txt"
printf 'D4 polling campaign passed; D4 remains OPEN. Evidence: %s\n' "$run_dir"
