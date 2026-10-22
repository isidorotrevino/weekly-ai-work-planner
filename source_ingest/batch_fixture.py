# SPDX-License-Identifier: GPL-3.0-only
"""I30 trusted in-memory relational fixtures; no SQL, transport or durable state."""
import base64
from copy import deepcopy
import hashlib
import json
import threading
import uuid

SCHEMA = 'd5.relational-batch-fixture.v1'
KINDS = ('REQUIREMENT', 'EPIC', 'TASK')
DEPENDENCIES = ('HARD', 'SOFT', 'MOCKABLE', 'OPTIONAL')
MAX_SOURCE = 2 * 1024 * 1024
MAX_MANIFEST = 4 * 1024 * 1024
MAX_ELEMENTS = 32
MAX_DECLARATIONS = 64
MAX_ENTITIES = 128
MAX_RELATIONS = 256
MAX_COMMANDS = 128
MAX_TEXT = 8192


class BatchError(ValueError):
    pass


def fail(code):
    raise BatchError(code)


def canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False,
                          sort_keys=True, separators=(',', ':')).encode('utf-8')
    except (ValueError, TypeError, UnicodeError, RecursionError):
        fail('INVALID_JSON')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def byte_hash(value):
    return hashlib.sha256(value).hexdigest()


def shape(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        fail('INVALID_SHAPE')


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


def number(value, minimum=0):
    if type(value) is not int or value < minimum:
        fail('INVALID_VERSION')
    return value


def text(value, *, nullable=False, empty=False, maximum=MAX_TEXT):
    if nullable and value is None:
        return
    if (type(value) is not str or len(value) > maximum or '\x00' in value
            or (not empty and not value.strip())):
        fail('INVALID_TEXT')
    canonical(value)


def _pairs(values):
    result = {}
    for k, v in values:
        if k in result:
            fail('DUPLICATE_JSON_KEY')
        result[k] = v
    return result


def decode(raw):
    try:
        return json.loads(raw, object_pairs_hook=_pairs,
                          parse_constant=lambda _: fail('INVALID_JSON'))
    except (ValueError, TypeError, UnicodeError, RecursionError):
        fail('INVALID_JSON')


def reference(project_id, document_id, source_key, kind):
    return dict(project_id=project_id, document_id=document_id, source_key=source_key, kind=kind)


def identity(ref):
    shape(ref, ('project_id', 'document_id', 'source_key', 'kind'))
    identifier(ref['project_id']); identifier(ref['document_id'])
    text(ref['source_key'], maximum=256)
    if ref['kind'] not in KINDS:
        fail('INVALID_KIND')
    return dict(profile=SCHEMA, **deepcopy(ref))


def element(key, kind, title, description=None, *, status='CLAIM_ONLY', verified='CLAIM_ONLY'):
    return dict(source_key=key, kind=kind, title=title, description=description,
                claims=dict(status=status, verified=verified))


def declaration(key, relation_type, left, right, *, kind=None):
    return dict(declaration_key=key, type=relation_type, left=left, right=right, kind=kind)


def envelope(project_id, document_id, revision, elements, relations):
    return canonical(dict(schema=SCHEMA, mode='SYNTHETIC_ONLY', project_id=project_id,
                          document_id=document_id, revision=revision,
                          elements=elements, relations=relations))


def validate_source(raw):
    if type(raw) is not bytes or len(raw) > MAX_SOURCE:
        fail('SOURCE_BUDGET')
    value = decode(raw)
    shape(value, ('schema', 'mode', 'project_id', 'document_id', 'revision', 'elements', 'relations'))
    if value['schema'] != SCHEMA or value['mode'] != 'SYNTHETIC_ONLY':
        fail('SYNTHETIC_ONLY')
    identifier(value['project_id']); identifier(value['document_id'])
    text(value['revision'], maximum=128)
    for key, limit in [('elements', MAX_ELEMENTS), ('relations', MAX_DECLARATIONS)]:
        if type(value[key]) is not list or len(value[key]) > limit:
            fail('SOURCE_ITEM_BUDGET')
    keys = set()
    for item in value['elements']:
        shape(item, ('source_key', 'kind', 'title', 'description', 'claims'))
        identity(reference(value['project_id'], value['document_id'], item['source_key'], item['kind']))
        text(item['title']); text(item['description'], nullable=True, empty=True)
        shape(item['claims'], ('status', 'verified'))
        for claim in item['claims'].values():
            text(claim, empty=True)
        if item['source_key'] in keys:
            fail('DUPLICATE_SOURCE_KEY')
        keys.add(item['source_key'])
    keys = set()
    for rel in value['relations']:
        shape(rel, ('declaration_key', 'type', 'left', 'right', 'kind'))
        text(rel['declaration_key'], maximum=256)
        identity(rel['left']); identity(rel['right'])
        if rel['type'] not in ('EPIC_REQUIREMENT', 'TASK_EPIC', 'TASK_DEPENDENCY'):
            fail('UNSUPPORTED_RELATION')
        if (rel['type'] == 'TASK_DEPENDENCY' and rel['kind'] not in DEPENDENCIES
                or rel['type'] != 'TASK_DEPENDENCY' and rel['kind'] is not None):
            fail('INVALID_RELATION_KIND')
        if rel['declaration_key'] in keys:
            fail('DUPLICATE_DECLARATION_KEY')
        keys.add(rel['declaration_key'])
    return value


def _incident(data, eid):
    return {k: v for k, v in data['relations'].items() if eid in (v['left'], v['right'])}


def _baseline(data, eid):
    return dict(entity=deepcopy(data['entities'][eid]), relations=deepcopy(_incident(data, eid)))


def _guard(data, eid):
    entity = data['entities'][eid]
    if eid not in data['mappings'] or eid not in data['bases']:
        fail('MAPPING_REQUIRED')
    if entity['has_work'] or entity['status'] != ('DRAFT' if entity['kind'] == 'REQUIREMENT' else 'BACKLOG'):
        fail('WORK_OR_STATE_GUARD')
    if _baseline(data, eid) != data['bases'][eid]:
        fail('LOCAL_DIVERGENCE')


def _validate_graph(data, project_id):
    expected = {'EPIC_REQUIREMENT':('EPIC','REQUIREMENT'), 'TASK_EPIC':('TASK','EPIC'),
                'TASK_DEPENDENCY':('TASK','TASK')}
    pairs = {}
    for rid, rel in data['relations'].items():
        shape(rel, ('type','left','right','kind'))
        if rel['type'] not in expected or digest(rel) != rid:
            fail('INVALID_GRAPH_RELATION')
        if rel['left'] not in data['entities'] or rel['right'] not in data['entities']:
            fail('GRAPH_REFERENCE_MISSING')
        left, right = data['entities'][rel['left']], data['entities'][rel['right']]
        if left['project_id'] != project_id or right['project_id'] != project_id:
            fail('CROSS_PROJECT_OUT_OF_SCOPE')
        if (left['kind'],right['kind']) != expected[rel['type']]:
            fail('RELATION_TYPE_MISMATCH')
        if rel['type'] == 'TASK_DEPENDENCY':
            if rel['kind'] not in DEPENDENCIES:
                fail('INVALID_RELATION_KIND')
            if rel['left'] == rel['right']:
                fail('SELF_LOOP')
            pair=(rel['left'],rel['right'])
            if pair in pairs and pairs[pair] != rel['kind']:
                fail('DEPENDENCY_KIND_CONFLICT')
            pairs[pair]=rel['kind']
        elif rel['kind'] is not None:
            fail('INVALID_RELATION_KIND')
        elif rel['type']=='TASK_EPIC' and left['epic_id'] != rel['right']:
            fail('EPIC_REASSIGNMENT_FORBIDDEN')


def _acyclic(data):
    graph = {}
    for rel in data['relations'].values():
        if rel['type'] == 'TASK_DEPENDENCY' and rel['kind'] == 'HARD':
            graph.setdefault(rel['left'], set()).add(rel['right'])
    pending = set()
    done = set()
    def visit(node):
        if node in pending:
            fail('HARD_CYCLE')
        if node in done:
            return
        pending.add(node)
        for successor in graph.get(node, ()):
            visit(successor)
        pending.remove(node); done.add(node)
    for node in graph:
        visit(node)


def _candidate(before, source, targets):
    if type(targets) is not list or len(targets) > MAX_ELEMENTS:
        fail('INVALID_TARGETS')
    choices = {}
    for target in targets:
        shape(target, ('source_key', 'target_id', 'target_key'))
        text(target['source_key'], maximum=256); identifier(target['target_id'])
        text(target['target_key'], maximum=256)
        if target['source_key'] in choices:
            fail('DUPLICATE_TARGET')
        choices[target['source_key']] = target
    if set(choices) != {i['source_key'] for i in source['elements']}:
        fail('EXPLICIT_TARGETS_REQUIRED')
    after = deepcopy(before)
    touched = {}
    rows = {}
    new_ids = set()
    def touch(eid, locator):
        touched.setdefault(eid, []).append(locator)
    for index, row in enumerate(source['elements']):
        target = choices[row['source_key']]
        eid = target['target_id']
        if eid in rows:
            fail('MAPPING_CONFLICT')
        ident = identity(reference(source['project_id'], source['document_id'], row['source_key'], row['kind']))
        for other_id, mapping in after['mappings'].items():
            if mapping['identity'] == ident and other_id != eid:
                fail('MAPPING_CONFLICT')
        for other_id, entity in after['entities'].items():
            if (other_id != eid and entity['project_id'] == source['project_id']
                    and entity['kind'] == row['kind'] and entity['key'] == target['target_key']):
                fail('TARGET_KEY_CONFLICT')
        if eid in after['entities']:
            _guard(before, eid)
            mapping = after['mappings'][eid]
            if mapping['identity'] != ident or after['entities'][eid]['key'] != target['target_key']:
                fail('MAPPING_CONFLICT')
        else:
            new_ids.add(eid)
            after['entities'][eid] = dict(id=eid, project_id=source['project_id'], kind=row['kind'],
                key=target['target_key'], title=row['title'],
                status='DRAFT' if row['kind']=='REQUIREMENT' else 'BACKLOG',
                row_version=0, has_work=False, foreign=dict(note='synthetic'))
            if row['kind'] == 'TASK':
                after['entities'][eid]['epic_id'] = None
            after['mappings'][eid] = dict(identity=ident, version=0, source_base=None)
        entity = after['entities'][eid]
        entity['title'] = row['title']
        if row['kind'] != 'EPIC':
            entity['description'] = row['description']
        after['mappings'][eid]['source_base'] = deepcopy(row)
        rows[eid] = index
        touch(eid, f'/elements/{index}')
    def resolve(ref):
        ident = identity(ref)
        if ref['project_id'] != source['project_id']:
            fail('CROSS_PROJECT_OUT_OF_SCOPE')
        found = [eid for eid, m in after['mappings'].items() if m['identity'] == ident]
        if len(found) != 1:
            fail('REFERENCE_NOT_REGISTERED')
        return found[0]
    relation_locators = {}
    for index, rel in enumerate(source['relations']):
        left, right = resolve(rel['left']), resolve(rel['right'])
        actual = (after['entities'][left]['kind'], after['entities'][right]['kind'])
        expected = {'EPIC_REQUIREMENT':('EPIC','REQUIREMENT'), 'TASK_EPIC':('TASK','EPIC'),
                    'TASK_DEPENDENCY':('TASK','TASK')}[rel['type']]
        if actual != expected:
            fail('RELATION_TYPE_MISMATCH')
        if rel['type'] == 'TASK_DEPENDENCY':
            if left == right:
                fail('SELF_LOOP')
            if any(r['type']=='TASK_DEPENDENCY' and (r['left'],r['right'])==(left,right)
                   and r['kind']!=rel['kind'] for r in after['relations'].values()):
                fail('DEPENDENCY_KIND_CONFLICT')
        if rel['type'] == 'TASK_EPIC':
            current = after['entities'][left]['epic_id']
            if current is not None and current != right:
                fail('EPIC_REASSIGNMENT_FORBIDDEN')
            after['entities'][left]['epic_id'] = right
        relationship = dict(type=rel['type'], left=left, right=right, kind=rel['kind'])
        rid = digest(relationship)
        after['relations'][rid] = relationship
        locator = f'/relations/{index}'
        touch(left, locator); touch(right, locator)
        relation_locators.setdefault(rid, []).append(locator)
    # Guard all existing participants against their previous applied base.
    for eid in touched:
        if eid not in new_ids:
            _guard(before, eid)
    # Requirements/epics also guard related tasks, including historical work flags.
    for eid in touched:
        kind = after['entities'][eid]['kind']
        epics = {eid} if kind == 'EPIC' else set()
        if kind == 'REQUIREMENT':
            epics = {r['left'] for r in after['relations'].values()
                     if r['type']=='EPIC_REQUIREMENT' and r['right']==eid}
        for tid, t in after['entities'].items():
            if t['kind']=='TASK' and t['epic_id'] in epics and tid in before['entities']:
                _guard(before, tid)
    _validate_graph(after, source['project_id'])
    _acyclic(after)
    if len(after['entities']) > MAX_ENTITIES or len(after['relations']) > MAX_RELATIONS:
        fail('STATE_BUDGET')
    for eid in touched:
        if eid not in new_ids and after['entities'][eid] != before['entities'][eid]:
            after['entities'][eid]['row_version'] = before['entities'][eid]['row_version'] + 1
        after['mappings'][eid]['version'] += 1
    for eid in touched:
        after['bases'][eid] = _baseline(after, eid)
    return after, dict(entities=touched, relations=relation_locators,
                       created=sorted(new_ids), element_rows=rows)


class BatchLab:
    """One-project volatile state; _head is an immutable bytes/hash pointer."""
    def __init__(self, project_id, *, test_hook=None):
        self.project_id = identifier(project_id)
        self.test_hook = test_hook
        self._lock = threading.RLock()
        self._sources = {}
        self._manifests = {}
        self._head = None
        self._save(dict(schema='d5.batch-fixture-root.v1', project_id=project_id,
                        root_revision=0, data_generation=0,
                        data=dict(entities={},mappings={},relations={},bases={},
                                  entity_provenance={},relation_provenance={}),
                        reviews=dict(SOURCE={}, BATCH={}), receipts={}))

    def _save(self, root):
        raw = canonical(root)
        self._head = (raw, byte_hash(raw))

    def _load(self):
        raw, expected = self._head
        if byte_hash(raw) != expected:
            fail('ROOT_CORRUPT')
        return decode(raw)

    def _meta(self, root):
        root['root_revision'] += 1
        self._save(root)

    def capture(self, raw):
        source = validate_source(raw)
        if source['project_id'] != self.project_id:
            fail('PROJECT_MISMATCH')
        sid = byte_hash(raw)
        with self._lock:
            root = self._load()
            self._sources[sid] = raw
            if sid not in root['reviews']['SOURCE']:
                root['reviews']['SOURCE'][sid] = dict(version=0, decision=None, reason='')
                self._meta(root)
        return sid

    def source(self, sid):
        hash_id(sid)
        with self._lock:
            raw = self._sources.get(sid)
        if raw is None:
            fail('SOURCE_REQUIRED')
        if byte_hash(raw) != sid:
            fail('SOURCE_CORRUPT')
        return validate_source(raw)

    def source_artifact(self, sid):
        source = self.source(sid)
        with self._lock:
            return dict(source_sha256=sid, content_base64=base64.b64encode(self._sources[sid]).decode(),
                        profile=SCHEMA, source=source)

    def manifest(self, mid):
        hash_id(mid)
        with self._lock:
            raw = self._manifests.get(mid)
        if raw is None or byte_hash(raw) != mid:
            fail('MANIFEST_CORRUPT')
        result = decode(raw)
        if len(raw) > MAX_MANIFEST or canonical(result) != raw:
            fail('MANIFEST_CORRUPT')
        return result

    @staticmethod
    def _accepted(root, stage, key, version):
        value = root['reviews'][stage].get(key)
        return value is not None and value['version']==version and value['decision']=='ACCEPT'

    def review(self, stage, key, *, expected_version, decision, reason):
        if stage not in ('SOURCE','BATCH') or decision not in ('ACCEPT','REJECT'):
            fail('INVALID_REVIEW')
        hash_id(key); number(expected_version); text(reason)
        with self._lock:
            root = self._load()
            old = root['reviews'][stage].get(key)
            if old is None or old['version'] != expected_version:
                fail('CONFLICT_REVIEW')
            generation = None
            if stage == 'SOURCE':
                self.source(key)
            elif decision == 'ACCEPT':
                m = self.manifest(key)
                self._current(root, m)
                generation = m['data_generation']
            root['reviews'][stage][key] = dict(version=expected_version+1, decision=decision,
                                              reason=reason, data_generation=generation)
            self._meta(root)
            return expected_version+1

    def _current(self, root, m):
        if (root['data_generation'] != m['data_generation'] or digest(root['data']) != m['data_sha256']):
            fail('CONFLICT_DATA')
        self.source(m['source_id'])
        if not self._accepted(root, 'SOURCE', m['source_id'], m['source_review_version']):
            fail('CONFLICT_SOURCE_REVIEW')

    def prepare(self, sid, targets, *, source_review_version):
        number(source_review_version, 1)
        source = self.source(sid)
        with self._lock:
            root = self._load()
            if not self._accepted(root, 'SOURCE', sid, source_review_version):
                fail('SOURCE_REVIEW_REQUIRED')
        after, plan = _candidate(root['data'], source, targets)
        m = dict(schema='d5.batch-fixture-manifest.v1', mode='SYNTHETIC_ONLY', project_id=self.project_id,
                 source_id=sid, source_review_version=source_review_version,
                 data_generation=root['data_generation'], data_sha256=digest(root['data']),
                 targets=deepcopy(targets), after_data=after, plan=plan, activation_allowed=False)
        raw = canonical(m)
        if len(raw) > MAX_MANIFEST:
            fail('MANIFEST_BUDGET')
        mid = byte_hash(raw)
        with self._lock:
            root = self._load()
            self._manifests[mid] = raw
            if mid not in root['reviews']['BATCH']:
                root['reviews']['BATCH'][mid] = dict(version=0, decision=None, reason='')
                self._meta(root)
        return mid

    def _hook(self, stage):
        if self.test_hook is not None:
            self.test_hook(stage)

    def apply(self, cid, mid, *, batch_review_version, data_generation):
        identifier(cid); hash_id(mid); number(batch_review_version, 1); number(data_generation)
        request_hash = digest(dict(manifest_id=mid, batch_review_version=batch_review_version,
                                   data_generation=data_generation))
        with self._lock:
            root = self._load()
            old = root['receipts'].get(cid)
            if old is not None:
                if old['request_sha256'] != request_hash:
                    fail('COMMAND_CONFLICT')
                return deepcopy(old)
            m = self.manifest(mid)
            self._authorize(root, m, mid, batch_review_version, data_generation)
        source = self.source(m['source_id'])
        after, plan = _candidate(root['data'], source, m['targets'])
        if after != m['after_data'] or plan != m['plan']:
            fail('MANIFEST_PLAN_CONFLICT')
        self._hook('candidate_ready')
        self._hook('before_publish')
        with self._lock:
            current = self._load()
            # A same-command race recovers the first publication rather than repeating it.
            old = current['receipts'].get(cid)
            if old is not None:
                if old['request_sha256'] != request_hash:
                    fail('COMMAND_CONFLICT')
                return deepcopy(old)
            self._authorize(current, m, mid, batch_review_version, data_generation)
            if len(current['receipts']) >= MAX_COMMANDS:
                fail('COMMAND_BUDGET')
            evidence = dict(source_sha256=m['source_id'], manifest_sha256=mid,
                            source_review_version=m['source_review_version'], batch_review_version=batch_review_version)
            for eid, locators in plan['entities'].items():
                after['entity_provenance'].setdefault(eid, []).append(dict(**evidence, locators=locators))
            for rid, locators in plan['relations'].items():
                after['relation_provenance'].setdefault(rid, []).append(dict(**evidence, locators=locators))
            receipt = dict(schema='d5.batch-fixture-receipt.v1', mode='SYNTHETIC_ONLY', command_id=cid,
                           request_sha256=request_hash, manifest_sha256=mid, source_sha256=m['source_id'],
                           result='SIMULATED_BATCH_APPLIED', data_generation=data_generation+1,
                           data_sha256=digest(after), created=len(plan['created']),
                           participants=len(plan['entities']), declared_relations=len(plan['relations']),
                           activation_allowed=False, persistent_D2_writes=0, remote_requests=0)
            current['data'] = after
            current['receipts'][cid] = receipt
            current['data_generation'] += 1
            current['root_revision'] += 1
            self._save(current)  # one publication: data, provenance and receipt together
        self._hook('after_publish')
        return deepcopy(receipt)

    def _authorize(self, root, m, mid, version, generation):
        self._current(root, m)
        review = root['reviews']['BATCH'].get(mid)
        if (not self._accepted(root, 'BATCH', mid, version) or review.get('data_generation') != generation
                or generation != m['data_generation']):
            fail('BATCH_REVIEW_REQUIRED')

    def read_command(self, cid, request_hash):
        identifier(cid); hash_id(request_hash)
        with self._lock:
            receipt = self._load()['receipts'].get(cid)
            if receipt is None:
                fail('COMMAND_NOT_CONFIRMED')
            if receipt['request_sha256'] != request_hash:
                fail('COMMAND_CONFLICT')
            return deepcopy(receipt)

    def fixture_edit_entity(self, eid, changes):
        """Trusted negative-fixture mutation: flags/states are not operations."""
        identifier(eid)
        if type(changes) is not dict or not changes or not set(changes) <= {'title','description','epic_id','foreign','has_work','status'}:
            fail('INVALID_FIXTURE_EDIT')
        for key,value in changes.items():
            if key=='has_work' and type(value) is not bool:
                fail('INVALID_FIXTURE_EDIT')
            if key in ('title','status'):
                text(value)
            if key=='description':
                text(value, nullable=True, empty=True)
            if key=='epic_id' and value is not None:
                identifier(value)
            if key=='foreign':
                shape(value, ('note',)); text(value['note'], empty=True)
        with self._lock:
            root=self._load()
            if eid not in root['data']['entities']:
                fail('ENTITY_REQUIRED')
            entity=root['data']['entities'][eid]
            if ('description' in changes and entity['kind']=='EPIC'
                    or 'epic_id' in changes and entity['kind']!='TASK'):
                fail('INVALID_FIXTURE_EDIT')
            entity.update(deepcopy(changes)); entity['row_version'] += 1
            root['data_generation'] += 1; root['root_revision'] += 1
            self._save(root)

    def fixture_add_relation(self, relation):
        """Trusted local-edit fixture; deliberately does not bless an applied base."""
        shape(relation, ('type','left','right','kind'))
        identifier(relation['left']); identifier(relation['right'])
        if relation['type'] not in ('EPIC_REQUIREMENT','TASK_EPIC','TASK_DEPENDENCY'):
            fail('INVALID_FIXTURE_RELATION')
        if (relation['type']=='TASK_DEPENDENCY' and relation['kind'] not in DEPENDENCIES
                or relation['type']!='TASK_DEPENDENCY' and relation['kind'] is not None):
            fail('INVALID_FIXTURE_RELATION')
        with self._lock:
            root=self._load(); data=root['data']
            if relation['left'] not in data['entities'] or relation['right'] not in data['entities']:
                fail('ENTITY_REQUIRED')
            data['relations'][digest(relation)] = deepcopy(relation)
            root['data_generation'] += 1; root['root_revision'] += 1
            self._save(root)

    def inspect(self):
        """Private full fixture snapshot. Returned objects cannot mutate authority."""
        with self._lock:
            return self._load()

    def summary(self):
        with self._lock:
            r=self._load()
            return dict(mode='SYNTHETIC_ONLY', storage='VOLATILE_MEMORY', root_revision=r['root_revision'],
                        data_generation=r['data_generation'], entities=len(r['data']['entities']),
                        relations=len(r['data']['relations']), confirmed_commands=len(r['receipts']),
                        persistent_D2_writes=0, remote_requests=0, operational_activation=False,
                        D5_closed=False, global_gaps_open=[f'G{i:02}' for i in range(1,8)])
