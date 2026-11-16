#!/usr/bin/env python3
"""I169 documentary packaging audit. Git/JSON/AST only; no target execution."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'd979f5ab7071a6f9a22c6ff93406eaa7b46c6492'
OUT = P+'D5-PFC126-03-RESOURCE-BUNDLE-BINDING-REVIEW.json'
REVIEW = P+'D5-I169-P09-preparation-review.json'
AUDIT = P+'D5-I169-audit.py'
SEAL = P+'D5-I169-integrity.json'
DESIGN = 'docs/design/D5-I169-P09-RESOURCE-BUNDLE-BINDING.md'
PLAN = P+'D5-I132-E01-E05-evidence-plan.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
PHASE = P+'D5-PFC126-03-E05-PHASE-BOUNDS.json'
SCOPE = P+'D5-PFC126-03-RESOURCE-SCOPE.json'
RUNTIME = P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
PLATFORM = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
BINDING = P+'D5-I122-binding-review.json'
REGISTRY = P+'D5-I122-CAPTURE-REGISTRY.json'
CERT = P+'D5-I122-CAPACITY-CERTIFICATE.json'
CAPACITY = P+'D5-I122-CAPACITY-CONTRACT.json'
MANIFEST = P+'D5-I122-COMPONENTS-MANIFEST.json'
OLD_SEAL = P+'D5-I168-integrity.json'
JOINT = 'testing/prospective_capture_joint_i122/capture.py'
READER = 'testing/prospective_capture/capture.py'
WORKER = 'testing/prospective_capture_joint_i122/worker.py'
FILES = {OUT,REVIEW,AUDIT,SEAL,DESIGN}
MUTABLE = {REGISTRY,CERT,CAPACITY,MANIFEST}


def rd(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def size(path):return len((ROOT/path).read_bytes())
def enc(value):return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(path):return dict(path=path,sha256=sha(path))


def selection():
    extras=[PHASE,P+'D5-I167-P08-preparation-review.json',P+'D5-I167-audit.py',P+'D5-I167-integrity.json',
        P+'D5-I168-P08-documentary-review.json',P+'D5-I168-P08-source-reconstruction.json',P+'D5-I168-audit.py',OLD_SEAL]
    return {**rd(PHASE)['input_pins'],**{p:sha(p) for p in extras}}


def inputs():return {**rd(BINDING)['current_known_input_pins'],**selection()}


def check_git_inputs():
    pins=inputs();request=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    for path,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',path
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(path),path


def source_evidence():
    specs=[(JOINT,'PhaseBytes.read'),(JOINT,'InputPlan.before'),(JOINT,'InputPlan.after'),(JOINT,'InputPlan.finish'),
        (JOINT,'checked_registry'),(JOINT,'require_admission'),(JOINT,'launch'),(READER,'Reader.read'),(READER,'Reader.finish'),(WORKER,'main')]
    trees={p:ast.parse((ROOT/p).read_text()) for p,_ in specs}
    anchors=[]
    for path,symbol in specs:
        node=trees[path]
        for part in symbol.split('.'):
            found=[n for n in ast.iter_child_nodes(node) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==part]
            assert len(found)==1,symbol
            node=found[0]
        anchors.append(dict(path=path,symbol=symbol,sha256=sha(path),line=node.lineno,end_line=node.end_lineno,
            AST_sha256=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()))
    updates=[n for n in ast.walk(trees[JOINT]) if isinstance(n,ast.Call) and ast.unparse(n.func)=='LIMITS.update']
    assert len(updates)==1;limits=ast.literal_eval(updates[0].args[0])
    expected={'file_bytes':16777216,'unique_bytes':134217728,'read_bytes':268435456,'paths':4096,
        'context_bytes':12582912,'launch_bytes':12582912,'evidence_unique_bytes':134217728,'evidence_read_bytes':297799680}
    assert all(limits[k]==v for k,v in expected.items())
    text=ast.unparse(trees[JOINT]);reader=ast.unparse(trees[READER])
    assert "AUTHORITY not in a['capture_inputs']" in text and "required == set(a['capture_inputs'])" in text
    assert "for name in self.view.bodies:" in text and 'self.reader.finish()' in text
    assert "for name in tuple(self.files):" in reader and 'self.read(name)' in reader
    assert 'return self.bodies[name]' in text
    return dict(anchors=anchors,limits=expected,syntax_only=True,
        three_pass_extension_condition='Only if every selected member is declared in one InputPlan authority manifest and the same physical Reader completes before/after/finish; fresh target checks are extra, not removed.',
        PhaseBytes_not_fresh_Reader=True,exact_current_input_set_rejects_direct_append=True,no_target_import_execution_or_sampling=True)


def binding_fields():
    b=rd(BINDING);chosen=selection();baseline=b['current_known_input_pins'];reg=rd(REGISTRY)['overrides'];cert=rd(CERT);manifest=rd(MANIFEST)
    assert set(baseline)==set(reg['required_prior_inputs'])|set(reg['implementation_sources'])|MUTABLE
    assert sum(size(p) for p in baseline)==b['known_union_bytes']==87104500
    assert cert['status']=='IMPLEMENTED_NOT_ADMITTED' and cert['component_validation']=='NOT_RUN'
    assert cert['source_revision']==manifest['source_revision']==reg['source_revision']=='I122-CANDIDATE-01'
    assert cert['source_bindings']=={p:baseline[p] for p in set(reg['required_prior_inputs'])|set(reg['implementation_sources'])|{REGISTRY,CAPACITY}}
    assert manifest['source_bindings']=={p:baseline[p] for p in set(reg['implementation_sources'])|{REGISTRY,CAPACITY,CERT}}
    extra=set(chosen)-set(baseline);fixed=set(baseline)-MUTABLE;known_fixed=fixed|extra
    extra_bytes=sum(size(p) for p in extra);fixed_bytes=sum(size(p) for p in fixed);lower=3*(fixed_bytes+extra_bytes)
    allpaths=set(baseline)|set(chosen)
    ledger=[dict(path=p,sha256=inputs()[p],bytes=size(p),in_frozen_resource_selection=p in chosen,
        in_original_known_graph=p in baseline,excluded_from_future_lower_bound_as_mutable=p in MUTABLE) for p in sorted(allpaths)]
    task_outputs={t['planned_output']:t['id'] for t in rd(PLAN)['tasks']}
    roles=[]
    for p,h in sorted(chosen.items()):
        role=('I132_'+task_outputs[p]+'_prepared_output' if p in task_outputs else
            'source_reference_not_execution_proof' if p.endswith('.py') and not p.startswith(P) else
            'documentary_integrity_record' if 'integrity' in p else 'supporting_source_or_documentary_reference')
        roles.append(dict(path=p,sha256=h,bytes=size(p),role=role,accepted_as_resource_proof=False))
    reference=rd(P+'D5-I127-runtime-reference-manifest.json')
    externals=[dict(role='historical_interpreter',**reference['interpreter'])]
    for key in ['stdlib_file_references','extension_references']:
        externals.extend(dict(role='historical_'+key,**x) for x in reference[key])
    model=b['top_metadata_model'];assert len(enc(model['value']))==model['encoded_bytes']==483286
    maps=model['value'];assert maps['capture_inputs_before'] and maps['capture_inputs_after']
    assert all(p not in maps['capture_inputs_before'] and p not in maps['capture_inputs_after'] for p in extra)
    delta=sum(len(enc({p:chosen[p]}))-1 for p in extra)
    top_projection=model['encoded_bytes']+2*delta
    limits=source_evidence()['limits']
    per_reader=[]
    for reader in ['coordinator_input_Reader','worker_input_Reader']:
        per_reader.append(dict(reader=reader,distinct_from_other_Reader=True,
            frozen_fixed_known_paths=len(known_fixed),frozen_fixed_known_unique_bytes=fixed_bytes+extra_bytes,
            known_fixed_file_max_bytes=max(size(p) for p in known_fixed),
            file_bytes_limit=limits['file_bytes'],paths_limit=limits['paths'],unique_bytes_limit=limits['unique_bytes'],read_bytes_limit=limits['read_bytes'],
            three_pass_known_fixed_read_lower_bytes=lower,excess_over_read_limit_bytes=lower-limits['read_bytes'],
            conditional_frozen_extension_fits=False,complete_final_graph_fit_verified=False,
            final_unique_bytes=None,final_path_count=None,final_read_bytes=None,
            fresh_target_or_late_reads_not_eliminated=True))
    return dict(
        all_evidence_artifacts_real_hashes_and_roles=dict(selection_rule='Freeze P08 input closure plus its I167 producer and I168 reviewer output/audit/seal records; no new I169 files or future P10.',
            selection_count=len(chosen),artifacts=roles,full_assessed_graph_ledger=ledger,
            all18_prior_plan_outputs_in_selection=all(t['planned_output'] in chosen for t in rd(PLAN)['tasks'] if t['id'] not in ['P09','P10']),
            real_Git_bound_repository_bytes=True,hash_binding_not_external_signature_or_resource_acceptance=True),
        external_attestation_trust_source_and_validity=dict(
            runtime_authority_record=rd(RUNTIME)['producer_authority_signature_and_validity'],
            platform_authority_record=rd(PLATFORM)['producer_authority_signature_and_validity'],
            authenticated_attestation_materials=[],valid_trust_chain_verified=False,signatures_verified=False,validity_verified=False,
            global_absence_claimed=False,external_contacts_made=False),
        external_runtime_binary_references_not_silently_copied_or_called_fresh_reads=dict(
            reference_manifest=pin(P+'D5-I127-runtime-reference-manifest.json'),historical_references=externals,
            paths_opened_or_restatted_now=False,bytes_copied_into_repository=False,included_in_Reader_graph=False,
            current_target_runtime_or_loaded_native_closure_verified=False,not_PhaseBytes_or_fresh_Reader_observations=True),
        source_contract_platform_manifest_consistency=dict(
            candidate_contract=pin(CONTRACT),candidate_contract_id=rd(CONTRACT)['contract_id'],
            fixed_I122_registry=pin(REGISTRY),capacity_contract=pin(CAPACITY),certificate=pin(CERT),component_manifest=pin(MANIFEST),
            source_revision='I122-CANDIDATE-01',numeric_candidates_match=cert['numeric_candidates']==reg['limits']==rd(CAPACITY)['numeric_candidates'],
            certificate_source_bindings_verified_as_documentary_bytes=True,component_manifest_source_bindings_verified_as_documentary_bytes=True,
            current_certificate_status=cert['status'],component_validation=cert['component_validation'],
            exact_current_admission_input_set_count=len(baseline)+3,
            direct_append_compatible_with_current_registry_and_required_set=False,
            future_registry_certificate_manifest_authority_pins_need_review=True,
            PFC126_document_not_current_admission_capacity_contract=True,external_platform_target_consistency_verified=False),
        future_input_graph_and_real_bytes_sizes=dict(
            proposal_kind='Conditional retained-input extension cost assessment, not an installed or complete future admission graph.',
            assumptions=['Retain the490 original known paths except allow four mutable registry/contract/certificate/manifest bodies to change.',
                'Declare all244 frozen resource-selection paths, including146 additional distinct members, in one future authority manifest.',
                'Keep the existing InputPlan before/after/finish physical Reader schedule and unchanged quota values.',
                'Do not prune, alias or replace any other frozen member; future final metadata and additional reads add nonnegative cost.'],
            original_known_count=len(baseline),original_known_bytes=b['known_union_bytes'],
            mutable_paths_excluded_from_lower_bound=sorted(MUTABLE),retained_fixed_count=len(fixed),retained_fixed_bytes=fixed_bytes,
            additional_frozen_count=len(extra),additional_frozen_bytes=extra_bytes,
            additional_members=[dict(path=p,sha256=chosen[p],bytes=size(p)) for p in sorted(extra)],
            frozen_union_current_paths=len(allpaths),retained_fixed_plus_extension_paths=len(known_fixed),
            retained_fixed_plus_extension_bytes=fixed_bytes+extra_bytes,
            pass_count_under_stated_graph=3,known_fixed_read_lower_bytes=lower,
            future_authority_component_raw_result_seal_final_bytes_known=False,
            final_rewritten_registry_certificate_manifest_sizes=None,final_P09_P10_or_new_external_evidence_bytes=None,
            complete_final_future_graph_or_authority_created=False,
            conditional_nonfit_proved_for_this_retained_extension=True,
            actual_runtime_CPU_heap_service_infeasibility_proved=False,all_alternative_future_packagings_rejected=False),
        per_Reader_unique_read_file_path_limits_and_top_metadata_impacts=dict(
            input_Reader_accounts=per_reader,Readers_not_pooled_or_reset=True,
            known_fixed_files_under_file_cap=all(size(p)<=limits['file_bytes'] for p in known_fixed),
            known_fixed_unique_lower_below_cap=fixed_bytes+extra_bytes<=limits['unique_bytes'],
            known_fixed_path_lower_below_cap=len(known_fixed)<=limits['paths'],
            unique_path_lower_checks_not_complete_fit=True,
            historical_worker_upper=b['read_schedule'],historical_margin_not_transferred_to_new_graph=True,
            evidence_Reader_separate=dict(unique_bytes_limit=limits['evidence_unique_bytes'],read_bytes_limit=limits['evidence_read_bytes'],
                resource_sources_not_output_packet_members=True,unchanged_output_envelopes_not_reproved=True),
            top_metadata_impact=dict(historical_width_model=pin(BINDING),historical_width_model_bytes=483286,
                historical_allowance_bytes=model['allowance'],real_new_pin_entry_delta_per_map_bytes=delta,
                maps_affected=['capture_inputs_before','capture_inputs_after'],two_map_delta_bytes=2*delta,
                same_other_fields_conditional_width_bytes=top_projection,conditional_width_margin_bytes=model['allowance']-top_projection,
                historical_placeholder_model_not_real_evidence=True,new_placeholder_hashes_generated=False,
                final_top_metadata_or_context_bytes=None,final_context_launch_or_package_fit_verified=False,
                new_authority_hash_pin_widths_rewrites_external_material_and_P09_P10_require_recalculation=True)),
        self_pin_cycles_and_historical_authority_reuse_rejected=dict(
            own_P09_and_later_P10_excluded_from_frozen_selection=True,own_hash_not_recorded_in_own_body=True,
            integrity_seal_does_not_pin_itself=True,
            allowed_direction='Frozen inputs -> P09 -> preparation review/design/audit artifacts -> integrity seal; no reverse byte-hash pin.',
            current_authority_self_pin_forbidden_by_source=True,source_certificate_excludes_its_own_hash=True,
            future_dependency_cycle_check_and_topological_pin_order_required=True,
            historical_I71_I77_I86_I89_I92_authorities_not_reused=True,
            no_old_INVALID_CAPTURE_or_component_NOT_RUN_as_new_evidence=True),
        no_quota_change_or_rebind_performed=dict(capture_inputs_modified=False,registry_certificate_manifest_modified=False,
            authority_created=False,capture_destination_created=False,product_quotas_changed=False,source_modified=False,
            runtime_or_component_execution=False,external_binaries_read_or_copied=False,reserves_transferred=False,
            proposal_enabled=False,documentary_publication_not_admission=True))


def build_output():
    task=next(t for t in rd(PLAN)['tasks'] if t['id']=='P09');fields=binding_fields()
    assert list(fields)==task['required_specific_fields']
    outputs={t['id']:t['planned_output'] for t in rd(PLAN)['tasks']}
    decision=dict(rd(PHASE)['decision']);decision['resource_bundle_binding_verified']=False
    return dict(schema=task['output_schema'],package_id='P09',increment='I169',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        status='PREPARED_PROVENANCE_INSUFFICIENT_RETAINED_EXTENSION_READ_OVERBUDGET_NOT_ADMITTED',
        evidence_kind='STATIC_PACKAGING_HASH_BYTE_GRAPH_REVIEW_NOT_ATTESTATION_REBIND_OR_EXECUTION_PROOF',
        plan_binding=dict(**pin(PLAN),task_record_canonical_sha256=digest(task)),candidate_binding=rd(PHASE)['candidate_binding'],input_pins=inputs(),
        dependencies=[dict(id=i,**pin(outputs[i]),accepted_for_resource_closure=False) for i in task['depends_on']],
        source_evidence=source_evidence(),**fields,
        field_assessment=[dict(field=f,result='INSUFFICIENT_FOR_COMPLETE_BUNDLE_ACCEPTANCE',
            documentary_preparation_present=True,resource_obligation_closed=False) for f in fields],
        acceptance=dict(rule=task['acceptance'],rejection_rule=task['rejection'],preparation_complete=True,
            accepted_as_complete_resource_bundle=False,future_actual_input_graph_fit_verified=False,
            external_provenance_trust_and_resource_assumptions_verified=False,resource_obligations_closed=0),
        early_stop=dict(retained_extension_over_existing_read_budget=True,external_evidence_block=True,
            quota_change_rebind_or_source_repair_authorized=False,all_future_packagings_impossible=False),
        provenance=dict(producer='Codex assistant preparing I169 in same chat as preceding packages',planned_author_role=task['responsible_role'],
            planned_review_role=task['review_role'],independent_reviewer_identity=None,independent_acceptance=False,custodian_acceptance=False),
        non_execution_and_zero_transfer_policy=rd(SCOPE)['non_execution_and_zero_transfer_policy'],E06=rd(PHASE)['E06'],decision=decision)


def build_review():
    o=rd(OUT);progress=[]
    for t in rd(PLAN)['tasks']:
        exists=(ROOT/t['planned_output']).exists()
        progress.append(dict(package_id=t['id'],path=t['planned_output'],output_created=exists,
            sha256=sha(t['planned_output']) if exists else None,accepted_for_resource_closure=False))
    return dict(schema='d5.i169-p09-preparation-review.v1',increment='I169',date='2026-11-16',base_commit=BASE,
        status='P09_PREPARED_NOT_ACCEPTED_RETAINED_EXTENSION_NONFIT_AND_PROVENANCE_GAPS',input_pins={**inputs(),OUT:sha(OUT)},output=pin(OUT),
        counts=dict(required_fields=8,dependencies=6,frozen_resource_members=244,original_known_members=490,
            extra_members=146,mutable_members_excluded=4,retained_fixed_plus_extension_members=632,input_pins=len(inputs()),
            prior_plan_outputs=18,source_anchors=10,historical_external_references=18,remaining_unproduced_packages=1),
        preparation_checks=dict(all8_fields_present=True,real_Git_bytes_and_hashes_bound=True,retained_graph_three_pass_premises_explicit=True,
            mutable_metadata_excluded_from_lower_bound=True,no_placeholder_attestation_or_new_hashes=True,
            per_Reader_accounts_not_pooled=True,conditional_top_metadata_not_final_fit=True,no_rebind_or_quota_mutation=True),
        package_progress=progress,acceptance=o['acceptance'],decision=o['decision'],E06=o['E06'],
        independent_review=dict(accepted=False,reviewer_identity=None),
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I169-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary hash/byte/AST packaging review only; product and component execution prohibited.',
            over400_lines=True,reason='Real artifact ledger, graph/Reader cost proof and self-contained documentary audit; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_does_not_admit_candidate=True))


def main():
    assert rd(OUT)==build_output() and rd(REVIEW)==build_review();check_git_inputs()
    prior=rd(OLD_SEAL);preserved={**prior['preserved_published318'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)};seal=rd(SEAL)
    assert len(preserved)==323 and seal['preserved_published323']==preserved
    assert seal['schema']=='d5.i169-integrity.v1' and seal['base_commit']==BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert sha(CONTRACT)=='e7a873a2aea8648d225f2272854e0b15c3f21de5826df06f16dfb6e45aa54576'
    assert len(selection())==244 and len(inputs())==636 and not FILES&set(inputs())
    o=rd(OUT);g=o['future_input_graph_and_real_bytes_sizes'];impact=o['per_Reader_unique_read_file_path_limits_and_top_metadata_impacts']
    assert g['additional_frozen_bytes']==8963747 and g['retained_fixed_bytes']==86983017
    assert g['known_fixed_read_lower_bytes']==3*(86983017+8963747)==287840292>268435456
    assert all(r['excess_over_read_limit_bytes']==19404836 for r in impact['input_Reader_accounts'])
    top=impact['top_metadata_impact'];assert top['same_other_fields_conditional_width_bytes']==517028 and top['conditional_width_margin_bytes']==7260
    assert all(x['accepted_as_resource_proof'] is False for x in o['all_evidence_artifacts_real_hashes_and_roles']['artifacts'])
    for t in rd(PLAN)['tasks']:
        if t['id']=='P10':assert not (ROOT/t['planned_output']).exists()
    for p in [P+'D5-JOINT-capture-authorization.json',P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists()
    for k in ['resource_bundle_verified','independent_acceptance','product_or_components_executed','quotas_changed','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    changes=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changes==FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I169',package='P09',preparation_complete=True,accepted_as_resource_bundle=False,
        frozen_resource_members=244,additional_members=146,additional_bytes=8963747,conditional_fixed_graph_read_lower_bytes=287840292,
        unchanged_read_limit=268435456,prior_published_files_preserved=323,new_files=5,product_or_components_executed=0,quotas_changed=False,
        resource_obligations_closed=0,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':main()
