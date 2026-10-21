#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
umask 077
root="$(cd "$(dirname "$0")/.." && pwd)"
run_dir="${1:?absolute development build directory required}"
mkdir -p "$run_dir" "$root/run_data/cache/m2"
java_image="maven@sha256:99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320"
python3 - "$root" "$run_dir" <<'PY'
import hashlib,json,shutil,sys
from pathlib import Path
root,run=map(Path,sys.argv[1:]);snapshot=run/'source';snapshot.mkdir()
names=['migrations','migrations-proposed','migrations-d3-proposed','migrations-d3-dispatch-proposed','migrations-d3-coordinator-proposed','migrations-d3-review-proposed','migrations-d4-proposed','scheduler-core','scheduler-postgres','worker-control-plane','worker-runtime','testing/D4']
for name in names:shutil.copytree(root/name,snapshot/name,ignore=shutil.ignore_patterns('target','__pycache__'))
(snapshot/'pom.xml').write_text((root/'pom.xml').read_text().replace('</modules>','<module>worker-control-plane</module><module>worker-runtime</module><module>testing/D4/lab</module></modules>'))
files=[root/'pom.xml']+[p for name in names for p in (root/name).rglob('*') if p.is_file() and not {'target','__pycache__'}&set(p.parts)]
(run/'inputs.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},indent=2)+'\n')
PY
timeout 600 docker run --rm --pull never --network bridge --user "$(id -u):$(id -g)" -e HOME=/tmp -e MAVEN_CONFIG=/tmp/maven \
 --mount "type=bind,src=$run_dir/source,dst=/project" --mount "type=bind,src=$root/run_data/cache/m2,dst=/maven-cache" -w /project "$java_image" \
 mvn -B -ntp -Dmaven.repo.local=/maven-cache -DskipTests package > "$run_dir/build.log" 2>&1
python3 - "$run_dir" <<'PY'
import os,shutil,sys,zipfile
from pathlib import Path
run=Path(sys.argv[1]);ctx=run/'image';ctx.mkdir()
with zipfile.ZipFile(run/'source/testing/D4/lab/target/d4-lab-0.1.0-SNAPSHOT-exec.jar') as jar:
 for name in jar.namelist():
  if name.endswith('/'):continue
  for prefix,target in [('BOOT-INF/classes/','classes'),('BOOT-INF/lib/','lib')]:
   if name.startswith(prefix):
    p=ctx/target/name[len(prefix):];p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(jar.read(name))
for p in (run/'source').glob('migrations*'):shutil.copytree(p,ctx/'sql'/p.name)
shutil.copyfile(run/'source/testing/D4/images/Dockerfile',ctx/'Dockerfile')
for p in ctx.rglob('*'):os.chmod(p,0o755 if p.is_dir() else 0o644)
os.chmod(ctx,0o755)
PY
image="wap-dev:$(basename "$run_dir" | tr '[:upper:]' '[:lower:]')"
docker build --network none --pull=false --build-arg "JAVA_IMAGE=$java_image" --build-arg "LAB_UID=$(id -u)" --build-arg "LAB_GID=$(id -g)" -t "$image" "$run_dir/image" > "$run_dir/image-build.log" 2>&1
printf '%s\n' "$image" > "$run_dir/image-tag.txt"
docker image inspect "$image" "$java_image" --format '{{json .Id}} {{json .RepoDigests}}' > "$run_dir/images.txt"
