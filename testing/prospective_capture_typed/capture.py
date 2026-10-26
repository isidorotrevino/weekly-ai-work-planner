# SPDX-License-Identifier: GPL-3.0-only
"""I76 typed capture components; historical imports require separate I77 authority."""
import json
import hashlib
import hmac
import inspect
import pathlib
import os
from pathlib import Path
import re
import sys
import types
from testing.prospective_capture import capture as c
from testing.prospective_capture_paged import capture as previous

ROOT=c.ROOT
REGISTRY='docs/validation/D5-TYPED-CAPTURE-REGISTRY.json'
AUTHORITY='docs/validation/D5-I77-capture-authorization.json'
DESTINATION='docs/validation/D5-I77-P01'
LAUNCH_COPY='docs/validation/D5-I77-P01-launch.json'
LIMITS=dict(c.LIMITS,events_campaign=131072,page_bytes=2097152,pages=32,event_pages_total_bytes=67108864,index_sidecar_bytes=12582912,context_bytes=12582912,launch_bytes=12582912,package_bytes=117444608,evidence_unique_bytes=134217728,evidence_read_bytes=268435456)
DECLARATION='OBSERVED_CONSTRUCTION_ARGUMENTS_AFTER_SUCCESS_NOT_HEAD_VERIFIED'
PAGE_SCHEMA='d5.capture-event-page.v1'
READY_KEYS={'event','scope','lease','pid','pgid','raw_inode','sidecar_inode','directory_device','directory_inode'}


def scope(value):c.require(value=='P01','INVALID_SCOPE');return value

def encode(value):return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf8')

def write_all(fd,data):
    left=memoryview(data)
    while left:
        n=os.write(fd,left);c.require(n>0,'WRITE_INCOMPLETE');left=left[n:]


def read_registry(root=ROOT):
    reader=c.Reader(root);reg=c.strict_json(reader.read(REGISTRY))
    keys={'schema','contract_path','contract_sha256','legacy_registry_sha256','entry','policies','constructor_observer','observer_specs','limits','functional_execution_authorized','semantic_baseline','snapshot_adapter','snapshot_scopes','negative_DI28','operand_scopes','class_allowlist','path_projection','exception_projection','typed_encoding','stdlib_binding'}
    c.require(set(reg)==keys and reg['schema']=='d5.typed-capture-registry.v1' and reg['functional_execution_authorized'] is False,'INVALID_REGISTRY')
    c.require(reg['contract_path']=='docs/validation/D5-I75-design-review.json','INVALID_REGISTRY');body=reader.read(reg['contract_path']);c.require(c.sha(body)==reg['contract_sha256'],'STALE_CONTRACT');design=c.strict_json(body)
    legacy=reader.read(previous.REGISTRY);c.require(c.sha(legacy)==reg['legacy_registry_sha256'],'STALE_LEGACY_REGISTRY');old=c.strict_json(legacy)
    for key in ('entry','policies','constructor_observer','observer_specs','limits','semantic_baseline'):c.require(reg[key]==old[key],'INVALID_REGISTRY')
    for key in ('snapshot_adapter','snapshot_scopes','negative_DI28','operand_scopes','class_allowlist','path_projection','exception_projection','typed_encoding'):c.require(reg[key]==design[key],'INVALID_REGISTRY')
    c.require(reg['policies']==design['previous_I72_policies_preserved'] and reg['limits']==design['proposed_limits'],'INVALID_REGISTRY')
    c.require(reg['entry']['expected_test_ids']==design['expected_test_ids'] and reg['entry']['expected_groups']==design['expected_groups'] and len(set(design['expected_test_ids']))==321,'INVALID_MANIFEST')
    c.require(len(reg['snapshot_scopes'])==29 and len(reg['operand_scopes'])==5,'INVALID_POLICY')
    for a in design['source_anchors']:c.require(c.sha(reader.read(a['path']))==a['sha256'],'STALE_POLICY_SOURCE')
    c.require(reg['stdlib_binding']==StdlibGuard().describe(),'STALE_STDLIB_BINDING');reader.finish();return reg


def authority_inputs():
    return {f'testing/prospective_capture_typed/{n}' for n in ('capture.py','worker.py','test_typed_capture.py','run_typed_lab.py','README.md')}|{REGISTRY,'testing/prospective_capture/capture.py','testing/prospective_capture_paged/capture.py','docs/validation/D5-I75-design-review.json','docs/validation/D5-I76-tests-raw.json','docs/validation/D5-I76-results.json','docs/validation/D5-I76-integrity.json'}|{f'docs/validation/D5-I{i}-integrity.json' for i in (69,70,71,72,73,74,75)}


def authority(root,requested,reg):
    scope(requested);reader=c.Reader(root)
    try:a=c.strict_json(reader.read(AUTHORITY))
    except FileNotFoundError:raise c.CaptureFault('I77_AUTHORIZATION_REQUIRED') from None
    c.require(set(a)=={'schema','phase','scopes','registry_sha256','capture_inputs'} and a['schema']=='d5.typed-capture-authority.v1' and a['phase']=='I77_EXPLICITLY_APPROVED' and a['scopes']==['P01'],'I77_AUTHORIZATION_REQUIRED')
    c.require(a['registry_sha256']==c.sha(reader.read(REGISTRY)) and type(a['capture_inputs']) is dict and authority_inputs()<=set(a['capture_inputs']),'STALE_AUTHORITY')
    for name,h in a['capture_inputs'].items():c.require(c.sha(reader.read(c.public_path(name)))==h,'STALE_AUTHORITY')
    evidence=c.strict_json(reader.read('docs/validation/D5-I76-tests-raw.json'));c.require(evidence.get('status')=='PASS' and evidence.get('tests_run')==80 and evidence.get('functional_campaigns_executed')==0 and evidence.get('forbidden_imports')==[],'COMPONENT_VALIDATION_REQUIRED')
    seal=c.strict_json(reader.read('docs/validation/D5-I76-integrity.json'));c.require(bool(seal.get('artifacts')),'COMPONENT_VALIDATION_REQUIRED')
    for name,h in seal['artifacts'].items():c.require(a['capture_inputs'].get(name)==h and c.sha(reader.read(name))==h,'STALE_AUTHORITY')
    reader.finish();return a


class ChannelRoot:
    """Inherited directory capability, never a worker-supplied filesystem path."""
    def __init__(self,fd,lease):
        self.fd=fd;self.nonce=lease;st=os.fstat(fd);c.require(c.stat.S_ISDIR(st.st_mode),'INVALID_DIRECTORY_CHANNEL');self.root_identity=(st.st_dev,st.st_ino);self.verify()
    def directory(self):
        st=os.fstat(self.fd);c.require((st.st_dev,st.st_ino)==self.root_identity,'OWNER_ROOT_CHANGED');return os.dup(self.fd)
    def verify(self):
        d=self.directory()
        try:
            fd=os.open('OWNER',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=d)
            try:c.require(c.stat.S_ISREG(os.fstat(fd).st_mode) and os.fstat(fd).st_size==36 and os.read(fd,128)==self.nonce.encode(),'INVALID_DIRECTORY_OWNER')
            finally:os.close(fd)
        finally:os.close(d)
    create=c.OwnedRoot.create


