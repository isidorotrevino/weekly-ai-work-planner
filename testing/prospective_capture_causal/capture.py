# SPDX-License-Identifier: GPL-3.0-only
"""I83 causal capture. Only pure capture helpers are imported; I84 is separate."""
import ast
import fnmatch
import json
import os
from pathlib import Path
import re
import sys
import types
import hashlib
import threading
import unittest
import inspect
import functools
import multiprocessing.connection
import multiprocessing.process
import multiprocessing.context
import multiprocessing.popen_spawn_posix
import multiprocessing.popen_fork
from testing.prospective_capture_late import capture as late
c=late.c;t=late.t;ROOT=late.ROOT;LIMITS=dict(late.LIMITS)
REGISTRY='docs/validation/D5-CAUSAL-CAPTURE-REGISTRY.json'
CONTRACT='docs/validation/D5-I82-design-review.json'
AUTHORITY='docs/validation/D5-I84-capture-authorization.json'
DESTINATION='docs/validation/D5-I84-P01'
LAUNCH_COPY='docs/validation/D5-I84-P01-launch.json'
NORMAL_SCHEMA='d5.causal-sidecar.v1';FAILURE_SCHEMA='d5.causal-worker-failure.v1'
DIAGNOSTIC_SCHEMA=late.DIAGNOSTIC_SCHEMA;PHASES=late.PHASES;CODES=late.CODES
PROTOCOL_POINTS=frozenset(('recovery_fsync','before_object','after_object','before_replace','directory_fsync','after_head','before_lock','fsync_failure','prepared'))
ChannelRoot=late.ChannelRoot;PageSink=late.PageSink;encode=late.encode;write_all=late.write_all
scope=late.scope;verify_ready=late.verify_ready;verify_release=late.verify_release
wait_worker=late.wait_worker;package_names=late.package_names;package_size=late.package_size
evidence_reader=late.evidence_reader;LateBindings=late.LateBindings

def runner_files(root,entry,reader=None):
    r=reader if reader is not None else c.Reader(root);names=set(entry['runner_explicit_input_paths'])
    for pattern in entry['runner_discovery_patterns']:
        parent,leaf=pattern.rsplit('/',1);c.public_path(parent)
        for name in r.listing(parent):
            if fnmatch.fnmatchcase(name,leaf):names.add(c.public_path(parent+'/'+name))
    names.update(entry['runner_effective_inputs']);return {n:c.sha(r.read(n)) for n in sorted(names)}

def safe_code(code):return next((literal for literal in CODES if type(code) is str and code==literal and literal!='OK'),'SANITIZED_WORKER_ERROR')

class Ledger:
    def __init__(self,lease,pid=None):
        self.lease=lease;self.pid=os.getpid() if pid is None else pid;self.phase='AUTHORITY';self.first=None;self.run_id=None
    def at(self,phase):c.require(phase in PHASES,'INVALID_WORKER_DIAGNOSTIC');self.phase=phase
    def fail(self,code):
        if self.first is None:self.first=(self.phase if self.phase!='COMPLETE' else 'FINALIZE',safe_code(code))
    def exception(self,ex):self.fail(ex.code if type(ex) is c.CaptureFault else None)
    def value(self):
        failed=self.first is not None;phase,code=self.first if failed else ('COMPLETE','OK')
        return dict(schema=DIAGNOSTIC_SCHEMA,status='FAILED' if failed else 'COMPLETED',phase=phase,code=code,scope='P01',lease=self.lease,pid=self.pid,pgid=self.pid,capture_run_id=self.run_id)

def validate_diagnostic(value,lease,pid,run_id=None,normal=False):
    c.require(type(value) is dict and set(value)=={'schema','status','phase','code','scope','lease','pid','pgid','capture_run_id'},'INVALID_WORKER_DIAGNOSTIC')
    c.require(value['schema']==DIAGNOSTIC_SCHEMA and value['scope']=='P01' and type(value['phase']) is str and value['phase'] in PHASES and type(value['code']) is str and value['code'] in CODES,'INVALID_WORKER_DIAGNOSTIC')
    c.require(value['lease']==lease and t.uuid_value(lease) and type(value['pid']) is int and type(value['pgid']) is int and type(pid) is int and pid>0 and value['pid']==value['pgid']==pid,'INVALID_WORKER_DIAGNOSTIC')
    rid=value['capture_run_id'];c.require((rid is None or t.uuid_value(rid)) and (not normal or t.uuid_value(run_id) and rid==run_id),'INVALID_WORKER_DIAGNOSTIC')
    c.require((value['status']=='COMPLETED' and value['phase']=='COMPLETE' and value['code']=='OK') or (value['status']=='FAILED' and value['phase']!='COMPLETE' and value['code']!='OK'),'INVALID_WORKER_DIAGNOSTIC')
    c.require(len(encode(value))<=4096,'WORKER_DIAGNOSTIC_BUDGET');return value

def read_sidecar(body,lease,pid):
    try:side=c.strict_json(body)
    except c.CaptureFault:raise c.CaptureFault('SIDECAR_PARTIAL_OR_INVALID') from None
    c.require(type(side) is dict and side.get('schema') in (NORMAL_SCHEMA,FAILURE_SCHEMA),'INVALID_WORKER_DIAGNOSTIC')
    failure=side['schema']==FAILURE_SCHEMA
    if failure:c.require(set(side)=={'schema','worker_diagnostic'} and len(body)<=4096,'INVALID_WORKER_DIAGNOSTIC')
    diagnostic=validate_diagnostic(side.get('worker_diagnostic'),lease,pid,side.get('capture_run_id'),not failure)
    if failure:c.require(diagnostic['status']=='FAILED','INVALID_WORKER_DIAGNOSTIC')
    elif side.get('status') in ('INVALID_CAPTURE','INCOMPLETE_CAPTURE'):c.require(diagnostic['status']=='FAILED','INVALID_WORKER_DIAGNOSTIC')
    return side,diagnostic

class SideWriter:
    """One attempt only; partial output can never be repaired by a second JSON."""
    def __init__(self,fd,lease,pid=None):self.fd=fd;self.lease=lease;self.pid=os.getpid() if pid is None else pid;self.started=False
    def write(self,value,limit=LIMITS['index_sidecar_bytes']):
        c.require(not self.started,'SIDECAR_WRITE_ALREADY_STARTED');body=encode(value);c.require(len(body)<=limit,'SIDECAR_BUDGET');read_sidecar(body,self.lease,self.pid);self.started=True;write_all(self.fd,body)
    def failure(self,ledger):
        if self.started:return False
        self.write(dict(schema=FAILURE_SCHEMA,worker_diagnostic=ledger.value()),4096);return True

def invocation(args=None):
    out=c.invocation('P01');out['command']=['python3','-B','-m','testing.prospective_capture_causal.worker','P01'];out['worker_arguments_observed']=args;return out

