# SPDX-License-Identifier: GPL-3.0-only
"""Separate disposable V11+V31+V32 lab; preserves the I4 runner and its evidence."""
import concurrent.futures
import hashlib
import json
import os
import unittest

from .run_postgres_lab import Lab, ROOT, RecordingResult
from . import postgres_scenarios as baseline
from .review_scenarios import Review


class ReviewLab(Lab):
    def start(self):
        super().start()
        self.sql('CREATE ROLE d5_reviewer LOGIN NOINHERIT;')
        path=ROOT/'migrations-d5-proposed/V32__comparison_review_simulation.sql'
        try:
            self.sql(path.read_text())
        except __import__('subprocess').CalledProcessError as ex:
            (self.work/'bootstrap-error.txt').write_text(ex.stderr)
            raise
        self.inputs[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        assert self.sql('SELECT count(*) FROM d5.comparisons;').stdout.strip()=='0'

    def concurrent(self,statements,role='d5_writer'):
        blocker=self.session('BEGIN; SELECT pg_advisory_xact_lock(742005); SELECT pg_sleep(60); ROLLBACK;','d5_barrier')
        self.wait_for(lambda:self.active('d5_barrier','PgSleep')==1)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(self.sql,s,role) for s in statements]
            try:
                self.wait_for(lambda:int(self.sql("SELECT count(*) FROM pg_stat_activity WHERE usename='"+role+"' AND wait_event='advisory';").stdout.strip())==2)
                self.waiter_counts.append(2)
            finally:
                self.terminate('d5_barrier')
            results=[json.loads(f.result(timeout=30).stdout) for f in futures]
        blocker.communicate(timeout=5)
        return results


def main():
    os.chdir(ROOT);os.umask(0o077)
    lab=ReviewLab();result=None
    report={'status':'FAIL_BOOTSTRAP','increment':'D5-I5','D5_closed':False,'writes_D2_tasks':False,'deployment':False,'real_data':False}
    try:
        lab.start();baseline.LAB=lab
        loader=unittest.TestLoader();loader.testMethodPrefix='test_R'
        suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(baseline.Persistence),loader.loadTestsFromTestCase(Review)])
        result=unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(suite)
        for name in ['source_ingest/review.py','testing/D5/review_scenarios.py','testing/D5/run_review_lab.py']:
            lab.inputs[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        report.update(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,passed=result.passed,
                      failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],
                      postgresql=lab.version,image_id=lab.image,inputs=lab.inputs,concurrent_waiters=lab.waiter_counts)
    finally:
        try:
            lab.cleanup();report['own_container_and_volume_removed']=True
        finally:
            (lab.work/'review-results.json').write_text(json.dumps(report,indent=2)+'\n')
            print('D5 I5 private evidence:',lab.work)
    return 0 if result and result.wasSuccessful() else 1


if __name__=='__main__':
    raise SystemExit(main())
