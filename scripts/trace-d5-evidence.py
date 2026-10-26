#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""I67 read-only trace auditor. Safe read/Git primitives adapted from audit-d5-evidence.py; no import or execution of I38."""
import ast
import collections
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import selectors
import stat
import subprocess
import sys
import time

REGISTRY = 'docs/validation/D5-TRACE-REGISTRY.json'
LIMITS = dict(entries=64, paths=4096, file_bytes=16*1024*1024,
              total_bytes=256*1024*1024, unique_bytes=128*1024*1024, ids=16384, rows=4096,
              refs=16384, output_bytes=12*1024*1024, depth=32, string=4096,
              git_calls=128, git_seconds=10, total_seconds=60, audit_seconds=180)
HASH = re.compile(r'[0-9a-f]{64}\Z')
OID = re.compile(r'[0-9a-f]{40}\Z')
PUBLIC = re.compile(r'[A-Za-z0-9_. /()+:–—;,-]{1,512}\Z')
PRIVATE = {'.git', '.env', '.aws', '.ssh', '.codex', '.agents', 'run_data',
           'dev', 'private', 'secrets', 'credentials', 'work', 'attachments',
           'data', 'artifacts', 'exports', 'backups', 'tmp', 'temp', 'internal',
           'node_modules', 'target', 'build', '__pycache__', '.venv', 'pgdata'}


class Fault(Exception):
    def __init__(self, code, unavailable=False):
        self.code, self.unavailable = code, unavailable
        super().__init__(code)


def require(ok, code='INVALID_SCHEMA'):
    if not ok:
        raise Fault(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def path_ok(name):
    require(isinstance(name, str) and 0 < len(name) <= 512, 'INVALID_PATH')
    require(re.fullmatch(r'[A-Za-z0-9_./-]+', name) is not None, 'INVALID_PATH')
    p = PurePosixPath(name)
    require(p.parts and not p.is_absolute() and str(p) == name, 'INVALID_PATH')
    require(all(x not in PRIVATE and x not in {'.', '..'} and
                not x.startswith('.env') for x in p.parts), 'PRIVATE_PATH')
    require(not name.endswith(('.key', '.pem', '.sqlite', '.log')), 'PRIVATE_PATH')
    return name


def strict_json(data, limits):
    require(len(data) <= limits['file_bytes'], 'FILE_LIMIT')
    # Bound nesting before the recursive standard-library decoder runs.
    depth = 0
    quoted = escaped = False
    for char in data.decode('utf-8', errors='strict'):
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            require(depth <= limits['depth'], 'JSON_DEPTH')
        elif char in ']}':
            depth -= 1

    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'DUPLICATE_KEY')
            out[key] = value
        return out

    def constant(_):
        raise Fault('NONFINITE_JSON')

    try:
        value = json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, RecursionError, UnicodeError):
        raise Fault('INVALID_JSON') from None

    def check(x):
        if isinstance(x, str):
            require(len(x) <= limits['string'], 'STRING_LIMIT')
        elif isinstance(x, dict):
            for k, v in x.items():
                check(k); check(v)
        elif isinstance(x, list):
            for v in x:
                check(v)
        elif isinstance(x, float):
            require(abs(x) < float('inf'), 'NONFINITE_JSON')
    check(value)
    return value


def fingerprint(st):
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


