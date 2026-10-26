# SPDX-License-Identifier: GPL-3.0-only
"""I79 late binding and bounded worker diagnostics. Functional execution requires I80."""
import fnmatch
import json
import os
from pathlib import Path
import re
import sys
import types
from testing.prospective_capture_typed import capture as t
c=t.c;ROOT=t.ROOT;LIMITS=dict(t.LIMITS)
REGISTRY='docs/validation/D5-LATE-CAPTURE-REGISTRY.json'
AUTHORITY='docs/validation/D5-I80-capture-authorization.json'
DESTINATION='docs/validation/D5-I80-P01'
LAUNCH_COPY='docs/validation/D5-I80-P01-launch.json'
ChannelRoot=t.ChannelRoot;PageSink=t.PageSink
encode=t.encode;write_all=t.write_all;scope=t.scope
verify_ready=t.verify_ready;verify_release=t.verify_release;wait_worker=t.wait_worker
package_names=t.package_names;package_size=t.package_size;evidence_reader=t.evidence_reader
NORMAL_SCHEMA='d5.late-sidecar.v1';FAILURE_SCHEMA='d5.late-worker-failure.v1';DIAGNOSTIC_SCHEMA='d5.worker-diagnostic.v1'

PHASES=frozenset(['AUTHORITY', 'CHANNELS', 'READY', 'RELEASE', 'RUNNER_INPUTS', 'RUNNER_IMPORT', 'TARGETS', 'RECORDER_INSTALL', 'ENTRYPOINT', 'FINALIZE', 'INPUTS_AFTER', 'AUTHORITY_AFTER', 'SIDECAR_WRITE', 'COMPLETE'])
CODES=frozenset(['OK', 'CLASS_MODULE_NOT_LOADED', 'CLASS_BINDING_CHANGED', 'STALE_CLASS_SOURCE', 'STALE_INPUTS', 'STALE_AUTHORITY', 'UNSUPPORTED_CLASS_BINDING', 'UNSUPPORTED_OBSERVER_API', 'UNSUPPORTED_OBSERVER_SIGNATURE', 'CONSTRUCTOR_OBSERVER_UNAVAILABLE', 'FIXTURE_MODULE_NOT_LOADED', 'INVALID_WORKER_CHANNEL', 'INVALID_DIRECTORY_OWNER', 'INVALID_WORKER_RELEASE', 'INVALID_WORKER_GROUP', 'UNEXPECTED_RUNNER_MODULE', 'STDLIB_BINDING_CHANGED', 'STDLIB_SOURCE_CHANGED', 'TYPED_PROJECTION_ERROR', 'ENTRYPOINT_EXCEPTION', 'RAW_UNAVAILABLE_OR_INVALID', 'RAW_FLUSH_ERROR', 'ENTRYPOINT_EXIT_MISMATCH', 'RAW_BUDGET', 'SIDECAR_BUDGET', 'PAGE_WRITE_ERROR', 'PAGE_FINALIZATION_ERROR', 'EVENT_SIZE_BUDGET', 'EVENT_TEST_BUDGET', 'EVENT_CAMPAIGN_BUDGET', 'PAGE_COUNT_BUDGET', 'PAGE_BYTES_BUDGET', 'PAGES_TOTAL_BUDGET', 'REFERENCE_BUDGET', 'FRAME_BUDGET', 'OPERAND_BUDGET', 'OPERAND_DEPTH', 'UNIQUE_BUDGET', 'READ_BUDGET', 'PATH_BUDGET', 'FILE_BUDGET', 'EXTERNAL_CAMPAIGN_TIMEOUT', 'SANITIZED_WORKER_ERROR', 'CAPTURE_INVALID', 'CAPTURE_INCOMPLETE'])

