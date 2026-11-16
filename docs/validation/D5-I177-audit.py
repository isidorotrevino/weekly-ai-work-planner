#!/usr/bin/env python3
"""I177 documentary plan audit. No target imports/execution or component discovery."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='49a160ffe78e31ac6eff277db62157bfe44561b3'
OUT=P+'D5-I177-FOUR-BINDINGS-EVIDENCE-PLAN.json'
REVIEW=P+'D5-I177-readiness-review.json'
AUDIT=P+'D5-I177-audit.py'
SEAL=P+'D5-I177-integrity.json'
DESIGN='docs/design/D5-I177-FOUR-BINDINGS-EVIDENCE-PLAN.md'
GRAPH=P+'D5-I175-PRP173-CANDIDATE-GRAPH.json'
LAST_REVIEW=P+'D5-I176-I175-documentary-review.json'
OLD_SEAL=P+'D5-I176-integrity.json'
PROP=P+'D5-I173-READER-PACKAGING-PROPOSAL.json'
INDEX=P+'D5-PFC126-03-RESOURCE-ADMISSION-INDEX-CANDIDATE.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CERT=P+'D5-I122-CAPACITY-CERTIFICATE.json'
REG=P+'D5-I122-CAPTURE-REGISTRY.json'
MAN=P+'D5-I122-COMPONENTS-MANIFEST.json'
C_REG=P+'D5-I175-candidate-bindings/registry.json'
C_CERT=P+'D5-I175-candidate-bindings/certificate.json'
C_MAN=P+'D5-I175-candidate-bindings/components-manifest.json'
DRAFT=P+'D5-I175-candidate-bindings/authority-binding-draft.json'
RAW=P+'D5-JOINT-tests-raw.json'
RESULT=P+'D5-JOINT-results.json'
COMPSEAL=P+'D5-JOINT-integrity.json'
AUTH=P+'D5-JOINT-capture-authorization.json'
JOINT='testing/prospective_capture_joint_i122/capture.py'
LAB='testing/prospective_capture_joint_i122/run_joint_lab.py'
TESTS='testing/prospective_capture_joint_i122/test_joint_capture.py'
COMMAND=['python3','-B','-m','testing.prospective_capture_joint_i122.run_joint_lab','--components-only']
FILES={OUT,REVIEW,AUDIT,SEAL,DESIGN}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def enc(x):return json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
def pin(p):return dict(path=p,sha256=sha(p))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def inputs():
    extras=[LAST_REVIEW,P+'D5-I176-I175-source-reconstruction.json',P+'D5-I176-audit.py',OLD_SEAL]
    return {**rd(P+'D5-I176-I175-source-reconstruction.json')['input_pins'],**{p:sha(p) for p in extras}}


def check_git_inputs():
    pins=inputs();req=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p


def source_evidence():
    trees={p:ast.parse((ROOT/p).read_text()) for p in [JOINT,LAB,TESTS]}
    def symbol(p,name):
        n=trees[p]
        for part in name.split('.'):
            matches=[x for x in ast.iter_child_nodes(n) if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name==part]
            assert len(matches)==1;n=matches[0]
        return n
    specs=[(JOINT,'checked_registry'),(JOINT,'require_admission'),(JOINT,'checked_component_metadata'),(JOINT,'canonical_metadata'),(LAB,'main'),(TESTS,'R2CandidateTests')]
    anchors=[]
    for p,name in specs:
        n=symbol(p,name);anchors.append(dict(path=p,symbol=name,sha256=sha(p),line=n.lineno,end_line=n.end_lineno,
            AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
    declared={n.targets[0].id:sorted(ast.literal_eval(n.value)) for n in symbol(JOINT,'checked_component_metadata').body
        if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['raw_keys','result_keys']}
    ids=['R2CandidateTests.'+n.name for n in symbol(TESTS,'R2CandidateTests').body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    assert len(ids)==10 and ids==rd(C_MAN)['tests']
    runner=symbol(LAB,'main');calls=[n for n in ast.walk(runner) if isinstance(n,ast.Call)]
    assert any(ast.unparse(n.func)=='print' for n in calls)
    assert not any(ast.unparse(n.func) in ['open','write_all','Path','canonical_metadata','read_registry'] or ast.unparse(n.func).endswith(('.write_text','.write_bytes')) for n in calls)
    assert any(isinstance(n,ast.Compare) and ast.unparse(n)=="args != ['--components-only']" for n in ast.walk(runner))
    return dict(anchors=anchors,raw_required_keys=declared['raw_keys'],result_required_keys=declared['result_keys'],
        seal_required_keys=['schema','source_revision','artifacts','source_bindings'],authority_required_keys=['schema','phase','scopes','registry_sha256','capture_inputs'],
        expected_component_ids=ids,source_revision='I122-CANDIDATE-01',runner_prints_raw_stdout_only=True,
        runner_does_not_write_raw_result_seal_or_read_bind_manifest=True,
        runtime_component_execution_or_discovery_performed=False,AST_only_not_imported=True,
        inspection_scope='Direct runner body and test-ID declarations, not execution or complete imported-module behavior proof.')


def step(id,depends,role,mode,scope,outputs,acceptance,reject):
    return dict(id=id,depends_on=depends,responsible_role=role,assigned_person=None,status='PLANNED_NOT_STARTED',
        mode=mode,scope=scope,planned_outputs=outputs,acceptance_requirements=acceptance,rejection_or_stop=reject,
        current_execution_authorized=False,current_artifacts_produced=False)


def tasks():
    return [
        step('S01',[],'Independent admission/provenance reviewer and named component custodian','DOCUMENTARY_SCOPE_AND_ROLE_REVIEW',
            'Name accountable people, exact source/runtime/test scope and staging custody. Decide certificate gate semantics before final certification; no future PASS assumed.',
            ['Named role/validity/authorization matrix','Exact candidate/gate-scope and semantic-order decision'],
            ['Identify what makes each certificate gate true, including CP07/correlated atomicity, and whether it needs prior component evidence.',
             'A source certificate must never depend semantically on the unperformed final run merely because its byte-hash DAG is acyclic.',
             'If source-gate evidence cannot precede final manifest, require a separately reviewed evidence/protocol split; no source/schema change authorized here.'],
            'Missing reviewer/custodian/semantic basis leaves downstream certification blocked; no flag forecast or automatic transfer.'),
        step('S02',['S01'],'Authorized component custodian plus independent atomicity reviewer','CONDITIONAL_FUTURE_QUALIFICATION_NOT_AUTHORIZED_NOW',
            'Only if no already accepted exact-scope atomicity basis exists: obtain qualifying component evidence on the frozen negative candidate in isolated versioned staging, under a distinct explicit component-only authorization.',
            ['Real qualifying-run evidence and source/runtime/provenance record, separate from final four runtime paths','Independent source-gate qualification decision'],
            ['Either cite genuinely accepted prior exact-scope evidence with a justified validity/transfer decision, or obtain explicit authority for a qualifying run; no run is authorized by this plan.',
             'Freeze effective transitive implementation/runtime and all10 test IDs, inputs/candidate manifest before/after, stdout/stderr/exit and custody.',
             'Qualifying evidence is not final-manifest E06. It cannot close E01-E05, imply capture authority or be copied as final evidence automatically.'],
            'Any failure/import/scope drift or unsupported transfer stays negative. If certificate scope cannot truthfully be justified, stop; do not prepare a positive certificate.'),
        step('S03',['S01','S02'],'Competent resource custodians and separate packaging/source-capacity acceptance reviewer','FUTURE_DOCUMENTARY_FREEZE_AFTER_REAL_ACCEPTANCE',
            'Resolve E01-E05 and source-gate basis, approve the out-of-band index protocol, then freeze a separately versioned accepted successor index and exact registry/certificate/manifest metadata.',
            ['Real accepted scoped resource/provenance decisions','Frozen positive successor metadata and acyclic binding ledger'],
            ['Current negative P01-P10/I175 bytes remain historical; accepted proofs use separately versioned scope.',
             'If S02 uses accepted prior evidence, record that decision; if a new qualifying run was needed, its real evidence precedes any verified source-gate claim.',
             'Bind all9 manifest sources and10 test IDs; null late-consumer fields remain intentional to avoid manifest/result/seal cycles.',
             'Independent review confirms gate truth, sizes, root/signature scope, transitive runtime and all PRP173 envelopes before freezing final-manifest execution context.'],
            'No competent resource acceptance or exact scoped source-gate basis means no positive freeze, even if the metadata fits Reader.'),
        step('S04',['S03'],'Explicitly authorized component custodian','FUTURE_COMPONENT_EXECUTION_REQUIRES_SEPARATE_PERMISSION',
            'Generate B01 by a real final component-only run against the frozen final implementation/runtime/manifest in isolated versioned staging. The runner does not itself bind the manifest.',
            ['B01 immutable real stdout raw bytes','External invocation/source/runtime/manifest pre-post provenance, stderr and exit record'],
            ['A separate explicit authorization must cover this final validation run; qualifying-run permission is not reused automatically.',
             'Record exact command, cwd/frozen root, revision, effective transitive source/runtime hashes, final9-source manifest SHA and10 test IDs before and after.',
             'Preserve real raw stdout bytes; validate closed schema, exact PASS/10/0failure/0error, forbidden_imports empty, product flag false and functional_campaigns0.',
             'Require genuine integer elapsed0..300000 and new_module_count0..9223372036854775807, exit0; do not synthesize measurements or substitute AST PASS.'],
            'FAIL, extra/missing tests, unexpected imports, malformed output, timeout or drift preserves failure evidence and leaves B01 unresolved for admission. No silent retry/repair.'),
        step('S05',['S04'],'Independent component-evidence reviewer, distinct from producer','FUTURE_DOCUMENTARY_REVIEW_OF_REAL_EVIDENCE',
            'Resolve B02 only after reviewing actual B01 bytes plus final-manifest/source/runtime provenance. Hash the final immutable raw and manifest.',
            ['B02 component-only review bytes','Attributed signed/custodied review decision outside closed runtime schema'],
            ['All B01 and provenance requirements hold with the exact final frozen manifest; no stale qualifying-run transfer without scoped review.',
             'Closed result schema, decision ACCEPTED_COMPONENTS_ONLY only on actual accepted evidence; raw_sha256 and manifest_sha256 are real exact-byte digests.',
             'tests_run10, functional_campaigns0, product_or_runner_imported false, closure/D5 false.'],
            'Review rejection must not produce a runtime acceptance/PASS record or change B01. Keep the binding unresolved and report the actual finding.'),
        step('S06',['S05'],'Evidence packager plus independent hash/manifest reviewer','FUTURE_DOCUMENTARY_SEAL_OF_ACCEPTED_REAL_BYTES',
            'Resolve B03 by hashing real B01/B02/final manifest; copy exactly the9 final manifest source bindings. Seal after all three bodies are immutable.',
            ['B03 component-integrity bytes','Byte/hash/schema/canonicalization verification receipt'],
            ['artifacts keys are exactly raw/result/manifest and values their SHA256; source_bindings equals final manifest map exactly.',
             'No seal self-pin, no result/seal back-reference in manifest, no resource closure or capture approval inferred from component acceptance.'],
            'Any mismatch, source drift, wrong keys or oversized body keeps B03 unresolved; never hash substitute or placeholder bodies.'),
        step('S07',['S03','S06'],'Explicit capture-admission authority with separate acceptance reviewer','FUTURE_AUTHORITY_ISSUANCE_REQUIRES_SEPARATE_PERMISSION',
            'Resolve B04 last, in separately authorized staging, only after complete accepted resources/gates and actual component chain. Descriptor I175 is not authority.',
            ['B04 genuine full authority bytes in authorized staging','Authority identity, signature/trust/validity and exact-scope issuance decision'],
            ['Separate explicit authority-issuance decision; this plan, Git publication or component-only authorization does not grant it.',
             'Full494 capture-input pins are real, exact-set matching final registry/sources/metadata, with final registry_sha256; AUTH is not self-pinned.',
             'Closed authority schema, JOINT_EXPLICITLY_APPROVED/P01 only when actually authorized; no copying or promoting the NOT_AUTHORIZED descriptor.',
             'No old I71/I77/I86/I89/I92 authority reuse and no old INVALID_CAPTURE reuse.'],
            'Any missing actual body/gate/trust/validity/approval, symbolic pin or alias mismatch blocks issuance. Do not create runtime authority at its active path.'),
        step('S08',['S07'],'Independent packaging/Reader reviewer and separate final admission reviewer','FUTURE_FINAL_DOCUMENTARY_VALIDATION_NO_CAPTURE',
            'Verify all495 final logical nodes and exact staging byte sources; recompute bindings, topological/protocol order, Reader/top-metadata/context/package limits. Actual rebind/capture is a separate decision.',
            ['Final495-node ledger with zero unresolved body hashes','Final byte/envelope/binding/acceptance report, no execution grant'],
            ['All actual serialized bodies fit unchanged Reader quotas and PRP173 envelopes; no blanket transfer of negative-candidate exact266402939 bound.',
             'Recheck all nine variable members and inherited fresh-read/directory assumptions; validate full output metadata/context/launch/package, not just partial483562 model.',
             'E01-E05 accepted independently, E06 actual final evidence accepted, source gates truthful, distinct roles/validity and exact authority scope documented.',
             'No current candidate path aliases or archival old hashes treated as installed/fresh final bytes; no self-pin or semantic qualification cycle.'],
            'Any missing proof/hash/role or changed bound keeps no admission. No quota increase, silent rebind, product run or capture launch follows from plan completion.')]


def build_plan():
    evidence=source_evidence();envelopes={x['path']:x['max_serialized_bytes'] for x in rd(PROP)['byte_envelopes']['variable_members']}
    bindings=[
        dict(id='B01',path=RAW,schema='d5.joint-component-raw.v2',producer_step='S04',depends_on=['S03'],
            max_bytes=envelopes[RAW],closed_required_keys=evidence['raw_required_keys'],hash_rule='SHA256 of genuine immutable canonical stdout JSON bytes, with optional single newline; do not rewrite failure as PASS.'),
        dict(id='B02',path=RESULT,schema='d5.joint-component-review.v2',producer_step='S05',depends_on=['B01'],
            max_bytes=envelopes[RESULT],closed_required_keys=evidence['result_required_keys'],hash_rule='raw_sha256=SHA256(real B01 bytes); manifest_sha256=SHA256(final frozen manifest); then SHA256(real review bytes).'),
        dict(id='B03',path=COMPSEAL,schema='d5.joint-component-integrity.v2',producer_step='S06',depends_on=['B01','B02'],
            max_bytes=envelopes[COMPSEAL],closed_required_keys=evidence['seal_required_keys'],hash_rule='artifacts exactly {raw:actualSHA,result:actualSHA,manifest:actualSHA}; source_bindings identical to final9-source manifest; no self-pin.'),
        dict(id='B04',path=AUTH,schema='d5.joint-capture-authority.v2',producer_step='S07',depends_on=['B01','B02','B03','S03'],
            max_bytes=envelopes[AUTH],closed_required_keys=evidence['authority_required_keys'],hash_rule='registry_sha256 and all494 capture_inputs use actual final SHA; AUTH excluded from its map; hash actual authority only after real issuance.')]
    for b in bindings:b.update(status='UNRESOLVED_NO_ARTIFACT_PRODUCED',sha256=None,current_path_created=False,assigned_person=None)
    return dict(schema='d5.i177-four-bindings-evidence-plan.v1',increment='I177',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal='PRP173-INDEX-01',status='CONCRETE_RESOLUTION_PLAN_PREPARED_NOT_EXECUTION_OR_ADMISSION_PERMISSION',
        input_pins=inputs(),current_graph=pin(GRAPH),current_review=pin(LAST_REVIEW),current_candidates=[pin(p) for p in [C_REG,C_CERT,C_MAN,DRAFT,INDEX]],
        four_binding_plan=bindings,steps=tasks(),source_evidence=evidence,
        future_command_reference=dict(argv=COMMAND,cwd='Future independently frozen and authorized isolated snapshot root; not this active admission tree.',
            executed=False,execution_authorized_now=False,approved_interpreter_path=None,approved_interpreter_sha256=None,
            generic_python3_is_reference_only_exact_accepted_executable_required=True,stdout='Immutable staging raw bytes, not current runtime path',stderr='Separate immutable diagnostic record',
            runner_source=pin(LAB),test_source=pin(TESTS),command_text_is_not_authorization=True),
        semantic_order=dict(byte_DAG_alone_does_not_justify_verified_certificate=True,
            current_certificate_status=rd(C_CERT)['status'],current_component_status=rd(C_CERT)['component_validation'],
            qualifying_evidence_scope='Independent exact-scope source-gate basis, not final-manifest E06 by assertion.',
            qualifying_then_final_validation_route='If no accepted basis exists, separately authorize a qualifying run before positive metadata, then separately authorize final validation on the actual final freeze.',
            qualifying_and_final_runs_not_authorized_or_performed=True,no_predicted_PASS_or_synthetic_verification=True,
            CP07_and_atomicity_gate_meaning_must_be_explicit=True,
            stop_if_downstream_evidence_required_to_justify_its_own_predecessor='Require separate reviewed protocol/evidence split; no current source/schema/certificate repair authorized.',
            automatic_prior_run_or_negative_candidate_transfer=False),
        staging_and_custody=dict(no_current_outputs_or_authority_written=True,
            target_paths_are_future_logical_names_not_current_write_instructions=True,
            future_stage_must_be_isolated_versioned_owned_and_explicitly_authorized=True,
            no_overwrite_of_historical_inputs_or_negative_candidates=True,
            provenance_must_cover_effective_transitive_runtime_and_sources_not_just_six_names=True,
            runner_does_not_bind_manifest_so_out_of_band_provenance_required=True,
            manifest_late_consumers_remain_null_to_avoid_cycles=True,
            witnesses_real_before_after_and_no_fabricated_elapsed_or_module_data=True),
        role_and_approval_policy=dict(planner='Codex assistant in same chat; no independent/custodian authority claimed',
            all_person_assignments_pending=True,all_authorizations_pending=True,
            standalone_qualifying_components_final_components_authority_issuance_and_actual_rebind_are_separate_scopes=True,
            resources_E01_E05_not_closed_by_component_PASS=True,E06_not_closed_by_AST_or_documentary_plan=True,
            no_automatic_retry_repair_or_quota_transfer=True),
        target_closure_criteria=dict(final_paths=495,real_bindings_required=495,pending_body_hashes_required=0,
            real_component_and_authority_evidence_required=True,independent_acceptance_required=True,
            actual_rebind_or_capture_permission_supplied=False),
        current_limits_and_unknowns=dict(raw_upper=512,result_upper=768,seal_upper=2048,authority_upper=65536,
            unchanged_reader_read_limit=268435456,PRP173_general_conditional_read_upper=266536487,
            negative_I175_exact_conditional_upper=266402939,positive_final_graph_must_be_recomputed=True,
            all_four_actual_hashes_and_final_bytes_unknown=True,final_context_launch_package_and_trust_review_pending=True),
        current_state=dict(known_bindings=491,unresolved_bindings=4,E01_E05_open=True,E06_NOT_RUN=True,
            plan_is_not_raw_result_seal_or_authority=True,product_or_components_executed=False,quotas_changed=False,
            rebind_applied=False,source_implementation_changed=False,active_gate_updated=False,resource_obligations_closed=0,
            independent_acceptance=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        decision=rd(GRAPH)['decision'],E06=rd(GRAPH)['E06'])


def build_review():
    o=rd(OUT)
    return dict(schema='d5.i177-plan-readiness-review.v1',increment='I177',date='2026-11-16',base_commit=BASE,
        status='PLAN_READY_FOR_REVIEW_ALL_FOUR_BINDINGS_AND_FUTURE_AUTHORIZATIONS_STILL_PENDING',input_pins={**inputs(),OUT:sha(OUT)},output=pin(OUT),
        counts=dict(historical_input_pins=len(inputs()),pending_bindings=4,steps=8,source_anchors=6,component_ids=10,new_files=5),
        readiness=dict(plan_concrete=True,execution_ready=False,component_execution_authorized=False,authority_issuance_authorized=False,
            independent_resource_or_packaging_acceptance=False,all_actual_binding_hashes_still_null=True),
        preparation_checks=dict(each_pending_path_has_schema_role_order_acceptance_rejection_and_byte_limit=True,
            runner_stdout_only_and_manifest_provenance_gap_explicit=True,certificate_semantic_order_not_confused_with_hash_DAG=True,
            qualification_and_final_validation_not_automatically_transferred=True,
            no_fake_hashes_PASS_time_or_authority=True,canonical_closed_schemas_and_four_limits_bound=True,
            capture_rebind_and_E06_separate=True),
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I177-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary evidence/authorization plan; target/component execution prohibited.',over400_lines=True,
            reason='Eight concrete steps, four schema-bound artifact plans and self-contained documentary audit; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_not_authorization=True))


def main():
    assert rd(OUT)==build_plan() and rd(REVIEW)==build_review();check_git_inputs()
    prior=rd(OLD_SEAL);preserved={**prior['preserved_published363'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)};seal=rd(SEAL)
    assert len(preserved)==368 and seal['preserved_published368']==preserved
    assert seal['schema']=='d5.i177-integrity.v1' and seal['base_commit']==BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert len(inputs())==675 and not FILES&set(inputs())
    o=rd(OUT);bindings=o['four_binding_plan'];steps=o['steps']
    assert len(bindings)==4 and {b['path'] for b in bindings}=={r['path'] for r in rd(GRAPH)['unresolved']}
    assert all(b['sha256'] is None and not b['current_path_created'] and b['assigned_person'] is None for b in bindings)
    assert [b['max_bytes'] for b in bindings]==[512,768,2048,65536]
    assert len(steps)==8 and [s['id'] for s in steps]==['S%02d'%i for i in range(1,9)]
    seen=set()
    for s in steps:
        assert set(s['depends_on'])<=seen and s['assigned_person'] is None
        assert not s['current_execution_authorized'] and not s['current_artifacts_produced']
        assert s['acceptance_requirements'] and s['rejection_or_stop'];seen.add(s['id'])
    assert all(b['producer_step'] in seen for b in bindings)
    assert not o['future_command_reference']['executed'] and not o['future_command_reference']['execution_authorized_now']
    assert o['source_evidence']['runner_does_not_write_raw_result_seal_or_read_bind_manifest']
    assert o['semantic_order']['byte_DAG_alone_does_not_justify_verified_certificate']
    assert o['semantic_order']['qualifying_and_final_runs_not_authorized_or_performed']
    assert rd(C_CERT)['status']=='IMPLEMENTED_NOT_ADMITTED' and rd(C_CERT)['component_validation']=='NOT_RUN'
    for p in {RAW,RESULT,COMPSEAL,AUTH,P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json'}:assert not (ROOT/p).exists()
    assert sha(CONTRACT)=='e7a873a2aea8648d225f2272854e0b15c3f21de5826df06f16dfb6e45aa54576'
    for k in ['resource_closure_verified','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    changes=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changes==FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I177',proposal='PRP173-INDEX-01',plan_steps=8,
        pending_bindings=4,actual_bindings_resolved=0,future_component_authorization_granted=False,
        prior_published_files_preserved=368,new_files=5,product_or_components_executed=0,quotas_changed=False,
        rebind_applied=False,resource_obligations_closed=0,independent_acceptance=False,proposal_enabled=False,
        D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':main()