def launch(requested,root=ROOT):
    scope(requested);inputs=c.Reader(root);reg=read_registry(root,inputs);approved=authority(root,requested,reg,inputs);entry=reg['entry']
    reader=c.Reader(root);fd=reader.directory('docs/validation')
    try:
        # Reserve both fixed paths without touching previous evidence.
        launchfd=os.open(Path(LAUNCH_COPY).name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        try:os.mkdir(Path(DESTINATION).name,0o700,dir_fd=fd)
        except BaseException:os.close(launchfd);raise
    finally:os.close(fd)
    try:owner=c.OwnedRoot(Path(root)/DESTINATION)
    except BaseException:os.close(launchfd);raise
    context=dict(scope='P01',invocation=invocation(),functional_execution='NEW_I84',closure=False,global_review='OPEN',publication_authorized=False)
    rawfd=sidefd=directory=ready_read=ready_write=release_read=release_write=None;process=None
    try:
        before=runner_files(root,entry,inputs);c.require(before==entry['runner_effective_inputs'],'STALE_INPUTS')
        rawfd=owner.create('runner-raw.json');sidefd=owner.create('sidecar.json');directory=owner.directory();ready_read,ready_write=os.pipe();release_read,release_write=os.pipe()
        cmd=[sys.executable,'-B','-m','testing.prospective_capture_causal.worker','P01',str(sidefd),str(ready_write),str(release_read),str(directory),owner.nonce]
        process=c.subprocess.Popen(cmd,cwd=root,stdin=c.subprocess.DEVNULL,stdout=rawfd,stderr=c.subprocess.DEVNULL,pass_fds=(sidefd,ready_write,release_read,directory),start_new_session=True,env=dict(PATH=os.defpath,LANG='C.UTF-8',LC_ALL='C.UTF-8',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8'))
        os.close(ready_write);ready_write=None;os.close(release_read);release_read=None
        verify_ready(c.receive_line(ready_read,LIMITS['wait_seconds']),owner.nonce,process.pid,rawfd,sidefd,directory)
        c.write_json_fd(release_write,dict(event='RELEASE',lease=owner.nonce),4096);write_all(release_write,b'\n');os.close(release_write);release_write=None
        if not wait_worker(process):context['timeout']=True
        context['cleanup']=c.stop_owned(process,owner,dict(pid=process.pid,pgid=process.pid,lease=owner.nonce));context['worker_exit_code']=process.returncode
        context['runner_inputs_before']=before;context['runner_inputs_after']=runner_files(root,entry,inputs);context['input_comparison']=c.compare_inputs(before,context['runner_inputs_after'])
        c.require(authority(root,'P01',reg,inputs)==approved,'STALE_AUTHORITY');context['capture_inputs_before']=approved['capture_inputs'];context['capture_inputs_after']=approved['capture_inputs']
        packet=evidence_reader(root);rawb=packet.read(DESTINATION+'/runner-raw.json');sideb=packet.read(DESTINATION+'/sidecar.json');side,diag=read_sidecar(sideb,owner.nonce,process.pid);context['worker_diagnostic']=diag
        if side['schema']==FAILURE_SCHEMA:
            context['capture_status']='BLOCKED_WORKER_FAILURE';context['artifact_error_code']='RAW_EMPTY' if not rawb else 'FUNCTIONAL_RAW_NOT_ACCEPTED_WITH_FAILURE_ENVELOPE'
            context['page_validation']=dict(status='NOT_ACCEPTED_WORKER_FAILURE');return context
        raw=c.strict_json(rawb)
        c.require(len(rawb)<=LIMITS['raw_bytes'] and len(sideb)<=LIMITS['index_sidecar_bytes'] and c.sha(rawb)==side.get('raw_sha256') and len(rawb)==side.get('raw_bytes'),'INVALID_PACKET_BINDING')
        c.require(side.get('runner_inputs_before')==before and side.get('runner_inputs_after')==context['runner_inputs_after'],'INVALID_PACKET_BINDING')
        c.require(side.get('capture_inputs_before')==side.get('capture_inputs_after')==approved['capture_inputs'],'INVALID_PACKET_BINDING')
        c.require(side.get('schema')==NORMAL_SCHEMA and side.get('observers_restored') is True and side.get('entrypoint_exit_code')==(0 if raw.get('status')=='PASS' else 1),'INVALID_PACKET_BINDING')
        context['artifacts']={'runner-raw.json':c.sha(rawb),'sidecar.json':c.sha(sideb)}
        # Invalid/partial pages are preserved, never accepted as a complete trace.
        if side.get('status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW':context['page_validation']=validate_pages(packet,DESTINATION,side,profile=reg);c.aggregate_capture(side,c.scenario_metadata(raw,entry),raw,entry)
        else:context['page_validation']=dict(status='NOT_ACCEPTED_INCOMPLETE_CAPTURE')
        packet.finish();context['capture_status']='BLOCKED_WORKER_FAILURE' if diag['status']=='FAILED' else 'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' if process.returncode==0 and side.get('status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' and context['cleanup']['status']=='OWN_GROUP_GONE' and context['input_comparison']['status']=='MATCH' else 'BLOCKED'
    except BaseException as ex:
        context['capture_status']='BLOCKED_WORKER_FAILURE' if context.get('worker_diagnostic',{}).get('status')=='FAILED' else 'INVALID_CAPTURE';context['error_code']=ex.code if isinstance(ex,c.CaptureFault) else 'SANITIZED_LAUNCH_ERROR'
        if 'worker_diagnostic' not in context:context['worker_diagnostic_status']='WORKER_DIAGNOSTIC_NOT_RECORDED'
        elif context['worker_diagnostic']['status']=='FAILED':context['artifact_error_code']=context['error_code']
        if process is not None:
            try:context['cleanup']=c.stop_owned(process,owner,dict(pid=process.pid,pgid=process.pid,lease=owner.nonce))
            except BaseException:context['cleanup']=dict(status='BLOCKED_OWNERSHIP_UNCONFIRMED')
            if 'worker_diagnostic' not in context:
                try:
                    packet=packet if 'packet' in locals() else evidence_reader(root);body=packet.read(DESTINATION+'/sidecar.json');parsed,diag=read_sidecar(body,owner.nonce,process.pid);context['worker_diagnostic']=diag
                    if diag['status']=='FAILED':context['capture_status']='BLOCKED_WORKER_FAILURE';context['artifact_error_code']=context['error_code']
                    context.pop('worker_diagnostic_status',None)
                except BaseException:pass
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


def fault(ok,code='CAUSAL_SCHEMA_INVALID'):
    c.require(ok,code)


def integer(v):return type(v) is int and 0<=v<=1023

def sha_value(v):return type(v) is str and re.fullmatch('[0-9a-f]{64}',v) is not None

def token(v):return type(v) is str and re.fullmatch(r'[A-Za-z0-9_.:/+\-]{1,128}',v) is not None


def bounded_builtin(value,limits=None):
    """Validate before JSON serialization, with I70's exact-type/depth/byte guard."""
    out=c.digest_value(value,dict(LIMITS,**(limits or {})))
    fault(out['status']=='OBSERVED_DIGEST','CAUSAL_FIELD_BUDGET')
    return out


def canonical_hash(value,drive=False,limits=None):
    digest=bounded_builtin(value,limits)
    body=json.dumps(value,sort_keys=True,ensure_ascii=drive,allow_nan=False,separators=(',',':')).encode('utf-8')+(b'\n' if drive else b'')
    fault(len(body)+digest['bytes']<=dict(LIMITS,**(limits or {}))['operand_bytes'],'CAUSAL_FIELD_BUDGET')
    return c.sha(body)


def selectors(value,spec):
    fault(type(value) is dict,'COMMAND_HEADER_INVALID');out={}
    for key,val in value.items():
        if key in spec['UUID']:valid=t.uuid_value(val)
        elif key in spec['SHA256']:valid=sha_value(val)
        elif key in spec['INTEGER']:valid=integer(val)
        elif key in spec['BOOL']:valid=type(val) is bool
        elif key in spec['CONSTANT_TOKEN']:valid=token(val)
        elif key in spec['IDENTITY_SCALAR']:
            allowed=spec['IDENTITY_SCALAR'][key];valid=('EXACT_UUID' in allowed and t.uuid_value(val)) or ('EXACT_SHA256' in allowed and sha_value(val))
        else:continue
        fault(valid,'COMMAND_HEADER_INVALID');out[key]=val
    fault(len(out)<=spec['maximum_selected_fields'],'CAUSAL_FIELD_BUDGET');return out


def store_request(bound,limits=None):
    fault(type(bound) is dict,'COMMAND_HEADER_INVALID')
    cid=bound.get('cid');kind=bound.get('kind');args=bound.get('args');expected=bound.get('expected')
    fault(t.uuid_value(cid) and token(kind) and type(args) is dict,'COMMAND_HEADER_INVALID')
    fault(expected is None or type(expected) is dict and set(expected)=={'seq','commit_sha256'} and integer(expected['seq']) and sha_value(expected['commit_sha256']),'COMMAND_HEADER_INVALID')
    args_digest=bounded_builtin(args,limits);op=dict(kind=kind,args=args,expected=expected);op_digest=bounded_builtin(op,limits);body=json.dumps(op,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')
    fault(args_digest['bytes']+op_digest['bytes']+len(body)<=dict(LIMITS,**(limits or {}))['operand_bytes'],'CAUSAL_FIELD_BUDGET')
    return dict(hash_namespace='STORE_REQUEST',command_id=cid,kind=kind,expected=expected.copy() if expected is not None else None,args_digest=args_digest,request_sha256=c.sha(body))


def drive_request(value,limits=None):
    lim=dict(LIMITS,**(limits or {}));original=None
    if type(value) is bytes:
        fault(len(value)<=lim['operand_bytes'],'CAUSAL_FIELD_BUDGET');original=c.sha(value)
        # strict_json checks duplicate keys, nonfinite literals and exact tree quotas.
        req=c.strict_json(value)
    else:req=value
    decoded_digest=bounded_builtin(req,lim)
    fault(type(req) is dict and set(req)=={'schema','command_id','expected_version','expected_head','page'},'COMMAND_HEADER_INVALID')
    fault(req['schema']=='d5.fixture-drive-command.v1' and t.uuid_value(req['command_id']) and integer(req['expected_version']) and sha_value(req['expected_head']),'COMMAND_HEADER_INVALID')
    body=json.dumps(req,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode('utf-8')+b'\n'
    fault(decoded_digest['bytes']+len(body)+(len(value) if type(value) is bytes else 0)<=lim['operand_bytes'],'CAUSAL_FIELD_BUDGET')
    return dict(hash_namespace='DRIVE_REQUEST',schema=req['schema'],command_id=req['command_id'],expected_version=req['expected_version'],expected_head=req['expected_head'],request_sha256=c.sha(body),input_bytes_sha256=original)


def store_receipt(value,spec,limits=None):
    whole_digest=bounded_builtin(value,limits);fault(type(value) is dict,'COMMAND_HEADER_INVALID')
    keys=set(spec['receipt_store']['required_fields'])-{'schema','source_schema','result_digest','result_metadata'}
    fault(keys<=set(value) and 'result' in value and value.get('schema')=='d5.durable-receipt.v1','COMMAND_HEADER_INVALID')
    out={k:value[k] for k in keys}
    fault(t.uuid_value(out['command_id']) and all(sha_value(out[k]) for k in ('request_sha256','before_state_sha256','after_data_sha256')),'COMMAND_HEADER_INVALID')
    fault(all(integer(out[k]) for k in ('before_seq','seq')) and type(out['historical']) is bool,'COMMAND_HEADER_INVALID')
    fault(out['grants_execution_authority'] is False and out['activation_allowed'] is False and type(out['quota_consumed']) is int and out['quota_consumed']==0 and type(out['reservations_created']) is int and out['reservations_created']==0,'COMMAND_HEADER_INVALID')
    result_digest=bounded_builtin(value['result'],limits);fault(whole_digest['bytes']+result_digest['bytes']<=dict(LIMITS,**(limits or {}))['operand_bytes'],'CAUSAL_FIELD_BUDGET')
    out.update(schema=spec['receipt_store']['schema'],source_schema=value['schema'],result_digest=result_digest,result_metadata=selectors(value['result'],spec['metadata_selectors']))
    return out


def drive_receipt(value,spec):
    bounded_builtin(value);fault(type(value) is dict,'COMMAND_HEADER_INVALID');fields=spec['receipt_drive']['fields'];keys=set(fields)-{'source_schema'}
    fault(set(value)==keys|{'schema'} and value['schema']=='d5.fixture-drive-receipt.v1','COMMAND_HEADER_INVALID')
    fault(t.uuid_value(value['command_id']) and sha_value(value['request_sha256']) and sha_value(value['commit_sha256']) and integer(value['version']),'COMMAND_HEADER_INVALID')
    fault(value['result']=='SYNTHETIC_CAPTURE_CONFIRMED' and value['reference_selected'] is False and type(value['persistent_D2_writes']) is int and value['persistent_D2_writes']==0 and type(value['remote_requests']) is int and value['remote_requests']==0,'COMMAND_HEADER_INVALID')
    return dict(schema=spec['receipt_drive']['schema'],source_schema=value['schema'],**{k:value[k] for k in keys})


def oracle_value(value,kind,spec,limits=None):
    digest=bounded_builtin(value,limits);fault(kind in ('T','R'),'ORACLE_VALUE_MISSING');keys=spec['retained_oracle']['value_keys'][kind+'_keys']
    fault(type(value) is dict and set(value)==set(keys),'ORACLE_VALUE_MISSING')
    fault(token(value['case']) and type(value['role']) is str and value['role'] in ('CLIENT','REMOTE') and t.uuid_value(value['store_id']),'ORACLE_VALUE_MISSING')
    for key in keys:
        if key.endswith('_sha256'):fault(sha_value(value[key]),'ORACLE_VALUE_MISSING')
        elif key not in ('case','role','store_id'):fault(integer(value[key]),'ORACLE_VALUE_MISSING')
    body=encode(value);fault(len(body)<=4096 and len(body)+digest['bytes']<=dict(LIMITS,**(limits or {}))['operand_bytes'],'CAUSAL_FIELD_BUDGET');return dict(value),digest


def stdlib_description():
    """No historical imports. Exact stdlib identities, signatures, bytes and code."""
    modules={'unittest.case':unittest.case,'multiprocessing.connection':multiprocessing.connection,'multiprocessing.process':multiprocessing.process,'multiprocessing.context':multiprocessing.context,'multiprocessing.popen_spawn_posix':multiprocessing.popen_spawn_posix,'multiprocessing.popen_fork':multiprocessing.popen_fork}
    specs=[]
    for mod,cls,name in [('unittest.case','TestCase','subTest'),('unittest.case','_SubTest','__init__'),('unittest.case','_OrderedChainMap','__iter__'),('multiprocessing.connection','_ConnectionBase','recv'),('multiprocessing.process','BaseProcess','join')]:
        m=modules[mod];fn=m.__dict__[cls].__dict__[name]
        fault(type(fn) is types.FunctionType,'UNSUPPORTED_SUBCASE_BINDING')
        specs.append(dict(module=mod,class_name=cls,method=name,parameters=list(inspect.signature(fn,eval_str=False).parameters),source_sha256=c.sha(Path(m.__file__).read_bytes()),origin='EXACT_STDLIB_MODULE_OBJECT_PRIVATE_PREFIX_NOT_EMITTED',callable_code_sha256=c.sha(fn.__code__.co_code),unwrapped_code_sha256=c.sha(inspect.unwrap(fn).__code__.co_code)))
    typespec=[]
    for mod,cls in [('multiprocessing.context','SpawnProcess'),('multiprocessing.popen_spawn_posix','Popen'),('multiprocessing.popen_fork','Popen')]:
        m=modules[mod];fault(type(m.__dict__[cls]) is type,'UNSUPPORTED_CAUSAL_API');typespec.append(dict(module=mod,class_name=cls,source_sha256=c.sha(Path(m.__file__).read_bytes()),origin='EXACT_STDLIB_MODULE_OBJECT_PRIVATE_PREFIX_NOT_EMITTED'))
    return dict(runtime=dict(python=c.platform.python_version(),implementation=c.platform.python_implementation(),platform=c.platform.system()),specs=specs,process_object_types=typespec)


def negative_catalog(inventory,reader):
    """Closed selectors fixed from pinned I82 test/helper AST and literal codes.

    This is source expectation only. Acceptance also requires the exact original
    runtime exception code; no guessed cid/request hash is filled in.
    """
    sources={};out={}
    for row in inventory:
        binding=row['source_binding'];name=binding['path']
        if name not in sources:
            body=reader.read(name);fault(c.sha(body)==binding['sha256'],'STALE_POLICY_SOURCE');sources[name]=ast.parse(body)
        tree=sources[name];owner=binding['symbol'].split('.')[0]
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==owner)
        methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in row['helper_closure']];codes=set()
        for method in methods:
            for node in ast.walk(method):
                if not isinstance(node,ast.Call):continue
                fn=node.func.attr if isinstance(node.func,ast.Attribute) else None
                if fn in ('error','assertRaisesRegex'):
                    for arg in node.args:
                        if isinstance(arg,ast.Constant) and type(arg.value) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,79}',arg.value):codes.add(arg.value)
        if codes:
            out[row['test_id']]=dict(source_binding=binding,exception_codes=sorted(codes),methods=['FixtureStore.advance'] if row['family']=='DRIVE' else ['Store.transact'],input_failures=['COMMAND_HEADER_INVALID','CAUSAL_FIELD_BUDGET','INVALID_JSON','JSON_DEPTH','JSON_STRING_BUDGET'])
    return out


def read_registry(root=ROOT,reader=None):
    r=reader or c.Reader(root);reg=c.strict_json(r.read(REGISTRY));design=c.strict_json(r.read(CONTRACT));old=late.read_registry(root,r)
    added={'inventory','source_anchors','stdlib_bindings','subcase_parameter_allowlist','retained_oracles','observer_scope','causal_graph','projection_schemas','future_runtime_dependency_scope'}
    fault(set(reg)==set(old)|added|{'negative_input_selectors'},'INVALID_REGISTRY')
    changed={'schema','contract_path','contract_sha256','legacy_registry_sha256','semantic_baseline'}
    fault(reg['schema']=='d5.causal-capture-registry.v1' and reg['contract_path']==CONTRACT and reg['contract_sha256']==c.sha(r.read(CONTRACT)) and reg['legacy_registry_sha256']==c.sha(r.read(late.REGISTRY)),'INVALID_REGISTRY')
    fault(all(reg[k]==old[k] for k in set(old)-changed) and all(reg[k]==design[k] for k in added),'INVALID_REGISTRY')
    fault(reg['semantic_baseline']=={'SUPPORTS_BOUNDED':83,'PARTIAL':1} and reg['limits']==design['proposed_limits'],'INVALID_REGISTRY')
    fault(reg['negative_input_selectors']==negative_catalog(reg['inventory'],r),'INVALID_REGISTRY')
    observed=stdlib_description();pinned=reg['stdlib_bindings']
    fault(all(observed[k]==pinned[k] for k in observed),'STDLIB_BINDING_CHANGED')
    for a in reg['source_anchors']:fault(c.sha(r.read(a['path']))==a['sha256'],'STALE_POLICY_SOURCE')
    return reg


def authority_inputs():
    return {f'testing/prospective_capture_causal/{n}' for n in ('capture.py','worker.py','test_causal_capture.py','run_causal_lab.py','README.md')}|{REGISTRY,CONTRACT,'docs/validation/D5-I82-integrity.json','docs/validation/D5-I83-tests-raw.json','docs/validation/D5-I83-results.json','docs/validation/D5-I83-integrity.json'}


def authority(root,requested,reg,reader=None):
    scope(requested);r=reader or c.Reader(root)
    try:a=c.strict_json(r.read(AUTHORITY))
    except FileNotFoundError:raise c.CaptureFault('I84_AUTHORIZATION_REQUIRED') from None
    fault(type(a) is dict and set(a)=={'schema','phase','scopes','registry_sha256','capture_inputs'} and a['schema']=='d5.causal-capture-authority.v1' and a['phase']=='I84_EXPLICITLY_APPROVED' and a['scopes']==['P01'],'I84_AUTHORIZATION_REQUIRED')
    fault(a['registry_sha256']==c.sha(r.read(REGISTRY)) and type(a['capture_inputs']) is dict and authority_inputs()<=set(a['capture_inputs']),'STALE_AUTHORITY')
    pins=reg['future_runtime_dependency_scope']['pinned_existing_names'];fault(all(a['capture_inputs'].get(n)==h for n,h in pins.items()),'STALE_AUTHORITY')
    for n,h in a['capture_inputs'].items():fault(sha_value(h) and c.sha(r.read(c.public_path(n)))==h,'STALE_AUTHORITY')
    raw=c.strict_json(r.read('docs/validation/D5-I83-tests-raw.json'));fault(raw.get('status')=='PASS' and raw.get('tests_run')==96 and raw.get('functional_campaigns_executed')==0 and raw.get('forbidden_imports')==[],'COMPONENT_VALIDATION_REQUIRED')
    seal=c.strict_json(r.read('docs/validation/D5-I83-integrity.json'));fault(bool(seal.get('artifacts')),'COMPONENT_VALIDATION_REQUIRED')
    for n,h in seal['artifacts'].items():fault(a['capture_inputs'].get(n)==h and c.sha(r.read(n))==h,'STALE_AUTHORITY')
    return a


def plan(root=ROOT):
    reg=read_registry(root)
    return dict(schema='d5.causal-capture-plan.v1',phase='I83_COMPONENTS_ONLY',scope='P01',expected_tests=321,status='NOT_RUN_I84_AUTHORIZATION_REQUIRED',functional_execution_authorized=False,semantic_baseline=reg['semantic_baseline'],closure=False,global_review='OPEN',publication_authorized=False)


class CausalState:
    """Per-recorder bounded memory. Object refs are strong, never Python id values."""
    def __init__(self,run_id,limits,spec,charge,emit,invalid):
        self.run_id=run_id;self.limits=limits;self.spec=spec;self.charge=charge;self.emit=emit;self.invalid=invalid
        self.tables={k:{} for k in ('retained_oracles','subcases','protocol_instances','causal_links')}
        self.objects=[];self.threads=[];self.domains={};self.oracle_guards=[];self.frame=None;self.test=None;self.test_thread=None;self.subobjects=[];self.stacks={};self.calls={};self.counter=0
    def ref(self,prefix):self.charge();self.counter+=1;return prefix+str(self.counter)
    def object_ref(self,obj):
        for old,ref in self.objects:
            if old is obj:return ref
        ref=self.external_owner(obj,None) if getattr(self,'external_owner',None) else self.ref('A')
        fault(ref is not None,'ORACLE_DOMAIN_IDENTITY_MISSING');self.charge();self.objects.append((obj,ref));return ref
    def thread(self):
        obj=threading.current_thread()
        for old,ref in self.threads:
            if old is obj:return ref
        ref=self.ref('T');self.threads.append((obj,ref));return ref
    def begin(self,frame,test):
        self.frame=frame;self.test=test;self.test_thread=threading.current_thread();self.subcase()
    def context(self):
        fault(self.frame is not None,'CAUSAL_LINK_MISSING')
        return dict(capture_run_id=self.run_id,test_frame_id=self.frame['test_frame_id'],subcase_ref=self.subcase(),thread_ref=self.thread())
    def subcase(self,explicit=None):
        thread=self.thread();sub=None;params={};kind='ROOT_FRAME'
        if threading.current_thread() is not self.test_thread:kind='THREAD_FRAME_SCOPE_ONLY'
        else:
            fault(isinstance(self.test,unittest.TestCase),'UNSUPPORTED_SUBCASE_BINDING')
            memory=object.__getattribute__(self.test,'__dict__');fault(type(memory) is dict,'UNSUPPORTED_SUBCASE_BINDING');sub=explicit if explicit is not None else memory.get('_subtest')
            if sub is not None:
                fault(type(sub) is unittest.case._SubTest,'UNSUPPORTED_SUBCASE_BINDING');kind='UNITTEST_SUBTEST'
                sm=object.__getattribute__(sub,'__dict__');cm=sm.get('params');fault(type(cm) is unittest.case._OrderedChainMap,'UNSUPPORTED_SUBCASE_BINDING')
                maps=object.__getattribute__(cm,'__dict__').get('maps');fault(type(maps) is list and len(maps)<=self.limits['depth'],'UNSUPPORTED_SUBCASE_BINDING')
                for m in reversed(maps):
                    fault(type(m) is dict,'UNSUPPORTED_SUBCASE_BINDING')
                    for k,v in m.items():
                        fault(type(k) is str and k in self.spec['subcase']['param_keys'],'UNSUPPORTED_SUBCASE_BINDING')
                        fault(v is None or type(v) is bool or integer(v) or token(v),'UNSUPPORTED_SUBCASE_BINDING');params[k]=v
        frame=self.frame['test_frame_id']
        for old,f,t,key in self.subobjects:
            if old is sub and f==frame and t==thread:
                fault(self.tables['subcases'][key]['params']==params,'UNSUPPORTED_SUBCASE_BINDING');return key
        key=self.ref('S');self.subobjects.append((sub,frame,thread,key))
        row=dict(schema=self.spec['subcase']['schema'],capture_run_id=self.run_id,test_frame_id=frame,subcase_ref=key,kind=kind,parent_ref=None,thread_ref=thread,params=params,result_refs=[])
        self.tables['subcases'][key]=row;self.row_budget(row);return key
    def row_budget(self,row):
        bounded_builtin(row,self.limits);fault(len(encode(row))<=4096,'CAUSAL_FIELD_BUDGET')
    def declaration(self,obj,identity):
        fault(type(identity) is dict and t.uuid_value(identity.get('run_id')),'ORACLE_DOMAIN_IDENTITY_MISSING')
        if 'store_id' in identity:fault(t.uuid_value(identity['store_id']) and identity.get('role') in ('CLIENT','REMOTE'),'ORACLE_DOMAIN_IDENTITY_MISSING')
        ctx=self.context();key=self.object_ref(obj);value=dict(identity,**ctx)
        prior=self.domains.get((ctx['test_frame_id'],ctx['subcase_ref'],key))
        fault(prior is None or all(prior.get(k)==v for k,v in identity.items()),'ORACLE_DOMAIN_IDENTITY_MISSING')
        self.domains[(ctx['test_frame_id'],ctx['subcase_ref'],key)]=value
        return key
    def domain(self,head):
        fault(type(head) is dict,'ORACLE_DOMAIN_IDENTITY_MISSING');ctx=self.context()
        candidates=[]
        for (frame,sub,key),row in self.domains.items():
            if frame==ctx['test_frame_id'] and sub==ctx['subcase_ref'] and all(row.get(k)==head.get(k) for k in ('run_id','store_id','role')):candidates.append(key)
        fault(len(candidates)==1,'ORACLE_DOMAIN_IDENTITY_MISSING');return candidates[0]
    def retain(self,module,index,value,kind,returned,call_ref):
        val,digest=oracle_value(value,kind,self.spec,self.limits);fault(type(returned) is dict and type(returned.get('head')) is dict and type(returned.get('state')) is dict and type(returned.get('chain')) is list,'ORACLE_VALUE_MISSING')
        head=returned['head'];hk='commit_sha256' if kind=='T' else 'head_sha256'
        fault(all(head.get(k)==val[k] for k in ('store_id','role','seq')) and head.get('commit_sha256')==val[hk] and canonical_hash(returned['state'],limits=self.limits)==val['state_sha256'],'ORACLE_VALUE_MISSING')
        fault(type(returned['state'].get('receipts')) is dict and len(returned['state']['receipts'])==val['receipts'],'ORACLE_VALUE_MISSING')
        domain=self.domain(head);ctx=self.context();key=self.ref('V')
        row=dict(schema=self.spec['retained_oracle']['schema'],capture_run_id=self.run_id,test_frame_id=ctx['test_frame_id'],subcase_ref=ctx['subcase_ref'],source_module=module,source_field='ORACLES',source_index=index,oracle_kind=kind,value=val,value_digest=digest,domain_ref=domain,oracle_return_ref=call_ref)
        self.row_budget(row);self.tables['retained_oracles'][key]=row;self.oracle_guards.append((value,digest));return key
    def check_retained(self):
        for value,digest in self.oracle_guards:fault(bounded_builtin(value,self.limits)==digest,'ORACLE_VALUE_MUTATED')
    def open_call(self,observer,obj,operation,request):
        ctx=self.context();thread=ctx['thread_ref'];stack=self.stacks.setdefault(thread,[]);fault(len(stack)<self.limits['depth'],'CAUSAL_FIELD_BUDGET');key=self.ref('C')
        row=dict(schema=self.spec['causal_call']['schema'],**ctx,call_ref=key,parent_call_ref=stack[-1] if stack else None,authority='OBSERVED_PARENT_RETURN',observer_id=observer,object_ref=self.object_ref(obj),domain_ref=None,input_ref=dict(test_id=self.frame['test_id'],frame_id=self.frame['test_frame_id'],worker_context_ref='/worker_context',inputs_ref='/runner_inputs_before',source_binding_ref='FRAME_SOURCE_BINDING'),operation=operation,request=request,output=None,exception=None,outcome=None)
        stack.append(key);self.calls[key]=row;return key
    def close_call(self,key,out=None,exception=None,publish=True):
        row=self.calls[key];stack=self.stacks[row['thread_ref']];fault(stack and stack[-1]==key,'CAUSAL_LINK_AMBIGUOUS');stack.pop()
        row.update(output=out,exception=exception,outcome='EXCEPTION' if exception is not None else 'RETURN')
        self.row_budget(row)
        if publish:self.emit('CAUSAL_TERMINAL',causal=row)
        return row
    def link(self,source,target,relation,domain=None):
        ctx=self.context();key=self.ref('L');self.charge(2)
        row=dict(schema='d5.causal-capture-link.v1',**ctx,source_ref=source,target_ref=target,relation=relation,domain_ref=domain)
        self.tables['causal_links'][key]=row;self.row_budget(row);return key
    def register(self,process,connection,identity,action,inp,point=None):
        fault(type(process) is multiprocessing.context.SpawnProcess and type(connection) is multiprocessing.connection.Connection,'UNSUPPORTED_CAUSAL_API')
        fault(token(action) and (point is None or token(point)),'UNSUPPORTED_PROTOCOL_MESSAGE');ctx=self.context();key=self.ref('P')
        row=dict(schema=self.spec['protocol']['schema'],capture_run_id=self.run_id,test_frame_id=ctx['test_frame_id'],subcase_ref=ctx['subcase_ref'],parent_intent_ref=key,process_ref=self.object_ref(process),connection_ref=self.object_ref(connection),domain_refs=identity,action=action,input_digest=bounded_builtin(inp,self.limits),expected_point=point,observed_messages=[],exit_observations=[])
        self.tables['protocol_instances'][key]=row;self.row_budget(row);return key
    def protocol_for(self,obj,field):
        for old,key in self.objects:
            if old is obj:
                rows=[(ref,row) for ref,row in self.tables['protocol_instances'].items() if row[field]==key]
                fault(len(rows)<=1,'CAUSAL_LINK_AMBIGUOUS');return rows[0] if rows else None
        return None
    def message(self,obj,value):
        found=self.protocol_for(obj,'connection_ref')
        if found is None:return False
        key,row=found;message=None
        if type(value) is str and value in PROTOCOL_POINTS:message=dict(kind='READY',point=value,authority='CHILD_PROTOCOL_RETURN')
        elif type(value) is tuple and len(value)==2 and type(value[0]) is str:
            kind,data=value
            if kind=='READY' and type(data) is str and data in PROTOCOL_POINTS:message=dict(kind=kind,point=data,authority='CHILD_PROTOCOL_RETURN')
            elif kind=='ERROR' and type(data) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,79}',data):message=dict(kind=kind,code=data,authority='CHILD_PROTOCOL_RETURN')
            elif kind=='OK':
                message=dict(kind=kind,value_digest=bounded_builtin(data,self.limits),authority='CHILD_PROTOCOL_RETURN',command_identity='CHILD_LOCAL_NOT_OBSERVED')
                if type(data) is dict and data.get('schema')=='d5.durable-receipt.v1':message['receipt']=store_receipt(data,self.spec,self.limits)
                elif type(data) is dict and data.get('schema')=='d5.fixture-drive-receipt.v1':message['receipt']=drive_receipt(data,self.spec)
                if 'receipt' in message:message['command_identity']='OBSERVED_PROTOCOL_RECEIPT'
        elif type(value) is dict and type(value.get('schema')) is str and value['schema']=='d5.fixture-drive-snapshot.v1':
            fault(t.uuid_value(value.get('run_id')) and integer(value.get('version')) and sha_value(value.get('head_sha256')),'UNSUPPORTED_PROTOCOL_MESSAGE')
            message=dict(kind='DRIVE_SNAPSHOT',run_id=value['run_id'],version=value['version'],head_sha256=value['head_sha256'],value_digest=bounded_builtin(value,self.limits),authority='CHILD_PROTOCOL_RETURN')
        fault(message is not None,'UNSUPPORTED_PROTOCOL_MESSAGE');self.charge();row['observed_messages'].append(message);self.row_budget(row);return True
    def exit(self,obj,code=None,direct=False):
        found=self.protocol_for(obj,'process_ref')
        if found is None:return False
        key,row=found
        if direct:
            fault(type(obj) is multiprocessing.context.SpawnProcess,'UNSUPPORTED_CAUSAL_API');popen=object.__getattribute__(obj,'__dict__').get('_popen')
            fault(type(popen) is multiprocessing.popen_spawn_posix.Popen,'UNSUPPORTED_CAUSAL_API');code=object.__getattribute__(popen,'__dict__').get('returncode')
        fault(code is None or type(code) is int and -255<=code<=255,'UNSUPPORTED_PROTOCOL_MESSAGE');self.charge()
        row['exit_observations'].append(dict(status='PENDING_PROCESS_EXIT' if code is None else 'OBSERVED_PARENT_RETURN',returncode=code));self.row_budget(row)
        if code is None:self.invalid('PENDING_CHILD_EXIT')
        return True


class Recorder(late.Recorder):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.causal=CausalState(self.run_id,self.limits,self.profile['projection_schemas'],self.reference,self.emit,self.invalid);self.causal.external_owner=self.owner;self.causal_inventory={r['test_id']:r for r in self.profile['inventory']};self.causal_test=None;self.causal_bindings=[];self.causal_records=[];self.causal_exception_types={};self.record_snapshots={};self.causal_sources={};self.causal_deferred=[]
    def attempt(self,fn,*args,**kwargs):
        try:return fn(*args,**kwargs)
        except BaseException as ex:self.invalid(ex.code if type(ex) is c.CaptureFault else 'CAUSAL_SCHEMA_INVALID');return None
    def start(self,test):
        self.causal_test=test;super().start(test)
        if self.active:
            self.attempt(self.causal.begin,self.active,test)
            if self.causal_enabled():self.attempt(self.bind_deferred)
    def emit(self,kind,**data):
        if getattr(self,'causal',None) is not None and self.active and self.causal.frame is self.active and kind in ('ASSERTION_RETURNED','ASSERTION_RAISED','EXPECTED_EXCEPTION_DECLARED','EXPECTED_EXCEPTION_EXIT_OBSERVED','TEST_RESULT'):
            ctx=self.attempt(self.causal.context)
            if ctx:
                data.update(causal_context=ctx)
                row=self.causal.tables['subcases'][ctx['subcase_ref']]
                if kind=='TEST_RESULT':self.reference();row['result_refs'].append(len(self.events))
        return super().emit(kind,**data)
    def exception(self,ex):
        if isinstance(ex,OSError):return dict(kind='OS_ERROR',code='OS_ERROR')
        for ref,cls in self.causal_exception_types.items():
            if type(ex) is cls:
                args=BaseException.args.__get__(ex,type(ex));fault(type(args) is tuple and len(args)==1 and type(args[0]) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,79}',args[0]),'COMMAND_HEADER_INVALID');return dict(kind=ref,code=args[0])
        fault(False,'COMMAND_HEADER_INVALID')
    def causal_enabled(self):return self.active is not None and self.active['test_id'] in self.causal_inventory
    def wrap_boundary(self,owner,name,observer):
        old=owner.__dict__.get(name);fault(type(old) is types.FunctionType,'UNSUPPORTED_CAUSAL_API');signature=inspect.signature(old,eval_str=False);rec=self
        @functools.wraps(old)
        def wrapped(*args,**kwargs):
            if not rec.causal_enabled():return old(*args,**kwargs)
            key=None;request=None;pre=None;negative=None
            try:
                bound=signature.bind(*args,**kwargs);bound.apply_defaults();b=dict(bound.arguments);obj=b.get('self',owner)
                if observer in ('Store.transact','FixtureStore.advance'):
                    try:request=store_request(b,rec.limits) if observer=='Store.transact' else drive_request(b.get('value'),rec.limits)
                    except c.CaptureFault as failure:
                        candidate=rec.profile.get('negative_input_selectors',{}).get(rec.active['test_id'])
                        fault(candidate is not None and observer in candidate['methods'] and failure.code in candidate['input_failures'],'COMMAND_HEADER_INVALID')
                        negative=candidate;request=dict(status='INVALID_INPUT_EXPECTED_NEGATIVE',reason=failure.code,request_sha256=None,input_digest=c.digest_value({k:v for k,v in b.items() if k!='self'},rec.limits))
                elif name=='perform':request=dict(args_digest=bounded_builtin({k:v for k,v in b.items() if k!='self'},rec.limits))
                elif name=='independent':
                    vals=owner.__dict__.get('ORACLES');fault(type(vals) is list,'ORACLE_VALUE_MISSING');pre=(vals,len(vals),[bounded_builtin(v,rec.limits) for v in vals]);request=dict(kind='ORIGINAL_HARNESS_ORACLE')
                elif name=='start':request=dict(action=b['action'],point=b.get('point'),role=b.get('role','CLIENT'));obj=b['lab']
                elif name=='spawn':request=dict(action='Drive.advance',point=b.get('fault'));obj=b['self']
                else:request=dict(kind='ORIGINAL_HARNESS_PROTOCOL')
                key=rec.causal.open_call(observer,obj,name,request)
            except BaseException as ex:
                # No generic negative exemption: unknown metadata is explicitly incomplete.
                rec.invalid(ex.code if type(ex) is c.CaptureFault else 'COMMAND_HEADER_INVALID')
            try:out=old(*args,**kwargs)
            except BaseException as ex:
                if key is not None:
                    projection=rec.attempt(rec.exception,ex) or dict(kind='NOT_OBSERVED_REQUIRED')
                    if negative is not None and projection.get('code') not in negative['exception_codes']:rec.invalid('COMMAND_HEADER_INVALID')
                    rec.attempt(rec.causal.close_call,key,exception=projection)
                raise
            if key is not None:
                try:
                    fault(negative is None,'COMMAND_HEADER_INVALID')
                    projected=None if name in ('start','spawn','independent') else dict(result_digest=bounded_builtin(out,rec.limits))
                    if observer=='Store.transact':projected=store_receipt(out,rec.profile['projection_schemas'],rec.limits)
                    elif observer=='FixtureStore.advance':projected=drive_receipt(out,rec.profile['projection_schemas'])
                    if observer in ('Store.transact','FixtureStore.advance'):
                        fault(projected['command_id']==request['command_id'] and projected['request_sha256']==request['request_sha256'],'REQUEST_HASH_CONFLICT')
                    if name=='independent':
                        vals,n,digests=pre;fault(owner.__dict__.get('ORACLES') is vals and len(vals)>=n and all(bounded_builtin(v,rec.limits)==h for v,h in zip(vals[:n],digests)),'ORACLE_VALUE_MUTATED')
                        fault(type(out) is dict and type(out.get('head')) is dict,'ORACLE_VALUE_MISSING');head=out['head'];domain=rec.causal.domain(head);retained=[]
                        for i in range(n,len(vals)):
                            v=vals[i];kind='R' if 'entities' in v else 'T';hk='head_sha256' if kind=='R' else 'commit_sha256'
                            fault(type(v) is dict and v.get('case')==owner.__dict__.get('CURRENT_CASE') and v.get('store_id')==head.get('store_id') and v.get('seq')==head.get('seq') and v.get(hk)==head.get('commit_sha256'),'CAUSAL_LINK_AMBIGUOUS')
                            retained.append(rec.causal.retain(owner.__name__,i,v,kind,out,key))
                        projected=dict(authority='RETAINED_HARNESS_ORACLE',head={k:head[k] for k in ('run_id','store_id','role','seq','commit_sha256')},retained_refs=retained,commit=oracle_commit(out,rec.profile['projection_schemas'],rec.limits))
                        rec.causal_sources[owner.__name__]=(owner,vals,bounded_builtin(vals,rec.limits))
                        for ref in retained:
                            rec.causal.link(key,ref,'RETURN_RETAINS_ORACLE',domain)
                            commit=projected['commit']
                            if commit['kind']=='COMMAND':
                                for command_ref,call in rec.causal.calls.items():
                                    output=call.get('output')
                                    if call['test_frame_id']==rec.active['test_frame_id'] and call['subcase_ref']==rec.causal.subcase() and call.get('domain_ref')==domain and type(output) is dict and output.get('schema')=='d5.store-receipt-projection.v1' and all(output.get(k)==commit['receipt'][k] for k in ('command_id','request_sha256','seq')):
                                        rec.causal.link(command_ref,ref,'COMMAND_RECEIPT_ORACLE_COMMIT',domain)
                    elif name in ('start','spawn'):
                        fault(type(out) is tuple and len(out)==2,'UNSUPPORTED_CAUSAL_API');lab=b.get('lab')
                        if lab is None:lab=object.__getattribute__(b['self'],'__dict__').get('lab')
                        fault(lab is not None,'ORACLE_DOMAIN_IDENTITY_MISSING')
                        allowed=[]
                        for module_name,class_name in [('source_ingest.durable_task_fixture','DurableLab'),('source_ingest.durable_relational_fixture','RelationalLab'),('source_ingest.incremental_fixture','TemporaryFixtureLab')]:
                            loaded=sys.modules.get(module_name)
                            if type(loaded) is types.ModuleType:allowed.append(loaded.__dict__.get(class_name))
                        fault(type(lab) in allowed,'UNSUPPORTED_CAUSAL_API');mem=object.__getattribute__(lab,'__dict__');identity={k:mem[k] for k in ('run_id','client_id','remote_id') if k in mem}
                        fault(t.uuid_value(identity.get('run_id')) and all(t.uuid_value(v) for v in identity.values()),'ORACLE_DOMAIN_IDENTITY_MISSING')
                        intent=rec.causal.register(out[0],out[1],identity,request['action'],b.get('args',b.get('req')),request['point']);projected=dict(parent_intent_ref=intent,command_identity='CHILD_LOCAL_NOT_OBSERVED')
                    elif name=='finish':rec.causal.exit(b['p'],out);projected=dict(returncode=out)
                    elif name=='receive':projected=dict(authority='CHILD_PROTOCOL_RETURN',registered=rec.causal.protocol_for(b.get('conn',b.get('c')),'connection_ref') is not None)
                    if observer=='Store.transact':
                        declaration=rec.declarations.get(rec.owner(obj,None))
                        if declaration:rec.causal.calls[key]['domain_ref']=rec.causal.declaration(obj,{k:declaration[k] for k in ('run_id','store_id','role')})
                    if observer=='Store.transact':fault(store_request(b,rec.limits)==request,'REQUEST_HASH_CONFLICT')
                    elif observer=='FixtureStore.advance':
                        fault(drive_request(b.get('value'),rec.limits)==request,'REQUEST_HASH_CONFLICT')
                        ref=rec.owner(obj,None)
                        if ref in rec.drive_identities:rec.causal.calls[key]['domain_ref']=ref
                    row=rec.causal.close_call(key,out=projected)
                    if row['parent_call_ref']:rec.causal.link(row['parent_call_ref'],key,'SAME_THREAD_NESTED_CALL')
                except BaseException as ex:rec.invalid(ex.code if type(ex) is c.CaptureFault else 'CAUSAL_SCHEMA_INVALID')
            return out
        self.patch(owner,name,wrapped)
    def wrap_return(self,cls,name):
        if name!='perform':return super().wrap_return(cls,name)
        old=cls.__dict__.get(name);fault(type(old) is types.FunctionType,'UNSUPPORTED_CAUSAL_API');rec=self
        @functools.wraps(old)
        def observed(obj,*args,**kwargs):
            key=None
            if rec.causal_enabled():
                try:key=rec.causal.open_call(cls.__name__+'.perform',obj,'perform',dict(args_digest=bounded_builtin((args,kwargs),rec.limits)))
                except BaseException as ex:rec.invalid(ex.code if type(ex) is c.CaptureFault else 'CAUSAL_SCHEMA_INVALID')
            try:out=old(obj,*args,**kwargs)
            except BaseException as ex:
                data={}
                if key is not None:data['causal']=rec.attempt(rec.causal.close_call,key,exception=rec.attempt(rec.exception,ex) or dict(kind='NOT_OBSERVED_REQUIRED'),publish=False)
                rec.emit('CALL_EXCEPTION',method='perform',exception_type=type(ex).__name__,**data);raise
            data={}
            if key is not None:
                try:data['causal']=rec.causal.close_call(key,out=dict(result_digest=bounded_builtin(out,rec.limits)),publish=False)
                except BaseException as ex:rec.invalid(ex.code if type(ex) is c.CaptureFault else 'CAUSAL_SCHEMA_INVALID')
            try:rec.emit('CALL_RETURN',method='perform',owner_ref=rec.owner(obj,out),result_digest=c.digest_value(out,rec.limits),**data)
            except BaseException as ex:rec.invalid(ex.code if type(ex) is c.CaptureFault else 'CAUSAL_SCHEMA_INVALID')
            return out
        self.patch(cls,name,observed)
    def bind_causal_target(self,spec,lookup=None):
        mod,cls,name,obs=spec;lookup=sys.modules.get if lookup is None else lookup;module=lookup(mod);fault(type(module) is types.ModuleType,'UNSUPPORTED_CAUSAL_API');owner=module.__dict__.get(cls) if cls else module
        fault(owner is not None,'UNSUPPORTED_CAUSAL_API')
        anchors=[a for a in self.profile['source_anchors'] if a['owner']==(cls or name) and a['method']==(name if cls else None)]
        fn=owner.__dict__.get(name);fault(type(fn) is types.FunctionType,'UNSUPPORTED_CAUSAL_API')
        matches=[a for a in anchors if Path(fn.__code__.co_filename).resolve()==(ROOT/a['path']).resolve()]
        fault(len(matches)==1,'UNSUPPORTED_CAUSAL_API');a=matches[0];fault(fn.__name__==name and fn.__code__.co_firstlineno==a['line'],'UNSUPPORTED_CAUSAL_API');fault(c.sha(self.projector.bindings.reader.read(a['path']))==a['sha256'],'STALE_OBSERVER_SOURCE')
        self.wrap_boundary(owner,name,obs)
    def bind_deferred(self,lookup=None):
        for spec in tuple(self.causal_deferred):
            self.bind_causal_target(spec,lookup);self.causal_deferred.remove(spec)
    def install_causal(self):
        observed=stdlib_description();pins=self.profile['stdlib_bindings'];fault(all(observed[k]==pins[k] for k in observed),'STDLIB_BINDING_CHANGED')
        # Only already loaded exact source-bound symbols. No discovery/imports here.
        rows=[]
        for mod,cls,name,obs in [('source_ingest.durable_store','Store','transact','Store.transact'),('source_ingest.incremental_fixture','FixtureStore','advance','FixtureStore.advance'),('testing.D5.durable_support',None,'independent','T.independent'),('testing.D5.relational_support',None,'independent','R.independent')]:rows.append((mod,cls,name,obs))
        for mod in ('testing.D5.durable_support','testing.D5.relational_support'):
            rows.extend((mod,None,name,mod+'.'+name) for name in ('start','receive','finish'))
        rows.append(('test_incremental_capture','IncrementalCaptureTest','spawn','Drive.spawn'))
        for spec in rows:
            if spec[0]=='test_incremental_capture' and sys.modules.get(spec[0]) is None:self.causal_deferred.append(spec)
            else:self.bind_causal_target(spec)
        for mod,name in [('source_ingest.durable_store','DurableError'),('source_ingest.incremental_fixture','IncrementalError')]:
            module=sys.modules.get(mod);cls=module.__dict__.get(name);fault(type(cls) is type and cls.__bases__==(ValueError,),'UNSUPPORTED_CAUSAL_API');self.causal_exception_types[mod+'.'+name]=cls
        rec=self
        callback=unittest.TestResult.__dict__['addSubTest']
        @functools.wraps(callback)
        def addsub(result,test,subtest,err):
            if rec.causal_enabled():
                actual=object.__getattribute__(test,'__dict__').get('_subtest')
                if test is not rec.causal_test or actual is not subtest:rec.invalid('UNSUPPORTED_SUBCASE_BINDING')
                else:rec.attempt(rec.causal.subcase,subtest)
            return callback(result,test,subtest,err)
        self.patch(unittest.TestResult,'addSubTest',addsub)
        cls=multiprocessing.connection._ConnectionBase;old=cls.__dict__['recv']
        @functools.wraps(old)
        def recv(obj):
            out=old(obj)
            if rec.causal_enabled():rec.attempt(rec.causal.message,obj,out)
            return out
        self.patch(cls,'recv',recv);cls=multiprocessing.process.BaseProcess;join=cls.__dict__['join']
        @functools.wraps(join)
        def joined(obj,*args,**kwargs):
            out=join(obj,*args,**kwargs)
            if rec.causal_enabled():rec.attempt(rec.causal.exit,obj,direct=True)
            return out
        self.patch(cls,'join',joined)
    def constructor(self,cls):
        super().constructor(cls)
        original=cls.__dict__['__init__'];sig=inspect.signature(original,eval_str=False);rec=self
        @functools.wraps(original)
        def observed(obj,*args,**kwargs):
            out=original(obj,*args,**kwargs)
            if rec.causal_enabled():
                try:
                    bound=sig.bind(obj,*args,**kwargs).arguments
                    rec.causal.declaration(obj,{k:bound[k] for k in ('run_id','store_id','role')})
                except BaseException as ex:rec.invalid(ex.code if type(ex) is c.CaptureFault else 'CAUSAL_SCHEMA_INVALID')
            return out
        self.patch(cls,'__init__',observed)
    def owner(self,obj,out):
        ref=super().owner(obj,out)
        if self.causal_enabled() and type(out) is dict and type(out.get('head')) is dict:
            h=out['head']
            if all(k in h for k in ('run_id','store_id','role')):self.attempt(self.causal.declaration,obj,{k:h[k] for k in ('run_id','store_id','role')})
        return ref
    def stop(self,test,result):
        frame=self.active
        if frame and self.causal_enabled():
            self.attempt(self.causal.check_retained)
            row=self.causal_inventory[frame['test_id']]
            # Source-only direct child construction has no permitted registration boundary.
            if frame['test_id'].endswith('test_DI07_fresh_process_recovers_state_from_disk'):
                frame['missing'].append('UNREGISTERED_CHILD_PROTOCOL_REQUIRED');self.invalid('CAUSAL_LINK_MISSING')
            if row['classification']=='CAUSAL_DOMAIN':
                refs=[r for r in self.causal.tables['retained_oracles'].values() if r['test_frame_id']==frame['test_frame_id']]
                if row['family'] in ('T','R') and not refs:frame['missing'].append('ORACLE_VALUE_MISSING')
            if any(self.causal.stacks.values()):frame['missing'].append('CAUSAL_LINK_MISSING');self.invalid('CAUSAL_LINK_MISSING')
            for protocol in self.causal.tables['protocol_instances'].values():
                if protocol['test_frame_id']!=frame['test_frame_id']:continue
                if not protocol['exit_observations'] or protocol['exit_observations'][-1]['returncode'] is None:frame['missing'].append('PENDING_CHILD_EXIT')
                for message in protocol['observed_messages']:
                    if message['kind']=='OK' and message.get('command_identity')=='CHILD_LOCAL_NOT_OBSERVED' and protocol['action'] not in ('snapshot','initialize'):frame['missing'].append('UNOBSERVED_CHILD_COMMAND')
        super().stop(test,result);self.causal.frame=None;self.causal.test=None
    def finish(self,raw=None):
        self.attempt(self.causal.check_retained)
        for module,values,digest in self.causal_sources.values():
            if module.__dict__.get('ORACLES') is not values or c.digest_value(values,self.limits)!=digest:self.invalid('ORACLE_VALUE_MUTATED')
        out=super().finish(raw);out.update(schema=NORMAL_SCHEMA,semantic_baseline=dict(SUPPORTS_BOUNDED=83,PARTIAL=1),shared_reference_count=self.references,**self.causal.tables)
        for row in out['retained_oracles'].values():
            f=next(f for f in out['frames'] if f['test_frame_id']==row['test_frame_id']);links=[b for b in f['record_links'] if (b['module'],b['field'],b['index'])==(row['source_module'],row['source_field'],row['source_index'])]
            if len(links)!=1 or links[0]['digest']!=row['value_digest']:self.invalid('ORACLE_VALUE_MISSING')
            else:
                key=next(k for k,v in out['retained_oracles'].items() if v is row);links[0]['sidecar_pointer']='/retained_oracles/'+key+'/value'
        out['errors']=list(self.errors)
        if self.errors:out['status']='INVALID_CAPTURE'
        elif any(f['missing'] for f in out.get('frames',[])):out['status']='INCOMPLETE_CAPTURE'
        if len(encode(out))>self.limits['index_sidecar_bytes']:return dict(schema=NORMAL_SCHEMA,status='INVALID_CAPTURE',errors=['SIDECAR_BUDGET'],closure=False)
        return out


def validate_causal(side,profile,limits=None):
    lim=dict(LIMITS,**(limits or {}));spec=profile['projection_schemas'];fault(side.get('schema')==NORMAL_SCHEMA,'CAUSAL_SCHEMA_INVALID')
    fault(len(encode(side))<=lim['index_sidecar_bytes'],'SIDECAR_BUDGET');frames={r['test_frame_id']:r for r in side['frames']};nodes={};refs=0
    for table in ('retained_oracles','subcases','protocol_instances','causal_links'):
        rows=side.get(table);fault(type(rows) is dict,'CAUSAL_SCHEMA_INVALID');refs+=len(rows)
        for key,row in rows.items():
            fault(type(key) is str and key not in nodes and type(row) is dict and len(encode(row))<=4096,'CAUSAL_SCHEMA_INVALID');nodes[key]=row
            fault(row.get('capture_run_id')==side['capture_run_id'] and row.get('test_frame_id') in frames,'CAUSAL_LINK_MISSING')
            expected_schema={'retained_oracles':spec['retained_oracle']['schema'],'subcases':spec['subcase']['schema'],'protocol_instances':spec['protocol']['schema'],'causal_links':'d5.causal-capture-link.v1'}[table]
            fault(row.get('schema')==expected_schema,'CAUSAL_SCHEMA_INVALID')
            if table=='causal_links':fault(set(row)=={'schema','capture_run_id','test_frame_id','subcase_ref','thread_ref','source_ref','target_ref','relation','domain_ref'},'CAUSAL_SCHEMA_INVALID')
            sub=row.get('subcase_ref');fault(sub in side['subcases'] and side['subcases'][sub]['test_frame_id']==row['test_frame_id'],'CAUSAL_LINK_MISSING')
            if table=='retained_oracles':
                fault(set(row)==set(spec['retained_oracle']['keys']),'CAUSAL_SCHEMA_INVALID');fault(type(row['source_index']) is int and 0<=row['source_index']<lim['refs'] and row['source_field']=='ORACLES','CAUSAL_SCHEMA_INVALID');v,h=oracle_value(row['value'],row['oracle_kind'],spec,lim);fault(h==row['value_digest'],'ORACLE_VALUE_MUTATED')
                f=frames[row['test_frame_id']];bindings=[b for b in f['record_links'] if (b['module'],b['field'],b['index'])==(row['source_module'],row['source_field'],row['source_index'])]
                fault(len(bindings)==1 and bindings[0]['digest']==h and bindings[0].get('sidecar_pointer')=='/retained_oracles/'+key+'/value','ORACLE_VALUE_MISSING')
                domain=row['domain_ref'];fault(domain in f.get('owner_context_refs',[]) and domain in side.get('owner_contexts',{}),'ORACLE_DOMAIN_IDENTITY_MISSING')
                identity=side['owner_contexts'][domain].get('identity');declaration=side.get('construction_declarations',{}).get(domain)
                fault((type(identity) is dict and identity.get('store_id')==v['store_id'] or type(declaration) is dict and declaration.get('store_id')==v['store_id'] and declaration.get('role')==v['role']),'ORACLE_DOMAIN_IDENTITY_MISSING')
            elif table=='subcases':
                fault(set(row)==set(spec['subcase']['keys']) and row['kind'] in spec['subcase']['kinds'] and key==row['subcase_ref'],'UNSUPPORTED_SUBCASE_BINDING')
                for k,v in row['params'].items():fault(k in spec['subcase']['param_keys'] and (v is None or type(v) is bool or integer(v) or token(v)),'UNSUPPORTED_SUBCASE_BINDING')
            elif table=='protocol_instances':
                fault(set(row)==set(spec['protocol']['keys']),'CAUSAL_SCHEMA_INVALID')
                fault(type(row['observed_messages']) is list and type(row['exit_observations']) is list,'CAUSAL_SCHEMA_INVALID')
                identity=row['domain_refs'];fault(type(identity) is dict and 'run_id' in identity and set(identity)<={'run_id','client_id','remote_id'} and all(t.uuid_value(v) for v in identity.values()),'ORACLE_DOMAIN_IDENTITY_MISSING')
                for message in row['observed_messages']:
                    fault(type(message) is dict and message.get('kind') in spec['protocol']['message_kinds'] and message.get('authority')=='CHILD_PROTOCOL_RETURN','UNSUPPORTED_PROTOCOL_MESSAGE')
                    kind=message['kind']
                    if kind=='READY':fault(set(message)=={'kind','point','authority'} and type(message['point']) is str and message['point'] in PROTOCOL_POINTS,'UNSUPPORTED_PROTOCOL_MESSAGE')
                    elif kind=='ERROR':fault(set(message)=={'kind','code','authority'} and type(message['code']) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,79}',message['code']),'UNSUPPORTED_PROTOCOL_MESSAGE')
                    elif kind=='DRIVE_SNAPSHOT':fault(set(message)=={'kind','run_id','version','head_sha256','value_digest','authority'} and t.uuid_value(message['run_id']) and integer(message['version']) and sha_value(message['head_sha256']),'UNSUPPORTED_PROTOCOL_MESSAGE')
                    else:fault(set(message) in ({'kind','value_digest','authority','command_identity'},{'kind','value_digest','authority','command_identity','receipt'}) and message['command_identity'] in ('CHILD_LOCAL_NOT_OBSERVED','OBSERVED_PROTOCOL_RECEIPT'),'UNSUPPORTED_PROTOCOL_MESSAGE')
                for exit in row['exit_observations']:
                    fault(type(exit) is dict and set(exit)=={'status','returncode'} and (exit['status']=='PENDING_PROCESS_EXIT' and exit['returncode'] is None or exit['status']=='OBSERVED_PARENT_RETURN' and type(exit['returncode']) is int),'CAUSAL_SCHEMA_INVALID')
    shared=side.get('shared_reference_count',refs);fault(type(shared) is int and refs<=shared<=lim['refs'],'REFERENCE_BUDGET')
    # References to event calls are resolved by the streaming page reader below.
    return dict(status='CAUSAL_TABLES_VERIFIED',rows=refs)


def validate_pages(reader,prefix,side,limits=None,profile=None):
    base=late.validate_pages(reader,prefix,side,limits,profile);tables=validate_causal(side,profile,limits)
    calls={};contexts={};events={};spec=profile['projection_schemas'];lim=dict(LIMITS,**(limits or {}))
    for page in side['pages']:
        for event in c.strict_json(reader.read(prefix+'/'+page['name']))['events']:
            fault(len(events)<lim['events_campaign'],'EVENT_CAMPAIGN_BUDGET');events[event['sequence']]=event
            if event.get('causal') is not None:
                row=event.get('causal');fault(type(row) is dict and set(row)==set(spec['causal_call']['keys']),'CAUSAL_SCHEMA_INVALID');key=row['call_ref'];fault(key not in calls,'CAUSAL_LINK_AMBIGUOUS');calls[key]=row
                fault(row['capture_run_id']==side['capture_run_id'] and row['test_frame_id']==event['test_frame_id'] and row['subcase_ref'] in side['subcases'],'CAUSAL_LINK_MISSING')
            ctx=event.get('causal_context')
            if ctx:fault(ctx['test_frame_id']==event['test_frame_id'] and ctx['capture_run_id']==side['capture_run_id'] and ctx['subcase_ref'] in side['subcases'],'CAUSAL_LINK_MISSING');contexts[event['sequence']]=ctx
    for key,row in calls.items():
        validate_call_header(row,spec)
        parent=row['parent_call_ref'];p=parent
        if p:
            fault(p in calls and all(calls[p][k]==row[k] for k in ('capture_run_id','test_frame_id','subcase_ref','thread_ref')),'CAUSAL_LINK_MISSING')
            visited={key};cursor=p
            while cursor:
                fault(cursor not in visited and len(visited)<=lim['depth'],'CAUSAL_LINK_AMBIGUOUS');visited.add(cursor);cursor=calls[cursor]['parent_call_ref']
    for key,row in side['retained_oracles'].items():fault(row['oracle_return_ref'] in calls and calls[row['oracle_return_ref']]['output'].get('retained_refs',[]).count(key)==1,'CAUSAL_LINK_MISSING')
    seen_links=set()
    for key,row in side['causal_links'].items():
        signature=(row['source_ref'],row['target_ref'],row['relation']);fault(signature not in seen_links,'CAUSAL_LINK_AMBIGUOUS');seen_links.add(signature)
        fault(row['source_ref'] in calls and row['target_ref'] in (calls|side['retained_oracles']),'CAUSAL_LINK_MISSING');a=calls[row['source_ref']];b=(calls|side['retained_oracles'])[row['target_ref']]
        fault(all(a[k]==b[k]==row[k] for k in ('capture_run_id','test_frame_id','subcase_ref')),'CAUSAL_LINK_AMBIGUOUS')
        relation=row['relation']
        if relation=='SAME_THREAD_NESTED_CALL':fault(b.get('parent_call_ref')==row['source_ref'] and b.get('thread_ref')==a.get('thread_ref'),'CAUSAL_LINK_AMBIGUOUS')
        elif relation=='RETURN_RETAINS_ORACLE':fault(b.get('oracle_return_ref')==row['source_ref'],'CAUSAL_LINK_AMBIGUOUS')
        elif relation=='COMMAND_RECEIPT_ORACLE_COMMIT':
            oracle=calls[b['oracle_return_ref']]['output'];receipt=oracle.get('commit',{}).get('receipt',{});output=a.get('output',{})
            fault(type(output) is dict and output.get('schema')=='d5.store-receipt-projection.v1' and a['domain_ref']==b['domain_ref']==row['domain_ref'] and all(output.get(k)==receipt.get(k) for k in ('command_id','request_sha256','seq')),'REQUEST_HASH_CONFLICT')
        else:fault(False,'CAUSAL_SCHEMA_INVALID')
    for key,row in side['subcases'].items():
        for seq in row['result_refs']:fault(seq in contexts and contexts[seq]['subcase_ref']==key and events[seq]['event']=='TEST_RESULT','CAUSAL_LINK_MISSING')
    return dict(**base,causal=tables,causal_calls=len(calls))


def validate_call_header(row,spec):
    fault(row['authority']=='OBSERVED_PARENT_RETURN' and row['outcome'] in ('RETURN','EXCEPTION'),'CAUSAL_SCHEMA_INVALID')
    if row['outcome']=='EXCEPTION':
        exception=row['exception'];fault(type(exception) is dict and row['output'] is None and set(exception)=={'kind','code'} and type(exception['code']) is str and re.fullmatch('[A-Z][A-Z0-9_]{0,79}',exception['code']),'COMMAND_HEADER_INVALID');return
    fault(row['exception'] is None,'CAUSAL_SCHEMA_INVALID')
    request=row['request'];output=row['output'];observer=row['observer_id']
    if observer=='Store.transact':
        fault(type(request) is dict and set(request)=={'hash_namespace','command_id','kind','expected','args_digest','request_sha256'} and request.get('hash_namespace')=='STORE_REQUEST' and t.uuid_value(request.get('command_id')) and sha_value(request.get('request_sha256')),'COMMAND_HEADER_INVALID')
        fault(type(output) is dict and set(output)==set(spec['receipt_store']['required_fields']) and output['schema']==spec['receipt_store']['schema'] and output['source_schema']=='d5.durable-receipt.v1','COMMAND_HEADER_INVALID')
        fault(output['command_id']==request['command_id'] and output['request_sha256']==request['request_sha256'],'REQUEST_HASH_CONFLICT')
        fault(all(sha_value(output[k]) for k in ('request_sha256','before_state_sha256','after_data_sha256')) and all(integer(output[k]) for k in ('seq','before_seq')) and type(output['historical']) is bool,'COMMAND_HEADER_INVALID')
        fault(output['grants_execution_authority'] is False and output['activation_allowed'] is False and type(output['quota_consumed']) is int and output['quota_consumed']==0 and type(output['reservations_created']) is int and output['reservations_created']==0,'COMMAND_HEADER_INVALID')
        fault(selectors(output['result_metadata'],spec['metadata_selectors'])==output['result_metadata'],'COMMAND_HEADER_INVALID')
    elif observer=='FixtureStore.advance':
        fault(type(request) is dict and set(request)=={'hash_namespace','schema','command_id','expected_version','expected_head','request_sha256','input_bytes_sha256'} and request.get('hash_namespace')=='DRIVE_REQUEST' and type(output) is dict and output.get('schema')==spec['receipt_drive']['schema'],'COMMAND_HEADER_INVALID')
        fault(output.get('command_id')==request.get('command_id') and output.get('request_sha256')==request.get('request_sha256'),'REQUEST_HASH_CONFLICT')
        raw={k:v for k,v in output.items() if k not in ('schema','source_schema')};raw['schema']=output['source_schema'];fault(drive_receipt(raw,spec)==output,'COMMAND_HEADER_INVALID')


def oracle_commit(returned,spec,limits=None):
    chain=returned.get('chain');fault(type(chain) is list and bool(chain),'ORACLE_VALUE_MISSING');last=chain[-1]
    fault(type(last) is dict and all(k in last for k in ('seq','command_id','request_sha256','operation','receipt')),'ORACLE_VALUE_MISSING')
    head=returned['head'];fault(last['seq']==head['seq'] and integer(last['seq']),'ORACLE_VALUE_MISSING')
    op=last['operation'];fault(type(op) is dict and set(op)=={'kind','args','expected'},'ORACLE_VALUE_MISSING')
    if last['seq']==0:
        fault(last['command_id'] is None and last['receipt'] is None and op['kind']=='GENESIS','ORACLE_VALUE_MISSING')
        return dict(authority='RETAINED_HARNESS_ORACLE',kind='GENESIS',seq=0,commit_sha256=head['commit_sha256'])
    request=store_request(dict(cid=last['command_id'],**op),limits)
    fault(last['request_sha256']==request['request_sha256'],'REQUEST_HASH_CONFLICT')
    receipt=store_receipt(dict(last['receipt'],historical=False),spec,limits)
    fault(receipt['command_id']==request['command_id'] and receipt['request_sha256']==request['request_sha256'] and receipt['seq']==head['seq'],'REQUEST_HASH_CONFLICT')
    return dict(authority='RETAINED_HARNESS_ORACLE',kind='COMMAND',seq=last['seq'],commit_sha256=head['commit_sha256'],request=request,receipt=receipt)


if __name__=='__main__':raise SystemExit(main())
