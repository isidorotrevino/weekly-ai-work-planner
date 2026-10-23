# SPDX-License-Identifier: GPL-3.0-only
"""I36 R campaign, with T and earlier regressions/resources kept separate."""
import io
import json
from pathlib import Path
import platform
import sys
import time
import unittest
from source_ingest.durable_relational_fixture import RelationalLab
from source_ingest.durable_task_fixture import DurableLab
from source_ingest.incremental_fixture import TemporaryFixtureLab
from testing.D5.run_incremental_lab import Recorded
from testing.D5.run_durable_lab import distinct_groups,applicability
from testing.D5 import relational_support as support,durable_support as previous
import hashlib


def coverage():return {f'DR{i:02}':[f'test_durable_relational.DurableRelationalTest.test_DR{i:02}'] for i in range(1,41)}


def inputs():
    paths=list(Path('source_ingest').glob('*.py'))+list(Path('testing/D5').glob('*.py'))+list(Path('testing/D5/fixtures').glob('*.md'))
    paths+=list(Path('docs/design').glob('D5-I35-*.md'))
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def main():
    RelationalLab.created_roots.clear();DurableLab.created_roots.clear();TemporaryFixtureLab.created_roots.clear()
    for module in (support,previous):
        module.CHILDREN.clear();module.CRASHES.clear();module.ORACLES.clear();module.ORACLE_KEYS.clear()
    started=time.monotonic();suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent),pattern='test*.py')
    result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=Recorded).run(suite)
    groups=distinct_groups(result.passed);own=set(RelationalLab.created_roots);t_roots=set(DurableLab.created_roots)
    cap_roots=set(TemporaryFixtureLab.created_roots)-t_roots
    t_children=previous.CHILDREN;cap=sys.modules.get('test_incremental_capture');cap_children=cap.CHILDREN if cap else []
    threads=[]
    for name in ('test_plane_reconciliation','test_relational_batch','test_profiles_quotas'):
        m=sys.modules.get(name)
        if m:threads.extend(m.THREADS)
    alive=lambda ps:sum(p.is_alive() for p in ps)
    remains=lambda roots:sum(Path(p).exists() or Path(p).is_symlink() for p in roots)
    clean=not (remains(own|t_roots|cap_roots) or alive(support.CHILDREN+t_children+cap_children) or alive(threads))
    report=dict(schema='d5.i36-durable-relational-campaign.v1',mode='SYNTHETIC_ONLY',status='PASS' if result.wasSuccessful() and clean else 'FAIL',
        python=platform.python_version(),platform=platform.system(),tests_run=result.testsRun,groups=groups,passed=sorted(set(result.passed)),
        new_tests=len(groups.get('test_durable_relational',[])),regression_tests=sum(len(v) for k,v in groups.items() if k!='test_durable_relational'),
        failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],skipped=[t.id() for t,_ in result.skipped],
        case_test_map=coverage(),owned_roots_created=len(own),owned_roots_remaining=remains(own),owned_children_started=len(support.CHILDREN),owned_children_alive=alive(support.CHILDREN),
        owned_child_exitcodes=[p.exitcode for p in support.CHILDREN],crash_exercises=support.CRASHES,independent_oracle_observations=support.ORACLES,
        T_regression_roots_created=len(t_roots),T_regression_roots_remaining=remains(t_roots),T_regression_children_started=len(t_children),T_regression_children_alive=alive(t_children),T_regression_child_exitcodes=[p.exitcode for p in t_children],
        capture_regression_roots_created=len(cap_roots),capture_regression_roots_remaining=remains(cap_roots),capture_regression_children_started=len(cap_children),capture_regression_children_alive=alive(cap_children),capture_regression_child_exitcodes=[p.exitcode for p in cap_children],
        regression_threads_started=len(threads),regression_threads_alive=alive(threads),cleanup_verified=clean,elapsed_seconds=round(time.monotonic()-started,3),inputs=inputs(),
        remote_requests=0,persistent_D2_writes=0,operations=0,operational_attempts=0,quota_consumed=0,reservations_created=0,operational_activation=False,
        D5_closed=False,global_gaps_open=[f'G{i:02}' for i in range(1,8)],real_evidence_criteria_not_run=7,docs_export_not_run=True,
        SQL_D2_D3_D4_reexecuted=False,distributed_atomicity_claimed=False)
    print(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False));return 0 if report['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
