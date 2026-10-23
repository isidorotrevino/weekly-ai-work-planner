#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Read-only, bounded D5 evidence audit. No imports of campaign runtime code."""
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

REGISTRY = 'docs/validation/D5-EVIDENCE-REGISTRY.json'
LIMITS = dict(entries=16, paths=4096, file_bytes=16*1024*1024,
              total_bytes=128*1024*1024, ids=16384, rows=512,
              output_bytes=2*1024*1024, depth=32, string=4096,
              git_calls=256, git_seconds=10, total_seconds=60)
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
        self.seen = {}
        self.directories = {}

    def charge(self, size):
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
                self.charge(opened.st_size)
                chunks = []
                left = opened.st_size
                while left:
                    data = os.read(handle, min(65536, left))
                    require(bool(data), 'UNSTABLE_SNAPSHOT')
                    chunks.append(data); left -= len(data)
                require(not os.read(handle, 1), 'UNSTABLE_SNAPSHOT')
                after = os.fstat(handle)
                require(fingerprint(opened) == fingerprint(after), 'UNSTABLE_SNAPSHOT')
                self.seen[name] = fingerprint(after)
                return b''.join(chunks)
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
        for name, expected in self.seen.items():
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
        env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
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


def selected(names, series):
    require(series in {'I34', 'I36'}, 'INVALID_DISCOVERY_RULE')
    prefix = 'D5-I33-' if series == 'I34' else 'D5-I35-'
    out = set()
    for name in names:
        p = PurePosixPath(name)
        if ((str(p.parent) in {'source_ingest', 'testing/D5'} and p.suffix == '.py') or
            (str(p.parent) == 'testing/D5/fixtures' and p.suffix == '.md') or
            (str(p.parent) == 'docs/design' and p.name.startswith(prefix) and p.suffix == '.md')):
            out.add(path_ok(name))
    return out


def discover(reader, series):
    names = [f'{parent}/{name}' for parent in ('source_ingest', 'testing/D5',
             'testing/D5/fixtures', 'docs/design') for name in reader.listing(parent)]
    paths = selected(names, series)
    for name in paths:
        fd = reader.directory(str(PurePosixPath(name).parent))
        try:
            require(stat.S_ISREG(os.stat(PurePosixPath(name).name, dir_fd=fd,
                                        follow_symlinks=False).st_mode), 'NONREGULAR_FILE')
        finally:
            os.close(fd)
    return paths


def id_list(value, limits):
    require(isinstance(value, list) and len(value) <= limits['ids'], 'INVALID_IDS')
    require(all(isinstance(x, str) and re.fullmatch(r'[A-Za-z0-9_.]+', x) for x in value), 'INVALID_IDS')
    require(len(set(value)) == len(value), 'DUPLICATE_IDS')
    return set(value)


def number(value):
    require(type(value) is int and value >= 0, 'INVALID_COUNT')
    return value