class Reader:
    """All paths relative to an open root; no symlink traversal or writes."""
    def __init__(self, root, limits):
        self.root, self.limits = Path(root), limits
        self.bytes = 0
        self.unique_bytes = 0
        self.started = time.monotonic()
        self.hashes = {}
        self.content = {}
        self.force = False
        self.seen = {}
        self.directories = {}

    def charge(self, size):
        require(time.monotonic()-self.started <= self.limits['audit_seconds'], 'AUDIT_TIMEOUT')
        require(size <= self.limits['file_bytes'], 'FILE_LIMIT')
        self.bytes += size
        require(self.bytes <= self.limits['total_bytes'], 'TOTAL_BYTE_LIMIT')

    def directory(self, name=''):
        if name:
            path_ok(name)
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for part in PurePosixPath(name).parts if name else ():
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd); fd = nxt
            return fd
        except BaseException:
            os.close(fd)
            raise

    def read(self, name):
        path_ok(name)
        require(len(self.seen) < self.limits['paths'] or name in self.seen, 'PATH_LIMIT')
        parent, leaf = str(PurePosixPath(name).parent), PurePosixPath(name).name
        fd = self.directory('' if parent == '.' else parent)
        try:
            before = os.stat(leaf, dir_fd=fd, follow_symlinks=False)
            require(stat.S_ISREG(before.st_mode), 'NONREGULAR_FILE')
            handle = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            try:
                opened = os.fstat(handle)
                require(fingerprint(before) == fingerprint(opened), 'UNSTABLE_SNAPSHOT')
                if name in self.content and not self.force:
                    require(self.seen[name] == fingerprint(opened), 'UNSTABLE_SNAPSHOT')
                    return self.content[name]
                self.charge(opened.st_size)
                chunks = []; digest = hashlib.sha256()
                if name not in self.seen:
                    self.unique_bytes += opened.st_size
                    require(self.unique_bytes <= self.limits['unique_bytes'], 'UNIQUE_BYTE_LIMIT')
                left = opened.st_size
                while left:
                    data = os.read(handle, min(65536, left))
                    require(bool(data), 'UNSTABLE_SNAPSHOT')
                    chunks.append(data); digest.update(data); left -= len(data)
                require(not os.read(handle, 1), 'UNSTABLE_SNAPSHOT')
                after = os.fstat(handle)
                require(fingerprint(opened) == fingerprint(after), 'UNSTABLE_SNAPSHOT')
                if name in self.seen:
                    require(self.hashes[name] == digest.hexdigest() and self.seen[name] == fingerprint(after), 'UNSTABLE_SNAPSHOT')
                self.hashes[name] = digest.hexdigest()
                self.seen[name] = fingerprint(after)
                self.content[name] = b''.join(chunks)
                return self.content[name]
            finally:
                os.close(handle)
        finally:
            os.close(fd)

    def listing(self, name):
        fd = self.directory(name)
        try:
            names = []
            with os.scandir(fd) as iterator:
                for entry in iterator:
                    require(len(names) < self.limits['paths'], 'PATH_LIMIT')
                    names.append(entry.name)
            names = tuple(sorted(names))
            self.directories.setdefault(name, names)
            require(self.directories[name] == names, 'UNSTABLE_SNAPSHOT')
            return names
        finally:
            os.close(fd)

    def finish(self):
        self.force = True
        for name, expected in tuple(self.seen.items()):
            self.read(name)
            parent, leaf = str(PurePosixPath(name).parent), PurePosixPath(name).name
            try:
                fd = self.directory('' if parent == '.' else parent)
            except OSError:
                raise Fault('UNSTABLE_SNAPSHOT') from None
            try:
                try:
                    require(fingerprint(os.stat(leaf, dir_fd=fd, follow_symlinks=False)) == expected,
                            'UNSTABLE_SNAPSHOT')
                except OSError:
                    raise Fault('UNSTABLE_SNAPSHOT') from None
            finally:
                os.close(fd)
        self.force = False
        for name in tuple(self.directories):
            self.listing(name)


