# SPDX-License-Identifier: GPL-3.0-only
"""D5 comparison/review/simulation integration, never operational application."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from .postgres_scenarios import Persistence, uid, PROFILE
from source_ingest.postgres import envelope
from source_ingest.preview import canonical
from source_ingest.review import ReviewClient, review_sql


class Review(Persistence):
    def setUp(self):
        super().setUp()
        self.client=ReviewClient(self.lab.container)
        self.reviewer=ReviewClient(self.lab.container,'d5_reviewer')
        self.reader=ReviewClient(self.lab.container,'d5_reader')

    def prepare(self,prefix='register',profile=PROFILE,select_before=True):
        self.profile=profile
        _,b=self.ingest(self.capture(Path(f'testing/D5/fixtures/{prefix}-before.md').read_bytes(),profile=profile))
        _,a=self.ingest(self.capture(Path(f'testing/D5/fixtures/{prefix}-after.md').read_bytes(),label='fixture-v2',profile=profile))
        self.before,self.after=b['observation_id'],a['observation_id']
        self.cid=uid()
        self.saved=self.client.compare(self.cid,self.pid,self.doc,self.before,self.after)
        self.report,self.digest=self.reader.recover_comparison(self.pid,self.doc,self.cid)
        self.items={x['source_key']:x for x in self.report['review_items']}
        if select_before:
            self.writer.submit(self.select(self.before,0,profile=profile))
        return self.saved

    def decision_request(self,key='PT-01',decision='ACCEPT',version=0,cid=None):
        return envelope(cid or uid(),'DECIDE_ROW',self.pid,self.doc,comparison_id=self.cid,
                        report_sha256=self.digest,source_key=key,row_sha256=self.items[key]['row_sha256'],
                        decision=decision,expected_version=version,reviewer_label='synthetic-reviewer',reason='Synthetic review of complete source change')

    def decide(self,key='PT-01',decision='ACCEPT',version=0,cid=None):
        req=self.decision_request(key,decision,version,cid)
        response=self.reviewer.decide(req['command_id'],self.pid,self.doc,self.cid,key,req['row_sha256'],self.digest,
                                      version,decision,req['reviewer_label'],req['reason'])
        return req,response

    def pin(self,key,response):
        return dict(source_key=key,row_sha256=self.items[key]['row_sha256'],decision_command_id=response['command_id'],expected_version=response['version_at_commit'])

    def simulation_request(self,pins,version=1,cid=None):
        return envelope(cid or uid(),'SIMULATE_APPLICATION',self.pid,self.doc,comparison_id=self.cid,
                        report_sha256=self.digest,expected_reference_version=version,items=sorted(pins,key=lambda x:x['source_key']))

    def simulate(self,pins,version=1,cid=None):
        req=self.simulation_request(pins,version,cid)
        return self.reviewer.simulate(req['command_id'],self.pid,self.doc,self.cid,self.digest,version,req['items'])

    def simulations(self):
        return int(self.scalar(f"SELECT count(*) FROM d5.simulations WHERE comparison_id='{self.cid}';"))

    def test_R01_compare_recover_dedup_and_unchanged_rows(self):
        self.prepare()
        self.assertEqual(self.saved['review_item_count'],3)
        self.assertEqual(set(self.items),{'PT-01','PT-02','PT-04'})
        replay=self.client.compare(self.cid,self.pid,self.doc,self.before,self.after)
        self.assertEqual(replay,self.saved)
        same=self.client.compare(uid(),self.pid,self.doc,self.before,self.after)
        self.assertEqual(same['report_sha256'],self.digest)
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d5.comparison_reports WHERE report_sha256='{self.digest}';"),'1')
        old=self.head()
        self.client.compare(uid(),self.pid,self.doc,self.before,self.before)
        self.assertEqual(self.head(),old)
        self.assertEqual(self.reader.read_command(self.cid),self.saved)

    def test_R02_annotations_keep_full_raw_rows(self):
        self.prepare('register-compat')
        self.assertEqual(set(self.items),{'PT-01'})
        row=json.loads(base64.b64decode(self.items['PT-01']['row_base64']))
        self.assertEqual(row['changed_fields'],['source_annotation'])
        self.assertIn('revised source claim',row['after']['row']['source_annotation']['text'])
        _,r=self.decide()
        self.assertEqual(self.simulate([self.pin('PT-01',r)])['actions'][0]['operation'],'STAGE_SOURCE_CHANGE')

    def test_R03_blocked_comparisons_cannot_review(self):
        self.prepare('register-compat',profile='task-register.v1')
        self.assertEqual(self.report['state'],'BLOCKED')
        self.assertEqual(self.items,{})
        req=envelope(uid(),'DECIDE_ROW',self.pid,self.doc,comparison_id=self.cid,report_sha256=self.digest,
                     source_key='PT-01',row_sha256='0'*64,decision='ACCEPT',expected_version=0,reviewer_label='fixture',reason='Blocked')
        response=self.reviewer.query(review_sql('decide_row',req))
        self.assertEqual(response['code'],'COMPARISON_BLOCKED')
        self.assertEqual(self.simulations(),0)

    def test_R04_missing_or_incompatible_observations(self):
        self.prepare()
        for pid,doc,bid,aid in [(uid(),self.doc,self.before,self.after),(self.pid,uid(),self.before,self.after),(self.pid,self.doc,uid(),self.after)]:
            with self.assertRaises(ValueError):
                self.client.compare(uid(),pid,doc,bid,aid)
        _,structural=self.ingest(self.capture(profile='markdown-structure.v1'))
        with self.assertRaises(ValueError):
            self.client.compare(uid(),self.pid,self.doc,structural['observation_id'],self.after)

    def test_R05_SQL_hash_scope_and_reconstruction_boundary(self):
        self.prepare()
        report=copy.deepcopy(self.report)
        report['observations']['before']['preview_sha256']='0'*64
        payload=canonical(report)
        req=envelope(uid(),'SAVE_COMPARISON',self.pid,self.doc,before_observation_id=self.before,
                     after_observation_id=self.after,profile=self.profile,report_sha256=hashlib.sha256(payload).hexdigest())
        self.denied(review_sql('save_comparison',req,payload))
        self.assertIsNone(self.reader.read_command(req['command_id']))
        # A direct trusted SQL writer can forge parser semantics. Recovery must refuse it.
        report=copy.deepcopy(self.report)
        item=report['review_items'][0]
        row=json.loads(base64.b64decode(item['row_base64']))
        row['after']['row']['fields']['status']='FORGED'
        rowbytes=canonical(row)
        item['row_base64']=base64.b64encode(rowbytes).decode('ascii');item['row_sha256']=hashlib.sha256(rowbytes).hexdigest()
        payload=canonical(report);req['command_id']=uid();req['report_sha256']=hashlib.sha256(payload).hexdigest()
        self.assertEqual(self.client.query(review_sql('save_comparison',req,payload))['status'],'OK')
        with self.assertRaises(ValueError):
            self.reader.recover_comparison(self.pid,self.doc,req['command_id'])
        with self.assertRaises(ValueError):
            self.reviewer.decide(uid(),self.pid,self.doc,req['command_id'],item['source_key'],item['row_sha256'],req['report_sha256'],0,'ACCEPT','fixture','Refuse forged semantics')

    def test_R06_decision_CAS_replay_and_whole_patch_binding(self):
        self.prepare()
        req,a=self.decide()
        _,rejected=self.decide(decision='REJECT',version=1)
        self.assertEqual(rejected['version_at_commit'],2)
        self.assertEqual(self.reviewer.query(review_sql('decide_row',req)),a)
        state=self.reader.review_state(self.pid,self.doc,self.cid,'PT-01')
        self.assertEqual((state['version'],state['decision']),(2,'REJECT'))
        _,stale=self.decide(version=0)
        self.assertEqual(stale['code'],'DECISION_VERSION_CONFLICT')
        changed=dict(req,expected_version=2)
        self.assertEqual(self.reviewer.query(review_sql('decide_row',changed))['code'],'COMMAND_CONTENT_CONFLICT')
        with self.assertRaises(ValueError):
            self.reviewer.decide(uid(),self.pid,self.doc,self.cid,'PT-01','0'*64,self.digest,2,'ACCEPT','fixture','Wrong patch')

    def test_R07_unreviewed_rejected_and_partial_simulation(self):
        self.prepare()
        _,a=self.decide('PT-01')
        _,r=self.decide('PT-04','REJECT')
        pins=[self.pin('PT-01',a),self.pin('PT-04',r)]
        rejected=self.simulate(pins)
        self.assertEqual(rejected['code'],'ROW_NOT_ACCEPTED')
        self.assertNotIn('actions',rejected)
        self.assertEqual(self.simulations(),0)
        unreviewed=dict(source_key='PT-02',row_sha256=self.items['PT-02']['row_sha256'],decision_command_id=uid(),expected_version=0)
        self.assertEqual(self.simulate([unreviewed])['code'],'DECISION_VERSION_CONFLICT')
        self.assertEqual(self.simulate([self.pin('PT-01',a)])['status'],'OK')

    def test_R08_reference_guard_ABA_and_historical_receipt(self):
        self.prepare(select_before=False)
        _,r=self.decide();pins=[self.pin('PT-01',r)]
        self.assertEqual(self.simulate(pins,0)['code'],'REFERENCE_VERSION_CONFLICT')
        self.writer.submit(self.select(self.before,0))
        cid=uid();first=self.simulate(pins,1,cid)
        self.writer.submit(self.select(self.after,1))
        self.assertEqual(self.simulate(pins,1)['code'],'REFERENCE_VERSION_CONFLICT')
        self.writer.submit(self.select(self.before,2))
        self.assertEqual(self.simulate(pins,1)['code'],'REFERENCE_VERSION_CONFLICT')
        self.assertEqual(self.simulate(pins,1,cid),first)
        self.assertEqual(first['reference_version_at_commit'],1)
        self.assertEqual(self.head()['version'],3)
        self.assertEqual(self.simulate(pins,3)['status'],'OK')

    def test_R09_decision_revocation_and_reacceptance(self):
        self.prepare();_,first=self.decide()
        pins=[self.pin('PT-01',first)]
        self.decide(decision='REJECT',version=1)
        self.assertEqual(self.simulate(pins)['code'],'DECISION_VERSION_CONFLICT')
        _,again=self.decide(version=2)
        self.assertEqual(self.simulate(pins)['code'],'DECISION_VERSION_CONFLICT')
        self.assertEqual(self.simulate([self.pin('PT-01',again)])['status'],'OK')

    def test_R10_concurrent_decisions_and_simulation(self):
        self.prepare()
        requests=[self.decision_request(decision=decision) for decision in ('ACCEPT','REJECT')]
        results=self.lab.concurrent([review_sql('decide_row',r) for r in requests],role='d5_reviewer')
        self.assertEqual(sorted(r['status'] for r in results),['CONFLICT','OK'])
        self.assertEqual(self.reader.review_state(self.pid,self.doc,self.cid,'PT-01')['version'],1)
        _,accepted=self.decide(version=1)
        pin=self.pin('PT-01',accepted)
        sim=self.simulation_request([pin]);reject=self.decision_request(decision='REJECT',version=2)
        results=self.lab.concurrent([review_sql('simulate_application',sim),review_sql('decide_row',reject)],role='d5_reviewer')
        self.assertEqual(results[1]['status'],'OK')
        self.assertIn(results[0]['status'],('OK','CONFLICT'))
        self.assertEqual(self.reader.review_state(self.pid,self.doc,self.cid,'PT-01')['decision'],'REJECT')
        self.assertEqual(self.simulate([pin])['code'],'DECISION_VERSION_CONFLICT')

    def test_R11_abort_decision_simulation_and_restart(self):
        self.prepare()
        req=self.decision_request()
        self.lab.abort_after(review_sql('decide_row',req))
        self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.reader.review_state(self.pid,self.doc,self.cid,'PT-01')['version'],0)
        r=self.reviewer.query(review_sql('decide_row',req));pins=[self.pin('PT-01',r)]
        sim=self.simulation_request(pins)
        self.lab.abort_after(review_sql('simulate_application',sim))
        self.assertIsNone(self.reader.read_command(sim['command_id']));self.assertEqual(self.simulations(),0)
        result=self.reviewer.query(review_sql('simulate_application',sim))
        self.lab.restart()
        self.assertEqual(self.reviewer.query(review_sql('simulate_application',sim)),result)
        recovered,digest=self.reader.recover_comparison(self.pid,self.doc,self.cid)
        self.assertEqual(digest,self.digest);self.assertEqual(recovered,self.report)

    def test_R12_no_D2_writes_and_absence_no_delete(self):
        self.prepare();before=self.lab.protected_state();head=self.head()
        pins=[]
        for key in sorted(self.items):
            _,r=self.decide(key);pins.append(self.pin(key,r))
        result=self.simulate(pins)
        self.assertEqual(result['status'],'OK')
        ops={x['source_key']:x['operation'] for x in result['actions']}
        self.assertEqual(ops,{'PT-01':'STAGE_SOURCE_CHANGE','PT-02':'KEEP_EXISTING_NO_DELETE','PT-04':'STAGE_SOURCE_ADDITION'})
        self.assertTrue(result['simulation_only']);self.assertFalse(result['writes_d2']);self.assertFalse(result['activation_allowed'])
        self.assertEqual(self.lab.protected_state(),before);self.assertEqual(self.head(),head)

    def test_R13_permissions_and_immutable_facts(self):
        self.prepare()
        req=self.decision_request()
        for role in ('d5_reader','d5_writer'):
            self.denied(review_sql('decide_row',req),role=role)
            self.denied(review_sql('simulate_application',self.simulation_request([dict(source_key='PT-01',row_sha256=self.items['PT-01']['row_sha256'],decision_command_id=uid(),expected_version=0)])),role=role)
        self.denied('SELECT * FROM public.tasks;',role='d5_reviewer')
        self.denied('UPDATE d5.row_review_heads SET version=0;',role='d5_reviewer')
        self.denied('SELECT d5.submit(\'{}\'::json);',role='d5_reviewer')
        self.denied('SELECT d5.review_finish(\'{}\'::jsonb,\'{}\'::jsonb);',role='d5_reviewer')
        for table in ('comparison_reports','comparisons','review_items','row_decisions','simulations'):
            self.denied(f'DELETE FROM d5.{table};',role='d5_lab_admin')
        self.denied(review_sql('decide_row',dict(req,extra='unsafe')),role='d5_reviewer')
        sim=self.simulation_request([dict(source_key='PT-01',row_sha256=self.items['PT-01']['row_sha256'],decision_command_id=uid(),expected_version=0)])
        self.denied(review_sql('simulate_application',dict(sim,items=sim['items']*2)),role='d5_reviewer')

    def test_R14_long_source_ID_is_not_truncated(self):
        key='LONG-'+'1'*5000
        b=Path('testing/D5/fixtures/register-before.md').read_bytes().replace(b'PT-01',key.encode())
        a=b.replace(b'Review only',b'Updated source claim')
        _,before=self.ingest(self.capture(b));_,after=self.ingest(self.capture(a,label='long-v2'))
        self.before,self.after=before['observation_id'],after['observation_id'];self.profile=PROFILE
        self.cid=uid();self.client.compare(self.cid,self.pid,self.doc,self.before,self.after)
        self.report,self.digest=self.reader.recover_comparison(self.pid,self.doc,self.cid)
        self.items={i['source_key']:i for i in self.report['review_items']}
        self.writer.submit(self.select(self.before,0))
        _,r=self.decide(key)
        self.assertEqual(self.simulate([self.pin(key,r)])['status'],'OK')

    def test_R15_CLI_compare_review_simulate(self):
        self.prepare()
        def cli(*args,code=0):
            r=subprocess.run([sys.executable,'-m','source_ingest.review','--container',self.lab.container,*args],capture_output=True,text=True)
            self.assertEqual(r.returncode,code,r.stderr)
            return json.loads(r.stdout)
        common=['--project-id',self.pid,'--document-id',self.doc]
        saved=cli('compare',*common,'--command-id',uid(),'--before-observation-id',self.before,'--after-observation-id',self.after)
        extra=['--comparison-id',saved['comparison_id']]
        with tempfile.TemporaryDirectory() as directory:
            exported=cli('export',*common,*extra,'--store',directory)
            self.assertEqual(hashlib.sha256(Path(exported['report']).read_bytes()).hexdigest(),saved['report_sha256'])
        shown=cli('row',*common,*extra,'--source-key','PT-01')
        self.assertEqual(shown['change']['after']['row']['fields']['status'],'WATCH')
        sha=shown['review']['row_sha256']
        decision=cli('decide',*common,*extra,'--source-key','PT-01','--command-id',uid(),'--row-sha256',sha,
                     '--report-sha256',saved['report_sha256'],'--expected-version','0','--decision','ACCEPT','--reviewer-label','fixture','--reason','Synthetic review')
        result=cli('simulate',*common,*extra,'--command-id',uid(),'--report-sha256',saved['report_sha256'],
                   '--expected-reference-version','1','--item','PT-01:'+sha+':'+decision['command_id']+':1')
        self.assertTrue(result['simulation_only'])
        cli('decide',*common,*extra,'--source-key','PT-01','--command-id',uid(),'--row-sha256',sha,
            '--report-sha256',saved['report_sha256'],'--expected-version','0','--decision','REJECT','--reviewer-label','fixture','--reason','Stale',code=2)