class PageSink:
    """Only the current encoded page is buffered; global slicing is unsupported."""
    def __init__(self,owner,run_id,limits=None):
        self.owner=owner;self.run_id=run_id;self.limits=dict(LIMITS,**(limits or {}));self.chunks=[];self.chunk_bytes=0;self.count=0;self.page_first=0;self.manifest=[];self.total_bytes=0;self.closed=False;self.peak_buffer_bytes=0
    def __len__(self):return self.count
    def header(self,count):
        return dict(schema=PAGE_SCHEMA,capture_run_id=self.run_id,page_index=len(self.manifest)+1,first_sequence=self.page_first,last_sequence=self.page_first+count-1,event_count=count)
    def size(self,count,chunk_bytes):return len(encode(self.header(count)))+len(b',"events":[]}')-1+chunk_bytes+max(0,count-1)
    def append(self,event):
        c.require(not self.closed,'PAGES_CLOSED');c.require(type(event) is dict,'INVALID_EVENT_SEQUENCE');b=encode(event)
        c.require(len(b)<=self.limits['event_bytes'],'EVENT_SIZE_BUDGET');c.require(self.count<self.limits['events_campaign'],'EVENT_CAMPAIGN_BUDGET')
        c.require(type(event.get('sequence')) is int and event['sequence']==self.count,'INVALID_EVENT_SEQUENCE')
        if self.chunks and self.size(len(self.chunks)+1,self.chunk_bytes+len(b))>self.limits['page_bytes']:self.flush()
        c.require(len(self.manifest)<self.limits['pages'],'PAGE_COUNT_BUDGET')
        n=self.size(len(self.chunks)+1,self.chunk_bytes+len(b));c.require(n<=self.limits['page_bytes'],'PAGE_BYTES_BUDGET')
        c.require(self.total_bytes+n<=self.limits['event_pages_total_bytes'],'PAGES_TOTAL_BUDGET')
        self.chunks.append(b);self.chunk_bytes+=len(b);self.count+=1;self.peak_buffer_bytes=max(self.peak_buffer_bytes,n)
    def flush(self):
        if not self.chunks:return
        header=self.header(len(self.chunks));b=encode(header)[:-1]+b',"events":['+b','.join(self.chunks)+b']}'
        c.require(len(b)==self.size(len(self.chunks),self.chunk_bytes) and len(b)<=self.limits['page_bytes'],'PAGE_BYTES_BUDGET')
        c.require(self.total_bytes+len(b)<=self.limits['event_pages_total_bytes'] and len(self.manifest)<self.limits['pages'],'PAGES_TOTAL_BUDGET')
        name=f'event-{len(self.manifest)+1:04}.json';fd=self.owner.create(name)
        try:write_all(fd,b)
        finally:os.close(fd)
        self.manifest.append(dict(name=name,sha256=c.sha(b),bytes=len(b),**{k:header[k] for k in ('page_index','first_sequence','last_sequence','event_count')}));self.total_bytes+=len(b);self.page_first=self.count;self.chunks=[];self.chunk_bytes=0
    def close(self):
        if not self.closed:self.flush();self.closed=True


FIXTURE_DECL='OBSERVED_FIXTURE_CONSTRUCTION_ARGUMENTS_AFTER_SUCCESS_NOT_HEAD'
DRIVE_OBS='OBSERVED_FIXTURE_DRIVE_SNAPSHOT_RETURN_NOT_DURABLE_STORE_ID'
TYPED_SCHEMA='d5.typed-operand-projection.v1'


def uuid_value(value):return type(value) is str and re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',value) is not None


def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode('ascii')


class StdlibGuard:
    def __init__(self):
        self.path_type=pathlib.PosixPath;self.pure_type=pathlib.PurePath;self.lexical=pathlib.PurePath.as_posix;self.string=pathlib.PurePath.__str__;self.args=BaseException.__dict__['args'];self.source=Path(pathlib.__file__);self.source_hash=c.sha(self.source.read_bytes())
    def check(self):
        c.require(pathlib.PosixPath is self.path_type and pathlib.PurePath is self.pure_type and pathlib.PurePath.as_posix is self.lexical and pathlib.PurePath.__str__ is self.string and BaseException.__dict__['args'] is self.args,'STDLIB_BINDING_CHANGED')
        c.require(c.sha(self.source.read_bytes())==self.source_hash,'STDLIB_SOURCE_CHANGED')
    def describe(self):
        self.check();return dict(python=c.platform.python_version(),implementation=c.platform.python_implementation(),platform=c.platform.system(),module='pathlib',source_sha256=self.source_hash,lexical_parameters=list(inspect.signature(self.lexical).parameters),lexical_code_sha256=c.sha(self.lexical.__code__.co_code),string_code_sha256=c.sha(self.string.__code__.co_code),exception_args_descriptor_type=type(self.args).__name__)


class ClassBindings:
    """Exact object references; synthetic classes may be injected by AT only."""
    def __init__(self,rows):
        self.rows={ref:dict(cls=cls,sha256=sha,module=module,name=name) for ref,cls,sha,module,name in rows};self.check()
    def check(self):
        for ref,row in self.rows.items():
            cls=row['cls'];c.require(type(cls) is type,'UNSUPPORTED_CLASS_BINDING')
            if row['module'] is not None:c.require(sys.modules.get(row['module'].__name__) is row['module'] and row['module'].__dict__.get(row['name']) is cls,'CLASS_BINDING_CHANGED')
    def class_row(self,value):return next(((ref,row) for ref,row in self.rows.items() if value is row['cls']),None)
    def instance_row(self,value):return next(((ref,row) for ref,row in self.rows.items() if type(value) is row['cls'] and ref!='builtins.dict'),None)


def loaded_bindings(reg,root=ROOT):
    rows=[];reader=c.Reader(root)
    for spec in reg['class_allowlist']:
        ref=spec['id']
        if ref=='builtins.dict':rows.append((ref,dict,None,None,None));continue
        module_name,name=ref.rsplit('.',1);module=sys.modules.get(module_name);c.require(module is not None,'CLASS_MODULE_NOT_LOADED');cls=module.__dict__.get(name)
        c.require(type(cls) is type and cls.__bases__==(ValueError,) and cls.__module__==module_name and cls.__name__==name,'UNSUPPORTED_CLASS_BINDING')
        a=spec['source'];c.require(c.sha(reader.read(a['path']))==a['sha256'],'STALE_CLASS_SOURCE');rows.append((ref,cls,a['sha256'],module,name))
    reader.finish();return ClassBindings(rows)