class Git:
    def __init__(self, root, reader, limits):
        self.root, self.reader, self.limits = root, reader, limits
        self.calls = 0
        self.started = time.monotonic()
        self.trees, self.blobs = {}, {}

    def run(self, args, data=None, max_output=None):
        self.calls += 1
        remaining = self.limits['total_seconds'] - (time.monotonic() - self.started)
        require(self.calls <= self.limits['git_calls'] and remaining > 0, 'GIT_BUDGET')
        # Drop inherited tracing/config/object redirections before invoking read-only Git.
        env = dict(PATH=os.defpath, LANG='C', LC_ALL='C')
        env.update(GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0',
                   GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_OPTIONAL_LOCKS='0', GIT_NO_REPLACE_OBJECTS='1', GIT_ALLOW_PROTOCOL='')
        cap = min(max_output or self.limits['total_bytes'], self.limits['total_bytes'])
        process = None
        try:
            process = subprocess.Popen(['git', '--no-replace-objects', '-c', 'core.fsmonitor=false',
                                        '-c', 'core.hooksPath=/dev/null', '-c', 'trace2.eventTarget=0',
                                        '-c', 'trace2.normalTarget=0', '-c', 'trace2.perfTarget=0', *args], cwd=self.root,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL, env=env)
            deadline = time.monotonic() + min(remaining, self.limits['git_seconds'])
            chunks = []; count = 0; sent = 0; data = data or b''
            with selectors.DefaultSelector() as selector:
                os.set_blocking(process.stdout.fileno(), False)
                selector.register(process.stdout, selectors.EVENT_READ)
                if data:
                    os.set_blocking(process.stdin.fileno(), False)
                    selector.register(process.stdin, selectors.EVENT_WRITE)
                else:
                    process.stdin.close()
                while selector.get_map():
                    left = deadline-time.monotonic()
                    require(left > 0, 'GIT_TIMEOUT')
                    for key, _ in selector.select(min(left, 0.1)):
                        if key.fileobj is process.stdin:
                            sent += os.write(process.stdin.fileno(), data[sent:sent+65536])
                            if sent == len(data):
                                selector.unregister(process.stdin); process.stdin.close()
                        else:
                            block = os.read(process.stdout.fileno(), min(65536, cap-count+1))
                            if block:
                                count += len(block)
                                require(count <= cap, 'GIT_OUTPUT_LIMIT')
                                chunks.append(block)
                            else:
                                selector.unregister(process.stdout)
                try:
                    process.wait(timeout=max(0.001, deadline-time.monotonic()))
                except subprocess.TimeoutExpired:
                    raise Fault('GIT_TIMEOUT') from None
            if process.returncode:
                raise Fault('GIT_OBJECT_UNAVAILABLE', True)
            return b''.join(chunks)
        except OSError:
            raise Fault('GIT_UNAVAILABLE', True) from None
        finally:
            if process is not None:
                if process.poll() is None:
                    process.kill()
                process.wait()
                process.stdin.close(); process.stdout.close()

    def tree(self, commit):
        require(isinstance(commit, str) and OID.fullmatch(commit), 'INVALID_OID')
        if commit not in self.trees:
            require(self.run(['cat-file', '-t', commit]).strip() == b'commit', 'NOT_COMMIT')
            data = self.run(['ls-tree', '-rlz', '--full-tree', commit], max_output=2*1024*1024)
            out = {}
            for line in data.split(b'\0'):
                if not line:
                    continue
                meta, name = line.split(b'\t', 1)
                mode, kind, oid, size = meta.split()
                # Tree names are metadata only; unselected names never enter output or reads.
                out[name.decode('utf-8', errors='surrogateescape')] = (mode, kind, oid, int(size) if size != b'-' else -1)
                require(len(out) <= self.limits['paths'], 'PATH_LIMIT')
            require(len(out) <= self.limits['paths'], 'PATH_LIMIT')
            self.trees[commit] = out
        return self.trees[commit]

    def load(self, commit, paths):
        tree = self.tree(commit)
        wanted = []
        for name in sorted(set(paths)):
            path_ok(name)
            require(name in tree, 'HISTORICAL_PATH_UNAVAILABLE')
            mode, kind, oid, size = tree[name]
            require(mode in {b'100644', b'100755'} and kind == b'blob', 'NONREGULAR_BLOB')
            if oid not in self.blobs and oid not in [x[0] for x in wanted]:
                self.reader.charge(size)
                wanted.append((oid, size))
        if wanted:
            data = self.run(['cat-file', '--batch'], b''.join(oid+b'\n' for oid, _ in wanted),
                            max_output=sum(size+100 for _, size in wanted))
            offset = 0
            for oid, size in wanted:
                end = data.find(b'\n', offset)
                require(data[offset:end] == oid+b' blob '+str(size).encode(), 'INVALID_GIT_BATCH')
                value = data[end+1:end+1+size]
                require(len(value) == size and data[end+1+size:end+2+size] == b'\n', 'INVALID_GIT_BATCH')
                self.blobs[oid] = value
                offset = end+2+size
            require(offset == len(data), 'INVALID_GIT_BATCH')
        return {name: self.blobs[tree[name][2]] for name in paths}



def pointer(doc, ref):
    require(isinstance(ref, str) and (ref == '' or ref.startswith('/')), 'INVALID_POINTER')
    for part in ref[1:].split('/') if ref else []:
        require(not re.search(r'~(?![01])', part), 'INVALID_POINTER')
        part = part.replace('~1', '/').replace('~0', '~')
        if isinstance(doc, list):
            require(re.fullmatch(r'0|[1-9][0-9]*', part) is not None and int(part) < len(doc), 'INVALID_POINTER')
            doc = doc[int(part)]
        else:
            require(isinstance(doc, dict) and part in doc, 'INVALID_POINTER')
            doc = doc[part]
    return doc


def token(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,512}', value), 'INVALID_PUBLIC_ID')
    return value


def number(value):
    return type(value) is int and value >= 0


def datum(value=None, status='NOT_RECORDED', origin=None, scope='RECORDED_SCOPE', reason=None):
    require(status in {'NOT_RECORDED','NOT_APPLICABLE','RECORDED_DECLARATION',
                      'INHERITED_PARENT_CONTEXT','SOURCE_DERIVED_EXPECTATION'}, 'INVALID_PROVENANCE')
    require(value is None or status not in {'NOT_RECORDED','NOT_APPLICABLE'}, 'INVALID_PROVENANCE')
    out = dict(value=value, status=status, origin=origin, scope=scope)
    if reason:
        out['reason'] = token(reason)
    return out


def origin(e, ref, context=False):
    return dict(path=e.get('context_path') if context and e.get('context_path') else e['path'],
                sha256=e['context_sha256'] if context and e.get('context_path') else e['sha256'],
                pointer=ref, commit=e['commit'])


def observed(e, doc, ref, context=False, inherited=False):
    value = pointer(doc, ref)
    def safe(x):
        if isinstance(x,str):require(re.fullmatch(r'[A-Za-z0-9_. :+(),;=\-]{0,512}',x) is not None,'SANITIZED_DIAGNOSTIC')
        elif isinstance(x,list):
            for item in x:safe(item)
        else:require(x is None or type(x) in (int,bool,float),'SANITIZED_DIAGNOSTIC')
    safe(value)
    return datum(value, 'INHERITED_PARENT_CONTEXT' if inherited else 'RECORDED_DECLARATION', origin(e,ref,context))


