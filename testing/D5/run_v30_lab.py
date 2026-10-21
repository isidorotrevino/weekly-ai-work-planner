# SPDX-License-Identifier: GPL-3.0-only
"""Fresh V1-V30 -> V31/V32 disposable SQL compatibility lab, without task creation."""
import hashlib
import json
import os
import re
import subprocess
import unittest
import uuid

from .run_postgres_lab import ROOT, RecordingResult
from .run_review_lab import ReviewLab
from . import postgres_scenarios as baseline
from .review_scenarios import Review
from .v30_scenarios import Compatibility
from source_ingest.postgres import sql_text


class V30Lab(ReviewLab):
    def apply(self,path):
        text=path.read_text()
        if path.parent.name!='migrations-d5-proposed':
            text='BEGIN;\n'+text+'\nCOMMIT;'
        try:
            self.sql(text)
        except subprocess.CalledProcessError as ex:
            (self.work/'bootstrap-error.txt').write_text(str(path.relative_to(ROOT))+'\n'+ex.stderr)
            raise
        self.inputs[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()

    def catalog(self):
        # Exact old function bodies, owners/ACL/config, plus non-FK trigger definitions.
        return json.loads(self.sql("""SELECT jsonb_build_object(
          'functions',(SELECT jsonb_object_agg(p.oid::regprocedure::text,jsonb_build_object(
            'body',pg_get_functiondef(p.oid),'owner',pg_get_userbyid(p.proowner),'acl',p.proacl::text,'config',p.proconfig))
            FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
            WHERE n.nspname IN ('public','d2','d3','d4') AND p.prokind='f'),
          'triggers',(SELECT jsonb_object_agg(t.tgrelid::regclass::text||'.'||t.tgname,pg_get_triggerdef(t.oid))
            FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE NOT t.tgisinternal AND n.nspname IN ('public','d2','d3','d4')));""").stdout)

    def start(self):
        self.docker('run','--pull','never','-d','--name',self.container,'--network','none',
                    '--label','wap.d5.disposable=true','--label','codex.project=weekly-ai-work-planner',
                    '--mount','type=volume,destination=/var/lib/postgresql/data',
                    '-e','POSTGRES_USER=d5_lab_admin','-e','POSTGRES_DB=d5_lab',
                    '-e','POSTGRES_HOST_AUTH_METHOD=trust','postgres:16-bookworm','postgres','-c','listen_addresses=')
        self.ready()
        self.wait_for(lambda:'PostgreSQL init process complete' in self.docker('logs',self.container).stdout)
        self.ready()
        meta=json.loads(self.docker('inspect',self.container).stdout)[0]
        self.volumes=[m['Name'] for m in meta['Mounts'] if m['Type']=='volume']
        assert len(self.volumes)==1 and not meta['HostConfig']['PortBindings']
        self.image=meta['Image'];self.version=self.sql('SHOW server_version;').stdout.strip()
        self.sql('CREATE ROLE d5_owner NOLOGIN NOINHERIT; CREATE ROLE d5_writer LOGIN NOINHERIT; CREATE ROLE d5_reader LOGIN NOINHERIT; CREATE ROLE d5_reviewer LOGIN NOINHERIT;')
        locations=['migrations','migrations-proposed','migrations-d3-proposed','migrations-d3-dispatch-proposed',
                   'migrations-d3-coordinator-proposed','migrations-d3-review-proposed','migrations-d4-proposed']
        files=sorted([p for location in locations for p in (ROOT/location).glob('V*.sql')],key=lambda p:int(re.match(r'V(\d+)',p.name)[1]))
        assert [int(re.match(r'V(\d+)',p.name)[1]) for p in files]==list(range(1,31))
        self.inputs={}
        for path in files:
            self.apply(path)
        self.v30_catalog=self.catalog()
        for name in ['V31__local_source_observations.sql','V32__comparison_review_simulation.sql']:
            self.apply(ROOT/'migrations-d5-proposed'/name)
        assert self.catalog()==self.v30_catalog
        self.seed_controls()
        self.catalog_hash=hashlib.sha256(json.dumps(self.v30_catalog,sort_keys=True).encode()).hexdigest()

    def seed_controls(self):
        # Owner-only non-task controls. Offline, disabled, no heartbeat or execution proof.
        self.worker,self.resource,self.account=[str(uuid.uuid4()) for _ in range(3)]
        self.sql(f"""INSERT INTO public.workers(id,worker_key,host_name,state)
          VALUES('{self.worker}','{self.worker}','synthetic.invalid','OFFLINE');
          INSERT INTO public.resources(id,resource_key,worker_id,provider,subscription,enabled)
          VALUES('{self.resource}','{self.resource}','{self.worker}','SYNTHETIC','none',false);
          INSERT INTO d2.accounts(id,resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity)
          VALUES('{self.account}','{self.resource}','synthetic','OPERATIONS','WEEK','synthetic-window',
            '2026-10-19T00:00:00Z','2026-10-26T00:00:00Z','D5 compatibility fixture only',1,100);
          INSERT INTO d4.worker_catalog(worker_id,enabled) VALUES('{self.worker}',false);""")
        request={'action':'PROFILE','reason':'D5 compatibility fixture, no task activation','epoch_id':str(uuid.uuid4()),
                 'calibration_epoch':'synthetic-v30','policy':{'schema_version':'d3.snapshot.v1','timezone':'Europe/Madrid',
                 'max_operations':10,'max_edges':20,'max_candidates':20,'max_compute_ms':5000}}
        self.sql("SELECT d3.configure('"+str(uuid.uuid4())+"',"+sql_text(json.dumps(request))+'::jsonb);')
        assert self.sql('SELECT count(*) FROM public.tasks;').stdout.strip()=='0'
        assert self.sql('SELECT count(*) FROM public.operations;').stdout.strip()=='0'

    def protected_state(self,include_sources=True):
        excluded="c.relname<>'source_revisions'" if include_sources else "c.relname NOT IN ('source_documents','source_revisions')"
        tables=self.sql("SELECT quote_ident(n.nspname)||'.'||quote_ident(c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='r' AND n.nspname IN ('public','d2','d3','d4') AND "+excluded+' ORDER BY 1;').stdout.splitlines()
        statements=["SELECT '"+name+"' name,coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text COLLATE \"C\"),'[]'::jsonb) rows FROM "+name+' t' for name in tables]
        return json.loads(self.sql('SELECT jsonb_object_agg(name,rows) FROM ('+' UNION ALL '.join(statements)+') s;').stdout)


def main():
    os.chdir(ROOT);os.umask(0o077)
    lab=V30Lab();result=None
    report={'status':'FAIL_BOOTSTRAP','increment':'D5-I6','target':'V1-V30 then V31/V32','D5_closed':False,
            'writes_D2_tasks':False,'deployment':False,'real_data':False,'workers_started':False}
    try:
        lab.start();baseline.LAB=lab
        loader=unittest.TestLoader();loader.testMethodPrefix='test_R'
        integration=unittest.TestLoader();integration.testMethodPrefix='test_T'
        suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(baseline.Persistence),
                                 loader.loadTestsFromTestCase(Review),integration.loadTestsFromTestCase(Compatibility)])
        result=unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(suite)
        for name in ['testing/D5/run_v30_lab.py','testing/D5/v30_scenarios.py','testing/D5/run_postgres_lab.py',
                     'testing/D5/run_review_lab.py','testing/D5/postgres_scenarios.py','testing/D5/review_scenarios.py',
                     'source_ingest/postgres.py','source_ingest/review.py','source_ingest/preview.py','source_ingest/compare.py','source_ingest/register.py']:
            lab.inputs[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        assert lab.catalog()==lab.v30_catalog
        assert lab.sql('SELECT count(*) FROM public.tasks;').stdout.strip()=='0'
        assert lab.sql('SELECT count(*) FROM public.operations;').stdout.strip()=='0'
        report.update(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,passed=result.passed,
                      failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],
                      postgresql=lab.version,image_id=lab.image,inputs=lab.inputs,concurrent_waiters=lab.waiter_counts,
                      v30_catalog_preserved=True,v30_catalog_sha256=lab.catalog_hash,task_rows=0,operation_rows=0)
    finally:
        try:
            lab.cleanup();report['own_container_and_volume_removed']=True
        finally:
            (lab.work/'v30-results.json').write_text(json.dumps(report,indent=2)+'\n')
            print('D5 I6 private evidence:',lab.work)
    return 0 if result and result.wasSuccessful() else 1


if __name__=='__main__':
    raise SystemExit(main())