class Projector:
    def __init__(self,run_id,bindings=None,limits=None,key=None):
        self.run_id=run_id;self.bindings=bindings or ClassBindings([('builtins.dict',dict,None,None,None)]);self.guard=StdlibGuard();self.limits=dict(LIMITS,**(limits or {}));self._key=os.urandom(32) if key is None else key;c.require(type(self._key) is bytes and len(self._key)==32,'INVALID_PATH_KEY')
    def check(self):self.guard.check();self.bindings.check()
    def erase(self):self._key=b''
    def observe(self,value,allowed):
        plain=c.digest_value(value,self.limits)
        if plain['status']=='OBSERVED_DIGEST' or plain.get('reason')!='UNSUPPORTED_OPERAND':return plain
        try:
            self.check();kind=type(value);graph=None
            if kind is self.guard.path_type:graph='exact-posix-path'
            elif kind is tuple and len(value)==2 and type(value[0]) is self.guard.path_type and type(value[1]) is str:graph='exact-tuple(exact-posix-path,builtin-str)'
            elif kind is list and all(type(v) is self.guard.path_type for v in value):graph='exact-list(exact-posix-path)'
            elif type(value) is type:
                row=self.bindings.class_row(value)
                if row:graph='class-'+row[0]
            else:
                row=self.bindings.instance_row(value)
                if row:graph='exact-'+row[0].rsplit('.',1)[-1]+'-instance-args-projection'
            c.require(graph is not None and graph in allowed,'TYPED_OPERAND_NOT_ALLOWED')
            digest=hashlib.sha256();used=0;refs=set();contains_path=False
            def charge(n):
                nonlocal used
                used+=n;c.require(used<=self.limits['operand_bytes'],'OPERAND_BUDGET')
            def emit(b):charge(len(b));digest.update(b)
            def leaf(node):emit(canonical(node))
            def visit(v,depth):
                nonlocal contains_path
                c.require(depth<=self.limits['depth'],'OPERAND_DEPTH');k=type(v)
                if k is self.guard.path_type:
                    c.require(len(self._key)==32,'PATH_KEY_ERASED');text=self.guard.lexical(v);c.require(type(text) is str and len(text)<=self.limits['operand_bytes'],'OPERAND_BUDGET');token=hmac.new(self._key,digestmod=hashlib.sha256);prefix=b'd5.path.lexical.v1\0';charge(len(prefix));token.update(prefix)
                    for i in range(0,len(text),4096):chunk=text[i:i+4096].encode('utf8','surrogatepass');charge(len(chunk));token.update(chunk)
                    contains_path=True;leaf(dict(kind='posix-path',token=token.hexdigest(),scope=self.run_id))
                elif k in (tuple,list):
                    emit(b'{"items":[')
                    for i,item in enumerate(v):
                        if i:emit(b',')
                        visit(item,depth+1)
                    emit(b'],"kind":'+canonical('tuple' if k is tuple else 'list')+b'}')
                elif k is type:
                    row=self.bindings.class_row(v);c.require(row is not None,'TYPED_OPERAND_NOT_ALLOWED');ref,data=row;refs.add(ref);leaf(dict(kind='class',ref=ref,source_sha256=data['sha256']))
                elif self.bindings.instance_row(v) is not None:
                    ref,data=self.bindings.instance_row(v);args=self.guard.args.__get__(v,type(v));c.require(type(args) is tuple and len(args)==1 and type(args[0]) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,79}',args[0]) is not None,'EXCEPTION_ARGS_NOT_ALLOWED')
                    result=c.digest_value(args,self.limits);c.require(result['status']=='OBSERVED_DIGEST','OPERAND_BUDGET');charge(result['bytes']);refs.add(ref);leaf(dict(kind='exception-type-args',class_ref=ref,source_sha256=data['sha256'],args_sha256=result['sha256']))
                else:
                    result=c.digest_value(v,self.limits);c.require(result['status']=='OBSERVED_DIGEST','TYPED_OPERAND_NOT_ALLOWED');charge(result['bytes']);leaf(dict(kind='builtin-i70',python_type=k.__name__,sha256=result['sha256'],bytes=result['bytes']))
            emit(b'd5.typed-operand-projection.v1\0');visit(value,0);self.check()
            out=dict(status='OBSERVED_TYPED_PROJECTION',schema=TYPED_SCHEMA,root_type=kind.__name__,projection_kind=graph,digest_algorithm='SHA256_OF_TYPED_REPRESENTATION',digest_hex=digest.hexdigest(),class_refs=sorted(refs))
            if contains_path:out.update(path_token_algorithm='HMAC-SHA256',path_scope=self.run_id)
            return out
        except (c.CaptureFault,ValueError,TypeError,RecursionError) as ex:return dict(status='NOT_RECORDED',reason=ex.code if isinstance(ex,c.CaptureFault) else 'TYPED_PROJECTION_ERROR',sha256=None)


def typed_witness(value,allowed,run_id):
    c.require(type(value) is dict and value.get('status')=='OBSERVED_TYPED_PROJECTION' and value.get('schema')==TYPED_SCHEMA and value.get('digest_algorithm')=='SHA256_OF_TYPED_REPRESENTATION','INVALID_TYPED_WITNESS')
    c.require(value.get('projection_kind') in allowed and type(value.get('digest_hex')) is str and re.fullmatch('[0-9a-f]{64}',value['digest_hex']) is not None,'INVALID_TYPED_WITNESS')
    refs=value.get('class_refs');c.require(type(refs) is list and refs==sorted(set(refs)) and set(refs)<={'builtins.dict','source_ingest.plane_fixture.PlaneError','source_ingest.eligibility_fixture.EligibilityError'},'INVALID_TYPED_WITNESS')
    has_path='posix-path' in value['projection_kind'];keys={'status','schema','root_type','projection_kind','digest_algorithm','digest_hex','class_refs'}|({'path_token_algorithm','path_scope'} if has_path else set())
    c.require(set(value)==keys,'INVALID_TYPED_WITNESS')
    if has_path:c.require(value['path_scope']==run_id and value['path_token_algorithm']=='HMAC-SHA256' and not refs,'INVALID_TYPED_WITNESS')
    else:c.require(len(refs)==1,'INVALID_TYPED_WITNESS')
    graph=value['projection_kind']
    expected={'exact-posix-path':('PosixPath',[]),'exact-tuple(exact-posix-path,builtin-str)':('tuple',[]),'exact-list(exact-posix-path)':('list',[])}
    if graph.startswith('class-'):expected[graph]=('type',[graph[6:]])
    for name,ref in [('PlaneError','source_ingest.plane_fixture.PlaneError'),('EligibilityError','source_ingest.eligibility_fixture.EligibilityError')]:expected['exact-'+name+'-instance-args-projection']=(name,[ref])
    c.require(graph in expected and (value.get('root_type'),refs)==expected[graph],'INVALID_TYPED_WITNESS')


