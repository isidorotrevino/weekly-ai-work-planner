# SPDX-License-Identifier: GPL-3.0-only
"""I28 volatile synthetic Plane protocol. No transport, persistence or D2 writes.

Fixture controls are trusted harness hooks, never source data or credentials.
Returned command views are sanitized; manifest/fixture inspection is private.
"""
from copy import deepcopy
import hashlib
import json
import threading
import uuid

MAX_BINDINGS = 64
MAX_COMMANDS = 128
MAX_ATTEMPTS = 3
MAX_QUERIES = 6
MAX_MANIFEST = 65536
MAX_TEXT = 8192
HARD_CONFLICTS = ('MULTIPLE_MATCHES', 'IDENTITY_CONFLICT', 'PROOF_CONFLICT',
                  'DESTINATION_CONFLICT', 'REMOTE_MISSING')


class PlaneError(ValueError):
    pass


def fail(code):
    raise PlaneError(code)


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False, allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, UnicodeError, RecursionError):
        fail('INVALID_JSON')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def shape(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        fail('INVALID_SHAPE')


def identifier(value):
    try:
        if type(value) is not str or str(uuid.UUID(value)) != value:
            fail('INVALID_ID')
    except (ValueError, AttributeError):
        fail('INVALID_ID')
    return value


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        fail('INVALID_INTEGER')
    return value


def text(value, *, nullable=False, empty=False):
    if nullable and value is None:
        return
    if type(value) is not str or len(value) > MAX_TEXT or (not value and not empty):
        fail('INVALID_TEXT')
    canonical(value)


def capabilities(*, create_unique=True, conditional_update=True, release=1):
    return dict(schema='d5.plane-fixture-capabilities.v1', mode='SYNTHETIC_ONLY',
                release=release, create_unique=create_unique,
                conditional_update=conditional_update, effect_lookup=True)


def validate_capabilities(card):
    shape(card, ('schema', 'mode', 'release', 'create_unique',
                 'conditional_update', 'effect_lookup'))
    if card['schema'] != 'd5.plane-fixture-capabilities.v1' or card['mode'] != 'SYNTHETIC_ONLY':
        fail('SYNTHETIC_ONLY')
    integer(card['release'], 1)
    if any(type(card[k]) is not bool for k in ('create_unique', 'conditional_update', 'effect_lookup')):
        fail('INVALID_CAPABILITY')


def binding(binding_id, project_id, task_id, workspace_id, remote_project_id):
    return dict(schema='d5.plane-fixture-binding.v1', mode='SYNTHETIC_ONLY',
                binding_id=binding_id, project_id=project_id, task_id=task_id,
                instance='SYNTHETIC_PLANE', workspace_id=workspace_id,
                remote_project_id=remote_project_id, policy_version=1)


def validate_binding(value):
    shape(value, ('schema', 'mode', 'binding_id', 'project_id', 'task_id',
                  'instance', 'workspace_id', 'remote_project_id', 'policy_version'))
    if (value['schema'] != 'd5.plane-fixture-binding.v1' or value['mode'] != 'SYNTHETIC_ONLY'
            or value['instance'] != 'SYNTHETIC_PLANE'):
        fail('SYNTHETIC_ONLY')
    for k in ('binding_id', 'project_id', 'task_id', 'workspace_id', 'remote_project_id'):
        identifier(value[k])
    integer(value['policy_version'], 1)


def creation_key(value):
    validate_binding(value)
    return digest(dict(schema='d5.plane-fixture-creation-key.v1',
                       **{k: value[k] for k in ('instance', 'workspace_id',
                           'remote_project_id', 'project_id', 'task_id')}))


def task(project_id, task_id, *, title='Synthetic title', description='Synthetic description', row_version=1):
    return dict(project_id=project_id, task_id=task_id, kind='TASK', state='BACKLOG',
                title=title, description=description, row_version=row_version)


def validate_task(value):
    shape(value, ('project_id', 'task_id', 'kind', 'state', 'title', 'description', 'row_version'))
    identifier(value['project_id']); identifier(value['task_id'])
    if value['kind'] != 'TASK' or value['state'] != 'BACKLOG':
        fail('SYNTHETIC_BACKLOG_ONLY')
    text(value['title']); text(value['description'], nullable=True, empty=True)
    integer(value['row_version'], 1)


def validate_manifest(value):
    shape(value, ('schema', 'mode', 'operation', 'binding', 'key', 'task',
                  'capabilities', 'payload', 'remote_base', 'activation_allowed'))
    if (value['schema'] != 'd5.plane-fixture-manifest.v1' or value['mode'] != 'SYNTHETIC_ONLY'
            or value['activation_allowed'] is not False):
        fail('SYNTHETIC_ONLY')
    validate_binding(value['binding']); validate_task(value['task'])
    validate_capabilities(value['capabilities'])
    b, t = value['binding'], value['task']
    if ((b['project_id'], b['task_id']) != (t['project_id'], t['task_id'])
            or value['key'] != creation_key(b)):
        fail('IDENTITY_CONFLICT')
    shape(value['payload'], ('name', 'description'))
    if value['payload'] != dict(name=t['title'], description=t['description']):
        fail('PAYLOAD_CONFLICT')
    if value['operation'] == 'CREATE':
        if value['remote_base'] is not None:
            fail('INVALID_BASE')
    elif value['operation'] == 'UPDATE':
        base = value['remote_base']
        shape(base, ('remote_id', 'version', 'payload_sha256'))
        identifier(base['remote_id']); integer(base['version'], 1)
        if (type(base['payload_sha256']) is not str or len(base['payload_sha256']) != 64
                or any(c not in '0123456789abcdef' for c in base['payload_sha256'])):
            fail('INVALID_BASE')
    else:
        fail('INVALID_OPERATION')
    if len(canonical(value)) > MAX_MANIFEST:
        fail('MANIFEST_BUDGET')


class PlaneFixture:
    """Atomic in-memory double. Its capabilities prove no real Plane semantics."""
    def __init__(self, card=None):
        self._card = deepcopy(card if card is not None else capabilities(
            create_unique=False, conditional_update=False))
        validate_capabilities(self._card)
        self._lock = threading.RLock()
        self._items = {}
        self._keys = {}
        self._proofs = {}
        self._tickets = {}
        self._attached = False
        self.write_calls = 0
        self.query_calls = 0
        self.before_send = None
        self.before_query = None
        self.send_mode = 'SUCCESS'
        self.query_mode = 'EXACT'
        self.retry_after = 2

    def card(self):
        with self._lock:
            return deepcopy(self._card)

    def change_card(self, card):
        validate_capabilities(card)
        with self._lock:
            if card['release'] <= self._card['release']:
                fail('CAPABILITY_VERSION_REQUIRED')
            self._card = deepcopy(card)

    def read(self, remote_id):
        identifier(remote_id)
        with self._lock:
            if remote_id not in self._items:
                fail('REMOTE_MISSING')
            return deepcopy(self._items[remote_id])

    def edit(self, remote_id, *, name=None, description=None, set_description=False, foreign=None):
        """Trusted fixture mutation; projected ABA increments monotonic version."""
        if name is not None:
            text(name)
        if set_description:
            text(description, nullable=True, empty=True)
        if foreign is not None:
            shape(foreign, ('labels',))
            if type(foreign['labels']) is not list or len(foreign['labels']) > 16:
                fail('INVALID_FOREIGN_FIXTURE')
            for value in foreign['labels']:
                text(value)
        with self._lock:
            item = self.read(remote_id)
            if name is not None or set_description:
                item['version'] += 1
            if name is not None:
                item['payload']['name'] = name
            if set_description:
                item['payload']['description'] = description
            if foreign is not None:
                item['foreign'] = deepcopy(foreign)
            self._items[remote_id] = item

    def remove(self, remote_id):
        """Trusted disappearance fixture; key and historical proofs remain."""
        with self._lock:
            self._items.pop(identifier(remote_id), None)

    def count(self):
        with self._lock:
            return len(self._items)

    def execute(self, ticket, manifest):
        identifier(ticket)
        validate_manifest(manifest)
        # The caller only supplies a closed manifest registered by ReconciliationLab.
        if self.before_send is not None:
            self.before_send()
        with self._lock:
            self.write_calls += 1
            mh = digest(manifest)
            if ticket in self._tickets:
                if self._tickets[ticket] != mh:
                    return dict(status='CONFLICT')
                return deepcopy(self._proofs.get(ticket, dict(status='UNKNOWN')))
            self._tickets[ticket] = mh
            mode = self.send_mode
            self.send_mode = 'SUCCESS'
            if mode in ('TIMEOUT_BEFORE', 'AMBIGUOUS_429'):
                return dict(status='UNKNOWN')
            if mode in ('REJECT', 'DENY', 'RATE_LIMIT'):
                result = dict(status='REJECTED_NO_EFFECT', code=mode,
                              ticket=ticket, manifest_sha256=mh)
                if mode == 'RATE_LIMIT':
                    result['retry_after'] = self.retry_after
                self._proofs[ticket] = deepcopy(result)
                return result
            if manifest['capabilities'] != self._card:
                return self._reject(ticket, mh, 'CAPABILITY_CHANGED')
            key, payload = manifest['key'], manifest['payload']
            if manifest['operation'] == 'CREATE':
                if not self._card['create_unique'] or not self._card['effect_lookup']:
                    return self._reject(ticket, mh, 'CAPABILITY_REQUIRED')
                if key in self._keys:
                    remote_id, original_hash = self._keys[key]
                    if original_hash != digest(payload) or remote_id not in self._items:
                        return self._reject(ticket, mh, 'CREATION_KEY_CONFLICT')
                    item = self._items[remote_id]
                else:
                    remote_id = str(uuid.uuid4())
                    item = dict(remote_id=remote_id, key=key, payload=deepcopy(payload),
                                version=1, foreign=dict(labels=['fixture-preserved']))
                    self._items[remote_id] = item
                    self._keys[key] = (remote_id, digest(payload))
                effect_version = 1
            else:
                if not self._card['conditional_update'] or not self._card['effect_lookup']:
                    return self._reject(ticket, mh, 'CAPABILITY_REQUIRED')
                remote_id = manifest['remote_base']['remote_id']
                item = self._items.get(remote_id)
                base = manifest['remote_base']
                if (item is None or item['key'] != key or item['version'] != base['version']
                        or digest(item['payload']) != base['payload_sha256']):
                    return self._reject(ticket, mh, 'REMOTE_PRECONDITION')
                item['payload'] = deepcopy(payload)
                item['version'] += 1
                effect_version = item['version']
            proof = dict(status='EFFECT_CONFIRMED', ticket=ticket, key=key,
                         manifest_sha256=mh, payload_sha256=digest(payload),
                         remote_id=remote_id, effect_version=effect_version,
                         operation=manifest['operation'])
            self._proofs[ticket] = deepcopy(proof)
            if mode == 'LOSE_AFTER':
                return dict(status='UNKNOWN')
            if mode == 'MALFORMED_AFTER':
                return dict(status='untrusted-body', raw='fixture-private-body')
            if mode == 'ACK_AFTER':
                return dict(status='ACK_LOCAL')
            return deepcopy(proof)

    def _reject(self, ticket, mh, code):
        result = dict(status='REJECTED_NO_EFFECT', code=code, ticket=ticket, manifest_sha256=mh)
        self._proofs[ticket] = deepcopy(result)
        return result

    def query(self, key, ticket):
        if self.before_query is not None:
            self.before_query()
        with self._lock:
            self.query_calls += 1
            mode = self.query_mode
            if mode == 'ERROR':
                raise PlaneError('FIXTURE_UNAVAILABLE')
            if mode in ('ZERO', 'STRONG_ZERO') or key not in self._keys:
                return dict(matches=[], proof=None)
            remote_id = self._keys[key][0]
            if remote_id not in self._items:
                return dict(matches=[], proof=None)
            item = self._items[remote_id]
            match = dict(remote_id=remote_id, key=key, version=item['version'],
                         payload_sha256=digest(item['payload']))
            if mode == 'FOREIGN':
                match['key'] = '0' * 64
            matches = [match, deepcopy(match)] if mode == 'DUPLICATES' else [match]
            proof = None if mode == 'UNPROVEN' else deepcopy(self._proofs.get(ticket))
            if mode == 'BAD_PROOF' and proof:
                proof['payload_sha256'] = '0' * 64
            if mode == 'MALFORMED':
                return dict(raw='fixture-private-body')
            return dict(matches=matches, proof=proof)


class ReconciliationLab:
    """Volatile ledger and explicit approvals, independent of historical modules."""
    def __init__(self, plane):
        if type(plane) is not PlaneFixture:
            fail('FIXTURE_REQUIRED')
        with plane._lock:
            if plane._attached:
                fail('LEDGER_RESTART_UNSUPPORTED')
            plane._attached = True
        self.plane = plane
        self._lock = threading.RLock()
        self._bindings = {}
        self._tasks = {}
        self._destinations = {}
        self._manifests = {}
        self._reviews = {}
        self._commands = {}
        self._package_commands = {}
        self._package_attempts = {}
        self._tick = 0

    def bind(self, value, task_snapshot):
        validate_binding(value); validate_task(task_snapshot)
        if (value['project_id'], value['task_id']) != (task_snapshot['project_id'], task_snapshot['task_id']):
            fail('PROJECT_TASK_MISMATCH')
        with self._lock:
            bid = value['binding_id']
            if bid in self._bindings:
                if self._bindings[bid] != value or self._tasks[bid] != task_snapshot:
                    fail('BINDING_CONFLICT')
                return creation_key(value)
            if len(self._bindings) >= MAX_BINDINGS:
                fail('BINDING_BUDGET')
            if any((old['project_id'], old['task_id']) == (value['project_id'], value['task_id'])
                   or creation_key(old) == creation_key(value) for old in self._bindings.values()):
                fail('BINDING_CONFLICT')
            self._bindings[bid] = deepcopy(value)
            self._tasks[bid] = deepcopy(task_snapshot)
            return creation_key(value)

    def edit_task(self, bid, value):
        identifier(bid); validate_task(value)
        with self._lock:
            if bid not in self._tasks:
                fail('BINDING_REQUIRED')
            old = self._tasks[bid]
            if (value['project_id'], value['task_id']) != (old['project_id'], old['task_id']):
                fail('PROJECT_TASK_MISMATCH')
            if value['row_version'] != old['row_version'] + 1:
                fail('TASK_VERSION_REQUIRED')
            self._tasks[bid] = deepcopy(value)

    def change_policy(self, bid, version):
        identifier(bid); integer(version, 1)
        with self._lock:
            if bid not in self._bindings:
                fail('BINDING_REQUIRED')
            if version != self._bindings[bid]['policy_version'] + 1:
                fail('POLICY_VERSION_REQUIRED')
            self._bindings[bid]['policy_version'] = version

    def advance_clock(self, tick):
        integer(tick)
        with self._lock:
            if tick < self._tick:
                fail('CLOCK_REWIND')
            self._tick = tick

    def prepare(self, bid, operation='CREATE'):
        identifier(bid)
        if operation not in ('CREATE', 'UPDATE'):
            fail('INVALID_OPERATION')
        with self._lock:
            if bid not in self._bindings:
                fail('BINDING_REQUIRED')
            b, t = deepcopy(self._bindings[bid]), deepcopy(self._tasks[bid])
            remote_id = self._destinations.get(bid)
        card = self.plane.card()
        remote_base = None
        if operation == 'UPDATE':
            if remote_id is None:
                fail('DESTINATION_REQUIRED')
            remote = self.plane.read(remote_id)
            remote_base = dict(remote_id=remote_id, version=remote['version'],
                               payload_sha256=digest(remote['payload']))
        elif remote_id is not None:
            fail('ALREADY_CREATED')
        manifest = dict(schema='d5.plane-fixture-manifest.v1', mode='SYNTHETIC_ONLY',
                        operation=operation, binding=b, key=creation_key(b), task=t,
                        capabilities=card, payload=dict(name=t['title'], description=t['description']),
                        remote_base=remote_base, activation_allowed=False)
        raw = canonical(manifest)
        if len(raw) > MAX_MANIFEST:
            fail('MANIFEST_BUDGET')
        mid = digest(manifest)
        with self._lock:
            self._manifests[mid] = raw
            self._reviews.setdefault(mid, dict(version=0, decision=None, reason=''))
        return mid

    def manifest(self, mid):
        if type(mid) is not str or len(mid) != 64 or any(c not in '0123456789abcdef' for c in mid):
            fail('INVALID_MANIFEST_ID')
        with self._lock:
            if mid not in self._manifests:
                fail('MANIFEST_REQUIRED')
            raw = self._manifests[mid]
            try:
                value = json.loads(raw)
            except (ValueError, TypeError, UnicodeError):
                fail('MANIFEST_CORRUPT')
            if canonical(value) != raw or digest(value) != mid:
                fail('MANIFEST_CORRUPT')
            validate_manifest(value)
            return value

    def review(self, mid, *, expected_version, decision, reason):
        integer(expected_version); text(reason)
        if decision not in ('ACCEPT', 'REJECT'):
            fail('INVALID_DECISION')
        with self._lock:
            self.manifest(mid)
            old = self._reviews[mid]
            if old['version'] != expected_version:
                fail('CONFLICT_REVIEW')
            self._reviews[mid] = dict(version=old['version'] + 1, decision=decision, reason=reason)
            return old['version'] + 1

    def _validity(self, m, rv, card):
        bid = m['binding']['binding_id']
        stale = []
        if self._tasks.get(bid) != m['task']:
            stale.append('STALE_LOCAL')
        if self._bindings.get(bid) != m['binding']:
            stale.append('STALE_BINDING')
        r = self._reviews[digest(m)]
        if r['version'] != rv or r['decision'] != 'ACCEPT':
            stale.append('STALE_REVIEW')
        if card != m['capabilities']:
            stale.append('STALE_CAPABILITY')
        return stale or ['CURRENT']

    def _view(self, entry, card):
        m = self.manifest(entry['manifest_id'])
        return dict(command_id=entry['command_id'], request_sha256=entry['request_sha256'],
                    manifest_id=entry['manifest_id'], version=entry['version'],
                    result=entry['result'], validity=self._validity(m, entry['review_version'], card),
                    conflict=entry['conflict'], write_blocked_by_identity_conflict=entry['hard_conflict'],
                    attempts=len(entry['attempts']),
                    queries=entry['queries'], effect_receipt=deepcopy(entry['receipt']),
                    activation_allowed=False)

    def command(self, cid):
        identifier(cid)
        card = self.plane.card()
        with self._lock:
            if cid not in self._commands:
                fail('COMMAND_REQUIRED')
            return self._view(self._commands[cid], card)

    def dispatch(self, cid, mid, *, review_version, expected_version=0, retry=False):
        identifier(cid); integer(review_version, 1); integer(expected_version)
        if type(retry) is not bool:
            fail('INVALID_RETRY')
        m = self.manifest(mid)
        rh = digest(dict(manifest_id=mid, review_version=review_version))
        card = self.plane.card()
        with self._lock:
            entry = self._commands.get(cid)
            if entry is not None:
                if entry['request_sha256'] != rh:
                    fail('COMMAND_CONFLICT')
                if not retry:
                    return self._view(entry, card)
                if entry['version'] != expected_version:
                    fail('CONFLICT_LEDGER')
                if entry['result'] != 'REJECTED_NO_EFFECT':
                    fail('RETRY_FORBIDDEN')
                if entry['retry_tick'] is None or self._tick < entry['retry_tick']:
                    fail('RETRY_NOT_ELIGIBLE')
            elif retry or expected_version != 0:
                fail('COMMAND_REQUIRED')
            if self._validity(m, review_version, card) != ['CURRENT']:
                fail('STALE_PACKAGE')
            required = 'create_unique' if m['operation'] == 'CREATE' else 'conditional_update'
            if not card[required] or not card['effect_lookup']:
                fail('CAPABILITY_REQUIRED')
            bid = m['binding']['binding_id']
            if any(e['binding_id'] == bid and (e['result'] in ('UNKNOWN', 'CONFLICT')
                    or e['hard_conflict'])
                   for e in self._commands.values()):
                fail('BINDING_UNRESOLVED')
            if m['operation'] == 'CREATE' and bid in self._destinations:
                fail('ALREADY_CREATED')
            if m['operation'] == 'UPDATE' and self._destinations.get(bid) != m['remote_base']['remote_id']:
                fail('DESTINATION_CONFLICT')
            if mid in self._package_commands and self._package_commands[mid] != cid:
                fail('PACKAGE_COMMAND_CONFLICT')
            if self._package_attempts.get(mid, 0) >= MAX_ATTEMPTS:
                fail('ATTEMPT_BUDGET')
            if entry is None:
                if len(self._commands) >= MAX_COMMANDS:
                    fail('COMMAND_BUDGET')
                entry = dict(command_id=cid, request_sha256=rh, manifest_id=mid,
                             review_version=review_version, binding_id=bid, version=0,
                             result='NOT_SENT', conflict=None, hard_conflict=False, attempts=[], queries=0,
                             receipt=None, retry_tick=0, events=[])
                self._commands[cid] = entry
                self._package_commands[mid] = cid
            self._package_attempts[mid] = self._package_attempts.get(mid, 0) + 1
            ticket = str(uuid.uuid4())
            entry['attempts'].append(ticket)
            entry['result'] = 'UNKNOWN'  # consumed dispatch ticket: possibly sent
            entry['version'] += 1
            entry['events'].append(dict(type='DISPATCHED', ticket=ticket, version=entry['version']))
            version = entry['version']
        try:
            response = self.plane.execute(ticket, m)
        except Exception:
            response = dict(status='UNKNOWN')
        card = self.plane.card()
        with self._lock:
            if entry['version'] != version:
                fail('CONFLICT_LEDGER')
            self._apply_response(entry, m, ticket, response)
            if entry['conflict'] in HARD_CONFLICTS:
                entry['hard_conflict'] = True
            entry['version'] += 1
            entry['events'].append(dict(type='SEND_RESULT', ticket=ticket, version=entry['version'],
                                       result=entry['result'], conflict=entry['conflict'],
                                       proof=deepcopy(response) if self._proof_ok(response, m, ticket)
                                           or self._negative_ok(response, m, ticket) else None))
            return self._view(entry, card)

    @staticmethod
    def _proof_ok(proof, m, ticket):
        keys = {'status', 'ticket', 'key', 'manifest_sha256', 'payload_sha256',
                'remote_id', 'effect_version', 'operation'}
        if type(proof) is not dict or set(proof) != keys:
            return False
        try:
            identifier(proof['remote_id']); integer(proof['effect_version'], 1)
        except PlaneError:
            return False
        return (proof['status'] == 'EFFECT_CONFIRMED' and proof['ticket'] == ticket
                and proof['key'] == m['key'] and proof['manifest_sha256'] == digest(m)
                and proof['payload_sha256'] == digest(m['payload'])
                and proof['operation'] == m['operation']
                and (m['operation'] == 'CREATE' or proof['remote_id'] == m['remote_base']['remote_id']))

    @staticmethod
    def _negative_ok(response, m, ticket):
        if type(response) is not dict:
            return False
        keys = {'status', 'code', 'ticket', 'manifest_sha256'}
        return (set(response) in (keys, keys | {'retry_after'})
                and response['status'] == 'REJECTED_NO_EFFECT'
                and response['ticket'] == ticket and response['manifest_sha256'] == digest(m)
                and response['code'] in ('REJECT', 'DENY', 'RATE_LIMIT', 'CAPABILITY_CHANGED',
                                         'CAPABILITY_REQUIRED', 'CREATION_KEY_CONFLICT', 'REMOTE_PRECONDITION')
                and ('retry_after' not in response or type(response['retry_after']) in (int, str, bool, type(None))))

    @staticmethod
    def _match_ok(match, key):
        if (type(match) is not dict or set(match) != {'remote_id', 'key', 'version', 'payload_sha256'}
                or match['key'] != key):
            return False
        try:
            identifier(match['remote_id']); integer(match['version'], 1)
        except PlaneError:
            return False
        h = match['payload_sha256']
        return type(h) is str and len(h) == 64 and all(c in '0123456789abcdef' for c in h)

    def _apply_response(self, entry, m, ticket, response):
        if self._proof_ok(response, m, ticket):
            remote_id = response['remote_id']
            bid = entry['binding_id']
            if ((bid in self._destinations and self._destinations[bid] != remote_id)
                    or any(k != bid and v == remote_id for k, v in self._destinations.items())):
                entry['result'], entry['conflict'] = 'CONFLICT', 'DESTINATION_CONFLICT'
                return
            self._destinations[bid] = remote_id
            entry['result'] = 'EFFECT_CONFIRMED'
            if entry['receipt'] is None:
                entry['receipt'] = deepcopy(response)
            return
        if self._negative_ok(response, m, ticket):
            entry['result'] = 'REJECTED_NO_EFFECT'
            entry['retry_tick'] = self._tick
            if response['code'] == 'RATE_LIMIT':
                delay = response.get('retry_after')
                entry['retry_tick'] = (self._tick + delay if type(delay) is int and 0 <= delay <= 1000000 else None)
            if response['code'] in ('REMOTE_PRECONDITION', 'CREATION_KEY_CONFLICT'):
                entry['conflict'] = response['code']
                entry['retry_tick'] = None

    def reconcile(self, cid, *, expected_version):
        identifier(cid); integer(expected_version)
        with self._lock:
            if cid not in self._commands:
                fail('COMMAND_REQUIRED')
            entry = self._commands[cid]
            if entry['version'] != expected_version:
                fail('CONFLICT_LEDGER')
            if entry['queries'] >= MAX_QUERIES:
                fail('QUERY_BUDGET')
            m = self.manifest(entry['manifest_id'])
            ticket = entry['attempts'][-1]
            entry['queries'] += 1  # queries count even errors / losing CAS
            version = entry['version']
        try:
            response = self.plane.query(m['key'], ticket)
        except Exception:
            response = None
        card = self.plane.card()
        with self._lock:
            if entry['version'] != version:
                fail('CONFLICT_LEDGER')
            entry['version'] += 1
            observation = 'INVALID_OR_UNAVAILABLE'
            observed_match = None
            observed_proof = None
            if type(response) is dict and set(response) == {'matches', 'proof'} and type(response['matches']) is list:
                matches = response['matches']
                observation = 'EMPTY' if not matches else 'UNPROVEN'
                if len(matches) > 1:
                    observation = 'MULTIPLE'
                    entry['conflict'] = 'MULTIPLE_MATCHES'
                    if entry['receipt'] is None:
                        entry['result'] = 'CONFLICT'
                elif len(matches) == 1:
                    match = matches[0]
                    if not self._match_ok(match, m['key']):
                        observation = 'IDENTITY_CONFLICT'
                        entry['conflict'] = 'IDENTITY_CONFLICT'
                        if entry['receipt'] is None:
                            entry['result'] = 'CONFLICT'
                    elif response['proof'] is not None:
                        observed_match = deepcopy(match)
                        proof = response['proof']
                        if self._negative_ok(proof, m, ticket):
                            observation = 'CONCLUSIVE_NO_EFFECT'
                            # A proven effect receipt can never be overwritten by a negative observation.
                            if entry['receipt'] is None:
                                self._apply_response(entry, m, ticket, proof)
                            else:
                                entry['conflict'] = 'PROOF_CONFLICT'
                        elif not self._proof_ok(proof, m, ticket) or proof['remote_id'] != match['remote_id']:
                            observation = 'PROOF_CONFLICT'
                            entry['conflict'] = 'PROOF_CONFLICT'
                            if entry['receipt'] is None:
                                entry['result'] = 'CONFLICT'
                        elif entry['result'] == 'REJECTED_NO_EFFECT':
                            observation = 'PROOF_CONFLICT'
                            entry['result'], entry['conflict'] = 'CONFLICT', 'PROOF_CONFLICT'
                        else:
                            observation = 'EXACT'
                            observed_proof = deepcopy(proof)
                            self._apply_response(entry, m, ticket, proof)
                            if (match['payload_sha256'] != proof['payload_sha256']
                                    or match['version'] != proof['effect_version']):
                                entry['conflict'] = 'REMOTE_EDIT'
                elif entry['receipt'] is not None:
                    entry['conflict'] = 'REMOTE_MISSING'
            if entry['conflict'] in HARD_CONFLICTS:
                entry['hard_conflict'] = True
            entry['events'].append(dict(type='QUERY_RESULT', ticket=ticket, version=entry['version'],
                                       result=entry['result'], conflict=entry['conflict'],
                                       observation=observation, match=observed_match, proof=observed_proof))
            return self._view(entry, card)

    def inspect_command(self, cid):
        """Private fixture ledger; copied so inspection cannot mutate authority."""
        identifier(cid)
        with self._lock:
            if cid not in self._commands:
                fail('COMMAND_REQUIRED')
            return deepcopy(self._commands[cid])

    def summary(self):
        with self._lock:
            return dict(mode='SYNTHETIC_ONLY', storage='VOLATILE_MEMORY',
                        bindings=len(self._bindings), commands=len(self._commands),
                        real_remote_requests=0, persistent_D2_writes=0,
                        operational_activation=False, D5_closed=False,
                        global_gaps_open=[f'G{i:02}' for i in range(1, 8)])
