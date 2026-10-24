# SPDX-License-Identifier: GPL-3.0-only
"""I55 NA raw stdout: its own campaign, no historical evidence rewriting."""
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
from testing.durable_native_ambiguity import support as s
from testing.durable_native_ambiguity.test_durable_native_ambiguity import NativeAmbiguityTest
from source_ingest.durable_ambiguity_fixture import NativeLab


def inputs():
    paths=set(Path('source_ingest').glob('*.py'))
    paths.update(Path('testing/D5').glob('*.py'))
    paths.update(Path('testing/D5/fixtures').glob('*.md'))
    for folder in ('testing/durable_concurrency','testing/durable_crash_boundaries','testing/durable_issue_create','testing/durable_uncertainty','testing/durable_inflight_revocation','testing/durable_native_ambiguity'):
        paths.update(Path(folder).glob('*.py'));paths.update(Path(folder).glob('*.md'))
    for prefix in ('D5-I35-','D5-I41-','D5-I43-','D5-I45-','D5-I49-','D5-I51-','D5-I54-'):
        paths.update(Path('docs/design').glob(prefix+'*.md'))
    paths.update(map(Path,['HANDOFF-D5-I32.md','docs/validation/D5-EVIDENCE-REGISTRY.json',
                          'docs/validation/D5-I40-results.json','docs/validation/D5-I41-design-review.json',
                          'docs/validation/D5-I42-results.json','docs/validation/D5-I43-design-review.json',
                          'docs/validation/D5-I44-results.json','docs/validation/D5-I45-design-review.json',
                          'docs/validation/D5-I46-results.json','docs/validation/D5-I48-results.json',
                          'docs/validation/D5-I49-scope-review.json','docs/validation/D5-I49-design-review.json',
                          'docs/validation/D5-I53-results.md','docs/validation/D5-I53-matrix.md',
                          'docs/validation/D5-I53-results.json','docs/validation/D5-I53-integrity.json',
                          'docs/validation/D5-I54-design-review.json']))
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
    for cls in (DurableLab,RelationalLab,TemporaryFixtureLab,NativeLab):cls.created_roots.clear()
    before=inputs();started=time.monotonic()
    context=dict(python=platform.python_version(),implementation=platform.python_implementation(),build=list(platform.python_build()),
                 platform=platform.system(),machine=platform.machine(),release=platform.release(),optimize=sys.flags.optimize,debug=__debug__,
                 filesystem_claim='LOCAL_LINUX_FLOCK_FSYNC_RENAME_ONLY',argv=['python3','-B','-m','testing.durable_native_ambiguity.run_native_ambiguity_lab'])
    old_signal=signal.getsignal(signal.SIGALRM)

    def expired(*_):
        Recorded.campaign_expired=True
        raise TimeoutError('CAMPAIGN_TIMEOUT')
    signal.signal(signal.SIGALRM,expired);signal.alarm(s.CAMPAIGN_SECONDS)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(NativeAmbiguityTest);expected=[t.id() for t in suite]
    try:result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=Recorded).run(suite)
    finally:signal.alarm(0);signal.signal(signal.SIGALRM,old_signal)
    after=inputs()
    roots=set(DurableLab.created_roots+RelationalLab.created_roots+TemporaryFixtureLab.created_roots+NativeLab.created_roots+s.EXTRA_ROOTS)
    remaining_roots=sum(Path(p).exists() or Path(p).is_symlink() for p in roots)
    remaining_children=sum(p.is_alive() for p,_ in s.CHILDREN)
    remaining_threads=sum(t is not threading.main_thread() and t.is_alive() for t in threading.enumerate())
    validation=[]
    try:
        s.validate_inventory(before,after)
        s.validate_report(result.passed,expected,result.skipped,remaining_roots+remaining_children+remaining_threads)
        s.require(all(r['status']=='PASS' and r['cleanup_verified'] for r in s.RECORDS),'SCENARIO_INCOMPLETE')
        s.require({r['case'] for r in s.RECORDS}=={f'NA{i:02}' for i in range(1,37)},'CASE_MAP_INCOMPLETE')
    except AssertionError as ex:validation.append(str(ex))
    events=[e for r in s.RECORDS for e in r['events']]
    report=dict(schema='d5.i55-native-ambiguity-raw.v1',mode='SYNTHETIC_ONLY',status='PASS' if result.wasSuccessful() and not validation else 'FAIL',
                context=context,tests_run=result.testsRun,passed=result.passed,failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],
                failure_identifiers=failure_identifiers(result.failures+result.errors),skipped=[t.id() for t,_ in result.skipped],validation_errors=validation,
                case_test_map={f'NA{i:02}':[NativeAmbiguityTest.__module__+'.NativeAmbiguityTest.test_NA'+f'{i:02}'] for i in range(1,37)},
                scenarios=s.RECORDS,scenario_count=len(s.RECORDS),model_gaps=[dict(id=g,status=status,is_test=False) for g,status in [('MG01','IMPLEMENTED_BOUNDED_REVIEW_PENDING'),('MG02','IMPLEMENTED_BOUNDED_REVIEW_PENDING_SYNTHETIC_PROTOCOL'),('MG03','OUT_OF_SCOPE_NO_ADOPTION')]],
                inputs_before=before,inputs_after=after,owned_roots_created=len(roots),owned_roots_remaining=remaining_roots,
                owned_children_started=len(s.CHILDREN),owned_children_alive=remaining_children,owned_threads_alive=remaining_threads,
                child_exitcodes=[dict(**label,exitcode=p.exitcode) for p,label in s.CHILDREN],elapsed_seconds=round(time.monotonic()-started,3),
                limits=dict(wait_seconds=s.WAIT_SECONDS,case_seconds=s.CASE_SECONDS,campaign_seconds=s.CAMPAIGN_SECONDS,live_children_per_case=4,
                            events_per_case=s.MAX_EVENTS,event_bytes=s.MAX_EVENT_BYTES,raw_bytes=s.MAX_RAW_BYTES),
                regressions_in_this_campaign=0,product_changed=False,new_synthetic_fixture_added=True,historical_tests_runners_I42_I44_I46_registry_changed=False,
                remote_requests=0,persistent_D2_writes=0,operations=0,operational_attempts=0,quota_consumed=0,reservations_created=0,
                operational_activation=False,migration_promotion=False,deployment=False,D6_started=False,publication_authorized=False,
                D5_closed=False,global_gaps_open=[f'G{i:02}' for i in range(1,8)],real_evidence_criteria_not_run=7,docs_durable_integration_not_run=True,
                historical_I34_I36_raw='NOT_RECORDED',power_loss_durability_claimed=False,
                UI20_3='PARTIAL_UNCHANGED',H07_closed=False,actual_HTTP_429_tested=False,native_multiple_matches_tested=True,native_synthetic_429_tested=True)
    # AST locations are descriptive links, never discovery/import of extra tests.
    import ast
    source=Path('testing/durable_native_ambiguity/test_durable_native_ambiguity.py')
    cls=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.ClassDef))
    report['method_sources']={n.name:dict(path=str(source),line=n.lineno,end_line=n.end_lineno,sha256=s.hash_inputs([source])[str(source)]) for n in cls.body if isinstance(n,ast.FunctionDef)}
    report['discovery_rules']=['source_ingest/*.py','testing/D5/*.py','testing/D5/fixtures/*.md',
        'helpers HC/HF/IC/UQ/RV and NA *.py/*.md','I35/I41/I43/I45/I49/I51/I54 design *.md',
        'explicit historical seals/registry/handoff and I53 documentation listed by inputs()']
    print(s.bounded_raw(report))
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
