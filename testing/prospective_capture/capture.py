# SPDX-License-Identifier: GPL-3.0-only
"""Bounded prospective capture components. Importing this module runs no campaign."""
import ast
import contextlib
import datetime
import functools
import hashlib
import inspect
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import re
import selectors
import signal
import stat
import subprocess
import sys
import threading
import time
import types
import unittest
import uuid
import weakref

ROOT=Path(__file__).resolve().parents[2]
REGISTRY='docs/validation/D5-PROSPECTIVE-CAPTURE-REGISTRY.json'
AUTHORITY='docs/validation/D5-I71-capture-authorization.json'
LIMITS=dict(raw_bytes=12*1024*1024,sidecar_bytes=12*1024*1024,event_bytes=4096,events_test=2048,events_campaign=16384,operand_bytes=16*1024*1024,frames=4096,refs=16384,depth=32,string=4096,paths=4096,file_bytes=16*1024*1024,unique_bytes=128*1024*1024,read_bytes=256*1024*1024,wait_seconds=20,campaign_seconds=900)
IDS={f'P{i:02}' for i in range(1,11)}
PRIVATE={'.git','.aws','.ssh','.codex','.agents','dev','run_data','private','secrets','credentials','work','attachments','data','artifacts','exports','backups','tmp','temp','internal','__pycache__','.venv','node_modules','pgdata'}
ASSERTIONS=('assertEqual','assertNotEqual','assertTrue','assertFalse','assertIn','assertNotIn','assertIsNone','assertIsNotNone','assertIsInstance','assertGreater','assertLess','assertRaises','assertRaisesRegex')
CALLBACKS=('startTest','stopTest','addSuccess','addFailure','addError','addSkip','addExpectedFailure','addUnexpectedSuccess','addSubTest')


class CaptureFault(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)


def require(ok,code):
    if not ok:raise CaptureFault(code)


def sha(data):return hashlib.sha256(data).hexdigest()


def public_id(value):
    require(type(value) is str and re.fullmatch(r'[A-Za-z0-9_.:+-]{1,512}',value) is not None,'INVALID_PUBLIC_ID');return value


def public_path(value):
    require(type(value) is str and re.fullmatch(r'[A-Za-z0-9_./-]{1,512}',value) is not None,'INVALID_PUBLIC_PATH')
    p=PurePosixPath(value)
    require(not p.is_absolute() and str(p)==value and all(x not in PRIVATE and x not in ('.','..') and not x.startswith('.env') for x in p.parts),'INVALID_PUBLIC_PATH')
    require(not p.suffix in ('.key','.pem','.sqlite','.log'),'INVALID_PUBLIC_PATH');return value


def strict_json(data,limits=None):
    lim=dict(LIMITS,**(limits or {}));require(len(data)<=lim['file_bytes'],'FILE_BUDGET')
    depth=0;quoted=False;escaped=False
    try:
        for c in data.decode('utf8'):
            if quoted:
                if escaped:escaped=False
                elif c=='\\':escaped=True
                elif c=='"':quoted=False
            elif c=='"':quoted=True
            elif c in '[{':depth+=1;require(depth<=lim['depth'],'JSON_DEPTH')
            elif c in ']}':depth-=1
        def pairs(items):
            d={}
            for k,v in items:require(k not in d,'DUPLICATE_KEY');d[k]=v
            return d
        def reject(_):raise CaptureFault('NONFINITE_JSON')
        out=json.loads(data,object_pairs_hook=pairs,parse_constant=reject)
        def check(x):
            if type(x) is str:require(len(x)<=lim['string'],'STRING_BUDGET')
            elif type(x) is list:
                for v in x:check(v)
            elif type(x) is dict:
                for k,v in x.items():check(k);check(v)
            elif type(x) is float:require(math.isfinite(x),'NONFINITE_JSON')
        check(out);return out
    except (UnicodeError,ValueError,RecursionError):raise CaptureFault('INVALID_JSON') from None


def pointer(doc,ref):
    require(type(ref) is str and (ref=='' or ref.startswith('/')),'INVALID_POINTER')
    for key in ref[1:].split('/') if ref else []:
        require(not re.search(r'~(?![01])',key),'INVALID_POINTER');key=key.replace('~1','/').replace('~0','~')
        if type(doc) is list:require(re.fullmatch('0|[1-9][0-9]*',key) is not None and int(key)<len(doc),'INVALID_POINTER');doc=doc[int(key)]
        else:require(type(doc) is dict and key in doc,'INVALID_POINTER');doc=doc[key]
    return doc


