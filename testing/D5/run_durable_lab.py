# SPDX-License-Identifier: GPL-3.0-only
"""I33 bounded durable campaign; test IDs, resources and inputs remain explicit."""
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import time
import unittest

from source_ingest.durable_task_fixture import DurableLab
from source_ingest.incremental_fixture import TemporaryFixtureLab
from testing.D5.run_incremental_lab import Recorded
from testing.D5 import durable_support as support


def applicability(inputs):
    return 'CURRENT' if all(Path(p).is_file() and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in inputs.items()) else 'STALE_INPUTS'


def distinct_groups(ids):
    groups={}
    for value in sorted(set(ids)):
        name=value.split('.')[0]
        groups.setdefault(name,[]).append(value)
    return groups


def coverage():
    return {f'DF{i:02}':[f'test_durable_integration.DurableIntegrationTest.test_DF{i:02}'] for i in range(1,49)}


def inputs():
    paths=list(Path('source_ingest').glob('*.py'))+list(Path('testing/D5').glob('*.py'))+list(Path('testing/D5/fixtures').glob('*.md'))
    paths+=list(Path('docs/design').glob('D5-I33-*.md'))
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def main():
    DurableLab.created_roots.clear();TemporaryFixtureLab.created_roots.clear();support.CHILDREN.clear();support.CRASHES.clear();support.ORACLES.clear();support.ORACLE_KEYS.clear()
    start=time.monotonic()
    suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent),pattern='test*.py')
    result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=Recorded).run(suite)
    groups=distinct_groups(result.passed)
    owned=set(DurableLab.created_roots)
    remaining=sum(Path(p).exists() or Path(p).is_symlink() for p in owned)
    regression_roots=set(TemporaryFixtureLab.created_roots)-owned
    previous=sys.modules.get('test_incremental_capture');previous_children=previous.CHILDREN if previous else []
    threads=[]
    for name in ('test_plane_reconciliation','test_relational_batch','test_profiles_quotas'):
        module=sys.modules.get(name)
        if module:threads.extend(module.THREADS)
    cleanup=(not remaining and not any(Path(p).exists() for p in regression_roots) and
             not any(p.is_alive() for p in support.CHILDREN+previous_children) and not any(t.is_alive() for t in threads))
    data=dict(schema='d5.i34-durable-task-campaign.v1',mode='SYNTHETIC_ONLY',
        status='PASS' if result.wasSuccessful() and cleanup else 'FAIL',python=platform.python_version(),platform=platform.system(),
        tests_run=result.testsRun,groups=groups,passed=sorted(set(result.passed)),
        failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],skipped=[t.id() for t,_ in result.skipped],
        new_tests=len(groups.get('test_durable_integration',[])),regression_tests=sum(len(v) for k,v in groups.items() if k!='test_durable_integration'),
        case_test_map=coverage(),owned_roots_created=len(owned),owned_roots_remaining=remaining,
        owned_children_started=len(support.CHILDREN),owned_children_alive=sum(p.is_alive() for p in support.CHILDREN),
        owned_child_exitcodes=[p.exitcode for p in support.CHILDREN],crash_exercises=support.CRASHES,independent_oracle_observations=support.ORACLES,
        regression_roots_created=len(regression_roots),regression_roots_remaining=sum(Path(p).exists() for p in regression_roots),
        regression_children_started=len(previous_children),regression_children_alive=sum(p.is_alive() for p in previous_children),
        regression_child_exitcodes=[p.exitcode for p in previous_children],regression_threads_started=len(threads),regression_threads_alive=sum(t.is_alive() for t in threads),
        cleanup_verified=cleanup,elapsed_seconds=round(time.monotonic()-start,3),inputs=inputs(),
        remote_requests=0,persistent_D2_writes=0,quota_consumed=0,reservations_created=0,operational_activation=False,
        D5_closed=False,global_gaps_open=[f'G{i:02}' for i in range(1,8)],real_evidence_criteria_not_run=7,
        relational_path_not_run=True,docs_export_not_run=True,SQL_D2_D3_D4_reexecuted=False,
        limits_campaign='Reduced limits for history/count/headroom branches; source >2 MiB full rejection; not capacity/performance benchmark')
    print(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2))
    return 0 if data['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
