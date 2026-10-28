# SPDX-License-Identifier: GPL-3.0-only
"""I95 CB32 synthetic-only lab; requires external300s timeout."""
import ast
import io
import json
import sys
import time
import unittest
from testing.prospective_capture_capacity import test_capacity as tests
p=tests.p;ROOT=p.ROOT;SOURCE='testing/prospective_capture_capacity/test_capacity.py';INPUTS=p.Reader(ROOT,p.DEFAULT_LIMITS)

class Recorded(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.records=[];self.passed=[]
    def startTest(self,test):super().startTest(test);self.before=p.sha(INPUTS.read(SOURCE));self.started=time.monotonic()
    def addSuccess(self,test):
        super().addSuccess(test);self.passed.append(test.id());self.records.append(dict(case=test._testMethodName[5:],test_id=test.id(),status='PASS',checks=test.observations,method_source_before=self.before,method_source_after=p.sha(INPUTS.read(SOURCE)),elapsed_seconds=round(time.monotonic()-self.started,6),scope='SYNTHETIC_CAPACITY_PLANNER_ONLY',inputs_before_ref='/inputs_before',inputs_after_ref='/inputs_after',context_ref='/context',functional_occurrences=0,global_accepted=False))

def main():
    if sys.flags.optimize or not __debug__:raise RuntimeError('OPTIMIZATION_NOT_SUPPORTED')
    started=time.monotonic();manifest=p.read_manifest(INPUTS);INPUTS.read('docs/design/D5-I95-CAPACITY-PLANNER-LAB.md');before=dict(INPUTS.hashes);stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,resultclass=Recorded).run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.CapacityTest));INPUTS.finish();after=dict(INPUTS.hashes);forbidden=tests.forbidden();roots=tests.ROOTS;threads=tests.THREADS
    absent=all(not (ROOT/n).exists() for n in ('docs/validation/D5-I96-capture-authorization.json','docs/validation/D5-I96-P01','docs/validation/D5-I96-P01-launch.json'))
    elapsed=time.monotonic()-started;valid=result.wasSuccessful() and result.testsRun==32 and len(result.records)==32 and len(set(result.passed))==32 and before==after and not forbidden and absent and all(r['ownership_verified'] and r['removed'] and r['sibling_preserved'] for r in roots) and not any(t['alive'] for t in threads) and elapsed<300
    body=(ROOT/SOURCE).read_bytes();cls=next(n for n in ast.parse(body).body if isinstance(n,ast.ClassDef) and n.name=='CapacityTest');anchors={n.name:dict(path=SOURCE,line=n.lineno,end_line=n.end_lineno,sha256=p.sha(body)) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_CB')}
    report=dict(schema='d5.i95-capacity-component-tests.v1',status='PASS' if valid else 'FAIL',tests_run=result.testsRun,passed=result.passed,case_test_map={r['case']:[r['test_id']] for r in result.records},scenarios=result.records,method_sources=anchors,failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],skipped=[t.id() for t,_ in result.skipped],diagnostics=stream.getvalue() if not valid else None,context=dict(argv=['python3','-B','-m','testing.prospective_capture_capacity.run_capacity_lab'],scope='I95_SYNTHETIC_PLANNER_ONLY',python=sys.version.split()[0],optimization=sys.flags.optimize),inputs_before=before,inputs_after=after,input_reader=dict(paths=len(INPUTS.hashes),unique_bytes=INPUTS.accounting.unique,read_bytes=INPUTS.accounting.total,unique_limit=manifest['limits']['input_unique_bytes'],read_limit=manifest['limits']['input_read_bytes'],scope='ONE_DOCUMENTARY_READER_INCLUDES_MANIFEST_SEALS_INPUTS_CASE_SOURCE_AND_FINISH_NOT_ALL_OS_UNIT_READS'),elapsed_seconds=round(elapsed,3),temporary_roots_created=len(roots),ownership_verified_roots=sum(x['ownership_verified'] for x in roots),temporary_roots_remaining=sum(not x['removed'] for x in roots),sibling_controls_preserved=sum(x['sibling_preserved'] for x in roots),owned_synthetic_threads=len(threads),owned_synthetic_threads_alive=sum(x['alive'] for x in threads),owned_threads=threads,owned_children_started=0,forbidden_imports=forbidden,historical_runners_or_product_imported=bool(forbidden),functional_campaigns_executed=0,old_tests_reexecuted=False,quota_changed=False,default_refs=16384,original_P01_capacity='NOT_ESTABLISHED',numeric_reference_certificate=None,functional_capture_profile_created=False,functional_capture_authority_created=False,I96_authority_destination_launcher_absent=absent,publication_authorized=False,semantic_baseline=dict(SUPPORTS_BOUNDED=83,PARTIAL=1),D5_closed=False,global_review='OPEN',closure=False)
    output=json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2);p.size(len(output.encode()),manifest['limits']['raw_bytes'],'RAW_BUDGET');print(output);return 0 if valid else 1

if __name__=='__main__':raise SystemExit(main())
