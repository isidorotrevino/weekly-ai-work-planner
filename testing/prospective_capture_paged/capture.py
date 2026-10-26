# SPDX-License-Identifier: GPL-3.0-only
"""I73 paged capture components; historical imports require separate I74 authority."""
import json
import os
from pathlib import Path
import re
import sys
import types
from testing.prospective_capture import capture as c

ROOT=c.ROOT
REGISTRY='docs/validation/D5-PAGED-CAPTURE-REGISTRY.json'
AUTHORITY='docs/validation/D5-I74-capture-authorization.json'
DESTINATION='docs/validation/D5-I74-P01'
LAUNCH_COPY='docs/validation/D5-I74-P01-launch.json'
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
    keys={'schema','contract_path','contract_sha256','legacy_registry_sha256','entry','policies','constructor_observer','observer_specs','limits','functional_execution_authorized','semantic_baseline'}
    c.require(set(reg)==keys and reg['schema']=='d5.paged-capture-registry.v1' and reg['functional_execution_authorized'] is False,'INVALID_REGISTRY')
    c.require(reg['contract_path']=='docs/validation/D5-I72-design-review.json','INVALID_REGISTRY')
    body=reader.read(reg['contract_path']);c.require(c.sha(body)==reg['contract_sha256'],'STALE_CONTRACT');design=c.strict_json(body)
    oldbytes=reader.read(c.REGISTRY);c.require(c.sha(oldbytes)==reg['legacy_registry_sha256'],'STALE_LEGACY_REGISTRY');old=c.strict_json(oldbytes)
    c.require(reg['entry']==old['entries'][0] and reg['observer_specs']==old['observer_specs'],'INVALID_REGISTRY')
    for key in ('policies','constructor_observer','semantic_baseline'):c.require(reg[key]==design[key],'INVALID_REGISTRY')
    expected=dict(design['proposed_limits'])
    for key in expected:
        mapped={'input_paths':'paths','input_file_bytes':'file_bytes','input_unique_bytes':'unique_bytes','input_read_bytes':'read_bytes'}.get(key,key)
        c.require(reg['limits'].get(key)==LIMITS.get(mapped,expected[key]),'INVALID_LIMITS')
    c.require(reg['limits']==expected,'INVALID_LIMITS')
    entry=reg['entry'];c.require(entry['id']=='P01' and entry['expected_tests']==321 and len(set(entry['expected_test_ids']))==321,'INVALID_MANIFEST')
    for key in ('expected_test_ids','expected_groups','expected_passed_ids_sha256'):c.require(entry[key]==design[key],'INVALID_MANIFEST')
    c.require([p['case'] for p in reg['policies']]==['DF01','DF02','DF48','DR01','DR02','DF07','DF43'],'INVALID_POLICY')
    for p in reg['policies']+[reg['constructor_observer']]:
        a=p['source'];c.require(c.sha(reader.read(a['path']))==a['sha256'],'STALE_POLICY_SOURCE')
    reader.finish();return reg


def authority_inputs():
    return {f'testing/prospective_capture_paged/{n}' for n in ('capture.py','worker.py','test_paged_capture.py','run_paged_lab.py','README.md')}|{REGISTRY,'testing/prospective_capture/capture.py','docs/validation/D5-I69-integrity.json','docs/validation/D5-I70-integrity.json','docs/validation/D5-I71-integrity.json','docs/validation/D5-I72-integrity.json','docs/validation/D5-I72-design-review.json','docs/validation/D5-I73-tests-raw.json','docs/validation/D5-I73-results.json','docs/validation/D5-I73-integrity.json'}