def read_registry(root=ROOT,reader=None):
    r=reader if reader is not None else c.Reader(root);reg=c.strict_json(r.read(REGISTRY))
    old=c.strict_json(r.read(t.REGISTRY));design=c.strict_json(r.read('docs/validation/D5-I78-design-review.json'))
    c.require(set(reg)==set(old)|{'late_binding','diagnostic'},'INVALID_REGISTRY')
    c.require(reg['schema']=='d5.late-capture-registry.v1' and reg['contract_path']=='docs/validation/D5-I78-design-review.json' and reg['functional_execution_authorized'] is False,'INVALID_REGISTRY')
    c.require(reg['contract_sha256']==c.sha(r.read(reg['contract_path'])) and reg['legacy_registry_sha256']==c.sha(r.read(t.REGISTRY)),'STALE_CONTRACT')
    for key in set(old)-{'schema','contract_path','contract_sha256','legacy_registry_sha256'}:c.require(reg[key]==old[key],'INVALID_REGISTRY')
    for key in ('late_binding','diagnostic'):c.require(reg[key]==design[key],'INVALID_REGISTRY')
    c.require(reg['limits']==design['proposed_limits'],'INVALID_REGISTRY')
    aliases={'input_paths':'paths','input_file_bytes':'file_bytes','input_unique_bytes':'unique_bytes','input_read_bytes':'read_bytes'}
    c.require(all(LIMITS[aliases.get(k,k)]==v for k,v in reg['limits'].items()),'INVALID_REGISTRY')
    c.require(set(reg['diagnostic']['codes'])==CODES and set(reg['diagnostic']['phases'])==PHASES,'INVALID_REGISTRY')
    for a in design['source_anchors']:c.require(c.sha(r.read(a['path']))==a['sha256'],'STALE_POLICY_SOURCE')
    c.require(reg['stdlib_binding']==t.StdlibGuard().describe(),'STALE_STDLIB_BINDING')
    return reg


def authority_inputs():
    return {f'testing/prospective_capture_late/{n}' for n in ('capture.py','worker.py','test_late_capture.py','run_late_lab.py','README.md')}|{REGISTRY,'testing/prospective_capture/capture.py','testing/prospective_capture_paged/capture.py','testing/prospective_capture_typed/capture.py','docs/validation/D5-I78-design-review.json','docs/validation/D5-I79-tests-raw.json','docs/validation/D5-I79-results.json','docs/validation/D5-I79-integrity.json'}|{f'docs/validation/D5-I{i}-integrity.json' for i in range(69,79)}


def authority(root,requested,reg,reader=None):
    scope(requested);r=reader if reader is not None else c.Reader(root)
    try:a=c.strict_json(r.read(AUTHORITY))
    except FileNotFoundError:raise c.CaptureFault('I80_AUTHORIZATION_REQUIRED') from None
    c.require(set(a)=={'schema','phase','scopes','registry_sha256','capture_inputs'} and a['schema']=='d5.late-capture-authority.v1' and a['phase']=='I80_EXPLICITLY_APPROVED' and a['scopes']==['P01'],'I80_AUTHORIZATION_REQUIRED')
    c.require(a['registry_sha256']==c.sha(r.read(REGISTRY)) and type(a['capture_inputs']) is dict and authority_inputs()<=set(a['capture_inputs']),'STALE_AUTHORITY')
    for name,h in a['capture_inputs'].items():c.require(c.sha(r.read(c.public_path(name)))==h,'STALE_AUTHORITY')
    raw=c.strict_json(r.read('docs/validation/D5-I79-tests-raw.json'));c.require(raw.get('status')=='PASS' and raw.get('tests_run')==64 and raw.get('functional_campaigns_executed')==0 and raw.get('forbidden_imports')==[],'COMPONENT_VALIDATION_REQUIRED')
    seal=c.strict_json(r.read('docs/validation/D5-I79-integrity.json'));c.require(bool(seal.get('artifacts')),'COMPONENT_VALIDATION_REQUIRED')
    for name,h in seal['artifacts'].items():c.require(a['capture_inputs'].get(name)==h and c.sha(r.read(name))==h,'STALE_AUTHORITY')
    return a


def runner_files(root,entry,reader=None):
    r=reader if reader is not None else c.Reader(root);names=set(entry['runner_explicit_input_paths'])
    for pattern in entry['runner_discovery_patterns']:
        parent,leaf=pattern.rsplit('/',1);c.public_path(parent)
        for name in r.listing(parent):
            if fnmatch.fnmatchcase(name,leaf):names.add(c.public_path(parent+'/'+name))
    names.update(entry['runner_effective_inputs']);return {n:c.sha(r.read(n)) for n in sorted(names)}


def plan(root=ROOT):
    reg=read_registry(root);return dict(schema='d5.late-capture-plan.v1',phase='I79_COMPONENTS_ONLY',scope='P01',expected_tests=321,status='NOT_RUN_I80_AUTHORIZATION_REQUIRED',functional_execution_authorized=False,semantic_baseline=reg['semantic_baseline'],closure=False,global_review='OPEN',publication_authorized=False)


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


