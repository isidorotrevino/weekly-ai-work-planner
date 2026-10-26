# SPDX-License-Identifier: GPL-3.0-only
"""I67 audit-only TT48. Does not import historical campaign runtime."""
import ast
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import time
import unittest
from testing.evidence_trace import test_evidence_trace as tests

ROOT=Path(__file__).resolve().parents[2]

def inputs():
    plan=json.loads((ROOT/'docs/validation/D5-I66-design-review.json').read_text())
    names=set(plan['inputs'])|set(plan['documentary_inputs'])
    names.update(['docs/validation/D5-I66-design-review.json','docs/validation/D5-I66-integrity.json','docs/validation/D5-TRACE-REGISTRY.json','scripts/trace-d5-evidence.py','docs/design/D5-I67-TRACEABILITY-LAB.md'])
    names.update(str(p.relative_to(ROOT)) for p in (ROOT/'testing/evidence_trace').iterdir() if p.is_file() and p.suffix in ('.py','.md'))
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(names)}


class Recorded(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.passed=[];self.records=[];self.started=time.monotonic()
    def startTest(self,test):super().startTest(test);self.case_started=time.monotonic()
    def addSuccess(self,test):
        super().addSuccess(test);self.passed.append(test.id());case=test._testMethodName[5:]
        detail=next((r for r in tests.RECORDS if r['case']==case),{})
        self.records.append(dict(detail,case=case,test_id=test.id(),status='PASS',elapsed_seconds=round(time.monotonic()-self.case_started,6),checks=test.observations,new_functional_tests=0,global_accepted=False))
    def stopTest(self,test):
        super().stopTest(test)
        if time.monotonic()-self.started>300:self.stop()


def main():
    if sys.flags.optimize or not __debug__:raise RuntimeError('OPTIMIZATION_NOT_SUPPORTED')
    before=inputs();tests.RECORDS.clear();tests.ROOTS.clear();started=time.monotonic()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.TraceTest)
    result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=Recorded).run(suite);after=inputs()
    valid=result.wasSuccessful() and result.testsRun==48 and len(set(result.passed))==48 and before==after and len(result.records)==48 and all(r['removed'] and r['ownership_verified'] for r in tests.ROOTS)
    source=ROOT/'testing/evidence_trace/test_evidence_trace.py';tree=ast.parse(source.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='TraceTest')
    methods={n.name:dict(path=str(source.relative_to(ROOT)),line=n.lineno,end_line=n.end_lineno,sha256=hashlib.sha256(source.read_bytes()).hexdigest()) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_TT')}
    report=dict(schema='d5.i67-trace-tests-raw.v1',status='PASS' if valid else 'FAIL',tests_run=result.testsRun,passed=result.passed,case_test_map={r['case']:[r['test_id']] for r in result.records},scenarios=result.records,method_sources=methods,failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],skipped=[t.id() for t,_ in result.skipped],diagnostic_codes=['AUDIT_TEST_FAILURE'] if not valid else [],context=dict(argv=['python3','-B','-m','testing.evidence_trace.run_trace_lab'],scope='AUDIT_ONLY_CURRENT_CONTEXT',python=platform.python_version(),implementation=platform.python_implementation(),build=list(platform.python_build()),platform=platform.system(),release=platform.release(),machine=platform.machine(),optimize=sys.flags.optimize,debug=__debug__),inputs_before=before,inputs_after=after,elapsed_seconds=round(time.monotonic()-started,3),functional_campaigns_executed=0,auditor_I38_executed=False,product_or_historical_harness_imported=False,owned_lab_processes=0,owned_lab_threads=0,temporary_roots_created=len(tests.ROOTS),ownership_verified_roots=sum(r['ownership_verified'] for r in tests.ROOTS),temporary_roots_remaining=sum(not r['removed'] for r in tests.ROOTS),semantic_baseline=dict(SUPPORTS_BOUNDED=81,PARTIAL=3),D5_closed=False,closure=False,global_review='OPEN',publication_authorized=False)
    data=json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)
    if len(data.encode())>12*1024*1024:raise RuntimeError('RAW_BUDGET')
    print(data)
    # Detailed unittest traces are never put into versioned output.
    if not valid:sys.stderr.write('AUDIT_TEST_FAILURE\n')
    return 0 if valid else 1


if __name__=='__main__':raise SystemExit(main())
