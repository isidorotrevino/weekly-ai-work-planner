# SPDX-License-Identifier: GPL-3.0-only
"""Only the I38 auditor campaign; never discovers testing/D5 or SQL tests."""
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
from testing.evidence_audit import test_evidence_audit as support


class Recorded(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.passed=[]; self.subcases=0

    def addSuccess(self,test):
        super().addSuccess(test); self.passed.append(test.id())

    def addSubTest(self,test,subtest,error):
        super().addSubTest(test,subtest,error); self.subcases+=1


def inputs():
    paths=['scripts/audit-d5-evidence.py','docs/validation/D5-EVIDENCE-REGISTRY.json',
           'testing/evidence_audit/test_evidence_audit.py',
           'testing/evidence_audit/run_audit_lab.py',
           'testing/evidence_audit/README.md',
           'docs/design/D5-I37-EVIDENCE-AUDIT-DESIGN.md',
           'docs/design/D5-I37-EVIDENCE-AUDIT-REVIEW.md']
    return {p:hashlib.sha256((support.ROOT/p).read_bytes()).hexdigest() for p in paths}


def main():
    support.OWNED.clear(); support.PROCESSES.clear(); support.OBSERVATIONS.clear()
    before=inputs(); started=time.monotonic()
    with patch.object(subprocess,'Popen',support.tracked_popen):
        suite=unittest.defaultTestLoader.loadTestsFromModule(support)
        result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=Recorded).run(suite)
        cli=subprocess.run([sys.executable,'-B','scripts/audit-d5-evidence.py'],cwd=support.ROOT,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=60)
    try:
        actual=json.loads(cli.stdout)
    except (ValueError,UnicodeError):
        actual={'audit_status':'INVALID','entries':[]}
    expected=cli.returncode==1 and actual.get('audit_status')=='FINDINGS'
    expected=expected and {e['id']:e['applicability'] for e in actual['entries']
                          if e['id'] in {'I34','I36'}}=={'I34':'STALE','I36':'CURRENT_RECORDED_SCOPE'}
    expected=expected and all(e['historical_integrity']=='MATCH' for e in actual['entries'])
    expected=expected and not cli.stderr
    clean=not any(Path(p).exists() for p in support.OWNED)
    clean=clean and all(p.poll() is not None for p in support.PROCESSES)
    unchanged=before==inputs()
    passed=sorted(set(result.passed))
    report=dict(schema='d5.i38-evidence-audit-campaign.v1',increment='D5-I38',
        status='PASS' if result.wasSuccessful() and expected and clean and unchanged else 'FAIL',
        mode='LOCAL_READ_ONLY_AND_SYNTHETIC_AUDITOR_FIXTURES',
        python=platform.python_version(),platform=platform.system(),tests_run=result.testsRun,
        passed=passed,new_tests=len(passed),functional_regression_tests_run=0,
        subcases_observed_not_additional_tests=result.subcases,
        case_test_map={f'EA{i:02}':[f'testing.evidence_audit.test_evidence_audit.EvidenceAuditTest.test_EA{i:02}'] for i in range(1,37)},
        failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],
        skipped=[t.id() for t,_ in result.skipped],
        inputs=before,inputs_unchanged_during_campaign=unchanged,
        audit_exit_code=cli.returncode,audit_findings_expected=expected,audit=actual,
        owned_roots_created=len(support.OWNED),owned_roots_remaining=sum(Path(p).exists() for p in support.OWNED),
        own_subprocesses_started=len(support.PROCESSES),
        own_subprocesses_alive=sum(p.poll() is None for p in support.PROCESSES),
        own_subprocesses_by_program={name:sum(Path(p.args[0]).name.startswith(name) for p in support.PROCESSES)
                                    for name in ('git','python')},
        own_subprocess_exitcodes={str(code):sum(p.returncode==code for p in support.PROCESSES)
                                 for code in sorted({p.returncode for p in support.PROCESSES},key=str)},
        fixture_audit_observations=support.OBSERVATIONS,cleanup_verified=clean,
        elapsed_seconds=round(time.monotonic()-started,3),
        functional_campaigns_reexecuted=False,SQL_D1_D2_D3_D4_reexecuted=False,
        remote_requests=0,operations=0,operational_attempts=0,quota_consumed=0,
        reservations_created=0,real_provider_access=False,credentials_used=False,
        operational_activation=False,migration_promotion=False,deployment=False,
        publication_authorized=False,D5_closed=False,D6_started=False,
        global_gaps_open=[f'G{i:02}' for i in range(1,8)],sufficiency='REVIEW_PENDING',
        local_I1_I20_accepted_milestone_unchanged=True,
        limit_tests='Reduced budgets explicitly used; not all full maxima or a performance benchmark')
    print(json.dumps(report,sort_keys=True,indent=2));return 0 if report['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
