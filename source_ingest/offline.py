# SPDX-License-Identifier: GPL-3.0-only
"""D5 I24 synthetic contracts. No I/O, HTTP, SQL, provider CLI or real authority.

The in-memory registries model review/version boundaries, not authentication or a
security sandbox against Python callers. Exact source bytes stay in captures;
receipts and summaries contain only fixed diagnostics, identities and hashes.
"""
import base64
from copy import deepcopy
import hashlib
import json
import threading
import uuid

from .preview import MAX_BYTES, MAX_ITEMS, PROFILE, build_observation

PROFILES = (PROFILE, 'task-register.v1', 'task-register-compat.v1')
FIRST_CRITERIA = (1, 2, 3, 5, 10, 13, 14, 19, 21, 23, 25, 26, 27, 31, 32, 35, 37, 41)
MAX_ENVELOPE = 32 * 1024 * 1024


class ContractError(ValueError):
    """Fixed diagnostics deliberately exclude input values."""


def _fail(code):
    raise ContractError(code)


def _shape(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        _fail('INVALID_FIELDS')


def _text(value, maximum=65536, empty=False):
    if (type(value) is not str or len(value) > maximum or (not empty and not value)
            or '\x00' in value):
        _fail('INVALID_TEXT')
    try:
        value.encode('utf-8')
    except UnicodeError:
        _fail('INVALID_TEXT')
    return value


def _id(value):
    try:
        if type(value) is not str or str(uuid.UUID(value)) != value:
            _fail('INVALID_ID')
    except (ValueError, AttributeError):
        _fail('INVALID_ID')
    return value


def _number(value):
    if type(value) is not int or not 0 <= value <= 2**63 - 1:
        _fail('INVALID_NUMBER')
    return value


def canonical(value):
    try:
        data = (json.dumps(value, sort_keys=True, ensure_ascii=True,
                           separators=(',', ':'), allow_nan=False) + '\n').encode()
    except (TypeError, ValueError, RecursionError):
        _fail('INVALID_JSON')
    if len(data) > MAX_ENVELOPE:
        _fail('ENVELOPE_LIMIT')
    return data


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _typed_elements(payload):
    _shape(payload, ('schema', 'elements'))
    if payload['schema'] != 'd5.offline-typed-fixture.v1' or type(payload['elements']) is not list or not 1 <= len(payload['elements']) <= MAX_ITEMS:
        _fail('INVALID_TYPED_FIXTURE')
    elements = {}
    for item in payload['elements']:
        _shape(item, ('kind', 'source_key', 'title', 'description'))
        if item['kind'] not in ('REQUIREMENT', 'EPIC', 'TASK'):
            _fail('INVALID_KIND')
        _text(item['source_key'], 256)
        _text(item['title'])
        _text(item['description'], empty=True)
        if item['source_key'] in elements:
            _fail('DUPLICATE_SOURCE_KEY')
        elements[item['source_key']] = item
    return elements


def decode_envelope(data):
    """Closed, bounded JSON entry boundary; reject duplicates and nonfinite values."""
    if type(data) is not bytes or len(data) > MAX_ENVELOPE:
        _fail('ENVELOPE_LIMIT')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                _fail('DUPLICATE_KEY')
            result[key] = value
        return result
    try:
        value = json.loads(data, object_pairs_hook=unique,
                           parse_constant=lambda _: _fail('INVALID_JSON'))
    except (ValueError, UnicodeError, RecursionError):
        _fail('INVALID_JSON')
    _shape(value, ('schema', 'mode', 'payload'))
    if value['schema'] != 'd5.offline-envelope.v1' or value['mode'] != 'SYNTHETIC_ONLY':
        _fail('SYNTHETIC_ONLY')
    _typed_elements(value['payload'])
    canonical(value)
    return value


def envelope(payload):
    return {'schema': 'd5.offline-envelope.v1', 'mode': 'SYNTHETIC_ONLY',
            'payload': deepcopy(payload)}


def _metadata(value):
    _shape(value, ('scope', 'file_id', 'version', 'mime_type'))
    for item in value.values():
        _text(item, 256)
    return deepcopy(value)


class MemoryDrive:
    """A fixture catalog, not a Drive client. No cursors or durability promised."""
    def __init__(self):
        self._files = {}

    def seed(self, file_id, content, *, scope='fixture-drive', version='fixture-1',
             mime_type='text/markdown'):
        _text(file_id, 256)
        if type(content) is not bytes or len(content) > MAX_BYTES:
            _fail('SOURCE_LIMIT')
        meta = _metadata(dict(scope=scope, file_id=file_id, version=version, mime_type=mime_type))
        self._files[file_id] = (content, meta)

    def read(self, file_id, *, change_during_read=None):
        if file_id not in self._files:
            _fail('FIXTURE_NOT_FOUND')
        content, before = self._files[file_id]
        if change_during_read is not None:
            _shape(change_during_read, ('content', 'version'))
            self.seed(file_id, change_during_read['content'], scope=before['scope'],
                      version=change_during_read['version'], mime_type=before['mime_type'])
        again, after = self._files[file_id]
        return content, deepcopy(before), deepcopy(after), content == again


class MemoryPlane:
    """Atomic fixture CAS on projected fields. No creation or remote transport."""
    def __init__(self, *, cas_supported=False,
                 workspace_id='00000000-0000-4000-8000-000000000010',
                 project_id='00000000-0000-4000-8000-000000000011'):
        self._workspace_id = _id(workspace_id)
        self._project_id = _id(project_id)
        if type(cas_supported) is not bool:
            _fail('INVALID_CAPABILITY')
        self.cas_supported = cas_supported
        self._items = {}
        self._queued = {}
        self._lock = threading.RLock()

    @staticmethod
    def projection(item):
        return {key: item[key] for key in ('name', 'description')}

    def seed(self, remote_id, item):
        _id(remote_id)
        if type(item) is not dict or not {'name', 'description'} <= item.keys():
            _fail('INVALID_REMOTE_FIXTURE')
        _text(item['name'])
        if item['description'] is not None:
            _text(item['description'], empty=True)
        canonical(item)
        with self._lock:
            self._items[remote_id] = deepcopy(item)

    def read(self, remote_id):
        with self._lock:
            if remote_id not in self._items:
                _fail('REMOTE_FIXTURE_NOT_FOUND')
            return deepcopy(self._items[remote_id])

    def edit_fixture(self, remote_id, fields, *, during_next_cas=False):
        """Explicit trusted test mutation; source text never calls this method."""
        canonical(fields)
        if type(fields) is not dict:
            _fail('INVALID_REMOTE_FIXTURE')
        with self._lock:
            if during_next_cas:
                self._queued[remote_id] = deepcopy(fields)
            else:
                item = self.read(remote_id)
                item.update(fields)
                self.seed(remote_id, item)

    def patch(self, remote_id, expected_hash, payload):
        _shape(payload, ('name', 'description'))
        _text(payload['name'])
        if payload['description'] is not None:
            _text(payload['description'], empty=True)
        with self._lock:
            if self.cas_supported is not True:
                return 'BLOCKED_ATOMIC_CAPABILITY'
            if remote_id in self._queued:
                self.edit_fixture(remote_id, self._queued.pop(remote_id))
            item = self.read(remote_id)
            if digest(self.projection(item)) != expected_hash:
                return 'CONFLICT_REMOTE_EDIT'
            item.update(deepcopy(payload))
            self._items[remote_id] = item
            return 'SIMULATED_PROJECTED'


def evaluate_route(card, *, capability, dimension, window, now, cost=1):
    """A contract check only: never consumes quota or grants execution authority."""
    _shape(card, ('schema', 'provider_id', 'release', 'capabilities', 'online',
                  'permission', 'quota'))
    if card['schema'] != 'd5.offline-provider.v1':
        _fail('SYNTHETIC_ONLY')
    _text(card['provider_id'], 128)
    _text(card['release'], 128)
    if type(card['capabilities']) is not list or len(card['capabilities']) > 100:
        _fail('INVALID_CAPABILITY')
    for c in card['capabilities']:
        _text(c, 128)
    if type(card['online']) is not bool:
        _fail('INVALID_CAPABILITY')
    if card['permission'] not in ('UNKNOWN', 'DECLARED_ONLY', 'SYNTHETIC_GRANTED'):
        _fail('INVALID_PERMISSION')
    quota = card['quota']
    _shape(quota, ('state', 'dimension', 'window', 'remaining', 'observed_at', 'expires_at'))
    for key in ('dimension', 'window'):
        _text(quota[key], 128)
    _number(now)
    _number(cost)
    _text(capability, 128)
    _text(dimension, 128)
    _text(window, 128)
    if cost == 0:
        _fail('INVALID_NUMBER')
    reason = 'SIMULATED_ELIGIBLE'
    if capability not in card['capabilities']:
        reason = 'BLOCKED_CAPABILITY'
    elif not card['online']:
        reason = 'BLOCKED_PROVIDER_OFFLINE'
    elif card['permission'] != 'SYNTHETIC_GRANTED':
        reason = 'BLOCKED_PERMISSION'
    elif quota['state'] != 'KNOWN':
        reason = 'BLOCKED_QUOTA_UNKNOWN'
    else:
        _number(quota['remaining'])
        _number(quota['observed_at'])
        _number(quota['expires_at'])
        if quota['dimension'] != dimension or quota['window'] != window:
            reason = 'BLOCKED_QUOTA_SCOPE'
        elif not quota['observed_at'] <= now < quota['expires_at']:
            reason = 'BLOCKED_QUOTA_STALE'
        elif quota['remaining'] < cost:
            reason = 'BLOCKED_QUOTA_EXHAUSTED'
    return {'schema': 'd5.offline-route-result.v1', 'result': reason,
            'permission_authority': 'SYNTHETIC_ONLY', 'activation_allowed': False,
            'fallback_allowed': False, 'quota_consumed': 0}


class MemoryLab:
    """Independent source/effect/projection review registries, all volatile."""
    def __init__(self, plane=None):
        if plane is not None and type(plane) is not MemoryPlane:
            _fail('SYNTHETIC_ONLY')
        self._plane = plane if plane is not None else MemoryPlane()
        self._captures = {}
        self._effects = {}
        self._projections = {}
        self._reviews = {}
        self._entities = {}
        self._bindings = {}
        self._receipts = {}

    @property
    def plane(self):
        return self._plane

    def capture(self, content, project_id, document_id, *, profile=PROFILE,
                source_kind='LOCAL_MARKDOWN', revision='fixture-1',
                metadata_before=None, metadata_after=None, repeated_bytes_equal=True):
        _id(project_id)
        _id(document_id)
        _text(profile, 128)
        _text(revision, 256)
        if type(content) is not bytes or len(content) > MAX_BYTES:
            _fail('SOURCE_LIMIT')
        if type(repeated_bytes_equal) is not bool:
            _fail('INVALID_CAPTURE')
        if source_kind not in ('LOCAL_MARKDOWN', 'DRIVE_BLOB', 'DRIVE_DOCS_EXPORT', 'TYPED_FIXTURE'):
            _fail('INVALID_SOURCE_KIND')
        before = after = None
        codes = []
        if source_kind.startswith('DRIVE_'):
            before, after = _metadata(metadata_before), _metadata(metadata_after)
            allowed = ('text/markdown', 'text/plain') if source_kind == 'DRIVE_BLOB' else ('application/vnd.google-apps.document',)
            if before['mime_type'] not in allowed:
                codes.append('BLOCKED_FORMAT')
            if before != after or not repeated_bytes_equal:
                codes.append('BLOCKED_CAPTURE_CHANGED')
        elif metadata_before is not None or metadata_after is not None:
            _fail('INVALID_CAPTURE')
        if profile not in PROFILES:
            codes.append('BLOCKED_PROFILE')
            preview = None
        else:
            try:
                preview = build_observation(content, 'fixture.md', project_id, document_id, revision, profile)
            except (ValueError, UnicodeError, RecursionError):
                _fail('INVALID_SOURCE')
            if any(d.get('blocking') for d in preview['diagnostics']):
                codes.append('BLOCKED_PARSE')
        result = {'schema': 'd5.offline-capture.v1', 'mode': 'SYNTHETIC_ONLY',
                  'project_id': project_id, 'document_id': document_id, 'profile': profile,
                  'source_kind': source_kind, 'revision_label': revision,
                  'content_base64': base64.b64encode(content).decode('ascii'),
                  'content_sha256': hashlib.sha256(content).hexdigest(), 'preview': preview,
                  'metadata_before': before, 'metadata_after': after,
                  'export_mime': 'text/plain' if source_kind == 'DRIVE_DOCS_EXPORT' else None,
                  'exporter': 'fixture-exporter.v1' if source_kind == 'DRIVE_DOCS_EXPORT' else None,
                  'provenance_grade': 'OBSERVED_EXPORT' if source_kind == 'DRIVE_DOCS_EXPORT' else 'SYNTHETIC_OBSERVATION',
                  'diagnostics': codes, 'state': 'BLOCKED' if codes else 'PREVIEW_ONLY',
                  'activation_allowed': False}
        key = digest(result)
        self._captures[key] = canonical(result)
        return key

    def capture_drive(self, drive, file_id, project_id, document_id, *, exported=False,
                      profile=PROFILE, change_during_read=None):
        if type(drive) is not MemoryDrive or type(exported) is not bool:
            _fail('SYNTHETIC_ONLY')
        content, before, after, equal = drive.read(file_id, change_during_read=change_during_read)
        return self.capture(content, project_id, document_id, profile=profile,
                            revision=before['version'], source_kind='DRIVE_DOCS_EXPORT' if exported else 'DRIVE_BLOB',
                            metadata_before=before, metadata_after=after, repeated_bytes_equal=equal)

    def capture_artifact(self, capture_id):
        if capture_id not in self._captures:
            _fail('CAPTURE_NOT_FOUND')
        value = json.loads(self._captures[capture_id])
        if digest(value) != capture_id:
            _fail('CAPTURE_TAMPERED')
        return value

    def review(self, stage, artifact_id, *, expected_version, decision, accept_observed_export=False):
        if stage not in ('SOURCE', 'EFFECT', 'PROJECTION') or decision not in ('ACCEPT', 'REJECT'):
            _fail('INVALID_REVIEW')
        _number(expected_version)
        if type(accept_observed_export) is not bool:
            _fail('INVALID_REVIEW')
        catalog = {'SOURCE': self._captures, 'EFFECT': self._effects, 'PROJECTION': self._projections}[stage]
        if artifact_id not in catalog:
            _fail('ARTIFACT_NOT_FOUND')
        if stage == 'SOURCE':
            capture = self.capture_artifact(artifact_id)
            if capture['state'] == 'BLOCKED':
                _fail('BLOCKED_CAPTURE')
            if decision == 'ACCEPT' and capture['provenance_grade'] == 'OBSERVED_EXPORT' and not accept_observed_export:
                _fail('EXPORT_GRADE_ACK_REQUIRED')
        elif accept_observed_export:
            _fail('INVALID_REVIEW')
        old = self._reviews.get((stage, artifact_id), {'version': 0, 'decision': None})
        if old['version'] != expected_version:
            _fail('CONFLICT_REVIEW_VERSION')
        if expected_version == 2**63 - 1:
            _fail('REVIEW_VERSION_EXHAUSTED')
        self._reviews[(stage, artifact_id)] = dict(version=expected_version + 1, decision=decision)
        return expected_version + 1

    def _accepted(self, stage, artifact_id, version):
        return self._reviews.get((stage, artifact_id)) == {'version': version, 'decision': 'ACCEPT'}

    def _candidate(self, capture_id, source_key):
        capture = self.capture_artifact(capture_id)
        _text(source_key, 256)
        if capture['state'] == 'BLOCKED':
            _fail('BLOCKED_CAPTURE')
        if capture['source_kind'] == 'TYPED_FIXTURE':
            value = decode_envelope(base64.b64decode(capture['content_base64']))
            found = _typed_elements(value['payload']).get(source_key)
            if found is None:
                _fail('SOURCE_KEY_NOT_FOUND')
            return capture, deepcopy(found), {'fixture_element': source_key}
        if capture['profile'] == PROFILE:
            _fail('PREVIEW_ONLY_NO_STABLE_ID')
        rows = [r for r in capture['preview']['proposals'] if r['source_key'] == source_key]
        if len(rows) != 1:
            _fail('SOURCE_KEY_NOT_FOUND')
        row = rows[0]
        return capture, dict(kind='TASK', source_key=source_key,
                             title=row['fields']['item'], description=row['fields']['objective']), deepcopy(row)

    def prepare_effect(self, capture_id, source_key, target_id, target_key, *, source_review_version):
        _id(target_id)
        _text(target_key, 256)
        _number(source_review_version)
        capture, candidate, evidence = self._candidate(capture_id, source_key)
        if not self._accepted('SOURCE', capture_id, source_review_version):
            _fail('SOURCE_REVIEW_REQUIRED')
        if not candidate['title'].strip():
            _fail('INVALID_TITLE')
        before = deepcopy(self._entities.get(target_id))
        identity = [capture['project_id'], capture['document_id'], capture['profile'], source_key, candidate['kind']]
        for existing_id, record in self._entities.items():
            if record['identity'] == identity and existing_id != target_id:
                _fail('CONFLICT_MAPPING')
            if record['entity']['project_id'] == capture['project_id'] and record['entity']['key'] == target_key and existing_id != target_id:
                _fail('CONFLICT_TARGET_KEY')
        if before is not None and (before['identity'] != identity or before['entity']['key'] != target_key):
            _fail('CONFLICT_MAPPING')
        entity = dict(id=target_id, project_id=capture['project_id'], key=target_key,
                      kind=candidate['kind'], title=candidate['title'],
                      status='DRAFT' if candidate['kind'] == 'REQUIREMENT' else 'BACKLOG',
                      row_version=0 if before is None else before['entity']['row_version'] + 1)
        if candidate['kind'] != 'EPIC':
            entity['description'] = candidate['description']
        manifest = dict(schema='d5.offline-effect.v1', mode='SYNTHETIC_ONLY',
                        capture_id=capture_id, source_review_version=source_review_version,
                        identity=identity, evidence=evidence, candidate=candidate,
                        before=before, after=entity, activation_allowed=False)
        key = digest(manifest)
        self._effects[key] = canonical(manifest)
        return key

    def manifest(self, stage, artifact_id):
        catalog = {'EFFECT': self._effects, 'PROJECTION': self._projections}.get(stage)
        if catalog is None or artifact_id not in catalog:
            _fail('ARTIFACT_NOT_FOUND')
        value = json.loads(catalog[artifact_id])
        if digest(value) != artifact_id:
            _fail('MANIFEST_TAMPERED')
        return value

    def _command(self, command_id, stage, artifact_id, review_version, operation):
        _id(command_id)
        _number(review_version)
        request = dict(stage=stage, artifact_id=artifact_id, review_version=review_version)
        request_hash = digest(request)
        if command_id in self._receipts:
            old = self._receipts[command_id]
            if old['request_sha256'] != request_hash:
                _fail('CONFLICT_COMMAND')
            return deepcopy(old)
        if not self._accepted(stage, artifact_id, review_version):
            _fail('EFFECT_REVIEW_REQUIRED' if stage == 'EFFECT' else 'PROJECTION_REVIEW_REQUIRED')
        outcome = operation()
        result = dict(schema='d5.offline-receipt.v1', mode='SYNTHETIC_ONLY',
                      command_id=command_id, stage=stage, manifest_sha256=artifact_id,
                      request_sha256=request_hash, result=outcome, activation_allowed=False,
                      persistent_D2_writes=0, remote_requests=0)
        self._receipts[command_id] = deepcopy(result)
        return result

    def apply_effect(self, command_id, artifact_id, *, review_version):
        manifest = self.manifest('EFFECT', artifact_id)
        def operation():
            capture_id = manifest['capture_id']
            self.capture_artifact(capture_id)
            if not self._accepted('SOURCE', capture_id, manifest['source_review_version']):
                return 'CONFLICT_SOURCE_REVIEW'
            before = self._entities.get(manifest['after']['id'])
            if before != manifest['before']:
                return 'CONFLICT_TARGET'
            for tid, record in self._entities.items():
                if tid != manifest['after']['id'] and (record['identity'] == manifest['identity'] or
                    (record['entity']['project_id'], record['entity']['key']) == (manifest['after']['project_id'], manifest['after']['key'])):
                    return 'CONFLICT_MAPPING'
            self._entities[manifest['after']['id']] = dict(identity=manifest['identity'], entity=manifest['after'])
            return 'SIMULATED_APPLIED'
        return self._command(command_id, 'EFFECT', artifact_id, review_version, operation)

    def entity(self, target_id):
        if target_id not in self._entities:
            _fail('ENTITY_NOT_FOUND')
        return deepcopy(self._entities[target_id]['entity'])

    def bind_plane(self, binding):
        _shape(binding, ('binding_id', 'internal_id', 'project_id', 'instance',
                         'workspace_id', 'remote_project_id', 'remote_id'))
        for key, value in binding.items():
            if key != 'instance':
                _id(value)
        if binding['instance'] != 'SYNTHETIC_PLANE':
            _fail('SYNTHETIC_ONLY')
        if (binding['workspace_id'] != self.plane._workspace_id or
                binding['remote_project_id'] != self.plane._project_id):
            _fail('CONFLICT_REMOTE_SCOPE')
        entity = self.entity(binding['internal_id'])
        if entity['project_id'] != binding['project_id'] or entity['kind'] != 'TASK':
            _fail('UNSUPPORTED_BINDING')
        self.plane.read(binding['remote_id'])
        for old in self._bindings.values():
            if old == binding:
                return
            if old['binding_id'] == binding['binding_id'] or old['internal_id'] == binding['internal_id'] or old['remote_id'] == binding['remote_id']:
                _fail('CONFLICT_BINDING')
        self._bindings[binding['binding_id']] = deepcopy(binding)

    def prepare_projection(self, binding_id):
        if binding_id not in self._bindings:
            _fail('BINDING_REQUIRED')
        binding = deepcopy(self._bindings[binding_id])
        entity = self.entity(binding['internal_id'])
        remote = self.plane.read(binding['remote_id'])
        value = dict(schema='d5.offline-projection.v1', mode='SYNTHETIC_ONLY',
                     binding=binding, local_entity=entity,
                     remote_base=self.plane.projection(remote),
                     remote_base_sha256=digest(self.plane.projection(remote)),
                     payload=dict(name=entity['title'], description=entity['description']),
                     activation_allowed=False)
        key = digest(value)
        self._projections[key] = canonical(value)
        return key

    def apply_projection(self, command_id, artifact_id, *, review_version):
        manifest = self.manifest('PROJECTION', artifact_id)
        def operation():
            binding = manifest['binding']
            if self._bindings.get(binding['binding_id']) != binding:
                return 'CONFLICT_BINDING'
            if self.entity(binding['internal_id']) != manifest['local_entity']:
                return 'CONFLICT_LOCAL_EDIT'
            return self.plane.patch(binding['remote_id'], manifest['remote_base_sha256'], manifest['payload'])
        return self._command(command_id, 'PROJECTION', artifact_id, review_version, operation)

    def summary(self):
        """Coverage labels describe a model, never a runtime test PASS or closure."""
        selected = set(FIRST_CRITERIA)
        return dict(schema='d5.offline-summary.v1', mode='SYNTHETIC_ONLY',
                    D5_closed=False, global_gaps_open=[f'G{i:02}' for i in range(1, 8)],
                    activation_allowed=False, persistent_D2_writes=0, remote_requests=0,
                    storage='VOLATILE_MEMORY', effects=len(self._entities), receipts=len(self._receipts),
                    real_validation_pending=[f'GI{i:02}' for i in range(6, 43, 6)],
                    criteria={f'GI{i:02}': 'SYNTHETIC_MODEL_ONLY' if i in selected else
                              'REAL_VALIDATION_PENDING' if i % 6 == 0 else 'NOT_IMPLEMENTED_THIS_CUT'
                              for i in range(1, 43)})
