# SPDX-License-Identifier: GPL-3.0-only
"""Run synthetic DI tests/regressions; emit sanitized evidence, never source bytes."""
import io
import json
from pathlib import Path
import platform
import sys
import time
import unittest

from source_ingest.incremental_fixture import TemporaryFixtureLab


class Recorded(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test.id())


def main():
    started = time.monotonic()
    TemporaryFixtureLab.created_roots.clear()
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern='test*.py')
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Recorded).run(suite)
    roots = TemporaryFixtureLab.created_roots
    remaining = sum(Path(p).exists() or Path(p).is_symlink() for p in roots)
    module = sys.modules.get('test_incremental_capture')
    children = module.CHILDREN if module is not None else []
    live = sum(p.is_alive() for p in children)
    new = [p for p in result.passed if p.startswith('test_incremental_capture.')]
    report = dict(schema='d5.incremental-fixture-campaign.v1', mode='SYNTHETIC_ONLY',
                  status='PASS' if result.wasSuccessful() and not remaining and not live else 'FAIL',
                  python=platform.python_version(), platform=platform.system(),
                  tests_run=result.testsRun, new_tests=len(new), local_regression=len(result.passed)-len(new),
                  passed=result.passed, failures=[t.id() for t,_ in result.failures],
                  errors=[t.id() for t,_ in result.errors], skipped=[t.id() for t,_ in result.skipped],
                  owned_roots_created=len(roots), owned_roots_remaining=remaining,
                  explicit_fixture_children_started=len(children), explicit_fixture_children_alive=live,
                  fixture_child_exitcodes=[p.exitcode for p in children],
                  cleanup_verified=not remaining and not live,
                  elapsed_seconds=round(time.monotonic()-started,3),
                  persistent_D2_writes=0, remote_requests=0, reference_selected=False,
                  D5_closed=False, real_provider_validation=False)
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
