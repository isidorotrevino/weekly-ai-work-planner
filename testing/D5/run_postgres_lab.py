# SPDX-License-Identifier: GPL-3.0-only
"""Run D5-only synthetic PostgreSQL tests; always remove own container and volume."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import unittest
import uuid

from . import postgres_scenarios as cases
from source_ingest.postgres import LabClient

ROOT = Path(__file__).resolve().parents[2]


class Lab:
    def __init__(self):
        self.container = 'd5-pg-' + uuid.uuid4().hex[:16]
        self.work = ROOT / 'work/d5/postgres' / self.container
        self.work.mkdir(parents=True, mode=0o700)
        self.sessions = []
        self.waiter_counts = []

    def docker(self, *args, **kwargs):
        return subprocess.run(['docker', *args], capture_output=True, text=True, check=True, timeout=90, **kwargs)

    def command(self, role='d5_lab_admin', app=None):
        return ['docker','exec','-i',*(['-e','PGAPPNAME='+app] if app else []), self.container,
                'psql','-X','-qAt','-U',role,'-d','d5_lab','-v','ON_ERROR_STOP=1']

    def sql(self, sql, role='d5_lab_admin', check=True):
        return subprocess.run(self.command(role), input=sql, capture_output=True, text=True, check=check, timeout=90)

    def ready(self):
        for _ in range(100):
            run = subprocess.run(['docker','exec',self.container,'pg_isready','-U','d5_lab_admin','-d','d5_lab'], capture_output=True)
            if run.returncode == 0:
                # pg_isready can briefly see the temporary bootstrap server.
                r = self.sql('SELECT 1;', check=False)
                if r.returncode == 0:
                    return
            time.sleep(.1)
        raise RuntimeError('D5 PostgreSQL did not become ready')

    def start(self):
        self.docker('run','--pull','never','-d','--name',self.container,'--network','none',
                    '--label','wap.d5.disposable=true','--label','codex.project=weekly-ai-work-planner',
                    '--mount','type=volume,destination=/var/lib/postgresql/data',
                    '-e','POSTGRES_USER=d5_lab_admin','-e','POSTGRES_DB=d5_lab',
                    '-e','POSTGRES_HOST_AUTH_METHOD=trust','postgres:16-bookworm',
                    'postgres','-c',"listen_addresses=")
        self.ready()
        # Wait for final server after image init (a real query must survive a restart).
        for _ in range(100):
            logs = self.docker('logs',self.container)
            if 'PostgreSQL init process complete' in logs.stdout:
                break
            time.sleep(.1)
        self.ready()
        self.sql('CREATE ROLE d5_owner NOLOGIN NOINHERIT; CREATE ROLE d5_writer LOGIN NOINHERIT; CREATE ROLE d5_reader LOGIN NOINHERIT;')
        files = sorted(list((ROOT/'migrations').glob('V*.sql')) + list((ROOT/'migrations-proposed').glob('V*.sql')),
                       key=lambda p:int(re.match(r'V(\d+)',p.name)[1]))
        assert [int(re.match(r'V(\d+)',p.name)[1]) for p in files] == list(range(1,12))
        self.inputs = {}
        for path in files + [ROOT/'migrations-d5-proposed/V31__local_source_observations.sql']:
            sql = path.read_text()
            if path.parent.name != 'migrations-d5-proposed':
                sql = 'BEGIN;\n' + sql + '\nCOMMIT;'
            try:
                self.sql(sql)
            except subprocess.CalledProcessError as ex:
                (self.work/'bootstrap-error.txt').write_text(str(path.relative_to(ROOT))+'\n'+ex.stderr)
                raise
            self.inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        assert self.sql('SELECT count(*) FROM d5.source_registrations;').stdout.strip() == '0'
        self.version = self.sql('SHOW server_version;').stdout.strip()
        meta = json.loads(self.docker('inspect',self.container).stdout)[0]
        self.image = meta['Image']
        self.volumes = [m['Name'] for m in meta['Mounts'] if m['Type']=='volume']
        assert len(self.volumes) == 1 and not meta['HostConfig']['PortBindings']

    def restart(self):
        self.docker('restart',self.container)
        self.ready()

    def active(self, app, wait=None):
        condition = "application_name='"+app+"'"
        if wait:
            condition += " AND wait_event='"+wait+"'"
        return int(self.sql('SELECT count(*) FROM pg_stat_activity WHERE '+condition+';').stdout.strip())

    def wait_for(self, predicate):
        end = time.monotonic()+15
        while time.monotonic()<end:
            if predicate():
                return
            time.sleep(.05)
        raise RuntimeError('Concurrency/recovery synchronization timed out')

    def session(self, sql, app):
        p = subprocess.Popen(self.command(app=app), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        p.stdin.write(sql)
        p.stdin.close()
        p.stdin = None
        self.sessions.append(p)
        return p

    def terminate(self, app):
        self.sql("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name='"+app+"';")

    def concurrent(self, statements):
        blocker = self.session("BEGIN; SELECT pg_advisory_xact_lock(742005); SELECT pg_sleep(60); ROLLBACK;", 'd5_barrier')
        self.wait_for(lambda:self.active('d5_barrier','PgSleep') == 1)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            def submit(statement):
                # Reader checks use the API; raw SQL here intentionally bypasses adapter only for concurrency control.
                return json.loads(self.sql(statement,role='d5_writer').stdout)
            futures = [pool.submit(submit,s) for s in statements]
            try:
                self.wait_for(lambda:int(self.sql("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_writer' AND wait_event='advisory';").stdout.strip()) == 2)
                self.waiter_counts.append(2)
            finally:
                self.terminate('d5_barrier')
            results = [f.result(timeout=30) for f in futures]
        blocker.communicate(timeout=5)
        return results

    def abort_after(self, statement):
        p = self.session('BEGIN;'+statement+'SELECT pg_sleep(60); COMMIT;', 'd5_abort')
        self.wait_for(lambda:self.active('d5_abort','PgSleep') == 1)
        self.terminate('d5_abort')
        p.communicate(timeout=5)

    def protected_state(self):
        tables = self.sql("SELECT quote_ident(n.nspname)||'.'||quote_ident(c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='r' AND n.nspname IN ('public','d2') AND c.relname<>'source_revisions' ORDER BY 1;").stdout.splitlines()
        return {t:self.sql("SELECT coalesce(jsonb_agg(v ORDER BY v::text),'[]'::jsonb) FROM (SELECT to_jsonb(x) v FROM "+t+" x) q;").stdout.strip() for t in tables}

    def cleanup(self):
        # Names generated here, never global prune/reset or another Compose project.
        if self.sessions:
            self.terminate('d5_barrier')
            self.terminate('d5_abort')
        for p in self.sessions:
            if p.poll() is None:
                p.terminate()
        run = subprocess.run(['docker','logs',self.container], capture_output=True,text=True)
        (self.work/'postgres.log').write_text(run.stdout+run.stderr)
        run = subprocess.run(['docker','rm','-fv',self.container], capture_output=True,text=True)
        (self.work/'cleanup.log').write_text(run.stdout+run.stderr)
        if run.returncode:
            raise RuntimeError('D5 container cleanup failed; see private evidence')
        for volume in getattr(self,'volumes',[]):
            check = subprocess.run(['docker','volume','inspect',volume],capture_output=True,text=True)
            if check.returncode == 0:
                raise RuntimeError('Own anonymous D5 volume remains after cleanup')
        self.cleaned = True


class RecordingResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.passed = []

    def addSuccess(self,test):
        self.passed.append(test.id())
        super().addSuccess(test)


def main():
    os.chdir(ROOT)
    os.umask(0o077)
    lab = Lab()
    report = {'status':'FAIL_BOOTSTRAP','scope':'D5 synthetic disposable lab only','D5_closed':False,'deployment':False,'real_data':False}
    result = None
    try:
        lab.start()
        cases.LAB = lab
        result = unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(cases.Persistence))
        report.update(status='PASS' if result.wasSuccessful() else 'FAIL', tests_run=result.testsRun,
                      passed=result.passed, failures=[t.id() for t,_ in result.failures], errors=[t.id() for t,_ in result.errors],
                      postgresql=lab.version,image_id=lab.image,inputs=lab.inputs,concurrent_waiters=lab.waiter_counts)
    finally:
        try:
            lab.cleanup()
            report['own_container_and_volume_removed'] = True
        finally:
            (lab.work/'results.json').write_text(json.dumps(report,indent=2)+'\n')
            print('D5 private evidence:',lab.work)
    return 0 if result and result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
