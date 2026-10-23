# SPDX-License-Identifier: GPL-3.0-only
"""I34 implementation of the I33-F durable TASK fixture contract. Legacy labs remain volatile references.

All stores/inspection contain private fixture data. Only summary/receipts are public.
No HTTP, SQL, provider CLI, quota consumption, D3 reservation or execution authority.
"""
import base64
import hashlib
from pathlib import Path
import shutil
import tempfile
import uuid

from .durable_store import (Store, DurableError, fail, shape, integer, identifier,
                            hash_id, canonical, decode, digest, copy, LIMITS)
from . import eligibility_fixture as q
from .preview import build_observation


STAGES = ('SOURCE','EVALUATION','EFFECT','PROJECTION')
CAPS = dict(release='durable-fixture-1',version=1,generation=1,create_unique=True,
            conditional_update=True,effect_lookup=True,settle_or_close=True)
BOUNDS = dict(profiles=16,accounts=16,constraints=16,observations=128,tasks=16,
              manifests=128,reviews=128,tickets=384,source_bytes=2097152,
              text_characters=8192,manifest_bytes=1048576,attempts=3,queries=6)


def label(value, maximum=256):
    if type(value) is not str or not value.strip() or len(value)>maximum or '\x00' in value:
        fail('INVALID_LABEL')
    canonical(value)
    return value


def checked(fn, value):
    try:
        fn(value)
    except q.EligibilityError as ex:
        fail(str(ex))


def config(project, document, workspace, remote_project, *, limits=None, bounds=None):
    return dict(project_id=project,document_id=document,workspace_id=workspace,
                remote_project_id=remote_project,instance='SYNTHETIC_DURABLE',
                limits=dict(LIMITS if limits is None else limits),
                bounds=dict(BOUNDS if bounds is None else bounds))


def validate_config(c):
    shape(c, ('project_id','document_id','workspace_id','remote_project_id','instance','limits','bounds'))
    for k in ('project_id','document_id','workspace_id','remote_project_id'):
        identifier(c[k])
    if c['instance']!='SYNTHETIC_DURABLE': fail('SYNTHETIC_ONLY')
    for group, defaults in (('limits',LIMITS),('bounds',BOUNDS)):
        shape(c[group],defaults)
        for k, maximum in defaults.items():
            if not 1<=integer(c[group][k],1)<=maximum: fail('INVALID_LIMIT')
    return copy(c)


def client_genesis(c):
    return dict(config=validate_config(c),tick=0,profile_generation=0,profile=None,profiles={},
                selection_generation=0,selected_source=None,sources={},policy_generation=0,
                policy=None,accounts={},manifests={},reviews={},review_count=0,data_generation=0,
                tasks={},mappings={},bases={},provenance={},bindings={},sends={},pending={})


def remote_genesis(c):
    return dict(config=validate_config(c),capabilities=copy(CAPS),entities={},keys={},tickets={})


def accepted(s, stage, mid, version):
    integer(version,1)
    if stage not in STAGES: fail('INVALID_STAGE')
    r=s['reviews'].get(stage+':'+mid)
    if not r or r['version']!=version or r['decision']!='ACCEPT': fail('REVIEW_REQUIRED')


def add_manifest(s, stage, body):
    m=dict(schema='d5.durable-manifest.v1',stage=stage,**body)
    if len(canonical(m))>s['config']['bounds']['manifest_bytes']:fail('MANIFEST_BUDGET')
    mid=digest(m)
    if mid not in s['manifests'] and len(s['manifests'])>=s['config']['bounds']['manifests']:fail('MANIFEST_BUDGET')
    s['manifests'][mid]=m
    return mid


def source_current(s, mid, rv=None):
    if mid not in s['sources'] or s['selected_source']!=mid:fail('STALE_SOURCE')
    src=s['sources'][mid]
    if src['profile_generation']!=s['profile_generation'] or src['profile_hash']!=s['profile']:fail('STALE_PROFILE')
    if src['selection_generation']!=s['selection_generation'] or src['blocked']:fail('BLOCKED_SOURCE')
    if rv is not None:accepted(s,'SOURCE',mid,rv)
    return src


def pins(s, source_id, source_review):
    source_current(s,source_id,source_review)
    return dict(source_id=source_id,source_review=source_review,
                selection_generation=s['selection_generation'],profile_generation=s['profile_generation'],
                policy_generation=s['policy_generation'],accounts_sha256=digest(s['accounts']))