def digest_value(value,limits=None):
    """Exact builtins only. Never repr(), custom iteration or properties."""
    lim=dict(LIMITS,**(limits or {}));h=hashlib.sha256();used=0;active=set()
    def add(b):
        nonlocal used
        used+=len(b);require(used<=lim['operand_bytes'],'OPERAND_BUDGET');h.update(b)
    def charge(size):
        nonlocal used
        used+=size;require(used<=lim['operand_bytes'],'OPERAND_BUDGET')
    def visit(x,depth):
        require(depth<=lim['depth'],'OPERAND_DEPTH');kind=type(x)
        if kind is bytes:
            add(b'bytes:');add(str(len(x)).encode()+b':')
            for i in range(0,len(x),65536):add(x[i:i+65536])
        elif kind in (str,int,float,bool,type(None)):
            if kind is float:require(math.isfinite(x),'NONFINITE_OPERAND')
            add(kind.__name__.encode()+b':')
            for chunk in json.JSONEncoder(ensure_ascii=True,allow_nan=False).iterencode(x):add(chunk.encode())
        elif kind in (list,tuple,dict,set,frozenset):
            require(id(x) not in active,'CYCLIC_OPERAND');active.add(id(x));add(kind.__name__.encode()+b'[')
            try:
                if kind is dict:
                    require(all(type(k) is str for k in x),'UNSUPPORTED_OPERAND')
                    for k in sorted(x):visit(k,depth+1);visit(x[k],depth+1)
                elif kind in (set,frozenset):
                    parts=[]
                    for v in x:
                        p=digest_value(v,dict(lim,operand_bytes=max(0,lim['operand_bytes']-used)));require(p['status']=='OBSERVED_DIGEST','UNSUPPORTED_OPERAND');used_before=p['bytes'];require(used+used_before<=lim['operand_bytes'],'OPERAND_BUDGET');add(b'element:');parts.append(p)
                        # Charge the bytes hashed in the child, in addition to its digest representation.
                        charge(used_before)
                    for p in sorted(parts,key=lambda v:v['sha256']):add(p['sha256'].encode());add(str(p['bytes']).encode())
                else:
                    for v in x:visit(v,depth+1)
            finally:active.remove(id(x))
            add(b']')
        else:raise CaptureFault('UNSUPPORTED_OPERAND')
    try:visit(value,0);return dict(status='OBSERVED_DIGEST',sha256=h.hexdigest(),bytes=used)
    except (CaptureFault,RecursionError,ValueError,RuntimeError) as ex:return dict(status='NOT_RECORDED',reason=ex.code if isinstance(ex,CaptureFault) else 'UNSUPPORTED_OPERAND',sha256=None)


def fingerprint(st):return (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)


