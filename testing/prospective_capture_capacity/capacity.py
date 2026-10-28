# SPDX-License-Identifier: GPL-3.0-only
"""I95 synthetic capacity planner. No capture entrypoint or product imports."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import threading

ROOT=Path(__file__).resolve().parents[2]
MANIFEST='docs/validation/D5-CAPACITY-PLANNER-MANIFEST.json'
DESIGN='docs/validation/D5-I94-design-review.json'
SCHEMA='d5.capacity-certificate.v1'
DEFAULT_LIMITS={'event_bytes': 4096, 'events_test': 2048, 'events_campaign': 131072, 'page_bytes': 2097152, 'pages': 32, 'event_pages_total_bytes': 67108864, 'raw_bytes': 12582912, 'index_sidecar_bytes': 12582912, 'context_bytes': 12582912, 'launch_bytes': 12582912, 'package_bytes': 117444608, 'evidence_unique_bytes': 134217728, 'evidence_read_bytes': 268435456, 'operand_bytes': 16777216, 'frames': 4096, 'refs': 16384, 'depth': 32, 'string': 4096, 'input_paths': 4096, 'input_file_bytes': 16777216, 'input_unique_bytes': 134217728, 'input_read_bytes': 268435456, 'wait_seconds': 20, 'campaign_seconds': 900}
PHASES=('AUTHORITY','TARGETS','ENTRYPOINT','FINALIZE','COMPLETE')
CODES=frozenset(['OK', 'CLASS_MODULE_NOT_LOADED', 'CLASS_BINDING_CHANGED', 'STALE_CLASS_SOURCE', 'STALE_INPUTS', 'STALE_AUTHORITY', 'UNSUPPORTED_CLASS_BINDING', 'UNSUPPORTED_OBSERVER_API', 'UNSUPPORTED_OBSERVER_SIGNATURE', 'CONSTRUCTOR_OBSERVER_UNAVAILABLE', 'FIXTURE_MODULE_NOT_LOADED', 'INVALID_WORKER_CHANNEL', 'INVALID_DIRECTORY_OWNER', 'INVALID_WORKER_RELEASE', 'INVALID_WORKER_GROUP', 'UNEXPECTED_RUNNER_MODULE', 'STDLIB_BINDING_CHANGED', 'STDLIB_SOURCE_CHANGED', 'TYPED_PROJECTION_ERROR', 'ENTRYPOINT_EXCEPTION', 'RAW_UNAVAILABLE_OR_INVALID', 'RAW_FLUSH_ERROR', 'ENTRYPOINT_EXIT_MISMATCH', 'RAW_BUDGET', 'SIDECAR_BUDGET', 'PAGE_WRITE_ERROR', 'PAGE_FINALIZATION_ERROR', 'EVENT_SIZE_BUDGET', 'EVENT_TEST_BUDGET', 'EVENT_CAMPAIGN_BUDGET', 'PAGE_COUNT_BUDGET', 'PAGE_BYTES_BUDGET', 'PAGES_TOTAL_BUDGET', 'REFERENCE_BUDGET', 'FRAME_BUDGET', 'OPERAND_BUDGET', 'OPERAND_DEPTH', 'UNIQUE_BUDGET', 'READ_BUDGET', 'PATH_BUDGET', 'FILE_BUDGET', 'EXTERNAL_CAMPAIGN_TIMEOUT', 'SANITIZED_WORKER_ERROR', 'CAPTURE_INVALID', 'CAPTURE_INCOMPLETE'])

class Fault(ValueError):
    def __init__(self,code):self.code=code;super().__init__(code)
def require(ok,code):
    if not ok:raise Fault(code)
def encode(value):return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'),sort_keys=True).encode('utf8')
def sha(body):return hashlib.sha256(body).hexdigest()
def integer(n):return type(n) is int and 0<=n<=(1<<63)-1
def size(n,limit,code):require(integer(n) and n<=limit,code);return n

def builtin(value,limits,depth=0):
    require(depth<=limits['depth'],'OPERAND_DEPTH');kind=type(value)
    require(kind in (dict,list,str,int,bool,type(None)),'OPERAND_BUDGET')
    if kind is str:require(len(value)<=limits['string'],'OPERAND_BUDGET')
    if kind is dict:
        require(all(type(k) is str for k in value),'OPERAND_BUDGET')
        for k,v in value.items():builtin(k,limits,depth+1);builtin(v,limits,depth+1)
    elif kind is list:
        for v in value:builtin(v,limits,depth+1)
    return value

def checked_row(row,limits):
    require(type(row) is dict,'CAUSAL_FIELD_BUDGET');builtin(row,limits);body=encode(row)
    size(len(body),limits['event_bytes'],'CAUSAL_FIELD_BUDGET');size(len(body)*2,limits['operand_bytes'],'OPERAND_BUDGET')
    return json.loads(body)

def check_operand(original_bytes,auxiliary_bytes,limits):
    require(integer(original_bytes) and integer(auxiliary_bytes),'OPERAND_BUDGET');return size(original_bytes+auxiliary_bytes,limits['operand_bytes'],'OPERAND_BUDGET')

def package_total(total,members,limits):
    size(members,37,'PACKAGE_SET_MISMATCH');size(total,limits['package_bytes'],'PACKAGE_BUDGET');return total

def page_sizes(pages,limits):
    require(type(pages) is list,'PAGE_COUNT_BUDGET');size(len(pages),limits['pages'],'PAGE_COUNT_BUDGET')
    for n in pages:size(n,limits['page_bytes'],'PAGE_BYTES_BUDGET')
    return size(sum(pages),limits['event_pages_total_bytes'],'PAGES_TOTAL_BUDGET')

def bundle_sizes(files,limits):
    require(type(files) is dict,'PACKAGE_SET_MISMATCH');base={'OWNER','runner-raw.json','sidecar.json','context.json','launch.json'}
    require(base<=set(files) and all(n in base or re.fullmatch(r'event-00(?:0[1-9]|[12][0-9]|3[0-2])\.json',n) for n in files),'PACKAGE_SET_MISMATCH')
    require(files['OWNER']==36,'PACKAGE_SET_MISMATCH');pages=sorted(n for n in files if n.startswith('event-'))
    require(pages==[f'event-{i:04}.json' for i in range(1,len(pages)+1)],'PACKAGE_SET_MISMATCH')
    for name,key in [('runner-raw.json','raw_bytes'),('sidecar.json','index_sidecar_bytes'),('context.json','context_bytes'),('launch.json','launch_bytes')]:size(files[name],limits[key],{'raw_bytes':'RAW_BUDGET','index_sidecar_bytes':'SIDECAR_BUDGET'}.get(key,'CONTEXT_BUDGET'))
    page_sizes([files[n] for n in pages],limits);return package_total(sum(files.values()),len(files),limits)

class ReadAccounting:
    def __init__(self,limits,kind='input'):
        require(kind in ('input','evidence'),'READ_BUDGET');self.limits=limits;self.kind=kind;self.files={};self.total=0;self.unique=0
    def charge(self,name,n):
        require(type(name) is str and name and not name.startswith('/') and all(x not in ('','..','.') for x in name.split('/')),'PATH_BUDGET');size(n,self.limits['input_file_bytes'] if self.kind=='input' else self.limits['package_bytes'],'FILE_BUDGET')
        fresh=name not in self.files
        require(fresh or self.files[name]==n,'STALE_INPUTS');size(len(self.files)+int(fresh),self.limits['input_paths'],'PATH_BUDGET')
        unique=self.unique+(n if fresh else 0);total=self.total+n
        size(unique,self.limits[self.kind+'_unique_bytes'],'UNIQUE_BUDGET');size(total,self.limits[self.kind+'_read_bytes'],'READ_BUDGET')
        self.files[name]=n;self.unique=unique;self.total=total
    def plan(self,reads):
        for name,n in reads:self.charge(name,n)
        return dict(paths=len(self.files),unique_bytes=self.unique,read_bytes=self.total)

class Reader:
    """Own input scope: one ledger for all reads and finish revalidation."""
    def __init__(self,root,limits):self.root=Path(root);self.accounting=ReadAccounting(limits);self.hashes={}
    def read(self,name):
        require(type(name) is str and name and not name.startswith('/') and all(x not in ('','..','.') for x in name.split('/')),'PATH_BUDGET')
        fd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            for part in name.split('/')[:-1]:
                nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=nxt
            handle=os.open(name.split('/')[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
            try:
                import stat
                st=os.fstat(handle);require(stat.S_ISREG(st.st_mode),'FILE_BUDGET');self.accounting.charge(name,st.st_size);chunks=[];left=st.st_size
                while left:
                    chunk=os.read(handle,min(left,65536));require(bool(chunk),'STALE_INPUTS');chunks.append(chunk);left-=len(chunk)
                require(not os.read(handle,1),'STALE_INPUTS');end=os.fstat(handle);require((st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)==(end.st_dev,end.st_ino,end.st_size,end.st_mtime_ns,end.st_ctime_ns),'STALE_INPUTS');body=b''.join(chunks)
            finally:os.close(handle)
        finally:os.close(fd)
        digest=sha(body);require(name not in self.hashes or self.hashes[name]==digest,'STALE_INPUTS');self.hashes[name]=digest;return body
    def finish(self):
        for name in list(self.hashes):self.read(name)


def read_manifest(reader):
    manifest=json.loads(reader.read(MANIFEST));require(set(manifest)=={'schema','contract','contract_sha256','limits','implementation_sources','preservation_inputs','closed_codes','functional_execution_authorized'},'STALE_AUTHORITY')
    require(manifest['schema']=='d5.capacity-planner-manifest.v1' and manifest['contract']==DESIGN and manifest['functional_execution_authorized'] is False,'STALE_AUTHORITY')
    body=reader.read(DESIGN);design=json.loads(body);require(sha(body)==manifest['contract_sha256'],'STALE_INPUTS')
    expected={r['key']:r['current'] for r in design['quota_comparison']};require(manifest['limits']==expected,'STALE_AUTHORITY');require(manifest['closed_codes']==sorted(CODES),'STALE_AUTHORITY')
    require(set(manifest['implementation_sources'])=={'testing/prospective_capture_capacity/'+n for n in ('capacity.py','test_capacity.py','run_capacity_lab.py','README.md')},'STALE_AUTHORITY')
    for name,h in manifest['implementation_sources'].items():require(sha(reader.read(name))==h,'STALE_INPUTS')
    for name,h in manifest['preservation_inputs'].items():require(sha(reader.read(name))==h,'STALE_INPUTS')
    return manifest

class Diagnostic:
    def __init__(self):self.phase='AUTHORITY';self.first=None
    def at(self,phase):require(phase in PHASES,'SANITIZED_WORKER_ERROR');self.phase=phase
    def fail(self,code):
        if self.first is None:self.first=(self.phase if self.phase!='COMPLETE' else 'FINALIZE',code if type(code) is str and code in CODES and code!='OK' else 'SANITIZED_WORKER_ERROR')
    def value(self):
        phase,code=self.first or ('COMPLETE','OK');out=dict(schema='d5.capacity-component-diagnostic.v1',phase=phase,code=code,status='FAILED' if self.first else 'COMPLETED',scope='SYNTHETIC_COMPONENT_ONLY');size(len(encode(out)),4096,'CONTEXT_BUDGET');return out

def write_all(fd,body):
    view=memoryview(body)
    while view:
        n=os.write(fd,view);require(n>0,'CONTEXT_BUDGET');view=view[n:]

class OneShot:
    def __init__(self,fd):self.fd=fd;self.started=False
    def write(self,value,limit=4096):
        require(not self.started,'CONTEXT_BUDGET');body=encode(value);size(len(body),limit,'CONTEXT_BUDGET');self.started=True;write_all(self.fd,body)
    def failure(self,diagnostic):
        if self.started:return False
        self.write(diagnostic.value());return True

class AtomicGuard:
    """One global committed ledger for new synthetic instrumentation only."""
    def __init__(self,limits):self.limits=dict(limits);self.used=0;self._tables={};self._events=[];self._test_counts={};self._lock=threading.Lock();self.diagnostic=Diagnostic();self.errors=[]
    def snapshot(self):
        with self._lock:return dict(used=self.used,tables=json.loads(encode(self._tables)),events=json.loads(encode(self._events)))
    def commit(self,n,additions,event=None):
        require(integer(n),'REFERENCE_BUDGET');require(type(additions) is dict and all(type(t) is str for t in additions),'CAUSAL_FIELD_BUDGET')
        # Detach validated exact builtins; caller mutation cannot affect a commit.
        staged={}
        for table,rows in additions.items():
            require(type(rows) is dict and all(type(k) is str for k in rows),'CAUSAL_FIELD_BUDGET');staged[table]={k:checked_row(row,self.limits) for k,row in rows.items()}
        require(n>=reference_cost(staged),'REFERENCE_BUDGET')
        detached=None
        if event is not None:
            require(type(event) is dict,'EVENT_SIZE_BUDGET');size(len(encode(builtin(event,self.limits))),self.limits['event_bytes'],'EVENT_SIZE_BUDGET');detached=checked_row(event,self.limits)
        with self._lock:
            require(n<=self.limits['refs']-self.used,'REFERENCE_BUDGET')
            # Build detached next state before publishing any table/key/count.
            tables={k:dict(v) for k,v in self._tables.items()}
            for table,rows in staged.items():
                target=tables.setdefault(table,{})
                require(not set(target)&set(rows),'CAUSAL_FIELD_BUDGET');target.update(rows)
            size(len(encode(tables)),self.limits['index_sidecar_bytes'],'SIDECAR_BUDGET')
            events=list(self._events);counts=dict(self._test_counts)
            if detached is not None:
                tid=detached.get('test_id');require(type(tid) is str,'EVENT_TEST_BUDGET');size(len(events)+1,self.limits['events_campaign'],'EVENT_CAMPAIGN_BUDGET');size(counts.get(tid,0)+1,self.limits['events_test'],'EVENT_TEST_BUDGET');events.append(detached);counts[tid]=counts.get(tid,0)+1
            self._tables=tables;self._events=events;self._test_counts=counts;self.used+=n
    def fail(self,code):
        with self._lock:
            if type(code) is str and code not in self.errors:self.errors.append(code if code in CODES or code=='OBSERVER_IDENTITY_CHANGED' else 'SANITIZED_WORKER_ERROR')
            self.diagnostic.fail(code)
    @property
    def should_stop(self):return self.diagnostic.first is not None
    def invoke(self,original,args=(),kwargs=None,observe=None):
        # No instrumentation lock is held across the original call or observer.
        try:out=original(*args,**(kwargs or {}))
        except BaseException:raise
        if observe is not None:
            try:n,rows,event=observe(out);self.commit(n,rows,event)
            except BaseException as ex:self.fail(ex.code if type(ex) is Fault else 'SANITIZED_WORKER_ERROR')
        return out

class PagePlanner:
    """Exact encoded lengths; no packet writer, worker or domain observations."""
    def __init__(self,limits):self.limits=limits;self.closed=[];self.current_bytes=0;self.current_count=0;self.count=0
    def length(self,count,body_bytes,index=None,first=None):
        header=dict(schema='d5.capture-event-page.v1',capture_run_id='11111111-1111-4111-8111-111111111111',page_index=len(self.closed)+1 if index is None else index,first_sequence=self.count-self.current_count if first is None else first,last_sequence=(self.count-self.current_count if first is None else first)+count-1,event_count=count)
        return len(encode(header))+len(b',"events":[]}')-1+body_bytes+max(0,count-1)
    def append(self,event):
        body=encode(event);size(len(body),self.limits['event_bytes'],'EVENT_SIZE_BUDGET');size(self.count+1,self.limits['events_campaign'],'EVENT_CAMPAIGN_BUDGET');roll=False
        candidate=self.length(self.current_count+1,self.current_bytes+len(body))
        if self.current_count and candidate>self.limits['page_bytes']:
            roll=True;candidate=self.length(1,len(body),index=len(self.closed)+2,first=self.count)
        size(len(self.closed)+1+int(roll),self.limits['pages'],'PAGE_COUNT_BUDGET');size(candidate,self.limits['page_bytes'],'PAGE_BYTES_BUDGET')
        previous=self.length(self.current_count,self.current_bytes) if roll else 0
        size(sum(self.closed)+previous+candidate,self.limits['event_pages_total_bytes'],'PAGES_TOTAL_BUDGET')
        if roll:self.closed.append(previous);self.current_bytes=0;self.current_count=0
        self.current_bytes+=len(body);self.current_count+=1;self.count+=1
    def sizes(self):return self.closed+([self.length(self.current_count,self.current_bytes)] if self.current_count else [])


def loop_bounds(source):
    tree=ast.parse(source);out=[]
    for node in ast.walk(tree):
        if not isinstance(node,(ast.For,ast.While)):continue
        bound=None;reason='UNKNOWN_DATA_OR_CONTROL'
        if isinstance(node,ast.For):
            it=node.iter
            if isinstance(it,(ast.List,ast.Tuple,ast.Set)):bound=len(it.elts);reason='LOCAL_LITERAL_ONLY'
            elif isinstance(it,ast.Call) and isinstance(it.func,ast.Name) and it.func.id=='range' and 1<=len(it.args)<=3 and not it.keywords and all(isinstance(a,ast.Constant) and type(a.value) is int for a in it.args):
                args=[a.value for a in it.args]
                if all(abs(a)<=(1<<31) for a in args) and (len(args)<3 or args[2]!=0):bound=len(range(*args));reason='LOCAL_LITERAL_ONLY'
        out.append(dict(line=node.lineno,bound=bound,reason=reason,transitive_bound_proven=False))
    return out

def graph_bound(name,graph,active=None):
    active=set() if active is None else set(active)
    if name in active or name not in graph:return None
    row=graph[name]
    if type(row) is not dict or row.get('local') is None:return None
    require(integer(row['local']),'REFERENCE_BUDGET');active.add(name);total=row['local']
    for child,multiplicity in row.get('calls',[]):
        if not integer(multiplicity):return None
        bound=graph_bound(child,graph,active)
        if bound is None:return None
        total+=multiplicity*bound
    return total

def resolve_methods(classes,derived):
    # Static, single-base synthetic model. Unsupported MROs remain unknown.
    result={};seen=set();current=derived
    while current is not None:
        require(current in classes and current not in seen,'STALE_INPUTS');seen.add(current);row=classes[current]
        for name,site in row['methods'].items():result.setdefault(name,site)
        current=row['base']
    return result


def evaluate(certificate,expected,limits):
    fields={'schema','source_pins','inventory_sha256','charging_sites','multiplicity_bounds','proposed_numeric_limits','joint_resource_envelope','unresolved','review_decision'}
    if certificate is None:return dict(status='NOT_ESTABLISHED',unresolved=['CERTIFICATE_ABSENT'],functional_release_authorized=False)
    require(type(certificate) is dict and set(certificate)==fields and certificate['schema']==SCHEMA,'STALE_AUTHORITY')
    require(certificate['source_pins']==expected['source_pins'] and certificate['inventory_sha256']==sha(encode(expected['inventory'])),'STALE_INPUTS')
    require(certificate['charging_sites']==expected['charging_sites'] and set(certificate['multiplicity_bounds'])==set(expected['charging_sites']),'STALE_INPUTS')
    require(certificate['proposed_numeric_limits']==limits,'STALE_AUTHORITY');require(certificate['review_decision']==dict(basis='PINNED_SOURCE_ENVELOPE',status='PLANNING_MODEL_ONLY'),'STALE_AUTHORITY')
    unknown=list(expected.get('unresolved',[]))+list(certificate['unresolved']);refs=0
    for key,weight in expected['charging_sites'].items():
        require(integer(weight),'STALE_INPUTS');multiplicity=certificate['multiplicity_bounds'][key]
        if multiplicity is None:unknown.append(key)
        else:require(integer(multiplicity),'STALE_INPUTS');refs+=weight*multiplicity
    if unknown:return dict(status='NOT_ESTABLISHED',unresolved=sorted(set(unknown)),functional_release_authorized=False)
    require(expected['scope']=='SYNTHETIC_MODEL','STALE_AUTHORITY')
    resource=certificate['joint_resource_envelope'];require(type(resource) is dict and set(resource)=={'refs','events_per_test','events','files','reads','operand_original','operand_auxiliary'},'STALE_AUTHORITY');require(resource['refs']==refs,'STALE_INPUTS');size(refs,limits['refs'],'REFERENCE_BUDGET')
    require(type(resource['events_per_test']) is list,'EVENT_TEST_BUDGET')
    for n in resource['events_per_test']:size(n,limits['events_test'],'EVENT_TEST_BUDGET')
    require(sum(resource['events_per_test'])==resource['events'],'EVENT_CAMPAIGN_BUDGET');size(resource['events'],limits['events_campaign'],'EVENT_CAMPAIGN_BUDGET');bundle_sizes(resource['files'],limits)
    ReadAccounting(limits,'evidence').plan(resource['reads']);check_operand(resource['operand_original'],resource['operand_auxiliary'],limits)
    return dict(status='CAPACITY_ESTABLISHED_SYNTHETIC_MODEL_ONLY',refs=refs,unresolved=[],functional_release_authorized=False)


def evidence_gate(capacity,missing):
    require(type(missing) is list and all(type(x) is str for x in missing),'STALE_INPUTS')
    return dict(capacity_status=capacity['status'],evidence_status='MISSING_REQUIRED_EVIDENCE' if missing else 'SYNTHETIC_PREDICATES_ONLY_NOT_SUFFICIENCY',missing=list(missing),functional_release_authorized=False,closure=False)

def validate_witness_group(group):
    require(type(group) is dict and set(group)=={'context','identity','witnesses'},'STALE_INPUTS');require(type(group['context']) is dict and set(group['context'])=={'capture','frame','subcase','thread'},'STALE_INPUTS');require(type(group['identity']) is dict and set(group['identity'])=={'run','store','role'} and group['identity']['role'] in ('CLIENT','REMOTE'),'STALE_INPUTS')
    refs=[]
    for witness in group['witnesses']:
        require(type(witness) is dict and set(witness)=={'object_ref','authorities'} and type(witness['object_ref']) is str and type(witness['authorities']) is list and witness['authorities'],'STALE_INPUTS');refs.append(witness['object_ref'])
    require(refs==sorted(set(refs)) and bool(refs),'STALE_INPUTS');return json.loads(encode(group))


def reference_cost(additions):
    """Minimum for component rows; full runtime charging still needs site proof."""
    def pointers(value,key=''):
        if type(value) is dict:return sum(pointers(v,k) for k,v in value.items())
        if type(value) is list:
            if key.endswith('_refs'):return len(value)
            return sum(pointers(v) for v in value)
        return int(key.endswith('_ref') and value is not None)
    return sum(1+pointers(row) for rows in additions.values() for row in rows.values())

class EventAccounting:
    """Planning descriptors only, never an event capture or dropped-event sink."""
    def __init__(self,limits):self.limits=limits;self.count=0;self.tests={}
    def accept(self,test_id,encoded_bytes):
        require(type(test_id) is str,'EVENT_TEST_BUDGET');size(encoded_bytes,self.limits['event_bytes'],'EVENT_SIZE_BUDGET');size(self.count+1,self.limits['events_campaign'],'EVENT_CAMPAIGN_BUDGET');size(self.tests.get(test_id,0)+1,self.limits['events_test'],'EVENT_TEST_BUDGET')
        self.count+=1;self.tests[test_id]=self.tests.get(test_id,0)+1

def restore_binding(owner,name,original,expected,guard):
    if getattr(owner,name) is not expected:guard.fail('OBSERVER_IDENTITY_CHANGED')
    setattr(owner,name,original)