def evaluation_current(s, mid, review):
    m=s['manifests'].get(mid)
    if not m or m['stage']!='EVALUATION':fail('MANIFEST_REQUIRED')
    if m['pins']!=pins(s,m['pins']['source_id'],m['pins']['source_review']):fail('STALE_EVALUATION')
    accepted(s,'EVALUATION',mid,review)
    account=s['accounts'].get(m['account_id'])
    if account is None or not eligible(s,account):fail('BLOCKED_EVALUATION')
    return m


def eligible(s,a):
    p=s['policy']; card=a['adapter']; tick=s['tick']
    if not p or not card['online'] or card['permission']!='SYNTHETIC_GRANTED' or p['capability'] not in card['capabilities']:
        return False
    if a['revoked']:return False
    for row in p['constraints']:
        obs=a['observations'].get(a['selected'].get(q.slot(row)))
        if not obs or obs['binding']!=a['binding'] or obs['adapter']!=q.adapter_identity(card):return False
        if (obs['state']!='KNOWN' or obs['remaining']<row['cost'] or
                not obs['observed_at']<=tick<obs['expires_at'] or
                not row['window_start']<=tick<row['window_end'] or
                tick+p['required_horizon']>min(obs['expires_at'],row['window_end'])):
            return False
    return True


def effect_current(s,m):
    evaluation_current(s,m['evaluation'],m['evaluation_review'])
    if m['data_generation']!=s['data_generation'] or m['before']!=s['tasks'].get(m['target_id']):fail('STALE_EFFECT')
    accepted(s,'SOURCE',m['source_id'],m['source_review'])


def projection_current(s,m):
    evaluation_current(s,m['evaluation'],m['evaluation_review'])
    if (m['data_generation']!=s['data_generation'] or m['task']!=s['tasks'].get(m['target_id']) or
            m['binding']!=s['bindings'].get(m['binding']['binding_id'])):fail('STALE_LOCAL')
    if m['effect_review']!=s['reviews'].get('EFFECT:'+m['effect_manifest']):fail('STALE_REVIEW')


def vector(source, key):
    rows=[r for r in source['preview']['proposals'] if r['source_key']==key]
    if len(rows)!=1:fail('SOURCE_KEY_NOT_FOUND')
    fields=rows[0]['fields']
    return dict(title=fields['item'],description=fields['objective'])


