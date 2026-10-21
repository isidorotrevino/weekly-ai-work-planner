# SPDX-License-Identifier: GPL-3.0-only
"""New disposable I8 V30 lab. Historical runners remain unchanged."""
import hashlib
import json
import os
import unittest

from .run_postgres_lab import ROOT, RecordingResult
from .run_v30_lab import V30Lab
from . import postgres_scenarios as baseline
from .review_scenarios import Review
from .v30_scenarios import Compatibility
from .mapping_scenarios import Mapping


class MappingLab(V30Lab):
    def start(self):
        super().start()
        self.sql('CREATE ROLE d5_apply_owner NOLOGIN NOINHERIT; CREATE ROLE d5_applier LOGIN NOINHERIT;')
        self.apply(ROOT/'migrations-d5-proposed/V33__synthetic_backlog_mapping.sql')
        assert self.catalog() == self.v30_catalog


def main():
    os.chdir(ROOT);os.umask(0o077)
    lab=MappingLab();result=None
    report=dict(status='FAIL_BOOTSTRAP',increment='D5-I8',D5_closed=False,real_data=False,deployment=False,
                workers_started=False,writes_synthetic_BACKLOG=True,operations_created=False)
    try:
        lab.start();baseline.LAB=lab
        for name in ['source_ingest/task_mapping.py','testing/D5/run_mapping_lab.py','testing/D5/mapping_scenarios.py',
                     'source_ingest/review.py','source_ingest/postgres.py','source_ingest/preview.py','source_ingest/compare.py','source_ingest/register.py',
                     'testing/D5/run_v30_lab.py','testing/D5/run_postgres_lab.py','testing/D5/run_review_lab.py',
                     'testing/D5/postgres_scenarios.py','testing/D5/review_scenarios.py','testing/D5/v30_scenarios.py']:
            lab.inputs[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(baseline.Persistence)])
        for cls,prefix in [(Review,'test_R'),(Compatibility,'test_T'),(Mapping,'test_M')]:
            loader=unittest.TestLoader();loader.testMethodPrefix=prefix
            suite.addTests(loader.loadTestsFromTestCase(cls))
        result=unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(suite)
        assert lab.catalog()==lab.v30_catalog
        counts=json.loads(lab.sql("SELECT jsonb_build_object('tasks',(SELECT count(*) FROM public.tasks),'operations',(SELECT count(*) FROM public.operations),'outbox',(SELECT count(*) FROM public.outbox_events));").stdout)
        assert counts['operations']==0 and counts['outbox']==0
        report.update(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,passed=result.passed,
                      failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],
                      postgresql=lab.version,image_id=lab.image,inputs=lab.inputs,concurrent_waiters=lab.waiter_counts,
                      v30_catalog_preserved=True,v30_catalog_sha256=lab.catalog_hash,final_counts=counts)
    finally:
        try:
            lab.cleanup();report['own_container_and_volume_removed']=True
        finally:
            (lab.work/'mapping-results.json').write_text(json.dumps(report,indent=2)+'\n')
            print('D5 I8 private evidence:',lab.work)
    return 0 if result and result.wasSuccessful() else 1


if __name__=='__main__':
    raise SystemExit(main())