def declarations(doc, entry, limits):
    require(isinstance(doc, dict) and set(doc) == set(entry['fields']), 'UNKNOWN_REPORT_FIELD')
    require(doc.get('schema') == entry['schema'], 'INVALID_REPORT_SCHEMA')
    passed = id_list(doc['passed'], limits)
    outcomes = [id_list(doc[k], limits) for k in ('failures', 'errors', 'skipped')]
    require(not any(passed & x for x in outcomes), 'OVERLAPPING_OUTCOMES')
    require(all(not x & y for i, x in enumerate(outcomes) for y in outcomes[i+1:]), 'OVERLAPPING_OUTCOMES')
    require(number(doc['tests_run']) == len(passed) + sum(map(len, outcomes)), 'TEST_COUNT_MISMATCH')
    groups = doc['groups']; require(isinstance(groups, dict), 'INVALID_GROUPS')
    flat = []
    for group, ids in groups.items():
        values = id_list(ids, limits)
        require(all(x.split('.')[0] == group for x in values), 'INVALID_GROUP_MEMBERSHIP')
        flat.extend(values)
    require(set(flat) == passed and len(flat) == len(passed), 'GROUP_PARTITION')
    own = len(groups.get(entry['new_group'], []))
    require(number(doc['new_tests']) == own and number(doc['regression_tests']) == len(passed)-own,
            'REGRESSION_COUNT_MISMATCH')
    require(doc['status'] in {'PASS', 'FAIL'}, 'INVALID_RESULT_STATUS')
    require(doc['status'] != 'PASS' or not any(outcomes), 'RESULT_STATUS_MISMATCH')
    ui = {}
    require(sum(len(x) for x in entry['maps'].values()) <= limits['rows'], 'ROW_LIMIT')
    for field, expected in entry['maps'].items():
        mapping = doc[field]
        require(isinstance(mapping, dict) and set(mapping) == set(expected), 'MAP_ROWS_MISMATCH')
        require(len(mapping) <= limits['rows'], 'ROW_LIMIT')
        for case, ids in mapping.items():
            values = id_list(ids, limits)
            require(values and values <= passed, 'MAP_NOT_PASS')
            if case.startswith('UI'):
                ui.setdefault(case, []).append(dict(field=field, test_ids=sorted(values)))
    for key, value in doc.items():
        if key.endswith(('_remaining', '_alive', '_started', '_created', '_SIGKILL', '_normal')) and key != 'D6_started':
            number(value)
        if key.endswith('_child_exitcodes'):
            require(isinstance(value, list) and all(type(v) is int or v is None for v in value), 'INVALID_EXITCODES')
            prefix = key[:-len('_child_exitcodes')]
            require(len(value) == number(doc[prefix+'_children_started']), 'CHILD_COUNT_MISMATCH')
            require(sum(v is None for v in value) == number(doc[prefix+'_children_alive']), 'CHILD_ALIVE_MISMATCH')
            for suffix, expected in (('_children_SIGKILL', sum(v == -9 for v in value)),
                                     ('_children_normal', sum(v == 0 for v in value))):
                if prefix+suffix in doc:
                    require(number(doc[prefix+suffix]) == expected, 'EXITCODE_COUNT_MISMATCH')
    remaining = [v for k, v in doc.items() if k.endswith(('_remaining', '_alive'))]
    require(type(doc['cleanup_verified']) is bool and (not doc['cleanup_verified'] or not any(remaining)),
            'CLEANUP_MISMATCH')
    require(doc['status'] != 'PASS' or doc['cleanup_verified'], 'RESULT_CLEANUP_MISMATCH')
    # Authority/exclusion fields are declarations, never current measurements.
    for key in ('D5_closed', 'publication_authorized', 'operational_activation', 'deployment',
                'migration_promotion', 'real_provider_access', 'credentials_used', 'D6_started'):
        require(doc.get(key) is False, 'AUTHORITY_CONTRADICTION')
    for key in ('remote_requests', 'persistent_D2_writes', 'quota_consumed', 'reservations_created'):
        require(number(doc[key]) == 0, 'ACTIVITY_CONTRADICTION')
    for key in ('operations', 'operational_attempts'):
        if key in doc:
            require(number(doc[key]) == 0, 'ACTIVITY_CONTRADICTION')
    for key in ('SQL_D2_D3_D4_reexecuted', 'new_SQL'):
        if key in doc:
            require(doc[key] is False, 'EXCLUSION_CONTRADICTION')
    if 'real_evidence_criteria_not_run' in doc:
        require(number(doc['real_evidence_criteria_not_run']) == 7, 'EXCLUSION_CONTRADICTION')
    if 'global_criteria_status' in doc:
        statuses = doc['global_criteria_status']
        require(isinstance(statuses, dict) and set(statuses) == {'GI33','GI34','GI38','GI39','GI40'}, 'EXCLUSION_CONTRADICTION')
        require(all(v in {'PASS_BOUNDED_T_FIXTURE_GLOBAL_PENDING',
                          'BOUNDED_T_AND_R_EVIDENCE_GLOBAL_REVIEW_PENDING'} for v in statuses.values()),
                'EXCLUSION_CONTRADICTION')
    require(doc['global_gaps_open'] == [f'G{i:02}' for i in range(1, 8)] and doc['docs_export_not_run'] is True,
            'EXCLUSION_CONTRADICTION')
    return passed, ui


