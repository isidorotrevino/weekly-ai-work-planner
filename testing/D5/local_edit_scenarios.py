# SPDX-License-Identifier: GPL-3.0-only
"""LE01-LE32: approved I13; full source/local choice without activation."""
import concurrent.futures
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from .reappearance_scenarios import Reappearance
from .mapping_scenarios import body
from .postgres_scenarios import uid
from source_ingest.local_edit import ENTRIES, LocalEditClient, local_edit_sql
from source_ingest.postgres import sql_text, submit_sql
from source_ingest.task_mapping import mapping_sql


class LocalEdit(Reappearance):
    def setUp(self):
        super().setUp()
        self.lwriter=LocalEditClient(self.lab.container,'d5_writer')
        self.lreviewer=LocalEditClient(self.lab.container,'d5_reviewer')
        self.lreader=LocalEditClient(self.lab.container)
        self.lapplier=LocalEditClient(self.lab.container,'d5_applier')

    def lsend(self,req):
        return {'d5_writer':self.lwriter,'d5_reviewer':self.lreviewer,'d5_applier':self.lapplier}[ENTRIES[req['action']][1]].submit_local_edit(req)

    def local(self,title='Local',description='Description',bump=False):
        self.lab.sql(f"UPDATE public.tasks SET title={sql_text(title)},description="+('NULL' if description is None else sql_text(description))+(',row_version=row_version+1' if bump else '')+f" WHERE id='{self.tid}';")

    def setup_change(self,present=None,after=None,key='PT-01',origin='bootstrap',edit=True):
        present=present or body(key=key);self.key=key
        if origin=='bootstrap':
            self.initial(present,key);_,p=self.bpropose(key);_,pkg=self.bpackage(p);self.assertEqual(self.bapply(pkg)[1]['status'],'OK')
        elif origin=='mapping':
            self.stage(body('Old',key=key),present);self.intent(key);_,p=self.propose(key);_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
        else:
            self.cycle(key=key);_,p=self.rpropose();_,pkg=self.rpackage(p);self.rapply(pkg);present=body('Returned',key=key)
        self.stage(present,after or body('Remote',key=key))
        if edit:self.local()

    def lrequest(self,**extra):
        version=int(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"))
        req=self.command('PREPARE_LOCAL_EDIT_TASK',intent_id=self.iid,comparison_id=self.cid,report_sha256=self.digest,
            row_sha256=self.items.get(self.key,{}).get('row_sha256','0'*64),expected_reference_version=self.refv,
            expected_mapping_version=version,choice='USE_SOURCE',reason='Synthetic review of complete source versus local result')
        return dict(req,**extra)

    def lpropose(self,accept_source=True,**extra):
        if accept_source:self.decide(self.key)
        req=self.lrequest(**extra);return req,self.lsend(req)

    def laccept(self,p,version=0,decision='ACCEPT'):
        req=self.command('REVIEW_LOCAL_EDIT_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],
            expected_version=version,decision=decision,reviewer_label='synthetic-reviewer',reason='Review whole projection choice and source evidence')
        return req,self.lsend(req)

    def lpackage(self,*proposals,accept=True):
        pins=[]
        for p in proposals:
            if accept:
                _,r=self.laccept(p)
                pin=dict(proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],review_command_id=r['command_id'],review_version=r['version_at_commit'])
            else:
                data=self.lreader.artifact(self.pid,self.doc,'proposal',p['proposal_id'])
                pin={k:data[k] for k in ('proposal_id','manifest_sha256','review_command_id','review_version')}
                pin['review_command_id']=pin['review_command_id'] or uid()
            pins.append(pin)
        req=self.command('PACKAGE_LOCAL_EDIT_TASKS',items=sorted(pins,key=lambda p:p['proposal_id']))
        return req,self.lsend(req)

    def lapply(self,pkg):
        req=self.command('APPLY_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
        count=self.scalar('SELECT count(*) FROM public.tasks;');r=self.lsend(req)
        self.assertEqual(self.scalar('SELECT count(*) FROM public.tasks;'),count)
        return req,r

    def resolution_state(self):
        state=self.lab.protected_state()
        names=self.scalar("SELECT string_agg(quote_ident(tablename),',' ORDER BY tablename) FROM pg_tables WHERE schemaname='d5' AND tablename<>'commands';").split(',')
        for name in names:
            state['d5.'+name]=self.scalar("SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text),'[]'::jsonb) FROM d5."+name+' t;')
        return state

    def test_LE01_prepare_existing_origins_without_writes(self):
        for n,origin in enumerate(('bootstrap','mapping','reappearance'),1):
            self.tid,self.tkey=uid(),uid();self.setup_change(origin=origin,key=f'PT-{n:02}')
            before=self.lab.protected_state();req,p=self.lpropose()
            self.assertEqual(p['status'],'OK');self.assertEqual(self.lsend(req),p);self.assertEqual(self.lab.protected_state(),before)
            self.assertEqual(p['manifest']['local_projection']['title'],'Local');self.assertEqual(p['manifest']['after_projection']['title'],'Remote')

    def test_LE02_scope_and_ownership(self):
        self.setup_change();self.decide();req=self.lrequest()
        for fields in (dict(intent_id=uid()),dict(project_id=uid()),dict(document_id=uid())):
            self.assertEqual(self.lwriter.query(local_edit_sql(dict(req,command_id=uid(),**fields)))['code'],'INTENT_SCOPE_CONFLICT')
        self.lab.sql(f"UPDATE public.tasks SET task_key='changed' WHERE id='{self.tid}';")
        self.assertEqual(self.lpropose(False)[1]['code'],'TARGET_IDENTITY_CONFLICT')
        self.denied(f"UPDATE d5.task_intents SET policy='other' WHERE intent_id='{self.iid}';",role='d5_lab_admin')

    def test_LE03_value_based_divergence(self):
        self.setup_change(edit=False);self.assertEqual(self.lpropose()[1]['code'],'NO_LOCAL_EDIT')
        for bump in (False,True):
            self.local(bump=bump);self.assertEqual(self.lpropose(False)[1]['status'],'OK')

    def test_LE04_present_changed_only(self):
        self.setup_change()
        for b,a in ((body(),body()),(body(key='PT-99'),body()),(body(),body(key='PT-99'))):
            self.stage(b,a);self.assertEqual(self.lpropose(False)[1]['code'],'PRESENT_CHANGED_ROW_REQUIRED')
        self.stage(body(),body('Remote')+b'| PT-01 | duplicate | x | x | - | OPEN | no | inert |\n')
        self.assertEqual(self.lpropose(False)[1]['code'],'COMPARISON_SCOPE_CONFLICT')

    def test_LE05_semantic_before_and_new_observation(self):
        self.setup_change();self.stage(body('Wrong base'),body('Remote'))
        self.assertEqual(self.lpropose()[1]['code'],'SOURCE_BASE_CONFLICT')
        self.stage(b'\n\n'+body(),body('Remote'));_,p=self.lpropose();_,pkg=self.lpackage(p)
        self.assertEqual(self.lapply(pkg)[1]['status'],'OK')

    def test_LE06_source_review_is_current(self):
        self.setup_change();self.assertEqual(self.lpropose(False)[1]['code'],'SOURCE_NOT_ACCEPTED')
        _,p=self.lpropose();_,pkg=self.lpackage(p)
        self.decide(decision='REJECT',version=1);self.decide(version=2)
        self.assertEqual(self.lapply(pkg)[1]['code'],'SOURCE_REVIEW_CONFLICT')

    def test_LE07_reference_ABA(self):
        self.setup_change();_,p=self.lpropose();_,pkg=self.lpackage(p)
        self.writer.submit(self.select(self.after,self.refv));self.writer.submit(self.select(self.before,self.refv+1))
        self.assertEqual(self.lapply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')
        self.assertEqual(self.lpropose(False)[1]['code'],'REFERENCE_VERSION_CONFLICT')

    def test_LE08_closed_immutable_manifest(self):
        self.setup_change();_,p=self.lpropose();req,_=self.laccept(p)
        for k,v in [('choice','KEEP_LOCAL'),('result_projection',{'title':'x'}),('force',True),('fields',['title'])]:
            self.denied(local_edit_sql(dict(req,command_id=uid(),**{k:v})),role='d5_reviewer')
        self.denied("UPDATE d5.local_edit_proposals SET manifest=manifest||'{\"choice\":\"KEEP_LOCAL\"}';",role='d5_lab_admin')
        bad=dict(req,command_id=uid(),manifest_sha256='0'*64,expected_version=1)
        with self.assertRaises(ValueError):self.lsend(bad)
        self.assertEqual(self.lreviewer.query(local_edit_sql(bad))['code'],'MANIFEST_SCOPE_CONFLICT')
        _,changed=self.lpropose(False,reason='Different explicit preparation reason')
        self.assertNotEqual(changed['manifest_sha256'],p['manifest_sha256'])
        self.assertEqual(self.lpackage(changed,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        original=self.lreader.artifact
        for key in ('result_projection','local_projection','before_projection','after_basis','choice'):
            forged=copy.deepcopy(p);forged['manifest'][key]='forged'
            self.lreader.artifact=lambda *args, data=forged:data
            with self.assertRaises((ValueError,TypeError)):self.lreader.verify_manifest(self.pid,self.doc,p['proposal_id'],p['manifest_sha256'])
        self.lreader.artifact=original

    def test_LE09_choice_and_reason(self):
        self.setup_change();self.decide()
        for fields in (dict(choice='FORCE'),dict(choice='SAME_SOURCE_ENTITY'),dict(reason=''),dict(reason=' \u00a0 '),dict(reason='a\nb'),dict(reason='x'*1025)):
            self.assertEqual(self.lpropose(False,**fields)[1]['code'],'RESOLUTION_CHOICE_REQUIRED')
        req=self.lrequest()
        for fields in (dict(reason=None),dict(choice=True),dict(reason=1)):
            self.denied(local_edit_sql(dict(req,command_id=uid(),**fields)))

    def test_LE10_USE_SOURCE_PATCH_only(self):
        self.setup_change();self.lab.sql(f"UPDATE public.tasks SET urgency=3,deferred_count=2 WHERE id='{self.tid}';");old=self.task()
        _,p=self.lpropose();_,pkg=self.lpackage(p);_,r=self.lapply(pkg);self.assertEqual(r['status'],'OK');new=self.task()
        self.assertEqual(new['title'],'Remote');self.assertEqual(new['row_version'],old['row_version']+1)
        self.assertEqual({k:v for k,v in old.items() if k not in ('title','description','row_version')},{k:v for k,v in new.items() if k not in ('title','description','row_version')})
        self.assertTrue(r['effects'][0]['writes_task'])

    def test_LE11_KEEP_LOCAL_retains_task_and_source_projection(self):
        self.setup_change();old=self.task();_,p=self.lpropose(choice='KEEP_LOCAL');_,pkg=self.lpackage(p);_,r=self.lapply(pkg)
        self.assertEqual(r['status'],'OK');self.assertEqual(self.task(),old);self.assertFalse(r['effects'][0]['writes_task'])
        self.assertEqual(r['effects'][0]['result_projection']['title'],'Local');self.assertEqual(r['effects'][0]['source_projection']['title'],'Remote')
        self.assertEqual(self.scalar(f"SELECT projection->>'title' FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'Remote')

    def test_LE12_convergence_both_choices_no_task_update(self):
        self.setup_change(after=body('Local'));old=self.task()
        for choice in ('USE_SOURCE','KEEP_LOCAL'):
            _,p=self.lpropose(choice=choice);_,pkg=self.lpackage(p)
            # A trigger makes any attempted UPDATE observable, even if values are unchanged.
            trigger="BEGIN;CREATE FUNCTION pg_temp.no_local_update() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'unexpected task update'; END $$;CREATE TRIGGER no_local_update BEFORE UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION pg_temp.no_local_update();"
            req=self.command('APPLY_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
            result=self.lab.sql(trigger+local_edit_sql(req)+'ROLLBACK;')
            self.assertEqual(json.loads(result.stdout.splitlines()[-1])['status'],'OK');self.assertEqual(self.task(),old)
        self.assertEqual(self.lapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old)

    def test_LE13_evidence_change_with_source_projection_unchanged(self):
        self.setup_change(after=body(status='DONE'))
        for choice in ('USE_SOURCE','KEEP_LOCAL'):
            _,p=self.lpropose(choice=choice);self.assertEqual(p['manifest']['before_projection'],p['manifest']['after_projection'])
            self.assertEqual(p['manifest']['result_projection']['title'],'Title' if choice=='USE_SOURCE' else 'Local')
        _,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK')

    def test_LE14_disjoint_fields_are_never_merged(self):
        self.setup_change(after=body(objective='Remote description'));old=self.task()
        for choice in ('USE_SOURCE','KEEP_LOCAL'):
            _,p=self.lpropose(choice=choice)
            self.assertEqual(p['manifest']['result_projection'],dict(title='Title',description='Remote description') if choice=='USE_SOURCE' else dict(title='Local',description='Description'))
        self.assertEqual(self.task(),old)

    def test_LE15_literal_long_ID_and_source_evidence(self):
        key='LONG-'+'1'*5000;text='Árbol **raw** \\| `literal`'
        self.setup_change(key=key,after=body(text,'ñ [x](https://example.invalid)',annotation=' source claim',key=key,struck=True))
        _,p=self.lpropose();_,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task()['title'],text);self.assertEqual(p['manifest']['intent']['source_key'],key)
        self.assertTrue(p['manifest']['source_change']['after']['row']['source_struck'])

    def test_LE16_invalid_titles_nullable_and_literal_descriptions(self):
        self.setup_change(after=body(' \u00a0 '));self.assertEqual(self.lpropose(choice='KEEP_LOCAL')[1]['code'],'INVALID_PROJECTION')
        self.stage(body(),body('Remote'));self.local(' \u00a0 ');self.assertEqual(self.lpropose()[1]['code'],'INVALID_PROJECTION')
        self.local(description=None);old=self.task();_,p=self.lpropose(False,choice='KEEP_LOCAL');_,pkg=self.lpackage(p)
        self.assertIsNone(p['manifest']['result_projection']['description']);self.assertEqual(self.lapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old)
        self.stage(body('Remote'),body('Next',''));_,p=self.lpropose();self.assertEqual(p['manifest']['after_projection']['description'],'')
        self.stage(body('Remote'),body('Next','-'));_,p=self.lpropose();_,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['description'],'-')

    def test_LE17_source_claims_remain_inert(self):
        self.setup_change(after=body('Remote',status='DONE',annotation=' verified approved'))
        _,p=self.lpropose();_,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['status'],'BACKLOG')
        self.assertIn('verified',p['manifest']['after_basis']['annotation_text'])

    def test_LE18_post_prepare_edit_without_version(self):
        self.setup_change();_,p=self.lpropose();_,pkg=self.lpackage(p);self.local('Unreviewed')
        self.assertEqual(self.lapply(pkg)[1]['code'],'RESOLUTION_CONTENT_CONFLICT');self.assertEqual(self.task()['title'],'Unreviewed')

    def test_LE19_full_CAS_and_observable_ABA(self):
        self.setup_change();_,p=self.lpropose();_,pkg=self.lpackage(p)
        self.lab.sql(f"UPDATE public.tasks SET urgency=4 WHERE id='{self.tid}';")
        self.assertEqual(self.lapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')
        _,p=self.lpropose(False);_,pkg=self.lpackage(p);self.local('Other',bump=True);self.local('Local',bump=True)
        self.assertEqual(self.lapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')
        self.local('Title');self.assertEqual(self.lapply(pkg)[1]['code'],'NO_LOCAL_EDIT')

    def test_LE20_state_operations_and_historical_schedule(self):
        self.setup_change();_,p=self.lpropose();_,pkg=self.lpackage(p)
        fixtures=[f"SELECT d2.transition('{uid()}','{json.dumps(dict(entity_type='TASK',entity_id=self.tid,expected_version=0,actor='fixture',reason='negative test',to='BLOCKED',**{'from':'BACKLOG'}))}');",
                  f"INSERT INTO public.operations(task_id,operation_type,idempotency_key) VALUES('{self.tid}','SYNTHETIC','{uid()}');"]
        plan=uid();fixtures.append(self.plan_fixture(plan)+f"INSERT INTO public.schedule_entries(planning_run_id,task_id,resource_id,pool,priority_snapshot,state) VALUES('{plan}','{self.tid}','{self.lab.resource}','PLANNED','{{}}','CANCELLED');")
        for choice in ('USE_SOURCE','KEEP_LOCAL'):
            _,p=self.lpropose(False,choice=choice);_,pkg=self.lpackage(p)
            for fixture in fixtures:
                req=self.command('APPLY_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
                r=self.lab.sql('BEGIN;'+fixture+'SET LOCAL ROLE d5_applier;'+local_edit_sql(req)+'ROLLBACK;',check=False)
                self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout.splitlines()[-1])['code'],'TARGET_HAS_WORK_OR_STATE')
        self.assertEqual(self.scalar('SELECT count(*) FROM public.operations;'),'0')

    def test_LE21_separate_versioned_review(self):
        self.setup_change();_,p=self.lpropose();self.assertEqual(self.lpackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        _,pkg=self.lpackage(p);self.laccept(p,1,'REJECT');self.laccept(p,2,'ACCEPT')
        self.assertEqual(self.lapply(pkg)[1]['code'],'LOCAL_EDIT_REVIEW_CONFLICT')
        _,fresh=self.lpackage(p,accept=False);self.assertEqual(self.lapply(fresh)[1]['status'],'OK')

    def test_LE22_package_limits_and_variant_isolation(self):
        self.setup_change();_,p=self.lpropose();_,p2=self.lpropose(False,choice='KEEP_LOCAL');_,r2=self.laccept(p2);req,pkg=self.lpackage(p)
        self.assertEqual(self.lsend(dict(req,command_id=uid()))['package_sha256'],pkg['package_sha256'])
        for items in ([],req['items']*2,req['items']*2001):self.denied(local_edit_sql(dict(req,command_id=uid(),items=items)))
        pin=dict(proposal_id=p2['proposal_id'],manifest_sha256=p2['manifest_sha256'],review_command_id=r2['command_id'],review_version=1)
        self.denied(local_edit_sql(dict(req,command_id=uid(),items=sorted(req['items']+[pin],key=lambda x:x['proposal_id']))))
        self.assertEqual(self.mapper.query(mapping_sql(dict(req,command_id=uid(),action='PACKAGE_TASK_PROPOSALS')))['code'],'MANIFEST_SCOPE_CONFLICT')
        from source_ingest.bootstrap import bootstrap_sql
        from source_ingest.reappearance import reappearance_sql
        for client,sql,action in [(self.bwriter,bootstrap_sql,'PACKAGE_BOOTSTRAP_TASKS'),(self.rwriter,reappearance_sql,'PACKAGE_REAPPEARANCE_TASKS')]:
            self.assertEqual(client.query(sql(dict(req,command_id=uid(),action=action)))['code'],'MANIFEST_SCOPE_CONFLICT')

    def test_LE23_replay_global_commands_never_restore(self):
        self.setup_change();_,p=self.lpropose();_,pkg=self.lpackage(p);req,r=self.lapply(pkg);self.local('Later',bump=True)
        self.assertEqual(self.lsend(req),r);self.assertEqual(self.lsend(dict(req,command_id=uid()))['status'],'ALREADY_APPLIED')
        self.assertEqual(self.task()['title'],'Later')
        self.assertEqual(self.lapplier.query(local_edit_sql(dict(req,package_sha256='0'*64)))['code'],'COMMAND_CONTENT_CONFLICT')
        self.assertEqual(self.applier.query(mapping_sql(dict(req,action='APPLY_TASK_PROPOSALS')))['code'],'COMMAND_CONTENT_CONFLICT')

    def test_LE24_real_concurrent_packages_and_review_reference(self):
        self.setup_change();_,p=self.lpropose();_,p2=self.lpropose(False,choice='KEEP_LOCAL');_,pkg=self.lpackage(p);_,pkg2=self.lpackage(p2)
        requests=[self.command('APPLY_LOCAL_EDIT_TASKS',package_sha256=x['package_sha256']) for x in (pkg,pkg2)]
        results=self.lab.concurrent([local_edit_sql(r) for r in requests],role='d5_applier')
        self.assertEqual(sorted(r['status'] for r in results),['CONFLICT','OK'])
        self.assertEqual(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'2')
        self.stage(body('Remote'),body('Again'));self.local();_,p=self.lpropose();_,pkg=self.lpackage(p)
        req=self.command('APPLY_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
        results=self.lab.concurrent([local_edit_sql(req),submit_sql(self.select(self.after,self.refv))],role='d5_lab_admin')
        self.assertEqual(results[1]['status'],'OK');self.assertIn(results[0]['status'],('OK','CONFLICT'))
        if results[0]['status']=='CONFLICT':self.assertEqual(results[0]['code'],'REFERENCE_VERSION_CONFLICT')
        # A revoke uses the same D5 mutex and must serialize with APPLY.
        self.tid,self.tkey=uid(),uid();self.setup_change(key='PT-02');_,p=self.lpropose();_,pkg=self.lpackage(p)
        req=self.command('APPLY_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
        review=self.command('REVIEW_LOCAL_EDIT_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],expected_version=1,decision='REJECT',reviewer_label='fixture',reason='Concurrent revoke')
        results=self.lab.concurrent([local_edit_sql(req),local_edit_sql(review)],role='d5_lab_admin')
        self.assertEqual(results[1]['status'],'OK');self.assertIn(results[0]['status'],('OK','CONFLICT'))

    def test_LE25_mixed_choices_atomicity_abort_and_late_failure(self):
        present=body()+b'| PT-02 | Second | x | x | - | OPEN | no | inert |\n'
        after=body('Remote')+b'| PT-02 | Second new | x | x | - | OPEN | no | inert |\n'
        self.initial(present);i1=self.iid;t1=self.tid;other=uid();self.intent('PT-02',other,uid());i2=self.iid
        _,b1=self.bpropose(iid=i1);_,b2=self.bpropose('PT-02',i2);_,bpkg=self.bpackage(b1,b2);self.bapply(bpkg)
        self.stage(present,after);self.iid=i1;self.key='PT-01';self.local();_,p1=self.lpropose()
        self.iid=i2;self.tid=other;self.key='PT-02';self.local('Local second');_,p2=self.lpropose(choice='KEEP_LOCAL');_,pkg=self.lpackage(p1,p2)
        self.lab.sql(f"UPDATE public.tasks SET urgency=2 WHERE id='{other}';");before=self.resolution_state()
        self.assertEqual(self.lapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT');self.assertEqual(self.resolution_state(),before)
        self.lab.sql(f"UPDATE public.tasks SET urgency=0 WHERE id='{other}';");before=self.resolution_state()
        req=self.command('APPLY_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256']);self.lab.abort_after(local_edit_sql(req))
        self.assertEqual(self.resolution_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        fault="""BEGIN;CREATE FUNCTION pg_temp.local_edit_fault() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic failure after local resolution effects'; END $$;
        CREATE TRIGGER local_edit_fault BEFORE INSERT ON d5.local_edit_applications FOR EACH ROW EXECUTE FUNCTION pg_temp.local_edit_fault();"""
        error=self.denied(fault+local_edit_sql(req)+'COMMIT;',role='d5_lab_admin');self.assertIn('synthetic failure after local resolution effects',error)
        self.assertEqual(self.resolution_state(),before);self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.scalar(f"SELECT bool_and(version=1) FROM d5.task_mapping_heads WHERE intent_id IN ('{i1}','{i2}');"),'t')
        old_second=self.task();self.assertEqual(self.lapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old_second);self.assertEqual(self.task(t1)['title'],'Remote')

    def test_LE26_lost_response_restart_CLI(self):
        self.setup_change();_,p=self.lpropose();_,pkg=self.lpackage(p);req=self.command('APPLY_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
        self.lab.sql(local_edit_sql(req),role='d5_applier');self.lab.restart();r=self.reader.read_command(req['command_id']);self.assertEqual(self.lsend(req),r)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'request.json';path.write_text(json.dumps(req))
            run=subprocess.run([sys.executable,'-m','source_ingest.local_edit','--container',self.lab.container,'--request',str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(json.loads(run.stdout),r)
            path.write_text('{"action":"x","action":"y"}')
            run=subprocess.run([sys.executable,'-m','source_ingest.local_edit','--container',self.lab.container,'--request',str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,1)
        self.assertEqual(self.task()['row_version'],1)

    def test_LE27_provenance_exact_reuse_append_only(self):
        self.setup_change();_,p=self.lpropose(choice='KEEP_LOCAL');m=p['manifest'];locator=m['source_change']['after']['row']['source_locator']
        self.lab.sql(f"INSERT INTO d2.task_sources VALUES('{self.tid}','{m['after_revision_id']}',{sql_text(locator)},'{self.doc}','{self.pid}');")
        before=self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';")
        _,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],'Local')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),before)
        self.denied(f"UPDATE d2.task_sources SET source_locator='forged' WHERE task_id='{self.tid}';",role='d5_lab_admin')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}' AND revision_id='{m['after_revision_id']}' AND source_locator={sql_text(locator)};"),'1')
        self.assertIsNone(self.lreader.artifact(uid(),self.doc,'proposal',p['proposal_id']))

    def test_LE28_KEEP_LOCAL_needs_new_resolution_next_change(self):
        self.setup_change();_,p=self.lpropose(choice='KEEP_LOCAL');_,pkg=self.lpackage(p);first,result=self.lapply(pkg)
        self.stage(body('Remote'),body('Next'));self.assertEqual(self.propose()[1]['code'],'LOCAL_EDIT_CONFLICT')
        _,p=self.lpropose(False,choice='KEEP_LOCAL');self.assertEqual(p['manifest']['before_projection']['title'],'Remote')
        self.assertEqual(p['manifest']['mapping_version'],2);_,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.task()['title'],'Local');self.assertEqual(self.task()['row_version'],0)
        self.assertEqual(self.scalar(f"SELECT projection->>'title' FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"),'Next')
        self.assertEqual(self.lsend(first),result)

    def test_LE29_USE_SOURCE_and_convergence_continue_I8(self):
        for n,(choice,title) in enumerate([('USE_SOURCE','Remote'),('KEEP_LOCAL','Local')],1):
            key=f'PT-{n:02}';after=body(title,key=key)
            self.tid,self.tkey=uid(),uid();self.setup_change(after=after,key=key);_,p=self.lpropose(choice=choice);_,pkg=self.lpackage(p);self.lapply(pkg)
            self.stage(after,body('Next',key=key));_,p=self.propose(key);_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')
            self.stage(body('Next',key=key),body('Again',key=key));self.local('New local');self.assertEqual(self.propose(key)[1]['code'],'LOCAL_EDIT_CONFLICT')

    def test_LE30_absence_and_reappearance_do_not_bypass_local_guard(self):
        self.setup_change();_,p=self.lpropose(choice='KEEP_LOCAL');_,pkg=self.lpackage(p);self.lapply(pkg)
        self.absent(body('Remote'));self.returned(body('Returned'));self.assertEqual(self.rpropose()[1]['code'],'LOCAL_EDIT_CONFLICT')
        self.assertEqual(self.lpropose(False)[1]['code'],'PRESENT_CHANGED_ROW_REQUIRED')
        self.assertEqual(self.task()['title'],'Local')

    def test_LE31_locks_roles_and_D3_stale_basis(self):
        self.setup_change();_,p=self.lpropose();_,pkg=self.lpackage(p);req=self.command('APPLY_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
        for role in ('d5_writer','d5_reviewer','d5_reader'):
            self.denied(local_edit_sql(req),role)
        for role in ('d5_writer','d5_reviewer','d5_reader','d5_applier'):
            self.denied('UPDATE public.tasks SET urgency=0;',role);self.denied('SELECT d5.task_lock_boundary();',role)
        self.denied('SELECT d3.lock_state();','d5_applier')
        self.denied('BEGIN ISOLATION LEVEL REPEATABLE READ;'+local_edit_sql(req),'d5_applier')
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742001);SELECT pg_sleep(60);ROLLBACK;','local_edit_boundary')
        self.lab.wait_for(lambda:self.lab.active('local_edit_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,local_edit_sql(req),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.writer.submit(self.select(self.before,self.refv))['status'],'OK')
                self.lab.terminate('local_edit_boundary');self.assertEqual(json.loads(future.result(timeout=30).stdout)['code'],'REFERENCE_VERSION_CONFLICT')
        finally:self.lab.terminate('local_edit_boundary');blocker.communicate(timeout=5)
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742005);SELECT pg_sleep(60);ROLLBACK;','local_edit_boundary')
        self.lab.wait_for(lambda:self.lab.active('local_edit_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(self.lab.sql,local_edit_sql(dict(req,command_id=uid())),'d5_applier')
                self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.scalar("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.usename='d5_applier' AND l.locktype='advisory' AND l.granted AND l.objid IN (742001,742002);"),'2')
                cid=uid();capture=self.lab.session(f"SELECT d3.capture('{cid}','{{\"action\":\"CAPTURE\"}}');",'local_edit_capture')
                self.lab.wait_for(lambda:self.lab.active('local_edit_capture','advisory')==1)
                self.lab.terminate('local_edit_boundary');future.result(timeout=30);out,error=capture.communicate(timeout=10)
                self.assertEqual(capture.returncode,0,error);self.assertEqual(json.loads(out)['capture_id'],cid)
        finally:self.lab.terminate('local_edit_boundary');blocker.communicate(timeout=5)
        self.refv=self.head()['version'];_,fresh=self.lpropose(False);_,pkg=self.lpackage(fresh)
        plan=uid();self.lab.sql(self.plan_fixture(plan,True));old=self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';")
        before=self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');");self.assertEqual(self.lapply(pkg)[1]['status'],'OK')
        self.assertNotEqual(before,self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');"))
        self.assertEqual(self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';"),old)
        self.denied(f"UPDATE public.planning_runs SET solver_version='changed' WHERE id='{plan}';",role='d5_lab_admin')


    def test_LE32_no_new_tasks_or_operational_activation(self):
        self.setup_change();before=self.scalar(f"SELECT count(*) FROM public.tasks WHERE project_id='{self.pid}';")
        _,p=self.lpropose();_,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK')
        self.assertEqual(self.scalar(f"SELECT count(*) FROM public.tasks WHERE project_id='{self.pid}';"),before)
        self.assertEqual(self.scalar(f"SELECT d2.task_eligible('{self.tid}');"),'t');self.assertEqual(self.task()['status'],'BACKLOG')
        for table in ('public.operations','public.outbox_events','public.execution_attempts','d2.reservations','d2.plan_reservations','d4.deliveries'):
            self.assertEqual(self.scalar('SELECT count(*) FROM '+table+';'),'0')
        self.assertEqual(self.lab.catalog(),self.lab.v30_catalog);self.lab.assert_previous_functions();self.lab.assert_local_previous_functions()