def validate_provenance(field, role):
    require(isinstance(field,dict) and field.get('status') in {'NOT_RECORDED','NOT_APPLICABLE',
            'RECORDED_DECLARATION','INHERITED_PARENT_CONTEXT','SOURCE_DERIVED_EXPECTATION'}, 'INVALID_PROVENANCE')
    if role == 'command':
        require((field.get('origin') or {}).get('pointer') != '/demo_command', 'REJECT_DEMO_AS_CAMPAIGN')
        require(field['status'] not in {'SOURCE_DERIVED_EXPECTATION'} and field.get('scope') != 'AUDITOR_CURRENT_CONTEXT', 'REJECT_PROVENANCE_PROMOTION')
    if role == 'group_context':
        require(field['status'] in {'INHERITED_PARENT_CONTEXT','NOT_RECORDED'}, 'REJECT_CONTEXT_SCOPE_PROMOTION')
    if role == 'run_id':
        require(field['status'] in {'RECORDED_DECLARATION','NOT_RECORDED','NOT_APPLICABLE'}, 'REJECT_FABRICATED_RUN_ID')
    if role == 'observation':
        require(field['status'] != 'SOURCE_DERIVED_EXPECTATION', 'REJECT_DESIGN_AS_OBSERVATION')
    if role == 'historical_environment':
        require(field.get('scope') != 'AUDITOR_CURRENT_CONTEXT', 'REJECT_CURRENT_AS_HISTORICAL')


def accounting(doc, e, limits):
    ids = doc.get('passed'); require(isinstance(ids,list) and len(ids) <= limits['ids'], 'INVALID_TEST_ACCOUNTING')
    require(all(isinstance(x,str) for x in ids) and len(set(ids)) == len(ids), 'INVALID_TEST_ACCOUNTING')
    for x in ids: token(x)
    require(number(doc.get('tests_run')) and doc['tests_run'] >= len(ids), 'INVALID_TEST_ACCOUNTING')
    failures = sum(len(doc.get(k,[])) for k in ('failures','errors','skipped'))
    require(doc['tests_run'] == len(ids)+failures, 'INVALID_TEST_ACCOUNTING')
    require(doc['tests_run'] == e['tests_recorded'], 'INVALID_TEST_ACCOUNTING')
    require(sha(json.dumps(sorted(ids),separators=(',',':')).encode()) == e['passed_ids_sha256'], 'INVALID_TEST_ACCOUNTING')
    groups = doc.get('groups', {e['id'].split('-')[-1]:ids})
    require(isinstance(groups,dict) and {k:len(v) for k,v in groups.items()} == e['group_counts'], 'INVALID_GROUP_PARTITION')
    flat = [x for v in groups.values() for x in v]
    require(len(flat)==len(set(flat)) and set(flat)==set(ids), 'INVALID_GROUP_PARTITION')
    for group in groups:token(group)
    require(e.get('group_target_overrides',{}).get('test_postgres_adapter') == ('MOCKED_QUERY_NO_DB' if 'test_postgres_adapter' in groups else None), 'REJECT_TARGET_PROMOTION_MOCKED_QUERY')
    maps=doc.get('case_test_map',{})
    require(isinstance(maps,dict), 'INVALID_CASE_BINDING')
    for key, tests in maps.items():
        token(key);require(isinstance(tests,list) and tests and len(tests)==len(set(tests)) and set(tests)<=set(ids), 'INVALID_CASE_BINDING')
    scenarios=doc.get('scenarios',[]);require(isinstance(scenarios,list) and len(scenarios)<=limits['rows'], 'SCENARIO_BUDGET')
    require(sum(len(s.get('events',[])) for s in scenarios)<=limits['refs'],'EVENT_BUDGET')
    actual=collections.Counter(s.get('case') for s in scenarios)
    require(dict(actual)==e.get('scenario_multiplicity',{}) and len(scenarios)==e['scenario_count'], 'INCOMPLETE_OR_UNEXPECTED_SCENARIOS')
    for s in scenarios:
        require(set(s)<=set(e['allowed_scenario_fields']) and s.get('case') in maps, 'INVALID_CASE_BINDING')
        for key in ('run_id','client_store_id','remote_store_id'):
            if key in s: require(isinstance(s[key],str) and re.fullmatch(r'[0-9a-f-]{36}',s[key]), 'INVALID_SCENARIO_IDENTITY')
        for oracle in s.get('oracles',[]):
            for role,store in [('client','client_store_id'),('remote','remote_store_id')]:
                h=oracle.get(role,{}).get('head',{})
                if 'run_id' in h:require(h['run_id']==s.get('run_id'),'INVALID_SCENARIO_IDENTITY')
                if store in s and 'store_id' in h:require(h['store_id']==s[store],'INVALID_SCENARIO_IDENTITY')
        identity=s.get('primary_identity',{})
        if identity:
            gates=[x for x in s.get('events',[]) if x.get('event')=='READY' and x.get('actor')=='primary']
            require(len(gates)==1 and all(gates[0].get(k)==v for k,v in identity.items()),'INVALID_SCENARIO_IDENTITY')
    return groups, maps, scenarios


