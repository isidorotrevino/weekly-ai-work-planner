#!/usr/bin/env python3
"""I171 documentary P10 assessment; JSON/Git/AST only, never execute target code."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='fd0a072bceeadd7055f1c0dda94daeaf3d6ea6db'
OUT=P+'D5-PFC126-03-E01-E05-CLOSURE-REVIEW.json'
REVIEW=P+'D5-I171-P10-preparation-review.json'
AUDIT=P+'D5-I171-audit.py'
SEAL=P+'D5-I171-integrity.json'
DESIGN='docs/design/D5-I171-P10-E01-E05-CLOSURE-REVIEW.md'
PLAN=P+'D5-I132-E01-E05-evidence-plan.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
OLD=P+'D5-I131-E01-E05-review.json'
SCOPE=P+'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME=P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM=P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
HEAP=P+'D5-PFC126-03-E02-HEAP-ROLLUP.json'
WORK=P+'D5-PFC126-03-E03-WORK-GROUPS.json'
COMPAT=P+'D5-PFC126-03-E03-E04-COMPATIBILITY.json'
PHASE=P+'D5-PFC126-03-E05-PHASE-BOUNDS.json'
BUNDLE=P+'D5-PFC126-03-RESOURCE-BUNDLE-BINDING-REVIEW.json'
CERT=P+'D5-I122-CAPACITY-CERTIFICATE.json'
OLD_SEAL=P+'D5-I170-integrity.json'
FILES={OUT,REVIEW,AUDIT,SEAL,DESIGN}


def rd(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(path):return dict(path=path,sha256=sha(path))
def pointer(obj,path):
    for key in path.strip('/').split('/'):
        key=key.replace('~1','/').replace('~0','~')
        obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    return obj

def ref(path,ptr):return dict(**pin(path),json_pointer=ptr,observed_canonical_sha256=digest(pointer(rd(path),ptr)))


def inputs():
    extras=[BUNDLE,P+'D5-I169-P09-preparation-review.json',P+'D5-I169-audit.py',P+'D5-I169-integrity.json',
        P+'D5-I170-P09-documentary-review.json',P+'D5-I170-P09-source-reconstruction.json',P+'D5-I170-audit.py',OLD_SEAL]
    return {**rd(BUNDLE)['input_pins'],**{p:sha(p) for p in extras}}


def check_git_inputs():
    pins=inputs();request=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    for path,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',path
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(path),path


CRITERIA=[
    ('E01-R1',[(RUNTIME,'/historical_reference')], 'P02 retains I127 as a historical file reference, not target runtime or loaded closure evidence.'),
    ('E01-R2',[(SCOPE,'/candidate_id_and_sha256'),(RUNTIME,'/source_anchors')], 'Candidate/source bytes remain bound; source anchors do not establish exact binary correspondence.'),
    ('E01-R3',[(RUNTIME,'/exact_interpreter_stdlib_frozen_builtin_extension_closure'),(RUNTIME,'/source_binary_build_correspondence')], 'P02 exact loaded/frozen/native/runtime and source-to-binary closure remains unaccepted.'),
    ('E01-R4',[(RUNTIME,'/producer_authority_signature_and_validity'),(PLATFORM,'/producer_authority_signature_and_validity')], 'No accepted custodian/platform authority, signatures, trust anchor or validity material.'),
    ('E02-R1',[(HEAP,'/requested_sum_plus_832MiB_reserve'),(HEAP,'/zero_allocation_ledger')], 'P05 conserves candidate11GiB requested/12GiB committed and zero allocations; no verified demand or capacity follows.'),
    ('E02-R2',[(HEAP,'/complete_owner_fit_vector')], 'P05 all11 complete owner upper bounds remain null and none is independently accepted.'),
    ('E02-R3',[(HEAP,'/H11_overhead_and_committed_sum'),(CONTRACT,'/reserve_accounting/heap')], 'H11 remains separate; no null-to-zero, borrowed reserve or allocator bound follows from the budget.'),
    ('E02-R4',[(HEAP,'/requested_sum_plus_832MiB_reserve'),(HEAP,'/H11_overhead_and_committed_sum'),(HEAP,'/available_capacity_and_process_scope_match')], 'Complete requested/committed sums and attested compatible capacity remain missing.'),
    ('E03-R1',[(WORK,'/all10_cost_group_inventory_and_source_anchors')], 'P06 adopts ten cost requirements and exact source anchors; inventory is not transitive work closure.'),
    ('E03-R2',[(WORK,'/all10_cost_group_inventory_and_source_anchors'),(WORK,'/per_process_phase_work_vectors_and_units')], 'Thirty group work/CPU/wall values and120 selected vector values remain null; no compatible whole-work upper.'),
    ('E03-R3',[(WORK,'/transitive_original_native_codec_GC_destruction_costs'),(COMPAT,'/work_to_service_conversion_or_WCET_derivation')], 'Complete transitive work/native/GC/destruction and work-to-service or WCET conversion remain unproved.'),
    ('E03-R4',[(WORK,'/worker_pre_READY_and_post_receipt_before_tR_coverage'),(WORK,'/wait_return_observation_and_success_finally_coverage')], 'Pre-main/pre-parent-tR worker work, exit-to-wait observation and finally through tF are requirements, not free work.'),
    ('E04-R1',[(COMPAT,'/worker_category_upper_vector_and_coverage_inequality'),(CONTRACT,'/reserve_accounting/worker_nested')], '600/90/60 sums750 only as a candidate; no extra category reserve or coverage guarantee.'),
    ('E04-R2',[(PLATFORM,'/compatible_CPU_service_unit_rate_latency_or_WCET_assumptions'),(COMPAT,'/work_to_service_conversion_or_WCET_derivation')], 'Rate, unit, latency and exact WCET route remain unselected or unverified.'),
    ('E04-R3',[(PLATFORM,'/bounded_scheduler_locks_IO_child_completion_observation_delays'),(COMPAT,'/CPU_IO_child_scheduler_and_native_delay_bounds')], 'No accepted scheduler/lock/IO/child/observation or native delay coverage for all required process/windows.'),
    ('E04-R4',[(COMPAT,'/latency_owner_map_without_unproved_deductions'),(COMPAT,'/exact_runtime_platform_process_unit_match')], 'Compatible units/processes and explicit latency owners required; CPU-time is not automatically wall and overlap is not deducted.'),
    ('E05-R1',[(PHASE,'/t0_tR_tW_tF_exact_source_and_clock_domain'),(PHASE,'/exact_True_wait_return_and_independent_success_qualification')], 'Four normative markers and exact-True tW remain distinct from later success eligibility and clock attestation.'),
    ('E05-R2',[(PHASE,'/verified_Tpre_Tworker_Tpost_upper_seconds')], 'Three phase uppers remain null; all seven conditional-theorem premises are unsatisfied.'),
    ('E05-R3',[(PHASE,'/60_750_60_plus30_conserved_zero_transfer_account')], '60+750+60+30=900 conserved, outer and nested transfers zero; arithmetic is not successful duration proof.'),
    ('E05-R4',[(PHASE,'/heap_runtime_service_assumptions_satisfied'),(PHASE,'/nonnegative_complete_phase_partition'),(PHASE,'/failure_paths_excluded_from_success_claim_without_omitting_heap_rejection_scope')], 'Actual clock/order/full coverage and resource assumptions unverified; no watchdog/absent-marker-zero/every-failure deadline substitute.'),
]


def current_criteria():
    original={c['id']:c for o in rd(OLD)['obligations'] for c in o['criteria']}
    result=[]
    for id,refs,basis in CRITERIA:
        old=original[id]
        for r in old['references']:
            assert r['sha256']==sha(r['path'])
            assert digest(pointer(rd(r['path']),r['json_pointer']))==r['observed_canonical_sha256']
        result.append(dict(id=id,obligation=id.split('-')[0],kind=old['kind'],inherited_result=old['result'],
            I171_result=old['result'],basis=basis,current_references=[ref(p,ptr) for p,ptr in refs],
            historical_reference_record_sha256=digest(old),closed=False,resource_obligation_closed=False))
    assert set(original)=={x['id'] for x in result} and len(result)==20
    return result


def source_evidence():
    c=rd(CONTRACT);anchors=c['cost_coverage']['source_anchors']
    trees={p:ast.parse((ROOT/p).read_text()) for p in {a['path'] for a in anchors}}
    def bind(a):
        found=[n for n in ast.walk(trees[a['path']]) if hasattr(n,'lineno') and
            (n.lineno,n.col_offset,n.end_lineno)==(a['line'],a['column'],a['end_line']) and
            hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']]
        assert len(found)==1
        if a.get('expression') is not None:assert ast.unparse(found[0])==a['expression']
        return dict(anchor=a,source_sha256=sha(a['path']),source_binding_verified=True)
    return dict(cost_anchors=[bind(a) for a in anchors],markers=[dict(id=m['id'],source_check=bind(m['source_anchor']),
        clock_value=None) for m in c['time']['normative_markers']],source_only_not_runtime_or_temporal_attestation=True)


def obligation_records():
    paths={t['id']:t['planned_output'] for t in rd(PLAN)['tasks']}
    groups={
        'E01':(['P01','P02','P03','P09'],'EXACT_RUNTIME_PROVENANCE_AND_PLATFORM_ACCEPTANCE_MISSING',
            'Complete target interpreter/stdlib/frozen/builtin/native/allocator/kernel/source-binary mapping, signed authority and validity absent.'),
        'E02':(['P01','P02','P03']+['P04-H%02d'%i for i in range(1,12)]+['P05','P09'],'COMPLETE_HEAP_AND_ATTESTED_CAPACITY_UNPROVED',
            'All11 complete owner uppers, requested/committed sums, allocator overhead and compatible available capacity remain unproved.'),
        'E03':(['P01','P02','P03','P06','P07','P09'],'COMPLETE_TRANSITIVE_WORK_OR_WCET_UNPROVED',
            'Ten requirement groups and20 vectors supply no complete compatible work/native/runtime/WCET upper.'),
        'E04':(['P02','P03','P06','P07','P09'],'COMPATIBLE_SERVICE_AND_BOUNDED_DELAYS_UNPROVED',
            'No attested rate/unit/process domain or justified exact-platform WCET; waits/locks/IO/children/observation and load/liveness unproved.'),
        'E05':(['P01','P02','P03','P05','P06','P07','P08','P09'],'QUALIFIED_SUCCESS_PHASE_BOUNDS_AND_900_UNPROVED',
            'Actual clock and complete ordered coverage absent, three phase uppers null and seven theorem premises unsatisfied.')}
    return [dict(id=id,status='OPEN_NOT_VERIFIED',finding=state,basis=basis,
        required_artifacts=[dict(package_id=i,**pin(paths[i])) for i in ids],
        criteria_ids=[c[0] for c in CRITERIA if c[0].startswith(id+'-')],
        complete_bound_accepted=False,attestation_accepted=False,dependency_assumptions_satisfied=False,
        independent_acceptance=False,verified=False,closed=False)
        for id,(ids,state,basis) in groups.items()]


def build_output():
    plan=rd(PLAN);task=next(t for t in plan['tasks'] if t['id']=='P10');criteria=current_criteria()
    heap,work,compat,phase,bundle=[rd(p) for p in [HEAP,WORK,COMPAT,PHASE,BUNDLE]]
    artifacts=[]
    for t in plan['tasks']:
        if t['id']=='P10':continue
        doc=rd(t['planned_output'])
        artifacts.append(dict(package_id=t['id'],**pin(t['planned_output']),schema=doc['schema'],
            status=doc['status'],accepted_for_resource_closure=False,planned_dependencies=t['depends_on']))
    decision=dict(bundle['decision']);decision['complete_E01_E05_resource_closure_verified']=False
    fields=dict(
        E01_E05_status_with_required_artifact_hashes=obligation_records(),
        all20_I131_criteria_reassessed=dict(baseline=pin(OLD),criteria=criteria,
            counts=dict(total=20,documentary_consistency_only=9,historical_reference_only=1,complete_evidence_not_supplied=10,
                verified_resource_criteria=0,resource_obligations_closed=0),counts_not_a_completion_percentage=True),
        complete_bound_and_attestation_acceptance_per_obligation=dict(
            vector=[dict(obligation='E%02d'%i,complete_bounds_accepted=False,complete_signed_attestation_accepted=False,
                assumptions_closed=False,independently_accepted=False,verified=False) for i in range(1,6)],
            current_dependency_acceptances=dict(P01=rd(SCOPE)['acceptance_state'],P02=rd(RUNTIME)['acceptance'],
                P03=rd(PLATFORM)['acceptance'],P05=heap['acceptance'],P06=work['acceptance'],P07=compat['acceptance'],P08=phase['acceptance'],P09=bundle['acceptance']),
            heap_complete_owner_upper_vector=[dict(owner=x['owner_id'],artifact=x['artifact'],latest_review=x['latest_review'],
                verified_complete_upper_bytes=x['verified_complete_upper_bytes'],independently_accepted=False) for x in heap['complete_owner_fit_vector']],
            complete_requested_sum_bytes=heap['requested_sum_plus_832MiB_reserve']['verified_complete_requested_sum_bytes'],
            complete_committed_upper_bytes=heap['H11_overhead_and_committed_sum']['verified_complete_committed_upper_bytes'],
            complete_work_upper=None,compatible_service_rate=None,verified_phase_upper_seconds={x['id']:x['verified_upper_seconds'] for x in phase['verified_Tpre_Tworker_Tpost_upper_seconds']['phases']},
            candidate_arithmetic_not_resource_acceptance=True),
        remaining_external_blocks_or_negative_findings=dict(
            runtime_authority=rd(RUNTIME)['producer_authority_signature_and_validity'],platform_authority=rd(PLATFORM)['producer_authority_signature_and_validity'],
            findings=[x['basis'] for x in obligation_records()]+[
                'P09 retained extension requires at least287840292 bytes per Input Reader versus268435456, conditionally under its frozen retained graph and three same-Reader passes.',
                'Direct append violates current exact admission input set; final authority/components/P09/P10 graph and metadata fit remain unverified.',
                'All package preparation does not supply independent resource review, separate acceptance or competent custodian authority.'],
            P09_negative_review=pin(P+'D5-I170-P09-documentary-review.json'),
            conditional_Reader_nonfit=dict(frozen_resource_members=244,additional_members=146,known_fixed_read_lower_bytes=287840292,
                read_limit=268435456,excess_per_Input_Reader_bytes=19404836,applies_only_to_P09_retained_extension=True,
                P10_or_I171_not_added_to_frozen_selection=True,not_all_packagings_or_actual_runtime_infeasible=True),
            future_packaging_or_quota_source_changes_authorized=False,external_contacts_made=False,global_absence_claimed=False),
        E06_still_separate_and_NOT_RUN=dict(inherited=phase['E06'],execution_authorized=False,
            component_validation=rd(CERT)['component_validation'],component_runtime_evidence_produced=False,
            all_E01_E05_verified_would_not_supply_E06=True),
        capture_authority_and_source_certificate_unchanged_until_independent_admission=dict(
            certificate=pin(CERT),certificate_status=rd(CERT)['status'],
            certificate_source_bindings_not_rewritten=True,capture_inputs_rebound=False,active_gate_updated=False,
            capture_authority_created=False,capture_destination_created=False,issue_SOURCE_CAPACITY_VERIFIED=False,
            proposal_enabled=False,product_quotas_changed=False,source_implementation_changed=False,
            reserves_transferred=False,documentary_assessment_not_execution_or_capture_permission=True),
        reviewer_identity_date_validity_and_source_scope=dict(
            preparer='Codex assistant in same chat; also prepared/reviewed preceding packages',date='2026-11-16',timezone='Europe/Madrid',
            planned_author_role=task['responsible_role'],planned_review_role=task['review_role'],
            actual_role='Documentary negative assessment preparer, not an independent resource-proof or separate acceptance reviewer',
            actor_independent=False,organizationally_independent=False,independent_reviewer_identity=None,separate_acceptance_reviewer_identity=None,
            custodian_identity=None,signature_or_authority=None,attestation_validity=None,independent_acceptance=False,
            source_scope=dict(candidate_contract=pin(CONTRACT),source_revision='I122-CANDIDATE-01',resource_scope=pin(SCOPE),
                P09_frozen_scope_not_mutated=True,no_new_external_runtime_or_platform_inspection=True)))
    assert list(fields)==task['required_specific_fields']
    paths={t['id']:t['planned_output'] for t in plan['tasks']}
    return dict(schema=task['output_schema'],package_id='P10',increment='I171',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        status='PREPARED_NEGATIVE_RESOURCE_ASSESSMENT_E01_E05_OPEN_NO_INDEPENDENT_ACCEPTANCE_NOT_ADMITTED',
        evidence_kind='DOCUMENTARY_NEGATIVE_ASSESSMENT_NOT_RESOURCE_CLOSURE_RUNTIME_OR_CAPTURE_PROOF',
        plan_binding=dict(**pin(PLAN),task_record_canonical_sha256=digest(task)),candidate_binding=phase['candidate_binding'],input_pins=inputs(),
        dependencies=[dict(id=i,**pin(paths[i]),accepted_for_resource_closure=False) for i in task['depends_on']],
        prior_plan_artifact_inventory=artifacts,source_evidence=source_evidence(),**fields,
        plan_endpoint=dict(all20_outputs_prepared_including_this_output=True,prior_output_count=19,
            truthful_negative_assessment_allowed_by_plan=True,I132_historical_bytes_unchanged=True,
            independent_P10_resource_review_and_separate_acceptance_pending=True,
            documentary_plan_endpoint_not_D5_closure=True,no_completion_claim_for_resource_obligations=True),
        acceptance=dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
            valid_as_truthful_negative_documentary_preparation=True,accepted_as_independent_resource_proof_review=False,
            accepted_by_separate_acceptance_reviewer=False,all_E01_E05_verified=False,resource_obligations_closed=0,
            E06_satisfied=False,proposal_enabled=False,D5_closed=False),
        reserve_accounting=rd(CONTRACT)['reserve_accounting'],non_execution_and_zero_transfer_policy=rd(SCOPE)['non_execution_and_zero_transfer_policy'],
        E06=phase['E06'],decision=decision)


def build_review():
    o=rd(OUT);progress=[]
    for t in rd(PLAN)['tasks']:
        exists=(ROOT/t['planned_output']).exists()
        progress.append(dict(package_id=t['id'],path=t['planned_output'],output_created=exists,
            sha256=sha(t['planned_output']) if exists else None,accepted_for_resource_closure=False))
    return dict(schema='d5.i171-p10-preparation-review.v1',increment='I171',date='2026-11-16',base_commit=BASE,
        status='P10_NEGATIVE_ASSESSMENT_PREPARED_E01_E05_OPEN_NO_ADMISSION',input_pins={**inputs(),OUT:sha(OUT)},output=pin(OUT),
        counts=dict(required_fields=7,obligations=5,open_obligations=5,criteria=20,documentary_only=9,historical_reference_only=1,
            complete_evidence_not_supplied=10,resource_obligations_closed=0,direct_dependencies=8,prior_plan_outputs=19,
            plan_outputs_prepared=20,remaining_unproduced_packages=0,source_cost_anchors=20,source_markers=4,input_pins=len(inputs())),
        preparation_checks=dict(all7_fields_present=True,all20_criteria_reassessed_from_current_artifacts=True,all5_obligations_open=True,
            all_prior_plan_outputs_real_and_pinned=True,conditional_P09_nonfit_scope_preserved=True,no_independence_fabricated=True,
            E06_and_capture_authority_separate=True,no_quota_rebind_or_source_change=True),
        package_progress=progress,acceptance=o['acceptance'],decision=o['decision'],E06=o['E06'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I171-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary negative resource assessment only; product/component execution prohibited.',over400_lines=True,
            reason='Twenty current criterion dispositions, exact artifact pins and self-contained documentary audit; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_does_not_admit_candidate=True))


def main():
    assert rd(OUT)==build_output() and rd(REVIEW)==build_review();check_git_inputs()
    prior=rd(OLD_SEAL);preserved={**prior['preserved_published328'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)};seal=rd(SEAL)
    assert len(preserved)==333 and seal['preserved_published333']==preserved
    assert seal['schema']=='d5.i171-integrity.v1' and seal['base_commit']==BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for p,h in pins.items():assert sha(p)==h,p
    o=rd(OUT);criteria=o['all20_I131_criteria_reassessed']['criteria']
    assert len(inputs())==644 and not FILES&set(inputs())
    assert len(criteria)==20 and len({r['id'] for r in criteria})==20
    assert sum(r['I171_result']=='DOCUMENTARY_CONSISTENCY_ONLY' for r in criteria)==9
    assert sum(r['I171_result']=='HISTORICAL_REFERENCE_ONLY' for r in criteria)==1
    assert sum(r['I171_result']=='COMPLETE_EVIDENCE_NOT_SUPPLIED' for r in criteria)==10
    assert all(not r['closed'] and not r['resource_obligation_closed'] for r in criteria)
    assert [r['id'] for r in o['E01_E05_status_with_required_artifact_hashes']]==['E01','E02','E03','E04','E05']
    assert all(not r['verified'] and not r['closed'] and r['status']=='OPEN_NOT_VERIFIED' for r in o['E01_E05_status_with_required_artifact_hashes'])
    assert len(o['prior_plan_artifact_inventory'])==19 and all((ROOT/t['planned_output']).exists() for t in rd(PLAN)['tasks'])
    assert len(o['dependencies'])==8 and [r['id'] for r in o['dependencies']]==['P01','P02','P03','P05','P06','P07','P08','P09']
    assert len(o['complete_bound_and_attestation_acceptance_per_obligation']['heap_complete_owner_upper_vector'])==11
    assert all(r['verified_complete_upper_bytes'] is None for r in o['complete_bound_and_attestation_acceptance_per_obligation']['heap_complete_owner_upper_vector'])
    assert all(v is None for v in o['complete_bound_and_attestation_acceptance_per_obligation']['verified_phase_upper_seconds'].values())
    assert sha(CONTRACT)=='e7a873a2aea8648d225f2272854e0b15c3f21de5826df06f16dfb6e45aa54576'
    assert o['E06_still_separate_and_NOT_RUN']['component_validation']=='NOT_RUN'
    assert o['remaining_external_blocks_or_negative_findings']['conditional_Reader_nonfit']['excess_per_Input_Reader_bytes']==287840292-268435456==19404836
    for t in o['prior_plan_artifact_inventory']:assert t['sha256']==sha(t['path']) and t['path'] in inputs()
    for p in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists()
    for k in ['resource_closure_verified','independent_acceptance','product_or_components_executed','quotas_changed','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    changes=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changes==FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I171',package='P10',preparation_complete=True,
        open_obligations=5,criteria_reassessed=20,documentary_only=9,historical_reference_only=1,complete_evidence_not_supplied=10,
        plan_outputs_prepared=20,independent_acceptance=False,prior_published_files_preserved=333,new_files=5,
        product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,proposal_enabled=False,
        D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':main()
