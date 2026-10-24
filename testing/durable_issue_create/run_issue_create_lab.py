# SPDX-License-Identifier: GPL-3.0-only
"""I46 IC raw stdout: its own campaign, no historical evidence rewriting."""
import io
import json
from pathlib import Path
import platform
import re
import signal
import sys
import threading
import time
import unittest

from source_ingest.durable_task_fixture import DurableLab
from source_ingest.durable_relational_fixture import RelationalLab
from source_ingest.incremental_fixture import TemporaryFixtureLab
from testing.durable_issue_create import support as s
from testing.durable_issue_create.test_durable_issue_create import IssueCreateTest


def inputs():
    paths=set(Path('source_ingest').glob('*.py'))
    paths.update(Path('testing/D5').glob('*.py'))
    paths.update(Path('testing/D5/fixtures').glob('*.md'))
    for folder in ('testing/durable_concurrency','testing/durable_crash_boundaries','testing/durable_issue_create'):
        paths.update(Path(folder).glob('*.py'));paths.update(Path(folder).glob('*.md'))
    for prefix in ('D5-I35-','D5-I41-','D5-I43-','D5-I45-'):
        paths.update(Path('docs/design').glob(prefix+'*.md'))
    paths.update(map(Path,['HANDOFF-D5-I32.md','docs/validation/D5-EVIDENCE-REGISTRY.json',
                          'docs/validation/D5-I40-results.json','docs/validation/D5-I41-design-review.json',
                          'docs/validation/D5-I42-results.json','docs/validation/D5-I43-design-review.json',
                          'docs/validation/D5-I44-results.json','docs/validation/D5-I45-design-review.json']))
    return s.hash_inputs(paths)


class Recorded(unittest.TextTestResult):
    campaign_expired=False

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.passed=[]

    def addSuccess(self,test):
        super().addSuccess(test);self.passed.append(test.id())

    def stopTest(self,test):
        super().stopTest(test)
        if self.campaign_expired:self.stop()


def failure_identifiers(items):
    result=[]
    for test,trace in items:
        final=trace.strip().splitlines()[-1]
        kind,_,detail=final.partition(': ')
        result.append(dict(test=test.id(),kind=kind if re.fullmatch('[A-Za-z]+',kind) else 'ERROR',
                           code=detail if re.fullmatch('[A-Z0-9_]+',detail) else 'DETAIL_REDACTED'))
    return result


def main():
    s.require(sys.flags.optimize==0 and __debug__,'OPTIMIZATION_NOT_SUPPORTED')
    s.RECORDS.clear();s.CHILDREN.clear();s.EXTRA_ROOTS.clear();Recorded.campaign_expired=False
    for cls in (DurableLab,RelationalLab,TemporaryFixtureLab):cls.created_roots.clear()
    before=inputs();started=time.monotonic()
    context=dict(python=platform.python_version(),implementation=platform.python_implementation(),build=list(platform.python_build()),
                 platform=platform.system(),machine=platform.machine(),release=platform.release(),optimize=sys.flags.optimize,debug=__debug__,
                 filesystem_claim='LOCAL_LINUX_FLOCK_FSYNC_RENAME_ONLY',argv=['python3','-B','-m','testing.durable_issue_create.run_issue_create_lab'])
    old_signal=signal.getsignal(signal.SIGALRM)

    def expired(*_):
        Recorded.campaign_expired=True
        raise TimeoutError('CAMPAIGN_TIMEOUT')
    signal.signal(signal.SIGALRM,expired);signal.alarm(s.CAMPAIGN_SECONDS)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(IssueCreateTest);expected=[t.id() for t in suite]
    try:result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=Recorded).run(suite)
    finally:signal.alarm(0);signal.signal(signal.SIGALRM,old_signal)
    after=inputs()
    roots=set(DurableLab.created_roots+RelationalLab.created_roots+TemporaryFixtureLab.created_roots+s.EXTRA_ROOTS)
    remaining_roots=sum(Path(p).exists() or Path(p).is_symlink() for p in roots)
    remaining_children=sum(p.is_alive() for p,_ in s.CHILDREN)
    remaining_threads=sum(t is not threading.main_thread() and t.is_alive() for t in threading.enumerate())
    validation=[]
    try:
        s.validate_inventory(before,after)
        s.validate_report(result.passed,expected,result.skipped,remaining_roots+remaining_children+remaining_threads)
        s.require(all(r['status']=='PASS' and r['cleanup_verified'] for r in s.RECORDS),'SCENARIO_INCOMPLETE')
        s.require({r['case'] for r in s.RECORDS}=={f'IC{i:02}' for i in range(1,31)},'CASE_MAP_INCOMPLETE')
    except AssertionError as ex:validation.append(str(ex))
    events=[e for r in s.RECORDS for e in r['events']]
    report=dict(schema='d5.i46-issue-create-raw.v1',mode='SYNTHETIC_ONLY',status='PASS' if result.wasSuccessful() and not validation else 'FAIL',
                context=context,tests_run=result.testsRun,passed=result.passed,failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],
                failure_identifiers=failure_identifiers(result.failures+result.errors),skipped=[t.id() for t,_ in result.skipped],validation_errors=validation,
                case_test_map={f'IC{i:02}':[IssueCreateTest.__module__+'.IssueCreateTest.test_IC'+f'{i:02}'] for i in range(1,31)},
                scenarios=s.RECORDS,scenario_count=len(s.RECORDS),forced_process_order_rows=sum(any(e['event']=='LOCK_HELD_OBSERVED' for e in r['events']) for r in s.RECORDS),
                observed_lock_probes=sum(e['event']=='LOCK_HELD_OBSERVED' for e in events),
                remote_extra_ticket_rows=[r['case'] for r in s.RECORDS if r.get('integrated_claim_allowed') is False],
                inputs_before=before,inputs_after=after,owned_roots_created=len(roots),owned_roots_remaining=remaining_roots,
                owned_children_started=len(s.CHILDREN),owned_children_alive=remaining_children,owned_threads_alive=remaining_threads,
                child_exitcodes=[dict(**label,exitcode=p.exitcode) for p,label in s.CHILDREN],elapsed_seconds=round(time.monotonic()-started,3),
                limits=dict(wait_seconds=s.WAIT_SECONDS,case_seconds=s.CASE_SECONDS,campaign_seconds=s.CAMPAIGN_SECONDS,live_children_per_case=4,
                            events_per_case=s.MAX_EVENTS,event_bytes=s.MAX_EVENT_BYTES,raw_bytes=s.MAX_RAW_BYTES),
                regressions_in_this_campaign=0,product_changed=False,historical_tests_runners_I42_I44_registry_changed=False,
                remote_requests=0,persistent_D2_writes=0,operations=0,operational_attempts=0,quota_consumed=0,reservations_created=0,
                operational_activation=False,migration_promotion=False,deployment=False,D6_started=False,publication_authorized=False,
                D5_closed=False,global_gaps_open=[f'G{i:02}' for i in range(1,8)],real_evidence_criteria_not_run=7,docs_durable_integration_not_run=True,
                historical_I34_I36_raw='NOT_RECORDED',power_loss_durability_claimed=False)
    print(s.bounded_raw(report))
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
