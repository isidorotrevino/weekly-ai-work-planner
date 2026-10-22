# SPDX-License-Identifier: GPL-3.0-only
"""Owned, temporary, synthetic Drive page capture. No provider/D2 integration.

Commit objects carry complete pages and cursor states; only the validated HEAD
chain is authoritative. Filesystem/process recovery is not hostile-owner, disk,
power-loss or remote-provider conformance. Test fault points are constructor-only.
"""
import base64
from contextlib import contextmanager
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import tempfile
import uuid

from .offline import ContractError, MemoryLab
from .preview import MAX_BYTES, _directory

MAX_EVENTS = 16
MAX_OBJECT = 32 * 1024 * 1024
MAX_COMMITS = 1024
HEX = re.compile(r'[0-9a-f]{64}')


class IncrementalError(ValueError):
    pass


def fail(code):
    raise IncrementalError(code)


def shape(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        fail('INVALID_FIELDS')


def text(value, maximum=256):
    if type(value) is not str or not 1 <= len(value) <= maximum or any(ord(c) < 32 or ord(c) == 127 for c in value):
        fail('INVALID_TEXT')
    try:
        value.encode('utf-8')
    except UnicodeError:
        fail('INVALID_TEXT')
    return value


def identity(value):
    try:
        if type(value) is not str or str(uuid.UUID(value)) != value:
            fail('INVALID_ID')
    except (ValueError, AttributeError):
        fail('INVALID_ID')
    return value


def number(value):
    if type(value) is not int or not 0 <= value < 2**63:
        fail('INVALID_NUMBER')
    return value


def hash_value(value):
    if type(value) is not str or not HEX.fullmatch(value):
        fail('INVALID_HASH')
    return value


def encode(value):
    try:
        data = (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    except (TypeError, ValueError, RecursionError):
        fail('INVALID_JSON')
    if len(data) > MAX_OBJECT:
        fail('OBJECT_LIMIT')
    return data


def decode(data):
    if type(data) is not bytes or len(data) > MAX_OBJECT:
        fail('OBJECT_LIMIT')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                fail('DUPLICATE_KEY')
            result[key] = value
        return result
    try:
        return json.loads(data, object_pairs_hook=unique, parse_constant=lambda _: fail('INVALID_JSON'))
    except (ValueError, UnicodeError, RecursionError):
        fail('INVALID_JSON')


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def scope_value(value):
    shape(value, ('schema', 'mode', 'project_id', 'connector_id', 'principal', 'corpus',
                  'drive', 'policy_version', 'export_mime', 'allowlist'))
    if value['schema'] != 'd5.fixture-drive-scope.v1' or value['mode'] != 'SYNTHETIC_ONLY' or value['export_mime'] != 'text/plain':
        fail('SYNTHETIC_SCOPE_REQUIRED')
    identity(value['project_id']); identity(value['connector_id'])
    for name in ('principal', 'corpus', 'drive', 'policy_version'):
        text(value[name])
    if type(value['allowlist']) is not list or not 1 <= len(value['allowlist']) <= 1024:
        fail('INVALID_ALLOWLIST')
    files, docs = set(), set()
    for item in value['allowlist']:
        shape(item, ('file_id', 'document_id', 'profile'))
        text(item['file_id']); identity(item['document_id']); text(item['profile'])
        if item['file_id'] in files or item['document_id'] in docs:
            fail('DUPLICATE_ALLOWLIST_ID')
        files.add(item['file_id']); docs.add(item['document_id'])
    result = deepcopy(value)
    result['allowlist'].sort(key=lambda x: x['file_id'])
    encode(result)
    return result


def file_event(file_id, content=b'', *, version='fixture-1', mime='text/markdown',
               outcome='AVAILABLE', changed=False):
    """Trusted fixture builder; not a Google response parser."""
    if type(content) is not bytes:
        fail('INVALID_FIXTURE_BYTES')
    available = outcome == 'AVAILABLE'
    size = len(content) if available else None
    if available and size > MAX_BYTES:
        outcome, available = 'TOO_LARGE', False
    return dict(change_type='file', file_id=file_id, outcome=outcome, version=version,
                mime_type=mime, content_base64=base64.b64encode(content).decode() if available else None,
                declared_size=size, after_version=version,
                repeated_bytes_equal=not changed)


def page(scope, state, events, *, next_token=None, new_start=None):
    return dict(schema='d5.fixture-drive-page.v1', scope_sha256=digest(scope_value(scope)),
                phase=state['phase'], request_token=state['token'], events=deepcopy(events),
                next_page_token=next_token, new_start_page_token=new_start)


def request(command_id, snapshot, fixture_page):
    return dict(schema='d5.fixture-drive-command.v1', command_id=command_id,
                expected_version=snapshot['version'], expected_head=snapshot['head_sha256'],
                page=deepcopy(fixture_page))


def initial_state(anchor):
    text(anchor)
    return dict(phase='INVENTORY', anchor=anchor, token=None, continuations=[])


def prepare_page(scope, before, value):
    shape(value, ('schema', 'scope_sha256', 'phase', 'request_token', 'events',
                  'next_page_token', 'new_start_page_token'))
    if value['schema'] != 'd5.fixture-drive-page.v1' or value['scope_sha256'] != digest(scope):
        fail('INCOMPATIBLE_SCOPE')
    if value['phase'] != before['phase'] or value['request_token'] != before['token']:
        fail('CONFLICT_CURSOR')
    events = value['events']
    if type(events) is not list or len(events) > MAX_EVENTS:
        fail('PAGE_EVENT_LIMIT')
    nxt, terminal = value['next_page_token'], value['new_start_page_token']
    if nxt is not None: text(nxt)
    if terminal is not None: text(terminal)
    after = deepcopy(before)
    if before['phase'] == 'INVENTORY':
        if terminal is not None:
            fail('INVALID_PAGE_TOKENS')
        if nxt is None:
            after.update(phase='CATCHUP', token=before['anchor'], continuations=[before['anchor']])
        else:
            if nxt == before['token'] or nxt in before['continuations']:
                fail('CONTINUATION_CYCLE')
            after.update(token=nxt, continuations=before['continuations'] + [nxt])
    else:
        if (nxt is None) == (terminal is None):
            fail('INVALID_PAGE_TOKENS')
        if nxt is not None:
            if nxt == before['token'] or nxt in before['continuations']:
                fail('CONTINUATION_CYCLE')
            after.update(token=nxt, continuations=before['continuations'] + [nxt])
        else:
            if terminal in before['continuations'] and not (terminal == before['token'] and not events):
                fail('CONTINUATION_CYCLE')
            after.update(phase='FOLLOWING', token=terminal, continuations=[terminal])
    mapping = {x['file_id']: x for x in scope['allowlist']}
    results = []
    for index, event in enumerate(events):
        results.append(event_result(scope, mapping, index, event))
    return results, after


def event_result(scope, mapping, index, event):
    shape(event, ('change_type', 'file_id', 'outcome', 'version', 'mime_type',
                  'content_base64', 'declared_size', 'after_version', 'repeated_bytes_equal'))
    if event['change_type'] not in ('file', 'drive'):
        fail('INVALID_CHANGE_TYPE')
    outcome = event['outcome']
    if outcome not in ('AVAILABLE', 'TOO_LARGE', 'REMOVED', 'ACCESS_DENIED', 'NOT_FOUND',
                        'TIMEOUT', 'RATE_LIMIT', 'AUTH_FAILURE', 'SCOPE_INVALID'):
        fail('INVALID_EVENT_OUTCOME')
    if type(event['repeated_bytes_equal']) is not bool:
        fail('INVALID_EVENT')
    for key in ('version', 'mime_type', 'after_version'):
        text(event[key])
    if event['change_type'] == 'file':
        text(event['file_id'])
    elif event['file_id'] is not None:
        fail('INVALID_EVENT')
    if outcome in ('AUTH_FAILURE', 'SCOPE_INVALID'):
        fail('BLOCKED_CONNECTOR')
    if outcome in ('TIMEOUT', 'RATE_LIMIT'):
        fail('TRANSIENT_PAGE')
    if outcome != 'AVAILABLE' and event['content_base64'] is not None:
        fail('INVALID_EVENT')
    base = dict(index=index, file_id=event['file_id'], authority='SYNTHETIC_FIXTURE')
    def diagnostic(code):
        return dict(base, status='TERMINAL_DIAGNOSTIC', code=code, capture=None,
                    observation_key=None, metadata=dict(version=event['version'], mime_type=event['mime_type']))
    if event['change_type'] == 'drive':
        if outcome != 'AVAILABLE':
            fail('BLOCKED_CONNECTOR')
        return diagnostic('NON_FILE_CHANGE')
    if outcome == 'REMOVED':
        return diagnostic('REMOVED_OR_ACCESS_LOST')
    if outcome in ('ACCESS_DENIED', 'NOT_FOUND'):
        return diagnostic('UNAVAILABLE_CONFIRMED')
    if event['file_id'] not in mapping:
        return diagnostic('OUTSIDE_ALLOWLIST')
    item = mapping[event['file_id']]
    if event['mime_type'] not in ('text/markdown', 'text/plain', 'application/vnd.google-apps.document'):
        return diagnostic('UNSUPPORTED_MIME')
    if outcome == 'TOO_LARGE':
        if number(event['declared_size']) <= MAX_BYTES:
            fail('INVALID_SIZE_DIAGNOSTIC')
        return diagnostic('SOURCE_SIZE_LIMIT')
    if type(event['content_base64']) is not str or len(event['content_base64']) > 4 * ((MAX_BYTES + 2) // 3):
        fail('INVALID_SOURCE_ENCODING')
    try:
        content = base64.b64decode(event['content_base64'], validate=True)
    except ValueError:
        fail('INVALID_SOURCE_ENCODING')
    if len(content) != number(event['declared_size']):
        fail('INVALID_SOURCE_SIZE')
    if not event['repeated_bytes_equal'] or event['version'] != event['after_version']:
        fail('TRANSIENT_PAGE')
    before_meta = dict(scope=digest(scope), file_id=event['file_id'], version=event['version'], mime_type=event['mime_type'])
    export = event['mime_type'] == 'application/vnd.google-apps.document'
    lab = MemoryLab()
    try:
        cap = lab.capture(content, scope['project_id'], item['document_id'], profile=item['profile'],
                          source_kind='DRIVE_DOCS_EXPORT' if export else 'DRIVE_BLOB',
                          revision=event['version'], metadata_before=before_meta, metadata_after=before_meta)
        capture = lab.capture_artifact(cap)
    except ContractError as ex:
        if str(ex) != 'INVALID_SOURCE':
            fail('CAPTURE_VALIDATION_FAILED')
        capture = dict(schema='d5.fixture-blocked-capture.v1', content_base64=event['content_base64'],
                       content_sha256=hashlib.sha256(content).hexdigest(), profile=item['profile'],
                       document_id=item['document_id'], metadata_before=before_meta,
                       provenance_grade='OBSERVED_EXPORT' if export else 'SYNTHETIC_OBSERVATION',
                       export_mime='text/plain' if export else None, diagnostics=['INVALID_SOURCE'], state='BLOCKED')
    key = digest(dict(scope=digest(scope), file_id=event['file_id'], document_id=item['document_id'],
                      profile=item['profile'], metadata=before_meta, grade=capture['provenance_grade'],
                      export_mime=capture.get('export_mime'), content_sha256=capture['content_sha256']))
    return dict(base, status='CAPTURED_BLOCKED' if capture['state'] == 'BLOCKED' else 'CAPTURED',
                code=None, capture=capture, observation_key=key)


def receipt(command_id, request_hash, version):
    return dict(schema='d5.fixture-drive-receipt.v1', command_id=command_id,
                request_sha256=request_hash, version=version, result='SYNTHETIC_CAPTURE_CONFIRMED',
                reference_selected=False, persistent_D2_writes=0, remote_requests=0)


class FixtureStore:
    """Open only a harness-created root with explicit expected identity/scope."""
    def __init__(self, root, run_id, scope, *, test_fault=None, test_ready=None):
        self.root = Path(root)
        self.run_id = identity(run_id)
        self.scope = scope_value(scope)
        self.scope_hash = digest(self.scope)
        if test_fault not in (None, 'before_object', 'after_object', 'before_replace', 'after_head', 'fsync_failure', 'prepared'):
            fail('INVALID_TEST_FAULT')
        self._fault, self._ready = test_fault, test_ready

    @staticmethod
    def _read(fd, name, limit=MAX_OBJECT):
        handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            info = os.fstat(handle)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_size > limit:
                fail('UNSAFE_OR_OVERSIZED_FILE')
            with os.fdopen(handle, 'rb') as stream:
                handle = None
                data = stream.read(limit + 1)
                after = os.fstat(stream.fileno())
            if len(data) > limit or (info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                fail('UNSTABLE_FILE')
            return data
        finally:
            if handle is not None: os.close(handle)

    @staticmethod
    def _write(fd, name, data):
        handle = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        with os.fdopen(handle, 'wb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())

    @contextmanager
    def _locked(self, exclusive=False):
        root = lock = objects = None
        try:
            root = _directory(self.root)
            info = os.fstat(root)
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                fail('UNSAFE_ROOT')
            lock = os.open('lock', os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=root)
            li = os.fstat(lock)
            if not stat.S_ISREG(li.st_mode) or li.st_nlink != 1 or li.st_uid != os.getuid() or li.st_mode & 0o077:
                fail('UNSAFE_LOCK')
            fcntl.flock(lock, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
            owner = decode(self._read(root, 'owner.json'))
            if owner != dict(schema='d5.fixture-drive-owner.v1', mode='SYNTHETIC_ONLY', run_id=self.run_id, scope_sha256=self.scope_hash):
                fail('WRONG_OWNER')
            if self._read(root, 'scope.json') != encode(self.scope):
                fail('INCOMPATIBLE_SCOPE')
            objects = os.open('objects', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root)
            oi = os.fstat(objects)
            if oi.st_uid != os.getuid() or oi.st_mode & 0o077:
                fail('UNSAFE_OBJECT_DIRECTORY')
            yield root, objects
        except OSError:
            fail('FILESYSTEM_REJECTED')
        finally:
            if objects is not None: os.close(objects)
            if lock is not None: os.close(lock)
            if root is not None: os.close(root)

    def _genesis(self, anchor, command_id):
        state = initial_state(anchor)
        request_hash = digest(dict(run_id=self.run_id, scope_sha256=self.scope_hash, anchor=anchor))
        return dict(schema='d5.fixture-drive-commit.v1', run_id=self.run_id, scope_sha256=self.scope_hash,
                    version=0, parent=None, command_id=identity(command_id), request_sha256=request_hash,
                    request=None, state_before=None, state_after=state, results=[], receipt=receipt(command_id, request_hash, 0))

    def _commit(self, req, prior, parent):
        shape(req, ('schema', 'command_id', 'expected_version', 'expected_head', 'page'))
        if req['schema'] != 'd5.fixture-drive-command.v1': fail('INVALID_COMMAND')
        identity(req['command_id']); number(req['expected_version']); hash_value(req['expected_head'])
        if req['expected_version'] != prior['version'] or req['expected_head'] != parent:
            fail('CONFLICT_HEAD')
        if prior['version'] + 1 >= MAX_COMMITS: fail('HISTORY_LIMIT')
        results, state = prepare_page(self.scope, prior['state_after'], req['page'])
        request_hash = digest(req)
        return dict(schema='d5.fixture-drive-commit.v1', run_id=self.run_id, scope_sha256=self.scope_hash,
                    version=prior['version'] + 1, parent=parent, command_id=req['command_id'], request_sha256=request_hash,
                    request=deepcopy(req), state_before=prior['state_after'], state_after=state,
                    results=results, receipt=receipt(req['command_id'], request_hash, prior['version'] + 1))

    def _load(self, root, objects):
        head = decode(self._read(root, 'head.json'))
        shape(head, ('schema', 'run_id', 'scope_sha256', 'version', 'commit_sha256'))
        if head['schema'] != 'd5.fixture-drive-head.v1' or head['run_id'] != self.run_id or head['scope_sha256'] != self.scope_hash:
            fail('CORRUPT_HEAD')
        number(head['version']); current = hash_value(head['commit_sha256'])
        chain, seen = [], set()
        while current is not None:
            if current in seen or len(chain) >= MAX_COMMITS: fail('CORRUPT_CHAIN')
            seen.add(current)
            data = self._read(objects, hash_value(current) + '.json')
            if hashlib.sha256(data).hexdigest() != current: fail('CORRUPT_OBJECT')
            value = decode(data)
            shape(value, ('schema', 'run_id', 'scope_sha256', 'version', 'parent', 'command_id',
                          'request_sha256', 'request', 'state_before', 'state_after', 'results', 'receipt'))
            identity(value['command_id'])
            if value['parent'] is not None: hash_value(value['parent'])
            chain.append((current, value)); current = value['parent']
        chain.reverse()
        commands = set()
        for index, (sha, value) in enumerate(chain):
            if value['version'] != index or value['command_id'] in commands: fail('CORRUPT_CHAIN')
            commands.add(value['command_id'])
            if index == 0:
                try: expected = self._genesis(value['state_after']['anchor'], value['command_id'])
                except (TypeError, KeyError): fail('CORRUPT_GENESIS')
            else:
                expected = self._commit(value['request'], chain[index-1][1], chain[index-1][0])
            if encode(expected) != encode(value): fail('CORRUPT_COMMIT')
        if not chain or chain[-1][1]['version'] != head['version']: fail('CORRUPT_HEAD')
        return head, chain

    def _checkpoint(self, point):
        if self._fault == point:
            if point == 'fsync_failure': raise OSError('injected fixture failure')
            if self._ready is None: fail('TEST_NOTIFIER_REQUIRED')
            self._ready.send(point)
            if point == 'prepared':
                if self._ready.recv() != 'CONTINUE': fail('INVALID_TEST_CONTROL')
                return
            while True: signal.pause()

    def _publish(self, root, objects, value):
        data = encode(value); sha = hashlib.sha256(data).hexdigest()
        temporary = '.object-' + str(uuid.uuid4())
        head_temporary = '.head-' + str(uuid.uuid4())
        replaced = False
        try:
            self._checkpoint('before_object')
            self._write(objects, temporary, data)
            try:
                os.link(temporary, sha + '.json', src_dir_fd=objects, dst_dir_fd=objects, follow_symlinks=False)
            except FileExistsError:
                # Only unreachable identical objects can be reused; no replacement.
                if self._read(objects, sha + '.json') != data: fail('OBJECT_COLLISION')
            os.unlink(temporary, dir_fd=objects)
            os.fsync(objects)
            self._checkpoint('after_object')
            head = dict(schema='d5.fixture-drive-head.v1', run_id=self.run_id,
                        scope_sha256=self.scope_hash, version=value['version'], commit_sha256=sha)
            self._write(root, head_temporary, encode(head))
            self._checkpoint('before_replace')
            os.replace(head_temporary, 'head.json', src_dir_fd=root, dst_dir_fd=root)
            replaced = True
            self._checkpoint('fsync_failure')
            os.fsync(root)
            self._checkpoint('after_head')
            return sha
        except OSError:
            fail('UNKNOWN_COMMIT' if replaced else 'IO_NOT_CONFIRMED')
        finally:
            for fd, name in [(objects, temporary), (root, head_temporary)]:
                try: os.unlink(name, dir_fd=fd)
                except FileNotFoundError: pass

    @staticmethod
    def _confirm_observed_head(root, objects):
        # Recovery may observe a valid rename whose directory fsync failed.
        # Do not emit a confirmed receipt until that visible authority is synced.
        try:
            os.fsync(objects)
            os.fsync(root)
        except OSError:
            fail('UNKNOWN_COMMIT')

    def advance(self, value):
        req = decode(value if type(value) is bytes else encode(value))
        shape(req, ('schema', 'command_id', 'expected_version', 'expected_head', 'page'))
        identity(req['command_id']); request_hash = digest(req)
        # Full deterministic preparation before the lock, with no published effect.
        with self._locked() as (root, objects):
            _, old_chain = self._load(root, objects)
            for sha, old in old_chain:
                if old['command_id'] == req['command_id']:
                    if old['request_sha256'] != request_hash: fail('CONFLICT_COMMAND')
                    self._confirm_observed_head(root, objects)
                    return dict(old['receipt'], commit_sha256=sha)
        self._commit(req, old_chain[-1][1], old_chain[-1][0])
        self._checkpoint('prepared')
        with self._locked(True) as (root, objects):
            _, chain = self._load(root, objects)
            for sha, old in chain:
                if old['command_id'] == req['command_id']:
                    if old['request_sha256'] != request_hash: fail('CONFLICT_COMMAND')
                    self._confirm_observed_head(root, objects)
                    return dict(old['receipt'], commit_sha256=sha)
            commit = self._commit(req, chain[-1][1], chain[-1][0])
            sha = self._publish(root, objects, commit)
            return dict(commit['receipt'], commit_sha256=sha)

    def snapshot(self):
        with self._locked() as (root, objects):
            head, chain = self._load(root, objects)
        occurrences = [r for _, v in chain for r in v['results']]
        return dict(schema='d5.fixture-drive-snapshot.v1', run_id=self.run_id,
                    version=head['version'], head_sha256=head['commit_sha256'],
                    state=deepcopy(chain[-1][1]['state_after']), committed_pages=len(chain)-1,
                    occurrences=len(occurrences), logical_observations=len({r['observation_key'] for r in occurrences if r['observation_key']}),
                    terminal_diagnostics=sum(r['status'] == 'TERMINAL_DIAGNOSTIC' for r in occurrences),
                    reference_selected=False, persistent_D2_writes=0, remote_requests=0)

    def read_command(self, command_id, request_hash):
        identity(command_id); hash_value(request_hash)
        with self._locked() as (root, objects):
            _, chain = self._load(root, objects)
            self._confirm_observed_head(root, objects)
            for sha, value in chain:
                if value['command_id'] == command_id:
                    if value['request_sha256'] != request_hash: fail('CONFLICT_COMMAND')
                    return dict(value['receipt'], commit_sha256=sha)
            return dict(result='NOT_COMMITTED_AT_HEAD')

    def inspect(self):
        """Private fixture data: full bytes, unlike snapshot/receipt summaries."""
        with self._locked() as (root, objects):
            _, chain = self._load(root, objects)
        return deepcopy(chain)


class TemporaryFixtureLab:
    """Own exactly one new private root. No cleanup API for arbitrary paths."""
    created_roots = []

    def __init__(self, scope, anchor='fixture-anchor'):
        self.scope = scope_value(scope); text(anchor)
        self.run_id = str(uuid.uuid4())
        self.root = Path(tempfile.mkdtemp(prefix='d5-drive-'))
        info = self.root.lstat(); self._identity = (info.st_dev, info.st_ino)
        self.created_roots.append(str(self.root))
        self.store = FixtureStore(self.root, self.run_id, self.scope)
        try:
            root = _directory(self.root)
            try:
                FixtureStore._write(root, 'owner.json', encode(dict(schema='d5.fixture-drive-owner.v1',
                    mode='SYNTHETIC_ONLY', run_id=self.run_id, scope_sha256=digest(self.scope))))
                FixtureStore._write(root, 'scope.json', encode(self.scope))
                FixtureStore._write(root, 'lock', b'')
                os.mkdir('objects', mode=0o700, dir_fd=root)
                objects = os.open('objects', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root)
                try: self.store._publish(root, objects, self.store._genesis(anchor, str(uuid.uuid4())))
                finally: os.close(objects)
            finally: os.close(root)
        except BaseException:
            self.close(); raise

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        if not self.root.exists() and not self.root.is_symlink(): return
        info = self.root.lstat()
        if not stat.S_ISDIR(info.st_mode) or (info.st_dev, info.st_ino) != self._identity:
            fail('CLEANUP_OWNERSHIP_CHANGED')
        # Identity was retained by this creator, independently of mutable markers.
        shutil.rmtree(self.root)
