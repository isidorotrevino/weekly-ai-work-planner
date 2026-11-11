# SPDX-License-Identifier: GPL-3.0-only
"""Explicit future component entrypoint. I122 wrote this source; NOT RUN."""
import json
import sys
import time
import unittest


def main(argv=None):
    args=sys.argv[1:] if argv is None else argv
    if args!=['--components-only']:
        print(json.dumps(dict(schema='d5.joint-component-plan.v2',status='NOT_RUN_EXPLICIT_COMPONENT_DECISION_REQUIRED',functional_campaigns_executed=0)));return 2
    before=set(sys.modules);started=time.monotonic()
    from .test_joint_capture import R2CandidateTests
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(R2CandidateTests)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(suite)
    forbidden=sorted(n for n in sys.modules if n=='source_ingest' or n.startswith('source_ingest.') or n.startswith('testing.D5.'))
    elapsed_ms=int((time.monotonic()-started)*1000)
    status='PASS' if result.wasSuccessful() and result.testsRun==10 and not forbidden and 0<=elapsed_ms<=300000 else 'FAIL'
    print(json.dumps(dict(schema='d5.joint-component-raw.v2',source_revision='I122-CANDIDATE-01',status=status,tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),functional_campaigns_executed=0,product_or_runner_imported=bool(forbidden),forbidden_imports=forbidden,elapsed_milliseconds=elapsed_ms,new_module_count=len(set(sys.modules)-before),closure=False,D5_closed=False),separators=(',',':'),allow_nan=False))
    return 0 if status=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
