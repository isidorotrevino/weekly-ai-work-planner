# SPDX-License-Identifier: GPL-3.0-only
"""I36 implements I35: new R state authority, atomic local batches, per-TASK remote effects.

Synthetic only. Inspection contains full fixture bytes; summaries/receipts are public.
No I30 private restoration, T schema conversion, provider, SQL or execution authority.
"""
import base64
import hashlib
import os
from pathlib import Path
import shutil
import stat
import tempfile
import uuid

from .durable_store import Store,DurableError,fail,shape,integer,identifier,hash_id,canonical,decode,digest,copy,LIMITS
from .batch_fixture import validate_source,BatchError,SCHEMA,text
from .relational_planner import plan_batch,baseline,guard
from .durable_task_fixture import capcheck,CAPS


BOUNDS=dict(elements=32,declarations=64,entities=128,relations=256,sources=128,manifests=128,reviews=128,
            selected=16,bindings=16,remote_tasks=16,tickets=384,source_bytes=2097152,text_characters=8192,
            batch_bytes=4194304,projection_bytes=1048576,attempts=3,queries=6)
CLIENT_SCHEMA='d5.durable-relational-client.v1'
REMOTE_SCHEMA='d5.durable-relational-remote.v1'
PROJECTION_SCHEMA='d5.relational-projection-fixture.v1'
CAPABILITIES=dict(CAPS,release='relational-fixture-1')
STAGES=('SOURCE','BATCH','PROJECTION')


def config(project,document,workspace,remote_project,*,limits=None,bounds=None):
    return dict(project_id=project,document_id=document,workspace_id=workspace,remote_project_id=remote_project,
                path='RELATIONAL_FIXTURE',client_schema=CLIENT_SCHEMA,remote_schema=REMOTE_SCHEMA,
                instance='SYNTHETIC_RELATIONAL',limits=dict(LIMITS if limits is None else limits),
                bounds=dict(BOUNDS if bounds is None else bounds))


def valid_config(c):
    shape(c,('project_id','document_id','workspace_id','remote_project_id','path','client_schema','remote_schema','instance','limits','bounds'))
    for key in ('project_id','document_id','workspace_id','remote_project_id'):identifier(c[key])
    if (c['path']!='RELATIONAL_FIXTURE' or c['client_schema']!=CLIENT_SCHEMA or
        c['remote_schema']!=REMOTE_SCHEMA or c['instance']!='SYNTHETIC_RELATIONAL'):fail('R_NAMESPACE_REQUIRED')
    for key,defaults in (('limits',LIMITS),('bounds',BOUNDS)):
        shape(c[key],defaults)
        for name,maximum in defaults.items():
            if not 1<=integer(c[key][name],1)<=maximum:fail('INVALID_LIMIT')
    return copy(c)


def client_genesis(c):
    return dict(schema=CLIENT_SCHEMA,config=valid_config(c),tick=0,selected_source=None,source_generation=0,
                sources={},manifests={},reviews={},review_count=0,data_generation=0,
                data=dict(entities={},mappings={},relations={},bases={},entity_provenance={},relation_provenance={}),
                selection=None,selection_generation=0,bindings={},sends={},pending={})


def remote_genesis(c):
    return dict(schema=REMOTE_SCHEMA,config=valid_config(c),capabilities=copy(CAPABILITIES),entities={},keys={},tickets={})


