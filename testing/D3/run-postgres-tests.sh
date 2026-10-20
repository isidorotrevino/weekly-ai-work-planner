#!/usr/bin/env bash
set -euo pipefail
# Disposable PostgreSQL network, no published ports, no production databases.
project_root="$(cd "$(dirname "$0")/../.." && pwd)"
audit_id="d3-i2-$(date +%Y%m%d%H%M%S)-$$"
audit_work="$project_root/work/d3-postgres/$audit_id"
cache_dir="${D3_MAVEN_CACHE:-$project_root/work/d3-core/m2}"
pg_image="${D3_PG_IMAGE:-postgres:16-bookworm}"
maven_image="${D3_MAVEN_IMAGE:-maven:3.9-eclipse-temurin-21}"
pg_container="$audit_id-pg"; test_container="$audit_id-tests"
mkdir -p "$audit_work" "$cache_dir"
cache_dir="$(cd "$cache_dir" && pwd)"
cleanup() {
  docker logs "$pg_container" > "$audit_work/postgres.log" 2>&1 || true
  docker rm -f "$test_container" "$pg_container" > "$audit_work/cleanup.log" 2>&1 || true
  docker network rm "$audit_id" >> "$audit_work/cleanup.log" 2>&1 || true
}
trap cleanup EXIT
# Offline mode is used with pre-existing images/cache. Online mode permits dependencies only.
run_args=(); maven_args=(-B -ntp)
if [[ "${D3_OFFLINE:-0}" == 1 ]]; then run_args+=(--pull never);maven_args+=(-o);fi
network_args=(--label codex.project=weekly-ai-work-planner)
if [[ "${D3_OFFLINE:-0}" == 1 ]];then network_args+=(--internal);fi
docker network create "${network_args[@]}" "$audit_id" > "$audit_work/network.txt"
docker run "${run_args[@]}" -d --name "$pg_container" --network "$audit_id" --network-alias d3-db \
  --label codex.project=weekly-ai-work-planner --tmpfs /var/lib/postgresql/data \
  -e POSTGRES_USER=d2_auditor -e POSTGRES_HOST_AUTH_METHOD=trust "$pg_image" > "$audit_work/postgres-container.txt"
ready=false
for attempt in {1..30}; do
  if docker exec "$pg_container" pg_isready -U d2_auditor -d postgres > /dev/null 2>&1;then ready=true;break;fi
  sleep 1
done
if [[ "$ready" != true ]];then echo 'Disposable PostgreSQL did not become ready' >&2;exit 1;fi
for db in d3_template d2_baseline d2_proposed d2_hardened d2_upgrade d2_contract d2_semver_upgrade;do
  docker exec "$pg_container" psql -X -U d2_auditor -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE $db" > /dev/null
done
docker exec "$pg_container" psql -X -U d2_auditor -d postgres -At -c 'SHOW server_version' > "$audit_work/postgresql-version.txt"
rm -rf "$project_root/scheduler-core/target" "$project_root/scheduler-postgres/target" "$project_root/testing/D2/target"
# Reuse one container for the isolated D3 suite and unchanged D2 regression.
docker run "${run_args[@]}" --name "$test_container" --network "$audit_id" --user "$(id -u):$(id -g)" \
  -e MAVEN_CONFIG=/tmp/maven -e HOME=/tmp \
  --mount "type=bind,src=$project_root,dst=/project" --mount "type=bind,src=$cache_dir,dst=/maven-cache" \
  --workdir /project "$maven_image" mvn "${maven_args[@]}" -Dmaven.repo.local=/maven-cache \
  -Dplanner.root=/project -Dd3.url=jdbc:postgresql://d3-db:5432/ test 2>&1 | tee "$audit_work/d3-tests.log"
docker rm "$test_container" > /dev/null
docker run "${run_args[@]}" --name "$test_container" --network "$audit_id" --user "$(id -u):$(id -g)" \
  -e MAVEN_CONFIG=/tmp/maven -e HOME=/tmp \
  --mount "type=bind,src=$project_root,dst=/project" --mount "type=bind,src=$cache_dir,dst=/maven-cache" \
  --workdir /project/testing/D2 "$maven_image" mvn "${maven_args[@]}" -Dmaven.repo.local=/maven-cache \
  -Daudit.url=jdbc:postgresql://d3-db:5432/ test 2>&1 | tee "$audit_work/d2-tests.log"
printf '%s\n' "$audit_id" > "$project_root/work/d3-postgres/latest-success.txt"
printf 'D3/D2 isolated audit evidence: %s\n' "$audit_work"
