#!/usr/bin/env python3
"""I162 P05 review: documentary Git/JSON only; no target execution/probes."""
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


def validate_preparation():
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
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
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

REVIEW_BASE = 'b44746d4fdebf5fd512f00d39005386732aea33e'
NEW_REVIEW = P+'D5-I162-P05-documentary-review.json'
RECON = P+'D5-I162-P05-source-reconstruction.json'
NEW_AUDIT = P+'D5-I162-audit.py'
NEW_SEAL = P+'D5-I162-integrity.json'
NEW_DESIGN = 'docs/design/D5-I162-P05-HEAP-ROLLUP-REVIEW.md'


def blobs(commit,paths):
    paths = list(paths)
    request = ''.join(commit+':'+path+'\n' for path in paths).encode()
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    result = {}
    for path in paths:
        header = stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob',path
        size = int(header[2])
        body = stream.read(size)
        assert len(body)==size and stream.read(1)==b'\n'
        result[path]=(header[0],body)
    assert not stream.read()
    return result


def reconstruct():
    oid,body = blobs(REVIEW_BASE,[OUT])[OUT]
    o = json.loads(body)
    assert hashlib.sha256(body).hexdigest()==sha(OUT)
    data = blobs(o['base_commit'],sorted(o['input_pins']))
    checks = []
    for path,h in sorted(o['input_pins'].items()):
        blob_oid,content = data[path]
        assert hashlib.sha256(content).hexdigest()==h==sha(path),path
        checks.append(dict(path=path,preparation_blob_oid=blob_oid,sha256=h,bytes=len(content)))
    def value(path):
        return json.loads(data[path][1])
    c,scope,platform = value(CONTRACT),value(SCOPE),value(PLATFORM)
    vector = o['complete_owner_fit_vector']
    assert [r['owner_id'] for r in vector]==OWNERS
    owner_checks,inv_checks,nulls,directions = [],[],[],{}
    for i,row in enumerate(vector,1):
        owner = row['owner_id']
        path = row['artifact']['path']
        source = value(path)
        review = value(row['latest_review']['path'])
        assert row['artifact']==o['all11_owner_artifact_sha256'][owner]==dict(path=owner_path(owner),sha256=o['input_pins'][path])
        assert row['latest_review']['path']==review_path(i)
        assert row['latest_review']['sha256']==o['input_pins'][row['latest_review']['path']]
        bound = source['verified_upper_bytes_and_derivation']
        fit = source['bound_fit_not_just_partial_payload']
        assert bound['verified_upper_bytes'] is None and bound['complete_derivation'] is None and not bound['verified']
        assert row['bound_record_sha256']==digest(bound) and row['fit_record_sha256']==digest(fit)
        assert row['latest_review_acceptance_sha256']==digest(review['acceptance'])
        assert not review['acceptance']['accepted_as_complete_'+owner+'_proof']
        assert row['fits'] is None and row['slack_bytes'] is None and not row['owner_proof_verified']
        assert row['metric']==c['heap']['owner_budgets'][i-1]['metric']
        assert row['candidate_budget_bytes']==source['candidate_budget_bytes']==c['heap']['owner_budgets'][i-1]['candidate_budget_bytes']
        owner_checks.append(dict(owner_id=owner,artifact=row['artifact'],review=row['latest_review'],
            vector_row_sha256=digest(row),bound_record_sha256=digest(bound),fit_record_sha256=digest(fit),
            complete_bound_missing=True,documentary_review_not_resource_acceptance=True))
        for n,req in enumerate(source['complete_live_allocation_inventory']['required_classes']):
            assert not req['verified']
            for key in ['cardinality_upper','size_upper_bytes','maximum_live_upper_bytes','lifetime_derivation']:
                assert req[key] is None
                nulls.append(dict(owner_id=owner,artifact_path=path,
                    json_pointer='/complete_live_allocation_inventory/required_classes/'+str(n)+'/'+key))
            inv_checks.append(dict(owner_id=owner,requirement_id=req['id'],record_sha256=digest(req)))
        for boundary in source['overlap_alias_original_and_rejected_prefix_treatment']['boundary_requirements']:
            assert not boundary['resolved']
            directions[(owner,boundary['other_owner'])]=boundary
    pairs = o['overlap_metric_process_review']['owner_pairs']
    assert len(pairs)==55 and len(directions)==110
    seen = set()
    pair_checks = []
    for pair in pairs:
        left,right = pair['owners']
        assert OWNERS.index(left)<OWNERS.index(right) and (left,right) not in seen
        seen.add((left,right))
        assert not pair['resolved']
        for side,other in [(left,right),(right,left)]:
            record = next(r for r in pair['directions'] if r['owner_id']==side and r['other_owner']==other)
            original = directions[(side,other)]
            assert record['record_sha256']==digest(original) and not record['resolved']
            assert record['required_treatment']==original.get('required_treatment',original.get('required_reconciliation'))
        pair_checks.append(dict(owners=[left,right],record_sha256=digest(pair),both_directions_unresolved=True))
    assert len(inv_checks)==132 and len(nulls)==528
    candidate_sum = sum(r['candidate_budget_bytes'] for r in vector[:10])
    assert candidate_sum==10938744832 and candidate_sum+872415232==11811160064
    assert 11811160064+1073741824==12884901888
    requested = o['requested_sum_plus_832MiB_reserve']
    committed = o['H11_overhead_and_committed_sum']
    assert requested['verified_complete_requested_sum_bytes'] is None and requested['verified_requested_sum_plus_reserve_bytes'] is None
    assert committed['verified_complete_H11_upper_bytes'] is None and committed['verified_complete_committed_upper_bytes'] is None
    assert not o['available_capacity_and_process_scope_match']['actual_runtime_capacity_process_scope_match_verified']
    available = platform['available_worker_requested_and_committed_heap']
    assert not available['verified'] and available['available_requested_heap_bytes'] is None and available['available_committed_heap_bytes'] is None
    assert available['worker_metric_definitions']==scope['requested_committed_metrics']
    assert not value(RUNTIME)['acceptance']['accepted_as_runtime_identity']
    rejected = o['all_missing_terms_rejected']
    assert rejected['memory_closure_halted'] and rejected['missing_complete_owner_bounds']==11
    assert rejected['partial_model_values_not_summed'] and len(rejected['rejected_partial_substitutes'])==11
    ledger = o['zero_allocation_ledger']
    assert ledger['reserve_accounting']==c['reserve_accounting']
    assert all(x==0 for x in ledger['heap_reserve_allocation_bytes'].values())
    assert not ledger['resources_reserved'] and not ledger['product_quotas_changed']
    return dict(preparation_commit=o['base_commit'],published_commit=REVIEW_BASE,
        P05_published_blob_oid=oid,P05_sha256=sha(OUT),input_pin_checks=checks,
        owner_checks=owner_checks,inventory_record_checks=inv_checks,unknown_inventory_values=nulls,
        pair_checks=pair_checks,unresolved_directed_boundary_records=len(directions),
        candidate_arithmetic=dict(requested_owner_budget_sum_bytes=candidate_sum,
            unassigned_requested_reserve_bytes=872415232,requested_candidate_bytes=11811160064,
            H11_candidate_bytes=1073741824,committed_candidate_bytes=12884901888,
            verified_requested_sum_bytes=None,verified_H11_upper_bytes=None,verified_committed_sum_bytes=None,
            candidate_values_not_demand_slack_or_capacity=True),
        capacity_record_sha256=digest(available),zero_ledger_sha256=digest(ledger),
        dependency_record_sha256=digest(o['dependencies']),missing_terms_record_sha256=digest(rejected),
        required_field_record_sha256={field:digest(o[field]) for field in next(t for t in value(PLAN)['tasks'] if t['id']=='P05')['required_specific_fields']},
        no_complete_memory_capacity_or_independent_acceptance_proof=True)


