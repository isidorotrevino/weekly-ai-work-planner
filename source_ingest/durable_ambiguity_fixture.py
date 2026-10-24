# SPDX-License-Identifier: GPL-3.0-only
"""I55 native synthetic ambiguity. New roots and schemas; no HTTP or provider.

The outer Store is the sole durable authority. Core reducers/receipts are composed,
never published in a second store. Catalog observations cannot create core effects.
"""
from pathlib import Path
import os
import shutil
import stat
import tempfile
import uuid

from . import durable_task_fixture as T, durable_relational_fixture as R
from .durable_store import Store, fail, shape, identifier, integer, hash_id, canonical, copy, digest, decode

CONFIG='d5.native-ambiguity-config.v1'
OBSERVATION='d5.native-ambiguity-observation.v1'
MAX_MATCHES,MAX_VIEWS,MAX_ENVELOPE=8,64,65536
MODES=('SUCCESS','AMBIGUOUS_429_BEFORE','AMBIGUOUS_429_AFTER','CONCLUSIVE_RATE_LIMIT')


def module(variant):
    if variant not in ('NATIVE_T','NATIVE_R'):fail('NATIVE_NAMESPACE_REQUIRED')
    return T if variant=='NATIVE_T' else R


def config(variant,base):
    return validate_config(dict(schema=CONFIG,variant=variant,project_id=base['project_id'],
        document_id=base['document_id'],limits=copy(base['limits']),base_config=copy(base)))


def validate_config(c):
    shape(c,('schema','variant','project_id','document_id','limits','base_config'))
    if c['schema']!=CONFIG:fail('NATIVE_NAMESPACE_REQUIRED')
    m=module(c['variant']);base=(m.validate_config if m is T else m.valid_config)(c['base_config'])
    if any(c[k]!=base[k] for k in ('project_id','document_id','limits')):fail('NATIVE_CONFIG_CONFLICT')
    return copy(c)


def genesis(c,role):
    c=validate_config(c);m=module(c['variant'])
    core=(m.client_genesis if role=='CLIENT' else m.remote_genesis)(c['base_config'])
    return dict(schema='d5.native-ambiguity-'+role.lower()+'.v1',config=c,core=core,
                extension=dict(observations=[] ) if role=='CLIENT' else dict(views={}))


def client_genesis(c):return genesis(c,'CLIENT')
def remote_genesis(c):return genesis(c,'REMOTE')


def core_view(s):
    core=copy(s['core']);core['receipts']=copy(s['receipts']);return core


def scope_hash(c):
    b=c['base_config']
    return digest(dict(variant=c['variant'],**{k:b[k] for k in ('instance','workspace_id','remote_project_id','project_id')}))


def match_shape(v):
    shape(v,('remote_id','creation_key','scope_hash','version','payload_hash'))
    identifier(v['remote_id']);integer(v['version'],1)
    for k in ('creation_key','scope_hash','payload_hash'):hash_id(v[k])


def matches_shape(values):
    if type(values) is not list or len(values)>MAX_MATCHES:fail('MATCH_BUDGET')
    for v in values:match_shape(v)


def reseal(e):
    e=copy(e);e.pop('response_id',None);return dict(e,response_id=digest(e))


def envelope_shape(e):
    shape(e,('schema','variant','run_id','remote_store_id','ticket','manifest_hash','creation_key',
             'channel','response_id','remote_head','http_status','retry_after_tick','matches','proof'))
    if len(canonical(e))>MAX_ENVELOPE:fail('ENVELOPE_BUDGET')
    if e['schema']!=OBSERVATION:fail('OBSERVATION_SCHEMA')
    module(e['variant'])
    for k in ('run_id','remote_store_id','ticket'):identifier(e[k])
    for k in ('manifest_hash','creation_key','response_id','remote_head'):hash_id(e[k])
    if e['channel'] not in ('EXECUTE','QUERY'):fail('OBSERVATION_CHANNEL')
    if type(e['http_status']) is not int or e['http_status'] not in (200,429):fail('OBSERVATION_STATUS')
    if e['retry_after_tick'] is not None:integer(e['retry_after_tick'])
    matches_shape(e['matches'])
    if e['proof'] is not None and type(e['proof']) is not dict:fail('OBSERVATION_PROOF_TYPE')
    if reseal(e)['response_id']!=e['response_id']:fail('RESPONSE_HASH')


