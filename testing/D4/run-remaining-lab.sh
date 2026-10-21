#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
umask 077
root="$(cd "$(dirname "$0")/../.." && pwd)"
run_dir="$root/work/d4/d4-remaining-$(date -u +%Y%m%dT%H%M%S)-$$"
mkdir -p "$run_dir"
for generator in generate-continuation-admission.py generate-v25-boundaries.py generate-recovery-admission.py generate-absence-admission.py generate-review-admission.py generate-presence-admission.py;do python3 "$root/testing/D4/$generator" --check;done
printf 'D4 A23/A24 campaign: %s\n' "$run_dir"
bash "$root/testing/D4/build-lab.sh" "$run_dir"
docker version --format '{{.Server.Version}}' > "$run_dir/docker-version.txt"
docker compose version --short > "$run_dir/compose-version.txt"
python3 "$root/testing/D4/lab-scenarios.py" "$run_dir" --scenarios S26 S27 S28 S29 S24 S15 S06 S02 S20
printf '%s\n' "$run_dir" > "$root/work/d4/latest-remaining-lab-success.txt"
printf 'A23/A24 bounded campaign passed; D4 remains OPEN. Evidence: %s\n' "$run_dir"
