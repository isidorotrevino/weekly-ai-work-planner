#!/usr/bin/env python3
"""I161 P05 documentary rollup: Git/JSON only; never import or run targets."""
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '3d4a726586c9c2fcc2976b96ba71e2507fe9a5a3'
OUT = P+'D5-PFC126-03-E02-HEAP-ROLLUP.json'
REVIEW = P+'D5-I161-P05-preparation-review.json'
AUDIT = P+'D5-I161-audit.py'
SEAL = P+'D5-I161-integrity.json'
DESIGN = 'docs/design/D5-I161-P05-HEAP-ROLLUP.md'
PLAN = P+'D5-I132-E01-E05-evidence-plan.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE = P+'D5-PFC126-03-RESOURCE-SCOPE.json'
P01_REVIEW = P+'D5-I134-P01-documentary-review.json'
RUNTIME = P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
OWNERS = ['H%02d'%i for i in range(1,12)]


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,allow_nan=False,
        sort_keys=True,separators=(',',':')).encode()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def owner_path(owner):
    return P+'D5-PFC126-03-E02-'+owner+'.json'


def review_path(index):
    return P+'D5-I'+str(138+2*index)+'-P04-H%02d-documentary-review.json'%index


def blob_evidence(pins):
    paths = sorted(pins)
    request = ''.join(BASE+':'+path+'\n' for path in paths).encode()
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    rows = []
    for path in paths:
        header = stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob',path
        size = int(header[2])
        body = stream.read(size)
        assert len(body)==size and stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==pins[path]==sha(path),path
        rows.append(dict(path=path,git_blob_oid=header[0],bytes=size,sha256=pins[path]))
    assert not stream.read()
    return dict(commit=BASE,input_pin_count=len(pins),input_blob_checks=rows,
        method='Git blob/current-byte and JSON record comparison; no target execution or new runtime/allocator proof.')