def selection(s,m):
    key=m['creation_key'];view=s['extension']['views'].get(key)
    if view is not None:
        return copy(view['matches']) if view['visible'] else [],view['query_status'],view['retry_after_tick']
    core=s['core'];rid=core['keys'].get(key);entity=core['entities'].get(rid)
    matches=[] if entity is None else [dict(remote_id=rid,creation_key=key,scope_hash=scope_hash(s['config']),
        version=entity['version'],payload_hash=digest(entity['payload']))]
    return matches,200,None


def native_manifest(s,ticket,m):
    identifier(ticket);module(s['config']['variant']).remote_manifest(m)
    b=s['config']['base_config']
    if m['task']['project_id']!=b['project_id']:fail('REMOTE_SCOPE')
    if m['creation_key']!=module(s['config']['variant']).creation_key(b,m['target_id']):fail('REMOTE_SCOPE')


def remote_reduce(s,kind,a):
    m=module(s['config']['variant']);core=core_view(s)
    if kind=='DECLARE_VIEW':
        shape(a,('creation_key','version','visible','matches','query_status','retry_after_tick'))
        key=hash_id(a['creation_key']);integer(a['version'],1);matches_shape(a['matches'])
        if type(a['visible']) is not bool:fail('VIEW_VISIBILITY')
        if type(a['query_status']) is not int or a['query_status'] not in (200,429):fail('OBSERVATION_STATUS')
        if a['retry_after_tick'] is not None:integer(a['retry_after_tick'])
        views=s['extension']['views'];old=views.get(key)
        if a['version']!=(old['version']+1 if old else 1):fail('VIEW_VERSION')
        if key not in views and len(views)>=MAX_VIEWS:fail('VIEW_BUDGET')
        views[key]=copy(a)
        result=dict(outcome='VIEW_DECLARED',creation_key=key,version=a['version'])
    elif kind=='EXECUTE_RESPONSE':
        shape(a,('ticket','manifest','run_id','store_id','mode','retry_after_tick'))
        native_manifest(s,a['ticket'],a['manifest']);mft=a['manifest'];mode=a['mode']
        if mode not in MODES:fail('TRANSPORT_MODE')
        if mft['remote_identity']!=dict(run_id=a['run_id'],store_id=a['store_id']):fail('REMOTE_IDENTITY')
        if a['retry_after_tick'] is not None:integer(a['retry_after_tick'])
        proof=None
        if mode!='AMBIGUOUS_429_BEFORE':
            if mode=='CONCLUSIVE_RATE_LIMIT' and a['retry_after_tick'] is None:fail('RETRY_TICK_REQUIRED')
            args=dict(ticket=a['ticket'],manifest=mft,run_id=a['run_id'],store_id=a['store_id'],
                      reject='RATE_LIMIT' if mode=='CONCLUSIVE_RATE_LIMIT' else None,
                      retry_tick=a['retry_after_tick'] if mode=='CONCLUSIVE_RATE_LIMIT' else 0)
            core,proof=m.remote_reduce(core,'EXECUTE',args)
        s['core']=core
        matches,_,_=selection(s,mft)
        result=dict(http_status=200 if mode=='SUCCESS' else 429,retry_after_tick=a['retry_after_tick'],
                    matches=matches if mode in ('SUCCESS','CONCLUSIVE_RATE_LIMIT') else [],
                    proof=proof if mode in ('SUCCESS','CONCLUSIVE_RATE_LIMIT') else None)
    else:fail('UNKNOWN_OPERATION')
    s['core'].pop('receipts',None)
    return s,result


def classification(s,v,m,e,query_id):
    ticket=v['attempts'][-1];identity=m['remote_identity']
    if (e['variant']!=s['config']['variant'] or e['run_id']!=identity['run_id'] or
        e['remote_store_id']!=identity['store_id'] or e['ticket']!=ticket or
        e['manifest_hash']!=digest(m) or e['creation_key']!=m['creation_key'] or
        e['channel']!=('QUERY' if query_id is not None else 'EXECUTE')):return 'IDENTITY_CONFLICT'
    matches=e['matches'];p=e['proof']
    if len(matches)>1:return 'MULTIPLE_MATCHES'
    if matches and (matches[0]['creation_key']!=m['creation_key'] or matches[0]['scope_hash']!=scope_hash(s['config'])):return 'MATCH_CONFLICT'
    if p is not None:
        if not module(s['config']['variant']).proof_ok(p,ticket,m,s['config']['base_config']):return 'PROOF_CONFLICT'
        if p['status']=='EFFECT_CONFIRMED':
            if e['http_status']==429:return 'TRANSPORT_PROOF_CONFLICT'
            if len(matches)!=1 or any(matches[0][k]!=p[pk] for k,pk in
                (('remote_id','remote_id'),('version','applied_version'),('payload_hash','payload_hash'))):return 'MATCH_PROOF_CONFLICT'
        if e['http_status']==429 and (p['status']!='NO_EFFECT' or p['code']!='RATE_LIMIT' or
            p['retry_tick'] is None or p['retry_tick']!=e['retry_after_tick']):return 'RETRY_METADATA_CONFLICT'
        return 'CONCLUSIVE_PROOF'
    return 'AMBIGUOUS_429' if e['http_status']==429 else ('SINGLE_UNPROVEN' if matches else 'EMPTY_VIEW')