def source_bytes(encoded,bounds):
    if type(encoded) is not str or len(encoded)>4*((bounds['source_bytes']+2)//3):fail('SOURCE_BUDGET')
    try:raw=base64.b64decode(encoded,validate=True)
    except (ValueError,TypeError):fail('SOURCE_ENCODING')
    if len(raw)>bounds['source_bytes'] or base64.b64encode(raw).decode()!=encoded:fail('SOURCE_BUDGET')
    try:value=validate_source(raw)
    except BatchError as ex:fail(str(ex))
    canonical(value)  # closed JSON scalar types, original source bytes remain unchanged
    if len(value['elements'])>bounds['elements'] or len(value['relations'])>bounds['declarations']:fail('SOURCE_ITEM_BUDGET')
    for item in value['elements']:
        for key in ('title','description'):
            if item[key] is not None and len(item[key])>bounds['text_characters']:fail('TEXT_BUDGET')
    return raw,value


def source_context(s):
    sid=s['selected_source']
    if sid is None or sid not in s['sources']:fail('SOURCE_REQUIRED')
    return dict(source_id=sid,source_generation=s['source_generation'])


def review_key(stage,mid):return stage+':'+mid


def accepted(s,stage,mid,version):
    integer(version,1)
    value=s['reviews'].get(review_key(stage,mid))
    if not value or value['version']!=version or value['decision']!='ACCEPT':fail('REVIEW_REQUIRED')
    return value


def manifest(s,stage,body):
    value=dict(schema='d5.relational-manifest.v1',stage=stage,**body)
    maximum=s['config']['bounds']['projection_bytes'] if stage=='PROJECTION' else s['config']['bounds']['batch_bytes']
    if len(canonical(value))>maximum:fail('MANIFEST_BUDGET')
    mid=digest(value)
    if mid not in s['manifests'] and len(s['manifests'])>=s['config']['bounds']['manifests']:fail('MANIFEST_BUDGET')
    s['manifests'][mid]=value
    return mid


def current_source(s,mid,version):
    m=s['manifests'].get(mid)
    if not m or m['stage']!='SOURCE' or m['context']!=source_context(s):fail('STALE_SOURCE')
    accepted(s,'SOURCE',mid,version)
    return m


def current_batch(s,m):
    current_source(s,m['source_manifest'],m['source_review'])
    if m['data_generation']!=s['data_generation'] or m['data_hash']!=digest(s['data']):fail('STALE_DATA')


def applied_batch(s,cid,rh):
    identifier(cid);hash_id(rh)
    r=s['receipts'].get(cid)
    if not r or r['request_sha256']!=rh or r['result'].get('outcome')!='BATCH_APPLIED':fail('BATCH_RECEIPT_REQUIRED')
    result=r['result'];m=s['manifests'][result['manifest_id']]
    accepted(s,'BATCH',result['manifest_id'],result['batch_review'])
    current_source(s,m['source_manifest'],m['source_review'])
    return r,m


def selection_current(s):
    v=s['selection']
    if v is None:fail('SELECTION_REQUIRED')
    r,m=applied_batch(s,v['batch_command'],v['batch_request'])
    if v['data_generation']!=s['data_generation'] or v['data_hash']!=digest(s['data']):fail('STALE_SELECTION')
    return v,r,m


def projection_current(s,m,review=None):
    v,_,_=selection_current(s)
    if (m['selection']!=v or m['selection_generation']!=s['selection_generation'] or
        m['task']!=s['data']['entities'].get(m['target_id']) or
        m['data_generation']!=s['data_generation'] or m['data_hash']!=digest(s['data']) or
        m['binding']!=s['bindings'].get(m['binding']['binding_id'])):fail('STALE_PROJECTION')
    # Exact revisions, not merely whichever ACCEPT is current.
    if m['batch_review']!=s['reviews'].get(review_key('BATCH',m['batch_manifest'])):fail('STALE_REVIEW')
    source=s['manifests'][m['batch_manifest']]
    current_source(s,source['source_manifest'],source['source_review'])
    guard(s['data'],m['target_id'])
    destinations={v['proof']['remote_id'] for v in s['sends'].values()
                  if v['binding_id']==m['binding']['binding_id'] and v['status']=='EFFECT_CONFIRMED'}
    own_confirmed=any(v['manifest_id']==digest(m) and v['status']=='EFFECT_CONFIRMED' for v in s['sends'].values())
    expected=None if m['remote_base'] is None else m['remote_base']['id']
    if len(destinations)>1 or (destinations and expected not in destinations and not (expected is None and own_confirmed)):
        fail('STALE_DESTINATION')
    if review is not None:accepted(s,'PROJECTION',digest(m),review)


def creation_key(c,tid):
    return digest([PROJECTION_SCHEMA,c['instance'],c['workspace_id'],c['remote_project_id'],c['project_id'],tid])


def client_reduce(s,kind,a):
    b=s['config']['bounds'];result={}
    if kind=='CAPTURE':
        shape(a,('content_base64',));raw,src=source_bytes(a['content_base64'],b)
        if src['project_id']!=s['config']['project_id'] or src['document_id']!=s['config']['document_id']:fail('SOURCE_SCOPE')
        sid=hashlib.sha256(raw).hexdigest()
        if sid not in s['sources'] and len(s['sources'])>=b['sources']:fail('SOURCE_COUNT_BUDGET')
        s['sources'][sid]=dict(content_base64=a['content_base64'],source=src,profile=SCHEMA)
        result=dict(source_id=sid)
    elif kind=='SELECT_SOURCE':
        shape(a,('source_id',));sid=a['source_id']
        if sid is not None and sid not in s['sources']:fail('SOURCE_REQUIRED')
        s['selected_source']=sid;s['source_generation']+=1
        result=dict(source_generation=s['source_generation'])
    elif kind=='PREPARE_SOURCE':
        shape(a,());result=dict(manifest_id=manifest(s,'SOURCE',dict(context=source_context(s))))
    elif kind=='REVIEW':
        shape(a,('stage','manifest_id','expected_version','decision','reason_code'))
        stage,mid=a['stage'],a['manifest_id'];integer(a['expected_version']);text(a['reason_code'],maximum=256)
        if stage not in STAGES or a['decision'] not in ('ACCEPT','REJECT','REVOKE'):fail('INVALID_REVIEW')
        m=s['manifests'].get(mid)
        if not m or m['stage']!=stage:fail('MANIFEST_REQUIRED')
        key=review_key(stage,mid);old=s['reviews'].get(key,dict(version=0))
        if old['version']!=a['expected_version']:fail('CONFLICT_REVIEW')
        if a['decision']=='ACCEPT':
            if stage=='SOURCE' and m['context']!=source_context(s):fail('STALE_SOURCE')
            if stage=='BATCH':current_batch(s,m)
            if stage=='PROJECTION':projection_current(s,m)
        if s['review_count']>=b['reviews']:fail('REVIEW_BUDGET')
        s['review_count']+=1;s['reviews'][key]=dict(version=old['version']+1,decision=a['decision'],reason_code=a['reason_code'])
        result=dict(version=old['version']+1)
    elif kind=='PREPARE_BATCH':
        shape(a,('source_manifest','source_review','targets'));m=current_source(s,a['source_manifest'],a['source_review'])
        sid=m['context']['source_id'];src=s['sources'][sid]['source']
        after,plan=plan_batch(s['data'],src,a['targets'],bounds=b)
        mid=manifest(s,'BATCH',dict(**a,source_id=sid,data_generation=s['data_generation'],data_hash=digest(s['data']),after=after,plan=plan))
        result=dict(manifest_id=mid)
    elif kind=='APPLY_BATCH':
        shape(a,('manifest_id','review_version'));m=s['manifests'].get(a['manifest_id'])
        if not m or m['stage']!='BATCH':fail('MANIFEST_REQUIRED')
        current_batch(s,m);accepted(s,'BATCH',a['manifest_id'],a['review_version'])
        src=s['sources'][m['source_id']]['source'];after,plan=plan_batch(s['data'],src,m['targets'],bounds=b)
        if after!=m['after'] or plan!=m['plan']:fail('PLAN_CONFLICT')
        proof=dict(source_sha256=m['source_id'],manifest_sha256=a['manifest_id'],
                   source_review_version=m['source_review'],batch_review_version=a['review_version'])
        for eid,locators in plan['entities'].items():after['entity_provenance'].setdefault(eid,[]).append(dict(**proof,locators=locators))
        for rid,locators in plan['relations'].items():after['relation_provenance'].setdefault(rid,[]).append(dict(**proof,locators=locators))
        s['data']=after;s['data_generation']+=1
        result=dict(outcome='BATCH_APPLIED',manifest_id=a['manifest_id'],batch_review=a['review_version'],
                    data_generation=s['data_generation'],data_hash=digest(after),created=plan['created'],
                    participants=sorted(plan['entities']),declared_relations=sorted(plan['relations']))
    elif kind=='SELECT_TASKS':
        shape(a,('batch_command','batch_request','task_ids'));r,m=applied_batch(s,a['batch_command'],a['batch_request'])
        ids=a['task_ids']
        if type(ids) is not list or not 1<=len(ids)<=b['selected']:fail('INVALID_TASK_SELECTION')
        for tid in ids:identifier(tid)
        if len(set(ids))!=len(ids):fail('INVALID_TASK_SELECTION')
        if r['result']['data_generation']!=s['data_generation'] or r['result']['data_hash']!=digest(s['data']):fail('STALE_BATCH_RECEIPT')
        for tid in ids:
            identifier(tid)
            if tid not in r['result']['participants'] or s['data']['entities'][tid]['kind']!='TASK':fail('TASK_PARTICIPANT_REQUIRED')
        s['selection_generation']+=1
        s['selection']=dict(**a,data_generation=s['data_generation'],data_hash=digest(s['data']))
        result=dict(selection_generation=s['selection_generation'])
    elif kind=='BIND':
        shape(a,('binding_id','target_id'));identifier(a['binding_id']);v,_,_=selection_current(s)
        if a['target_id'] not in v['task_ids']:fail('TASK_SELECTION_REQUIRED')
        if a['binding_id'] in s['bindings'] or any(v['target_id']==a['target_id'] for v in s['bindings'].values()):fail('BINDING_EXISTS')
        if len(s['bindings'])>=b['bindings']:fail('BINDING_BUDGET')
        s['bindings'][a['binding_id']]=a
    elif kind=='PREPARE_PROJECTION':
        shape(a,('binding_id','remote_identity','capabilities','remote_base'));v,r,bm=selection_current(s)
        bind=s['bindings'].get(a['binding_id'])
        if not bind or bind['target_id'] not in v['task_ids']:fail('BINDING_SELECTION_REQUIRED')
        rid=a['remote_identity'];shape(rid,('run_id','store_id'));identifier(rid['run_id']);identifier(rid['store_id']);capcheck(a['capabilities'])
        tid=bind['target_id'];guard(s['data'],tid);task=s['data']['entities'][tid]
        destination=None
        for entry in s['sends'].values():
            if entry['binding_id']==a['binding_id'] and entry['status']=='EFFECT_CONFIRMED':destination=entry['proof']['remote_id']
        if a['remote_base'] is not None:
            remote_entity(a['remote_base'])
            if destination!=a['remote_base']['id']:fail('DESTINATION_CONFLICT')
        elif destination is not None:fail('DESTINATION_REQUIRED')
        pm=dict(schema=PROJECTION_SCHEMA,stage='PROJECTION',selection=v,selection_generation=s['selection_generation'],
                batch_command=v['batch_command'],batch_request=v['batch_request'],batch_manifest=r['result']['manifest_id'],
                batch_review=s['reviews'][review_key('BATCH',r['result']['manifest_id'])],
                data_generation=s['data_generation'],data_hash=digest(s['data']),binding=bind,target_id=tid,task=task,
                remote_identity=rid,capabilities=a['capabilities'],remote_base=a['remote_base'],creation_key=creation_key(s['config'],tid),
                operation='CREATE' if destination is None else 'UPDATE',payload=dict(name=task['title'],description=task['description']))
        if len(canonical(pm))>b['projection_bytes']:fail('MANIFEST_BUDGET')
        mid=digest(pm)
        if mid not in s['manifests'] and len(s['manifests'])>=b['manifests']:fail('MANIFEST_BUDGET')
        s['manifests'][mid]=pm;result=dict(manifest_id=mid)
    elif kind in ('EDIT_ENTITY','ADD_RELATION'):
        if kind=='EDIT_ENTITY':
            shape(a,('entity_id','changes'));entity=s['data']['entities'].get(a['entity_id']);ch=a['changes']
            if entity is None or type(ch) is not dict or not ch or not set(ch)<=set(('title','description','epic_id','foreign','has_work','status')):fail('INVALID_EDIT')
            for key,value in ch.items():
                if key=='has_work' and type(value) is not bool:fail('INVALID_EDIT')
                if key in ('title','status'):text(value)
                if key=='description':
                    if entity['kind']=='EPIC':fail('INVALID_EDIT')
                    text(value,nullable=True,empty=True)
                if key=='epic_id':
                    if entity['kind']!='TASK':fail('INVALID_EDIT')
                    if value is not None:identifier(value)
                if key=='foreign':shape(value,('note',));text(value['note'],empty=True)
            entity.update(ch);entity['row_version']+=1
        else:
            shape(a,('relation',));rel=a['relation'];shape(rel,('type','left','right','kind'))
            if rel['type'] not in ('EPIC_REQUIREMENT','TASK_EPIC','TASK_DEPENDENCY'):fail('INVALID_RELATION')
            if rel['left'] not in s['data']['entities'] or rel['right'] not in s['data']['entities']:fail('ENTITY_REQUIRED')
            if (rel['type']=='TASK_DEPENDENCY' and rel['kind'] not in ('HARD','SOFT','MOCKABLE','OPTIONAL') or rel['type']!='TASK_DEPENDENCY' and rel['kind'] is not None):fail('INVALID_RELATION')
            rid=digest(rel)
            if rid not in s['data']['relations'] and len(s['data']['relations'])>=b['relations']:fail('RELATION_BUDGET')
            s['data']['relations'][rid]=rel
        s['data_generation']+=1
    elif kind=='CLOCK':
        shape(a,('tick',));integer(a['tick'])
        if a['tick']<s['tick']:fail('CLOCK_BACKWARDS')
        s['tick']=a['tick']
    elif kind in ('ISSUE','QUERY','RESULT'):
        s,result=ledger_transition(s,kind,a)
    else:fail('UNKNOWN_R_OPERATION')
    return s,result


def ledger_transition(s,kind,a):
    b=s['config']['bounds'];result={}
    if kind=='ISSUE':
        shape(a,('manifest_id','review_version','send_id','ticket','capabilities','retry'))
        identifier(a['send_id']);identifier(a['ticket']);capcheck(a['capabilities'])
        if type(a['retry']) is not bool:fail('INVALID_RETRY')
        m=s['manifests'].get(a['manifest_id'])
        if not m or m['stage']!='PROJECTION':fail('MANIFEST_REQUIRED')
        projection_current(s,m);accepted(s,'PROJECTION',a['manifest_id'],a['review_version'])
        if m['capabilities']!=a['capabilities']:fail('STALE_CAPABILITY')
        if not all(a['capabilities'][k] for k in ('create_unique','conditional_update','effect_lookup')):fail('CAPABILITY_REQUIRED')
        sid=a['send_id'];bid=m['binding']['binding_id'];old=s['sends'].get(sid)
        if any(v['binding_id']==bid and (v['status'] in ('UNKNOWN','CONFLICT') or v['hard_conflict']) for v in s['sends'].values()):fail('BINDING_UNRESOLVED')
        if any(v['manifest_id']==a['manifest_id'] and k!=sid for k,v in s['sends'].items()):fail('PACKAGE_COMMAND_CONFLICT')
        if old:
            if not a['retry'] or old['manifest_id']!=a['manifest_id'] or old['review_version']!=a['review_version'] or old['status'] not in ('NO_EFFECT','CLOSED_NO_EFFECT'):fail('RETRY_FORBIDDEN')
            if old['retry_tick'] is None or s['tick']<old['retry_tick']:fail('RETRY_NOT_ELIGIBLE')
            if len(old['attempts'])>=b['attempts']:fail('ATTEMPT_BUDGET')
        elif a['retry']:fail('SEND_REQUIRED')
        if any(a['ticket'] in v['attempts'] for v in s['sends'].values()):fail('TICKET_EXISTS')
        if not old:
            old=dict(manifest_id=a['manifest_id'],review_version=a['review_version'],binding_id=bid,status='NOT_SENT',
                     attempts=[],ledger_version=0,queries=0,proof=None,retry_tick=0,hard_conflict=False,events=[])
            s['sends'][sid]=old
        old['attempts'].append(a['ticket']);old['ledger_version']+=1;old['status']='UNKNOWN';old['proof']=None
        old['events'].append(dict(type='ISSUED',ticket=a['ticket']))
        s['pending']['send:'+a['ticket']]=dict(send_id=sid)
        result=dict(ticket=a['ticket'],ledger_version=old['ledger_version'],outcome='UNKNOWN')
    elif kind=='QUERY':
        shape(a,('send_id','query_id','ledger_version'));identifier(a['query_id']);integer(a['ledger_version'],1);v=s['sends'].get(a['send_id'])
        if not v or v['ledger_version']!=a['ledger_version']:fail('CONFLICT_LEDGER')
        if v['queries']>=b['queries']:fail('QUERY_BUDGET')
        if a['query_id'] in s['pending']:fail('QUERY_EXISTS')
        v['queries']+=1;s['pending'][a['query_id']]=dict(send_id=a['send_id'])
        result=dict(ledger_version=v['ledger_version'],ticket=v['attempts'][-1])
    elif kind=='RESULT':
        shape(a,('send_id','ledger_version','proof','query_id'));integer(a['ledger_version'],1);v=s['sends'].get(a['send_id'])
        if not v or v['ledger_version']!=a['ledger_version']:fail('CONFLICT_LEDGER')
        m=s['manifests'][v['manifest_id']];proof=a['proof'];ticket=v['attempts'][-1]
        pending=a['query_id'] if a['query_id'] is not None else 'send:'+ticket
        if pending not in s['pending']:fail('RESULT_NOT_EXPECTED')
        if len(canonical(proof))>s['config']['limits']['proof_bytes']:fail('PROOF_BUDGET')
        if proof is None:
            result=dict(outcome=v['status'])
        elif not proof_ok(proof,ticket,m,s['config']):
            v['status']='CONFLICT';v['hard_conflict']=True;result=dict(outcome='CONFLICT')
        else:
            if not v['hard_conflict']:
                v['status']=proof['status'];v['proof']=proof;v['retry_tick']=proof['retry_tick']
            result=dict(outcome=v['status'])
        v['ledger_version']+=1;v['events'].append(dict(type='OBSERVED',proof=proof))
        s['pending'].pop(pending,None)
        if proof is not None:
            for key in list(s['pending']):
                if s['pending'][key]['send_id']==a['send_id']:s['pending'].pop(key)
    else:fail('UNKNOWN_LEDGER_OPERATION')
    return s,result


def remote_entity(v):
    shape(v,('id','version','payload','foreign'));identifier(v['id']);integer(v['version'],1)
    payload(v['payload'])
    if type(v['foreign']) is not dict or any(type(x) is not str for x in v['foreign'].values()):fail('INVALID_FOREIGN')


def payload(v):
    shape(v,('name','description'));text(v['name']);text(v['description'],nullable=True,empty=True)


def remote_manifest(m):
    shape(m,('schema','stage','selection','selection_generation','batch_command','batch_request','batch_manifest','batch_review',
             'data_generation','data_hash','binding','target_id','task','remote_identity','capabilities','remote_base',
             'creation_key','operation','payload'))
    if m['schema']!=PROJECTION_SCHEMA or m['stage']!='PROJECTION' or m['operation'] not in ('CREATE','UPDATE'):fail('R_PROJECTION_REQUIRED')
    shape(m['binding'],('binding_id','target_id'));identifier(m['binding']['binding_id']);identifier(m['target_id'])
    shape(m['remote_identity'],('run_id','store_id'));identifier(m['remote_identity']['run_id']);identifier(m['remote_identity']['store_id'])
    task=m['task'];shape(task,('id','project_id','kind','key','title','description','status','row_version','has_work','foreign','epic_id'))
    identifier(task['id']);identifier(task['project_id']);integer(task['row_version']);text(task['key'])
    if task['epic_id'] is not None:identifier(task['epic_id'])
    shape(task['foreign'],('note',));text(task['foreign']['note'],empty=True)
    if (task['kind']!='TASK' or task['status']!='BACKLOG' or task['has_work'] is not False or
        m['binding']['target_id']!=m['target_id'] or task['id']!=m['target_id']):fail('R_TASK_REQUIRED')
    shape(m['selection'],('batch_command','batch_request','task_ids','data_generation','data_hash'))
    selected=m['selection']
    if (type(selected['task_ids']) is not list or m['target_id'] not in selected['task_ids'] or
        selected['batch_command']!=m['batch_command'] or selected['batch_request']!=m['batch_request'] or
        selected['data_generation']!=m['data_generation'] or selected['data_hash']!=m['data_hash']):fail('R_SELECTION_CONFLICT')
    for tid in selected['task_ids']:identifier(tid)
    payload(m['payload'])
    if m['payload']!=dict(name=task['title'],description=task['description']):fail('PAYLOAD_CONFLICT')
    capcheck(m['capabilities']);hash_id(m['creation_key']);hash_id(m['data_hash']);hash_id(m['batch_manifest']);hash_id(m['batch_request']);identifier(m['batch_command'])
    integer(m['data_generation']);integer(m['selection_generation'],1)
    if m['remote_base'] is not None:remote_entity(m['remote_base'])


def proof_ok(p,ticket,m,c):
    try:
        shape(p,('schema','run_id','store_id','ticket','request_hash','creation_key','manifest_hash','status',
                 'remote_id','applied_version','payload_hash','retry_tick','code'))
        if p['schema']!='d5.relational-remote-proof.v1':return False
        if dict(run_id=p['run_id'],store_id=p['store_id'])!=m['remote_identity']:return False
        if (p['ticket']!=ticket or p['request_hash']!=digest(m) or p['manifest_hash']!=digest(m) or p['creation_key']!=m['creation_key']):return False
        codes={'EFFECT_CONFIRMED':('CONFIRMED',),'CLOSED_NO_EFFECT':('CLOSED',),'NO_EFFECT':('REJECTED','RATE_LIMIT','REMOTE_PRECONDITION','CREATION_KEY_CONFLICT')}
        if p['status'] not in codes or p['code'] not in codes[p['status']]:return False
        if p['status']=='EFFECT_CONFIRMED':
            identifier(p['remote_id']);integer(p['applied_version'],1)
            if p['payload_hash']!=digest(m['payload']):return False
        elif any(p[k] is not None for k in ('remote_id','applied_version','payload_hash')):return False
        if p['retry_tick'] is not None:integer(p['retry_tick'])
        if p['code'] in ('REMOTE_PRECONDITION','CREATION_KEY_CONFLICT') and p['retry_tick'] is not None:return False
        return True
    except DurableError:return False


def remote_reduce(s,kind,a):
    b=s['config']['bounds']
    if kind=='CAPABILITY':
        shape(a,('capabilities',));capcheck(a['capabilities'])
        if a['capabilities']['generation']!=s['capabilities']['generation']+1:fail('CONFLICT_CAPABILITY')
        s['capabilities']=a['capabilities'];return s,{}
    if kind=='EDIT':
        shape(a,('remote_id','expected_version','payload','foreign'));integer(a['expected_version'],1);v=s['entities'].get(a['remote_id'])
        if not v or v['version']!=a['expected_version']:fail('REMOTE_CAS')
        v['version']+=1;v['payload']=a['payload'];v['foreign']=a['foreign'];remote_entity(v)
        return s,{}
    if kind not in ('EXECUTE','CLOSE'):fail('UNKNOWN_OPERATION')
    shape(a,('ticket','manifest','run_id','store_id','reject','retry_tick'))
    ticket=identifier(a['ticket']);m=a['manifest'];remote_manifest(m)
    if m['remote_identity']!=dict(run_id=a['run_id'],store_id=a['store_id']):fail('REMOTE_IDENTITY')
    if m['creation_key']!=creation_key(s['config'],m['target_id']) or m['task']['project_id']!=s['config']['project_id']:fail('REMOTE_SCOPE')
    if a['run_id'] is None or a['store_id'] is None:fail('REMOTE_IDENTITY')
    identifier(a['run_id']);identifier(a['store_id'])
    old=s['tickets'].get(ticket)
    if old:
        if old['request_hash']!=digest(m):fail('TICKET_CONFLICT')
        return s,old
    if len(s['tickets'])>=b['tickets']:fail('TICKET_BUDGET')
    if m['capabilities']!=s['capabilities']:fail('STALE_CAPABILITY')
    required='settle_or_close' if kind=='CLOSE' else ('create_unique' if m['operation']=='CREATE' else 'conditional_update')
    if not s['capabilities'][required]:fail('CAPABILITY_REQUIRED')
    p=dict(schema='d5.relational-remote-proof.v1',run_id=a['run_id'],store_id=a['store_id'],ticket=ticket,
           request_hash=digest(m),creation_key=m['creation_key'],manifest_hash=digest(m),status='CLOSED_NO_EFFECT',
           remote_id=None,applied_version=None,payload_hash=None,retry_tick=0,code='CLOSED')
    if kind=='EXECUTE':
        p['status']='NO_EFFECT';p['code']='CREATION_KEY_CONFLICT' if m['operation']=='CREATE' else 'REMOTE_PRECONDITION';p['retry_tick']=None
        if a['reject'] not in (None,'REJECTED','RATE_LIMIT'):fail('INVALID_REJECTION')
        if a['retry_tick'] is not None:integer(a['retry_tick'])
        if a['reject']:
            p['code']=a['reject'];p['retry_tick']=a['retry_tick']
        else:
            key=m['creation_key'];rid=s['keys'].get(key);entity=s['entities'].get(rid)
            can=False
            if m['operation']=='CREATE':
                if rid is None:
                    if len(s['entities'])>=b['remote_tasks']:fail('REMOTE_TASK_BUDGET')
                    rid=str(uuid.uuid5(uuid.UUID(a['store_id']),key));can=True
                    entity=dict(id=rid,version=0,payload=m['payload'],foreign={})
            elif entity is not None and m['remote_base']==entity:can=True
            if can:
                entity['version']+=1;entity['payload']=copy(m['payload']);s['entities'][rid]=entity;s['keys'][key]=rid
                p.update(status='EFFECT_CONFIRMED',remote_id=rid,applied_version=entity['version'],payload_hash=digest(entity['payload']),code='CONFIRMED')
    s['tickets'][ticket]=p
    return s,p



# Reuse only the public generic local-call facade; new reducers, roots and R schema.
from .durable_task_fixture import Remote as LocalRemoteFacade


class Remote(LocalRemoteFacade):
    def __init__(self,path,run_id,store_id,*,hook=None):
        self.store=Store(path,run_id,store_id,'REMOTE',remote_reduce,remote_genesis,hook=hook)


class Client:
    def __init__(self,path,run_id,store_id,remote,*,hook=None):
        self.store=Store(path,run_id,store_id,'CLIENT',client_reduce,client_genesis,hook=hook)
        self.remote=remote

    def snapshot(self):return self.store.snapshot()

    def perform(self,kind,args,*,cid=None,expected=None):
        snap=self.snapshot()
        if expected is None:expected={k:snap['head'][k] for k in ('seq','commit_sha256')}
        return self.store.transact(cid or str(uuid.uuid4()),kind,args,expected)

    def capture(self,raw):
        if type(raw) is not bytes:fail('SOURCE_BYTES_REQUIRED')
        return self.perform('CAPTURE',dict(content_base64=base64.b64encode(raw).decode()))

    def select_source(self,sid):return self.perform('SELECT_SOURCE',dict(source_id=sid))

    def review(self,stage,mid,*,decision='ACCEPT',version=0):
        return self.perform('REVIEW',dict(stage=stage,manifest_id=mid,expected_version=version,decision=decision,reason_code='SYNTHETIC_REVIEW'))

    def prepare_projection(self,bid):
        rs=self.remote.snapshot()['state'];cs=self.snapshot()['state'];base=None
        for v in cs['sends'].values():
            if v['binding_id']==bid and v['status']=='EFFECT_CONFIRMED':
                base=rs['entities'].get(v['proof']['remote_id'])
                if base is None:fail('DESTINATION_MISSING')
        return self.perform('PREPARE_PROJECTION',dict(binding_id=bid,remote_identity=dict(run_id=self.remote.store.run_id,store_id=self.remote.store.store_id),
            capabilities=rs['capabilities'],remote_base=base))

    def dispatch(self,mid,review_version,*,send_id=None,retry=False,reject=None,retry_tick=0,deliver=True):
        sid=send_id or str(uuid.uuid4());ticket=str(uuid.uuid4());card=self.remote.snapshot()['state']['capabilities']
        r=self.perform('ISSUE',dict(manifest_id=mid,review_version=review_version,send_id=sid,ticket=ticket,capabilities=card,retry=retry))
        self.store.checkpoint('after_issue')
        if deliver:
            m=self.snapshot()['state']['manifests'][mid]
            try:proof=self.remote.execute(ticket,m,reject=reject,retry_tick=retry_tick)
            except (DurableError,OSError):proof=None
            self.store.checkpoint('after_remote')
            r=self.perform('RESULT',dict(send_id=sid,ledger_version=r['result']['ledger_version'],proof=proof,query_id=None))
        return dict(send_id=sid,ticket=ticket,receipt=r)

    def reconcile(self,sid,*,close=False,proof_hook=None):
        s=self.snapshot()['state'];v=s['sends'][sid];m=s['manifests'][v['manifest_id']];qid=str(uuid.uuid4())
        r=self.perform('QUERY',dict(send_id=sid,query_id=qid,ledger_version=v['ledger_version']))
        self.store.checkpoint('after_query')
        try:proof=self.remote.execute(v['attempts'][-1],m,close=True) if close else self.remote.lookup(v['attempts'][-1],m)
        except (DurableError,OSError):proof=None
        if proof_hook:proof=proof_hook(proof)
        self.store.checkpoint('before_result')
        return self.perform('RESULT',dict(send_id=sid,ledger_version=r['result']['ledger_version'],proof=proof,query_id=qid))

    def summary(self):
        s=self.snapshot()['state'];card=self.remote.snapshot()['state']['capabilities'];views=[]
        for sid,v in s['sends'].items():
            m=s['manifests'][v['manifest_id']]
            try:
                projection_current(s,m,v['review_version'])
                if m['capabilities']!=card:fail('STALE_CAPABILITY')
                current='CURRENT'
            except DurableError:current='STALE'
            views.append(dict(send_id=sid,target_id=m['target_id'],status=v['status'],validity=current,attempts=len(v['attempts']),queries=v['queries']))
        return dict(schema='d5.relational-summary.v1',mode='SYNTHETIC_ONLY',entities=len(s['data']['entities']),relations=len(s['data']['relations']),
                    data_generation=s['data_generation'],selected_TASKs=0 if s['selection'] is None else len(s['selection']['task_ids']),sends=views,
                    pending=len(s['pending']),clock_tick=s['tick'],remote_requests=0,persistent_D2_writes=0,operations=0,operational_attempts=0,
                    quota_consumed=0,reservations_created=0,activation_allowed=False,grants_execution_authority=False,
                    D5_closed=False,global_gaps_open=[f'G{i:02}' for i in range(1,8)])


class RelationalLab:
    created_roots=[]

    def __init__(self,c):
        self.config=valid_config(c);self.home=Path(tempfile.mkdtemp(prefix='d5-relational-'));self.root=self.home/'run';self.root.mkdir(mode=0o700)
        self.sentinel=self.home/'sentinel';self.sentinel.write_bytes(b'SYNTHETIC_SIBLING')
        self.run_id=str(uuid.uuid4());self.client_id=str(uuid.uuid4());self.remote_id=str(uuid.uuid4())
        self.owner=dict(schema='d5.relational-owner.v1',run_id=self.run_id,client_id=self.client_id,remote_id=self.remote_id)
        (self.root/'owner.json').write_bytes(canonical(self.owner))
        self.identities={p:(p.stat().st_dev,p.stat().st_ino) for p in (self.home,self.root)}
        self.created_roots.append(str(self.home));self.closed=False
        self.remote=Remote(self.root/'remote',self.run_id,self.remote_id);self.remote.store.create(c)
        self.client=Client(self.root/'client',self.run_id,self.client_id,self.remote);self.client.store.create(c)

    def fresh(self,*,client_hook=None,remote_hook=None):
        r=Remote(self.root/'remote',self.run_id,self.remote_id,hook=remote_hook)
        return Client(self.root/'client',self.run_id,self.client_id,r,hook=client_hook)

    def close(self):
        if self.closed:return
        for p,identity in self.identities.items():
            info=p.lstat()
            if not stat.S_ISDIR(info.st_mode) or (info.st_dev,info.st_ino)!=identity:fail('CLEANUP_OWNERSHIP')
        if (self.root/'owner.json').read_bytes()!=canonical(self.owner):fail('CLEANUP_MARKER')
        for path,marker in ((self.root/'client',self.client.store.marker),(self.root/'remote',self.remote.store.marker)):
            if path.is_symlink() or decode((path/'marker.json').read_bytes())!=marker:fail('CLEANUP_MARKER')
        if any(p.is_symlink() for p in self.home.rglob('*')):fail('CLEANUP_SYMLINK')
        if self.sentinel.read_bytes()!=b'SYNTHETIC_SIBLING':fail('SENTINEL_CHANGED')
        shutil.rmtree(self.root)
        if self.sentinel.read_bytes()!=b'SYNTHETIC_SIBLING':fail('SENTINEL_CHANGED')
        self.sentinel.unlink();self.home.rmdir();self.closed=True

    def __enter__(self):return self
    def __exit__(self,*_):self.close()
