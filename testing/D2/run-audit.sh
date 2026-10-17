#!/usr/bin/env bash
set -euo pipefail
# Run only against a new disposable cluster; no existing database is used.
# Requirements: Java 21+, Maven, PostgreSQL 16+ server binaries and pgcrypto.
project_root="$(cd "$(dirname "$0")/../.." && pwd)"
audit_work="$project_root/work/d2-runtime"
pg_bin="${PG_BIN:-/usr/lib/postgresql/18/bin}"
maven_bin="${MAVEN_BIN:-mvn}"
audit_port="${AUDIT_PORT:-55439}"
mkdir -p "$audit_work"
audit_run="$(mktemp -d "$audit_work/run-XXXXXX")"
mkdir "$audit_run/socket"
"$pg_bin/initdb" -D "$audit_run/data" -U d2_auditor -A trust --no-locale --encoding=UTF8 > "$audit_run/initdb.log"
cleanup() { "$pg_bin/pg_ctl" -D "$audit_run/data" -m fast stop > "$audit_run/stop.log" 2>&1 || true; }
trap cleanup EXIT
"$pg_bin/pg_ctl" -D "$audit_run/data" -l "$audit_run/postgres.log" -o "-h 127.0.0.1 -p $audit_port -k $audit_run/socket" start
for db in d2_baseline d2_proposed d2_hardened d2_upgrade d2_contract; do
 psql -X -h 127.0.0.1 -p "$audit_port" -U d2_auditor -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE $db"
done
cd "$project_root/testing/D2"
"$maven_bin" -B -ntp "-Dmaven.repo.local=${AUDIT_M2:-$project_root/work/m2}" "-Daudit.url=jdbc:postgresql://127.0.0.1:$audit_port/" test 2>&1 | tee "$audit_run/maven-audit.log"
printf 'Evidence directory: %s\n' "$audit_run"