def client_reduce(s,kind,a):
    core=core_view(s);m=module(s['config']['variant'])
    if kind=='CORE':
        shape(a,('kind','args'))
        if a['kind'] in ('RESULT',):fail('NATIVE_OBSERVE_REQUIRED')
        core,result=m.client_reduce(core,a['kind'],a['args'])
    elif kind=='OBSERVE':
        shape(a,('send_id','ledger_version','query_id','envelope'));e=a['envelope'];envelope_shape(e)
        if len(canonical(e['proof']))>core['config']['limits']['proof_bytes']:fail('PROOF_BUDGET')
        integer(a['ledger_version'],1);identifier(a['send_id'])
        if a['query_id'] is not None:identifier(a['query_id'])
        v=core['sends'].get(a['send_id'])
        if not v or v['ledger_version']!=a['ledger_version']:fail('CONFLICT_LEDGER')
        ticket=v['attempts'][-1];pending=a['query_id'] if a['query_id'] is not None else 'send:'+ticket
        if pending not in core['pending'] or core['pending'][pending]['send_id']!=a['send_id']:fail('RESULT_NOT_EXPECTED')
        manifest=core['manifests'][v['manifest_id']];code=classification(s,v,manifest,e,a['query_id'])
        conflict=code.endswith('CONFLICT') or code=='MULTIPLE_MATCHES'
        adopt=code=='CONCLUSIVE_PROOF' and not v['hard_conflict']
        if conflict:v['status']='CONFLICT';v['hard_conflict']=True
        elif adopt:
            p=e['proof'];v['status']=p['status'];v['proof']=copy(p);v['retry_tick']=p['retry_tick']
        v['ledger_version']+=1
        observation=dict(send_id=a['send_id'],ticket=ticket,manifest_id=v['manifest_id'],query_id=a['query_id'],
            envelope=copy(e),envelope_sha256=digest(e),classification=code,adopted=adopt,ledger_version=v['ledger_version'])
        s['extension']['observations'].append(observation)
        v['events'].append(dict(type='NATIVE_OBSERVED',response_id=e['response_id'],classification=code))
        core['pending'].pop(pending)
        if conflict or adopt:
            for key in list(core['pending']):
                if core['pending'][key]['send_id']==a['send_id']:core['pending'].pop(key)
        result=dict(outcome=v['status'],classification=code,ledger_version=v['ledger_version'],response_id=e['response_id'])
    else:fail('UNKNOWN_OPERATION')
    core.pop('receipts',None);s['core']=core
    return s,result


class CoreStore:
    """Delegation adapter only. All receipts and commits belong to outer Store."""
    def __init__(self,owner):self.owner=owner
    def transact(self,cid,kind,args,expected=None):
        return self.owner.store.transact(cid,'CORE',dict(kind=kind,args=args),expected)


class CoreRemote:
    def __init__(self,owner):self.owner=owner;self.store=owner.store
    def snapshot(self):
        s=self.owner.snapshot();return dict(head=s['head'],state=core_view(s['state']))


class CoreClient:
    def __init__(self,owner,capture):
        self.owner=owner;self.store=CoreStore(owner);self.remote=CoreRemote(owner.remote);self.capture=capture
    def snapshot(self):
        s=self.owner.snapshot();return dict(head=s['head'],state=core_view(s['state']))
    def perform(self,*args,**kw):
        m=module(self.owner.variant);return m.Client.perform(self,*args,**kw)
    def review(self,*args,**kw):return module(self.owner.variant).Client.review(self,*args,**kw)
    def prepare_projection(self,*args,**kw):return module(self.owner.variant).Client.prepare_projection(self,*args,**kw)
    def _pin(self,*args):return T.Client._pin(self,*args)
    def import_event(self,*args):return T.Client.import_event(self,*args)
    def select_source(self,*args):return R.Client.select_source(self,*args)
    def capture_bytes(self,*args):return R.Client.capture(self,*args)


