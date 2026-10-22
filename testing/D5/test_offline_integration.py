# SPDX-License-Identifier: GPL-3.0-only
"""I24 tests: expected contract behavior, not real integration conformance."""
import base64
from copy import deepcopy
from contextlib import ExitStack
import json
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch
import uuid

from source_ingest.offline import (ContractError, FIRST_CRITERIA, MAX_ENVELOPE,
    MemoryDrive, MemoryLab, MemoryPlane, canonical, decode_envelope, digest,
    envelope, evaluate_route)
from source_ingest.preview import build_observation

PROJECT = '00000000-0000-4000-8000-000000000001'
DOCUMENT = '00000000-0000-4000-8000-000000000002'
TARGET = '00000000-0000-4000-8000-000000000003'
REMOTE = '00000000-0000-4000-8000-000000000004'
BINDING = '00000000-0000-4000-8000-000000000005'
WORKSPACE = '00000000-0000-4000-8000-000000000010'
REMOTE_PROJECT = '00000000-0000-4000-8000-000000000011'
PROFILE = 'task-register.v1'


def command():
    return str(uuid.uuid4())


def provider():
    return dict(schema='d5.offline-provider.v1', provider_id='fixture-provider',
                release='fixture-v1', capabilities=['extract'], online=True,
                permission='SYNTHETIC_GRANTED', quota=dict(state='KNOWN',
                dimension='OPERATIONS', window='fixture-window', remaining=5,
                observed_at=10, expires_at=20))


class OfflineIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.register = Path('testing/D5/fixtures/register-before.md').read_bytes()
        self.compat = Path('testing/D5/fixtures/register-compat-before.md').read_bytes()
        self.plan = Path('testing/D5/fixtures/plan.md').read_bytes()
        self.lab = MemoryLab(MemoryPlane(cas_supported=True))

    def capture(self, content=None, profile=PROFILE, **extra):
        return self.lab.capture(self.register if content is None else content,
                                PROJECT, DOCUMENT, profile=profile, **extra)

    def effect(self, key='PT-01', target=TARGET, capture=None):
        cap = capture or self.capture()
        self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT')
        proposal = self.lab.prepare_effect(cap, key, target, 'FIXTURE-TASK', source_review_version=1)
        return cap, proposal

    def applied(self):
        cap, proposal = self.effect()
        self.lab.review('EFFECT', proposal, expected_version=0, decision='ACCEPT')
        result = self.lab.apply_effect(command(), proposal, review_version=1)
        self.assertEqual('SIMULATED_APPLIED', result['result'])
        return cap, proposal

    def binding(self):
        return dict(binding_id=BINDING, internal_id=TARGET, project_id=PROJECT,
                    instance='SYNTHETIC_PLANE', workspace_id=WORKSPACE,
                    remote_project_id=REMOTE_PROJECT, remote_id=REMOTE)

    def projection(self):
        self.applied()
        self.lab.plane.seed(REMOTE, dict(name='Old name', description='Old description',
                                        state='DONE', labels=['preserve'], comments=['foreign']))
        self.lab.bind_plane(self.binding())
        return self.lab.prepare_projection(BINDING)

    def test_GI01_exact_bytes_fields_and_existing_profile_reconstruction(self):
        cap = self.capture()
        artifact = self.lab.capture_artifact(cap)
        self.assertEqual(self.register, base64.b64decode(artifact['content_base64']))
        expected = build_observation(self.register, 'fixture.md', PROJECT, DOCUMENT, 'fixture-1', PROFILE)
        self.assertEqual(expected, artifact['preview'])
        self.assertEqual(5, expected['proposals'][0]['line_start'])
        self.assertIn('source_locator', expected['proposals'][0])
        self.assertEqual('CLOSED', expected['proposals'][1]['fields']['status'])
        artifact['preview']['proposals'].clear()
        self.assertEqual(3, len(self.lab.capture_artifact(cap)['preview']['proposals']))

    def test_GI01_unknown_profile_retains_bytes_but_cannot_be_reviewed(self):
        cap = self.capture(profile='unknown-profile.v1')
        artifact = self.lab.capture_artifact(cap)
        self.assertEqual(['BLOCKED_PROFILE'], artifact['diagnostics'])
        self.assertEqual(self.register, base64.b64decode(artifact['content_base64']))
        with self.assertRaisesRegex(ContractError, 'BLOCKED_CAPTURE'):
            self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT')

    def test_GI01_compatibility_remains_opt_in_and_annotations_stay_raw(self):
        strict = self.lab.capture_artifact(self.capture(self.compat))
        compat = self.lab.capture_artifact(self.capture(self.compat, 'task-register-compat.v1'))
        self.assertEqual('BLOCKED', strict['state'])
        self.assertEqual('PREVIEW_ONLY', compat['state'])
        self.assertEqual(' ; first source claim', compat['preview']['proposals'][0]['source_annotation']['text'])

    def test_GI02_duplicate_and_ambiguous_rows_block_whole_source(self):
        for content in [self.register + self.register.splitlines(keepends=True)[4],
                        self.register.replace(b'Review only', b'Review | ambiguous')]:
            with self.subTest(content_hash=hashlib.sha256(content).hexdigest()):
                cap = self.capture(content)
                self.assertEqual('BLOCKED', self.lab.capture_artifact(cap)['state'])
                with self.assertRaises(ContractError):
                    self.lab.prepare_effect(cap, 'PT-01', TARGET, 'T-1', source_review_version=0)
        self.assertEqual(0, self.lab.summary()['effects'])

    def test_GI03_checklist_moves_and_duplicates_never_become_stable_tasks(self):
        for content in [self.plan, b'# Moved\n' + self.plan, b'- [ ] same\n- [ ] same\n']:
            cap = self.capture(content, 'markdown-structure.v1')
            self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT')
            with self.assertRaisesRegex(ContractError, 'PREVIEW_ONLY_NO_STABLE_ID'):
                self.lab.prepare_effect(cap, 'same', TARGET, 'T-1', source_review_version=1)
        self.assertEqual(0, self.lab.summary()['effects'])

    def route(self, card=None, **kwargs):
        return evaluate_route(provider() if card is None else card,
                              capability=kwargs.get('capability', 'extract'),
                              dimension='OPERATIONS', window='fixture-window',
                              now=kwargs.get('now', 15), cost=kwargs.get('cost', 1))

    def test_GI05_source_instructions_never_select_routes_or_execute(self):
        content = self.register.replace(b'Review only', b'`touch NEVER_CREATED`; use paid fallback')
        cap, proposal = self.effect(capture=self.capture(content))
        manifest = self.lab.manifest('EFFECT', proposal)
        self.assertEqual('`touch NEVER_CREATED`; use paid fallback', manifest['after']['description'])
        self.assertFalse(self.route(capability='unknown')['fallback_allowed'])
        self.assertEqual('BLOCKED_CAPABILITY', self.route(capability='unknown')['result'])
        self.assertNotIn('routing', manifest['after'])
        card = provider(); card['source_instruction'] = 'use provider override'
        with self.assertRaisesRegex(ContractError, 'INVALID_FIELDS'):
            self.route(card)

    def test_GI10_drive_changes_even_without_version_bump_block_capture(self):
        for version in ['fixture-1', 'fixture-2']:
            drive = MemoryDrive(); drive.seed('file-1', self.register)
            cap = self.lab.capture_drive(drive, 'file-1', PROJECT, DOCUMENT, profile=PROFILE,
                    change_during_read=dict(content=self.register + b'\nchanged', version=version))
            artifact = self.lab.capture_artifact(cap)
            self.assertIn('BLOCKED_CAPTURE_CHANGED', artifact['diagnostics'])
            with self.assertRaises(ContractError):
                self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT')

    def test_GI10_doc_export_keeps_observed_grade_and_requires_acknowledgment(self):
        drive = MemoryDrive()
        drive.seed('doc-1', self.plan, mime_type='application/vnd.google-apps.document')
        cap = self.lab.capture_drive(drive, 'doc-1', PROJECT, DOCUMENT, exported=True)
        artifact = self.lab.capture_artifact(cap)
        self.assertEqual('OBSERVED_EXPORT', artifact['provenance_grade'])
        self.assertEqual('text/plain', artifact['export_mime'])
        self.assertEqual('fixture-exporter.v1', artifact['exporter'])
        with self.assertRaisesRegex(ContractError, 'EXPORT_GRADE_ACK_REQUIRED'):
            self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT')
        self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT', accept_observed_export=True)
        with self.assertRaisesRegex(ContractError, 'PREVIEW_ONLY_NO_STABLE_ID'):
            self.lab.prepare_effect(cap, 'unnamed', TARGET, 'T-1', source_review_version=1)

    def test_GI10_pdf_docx_and_wrong_export_mime_do_not_become_text_profiles(self):
        for mime in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            drive = MemoryDrive(); drive.seed('file-1', self.register, mime_type=mime)
            cap = self.lab.capture_drive(drive, 'file-1', PROJECT, DOCUMENT, profile=PROFILE)
            self.assertEqual('BLOCKED', self.lab.capture_artifact(cap)['state'])
        drive = MemoryDrive(); drive.seed('file-1', self.register)
        cap = self.lab.capture_drive(drive, 'file-1', PROJECT, DOCUMENT, exported=True, profile=PROFILE)
        self.assertEqual('BLOCKED', self.lab.capture_artifact(cap)['state'])

    def test_GI13_explicit_binding_projection_preserves_foreign_fields_and_D2_state(self):
        projection = self.projection()
        self.assertEqual(dict(name='Old name', description='Old description'),
                         self.lab.manifest('PROJECTION', projection)['remote_base'])
        self.lab.review('PROJECTION', projection, expected_version=0, decision='ACCEPT')
        result = self.lab.apply_projection(command(), projection, review_version=1)
        self.assertEqual('SIMULATED_PROJECTED', result['result'])
        remote = self.lab.plane.read(REMOTE)
        self.assertEqual(r'Review A \| B', remote['name'])
        self.assertEqual('Review only', remote['description'])
        self.assertEqual(['preserve'], remote['labels'])
        self.assertEqual(['foreign'], remote['comments'])
        self.assertEqual('DONE', remote['state'])
        self.assertEqual('BACKLOG', self.lab.entity(TARGET)['status'])

    def test_GI13_no_name_adoption_wrong_scope_or_real_instance(self):
        self.applied()
        self.lab.plane.seed(REMOTE, dict(name=r'Review A \| B', description='Review only'))
        with self.assertRaisesRegex(ContractError, 'BINDING_REQUIRED'):
            self.lab.prepare_projection(BINDING)
        for key, value in [('workspace_id', command()), ('project_id', command()),
                           ('instance', 'https://example.invalid')]:
            binding = self.binding(); binding[key] = value
            with self.subTest(key=key), self.assertRaises(ContractError):
                self.lab.bind_plane(binding)
        self.assertEqual(0, len(self.lab._bindings))

    def test_GI14_missing_atomic_capability_blocks_even_after_approval(self):
        projection = self.projection()
        self.lab.plane.cas_supported = False
        before = self.lab.plane.read(REMOTE)
        self.lab.review('PROJECTION', projection, expected_version=0, decision='ACCEPT')
        command_id = command()
        result = self.lab.apply_projection(command_id, projection, review_version=1)
        self.assertEqual('BLOCKED_ATOMIC_CAPABILITY', result['result'])
        self.assertEqual(before, self.lab.plane.read(REMOTE))
        self.lab.plane.cas_supported = True
        self.assertEqual(result, self.lab.apply_projection(command_id, projection, review_version=1))
        self.assertEqual(before, self.lab.plane.read(REMOTE))

    def test_GI14_remote_edit_before_or_during_atomic_check_is_never_overwritten(self):
        for during in [False, True]:
            self.lab = MemoryLab(MemoryPlane(cas_supported=True))
            proposal = self.projection()
            self.lab.review('PROJECTION', proposal, expected_version=0, decision='ACCEPT')
            self.lab.plane.edit_fixture(REMOTE, dict(name='Concurrent edit'), during_next_cas=during)
            result = self.lab.apply_projection(command(), proposal, review_version=1)
            self.assertEqual('CONFLICT_REMOTE_EDIT', result['result'])
            self.assertEqual('Concurrent edit', self.lab.plane.read(REMOTE)['name'])
            self.assertEqual(r'Review A \| B', self.lab.entity(TARGET)['title'])

    def test_GI14_unrelated_remote_edit_is_preserved(self):
        proposal = self.projection()
        self.lab.review('PROJECTION', proposal, expected_version=0, decision='ACCEPT')
        self.lab.plane.edit_fixture(REMOTE, dict(comments=['new unrelated comment']))
        self.assertEqual('SIMULATED_PROJECTED', self.lab.apply_projection(command(), proposal, review_version=1)['result'])
        self.assertEqual(['new unrelated comment'], self.lab.plane.read(REMOTE)['comments'])

    def test_GI19_unknown_stale_zero_and_invalid_quota_never_grant_work(self):
        changes = [dict(state='UNKNOWN'), dict(state='UNLIMITED_DECLARED'),
                   dict(remaining=0), dict(expires_at=15), dict(observed_at=16)]
        for delta in changes:
            card = provider(); card['quota'].update(delta)
            self.assertTrue(self.route(card)['result'].startswith('BLOCKED'))
        for invalid in [-1, True, 1.5, float('nan')]:
            card = provider(); card['quota']['remaining'] = invalid
            with self.subTest(invalid=repr(invalid)), self.assertRaises(ContractError):
                self.route(card)
        self.assertEqual('SIMULATED_ELIGIBLE', self.route()['result'])
        self.assertFalse(self.route()['activation_allowed'])

    def test_GI19_quota_observation_is_not_consumption_or_cross_scope_capacity(self):
        card = provider(); before = deepcopy(card)
        self.route(card); self.route(card)
        self.assertEqual(before, card)
        card['quota']['window'] = 'another-window'
        self.assertEqual('BLOCKED_QUOTA_SCOPE', self.route(card)['result'])
        self.assertEqual(0, self.route(card)['quota_consumed'])

    def test_GI21_provider_permission_capability_fail_without_paid_fallback(self):
        for delta in [dict(online=False), dict(permission='UNKNOWN'),
                      dict(permission='DECLARED_ONLY'), dict(capabilities=['different'])]:
            card = provider(); card.update(delta)
            result = self.route(card)
            self.assertTrue(result['result'].startswith('BLOCKED'))
            self.assertFalse(result['fallback_allowed'])
            self.assertFalse(result['activation_allowed'])
            self.assertEqual('SYNTHETIC_ONLY', result['permission_authority'])

    def test_GI23_closed_envelopes_reject_credentials_duplicates_nan_and_modes(self):
        good = envelope(dict(schema='d5.offline-typed-fixture.v1', elements=[
            dict(kind='TASK', source_key='FIXTURE-1', title='Fixture', description='Text')]))
        self.assertEqual(good, decode_envelope(canonical(good)))
        values = [b'{"schema":"a","schema":"b","mode":"SYNTHETIC_ONLY","payload":{}}',
                  b'{"schema":"d5.offline-envelope.v1","mode":"SYNTHETIC_ONLY","payload":NaN}',
                  canonical(dict(good, api_key='SYNTHETIC_PRIVATE_SENTINEL')),
                  canonical(dict(good, mode='REAL')),
                  canonical(envelope(dict(schema='d5.offline-typed-fixture.v1',
                      elements=[], auth_token='SYNTHETIC_PRIVATE_SENTINEL')))]
        for value in values:
            with self.assertRaises(ContractError) as caught:
                decode_envelope(value)
            self.assertNotIn('PRIVATE_SENTINEL', str(caught.exception))
        with self.assertRaises(ContractError):
            decode_envelope(b' ' * (MAX_ENVELOPE + 1))
        card = provider(); card['auth_token'] = 'SYNTHETIC_PRIVATE_SENTINEL'
        with self.assertRaises(ContractError):
            self.route(card)

    def test_GI23_receipts_and_errors_do_not_echo_source_text(self):
        content = self.register.replace(b'Review only', b'SYNTHETIC_PRIVATE_SENTINEL')
        _, proposal = self.effect(capture=self.capture(content))
        self.lab.review('EFFECT', proposal, expected_version=0, decision='ACCEPT')
        receipt = self.lab.apply_effect(command(), proposal, review_version=1)
        self.assertNotIn('SYNTHETIC_PRIVATE_SENTINEL', json.dumps(receipt))
        with self.assertRaises(ContractError) as caught:
            self.capture(b'\xff')
        self.assertEqual('INVALID_SOURCE', str(caught.exception))

    def typed(self, kind, extra=None):
        item = dict(kind=kind, source_key='FIXTURE-1', title='Explicit fixture', description='Extra source text')
        if extra: item.update(extra)
        data = canonical(envelope(dict(schema='d5.offline-typed-fixture.v1', elements=[item])))
        return self.capture(data, 'markdown-structure.v1', source_kind='TYPED_FIXTURE')

    def test_GI25_narrative_does_not_infer_requirements_epics_or_dependencies(self):
        cap = self.capture(b'# Epic\nRequirement: something\nBlocked on: external\n', 'markdown-structure.v1')
        self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT')
        with self.assertRaisesRegex(ContractError, 'PREVIEW_ONLY_NO_STABLE_ID'):
            self.lab.prepare_effect(cap, 'something', TARGET, 'REQ-1', source_review_version=1)
        self.assertEqual(0, self.lab.summary()['effects'])
        _, proposal = self.effect()
        self.assertEqual('TASK', self.lab.manifest('EFFECT', proposal)['after']['kind'])
        self.assertNotIn('dependencies', self.lab.manifest('EFFECT', proposal)['after'])

    def test_GI26_typed_fixture_preserves_epic_extra_text_as_evidence_only(self):
        cap = self.typed('EPIC')
        _, proposal = self.effect(key='FIXTURE-1', capture=cap)
        manifest = self.lab.manifest('EFFECT', proposal)
        self.assertEqual('Extra source text', manifest['candidate']['description'])
        self.assertNotIn('description', manifest['after'])
        self.assertEqual('EPIC', manifest['after']['kind'])
        self.assertEqual(TARGET, manifest['after']['id'])
        self.assertEqual(PROJECT, manifest['after']['project_id'])
        for unknown in [dict(status='DONE'), dict(dependencies=['other']), dict(api_key='synthetic')]:
            bad = self.typed('EPIC', unknown)
            self.lab.review('SOURCE', bad, expected_version=0, decision='ACCEPT')
            with self.assertRaisesRegex(ContractError, 'INVALID_FIELDS'):
                self.lab.prepare_effect(bad, 'FIXTURE-1', command(), 'E-2', source_review_version=1)

    def test_GI26_explicit_uuid_binding_does_not_adopt_by_title(self):
        self.applied()
        cap = self.capture(self.register + b'\n')
        self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT')
        with self.assertRaisesRegex(ContractError, 'CONFLICT_MAPPING'):
            self.lab.prepare_effect(cap, 'PT-01', command(), 'another-key', source_review_version=1)
        self.assertEqual(1, self.lab.summary()['effects'])

    def test_GI27_source_accept_is_not_effect_or_projection_accept(self):
        cap, proposal = self.effect()
        with self.assertRaisesRegex(ContractError, 'EFFECT_REVIEW_REQUIRED'):
            self.lab.apply_effect(command(), proposal, review_version=1)
        with self.assertRaisesRegex(ContractError, 'ARTIFACT_NOT_FOUND'):
            self.lab.review('EFFECT', cap, expected_version=0, decision='ACCEPT')
        self.lab.review('EFFECT', proposal, expected_version=0, decision='ACCEPT')
        self.lab.apply_effect(command(), proposal, review_version=1)
        self.lab.plane.seed(REMOTE, dict(name='old', description='old'))
        self.lab.bind_plane(self.binding())
        projection = self.lab.prepare_projection(BINDING)
        with self.assertRaisesRegex(ContractError, 'PROJECTION_REVIEW_REQUIRED'):
            self.lab.apply_projection(command(), projection, review_version=1)

    def test_GI27_source_claims_never_choose_initial_workflow(self):
        cap = self.capture()
        _, proposal = self.effect('PT-02', capture=cap)
        self.assertEqual('BACKLOG', self.lab.manifest('EFFECT', proposal)['after']['status'])
        self.lab = MemoryLab()
        cap = self.typed('REQUIREMENT')
        _, proposal = self.effect('FIXTURE-1', capture=cap)
        self.assertEqual('DRAFT', self.lab.manifest('EFFECT', proposal)['after']['status'])

    def test_GI27_review_versions_reject_reaccept_pins_and_mutable_artifact_copies(self):
        cap, proposal = self.effect()
        copy = self.lab.manifest('EFFECT', proposal); copy['after']['status'] = 'DONE'
        self.lab.review('EFFECT', proposal, expected_version=0, decision='ACCEPT')
        self.lab.review('EFFECT', proposal, expected_version=1, decision='REJECT')
        self.lab.review('EFFECT', proposal, expected_version=2, decision='ACCEPT')
        with self.assertRaises(ContractError):
            self.lab.apply_effect(command(), proposal, review_version=1)
        self.lab.review('SOURCE', cap, expected_version=1, decision='REJECT')
        self.assertEqual('CONFLICT_SOURCE_REVIEW', self.lab.apply_effect(command(), proposal, review_version=3)['result'])
        self.assertEqual(0, self.lab.summary()['effects'])

    def test_GI31_all_global_gaps_have_explicit_model_and_pending_statuses(self):
        result = self.lab.summary()
        self.assertEqual([f'G{i:02}' for i in range(1, 8)], result['global_gaps_open'])
        self.assertEqual(42, len(result['criteria']))
        self.assertEqual(18, sum(v == 'SYNTHETIC_MODEL_ONLY' for v in result['criteria'].values()))
        self.assertEqual(17, sum(v == 'NOT_IMPLEMENTED_THIS_CUT' for v in result['criteria'].values()))
        self.assertEqual(7, sum(v == 'REAL_VALIDATION_PENDING' for v in result['criteria'].values()))
        self.assertEqual(18, len(FIRST_CRITERIA))

    def test_GI32_publication_contract_approval_and_global_acceptance_are_not_review_stages(self):
        cap = self.capture()
        for stage in ['PUBLICATION', 'CONTRACT', 'GLOBAL', 'ACTIVATION']:
            with self.assertRaisesRegex(ContractError, 'INVALID_REVIEW'):
                self.lab.review(stage, cap, expected_version=0, decision='ACCEPT')
        self.assertFalse(self.lab.summary()['D5_closed'])

    def test_GI35_real_pending_work_is_not_displaced_into_D6(self):
        result = self.lab.summary()
        self.assertEqual(['GI06', 'GI12', 'GI18', 'GI24', 'GI30', 'GI36', 'GI42'], result['real_validation_pending'])
        self.assertFalse(result['D5_closed'])
        self.assertEqual('VOLATILE_MEMORY', result['storage'])
        self.assertNotIn('D6_complete', result)

    def test_GI37_end_to_end_and_replay_never_restore_a_remote_edit(self):
        drive = MemoryDrive(); drive.seed('register', self.register)
        cap = self.lab.capture_drive(drive, 'register', PROJECT, DOCUMENT, profile=PROFILE)
        self.applied_from_capture(cap)
        self.lab.plane.seed(REMOTE, dict(name='remote old', description='old', labels=['retain']))
        self.lab.bind_plane(self.binding())
        projection = self.lab.prepare_projection(BINDING)
        self.lab.review('PROJECTION', projection, expected_version=0, decision='ACCEPT')
        cid = command(); receipt = self.lab.apply_projection(cid, projection, review_version=1)
        self.assertEqual('SIMULATED_PROJECTED', receipt['result'])
        self.assertEqual('Review only', self.lab.plane.read(REMOTE)['description'])
        self.lab.plane.edit_fixture(REMOTE, dict(name='later local Plane edit'))
        self.assertEqual(receipt, self.lab.apply_projection(cid, projection, review_version=1))
        self.assertEqual('later local Plane edit', self.lab.plane.read(REMOTE)['name'])
        self.assertEqual(cap, self.lab.manifest('EFFECT', self.proposal_id)['capture_id'])
        self.assertEqual(TARGET, self.lab.manifest('PROJECTION', projection)['binding']['internal_id'])
        with self.assertRaisesRegex(ContractError, 'CONFLICT_COMMAND'):
            self.lab.apply_effect(cid, self.proposal_id, review_version=1)

    def applied_from_capture(self, cap):
        _, proposal = self.effect(capture=cap)
        self.proposal_id = proposal
        self.lab.review('EFFECT', proposal, expected_version=0, decision='ACCEPT')
        self.assertEqual('SIMULATED_APPLIED', self.lab.apply_effect(command(), proposal, review_version=1)['result'])

    def test_GI37_supported_workflow_makes_no_files_processes_or_network_calls(self):
        with ExitStack() as stack:
            for name in ['builtins.open', 'os.open', 'os.system', 'subprocess.run', 'subprocess.Popen',
                         'socket.socket', 'socket.create_connection']:
                stack.enter_context(patch(name, side_effect=AssertionError('FORBIDDEN_IO')))
            proposal = self.projection()
            self.lab.review('PROJECTION', proposal, expected_version=0, decision='ACCEPT')
            self.assertEqual('SIMULATED_PROJECTED', self.lab.apply_projection(command(), proposal, review_version=1)['result'])
            self.assertEqual(0, self.lab.summary()['remote_requests'])
            self.assertEqual(0, self.lab.summary()['persistent_D2_writes'])

    def test_GI01_internal_capture_tampering_is_detected_before_review(self):
        cap = self.capture()
        value = json.loads(self.lab._captures[cap])
        value['preview']['proposals'][0]['fields']['item'] = 'Forged title'
        self.lab._captures[cap] = canonical(value)
        with self.assertRaisesRegex(ContractError, 'CAPTURE_TAMPERED'):
            self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT')

    def test_GI26_fixture_duplicates_and_invalid_ids_are_blocked(self):
        item = dict(kind='REQUIREMENT', source_key='REQ-1', title='Explicit', description='Source')
        payload = canonical(envelope(dict(schema='d5.offline-typed-fixture.v1', elements=[item, item])))
        cap = self.capture(payload, 'markdown-structure.v1', source_kind='TYPED_FIXTURE')
        self.lab.review('SOURCE', cap, expected_version=0, decision='ACCEPT')
        with self.assertRaisesRegex(ContractError, 'DUPLICATE_SOURCE_KEY'):
            self.lab.prepare_effect(cap, 'REQ-1', TARGET, 'R-1', source_review_version=1)
        with self.assertRaisesRegex(ContractError, 'INVALID_ID'):
            self.lab.prepare_effect(cap, 'REQ-1', 'not-uuid', 'R-1', source_review_version=1)
        self.assertEqual(0, self.lab.summary()['effects'])

    def test_GI14_unknown_capability_cannot_be_truthy_authorization(self):
        proposal = self.projection()
        self.lab.review('PROJECTION', proposal, expected_version=0, decision='ACCEPT')
        self.lab.plane.cas_supported = 'UNKNOWN'
        self.assertEqual('BLOCKED_ATOMIC_CAPABILITY', self.lab.apply_projection(command(), proposal, review_version=1)['result'])

    def test_GI27_local_advance_invalidates_old_projection(self):
        proposal = self.projection()
        self.lab.review('PROJECTION', proposal, expected_version=0, decision='ACCEPT')
        cap = self.capture(self.register.replace(b'Review only', b'New approved description'))
        self.applied_from_capture(cap)
        self.assertEqual('CONFLICT_LOCAL_EDIT', self.lab.apply_projection(command(), proposal, review_version=1)['result'])
        self.assertEqual('Old name', self.lab.plane.read(REMOTE)['name'])

    def test_GI41_reports_distinguish_model_coverage_from_real_or_executed_tests(self):
        self.applied()
        result = self.lab.summary()
        self.assertEqual('SYNTHETIC_ONLY', result['mode'])
        self.assertNotIn('tests_passed', result)
        self.assertEqual('SYNTHETIC_MODEL_ONLY', result['criteria']['GI37'])
        self.assertEqual('REAL_VALIDATION_PENDING', result['criteria']['GI42'])
        self.assertEqual(1, result['effects'])
        self.assertFalse(result['D5_closed'])


if __name__ == '__main__':
    unittest.main()