def owner_integration():
    c,scope = rd(CONTRACT),rd(SCOPE)
    hashes,vector,requirements,directed,partials = {},[],[],{},[]
    for i,owner in enumerate(OWNERS,1):
        path = owner_path(owner)
        o = rd(path)
        review = review_path(i)
        r = rd(review)
        expected = c['heap']['owner_budgets'][i-1]
        identity = o['owner_id_metric_and_exact_units']
        bound = o['verified_upper_bytes_and_derivation']
        fit = o['bound_fit_not_just_partial_payload']
        assert o['package_id']=='P04-'+owner and o['candidate_owner_record']==expected
        assert o['candidate_binding']['path']==CONTRACT and o['candidate_binding']['sha256']==sha(CONTRACT)
        assert o['candidate_binding']['contract_id']==c['contract_id'] and o['candidate_binding']['subject']==c['subject']
        assert identity['owner_id']==owner and identity['unit']=='exact_integer_bytes'
        assert identity['metric']==('allocator_overhead' if owner=='H11' else 'peak_requested_live_heap')
        assert o['candidate_budget_bytes']==expected['candidate_budget_bytes']
        assert bound['verified_upper_bytes'] is None and bound['complete_derivation'] is None and not bound['verified']
        assert fit['fits'] is None and fit['slack_bytes'] is None and not fit['overbudget_proved']
        assert not o['acceptance']['accepted_as_complete_'+owner+'_proof'] and not o['acceptance'][owner+'_verified']
        independent = r['acceptance'].get('independent_acceptance',r['acceptance'].get('independent_documentary_acceptance'))
        assert independent is False and r['documentary_dossier_conformance']
        assert not r['acceptance']['accepted_as_complete_'+owner+'_proof'] and r['acceptance']['resource_obligations_closed']==0
        hashes[owner] = dict(path=path,sha256=sha(path))
        vector.append(dict(owner_id=owner,artifact=hashes[owner],latest_review=dict(path=review,sha256=sha(review)),
            metric=identity['metric'],unit=identity['unit'],process_scope=identity['process'],
            candidate_budget_bytes=expected['candidate_budget_bytes'],verified_complete_upper_bytes=None,
            complete_derivation_supplied=False,owner_proof_verified=False,independently_accepted=False,
            fits=None,slack_bytes=None,fit_disposition=fit['fit_result'],overbudget_proved=False,
            documentary_dossier_conformance=True,resource_obligations_closed=0,
            bound_record_sha256=digest(bound),fit_record_sha256=digest(fit),
            latest_review_acceptance_sha256=digest(r['acceptance'])))
        inv = o['complete_live_allocation_inventory']
        assert not inv['complete'] and len(inv['required_classes'])==12
        for n,row in enumerate(inv['required_classes']):
            unknown = ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation']
            assert not row['verified'] and all(row[k] is None for k in unknown)
            requirements.append(dict(owner_id=owner,requirement_id=row['id'],record_sha256=digest(row),
                unknown_pointers=['/complete_live_allocation_inventory/required_classes/'+str(n)+'/'+k for k in unknown]))
        overlap = o['overlap_alias_original_and_rejected_prefix_treatment']
        assert overlap['inherited_scope']==scope['worker_heap_vs_other_process_scope']
        assert overlap['source_applicability']==scope['321_root_12_group_applicability']['I124_applicability']
        assert not overlap['complete_ownership_alias_lifetime_proof']
        assert {row['other_owner'] for row in overlap['boundary_requirements']}==set(OWNERS)-{owner}
        for row in overlap['boundary_requirements']:
            assert not row['resolved']
            directed[(owner,row['other_owner'])] = dict(owner_id=owner,other_owner=row['other_owner'],
                required_treatment=row.get('required_treatment',row.get('required_reconciliation')),
                record_sha256=digest(row),resolved=False)
        partials.append(dict(owner_id=owner,candidate_known_partial_upper=expected['known_partial_upper'],
            candidate_known_partial_unit=expected['known_partial_unit'],is_complete_term=False,
            rejection_rule=o['acceptance']['rejection_rule'],substituted_into_sum=False,
            not_actual_lower_bound_overbudget_or_infeasibility_proof=True))
    pairs = []
    for i,left in enumerate(OWNERS):
        for right in OWNERS[i+1:]:
            pairs.append(dict(owners=[left,right],directions=[directed[(left,right)],directed[(right,left)]],
                resolved=False,status='UNRESOLVED_TWO_DIRECTION_RECORDS_NOT_RECONCILED'))
    assert len(requirements)==132 and sum(len(r['unknown_pointers']) for r in requirements)==528
    assert len(directed)==110 and len(pairs)==55
    return dict(hashes=hashes,fit_vector=vector,unproved_requirement_records=requirements,
        unproved_inventory_value_count=528,unresolved_pairs=pairs,rejected_partial_substitutes=partials)


