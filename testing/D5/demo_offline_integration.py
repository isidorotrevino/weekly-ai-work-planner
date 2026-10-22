# SPDX-License-Identifier: GPL-3.0-only
"""Fixed synthetic demo. Reads one tracked fixture, writes nothing, no arguments."""
import json
from pathlib import Path

from source_ingest.offline import MemoryDrive, MemoryLab, MemoryPlane, evaluate_route


def demo():
    ids = [f'00000000-0000-4000-8000-{i:012d}' for i in range(1, 12)]
    project, document, target, remote, binding_id = ids[:5]
    plane = MemoryPlane(cas_supported=True)
    lab = MemoryLab(plane)
    drive = MemoryDrive()
    # This catalog is a double; it does not receive a Drive URL or credentials.
    drive.seed('fixture-register', (Path(__file__).parent / 'fixtures/register-before.md').read_bytes())
    capture = lab.capture_drive(drive, 'fixture-register', project, document, profile='task-register.v1')
    lab.review('SOURCE', capture, expected_version=0, decision='ACCEPT')
    effect = lab.prepare_effect(capture, 'PT-01', target, 'FIXTURE-TASK', source_review_version=1)
    lab.review('EFFECT', effect, expected_version=0, decision='ACCEPT')
    applied = lab.apply_effect(ids[5], effect, review_version=1)
    plane.seed(remote, dict(name='Previous fixture name', description='Previous fixture text', labels=['preserved']))
    lab.bind_plane(dict(binding_id=binding_id, internal_id=target, project_id=project,
                        instance='SYNTHETIC_PLANE', workspace_id=ids[9],
                        remote_project_id=ids[10], remote_id=remote))
    projection = lab.prepare_projection(binding_id)
    lab.review('PROJECTION', projection, expected_version=0, decision='ACCEPT')
    projected = lab.apply_projection(ids[6], projection, review_version=1)
    card = dict(schema='d5.offline-provider.v1', provider_id='fixture-provider', release='fixture-v1',
                capabilities=['extract'], online=True, permission='SYNTHETIC_GRANTED',
                quota=dict(state='KNOWN', dimension='OPERATIONS', window='fixture-window',
                           remaining=5, observed_at=10, expires_at=20))
    routing = evaluate_route(card, capability='extract', dimension='OPERATIONS',
                             window='fixture-window', now=15)
    return dict(schema='d5.offline-demo.v1', capture_sha256=capture,
                effect_receipt=applied, projection_receipt=projected, route=routing,
                projected_fields=['name', 'description'], preserved_fields=['labels'],
                summary=lab.summary())


if __name__ == '__main__':
    print(json.dumps(demo(), indent=2, sort_keys=True))