def client_reduce(s,kind,a):
    b=s['config']['bounds']
    result={}
    if kind=='REGISTER_PROFILE':
        shape(a,('descriptor',));checked(q.validate_descriptor,a['descriptor']);h=digest(a['descriptor'])
        if h not in s['profiles'] and len(s['profiles'])>=b['profiles']:fail('PROFILE_BUDGET')
        s['profiles'][h]=a['descriptor'];result=dict(profile_hash=h)
    elif kind=='SELECT_PROFILE':
        shape(a,('profile_hash',));h=a['profile_hash']
        if h is not None and h not in s['profiles']:fail('UNKNOWN_PROFILE')
        s['profile']=h;s['profile_generation']+=1
    elif kind=='IMPORT':
        shape(a,('pin','capture'))
        shape(a['pin'],('run_id','scope_sha256','commit_sha256','event_index','capture_sha256'))
        identifier(a['pin']['run_id']);hash_id(a['pin']['scope_sha256']);hash_id(a['pin']['commit_sha256']);integer(a['pin']['event_index'])
        cap=a['capture']
        shape(cap,('schema','mode','project_id','document_id','profile','source_kind','revision_label',
                   'content_base64','content_sha256','preview','metadata_before','metadata_after',
                   'export_mime','exporter','provenance_grade','diagnostics','state','activation_allowed'))
        if cap['schema']!='d5.offline-capture.v1' or cap['mode']!='SYNTHETIC_ONLY' or cap['activation_allowed'] is not False:fail('INVALID_CAPTURE')
        if digest(cap)!=a['pin']['capture_sha256']:fail('PIN_HASH')
        # Captures are validated I26 artifacts. No arbitrary decoder/import/routing.
        if cap.get('document_id')!=s['config']['document_id'] or cap.get('project_id')!=s['config']['project_id']:fail('PIN_SCOPE')
        try:raw=base64.b64decode(cap.get('content_base64',''),validate=True)
        except (ValueError,TypeError):fail('INVALID_SOURCE_ENCODING')
        if len(raw)>b['source_bytes'] or base64.b64encode(raw).decode()!=cap.get('content_base64'):fail('SOURCE_BUDGET')
        if hashlib.sha256(raw).hexdigest()!=cap.get('content_sha256'):fail('PIN_HASH')
        s['selection_generation']+=1
        desc=s['profiles'].get(s['profile']);preview=None;blocked=True
        if desc and desc['decoder_id']=='task-register.v1' and desc['decoder_contract_version']==1 and desc['decoder_contract_sha256']==q.decoder_hash('task-register.v1'):
            try:
                preview=build_observation(raw,'fixture.md',s['config']['project_id'],s['config']['document_id'],
                                          cap['revision_label'],'task-register.v1')
                blocked=(cap.get('state')=='BLOCKED' or cap.get('metadata_before',{}).get('mime_type')!='text/markdown' or
                         cap.get('provenance_grade')!='SYNTHETIC_OBSERVATION' or any(d.get('blocking') for d in preview['diagnostics']))
            except (ValueError,UnicodeError):blocked=True
        src=dict(pin=a['pin'],capture=cap,profile_hash=s['profile'],profile_generation=s['profile_generation'],
                 selection_generation=s['selection_generation'],preview=preview,blocked=blocked)
        sid=digest(src);s['sources'][sid]=src;s['selected_source']=sid
        # SOURCE is reviewed directly by immutable capture ID.
        result=dict(source_id=sid,blocked=blocked)
    elif kind=='POLICY':
        shape(a,('policy',));checked(q.validate_policy,a['policy'])
        if len(a['policy']['constraints'])>b['constraints']:fail('CONSTRAINT_BUDGET')
        s['policy']=a['policy'];s['policy_generation']+=1
    elif kind=='BIND_ACCOUNT':
        shape(a,('binding','adapter'));checked(q.validate_account,a['binding']);checked(q.validate_adapter,a['adapter'])
        if a['binding']['project_id']!=s['config']['project_id']:fail('ACCOUNT_SCOPE')
        bid=a['binding']['binding_id']
        if bid in s['accounts']:fail('ACCOUNT_EXISTS')
        if len(s['accounts'])>=b['accounts']:fail('ACCOUNT_BUDGET')
        for v in s['accounts'].values():
            if (v['binding']['resource_id']==a['binding']['resource_id'] or
                v['binding']['physical_account_id']==a['binding']['physical_account_id']):fail('ACCOUNT_ALIAS')
        s['accounts'][bid]=dict(binding=a['binding'],adapter=a['adapter'],generation=1,
                                observations={},selected={},revoked=False)
    elif kind in ('OBSERVE','SELECT_OBSERVATION','REVOKE_OBSERVATION','ADAPTER'):
        fields={'OBSERVE':('account_id','observation','generation'),'SELECT_OBSERVATION':('account_id','observation_id','generation'),
                'REVOKE_OBSERVATION':('account_id','observation_id','generation'),'ADAPTER':('account_id','adapter','generation')}
        shape(a,fields[kind]);account=s['accounts'].get(a['account_id'])
        integer(a['generation'],1)
        if not account or a['generation']!=account['generation']:fail('CONFLICT_ACCOUNT')
        if kind=='ADAPTER':checked(q.validate_adapter,a['adapter']);account['adapter']=a['adapter']
        elif kind=='OBSERVE':
            obs=a['observation'];checked(q.validate_observation,obs);oid=obs['observation_id']
            if obs['binding']!=account['binding'] or obs['adapter']!=q.adapter_identity(account['adapter']):fail('OBSERVATION_SCOPE')
            if oid in account['observations']:
                if account['observations'][oid]!=obs:fail('OBSERVATION_CONFLICT')
                return s,dict(generation=account['generation'])
            if sum(len(v['observations']) for v in s['accounts'].values())>=b['observations']:fail('OBSERVATION_BUDGET')
            account['observations'][oid]=obs
        else:
            obs=account['observations'].get(a['observation_id'])
            if obs is None:fail('OBSERVATION_REQUIRED')
            if kind=='SELECT_OBSERVATION':account['selected'][q.slot(obs['window'])]=a['observation_id']
            else:account['revoked']=True
        account['generation']+=1;result=dict(generation=account['generation'])
    elif kind=='CLOCK':
        shape(a,('tick',));integer(a['tick'])
        if a['tick']<s['tick']:fail('CLOCK_BACKWARDS')
        s['tick']=a['tick']
    elif kind=='REVIEW':
        shape(a,('stage','manifest_id','expected_version','decision','reason_code'))
        stage,mid=a['stage'],a['manifest_id'];label(a['reason_code'])
        if stage not in STAGES or a['decision'] not in ('ACCEPT','REJECT','REVOKE'):fail('INVALID_REVIEW')
        if stage=='SOURCE':
            if mid not in s['sources']:fail('SOURCE_REQUIRED')
        elif s['manifests'].get(mid,{}).get('stage')!=stage:fail('MANIFEST_REQUIRED')
        key=stage+':'+mid;old=s['reviews'].get(key,dict(version=0))
        if old['version']!=integer(a['expected_version']):fail('CONFLICT_REVIEW')
        if s['review_count']>=b['reviews']:fail('REVIEW_BUDGET')
        s['review_count']+=1;s['reviews'][key]=dict(version=old['version']+1,decision=a['decision'],reason_code=a['reason_code'])
        result=dict(version=old['version']+1)
    elif kind=='PREPARE_EVALUATION':
        shape(a,('source_id','source_review','account_id'))
        if a['account_id'] not in s['accounts'] or not s['policy']:fail('POLICY_ACCOUNT_REQUIRED')
        mid=add_manifest(s,'EVALUATION',dict(pins=pins(s,a['source_id'],a['source_review']),
             account_id=a['account_id'],evaluated_at=s['tick']))
        result=dict(manifest_id=mid)
    elif kind=='VALIDATE_EVALUATION':
        shape(a,('manifest_id','review_version'));evaluation_current(s,a['manifest_id'],a['review_version'])
        result=dict(outcome='SIMULATED_ELIGIBLE',tick=s['tick'])
    elif kind=='PREPARE_EFFECT':
        shape(a,('evaluation','evaluation_review','source_key','target_id','target_key'))
        identifier(a['target_id']);label(a['target_key']);label(a['source_key'])
        em=evaluation_current(s,a['evaluation'],a['evaluation_review']);sid=em['pins']['source_id'];src=s['sources'][sid]
        value=vector(src,a['source_key'])
        for text in value.values():label(text,b['text_characters'])
        identity=[s['config']['project_id'],s['config']['document_id'],src['profile_hash'],a['source_key']]
        before=s['tasks'].get(a['target_id'])
        for tid,task in s['tasks'].items():
            if tid!=a['target_id'] and (s['mappings'][tid]==identity or task['key']==a['target_key']):fail('MAPPING_CONFLICT')
        if before is not None and (s['mappings'][a['target_id']]!=identity or before['key']!=a['target_key'] or before!=s['bases'][a['target_id']] or before['has_work']):fail('LOCAL_DIVERGENCE')
        if before is None and len(s['tasks'])>=b['tasks']:fail('TASK_BUDGET')
        after=dict(id=a['target_id'],project_id=s['config']['project_id'],key=a['target_key'],status='BACKLOG',
                   row_version=0 if before is None else before['row_version']+1,foreign={} if before is None else before['foreign'],
                   has_work=False,**value)
        mid=add_manifest(s,'EFFECT',dict(**a,source_id=sid,source_review=em['pins']['source_review'],identity=identity,
                                       data_generation=s['data_generation'],before=before,after=after))
        result=dict(manifest_id=mid)
    elif kind=='APPLY':
        shape(a,('manifest_id','review_version'));m=s['manifests'].get(a['manifest_id'])
        if not m or m['stage']!='EFFECT':fail('MANIFEST_REQUIRED')
        effect_current(s,m);accepted(s,'EFFECT',a['manifest_id'],a['review_version'])
        tid=m['target_id'];s['tasks'][tid]=copy(m['after']);s['bases'][tid]=copy(m['after']);s['mappings'][tid]=m['identity']
        s['provenance'][tid]=dict(source_id=m['source_id'],effect_manifest=a['manifest_id'],review_version=a['review_version'])
        s['data_generation']+=1;result=dict(outcome='APPLIED',target_id=tid,data_generation=s['data_generation'])
    elif kind=='EDIT_TASK':
        shape(a,('target_id','changes'));t=s['tasks'].get(a['target_id'])
        if t is None or type(a['changes']) is not dict or not set(a['changes'])<=set(('title','description','foreign','has_work')):fail('INVALID_EDIT')
        for k,v in a['changes'].items():
            if k in ('title','description'):label(v,b['text_characters'])
            elif k=='has_work' and type(v) is not bool:fail('INVALID_EDIT')
            elif k=='foreign' and (type(v) is not dict or any(type(x) is not str for x in v.values())):fail('INVALID_EDIT')
            t[k]=v
        t['row_version']+=1;s['data_generation']+=1
    elif kind=='BIND':
        shape(a,('binding_id','target_id'));identifier(a['binding_id'])
        if a['target_id'] not in s['tasks']:fail('TASK_REQUIRED')
        if a['binding_id'] in s['bindings'] or any(x['target_id']==a['target_id'] for x in s['bindings'].values()):fail('BINDING_EXISTS')
        if len(s['bindings'])>=b['tasks']:fail('BINDING_BUDGET')
        s['bindings'][a['binding_id']]=copy(a);s['data_generation']+=1
    elif kind=='PREPARE_PROJECTION':
        shape(a,('binding_id','capabilities','remote_base','remote_identity'))
        capcheck(a['capabilities']);shape(a['remote_identity'],('run_id','store_id'))
        identifier(a['remote_identity']['run_id']);identifier(a['remote_identity']['store_id']);binding=s['bindings'].get(a['binding_id'])
        if not binding:fail('BINDING_REQUIRED')
        tid=binding['target_id'];task=s['tasks'][tid];prov=s['provenance'][tid];eff=s['manifests'][prov['effect_manifest']]
        if task!=s['bases'][tid] or task['has_work']:fail('LOCAL_DIVERGENCE')
        evaluation_current(s,eff['evaluation'],eff['evaluation_review'])
        accepted(s,'EFFECT',prov['effect_manifest'],prov['review_version'])
        # Destination is accepted only from an exact prior durable proof, never adoption.
        destinations=[v['proof']['remote_id'] for v in s['sends'].values() if v['binding_id']==a['binding_id'] and v['status']=='EFFECT_CONFIRMED']
        dest=destinations[-1] if destinations else None
        if a['remote_base'] is not None:
            validate_remote_entity(a['remote_base'])
            if a['remote_base']['id']!=dest:fail('DESTINATION_CONFLICT')
        elif dest is not None:fail('DESTINATION_REQUIRED')
        key=creation_key(s['config'],tid)
        mid=add_manifest(s,'PROJECTION',dict(binding=binding,target_id=tid,task=task,
            effect_manifest=prov['effect_manifest'],effect_review=s['reviews']['EFFECT:'+prov['effect_manifest']],
            evaluation=eff['evaluation'],evaluation_review=eff['evaluation_review'],data_generation=s['data_generation'],
            capabilities=a['capabilities'],remote_base=a['remote_base'],remote_identity=a['remote_identity'],creation_key=key,
            operation='CREATE' if dest is None else 'UPDATE',payload=dict(name=task['title'],description=task['description'])))
        result=dict(manifest_id=mid)
    elif kind=='ISSUE':
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
    else:fail('UNKNOWN_OPERATION')
    return s,result


