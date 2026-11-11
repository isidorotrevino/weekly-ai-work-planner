# SPDX-License-Identifier: GPL-3.0-only
"""I122 metadata transactions. Source only: NOT imported or run during I122.

The draft copies exact builtin metadata containers, preserving aliases via one
short-lived memo and retaining original operands as opaque objects. No deepcopy
hooks, original methods or filesystem operations run inside a transaction.
This conservative copying implementation needs future resource/performance
validation; source integration alone never grants capture admission.
"""
import threading

FIELDS = ('frames','active','owners','owner_contexts','record_baselines',
          'record_refs','declarations','frame_summary','references','errors',
          'drive_identities','drive_observations','fixture_declarations',
          'pending_drive','parent_snapshots','parent_assertions','parent_outcomes',
          'pending_domain_observation','causal_sources','causal_records',
          'record_snapshots','causal_test')


def clone_metadata(value, memo, opaque):
    """Only exact builtin containers. Never invoke an object's copy protocol."""
    key=id(value)
    if key in opaque:return value
    if key in memo:return memo[key]
    kind=type(value)
    if kind is dict:
        out={};memo[key]=out
        for k,v in value.items():out[clone_metadata(k,memo,opaque)]=clone_metadata(v,memo,opaque)
    elif kind is list:
        out=[];memo[key]=out;out.extend(clone_metadata(v,memo,opaque) for v in value)
    elif kind is tuple:
        out=tuple(clone_metadata(v,memo,opaque) for v in value);memo[key]=out
    elif kind is set:
        out=set();memo[key]=out;out.update(clone_metadata(v,memo,opaque) for v in value)
    elif kind is frozenset:
        out=frozenset(clone_metadata(v,memo,opaque) for v in value);memo[key]=out
    else:return value
    return out


def opaque_originals(rec):
    """Mutation guards MUST keep the actual original list/value identities."""
    result=set()
    for _,value in rec.record_refs:result.add(id(value))
    for values,_,_ in rec.record_baselines.values():result.add(id(values))
    for value,_ in rec._causal_data.oracle_guards:result.add(id(value))
    for _,values,_ in rec.causal_sources.values():result.add(id(values))
    return result


