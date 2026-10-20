#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
umask 077
root="$(cd "$(dirname "$0")/../.." && pwd)"
kind="${D4_RUN_KIND:-delivery}"
if [[ "$kind" != delivery && "$kind" != transport && "$kind" != process ]];then echo 'Invalid D4 run kind' >&2;exit 2;fi
run_id="d4-$kind-$(date -u +%Y%m%dT%H%M%S)-$$"
run_dir="$root/work/d4/$run_id"
cache="${D4_MAVEN_CACHE:-$root/work/d4/m2}"
pg_image="${D4_PG_IMAGE:-postgres:16-bookworm}"
maven_image="${D4_MAVEN_IMAGE:-maven:3.9-eclipse-temurin-21}"
pg="$run_id-db";tests="$run_id-tests"
mkdir -p "$run_dir" "$cache"
cache="$(cd "$cache" && pwd)"
cleanup() {
  docker logs "$pg" > "$run_dir/postgres.log" 2>&1 || true
  docker rm -f "$tests" "$pg" > "$run_dir/cleanup.log" 2>&1 || true
  docker network rm "$run_id" >> "$run_dir/cleanup.log" 2>&1 || true
}
trap cleanup EXIT
# Source snapshot avoids touching the historical modules' target/reports.
python3 - "$root" "$run_dir" <<'PY'
import hashlib,json,secrets,shutil,sys
from pathlib import Path
root,run=map(Path,sys.argv[1:])
snapshot=run/'source';snapshot.mkdir()
folders=['migrations','migrations-proposed','migrations-d3-proposed',
 'migrations-d3-dispatch-proposed','migrations-d3-coordinator-proposed',
 'migrations-d3-review-proposed','migrations-d4-proposed','scheduler-core','scheduler-postgres','worker-control-plane','worker-runtime','testing/D4']
for name in folders:
    shutil.copytree(root/name,snapshot/name,ignore=shutil.ignore_patterns('target','__pycache__'))
text=(root/'pom.xml').read_text().replace('</modules>','<module>worker-control-plane</module><module>worker-runtime</module><module>testing/D4/lab</module><module>testing/D4</module></modules>')
(snapshot/'pom.xml').write_text(text)
password=secrets.token_hex(24)
(run/'postgres.env').write_text('POSTGRES_USER=d4_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_HOST_AUTH_METHOD=scram-sha-256\n')
(run/'client.env').write_text('PGUSER=d4_owner\nPGPASSWORD='+password+'\n')
paths=[root/'pom.xml']+[p for n in folders for p in (root/n).rglob('*') if p.is_file() and not {'target','__pycache__'} & set(p.parts)]
(run/'inputs.json').write_text(json.dumps({p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)},indent=2)+'\n')
PY
docker version --format '{{.Server.Version}}' > "$run_dir/docker-version.txt"
docker image inspect "$pg_image" "$maven_image" --format '{{json .RepoTags}} {{json .Id}} {{json .RepoDigests}}' > "$run_dir/images.txt"
# Runtime is internal even during Maven bootstrap: Maven's build container is
# disconnected from this database network until an explicit offline test run.
docker network create --internal --label "codex.d4.run=$run_id" "$run_id" > "$run_dir/network.txt"
docker run --pull never -d --name "$pg" --network "$run_id" --network-alias d4-db \
  --label "codex.d4.run=$run_id" --tmpfs /var/lib/postgresql/data \
  --env-file "$run_dir/postgres.env" "$pg_image" > "$run_dir/postgres-container.txt"
ready=false
for attempt in {1..30};do
  if docker exec "$pg" pg_isready -U d4_owner -d postgres > /dev/null 2>&1;then ready=true;break;fi
  sleep 1
done
if [[ "$ready" != true ]];then echo 'D4 disposable PostgreSQL readiness failed' >&2;exit 1;fi
docker exec "$pg" psql -X -U d4_owner -d postgres -At -c 'SHOW server_version' > "$run_dir/postgresql-version.txt"
if [[ "${D4_OFFLINE:-0}" != 1 ]];then
  # Fetch/build only; no tests, SQL endpoint or credentials in bootstrap container.
  timeout 600 docker run --pull never --name "$tests" --label "codex.d4.run=$run_id" \
    --user "$(id -u):$(id -g)" -e HOME=/tmp -e MAVEN_CONFIG=/tmp/maven \
    --mount "type=bind,src=$run_dir/source,dst=/project" --mount "type=bind,src=$cache,dst=/maven-cache" \
    -w /project "$maven_image" mvn -B -ntp -Dmaven.repo.local=/maven-cache -DskipTests package \
    > "$run_dir/bootstrap.log" 2>&1
  docker rm "$tests" > /dev/null
fi
timeout 600 docker run --pull never --name "$tests" --network "$run_id" --label "codex.d4.run=$run_id" \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -e MAVEN_CONFIG=/tmp/maven --env-file "$run_dir/client.env" \
  --mount "type=bind,src=$run_dir/source,dst=/project" --mount "type=bind,src=$cache,dst=/maven-cache" \
  -w /project "$maven_image" mvn -o -B -ntp -Dmaven.repo.local=/maven-cache \
  -Dplanner.root=/project -Dd4.url=jdbc:postgresql://d4-db:5432/ \
  "-Dtest=${D4_TESTS:-DeliveryStoreTest}" -Dsurefire.failIfNoSpecifiedTests=false test > "$run_dir/tests.log" 2>&1
printf '%s\n' "$run_id" > "$root/work/d4/latest-$kind-success.txt"
printf 'D4 %s checks passed. Evidence: work/d4/%s\n' "$kind" "$run_id"
