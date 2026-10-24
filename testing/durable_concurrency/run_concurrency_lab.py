# SPDX-License-Identifier: GPL-3.0-only
"""Separate I42 HC campaign. JSON stdout is the new raw; never rewrites history."""
import io
import json
import platform
from pathlib import Path
import signal
import sys
import threading
import time
import unittest

from source_ingest.durable_task_fixture import DurableLab
from source_ingest.durable_relational_fixture import RelationalLab
from source_ingest.incremental_fixture import TemporaryFixtureLab
from testing.durable_concurrency import support as s
from testing.durable_concurrency.test_durable_concurrency import DurableConcurrencyTest


def inputs():
    paths = set(Path('source_ingest').glob('*.py'))
    paths.update(Path('testing/D5').glob('*.py'))
    paths.update(Path('testing/D5/fixtures').glob('*.md'))
    paths.update(Path('testing/durable_concurrency').glob('*.py'))
    paths.update(Path('testing/durable_concurrency').glob('*.md'))
    paths.update(Path('docs/design').glob('D5-I41-*.md'))
    paths.update(Path('docs/design').glob('D5-I35-*.md'))
    paths.update(map(Path, ['HANDOFF-D5-I32.md', 'docs/validation/D5-I41-design-review.json',
                           'docs/validation/D5-I40-results.json', 'docs/validation/D5-EVIDENCE-REGISTRY.json']))
    return s.hash_inputs(paths)


class Recorded(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = []

    campaign_expired = False

    def stopTest(self, test):
        super().stopTest(test)
        if self.campaign_expired:
            self.stop()

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test.id())


def main():
    s.require(sys.flags.optimize == 0 and __debug__, 'OPTIMIZATION_NOT_SUPPORTED')
    s.RECORDS.clear(); s.CHILDREN.clear(); s.EXTRA_ROOTS.clear()
    Recorded.campaign_expired = False
    for cls in (DurableLab, RelationalLab, TemporaryFixtureLab):
        cls.created_roots.clear()
    before = inputs()
    context = dict(python=platform.python_version(), implementation=platform.python_implementation(),
                   build=list(platform.python_build()), platform=platform.system(), machine=platform.machine(),
                   release=platform.release(), optimize=sys.flags.optimize, debug=__debug__,
                   filesystem_claim='LOCAL_LINUX_FLOCK_FSYNC_RENAME_ONLY', argv=['python3', '-B', '-m', 'testing.durable_concurrency.run_concurrency_lab'])
    started = time.monotonic()
    original_alarm = signal.getsignal(signal.SIGALRM)

    def timed_out(*_):
        Recorded.campaign_expired = True
        raise TimeoutError('CAMPAIGN_TIMEOUT')
    signal.signal(signal.SIGALRM, timed_out)
    signal.alarm(900)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DurableConcurrencyTest)
    expected = [t.id() for t in suite]
    try:
        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=Recorded).run(suite)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_alarm)
    after = inputs()
    roots = set(DurableLab.created_roots + RelationalLab.created_roots + TemporaryFixtureLab.created_roots + s.EXTRA_ROOTS)
    remaining_roots = sum(Path(p).exists() or Path(p).is_symlink() for p in roots)
    remaining_children = sum(p.is_alive() for p, _ in s.CHILDREN)
    remaining_threads = sum(t is not threading.main_thread() and t.is_alive() for t in threading.enumerate())
    validation = []
    try:
        s.validate_inventory(before, after)
        s.validate_report(result.passed, expected, result.skipped, remaining_roots+remaining_children+remaining_threads)
        s.require(all(r['status'] == 'PASS' and r['cleanup_verified'] for r in s.RECORDS), 'SCENARIO_INCOMPLETE')
        s.require({r['case'] for r in s.RECORDS} == {f'HC{i:02}' for i in range(1, 25)}, 'CASE_MAP_INCOMPLETE')
    except AssertionError as ex:
        validation.append(str(ex))
    report = dict(schema='d5.i42-concurrency-raw.v1', mode='SYNTHETIC_ONLY',
                  status='PASS' if result.wasSuccessful() and not validation else 'FAIL', context=context,
                  tests_run=result.testsRun, passed=result.passed, failures=[t.id() for t, _ in result.failures],
                  errors=[t.id() for t, _ in result.errors], skipped=[t.id() for t, _ in result.skipped], validation_errors=validation,
                  case_test_map={f'HC{i:02}':[DurableConcurrencyTest.__module__+'.DurableConcurrencyTest.test_HC'+f'{i:02}'] for i in range(1,25)},
                  scenarios=s.RECORDS, scenario_count=len(s.RECORDS), inputs_before=before, inputs_after=after,
                  owned_roots_created=len(roots), owned_roots_remaining=remaining_roots,
                  owned_children_started=len(s.CHILDREN), owned_children_alive=remaining_children, owned_threads_alive=remaining_threads,
                  child_exitcodes=[dict(**label, exitcode=p.exitcode) for p, label in s.CHILDREN],
                  elapsed_seconds=round(time.monotonic()-started, 3),
                  product_changed=False, historical_tests_runners_registry_changed=False,
                  remote_requests=0, persistent_D2_writes=0, operations=0, operational_attempts=0, quota_consumed=0, reservations_created=0,
                  operational_activation=False, migration_promotion=False, deployment=False, D6_started=False,
                  publication_authorized=False, D5_closed=False, global_gaps_open=[f'G{i:02}' for i in range(1,8)],
                  real_evidence_criteria_not_run=7, docs_durable_integration_not_run=True, historical_I34_I36_raw='NOT_RECORDED',
                  limits=dict(wait_seconds=s.WAIT_SECONDS, case_seconds=s.CASE_SECONDS, campaign_seconds=900,
                              live_children_per_case=4, events_per_case=s.MAX_EVENTS, raw_bytes=s.MAX_RAW_BYTES, event_bytes=s.MAX_EVENT_BYTES),
                  regressions_in_this_campaign=0)
    raw = json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2)
    s.require(len(raw.encode()) <= s.MAX_RAW_BYTES, 'RAW_BUDGET')
    print(raw)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
