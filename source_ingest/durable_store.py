# SPDX-License-Identifier: GPL-3.0-only
"""Bounded Linux fixture commits. No transport or production persistence claim.

Reducers are closed pure fixture transitions. Hooks are trusted test controls.
Reads/receipts confirm only a fully checked, fsynced reachable chain.
"""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid


class DurableError(ValueError):
    pass


def fail(code):
    raise DurableError(code)


def shape(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        fail('INVALID_SHAPE')


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        fail('INVALID_INTEGER')
    return value


def identifier(value):
    try:
        if type(value) is not str or str(uuid.UUID(value)) != value:
            fail('INVALID_ID')
    except (ValueError, AttributeError):
        fail('INVALID_ID')
    return value


def hash_id(value):
    if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        fail('INVALID_HASH')
    return value


def _tree(value):
    if value is None or type(value) in (str, int, bool):
        return
    if type(value) is list:
        for v in value:
            _tree(v)
    elif type(value) is dict and all(type(k) is str for k in value):
        for v in value.values():
            _tree(v)
    else:
        fail('INVALID_JSON')


def canonical(value):
    try:
        _tree(value)
        return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                          separators=(',', ':')).encode('utf-8')
    except (UnicodeError, RecursionError, TypeError, ValueError) as ex:
        if isinstance(ex, DurableError):
            raise
        fail('INVALID_JSON')


