#!/usr/bin/env bash
set -euo pipefail
# Dedicated PostgreSQL and Java 21 containers; no published host ports.
project_root="$(cd "$(dirname "$0")/../.." && pwd)"
docker info > /dev/null
audit_id="d2-$(date +%Y%m%d%H%M%S)-$$"
audit_work="$project_root/work/docker-audit/$audit_id"
pg_image="${AUDIT_PG_IMAGE:-postgres:16-bookworm}"
maven_image="${AUDIT_MAVEN_IMAGE:-maven:3.9-eclipse-temurin-21}"
pg_container="$audit_id-pg"
test_container="$audit_id-tests"
mkdir -p "$audit_work/m2" "$audit_work/evidence"
cleanup() {
 docker logs "$pg_container" > "$audit_work/postgres.log" 2>&1 || true
 docker rm -f "$test_container" "$pg_container" > "$audit_work/cleanup.log" 2>&1 || true
 docker network rm "$audit_id" >> "$audit_work/cleanup.log" 2>&1 || true
}
trap cleanup EXIT
docker pull "$pg_image"
docker pull "$maven_image"
docker image inspect "$pg_image" "$maven_image" > "$audit_work/images.json"
docker version > "$audit_work/docker-version.txt"
docker network create --label codex.project=weekly-ai-work-planner "$audit_id" > "$audit_work/network-id.txt"
docker run -d --name "$pg_container" --network "$audit_id" --network-alias audit-db \
 --label codex.project=weekly-ai-work-planner --tmpfs /var/lib/postgresql/data \
 -e POSTGRES_USER=d2_auditor -e POSTGRES_HOST_AUTH_METHOD=trust "$pg_image" \
 > "$audit_work/container-id.txt"
pg_ready=false
for attempt in {1..30}; do
 if docker exec "$pg_container" pg_isready -U d2_auditor -d postgres > /dev/null 2>&1; then
  pg_ready=true; break
 fi
 sleep 1
done
if [[ "$pg_ready" != true ]]; then echo 'PostgreSQL container did not become ready' >&2; exit 1; fi
for db in d2_baseline d2_proposed d2_hardened d2_upgrade d2_contract; do
 docker exec "$pg_container" psql -X -U d2_auditor -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE $db"
done
docker exec "$pg_container" psql -X -U d2_auditor -d postgres -At -c 'SELECT version()' > "$audit_work/postgresql-version.txt"
docker run --name "$test_container" --network "$audit_id" \
 --label codex.project=weekly-ai-work-planner --user "$(id -u):$(id -g)" \
 -e MAVEN_CONFIG=/tmp/maven -e HOME=/tmp \
 --mount "type=bind,src=$project_root,dst=/project" \
 --workdir /project/testing/D2 "$maven_image" \
 mvn -B -ntp "-Dmaven.repo.local=/project/work/docker-audit/$audit_id/m2" \
 "-Daudit.reports=/project/work/docker-audit/$audit_id/evidence" -Daudit.url=jdbc:postgresql://audit-db:5432/ test 2>&1 | tee "$audit_work/maven-audit.log"
printf 'Docker audit evidence: %s\n' "$audit_work"