def validate_registry(reg, limits):
    require(isinstance(reg,dict) and set(reg)=={'schema','contract_path','contract_sha256','entries','semantic_baseline'} and reg['schema']=='d5.trace-registry.v1','INVALID_REGISTRY_OR_SCHEMA')
    path_ok(reg['contract_path']);require(HASH.fullmatch(reg['contract_sha256']) is not None,'INVALID_REGISTRY_OR_SCHEMA')
    require(isinstance(reg['entries'],list) and 0<len(reg['entries'])<=limits['entries'],'INVALID_REGISTRY_OR_SCHEMA')
    require(len({e['id'] for e in reg['entries']})==len(reg['entries']),'INVALID_REGISTRY_OR_SCHEMA')
    for e in reg['entries']:
        token(e['id']);require(OID.fullmatch(e['commit']) and HASH.fullmatch(e['sha256']),'INVALID_REGISTRY_OR_SCHEMA')
        require(e['adapter_version']=='trace.'+e['id'].lower()+'.v1','INVALID_REGISTRY_OR_SCHEMA')
        require(e['kind'] in {'LEGACY_RECORDED_REPORT_NO_RAW','SEALED_RAW_WITH_CONTEXT'},'INVALID_REGISTRY_OR_SCHEMA')
        path_ok(e['path'])
        for p,h in e['effective_inputs'].items():path_ok(p);require(HASH.fullmatch(h),'INVALID_REGISTRY_OR_SCHEMA')
        if e.get('context_path'):path_ok(e['context_path']);require(HASH.fullmatch(e['context_sha256']),'INVALID_REGISTRY_OR_SCHEMA')
        for pat in e['discovery_patterns']:
            require(pat.count('*')==1 and '/' in pat,'INVALID_REGISTRY_OR_SCHEMA');parent,leaf=pat.rsplit('/',1);path_ok(parent);require(re.fullmatch(r'[A-Za-z0-9_.-]*\*[A-Za-z0-9_.-]+',leaf),'INVALID_REGISTRY_OR_SCHEMA')
        for p in e['explicit_input_paths']:path_ok(p)
    require(reg['semantic_baseline']=={'SUPPORTS_BOUNDED':81,'PARTIAL':3},'INVALID_REGISTRY_OR_SCHEMA')


def discover(reader,e):
    names=set(e['explicit_input_paths'])
    for pattern in e['discovery_patterns']:
        parent,leaf=pattern.rsplit('/',1)
        for name in reader.listing(parent):
            if fnmatch.fnmatchcase(name,leaf):names.add(path_ok(parent+'/'+name))
    return names


def method_ref(e,tid,git,limits,cache):
    parts=tid.split('.');module,cls,method=parts[-3:]
    path='/'.join(parts[:-2])+'.py' if tid.startswith('testing.') else 'testing/D5/'+module+'.py'
    require(path in e['effective_inputs'],'UNREGISTERED_METHOD_SOURCE')
    key=(e['commit'],path)
    if key not in cache:
        data=git.load(e['commit'],[path])[path]
        require(sha(data)==e['effective_inputs'][path],'HASH_MISMATCH')
        cache[key]=ast.parse(data)
    symbol=method
    if module=='test_durable_integration' and re.fullmatch('test_DF[0-9]{2}',method):symbol=method[5:].lower()
    if module=='test_durable_relational' and re.fullmatch('test_DR[0-9]{2}',method):symbol=method[5:].lower()
    node=next((n for n in cache[key].body if isinstance(n,ast.ClassDef) and n.name==cls),None)
    node=next((n for n in node.body if isinstance(n,ast.FunctionDef) and n.name==symbol),None) if node else None
    if not node:return datum(reason='METHOD_AST_NOT_RECORDED')
    return datum(dict(symbol=cls+'.'+symbol,line=node.lineno,end_line=node.end_lineno),'SOURCE_DERIVED_EXPECTATION',dict(path=path,sha256=e['effective_inputs'][path],commit=e['commit'],pointer=None),scope='METHOD_BINDING_NOT_RUNTIME')