class Recorder(c.Recorder):
    def __init__(self,entry,owner,policies=(),limits=None,profile=None,bindings=None):
        super().__init__(entry,dict(LIMITS,**(limits or {})));self.events=PageSink(owner,self.run_id,self.limits);self.policies={p['test_id']:p for p in policies};self.declarations={};self.frame_summary={};self.references=0;self.profile=profile or {};self.snapshot_ids={r['test_id'] for r in self.profile.get('snapshot_scopes',[])};self.negative_id=self.profile.get('negative_DI28',{}).get('criterion',{}).get('test_id');self.operand_rows={r['test_id']:r for r in self.profile.get('operand_scopes',[])};self.projector=Projector(self.run_id,bindings,self.limits);self.fixture_class=None;self.drive_identities={};self.drive_observations={};self.fixture_declarations={};self.pending_drive=None
    def reference(self,n=1):self.references+=n;c.require(self.references<=self.limits['refs'],'REFERENCE_BUDGET')
    def start(self,test):
        self.frame_summary=dict(operands_missing=False,returns_missing=False)
        super().start(test)
        if self.active:self.active.update(construction_refs=[],drive_snapshot_refs=[],fixture_construction_refs=[])
    def emit(self,kind,**data):
        if kind=='CALL_RETURN' and self.pending_drive is not None:
            owner,ref=self.pending_drive
            if data.get('owner_ref')==owner:data['drive_snapshot_ref']=ref
            self.pending_drive=None
        try:
            frame=self.active
            if frame:c.require(frame['event_count']<self.limits['events_test'],'EVENT_TEST_BUDGET')
            item=dict(event=c.public_id(kind),sequence=len(self.events),test_frame_id=frame['test_frame_id'] if frame else None,**data)
            self.events.append(item)
            if frame:
                frame['event_count']+=1
                self.frame_summary['operands_missing']|=bool(item.get('operands_missing'))
                self.frame_summary['returns_missing']|=item.get('result_digest',{}).get('status')=='NOT_RECORDED'
        except (c.CaptureFault,OSError,ValueError,TypeError,RecursionError) as ex:self.invalid(ex.code if isinstance(ex,c.CaptureFault) else 'PAGE_WRITE_ERROR')
    def outcome(self,name,subtest=False,failed=False):
        if self.active is None:self.invalid('RESULT_WITHOUT_TEST');return
        if subtest:self.active['subtests'].append('FAIL' if failed else 'PASS')
        else:
            if self.active['result'] is not None and self.active['result']!=name:self.invalid('MULTIPLE_TEST_RESULTS')
            self.active['result']=name
        self.emit('TEST_RESULT',outcome=name,subtest_failed=bool(subtest and failed))
    def owner(self,obj,out):
        self.pending_drive=None
        old=self.owners.get(id(obj))
        if old is None or old[0]() is not obj:self.reference()
        ref=super().owner(obj,out)
        if ref and ref in self.declarations and self.owner_contexts[ref]['identity']:
            d=self.declarations[ref];actual=self.owner_contexts[ref]['identity']
            if any(actual.get(k)!=d[k] for k in ('run_id','store_id')):self.invalid('CONSTRUCTION_HEAD_IDENTITY_CONFLICT')
        if self.active and self.active['test_id'] in self.snapshot_ids and type(obj) is self.fixture_class and out is not None:
            try:
                c.require(type(out) is dict and out.get('schema')=='d5.fixture-drive-snapshot.v1' and uuid_value(out.get('run_id')) and type(out.get('version')) is int and 0<=out['version']<=1023 and type(out.get('head_sha256')) is str and re.fullmatch('[0-9a-f]{64}',out['head_sha256']) is not None,'INVALID_DRIVE_SNAPSHOT')
                prior=self.drive_identities.get(ref)
                if prior and prior['run_id']!=out['run_id']:self.invalid('DRIVE_IDENTITY_CHANGED')
                if prior is None:self.reference();self.drive_identities[ref]=dict(kind='FIXTURE_DRIVE_RUN',run_id=out['run_id'])
                self.reference(2);key='D'+str(len(self.drive_observations)+1);self.drive_observations[key]=dict(object_ref=ref,run_id=out['run_id'],version=out['version'],head_sha256=out['head_sha256'],authority=DRIVE_OBS,process_scope='PARENT_ONLY');self.active['drive_snapshot_refs'].append(key);self.pending_drive=(ref,key)
            except BaseException as ex:
                self.active.setdefault('drive_missing',True);self.invalid(ex.code if isinstance(ex,c.CaptureFault) else 'DRIVE_OBSERVER_ERROR')
        return ref
    def constructor(self,cls):
        old=cls.__dict__.get('__init__');c.require(type(old) is types.FunctionType,'UNSUPPORTED_OBSERVER_API')
        params=['self','path','run_id','store_id','role','reducer','genesis','hook'];signature=c.inspect.signature(old,eval_str=False)
        c.require(list(signature.parameters)==params and signature.parameters['hook'].kind is c.inspect.Parameter.KEYWORD_ONLY,'UNSUPPORTED_OBSERVER_SIGNATURE')
        capture=self;signature=c.inspect.signature(old,eval_str=False)
        @c.functools.wraps(old)
        def wrapped(obj,*args,**kwargs):
            try:out=old(obj,*args,**kwargs)
            except BaseException:
                capture.emit('CONSTRUCTION_EXCEPTION');raise
            try:
                args_bound=signature.bind(obj,*args,**kwargs).arguments
                d={k:args_bound[k] for k in ('run_id','store_id','role')}
                c.require(all(type(d[k]) is str and re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',d[k]) for k in ('run_id','store_id')) and type(d['role']) is str and d['role'] in ('CLIENT','REMOTE'),'INVALID_CONSTRUCTION_METADATA')
                ref=capture.owner(obj,None);c.require(ref is not None,'CONSTRUCTION_OBJECT_UNSUPPORTED')
                previous=capture.declarations.get(ref)
                if previous is not None and any(previous[k]!=d[k] for k in d):
                    capture.invalid('CONSTRUCTION_IDENTITY_CHANGED');capture.emit('CONSTRUCTION_IDENTITY_CONFLICT',object_ref=ref,previous=previous,observed=d);return out
                if previous is None:capture.reference()
                capture.declarations[ref]=dict(d,authority=DECLARATION,process_scope='PARENT_ONLY')
                if capture.active and ref not in capture.active['construction_refs']:capture.reference();capture.active['construction_refs'].append(ref)
                capture.emit('CONSTRUCTION_OBSERVED',object_ref=ref,**capture.declarations[ref])
            except BaseException as ex:capture.invalid(ex.code if isinstance(ex,c.CaptureFault) else 'CONSTRUCTOR_OBSERVER_ERROR')
            return out
        self.patch(cls,'__init__',wrapped)
    def fixture_constructor(self,cls):
        old=cls.__dict__.get('__init__');c.require(type(old) is types.FunctionType,'UNSUPPORTED_OBSERVER_API');sig=inspect.signature(old,eval_str=False)
        c.require(list(sig.parameters)==['self','root','run_id','scope','test_fault','test_ready'] and all(sig.parameters[k].kind is inspect.Parameter.KEYWORD_ONLY for k in ('test_fault','test_ready')),'UNSUPPORTED_OBSERVER_SIGNATURE');self.fixture_class=cls;capture=self
        @c.functools.wraps(old)
        def wrapped(obj,*args,**kwargs):
            try:out=old(obj,*args,**kwargs)
            except BaseException:
                if capture.active and capture.active['test_id']==capture.negative_id:capture.emit('FIXTURE_CONSTRUCTION_EXCEPTION')
                raise
            if capture.active and capture.active['test_id']==capture.negative_id:
                try:
                    rid=sig.bind(obj,*args,**kwargs).arguments['run_id'];c.require(uuid_value(rid),'INVALID_FIXTURE_CONSTRUCTION');ref=capture.owner(obj,None);c.require(ref is not None,'CONSTRUCTION_OBJECT_UNSUPPORTED');prior=capture.fixture_declarations.get(ref)
                    if prior and prior['run_id']!=rid:
                        capture.invalid('FIXTURE_CONSTRUCTION_IDENTITY_CHANGED');capture.emit('FIXTURE_CONSTRUCTION_CONFLICT',object_ref=ref,previous=prior,observed_run_id=rid);return out
                    if prior is None:capture.reference();capture.fixture_declarations[ref]=dict(run_id=rid,authority=FIXTURE_DECL,process_scope='PARENT_ONLY')
                    if ref not in capture.active['fixture_construction_refs']:capture.reference();capture.active['fixture_construction_refs'].append(ref)
                    capture.emit('FIXTURE_CONSTRUCTION_OBSERVED',object_ref=ref,**capture.fixture_declarations[ref])
                except BaseException as ex:capture.invalid(ex.code if isinstance(ex,c.CaptureFault) else 'FIXTURE_CONSTRUCTOR_ERROR')
            return out
        self.patch(cls,'__init__',wrapped)

    def operand(self,value,helper,slot):
        row=self.operand_rows.get(self.active['test_id']) if self.active else None
        if row and row['helper']==helper:
            try:
                out=self.projector.observe(value,row['operand_roles'].get(str(slot),[]))
                if out.get('status')=='NOT_RECORDED' and out.get('reason') not in ('TYPED_OPERAND_NOT_ALLOWED','UNSUPPORTED_OPERAND','EXCEPTION_ARGS_NOT_ALLOWED'):self.invalid(out.get('reason','TYPED_PROJECTION_ERROR'))
                return out
            except BaseException:
                self.invalid('TYPED_PROJECTION_ERROR');return dict(status='NOT_RECORDED',reason='TYPED_PROJECTION_ERROR',sha256=None)
        return c.digest_value(value,self.limits)

    def install(self,targets=()):
            c.require(not self.patches,'ALREADY_INSTALLED')
            capture=self
            try:
                for name in c.CALLBACKS:
                    old=c.unittest.TestResult.__dict__.get(name);c.require(type(old) is types.FunctionType,'UNSUPPORTED_UNITTEST_API')
                    def factory(old,name):
                        @c.functools.wraps(old)
                        def wrapped(result,test,*args,**kwargs):
                            if name=='startTest':capture.safe(capture.start,test)
                            out=old(result,test,*args,**kwargs)
                            if name=='stopTest':capture.safe(capture.stop,test,result)
                            elif name not in ('startTest',):
                                mapping=dict(addSuccess='PASS',addFailure='FAIL',addError='ERROR',addSkip='SKIP',addExpectedFailure='EXPECTED_FAILURE',addUnexpectedSuccess='UNEXPECTED_SUCCESS',addSubTest='SUBTEST')
                                capture.safe(capture.outcome,mapping[name],name=='addSubTest',name=='addSubTest' and len(args)>1 and args[1] is not None)
                            return out
                        return wrapped
                    self.patch(c.unittest.TestResult,name,factory(old,name))
                for name in c.ASSERTIONS:
                    old=c.unittest.TestCase.__dict__.get(name);c.require(type(old) is types.FunctionType,'UNSUPPORTED_UNITTEST_API')
                    def factory(old,name):
                        @c.functools.wraps(old)
                        def wrapped(test,*args,**kwargs):
                            depth=getattr(capture.local,'assert_depth',0);capture.local.assert_depth=depth+1
                            try:
                                try:out=old(test,*args,**kwargs)
                                except BaseException:
                                    if depth==0:capture.emit('ASSERTION_RAISED',helper=name)
                                    raise
                                if depth==0:
                                    digests=[]
                                    if name not in ('assertRaises','assertRaisesRegex'):
                                        try:
                                            bound=c.inspect.signature(old,eval_str=False).bind(test,*args,**kwargs)
                                            digests=[capture.operand(v,name,i) for i,(k,v) in enumerate((k,v) for k,v in bound.arguments.items() if k not in ('self','msg'))]
                                        except BaseException:digests=[dict(status='NOT_RECORDED',reason='ASSERTION_ARGUMENT_BINDING_MISSING',sha256=None)]
                                    capture.emit('EXPECTED_EXCEPTION_DECLARED' if name in ('assertRaises','assertRaisesRegex') else 'ASSERTION_RETURNED',helper=name,operands=digests,operands_missing=any(v['status']=='NOT_RECORDED' for v in digests))
                                return out
                            finally:capture.local.assert_depth=depth
                        return wrapped
                    self.patch(c.unittest.TestCase,name,factory(old,name))
                cls=c.unittest.case._AssertRaisesContext;old=cls.__dict__['__exit__']
                @c.functools.wraps(old)
                def context_exit(context,*args):
                    try:out=old(context,*args)
                    except BaseException:capture.emit('EXPECTED_EXCEPTION_EXIT_RAISED');raise
                    capture.emit('EXPECTED_EXCEPTION_EXIT_OBSERVED',suppressed=bool(out),exception_type=c.public_id(args[0].__name__) if args and args[0] else None);return out
                self.patch(cls,'__exit__',context_exit)
                for cls,name in targets:self.wrap_return(cls,name)
            except BaseException:self.restore();raise
            return self
    def stop(self,test,result):
        f=self.active
        if f is None:self.invalid('STOP_WITHOUT_TEST');return
        try:
            c.require(f['test_id']==test.id(),'STOP_TEST_MISMATCH')
            if f['result'] is None:
                if 'FAIL' in f['subtests']:f['result']='FAIL'
                else:f['missing'].append('RESULT_CALLBACK_NOT_RECORDED');self.invalid('RESULT_CALLBACK_NOT_RECORDED')
            for key,(values,start,ptr) in self.record_baselines.items():
                c.require(len(values)>=start,'RECORD_SOURCE_REWOUND')
                for i in range(start,len(values)):
                    v=values[i];metadata={}
                    if type(v) is dict:
                        for k in ('case','run_id','store_id','client_store_id','remote_store_id','role'):
                            if type(v.get(k)) is str:
                                if k.endswith('_id') and k!='case':c.require(re.fullmatch('[0-9a-f-]{36}',v[k]) is not None,'INVALID_RECORD_IDENTITY')
                                metadata[k]=c.public_id(v[k])
                    self.reference();binding=dict(module=key[0],field=key[1],index=i,digest=c.digest_value(v,self.limits),raw_pointer=(ptr+'/'+str(i)) if ptr else None,observed_metadata=metadata)
                    f['record_links'].append(binding);self.record_refs.append((binding,v))
            policy=self.entry['group_policies'][f['group_id']];override=self.policies.get(f['test_id'])
            has_identity=any(self.owner_contexts[k]['identity'] for k in f['owner_context_refs']) or any('run_id' in r['observed_metadata'] for r in f['record_links'])
            if f['test_id'] in self.snapshot_ids:
                f['domain_scope']=dict(status='FIXTURE_DRIVE_SNAPSHOT_RETURN',reason='Typed Drive run/head observation, not Store identity')
                if not f['drive_snapshot_refs'] or f.get('drive_missing'):f['missing'].append('DOMAIN_IDENTITY_NOT_RECORDED')
            elif f['test_id']==self.negative_id:
                f['domain_scope']=dict(status='NEGATIVE_DOMAIN_FIXTURE_CLEANUP',reason='Observed construction declaration, not head')
                if not f['fixture_construction_refs']:f['missing'].append('FIXTURE_CONSTRUCTION_NOT_RECORDED')
            elif override and override['classification']=='NO_STORE_CONTROL':f['domain_scope']=dict(status='NOT_APPLICABLE',reason=override['reason'])
            elif override and override['classification']=='NEGATIVE_DOMAIN':
                f['domain_scope']=dict(status='NEGATIVE_DOMAIN_CONSTRUCTION_REFERENCE',reason=override['reason'])
                if not f['construction_refs']:f['missing'].append('CONSTRUCTION_IDENTITY_NOT_RECORDED')
            else:
                f['domain_scope']=dict(status='OBSERVED_OWNER_CONTEXT' if has_identity else 'DOMAIN_REFERENCES_REQUIRED' if policy['domain_required'] else 'NOT_APPLICABLE',reason=policy['no_store_reason'])
                if policy['domain_required'] and not has_identity:f['missing'].append('DOMAIN_IDENTITY_NOT_RECORDED')
            if self.frame_summary['operands_missing']:f['missing'].append('OPERAND_NOT_RECORDED')
            if self.frame_summary['returns_missing']:f['missing'].append('RETURN_DIGEST_NOT_RECORDED')
            if any(r['digest']['status']=='NOT_RECORDED' for r in f['record_links']):f['missing'].append('RECORD_DIGEST_NOT_RECORDED')
            f['source_binding']=self.entry.get('method_bindings',{}).get(f['test_id'],dict(status='NOT_RECORDED'))
            if f['source_binding']['status']=='NOT_RECORDED':f['missing'].append('METHOD_BINDING_MISSING')
            self.reference(len(f['owner_context_refs'])+1);f['ended_ns']=c.time.monotonic_ns();self.emit('TEST_END');f['event_end']=len(self.events)
        except BaseException as ex:self.invalid(ex.code if isinstance(ex,c.CaptureFault) else 'STOP_OBSERVER_ERROR')
        finally:self.active=None
        if self.errors:result.stop()
    def finish(self,raw=None):
        if self.active:self.invalid('UNFINISHED_TEST')
        ids=[f['test_id'] for f in self.frames]
        if len(ids)!=len(set(ids)) or set(ids)!=set(self.entry['expected_test_ids']):self.invalid('INCOMPLETE_TEST_SET')
        for b,v in self.record_refs:
            if c.digest_value(v,self.limits)!=b['digest']:self.invalid('RECORD_MUTATED_AFTER_TEST')
            if raw is not None and b['raw_pointer']:
                try:c.require(c.digest_value(c.pointer(raw,b['raw_pointer']),self.limits)==b['digest'],'INVALID_RECORD_BINDING')
                except c.CaptureFault as ex:self.invalid(ex.code)
        if self.patches:self.invalid('OBSERVERS_NOT_RESTORED')
        try:self.projector.check()
        except c.CaptureFault as ex:self.invalid(ex.code)
        self.projector.erase()
        try:self.events.close();self.reference(len(self.events.manifest))
        except BaseException as ex:self.invalid(ex.code if isinstance(ex,c.CaptureFault) else 'PAGE_FINALIZATION_ERROR')
        for f in self.frames:f['capture_completeness']='INCOMPLETE' if f['missing'] else 'CAPTURED_FIELDS_PENDING_REVIEW'
        out=dict(schema='d5.typed-sidecar.v1',capture_run_id=self.run_id,scope=self.entry['id'],status='INVALID_CAPTURE' if self.errors else 'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW',frames=self.frames,pages=self.events.manifest,event_count=len(self.events),pages_bytes=self.events.total_bytes,peak_page_buffer_bytes=self.events.peak_buffer_bytes,owner_contexts=self.owner_contexts,construction_declarations=self.declarations,drive_identities=self.drive_identities,drive_observations=self.drive_observations,fixture_construction_declarations=self.fixture_declarations,errors=list(self.errors),observers_restored=self.restored,worker_context=c.environment(),raw_functional_status=raw.get('status') if type(raw) is dict else 'NOT_RECORDED',child_context_scope='ONLY_EXISTING_PROTOCOL_RECORDS_NOT_PARENT_INSTRUMENTATION',global_review='OPEN',closure=False,D5_closed=False,semantic_baseline=dict(SUPPORTS_BOUNDED=81,PARTIAL=3),sufficiency='REVIEW_PENDING',new_distinct_functional_tests=0)
        if len(encode(out))>self.limits['index_sidecar_bytes']:return dict(schema=out['schema'],status='INVALID_CAPTURE',errors=['SIDECAR_BUDGET'],closure=False)
        return out


def evidence_reader(root,limits=None):
    lim=dict(LIMITS,**(limits or {}));return c.Reader(root,dict(unique_bytes=lim['evidence_unique_bytes'],read_bytes=lim['evidence_read_bytes']))


def validate_pages(reader,prefix,side,limits=None,profile=None):
    lim=dict(LIMITS,**(limits or {}));pages=side.get('pages');c.require(type(pages) is list and len(pages)<=lim['pages'],'INVALID_PAGE_MANIFEST')
    c.require({n for n in reader.listing(prefix) if n.startswith('event-')}=={p.get('name') for p in pages},'PAGE_SET_MISMATCH')
    frames=side.get('frames',[]);frame_map={f['test_frame_id']:f for f in frames};c.require(len(frame_map)==len(frames),'DUPLICATE_FRAME')
    profile=profile or {};snap_ids={r['test_id'] for r in profile.get('snapshot_scopes',[])};negative_id=profile.get('negative_DI28',{}).get('criterion',{}).get('test_id');operand_rows={r['test_id']:r for r in profile.get('operand_scopes',[])};drive={k:[] for k in frame_map};fixture={k:[] for k in frame_map};seen_drive=set();seen_fixture=set()
    constructions={k:[] for k in frame_map}
    counts={k:0 for k in frame_map};kinds={k:dict(start=0,end=0,result=[],failed_subtest=False) for k in frame_map};seq=0;total=0;active=None
    for ordinal,p in enumerate(pages,1):
        name=f'event-{ordinal:04}.json';c.require(type(p) is dict and set(p)=={'name','sha256','bytes','page_index','first_sequence','last_sequence','event_count'} and p['name']==name,'INVALID_PAGE_MANIFEST')
        c.require(all(type(p[k]) is int for k in ('bytes','page_index','first_sequence','last_sequence','event_count')) and type(p['sha256']) is str and re.fullmatch('[0-9a-f]{64}',p['sha256']) is not None,'INVALID_PAGE_MANIFEST')
        b=reader.read(prefix+'/'+name);c.require(len(b)<=lim['page_bytes'] and len(b)==p['bytes'] and c.sha(b)==p['sha256'],'INVALID_PACKET_BINDING')
        total+=len(b);c.require(total<=lim['event_pages_total_bytes'],'PAGES_TOTAL_BUDGET');page=c.strict_json(b)
        c.require(set(page)=={'schema','capture_run_id','page_index','first_sequence','last_sequence','event_count','events'} and page['schema']==PAGE_SCHEMA and page['capture_run_id']==side['capture_run_id'],'INVALID_PAGE_HEADER')
        events=page['events'];c.require(type(events) is list and bool(events),'EMPTY_PAGE')
        header=dict(page_index=ordinal,first_sequence=seq,last_sequence=seq+len(events)-1,event_count=len(events))
        c.require(all(type(page[k]) is int and page[k]==p[k]==v for k,v in header.items()),'INVALID_PAGE_HEADER')
        for e in events:
            c.require(type(e) is dict and len(encode(e))<=lim['event_bytes'] and type(e.get('sequence')) is int and e['sequence']==seq,'INVALID_EVENT_SEQUENCE');c.require(seq<lim['events_campaign'],'EVENT_CAMPAIGN_BUDGET')
            ref=e.get('test_frame_id');kind=e.get('event')
            if ref is None:c.require(active is None and kind not in ('TEST_START','TEST_END','TEST_RESULT'),'EVENT_WITHOUT_FRAME')
            else:
                c.require(ref in frame_map,'UNKNOWN_FRAME');f=frame_map[ref]
                c.require(type(f.get('event_start')) is int and type(f.get('event_end')) is int and f['event_start']<=seq<f['event_end'],'INVALID_FRAME_RANGE')
                counts[ref]+=1;c.require(counts[ref]<=lim['events_test'],'EVENT_TEST_BUDGET')
                if e.get('operands_missing'):c.require('OPERAND_NOT_RECORDED' in f['missing'],'MISSING_METADATA_NOT_PROPAGATED')
                if e.get('result_digest',{}).get('status')=='NOT_RECORDED':c.require('RETURN_DIGEST_NOT_RECORDED' in f['missing'],'MISSING_METADATA_NOT_PROPAGATED')
                if kind=='TEST_START':c.require(active is None and seq==f['event_start'],'INVALID_LIFECYCLE');active=ref;kinds[ref]['start']+=1
                else:c.require(active==ref,'INVALID_LIFECYCLE')
                if kind=='TEST_END':c.require(seq==f['event_end']-1,'INVALID_LIFECYCLE');active=None;kinds[ref]['end']+=1
                if kind=='CONSTRUCTION_OBSERVED':
                    key=e.get('object_ref');decl=side.get('construction_declarations',{}).get(key)
                    c.require(type(decl) is dict and decl.get('authority')==DECLARATION and decl.get('process_scope')=='PARENT_ONLY' and all(e.get(k)==v for k,v in decl.items()),'INVALID_CONSTRUCTION_BINDING')
                    if key not in constructions[ref]:constructions[ref].append(key)
                if e.get('drive_snapshot_ref') is not None:
                    key=e['drive_snapshot_ref'];v=side.get('drive_observations',{}).get(key);c.require(f['test_id'] in snap_ids and kind=='CALL_RETURN' and e.get('method')=='snapshot' and key not in seen_drive and type(v) is dict,'INVALID_DRIVE_BINDING')
                    c.require(set(v)=={'object_ref','run_id','version','head_sha256','authority','process_scope'} and v['object_ref']==e.get('owner_ref') and v['object_ref'] in side['owner_contexts'] and v['authority']==DRIVE_OBS and v['process_scope']=='PARENT_ONLY' and uuid_value(v['run_id']) and type(v['version']) is int and 0<=v['version']<=1023 and type(v['head_sha256']) is str and re.fullmatch('[0-9a-f]{64}',v['head_sha256']) is not None,'INVALID_DRIVE_BINDING')
                    c.require(side.get('drive_identities',{}).get(v['object_ref'])==dict(kind='FIXTURE_DRIVE_RUN',run_id=v['run_id']),'INVALID_DRIVE_BINDING');seen_drive.add(key);drive[ref].append(key)
                if kind=='FIXTURE_CONSTRUCTION_OBSERVED':
                    key=e.get('object_ref');v=side.get('fixture_construction_declarations',{}).get(key);c.require(f['test_id']==negative_id and key in side['owner_contexts'] and type(v) is dict and set(v)=={'run_id','authority','process_scope'} and uuid_value(v['run_id']) and v['authority']==FIXTURE_DECL and v['process_scope']=='PARENT_ONLY' and all(e.get(k)==x for k,x in v.items()),'INVALID_FIXTURE_BINDING')
                    seen_fixture.add(key)
                    if key not in fixture[ref]:fixture[ref].append(key)
                for slot,value in enumerate(e.get('operands',[])):
                    if type(value) is dict and value.get('status')=='OBSERVED_TYPED_PROJECTION':
                        row=operand_rows.get(f['test_id']);c.require(row is not None and row['helper']==e.get('helper'),'INVALID_TYPED_SCOPE');typed_witness(value,row['operand_roles'].get(str(slot),[]),side['capture_run_id'])
                if kind=='TEST_RESULT':
                    if e.get('outcome')!='SUBTEST':kinds[ref]['result'].append(e.get('outcome'))
                    else:kinds[ref]['failed_subtest']|=e.get('subtest_failed') is True
            seq+=1
    c.require(active is None and type(side.get('event_count')) is int and type(side.get('pages_bytes')) is int and seq==side['event_count'] and total==side['pages_bytes'],'INCOMPLETE_EVENT_STREAM')
    c.require(seen_drive==set(side.get('drive_observations',{})) and seen_fixture==set(side.get('fixture_construction_declarations',{})),'ORPHAN_TYPED_REFERENCE')
    c.require(set(side.get('drive_identities',{}))=={v['object_ref'] for v in side.get('drive_observations',{}).values()},'ORPHAN_TYPED_REFERENCE')
    for ref,f in frame_map.items():
        c.require(drive[ref]==f.get('drive_snapshot_refs',[]) and fixture[ref]==f.get('fixture_construction_refs',[]),'INVALID_TYPED_FRAME_BINDING')
        if f['test_id'] in snap_ids and not f.get('missing'):c.require(bool(drive[ref]) and f['domain_scope']['status']=='FIXTURE_DRIVE_SNAPSHOT_RETURN','INVALID_TYPED_FRAME_BINDING')
        if f['test_id']==negative_id and not f.get('missing'):c.require(bool(fixture[ref]) and f['domain_scope']['status']=='NEGATIVE_DOMAIN_FIXTURE_CLEANUP','INVALID_TYPED_FRAME_BINDING')
        c.require(constructions[ref]==f.get('construction_refs',[]),'INVALID_CONSTRUCTION_BINDING')
        k=kinds[ref];c.require(counts[ref]==f['event_count'] and k['start']==k['end']==1 and (k['result']==[f['result']] or (not k['result'] and k['failed_subtest'] and f['result']=='FAIL')),'INVALID_LIFECYCLE')
    return dict(pages=len(pages),events=seq,bytes=total,status='PAGE_BINDINGS_VERIFIED')


def package_names(reader,prefix,side):
    expected={'OWNER','runner-raw.json','sidecar.json','context.json'}|{p['name'] for p in side.get('pages',[])}
    c.require(set(reader.listing(prefix))==expected,'PACKAGE_SET_MISMATCH');return expected


def package_size(sizes,limits=None):
    lim=dict(LIMITS,**(limits or {}));caps={'runner-raw.json':lim['raw_bytes'],'sidecar.json':lim['index_sidecar_bytes'],'context.json':lim['context_bytes'],'launch.json':lim['launch_bytes'],'OWNER':4096}
    c.require(len(sizes)<=37 and all(name in caps or re.fullmatch(r'event-00(?:0[1-9]|[12][0-9]|3[0-2])\.json',name) for name in sizes),'PACKAGE_SET_MISMATCH')
    for name,n in sizes.items():c.require(type(n) is int and 0<=n<=caps.get(name,lim['page_bytes']),'PACKAGE_FILE_BUDGET')
    c.require(sum(sizes.values())<=lim['package_bytes'],'PACKAGE_BUDGET');return sum(sizes.values())


def invocation(args=None):
    out=c.invocation('P01');out['command']=['python3','-B','-m','testing.prospective_capture_typed.worker','P01'];out['worker_arguments_observed']=args;return out


def verify_ready(message,lease,pid,rawfd,sidefd,dirfd):
    c.require(set(message)==READY_KEYS,'INVALID_WORKER_IDENTITY');st=os.fstat(dirfd)
    c.require((message['directory_device'],message['directory_inode'])==(st.st_dev,st.st_ino),'INVALID_DIRECTORY_CHANNEL')
    c.verify_ready({k:v for k,v in message.items() if not k.startswith('directory_')},'P01',lease,pid,rawfd,sidefd)


def plan(root=ROOT):
    reg=read_registry(root);return dict(schema='d5.typed-capture-plan.v1',phase='I76_COMPONENTS_ONLY',scope='P01',expected_tests=321,status='NOT_RUN_I77_AUTHORIZATION_REQUIRED',functional_execution_authorized=False,semantic_baseline=reg['semantic_baseline'],closure=False,global_review='OPEN',publication_authorized=False)


def verify_release(message,lease):c.require(message==dict(event='RELEASE',lease=lease),'INVALID_WORKER_RELEASE')


def wait_worker(process,seconds=None):
    limit=LIMITS['campaign_seconds'] if seconds is None else min(LIMITS['campaign_seconds'],seconds)
    try:process.wait(timeout=limit);return True
    except c.subprocess.TimeoutExpired:return False


def launch(requested,root=ROOT):
    scope(requested);reg=read_registry(root);approved=authority(root,requested,reg);entry=reg['entry']
    reader=c.Reader(root);fd=reader.directory('docs/validation')
    try:
        # Reserve both fixed paths without touching previous evidence.
        launchfd=os.open(Path(LAUNCH_COPY).name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        try:os.mkdir(Path(DESTINATION).name,0o700,dir_fd=fd)
        except BaseException:os.close(launchfd);raise
    finally:os.close(fd)
    try:owner=c.OwnedRoot(Path(root)/DESTINATION)
    except BaseException:os.close(launchfd);raise
    context=dict(scope='P01',invocation=invocation(),functional_execution='NEW_I77',closure=False,global_review='OPEN',publication_authorized=False)
    rawfd=sidefd=directory=ready_read=ready_write=release_read=release_write=None;process=None
    try:
        before=c.runner_files(root,entry);c.require(before==entry['runner_effective_inputs'],'STALE_INPUTS')
        rawfd=owner.create('runner-raw.json');sidefd=owner.create('sidecar.json');directory=owner.directory();ready_read,ready_write=os.pipe();release_read,release_write=os.pipe()
        cmd=[sys.executable,'-B','-m','testing.prospective_capture_typed.worker','P01',str(sidefd),str(ready_write),str(release_read),str(directory),owner.nonce]
        process=c.subprocess.Popen(cmd,cwd=root,stdin=c.subprocess.DEVNULL,stdout=rawfd,stderr=c.subprocess.DEVNULL,pass_fds=(sidefd,ready_write,release_read,directory),start_new_session=True,env=dict(PATH=os.defpath,LANG='C.UTF-8',LC_ALL='C.UTF-8',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8'))
        os.close(ready_write);ready_write=None;os.close(release_read);release_read=None
        verify_ready(c.receive_line(ready_read,LIMITS['wait_seconds']),owner.nonce,process.pid,rawfd,sidefd,directory)
        c.write_json_fd(release_write,dict(event='RELEASE',lease=owner.nonce),4096);write_all(release_write,b'\n');os.close(release_write);release_write=None
        if not wait_worker(process):context['timeout']=True
        context['cleanup']=c.stop_owned(process,owner,dict(pid=process.pid,pgid=process.pid,lease=owner.nonce));context['worker_exit_code']=process.returncode
        context['runner_inputs_before']=before;context['runner_inputs_after']=c.runner_files(root,entry);context['input_comparison']=c.compare_inputs(before,context['runner_inputs_after'])
        c.require(authority(root,'P01',reg)==approved,'STALE_AUTHORITY');context['capture_inputs_before']=approved['capture_inputs'];context['capture_inputs_after']=approved['capture_inputs']
        packet=evidence_reader(root);rawb=packet.read(DESTINATION+'/runner-raw.json');sideb=packet.read(DESTINATION+'/sidecar.json');side=c.strict_json(sideb);raw=c.strict_json(rawb)
        c.require(len(rawb)<=LIMITS['raw_bytes'] and len(sideb)<=LIMITS['index_sidecar_bytes'] and c.sha(rawb)==side.get('raw_sha256') and len(rawb)==side.get('raw_bytes'),'INVALID_PACKET_BINDING')
        c.require(side.get('runner_inputs_before')==before and side.get('runner_inputs_after')==context['runner_inputs_after'],'INVALID_PACKET_BINDING')
        c.require(side.get('capture_inputs_before')==side.get('capture_inputs_after')==approved['capture_inputs'],'INVALID_PACKET_BINDING')
        c.require(side.get('schema')=='d5.typed-sidecar.v1' and side.get('observers_restored') is True and side.get('entrypoint_exit_code')==(0 if raw.get('status')=='PASS' else 1),'INVALID_PACKET_BINDING')
        context['artifacts']={'runner-raw.json':c.sha(rawb),'sidecar.json':c.sha(sideb)}
        # Invalid/partial pages are preserved, never accepted as a complete trace.
        if side.get('status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW':context['page_validation']=validate_pages(packet,DESTINATION,side,profile=reg);c.aggregate_capture(side,c.scenario_metadata(raw,entry),raw,entry)
        else:context['page_validation']=dict(status='NOT_ACCEPTED_INCOMPLETE_CAPTURE')
        packet.finish();context['capture_status']='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' if process.returncode==0 and side.get('status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' and context['cleanup']['status']=='OWN_GROUP_GONE' and context['input_comparison']['status']=='MATCH' else 'BLOCKED'
    except BaseException as ex:
        context['capture_status']='INVALID_CAPTURE';context['error_code']=ex.code if isinstance(ex,c.CaptureFault) else 'SANITIZED_LAUNCH_ERROR'
        if process is not None:
            try:context['cleanup']=c.stop_owned(process,owner,dict(pid=process.pid,pgid=process.pid,lease=owner.nonce))
            except BaseException:context['cleanup']=dict(status='BLOCKED_OWNERSHIP_UNCONFIRMED')
    finally:
        for f in (rawfd,sidefd,directory,ready_read,ready_write,release_read,release_write):
            if f is not None:os.close(f)
        try:
            owner.verify();b=encode(context);c.require(len(b)<=min(LIMITS['context_bytes'],LIMITS['launch_bytes']),'CONTEXT_BUDGET')
            packet=packet if 'packet' in locals() else evidence_reader(root);names=packet.listing(DESTINATION);sizes={}
            for name in names:
                c.require(name in {'OWNER','runner-raw.json','sidecar.json'} or re.fullmatch(r'event-00(?:0[1-9]|[12][0-9]|3[0-2])\.json',name),'PACKAGE_SET_MISMATCH')
                key=DESTINATION+'/'+name
                if key not in packet.files:packet.read(key)
                sizes[name]=packet.files[key][0][2]
            sizes.update({'context.json':len(b),'launch.json':len(b)});package_size(sizes)
            if 'side' in locals():c.require(set(names)=={'OWNER','runner-raw.json','sidecar.json'}|{p['name'] for p in side.get('pages',[])},'PACKAGE_SET_MISMATCH')
        except BaseException as ex:
            context['capture_status']='INVALID_CAPTURE';context['error_code']=ex.code if isinstance(ex,c.CaptureFault) else 'PACKAGE_VALIDATION_ERROR';b=encode(context)
            if len(b)>LIMITS['context_bytes']:context=dict(scope='P01',capture_status='INVALID_CAPTURE',error_code='CONTEXT_BUDGET',closure=False);b=encode(context)
        try:
            fd=owner.create('context.json')
            try:write_all(fd,b)
            finally:os.close(fd)
            write_all(launchfd,b)
        finally:os.close(launchfd)
    return context


def main(argv=None):
    args=sys.argv[1:] if argv is None else argv
    try:
        if not args:out=plan();code=0
        else:c.require(len(args)==2 and args[0]=='--capture','INVALID_ARGUMENTS');out=launch(args[1]);code=0 if out.get('capture_status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' else 1
    except (c.CaptureFault,OSError,ValueError,KeyError,TypeError) as ex:out=dict(status='BLOCKED',code=ex.code if isinstance(ex,c.CaptureFault) else 'SANITIZED_COMPONENT_ERROR',closure=False,publication_authorized=False);code=2
    print(json.dumps(out,ensure_ascii=False));return code


if __name__=='__main__':raise SystemExit(main())