def required_fields(integrated):
    c,scope,runtime,platform = rd(CONTRACT),rd(SCOPE),rd(RUNTIME),rd(PLATFORM)
    heap = c['heap']
    candidate_sum = sum(r['candidate_budget_bytes'] for r in integrated['fit_vector'][:10])
    reserve = heap['unassigned_requested_reserve_bytes']
    assert candidate_sum==10938744832 and reserve==872415232
    assert candidate_sum+reserve==heap['requested_heap_candidate_bytes']==11811160064
    assert 11811160064+1073741824==heap['committed_heap_candidate_bytes']==12884901888
    assert not rd(P01_REVIEW)['acceptance']['independent_documentary_acceptance']
    assert not runtime['acceptance']['accepted_as_runtime_identity'] and not platform['acceptance']['accepted_as_platform_evidence']
    available = platform['available_worker_requested_and_committed_heap']
    processes = platform['coordinator_child_resource_and_interference_scope']
    assert not available['verified'] and available['available_requested_heap_bytes'] is None and available['available_committed_heap_bytes'] is None
    assert available['worker_metric_definitions']==scope['requested_committed_metrics']
    assert processes['declared_process_scope']==scope['worker_heap_vs_other_process_scope'] and not processes['verified']
    missing = [dict(owner_id=r['owner_id'],artifact=r['artifact'],rejection='MISSING_COMPLETE_BOUND_DERIVATION_AND_ACCEPTANCE',
        complete_upper_bytes=None,treated_as_zero=False,budget_or_partial_substitution_allowed=False,memory_closure_allowed=False)
        for r in integrated['fit_vector']]
    return dict(
        all11_owner_artifact_sha256=integrated['hashes'],
        complete_owner_fit_vector=integrated['fit_vector'],
        requested_sum_plus_832MiB_reserve=dict(owner_ids=OWNERS[:10],
            verified_complete_requested_sum_bytes=None,unassigned_reserve_bytes=reserve,
            verified_requested_sum_plus_reserve_bytes=None,requested_heap_candidate_bytes=11811160064,
            comparison='NOT_EVALUABLE_MISSING_TEN_COMPLETE_REQUESTED_BOUNDS',fits=None,slack_bytes=None,
            candidate_budget_arithmetic=dict(requested_owner_budget_sum_bytes=candidate_sum,reserve_bytes=reserve,
                sum_bytes=candidate_sum+reserve,equals11GiB_candidate=True,not_verified_demand_or_slack=True),
            no_null_to_zero_or_partial_budget_substitution=True),
        H11_overhead_and_committed_sum=dict(H11_metric='allocator_overhead',verified_complete_H11_upper_bytes=None,
            H11_candidate_budget_bytes=1073741824,H11_fits=None,verified_complete_committed_upper_bytes=None,
            committed_heap_candidate_bytes=12884901888,committed_fits=None,slack_bytes=None,
            coverage_record=dict(path=owner_path('H11'),sha256=sha(owner_path('H11')),
                metric_record_sha256=digest(rd(owner_path('H11'))['metric_and_coverage_requirements'])),
            conditional_rule='Only complete same-worker/domain coverage and complete requested/overhead bounds justify an additive committed upper.',
            candidate11_plus1_equals12GiB=True,candidate_arithmetic_not_committed_demand_or_capacity=True,
            no_independent_peak_subtraction_or_borrowed_requested_reserve=True),
        all_missing_terms_rejected=dict(owner_rejections=missing,missing_complete_owner_bounds=11,
            dependencies_not_accepted_for_closure=['P01','P02','P03'],
            unproved_inventory_requirements=integrated['unproved_requirement_records'],unproved_inventory_values=528,
            unresolved_ownership_pairs=55,unresolved_directed_boundary_records=110,
            capacity_attestation_missing=True,requested_backing_correspondence_missing=True,
            stop_memory_closure_on_any_missing_or_overbudget_term=True,memory_closure_halted=True,
            rejected_partial_substitutes=integrated['rejected_partial_substitutes'],
            partial_model_values_not_summed=True,no_actual_overbudget_or_infeasibility_proof=True,
            no_source_optimization_or_contract_revision_in_this_scope=True),
        available_capacity_and_process_scope_match=dict(platform=dict(path=PLATFORM,sha256=sha(PLATFORM)),
            available_requested_heap_bytes=None,available_committed_heap_bytes=None,
            availability_validity_interval=available['availability_validity_interval'],capacity_attested=False,
            declared_metric_and_worker_scope_consistent=True,actual_runtime_capacity_process_scope_match_verified=False,
            worker_scope=scope['worker_heap_vs_other_process_scope'],
            metric_record_sha256=digest(scope['requested_committed_metrics']),
            platform_availability_record_sha256=digest(available),platform_process_record_sha256=digest(processes),
            platform_identity_record_sha256=digest(platform['platform_runtime_pin_set_and_validity']),
            no_parent_child_RSS_or_budget_as_worker_capacity=True,no_joint_host_capacity_claim=True),
        zero_allocation_ledger=dict(state_metric='Documentary zero transfer ledger; not measured runtime usage or proved spare capacity.',
            reserve_accounting=c['reserve_accounting'],heap_reserve_allocation_bytes={k:0 for k in OWNERS[:10]},
            allocated_heap_reserve_total_bytes=0,H11_borrowed_bytes=0,time_reserve_allocated_seconds=0,
            nested_worker_allocated_seconds=0,resources_reserved=False,product_quotas_changed=False,
            candidate_budgets_changed=False,capture_inputs_rebound=False,authority_or_destination_created=False,
            independent_availability_or_capacity_proved=False))