def bind_context(doc,e,ctx):
    if e['kind']=='LEGACY_RECORDED_REPORT_NO_RAW':return
    require(sorted(ctx)==e['allowed_context_fields'],'INVALID_CONTEXT_BINDING')
    if e.get('context_path'):
        require(ctx.get('exit_code')==0 and ctx.get('stderr_bytes')==0 and ctx.get('inputs_before')==ctx.get('inputs_after')==e['effective_inputs'],'INVALID_CONTEXT_BINDING')
        for k in ('python','platform','implementation','build','machine','release','optimize','debug'):
            if k in doc and k in ctx:require(doc[k]==ctx[k],'INVALID_CONTEXT_BINDING')
            if k in doc.get('context',{}) and k in ctx:require(doc['context'][k]==ctx[k],'INVALID_CONTEXT_BINDING')
        if 'context' in doc:require(doc['context'].get('argv')==ctx['command'],'INVALID_CONTEXT_BINDING')
    else: require(doc.get('inputs_before')==doc.get('inputs_after')==e['effective_inputs'],'INVALID_CONTEXT_BINDING')
    require(ctx.get('command',ctx.get('argv'))==e['command'],'INVALID_CONTEXT_BINDING')


def build_entry(e,doc,ctx,git,limits,cache):
    require(sorted(doc)==e['allowed_root_fields'] and doc.get('schema')==e['schema'],'INVALID_REGISTRY_OR_SCHEMA')
    require(doc.get('status') in {'PASS','FAIL','NOT_RUN','BLOCKED'},'INVALID_RECORDED_STATUS')
    if e['kind']=='LEGACY_RECORDED_REPORT_NO_RAW':require(doc.get('inputs')==e['effective_inputs'],'INVALID_CONTEXT_BINDING')
    groups,maps,scenarios=accounting(doc,e,limits);bind_context(doc,e,ctx)
    has_context=e['kind']!='LEGACY_RECORDED_REPORT_NO_RAW'
    cref='/command' if e.get('context_path') else '/context/argv'
    command=observed(e,ctx,cref,True) if e.get('context_path') else observed(e,doc,cref) if has_context else datum(reason='CAMPAIGN_COMMAND_NOT_RECORDED')
    validate_provenance(command,'command')
    environment={}
    for key in ('python','implementation','build','platform','machine','release','optimize','debug'):
        if e.get('context_path') and key in ctx:
            environment[key]=observed(e,ctx,'/'+key,True)
        elif key in doc.get('context',{}):
            environment[key]=observed(e,doc,'/context/'+key)
        elif key in doc:
            environment[key]=observed(e,doc,'/'+key)
        else:environment[key]=datum(reason='ENVIRONMENT_FIELD_NOT_RECORDED')
    row=dict(id=e['id'],historical_integrity='MATCH',current_inputs='MATCH',command_context='RECORDED_PARENT' if has_context else 'NOT_RECORDED',scenario_trace='INCOMPLETE',recorded_result=observed(e,doc,'/status'),raw_binding='MATCH' if has_context else 'NOT_RECORDED',invocation=dict(command=command,environment=environment),groups=[],tests=[],scenarios=[],missing_fields=[],sufficiency='REVIEW_PENDING',global_review='OPEN',closure=False)
    for group,ids in groups.items():
        parent=datum(command['value'],'INHERITED_PARENT_CONTEXT',command['origin'],scope='SAME_PARENT_INVOCATION') if has_context else datum(reason='PARENT_COMMAND_NOT_RECORDED')
        validate_provenance(parent,'group_context')
        row['groups'].append(dict(group_id=group,classification='RECORDED_DECLARATION' if 'groups' in doc else 'ADAPTER_CLASSIFICATION',test_ids=ids,parent_invocation=parent,target=e.get('group_target_overrides',{}).get(group,e['target']),versions=dict(environment_ref='/entries/'+e['id']+'/invocation/environment',scope='INHERITED_PARENT_CONTEXT',external_versions=datum(reason='EXTERNAL_VERSIONS_NOT_RECORDED'))))
        for tid in ids:
            refs=[j for j,s in enumerate(scenarios) if tid in maps.get(s['case'],[])]
            missing=[] if refs else ['SCENARIO_RUN_ID_NOT_RECORDED','PER_PHASE_ORACLE_NOT_RECORDED','FRONTIER_NOT_RECORDED']
            if not has_context:missing.append('CAMPAIGN_COMMAND_NOT_RECORDED')
            source=method_ref(e,tid,git,limits,cache)
            if source['status']=='NOT_RECORDED':missing.append('METHOD_AST_NOT_RECORDED')
            index=doc['passed'].index(tid)
            row['tests'].append(dict(entry_id=e['id'],group_id=group,test_id=tid,recorded_result_ref=origin(e,'/passed/'+str(index)),parent_invocation_ref=e['id']+'/invocation',inputs_ref=e['id']+'/effective_inputs',source_method_ref=source,scenario_refs=[origin(e,'/scenarios/'+str(j)) for j in refs],missing_fields=missing,scenario_trace='INCOMPLETE' if missing else 'COMPLETE_RECORDED_SCOPE'))
    for j,s in enumerate(scenarios):
        ref='/scenarios/'+str(j);fields={};control=s.get('family') in {'PROTOCOL_OWNERSHIP','INVENTORY_RAW'}
        for key in ('run_id','client_store_id','remote_store_id','path','family','authority','frontier','frontier_row','logical_operation','mode','point','stage','order','mutation_id','UI_part','command','primary_identity','manifest','issued_ticket','send_id','ticket','variant'):
            # Large domain records are references, never payload copies.
            if key in s:
                value=s[key]
                if isinstance(value,(dict,list)):value=dict(reference=origin(e,ref+'/'+key))
                else:token(value) if isinstance(value,str) else None
                fields[key]=datum(value,'RECORDED_DECLARATION',origin(e,ref+'/'+key))
            elif control and key in {'frontier','frontier_row','point','mode','stage','command','primary_identity','logical_operation'}:fields[key]=datum(status='NOT_APPLICABLE',reason='CONTROL_NO_DOMAIN_FRONTIER')
            else:fields[key]=datum(reason='SCENARIO_FIELD_NOT_RECORDED')
        validate_provenance(fields['run_id'],'run_id')
        missing=[key.upper()+'_NOT_RECORDED' for key in e['fields_required_for_trace'] if key not in s]
        if not control and not any(key in s for key in ('frontier','point')):missing.append('FRONTIER_NOT_RECORDED')
        if not control and not any(key in s for key in ('command','primary_identity','logical_operation','actors')):missing.append('OPERATION_NOT_RECORDED')
        row['scenarios'].append(dict(entry_id=e['id'],case_id=s['case'],raw_pointer=ref,variant_ordinal=j,fields=fields,inputs_ref=e['id']+'/effective_inputs',events_ref=origin(e,ref+'/events') if 'events' in s else None,oracles_ref=origin(e,ref+'/oracles') if 'oracles' in s else None,recorded_status=observed(e,doc,ref+'/status'),missing_fields=missing,scenario_trace='INCOMPLETE' if missing else 'COMPLETE_RECORDED_SCOPE',global_accepted=False))
    row['missing_fields']=sorted({x for t in row['tests']+row['scenarios'] for x in t['missing_fields']})
    if not has_context:row['missing_fields'].append('RAW_NOT_RECORDED')
    if any(f['status']=='NOT_RECORDED' for f in environment.values()):row['missing_fields'].append('ENVIRONMENT_METADATA_INCOMPLETE')
    row['scenario_trace']='INCOMPLETE' if row['missing_fields'] else 'COMPLETE_RECORDED_SCOPE'
    row['effective_inputs']=e['effective_inputs']
    return row