def capcheck(c):
    shape(c,CAPS)
    label(c['release']);integer(c['version'],1);integer(c['generation'],1)
    if any(type(c[k]) is not bool for k in ('create_unique','conditional_update','effect_lookup','settle_or_close')):fail('INVALID_CAPABILITY')


def creation_key(c,tid):
    return digest([c['instance'],c['workspace_id'],c['remote_project_id'],c['project_id'],tid])


def validate_remote_entity(v):
    shape(v,('id','version','payload','foreign'));identifier(v['id']);integer(v['version'],1)
    shape(v['payload'],('name','description'))
    for x in v['payload'].values():label(x,8192)
    if type(v['foreign']) is not dict or any(type(x) is not str for x in v['foreign'].values()):fail('INVALID_FOREIGN')


def remote_manifest(m):
    shape(m,('schema','stage','binding','target_id','task','effect_manifest','effect_review',
             'evaluation','evaluation_review','data_generation','capabilities','remote_base','remote_identity','creation_key','operation','payload'))
    if m['schema']!='d5.durable-manifest.v1' or m['stage']!='PROJECTION' or m['operation'] not in ('CREATE','UPDATE'):fail('INVALID_REMOTE_MANIFEST')
    shape(m['binding'],('binding_id','target_id'));identifier(m['binding']['binding_id']);identifier(m['target_id'])
    shape(m['remote_identity'],('run_id','store_id'))
    identifier(m['remote_identity']['run_id']);identifier(m['remote_identity']['store_id'])
    if m['binding']['target_id']!=m['target_id'] or m['task'].get('id')!=m['target_id']:fail('REMOTE_SCOPE')
    if m['payload']!=dict(name=m['task'].get('title'),description=m['task'].get('description')):fail('PAYLOAD_CONFLICT')
    capcheck(m['capabilities']);hash_id(m['creation_key']);shape(m['payload'],('name','description'))
    for text in m['payload'].values():label(text,8192)
    if m['remote_base'] is not None:validate_remote_entity(m['remote_base'])


