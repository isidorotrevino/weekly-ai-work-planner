# SPDX-License-Identifier: GPL-3.0-only
"""I32 volatile profile/quota model. No transport, consumption, reservation or D2.

Fixture registration/hooks are trusted harness controls, never source instructions.
Artifact inspection contains private fixture bytes; receipts contain fixed codes.
"""
import base64
from copy import deepcopy
import hashlib
import json
import threading
import uuid

from .preview import build_observation

MAX_PROFILES = 16
MAX_ACCOUNTS = 16
MAX_CONSTRAINTS = 16
MAX_OBSERVATIONS = 128
MAX_RECEIPTS = 128
MAX_SOURCE = 2 * 1024 * 1024
MAX_MANIFEST = 1024 * 1024
MAX_LABEL = 256
DECODERS = ('task-register.v1', 'task-register-compat.v1', 'markdown-structure.v1')


class EligibilityError(ValueError):
    pass


def fail(code):
    raise EligibilityError(code)


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                          separators=(',', ':')).encode('utf-8')
    except (ValueError, TypeError, UnicodeError, RecursionError):
        fail('INVALID_JSON')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def shape(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        fail('INVALID_SHAPE')


def label(value):
    if type(value) is not str or not value.strip() or len(value) > MAX_LABEL or '\x00' in value:
        fail('INVALID_LABEL')
    canonical(value)


def identifier(value):
    try:
        if type(value) is not str or str(uuid.UUID(value)) != value:
            fail('INVALID_ID')
    except (ValueError, AttributeError):
        fail('INVALID_ID')
    return value


def hash_id(value):
    if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        fail('INVALID_HASH')
    return value


def number(value, minimum=0):
    if type(value) is not int or value < minimum:
        fail('INVALID_NUMBER')
    return value


def decoder_hash(decoder_id):
    # Hash of a declared fixture interface, not an attestation of executable bytes.
    return digest(dict(interface='build_observation', contract_version=1, decoder_id=decoder_id))


def descriptor(version=1, policy_version=1, decoder_id='task-register.v1'):
    return dict(schema='d5.profile-fixture.v1', mode='SYNTHETIC_ONLY',
                profile_id='fixture-extraction', profile_version=version,
                extraction_policy_version=policy_version, decoder_id=decoder_id,
                decoder_contract_version=1, decoder_contract_sha256=decoder_hash(decoder_id))


def validate_descriptor(value):
    shape(value, ('schema','mode','profile_id','profile_version','extraction_policy_version',
                  'decoder_id','decoder_contract_version','decoder_contract_sha256'))
    if value['schema']!='d5.profile-fixture.v1' or value['mode']!='SYNTHETIC_ONLY':
        fail('SYNTHETIC_ONLY')
    label(value['profile_id']); label(value['decoder_id'])
    for k in ('profile_version','extraction_policy_version','decoder_contract_version'):
        number(value[k],1)
    hash_id(value['decoder_contract_sha256'])


def account(binding_id, physical_account_id, resource_id, project_id, provider_id='fixture-provider'):
    return dict(schema='d5.account-fixture.v1',mode='SYNTHETIC_ONLY',binding_id=binding_id,
                physical_account_id=physical_account_id,resource_id=resource_id,
                project_id=project_id,provider_id=provider_id,instance='SYNTHETIC_PROVIDER')


def validate_account(value):
    shape(value, ('schema','mode','binding_id','physical_account_id','resource_id','project_id','provider_id','instance'))
    if (value['schema']!='d5.account-fixture.v1' or value['mode']!='SYNTHETIC_ONLY'
            or value['instance']!='SYNTHETIC_PROVIDER'):
        fail('SYNTHETIC_ONLY')
    for k in ('binding_id','physical_account_id','resource_id','project_id'):
        identifier(value[k])
    label(value['provider_id'])


def adapter(adapter_id, release='fixture-1', *, permission='SYNTHETIC_GRANTED', online=True, capabilities=None):
    return dict(adapter_id=adapter_id,release=release,contract_sha256=digest(dict(release=release,contract='fixture-adapter.v1')),
                permission=permission,online=online,capabilities=['extract'] if capabilities is None else capabilities)


def validate_adapter(value):
    shape(value, ('adapter_id','release','contract_sha256','permission','online','capabilities'))
    identifier(value['adapter_id']); label(value['release']); hash_id(value['contract_sha256'])
    if value['permission'] not in ('UNKNOWN','DECLARED_ONLY','SYNTHETIC_GRANTED','REVOKED') or type(value['online']) is not bool:
        fail('INVALID_PERMISSION')
    caps=value['capabilities']
    if type(caps) is not list or len(caps)>MAX_CONSTRAINTS:
        fail('CAPABILITY_BUDGET')
    for c in caps: label(c)
    if len(set(caps))!=len(caps): fail('DUPLICATE_CAPABILITY')


def adapter_identity(card):
    return {k:deepcopy(card[k]) for k in ('adapter_id','release','contract_sha256')}


def constraint(dimension='REQUESTS', unit='REQUEST', window_id='short', cost=1, start=0, end=100):
    return dict(dimension=dimension,unit=unit,window_id=window_id,cost=cost,window_start=start,window_end=end)


def slot(value):
    return digest({k:value[k] for k in ('dimension','unit','window_id','window_start','window_end')})


def validate_window(value):
    for k in ('dimension','unit','window_id'): label(value[k])
    number(value['window_start']); number(value['window_end'],1)
    if value['window_end']<=value['window_start']: fail('INVALID_WINDOW')


def policy(policy_id, constraints, *, version=1, horizon=1, capability='extract'):
    return dict(schema='d5.demand-fixture.v1',mode='SYNTHETIC_ONLY',policy_id=policy_id,
                version=version,capability=capability,required_horizon=horizon,constraints=constraints)


def validate_policy(value):
    shape(value, ('schema','mode','policy_id','version','capability','required_horizon','constraints'))
    if value['schema']!='d5.demand-fixture.v1' or value['mode']!='SYNTHETIC_ONLY': fail('SYNTHETIC_ONLY')
    identifier(value['policy_id']); number(value['version'],1); label(value['capability']); number(value['required_horizon'],1)
    rows=value['constraints']
    if type(rows) is not list or not 1<=len(rows)<=MAX_CONSTRAINTS: fail('CONSTRAINT_BUDGET')
    keys=set()
    for row in rows:
        shape(row, ('dimension','unit','window_id','cost','window_start','window_end'))
        validate_window(row); number(row['cost'],1)
        key=slot(row)
        if key in keys: fail('DUPLICATE_CONSTRAINT')
        keys.add(key)


def observation(oid, binding, card, demand, *, revision=1, remaining=10, state='KNOWN', observed_at=0, expires_at=100):
    return dict(schema='d5.observation-fixture.v1',mode='SYNTHETIC_ONLY',observation_id=oid,
                binding=deepcopy(binding),adapter=adapter_identity(card),revision=revision,
                window={k:deepcopy(demand[k]) for k in ('dimension','unit','window_id','window_start','window_end')},
                state=state,remaining=remaining,observed_at=observed_at,expires_at=expires_at)


def validate_observation(value):
    shape(value, ('schema','mode','observation_id','binding','adapter','revision','window','state','remaining','observed_at','expires_at'))
    if value['schema']!='d5.observation-fixture.v1' or value['mode']!='SYNTHETIC_ONLY': fail('SYNTHETIC_ONLY')
    identifier(value['observation_id']); validate_account(value['binding']); number(value['revision'],1)
    shape(value['adapter'], ('adapter_id','release','contract_sha256'))
    identifier(value['adapter']['adapter_id']); label(value['adapter']['release']); hash_id(value['adapter']['contract_sha256'])
    shape(value['window'], ('dimension','unit','window_id','window_start','window_end')); validate_window(value['window'])
    number(value['observed_at']); number(value['expires_at'],1)
    if value['expires_at']<=value['observed_at']: fail('INVALID_OBSERVATION_INTERVAL')
    if value['state']=='KNOWN': number(value['remaining'])
    elif value['state'] not in ('UNKNOWN','UNLIMITED_DECLARED','REVOKED') or value['remaining'] is not None:
        fail('INVALID_QUOTA_STATE')


class EligibilityLab:
    def __init__(self, *, test_hook=None):
        self._lock=threading.RLock()
        self.test_hook=test_hook
        self._profiles={}; self._selections={}; self._captures={}; self._mappings={}
        self._accounts={}; self._observations={}; self._policies={}; self._policy_definitions={}
        self._manifests={}; self._reviews={'SOURCE':{},'EVALUATION':{}}; self._receipts={}
        self._now=0

    @staticmethod
    def _scope(project_id, document_id):
        identifier(project_id); identifier(document_id)
        return digest(dict(project_id=project_id,document_id=document_id))

    def register_profile(self, value):
        validate_descriptor(value); raw=canonical(value); key=digest(value)
        with self._lock:
            if key in self._profiles: return key
            if len(self._profiles)>=MAX_PROFILES: fail('PROFILE_BUDGET')
            tag=tuple(value[k] for k in ('profile_id','profile_version','extraction_policy_version'))
            for old_raw in self._profiles.values():
                old=json.loads(old_raw)
                if tuple(old[k] for k in ('profile_id','profile_version','extraction_policy_version'))==tag:
                    fail('PROFILE_TAG_CONFLICT')
            self._profiles[key]=raw
        return key

    def select_profile(self, project_id, document_id, profile_hash, *, expected_generation):
        scope=self._scope(project_id,document_id); number(expected_generation)
        if profile_hash is not None: hash_id(profile_hash)
        with self._lock:
            old=self._selections.get(scope,dict(generation=0,profile_hash=None))
            if old['generation']!=expected_generation: fail('CONFLICT_PROFILE_GENERATION')
            if profile_hash is not None and profile_hash not in self._profiles: fail('PROFILE_REQUIRED')
            self._selections[scope]=dict(generation=expected_generation+1,profile_hash=profile_hash)
            return expected_generation+1

    def capture(self, content, project_id, document_id, revision, *, profile_hash=None):
        scope=self._scope(project_id,document_id); label(revision)
        if type(content) is not bytes or len(content)>MAX_SOURCE: fail('SOURCE_BUDGET')
        with self._lock:
            selected=deepcopy(self._selections.get(scope,dict(generation=0,profile_hash=None)))
            chosen=profile_hash if profile_hash is not None else selected['profile_hash']
            if chosen is not None: hash_id(chosen)
            desc=json.loads(self._profiles[chosen]) if chosen in self._profiles else None
        codes=[]; preview=None
        if desc is None: codes.append('BLOCKED_PROFILE')
        elif (desc['decoder_id'] not in DECODERS or desc['decoder_contract_version']!=1
                or desc['decoder_contract_sha256']!=decoder_hash(desc['decoder_id'])):
            codes.append('BLOCKED_DECODER')
        else:
            try:
                preview=build_observation(content,'fixture.md',project_id,document_id,revision,desc['decoder_id'])
                if any(d.get('blocking') for d in preview['diagnostics']): codes.append('BLOCKED_PARSE')
            except (ValueError,UnicodeError,RecursionError): codes.append('BLOCKED_PARSE')
        if chosen!=selected['profile_hash'] or chosen is None: codes.append('BLOCKED_SELECTION')
        stable=desc is not None and desc['decoder_id'] in ('task-register.v1','task-register-compat.v1')
        value=dict(schema='d5.versioned-capture-fixture.v1',mode='SYNTHETIC_ONLY',project_id=project_id,
                   document_id=document_id,revision=revision,descriptor=desc,profile_hash=chosen,
                   profile_generation=selected['generation'],content_base64=base64.b64encode(content).decode(),
                   content_sha256=hashlib.sha256(content).hexdigest(),preview=preview,
                   preview_sha256=digest(dict(profile_hash=chosen,generation=selected['generation'],preview=preview)),
                   stable_identity=stable,diagnostics=codes,state='BLOCKED' if codes else 'PREVIEW_ONLY')
        key=digest(value)
        with self._lock:
            self._captures[key]=canonical(value)
            self._reviews['SOURCE'].setdefault(key,dict(version=0,decision=None,reason=''))
        return key

    def artifact(self, key):
        hash_id(key)
        with self._lock: raw=self._captures.get(key)
        if raw is None or hashlib.sha256(raw).hexdigest()!=key: fail('CAPTURE_CORRUPT')
        return json.loads(raw)

    def _source_current(self, cap):
        current=self._selections.get(self._scope(cap['project_id'],cap['document_id']))
        if current!=dict(generation=cap['profile_generation'],profile_hash=cap['profile_hash']): fail('STALE_PROFILE')
        if cap['state']=='BLOCKED' or not cap['stable_identity']: fail('SOURCE_PREVIEW_ONLY')

    def record_mapping_fixture(self, capture_id, source_key, target_id):
        """Trusted immutable historical mapping fixture; no task is materialized."""
        label(source_key); identifier(target_id); cap=self.artifact(capture_id)
        if cap['state']=='BLOCKED' or not cap['stable_identity']: fail('SOURCE_PREVIEW_ONLY')
        if not any(r.get('source_key')==source_key for r in cap['preview']['proposals']): fail('SOURCE_KEY_REQUIRED')
        value=dict(project_id=cap['project_id'],document_id=cap['document_id'],profile_hash=cap['profile_hash'],
                   source_key=source_key,target_id=target_id,capture_id=capture_id)
        key=digest(value)
        with self._lock:
            for old_raw in self._mappings.values():
                old=json.loads(old_raw)
                if old==value: return key
                if old['target_id']==target_id or (old['project_id'],old['document_id'],old['source_key'])==(value['project_id'],value['document_id'],source_key):
                    fail('MAPPING_FIXTURE_CONFLICT')
            self._mappings[key]=canonical(value)
        return key

    def check_mapping_fixture(self, capture_id, source_key, target_id):
        label(source_key); identifier(target_id); cap=self.artifact(capture_id)
        if cap['state']=='BLOCKED' or not cap['stable_identity']: fail('SOURCE_PREVIEW_ONLY')
        if not any(r.get('source_key')==source_key for r in cap['preview']['proposals']): fail('SOURCE_KEY_REQUIRED')
        with self._lock:
            for raw in self._mappings.values():
                old=json.loads(raw)
                if old['target_id']==target_id or (old['project_id'],old['document_id'],old['source_key'])==(cap['project_id'],cap['document_id'],source_key):
                    if (old['project_id'],old['document_id'],old['source_key'],old['target_id'])!=(cap['project_id'],cap['document_id'],source_key,target_id):
                        return 'BLOCKED_MAPPING_IDENTITY'
                    if old['profile_hash']!=cap['profile_hash']: return 'BLOCKED_PROFILE_MAPPING_REUSE'
                    return 'MAPPING_FIXTURE_MATCH'
        return 'NO_MAPPING_FIXTURE'

    def bind_account(self, value, card):
        validate_account(value); validate_adapter(card)
        with self._lock:
            bid=value['binding_id']
            if bid in self._accounts:
                if self._accounts[bid]['binding']==value and self._accounts[bid]['card']==card: return bid
                fail('BINDING_CONFLICT')
            if len(self._accounts)>=MAX_ACCOUNTS: fail('ACCOUNT_BUDGET')
            if any(a['binding']['resource_id']==value['resource_id'] or a['binding']['physical_account_id']==value['physical_account_id'] for a in self._accounts.values()):
                fail('BINDING_CONFLICT')
            self._accounts[bid]=dict(binding=deepcopy(value),card=deepcopy(card),generation=1,selected={},revoked=[])
        return bid

    def _account(self, bid, expected=None):
        identifier(bid)
        if bid not in self._accounts: fail('ACCOUNT_REQUIRED')
        result=self._accounts[bid]
        if expected is not None and result['generation']!=expected: fail('CONFLICT_ACCOUNT_GENERATION')
        return result

    def account_snapshot(self, bid):
        with self._lock: return deepcopy(self._account(bid))

    def change_adapter(self, bid, card, *, expected_generation):
        validate_adapter(card); number(expected_generation,1)
        with self._lock:
            value=self._account(bid,expected_generation)
            value['card']=deepcopy(card); value['generation']+=1
            return value['generation']

    def publish_observation(self, bid, value, *, expected_generation):
        validate_observation(value); number(expected_generation,1)
        oid=value['observation_id']; raw=canonical(value)
        with self._lock:
            a=self._account(bid)
            if value['binding']!=a['binding']: fail('OBSERVATION_SCOPE')
            if oid in self._observations:
                if self._observations[oid]!=raw: fail('OBSERVATION_ID_CONFLICT')
                return a['generation']  # immutable fact replay never reselects/restores
            self._account(bid,expected_generation)
            if len(self._observations)>=MAX_OBSERVATIONS: fail('OBSERVATION_BUDGET')
            self._observations[oid]=raw; a['generation']+=1
            return a['generation']

    def select_observation(self, bid, oid, *, expected_generation):
        identifier(oid); number(expected_generation,1)
        with self._lock:
            a=self._account(bid,expected_generation)
            if oid not in self._observations: fail('OBSERVATION_REQUIRED')
            obs=json.loads(self._observations[oid])
            if obs['binding']!=a['binding']: fail('OBSERVATION_SCOPE')
            a['selected'][slot(obs['window'])]=oid; a['generation']+=1
            return a['generation']

    def revoke_observation(self, bid, oid, *, expected_generation):
        identifier(oid); number(expected_generation,1)
        with self._lock:
            a=self._account(bid,expected_generation)
            if oid not in self._observations or json.loads(self._observations[oid])['binding']!=a['binding']: fail('OBSERVATION_SCOPE')
            if oid not in a['revoked']: a['revoked'].append(oid)
            a['generation']+=1
            return a['generation']

    def select_policy(self, project_id, value, *, expected_generation):
        identifier(project_id); number(expected_generation)
        if value is not None: validate_policy(value)
        with self._lock:
            old=self._policies.get(project_id,dict(generation=0,policy=None))
            if old['generation']!=expected_generation: fail('CONFLICT_POLICY_GENERATION')
            if value is not None:
                tag=(value['policy_id'],value['version']); raw=canonical(value)
                if tag in self._policy_definitions and self._policy_definitions[tag]!=raw: fail('POLICY_TAG_CONFLICT')
                self._policy_definitions[tag]=raw
            self._policies[project_id]=dict(generation=expected_generation+1,policy=deepcopy(value))
            return expected_generation+1

    def advance_clock(self, tick):
        number(tick)
        with self._lock:
            if tick<self._now: fail('CLOCK_REWIND')
            self._now=tick

    def manifest(self, mid):
        hash_id(mid)
        with self._lock: raw=self._manifests.get(mid)
        if raw is None or len(raw)>MAX_MANIFEST or hashlib.sha256(raw).hexdigest()!=mid: fail('MANIFEST_CORRUPT')
        return json.loads(raw)

    def _current(self, m):
        cap=self.artifact(m['capture_id']); self._source_current(cap)
        if cap['preview_sha256']!=m['preview_sha256']: fail('CAPTURE_CORRUPT')
        r=self._reviews['SOURCE'].get(m['capture_id'])
        if r is None or r['version']!=m['source_review_version'] or r['decision']!='ACCEPT': fail('SOURCE_REVIEW_REQUIRED')
        if self._account(m['account']['binding']['binding_id'])!=m['account']: fail('STALE_ACCOUNT')
        if self._policies.get(cap['project_id'])!=m['policy_selection']: fail('STALE_POLICY')

    def prepare_evaluation(self, capture_id, bid, *, source_review_version):
        number(source_review_version,1); cap=self.artifact(capture_id)
        with self._lock:
            self._source_current(cap)
            r=self._reviews['SOURCE'][capture_id]
            if r['version']!=source_review_version or r['decision']!='ACCEPT': fail('SOURCE_REVIEW_REQUIRED')
            a=deepcopy(self._account(bid)); p=deepcopy(self._policies.get(cap['project_id']))
            if a['binding']['project_id']!=cap['project_id']: fail('ACCOUNT_SCOPE')
            if p is None or p['policy'] is None: fail('POLICY_REQUIRED')
            observations={oid:json.loads(self._observations[oid]) for oid in set(a['selected'].values())}
            now=self._now
        m=dict(schema='d5.eligibility-fixture-manifest.v1',mode='SYNTHETIC_ONLY',capture_id=capture_id,
               preview_sha256=cap['preview_sha256'],descriptor=cap['descriptor'],profile_generation=cap['profile_generation'],
               source_review_version=source_review_version,account=a,policy_selection=p,
               observations=observations,observation_sha256={oid:digest(o) for oid,o in observations.items()},evaluated_at=now)
        m['evaluation']=self._evaluate(m,now)
        raw=canonical(m)
        if len(raw)>MAX_MANIFEST: fail('MANIFEST_BUDGET')
        mid=digest(m)
        with self._lock:
            self._manifests[mid]=raw
            self._reviews['EVALUATION'].setdefault(mid,dict(version=0,decision=None,reason=''))
        return mid

    @staticmethod
    def _evaluate(m, now):
        a=m['account']; card=a['card']; p=m['policy_selection']['policy']; diagnostics=[]
        if p['capability'] not in card['capabilities']: diagnostics.append('BLOCKED_CAPABILITY')
        if not card['online']: diagnostics.append('BLOCKED_PROVIDER_OFFLINE')
        if card['permission']!='SYNTHETIC_GRANTED': diagnostics.append('BLOCKED_PERMISSION')
        for row in p['constraints']:
            oid=a['selected'].get(slot(row)); obs=m['observations'].get(oid)
            if obs is None: diagnostics.append('BLOCKED_MISSING_OBSERVATION'); continue
            if obs['binding']!=a['binding'] or obs['adapter']!=adapter_identity(card):
                diagnostics.append('BLOCKED_OBSERVATION_SCOPE'); continue
            if oid in a['revoked'] or obs['state']!='KNOWN':
                diagnostics.append('BLOCKED_QUOTA_'+('REVOKED' if oid in a['revoked'] else obs['state'])); continue
            if (not obs['observed_at']<=now<obs['expires_at'] or not row['window_start']<=now<row['window_end']
                    or now+p['required_horizon']>min(obs['expires_at'],row['window_end'])):
                diagnostics.append('BLOCKED_QUOTA_TIME'); continue
            if obs['remaining']<row['cost']: diagnostics.append('BLOCKED_QUOTA_EXHAUSTED')
        return dict(result='BLOCKED' if diagnostics else 'SIMULATED_ELIGIBLE',diagnostics=diagnostics)

    def review(self, stage, key, *, expected_version, decision, reason):
        if stage not in ('SOURCE','EVALUATION') or decision not in ('ACCEPT','REJECT'): fail('INVALID_REVIEW')
        hash_id(key); number(expected_version); label(reason)
        with self._lock:
            old=self._reviews[stage].get(key)
            if old is None or old['version']!=expected_version: fail('CONFLICT_REVIEW')
            if decision=='ACCEPT':
                if stage=='SOURCE': self._source_current(self.artifact(key))
                else: self._current(self.manifest(key))
            self._reviews[stage][key]=dict(version=expected_version+1,decision=decision,reason=reason)
            return expected_version+1

    def _evaluation_accepted(self, mid, version):
        r=self._reviews['EVALUATION'].get(mid)
        if r is None or r['version']!=version or r['decision']!='ACCEPT': fail('EVALUATION_REVIEW_REQUIRED')

    def _hook(self, stage):
        if self.test_hook is not None: self.test_hook(stage)

    def validate_evaluation(self, cid, mid, *, evaluation_review_version):
        identifier(cid); hash_id(mid); number(evaluation_review_version,1)
        request_hash=digest(dict(manifest_id=mid,evaluation_review_version=evaluation_review_version))
        with self._lock:
            if cid in self._receipts: return self._historical(cid,request_hash)
            m=self.manifest(mid); self._current(m); self._evaluation_accepted(mid,evaluation_review_version)
            if self._evaluate(m,m['evaluated_at'])!=m['evaluation']: fail('MANIFEST_PLAN_CONFLICT')
        self._hook('validation_ready')
        with self._lock:
            if cid in self._receipts: return self._historical(cid,request_hash)
            self._current(m); self._evaluation_accepted(mid,evaluation_review_version)
            # Time can change independently of fact generations. Evaluate again at confirmation.
            current=self._evaluate(m,self._now)
            if len(self._receipts)>=MAX_RECEIPTS: fail('RECEIPT_BUDGET')
            receipt=dict(schema='d5.eligibility-fixture-receipt.v1',mode='SYNTHETIC_ONLY',command_id=cid,
                         request_sha256=request_hash,manifest_sha256=mid,evaluation_review_version=evaluation_review_version,
                         account_generation=m['account']['generation'],profile_generation=m['profile_generation'],
                         policy_generation=m['policy_selection']['generation'],tick=self._now,**current,
                         historical=False,grants_execution_authority=False,quota_consumed=0,reservations_created=0,
                         activation_allowed=False,fallback_allowed=False)
            self._receipts[cid]=canonical(receipt)
        self._hook('after_confirm')
        return deepcopy(receipt)

    def _historical(self, cid, request_hash):
        value=json.loads(self._receipts[cid])
        if value['request_sha256']!=request_hash: fail('COMMAND_CONFLICT')
        value['historical']=True; value['grants_execution_authority']=False
        return value

    def read_command(self, cid, request_hash):
        identifier(cid); hash_id(request_hash)
        with self._lock:
            if cid not in self._receipts: fail('COMMAND_REQUIRED')
            return self._historical(cid,request_hash)

    def inspect_facts(self):
        """Private complete fixture facts; values are copies, never live authority."""
        with self._lock:
            return deepcopy(dict(accounts=self._accounts,policies=self._policies,selections=self._selections,
                                 profiles={k:json.loads(v) for k,v in self._profiles.items()},
                                 observations={k:json.loads(v) for k,v in self._observations.items()},
                                 mappings={k:json.loads(v) for k,v in self._mappings.items()}))

    def summary(self):
        with self._lock:
            return dict(mode='SYNTHETIC_ONLY',storage='VOLATILE_MEMORY',profiles=len(self._profiles),
                        accounts=len(self._accounts),observations=len(self._observations),receipts=len(self._receipts),
                        quota_consumed=0,reservations_created=0,persistent_D2_writes=0,remote_requests=0,
                        operational_activation=False,D5_closed=False,global_gaps_open=[f'G{i:02}' for i in range(1,8)])