class Reader:
    def __init__(self,root,limits=None):self.root=Path(root);self.limits=dict(LIMITS,**(limits or {}));self.files={};self.dirs={};self.unique=0;self.total=0
    def directory(self,name=''):
        if name:public_path(name)
        fd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            for part in PurePosixPath(name).parts if name else ():
                nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=nxt
            return fd
        except BaseException:os.close(fd);raise
    def read(self,name):
        public_path(name);parent,leaf=name.rsplit('/',1) if '/' in name else ('',name);fd=self.directory(parent)
        try:
            st=os.stat(leaf,dir_fd=fd,follow_symlinks=False);require(stat.S_ISREG(st.st_mode),'NONREGULAR_FILE');require(st.st_size<=self.limits['file_bytes'],'FILE_BUDGET')
            h=os.open(leaf,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
            try:
                require(fingerprint(st)==fingerprint(os.fstat(h)),'UNSTABLE_SNAPSHOT');chunks=[];digest=hashlib.sha256();left=st.st_size
                self.total+=st.st_size;require(self.total<=self.limits['read_bytes'],'READ_BUDGET')
                if name not in self.files:self.unique+=st.st_size;require(self.unique<=self.limits['unique_bytes'],'UNIQUE_BUDGET')
                require(len(self.files)<self.limits['paths'] or name in self.files,'PATH_BUDGET')
                while left:
                    b=os.read(h,min(left,65536));require(bool(b),'UNSTABLE_SNAPSHOT');chunks.append(b);digest.update(b);left-=len(b)
                require(not os.read(h,1) and fingerprint(st)==fingerprint(os.fstat(h)),'UNSTABLE_SNAPSHOT')
                value=(fingerprint(st),digest.hexdigest())
                if name in self.files:require(self.files[name]==value,'UNSTABLE_SNAPSHOT')
                self.files[name]=value;return b''.join(chunks)
            finally:os.close(h)
        finally:os.close(fd)
    def listing(self,name):
        fd=self.directory(name)
        try:
            names=tuple(sorted(os.listdir(fd)));require(len(names)<=self.limits['paths'],'PATH_BUDGET')
            if name in self.dirs:require(self.dirs[name]==names,'UNSTABLE_SNAPSHOT')
            self.dirs[name]=names;return names
        finally:os.close(fd)
    def finish(self):
        for name in tuple(self.files):self.read(name)
        for name in tuple(self.dirs):self.listing(name)


def read_registry(root=ROOT):
    reader=Reader(root);reg=strict_json(reader.read(REGISTRY));require(set(reg)=={'schema','contract_path','contract_sha256','entries','functional_execution_authorized','semantic_baseline','observer_specs'},'INVALID_REGISTRY')
    require(reg['schema']=='d5.prospective-capture-registry.v1' and reg['functional_execution_authorized'] is False,'INVALID_REGISTRY')
    contract=reader.read(public_path(reg['contract_path']));require(sha(contract)==reg['contract_sha256'],'HASH_MISMATCH');plan=strict_json(contract)
    require(len(reg['entries'])==10 and [e['id'] for e in reg['entries']]==[f'P{i:02}' for i in range(1,11)],'INVALID_REGISTRY')
    for e,old in zip(reg['entries'],plan['capture_catalog']):
        for key,value in old.items():require(e.get(key)==value,'INVALID_REGISTRY')
        require(len(e['expected_test_ids'])==len(set(e['expected_test_ids']))==e['expected_tests'],'INVALID_MANIFEST')
        require(sha(json.dumps(sorted(e['expected_test_ids']),separators=(',',':')).encode())==e['expected_passed_ids_sha256'],'INVALID_MANIFEST')
    reader.finish();return reg


def authority(root,scope,reg):
    require(scope in IDS,'INVALID_SCOPE');r=Reader(root)
    try:a=strict_json(r.read(AUTHORITY))
    except FileNotFoundError:raise CaptureFault('I71_AUTHORIZATION_REQUIRED') from None
    require(set(a)=={'schema','scopes','registry_sha256','capture_inputs','phase'} and a['schema']=='d5.capture-authority.v1' and a['phase']=='I71_EXPLICITLY_APPROVED','I71_AUTHORIZATION_REQUIRED')
    require(scope in a['scopes'] and set(a['scopes'])<=IDS,'I71_AUTHORIZATION_REQUIRED')
    require(a['registry_sha256']==sha(r.read(REGISTRY)),'STALE_AUTHORITY')
    require(type(a['capture_inputs']) is dict and a['capture_inputs'],'STALE_AUTHORITY')
    required={'testing/prospective_capture/capture.py','testing/prospective_capture/worker.py','testing/prospective_capture/README.md','testing/prospective_capture/test_prospective_capture.py','testing/prospective_capture/run_capture_lab.py','docs/validation/D5-I70-tests-raw.json','docs/validation/D5-I69-design-review.json','docs/validation/D5-I70-results.json','docs/validation/D5-I70-integrity.json'}
    require(required<=set(a['capture_inputs']),'STALE_AUTHORITY')
    for p,h in a['capture_inputs'].items():require(sha(r.read(public_path(p)))==h,'STALE_AUTHORITY')
    r.finish();return a


def environment():return dict(python=platform.python_version(),implementation=platform.python_implementation(),build=list(platform.python_build()),platform=platform.system(),release=platform.release(),machine=platform.machine(),optimize=sys.flags.optimize,debug=__debug__)


def invocation(scope,worker_arguments=None):
    require(scope in IDS,'INVALID_SCOPE')
    if worker_arguments is not None:
        require(len(worker_arguments)==5 and worker_arguments[0]==scope and all(type(v) is str and len(v)<=128 for v in worker_arguments),'INVALID_WORKER_ARGUMENTS')
    return dict(command=['python3','-B','-m','testing.prospective_capture.worker',scope],command_role='PUBLIC_LOGICAL_VECTOR_PREFIX_NORMALIZED',worker_arguments_observed=worker_arguments,entrypoint_role='FIXED_MODULE_MAIN_NOT_SEPARATE_EXECVE',interpreter=dict(basename=Path(sys.executable).name,path_sha256=sha(os.fsencode(sys.executable)),normalization='PRIVATE_PREFIX_NOT_EMITTED'),worker_environment=environment(),runner_context_role='RUNNER_DECLARATION_NOT_WORKER_ARGV')


class Recorder:
    def __init__(self,entry,limits=None):
        self.entry=entry;self.limits=dict(LIMITS,**(limits or {}));self.run_id=str(uuid.uuid4());self.frames=[];self.events=[];self.errors=[];self.active=None;self.local=threading.local();self.patches=[];self.owners={};self.owner_contexts={};self.record_baselines={};self.record_refs=[];self.restored=False;self.result=None
    def invalid(self,code):
        code=code if type(code) is str and re.fullmatch('[A-Z0-9_]{1,80}',code) else 'OBSERVER_ERROR'
        if code not in self.errors and len(self.errors)<32:self.errors.append(code)
    def emit(self,kind,**data):
        try:
            require(len(self.events)<self.limits['events_campaign'],'EVENT_CAMPAIGN_BUDGET')
            frame=self.active
            if frame:require(frame['event_count']<self.limits['events_test'],'EVENT_TEST_BUDGET')
            item=dict(event=public_id(kind),sequence=len(self.events),test_frame_id=frame['test_frame_id'] if frame else None,**data)
            require(len(json.dumps(item,separators=(',',':')).encode())<=self.limits['event_bytes'],'EVENT_SIZE_BUDGET')
            self.events.append(item)
            if frame:frame['event_count']+=1
        except (CaptureFault,ValueError,TypeError,RecursionError) as ex:self.invalid(ex.code if isinstance(ex,CaptureFault) else 'OBSERVER_ERROR')
    def source_positions(self):
        out={}
        for s in self.entry.get('record_sources',[]):
            module=sys.modules.get(s['module']);values=module.__dict__.get(s['field']) if module else None
            if type(values) is list:out[(s['module'],s['field'])]=(values,len(values),s['raw_pointer'])
        return out
    def start(self,test):
        try:
            require(self.active is None,'NESTED_TEST_LIFECYCLE');tid=public_id(test.id());require(tid in self.entry['expected_test_ids'],'UNEXPECTED_TEST_ID');require(len(self.frames)<self.limits['frames'],'FRAME_BUDGET')
            group=next((g for g in self.entry['expected_groups'] if (tid.split('.')[-3] if len(tid.split('.'))>=3 else '')==g),None)
            if group is None:
                require(len(self.entry['expected_groups'])==1,'INVALID_GROUP_BINDING');group=next(iter(self.entry['expected_groups']))
            frame=dict(test_id=tid,group_id=group,test_frame_id=str(uuid.uuid4()),capture_run_id=self.run_id,owner_context_refs=[],event_start=len(self.events),event_count=0,result=None,subtests=[],record_links=[],missing=[],started_ns=time.monotonic_ns())
            self.frames.append(frame);self.active=frame;self.record_baselines=self.source_positions();self.emit('TEST_START')
        except (CaptureFault,ValueError,TypeError) as ex:self.invalid(ex.code if isinstance(ex,CaptureFault) else 'LIFECYCLE_ERROR')
    def safe(self,method,*args):
        try:return method(*args)
        except BaseException:self.invalid('OBSERVER_ERROR');return None
    def outcome(self,name,subtest=False,failed=False):
        if self.active is None:self.invalid('RESULT_WITHOUT_TEST');return
        if subtest:self.active['subtests'].append('FAIL' if failed else 'PASS')
        else:
            if self.active['result'] is not None and self.active['result']!=name:self.invalid('MULTIPLE_TEST_RESULTS')
            self.active['result']=name
        self.emit('TEST_RESULT',outcome=name)
    def stop(self,test,result):
        frame=self.active
        if frame is None:self.invalid('STOP_WITHOUT_TEST');return
        if frame['test_id']!=test.id():self.invalid('STOP_TEST_MISMATCH')
        if frame['result'] is None:
            if any(x=='FAIL' for x in frame['subtests']):frame['result']='FAIL'
            else:frame['missing'].append('RESULT_CALLBACK_NOT_RECORDED');self.invalid('RESULT_CALLBACK_NOT_RECORDED')
        for key,(values,start,rawptr) in self.record_baselines.items():
            if len(values)<start:self.invalid('RECORD_SOURCE_REWOUND');continue
            for i in range(start,len(values)):
                value=values[i];metadata={}
                if type(value) is dict:
                    for k in ('case','run_id','store_id','client_store_id','remote_store_id','role'):
                        if type(value.get(k)) is str:
                            try:
                                if k.endswith('_id') and k!='case':require(re.fullmatch('[0-9a-f-]{36}',value[k]) is not None,'INVALID_RECORD_IDENTITY')
                                metadata[k]=public_id(value[k])
                            except CaptureFault:self.invalid('INVALID_RECORD_METADATA')
                binding=dict(module=key[0],field=key[1],index=i,digest=digest_value(value,self.limits),raw_pointer=(rawptr+'/'+str(i)) if rawptr else None,observed_metadata=metadata)
                frame['record_links'].append(binding)
                self.record_refs.append((binding,values[i]))
        policy=self.entry['group_policies'][frame['group_id']]
        frame['domain_scope']=dict(status='DOMAIN_REFERENCES_REQUIRED' if policy['domain_required'] else 'NOT_APPLICABLE',reason=policy['no_store_reason'])
        has_identity=any(self.owner_contexts[k]['identity'] for k in frame['owner_context_refs']) or any('run_id' in r['observed_metadata'] for r in frame['record_links'])
        if policy['domain_required'] and not has_identity:frame['missing'].append('DOMAIN_IDENTITY_NOT_RECORDED')
        if has_identity:frame['domain_scope']=dict(status='OBSERVED_OWNER_CONTEXT',reason=None)
        frame_events=self.events[frame['event_start']:]
        if any(e.get('operands_missing') for e in frame_events):frame['missing'].append('OPERAND_NOT_RECORDED')
        if any(e.get('result_digest',{}).get('status')=='NOT_RECORDED' for e in frame_events):frame['missing'].append('RETURN_DIGEST_NOT_RECORDED')
        if any(r['digest']['status']=='NOT_RECORDED' for r in frame['record_links']):frame['missing'].append('RECORD_DIGEST_NOT_RECORDED')
        frame['source_binding']=self.entry.get('method_bindings',{}).get(frame['test_id'],dict(status='NOT_RECORDED',reason='METHOD_BINDING_MISSING'))
        if frame['source_binding']['status']=='NOT_RECORDED':frame['missing'].append('METHOD_BINDING_MISSING')
        frame['ended_ns']=time.monotonic_ns();self.emit('TEST_END');self.active=None
        if self.errors:result.stop()
    def owner(self,obj,out):
        oid=id(obj);old=self.owners.get(oid)
        if not old or old[0]() is not obj:
            try:ref=weakref.ref(obj)
            except TypeError:return None
            key='O'+str(len(self.owner_contexts)+1);self.owners[oid]=(ref,key);self.owner_contexts[key]=dict(scope='OBSERVER_OBJECT_NOT_STORE_ID',identity=None)
        key=self.owners[oid][1]
        if type(out) is dict and type(out.get('head')) is dict:
            head=out['head'];ident={k:head[k] for k in ('run_id','store_id') if type(head.get(k)) is str and re.fullmatch('[0-9a-f-]{36}',head[k])}
            if ident:
                previous=self.owner_contexts[key]['identity']
                if previous and previous!=ident:self.invalid('OWNER_IDENTITY_CHANGED')
                self.owner_contexts[key]['identity']=ident
        if self.active and key not in self.active['owner_context_refs']:self.active['owner_context_refs'].append(key)
        return key
    def wrap_return(self,cls,name):
        require(name in cls.__dict__ and type(cls.__dict__[name]) is types.FunctionType,'UNSUPPORTED_OBSERVER_API');old=cls.__dict__[name];capture=self
        @functools.wraps(old)
        def wrapped(obj,*args,**kwargs):
            try:out=old(obj,*args,**kwargs)
            except BaseException as ex:
                try:capture.emit('CALL_EXCEPTION',method=public_id(name),exception_type=public_id(type(ex).__name__))
                except BaseException:capture.invalid('OBSERVER_ERROR')
                raise
            try:capture.emit('CALL_RETURN',method=public_id(name),owner_ref=capture.owner(obj,out),result_digest=digest_value(out,capture.limits))
            except BaseException:capture.invalid('OBSERVER_ERROR')
            return out
        self.patch(cls,name,wrapped)
    def patch(self,cls,name,replacement):
        old=cls.__dict__.get(name);require(old is not None,'UNSUPPORTED_OBSERVER_API');self.patches.append((cls,name,old,replacement));setattr(cls,name,replacement)
    def install(self,targets=()):
        require(not self.patches,'ALREADY_INSTALLED')
        capture=self
        try:
            for name in CALLBACKS:
                old=unittest.TestResult.__dict__.get(name);require(type(old) is types.FunctionType,'UNSUPPORTED_UNITTEST_API')
                def factory(old,name):
                    @functools.wraps(old)
                    def wrapped(result,test,*args,**kwargs):
                        if name=='startTest':capture.safe(capture.start,test)
                        out=old(result,test,*args,**kwargs)
                        if name=='stopTest':capture.safe(capture.stop,test,result)
                        elif name not in ('startTest',):
                            mapping=dict(addSuccess='PASS',addFailure='FAIL',addError='ERROR',addSkip='SKIP',addExpectedFailure='EXPECTED_FAILURE',addUnexpectedSuccess='UNEXPECTED_SUCCESS',addSubTest='SUBTEST')
                            capture.safe(capture.outcome,mapping[name],name=='addSubTest',name=='addSubTest' and len(args)>1 and args[1] is not None)
                        return out
                    return wrapped
                self.patch(unittest.TestResult,name,factory(old,name))
            for name in ASSERTIONS:
                old=unittest.TestCase.__dict__.get(name);require(type(old) is types.FunctionType,'UNSUPPORTED_UNITTEST_API')
                def factory(old,name):
                    @functools.wraps(old)
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
                                        bound=inspect.signature(old,eval_str=False).bind(test,*args,**kwargs)
                                        digests=[digest_value(v,capture.limits) for k,v in bound.arguments.items() if k not in ('self','msg')]
                                    except BaseException:digests=[dict(status='NOT_RECORDED',reason='ASSERTION_ARGUMENT_BINDING_MISSING',sha256=None)]
                                capture.emit('EXPECTED_EXCEPTION_DECLARED' if name in ('assertRaises','assertRaisesRegex') else 'ASSERTION_RETURNED',helper=name,operands=digests,operands_missing=any(v['status']=='NOT_RECORDED' for v in digests))
                            return out
                        finally:capture.local.assert_depth=depth
                    return wrapped
                self.patch(unittest.TestCase,name,factory(old,name))
            cls=unittest.case._AssertRaisesContext;old=cls.__dict__['__exit__']
            @functools.wraps(old)
            def context_exit(context,*args):
                try:out=old(context,*args)
                except BaseException:capture.emit('EXPECTED_EXCEPTION_EXIT_RAISED');raise
                capture.emit('EXPECTED_EXCEPTION_EXIT_OBSERVED',suppressed=bool(out),exception_type=public_id(args[0].__name__) if args and args[0] else None);return out
            self.patch(cls,'__exit__',context_exit)
            for cls,name in targets:self.wrap_return(cls,name)
        except BaseException:self.restore();raise
        return self
    def restore(self):
        for cls,name,old,replacement in reversed(self.patches):
            if cls.__dict__.get(name) is not replacement:self.invalid('OBSERVER_IDENTITY_CHANGED')
            setattr(cls,name,old)
        self.patches.clear();self.restored=True
    def finish(self,raw=None):
        if self.active:self.invalid('UNFINISHED_TEST')
        observed=[f['test_id'] for f in self.frames]
        if len(observed)!=len(set(observed)) or set(observed)!=set(self.entry['expected_test_ids']):self.invalid('INCOMPLETE_TEST_SET')
        for binding,value in self.record_refs:
            if digest_value(value,self.limits)!=binding['digest']:self.invalid('RECORD_MUTATED_AFTER_TEST')
            if raw is not None and binding['raw_pointer']:
                try:require(digest_value(pointer(raw,binding['raw_pointer']),self.limits)==binding['digest'],'INVALID_RECORD_BINDING')
                except CaptureFault as ex:self.invalid(ex.code)
        if self.patches:self.invalid('OBSERVERS_NOT_RESTORED')
        out=dict(schema='d5.prospective-sidecar.v1',capture_run_id=self.run_id,scope=self.entry['id'],status='INVALID_CAPTURE' if self.errors else 'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW',frames=self.frames,events=self.events,owner_contexts=self.owner_contexts,errors=self.errors,observers_restored=self.restored,worker_context=environment(),raw_functional_status=raw.get('status') if type(raw) is dict else 'NOT_RECORDED',new_distinct_functional_tests=0,global_review='OPEN',closure=False,D5_closed=False,semantic_baseline=dict(SUPPORTS_BOUNDED=81,PARTIAL=3),historical_evidence_modified=False,child_context_scope='ONLY_EXISTING_PROTOCOL_RECORDS_NOT_PARENT_INSTRUMENTATION')
        for f in self.frames:f['capture_completeness']='INCOMPLETE' if f['missing'] else 'CAPTURED_FIELDS_PENDING_REVIEW'
        if len(json.dumps(out,separators=(',',':')).encode())>self.limits['sidecar_bytes']:return dict(schema=out['schema'],status='INVALID_CAPTURE',errors=['SIDECAR_BUDGET'],global_review='OPEN',closure=False,D5_closed=False)
        return out


def scenario_metadata(raw,entry):
    rows=raw.get('scenarios',[]);require(type(rows) is list and len(rows)<=LIMITS['frames'],'SCENARIO_BUDGET')
    counts={}
    out=[];total_refs=0
    for i,row in enumerate(rows):
        require(type(row) is dict and type(row.get('case')) is str,'INVALID_SCENARIO_BINDING');case=public_id(row['case']);counts[case]=counts.get(case,0)+1
        refs=[]
        for j,event in enumerate(row.get('events',[])):
            if type(event) is not dict:raise CaptureFault('INVALID_EVENT_BINDING')
            for key in ('point','operation'):
                if event.get(key) is not None:refs.append(dict(field=key,pointer=f'/scenarios/{i}/events/{j}/{key}',classification='RECORDED_EVENT_LABEL_NOT_CAUSAL_ATTESTATION'))
        total_refs+=len(refs);require(total_refs<=LIMITS['refs'],'REFERENCE_BUDGET')
        if 'run_id' in row:require(type(row['run_id']) is str and re.fullmatch('[0-9a-f-]{36}',row['run_id']) is not None,'INVALID_SCENARIO_IDENTITY')
        required=[k for k in ('run_id','events','oracles','status') if k not in row]
        out.append(dict(case=case,raw_pointer=f'/scenarios/{i}',metadata_refs=refs,missing=required,status='INCOMPLETE' if required else 'CAPTURED_FIELDS_PENDING_REVIEW'))
    require(counts==entry['expected_scenario_multiplicity'] and len(rows)==entry['expected_raw_scenarios'],'SCENARIO_MULTIPLICITY_MISMATCH')
    return out


def aggregate_capture(sidecar,scenarios,raw,entry):
    require(raw.get('status') in {'PASS','FAIL','BLOCKED','NOT_RUN'},'INVALID_FUNCTIONAL_STATUS')
    require(type(raw.get('passed')) is list and len(raw['passed'])==len(set(raw['passed'])) and set(raw['passed'])<=set(entry['expected_test_ids']),'INVALID_RESULT_BINDING')
    require(type(raw.get('tests_run')) is int and raw['tests_run']==entry['expected_tests'],'INVALID_TEST_COUNT')
    frames=sidecar.get('frames',[]);require(len(frames)==entry['expected_tests'],'INCOMPLETE_TEST_SET')
    seen=[f['test_id'] for f in frames];require(len(seen)==len(set(seen)) and set(seen)==set(entry['expected_test_ids']),'INCOMPLETE_TEST_SET')
    for frame in frames:
        require((frame['test_id'] in raw['passed'])==(frame['result']=='PASS'),'INVALID_RESULT_BINDING')
        bad=[]
        for ref in frame['record_links']:
            p=ref['raw_pointer']
            if p and p.startswith('/scenarios/'):
                child=next((s for s in scenarios if s['raw_pointer']==p),None);require(child is not None,'INVALID_SCENARIO_BINDING')
                scenario=pointer(raw,p);mapping=raw.get('case_test_map',{}).get(child['case'],[]);require(frame['test_id'] in mapping,'INVALID_CASE_TEST_BINDING')
                if child['missing']:bad.extend(child['missing'])
        if bad:frame['missing'].append('INCOMPLETE_CHILD_SCENARIO');frame['capture_completeness']='INCOMPLETE'
    groups=[]
    for group,count in entry['expected_groups'].items():
        children=[f for f in frames if f['group_id']==group];require(len(children)==count,'INVALID_GROUP_PARTITION')
        groups.append(dict(group_id=group,target=entry['group_policies'][group]['target'],context_scope='INHERITED_WORKER_CONTEXT',context_ref='/worker_context',status='INCOMPLETE' if any(f['missing'] for f in children) else 'CAPTURED_FIELDS_PENDING_REVIEW'))
    sidecar['scenario_metadata']=scenarios;sidecar['groups']=groups
    if any(g['status']=='INCOMPLETE' for g in groups) and sidecar['status']!='INVALID_CAPTURE':sidecar['status']='INCOMPLETE_CAPTURE'
    sidecar['sufficiency']='REVIEW_PENDING';return sidecar


def runner_files(root,entry):
    reader=Reader(root);names=set(entry['runner_explicit_input_paths'])
    import fnmatch
    for pattern in entry['runner_discovery_patterns']:
        parent,leaf=pattern.rsplit('/',1);public_path(parent)
        for name in reader.listing(parent):
            if fnmatch.fnmatchcase(name,leaf):names.add(public_path(parent+'/'+name))
    names.update(entry['runner_effective_inputs'])
    return {p:sha(reader.read(p)) for p in sorted(names)}


def compare_inputs(before,after):
    added=sorted(set(after)-set(before));removed=sorted(set(before)-set(after));changed=[p for p in before.keys()&after.keys() if before[p]!=after[p]]
    runtime=sorted(p for p in changed if p.endswith('.py'));docs=sorted(set(changed)-set(runtime))
    return dict(status='STALE_INPUTS' if added or removed or runtime else 'DOCUMENT_ONLY_CHANGE_REVIEW_PENDING' if docs else 'MATCH',added=added,removed=removed,changed_runtime=runtime,changed_documentary=docs)


def authority_scope(scope):require(scope in IDS,'INVALID_SCOPE');return scope


class BoundedOutput(io.TextIOBase):
    def __init__(self,target,limit):self.target=target;self.limit=limit;self.count=0;self.hash=hashlib.sha256()
    @property
    def encoding(self):return 'utf-8'
    def write(self,value):
        require(type(value) is str,'INVALID_OUTPUT_TYPE');b=value.encode('utf8');require(self.count+len(b)<=self.limit,'RAW_BUDGET');out=self.target.write(value);self.count+=len(b);self.hash.update(b);return out
    def flush(self):
        if not getattr(self.target,'closed',False):return self.target.flush()


class OwnedRoot:
    def __init__(self,root):
        self.root=Path(root);require(self.root.is_dir() and not self.root.is_symlink(),'INVALID_OWNER_ROOT');self.root_identity=(self.root.stat().st_dev,self.root.stat().st_ino);self.nonce=str(uuid.uuid4());self.path=self.root/'OWNER';fd=os.open(self.path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:os.write(fd,self.nonce.encode());self.identity=fingerprint(os.fstat(fd))
        finally:os.close(fd)
    def directory(self):
        fd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        if (os.fstat(fd).st_dev,os.fstat(fd).st_ino)!=self.root_identity:os.close(fd);raise CaptureFault('OWNER_ROOT_CHANGED')
        return fd
    def verify(self):
        directory=self.directory()
        try:
            fd=os.open('OWNER',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
            try:require(stat.S_ISREG(os.fstat(fd).st_mode) and fingerprint(os.fstat(fd))==self.identity and os.read(fd,128)==self.nonce.encode(),'OWNER_NOT_RESTORED')
            finally:os.close(fd)
        finally:os.close(directory)
    def create(self,name):
        self.verify();require(type(name) is str and re.fullmatch('[A-Za-z0-9_.-]+',name),'INVALID_OUTPUT_PATH');fd=self.directory()
        try:return os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        finally:os.close(fd)


def write_json_fd(fd,value,limit):
    b=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode();require(len(b)<=limit,'SIDECAR_BUDGET');left=memoryview(b)
    while left:left=left[os.write(fd,left):]


def receive_line(fd,seconds):
    end=time.monotonic()+seconds;data=b''
    with selectors.DefaultSelector() as selector:
        selector.register(fd,selectors.EVENT_READ)
        while b'\n' not in data:
            require(time.monotonic()<end,'WORKER_TIMEOUT')
            if not selector.select(max(0,end-time.monotonic())):raise CaptureFault('WORKER_TIMEOUT')
            chunk=os.read(fd,4096);require(bool(chunk),'WORKER_EOF');data+=chunk;require(len(data)<=4096,'WORKER_PROTOCOL_BUDGET')
    require(data.endswith(b'\n') and data.count(b'\n')==1,'INVALID_WORKER_PROTOCOL');return strict_json(data)


def verify_ready(message,scope,lease,pid,rawfd,sidefd):
    require(message==dict(event='READY',scope=scope,lease=lease,pid=pid,pgid=pid,raw_inode=os.fstat(rawfd).st_ino,sidecar_inode=os.fstat(sidefd).st_ino),'INVALID_WORKER_IDENTITY')
    require(os.getpgid(pid)==pid,'INVALID_WORKER_GROUP')


def stop_owned(process,owner,identity,grace=2):
    owner.verify();require(identity.get('pid')==process.pid and identity.get('pgid')==process.pid and identity.get('lease')==owner.nonce,'INVALID_WORKER_IDENTITY')
    if process.poll() is None:
        require(os.getpgid(process.pid)==process.pid,'INVALID_WORKER_GROUP')
        os.killpg(process.pid,signal.SIGINT)
        try:process.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=5)
    try:os.killpg(process.pid,0)
    except ProcessLookupError:return dict(status='OWN_GROUP_GONE',worker_exit=process.returncode)
    return dict(status='BLOCKED_DESCENDANTS_UNCONFIRMED',worker_exit=process.returncode)


def launch(scope,root=ROOT):
    scope=authority_scope(scope);reg=read_registry(root);a=authority(root,scope,reg)
    entry=next(e for e in reg['entries'] if e['id']==scope)
    # Fixed future destination, no overwrite and no arbitrary roots from the CLI.
    reader=Reader(root);fd=reader.directory('docs/validation');name='D5-I71-'+scope
    try:os.mkdir(name,0o700,dir_fd=fd)
    finally:os.close(fd)
    outroot=Path(root)/'docs/validation'/name;owner=OwnedRoot(outroot);rawfd=sidefd=None;process=None;release_write=ready_read=None
    context=dict(scope=scope,invocation=invocation(scope),functional_execution='NEW_I71',global_review='OPEN',closure=False,publication_authorized=False)
    try:
        before=runner_files(root,entry);require(before==entry['runner_effective_inputs'],'STALE_INPUTS')
        rawfd=owner.create('runner-raw.json');sidefd=owner.create('sidecar.json');ready_read,ready_write=os.pipe();release_read,release_write=os.pipe()
        cmd=[sys.executable,'-B','-m','testing.prospective_capture.worker',scope,str(sidefd),str(ready_write),str(release_read),owner.nonce]
        env=dict(PATH=os.defpath,LANG='C.UTF-8',LC_ALL='C.UTF-8',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
        process=subprocess.Popen(cmd,cwd=root,stdin=subprocess.DEVNULL,stdout=rawfd,stderr=subprocess.DEVNULL,pass_fds=(sidefd,ready_write,release_read),start_new_session=True,env=env)
        os.close(ready_write);os.close(release_read)
        message=receive_line(ready_read,LIMITS['wait_seconds']);verify_ready(message,scope,owner.nonce,process.pid,rawfd,sidefd)
        identity=dict(pid=process.pid,pgid=process.pid,lease=owner.nonce);write_json_fd(release_write,dict(event='RELEASE',lease=owner.nonce),4096);os.write(release_write,b'\n');os.close(release_write);release_write=None
        try:process.wait(timeout=LIMITS['campaign_seconds'])
        except subprocess.TimeoutExpired:context['timeout']=True
        context['cleanup']=stop_owned(process,owner,identity);context['worker_exit_code']=process.returncode
        context['runner_inputs_before']=before;context['runner_inputs_after']=runner_files(root,entry);context['input_comparison']=compare_inputs(before,context['runner_inputs_after'])
        context['artifacts']={p.name:sha(p.read_bytes()) for p in [outroot/'runner-raw.json',outroot/'sidecar.json'] if p.is_file()}
        after_authority=authority(root,scope,reg);require(after_authority==a,'STALE_AUTHORITY')
        packet_reader=Reader(root);rawbytes=packet_reader.read('docs/validation/'+name+'/runner-raw.json');side= strict_json(packet_reader.read('docs/validation/'+name+'/sidecar.json'));raw=strict_json(rawbytes)
        require(side.get('raw_sha256')==sha(rawbytes) and side.get('raw_bytes')==len(rawbytes),'INVALID_PACKET_BINDING')
        require(side.get('runner_inputs_before')==before and side.get('runner_inputs_after')==context['runner_inputs_after'],'INVALID_PACKET_BINDING')
        context['capture_inputs_before']=a['capture_inputs'];context['capture_inputs_after']=after_authority['capture_inputs']
        context['capture_status']='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' if process.returncode==0 and side.get('status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' and context['cleanup']['status']=='OWN_GROUP_GONE' and context['input_comparison']['status']=='MATCH' else 'BLOCKED'
    except (CaptureFault,OSError,ValueError) as ex:
        context['capture_status']='INVALID_CAPTURE';context['error_code']=ex.code if isinstance(ex,CaptureFault) else 'SANITIZED_LAUNCH_ERROR'
        if process is not None:
            # Identity comes from our Popen session, never from untrusted stdout.
            context['cleanup']=stop_owned(process,owner,dict(pid=process.pid,pgid=process.pid,lease=owner.nonce))
    finally:
        for fd in [rawfd,sidefd,ready_read,release_write]:
            if fd is not None:os.close(fd)
        cfd=owner.create('context.json')
        try:write_json_fd(cfd,context,LIMITS['sidecar_bytes'])
        finally:os.close(cfd)
    return context


def plan(root=ROOT):
    reg=read_registry(root)
    return dict(schema='d5.prospective-capture-plan.v1',phase='I70_COMPONENTS_ONLY',functional_execution_authorized=False,catalog=[dict(id=e['id'],scope=e['scope'],expected_tests=e['expected_tests'],status='NOT_RUN_I71_AUTHORIZATION_REQUIRED') for e in reg['entries']],semantic_baseline=reg['semantic_baseline'],global_review='OPEN',closure=False,publication_authorized=False)


def main(argv=None):
    args=sys.argv[1:] if argv is None else argv
    try:
        if not args:out=plan();code=0
        else:require(len(args)==2 and args[0]=='--capture','INVALID_ARGUMENTS');out=launch(args[1]);code=0 if out.get('capture_status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' else 1
    except (CaptureFault,OSError,ValueError,KeyError,TypeError) as ex:out=dict(status='BLOCKED',code=ex.code if isinstance(ex,CaptureFault) else 'SANITIZED_COMPONENT_ERROR',closure=False,publication_authorized=False);code=2
    print(json.dumps(out,ensure_ascii=False));return code


if __name__=='__main__':raise SystemExit(main())