def proof_ok(p,ticket,m,c):
    try:
        shape(p,('schema','run_id','store_id','ticket','request_hash','creation_key','manifest_hash','status',
                 'remote_id','applied_version','payload_hash','retry_tick','code'))
        identifier(p['store_id']);identifier(p['run_id'])
        if dict(run_id=p['run_id'],store_id=p['store_id'])!=m['remote_identity']:return False
        if (p['schema']!='d5.durable-remote-proof.v1' or p['ticket']!=ticket or p['request_hash']!=digest(m) or
            p['manifest_hash']!=digest(m) or p['creation_key']!=m['creation_key']):return False
        if p['status'] not in ('EFFECT_CONFIRMED','NO_EFFECT','CLOSED_NO_EFFECT'):return False
        if p['status']=='EFFECT_CONFIRMED':
            identifier(p['remote_id']);integer(p['applied_version'],1)
            if p['payload_hash']!=digest(m['payload']):return False
        else:
            if any(p[k] is not None for k in ('remote_id','applied_version','payload_hash')):return False
        if p['retry_tick'] is not None:integer(p['retry_tick'])
        codes={'EFFECT_CONFIRMED':('CONFIRMED',),'CLOSED_NO_EFFECT':('CLOSED',),
               'NO_EFFECT':('REJECTED','RATE_LIMIT','REMOTE_PRECONDITION','CREATION_KEY_CONFLICT')}
        if p['code'] not in codes[p['status']]:return False
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
        v['version']+=1;v['payload']=a['payload'];v['foreign']=a['foreign'];validate_remote_entity(v)
        return s,{}
    if kind not in ('EXECUTE','CLOSE'):fail('UNKNOWN_OPERATION')
    shape(a,('ticket','manifest','run_id','store_id','reject','retry_tick'))
    ticket=identifier(a['ticket']);m=a['manifest'];remote_manifest(m)
    if m['remote_identity']!=dict(run_id=a['run_id'],store_id=a['store_id']):fail('REMOTE_IDENTITY')
    if m['creation_key']!=creation_key(s['config'],m['target_id']):fail('REMOTE_SCOPE')
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
    p=dict(schema='d5.durable-remote-proof.v1',run_id=a['run_id'],store_id=a['store_id'],ticket=ticket,
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
                    if len(s['entities'])>=b['tasks']:fail('REMOTE_TASK_BUDGET')
                    rid=str(uuid.uuid5(uuid.UUID(a['store_id']),key));can=True
                    entity=dict(id=rid,version=0,payload=m['payload'],foreign={})
            elif entity is not None and m['remote_base']==entity:can=True
            if can:
                entity['version']+=1;entity['payload']=copy(m['payload']);s['entities'][rid]=entity;s['keys'][key]=rid
                p.update(status='EFFECT_CONFIRMED',remote_id=rid,applied_version=entity['version'],payload_hash=digest(entity['payload']),code='CONFIRMED')
    s['tickets'][ticket]=p
    return s,p


class Remote:
    def __init__(self,path,run_id,store_id,*,hook=None):
        self.store=Store(path,run_id,store_id,'REMOTE',remote_reduce,remote_genesis,hook=hook)

    def snapshot(self):
        return self.store.snapshot()

    def execute(self,ticket,m,*,close=False,reject=None,retry_tick=0):
        op='CLOSE' if close else 'EXECUTE'
        args=dict(ticket=ticket,manifest=m,run_id=self.store.run_id,store_id=self.store.store_id,
                  reject=reject,retry_tick=retry_tick)
        cid=str(uuid.uuid5(uuid.UUID(self.store.store_id),op+ticket+digest(m)))
        r=self.store.transact(cid,op,args)
        return r['result']

    def lookup(self,ticket,m):
        value=self.snapshot()['state']['tickets'].get(ticket)
        if value is not None and value['request_hash']!=digest(m):fail('TICKET_CONFLICT')
        return copy(value)

    def edit(self,remote_id,*,payload=None,foreign=None):
        snap=self.snapshot();v=snap['state']['entities'][remote_id]
        return self.store.transact(str(uuid.uuid4()),'EDIT',dict(remote_id=remote_id,expected_version=v['version'],
             payload=v['payload'] if payload is None else payload,foreign=v['foreign'] if foreign is None else foreign))


class Client:
    def __init__(self,path,run_id,store_id,capture,remote,*,hook=None):
        self.store=Store(path,run_id,store_id,'CLIENT',client_reduce,client_genesis,hook=hook)
        self.capture,self.remote=capture,remote

    def snapshot(self):
        return self.store.snapshot()

    def _pin(self,pin):
        if pin['run_id']!=self.capture.run_id or pin['scope_sha256']!=self.capture.scope_hash:fail('PIN_SCOPE')
        chain=self.capture.inspect()
        for h,commit in chain:
            if h==pin['commit_sha256']:
                index=pin['event_index']
                if type(index) is not int or not 0<=index<len(commit['results']):fail('PIN_EVENT')
                cap=commit['results'][index]['capture']
                if cap is None or digest(cap)!=pin['capture_sha256']:fail('PIN_HASH')
                return copy(cap)
        fail('PIN_UNREACHABLE')

    def perform(self,kind,args,*,cid=None,expected=None):
        cid=cid or str(uuid.uuid4())
        snap=self.snapshot()
        if kind=='IMPORT':
            shape(args,('pin','capture'))
            shape(args['pin'],('run_id','scope_sha256','commit_sha256','event_index','capture_sha256'))
            if self._pin(args['pin'])!=args['capture']:fail('PIN_HASH')
        if kind in ('PREPARE_EVALUATION','VALIDATE_EVALUATION','PREPARE_EFFECT','APPLY','PREPARE_PROJECTION','ISSUE'):
            sid=snap['state']['selected_source']
            if sid is None:fail('SOURCE_REQUIRED')
            self._pin(snap['state']['sources'][sid]['pin'])
        if expected is None:expected={k:snap['head'][k] for k in ('seq','commit_sha256')}
        return self.store.transact(cid,kind,args,expected)

    def import_event(self,commit_hash,event_index=0):
        for h,value in self.capture.inspect():
            if h==commit_hash:
                if type(event_index) is not int or not 0<=event_index<len(value['results']):fail('PIN_EVENT')
                cap=value['results'][event_index]['capture']
                if cap is None:fail('PIN_DIAGNOSTIC')
                pin=dict(run_id=self.capture.run_id,scope_sha256=self.capture.scope_hash,
                         commit_sha256=h,event_index=event_index,capture_sha256=digest(cap))
                self._pin(pin)
                return self.perform('IMPORT',dict(pin=pin,capture=cap))
        fail('PIN_UNREACHABLE')

    def review(self,stage,mid,decision='ACCEPT',version=0):
        return self.perform('REVIEW',dict(stage=stage,manifest_id=mid,expected_version=version,
                                        decision=decision,reason_code='SYNTHETIC_REVIEW'))

    def prepare_projection(self,bid):
        rs=self.remote.snapshot()['state'];cs=self.snapshot()['state'];remote_base=None
        for v in cs['sends'].values():
            if v['binding_id']==bid and v['status']=='EFFECT_CONFIRMED':
                remote_base=rs['entities'].get(v['proof']['remote_id'])
                if remote_base is None:fail('DESTINATION_MISSING')
        return self.perform('PREPARE_PROJECTION',dict(binding_id=bid,capabilities=rs['capabilities'],remote_base=remote_base,
            remote_identity=dict(run_id=self.remote.store.run_id,store_id=self.remote.store.store_id)))

    def dispatch(self,mid,review_version,*,send_id=None,retry=False,reject=None,retry_tick=0,deliver=True):
        sid=send_id or str(uuid.uuid4());ticket=str(uuid.uuid4())
        card=self.remote.snapshot()['state']['capabilities']
        r=self.perform('ISSUE',dict(manifest_id=mid,review_version=review_version,send_id=sid,ticket=ticket,
                                   capabilities=card,retry=retry))
        self.store.checkpoint('after_issue')
        if deliver:
            m=self.snapshot()['state']['manifests'][mid]
            try:
                proof=self.remote.execute(ticket,m,reject=reject,retry_tick=retry_tick)
            except (DurableError,OSError):
                proof=None
            self.store.checkpoint('after_remote')
            r=self.perform('RESULT',dict(send_id=sid,ledger_version=r['result']['ledger_version'],proof=proof,query_id=None))
        return dict(send_id=sid,ticket=ticket,receipt=r)

    def reconcile(self,sid,*,close=False,proof_hook=None):
        state=self.snapshot()['state'];v=state['sends'][sid];m=state['manifests'][v['manifest_id']]
        qid=str(uuid.uuid4())
        r=self.perform('QUERY',dict(send_id=sid,query_id=qid,ledger_version=v['ledger_version']))
        self.store.checkpoint('after_query')
        try:
            proof=self.remote.execute(v['attempts'][-1],m,close=True) if close else self.remote.lookup(v['attempts'][-1],m)
        except (DurableError,OSError):proof=None
        if proof_hook:proof=proof_hook(proof)
        self.store.checkpoint('before_result')
        return self.perform('RESULT',dict(send_id=sid,ledger_version=r['result']['ledger_version'],proof=proof,query_id=qid))

    def summary(self):
        card=self.remote.snapshot()['state']['capabilities']
        s=self.snapshot()['state']
        sends=[]
        for sid,v in s['sends'].items():
            m=s['manifests'][v['manifest_id']]
            try:
                projection_current(s,m);accepted(s,'PROJECTION',v['manifest_id'],v['review_version'])
                if m['capabilities']!=card:fail('STALE_CAPABILITY')
                validity='CURRENT'
            except DurableError:validity='STALE'
            sends.append(dict(send_id=sid,status=v['status'],validity=validity,attempts=len(v['attempts']),queries=v['queries']))
        return dict(schema='d5.durable-summary.v1',mode='SYNTHETIC_ONLY',tasks=len(s['tasks']),sends=sends,
                    pending=len(s['pending']),clock_tick=s['tick'],remote_requests=0,persistent_D2_writes=0,
                    operations=0,operational_attempts=0,quota_consumed=0,reservations_created=0,
                    activation_allowed=False,grants_execution_authority=False,D5_closed=False,
                    global_gaps_open=[f'G{i:02}' for i in range(1,8)])


class DurableLab:
    """Trusted creator-only lifecycle; capture remains an independent public I26 lab."""
    created_roots=[]

    def __init__(self,cfg):
        from .incremental_fixture import TemporaryFixtureLab
        self.config=validate_config(cfg)
        self.home=Path(tempfile.mkdtemp(prefix='d5-durable-'));self.root=self.home/'run';self.root.mkdir(mode=0o700)
        self.sentinel=self.home/'sentinel';self.sentinel.write_bytes(b'SYNTHETIC_SIBLING')
        self.run_id=str(uuid.uuid4());self.client_id=str(uuid.uuid4());self.remote_id=str(uuid.uuid4())
        self.marker=dict(schema='d5.durable-owner.v1',run_id=self.run_id,client_id=self.client_id,remote_id=self.remote_id)
        (self.root/'owner.json').write_bytes(canonical(self.marker))
        self.scope=dict(schema='d5.fixture-drive-scope.v1',mode='SYNTHETIC_ONLY',project_id=cfg['project_id'],
            connector_id=str(uuid.uuid4()),principal='fixture-principal',corpus='fixture-corpus',drive='fixture-drive',
            policy_version='fixture-policy.v1',export_mime='text/plain',allowlist=[dict(file_id='file-1',document_id=cfg['document_id'],profile='task-register.v1')])
        self.capture_lab=TemporaryFixtureLab(self.scope);self.capture=self.capture_lab.store
        self.capture_owner=(self.capture.root/'owner.json').read_bytes()
        self.identities={p:(p.stat().st_dev,p.stat().st_ino) for p in (self.home,self.root,self.capture.root)}
        self.created_roots.extend([str(self.home),str(self.capture.root)])
        self.remote=Remote(self.root/'remote',self.run_id,self.remote_id);self.remote.store.create(cfg)
        self.client=Client(self.root/'client',self.run_id,self.client_id,self.capture,self.remote);self.client.store.create(cfg)
        self.closed=False

    def fresh(self,*,client_hook=None,remote_hook=None):
        from .incremental_fixture import FixtureStore
        cap=FixtureStore(self.capture.root,self.capture.run_id,self.scope)
        remote=Remote(self.root/'remote',self.run_id,self.remote_id,hook=remote_hook)
        return Client(self.root/'client',self.run_id,self.client_id,cap,remote,hook=client_hook)

    def close(self):
        if self.closed:return
        import stat
        for p,identity in self.identities.items():
            info=p.lstat()
            if not stat.S_ISDIR(info.st_mode) or (info.st_dev,info.st_ino)!=identity:fail('CLEANUP_OWNERSHIP')
        if (self.root/'owner.json').read_bytes()!=canonical(self.marker) or (self.capture.root/'owner.json').read_bytes()!=self.capture_owner:fail('CLEANUP_MARKER')
        for path in (self.root/'client',self.root/'remote'):
            expected=self.client.store.marker if path.name=='client' else self.remote.store.marker
            if path.is_symlink() or decode((path/'marker.json').read_bytes())!=expected:fail('CLEANUP_MARKER')
        for base in (self.home,self.capture.root):
            if any(p.is_symlink() for p in base.rglob('*')):fail('CLEANUP_SYMLINK')
        if self.sentinel.read_bytes()!=b'SYNTHETIC_SIBLING':fail('SENTINEL_CHANGED')
        self.capture_lab.close();shutil.rmtree(self.root)
        if self.sentinel.read_bytes()!=b'SYNTHETIC_SIBLING':fail('SENTINEL_CHANGED')
        self.sentinel.unlink();self.home.rmdir();self.closed=True

    def __enter__(self):return self
    def __exit__(self,*_):self.close()