def compare_raw(raw, recorded, common, added, limits):
    """Explicit comparator for future/synthetic packets; never fabricates legacy raw."""
    require(not set(common) & set(added), 'INVALID_RAW_ADAPTER')
    require(set(raw) == set(common) and set(recorded) == set(common) | set(added), 'UNKNOWN_RAW_FIELD')
    for key in common:
        if key == 'passed':
            if id_list(raw[key], limits) != id_list(recorded[key], limits):
                return 'MISMATCH'
        elif raw[key] != recorded[key]:
            return 'MISMATCH'
    return 'MATCH'


def applicability(hist, runtime, discovery, context, declared, raw):
    if hist in {'INVALID', 'MISMATCH'} or runtime == 'INVALID' or discovery == 'INVALID' or declared == 'INCONSISTENT' or raw == 'MISMATCH':
        return 'INVALID'
    if runtime in {'CHANGED', 'MISSING'} or discovery in {'ADDED', 'REMOVED', 'ADDED_AND_REMOVED'} or context == 'DIFFERENT':
        return 'STALE'
    if hist == 'UNAVAILABLE' or context == 'NOT_RECORDED' or declared == 'NOT_RECORDED' or discovery == 'NOT_RECORDED' or raw == 'UNAVAILABLE':
        return 'UNDETERMINED'
    return 'CURRENT_RECORDED_SCOPE'


def reference_maps(doc, entry):
    """Explicit adapters only; not recursive discovery of arbitrary hash-like fields."""
    refs = []
    for field, role in entry['hash_fields'].items():
        mapping = doc[field]
        require(isinstance(mapping, dict), 'INVALID_HASH_MAP')
        refs.extend((name, value, role) for name, value in mapping.items())
    for spec in entry['references']:
        current = doc
        for key in spec['path_keys']:
            current = current[key]
        expected = spec['sha256']
        if spec['hash_keys']:
            expected = doc
            for key in spec['hash_keys']:
                expected = expected[key]
        refs.append((current, expected, spec['role']))
    for name, digest, role in refs:
        path_ok(name)
        require(isinstance(digest, str) and HASH.fullmatch(digest), 'INVALID_HASH')
        require(role in {'runtime', 'documentary', 'preserved'}, 'INVALID_ROLE')
    return sorted(set(refs))