def authority(root,requested,reg):
    scope(requested);reader=c.Reader(root)
    try:a=c.strict_json(reader.read(AUTHORITY))
    except FileNotFoundError:raise c.CaptureFault('I74_AUTHORIZATION_REQUIRED') from None
    c.require(set(a)=={'schema','phase','scopes','registry_sha256','capture_inputs'} and a['schema']=='d5.paged-capture-authority.v1' and a['phase']=='I74_EXPLICITLY_APPROVED' and a['scopes']==['P01'],'I74_AUTHORIZATION_REQUIRED')
    c.require(a['registry_sha256']==c.sha(reader.read(REGISTRY)) and type(a['capture_inputs']) is dict and authority_inputs()<=set(a['capture_inputs']),'STALE_AUTHORITY')
    for p,h in a['capture_inputs'].items():c.require(c.sha(reader.read(c.public_path(p)))==h,'STALE_AUTHORITY')
    evidence=c.strict_json(reader.read('docs/validation/D5-I73-tests-raw.json'))
    c.require(evidence.get('status')=='PASS' and evidence.get('tests_run')==64 and evidence.get('functional_campaigns_executed')==0 and evidence.get('forbidden_imports')==[],'COMPONENT_VALIDATION_REQUIRED')
    seal=c.strict_json(reader.read('docs/validation/D5-I73-integrity.json'))
    for p,h in seal.get('artifacts',{}).items():c.require(a['capture_inputs'].get(p)==h and c.sha(reader.read(p))==h,'STALE_AUTHORITY')
    c.require(bool(seal.get('artifacts')),'COMPONENT_VALIDATION_REQUIRED');reader.finish();return a


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


class Recorder(c.Recorder):
    def __init__(self,entry,owner,policies=(),limits=None):
        super().__init__(entry,dict(LIMITS,**(limits or {})));self.events=PageSink(owner,self.run_id,self.limits);self.policies={p['test_id']:p for p in policies};self.declarations={};self.frame_summary={};self.references=0
    def reference(self,n=1):self.references+=n;c.require(self.references<=self.limits['refs'],'REFERENCE_BUDGET')
    def start(self,test):
        self.frame_summary=dict(operands_missing=False,returns_missing=False)
        super().start(test)
        if self.active:self.active['construction_refs']=[]
    def emit(self,kind,**data):
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
        old=self.owners.get(id(obj))
        if old is None or old[0]() is not obj:self.reference()
        ref=super().owner(obj,out)
        if ref and ref in self.declarations and self.owner_contexts[ref]['identity']:
            d=self.declarations[ref];actual=self.owner_contexts[ref]['identity']
            if any(actual.get(k)!=d[k] for k in ('run_id','store_id')):self.invalid('CONSTRUCTION_HEAD_IDENTITY_CONFLICT')
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
            if override and override['classification']=='NO_STORE_CONTROL':f['domain_scope']=dict(status='NOT_APPLICABLE',reason=override['reason'])
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
        try:self.events.close();self.reference(len(self.events.manifest))
        except BaseException as ex:self.invalid(ex.code if isinstance(ex,c.CaptureFault) else 'PAGE_FINALIZATION_ERROR')
        for f in self.frames:f['capture_completeness']='INCOMPLETE' if f['missing'] else 'CAPTURED_FIELDS_PENDING_REVIEW'
        out=dict(schema='d5.paged-sidecar.v1',capture_run_id=self.run_id,scope=self.entry['id'],status='INVALID_CAPTURE' if self.errors else 'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW',frames=self.frames,pages=self.events.manifest,event_count=len(self.events),pages_bytes=self.events.total_bytes,peak_page_buffer_bytes=self.events.peak_buffer_bytes,owner_contexts=self.owner_contexts,construction_declarations=self.declarations,errors=list(self.errors),observers_restored=self.restored,worker_context=c.environment(),raw_functional_status=raw.get('status') if type(raw) is dict else 'NOT_RECORDED',child_context_scope='ONLY_EXISTING_PROTOCOL_RECORDS_NOT_PARENT_INSTRUMENTATION',global_review='OPEN',closure=False,D5_closed=False,semantic_baseline=dict(SUPPORTS_BOUNDED=81,PARTIAL=3),sufficiency='REVIEW_PENDING',new_distinct_functional_tests=0)
        if len(encode(out))>self.limits['index_sidecar_bytes']:return dict(schema=out['schema'],status='INVALID_CAPTURE',errors=['SIDECAR_BUDGET'],closure=False)
        return out


