#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
umask 077
root="$(cd "$(dirname "$0")/../.." && pwd)"
run_dir="$root/work/d4/d4-latest-$(date -u +%Y%m%dT%H%M%S)-$$"
mkdir -p "$run_dir"
for generator in generate-continuation-admission.py generate-v25-boundaries.py generate-recovery-admission.py generate-absence-admission.py generate-review-admission.py generate-presence-admission.py;do python3 "$root/testing/D4/$generator" --check;done
printf 'D4 full V30 matrix: %s\n' "$run_dir"
bash "$root/testing/D4/build-lab.sh" "$run_dir"
docker version --format '{{.Server.Version}}' > "$run_dir/docker-version.txt"
docker compose version --short > "$run_dir/compose-version.txt"
python3 - "$root" "$run_dir" <<'PY'
import concurrent.futures,json,shutil,subprocess,sys
from pathlib import Path
root,run=map(Path,sys.argv[1:]);groups=[list(range(1,16)),list(range(16,31))]
def execute(index,numbers):
 group=run/('group-'+str(index));group.mkdir();shutil.copyfile(run/'image-tag.txt',group/'image-tag.txt');scenarios=['S'+str(n).zfill(2) for n in numbers]
 with (group/'campaign.log').open('w') as out:r=subprocess.run(['python3',str(run/'source/testing/D4/lab-scenarios.py'),str(group),'--keep-going','--scenarios',*scenarios],stdout=out,stderr=subprocess.STDOUT)
 print('group',index,'exit',r.returncode,flush=True);return group,r.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda item:execute(*item),enumerate(groups,1)))
rows=[row for group,code in results for row in json.loads((group/'scenario-results.json').read_text())]
(run/'scenario-results.json').write_text(json.dumps(rows,indent=2)+'\n')
assert not any(code for group,code in results),'Campaign group failed; inspect separate logs'
assert len(rows)==30 and all(row['status']=='PASS' and not any(row['cleanup_remaining'].values()) for row in rows)
print('All 30 current-target scenarios passed:',sum(len(row['checks']) for row in rows),'checks',flush=True)
PY
printf '%s\n' "$run_dir" > "$root/work/d4/latest-full-matrix-success.txt"
printf 'Full bounded V30 matrix passed; D4 remains OPEN. Evidence: %s\n' "$run_dir"
