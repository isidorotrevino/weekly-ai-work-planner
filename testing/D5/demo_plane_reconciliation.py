# SPDX-License-Identifier: GPL-3.0-only
"""In-memory lost-response example; prints statuses/counters, never fixture text."""
import json

from source_ingest.plane_fixture import (PlaneFixture, ReconciliationLab,
    binding, capabilities, task)


def fixture_id(n):
    return f'00000000-0000-4000-8000-{n:012d}'


def main():
    plane = PlaneFixture(capabilities())
    lab = ReconciliationLab(plane)
    b = binding(*(fixture_id(i) for i in range(1,6)))
    local = task(b['project_id'], b['task_id'])
    lab.bind(b, local)
    mid = lab.prepare(b['binding_id'])
    lab.review(mid, expected_version=0, decision='ACCEPT', reason='Synthetic creation')
    plane.send_mode = 'LOSE_AFTER'
    cid = fixture_id(10)
    first = lab.dispatch(cid, mid, review_version=1)
    local.update(title='New synthetic text', row_version=2)
    lab.edit_task(b['binding_id'], local)
    recovered = lab.reconcile(cid, expected_version=first['version'])
    newer = lab.prepare(b['binding_id'], 'UPDATE')
    lab.review(newer, expected_version=0, decision='ACCEPT', reason='Synthetic update')
    updated = lab.dispatch(fixture_id(11), newer, review_version=1)
    remote_id = updated['effect_receipt']['remote_id']
    plane.edit(remote_id, name='Later remote fixture edit')
    replay = lab.dispatch(cid, mid, review_version=1)
    assert plane.read(remote_id)['payload']['name'] == 'Later remote fixture edit'
    print(json.dumps(dict(schema='d5.plane-fixture-demo.v1',
        initial_result=first['result'], recovered_result=recovered['result'],
        recovered_validity=recovered['validity'], update_result=updated['result'],
        replay_result=replay['result'], remote_edit_preserved=True,
        fixture_objects=plane.count(), fixture_write_calls=plane.write_calls,
        fixture_query_calls=plane.query_calls, **lab.summary()), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