def evidence_reader(root,limits=None):
    lim=dict(LIMITS,**(limits or {}));return c.Reader(root,dict(unique_bytes=lim['evidence_unique_bytes'],read_bytes=lim['evidence_read_bytes']))


def validate_pages(reader,prefix,side,limits=None):
    lim=dict(LIMITS,**(limits or {}));pages=side.get('pages');c.require(type(pages) is list and len(pages)<=lim['pages'],'INVALID_PAGE_MANIFEST')
    c.require({n for n in reader.listing(prefix) if n.startswith('event-')}=={p.get('name') for p in pages},'PAGE_SET_MISMATCH')
    frames=side.get('frames',[]);frame_map={f['test_frame_id']:f for f in frames};c.require(len(frame_map)==len(frames),'DUPLICATE_FRAME')
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
                if kind=='TEST_RESULT':
                    if e.get('outcome')!='SUBTEST':kinds[ref]['result'].append(e.get('outcome'))
                    else:kinds[ref]['failed_subtest']|=e.get('subtest_failed') is True
            seq+=1
    c.require(active is None and type(side.get('event_count')) is int and type(side.get('pages_bytes')) is int and seq==side['event_count'] and total==side['pages_bytes'],'INCOMPLETE_EVENT_STREAM')
    for ref,f in frame_map.items():
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
    out=c.invocation('P01');out['command']=['python3','-B','-m','testing.prospective_capture_paged.worker','P01'];out['worker_arguments_observed']=args;return out


def verify_ready(message,lease,pid,rawfd,sidefd,dirfd):
    c.require(set(message)==READY_KEYS,'INVALID_WORKER_IDENTITY');st=os.fstat(dirfd)
    c.require((message['directory_device'],message['directory_inode'])==(st.st_dev,st.st_ino),'INVALID_DIRECTORY_CHANNEL')
    c.verify_ready({k:v for k,v in message.items() if not k.startswith('directory_')},'P01',lease,pid,rawfd,sidefd)


def plan(root=ROOT):
    reg=read_registry(root);return dict(schema='d5.paged-capture-plan.v1',phase='I73_COMPONENTS_ONLY',scope='P01',expected_tests=321,status='NOT_RUN_I74_AUTHORIZATION_REQUIRED',functional_execution_authorized=False,semantic_baseline=reg['semantic_baseline'],closure=False,global_review='OPEN',publication_authorized=False)


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
    context=dict(scope='P01',invocation=invocation(),functional_execution='NEW_I74',closure=False,global_review='OPEN',publication_authorized=False)
    rawfd=sidefd=directory=ready_read=ready_write=release_read=release_write=None;process=None
    try:
        before=c.runner_files(root,entry);c.require(before==entry['runner_effective_inputs'],'STALE_INPUTS')
        rawfd=owner.create('runner-raw.json');sidefd=owner.create('sidecar.json');directory=owner.directory();ready_read,ready_write=os.pipe();release_read,release_write=os.pipe()
        cmd=[sys.executable,'-B','-m','testing.prospective_capture_paged.worker','P01',str(sidefd),str(ready_write),str(release_read),str(directory),owner.nonce]
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
        c.require(side.get('schema')=='d5.paged-sidecar.v1' and side.get('observers_restored') is True and side.get('entrypoint_exit_code')==(0 if raw.get('status')=='PASS' else 1),'INVALID_PACKET_BINDING')
        context['artifacts']={'runner-raw.json':c.sha(rawb),'sidecar.json':c.sha(sideb)}
        # Invalid/partial pages are preserved, never accepted as a complete trace.
        if side.get('status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW':context['page_validation']=validate_pages(packet,DESTINATION,side);c.aggregate_capture(side,c.scenario_metadata(raw,entry),raw,entry)
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