class LateBindings(t.ClassBindings):
    def __init__(self,specs,reader,lookup=None,on_reference=None):
        self.reader=reader;self.lookup=sys.modules.get if lookup is None else lookup;self.on_reference=on_reference or (lambda:None);self.specs={s['id']:s for s in specs};c.require(len(specs)==len(self.specs)<=3 and 'builtins.dict' in self.specs,'INVALID_POLICY');self.states={ref:'UNRESOLVED' for ref in self.specs};self.states['builtins.dict']='BOUND';self.rows={'builtins.dict':dict(cls=dict,sha256=None,module=None,name=None)}
    def check(self):
        for ref,row in self.rows.items():
            c.require(self.states[ref]!='INVALID','CLASS_BINDING_CHANGED')
            if ref=='builtins.dict':continue
            try:
                spec=self.specs[ref];module,name=ref.rsplit('.',1)
                c.require(self.lookup(module) is row['module'] and row['module'].__dict__.get(name) is row['cls'],'CLASS_BINDING_CHANGED')
                c.require(c.sha(self.reader.read(spec['source']['path']))==row['sha256'],'STALE_CLASS_SOURCE')
            except BaseException:self.states[ref]='INVALID';raise
    def prepare(self,allowed):
        refs=[]
        for graph in allowed:
            if graph.startswith('class-'):refs.append(graph[6:])
            elif graph=='exact-PlaneError-instance-args-projection':refs.append('source_ingest.plane_fixture.PlaneError')
            elif graph=='exact-EligibilityError-instance-args-projection':refs.append('source_ingest.eligibility_fixture.EligibilityError')
        self.check()
        for ref in refs:
            c.require(ref in self.specs,'UNSUPPORTED_CLASS_BINDING');c.require(self.states[ref]!='INVALID','CLASS_BINDING_CHANGED')
            if self.states[ref]=='BOUND':continue
            try:
                module_name,name=ref.rsplit('.',1);module=self.lookup(module_name);c.require(type(module) is types.ModuleType,'CLASS_MODULE_NOT_LOADED');cls=module.__dict__.get(name)
                c.require(type(cls) is type and cls.__bases__==(ValueError,) and cls.__module__==module_name and cls.__name__==name,'UNSUPPORTED_CLASS_BINDING')
                spec=self.specs[ref];c.require(c.sha(self.reader.read(spec['source']['path']))==spec['source']['sha256'],'STALE_CLASS_SOURCE');self.on_reference();self.rows[ref]=dict(cls=cls,sha256=spec['source']['sha256'],module=module,name=name);self.states[ref]='BOUND'
            except BaseException:self.states[ref]='INVALID';raise
        self.check()


class Recorder(t.Recorder):
    def __init__(self,*args,ledger=None,**kwargs):
        self.ledger=ledger;super().__init__(*args,**kwargs)
        if self.ledger:self.ledger.run_id=self.run_id
        if isinstance(self.projector.bindings,LateBindings):self.projector.bindings.on_reference=self.reference;self.reference(len(self.projector.bindings.rows))
    def invalid(self,code):
        super().invalid(code)
        if self.ledger:self.ledger.fail(code)
    def operand(self,value,helper,slot):
        row=self.operand_rows.get(self.active['test_id']) if self.active else None
        if row and row['helper']==helper:
            plain=c.digest_value(value,self.limits)
            if plain['status']=='OBSERVED_DIGEST':return plain
            try:
                self.projector.bindings.prepare(row['operand_roles'].get(str(slot),[]))
            except BaseException as ex:
                code=ex.code if type(ex) is c.CaptureFault else 'TYPED_PROJECTION_ERROR';self.invalid(code);return dict(status='NOT_RECORDED',reason=safe_code(code),sha256=None)
        return super().operand(value,helper,slot)
    def finish(self,raw=None):
        out=super().finish(raw);out['schema']=NORMAL_SCHEMA;return out


def validate_pages(reader,prefix,side,limits=None,profile=None):return t.validate_pages(reader,prefix,side,limits,profile)


def invocation(args=None):
    out=c.invocation('P01');out['command']=['python3','-B','-m','testing.prospective_capture_late.worker','P01'];out['worker_arguments_observed']=args;return out

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
    context=dict(scope='P01',invocation=invocation(),functional_execution='NEW_I80',closure=False,global_review='OPEN',publication_authorized=False)
    rawfd=sidefd=directory=ready_read=ready_write=release_read=release_write=None;process=None
    try:
        before=runner_files(root,entry,inputs);c.require(before==entry['runner_effective_inputs'],'STALE_INPUTS')
        rawfd=owner.create('runner-raw.json');sidefd=owner.create('sidecar.json');directory=owner.directory();ready_read,ready_write=os.pipe();release_read,release_write=os.pipe()
        cmd=[sys.executable,'-B','-m','testing.prospective_capture_late.worker','P01',str(sidefd),str(ready_write),str(release_read),str(directory),owner.nonce]
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


if __name__=='__main__':raise SystemExit(main())