def decode(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                fail('DUPLICATE_KEY')
            result[k] = v
        return result
    try:
        value = json.loads(raw, object_pairs_hook=pairs)
        if canonical(value) != raw:
            fail('NONCANONICAL_JSON')
        return value
    except (ValueError, UnicodeError, RecursionError) as ex:
        if isinstance(ex, DurableError):
            raise
        fail('INVALID_JSON')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def copy(value):
    return decode(canonical(value))


LIMITS = dict(commits=256, commands=128, commit_bytes=32*1024*1024,
              store_bytes=256*1024*1024, proof_bytes=65536)


def receipt(cid, rh, result, before, after, seq):
    return dict(schema='d5.durable-receipt.v1', command_id=cid, request_sha256=rh,
                result=result, before_seq=seq-1, seq=seq, before_state_sha256=digest(before),
                after_data_sha256=digest(after), grants_execution_authority=False,
                quota_consumed=0, reservations_created=0, activation_allowed=False)


class Store:
    """One fixed-role store; no implicit create/open repair or garbage collection."""
    def __init__(self, path, run_id, store_id, role, reducer, genesis, *, hook=None):
        self.path = Path(path)
        self.run_id, self.store_id = identifier(run_id), identifier(store_id)
        if role not in ('CLIENT', 'REMOTE'):
            fail('INVALID_ROLE')
        self.role, self.reducer, self.genesis, self.hook = role, reducer, genesis, hook
        self.poisoned = False

    @property
    def marker(self):
        return dict(schema='d5.durable-marker.v1', run_id=self.run_id,
                    store_id=self.store_id, role=self.role)

    def checkpoint(self, point):
        if self.hook:
            self.hook(point)

    @staticmethod
    def _write(fd, name, raw):
        out = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        try:
            with os.fdopen(out, 'wb', closefd=False) as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(out)
        finally:
            os.close(out)

    @staticmethod
    def _read(fd, name, maximum):
        try:
            handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            try:
                info = os.fstat(handle)
                if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
                    fail('FILE_BUDGET_OR_TYPE')
                with os.fdopen(handle, 'rb', closefd=False) as stream:
                    raw = stream.read(maximum+1)
                if len(raw) > maximum:
                    fail('FILE_BUDGET')
                return raw
            finally:
                os.close(handle)
        except OSError:
            fail('STORE_UNAVAILABLE')

    @contextlib.contextmanager
    def locked(self):
        if self.poisoned:
            fail('RECOVERY_REQUIRED')
        try:
            root = os.open(self.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError:
            fail('INITIALIZATION_INCOMPLETE')
        lock = objects = None
        try:
            if decode(self._read(root, 'marker.json', 4096)) != self.marker:
                fail('STORE_IDENTITY')
            lock = os.open('lock', os.O_RDWR | os.O_NOFOLLOW, dir_fd=root)
            if not stat.S_ISREG(os.fstat(lock).st_mode):
                fail('INVALID_LOCK')
            fcntl.flock(lock, fcntl.LOCK_EX)
            objects = os.open('objects', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root)
            yield root, objects
        except OSError:
            fail('STORE_UNAVAILABLE')
        finally:
            if objects is not None:
                os.close(objects)
            if lock is not None:
                os.close(lock)
            os.close(root)

    def create(self, config):
        identifier(config['project_id']); identifier(config['document_id'])
        try:
            self.path.mkdir(mode=0o700)
        except FileExistsError:
            fail('ALREADY_EXISTS')
        root = os.open(self.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            self._write(root, 'marker.json', canonical(self.marker))
            self._write(root, 'lock', b'')
            os.mkdir('objects', 0o700, dir_fd=root)
            os.fsync(root)
        finally:
            os.close(root)
        state = self.genesis(config)
        state['receipts'] = {}
        value = dict(schema='d5.durable-commit.v1', **self.marker_identity(), seq=0,
                     parent_sha256=None, command_id=None, request_sha256=digest(config),
                     operation=dict(kind='GENESIS', args=config, expected=None), state=state, receipt=None)
        with self.locked() as (root, objects):
            self._publish(root, objects, value)
        parent = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)

    def marker_identity(self):
        return dict(run_id=self.run_id, store_id=self.store_id, role=self.role)

    def _next(self, prior, cid, operation):
        shape(operation, ('kind', 'args', 'expected'))
        identifier(cid)
        rh = digest(operation)
        state = copy(prior['state'])
        if cid in state['receipts']:
            fail('DUPLICATE_CHAIN_COMMAND')
        if self.role == 'CLIENT':
            expected = operation['expected']
            shape(expected, ('seq', 'commit_sha256'))
            integer(expected['seq']); hash_id(expected['commit_sha256'])
            if expected != dict(seq=prior['seq'], commit_sha256=digest(prior)):
                fail('CONFLICT_HEAD')
        elif operation['expected'] is not None:
            fail('INVALID_EXPECTATION')
        if len(state['receipts']) >= state['config']['limits']['commands']:
            fail('COMMAND_BUDGET')
        before = copy(state)
        # Pure closed transition; no disk, transport, hooks or arbitrary command execution.
        if self.role == 'REMOTE' and operation['kind'] in ('EXECUTE','CLOSE'):
            if any(operation['args'].get(k) != v for k,v in self.marker_identity().items() if k != 'role'):
                fail('REMOTE_IDENTITY')
        state, result = self.reducer(state, operation['kind'], copy(operation['args']))
        seq = prior['seq']+1
        r = receipt(cid, rh, result, before, state, seq)
        state['receipts'][cid] = copy(r)
        return dict(schema='d5.durable-commit.v1', **self.marker_identity(), seq=seq,
                    parent_sha256=digest(prior), command_id=cid, request_sha256=rh,
                    operation=operation, state=state, receipt=r)

    def _load(self, root, objects):
        try:
            head = decode(self._read(root, 'head.json', 4096))
        except DurableError:
            fail('CORRUPT_OR_INCOMPLETE_HEAD')
        shape(head, ('schema', 'run_id', 'store_id', 'role', 'seq', 'commit_sha256'))
        if head['schema'] != 'd5.durable-head.v1' or any(head[k] != v for k,v in self.marker_identity().items()):
            fail('STORE_IDENTITY')
        integer(head['seq']); current = hash_id(head['commit_sha256'])
        chain, seen = [], set()
        while current is not None:
            if current in seen or len(chain) >= LIMITS['commits']:
                fail('CORRUPT_CHAIN')
            seen.add(current)
            raw = self._read(objects, current+'.json', LIMITS['commit_bytes'])
            if hashlib.sha256(raw).hexdigest() != current:
                fail('CORRUPT_OBJECT')
            value = decode(raw)
            shape(value, ('schema','run_id','store_id','role','seq','parent_sha256',
                          'command_id','request_sha256','operation','state','receipt'))
            if value['schema'] != 'd5.durable-commit.v1' or any(value[k] != v for k,v in self.marker_identity().items()):
                fail('STORE_IDENTITY')
            chain.append(value)
            current = value['parent_sha256']
            if current is not None:
                hash_id(current)
        chain.reverse()
        if not chain or chain[-1]['seq'] != head['seq']:
            fail('CORRUPT_HEAD')
        first = chain[0]
        shape(first['operation'], ('kind','args','expected'))
        config = first['operation']['args']
        initial = self.genesis(config); initial['receipts'] = {}
        expected = dict(schema='d5.durable-commit.v1', **self.marker_identity(), seq=0,
                        parent_sha256=None, command_id=None, request_sha256=digest(config),
                        operation=dict(kind='GENESIS', args=config, expected=None), state=initial, receipt=None)
        if first != expected:
            fail('CORRUPT_GENESIS')
        for prior, value in zip(chain, chain[1:]):
            if value != self._next(prior, value['command_id'], value['operation']):
                fail('CORRUPT_TRANSITION')
        limits = chain[-1]['state']['config']['limits']
        if len(chain) > limits['commits']:
            fail('HISTORY_BUDGET')
        try:
            self.checkpoint('recovery_fsync')
            os.fsync(objects); os.fsync(root)
        except OSError:
            self.poisoned = True
            fail('COMMIT_UNKNOWN')
        return head, chain[-1]

    @staticmethod
    def _size(root, objects):
        total = 0
        for fd in (root, objects):
            for name in os.listdir(fd):
                info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    fail('SYMLINK_STORE')
                if stat.S_ISREG(info.st_mode):
                    total += info.st_size
        return total

    def _publish(self, root, objects, value):
        raw = canonical(value); h = digest(value)
        limits = value['state']['config']['limits']
        # Every outstanding result reserves a worst-case commit and receipt slot.
        pending = value['state'].get('pending', {})
        if (value['seq']+1+len(pending) > limits['commits'] or
                len(value['state']['receipts'])+len(pending) > limits['commands']):
            fail('HISTORY_HEADROOM')
        if len(raw)+len(pending)*(4*limits['proof_bytes']+8192) > limits['commit_bytes']:
            fail('COMMIT_BUDGET')
        worst = limits['commit_bytes']
        if self._size(root, objects)+len(raw)+8192+len(pending)*(worst+8192) > limits['store_bytes']:
            fail('STORE_HEADROOM')
        obj, headtmp = '.object-'+str(uuid.uuid4()), '.head-'+str(uuid.uuid4())
        replaced = False
        try:
            self.checkpoint('before_object')
            self._write(objects, obj, raw)
            try:
                os.link(obj, h+'.json', src_dir_fd=objects, dst_dir_fd=objects, follow_symlinks=False)
            except FileExistsError:
                if self._read(objects, h+'.json', limits['commit_bytes']) != raw:
                    fail('OBJECT_COLLISION')
            os.unlink(obj, dir_fd=objects); os.fsync(objects)
            self.checkpoint('after_object')
            head = dict(schema='d5.durable-head.v1', **self.marker_identity(), seq=value['seq'], commit_sha256=h)
            self._write(root, headtmp, canonical(head))
            self.checkpoint('before_replace')
            os.replace(headtmp, 'head.json', src_dir_fd=root, dst_dir_fd=root)
            replaced = True
            self.checkpoint('directory_fsync')
            os.fsync(root)
            self.checkpoint('after_head')
        except OSError:
            self.poisoned = True
            fail('COMMIT_UNKNOWN' if replaced else 'IO_NOT_CONFIRMED')
        finally:
            for fd, name in ((objects,obj),(root,headtmp)):
                try:
                    os.unlink(name, dir_fd=fd)
                except FileNotFoundError:
                    pass

    def snapshot(self):
        with self.locked() as (root, objects):
            head, value = self._load(root, objects)
            return dict(head=head, state=copy(value['state']))

    def transact(self, cid, kind, args, expected=None):
        operation = dict(kind=kind, args=copy(args), expected=copy(expected))
        rh = digest(operation); identifier(cid)
        self.checkpoint('before_lock')
        with self.locked() as (root, objects):
            head, prior = self._load(root, objects)
            old = prior['state']['receipts'].get(cid)
            if old:
                if old['request_sha256'] != rh:
                    fail('COMMAND_CONFLICT')
                return dict(copy(old), historical=True)
            value = self._next(prior, cid, operation)
            self._publish(root, objects, value)
            return dict(copy(value['receipt']), historical=False)

    def read_command(self, cid, request_hash):
        identifier(cid); hash_id(request_hash)
        state = self.snapshot()['state']
        value = state['receipts'].get(cid)
        if value is None:
            return dict(result='NOT_COMMITTED_AT_HEAD', grants_execution_authority=False)
        if value['request_sha256'] != request_hash:
            fail('COMMAND_CONFLICT')
        return dict(copy(value), historical=True)