def validate_registry(registry, limits):
    require(set(registry) == {'schema', 'entries', 'UI_obligations', 'limitations'}, 'INVALID_REGISTRY')
    require(registry['schema'] == 'd5.evidence-registry.v1', 'INVALID_REGISTRY')
    entries = registry['entries']
    require(isinstance(entries, list) and 0 < len(entries) <= limits['entries'], 'ENTRY_LIMIT')
    ids = set(); paths = set()
    fields = {'id', 'kind', 'path', 'commit', 'sha256', 'schema', 'fields', 'hash_fields',
              'references', 'dependency_commit', 'dependency_paths', 'target', 'maps', 'new_group'}
    for e in entries:
        require(set(e) == fields and re.fullmatch(r'[A-Z0-9_-]+', e['id']), 'INVALID_ENTRY')
        require(e['id'] not in ids, 'DUPLICATE_ENTRY'); ids.add(e['id'])
        require(e['kind'] in {'campaign', 'preserved', 'obligations'}, 'INVALID_ENTRY_KIND')
        if e['kind'] == 'obligations':
            require(not any(e[k] for k in ('hash_fields','references','dependency_paths','maps')), 'INVALID_OBLIGATION_ENTRY')
        path_ok(e['path']); paths.add(e['path'])
        require(OID.fullmatch(e['commit']) and OID.fullmatch(e['dependency_commit']), 'INVALID_OID')
        require(HASH.fullmatch(e['sha256']) and PUBLIC.fullmatch(e['target']), 'INVALID_ENTRY')
        require(len(e['maps']) <= limits['rows'], 'ROW_LIMIT')
        require(len(e['dependency_paths']) == len(set(e['dependency_paths'])), 'DUPLICATE_PATH')
        for name in e['dependency_paths']:
            paths.add(path_ok(name))
    require(len(paths) <= limits['paths'], 'PATH_LIMIT')
    obligations = registry['UI_obligations']
    require(set(obligations) == {f'UI{i:02}' for i in range(1, 41)}, 'INVALID_OBLIGATIONS')
    for case, value in obligations.items():
        require(set(value) == {'GI', 'mode', 'obligation'} and value['mode'] in {'M', 'F', 'R'}, 'INVALID_OBLIGATIONS')
        require(value['GI'] in {'GI33', 'GI34', 'GI38', 'GI39', 'GI40'}, 'INVALID_OBLIGATIONS')
        require(isinstance(value['obligation'], str), 'INVALID_OBLIGATIONS')