def main():
    validate_preparation()
    o,z,r,seal = rd(OUT),rd(RECON),rd(NEW_REVIEW),rd(NEW_SEAL)
    prior = rd(SEAL)
    preserved = {**prior['preserved_published283'],**prior['artifacts'],SEAL:sha(SEAL)}
    expected = {NEW_REVIEW,RECON,NEW_AUDIT,NEW_SEAL,NEW_DESIGN}
    assert len(preserved)==288 and seal['preserved_published288']==preserved
    assert set(seal['artifacts'])|{NEW_SEAL}==expected
    for pins in [preserved,seal['artifacts'],z['input_pins'],r['input_pins']]:
        for path,h in pins.items():
            assert sha(path)==h,path
    assert set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    if git('rev-parse','HEAD')!=REVIEW_BASE:
        assert not git('diff','HEAD','--name-only')
    assert r['base_commit']==z['base_commit']==seal['base_commit']==REVIEW_BASE
    assert r['date']==z['date']==seal['date']=='2026-11-15'
    assert r['schema']=='d5.i162-p05-documentary-review.v1' and z['schema']=='d5.i162-p05-source-reconstruction.v1'
    assert seal['schema']=='d5.i162-integrity.v1' and z['reconstruction']==reconstruct()
    pins = {**o['input_pins'],OUT:sha(OUT),REVIEW:sha(REVIEW),SEAL:sha(SEAL),AUDIT:sha(AUDIT)}
    assert z['input_pins']==pins and r['input_pins']=={**pins,RECON:sha(RECON)}
    assert r['P05']==dict(path=OUT,sha256=sha(OUT),bytes_preserved=True)
    assert r['source_reconstruction']==dict(path=RECON,sha256=sha(RECON)) and r['plan_binding']==o['plan_binding']
    assert r['status']=='REVIEW_COMPLETE_P05_DOSSIER_CONFORMANT_MEMORY_CLOSURE_REJECTED_NO_ADMISSION'
    assert r['documentary_dossier_conformance'] and not r['P05_change_required'] and r['blocking_dossier_defects']==[]
    reviewer = r['reviewer']
    assert reviewer['same_assistant_as_preparer'] and reviewer['methodologically_separate_reconstruction']
    assert not reviewer['actor_independence'] and not reviewer['organizational_independence'] and not reviewer['runtime_custodian_authority']
    assert [x['id'] for x in r['checks']]==['R%02d'%i for i in range(1,16)]
    for check in r['checks']:
        assert check['result']=='CONFORMANT_DOCUMENTARY_INSUFFICIENCY_JUDGMENT' and check['basis'] and not check['resource_obligation_closed']
    assert r['field_disposition']==[dict(field=x['field'],inherited_result=x['result'],I162_result=x['result'],
        record_sha256=digest(o[x['field']]),resource_obligation_closed=False) for x in o['field_assessment']]
    assert r['E02_criterion_disposition']==[dict(id=x['id'],inherited_result=x['I161_result'],I162_result=x['I161_result'],closed=False) for x in o['E02_criterion_disposition']]
    assert r['acceptance']==dict(review_completed=True,insufficiency_judgment_confirmed=True,
        accepted_as_complete_heap_rollup=False,independent_acceptance=False,independent_reviewer_identity=None,
        requested_sum_verified=False,H11_overhead_verified=False,committed_sum_verified=False,capacity_attested=False,
        E02_closed=False,E01_E05_closed=False,resource_obligations_closed=0)
    assert r['counts']==dict(input_pins_reconstructed=212,owner_artifacts=11,latest_owner_reviews=11,
        missing_complete_owner_bounds=11,inventory_requirement_records=132,unknown_inventory_values=528,
        unresolved_owner_pairs=55,unresolved_directed_boundaries=110,formal_dependencies=14,
        required_fields=7,documentary_or_rejection_policy_fields=3,insufficient_fields=4,review_checks=15,other_unproduced_packages=5)
    assert all(r[k] is None for k in ['verified_requested_sum_bytes','verified_H11_overhead_upper_bytes','verified_committed_sum_bytes','fits','slack_bytes'])
    assert r['other_packages_started']==0 and r['pending_P01_P02_P03_not_bypassed'] and len(r['limitations'])>=10
    assert r['decision']==o['decision'] and r['E06']==o['E06'] and r['git_publication']['commit_and_push_all_requested']
    assert set(r['work_unit']['rollback_files'])==expected and r['work_unit']['runtime_harness'].startswith('N/A:')
    assert r['work_unit']['verification_command']=='python3 docs/validation/D5-I162-audit.py' and r['work_unit']['expected_result']=='PASS_STATIC_SOURCE_ONLY'
    assert seal['source_only'] and seal['documentary_dossier_conformance']
    assert not any(seal[k] for k in ['heap_rollup_verified','independent_acceptance','product_or_components_executed','quotas_changed','proposal_enabled','D5_closed'])
    assert seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I162',package='P05',documentary_dossier_conformance=True,
        accepted_as_complete_heap_rollup=False,independent_acceptance=False,Git_input_pins_checked=212,
        missing_complete_owner_bounds=11,unknown_inventory_values=528,unresolved_owner_pairs=55,
        requested_sum_bytes=None,H11_upper_bytes=None,committed_sum_bytes=None,capacity_attested=False,
        prior_published_files_preserved=288,new_files=5,product_or_components_executed=0,quotas_changed=False,
        resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
