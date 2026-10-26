# SPDX-License-Identifier: GPL-3.0-only
"""PF60 component campaign. Historical runners and product must stay unloaded."""
import ast
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import time
import unittest
from testing.prospective_capture import test_prospective_capture as tests

ROOT=Path(__file__).resolve().parents[2]


def inputs():
    plan=json.loads((ROOT/'docs/validation/D5-I69-design-review.json').read_text());names=set(plan['inputs'])|set(plan['documentary_inputs'])
    names.update(['docs/validation/D5-I69-design-review.json','docs/validation/D5-I69-integrity.json','docs/validation/D5-PROSPECTIVE-CAPTURE-REGISTRY.json','docs/design/D5-I70-PROSPECTIVE-CAPTURE-LAB.md'])
    names.update(str(p.relative_to(ROOT)) for p in (ROOT/'testing/prospective_capture').iterdir() if p.is_file() and p.suffix in ('.py','.md'))
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(names)}


class Recorded(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.passed=[];self.records=[];self.started=time.monotonic()
    def startTest(self,test):super().startTest(test);self.case_started=time.monotonic()
    def addSuccess(self,test):
        super().addSuccess(test);self.passed.append(test.id());case=test._testMethodName[5:];detail=next((r for r in tests.DETAILS if r['case']==case),{})
        self.records.append(dict(detail,case=case,test_id=test.id(),status='PASS',elapsed_seconds=round(time.monotonic()-self.case_started,6),checks=test.observations,new_functional_tests=0,global_accepted=False))
    def stopTest(self,test):
        super().stopTest(test)
        if time.monotonic()-self.started>300:self.stop()


def main():
    if sys.flags.optimize or not __debug__:raise RuntimeError('OPTIMIZATION_NOT_SUPPORTED')
    tests.OWN_ROOTS.clear();tests.CHILDREN.clear();tests.DETAILS.clear();before=inputs();started=time.monotonic();diagnostics=io.StringIO()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.CaptureTest);result=unittest.TextTestRunner(stream=diagnostics,resultclass=Recorded).run(suite);after=inputs()
    forbidden=sorted(m for m in sys.modules if m.startswith(('source_ingest','testing.D5','testing.durable_','testing.gi39_interleavings','testing.causal_frontier_cells','testing.evidence_trace','testing.evidence_audit')))
    roots_remaining=sum(not r['removed'] for r in tests.OWN_ROOTS);ownership=sum(r['ownership_verified'] for r in tests.OWN_ROOTS);children_unsettled=sum(r['exitcode'] is None for r in tests.CHILDREN)
    valid=result.wasSuccessful() and result.testsRun==60 and len(set(result.passed))==60 and len(result.records)==60 and before==after and not forbidden and not roots_remaining and not children_unsettled and ownership==len(tests.OWN_ROOTS)
    source=ROOT/'testing/prospective_capture/test_prospective_capture.py';cls=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.ClassDef) and n.name=='CaptureTest')
    anchors={n.name:dict(path=str(source.relative_to(ROOT)),line=n.lineno,end_line=n.end_lineno,sha256=hashlib.sha256(source.read_bytes()).hexdigest()) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_PF')}
    report=dict(schema='d5.i70-capture-component-tests.v1',status='PASS' if valid else 'FAIL',tests_run=result.testsRun,passed=result.passed,case_test_map={r['case']:[r['test_id']] for r in result.records},scenarios=result.records,method_sources=anchors,failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],skipped=[t.id() for t,_ in result.skipped],diagnostic_codes=[] if valid else ['COMPONENT_TEST_FAILURE'],context=dict(argv=['python3','-B','-m','testing.prospective_capture.run_capture_lab'],scope='I70_COMPONENTS_ONLY',**tests.c.environment()),inputs_before=before,inputs_after=after,elapsed_seconds=round(time.monotonic()-started,3),temporary_roots_created=len(tests.OWN_ROOTS),ownership_verified_roots=ownership,temporary_roots_remaining=roots_remaining,owned_synthetic_children=len(tests.CHILDREN),owned_synthetic_child_exitcodes=tests.CHILDREN,owned_children_unsettled=children_unsettled,positive_domain_SIGKILLs=0,forbidden_imports=forbidden,historical_runners_or_product_imported=bool(forbidden),functional_campaigns_executed=0,auditor_I38_executed=False,tracer_I67_executed=False,functional_capture_execution_authorized=False,prospective_scopes={f'P{i:02}':'NOT_RUN_I71_AUTHORIZATION_REQUIRED' for i in range(1,11)},semantic_baseline=dict(SUPPORTS_BOUNDED=81,PARTIAL=3),D5_closed=False,global_review='OPEN',closure=False,publication_authorized=False)
    data=json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)
    if len(data.encode())>12*1024*1024:raise RuntimeError('RAW_BUDGET')
    print(data)
    if not valid:sys.stderr.write('COMPONENT_TEST_FAILURE\n')
    return 0 if valid else 1


if __name__=='__main__':raise SystemExit(main())
