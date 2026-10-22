# SPDX-License-Identifier: GPL-3.0-only
"""I28 sanitized campaign; historical I26 filesystem regression stays separate."""
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
    started = time.monotonic()
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern='test*.py')
    result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=Recorded).run(suite)
    roots = TemporaryFixtureLab.created_roots
    roots_left = sum(Path(p).exists() or Path(p).is_symlink() for p in roots)
    incremental = sys.modules.get('test_incremental_capture')
    children = incremental.CHILDREN if incremental else []
    plane = sys.modules.get('test_plane_reconciliation')
    threads = plane.THREADS if plane else []
    children_left = sum(c.is_alive() for c in children)
    threads_left = sum(t.is_alive() for t in threads)
    new = [p for p in result.passed if p.startswith('test_plane_reconciliation.')]
    cleanup = not roots_left and not children_left and not threads_left
    report = dict(schema='d5.plane-fixture-campaign.v1', mode='SYNTHETIC_ONLY',
                  status='PASS' if result.wasSuccessful() and cleanup else 'FAIL',
                  python=platform.python_version(), platform=platform.system(),
                  tests_run=result.testsRun, new_tests=len(new),
                  regression_tests=len(result.passed)-len(new), passed=result.passed,
                  failures=[t.id() for t,_ in result.failures],
                  errors=[t.id() for t,_ in result.errors], skipped=[t.id() for t,_ in result.skipped],
                  new_owned_threads_started=len(threads), new_owned_threads_alive=threads_left,
                  regression_owned_roots_created=len(roots), regression_owned_roots_remaining=roots_left,
                  regression_fixture_children_started=len(children), regression_fixture_children_alive=children_left,
                  regression_fixture_child_exitcodes=[c.exitcode for c in children], cleanup_verified=cleanup,
                  elapsed_seconds=round(time.monotonic()-started,3),
                  real_remote_requests=0, persistent_D2_writes=0, operational_activation=False,
                  D5_closed=False, real_provider_validation=False)
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if report['status']=='PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
