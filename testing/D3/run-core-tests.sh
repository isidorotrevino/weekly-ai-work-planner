#!/usr/bin/env bash
set -euo pipefail
# Pure Java tests only. No PostgreSQL, workers, publication or provider calls.
project_root="$(cd "$(dirname "$0")/../.." && pwd)"
maven_bin="${MAVEN_BIN:-mvn}"
args=(-V -B -ntp -f "$project_root/scheduler-core/pom.xml")
if [[ -n "${D3_MAVEN_CACHE:-}" ]]; then args+=("-Dmaven.repo.local=$D3_MAVEN_CACHE"); fi
if [[ "${D3_OFFLINE:-0}" == 1 ]]; then args+=(-o); fi
# Only disposable output of this module; avoid stale test classes/reports.
rm -rf "$project_root/scheduler-core/target"
"$maven_bin" "${args[@]}" test
