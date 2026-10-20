#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
umask 077
root="$(cd "$(dirname "$0")/../.." && pwd)"
run_dir="$root/work/d4/d4-multicount-$(date -u +%Y%m%dT%H%M%S)-$$"
mkdir -p "$run_dir"
python3 "$root/testing/D4/generate-continuation-admission.py" --check
printf 'D4 multicount campaign: %s\n' "$run_dir"
bash "$root/testing/D4/build-lab.sh" "$run_dir"
docker version --format '{{.Server.Version}}' > "$run_dir/docker-version.txt"
docker compose version --short > "$run_dir/compose-version.txt"
docker image inspect postgres@sha256:0ea6700a3b4f0ae6ce746519073558aed4d88a79d8d07622a9a644946c7319c4 --format '{{json .Id}} {{json .RepoDigests}}' >> "$run_dir/images.txt"
python3 "$root/testing/D4/lab-scenarios.py" "$run_dir" --scenarios S14 S05 S13
printf '%s\n' "$run_dir" > "$root/work/d4/latest-multicount-lab-success.txt"
printf 'D4 multicount campaign passed; D4 remains OPEN. Evidence: %s\n' "$run_dir"
