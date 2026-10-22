# SPDX-License-Identifier: GPL-3.0-only
"""IL01-IL36: isolated local resolution; no fabricated source comparisons."""
import concurrent.futures
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from .local_reappearance_scenarios import LocalReappearance
from .mapping_scenarios import body
from .postgres_scenarios import uid, PROFILE
from source_ingest.isolated_local_edit import ENTRIES, IsolatedLocalEditClient, isolated_local_edit_sql
from source_ingest.postgres import sql_text, submit_sql
from source_ingest.preview import canonical
from source_ingest.task_mapping import mapping_sql
from source_ingest.local_edit import local_edit_sql


class IsolatedLocalEdit(LocalReappearance):
    def setUp(self):
        super().setUp()
        self.owriter=IsolatedLocalEditClient(self.lab.container,'d5_writer')
        self.oreviewer=IsolatedLocalEditClient(self.lab.container,'d5_reviewer')
        self.oreader=IsolatedLocalEditClient(self.lab.container)
        self.oapplier=IsolatedLocalEditClient(self.lab.container,'d5_applier')

    def osend(self,req,row=None):
        return {'d5_writer':self.owriter,'d5_reviewer':self.oreviewer,'d5_applier':self.oapplier}[ENTRIES[req['action']][1]].submit_isolated_local_edit(req,row)

    def choose(self,data=None,select=True):
        data=self.source if data is None else data
        _,r=self.ingest(self.capture(data));self.oid=r['observation_id']
        self.snapshot=self.oreader.snapshot(self.pid,self.doc,self.oid)[0]
        self.refv=self.head()['version']
        if select:self.refv=self.writer.submit(self.select(self.oid,self.refv))['version_at_commit']

    def setup_isolated(self,key='PT-01',origin='bootstrap',edit=True,data=None):
        self.key=key;self.source=body(key=key) if data is None else data
        if origin=='bootstrap':
            self.initial(self.source,key);_,p=self.bpropose(key);_,pkg=self.bpackage(p);req,r=self.bapply(pkg)
        elif origin=='mapping':
            self.stage(body('Old',key=key),self.source);self.intent(key);_,p=self.propose(key);_,pkg=self.package(p);req,r=self.apply(pkg)
        elif origin=='adoption':
            self.ainitial(self.source,key,title='Local' if edit else 'Title');_,p=self.apropose();_,pkg=self.apackage(p);req,r=self.aapply(pkg)
        elif origin in ('reappearance','local_reappearance'):
            self.cycle(key=key,returning=self.source,local_edit=origin=='local_reappearance')
            _,p=self.rpropose() if origin=='reappearance' else self.xpropose(choice='KEEP_LOCAL')
            _,pkg=self.rpackage(p) if origin=='reappearance' else self.xpackage(p)
            req,r=self.rapply(pkg) if origin=='reappearance' else self.xapply(pkg)
        elif origin=='local_edit':
            self.setup_change(key=key,present=body('Old',key=key),after=self.source);_,p=self.lpropose(choice='KEEP_LOCAL');_,pkg=self.lpackage(p);req,r=self.lapply(pkg)
        self.assertEqual(r['status'],'OK');self.head_aid=req['command_id'];self.head_pid=p['proposal_id']
        self.choose()
        if edit:self.local()

    def orequest(self,**extra):
        row=next((r for r in self.snapshot['proposals'] if r['source_key']==self.key),None);payload=canonical(row)
        version=int(self.scalar(f"SELECT version FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';"))
        req=self.command('PREPARE_ISOLATED_LOCAL_EDIT_TASK',intent_id=self.iid,source_key=self.key,observation_id=self.oid,
            content_sha256=self.snapshot['content_sha256'],preview_sha256=hashlib.sha256(canonical(self.snapshot)).hexdigest(),snapshot_row_sha256=hashlib.sha256(payload).hexdigest(),
            expected_reference_version=self.refv,expected_mapping_version=version,head_application_command_id=self.head_aid,head_proposal_id=self.head_pid,
            choice='USE_SOURCE',reason='Synthetic review of isolated local text and unchanged source')
        return dict(req,**extra),payload

    def opropose(self,**extra):
        req,row=self.orequest(**extra);return req,self.osend(req,row)

    def oaccept(self,p,version=0,decision='ACCEPT'):
        req=self.command('REVIEW_ISOLATED_LOCAL_EDIT_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],expected_version=version,
            decision=decision,reviewer_label='synthetic-reviewer',reason='Review entire isolated local choice and head proof')
        return req,self.osend(req)

    def opackage(self,*proposals,accept=True):
        pins=[]
        for p in proposals:
            if accept:
                _,r=self.oaccept(p);pin=dict(proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],review_command_id=r['command_id'],review_version=r['version_at_commit'])
            else:
                data=self.oreader.artifact(self.pid,self.doc,'proposal',p['proposal_id']);pin={k:data[k] for k in ('proposal_id','manifest_sha256','review_command_id','review_version')};pin['review_command_id']=pin['review_command_id'] or uid()
            pins.append(pin)
        req=self.command('PACKAGE_ISOLATED_LOCAL_EDIT_TASKS',items=sorted(pins,key=lambda x:x['proposal_id']));return req,self.osend(req)

    def oapply(self,pkg):
        req=self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256']);count=self.scalar('SELECT count(*) FROM public.tasks;')
        r=self.osend(req);self.assertEqual(self.scalar('SELECT count(*) FROM public.tasks;'),count)
        return req,r

    def ostate(self):
        return self.scalar(f"SELECT jsonb_build_object('version',version,'source_basis',source_basis,'digest',source_basis_sha256,'projection',projection) FROM d5.task_mapping_heads WHERE intent_id='{self.iid}';")

    def test_IL01_prepare_origins_no_protected_writes(self):
        for n,origin in enumerate(('bootstrap','mapping','adoption','reappearance','local_edit','local_reappearance'),1):
            self.tid,self.tkey=uid(),uid();self.setup_isolated(key=f'PT-{n:02}',origin=origin)
            before=self.lab.protected_state();head=self.ostate();req,p=self.opropose()
            self.assertEqual(p['status'],'OK');self.assertEqual(self.osend(req),p);self.assertEqual(self.lab.protected_state(),before);self.assertEqual(self.ostate(),head)
            self.assertTrue(p['manifest']['head_proof']['source_present']);self.assertEqual(p['manifest']['before_projection'],p['manifest']['after_projection'])

    def test_IL02_scope_identity_and_unmaterialized(self):
        self.setup_isolated();req,row=self.orequest()
        for extra in (dict(intent_id=uid()),dict(project_id=uid()),dict(document_id=uid()),dict(source_key='other')):
            self.assertEqual(self.owriter.query(isolated_local_edit_sql(dict(req,command_id=uid(),**extra),row))['code'],'INTENT_SCOPE_CONFLICT')
        self.lab.sql(f"UPDATE public.tasks SET task_key='changed' WHERE id='{self.tid}';");self.assertEqual(self.opropose()[1]['code'],'TARGET_IDENTITY_CONFLICT')
        self.tid,self.tkey=uid(),uid();self.intent('PT-02');self.key='PT-02';self.choose(body(key=self.key));req,row=self.orequest()
        self.assertEqual(self.owriter.query(isolated_local_edit_sql(req,row))['code'],'MAPPING_VERSION_CONFLICT')

    def test_IL03_no_divergence_or_late_convergence(self):
        self.setup_isolated(edit=False);self.assertEqual(self.opropose()[1]['code'],'NO_LOCAL_EDIT');self.local('Title',bump=True)
        self.assertEqual(self.opropose()[1]['code'],'NO_LOCAL_EDIT');self.local();_,p=self.opropose();_,pkg=self.opackage(p);self.local('Title')
        self.assertEqual(self.oapply(pkg)[1]['code'],'NO_LOCAL_EDIT')

    def test_IL04_current_complete_local_snapshot(self):
        self.setup_isolated(origin='adoption')
        for bump in (False,True):
            self.local('Current text',description=None,bump=bump);_,p=self.opropose();self.assertEqual(p['manifest']['target'],self.task())
            self.assertIsNone(p['manifest']['local_projection']['description'])

    def test_IL05_no_comparison_or_I5_decision_created(self):
        self.setup_isolated();tables=('d5.comparisons','d5.review_items','d5.row_decisions')
        before={t:self.scalar('SELECT count(*) FROM '+t+';') for t in tables};_,p=self.opropose();_,pkg=self.opackage(p)
        self.assertEqual(self.oapply(pkg)[1]['status'],'OK')
        self.assertEqual({t:self.scalar('SELECT count(*) FROM '+t+';') for t in tables},before)
        self.assertNotIn('comparison_id',p['manifest']);self.assertNotIn('source_decision_command_id',p['manifest'])

    def test_IL06_entire_source_basis_must_match(self):
        self.setup_isolated()
        variants=[body(status='DONE'),body(annotation=' approved'),body(struck=True),body().replace(b'approved',b'unverified'),
                  body().replace(b'`example`',b'component'),body().replace(b'| - |',b'| blocked |')]
        for data in variants:
            self.choose(data);self.assertEqual(self.opropose(choice='KEEP_LOCAL')[1]['code'],'SOURCE_BASE_CONFLICT')
        self.choose();self.assertEqual(self.opropose()[1]['status'],'OK')

    def test_IL07_equal_semantic_row_different_bytes_and_locator(self):
        self.setup_isolated();self.choose(b'\n\n'+self.source);_,p=self.opropose();m=p['manifest']
        self.assertNotEqual(m['revision_id'],m['head_proof']['manifest']['revision_id']);self.assertEqual(m['snapshot_row']['line_start'],5)
        _,pkg=self.opackage(p);self.assertEqual(self.oapply(pkg)[1]['status'],'OK')

    def test_IL08_applied_absence_cannot_be_bypassed(self):
        self.setup_isolated();old_a,old_p=self.head_aid,self.head_pid
        self.absent(self.source);self.head_aid,self.head_pid=self.abs_aid,self.abs_pid;self.choose(self.source)
        before=self.ostate()
        for choice in ('USE_SOURCE','KEEP_LOCAL'):
            self.assertEqual(self.opropose(choice=choice)[1]['code'],'APPLIED_ABSENCE_BLOCKED')
            self.assertEqual(self.opropose(choice=choice,head_application_command_id=old_a,head_proposal_id=old_p)[1]['code'],'HEAD_PROOF_VERSION_CONFLICT')
        self.assertEqual(self.ostate(),before)

    def test_IL09_proof_chain_scope_version_and_receipt(self):
        self.setup_isolated();req,row=self.orequest()
        for extra in (dict(head_application_command_id=uid()),dict(head_proposal_id=uid()),dict(head_application_command_id=self.head_pid)):
            bad=dict(req,command_id=uid(),**extra)
            with self.assertRaises(ValueError):self.osend(bad,row)
            self.assertEqual(self.owriter.query(isolated_local_edit_sql(bad,row))['code'],'CONFIRMED_HEAD_REQUIRED')
        proof=self.oreader.head_proof(self.pid,self.doc,self.iid,self.head_aid,self.head_pid)
        self.assertEqual(proof['receipt']['status'],'OK');self.assertEqual(proof['mapping_version_after'],1)
        self.assertEqual(proof['review_pin']['manifest_sha256'],proof['manifest_sha256'])
        fake=uid()
        negative=f"""BEGIN;
        INSERT INTO d5.commands(command_id,request,request_sha256,response)
        SELECT '{fake}',q,encode(public.digest('d5.source-command.v1:'||q::text,'sha256'),'hex'),'{{"status":"CONFLICT"}}'
        FROM (SELECT request||jsonb_build_object('command_id','{fake}') q FROM d5.commands WHERE command_id='{self.head_aid}') s;
        INSERT INTO d5.bootstrap_applications(package_sha256,command_id,result)
        SELECT package_sha256,'{fake}','{{"status":"CONFLICT"}}' FROM d5.bootstrap_applications WHERE command_id='{self.head_aid}';
        SELECT coalesce(d5.read_isolated_local_head_proof('{self.pid}','{self.doc}','{self.iid}','{fake}','{self.head_pid}'),'null'::jsonb);ROLLBACK;"""
        # Avoid the existing package PK with a separate, correctly hashed empty package.
        empty=f"d5.task_hash('d5.bootstrap-task-package.v1',jsonb_build_object('project_id','{self.pid}','document_id','{self.doc}','items','[]'::jsonb))"
        negative=negative.replace("INSERT INTO d5.bootstrap_applications",f"INSERT INTO d5.bootstrap_packages VALUES({empty},'{self.pid}','{self.doc}','[]');INSERT INTO d5.bootstrap_applications")
        negative=negative.replace("SELECT package_sha256,'",f"SELECT {empty},'")
        negative=negative.replace(f"'command_id','{fake}'",f"'command_id','{fake}','package_sha256',{empty}")
        self.assertIsNone(json.loads(self.lab.sql(negative).stdout.strip()))
        # Historical chain including deliberately incoherent CONFLICT receipt is checked by the unchanged I12 reader.
        self.setUp();self.test_RP05_proof_scope_and_incoherent_receipt()

    def test_IL10_adoption_present_cycles_and_isolated_head_chain(self):
        self.setup_isolated(origin='adoption');_,p=self.opropose(choice='KEEP_LOCAL');_,pkg=self.opackage(p);req,r=self.oapply(pkg)
        self.assertEqual(r['status'],'OK');self.oaccept(p,1,'REJECT');self.head_aid,self.head_pid=req['command_id'],p['proposal_id'];_,p=self.opropose(choice='KEEP_LOCAL')
        self.assertEqual(p['manifest']['head_proof']['kind'],'isolated_local_edit');_,pkg=self.opackage(p);req,r=self.oapply(pkg);self.assertEqual(r['status'],'OK')
        self.head_aid,self.head_pid=req['command_id'],p['proposal_id'];self.assertEqual(self.opropose()[1]['status'],'OK')
        self.setUp();self.setup_isolated(origin='local_reappearance');self.assertEqual(self.opropose()[1]['status'],'OK')

    def test_IL11_missing_duplicate_blocked_snapshot_and_profile(self):
        self.setup_isolated()
        for data in (body(key='PT-99'),self.source+b'| PT-99 | x | x | x | - | OPEN | no | inert |\n| PT-99 | dup | x | x | - | OPEN | no | inert |\n',self.source+b'| bad | row |\n'):
            _,r=self.ingest(self.capture(data))
            req,row=self.orequest(observation_id=r['observation_id'],content_sha256=hashlib.sha256(data).hexdigest(),preview_sha256=r['preview_sha256'])
            with self.assertRaises(ValueError):self.osend(req)
            code=self.owriter.query(isolated_local_edit_sql(req,row))['code'];self.assertIn(code,('OBSERVATION_BLOCKED','SOURCE_ROW_NOT_UNIQUE'))
        _,r=self.ingest(self.capture(self.source,profile='task-register.v1'));req,row=self.orequest(observation_id=r['observation_id'],preview_sha256=r['preview_sha256'])
        self.assertEqual(self.owriter.query(isolated_local_edit_sql(req,row))['code'],'OBSERVATION_SCOPE_CONFLICT')

    def test_IL12_reference_version_and_ABA(self):
        self.setup_isolated();self.assertEqual(self.opropose(expected_reference_version=self.refv+1)[1]['code'],'REFERENCE_VERSION_CONFLICT')
        _,p=self.opropose();_,pkg=self.opackage(p);_,r=self.ingest(self.capture(body('Other')))
        self.writer.submit(self.select(r['observation_id'],self.refv));self.writer.submit(self.select(self.oid,self.refv+1));self.assertEqual(self.oapply(pkg)[1]['code'],'REFERENCE_VERSION_CONFLICT')

    def test_IL13_bytes_hash_and_provenance_integrity(self):
        self.setup_isolated();req,row=self.orequest()
        for field in ('content_sha256','preview_sha256','snapshot_row_sha256'):
            bad=dict(req,command_id=uid(),**{field:'0'*64})
            with self.assertRaises(ValueError):self.osend(bad,row)
            if field=='snapshot_row_sha256':self.denied(isolated_local_edit_sql(bad,row))
            else:self.assertIn(self.owriter.query(isolated_local_edit_sql(bad,row))['code'],('SOURCE_HASH_CONFLICT','OBSERVATION_SCOPE_CONFLICT'))
        self.denied(isolated_local_edit_sql(req,row+b' '))

    def test_IL14_literal_ID_unicode_and_evidence(self):
        key='LONG-'+'1'*5000;text='Árbol **raw** \\| `literal`';self.setup_isolated(key=key,data=body(text,'ñ [x](https://example.invalid)',key=key,struck=True,annotation=' source claim'))
        _,p=self.opropose();_,pkg=self.opackage(p);self.assertEqual(self.oapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],text)
        self.assertTrue(p['manifest']['snapshot_row']['source_struck']);self.assertEqual(p['manifest']['intent']['source_key'],key)

    def test_IL15_projection_validity_NULL_and_literal_description(self):
        self.setup_isolated();self.local(' \u00a0 ');self.assertEqual(self.opropose()[1]['code'],'INVALID_PROJECTION')
        self.local(description=None);old=self.task();_,p=self.opropose(choice='KEEP_LOCAL');_,pkg=self.opackage(p);self.assertEqual(self.oapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old)
        for n,description in enumerate(('','-'),2):
            self.tid,self.tkey=uid(),uid();self.setup_isolated(key=f'PT-{n:02}',data=body(objective=description,key=f'PT-{n:02}'))
            _,p=self.opropose();_,pkg=self.opackage(p);applied,result=self.oapply(pkg);self.assertEqual(result['status'],'OK');self.assertEqual(self.task()['description'],description);self.head_aid,self.head_pid=applied['command_id'],p['proposal_id']
        # A bad source is rejected before adoption/import; isolated selection with invalid source remains blocked.
        self.choose(body(' \u00a0 ',key=self.key));self.assertEqual(self.opropose(choice='KEEP_LOCAL')[1]['code'],'INVALID_PROJECTION')

    def test_IL16_reason_choice_closed_request(self):
        self.setup_isolated()
        for value in ('',' \u00a0 ','x\n','x'*1025):self.assertEqual(self.opropose(reason=value)[1]['code'],'RESOLUTION_CHOICE_REQUIRED')
        req,row=self.orequest()
        for fields in (dict(reason=None),dict(choice='MERGE'),dict(force=True),dict(result_projection={'title':'manual'})):
            bad=dict(req,command_id=uid(),**fields)
            if fields.get('choice')=='MERGE':self.assertEqual(self.owriter.query(isolated_local_edit_sql(bad,row))['status'],'CONFLICT')
            else:self.denied(isolated_local_edit_sql(bad,row))

    def test_IL17_own_review_not_previous_domains(self):
        self.setup_isolated();_,p=self.opropose();self.assertEqual(self.opackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        req=self.command('REVIEW_LOCAL_EDIT_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],expected_version=0,decision='ACCEPT',reviewer_label='fixture',reason='wrong domain')
        self.assertEqual(self.lreviewer.query(local_edit_sql(req))['code'],'MANIFEST_SCOPE_CONFLICT')
        _,p2=self.opropose(choice='KEEP_LOCAL');self.oaccept(p2);self.assertEqual(self.opackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')

    def test_IL18_review_reject_and_ABA(self):
        self.setup_isolated();_,p=self.opropose();self.oaccept(p,decision='REJECT');self.assertEqual(self.opackage(p,accept=False)[1]['code'],'MANIFEST_NOT_ACCEPTED')
        self.oaccept(p,1);_,pkg=self.opackage(p,accept=False);self.oaccept(p,2,'REJECT');self.oaccept(p,3)
        self.assertEqual(self.oapply(pkg)[1]['code'],'ISOLATED_LOCAL_EDIT_REVIEW_CONFLICT')

    def test_IL19_manifest_immutable_and_reconstructed(self):
        self.setup_isolated();_,p=self.opropose();self.denied(f"UPDATE d5.isolated_local_edit_proposals SET manifest=manifest||'{{\"choice\":\"KEEP_LOCAL\"}}' WHERE proposal_id='{p['proposal_id']}';",'d5_lab_admin')
        original=self.oreader.artifact;data=original(self.pid,self.doc,'proposal',p['proposal_id'])
        for field,value in [('choice','KEEP_LOCAL'),('last_applied_basis',{}),('after_projection',{}),('head_proof',{}),('target',{})]:
            changed=copy.deepcopy(data);changed['manifest'][field]=value;self.oreader.artifact=lambda *args:changed
            with self.assertRaises((ValueError,KeyError)):self.oreader.verify_manifest(self.pid,self.doc,p['proposal_id'],p['manifest_sha256'])
        self.oreader.artifact=original

    def test_IL20_USE_SOURCE_only_text_and_one_version(self):
        self.setup_isolated();self.lab.sql(f"UPDATE public.tasks SET urgency=3,deferred_count=2,deadline_at='2026-11-01' WHERE id='{self.tid}';");old=self.task()
        epic,other=uid(),uid()
        self.lab.sql(f"INSERT INTO public.epics(id,project_id,epic_key,title) VALUES('{epic}','{self.pid}','synthetic','Synthetic epic');INSERT INTO public.tasks(id,project_id,task_key,title) VALUES('{other}','{self.pid}','other','Other fixture');UPDATE public.tasks SET epic_id='{epic}' WHERE id='{self.tid}';INSERT INTO public.task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES('{other}','{self.tid}','SOFT');")
        old=self.task();dependency=self.scalar(f"SELECT to_jsonb(d) FROM public.task_dependencies d WHERE successor_task_id='{self.tid}';")
        _,p=self.opropose();_,pkg=self.opackage(p);_,r=self.oapply(pkg);new=self.task();self.assertEqual(r['status'],'OK')
        self.assertEqual(new['title'],'Title');self.assertEqual(new['row_version'],old['row_version']+1)
        self.assertEqual(self.scalar(f"SELECT to_jsonb(d) FROM public.task_dependencies d WHERE successor_task_id='{self.tid}';"),dependency)
        self.assertEqual({k:v for k,v in old.items() if k not in ('title','description','row_version')},{k:v for k,v in new.items() if k not in ('title','description','row_version')})

    def test_IL21_KEEP_LOCAL_no_UPDATE(self):
        self.setup_isolated();_,p=self.opropose(choice='KEEP_LOCAL');_,pkg=self.opackage(p);old=self.task()
        req=self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
        fault="BEGIN;CREATE FUNCTION pg_temp.no_isolated_update() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'unexpected UPDATE'; END $$;CREATE TRIGGER no_isolated_update BEFORE UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION pg_temp.no_isolated_update();"
        self.assertEqual(json.loads(self.lab.sql(fault+isolated_local_edit_sql(req)+'ROLLBACK;').stdout)['status'],'OK')
        self.assertEqual(self.oapply(pkg)[1]['status'],'OK');self.assertEqual(self.task(),old)

    def test_IL22_only_mapping_version_advances(self):
        for n,choice in enumerate(('USE_SOURCE','KEEP_LOCAL'),1):
            self.tid,self.tkey=uid(),uid();self.setup_isolated(key=f'PT-{n:02}');old=json.loads(self.ostate());_,p=self.opropose(choice=choice);_,pkg=self.opackage(p);_,r=self.oapply(pkg);new=json.loads(self.ostate())
            self.assertEqual(new.pop('version'),old.pop('version')+1);self.assertEqual(new,old);self.assertEqual(r['effects'][0]['mapping_version_after'],2)

    def test_IL23_unchanged_source_still_invalidates_old_packages(self):
        self.setup_isolated();self.stage(self.source,body('Remote'));_,remote=self.lpropose();_,rpkg=self.lpackage(remote)
        # stage selected a new but semantically equal before observation; isolate against that exact reference.
        self.oid=self.before;self.snapshot=self.oreader.snapshot(self.pid,self.doc,self.oid)[0];self.refv=self.head()['version']
        _,p=self.opropose(choice='KEEP_LOCAL');_,p2=self.opropose();_,pkg=self.opackage(p);_,pkg2=self.opackage(p2)
        self.assertEqual(self.oapply(pkg)[1]['status'],'OK');self.assertEqual(self.oapply(pkg2)[1]['code'],'MAPPING_VERSION_CONFLICT')
        self.assertEqual(self.lapply(rpkg)[1]['code'],'MAPPING_VERSION_CONFLICT')
        self.setUp();self.setup_isolated(edit=False);self.stage(self.source,body('Remote'));_,remote=self.propose();_,rpkg=self.package(remote)
        self.local();self.oid=self.before;self.snapshot=self.oreader.snapshot(self.pid,self.doc,self.oid)[0];_,p=self.opropose(choice='KEEP_LOCAL');_,pkg=self.opackage(p);self.oapply(pkg)
        self.assertEqual(self.apply(rpkg)[1]['code'],'INTENT_VERSION_CONFLICT')

    def test_IL24_CAS_edits_without_version_and_ABA(self):
        self.setup_isolated();_,p=self.opropose();_,pkg=self.opackage(p);self.local('Other')
        self.assertEqual(self.oapply(pkg)[1]['code'],'RESOLUTION_CONTENT_CONFLICT');self.local();self.lab.sql(f"UPDATE public.tasks SET urgency=4 WHERE id='{self.tid}';")
        self.assertEqual(self.oapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT');_,p=self.opropose();_,pkg=self.opackage(p);self.local('Other',bump=True);self.local(bump=True)
        self.assertEqual(self.oapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT')

    def test_IL25_state_operations_historical_plan_block(self):
        self.setup_isolated();plan=uid();fixtures=[f"SELECT d2.transition('{uid()}','{json.dumps(dict(entity_type='TASK',entity_id=self.tid,expected_version=0,actor='fixture',reason='negative',to='BLOCKED',**{'from':'BACKLOG'}))}');",f"INSERT INTO public.operations(task_id,operation_type,idempotency_key) VALUES('{self.tid}','SYNTHETIC','{uid()}');",self.plan_fixture(plan)+f"INSERT INTO public.schedule_entries(planning_run_id,task_id,resource_id,pool,priority_snapshot,state) VALUES('{plan}','{self.tid}','{self.lab.resource}','PLANNED','{{}}','CANCELLED');"]
        for choice in ('USE_SOURCE','KEEP_LOCAL'):
            _,p=self.opropose(choice=choice);_,pkg=self.opackage(p);req,row=self.orequest(choice=choice)
            for fixture in fixtures:
                for statement in (isolated_local_edit_sql(req,row),isolated_local_edit_sql(self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256']))):
                    r=self.lab.sql('BEGIN;'+fixture+statement+'ROLLBACK;');self.assertEqual(json.loads(r.stdout.splitlines()[-1])['code'],'TARGET_HAS_WORK_OR_STATE')
        self.assertEqual(self.scalar('SELECT count(*) FROM public.operations;'),'0')

    def test_IL26_explicit_package_limits_and_snapshot(self):
        self.setup_isolated();_,p=self.opropose();req,pkg=self.opackage(p)
        for items in ([],req['items']*2,req['items']*2001):self.denied(isolated_local_edit_sql(dict(req,command_id=uid(),items=items)))
        _,p2=self.opropose(choice='KEEP_LOCAL');_,review=self.oaccept(p2)
        pin=dict(proposal_id=p2['proposal_id'],manifest_sha256=p2['manifest_sha256'],review_command_id=review['command_id'],review_version=1)
        self.denied(isolated_local_edit_sql(dict(req,command_id=uid(),items=sorted(req['items']+[pin],key=lambda x:x['proposal_id']))))
        self.assertEqual(self.mapper.query(mapping_sql(dict(req,command_id=uid(),action='PACKAGE_TASK_PROPOSALS')))['code'],'MANIFEST_SCOPE_CONFLICT')
        self.tid,self.tkey=uid(),uid();self.setup_isolated(key='PT-02');_,second=self.opropose();_,review=self.oaccept(second)
        secondpin=dict(proposal_id=second['proposal_id'],manifest_sha256=second['manifest_sha256'],review_command_id=review['command_id'],review_version=1)
        self.denied(isolated_local_edit_sql(dict(req,command_id=uid(),items=sorted(req['items']+[secondpin],key=lambda x:x['proposal_id']))))

    def test_IL27_real_concurrent_packages_one_head_winner(self):
        self.setup_isolated();_,p=self.opropose(choice='KEEP_LOCAL');_,p2=self.opropose();_,pkg=self.opackage(p);_,pkg2=self.opackage(p2)
        requests=[self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=x['package_sha256']) for x in (pkg,pkg2)]
        r=self.lab.concurrent([isolated_local_edit_sql(q) for q in requests],role='d5_applier');self.assertEqual(sorted(x['status'] for x in r),['CONFLICT','OK']);self.assertEqual(json.loads(self.ostate())['version'],2)
        self.setUp();self.setup_isolated();self.stage(self.source,body(key='PT-99'));_,absence=self.propose();_,apkg=self.package(absence)
        self.oid=self.before;self.snapshot=self.oreader.snapshot(self.pid,self.doc,self.oid)[0];_,p=self.opropose(choice='KEEP_LOCAL');_,pkg=self.opackage(p)
        areq=self.command('APPLY_TASK_PROPOSALS',package_sha256=apkg['package_sha256']);oreq=self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
        r=self.lab.concurrent([mapping_sql(areq),isolated_local_edit_sql(oreq)],role='d5_applier');self.assertEqual(sorted(x['status'] for x in r),['CONFLICT','OK']);self.assertEqual(json.loads(self.ostate())['version'],2)
        if r[0]['status']=='OK':
            self.head_aid,self.head_pid=areq['command_id'],absence['proposal_id'];self.assertEqual(self.opropose()[1]['code'],'APPLIED_ABSENCE_BLOCKED')

    def test_IL28_concurrent_review_reference_and_current_check(self):
        self.setup_isolated();_,p=self.opropose();_,pkg=self.opackage(p)
        req=self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256']);review=self.command('REVIEW_ISOLATED_LOCAL_EDIT_TASK',proposal_id=p['proposal_id'],manifest_sha256=p['manifest_sha256'],expected_version=1,decision='REJECT',reviewer_label='fixture',reason='Concurrent revoke')
        r=self.lab.concurrent([isolated_local_edit_sql(req),isolated_local_edit_sql(review)],role='d5_lab_admin');self.assertEqual(r[1]['status'],'OK');self.assertIn(r[0]['status'],('OK','CONFLICT'))
        self.setUp();self.setup_isolated();_,p=self.opropose();_,pkg=self.opackage(p);req=self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
        r=self.lab.concurrent([isolated_local_edit_sql(req),submit_sql(self.select(self.oid,self.refv))],role='d5_lab_admin');self.assertEqual(r[1]['status'],'OK');self.assertIn(r[0]['status'],('OK','CONFLICT'))

    def test_IL29_mixed_atomicity_abort_and_late_failure(self):
        present=body()+b'| PT-02 | Second | x | x | - | OPEN | no | inert |\n'
        self.initial(present);i1=self.iid;t1=self.tid;other=uid();self.intent('PT-02',other,uid());i2=self.iid
        _,b1=self.bpropose(iid=i1);_,b2=self.bpropose('PT-02',i2);_,bpkg=self.bpackage(b1,b2);br,r=self.bapply(bpkg);self.assertEqual(r['status'],'OK');self.head_aid=br['command_id'];self.source=present;self.choose()
        self.iid=i1;self.tid=t1;self.key='PT-01';self.head_pid=b1['proposal_id'];self.local();_,p1=self.opropose()
        self.iid=i2;self.tid=other;self.key='PT-02';self.head_pid=b2['proposal_id'];self.local('Second local');_,p2=self.opropose(choice='KEEP_LOCAL');_,pkg=self.opackage(p1,p2)
        self.lab.sql(f"UPDATE public.tasks SET urgency=2 WHERE id='{other}';");old=self.resolution_state();self.assertEqual(self.oapply(pkg)[1]['code'],'TARGET_CAS_CONFLICT');self.assertEqual(self.resolution_state(),old)
        self.lab.sql(f"UPDATE public.tasks SET urgency=0 WHERE id='{other}';");old=self.resolution_state();req=self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256']);self.lab.abort_after(isolated_local_edit_sql(req))
        self.assertEqual(self.resolution_state(),old);self.assertIsNone(self.reader.read_command(req['command_id']))
        fault="BEGIN;CREATE FUNCTION pg_temp.isolated_fault() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic late isolated failure'; END $$;CREATE TRIGGER isolated_fault BEFORE INSERT ON d5.isolated_local_edit_applications FOR EACH ROW EXECUTE FUNCTION pg_temp.isolated_fault();"
        self.assertIn('synthetic late isolated failure',self.denied(fault+isolated_local_edit_sql(req)+'COMMIT;','d5_lab_admin'));self.assertEqual(self.resolution_state(),old);self.assertIsNone(self.reader.read_command(req['command_id']))
        self.assertEqual(self.oapply(pkg)[1]['status'],'OK');self.assertEqual(self.task()['title'],'Second local');self.assertEqual(self.task(t1)['title'],'Title')

    def test_IL30_replay_never_restores_and_global_commands(self):
        self.setup_isolated();_,p=self.opropose();_,pkg=self.opackage(p);req,r=self.oapply(pkg);self.local('Later',bump=True)
        self.assertEqual(self.osend(req),r);self.assertEqual(self.osend(dict(req,command_id=uid()))['status'],'ALREADY_APPLIED');self.assertEqual(self.task()['title'],'Later')
        self.assertEqual(self.oapplier.query(isolated_local_edit_sql(dict(req,package_sha256='0'*64)))['code'],'COMMAND_CONTENT_CONFLICT')
        self.assertEqual(self.applier.query(mapping_sql(dict(req,action='APPLY_TASK_PROPOSALS')))['code'],'COMMAND_CONTENT_CONFLICT')

    def test_IL31_lost_response_restart_and_CLI(self):
        self.setup_isolated();_,p=self.opropose();_,pkg=self.opackage(p);req=self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256']);self.lab.sql(isolated_local_edit_sql(req),'d5_applier');self.lab.restart();r=self.reader.read_command(req['command_id'])
        self.assertEqual(self.osend(req),r)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'request.json';path.write_text(json.dumps(req));command=[sys.executable,'-m','source_ingest.isolated_local_edit','--container',self.lab.container,'--request',str(path)]
            run=subprocess.run(command,capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(json.loads(run.stdout),r)
            path.write_text('{"action":"x","action":"y"}');self.assertEqual(subprocess.run(command,capture_output=True,text=True).returncode,1)

    def test_IL32_provenance_reuse_append_only(self):
        self.setup_isolated();_,p=self.opropose(choice='KEEP_LOCAL');m=p['manifest'];old=self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';")
        req,row=self.orequest();forged=json.loads(row);forged['source_locator']='sha256:forged#L1';bad=canonical(forged)
        self.assertEqual(self.owriter.query(isolated_local_edit_sql(dict(req,snapshot_row_sha256=hashlib.sha256(bad).hexdigest()),bad))['code'],'SNAPSHOT_ROW_CONFLICT')
        _,pkg=self.opackage(p);self.assertEqual(self.oapply(pkg)[1]['status'],'OK');self.assertEqual(self.scalar(f"SELECT count(*) FROM d2.task_sources WHERE task_id='{self.tid}';"),old)
        self.assertEqual(self.task()['title'],'Local');self.denied(f"DELETE FROM d2.task_sources WHERE task_id='{self.tid}';",'d5_lab_admin')
        self.assertIsNone(self.oreader.artifact(uid(),self.doc,'proposal',p['proposal_id']))

    def test_IL33_future_I8_I14_and_isolated_choices(self):
        for n,choice in enumerate(('USE_SOURCE','KEEP_LOCAL'),1):
            self.tid,self.tkey=uid(),uid();self.setup_isolated(key=f'PT-{n:02}');_,p=self.opropose(choice=choice);_,pkg=self.opackage(p);req,r=self.oapply(pkg);self.assertEqual(r['status'],'OK')
            if choice=='KEEP_LOCAL':
                self.head_aid,self.head_pid=req['command_id'],p['proposal_id'];_,again=self.opropose();_,againpkg=self.opackage(again);self.assertEqual(self.oapply(againpkg)[1]['status'],'OK');self.local()
            self.stage(self.source,body('Next',key=self.key))
            if choice=='KEEP_LOCAL':
                self.assertEqual(self.propose(self.key)[1]['code'],'LOCAL_EDIT_CONFLICT');_,p=self.lpropose(False,choice='KEEP_LOCAL');_,pkg=self.lpackage(p);self.assertEqual(self.lapply(pkg)[1]['status'],'OK')
            else:
                _,p=self.propose(self.key);_,pkg=self.package(p);self.assertEqual(self.apply(pkg)[1]['status'],'OK')

    def test_IL34_future_absence_reappearance_preserves_gates(self):
        self.setup_isolated();_,p=self.opropose(choice='KEEP_LOCAL');_,pkg=self.opackage(p);self.oapply(pkg);self.absent(self.source);self.returned(self.source)
        self.assertEqual(self.rpropose()[1]['code'],'LOCAL_EDIT_CONFLICT');_,p=self.xpropose(False,choice='KEEP_LOCAL');_,pkg=self.xpackage(p);self.assertEqual(self.xapply(pkg)[1]['status'],'OK')
        self.lab.assert_previous_functions();self.lab.assert_local_previous_functions();self.lab.assert_adoption_previous_functions();self.lab.assert_local_reappearance_previous_functions()

    def test_IL35_roles_locks_D3_and_published_plan(self):
        self.setup_isolated();_,p=self.opropose();_,pkg=self.opackage(p);req=self.command('APPLY_ISOLATED_LOCAL_EDIT_TASKS',package_sha256=pkg['package_sha256'])
        for role in ('d5_writer','d5_reviewer','d5_reader'):self.denied(isolated_local_edit_sql(req),role)
        for role in ('d5_writer','d5_reviewer','d5_reader','d5_applier'):
            self.denied('UPDATE public.tasks SET urgency=0;',role);self.denied('SELECT d5.task_lock_boundary();',role);self.denied('SELECT * FROM d5.isolated_local_edit_proposals;',role)
        self.denied('BEGIN ISOLATION LEVEL REPEATABLE READ;'+isolated_local_edit_sql(req),'d5_applier')
        blocker=self.lab.session('BEGIN;SELECT pg_advisory_xact_lock(742005);SELECT pg_sleep(60);ROLLBACK;','isolated_boundary');self.lab.wait_for(lambda:self.lab.active('isolated_boundary','PgSleep')==1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                f=pool.submit(self.lab.sql,isolated_local_edit_sql(req),'d5_applier');self.lab.wait_for(lambda:int(self.scalar("SELECT count(*) FROM pg_stat_activity WHERE usename='d5_applier' AND wait_event='advisory';"))==1)
                self.assertEqual(self.scalar("SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.usename='d5_applier' AND l.locktype='advisory' AND l.granted AND l.objid IN (742001,742002);"),'2')
                cid=uid();capture=self.lab.session(f"SELECT d3.capture('{cid}','{{\"action\":\"CAPTURE\"}}');",'isolated_capture');self.lab.wait_for(lambda:self.lab.active('isolated_capture','advisory')==1)
                self.lab.terminate('isolated_boundary');self.assertEqual(json.loads(f.result(timeout=30).stdout)['status'],'OK');out,error=capture.communicate(timeout=10);self.assertEqual(capture.returncode,0,error)
        finally:self.lab.terminate('isolated_boundary');blocker.communicate(timeout=5)
        self.local();proof=self.oreader.head_proof(self.pid,self.doc,self.iid,req['command_id'],p['proposal_id']);self.head_aid,self.head_pid=proof['application_command_id'],proof['proposal_id'];_,p=self.opropose();_,pkg=self.opackage(p)
        plan=uid();self.lab.sql(self.plan_fixture(plan,True));old=self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';");digest=self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');")
        self.assertEqual(self.oapply(pkg)[1]['status'],'OK');self.assertNotEqual(digest,self.scalar("SELECT encode(public.digest(d3.state_body()::text,'sha256'),'hex');"));self.assertEqual(self.scalar(f"SELECT to_jsonb(p) FROM public.planning_runs p WHERE id='{plan}';"),old)
        self.denied(f"UPDATE public.planning_runs SET solver_version='changed' WHERE id='{plan}';",'d5_lab_admin')

    def test_IL36_no_new_tasks_activation_and_catalog(self):
        self.setup_isolated();before=self.scalar('SELECT count(*) FROM public.tasks;');_,p=self.opropose();_,pkg=self.opackage(p);self.assertEqual(self.oapply(pkg)[1]['status'],'OK');self.assertEqual(self.scalar('SELECT count(*) FROM public.tasks;'),before)
        self.assertEqual(self.task()['status'],'BACKLOG')
        for table in ('public.operations','public.outbox_events','public.execution_attempts','d2.reservations','d2.plan_reservations','d4.deliveries'):self.assertEqual(self.scalar('SELECT count(*) FROM '+table+';'),'0')
        self.assertEqual(self.lab.catalog(),self.lab.v30_catalog);self.lab.assert_isolated_previous_functions()
