#!/usr/bin/env python3
"""I182 versioned gate-order review: documentary Git/JSON/AST/graphs only; no target execution."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='49644701b654c55c468272f2e721f153f126e37a'
OUT=P+'D5-I181-F179-01-GATE-ORDER-PROPOSAL.json'
REVIEW=P+'D5-I181-preparation-review.json'
AUDIT=P+'D5-I181-audit.py'
SEAL=P+'D5-I181-integrity.json'
DESIGN='docs/design/D5-I181-F179-01-GATE-ORDER-PROPOSAL.md'
S01=P+'D5-I179-S01-ROLES-SCOPE-GATES.json'
S01_REVIEW=P+'D5-I180-S01-documentary-review.json'
OLD_SEAL=P+'D5-I180-integrity.json'
PROP=P+'D5-I173-READER-PACKAGING-PROPOSAL.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
REG=P+'D5-I122-CAPTURE-REGISTRY.json'
CERT=P+'D5-I122-CAPACITY-CERTIFICATE.json'
CAP=P+'D5-I122-CAPACITY-CONTRACT.json'
C_CERT=P+'D5-I175-candidate-bindings/certificate.json'
C_MAN=P+'D5-I175-candidate-bindings/components-manifest.json'
JOINT='testing/prospective_capture_joint_i122/capture.py'
ROOT_PATH=P+'D5-PRP181-FINAL-ADMISSION-ROOT.json'
SOURCE_DIR='testing/prospective_capture_joint_prp181/'
PATHS={
    'REGISTRY':P+'D5-PRP181-CAPTURE-REGISTRY.json',
    'CAPACITY_CONTRACT':P+'D5-PRP181-CAPACITY-CONTRACT.json',
    'SOURCE_BASIS_CERT':P+'D5-PRP181-SOURCE-BASIS-CERTIFICATE.json',
    'COMPONENT_MANIFEST':P+'D5-PRP181-COMPONENTS-MANIFEST.json',
    'RESOURCE_INDEX':P+'D5-PRP181-RESOURCE-INDEX.json',
    'FINAL_RAW':P+'D5-PRP181-tests-raw.json',
    'FINAL_REVIEW':P+'D5-PRP181-results.json',
    'FINAL_SEAL':P+'D5-PRP181-integrity.json',
    'AUTHORITY_PAYLOAD':P+'D5-PRP181-AUTHORITY-PAYLOAD.json',
    'FINAL_ROOT':ROOT_PATH}
MAX_BYTES={'REGISTRY':65536,'CAPACITY_CONTRACT':8192,'SOURCE_BASIS_CERT':65536,'COMPONENT_MANIFEST':4096,
    'RESOURCE_INDEX':32768,'FINAL_RAW':512,'FINAL_REVIEW':768,'FINAL_SEAL':2048,'AUTHORITY_PAYLOAD':65536,'FINAL_ROOT':8192}
FILES={OUT,REVIEW,AUDIT,SEAL,DESIGN}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def size(p):return len((ROOT/p).read_bytes())
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pin(p):return dict(path=p,sha256=sha(p))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def inputs():return {**rd(P+'D5-I180-S01-source-reconstruction.json')['input_pins'],**{p:sha(p) for p in [S01_REVIEW,P+'D5-I180-S01-source-reconstruction.json',P+'D5-I180-audit.py',OLD_SEAL,P.replace('validation/','design/')+'D5-I180-S01-ROLES-SCOPE-GATES-REVIEW.md']}}


def check_git_inputs():
    pins=inputs();req=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p


def topo(edges):
    pending={k:set(v) for k,v in edges.items()};order=[]
    assert all(q in pending for deps in pending.values() for q in deps)
    while pending:
        ready=sorted(k for k,v in pending.items() if not v)
        if not ready:return None
        order.extend(ready)
        for k in ready:del pending[k]
        for v in pending.values():v.difference_update(ready)
    return order


def dependencies():
    return {
        'HISTORICAL_FIXED':[], 'NEW_SOURCE_SCOPE':[],
        'CAPACITY_CONTRACT':['HISTORICAL_FIXED','NEW_SOURCE_SCOPE'],
        'E01_E05_PROOFS':['HISTORICAL_FIXED','NEW_SOURCE_SCOPE','CAPACITY_CONTRACT'],
        'ATOMICITY_ANTECEDENT':['NEW_SOURCE_SCOPE','HISTORICAL_FIXED'],
        'RESOURCE_INDEX':['E01_E05_PROOFS','ATOMICITY_ANTECEDENT','CAPACITY_CONTRACT'],
        'REGISTRY':['HISTORICAL_FIXED','NEW_SOURCE_SCOPE','CAPACITY_CONTRACT','RESOURCE_INDEX'],
        'SOURCE_BASIS_CERT':['REGISTRY','RESOURCE_INDEX','E01_E05_PROOFS','ATOMICITY_ANTECEDENT','NEW_SOURCE_SCOPE'],
        'COMPONENT_MANIFEST':['SOURCE_BASIS_CERT','REGISTRY','CAPACITY_CONTRACT','NEW_SOURCE_SCOPE'],
        'FINAL_RAW':['COMPONENT_MANIFEST','NEW_SOURCE_SCOPE'],
        'FINAL_REVIEW':['FINAL_RAW','COMPONENT_MANIFEST'],
        'FINAL_SEAL':['FINAL_RAW','FINAL_REVIEW','COMPONENT_MANIFEST'],
        'AUTHORITY_PAYLOAD':['FINAL_SEAL','REGISTRY','SOURCE_BASIS_CERT','COMPONENT_MANIFEST','RESOURCE_INDEX','NEW_SOURCE_SCOPE'],
        'FINAL_ROOT':['AUTHORITY_PAYLOAD','SOURCE_BASIS_CERT','FINAL_RAW','FINAL_REVIEW','FINAL_SEAL','E01_E05_PROOFS','ATOMICITY_ANTECEDENT','REGISTRY','COMPONENT_MANIFEST','CAPACITY_CONTRACT','RESOURCE_INDEX','NEW_SOURCE_SCOPE'],
        'RUNTIME_ADMISSION_DECISION':['FINAL_ROOT','AUTHORITY_PAYLOAD','FINAL_RAW','FINAL_REVIEW','FINAL_SEAL','SOURCE_BASIS_CERT','COMPONENT_MANIFEST']}


def source_evidence():
    tree=ast.parse((ROOT/JOINT).read_text());rows=[]
    for name in ['require_admission','checked_component_metadata']:
        n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
        rows.append(dict(path=JOINT,symbol=name,sha256=sha(JOINT),line=n.lineno,end_line=n.end_lineno,
            AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='require_admission')
    checks={ast.unparse(n) for n in ast.walk(fn) if isinstance(n,ast.Compare)}
    assert "cert.get('status') == 'SOURCE_CAPACITY_VERIFIED'" in checks
    assert "cert.get('CP07_exact_admission_resolved') is True" in checks
    return dict(anchors=rows,current_parser_requires_legacy_status_and_CP07_on_predecessor=True,
        new_protocol_not_supported_by_current_parser=True,current_source_not_modified_or_executed=True)


def build_proposal():
    old=rd(REG)['overrides'];historical=set(old['required_prior_inputs']);old_impl=old['implementation_sources']
    historical_bytes=sum(size(p) for p in historical);old_source_bytes=sum(size(p) for p in old_impl)
    assert len(historical)==480 and historical_bytes==86765083 and len(old_impl)==6 and old_source_bytes==217934
    source_cap=262144;variable_cap=sum(MAX_BYTES.values());unique=historical_bytes+source_cap+variable_cap
    fresh_design_cap=4852460;read_budget=3*unique+fresh_design_cap
    edges=dependencies();order=topo(edges);assert order is not None
    full_conditions=[
        'accepted_exact_source_basis_and_CP03_scope', 'accepted_E01_E05_complete_bounds_and_assumptions',
        'accepted_atomicity_antecedent_scope_not_just_source_written',
        'real_final_E06_raw_review_seal_bound_to_exact_final_manifest_runtime_sources',
        'all_actual_authority_payload_and494_manifest_body_hashes_match',
        'trusted_root_issuer_signature_scope_validity_and_distinct_acceptance',
        'root_and_all495_ancestor_bodies_stable_in_same_physical_Reader',
        'unchanged_file_unique_read_path_and_output_limits_hold_for_final_bytes',
        'explicit_separate_runtime_execution_request_and_admission_decision']
    return dict(schema='d5.i181-f179-01-gate-order-proposal.v1',increment='I181',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal_id='PGO181-SPLIT-ROOT-01',status='VERSIONED_SEMANTIC_ORDER_SOLUTION_PROPOSED_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        input_pins=inputs(),finding=rd(S01)['semantic_predecessor_finding'],scope_reference=pin(S01),review_reference=pin(S01_REVIEW),
        route_decision=dict(selected_route='Versioned predecessor-basis/final-full-admission split with a charged non-self-pinned final root.',
            no_silent_reinterpretation_of_legacy_CP07=True,old_CP07_stays_false=True,
            source_or_schema_changes_required_for_adoption=True,changes_implemented=False,
            not_a_drop_in_rebind_for_PRP173_or_current_I122=True,
            current_PFC126_I122_proofs_not_automatically_valid_for_successor=True),
        stage_claims=[
            dict(id='BASIS',proposed_schema='d5.prp181-source-basis.v3',proposed_status='ANTECEDENT_BASIS_ONLY_NOT_ADMISSION',
                asserts='Only already accepted exact-source CP03/resource/atomicity antecedent evidence.',
                forbidden_assertions=['full_CP07_admission','final_E06_pass','authority_or_capture_permission'],
                legacy_CP07_exact_admission_resolved_field_present=False,
                antecedents=['E01_E05_PROOFS','ATOMICITY_ANTECEDENT','RESOURCE_INDEX','NEW_SOURCE_SCOPE'],
                current_accepted=False),
            dict(id='FINAL_COMPONENTS',proposed_schema_family='d5.prp181-component-*.v3',
                asserts='Actual final-manifest component run plus independent review/seal with exact real hashes.',
                no_transfer_from_qualifying_run_by_assertion=True,current_accepted=False),
            dict(id='PAYLOAD',proposed_schema='d5.prp181-authority-payload.v3',proposed_phase='BINDING_PAYLOAD_ONLY_NO_RUNTIME_PERMISSION',
                asserts='Actual final494 capture-input pins and explicit issuer scope, not admission grant.',
                excludes_own_path_and_final_root_from_capture_inputs=True,current_accepted=False),
            dict(id='FULL_ADMISSION',proposed_schema='d5.prp181-final-admission-root.v3',
                asserts='Final observed closure and genuine independent issuance after all predecessor bodies exist.',
                full_CP07_exact_admission_resolved_computed_only_after_root_and_all_conditions_validate=True,
                required_conditions=full_conditions,current_accepted=False)],
        semantic_rules=dict(source_basis_has_no_descendant_evidence_claim=True,
            atomicity_antecedent_must_be_real_and_accepted_before_basis_issuance=True,
            qualifying_component_route_only_with_separate_future_authorization_and_exact_scope=True,
            final_E06_required_even_if_antecedent_basis_accepted=True,
            full_CP07_not_reduced_to_source_hashes_count_Reader_fit_or_test_count=True,
            no_issued_verified_certificate_based_on_unperformed_final_run=True,
            final_root_signature_or_decision_not_a_substitute_for_true_resource_evidence=True),
        dependency_model=dict(direction='consumer -> prior evidence/body; protocol/semantic requirements included',nodes=edges,
            proposed_order=order,scoped_hash_and_semantic_dependency_model_acyclic=True,
            no_final_raw_review_seal_payload_or_root_in_basis_or_resource_index=True,
            unresolved_legacy_interpretation_counterexample=dict(
                conditional_assumption='If a predecessor full-CP07 claim requires its own final component seal.',
                edges={'LEGACY_FULL_CERT':['FINAL_SEAL'],'FINAL_SEAL':['FINAL_MANIFEST'],'FINAL_MANIFEST':['LEGACY_FULL_CERT']},
                cycle_under_that_assumption=True,not_a_claim_current_negative_I175_hash_DAG_is_cyclic=True)),
        final_root_protocol=dict(planned_path=ROOT_PATH,created=False,
            bootstrap_role='Trusted, explicitly selected final-root entrypoint, before authority/discovery checks in each InputPlan.',
            signed_core_fields=['protocol_version','proposal_source_scope','source_basis_sha256','registry_sha256','manifest_sha256',
                'raw_sha256','review_sha256','seal_sha256','authority_payload_sha256','ancestor_input_root_sha256',
                'role_acceptance_scope','validity','trust_verifier_profile'],
            signature_domain='Signature covers canonical signed_core only; signature field, root-file hash and future execution outcome excluded.',
            signature_issuer=None,trust_profile=None,key_material_created=False,signature_created=False,
            trust_anchor_requires_independent_accepted_runtime_caller_configuration=True,
            no_unaccounted_repository_or_trust_key_file_reads=True,
            root_not_pinned_by_authority_manifest_certificate_or_itself=True,
            same_Input_Reader_before_after_finish=True,root_in_PhaseBytes_and_Reader_finish_union=True,
            physical_union_rule='ROOT + AUTHORITY_PAYLOAD +494 payload manifest members; ROOT is a discovery root, never a free snapshot.',
            no_new_Reader_reset_or_extra_quota=True,
            fail_closed_on_absent_untrusted_expired_mismatched_unstable_root=True,
            root_verification_before_capture_path_reservation_and_worker_READY_RELEASE_functional_import=True,
            verification_inside_launch_t0_to_tR_and_all_actual_worker_windows=True,
            signature_parsing_IO_memory_CPU_GC_and_native_costs_not_free=True,
            same_root_digest_bound_into_parent_worker_invocation_READY_RELEASE=True,
            post_admission_capture_evidence_records_actual_root_digest_as_later_consumer=True,
            handshake_and_output_schemas_versioned_and_existing_limits_reproved=True),
        logical_future_slots=[dict(role=k,path=p,max_serialized_bytes=MAX_BYTES[k],actual_sha256=None,body_created=False) for k,p in PATHS.items()],
        successor_source_scope=dict(planned_namespace=SOURCE_DIR,created=False,
            slots=[SOURCE_DIR+n for n in ['capture.py','atomic.py','worker.py','test_joint_capture.py','run_joint_lab.py','README.md']],
            actual_source_hashes=None,total_six_source_bytes_design_upper=source_cap,
            old_I122_implementation_pins=old_impl,old_six_source_bytes=old_source_bytes,
            all_source_runtime_321_root_operand_atomicity_and_resource_proofs_require_requalification=True,
            no_unaccounted_old_I122_source_fresh_reads_or_helpers_allowed_by_budget=True),
        binding_and_reader_design_budget=dict(
            historical480_pins={p:sha(p) for p in sorted(historical)},historical480_bytes=historical_bytes,
            six_successor_sources_design_upper_bytes=source_cap,old_PRP173_nine_body_envelope_bytes=244992,
            final_root_extra_upper_bytes=8192,all_ten_body_upper_bytes=variable_cap,
            capture_manifest_members=494,ancestor_union_with_payload=495,physical_union_with_root=496,
            unique_design_upper_bytes=unique,three_pass_design_upper_bytes=3*unique,
            additional_fresh_design_ceiling_bytes=fresh_design_cap,read_design_upper_bytes=read_budget,
            unchanged_limits=dict(file_bytes=16777216,unique_bytes=134217728,read_bytes=268435456,paths=4096),
            design_margin_bytes=268435456-read_budget,
            numerical_budget_feasible_if_all_design_bounds_proved=True,successor_Reader_fit_verified=False,
            inherited4852460_not_automatically_transferable_to_changed_code=True,
            actual_sources_schemas_component_widths_key_IO_fresh_graph_listings_and_outputs_require_proof=True,
            no_new_body_envelope_is_a_product_quota_or_runtime_enforcement_change=True),
        acceptance_work=[
            'Named independent custodians/reviewers adopt or reject this versioned scope and gate split; F179-01 not closed by this proposal.',
            'Specify exact schemas, trust profile and fail-closed guard; implement only in separately authorized reviewed successor scope, never edit current I122 to bypass legacy CP07.',
            'Prove effective source/runtime closure, all original operand/atomicity scope and complete E01-E05 resources including new root verification costs.',
            'Prove final Reader graph/fresh ceilings and metadata/context/launch/package bounds for actual successor source bodies and schemas; all extra helper/key files must be charged or budget rejected.',
            'Obtain real qualifying antecedent evidence if needed and separately authorized final E06 on frozen predecessor metadata; no fake PASS or automatic transfer.',
            'Bind actual authority payload, issue trusted final root last and review every real hash/signature/validity/bound; no root self-pin.',
            'Separate explicit runtime/rebind/capture decision after complete acceptance; current task grants none.'],
        current_effect=dict(F179_01_solution_model_prepared=True,F179_01_resolved=False,S01_accepted=False,semantic_adoption=False,
            source_implementation_changed=False,contract_or_active_schema_changed=False,product_or_components_executed=False,
            quotas_changed=False,rebind_applied=False,pending_I175_bindings=4,resource_obligations_closed=0,
            independent_acceptance=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        source_evidence=source_evidence(),decision=rd(S01)['decision'],E06=rd(S01)['E06'])


def build_review():
    o=rd(OUT)
    return dict(schema='d5.i181-preparation-review.v1',increment='I181',date='2026-11-16',base_commit=BASE,
        status='VERSIONED_GATE_ORDER_PROPOSAL_PREPARED_REQUIRES_ADOPTION_IMPLEMENTATION_AND_EVIDENCE',input_pins={**inputs(),OUT:sha(OUT)},output=pin(OUT),
        counts=dict(historical_input_pins=len(inputs()),claim_stages=4,dependency_nodes=15,future_body_slots=10,source_slots=6,new_files=5),
        preparation_checks=dict(legacy_CP07_not_narrowed=True,basis_claim_excludes_future_components_and_full_admission=True,
            full_CP07_final_conditions_include_real_components_and_all_bindings=True,
            root_last_not_pinned_by_predecessors=True,root_charged_to_same_Input_Reader_all_three_passes=True,
            new_source_bytes_and_root_added_to_design_budget=True,new_proofs_not_assumed_inherited=True,
            no_positive_body_signature_authority_or_component_created=True),
        readiness=dict(documentary_solution_model_complete=True,semantic_adoption=False,implementation_ready=False,
            successor_Reader_fit_verified=False,execution_authorized=False,F179_01_resolved=False),
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I181-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: versioned protocol semantics/order proposal only; target/component execution prohibited.',over400_lines=True,
            reason='Concrete claim split, dependency model, charged root/source design budget and self-contained audit; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_not_adoption_or_authority=True))


def validate_preparation():
    assert rd(OUT)==build_proposal() and rd(REVIEW)==build_review();check_git_inputs()
    prior=rd(OLD_SEAL);preserved={**prior['preserved_published383'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)};seal=rd(SEAL)
    assert len(preserved)==388 and seal['preserved_published388']==preserved
    assert seal['schema']=='d5.i181-integrity.v1' and seal['base_commit']==BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert len(inputs())==696 and not FILES&set(inputs())
    o=rd(OUT);edges=o['dependency_model']['nodes'];order=topo(edges);assert order is not None and len(order)==15
    def ancestors(n):
        result=set();todo=list(edges[n])
        while todo:
            p=todo.pop()
            if p not in result:result.add(p);todo.extend(edges[p])
        return result
    late={'FINAL_RAW','FINAL_REVIEW','FINAL_SEAL','AUTHORITY_PAYLOAD','FINAL_ROOT','RUNTIME_ADMISSION_DECISION'}
    assert not ancestors('SOURCE_BASIS_CERT')&late and not ancestors('RESOURCE_INDEX')&late
    assert {'AUTHORITY_PAYLOAD','FINAL_RAW','FINAL_REVIEW','FINAL_SEAL','SOURCE_BASIS_CERT'}<=ancestors('FINAL_ROOT')
    assert topo(o['dependency_model']['unresolved_legacy_interpretation_counterexample']['edges']) is None
    assert all(not c['current_accepted'] for c in o['stage_claims'])
    assert not o['stage_claims'][0]['legacy_CP07_exact_admission_resolved_field_present']
    assert len(o['stage_claims'][3]['required_conditions'])==9
    budget=o['binding_and_reader_design_budget']
    assert budget['all_ten_body_upper_bytes']==253184 and budget['unique_design_upper_bytes']==87280411
    assert budget['read_design_upper_bytes']==266693693 and budget['design_margin_bytes']==1741763
    assert budget['read_design_upper_bytes']<budget['unchanged_limits']['read_bytes'] and budget['physical_union_with_root']==496<=4096
    assert budget['unique_design_upper_bytes']<budget['unchanged_limits']['unique_bytes']
    assert max([size(p) for p in rd(REG)['overrides']['required_prior_inputs']]+[262144]+list(MAX_BYTES.values()))<budget['unchanged_limits']['file_bytes']
    limits=rd(REG)['overrides']['limits']
    assert [limits[k] for k in ['input_file_bytes','input_unique_bytes','input_read_bytes','input_paths']]==[16777216,134217728,268435456,4096]
    assert not budget['successor_Reader_fit_verified']
    assert not (ROOT/SOURCE_DIR).exists()
    for p in list(PATHS.values())+[P+'D5-JOINT-tests-raw.json',P+'D5-JOINT-results.json',P+'D5-JOINT-integrity.json',P+'D5-JOINT-capture-authorization.json']:
        assert not (ROOT/p).exists(),p
    assert rd(C_CERT)['status']=='IMPLEMENTED_NOT_ADMITTED' and rd(C_CERT)['CP07_exact_admission_resolved'] is False
    assert rd(C_CERT)['correlated_atomicity_verified'] is False and rd(C_CERT)['component_validation']=='NOT_RUN'
    assert sha(CONTRACT)=='e7a873a2aea8648d225f2272854e0b15c3f21de5826df06f16dfb6e45aa54576'
    for k in ['resource_closure_verified','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)


REVIEW_BASE='1160581c48115cbc8e9053aa762e0c3ea0f0847d'
NEW_REVIEW=P+'D5-I182-PGO181-documentary-review.json'
RECON=P+'D5-I182-PGO181-source-reconstruction.json'
NEW_AUDIT=P+'D5-I182-audit.py'
NEW_SEAL=P+'D5-I182-integrity.json'
NEW_DESIGN='docs/design/D5-I182-F179-01-GATE-ORDER-REVIEW.md'
NEW_FILES={NEW_REVIEW,RECON,NEW_AUDIT,NEW_SEAL,NEW_DESIGN}


def review_blobs(pins):
    req=''.join(REVIEW_BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req));blobs={}
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
        blobs[p]=body
    return blobs


def dfs_order(edges):
    state={};order=[]
    def visit(n):
        assert n in edges
        if state.get(n)==1:raise ValueError('cycle')
        if state.get(n)==2:return
        state[n]=1
        for p in edges[n]:visit(p)
        state[n]=2;order.append(n)
    try:
        for n in edges:visit(n)
    except ValueError:return None
    return order


def reconstruct():
    pins={**rd(OUT)['input_pins'],**{p:sha(p) for p in FILES}}
    blobs=review_blobs(pins)
    def doc(p):return json.loads(blobs[p])
    o=doc(OUT);edges=o['dependency_model']['nodes'];order=dfs_order(edges)
    assert order is not None and len(order)==len(edges)==15
    position={n:i for i,n in enumerate(order)}
    assert all(position[p]<position[n] for n,deps in edges.items() for p in deps)
    def closure(n):
        reached=set();queue=list(edges[n])
        while queue:
            p=queue.pop()
            if p not in reached:reached.add(p);queue.extend(edges[p])
        return reached
    late={'FINAL_RAW','FINAL_REVIEW','FINAL_SEAL','AUTHORITY_PAYLOAD','FINAL_ROOT','RUNTIME_ADMISSION_DECISION'}
    assert not closure('SOURCE_BASIS_CERT')&late and not closure('RESOURCE_INDEX')&late
    root_needed={'SOURCE_BASIS_CERT','FINAL_RAW','FINAL_REVIEW','FINAL_SEAL','AUTHORITY_PAYLOAD','E01_E05_PROOFS','ATOMICITY_ANTECEDENT','REGISTRY','COMPONENT_MANIFEST','CAPACITY_CONTRACT','RESOURCE_INDEX','NEW_SOURCE_SCOPE'}
    assert root_needed<=closure('FINAL_ROOT')
    assert 'FINAL_ROOT' in closure('RUNTIME_ADMISSION_DECISION')
    assert not any('FINAL_ROOT' in closure(n) for n in edges if n not in ['FINAL_ROOT','RUNTIME_ADMISSION_DECISION'])
    counter=o['dependency_model']['unresolved_legacy_interpretation_counterexample']
    assert dfs_order(counter['edges']) is None and counter['not_a_claim_current_negative_I175_hash_DAG_is_cyclic']
    claims=o['stage_claims'];assert [c['id'] for c in claims]==['BASIS','FINAL_COMPONENTS','PAYLOAD','FULL_ADMISSION']
    basis,components,payload,full=claims
    assert not basis['legacy_CP07_exact_admission_resolved_field_present']
    assert basis['proposed_status']!='SOURCE_CAPACITY_VERIFIED'
    assert {'full_CP07_admission','final_E06_pass','authority_or_capture_permission'}<=set(basis['forbidden_assertions'])
    assert components['no_transfer_from_qualifying_run_by_assertion'] and payload['excludes_own_path_and_final_root_from_capture_inputs']
    assert payload['proposed_phase']!='JOINT_EXPLICITLY_APPROVED'
    required={
        'accepted_exact_source_basis_and_CP03_scope','accepted_E01_E05_complete_bounds_and_assumptions',
        'accepted_atomicity_antecedent_scope_not_just_source_written',
        'real_final_E06_raw_review_seal_bound_to_exact_final_manifest_runtime_sources',
        'all_actual_authority_payload_and494_manifest_body_hashes_match',
        'trusted_root_issuer_signature_scope_validity_and_distinct_acceptance',
        'root_and_all495_ancestor_bodies_stable_in_same_physical_Reader',
        'unchanged_file_unique_read_path_and_output_limits_hold_for_final_bytes',
        'explicit_separate_runtime_execution_request_and_admission_decision'}
    assert set(full['required_conditions'])==required and len(full['required_conditions'])==9
    assert full['full_CP07_exact_admission_resolved_computed_only_after_root_and_all_conditions_validate']
    assert all(not c['current_accepted'] for c in claims)
    root=o['final_root_protocol']
    assert root['root_not_pinned_by_authority_manifest_certificate_or_itself'] and root['same_Input_Reader_before_after_finish']
    assert root['root_in_PhaseBytes_and_Reader_finish_union'] and root['no_new_Reader_reset_or_extra_quota']
    assert root['fail_closed_on_absent_untrusted_expired_mismatched_unstable_root']
    assert root['root_verification_before_capture_path_reservation_and_worker_READY_RELEASE_functional_import']
    assert root['verification_inside_launch_t0_to_tR_and_all_actual_worker_windows'] and root['signature_parsing_IO_memory_CPU_GC_and_native_costs_not_free']
    assert root['same_root_digest_bound_into_parent_worker_invocation_READY_RELEASE']
    assert root['post_admission_capture_evidence_records_actual_root_digest_as_later_consumer']
    assert root['handshake_and_output_schemas_versioned_and_existing_limits_reproved']
    assert all(root[k] is None for k in ['signature_issuer','trust_profile']) and not root['signature_created'] and not root['key_material_created']
    assert not any(x in root['signed_core_fields'] for x in ['signature','root_sha256','future_execution_outcome'])
    # Recompute the new numeric allocation from exact historical bytes, not a
    # transfer of the old changed-source fresh-read proof.
    r=doc(REG)['overrides'];historical=set(r['required_prior_inputs']);old_sources=r['implementation_sources']
    hbytes=sum(len(blobs[p]) for p in historical);sbytes=sum(len(blobs[p]) for p in old_sources)
    assert len(historical)==480 and hbytes==86765083 and len(old_sources)==6 and sbytes==217934
    for p,h in old_sources.items():assert pins[p]==h
    slots=o['logical_future_slots'];assert len(slots)==10 and len({s['path'] for s in slots})==10
    assert all(s['actual_sha256'] is None and not s['body_created'] for s in slots)
    maxima={s['role']:s['max_serialized_bytes'] for s in slots}
    assert maxima['FINAL_ROOT']==8192 and sum(maxima.values())==253184
    source_cap=o['successor_source_scope']['total_six_source_bytes_design_upper'];assert source_cap==262144
    unique=hbytes+source_cap+sum(maxima.values());fresh=o['binding_and_reader_design_budget']['additional_fresh_design_ceiling_bytes']
    assert fresh==4852460 and unique==87280411
    read_upper=3*unique+fresh;assert read_upper==266693693 and 268435456-read_upper==1741763
    budget=o['binding_and_reader_design_budget']
    assert budget['physical_union_with_root']==480+6+10==496 and budget['capture_manifest_members']==494
    assert budget['ancestor_union_with_payload']==495 and budget['inherited4852460_not_automatically_transferable_to_changed_code']
    assert budget['actual_sources_schemas_component_widths_key_IO_fresh_graph_listings_and_outputs_require_proof']
    assert not budget['successor_Reader_fit_verified'] and not o['successor_source_scope']['created']
    assert o['successor_source_scope']['actual_source_hashes'] is None
    route=o['route_decision'];assert route['no_silent_reinterpretation_of_legacy_CP07'] and route['old_CP07_stays_false']
    assert route['source_or_schema_changes_required_for_adoption'] and not route['changes_implemented']
    assert route['not_a_drop_in_rebind_for_PRP173_or_current_I122'] and route['current_PFC126_I122_proofs_not_automatically_valid_for_successor']
    tree=ast.parse(blobs[JOINT].decode());anchors=[]
    for a in o['source_evidence']['anchors']:
        n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==a['symbol'])
        h=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()
        assert (n.lineno,n.end_lineno,h)==(a['line'],a['end_line'],a['AST_sha256'])
        anchors.append(dict(path=JOINT,symbol=a['symbol'],source_sha256=pins[JOINT],line=n.lineno,end_line=n.end_lineno,AST_sha256=h))
    require=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='require_admission')
    cmp={ast.unparse(n) for n in ast.walk(require) if isinstance(n,ast.Compare)}
    assert "cert.get('status') == 'SOURCE_CAPACITY_VERIFIED'" in cmp and "cert.get('CP07_exact_admission_resolved') is True" in cmp
    assert doc(C_CERT)['status']=='IMPLEMENTED_NOT_ADMITTED' and doc(C_CERT)['CP07_exact_admission_resolved'] is False
    return dict(schema='d5.i182-pgo181-source-reconstruction.v1',increment='I182',date='2026-11-16',base_commit=REVIEW_BASE,input_pins=pins,
        method='Fresh Git blobs, independent DFS/cycle and ancestor analysis, claim exclusion/full-predicate joins, charged root/source envelope arithmetic and legacy predicate AST bindings.',
        methodologically_separate=True,actor_independent=False,organizationally_independent=False,
        dependency_order=order,antecedent_closure_checks=[dict(node=n,ancestors=sorted(closure(n)),contains_late_evidence=False) for n in ['SOURCE_BASIS_CERT','RESOURCE_INDEX']],
        full_root_ancestor_check=dict(required_prior_nodes=sorted(root_needed),all_present=True),
        conditional_legacy_counterexample_is_cyclic=True,counterexample_not_a_current_I175_hash_cycle=True,
        claim_checks=[dict(id=c['id'],schema=c.get('proposed_schema',c.get('proposed_schema_family')),current_accepted=False) for c in claims],
        full_CP07_final_conditions=sorted(required),root_scope_checks=dict(same_physical_Reader_three_passes=True,not_free_or_extra_quota=True,
            no_predecessor_self_or_back_pin=True,fail_closed_is_required_not_implemented=True,
            signature_domain_antecedent_core_only=True,same_root_identity_handshake_and_later_evidence_required=True,
            verification_costs_inside_phase_scope=True,actual_trust_profile_or_signature=None),
        numeric_design_budget=dict(exact_historical480_bytes=hbytes,old_six_source_bytes=sbytes,new_six_source_design_ceiling=source_cap,
            ten_variable_body_design_ceiling=sum(maxima.values()),including_root_bytes=8192,unique_design_ceiling=unique,
            additional_fresh_ceiling_unproved=fresh,read_design_ceiling=read_upper,numeric_margin_if_all_conditions_hold=1741763,
            physical_paths=496,not_an_actual_successor_Reader_fit_proof=True),
        current_parser_legacy_predicates_unchanged=anchors,
        readiness_gaps=[
            'Named independent roles/custodians and semantic/protocol adoption absent; F179-01 remains open.',
            'Exact v3 schemas/canonical encoding/trust verifier profile and fail-closed implementation not supplied.',
            'Successor source bodies/hashes, original operand/30-site/321-root compatibility and E01-E05 resources require full requalification.',
            'Fresh-read ceiling, keys/helpers/listings, new handshake/output/context/package and every actual byte bound unproved.',
            'Real antecedent qualification if required, final E06, authority payload/root signatures and separate admission/execute permissions absent.'],
        counts=dict(input_pins=len(pins),claim_stages=4,dependency_nodes=15,full_CP07_conditions=9,source_slots=6,future_body_slots=10,legacy_source_anchors=2),
        semantic_solution_model_coherent=True,adopted=False,implemented=False,F179_01_resolved=False,resource_obligations_closed=0,execution_count=0)


CHECKS=[
    ('R01','Four distinct claims and incompatible v3 predecessor status/schema','PASS_VERSIONED_SCOPE_DESIGN'),
    ('R02','Basis/index exclude final E06, payload, root and runtime decision from ancestors','PASS_ANTECEDENT_ORDER_MODEL'),
    ('R03','Actual final E06 and complete bindings required at final-root stage','PASS_NO_FORECAST_OR_SCOPE_LOSS'),
    ('R04','Full CP07 remains nine-condition final predicate, not a static binding/count shortcut','PASS_FULL_ADMISSION_CONDITION_MODEL'),
    ('R05','Independent DFS and ancestor closure of15 evidence/body/decision nodes','PASS_SCOPED_MODEL_ACYCLICITY'),
    ('R06','Conditional legacy semantic cycle counterexample not confused with I175 byte DAG','PASS_COUNTEREXAMPLE_SCOPE'),
    ('R07','Root not back-pinned or self-pinned; signed core excludes signature/root hash/future result','PASS_PROPOSED_DEPENDENCY_RULE'),
    ('R08','Trusted fail-closed root, same-root handshake and later output evidence required','IMPLEMENTATION_SPEC_AND_TRUST_NOT_READY'),
    ('R09','Root charged to same Reader before/after/finish;496 paths, no reset or quota pool','PASS_DECLARED_IO_ACCOUNTING'),
    ('R10','New source/root bytes included;266693693 feasible arithmetic only','PASS_NUMERIC_DESIGN_BUDGET_NOT_FIT_PROOF'),
    ('R11','4852460 fresh ceiling and all new crypto/runtime/phase/output work need new proof','RESOURCE_AND_BYTE_PROOFS_PENDING'),
    ('R12','Existing parser cannot consume proposed schema/status; no silent legacy bypass','PASS_COMPATIBILITY_DISCLOSURE'),
    ('R13','No code, signatures, accepted root/payload or component PASS created','PASS_CURRENT_NONIMPLEMENTATION'),
    ('R14','Same actor; no independent adoption, role or custodian acceptance','PASS_PROVENANCE_DISCLOSURE'),
    ('R15','F179-01/S01/E01-E05/E06 and actual admission not closed by model review','NO_MATERIAL_CLOSURE'),
    ('R16','Prior bytes/no product/components/quota/source/rebind changes','PASS_PRESERVATION_ONLY')]


def review_record(rec):
    o=rd(OUT)
    return dict(schema='d5.i182-pgo181-documentary-review.v1',increment='I182',date='2026-11-16',base_commit=REVIEW_BASE,
        proposal_id='PGO181-SPLIT-ROOT-01',status='COHERENT_VERSIONED_SEMANTIC_SOLUTION_MODEL_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        input_pins={**rec['input_pins'],RECON:sha(RECON)},reconstruction=pin(RECON),
        provenance=dict(reviewer='Codex assistant in same chat; also prepared I181',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,independent_reviewer_identity=None,independent_acceptance=False,custodian_acceptance=False),
        checks=[dict(id=i,scope=s,result=r,resource_obligation_closed=False) for i,s,r in CHECKS],
        findings=dict(blocking_documentary_defects=[],semantic_solution_model_confirmed=True,readiness_gaps=rec['readiness_gaps'],
            review_not_an_implementation_security_proof_or_adoption=True,
            no_automatic_closure_of_F179_01_or_transfer_of_old_source_capacity_proofs=True),
        counts=rec['counts'],
        verdict=dict(documentary_conformance=True,model_coherent_under_stated_claims_and_edges=True,adopted=False,implemented=False,
            implementation_ready=False,successor_Reader_fit_verified=False,F179_01_resolved=False,
            resource_obligations_closed=0,independent_acceptance=False,rebind_applied=False,proposal_enabled=False,D5_closed=False),
        decision=o['decision'],E06=o['E06'],
        next_evidence_required='Obtain competent versioned protocol/semantic adjudication and exact schema/trust/source-impact specifications before separately authorized implementation. Requalify every bound and scope, obtain actual E06/root evidence and separate admission; no execution, source/quota or rebind change authorized by this review.',
        work_unit=dict(rollback_files=sorted(NEW_FILES),verification_command='python3 docs/validation/D5-I182-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary semantic/order model review; product/component execution prohibited.',over400_lines=True,
            reason='Self-contained historical checks, independent graph/claim/budget reconstruction and review evidence; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_not_adoption_or_authority=True))


def main():
    validate_preparation()
    rec=reconstruct();assert rd(RECON)==rec and rd(NEW_REVIEW)==review_record(rec)
    prior=rd(SEAL);preserved={**prior['preserved_published388'],**prior['artifacts'],SEAL:sha(SEAL)};seal=rd(NEW_SEAL)
    assert len(preserved)==393 and seal['preserved_published393']==preserved
    assert seal['schema']=='d5.i182-integrity.v1' and seal['base_commit']==REVIEW_BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==NEW_FILES-{NEW_SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    for k in ['resource_closure_verified','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert rec['counts']['input_pins']==701
    changes=set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changes==NEW_FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',REVIEW_BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=REVIEW_BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I182',proposal='PGO181-SPLIT-ROOT-01',documentary_conformance=True,
        semantic_solution_model_coherent=True,adopted=False,implemented=False,F179_01_resolved=False,successor_Reader_fit_verified=False,
        prior_published_files_preserved=393,new_files=5,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,independent_acceptance=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':main()