class Remote:
    def __init__(self,path,run_id,store_id,*,hook=None):
        self.store=Store(path,run_id,store_id,'REMOTE',remote_reduce,remote_genesis,hook=hook)
        self.calls=dict(execute=0,query=0)
    def snapshot(self):return self.store.snapshot()
    def _envelope(self,snap,ticket,m,channel,result,head=None):
        return reseal(dict(schema=OBSERVATION,variant=snap['state']['config']['variant'],run_id=self.store.run_id,
            remote_store_id=self.store.store_id,ticket=ticket,manifest_hash=digest(m),creation_key=m['creation_key'],
            channel=channel,remote_head=head or snap['head']['commit_sha256'],**result))
    def execute_response(self,ticket,m,mode='SUCCESS',retry_after_tick=None):
        self.calls['execute']+=1
        snap=self.snapshot();native_manifest(snap['state'],ticket,m)
        if m['remote_identity']!=dict(run_id=self.store.run_id,store_id=self.store.store_id):fail('REMOTE_IDENTITY')
        cid=str(uuid.uuid5(uuid.UUID(self.store.store_id),'EXECUTE_RESPONSE'+ticket+digest(m)))
        r=self.store.transact(cid,'EXECUTE_RESPONSE',dict(ticket=ticket,manifest=m,run_id=self.store.run_id,
            store_id=self.store.store_id,mode=mode,retry_after_tick=retry_after_tick))
        # Walk immutable ancestry by receipt seq: a later HEAD cannot rewrite this response.
        current=self.snapshot()['head']['commit_sha256']
        while True:
            value=decode((self.store.path/'objects'/(current+'.json')).read_bytes())
            if digest(value)!=current:fail('CORRUPT_OBJECT_HASH')
            if value['seq']==r['seq']:break
            current=value['parent_sha256']
            if current is None:fail('RESPONSE_COMMIT_MISSING')
        return self._envelope(snap,ticket,m,'EXECUTE',r['result'],current)
    def query(self,ticket,m):
        self.calls['query']+=1;snap=self.snapshot();s=snap['state'];native_manifest(s,ticket,m)
        if m['remote_identity']!=dict(run_id=self.store.run_id,store_id=self.store.store_id):fail('REMOTE_IDENTITY')
        proof=s['core']['tickets'].get(ticket)
        if proof is not None and proof['request_hash']!=digest(m):fail('TICKET_CONFLICT')
        matches,status,tick=selection(s,m)
        return self._envelope(snap,ticket,m,'QUERY',dict(matches=[] if status==429 else matches,
            proof=None if status==429 else copy(proof),http_status=status,retry_after_tick=tick))
    def declare_view(self,key,matches,*,visible=True,query_status=200,retry_after_tick=None):
        snap=self.snapshot();old=snap['state']['extension']['views'].get(key)
        return self.store.transact(str(uuid.uuid4()),'DECLARE_VIEW',dict(creation_key=key,
            version=old['version']+1 if old else 1,visible=visible,matches=matches,
            query_status=query_status,retry_after_tick=retry_after_tick))


class Client:
    def __init__(self,path,run_id,store_id,remote,*,capture=None,hook=None,variant=None):
        self.store=Store(path,run_id,store_id,'CLIENT',client_reduce,client_genesis,hook=hook)
        self.remote=remote;self.variant=variant;self.core=CoreClient(self,capture)
        if variant=='NATIVE_R':self.core.capture=self.core.capture_bytes
    def snapshot(self):
        snap=self.store.snapshot();v=snap['state']['config']['variant']
        if self.variant is not None and v!=self.variant:fail('NATIVE_NAMESPACE_REQUIRED')
        return snap
    def observe(self,sid,ledger,envelope,query_id=None,*,cid=None,expected=None):
        snap=self.snapshot()
        return self.store.transact(cid or str(uuid.uuid4()),'OBSERVE',dict(send_id=sid,ledger_version=ledger,
            query_id=query_id,envelope=envelope),expected or {k:snap['head'][k] for k in ('seq','commit_sha256')})
    def dispatch(self,mid,review_version,*,send_id=None,retry=False,deliver=True,mode='SUCCESS',retry_after_tick=None):
        sid=send_id or str(uuid.uuid4());ticket=str(uuid.uuid4());card=self.remote.snapshot()['state']['core']['capabilities']
        r=self.core.perform('ISSUE',dict(manifest_id=mid,review_version=review_version,send_id=sid,ticket=ticket,
            capabilities=card,retry=retry));e=None
        if deliver:
            m=self.snapshot()['state']['core']['manifests'][mid]
            e=self.remote.execute_response(ticket,m,mode,retry_after_tick)
            r=self.observe(sid,r['result']['ledger_version'],e)
        return dict(send_id=sid,ticket=ticket,receipt=r,envelope=e)
    def begin_query(self,sid):
        s=self.snapshot()['state']['core'];v=s['sends'][sid];qid=str(uuid.uuid4())
        r=self.core.perform('QUERY',dict(send_id=sid,query_id=qid,ledger_version=v['ledger_version']))
        e=self.remote.query(v['attempts'][-1],s['manifests'][v['manifest_id']])
        return dict(sid=sid,ledger=r['result']['ledger_version'],query_id=qid,envelope=e)
    def reconcile(self,sid):
        q=self.begin_query(sid);self.store.checkpoint('before_observe')
        return self.observe(q['sid'],q['ledger'],q['envelope'],q['query_id'])


