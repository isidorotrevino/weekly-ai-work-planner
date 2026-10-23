# SPDX-License-Identifier: GPL-3.0-only
"""Public pure I36 relational planner, adapted from this repository's I30 model.

No private I30 calls or state restoration. Caller supplies validated fixture data.
"""
from copy import deepcopy
from .durable_store import fail, shape, identifier, digest
from .batch_fixture import identity, reference, text, DEPENDENCIES


def incident(data, eid):
    return {k: v for k, v in data['relations'].items() if eid in (v['left'], v['right'])}


def baseline(data, eid):
    return dict(entity=deepcopy(data['entities'][eid]), relations=deepcopy(incident(data, eid)))


def guard(data, eid):
    entity = data['entities'][eid]
    if eid not in data['mappings'] or eid not in data['bases']:
        fail('MAPPING_REQUIRED')
    if entity['has_work'] or entity['status'] != ('DRAFT' if entity['kind'] == 'REQUIREMENT' else 'BACKLOG'):
        fail('WORK_OR_STATE_GUARD')
    if baseline(data, eid) != data['bases'][eid]:
        fail('LOCAL_DIVERGENCE')


def validate_graph(data, project_id):
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


def acyclic(data):
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


def plan_batch(before, source, targets, *, bounds=None):
    limits = dict(elements=32, entities=128, relations=256) if bounds is None else bounds
    if type(targets) is not list or len(targets) > limits['elements']:
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
            guard(before, eid)
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
            guard(before, eid)
    # Requirements/epics also guard related tasks, including historical work flags.
    for eid in touched:
        kind = after['entities'][eid]['kind']
        epics = {eid} if kind == 'EPIC' else set()
        if kind == 'REQUIREMENT':
            epics = {r['left'] for r in after['relations'].values()
                     if r['type']=='EPIC_REQUIREMENT' and r['right']==eid}
        for tid, t in after['entities'].items():
            if t['kind']=='TASK' and t['epic_id'] in epics and tid in before['entities']:
                guard(before, tid)
    validate_graph(after, source['project_id'])
    acyclic(after)
    if len(after['entities']) > limits['entities'] or len(after['relations']) > limits['relations']:
        fail('STATE_BUDGET')
    for eid in touched:
        if eid not in new_ids and after['entities'][eid] != before['entities'][eid]:
            after['entities'][eid]['row_version'] = before['entities'][eid]['row_version'] + 1
        after['mappings'][eid]['version'] += 1
    for eid in touched:
        after['bases'][eid] = baseline(after, eid)
    return after, dict(entities=touched, relations=relation_locators,
                       created=sorted(new_ids), element_rows=rows)
