# SPDX-License-Identifier: GPL-3.0-only
"""I32 sanitized memory campaign with historical regression resources separated."""
import io
import json
from pathlib import Path
import platform
import sys
import time
import unittest

from source_ingest.incremental_fixture import TemporaryFixtureLab
from testing.D5.run_incremental_lab import Recorded


def main():
    TemporaryFixtureLab.created_roots.clear()
    started=time.monotonic()
    suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent),pattern='test*.py')
    result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=Recorded).run(suite)
    roots=TemporaryFixtureLab.created_roots
    remaining=sum(Path(p).exists() or Path(p).is_symlink() for p in roots)
    capture=sys.modules.get('test_incremental_capture')
    children=capture.CHILDREN if capture else []
    previous_threads=[]
    for name in ('test_plane_reconciliation','test_relational_batch'):
        module=sys.modules.get(name)
        if module: previous_threads.extend(module.THREADS)
    module=sys.modules.get('test_profiles_quotas')
    threads=module.THREADS if module else []
    children_left=sum(c.is_alive() for c in children)
    previous_threads_left=sum(t.is_alive() for t in previous_threads)
    threads_left=sum(t.is_alive() for t in threads)
    new=[p for p in result.passed if p.startswith('test_profiles_quotas.')]
    cleanup=not remaining and not children_left and not previous_threads_left and not threads_left
    report=dict(schema='d5.eligibility-fixture-campaign.v1',mode='SYNTHETIC_ONLY',
        status='PASS' if result.wasSuccessful() and cleanup else 'FAIL',
        python=platform.python_version(),platform=platform.system(),tests_run=result.testsRun,
        new_tests=len(new),regression_tests=len(result.passed)-len(new),passed=result.passed,
        failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],
        skipped=[t.id() for t,_ in result.skipped],new_owned_threads_started=len(threads),
        new_owned_threads_alive=threads_left,regression_owned_threads_started=len(previous_threads),
        regression_owned_threads_alive=previous_threads_left,regression_owned_roots_created=len(roots),
        regression_owned_roots_remaining=remaining,regression_fixture_children_started=len(children),
        regression_fixture_children_alive=children_left,regression_fixture_child_exitcodes=[c.exitcode for c in children],
        cleanup_verified=cleanup,elapsed_seconds=round(time.monotonic()-started,3),
        remote_requests=0,persistent_D2_writes=0,quota_consumed=0,reservations_created=0,
        operational_activation=False,D5_closed=False,real_provider_validation=False)
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
