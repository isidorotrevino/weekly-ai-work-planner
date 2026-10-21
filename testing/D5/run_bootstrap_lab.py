# SPDX-License-Identifier: GPL-3.0-only
"""I10: own V30+V31-V34 lab; original I4-I8 runners and evidence unchanged."""
import hashlib
import json
import os
import unittest

from .run_postgres_lab import ROOT, RecordingResult
from .run_mapping_lab import MappingLab
from . import postgres_scenarios as baseline
from .review_scenarios import Review
from .v30_scenarios import Compatibility
from .mapping_scenarios import Mapping
from .bootstrap_scenarios import Bootstrap


class BootstrapLab(MappingLab):
    def start(self):
        super().start()
        self.i8_functions=self.sql("SELECT jsonb_object_agg(p.oid::regprocedure::text,pg_get_functiondef(p.oid)) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='d5';").stdout
        self.apply(ROOT/'migrations-d5-proposed/V34__synthetic_initial_bootstrap.sql')
        assert self.catalog()==self.v30_catalog
        self.assert_i8_functions()

    def assert_i8_functions(self):
        before=json.loads(self.i8_functions)
        now=json.loads(self.sql("SELECT jsonb_object_agg(p.oid::regprocedure::text,pg_get_functiondef(p.oid)) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='d5';").stdout)
        assert all(now.get(k)==v for k,v in before.items())


def main():
    os.chdir(ROOT);os.umask(0o077)
    lab=BootstrapLab();result=None
    report=dict(status='FAIL_BOOTSTRAP',increment='D5-I10',D5_closed=False,real_data=False,deployment=False,
                workers_started=False,writes_synthetic_BACKLOG=True,operational_activation=False,
                transient_negative_operation_fixture='I8 M12 only; mandatory rollback, never executed')
    try:
        lab.start();baseline.LAB=lab
        paths=['source_ingest/bootstrap.py','testing/D5/bootstrap_scenarios.py','testing/D5/run_bootstrap_lab.py']
        paths += [p for p in json.loads((ROOT/'docs/validation/D5-I8-results.json').read_text())['inputs'] if p.endswith(('.py','.md'))]
        for name in paths:lab.inputs[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(baseline.Persistence)])
        for cls,prefix in [(Review,'test_R'),(Compatibility,'test_T'),(Mapping,'test_M'),(Bootstrap,'test_B')]:
            loader=unittest.TestLoader();loader.testMethodPrefix=prefix
            suite.addTests(loader.loadTestsFromTestCase(cls))
        result=unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(suite)
        assert lab.catalog()==lab.v30_catalog;lab.assert_i8_functions()
        tables={'tasks':'public.tasks','operations':'public.operations','outbox':'public.outbox_events',
                'deliveries':'d4.deliveries','reservations':'d2.reservations','plan_reservations':'d2.plan_reservations','attempts':'public.execution_attempts'}
        counts={name:int(lab.sql('SELECT count(*) FROM '+table+';').stdout) for name,table in tables.items()}
        assert all(value==0 for name,value in counts.items() if name!='tasks')
        assert lab.sql("SELECT count(*) FROM public.tasks WHERE status<>'BACKLOG';").stdout.strip()=='0'
        report.update(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,passed=result.passed,
                      failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],
                      postgresql=lab.version,image_id=lab.image,inputs=lab.inputs,concurrent_waiters=lab.waiter_counts,
                      v30_catalog_preserved=True,v30_catalog_sha256=lab.catalog_hash,i8_functions_preserved=True,final_counts=counts)
    finally:
        try:lab.cleanup();report['own_container_and_volume_removed']=True
        finally:
            (lab.work/'bootstrap-results.json').write_text(json.dumps(report,indent=2)+'\n')
            print('D5 I10 private evidence:',lab.work)
    return 0 if result and result.wasSuccessful() else 1


if __name__=='__main__':
    raise SystemExit(main())