def build(p):
    Old=p.Recorder
    t=p.t
    encode=p.encode
    NORMAL_SCHEMA=p.NORMAL_SCHEMA
    c=p.c
    functools=p.functools
    inspect=p.inspect
    re=p.re
    sys=p.sys
    types=p.types
    multiprocessing=p.multiprocessing
    Path=p.Path
    unittest=p.unittest
    fault=p.fault
    bounded_builtin=p.bounded_builtin
    store_request=p.store_request
    drive_request=p.drive_request
    store_receipt=p.store_receipt
    drive_receipt=p.drive_receipt
    oracle_commit=p.oracle_commit
    child_header=p.child_header
    policy_for=p.policy_for
    child_selector_context=p.child_selector_context
    uuid_value=p.t.uuid_value
    FIXTURE_DECL=p.t.FIXTURE_DECL

    class Pages(p.t.PageSink):
        def append(self,event):
            p.fault(self._planning,'CAUSAL_SCHEMA_INVALID');return super().append(event)
        def flush(self):
            p.fault(self._planning,'CAUSAL_SCHEMA_INVALID')
            if not self.chunks:return
            header=self.header(len(self.chunks))
            body=p.encode(header)[:-1]+b',"events":['+b','.join(self.chunks)+b']}'
            p.fault(len(body)==self.size(len(self.chunks),self.chunk_bytes) and len(body)<=self.limits['page_bytes'],'PAGE_BYTES_BUDGET')
            p.fault(self.total_bytes+len(body)<=self.limits['event_pages_total_bytes'] and len(self.manifest)<self.limits['pages'],'PAGES_TOTAL_BUDGET')
            name=f'event-{len(self.manifest)+1:04}.json'
            self._reference()  # Q16: reserve this page BEFORE manifest/I/O publication.
            self._writes.append((name,body))
            self.manifest.append(dict(name=name,sha256=p.c.sha(body),bytes=len(body),**{k:header[k] for k in ('page_index','first_sequence','last_sequence','event_count')}))
            self.total_bytes+=len(body);self.page_first=self.count;self.chunks=[];self.chunk_bytes=0
        def close(self):
            p.fault(self._planning,'CAUSAL_SCHEMA_INVALID');return super().close()

    class CausalProxy:
        def __init__(self,rec):object.__setattr__(self,'_rec',rec)
        def __getattr__(self,name):
            rec=self._rec
            with rec._state_lock:
                value=getattr(rec._causal_data,name)
                if not callable(value):return clone_metadata(value,{},opaque_originals(rec))
            def observed(*args,**kwargs):
                if name in ('selected','check_retained','protocol_for','witnesses'):
                    # These exact helpers are pure: no context allocation, charge,
                    # external call or I/O. Return an isolated read snapshot.
                    with rec._state_lock:
                        value=getattr(rec._causal_data,name)(*args,**kwargs)
                        return clone_metadata(value,{},opaque_originals(rec))
                return rec._atomic(lambda draft:getattr(draft.causal,name)(*(draft._memo.get(id(v),v) for v in args),**{k:draft._memo.get(id(v),v) for k,v in kwargs.items()}))
            return observed
        def __setattr__(self,name,value):
            self._rec._atomic(lambda draft:setattr(draft.causal,name,draft._memo.get(id(value),value)))

    class Bindings(p.late.LateBindings):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs);self._owner=None
        def check(self):
            # Reader checks remain fresh and OUTSIDE the metadata lock.
            owner=self._owner
            p.fault(owner is None or not owner._state_lock._is_owned(),'CAUSAL_SCHEMA_INVALID')
            if owner is None:rows=dict(self.rows);states=dict(self.states)
            else:
                with owner._state_lock:rows=dict(self.rows);states=dict(self.states)
            for ref,row in rows.items():
                p.fault(states[ref]!='INVALID','CLASS_BINDING_CHANGED')
                if ref=='builtins.dict':continue
                try:
                    spec=self.specs[ref];module,name=ref.rsplit('.',1)
                    p.fault(self.lookup(module) is row['module'] and row['module'].__dict__.get(name) is row['cls'],'CLASS_BINDING_CHANGED')
                    p.fault(p.c.sha(self.reader.read(spec['source']['path']))==row['sha256'],'STALE_CLASS_SOURCE')
                except BaseException:
                    if owner is not None:owner.invalid('CLASS_BINDING_CHANGED')
                    raise
        def prepare(self,allowed):
            refs=[]
            for graph in allowed:
                if graph.startswith('class-'):refs.append(graph[6:])
                elif graph=='exact-PlaneError-instance-args-projection':refs.append('source_ingest.plane_fixture.PlaneError')
                elif graph=='exact-EligibilityError-instance-args-projection':refs.append('source_ingest.eligibility_fixture.EligibilityError')
            refs=list(dict.fromkeys(refs))
            self.check();pending=[]
            p.fault(self._owner is not None,'CLASS_BINDING_CHANGED')
            for ref in refs:
                with self._owner._state_lock:state=self.states.get(ref)
                p.fault(ref in self.specs and state!='INVALID','CLASS_BINDING_CHANGED')
                if state=='BOUND':continue
                module_name,name=ref.rsplit('.',1);module=self.lookup(module_name)
                p.fault(type(module) is p.types.ModuleType,'CLASS_MODULE_NOT_LOADED');cls=module.__dict__.get(name)
                p.fault(type(cls) is type and cls.__bases__==(ValueError,) and cls.__module__==module_name and cls.__name__==name,'UNSUPPORTED_CLASS_BINDING')
                spec=self.specs[ref]
                p.fault(p.c.sha(self.reader.read(spec['source']['path']))==spec['source']['sha256'],'STALE_CLASS_SOURCE')
                pending.append((ref,dict(cls=cls,sha256=spec['source']['sha256'],module=module,name=name)))
            def publish(draft):
                bindings=draft.projector.bindings
                for ref,row in pending:
                    if bindings.states[ref]=='BOUND':
                        p.fault(bindings.rows[ref]['cls'] is row['cls'],'CLASS_BINDING_CHANGED');continue
                    draft.reference();bindings.rows[ref]=row;bindings.states[ref]='BOUND'
            self._owner._atomic(publish)
            self.check()

    class Recorder(Old):
        def __init__(self,entry,owner,policies=(),limits=None,profile=None,bindings=None,ledger=None):
            self._draft=False;self._state_lock=threading.RLock()
            self._ref_lock=self._state_lock;self._emit_lock=self._state_lock
            self._idle=threading.Condition(self._state_lock);self._pending_io=0;self._failed=False;self._finalizing=False
            self.ledger=ledger
            p.fault(type(bindings) is Bindings,'CLASS_BINDING_CHANGED')
            # Deliberately bypass late.Recorder.__init__: it published its callback
            # before Q18. No caller-visible callback is installed before admission.
            p.t.Recorder.__init__(self,entry,owner,policies,limits,profile,bindings)
            prior_pages=self.events;self.events=object.__new__(Pages);self.events.__dict__.update(prior_pages.__dict__)
            self.events._planning=False;self.events._writes=[];self.events._reference=self.reference
            self.causal_inventory={r['test_id']:r for r in self.profile['inventory']}
            self.causal_test=None;self.causal_bindings=[];self.causal_records=[]
            self.causal_exception_types={};self.record_snapshots={};self.causal_sources={};self.causal_deferred=[]
            self.parent_snapshots=[];self.parent_assertions=[];self.parent_outcomes=[];self.pending_domain_observation=None
            self._causal_data=p.DomainState(self.run_id,self.limits,self.profile['projection_schemas'],self.reference,self.emit,self.invalid,contract=self.profile['parental_contract'])
            self._causal_data.external_owner=self.owner;self.causal=CausalProxy(self)
            self._atomic(lambda draft:draft.reference(len(draft.projector.bindings.rows)))
            with self._state_lock:
                bindings._owner=self;bindings.on_reference=self.reference
                if self.ledger:self.ledger.run_id=self.run_id
        def _fork(self):
            memo={};opaque=opaque_originals(self)
            draft=object.__new__(type(self));draft.__dict__.update(self.__dict__)
            for field in FIELDS:setattr(draft,field,clone_metadata(getattr(self,field),memo,opaque))
            draft._draft=True;draft._rejection=None;draft._memo=memo
            causal=object.__new__(type(self._causal_data))
            causal.__dict__.update({k:clone_metadata(v,memo,opaque) for k,v in self._causal_data.__dict__.items()})
            causal.charge=draft.reference;causal.emit=draft.emit;causal.invalid=draft.invalid;causal.external_owner=draft.owner
            draft.causal=causal;draft._causal_data=causal
            pages=object.__new__(Pages)
            pages.__dict__.update({k:clone_metadata(v,memo,opaque) for k,v in self.events.__dict__.items()})
            pages._planning=True;pages._writes=[];pages._reference=draft.reference;draft.events=pages
            projector=object.__new__(type(self.projector));projector.__dict__.update(self.projector.__dict__)
            bindings=object.__new__(Bindings);bindings.__dict__.update(self.projector.bindings.__dict__)
            bindings.rows=clone_metadata(bindings.rows,memo,opaque);bindings.states=clone_metadata(bindings.states,memo,opaque)
            projector.bindings=bindings;draft.projector=projector
            return draft
        def _publish(self,draft):
            # Only this fixed field set can reach the live observer. Original
            # operands/modules/objects remain opaque, with no copying hooks.
            for field in FIELDS:setattr(self,field,getattr(draft,field))
            causal=draft.causal;causal.charge=self.reference;causal.emit=self.emit
            causal.invalid=self.invalid;causal.external_owner=self.owner;self._causal_data=causal
            self.events=draft.events;self.events._planning=False;self.events._writes=[];self.events._reference=self.reference
            self.projector.bindings.rows=draft.projector.bindings.rows
            self.projector.bindings.states=draft.projector.bindings.states
        def _atomic(self,operation,seal=False):
            if self._draft:return operation(self)
            error=None;writes=();value=None
            try:
                p.fault(not self._state_lock._is_owned(),'CAUSAL_SCHEMA_INVALID')
                with self._state_lock:
                    p.fault(not self._failed and not self._finalizing,'CAUSAL_SCHEMA_INVALID')
                    draft=self._fork();value=operation(draft)
                    p.fault(draft._rejection is None,draft._rejection or 'CAUSAL_SCHEMA_INVALID')
                    p.fault(type(draft.references) is int and self.references<=draft.references<=self.limits['refs'],'REFERENCE_BUDGET')
                    p.fault(not self._failed,'CAUSAL_SCHEMA_INVALID')
                    writes=tuple(draft.events._writes)
                    self._publish(draft)
                    if seal:self._finalizing=True
                    if writes:self._pending_io+=1
            except BaseException as ex:
                error=ex
            if error is not None:
                self.invalid(error.code if type(error) is p.c.CaptureFault else 'CAUSAL_SCHEMA_INVALID')
                raise error
            # NO metadata/ledger/emit lock is held across creation, writes or close.
            if writes:
                try:
                    p.fault(not self._state_lock._is_owned(),'CAUSAL_SCHEMA_INVALID')
                    for name,body in writes:
                        fd=self.events.owner.create(name)
                        try:p.write_all(fd,body)
                        finally:p.os.close(fd)
                except BaseException:
                    self.invalid('PAGE_WRITE_ERROR');raise
                finally:
                    with self._idle:self._pending_io-=1;self._idle.notify_all()
            return value
        def _drain(self):
            deadline=p.c.time.monotonic()+self.limits['wait_seconds']
            with self._idle:
                while self._pending_io:
                    remaining=deadline-p.c.time.monotonic();p.fault(remaining>0,'PAGE_WRITE_ERROR')
                    self._idle.wait(remaining)  # Condition releases the ledger lock.
        def _observe(self,operation):
            try:return self._atomic(operation)
            except BaseException:return None
        def invalid(self,code):
            if self._draft:
                if self._rejection is None:self._rejection=code
                p.c.Recorder.invalid(self,code);return
            with self._state_lock:
                self._failed=True;Old.invalid(self,code)
        def reference(self,n=1):
            if not self._draft:return self._atomic(lambda draft:draft.reference(n))
            p.fault(type(n) is int and n>=0,'REFERENCE_BUDGET')
            proposed=self.references+n;p.fault(proposed<=self.limits['refs'],'REFERENCE_BUDGET');self.references=proposed
        def owner(self,obj,out):
            if not self._draft:return self._atomic(lambda draft:draft.owner(obj,out))
            before=len(self.active['owner_context_refs']) if self.active else 0
            ref=Old.owner(self,obj,out)
            p.fault(ref is not None,'CONSTRUCTION_OBJECT_UNSUPPORTED')
            if self.active:self.reference(len(self.active['owner_context_refs'])-before)  # Q15 membership, charged where published.
            return ref
        def emit(self,kind,**data):
            return Old.emit(self,kind,**data) if self._draft else self._observe(lambda draft:Old.emit(draft,kind,**data))
        def outcome(self,name,subtest=False,failed=False):
            return p.t.Recorder.outcome(self,name,subtest,failed) if self._draft else self._observe(lambda draft:p.t.Recorder.outcome(draft,name,subtest,failed))

        def wrap_boundary(self, owner, name, observer):
            old = owner.__dict__.get(name)
            fault(type(old) is types.FunctionType, 'UNSUPPORTED_CAUSAL_API')
            signature = inspect.signature(old, eval_str=False)
            rec = self

            @functools.wraps(old)
            def wrapped(*args, **kwargs):
                if not rec.causal_enabled():
                    return old(*args, **kwargs)
                key = None
                request = None
                pre = None
                negative = None
                try:

                    def _prepare(rec):
                        key = request = pre = negative = b = obj = None
                        bound = signature.bind(*args, **kwargs)
                        bound.apply_defaults()
                        b = dict(bound.arguments)
                        obj = b.get('self', owner)
                        if observer in ('Store.transact', 'FixtureStore.advance'):
                            try:
                                request = store_request(b, rec.limits) if observer == 'Store.transact' else drive_request(b.get('value'), rec.limits)
                            except c.CaptureFault as failure:
                                candidate = rec.profile.get('negative_input_selectors', {}).get(rec.active['test_id'])
                                fault(candidate is not None and observer in candidate['methods'] and (failure.code in candidate['input_failures']), 'COMMAND_HEADER_INVALID')
                                negative = candidate
                                request = dict(status='INVALID_INPUT_EXPECTED_NEGATIVE', reason=failure.code, request_sha256=None, input_digest=c.digest_value({k: v for k, v in b.items() if k != 'self'}, rec.limits))
                        elif name == 'perform':
                            request = dict(args_digest=bounded_builtin({k: v for k, v in b.items() if k != 'self'}, rec.limits))
                        elif name == 'independent':
                            vals = owner.__dict__.get('ORACLES')
                            fault(type(vals) is list, 'ORACLE_VALUE_MISSING')
                            pre = (vals, len(vals), [bounded_builtin(v, rec.limits) for v in vals])
                            request = dict(kind='ORIGINAL_HARNESS_ORACLE')
                        elif name == 'start':
                            request = dict(action=b['action'], point=b.get('point'), role=b.get('role', 'CLIENT'))
                            obj = b['lab']
                        elif name == 'spawn':
                            request = dict(action='Drive.advance', point=b.get('fault'))
                            obj = b['self']
                        else:
                            request = dict(kind='ORIGINAL_HARNESS_PROTOCOL')
                        key = rec.causal.open_call(observer, obj, name, request)
                        return (key, request, pre, negative, b, obj)
                    key, request, pre, negative, b, obj = rec._atomic(_prepare)
                except BaseException as ex:
                    rec.invalid(ex.code if type(ex) is c.CaptureFault else 'COMMAND_HEADER_INVALID')
                try:
                    out = old(*args, **kwargs)
                except BaseException as ex:

                    def _publish_exception(rec):
                        if key is not None:
                            projection = rec.attempt(rec.exception, ex) or dict(kind='NOT_OBSERVED_REQUIRED')
                            if negative is not None and projection.get('code') not in negative['exception_codes']:
                                rec.invalid('COMMAND_HEADER_INVALID')
                            rec.attempt(rec.causal.close_call, key, exception=projection)
                    rec._observe(_publish_exception)
                    raise
                if key is not None:
                    try:

                        def _publish_return(rec):
                            fault(negative is None, 'COMMAND_HEADER_INVALID')
                            projected = None if name in ('start', 'spawn', 'independent') else dict(result_digest=bounded_builtin(out, rec.limits))
                            if observer == 'Store.transact':
                                projected = store_receipt(out, rec.profile['projection_schemas'], rec.limits, rec.selector_context(obj, request['kind']))
                            elif observer == 'FixtureStore.advance':
                                projected = drive_receipt(out, rec.profile['projection_schemas'])
                            if observer in ('Store.transact', 'FixtureStore.advance'):
                                fault(projected['command_id'] == request['command_id'] and projected['request_sha256'] == request['request_sha256'], 'REQUEST_HASH_CONFLICT')
                            if name == 'independent':
                                vals, n, digests = pre
                                fault(owner.__dict__.get('ORACLES') is vals and len(vals) >= n and all((bounded_builtin(v, rec.limits) == h for v, h in zip(vals[:n], digests))), 'ORACLE_VALUE_MUTATED')
                                fault(type(out) is dict and type(out.get('head')) is dict, 'ORACLE_VALUE_MISSING')
                                head = out['head']
                                domain = rec.causal.domain(head)
                                retained = []
                                for i in range(n, len(vals)):
                                    v = vals[i]
                                    kind = 'R' if 'entities' in v else 'T'
                                    hk = 'head_sha256' if kind == 'R' else 'commit_sha256'
                                    fault(type(v) is dict and v.get('case') == owner.__dict__.get('CURRENT_CASE') and (v.get('store_id') == head.get('store_id')) and (v.get('seq') == head.get('seq')) and (v.get(hk) == head.get('commit_sha256')), 'CAUSAL_LINK_AMBIGUOUS')
                                    retained.append(rec.causal.retain(owner.__name__, i, v, kind, out, key))
                                projected = dict(authority='RETAINED_HARNESS_ORACLE', head={k: head[k] for k in ('run_id', 'store_id', 'role', 'seq', 'commit_sha256')}, retained_refs=retained, commit=oracle_commit(out, rec.profile['projection_schemas'], rec.limits, 'R' if observer == 'R.independent' else 'T'))
                                rec.causal_sources[owner.__name__] = (owner, vals, bounded_builtin(vals, rec.limits))
                                for ref in retained:
                                    rec.causal.link(key, ref, 'RETURN_RETAINS_ORACLE', domain)
                                    commit = projected['commit']
                                    if commit['kind'] == 'COMMAND':
                                        rec.causal.link_receipt_candidates(ref, projected, domain)
                            elif name in ('start', 'spawn'):
                                fault(type(out) is tuple and len(out) == 2, 'UNSUPPORTED_CAUSAL_API')
                                lab = b.get('lab')
                                if lab is None:
                                    lab = object.__getattribute__(b['self'], '__dict__').get('lab')
                                fault(lab is not None, 'ORACLE_DOMAIN_IDENTITY_MISSING')
                                allowed = []
                                for module_name, class_name in [('source_ingest.durable_task_fixture', 'DurableLab'), ('source_ingest.durable_relational_fixture', 'RelationalLab'), ('source_ingest.incremental_fixture', 'TemporaryFixtureLab')]:
                                    loaded = sys.modules.get(module_name)
                                    if type(loaded) is types.ModuleType:
                                        allowed.append(loaded.__dict__.get(class_name))
                                fault(type(lab) in allowed, 'UNSUPPORTED_CAUSAL_API')
                                mem = object.__getattribute__(lab, '__dict__')
                                identity = {k: mem[k] for k in ('run_id', 'client_id', 'remote_id') if k in mem}
                                fault(t.uuid_value(identity.get('run_id')) and all((t.uuid_value(v) for v in identity.values())), 'ORACLE_DOMAIN_IDENTITY_MISSING')
                                intent = rec.causal.register(out[0], out[1], identity, request['action'], b.get('args', b.get('req')), request['point'], family='DRIVE' if name == 'spawn' else 'R' if 'relational' in observer else 'T')
                                projected = dict(parent_intent_ref=intent, command_identity='CHILD_LOCAL_NOT_OBSERVED')
                            elif name == 'finish':
                                rec.causal.exit(b['p'], out)
                                projected = dict(returncode=out)
                            elif name == 'receive':
                                projected = dict(authority='CHILD_PROTOCOL_RETURN', registered=rec.causal.protocol_for(b.get('conn', b.get('c')), 'connection_ref') is not None)
                            if observer == 'Store.transact':
                                declaration = rec.declarations.get(rec.owner(obj, None))
                                if declaration:
                                    rec.causal.calls[key]['domain_ref'] = rec.causal.declaration(obj, {k: declaration[k] for k in ('run_id', 'store_id', 'role')})
                            if observer == 'Store.transact':
                                fault(store_request(b, rec.limits) == request, 'REQUEST_HASH_CONFLICT')
                            elif observer == 'FixtureStore.advance':
                                fault(drive_request(b.get('value'), rec.limits) == request, 'REQUEST_HASH_CONFLICT')
                                ref = rec.owner(obj, None)
                                if ref in rec.drive_identities:
                                    rec.causal.calls[key]['domain_ref'] = ref
                            row = rec.causal.close_call(key, out=projected)
                            if row['parent_call_ref']:
                                rec.causal.link(row['parent_call_ref'], key, 'SAME_THREAD_NESTED_CALL')
                        rec._atomic(_publish_return)
                    except BaseException as ex:
                        rec.invalid(ex.code if type(ex) is c.CaptureFault else 'CAUSAL_SCHEMA_INVALID')
                return out
            self.patch(owner, name, wrapped)

        def fixture_constructor(self, cls):
            old = cls.__dict__.get('__init__')
            c.require(type(old) is types.FunctionType, 'UNSUPPORTED_OBSERVER_API')
            sig = inspect.signature(old, eval_str=False)
            c.require(list(sig.parameters) == ['self', 'root', 'run_id', 'scope', 'test_fault', 'test_ready'] and all((sig.parameters[k].kind is inspect.Parameter.KEYWORD_ONLY for k in ('test_fault', 'test_ready'))), 'UNSUPPORTED_OBSERVER_SIGNATURE')
            self.fixture_class = cls
            capture = self

            @c.functools.wraps(old)
            def wrapped(obj, *args, **kwargs):
                try:
                    out = old(obj, *args, **kwargs)
                except BaseException:
                    if capture.active and capture.active['test_id'] == capture.negative_id:
                        capture.emit('FIXTURE_CONSTRUCTION_EXCEPTION')
                    raise
                if capture.active and capture.active['test_id'] == capture.negative_id:
                    try:

                        def _fixture_metadata(capture):
                            rid = sig.bind(obj, *args, **kwargs).arguments['run_id']
                            c.require(uuid_value(rid), 'INVALID_FIXTURE_CONSTRUCTION')
                            ref = capture.owner(obj, None)
                            c.require(ref is not None, 'CONSTRUCTION_OBJECT_UNSUPPORTED')
                            prior = capture.fixture_declarations.get(ref)
                            if prior and prior['run_id'] != rid:
                                capture.invalid('FIXTURE_CONSTRUCTION_IDENTITY_CHANGED')
                                capture.emit('FIXTURE_CONSTRUCTION_CONFLICT', object_ref=ref, previous=prior, observed_run_id=rid)
                                return out
                            if prior is None:
                                capture.reference()
                                capture.fixture_declarations[ref] = dict(run_id=rid, authority=FIXTURE_DECL, process_scope='PARENT_ONLY')
                            if ref not in capture.active['fixture_construction_refs']:
                                capture.reference()
                                capture.active['fixture_construction_refs'].append(ref)
                            capture.emit('FIXTURE_CONSTRUCTION_OBSERVED', object_ref=ref, **capture.fixture_declarations[ref])
                        capture._atomic(_fixture_metadata)
                    except BaseException as ex:
                        capture.invalid(ex.code if isinstance(ex, c.CaptureFault) else 'FIXTURE_CONSTRUCTOR_ERROR')
                return out
            self.patch(cls, '__init__', wrapped)

        def _stop_fields(self, tid, ended):
            f = self.active
            if f is None:
                self.invalid('STOP_WITHOUT_TEST')
                return
            try:
                c.require(f['test_id'] == tid, 'STOP_TEST_MISMATCH')
                if f['result'] is None:
                    if 'FAIL' in f['subtests']:
                        f['result'] = 'FAIL'
                    else:
                        f['missing'].append('RESULT_CALLBACK_NOT_RECORDED')
                        self.invalid('RESULT_CALLBACK_NOT_RECORDED')
                for key, (values, start, ptr) in self.record_baselines.items():
                    c.require(len(values) >= start, 'RECORD_SOURCE_REWOUND')
                    for i in range(start, len(values)):
                        v = values[i]
                        metadata = {}
                        if type(v) is dict:
                            for k in ('case', 'run_id', 'store_id', 'client_store_id', 'remote_store_id', 'role'):
                                if type(v.get(k)) is str:
                                    if k.endswith('_id') and k != 'case':
                                        c.require(re.fullmatch('[0-9a-f-]{36}', v[k]) is not None, 'INVALID_RECORD_IDENTITY')
                                    metadata[k] = c.public_id(v[k])
                        self.reference()
                        binding = dict(module=key[0], field=key[1], index=i, digest=c.digest_value(v, self.limits), raw_pointer=ptr + '/' + str(i) if ptr else None, observed_metadata=metadata)
                        f['record_links'].append(binding)
                        self.record_refs.append((binding, v))
                policy = self.entry['group_policies'][f['group_id']]
                override = self.policies.get(f['test_id'])
                has_identity = any((self.owner_contexts[k]['identity'] for k in f['owner_context_refs'])) or any(('run_id' in r['observed_metadata'] for r in f['record_links']))
                if f['test_id'] in self.snapshot_ids:
                    f['domain_scope'] = dict(status='FIXTURE_DRIVE_SNAPSHOT_RETURN', reason='Typed Drive run/head observation, not Store identity')
                    if not f['drive_snapshot_refs'] or f.get('drive_missing'):
                        f['missing'].append('DOMAIN_IDENTITY_NOT_RECORDED')
                elif f['test_id'] == self.negative_id:
                    f['domain_scope'] = dict(status='NEGATIVE_DOMAIN_FIXTURE_CLEANUP', reason='Observed construction declaration, not head')
                    if not f['fixture_construction_refs']:
                        f['missing'].append('FIXTURE_CONSTRUCTION_NOT_RECORDED')
                elif override and override['classification'] == 'NO_STORE_CONTROL':
                    f['domain_scope'] = dict(status='NOT_APPLICABLE', reason=override['reason'])
                elif override and override['classification'] == 'NEGATIVE_DOMAIN':
                    f['domain_scope'] = dict(status='NEGATIVE_DOMAIN_CONSTRUCTION_REFERENCE', reason=override['reason'])
                    if not f['construction_refs']:
                        f['missing'].append('CONSTRUCTION_IDENTITY_NOT_RECORDED')
                else:
                    f['domain_scope'] = dict(status='OBSERVED_OWNER_CONTEXT' if has_identity else 'DOMAIN_REFERENCES_REQUIRED' if policy['domain_required'] else 'NOT_APPLICABLE', reason=policy['no_store_reason'])
                    if policy['domain_required'] and (not has_identity):
                        f['missing'].append('DOMAIN_IDENTITY_NOT_RECORDED')
                if self.frame_summary['operands_missing']:
                    f['missing'].append('OPERAND_NOT_RECORDED')
                if self.frame_summary['returns_missing']:
                    f['missing'].append('RETURN_DIGEST_NOT_RECORDED')
                if any((r['digest']['status'] == 'NOT_RECORDED' for r in f['record_links'])):
                    f['missing'].append('RECORD_DIGEST_NOT_RECORDED')
                f['source_binding'] = self.entry.get('method_bindings', {}).get(f['test_id'], dict(status='NOT_RECORDED'))
                if f['source_binding']['status'] == 'NOT_RECORDED':
                    f['missing'].append('METHOD_BINDING_MISSING')
                self.reference(1)  # Q15 final marker; owner memberships were already charged.
                f['ended_ns'] = ended
                self.emit('TEST_END')
                f['event_end'] = len(self.events)
            except BaseException as ex:
                self.invalid(ex.code if isinstance(ex, c.CaptureFault) else 'STOP_OBSERVER_ERROR')
            finally:
                self.active = None

        def _close_frame(self, tid, ended):
            frame = self.active
            if frame and self.causal_enabled():
                self.attempt(self.causal.check_retained)
                row = self.causal_inventory[frame['test_id']]
                if frame['test_id'] == self.profile['parental_contract']['direct_selector']['test_id']:
                    self.attempt(self.verify_direct_completion)
                if row['classification'] == 'CAUSAL_DOMAIN':
                    refs = [r for r in self.causal.tables['retained_oracles'].values() if r['test_frame_id'] == frame['test_frame_id']]
                    if row['family'] in ('T', 'R') and (not refs):
                        frame['missing'].append('ORACLE_VALUE_MISSING')
                if any(self.causal.stacks.values()):
                    frame['missing'].append('CAUSAL_LINK_MISSING')
                    self.invalid('CAUSAL_LINK_MISSING')
                for protocol in self.causal.tables['protocol_instances'].values():
                    if protocol['test_frame_id'] != frame['test_frame_id']:
                        continue
                    if not protocol['exit_observations'] or protocol['exit_observations'][-1]['returncode'] is None:
                        frame['missing'].append('PENDING_CHILD_EXIT')
                    for message in protocol['observed_messages']:
                        if message['kind'] == 'OK' and message.get('command_identity') == 'CHILD_LOCAL_NOT_OBSERVED' and (protocol['action'] not in ('snapshot', 'initialize')):
                            frame['missing'].append('UNOBSERVED_CHILD_COMMAND')
            self._stop_fields(tid, ended)
            self.causal.frame = None
            self.causal.test = None

        def _typed_finish(self, raw=None):
            if self.active:
                self.invalid('UNFINISHED_TEST')
            ids = [f['test_id'] for f in self.frames]
            if len(ids) != len(set(ids)) or set(ids) != set(self.entry['expected_test_ids']):
                self.invalid('INCOMPLETE_TEST_SET')
            for b, v in self.record_refs:
                if c.digest_value(v, self.limits) != b['digest']:
                    self.invalid('RECORD_MUTATED_AFTER_TEST')
                if raw is not None and b['raw_pointer']:
                    try:
                        c.require(c.digest_value(c.pointer(raw, b['raw_pointer']), self.limits) == b['digest'], 'INVALID_RECORD_BINDING')
                    except c.CaptureFault as ex:
                        self.invalid(ex.code)
            if self.patches:
                self.invalid('OBSERVERS_NOT_RESTORED')
            try:
                self.projector.check()
            except c.CaptureFault as ex:
                self.invalid(ex.code)
            self.projector.erase()
            try:
                self._drain()
                self._atomic(lambda draft: draft.events.close(), seal=True)
                self._drain()
            except BaseException as ex:
                self.invalid(ex.code if isinstance(ex, c.CaptureFault) else 'PAGE_FINALIZATION_ERROR')
            for f in self.frames:
                f['capture_completeness'] = 'INCOMPLETE' if f['missing'] else 'CAPTURED_FIELDS_PENDING_REVIEW'
            out = dict(schema='d5.typed-sidecar.v1', capture_run_id=self.run_id, scope=self.entry['id'], status='INVALID_CAPTURE' if self.errors else 'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW', frames=self.frames, pages=self.events.manifest, event_count=len(self.events), pages_bytes=self.events.total_bytes, peak_page_buffer_bytes=self.events.peak_buffer_bytes, owner_contexts=self.owner_contexts, construction_declarations=self.declarations, drive_identities=self.drive_identities, drive_observations=self.drive_observations, fixture_construction_declarations=self.fixture_declarations, errors=list(self.errors), observers_restored=self.restored, worker_context=c.environment(), raw_functional_status=raw.get('status') if type(raw) is dict else 'NOT_RECORDED', child_context_scope='ONLY_EXISTING_PROTOCOL_RECORDS_NOT_PARENT_INSTRUMENTATION', global_review='OPEN', closure=False, D5_closed=False, semantic_baseline=dict(SUPPORTS_BOUNDED=81, PARTIAL=3), sufficiency='REVIEW_PENDING', new_distinct_functional_tests=0)
            if len(encode(out)) > self.limits['index_sidecar_bytes']:
                return dict(schema=out['schema'], status='INVALID_CAPTURE', errors=['SIDECAR_BUDGET'], closure=False)
            return out

        def finish(self, raw=None):
            self.attempt(self.causal.check_retained)
            for module, values, digest in self.causal_sources.values():
                if module.__dict__.get('ORACLES') is not values or c.digest_value(values, self.limits) != digest:
                    self.invalid('ORACLE_VALUE_MUTATED')
            out = self._typed_finish(raw)
            out.update(schema=NORMAL_SCHEMA, semantic_baseline=dict(SUPPORTS_BOUNDED=83, PARTIAL=1), shared_reference_count=self.references, **self.causal.tables)
            for row in out['retained_oracles'].values():
                f = next((f for f in out['frames'] if f['test_frame_id'] == row['test_frame_id']))
                links = [b for b in f['record_links'] if (b['module'], b['field'], b['index']) == (row['source_module'], row['source_field'], row['source_index'])]
                if len(links) != 1 or links[0]['digest'] != row['value_digest']:
                    self.invalid('ORACLE_VALUE_MISSING')
                else:
                    key = next((k for k, v in out['retained_oracles'].items() if v is row))
                    links[0]['sidecar_pointer'] = '/retained_oracles/' + key + '/value'
            out['errors'] = list(self.errors)
            if self.errors:
                out['status'] = 'INVALID_CAPTURE'
            elif any((f['missing'] for f in out.get('frames', []))):
                out['status'] = 'INCOMPLETE_CAPTURE'
            if len(encode(out)) > self.limits['index_sidecar_bytes']:
                return dict(schema=NORMAL_SCHEMA, status='INVALID_CAPTURE', errors=['SIDECAR_BUDGET'], closure=False)
            return out

        def start(self,test):
            # Original unittest method, entropy and clock are observed before locking.
            tid=p.c.public_id(test.id());frame_id=str(p.c.uuid.uuid4());started=p.c.time.monotonic_ns()
            def metadata(draft):
                p.fault(draft.active is None,'NESTED_TEST_LIFECYCLE')
                p.fault(tid in draft.entry['expected_test_ids'],'UNEXPECTED_TEST_ID')
                p.fault(len(draft.frames)<draft.limits['frames'],'FRAME_BUDGET')
                group=next((g for g in draft.entry['expected_groups'] if tid.split('.')[-3]==g),None)
                if group is None:
                    p.fault(len(draft.entry['expected_groups'])==1,'INVALID_GROUP_BINDING');group=next(iter(draft.entry['expected_groups']))
                draft.frame_summary=dict(operands_missing=False,returns_missing=False)
                frame=dict(test_id=tid,group_id=group,test_frame_id=frame_id,capture_run_id=draft.run_id,owner_context_refs=[],event_start=len(draft.events),event_count=0,result=None,subtests=[],record_links=[],missing=[],started_ns=started)
                draft.frames.append(frame);draft.active=frame;draft.record_baselines=draft.source_positions()
                draft.emit('TEST_START');frame.update(construction_refs=[],drive_snapshot_refs=[],fixture_construction_refs=[])
                draft.causal_test=test;draft.causal.begin(frame,test)
            self._observe(metadata)
            # Pin reads and monkeypatch setup are outside the transaction.
            if self.active and not self._failed:
                if self.causal_enabled():self.attempt(self.bind_deferred)
                if self.causal.selected():self.attempt(self.bind_direct)
        def stop(self,test,result):
            tid=test.id();ended=p.c.time.monotonic_ns()
            self._observe(lambda draft:draft._close_frame(tid,ended))
            if self.errors:result.stop()  # Original callback, no ledger lock.
        def constructor(self,cls):
            old=cls.__dict__.get('__init__');p.fault(type(old) is p.types.FunctionType,'UNSUPPORTED_OBSERVER_API')
            sig=p.inspect.signature(old,eval_str=False)
            params=['self','path','run_id','store_id','role','reducer','genesis','hook']
            p.fault(list(sig.parameters)==params and sig.parameters['hook'].kind is p.inspect.Parameter.KEYWORD_ONLY,'UNSUPPORTED_OBSERVER_SIGNATURE')
            rec=self
            @p.functools.wraps(old)
            def wrapped(obj,*args,**kwargs):
                try:out=old(obj,*args,**kwargs)
                except BaseException:
                    rec.emit('CONSTRUCTION_EXCEPTION');raise
                def metadata(draft):
                    values=sig.bind(obj,*args,**kwargs).arguments
                    d={k:values[k] for k in ('run_id','store_id','role')}
                    p.fault(p.t.uuid_value(d['run_id']) and p.t.uuid_value(d['store_id']) and d['role'] in ('CLIENT','REMOTE'),'INVALID_CONSTRUCTION_METADATA')
                    ref=draft.owner(obj,None);p.fault(ref is not None,'CONSTRUCTION_OBJECT_UNSUPPORTED')
                    prior=draft.declarations.get(ref)
                    p.fault(prior is None or all(prior[k]==d[k] for k in d),'CONSTRUCTION_IDENTITY_CHANGED')
                    if prior is None:draft.reference()
                    draft.declarations[ref]=dict(d,authority=p.t.DECLARATION,process_scope='PARENT_ONLY')
                    if draft.active and ref not in draft.active['construction_refs']:
                        draft.reference();draft.active['construction_refs'].append(ref)
                    draft.emit('CONSTRUCTION_OBSERVED',object_ref=ref,**draft.declarations[ref])
                    if draft.causal_enabled():draft.causal.declaration(obj,d)
                rec._observe(metadata);return out
            self.patch(cls,'__init__',wrapped)
        def wrap_return(self,cls,name):
            old=cls.__dict__.get(name);p.fault(type(old) is p.types.FunctionType,'UNSUPPORTED_OBSERVER_API')
            rec=self
            @p.functools.wraps(old)
            def observed(obj,*args,**kwargs):
                key=None
                if name=='perform' and rec.causal_enabled():
                    def before(draft):
                        return draft.causal.open_call(cls.__name__+'.perform',obj,'perform',dict(args_digest=p.bounded_builtin((args,kwargs),draft.limits)))
                    key=rec._observe(before)
                try:out=old(obj,*args,**kwargs)
                except BaseException as ex:
                    def failure(draft):
                        data={}
                        if key is not None:data['causal']=draft.causal.close_call(key,exception=draft.exception(ex),publish=False)
                        draft.emit('CALL_EXCEPTION',method=name,exception_type=type(ex).__name__,**data)
                    rec._observe(failure);raise
                def after(draft):
                    data={}
                    if key is not None:data['causal']=draft.causal.close_call(key,out=dict(result_digest=p.bounded_builtin(out,draft.limits)),publish=False)
                    ref=draft.owner(obj,out)
                    draft.emit('CALL_RETURN',method=name,owner_ref=ref,result_digest=p.c.digest_value(out,draft.limits),**data)
                    if name=='snapshot' and draft.causal.selected():
                        header=p.child_header(out,p.policy_for(draft.profile['parental_contract'],'DRIVE','snapshot'),draft.profile['parental_contract'],draft.profile['projection_schemas'],draft.limits)
                        ctx=draft.causal.context();draft.reference()
                        draft.parent_snapshots.append(dict(context=ctx,header=header,authority='OWN_FIXTURE_SNAPSHOT'))
                rec._observe(after);return out
            self.patch(cls,name,observed)

    return Recorder,Bindings