def main():
    o,r,seal = rd(OUT),rd(REVIEW),rd(SEAL)
    c,plan = rd(CONTRACT),rd(PLAN)
    task = next(t for t in plan['tasks'] if t['id']=='P05')
    prior = rd(P+'D5-I160-integrity.json')
    preserved = {**prior['preserved_published278'],**prior['artifacts'],P+'D5-I160-integrity.json':sha(P+'D5-I160-integrity.json')}
    expected = {OUT,REVIEW,AUDIT,SEAL,DESIGN}
    assert len(preserved)==283 and seal['preserved_published283']==preserved
    assert set(seal['artifacts'])|{SEAL}==expected
    for pins in [preserved,seal['artifacts'],o['input_pins'],r['input_pins'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for path,h in pins.items():
            assert sha(path)==h,path
    assert set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('diff','HEAD','--name-only')
    assert o['base_commit']==r['base_commit']==seal['base_commit']==BASE
    assert o['date']==r['date']==seal['date']=='2026-11-15'
    assert o['schema']==task['output_schema'] and OUT==task['planned_output'] and o['package_id']=='P05'
    assert r['schema']=='d5.i161-p05-preparation-review.v1' and seal['schema']=='d5.i161-integrity.v1'
    assert o['status']=='PREPARED_INSUFFICIENT_HEAP_ROLLUP_E02_OPEN_NOT_ADMITTED'
    assert r['status']=='P05_PREPARATION_COMPLETE_MEMORY_CLOSURE_REJECTED_NO_ADMISSION'
    assert o['plan_binding']==dict(path=PLAN,sha256=sha(PLAN),package_id='P05',task_record_canonical_sha256=digest(task))
    assert o['candidate_binding']==dict(path=CONTRACT,sha256=sha(CONTRACT),contract_id=c['contract_id'],subject=c['subject'],source_revision='I122-CANDIDATE-01')
    assert len(o['input_pins'])==212 and o['provenance']==blob_evidence(o['input_pins'])
    integrated = owner_integration()
    fields = required_fields(integrated)
    assert set(task['required_specific_fields'])==set(fields) and len(fields)==7
    for key,value in fields.items():
        assert o[key]==value,key
    assert o['overlap_metric_process_review']==dict(
        owner_pairs=integrated['unresolved_pairs'],pair_count=55,directed_record_count=110,
        complete_ownership_alias_lifetime_coverage=False,all_required_inventory_classes_complete=False,
        requested_owner_ids=OWNERS[:10],overhead_owner_id='H11',
        H11_requested_backing_correspondence_proved=False,no_omission_alias_discount_or_physical_witness_merge=True,
        H02_suite_parent_is_inside_worker_not_coordinator=True,
        no_sum_of_partial_models_or_owner_budgets_as_complete_demand=True)
    assert [row['field'] for row in o['field_assessment']]==task['required_specific_fields']
    documentary = {'all11_owner_artifact_sha256','all_missing_terms_rejected','zero_allocation_ledger'}
    for row in o['field_assessment']:
        assert row['result']==('DOCUMENTARY_BINDING_OR_REJECTION_POLICY_ONLY' if row['field'] in documentary else 'INSUFFICIENT_FOR_ACCEPTANCE')
        assert row['basis'] and not row['resource_obligation_closed']
    assert o['acceptance']==dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
        accepted_as_complete_heap_rollup=False,all11_owner_fits_verified=False,requested_sum_verified=False,
        H11_overhead_verified=False,committed_sum_verified=False,capacity_attested=False,
        E02_closed=False,resource_obligations_closed=0,no_reserve_transfer=True)
    assert [d['id'] for d in o['dependencies']]==task['depends_on'] and len(o['dependencies'])==14
    for row in o['dependencies']:
        assert row['sha256']==sha(row['path']) and row['output_created'] and not row['accepted_for_resource_closure']
    provenance = o['producer_and_review_provenance']
    assert provenance['producer_identity']=='Codex assistant preparing I161 in this chat'
    assert provenance['planned_author_role']==task['responsible_role'] and provenance['planned_review_role']==task['review_role']
    assert provenance['independent_reviewer_identity'] is None and not provenance['independent_acceptance'] and not provenance['runtime_custodian_authority_claimed']
    assert o['non_execution_and_zero_transfer_policy']==rd(SCOPE)['non_execution_and_zero_transfer_policy']
    assert o['reserve_accounting']==c['reserve_accounting']
    for row,old in zip(o['E02_criterion_disposition'],rd(owner_path('H11'))['E02_criterion_disposition'],strict=True):
        assert row==dict(id=old['id'],inherited_result=old['I159_result'],I161_result=old['I159_result'],closed=False)
    assert r['E02_criterion_disposition']==o['E02_criterion_disposition']
    assert r['input_pins']=={**o['input_pins'],OUT:sha(OUT)}
    assert r['output']==dict(path=OUT,sha256=sha(OUT),schema=o['schema'],evidence_kind=o['evidence_kind'],produced=True)
    assert all(r['preparation_checks'].values())
    assert r['counts']==dict(required_fields=7,documentary_or_rejection_policy_fields=3,insufficient_fields=4,
        owner_artifacts=11,latest_owner_reviews=11,complete_owner_bounds=0,missing_owner_bounds=11,
        requested_owner_bounds=10,overhead_owner_bounds=1,unproved_inventory_classes=132,
        unproved_inventory_values=528,unresolved_owner_pairs=55,unresolved_directed_boundaries=110,
        formal_dependencies=14,input_pins=212,other_unproduced_packages=5)
    for progress,t in zip(r['package_progress'],plan['tasks'],strict=True):
        exists = t['id'] in ['P01','P02','P03','P05']+['P04-H%02d'%i for i in range(1,12)]
        assert (ROOT/t['planned_output']).exists()==progress['output_created']==exists
        assert progress['package_id']==t['id'] and progress['path']==t['planned_output']
        assert progress['sha256']==(sha(t['planned_output']) if exists else None)
    assert r['independent_review']==dict(accepted=False,reviewer_identity=None,no_independent_review_fabricated=True)
    old_decision = rd(owner_path('H11'))['decision']
    negative = {('complete_heap_rollup_verified' if k=='complete_H11_bound_verified' else k):v for k,v in old_decision.items()}
    assert o['decision']==r['decision']==negative and o['E06']==r['E06']==rd(owner_path('H11'))['E06']
    assert not any(o['external_material_scope'][k] for k in ['global_absence_claimed','external_contacts_made','runtime_or_platform_sampled'])
    assert seal['source_only'] and not any(seal[k] for k in ['heap_rollup_verified','independent_acceptance',
        'proposal_enabled','product_or_components_executed','quotas_changed','D5_closed'])
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I161-audit.py'
    assert r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY' and r['work_unit']['diff_budget_note']
    for path in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:
        assert not (ROOT/path).exists()
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I161',package='P05',preparation_complete=True,
        accepted_as_complete_heap_rollup=False,owner_artifacts=11,missing_complete_owner_bounds=11,
        requested_sum_bytes=None,H11_upper_bytes=None,committed_sum_bytes=None,capacity_attested=False,
        unresolved_owner_pairs=55,prior_published_files_preserved=283,new_files=5,
        product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