def audit(root, registry=None, limits=None):
    limits = dict(LIMITS, **(limits or {}))
    reader = Reader(root, limits); git = Git(root, reader, limits)
    findings = []; entries = []; campaigns = {}; ui = {}
    def finding(code, entry=None, path=None):
        row = dict(code=code)
        if entry:
            row['entry'] = entry
        if path:
            row['path'] = path_ok(path)
        findings.append(row)
    try:
        if registry is None:
            registry = strict_json(reader.read(REGISTRY), limits)
        validate_registry(registry, limits)
        for e in registry['entries']:
            phase = 'historical'
            row = dict(id=e['id'], target=e['target'], historical_integrity='MATCH',
                       recorded_files_now={'runtime': 'MATCH', 'documentary': 'MATCH', 'preserved': 'MATCH'},
                       discovery_now='NOT_RECORDED', runtime_context='NOT_RECORDED',
                       declarations='NOT_RECORDED', raw_binding='NOT_RECORDED', sufficiency='REVIEW_PENDING',
                       verified_hash_entries=0, declared_execution='HISTORICAL_NOT_RERUN',
                       embedded_configuration='BOUND_TO_RECORDED_BYTES_ONLY',
                       external_capabilities='NOT_RECORDED')
            row['historical_inputs_verified'] = False
            entries.append(row)
            try:
                blob = git.load(e['commit'], [e['path']])[e['path']]
                require(sha(blob) == e['sha256'], 'HISTORICAL_DOCUMENT_MISMATCH')
                phase = 'declarations'
                if e['kind'] == 'obligations':
                    refs = []
                    row['declarations'] = 'NOT_RECORDED'
                else:
                    doc = strict_json(blob, limits)
                    require(set(doc) == set(e['fields']), 'UNKNOWN_REPORT_FIELD')
                    refs = reference_maps(doc, e)
                    require({name for name, _, _ in refs} == set(e['dependency_paths']), 'DEPENDENCY_SET_MISMATCH')
                    phase = 'historical'
                    dep_blobs = git.load(e['dependency_commit'], e['dependency_paths'])
                    checks = [(e['path'], e['sha256'], 'documentary', blob)] + [
                        (name, digest, role, dep_blobs[name]) for name, digest, role in refs]
                    for _, digest, _, historical in checks:
                        require(sha(historical) == digest, 'HISTORICAL_INPUT_MISMATCH')
                    row['verified_hash_entries'] = len(checks)
                    row['historical_inputs_verified'] = True
                    phase = 'declarations'
                    if e['kind'] == 'campaign':
                        passed, mapping = declarations(doc, e, limits)
                        campaigns[e['id']] = passed
                        ui[e['id']] = mapping
                        row.update(declarations='CONSISTENT', declared_execution='HISTORICAL_PYTHON_NOT_RERUN',
                                   declared_tests=doc['tests_run'], declared_new=doc['new_tests'],
                                   declared_regressions=doc['regression_tests'], declared_result=doc['status'])
                        versions = (doc.get('python'), doc.get('platform'))
                        row['runtime_context'] = ('NOT_RECORDED' if None in versions else
                            'MATCH_DECLARED' if versions == (platform.python_version(), platform.system()) else 'DIFFERENT')
                        phase = 'historical'
                        expected = selected(git.tree(e['commit']), e['id'])
                        require(expected == set(doc['inputs']), 'HISTORICAL_DISCOVERY_MISMATCH')
                        phase = 'discovery'
                        now = discover(reader, e['id'])
                        added, removed = sorted(now-expected), sorted(expected-now)
                        row['discovery_now'] = ('ADDED_AND_REMOVED' if added and removed else
                                               'ADDED' if added else 'REMOVED' if removed else 'SAME')
                        row['discovery_added'], row['discovery_removed'] = added, removed
                        for name in added+removed:
                            finding('DISCOVERY_CHANGED', e['id'], name)
                    else:
                        row['declarations'] = 'CONSISTENT'
                        row['historical_test_groups'] = doc.get('test_groups', doc.get('recorded_runtime_evidence', {}).get('groups', {}))
                        # Output only known group names/targets and numeric counts, not arbitrary document data.
                        row['historical_test_groups'] = {k: {a: b for a, b in v.items()
                            if re.fullmatch(r'[A-Za-z0-9_]+', a) and type(b) is int}
                            for k, v in row['historical_test_groups'].items()
                            if re.fullmatch(r'[A-Za-z0-9_]+', k) and isinstance(v, dict)}
                        original_groups = doc.get('test_groups', doc.get('recorded_runtime_evidence', {}).get('groups', {}))
                        for k, v in row['historical_test_groups'].items():
                            target = original_groups[k].get('target')
                            v['target'] = target if isinstance(target, str) and PUBLIC.fullmatch(target) else 'NOT_RECORDED'
                if e['kind'] == 'obligations':
                    checks = [(e['path'], e['sha256'], 'documentary', blob)]
                    row['historical_inputs_verified'] = True
                    row['verified_hash_entries'] = 1
                row['preservation_paths'] = sorted(e['dependency_paths']) if e['kind'] == 'preserved' else []
                for name, digest, role, historical in checks:
                    phase = 'current'
                    try:
                        now_blob = reader.read(name)
                        if sha(now_blob) != digest:
                            if row['recorded_files_now'][role] != 'MISSING':
                                row['recorded_files_now'][role] = 'CHANGED'
                            finding('CURRENT_BYTES_CHANGED', e['id'], name)
                    except FileNotFoundError:
                        row['recorded_files_now'][role] = 'MISSING'
                        finding('CURRENT_FILE_MISSING', e['id'], name)
                if e['kind'] == 'campaign':
                    row['applicability'] = applicability(row['historical_integrity'], row['recorded_files_now']['runtime'],
                        row['discovery_now'], row['runtime_context'], row['declarations'], row['raw_binding'])
                else:
                    row['applicability'] = 'NOT_APPLICABLE_HISTORICAL_REFERENCE'
            except Fault as err:
                if err.code == 'UNSTABLE_SNAPSHOT':
                    raise
                if phase == 'historical' or err.unavailable:
                    row['historical_integrity'] = ('UNAVAILABLE' if err.unavailable or err.code == 'HISTORICAL_PATH_UNAVAILABLE'
                                                   else 'MISMATCH' if err.code.startswith('HISTORICAL_') else 'INVALID')
                row['applicability'] = 'UNDETERMINED' if err.unavailable or err.code == 'HISTORICAL_PATH_UNAVAILABLE' else 'INVALID'
                if phase == 'declarations':
                    row['declarations'] = 'INCONSISTENT'
                    if not row['historical_inputs_verified']:
                        row['historical_integrity'] = 'INVALID'
                elif phase == 'current':
                    row['recorded_files_now'][role] = 'INVALID'
                elif phase == 'discovery':
                    row['discovery_now'] = 'INVALID'
                finding(err.code, e['id'])
        reader.finish()
        require(time.monotonic()-git.started <= limits['total_seconds'], 'GIT_BUDGET')
        coverage = []
        for case, obligation in registry['UI_obligations'].items():
            sources = [{ 'campaign': campaign, 'maps': mapping[case]}
                       for campaign, mapping in ui.items() if case in mapping]
            coverage.append(dict(id=case, GI=obligation['GI'], mode=obligation['mode'],
                                 obligation_reference='I33_UI_MATRIX',
                                 declared_sources=sources, sufficiency='REVIEW_PENDING',
                                 evidence='DECLARED_BOUNDED_FIXTURE' if sources else 'NOT_RECORDED'))
        overlaps = []
        names = sorted(campaigns)
        for i, left in enumerate(names):
            for right in names[i+1:]:
                overlaps.append(dict(left=left, right=right,
                                     shared_test_ids=len(campaigns[left] & campaigns[right]),
                                     totals_must_not_be_added=True))
        invalid = any(x.get('applicability') == 'INVALID' for x in entries)
        unresolved = any(x.get('applicability') in {'STALE', 'UNDETERMINED'} for x in entries)
        code = 2 if invalid else 1 if findings or unresolved else 0
        result = dict(schema='d5.evidence-audit.v1', audit_status='INVALID' if invalid else 'FINDINGS' if code else 'CONSISTENT',
                      entries=entries, findings=findings, UI_inventory=coverage, campaign_intersections=overlaps,
                      raw_binding_counts={k: sum(e['raw_binding'] == k for e in entries if e['id'] in campaigns)
                                          for k in ('MATCH','MISMATCH','NOT_RECORDED','UNAVAILABLE')},
                      D5_closed=False, global_gaps_open=[f'G{i:02}' for i in range(1,8)], sufficiency='REVIEW_PENDING',
                      real_evidence_criteria_not_run=7, functional_campaigns_reexecuted=False,
                      external_capabilities='NOT_RECORDED',
                      D1_D2_preservation='EXPLICIT_REFERENCES_ONLY_NOT_EXHAUSTIVE',
                      D1_D2_target_extensions='NOT_RECORDED',
                      SQL_D1_D2_D3_D4_reexecuted=False, operational_activation=False, publication_authorized=False,
                      git_calls=git.calls, bytes_read=reader.bytes, exit_code=code)
        require(len(json.dumps(result).encode()) <= limits['output_bytes'], 'OUTPUT_LIMIT')
        return result, code
    except (Fault, OSError, ValueError, KeyError, TypeError, RecursionError) as err:
        unstable = isinstance(err, Fault) and err.code == 'UNSTABLE_SNAPSHOT'
        code = err.code if isinstance(err, Fault) else 'INVALID_INPUT_OR_IO'
        return dict(schema='d5.evidence-audit.v1', audit_status='FINDINGS' if unstable else 'INVALID',
                    applicability='UNDETERMINED' if unstable else 'INVALID', findings=[dict(code=code)],
                    sufficiency='REVIEW_PENDING', D5_closed=False, publication_authorized=False,
                    global_gaps_open=[f'G{i:02}' for i in range(1,8)], exit_code=1 if unstable else 2), 1 if unstable else 2


def main():
    if len(sys.argv) != 1:
        print('{"audit_status":"INVALID","findings":[{"code":"ARGUMENTS_NOT_ALLOWED"}],"exit_code":2}')
        return 2
    root = Path(__file__).absolute().parent.parent
    result, code = audit(root)
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