def summary(entries):
    missing=collections.Counter(x for e in entries for x in e.get('missing_fields',[]))
    return dict(entries=len(entries),group_occurrences=sum(len(e.get('groups',[])) for e in entries),test_occurrences=sum(len(e.get('tests',[])) for e in entries),scenario_rows=sum(len(e.get('scenarios',[])) for e in entries),new_functional_tests=0,missingness=dict(sorted(missing.items())),sufficiency='REVIEW_PENDING',global_review='OPEN',closure=False)


def trace(root,registry=None,limits=None):
    limits=dict(LIMITS,**(limits or {}));reader=Reader(root,limits);git=Git(root,reader,limits);entries=[];findings=[];cache={}
    out=dict(schema='d5.i67-trace-report.v1',trace_status='INVALID',entries=entries,findings=findings,semantic_baseline=dict(SUPPORTS_BOUNDED=81,PARTIAL=3),outside_registered_scope='NOT_RUN',real_or_human_requirements='NOT_RUN',new_functional_tests=0,D5_closed=False,global_gaps_open=[f'G{i:02}' for i in range(1,8)],global_review='OPEN',closure=False,publication_authorized=False)
    try:
        reg=registry if registry is not None else strict_json(reader.read(REGISTRY),limits)
        validate_registry(reg,limits)
        contract=reader.read(reg['contract_path']);require(sha(contract)==reg['contract_sha256'],'HASH_MISMATCH')
        plan=strict_json(contract,limits);expected={c['id']:c for c in plan['source_catalog']}
        require(set(expected)=={e['id'] for e in reg['entries']},'INVALID_REGISTRY_OR_SCHEMA')
        for e in reg['entries']:
            for key,value in expected[e['id']].items():require(e.get(key)==value,'INVALID_REGISTRY_OR_SCHEMA')
            phase='historical'
            try:
                paths=[e['path']]+([e['context_path']] if e.get('context_path') else [])
                historical=git.load(e['commit'],paths+list(e['effective_inputs']))
                for p in paths:require(sha(historical[p])==(e['sha256'] if p==e['path'] else e['context_sha256']),'HASH_MISMATCH')
                for p,h in e['effective_inputs'].items():require(sha(historical[p])==h,'HASH_MISMATCH')
                doc=strict_json(historical[e['path']],limits)
                ctx=strict_json(historical[e['context_path']],limits) if e.get('context_path') else doc.get('context',{})
                if e.get('context_path'):require(ctx['raw_bytes']==len(historical[e['path']]),'INVALID_CONTEXT_BINDING')
                require(sum(len(r.get('tests',[])) for r in entries)+len(doc.get('passed',[]))<=limits['ids'],'ID_BUDGET')
                require(sum(len(r.get('scenarios',[])) for r in entries)+len(doc.get('scenarios',[]))<=limits['rows'],'SCENARIO_BUDGET')
                row=build_entry(e,doc,ctx,git,limits,cache);index=len(entries);entries.append(row);phase='current'
                for group in row['groups']:group['versions']['environment_ref']=f'/entries/{index}/invocation/environment'
                for test in row['tests']:test['parent_invocation_ref']=f'/entries/{index}/invocation';test['inputs_ref']=f'/entries/{index}/effective_inputs'
                for scenario in row['scenarios']:scenario['inputs_ref']=f'/entries/{index}/effective_inputs'
                for p in paths:
                    try:require(sha(reader.read(p))==(e['sha256'] if p==e['path'] else e['context_sha256']),'HASH_MISMATCH')
                    except FileNotFoundError:row['current_inputs']='UNDETERMINED';findings.append(dict(entry=e['id'],code='CURRENT_EVIDENCE_MISSING'))
                names=discover(reader,e);original=set(e['effective_inputs']);row['discovery']=dict(added=sorted(names-original),removed=sorted(original-names))
                changes=[];docs=[]
                for p,h in e['effective_inputs'].items():
                    try:
                        if sha(reader.read(p))!=h:(changes if p.endswith('.py') else docs).append(p)
                    except FileNotFoundError:row['discovery']['removed'].append(p)
                row['changed_runtime_inputs']=changes;row['changed_documentary_inputs']=docs
                if changes or row['discovery']['added'] or row['discovery']['removed']:row['current_inputs']='CHANGED';findings.append(dict(entry=e['id'],code='STALE_INPUTS'))
                if docs:findings.append(dict(entry=e['id'],code='DOCUMENT_ONLY_CHANGE_REVIEW_PENDING'))
                if row['missing_fields']:findings.append(dict(entry=e['id'],code='INCOMPLETE_RECORDED_TRACE',missing_fields=row['missing_fields']))
            except Fault as ex:
                findings.append(dict(entry=e['id'],code=ex.code,phase=phase))
                if ex.unavailable:entries.append(dict(id=e['id'],historical_integrity='UNAVAILABLE',current_inputs='UNDETERMINED',scenario_trace='INCOMPLETE',recorded_result=datum(reason='HISTORICAL_OBJECT_UNAVAILABLE'),sufficiency='REVIEW_PENDING',global_review='OPEN',closure=False));continue
                raise
        reader.finish()
        out['summary']=summary(entries);out['trace_status']='FINDINGS' if findings else 'CONSISTENT_RECORDED_SCOPE'
        out['read_metrics']=dict(paths=len(reader.seen),unique_bytes=reader.unique_bytes,read_bytes=reader.bytes,git_calls=git.calls)
        out['auditor_current_context']=dict(scope='AUDITOR_CURRENT_CONTEXT',python=platform.python_version(),implementation=platform.python_implementation(),build=list(platform.python_build()),platform=platform.system(),release=platform.release(),machine=platform.machine(),optimize=sys.flags.optimize,debug=__debug__)
        code=1 if findings else 0
    except (Fault,OSError,ValueError,KeyError,TypeError,IndexError,StopIteration,RecursionError,SyntaxError) as ex:
        code=2;out['trace_status']='INVALID';out['findings'].append(dict(code=ex.code if isinstance(ex,Fault) else 'SANITIZED_READ_OR_SCHEMA_ERROR'));out['summary']=summary(entries)
    def count_refs(x):
        if isinstance(x,dict):return int('pointer' in x)+sum(count_refs(v) for v in x.values())
        if isinstance(x,list):return sum(count_refs(v) for v in x)
        return 0
    if count_refs(out)>limits['refs']:
        return dict(schema=out['schema'],trace_status='INVALID',findings=[dict(code='REFERENCE_BUDGET')],global_review='OPEN',closure=False,D5_closed=False,publication_authorized=False),2
    encoded=json.dumps(out,ensure_ascii=False,separators=(',',':')).encode()
    if len(encoded)>limits['output_bytes']:
        return dict(schema=out['schema'],trace_status='INVALID',findings=[dict(code='OUTPUT_BUDGET')],global_review='OPEN',closure=False,D5_closed=False,publication_authorized=False),2
    return out,code


def main(argv=None):
    args=sys.argv[1:] if argv is None else argv
    if args:
        print(json.dumps(dict(trace_status='INVALID',findings=[dict(code='ARGUMENTS_NOT_SUPPORTED')],closure=False)))
        return 2
    out,code=trace(Path(__file__).resolve().parents[1]);print(json.dumps(out,ensure_ascii=False,separators=(',',':')));return code


if __name__=='__main__':raise SystemExit(main())
