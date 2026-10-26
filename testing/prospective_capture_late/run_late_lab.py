# SPDX-License-Identifier: GPL-3.0-only
"""LB64 component campaign, no historical imports or functional executions."""
import ast
import io
import json
from pathlib import Path
import sys
import time
import unittest
from testing.prospective_capture_late import test_late_capture as tests
p=tests.p;c=p.c;ROOT=p.ROOT


def inputs():
    design=json.loads((ROOT/'docs/validation/D5-I78-design-review.json').read_text());names=set(design['inputs'])
    names.update(['docs/validation/D5-I78-design-review.json','docs/validation/D5-I78-integrity.json','docs/design/D5-I78-LATE-BINDING-DESIGN.md','docs/design/D5-I78-LATE-BINDING-REVIEW.md','docs/design/D5-I79-LATE-CAPTURE-LAB.md',p.REGISTRY])
    names.update(str(q.relative_to(ROOT)) for q in (ROOT/'testing/prospective_capture_late').iterdir() if q.is_file() and q.suffix in ('.py','.md'))
    return {name:c.sha((ROOT/name).read_bytes()) for name in sorted(names)}


class Recorded(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.passed=[];self.records=[];self.started=time.monotonic()
    def startTest(self,test):super().startTest(test);self.case_started=time.monotonic()
    def addSuccess(self,test):
        super().addSuccess(test);self.passed.append(test.id());self.records.append(dict(case=test._testMethodName[5:],test_id=test.id(),status='PASS',checks=test.observations,elapsed_seconds=round(time.monotonic()-self.case_started,6),scope='SYNTHETIC_COMPONENT_ONLY',functional_occurrences=0,global_accepted=False))
    def stopTest(self,test):
        super().stopTest(test)
        if time.monotonic()-self.started>300:self.stop()


def main():
    if sys.flags.optimize or not __debug__:raise RuntimeError('OPTIMIZATION_NOT_SUPPORTED')
    tests.ROOTS.clear();tests.CHILDREN.clear();before=inputs();started=time.monotonic();diagnostics=io.StringIO()
    result=unittest.TextTestRunner(stream=diagnostics,resultclass=Recorded).run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.LateTest));after=inputs();forbidden=tests.forbidden()
    roots=tests.ROOTS;children=tests.CHILDREN;pending=sum(ch['exitcode'] is None for ch in children)
    absent=not (ROOT/p.AUTHORITY).exists() and not (ROOT/p.DESTINATION).exists() and not (ROOT/p.LAUNCH_COPY).exists()
    elapsed=time.monotonic()-started
    valid=result.wasSuccessful() and result.testsRun==64 and len(set(result.passed))==64 and len(result.records)==64 and before==after and not forbidden and not pending and absent and all(r['ownership_verified'] and r['removed'] and r['sibling_preserved'] for r in roots) and elapsed<300
    source=ROOT/'testing/prospective_capture_late/test_late_capture.py';cls=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.ClassDef) and n.name=='LateTest')
    anchors={n.name:dict(path=str(source.relative_to(ROOT)),line=n.lineno,end_line=n.end_lineno,sha256=c.sha(source.read_bytes())) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_LB')}
    report=dict(schema='d5.i79-late-component-tests.v1',status='PASS' if valid else 'FAIL',tests_run=result.testsRun,passed=result.passed,case_test_map={r['case']:[r['test_id']] for r in result.records},scenarios=result.records,method_sources=anchors,failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],skipped=[t.id() for t,_ in result.skipped],diagnostic_codes=[] if valid else ['COMPONENT_TEST_FAILURE'],context=dict(argv=['python3','-B','-m','testing.prospective_capture_late.run_late_lab'],scope='I79_COMPONENTS_ONLY',**c.environment()),inputs_before=before,inputs_after=after,elapsed_seconds=round(elapsed,3),temporary_roots_created=len(roots),ownership_verified_roots=sum(r['ownership_verified'] for r in roots),temporary_roots_remaining=sum(not r['removed'] for r in roots),sibling_controls_preserved=sum(r['sibling_preserved'] for r in roots),owned_synthetic_children=len(children),owned_synthetic_child_exitcodes=children,owned_children_unsettled=pending,positive_domain_SIGKILLs=0,forbidden_imports=forbidden,historical_runners_or_product_imported=bool(forbidden),functional_campaigns_executed=0,auditor_I38_executed=False,tracer_I67_executed=False,functional_capture_execution_authorized=False,I80_authority_and_destination_absent=absent,prospective_P01='NOT_RUN_I80_AUTHORIZATION_REQUIRED',semantic_baseline=dict(SUPPORTS_BOUNDED=81,PARTIAL=3),D5_closed=False,global_review='OPEN',closure=False,publication_authorized=False)
    data=json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2);c.require(len(data.encode())<=12*1024*1024,'RAW_BUDGET');print(data)
    if not valid:sys.stderr.write('COMPONENT_TEST_FAILURE\n')
    return 0 if valid else 1


if __name__=='__main__':raise SystemExit(main())
