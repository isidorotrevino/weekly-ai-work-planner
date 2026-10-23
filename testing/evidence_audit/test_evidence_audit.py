# SPDX-License-Identifier: GPL-3.0-only
"""Independent synthetic packets and local repos for EA01-EA36; no T/R execution."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).absolute().parents[2]
spec = importlib.util.spec_from_file_location('evidence_auditor', ROOT/'scripts/audit-d5-evidence.py')
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
OWNED = []
PROCESSES = []
OBSERVATIONS = []
REAL_POPEN = subprocess.Popen


def tracked_popen(*args, **kwargs):
    p = REAL_POPEN(*args, **kwargs)
    PROCESSES.append(p)
    return p


def digest(b):
    return hashlib.sha256(b).hexdigest()


def write(root, name, data):
    p = root/name; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data if isinstance(data, bytes) else data.encode())


def git(root, *args):
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    for key in tuple(env):
        if key.startswith('GIT_') and key not in {'GIT_CONFIG_NOSYSTEM', 'GIT_CONFIG_GLOBAL'}:
            env.pop(key)
    return subprocess.run(['git', *args], cwd=root, env=env, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()


class Packet:
    def __init__(self, root):
        self.root = root; root.mkdir()
        self.inputs = {'source_ingest/model.py': b'# fixture model\n',
                       'testing/D5/test_model.py': b'# fixture test, never imported\n',
                       'testing/D5/fixtures/source.md': b'# fixture source\n',
                       'docs/design/D5-I35-CONTRACT.md': b'# fixture contract\n'}
        for p, b in self.inputs.items():
            write(root, p, b)
        self.path = 'docs/validation/D5-I36-results.json'
        ids = [f'test_durable_relational.Fixture.test_DR{i:02}' for i in range(1,41)]
        self.doc = dict(schema='d5.synthetic-auditor-test.v1', passed=ids,
            tests_run=40, groups={'test_durable_relational': ids.copy()},
            new_tests=40, regression_tests=0, failures=[], errors=[], skipped=[],
            status='PASS', inputs={p:digest(b) for p,b in self.inputs.items()},
            documentary_inputs={}, python=platform.python_version(), platform=platform.system(),
            case_test_map={f'DR{i:02}':[ids[i-1]] for i in range(1,41)},
            UI_test_map={'UI25':[ids[0]], 'UI34':[ids[0]]}, cleanup_verified=True,
            owned_children_started=2, owned_children_alive=0, owned_child_exitcodes=[0,-9],
            owned_children_normal=1, owned_children_SIGKILL=1, owned_roots_created=1,
            owned_roots_remaining=0, D5_closed=False, publication_authorized=False,
            operational_activation=False, deployment=False, migration_promotion=False,
            real_provider_access=False, credentials_used=False, D6_started=False,
            remote_requests=0, persistent_D2_writes=0, quota_consumed=0, reservations_created=0,
            global_gaps_open=[f'G{i:02}' for i in range(1,8)], docs_export_not_run=True)
        self.raw_bytes = None

    def seal(self):
        write(self.root,self.path, self.raw_bytes if self.raw_bytes is not None else json.dumps(self.doc))
        if not (self.root/'.git').exists():
            git(self.root,'init','-q')
            git(self.root,'config','user.name','Synthetic audit fixture')
            git(self.root,'config','user.email','fixture@example.test')
        git(self.root,'add','.')
        git(self.root,'commit','-qm','Synthetic evidence packet','--allow-empty')
        commit=git(self.root,'rev-parse','HEAD')
        e=dict(id='I36',kind='campaign',path=self.path,commit=commit,
               sha256=digest((self.root/self.path).read_bytes()),schema=self.doc['schema'],
               fields=sorted(self.doc),hash_fields={'inputs':'runtime','documentary_inputs':'documentary'},
               references=[],dependency_commit=commit,
               dependency_paths=sorted(set(self.doc['inputs'])|set(self.doc['documentary_inputs'])),
               target='Synthetic audit fixture only', maps={
                   'case_test_map':[f'DR{i:02}' for i in range(1,41)], 'UI_test_map':['UI25','UI34']},
               new_group='test_durable_relational')
        self.registry=dict(schema='d5.evidence-registry.v1',entries=[e],UI_obligations={
            f'UI{i:02}':dict(GI='GI33',mode='R' if i in {25,34} else 'M',obligation='Fixture obligation')
            for i in range(1,41)},limitations=['Synthetic packet only'])
        return self.registry


class EvidenceAuditTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='d5-evidence-test-')
        OWNED.append(self.temp.name);self.addCleanup(self.temp.cleanup)
        self.parent=Path(self.temp.name)
        (self.parent/'sentinel').write_bytes(b'sibling sentinel')
        self.counter=0

    def packet(self):
        self.counter+=1
        return Packet(self.parent/f'repo-{self.counter}')

    def run_packet(self,p,**kwargs):
        result,code=A.audit(p.root,p.registry,**kwargs)
        OBSERVATIONS.append(dict(case=self.id().rsplit('.',1)[1],exit_code=code,
                                 audit_status=result['audit_status']))
        return result,code

    def valid(self):
        p=self.packet();p.seal();return p

    def state(self,result):
        return result['entries'][0]

    def codes(self,result):
        return {x['code'] for x in result['findings']}

    def test_EA01(self):
        p=self.valid();r,c=self.run_packet(p)
        self.assertEqual(c,0);self.assertEqual(r['audit_status'],'CONSISTENT')
        self.assertEqual(self.state(r)['applicability'],'CURRENT_RECORDED_SCOPE')
        self.assertEqual(self.state(r)['historical_integrity'],'MATCH')
        self.assertEqual(r['sufficiency'],'REVIEW_PENDING');self.assertFalse(r['D5_closed'])

    def test_EA02(self):
        p=self.valid();p.registry['entries'][0]['sha256']='0'*64
        r,c=self.run_packet(p);self.assertEqual(c,2)
        self.assertEqual(self.state(r)['historical_integrity'],'MISMATCH')

    def test_EA03(self):
        p=self.valid();p.registry['entries'][0]['commit']='0'*40
        r,c=self.run_packet(p);self.assertEqual(c,1)
        self.assertEqual(self.state(r)['historical_integrity'],'UNAVAILABLE')
        p=self.valid();p.registry['entries'][0]['path']='docs/validation/missing.json'
        r,c=self.run_packet(p);self.assertEqual(c,1)
        self.assertIn('HISTORICAL_PATH_UNAVAILABLE',self.codes(r))

    def test_EA04(self):
        p=self.valid();write(p.root,'source_ingest/model.py',b'# changed\n')
        r,c=self.run_packet(p);self.assertEqual(c,1)
        self.assertEqual(self.state(r)['historical_integrity'],'MATCH')
        self.assertEqual(self.state(r)['recorded_files_now']['runtime'],'CHANGED')
        self.assertEqual(self.state(r)['applicability'],'STALE')

    def test_EA05(self):
        p=self.valid();(p.root/'source_ingest/model.py').unlink()
        r,c=self.run_packet(p);self.assertEqual(c,1)
        self.assertEqual(self.state(r)['recorded_files_now']['runtime'],'MISSING')
        self.assertEqual(self.state(r)['discovery_now'],'REMOVED')

    def test_EA06(self):
        for name in ['source_ingest/new.py','testing/D5/new.py','testing/D5/fixtures/new.md','docs/design/D5-I35-NEW.md']:
            with self.subTest(path=name):
                p=self.valid();write(p.root,name,b'fixture')
                r,c=self.run_packet(p);self.assertEqual(c,1)
                self.assertEqual(self.state(r)['discovery_added'],[name])
                self.assertEqual(self.state(r)['recorded_files_now']['runtime'],'MATCH')
        self.assertEqual(A.selected(['docs/design/D5-I33-NEW.md'],'I34'),{'docs/design/D5-I33-NEW.md'})
        self.assertEqual(A.selected(['docs/design/D5-I35-NEW.md'],'I34'),set())

    def test_EA07(self):
        p=self.packet();write(p.root,'docs/README.md',b'old')
        p.doc['documentary_inputs']={'docs/README.md':digest(b'old')};p.seal()
        write(p.root,'docs/README.md',b'new')
        r,c=self.run_packet(p);self.assertEqual(c,1)
        self.assertEqual(self.state(r)['recorded_files_now']['documentary'],'CHANGED')
        self.assertEqual(self.state(r)['applicability'],'CURRENT_RECORDED_SCOPE')

    def test_EA08(self):
        p=self.valid()
        for name in ['scripts/audit-d5-evidence.py','testing/evidence_audit/test_evidence_audit.py',A.REGISTRY]:
            write(p.root,name,b'new observer')
        r,c=self.run_packet(p);self.assertEqual(c,0)
        write(p.root,'testing/D5/audit_observer.py',b'new observer')
        r,c=self.run_packet(p);self.assertEqual(c,1)

    def test_EA09(self):
        p=self.packet();write(p.root,'testing/D5/run_relational_durable_lab.py',b'# old rule')
        p.doc['inputs']['testing/D5/run_relational_durable_lab.py']=digest(b'# old rule');p.seal()
        write(p.root,'testing/D5/run_relational_durable_lab.py',b'raise RuntimeError("never execute")')
        r,c=self.run_packet(p);self.assertEqual(c,1);self.assertEqual(self.state(r)['applicability'],'STALE')

    def test_EA10(self):
        for key,value,context,app in [('python','0.0.0','DIFFERENT','STALE'),('platform','Other','DIFFERENT','STALE'),('python',None,'NOT_RECORDED','UNDETERMINED')]:
            with self.subTest(field=key,value=value):
                p=self.packet();p.doc[key]=value;p.seal();r,c=self.run_packet(p)
                self.assertEqual(c,1);self.assertEqual(self.state(r)['runtime_context'],context)
                self.assertEqual(self.state(r)['applicability'],app)

    def test_EA11(self):
        p=self.valid();r,c=self.run_packet(p)
        self.assertEqual(c,0)
        self.assertEqual(r['external_capabilities'],'NOT_RECORDED')
        self.assertEqual(self.state(r)['embedded_configuration'],'BOUND_TO_RECORDED_BYTES_ONLY')

    def test_EA12(self):
        p=self.packet();p.doc['passed'].append('legacy.Fixture.test_old')
        p.doc['groups']['legacy']=['legacy.Fixture.test_old'];p.doc['tests_run']=41;p.doc['regression_tests']=1;p.seal()
        r,c=self.run_packet(p);self.assertEqual(c,0)
        self.assertEqual(self.state(r)['declared_tests'],41);self.assertEqual(self.state(r)['declared_regressions'],1)

    def test_EA13(self):
        for field in ['duplicate','empty','count','group']:
            with self.subTest(field=field):
                p=self.packet()
                if field=='duplicate':p.doc['passed'].append(p.doc['passed'][0])
                elif field=='empty':p.doc['passed'][0]=''
                elif field=='count':p.doc['tests_run']=True
                else:p.doc['groups']['other']=[p.doc['passed'][0]]
                p.seal();r,c=self.run_packet(p);self.assertEqual(c,2)

    def test_EA14(self):
        for status in ['PASS','FAIL']:
            p=self.packet();p.doc['errors']=['failed.Fixture.test_failure'];p.doc['tests_run']=41;p.doc['status']=status;p.seal()
            r,c=self.run_packet(p);self.assertEqual(c,2 if status=='PASS' else 0)
            if status=='FAIL':self.assertEqual(self.state(r)['declared_result'],'FAIL')

    def test_EA15(self):
        for change in ['missing','extra','empty','not_pass']:
            p=self.packet()
            if change=='missing':del p.doc['case_test_map']['DR01']
            elif change=='extra':p.doc['case_test_map']['DR99']=[p.doc['passed'][0]]
            elif change=='empty':p.doc['case_test_map']['DR01']=[]
            else:p.doc['case_test_map']['DR01']=['never.Executed.test_missing']
            p.seal();r,c=self.run_packet(p);self.assertEqual(c,2)

    def test_EA16(self):
        p=self.valid();r,c=self.run_packet(p);self.assertEqual(c,0)
        mapped=[x for x in r['UI_inventory'] if x['declared_sources']]
        self.assertEqual([x['id'] for x in mapped],['UI25','UI34'])
        self.assertEqual(self.state(r)['declared_tests'],40)

    def test_EA17(self):
        p=self.valid();r,c=self.run_packet(p)
        self.assertEqual(len(r['UI_inventory']),40)
        self.assertTrue(all(x['evidence']=='NOT_RECORDED' for x in r['UI_inventory'] if x['id'] not in {'UI25','UI34'}))
        self.assertTrue(all(x['sufficiency']=='REVIEW_PENDING' for x in r['UI_inventory']))
        self.assertEqual(r['real_evidence_criteria_not_run'],7)
        actual,_=A.audit(ROOT)
        self.assertEqual(sum(bool(x['declared_sources']) for x in actual['UI_inventory']),40)
        rel=next(x for x in actual['UI_inventory'] if x['id']=='UI25')
        self.assertEqual([x['campaign'] for x in rel['declared_sources']],['I36'])

    def test_EA18(self):
        p=self.valid();e=copy.deepcopy(p.registry['entries'][0]);e['id']='SECOND'
        # Campaign identity must be an explicit supported adapter, not a guessed runner.
        p.registry['entries'].append(e)
        r,c=self.run_packet(p);self.assertEqual(c,2)
        q=ROOT/'docs/validation/D5-EVIDENCE-REGISTRY.json'
        registry=json.loads(q.read_text());r,c=A.audit(ROOT,registry)
        self.assertIn(dict(left='I34',right='I36',shared_test_ids=281,totals_must_not_be_added=True),r['campaign_intersections'])
        self.assertNotIn('tests_total',r)

    def test_EA19(self):
        registry=json.loads((ROOT/A.REGISTRY).read_text());r,c=A.audit(ROOT,registry)
        for id in ['D3','D4','A52']:
            e=next(x for x in r['entries'] if x['id']==id)
            self.assertEqual(e['historical_integrity'],'MATCH')
            self.assertEqual(e['declared_execution'],'HISTORICAL_NOT_RERUN')
        paths=next(x for x in r['entries'] if x['id']=='A52')['preservation_paths']
        self.assertIn('docs/design/D1-architecture-baseline.md',paths)
        self.assertIn('docs/design/D2.9-approved.md',paths)

    def test_EA20(self):
        p=self.packet();sql='migrations-fixture/V1__fixture.sql';write(p.root,sql,b'-- inert SQL')
        p.doc['inputs'][sql]=digest(b'-- inert SQL');p.seal()
        e=p.registry['entries'][0];e['kind']='preserved';e['maps']={}
        e['hash_fields']['inputs']='preserved';e['target']='Historical SQL fixture only'
        write(p.root,sql,b'-- changed inert SQL')
        r,c=self.run_packet(p);self.assertEqual(c,1)
        self.assertEqual(self.state(r)['recorded_files_now']['preserved'],'CHANGED')
        self.assertEqual(self.state(r)['declared_execution'],'HISTORICAL_NOT_RERUN')
        self.assertIn(sql,[x.get('path') for x in r['findings']])
        p.registry['entries'][0]['dependency_paths'].append('docs/missing.md')
        r,c=self.run_packet(p);self.assertEqual(c,2)
        self.assertIn('DEPENDENCY_SET_MISMATCH',self.codes(r))

    def test_EA21(self):
        p=self.valid();r,c=self.run_packet(p)
        self.assertEqual(r['D1_D2_preservation'],'EXPLICIT_REFERENCES_ONLY_NOT_EXHAUSTIVE')
        self.assertEqual(r['D1_D2_target_extensions'],'NOT_RECORDED')
        self.assertFalse(r['SQL_D1_D2_D3_D4_reexecuted'])

    def test_EA22(self):
        p=self.valid();r,c=self.run_packet(p)
        self.assertEqual(c,0);self.assertEqual(self.state(r)['raw_binding'],'NOT_RECORDED')
        self.assertEqual(r['raw_binding_counts']['NOT_RECORDED'],1)

    def test_EA23(self):
        raw={'passed':['x.t.b','x.t.a'],'tests_run':2}
        recorded={'tests_run':2,'passed':['x.t.a','x.t.b'],'note':'reviewed documentary enrichment'}
        self.assertEqual(A.compare_raw(raw,recorded,['passed','tests_run'],['note'],A.LIMITS),'MATCH')

    def test_EA24(self):
        raw={'passed':['x.t.a'],'tests_run':1};recorded={'passed':['x.t.a'],'tests_run':2}
        self.assertEqual(A.compare_raw(raw,recorded,raw,[],A.LIMITS),'MISMATCH')
        for r in [dict(raw,unknown='sensitive_marker'),dict(raw,passed=['x.t.a','x.t.a'])]:
            with self.assertRaises(A.Fault):A.compare_raw(r,raw,raw,[],A.LIMITS)

    def test_EA25(self):
        for value in [b'{"x":1,"x":2}',b'{',b'{"x":NaN}',b'{"x":1e999}',b'\xff']:
            p=self.packet();p.raw_bytes=value;p.seal();r,c=self.run_packet(p)
            self.assertEqual(c,2);self.assertNotIn('Traceback',json.dumps(r))
        p=self.packet();p.doc['unknown']='sensitive_marker';p.seal()
        del p.registry['entries'][0]['fields'][p.registry['entries'][0]['fields'].index('unknown')]
        r,c=self.run_packet(p);self.assertEqual(c,2)

    def test_EA26(self):
        for name in ['.','/outside','../outside','source_ingest/../outside','https://fixture','dev/file','run_data/file','.env','docs/internal/file','docs/./file','docs//file','docs/a\\b','docs/a\nfile']:
            with self.subTest(path=name):
                p=self.valid();p.registry['entries'][0]['path']=name
                r,c=self.run_packet(p);self.assertEqual(c,2)
                self.assertTrue(all('path' not in finding for finding in r['findings']))

    def test_EA27(self):
        for kind in ['final','parent','fifo']:
            p=self.valid();f=p.root/'source_ingest/model.py'
            if kind=='final':f.unlink();f.symlink_to(self.parent/'sentinel')
            elif kind=='parent':
                f.unlink();f.parent.rmdir();f.parent.symlink_to(self.parent,target_is_directory=True)
            else:f.unlink();os.mkfifo(f)
            r,c=self.run_packet(p);self.assertEqual(c,2)
            self.assertEqual((self.parent/'sentinel').read_bytes(),b'sibling sentinel')
        p=self.packet();f=p.root/'source_ingest/model.py';f.unlink();f.symlink_to('../docs/design/D5-I35-CONTRACT.md');p.seal()
        r,c=self.run_packet(p);self.assertEqual(c,2)

    def test_EA28(self):
        p=self.valid();ready=threading.Event();done=threading.Event()
        def writer():
            if ready.wait(5):write(p.root,'source_ingest/model.py',b'coordinated change')
            done.set()
        t=threading.Thread(target=writer);t.start()
        original=A.Reader.read
        def read(reader,name):
            value=original(reader,name)
            if name=='source_ingest/model.py':
                ready.set();self.assertTrue(done.wait(5))
            return value
        try:
            with patch.object(A.Reader,'read',read):r,c=self.run_packet(p)
        finally:ready.set();t.join(5)
        self.assertFalse(t.is_alive());self.assertEqual(c,1)
        self.assertEqual(r['applicability'],'UNDETERMINED')
        self.assertIn('UNSTABLE_SNAPSHOT',self.codes(r))

    def test_EA29(self):
        for budget in [dict(entries=0),dict(paths=1),dict(file_bytes=16),dict(total_bytes=16),dict(ids=1),dict(rows=1),dict(output_bytes=1),dict(depth=1),dict(string=1)]:
            with self.subTest(reduced_budget=budget):
                p=self.valid();r,c=self.run_packet(p,limits=budget);self.assertEqual(c,2)
        with self.assertRaises(A.Fault):A.strict_json(b'['*33+b'0'+b']'*33,A.LIMITS)

    def test_EA30(self):
        p=self.valid();r,c=self.run_packet(p,limits={'git_calls':0});self.assertEqual(c,2)
        spawned=[]
        def waiting(*args,**kwargs):
            child=REAL_POPEN([sys.executable,'-c','import signal; print("ready",flush=True); signal.pause()'],**kwargs)
            spawned.append(child);PROCESSES.append(child);return child
        with patch.object(A.subprocess,'Popen',waiting):r,c=self.run_packet(p,limits={'git_seconds':0.2})
        self.assertEqual(c,2);self.assertIn('GIT_TIMEOUT',self.codes(r))
        self.assertTrue(spawned and all(x.poll() is not None and x.stdout.closed for x in spawned))

    def test_EA31(self):
        marker='sensitive_marker_do_not_echo'
        p=self.packet();p.doc['passed']=[marker+' /home/privatevalue'];p.seal()
        r,c=self.run_packet(p);self.assertEqual(c,2)
        output=json.dumps(r);self.assertNotIn(marker,output);self.assertNotIn(self.temp.name,output)
        self.assertNotIn('/home/privatevalue',output)

    def test_EA32(self):
        p=self.valid()
        def snapshot():return {str(x.relative_to(p.root)):digest(x.read_bytes()) for x in p.root.rglob('*') if x.is_file()}
        before=snapshot()
        trace=self.parent/'forbidden-trace'
        with patch.dict(os.environ,{'GIT_TRACE2_EVENT':str(trace),'GIT_TRACE':str(trace)}):
            r,c=self.run_packet(p)
        self.assertEqual(c,0);self.assertFalse(trace.exists())
        self.assertEqual(snapshot(),before)

    def test_EA33(self):
        p=self.valid();r,c=self.run_packet(p);self.assertEqual(c,0)
        self.assertEqual((self.parent/'sentinel').read_bytes(),b'sibling sentinel')
        self.assertTrue(all(child.poll() is not None for child in PROCESSES))
        self.assertFalse(r['operational_activation']);self.assertFalse(r['publication_authorized'])

    def test_EA34(self):
        self.assertEqual(A.applicability('MATCH','CHANGED','SAME','NOT_RECORDED','CONSISTENT','NOT_RECORDED'),'STALE')
        self.assertEqual(A.applicability('MATCH','CHANGED','SAME','DIFFERENT','INCONSISTENT','NOT_RECORDED'),'INVALID')
        self.assertEqual(A.applicability('UNAVAILABLE','MATCH','SAME','MATCH_DECLARED','CONSISTENT','NOT_RECORDED'),'UNDETERMINED')
        self.assertEqual(A.applicability('MATCH','MATCH','SAME','MATCH_DECLARED','CONSISTENT','NOT_RECORDED'),'CURRENT_RECORDED_SCOPE')

    def test_EA35(self):
        r,c=A.audit(ROOT);self.assertEqual(c,1)
        by={e['id']:e for e in r['entries']}
        self.assertEqual(by['I34']['applicability'],'STALE')
        self.assertEqual(len(by['I34']['discovery_added']),6)
        self.assertEqual(by['I36']['applicability'],'CURRENT_RECORDED_SCOPE')
        self.assertEqual(by['I36']['verified_hash_entries'],86)
        self.assertTrue(all(e['historical_integrity']=='MATCH' for e in r['entries']))
        self.assertFalse(r['functional_campaigns_reexecuted'])

    def test_EA36(self):
        p=self.valid();r,c=self.run_packet(p)
        self.assertEqual(c,0);self.assertEqual(r['global_gaps_open'],[f'G{i:02}' for i in range(1,8)])
        self.assertFalse(r['publication_authorized']);self.assertFalse(r['D5_closed'])
        report=ROOT/'docs/validation/D5-I37-design-review.json'
        d=json.loads(report.read_text())
        self.assertEqual(len(d['proposed_cases']),36)
        self.assertEqual({x['status'] for x in d['proposed_cases']},{'DESIGN_NOT_EXECUTED'})


if __name__=='__main__':
    with patch.object(subprocess,'Popen',tracked_popen):unittest.main()
