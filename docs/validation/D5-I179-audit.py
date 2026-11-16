#!/usr/bin/env python3
"""I179 S01 documentary roles/scope/gate draft. No target execution or imports."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='f1eb517283b3025ef555144e088c9803fd52e976'
OUT=P+'D5-I179-S01-ROLES-SCOPE-GATES.json'
REVIEW=P+'D5-I179-S01-preparation-review.json'
AUDIT=P+'D5-I179-audit.py'
SEAL=P+'D5-I179-integrity.json'
DESIGN='docs/design/D5-I179-S01-ROLES-SCOPE-GATES.md'
PLAN=P+'D5-I177-FOUR-BINDINGS-EVIDENCE-PLAN.json'
PLAN_REVIEW=P+'D5-I178-I177-documentary-review.json'
OLD_SEAL=P+'D5-I178-integrity.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CAP=P+'D5-I122-CAPACITY-CONTRACT.json'
CERT=P+'D5-I122-CAPACITY-CERTIFICATE.json'
REG=P+'D5-I122-CAPTURE-REGISTRY.json'
MAN=P+'D5-I122-COMPONENTS-MANIFEST.json'
C_REG=P+'D5-I175-candidate-bindings/registry.json'
C_CERT=P+'D5-I175-candidate-bindings/certificate.json'
C_MAN=P+'D5-I175-candidate-bindings/components-manifest.json'
DRAFT=P+'D5-I175-candidate-bindings/authority-binding-draft.json'
GRAPH=P+'D5-I175-PRP173-CANDIDATE-GRAPH.json'
INDEX=P+'D5-PFC126-03-RESOURCE-ADMISSION-INDEX-CANDIDATE.json'
CP07=P+'D5-I119-CP07-binding-review.json'
GATE122=P+'D5-I122-gate-disposition.json'
ATOMIC=P+'D5-I122-atomicity-implementation.json'
COUNTS=P+'D5-I124-global-batch-lifetime-proof.json'
CP03=P+'D5-I120-unit-operand-source-proof.json'
RUNTIME=P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM=P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
JOINT='testing/prospective_capture_joint_i122/capture.py'
LAB='testing/prospective_capture_joint_i122/run_joint_lab.py'
TESTS='testing/prospective_capture_joint_i122/test_joint_capture.py'
RAW=P+'D5-JOINT-tests-raw.json'
RESULT=P+'D5-JOINT-results.json'
COMPSEAL=P+'D5-JOINT-integrity.json'
AUTH=P+'D5-JOINT-capture-authorization.json'
FILES={OUT,REVIEW,AUDIT,SEAL,DESIGN}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pin(p):return dict(path=p,sha256=sha(p))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def inputs():
    extras=[PLAN_REVIEW,P+'D5-I178-I177-source-reconstruction.json',P+'D5-I178-audit.py',OLD_SEAL]
    return {**rd(P+'D5-I178-I177-source-reconstruction.json')['input_pins'],**{p:sha(p) for p in extras}}


def check_git_inputs():
    pins=inputs();req=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p


def evidence():
    trees={p:ast.parse((ROOT/p).read_text()) for p in [JOINT,LAB,TESTS]}
    def node(p,name):
        n=trees[p]
        for part in name.split('.'):
            matches=[x for x in ast.iter_child_nodes(n) if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name==part]
            if p==JOINT and part=='authority':
                assert matches;n=matches[-1]  # Final module binding supersedes inherited definitions.
            else:
                assert len(matches)==1;n=matches[0]
        return n
    specs=[(JOINT,'require_admission'),(JOINT,'checked_component_metadata'),(JOINT,'InputPlan.before'),(JOINT,'checked_registry'),(JOINT,'authority'),(LAB,'main'),(TESTS,'R2CandidateTests')]
    anchors=[]
    for p,name in specs:
        n=node(p,name);anchors.append(dict(path=p,symbol=name,sha256=sha(p),line=n.lineno,end_line=n.end_lineno,
            AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
    required=node(JOINT,'require_admission')
    comparisons={ast.unparse(n) for n in ast.walk(required) if isinstance(n,ast.Compare)}
    preds=["cert.get('status') == 'SOURCE_CAPACITY_VERIFIED'", "cert.get('CP03_global_resolved') is True", "cert.get('CP07_exact_admission_resolved') is True", "cert.get('correlated_atomicity_verified') is True"]
    assert set(preds)<=comparisons
    direct_component_field_checks=[n for n in ast.walk(required) if isinstance(n,ast.Constant) and n.value=='component_validation']
    assert not direct_component_field_checks
    ids=['R2CandidateTests.'+n.name for n in node(TESTS,'R2CandidateTests').body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    assert ids==rd(C_MAN)['tests'] and len(ids)==10
    return dict(anchors=anchors,direct_certificate_predicates=preds,
        certificate_component_validation_directly_checked_here=False,accepted_component_metadata_checked_separately=True,
        component_ids=ids,static_source_only=True,product_or_component_imported_or_executed=False,
        authority_anchor_is_last_module_definition_not_superseded_inherited_body=True)


def roles():
    specs=[
        ('R01','Runtime image/build provenance custodian','Exact target interpreter/stdlib/frozen/builtin/native/allocator/source-binary identity and validity',['RUNTIME_ATTESTATION'],[]),
        ('R02','Platform/service custodian','Actual worker/coordinator/child capacity, CPU/wall/clock/IO/scheduler/load domain and validity',['PLATFORM_ATTESTATION'],[]),
        ('R03','Independent resource-proof reviewer','Complete E01-E05 evidence and assumptions; source/root scope correspondence',['RESOURCE_ACCEPTANCE'],['DOCUMENTARY_PREPARER']),
        ('R04','Named component custodian','Future explicitly authorized qualifying/final isolated runs, effective runtime/source freeze and raw custody',['QUALIFYING_COMPONENT_EXECUTION','FINAL_COMPONENT_EXECUTION'],[]),
        ('R05','Independent component-evidence reviewer','Actual raw/provenance and exact final manifest, component-only review',['COMPONENT_EVIDENCE_ACCEPTANCE'],['R04']),
        ('R06','Independent admission/provenance/Reader reviewer','Gate meanings, index protocol, binding impact, archival identity, exact byte/Reader/output scope',['S01_SCOPE_ADOPTION','PACKAGING_REVIEW'],['DOCUMENTARY_PREPARER']),
        ('R07','Capture-authority issuer','Explicit scoped authority issuance with complete real pins, trust and validity',['AUTHORITY_ISSUANCE'],[]),
        ('R08','Separate acceptance reviewer','Final resource/packaging/admission decision separate from evidence production and primary review',['SEPARATE_ADMISSION_ACCEPTANCE'],['DOCUMENTARY_PREPARER','R03','R04','R06','R07'])]
    return [dict(id=id,role=role,responsibility=scope,assigned_person=None,assignment_status='UNASSIGNED_PENDING_AUTHORIZED_OWNER',
        required_decision_scopes=scopes,separation_required_from=separation,authority_record=None,signature_or_trust_record=None,
        validity_from=None,validity_until=None,competence_and_exact_source_scope_record=None,
        accepted_appointment=False,role_listing_does_not_grant_permissions=True) for id,role,scope,scopes,separation in specs]


def gates():
    c=rd(C_CERT);old=rd(CP07)
    assert old['CP07_candidate_sources_exactly_bound'] and old['CP07_candidate_numeric_schedule_resolved']
    assert not old['CP07_future_exact_binding_resolved'] and not old['CP07_global_admission_resolved']
    specs=[
        ('G00','SOURCE_CAPACITY_VERIFIED','DIRECT_CERTIFICATE_STATUS',c['status'],
            "cert.get('status') == 'SOURCE_CAPACITY_VERIFIED'",
            'Complete accepted exact-scope source/capacity evidence and truthful subordinate gates, not a document/status forecast.',
            ['E01-E05 accepted complete bounds/provenance and assumptions','Truthful CP03/CP07/atomicity gate evidence','Competent issuer, scope, binding-impact and separate acceptance'],
            [CONTRACT,CAP,C_CERT,PLAN],
            'Keep IMPLEMENTED_NOT_ADMITTED. No candidate schema/hash DAG or qualifying test count alone supplies a verified certificate.'),
        ('G01','CP03_global_resolved','DIRECT_CERTIFICATE_BOOLEAN',c['CP03_global_resolved'],
            "cert.get('CP03_global_resolved') is True",
            'Inherited I120 original operand/source proof,179 unit cases within the fixed321-root/12-group route and its preconditions; not complete heap/CPU or runtime service.',
            ['Exact original-source proof binding and unchanged applicability reviewed','No altered source/control/import/retained-object scope silently covered'],
            [CP03,COUNTS,C_CERT],
            'Retain the inherited True without issuing new verification or enlarging scope; drift requires reviewed proof, not budget substitution.'),
        ('G02','CP07_exact_admission_resolved','DIRECT_CERTIFICATE_BOOLEAN',c['CP07_exact_admission_resolved'],
            "cert.get('CP07_exact_admission_resolved') is True",
            'Full exact admission is distinct from documentary source bindings and numerical Reader capacity. Historical records leave real future hashes/accepted evidence pending.',
            ['Clarify certificate claim boundary versus final admission predicate without silently narrowing full CP07','Real final bytes/pins and accepted component/provenance/authority material at the appropriate reviewed stage','Exact runtime input sets, source/schema/contract/manifest consistency and all unchanged quotas'],
            [CP07,GATE122,GRAPH,CAP,C_CERT],
            'Keep False. Candidate491/495, a conditional Reader fit or a future flag prediction does not resolve full CP07. Block early certification pending a competent scope/order decision.'),
        ('G03','correlated_atomicity_verified','DIRECT_CERTIFICATE_BOOLEAN',c['correlated_atomicity_verified'],
            "cert.get('correlated_atomicity_verified') is True",
            'Actual accepted correlated atomicity basis for all30 integrated sites and exact implementation/runtime/test scope; implementation-written is not validation.',
            ['Reviewed source argument covers all30 sites and boundaries','Real qualifying/final component evidence as required by the adopted claim scope','No inference from ten passing fixtures to all interleavings or heap/CPU/E01-E05 capacity'],
            [ATOMIC,CAP,C_CERT,PLAN],
            'Keep False. If only downstream unperformed validation could justify this predecessor claim, require reviewed evidence/protocol separation; no synthetic PASS.'),
        ('G04','component_validation','INFORMATIONAL_CERTIFICATE_FIELD_NOT_THIS_DIRECT_GATE',c['component_validation'],
            'No direct component_validation lookup in require_admission; checked_component_metadata separately enforces actual records.',
            'Truthful reported status with explicit qualifying-versus-final scope. A label cannot replace the real raw/result/seal or automatically transfer a prior run.',
            ['Define what the reported field means before changing it','Keep final E06 separate from earlier source qualification','No forecast PASS or new enum/schema invented here'],
            [C_CERT,C_MAN,PLAN],
            'Keep NOT_RUN. No informational field edit satisfies the separate runtime component checks.'),
        ('G05','accepted_component_metadata','SEPARATE_COMPOUND_RUNTIME_CHECK',False,
            'checked_component_metadata: real canonical raw/result/seal; raw and result PASS, tests10, forbidden imports absent, exact hashes and final9-source manifest.',
            'Actual authorized final-manifest component evidence plus independent provenance/review, not an AST plan, metadata writer or old qualifying run by assertion.',
            ['S04 real raw/stdout/exit and exact manifest/runtime/source provenance','S05 component-only actual review binds raw and final manifest','S06 exact seal artifacts/source map, no self or late-consumer cycle'],
            [C_MAN,PLAN,GRAPH],
            'Three real runtime component bodies are absent. Keep E06 NOT_RUN and hashes unresolved; none is created here.'),
        ('G06','authority_and_exact_capture_scope','SEPARATE_INPUTPLAN_AND_ADMISSION_CHECK',False,
            'InputPlan.before checks closed authority schema/phase/P01/no self-pin; require_admission checks exact capture_inputs and registry/source/component hashes.',
            'Genuine separately authorized issuer and exact final bindings; parser literals/hash checks do not independently authenticate an external signer or resource truth.',
            ['Named authorized issuer, trust and validity accepted outside the parser','All actual final capture pins, authority last, no historical authority reuse','No promotion of the I175 NOT_AUTHORIZED descriptor; actual rebind/capture separately authorized'],
            [GRAPH,DRAFT,PLAN],
            'No runtime authority exists. Keep no admission; descriptor and Git publication grant no authority.')]
    return [dict(id=id,name=name,kind=kind,current_candidate_value=value,machine_check=predicate,proposed_truth_scope=scope,
        necessary_evidence=necessary,source_references=[pin(p) for p in refs],current_disposition=decision,
        interpretation_status='CANDIDATE_FOR_COMPETENT_REVIEW_NOT_ADOPTED',truth_or_scope_accepted_by_I179=False)
        for id,name,kind,value,predicate,scope,necessary,refs,decision in specs]


def build_scope():
    r=rd(C_REG)['overrides'];roots=rd(COUNTS);atomic=rd(ATOMIC);ids=evidence()['component_ids']
    assert roots['root_count']==len(roots['root_rows'])==321 and '12-group' in roots['scope']
    assert len(atomic['rows'])==30 and len({x['site'] for x in atomic['rows']})==30
    return dict(candidate_contract=pin(CONTRACT),proposal='PRP173-INDEX-01',source_revision='I122-CANDIDATE-01',
        original_source_scope=dict(root_count=321,group_count=12,applicability=roots['scope'],proof=pin(COUNTS),operand_proof=pin(CP03),
            not_a_permission_to_run_original_functional_campaigns=True),
        implementation_scope=dict(sources=r['implementation_sources'],source_count=6,atomicity_review=pin(ATOMIC),integrated_sites=30,
            source_written_not_runtime_verified=True),
        future_component_scope=dict(source_entrypoint=pin(LAB),test_source=pin(TESTS),ids=ids,count=10,
            synthetic_atomicity_components_not321_original_tests=True,full_functional_campaigns_allowed=False,
            qualifying_and_final_evidence_scopes_distinct=True,no_execution_authorized=True),
        binding_scope=dict(graph=pin(GRAPH),metadata_aliases=[dict(logical_path=p,candidate=pin(q)) for p,q in [(REG,C_REG),(CERT,C_CERT),(MAN,C_MAN)]],
            descriptor=pin(DRAFT),negative_index=pin(INDEX),physical_union_paths=495,known_bindings=491,pending=4,
            archive_refs_stay_at_backing_commit=True,preview_aliases_not_installed=True),
        target_runtime_platform_scope=dict(interpreter_path=None,interpreter_sha256=None,loaded_native_allocator_kernel_closure=None,
            clock_process_service_domain=None,accepted_P02_P03_scope=None,
            runtime_record=pin(RUNTIME),platform_record=pin(PLATFORM),historical_I127_reference_not_current_target_or_attestation=True,
            local_runtime_or_platform_inspected=False),
        staging_custody_scope=dict(isolated_versioned_root=None,freeze_id=None,owner=None,approved_environment=None,
            pre_post_manifest_effective_source_runtime_provenance_required=True,stdout_stderr_exit_custody_required=True,
            no_current_staging_created=True,no_active_runtime_paths_written=True),
        unchanged_size_scope=dict(PRP173_conditional_upper_bytes=266536487,I175_negative_candidate_conditional_upper_bytes=266402939,
            positive_successor_rechecks_required=True,quota_changes_authorized=False,source_schema_or_protocol_repair_authorized=False))


def build_output():
    task=rd(PLAN)['steps'][0];assert task['id']=='S01'
    decisions=[
        ('D179-01','Do not equate CP07 source/Reader documentary consistency with full admission. Preserve full CP07 pending real exact evidence.'),
        ('D179-02','Separate source-written atomicity, accepted qualifying basis and final-manifest E06; no inference from a byte DAG or test count to truth of a predecessor certificate.'),
        ('D179-03','Block positive certification if the required gate claim depends on its own unperformed downstream evidence. Require competent signed scope/order adjudication or a separately reviewed versioned evidence/protocol split; do not narrow gates or change source here.'),
        ('D179-04','component_validation is reported state, not the direct require_admission boolean gate. Keep NOT_RUN truthful and enforce real raw/result/seal separately; no predictive status.'),
        ('D179-05','Authority schema/phase/hash checks do not supply issuer trust or permissions. Require exact independently accepted scope, custody and separate action authorizations.'),
        ('D179-06','Treat logical candidate aliases and historical archive identities separately; all accepted future versions need new exact hashes and bound/source scope review.')]
    perms=['QUALIFYING_COMPONENT_EXECUTION','FINAL_COMPONENT_EXECUTION','AUTHORITY_ISSUANCE','ACTUAL_REBIND','PRODUCT_OR_CAPTURE_EXECUTION','SOURCE_SCHEMA_PROTOCOL_OR_QUOTA_CHANGE']
    return dict(schema='d5.i179-s01-roles-scope-gates.v1',increment='I179',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        status='S01_CANDIDATE_PREPARED_ROLES_UNASSIGNED_GATE_ADOPTION_PENDING_NO_ADMISSION',
        input_pins=inputs(),plan_binding=dict(**pin(PLAN),step_id='S01',task_canonical_sha256=digest(task)),last_plan_review=pin(PLAN_REVIEW),
        documentary_preparer=dict(identity='Codex assistant in this chat',role='Documentary preparer only',independent=False,custodian_authority=False,
            current_authorized_scope='Prepare/review repository documents and requested Git publication only.'),
        role_authority_validity_matrix=roles(),scope=build_scope(),gate_catalog=gates(),source_evidence=evidence(),
        proposed_semantic_decisions=[dict(id=id,proposal=text,adopted=False,adopting_person=None,authority_record=None,signature=None,validity=None) for id,text in decisions],
        permission_scope_matrix=[dict(scope=p,granted=False,granting_person=None,decision_record=None,exact_scope_and_validity=None) for p in perms],
        semantic_predecessor_finding=dict(id='F179-01',status='OPEN_SCOPE_AND_EVIDENCE_ORDER_REQUIRES_COMPETENT_ADJUDICATION',
            basis='Historical CP07 records distinguish reviewed candidate bindings/capacity from full actual admission; the parser consumes a True flag without defining an authenticated issuance-time claim boundary.',
            current_negative_graph_and_byte_DAG_not_defective_by_this_finding=True,
            positive_certificate_scope_or_issuance_order_not_accepted=True,
            neither_qualifying_test_evidence_nor_numerical_Reader_fit_closes_full_CP07_automatically=True,
            action_now='Keep CP07/correlated atomicity/status negative. Prepare independent role/scope/evidence-order decision; do not produce a positive certificate or authorize execution.'),
        S01_acceptance_checklist=dict(named_independent_admission_provenance_reviewer=False,named_component_custodian=False,
            competent_resource_runtime_platform_and_separate_acceptance_roles_confirmed=False,
            signed_valid_role_scope_authority_records=False,exact_target_runtime_and_source_scope_accepted=False,
            gate_truth_and_semantic_predecessor_boundary_adopted=False,accepted_prior_qualifying_basis_or_separately_scoped_route=False),
        readiness=dict(documentary_preparation_complete=True,named_assignments_complete=False,semantic_rules_prepared=True,
            semantic_rules_adopted=False,S01_accepted=False,S02_execution_ready=False,S03_positive_certification_ready=False,
            resource_obligations_closed=0,pending_binding_hashes=4,actual_binding_hashes_resolved=0),
        handoff_requirements=[
            'Authorized owner supplies actual names, competence/independence, authority records, validity and exact source/target scope for each required role.',
            'Competent R06/R03 plus separate R08 adjudicate F179-01 and adopt or reject candidate gate scopes without weakening CP07 or forecasting downstream PASS.',
            'Only after accepted semantic scope and real prior evidence assessment decide whether S02 qualification is needed; no current permission follows.',
            'Keep S03 blocked until all gate claims and E01-E05 are truthfully supported; any protocol/evidence repair is a separate reviewed task.',
            'Rebind, authority issuance, component execution and capture remain separately authorized future actions; no placeholders replace missing evidence.'],
        unchanged_state=dict(certificate=pin(CERT),candidate_certificate=pin(C_CERT),certificate_status=rd(C_CERT)['status'],
            CP03_inherited_value=rd(C_CERT)['CP03_global_resolved'],CP07_value=False,correlated_atomicity_verified=False,component_validation='NOT_RUN',
            E01_E05_open=True,E06_NOT_RUN=True,product_or_components_executed=False,quotas_changed=False,rebind_applied=False,
            source_implementation_changed=False,active_gate_updated=False,resource_obligations_closed=0,
            independent_acceptance=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        decision=rd(GRAPH)['decision'],E06=rd(GRAPH)['E06'])


def build_review():
    o=rd(OUT)
    return dict(schema='d5.i179-s01-preparation-review.v1',increment='I179',date='2026-11-16',base_commit=BASE,
        status='S01_DOCUMENTARY_CANDIDATE_READY_FOR_REVIEW_NOT_ACCEPTED_NO_EXECUTION_READY',input_pins={**inputs(),OUT:sha(OUT)},output=pin(OUT),
        counts=dict(historical_input_pins=len(inputs()),pending_role_assignments=8,gates=7,semantic_decisions=6,permission_scopes=6,
            source_anchors=7,implementation_sources=6,integrated_sites=30,inherited_roots=321,inherited_groups=12,component_ids=10,pending_bindings=4,new_files=5),
        preparation_checks=dict(real_scope_and_source_bindings=True,role_assignment_absence_disclosed=True,
            direct_code_predicates_distinguished_from_evidence_meaning=True,CP07_candidate_vs_full_admission_distinction_preserved=True,
            certificate_component_status_not_misrepresented_as_direct_parser_gate=True,
            predecessor_evidence_order_gap_explicit=True,no_predicted_PASS_or_permission=True,negative_gates_preserved=True),
        readiness=o['readiness'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I179-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary role/scope/gate candidate only; product/component execution prohibited.',over400_lines=True,
            reason='Role/authority matrix, source-grounded gate catalog and semantic-order decision draft with self-contained audit; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_not_authority_or_semantic_adoption=True))


def main():
    assert rd(OUT)==build_output() and rd(REVIEW)==build_review();check_git_inputs()
    prior=rd(OLD_SEAL);preserved={**prior['preserved_published373'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)};seal=rd(SEAL)
    assert len(preserved)==378 and seal['preserved_published378']==preserved
    assert seal['schema']=='d5.i179-integrity.v1' and seal['base_commit']==BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert len(inputs())==684 and not FILES&set(inputs())
    o=rd(OUT);assert len(o['role_authority_validity_matrix'])==8 and len(o['gate_catalog'])==7
    assert all(r['assigned_person'] is None and not r['accepted_appointment'] for r in o['role_authority_validity_matrix'])
    assert all(not d['adopted'] and d['adopting_person'] is None for d in o['proposed_semantic_decisions'])
    assert all(not p['granted'] for p in o['permission_scope_matrix'])
    assert [g['current_candidate_value'] for g in o['gate_catalog'][:5]]==['IMPLEMENTED_NOT_ADMITTED',True,False,False,'NOT_RUN']
    assert not o['readiness']['S01_accepted'] and not o['readiness']['S02_execution_ready'] and not o['readiness']['S03_positive_certification_ready']
    assert o['semantic_predecessor_finding']['status'].startswith('OPEN_')
    assert rd(C_CERT)['CP07_exact_admission_resolved'] is False and rd(C_CERT)['correlated_atomicity_verified'] is False
    assert len(rd(C_REG)['overrides']['implementation_sources'])==6
    for p,h in o['scope']['implementation_scope']['sources'].items():assert sha(p)==h,p
    for p in [RAW,RESULT,COMPSEAL,AUTH,P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists()
    assert sha(CONTRACT)=='e7a873a2aea8648d225f2272854e0b15c3f21de5826df06f16dfb6e45aa54576'
    for k in ['resource_closure_verified','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    changes=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changes==FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I179',step='S01',documentary_preparation_complete=True,
        pending_role_assignments=8,gate_catalog_entries=7,semantic_decisions_adopted=0,S01_accepted=False,
        S02_execution_ready=False,S03_positive_certification_ready=False,pending_bindings=4,prior_published_files_preserved=378,
        new_files=5,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,
        independent_acceptance=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':main()