class NativeLab:
    created_roots=[]
    def __init__(self,c):
        self.config=validate_config(c);self.variant=c['variant'];self.closed=False
        self.home=Path(tempfile.mkdtemp(prefix='d5-native-ambiguity-'));self.root=self.home/'run';self.root.mkdir(mode=0o700)
        self.sentinel=self.home/'sentinel';self.sentinel.write_bytes(b'SYNTHETIC_SIBLING')
        self.run_id,self.client_id,self.remote_id=(str(uuid.uuid4()) for _ in range(3))
        self.owner=dict(schema='d5.native-ambiguity-owner.v1',run_id=self.run_id,client_id=self.client_id,remote_id=self.remote_id)
        (self.root/'owner.json').write_bytes(canonical(self.owner));self.capture=None;self.capture_lab=None
        self.identities={p:(p.stat().st_dev,p.stat().st_ino) for p in (self.home,self.root)}
        self.created_roots.append(str(self.home))
        if self.variant=='NATIVE_T':
            from .incremental_fixture import TemporaryFixtureLab
            self.scope=dict(schema='d5.fixture-drive-scope.v1',mode='SYNTHETIC_ONLY',project_id=c['project_id'],connector_id=str(uuid.uuid4()),
                principal='fixture-principal',corpus='fixture-corpus',drive='fixture-drive',policy_version='fixture-policy.v1',export_mime='text/plain',
                allowlist=[dict(file_id='file-1',document_id=c['document_id'],profile='task-register.v1')])
            self.capture_lab=TemporaryFixtureLab(self.scope);self.capture=self.capture_lab.store
            self.capture_owner=(self.capture.root/'owner.json').read_bytes()
            self.identities[self.capture.root]=(self.capture.root.stat().st_dev,self.capture.root.stat().st_ino)
            self.created_roots.append(str(self.capture.root))
        self.remote=Remote(self.root/'remote',self.run_id,self.remote_id);self.remote.store.create(c)
        self.client=Client(self.root/'client',self.run_id,self.client_id,self.remote,capture=self.capture,variant=self.variant);self.client.store.create(c)
    def close(self):
        if self.closed:return
        for p,identity in self.identities.items():
            info=p.lstat()
            if not stat.S_ISDIR(info.st_mode) or (info.st_dev,info.st_ino)!=identity:fail('CLEANUP_OWNERSHIP')
        if (self.root/'owner.json').read_bytes()!=canonical(self.owner):fail('CLEANUP_MARKER')
        for path,expected in ((self.root/'client',self.client.store.marker),(self.root/'remote',self.remote.store.marker)):
            if path.is_symlink() or decode((path/'marker.json').read_bytes())!=expected:fail('CLEANUP_MARKER')
        bases=[self.home]+([self.capture.root] if self.capture else [])
        if any(p.is_symlink() for base in bases for p in base.rglob('*')):fail('CLEANUP_SYMLINK')
        if self.sentinel.read_bytes()!=b'SYNTHETIC_SIBLING':fail('SENTINEL_CHANGED')
        if self.capture:
            if (self.capture.root/'owner.json').read_bytes()!=self.capture_owner:fail('CLEANUP_MARKER')
            self.capture_lab.close()
        shutil.rmtree(self.root)
        if self.sentinel.read_bytes()!=b'SYNTHETIC_SIBLING':fail('SENTINEL_CHANGED')
        self.sentinel.unlink();self.home.rmdir();self.closed=True
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
