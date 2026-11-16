#!/usr/bin/env python3
"""I174 documentary packaging review; Git/JSON/AST/widths only, no target execution."""
import ast
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='f7e5b70a424100b9e0c3dff6369cb2dd225587f8'
INDEX=P+'D5-PFC126-03-RESOURCE-ADMISSION-INDEX-CANDIDATE.json'
OUT=P+'D5-I173-READER-PACKAGING-PROPOSAL.json'
REVIEW=P+'D5-I173-preparation-review.json'
AUDIT=P+'D5-I173-audit.py'
SEAL=P+'D5-I173-integrity.json'
DESIGN='docs/design/D5-I173-READER-PACKAGING-PROPOSAL.md'
PLAN=P+'D5-I132-E01-E05-evidence-plan.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
SCOPE=P+'D5-PFC126-03-RESOURCE-SCOPE.json'
HEAP=P+'D5-PFC126-03-E02-HEAP-ROLLUP.json'
P10=P+'D5-PFC126-03-E01-E05-CLOSURE-REVIEW.json'
P09=P+'D5-PFC126-03-RESOURCE-BUNDLE-BINDING-REVIEW.json'
BIND=P+'D5-I122-binding-review.json'
REG=P+'D5-I122-CAPTURE-REGISTRY.json'
CERT=P+'D5-I122-CAPACITY-CERTIFICATE.json'
CAP=P+'D5-I122-CAPACITY-CONTRACT.json'
MAN=P+'D5-I122-COMPONENTS-MANIFEST.json'
AUTH=P+'D5-JOINT-capture-authorization.json'
RAW=P+'D5-JOINT-tests-raw.json'
RESULT=P+'D5-JOINT-results.json'
COMPSEAL=P+'D5-JOINT-integrity.json'
OLD_SEAL=P+'D5-I172-integrity.json'
JOINT='testing/prospective_capture_joint_i122/capture.py'
READER='testing/prospective_capture/capture.py'
FILES={INDEX,OUT,REVIEW,AUDIT,SEAL,DESIGN}
# Reviewable serialized-size envelopes, NOT edits to product quotas/configuration.
ENVELOPES={REG:65536,CERT:65536,CAP:8192,MAN:4096,INDEX:32768,AUTH:65536,RAW:512,RESULT:768,COMPSEAL:2048}


def rd(p):return json.loads((ROOT/p).read_text())
def enc(x):return json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def size(p):return len((ROOT/p).read_bytes())
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pin(p):return dict(path=p,sha256=sha(p))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def inputs():
    extras=[P+'D5-I172-P10-documentary-review.json',P+'D5-I172-P10-source-reconstruction.json',P+'D5-I172-audit.py',OLD_SEAL]
    return {**rd(P+'D5-I172-P10-source-reconstruction.json')['input_pins'],**{p:sha(p) for p in extras}}


def check_git_inputs():
    pins=inputs();req=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p


def build_index():
    latest={id:P+f'D5-I{n}-{id}-documentary-review.json' for id,n in [('P01',134),('P02',136),('P03',138),('P05',162),('P06',164),('P07',166),('P08',168),('P09',170),('P10',172)]}
    latest.update({'P04-'+x['owner_id']:x['latest_review']['path'] for x in rd(HEAP)['complete_owner_fit_vector']})
    artifacts=[]
    for t in rd(PLAN)['tasks']:
        artifacts.append(dict(package_id=t['id'],**pin(t['planned_output']),bytes=size(t['planned_output']),
            documentary_review=pin(latest[t['id']]),resource_verified=False))
    return dict(schema='d5.pfc126-03.resource-admission-index-candidate.v1',increment='I173',date='2026-11-16',
        status='CANDIDATE_NEGATIVE_NOT_ADMITTED',candidate_contract=pin(CONTRACT),source_revision='I122-CANDIDATE-01',
        implementation_sources=rd(REG)['overrides']['implementation_sources'],capacity_contract=pin(CAP),
        backing_material_commit=BASE,backing_material_pin_count=len(inputs()),backing_material_root_sha256=digest(inputs()),
        root_encoding='SHA256 of UTF8 canonical JSON path-to-SHA map; sorted keys, compact separators, ensure_ascii=False.',
        backing_manifest=pin(P+'D5-I172-P10-source-reconstruction.json'),latest_resource_review=pin(P+'D5-I172-P10-documentary-review.json'),
        latest_integrity_record=pin(OLD_SEAL),artifacts=artifacts,
        reference_semantics='Reviewer material only. Input Reader hashes this index as opaque bytes; it does not follow references, verify signatures or attest resource truth.',
        signed_resource_acceptance_record=None,independent_acceptance=False,E01_E05_verified=False,E06_satisfied=False,
        proposal_enabled=False,capture_authority=False,
        cycle_rule='A future detached approval signs prior evidence-root/candidate/source scope, not future registry/certificate/authority hashes. Approval precedes successor index; certificate and authority follow. This negative index is not promotable by its existence.')


def source_evidence():
    trees={p:ast.parse((ROOT/p).read_text()) for p in [JOINT,READER]}
    def node(path,name):
        n=trees[path]
        for part in name.split('.'):
            matches=[x for x in ast.iter_child_nodes(n) if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name==part]
            assert len(matches)==1; n=matches[0]
        return n
    specs=[(JOINT,'InputPlan.before'),(JOINT,'InputPlan.after'),(JOINT,'InputPlan.finish'),(JOINT,'PhaseBytes.read'),
        (JOINT,'checked_registry'),(JOINT,'require_admission'),(JOINT,'checked_component_metadata'),(READER,'Reader.read'),(READER,'Reader.finish')]
    rows=[]
    for path,name in specs:
        n=node(path,name);rows.append(dict(path=path,symbol=name,sha256=sha(path),line=n.lineno,end_line=n.end_lineno,
            AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
    text=ast.unparse(trees[JOINT]);reader=ast.unparse(trees[READER])
    assert "required == set(a['capture_inputs'])" in text and "AUTHORITY not in a['capture_inputs']" in text
    assert 'for mapping in (reg[\'implementation_sources\'], reg[\'required_prior_inputs\']):' in text
    assert 'c.sha(snapshot.read(name))' in text and 'return self.bodies[name]' in text
    assert 'self.reader.finish()' in text and 'for name in self.view.bodies:' in text
    assert 'for name in tuple(self.files):' in reader and 'self.total += st.st_size' in reader
    update=next(n for n in ast.walk(trees[JOINT]) if isinstance(n,ast.Call) and ast.unparse(n.func)=='LIMITS.update')
    limits=ast.literal_eval(update.args[0]);assert (limits['file_bytes'],limits['unique_bytes'],limits['read_bytes'],limits['paths'])==(16777216,134217728,268435456,4096)
    return dict(anchors=rows,unchanged_input_limits={k:limits[k] for k in ['file_bytes','unique_bytes','read_bytes','paths']},
        new_index_is_only_extra_manifest_member=True,index_references_not_recursively_followed=True,index_semantics_not_validated_by_worker=True,
        pure_schema_checks_use_PhaseBytes_not_fresh_Reader=True,three_pass_schedule_unchanged=True,
        additional_target_fresh_read_schedule_unchanged_condition='No implementation/runner/target/binding/source-path or source_revision change; only append index to required_prior_inputs and corresponding exact metadata pins.',
        no_runtime_or_component_execution=True)


def symbolic_widths():
    # Width algebra only: no invented hashes or fabricated PASS/authority artifacts.
    sw=lambda s:len(enc(s))
    def obj(fields):return 2+sum(sw(k)+1+w for k,w in fields.items())+max(0,len(fields)-1)
    def hash_map(paths):return 2+sum(sw(p)+1+66 for p in paths)+max(0,len(paths)-1)
    old=set(rd(BIND)['current_known_input_pins']);future_manifest=old|{INDEX,RAW,RESULT,COMPSEAL}
    rev=sw('I122-CANDIDATE-01')
    auth=obj(dict(schema=sw('d5.joint-capture-authority.v2'),phase=sw('JOINT_EXPLICITLY_APPROVED'),scopes=len(enc(['P01'])),registry_sha256=66,capture_inputs=hash_map(future_manifest)))+1
    raw=obj(dict(schema=sw('d5.joint-component-raw.v2'),source_revision=rev,status=sw('PASS'),tests_run=2,failures=1,errors=1,
        functional_campaigns_executed=1,product_or_runner_imported=5,forbidden_imports=2,elapsed_milliseconds=6,new_module_count=19,closure=5,D5_closed=5))+1
    result=obj(dict(schema=sw('d5.joint-component-review.v2'),source_revision=rev,status=sw('PASS'),tests_run=2,functional_campaigns_executed=1,
        product_or_runner_imported=5,raw_sha256=66,manifest_sha256=66,decision=sw('ACCEPTED_COMPONENTS_ONLY'),closure=5,D5_closed=5))+1
    seal=obj(dict(schema=sw('d5.joint-component-integrity.v2'),source_revision=rev,artifacts=hash_map([RAW,RESULT,MAN]),source_bindings=hash_map(rd(MAN)['source_bindings'])))+1
    return {AUTH:auth,RAW:raw,RESULT:result,COMPSEAL:seal}


def build_proposal():
    b=rd(BIND);reg=rd(REG)['overrides'];original=set(b['current_known_input_pins']);fixed=original-{REG,CERT,CAP,MAN}
    assert len(fixed)==486 and sum(size(p) for p in fixed)==86983017
    max_unique=sum(size(p) for p in fixed)+sum(ENVELOPES.values())
    widths=symbolic_widths();assert all(widths[p]<=ENVELOPES[p] for p in widths)
    limits=source_evidence()['unchanged_input_limits'];fresh_worker=4852460
    # Charge coordinator the worker's larger inherited fresh bound as conservative overcount.
    max_read=3*max_unique+fresh_worker
    maps_delta=2*(len(enc({INDEX:sha(INDEX)}))-1)
    top=b['top_metadata_model']['encoded_bytes']+maps_delta
    assert size(INDEX)<=ENVELOPES[INDEX]
    old_selection={x['path'] for x in rd(P09)['all_evidence_artifacts_real_hashes_and_roles']['artifacts']}
    changed=old_selection-original
    return dict(schema='d5.i173-reader-packaging-proposal.v1',increment='I173',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal_id='PRP173-INDEX-01',status='CONCRETE_CONDITIONAL_READER_FIT_PROPOSAL_NOT_APPLIED_NOT_ADMITTED',
        subject=rd(P10)['candidate_binding'],input_pins=inputs(),candidate_index=dict(**pin(INDEX),actual_bytes=size(INDEX),max_proposed_serialized_bytes=ENVELOPES[INDEX]),
        structure=dict(retained_historical_required_inputs=len(reg['required_prior_inputs']),retained_implementation_sources=len(reg['implementation_sources']),
            proposed_extra_Input_Reader_paths=[INDEX],resource_proof_references=20,documentary_material_root_sha256=digest(inputs()),
            reviewer_material_outside_Input_Reader_not_discarded=True,old_P09_additional_members=len(changed),
            those_members_not_added_to_future_capture_manifest=True,existing_historical_sources_not_pruned=True,
            reference_hashes_not_resource_acceptance_or_fresh_reads=True),
        future_binding_delta=dict(applied=False,registry_required_prior_inputs_count=[480,481],certificate_source_binding_count=[488,489],
            component_source_binding_count=[9,9],capture_manifest_count=[493,494],union_with_authority_count=[494,495],
            expected_source_schemas_unchanged=True,numeric_candidates_unchanged=True,source_revision_unchanged=True,
            source_edits_required_for_reader_graph=False,exact_rebind_and_binding_impact_review_still_required=True,
            index_not_yet_in_registry_certificate_authority=True,
            semantic_limit='Existing code only hashes the extra index. It neither follows its refs nor proves resource acceptance; an independently accepted exact scoped approval and future source-capacity certificate remain mandatory.'),
        byte_envelopes=dict(purpose='Proposal acceptance envelopes below unchanged file quotas; no new runtime enforcement/quota or reservation.',
            frozen_fixed_count=486,frozen_fixed_bytes=86983017,
            variable_members=[dict(path=p,max_serialized_bytes=n,current_bytes=size(p) if (ROOT/p).exists() else None,
                currently_materialized=p==INDEX or p in {REG,CERT,CAP,MAN}) for p,n in ENVELOPES.items()],
            sum_variable_upper_bytes=sum(ENVELOPES.values()),symbolic_closed_schema_future_widths=widths,
            optional_final_newline_included=True,all_future_final_bodies_must_be_rechecked_against_envelopes=True,
            inherited_directory_listing_stability_and_4096_entry_limit_must_hold=True),
        per_Input_Reader_upper_accounts=[dict(reader=name,unique_upper_bytes=max_unique,path_upper=495,
            file_upper_bytes=max([size(p) for p in fixed]+list(ENVELOPES.values())),
            three_pass_read_upper_bytes=3*max_unique,additional_fresh_read_upper_bytes=fresh_worker,
            total_read_upper_bytes=max_read,unchanged_limits=limits,read_margin_bytes=limits['read_bytes']-max_read,
            unique_margin_bytes=limits['unique_bytes']-max_unique,path_margin=limits['paths']-495,
            finite_envelope_fits=True,conditional_on_declared_same_graph_and_all_envelopes=True)
            for name in ['coordinator_input_Reader','worker_input_Reader']],
        top_metadata=dict(historical_width_model=pin(BIND),historical_model_bytes=483286,
            capture_pin_maps_new_entry_count=1,new_real_index_pin_two_map_delta_bytes=maps_delta,
            conditional_same_other_fields_upper_bytes=top,historical_allowance_bytes=524288,
            conditional_margin_bytes=524288-top,
            no_index_or_backing_bodies_embedded_in_sidecar_context=True,
            materialized_registry_compact_previous_bytes=b['materialized_registry_compact_bytes'],
            materialized_registry_one_pin_delta_bytes=len(enc({INDEX:sha(INDEX)}))-1,
            unchanged_OUTPUT_envelopes_not_reproved=True,final_context_launch_package_binding_review_pending=True,
            historical_width_model_not_measurement_or_capture_evidence=True),
        source_evidence=source_evidence(),
        fit_verdict=dict(P09_retained_extension_excess_removed_by_different_proposed_graph=True,
            conditional_reader_upper_proved=True,actual_final_graph_or_external_evidence_accepted=False,
            independent_packaging_review_obtained=False,resource_obligations_closed=0,resource_truth_not_derived_from_index=True,
            no_claim_this_is_only_possible_packaging=True),
        approval_and_order=dict(current_index_negative_not_a_success_attestation=True,
            required_before_actual_rebind=[
                'Independent resource review and competent custodians supply complete exact-scope E01-E05 evidence; E06 remains separate.',
                'Use separately versioned accepted proof artifacts; do not overwrite or reclassify the retained historical inputs or current negative P01-P10 records.',
                'Review the packaging/binding impact against PFC126/I122 proofs; declare exactly what is reviewed out of band versus physically read.',
                'A detached approval signs prior evidence-root/candidate/source scope, excluding later index/registry/certificate/authority hashes to avoid cycles.',
                'Create a separately reviewed successor index binding that approval and all real final proofs within32768 bytes; never promote this negative candidate by existence.',
                'Finalize exact registry/contract/certificate/manifest pins and authorized component records, then authority last without self-pin; all final bytes must meet these envelopes.',
                'Recompute every physical Reader, metadata/context/package binding and obtain separate packaging/admission acceptance before any capture; no execution permission is supplied here.'],
            no_current_actor_independence_or_authority_claim=True,no_signature_or_component_PASS_created=True),
        unchanged_state=dict(certificate=pin(CERT),certificate_status=rd(CERT)['status'],E01_E05_open=True,E06_NOT_RUN=True,
            source_implementation_changed=False,capture_inputs_rebound=False,registry_or_certificate_or_manifest_changed=False,
            quota_values_changed=False,reserves_transferred=False,active_gate_updated=False,authority_created=False,
            product_or_components_executed=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        decision=rd(P10)['decision'],E06=rd(P10)['E06'])


def build_review():
    o=rd(OUT)
    return dict(schema='d5.i173-packaging-preparation-review.v1',increment='I173',date='2026-11-16',base_commit=BASE,
        status='INDEX_AND_CONDITIONAL_READER_FIT_PROPOSAL_PREPARED_NO_ADMISSION',input_pins={**inputs(),INDEX:sha(INDEX),OUT:sha(OUT)},
        outputs=[pin(INDEX),pin(OUT)],counts=dict(input_pins=len(inputs()),backing_packages=20,old_additional_members=146,
            proposed_extra_input_members=1,future_union_paths=495,source_anchors=9,new_files=6),
        preparation_checks=dict(real_index_and_proof_hashes=True,original480_prior_inputs_retained=True,
            finite_complete_Input_Reader_envelope_fits=True,variable_rebind_bytes_and_future_metadata_bounded=True,
            symbolic_widths_without_fake_hashes_or_PASS_records=True,top_metadata_one_pin_delta_only=True,
            no_hidden_dereference_or_freshness_claim=True,negative_resources_and_E06_preserved=True),
        runtime_harness='N/A: documentary packaging/index/width proposal; no target boundary changed or executed.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I173-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            over400_lines=True,reason='Concrete index, frozen byte graph, explicit binding/envelope conditions and self-contained audit; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_not_admission=True))


def validate_preparation():
    assert (ROOT/INDEX).read_bytes()==enc(build_index())+b'\n'
    assert rd(OUT)==build_proposal() and rd(REVIEW)==build_review();check_git_inputs()
    prior=rd(OLD_SEAL);preserved={**prior['preserved_published338'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)};seal=rd(SEAL)
    assert len(preserved)==343 and seal['preserved_published343']==preserved
    assert seal['schema']=='d5.i173-integrity.v1' and seal['base_commit']==BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert len(inputs())==652 and not FILES&set(inputs())
    o=rd(OUT);idx=rd(INDEX)
    assert len(idx['artifacts'])==20 and all(not x['resource_verified'] for x in idx['artifacts'])
    assert idx['signed_resource_acceptance_record'] is None and not idx['independent_acceptance']
    for row in idx['artifacts']:
        assert row['sha256']==sha(row['path']) and row['bytes']==size(row['path'])
        assert row['documentary_review']['sha256']==sha(row['documentary_review']['path'])
    assert idx['backing_material_root_sha256']==digest(inputs())
    for p in [REG,CERT,CAP,MAN]:assert size(p)<=ENVELOPES[p]
    assert o['byte_envelopes']['sum_variable_upper_bytes']==244992
    for account in o['per_Input_Reader_upper_accounts']:
        assert account['unique_upper_bytes']==87228009 and account['total_read_upper_bytes']==266536487
        assert account['read_margin_bytes']==1898969 and account['finite_envelope_fits']
        lim=account['unchanged_limits']
        assert account['unique_upper_bytes']<=lim['unique_bytes'] and account['file_upper_bytes']<=lim['file_bytes'] and account['path_upper']<=lim['paths']
    assert o['top_metadata']['conditional_same_other_fields_upper_bytes']<524288
    assert sha(CONTRACT)=='e7a873a2aea8648d225f2272854e0b15c3f21de5826df06f16dfb6e45aa54576'
    for p in [AUTH,RAW,RESULT,COMPSEAL,P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json']:assert not (ROOT/p).exists()
    for k in ['resource_closure_verified','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)


REVIEW_BASE='7fece6cee8701a4ef6b2407ef7bdc28168d08579'
NEW_REVIEW=P+'D5-I174-PRP173-documentary-review.json'
RECON=P+'D5-I174-PRP173-source-reconstruction.json'
NEW_AUDIT=P+'D5-I174-audit.py'
NEW_SEAL=P+'D5-I174-integrity.json'
NEW_DESIGN='docs/design/D5-I174-READER-PACKAGING-REVIEW.md'
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


def reconstruct():
    import copy
    pins={**rd(OUT)['input_pins'],**{p:sha(p) for p in FILES}}
    blobs=review_blobs(pins)
    def doc(p):return json.loads(blobs[p])
    o,idx,b,stored,cert,man,c=[doc(p) for p in [OUT,INDEX,BIND,REG,CERT,MAN,CONTRACT]]
    r=stored['overrides'];prior=set(r['required_prior_inputs']);implementation=set(r['implementation_sources'])
    known=prior|implementation|{REG,CERT,CAP,MAN}
    assert len(prior)==480 and len(implementation)==6 and known==set(b['current_known_input_pins']) and len(known)==490
    assert INDEX not in known
    proposed_prior=prior|{INDEX}
    proposed_cert_sources=proposed_prior|implementation|{REG,CAP}
    proposed_component_sources=implementation|{REG,CAP,CERT}
    proposed_capture=proposed_prior|implementation|{REG,CERT,CAP,MAN,RAW,RESULT,COMPSEAL}
    proposed_union=proposed_capture|{AUTH}
    assert list(map(len,[proposed_prior,proposed_cert_sources,proposed_component_sources,proposed_capture,proposed_union]))==[481,489,9,494,495]
    fixed=known-{REG,CERT,CAP,MAN}
    variable={x['path']:x['max_serialized_bytes'] for x in o['byte_envelopes']['variable_members']}
    assert set(variable)=={REG,CERT,CAP,MAN,INDEX,AUTH,RAW,RESULT,COMPSEAL}
    assert all(type(v) is int and 0<v<=16777216 for v in variable.values())
    fixed_bytes=sum(len(blobs[p]) for p in fixed);unique=fixed_bytes+sum(variable.values())
    assert len(fixed)==486 and fixed_bytes==86983017 and sum(variable.values())==244992 and unique==87228009
    fresh=b['read_schedule']['worker_file_read_upper']-3*(b['known_union_bytes']+b['future_metadata_bytes_upper'])
    assert fresh==4852460 and b['read_schedule']['launcher_file_read_upper']==3*(b['known_union_bytes']+b['future_metadata_bytes_upper'])
    read_upper=3*unique+fresh;assert read_upper==266536487 and 268435456-read_upper==1898969
    assert unique<=134217728 and len(proposed_union)<=4096
    filemax=max([len(blobs[p]) for p in fixed]+list(variable.values()));assert filemax==9755833<16777216
    # Independent width descriptions: pairs of key/width, never hash or PASS records.
    sw=lambda x:len(enc(x))
    def object_width(pairs):return 2+sum(sw(k)+1+v for k,v in pairs)+max(0,len(pairs)-1)
    def pinmap_width(paths):return 2+sum(sw(p)+1+66 for p in paths)+max(0,len(paths)-1)
    revision_width=sw('I122-CANDIDATE-01')
    raw_fields=[('schema',sw('d5.joint-component-raw.v2')),('source_revision',revision_width),('status',6),('tests_run',2),('failures',1),('errors',1),
        ('functional_campaigns_executed',1),('product_or_runner_imported',5),('forbidden_imports',2),('elapsed_milliseconds',6),('new_module_count',19),('closure',5),('D5_closed',5)]
    result_fields=[('schema',sw('d5.joint-component-review.v2')),('source_revision',revision_width),('status',6),('tests_run',2),('functional_campaigns_executed',1),
        ('product_or_runner_imported',5),('raw_sha256',66),('manifest_sha256',66),('decision',sw('ACCEPTED_COMPONENTS_ONLY')),('closure',5),('D5_closed',5)]
    widths={
        AUTH:object_width([('schema',sw('d5.joint-capture-authority.v2')),('phase',sw('JOINT_EXPLICITLY_APPROVED')),('scopes',sw(['P01'])),('registry_sha256',66),('capture_inputs',pinmap_width(proposed_capture))])+1,
        RAW:object_width(raw_fields)+1,RESULT:object_width(result_fields)+1,
        COMPSEAL:object_width([('schema',sw('d5.joint-component-integrity.v2')),('source_revision',revision_width),('artifacts',pinmap_width([RAW,RESULT,MAN])),('source_bindings',pinmap_width(proposed_component_sources))])+1}
    assert widths=={AUTH:55142,RAW:327,RESULT:417,COMPSEAL:1529}==o['byte_envelopes']['symbolic_closed_schema_future_widths']
    assert all(widths[p]<=variable[p] for p in widths)
    trees={p:ast.parse(blobs[p].decode()) for p in [JOINT,READER]}
    def symbol(p,name):
        n=trees[p]
        for part in name.split('.'):
            matches=[x for x in ast.iter_child_nodes(n) if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name==part]
            assert len(matches)==1;n=matches[0]
        return n
    anchors=[]
    for a in o['source_evidence']['anchors']:
        n=symbol(a['path'],a['symbol']);h=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()
        assert n.lineno==a['line'] and n.end_lineno==a['end_line'] and h==a['AST_sha256']
        anchors.append(dict(path=a['path'],symbol=a['symbol'],source_sha256=pins[a['path']],line=n.lineno,end_line=n.end_lineno,AST_sha256=h))
    def call(n,s):return any(isinstance(x,ast.Call) and ast.unparse(x)==s for x in ast.walk(n))
    before=symbol(JOINT,'InputPlan.before');after=symbol(JOINT,'InputPlan.after');finish=symbol(JOINT,'InputPlan.finish')
    assert any(isinstance(n,ast.For) and ast.unparse(n.iter)=="a['capture_inputs'].items()" and call(n,'self.reader.read(name)') for n in ast.walk(before))
    assert any(isinstance(n,ast.For) and ast.unparse(n.iter)=='self.view.bodies' and call(n,'self.reader.read(name)') for n in ast.walk(after))
    assert call(finish,'self.reader.finish()')
    assert any(isinstance(n,ast.For) and ast.unparse(n.iter)=='tuple(self.files)' and call(n,'self.read(name)') for n in ast.walk(symbol(READER,'Reader.finish')))
    assert any(isinstance(n,ast.Return) and ast.unparse(n)=='return self.bodies[name]' for n in ast.walk(symbol(JOINT,'PhaseBytes.read')))
    assert call(symbol(JOINT,'checked_registry'),'c.sha(snapshot.read(name))')
    assert INDEX not in blobs[JOINT].decode()
    component=symbol(JOINT,'checked_component_metadata')
    declared={n.targets[0].id:ast.literal_eval(n.value) for n in component.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['raw_keys','result_keys']}
    assert declared['raw_keys']=={k for k,_ in raw_fields} and declared['result_keys']=={k for k,_ in result_fields}
    # Check the backing root against the exact previous pin manifest, not a desired root.
    backing={**doc(P+'D5-I172-P10-source-reconstruction.json')['input_pins'],**{p:pins[p] for p in [P+'D5-I172-P10-documentary-review.json',P+'D5-I172-P10-source-reconstruction.json',P+'D5-I172-audit.py',P+'D5-I172-integrity.json']}}
    assert len(backing)==652 and digest(backing)==idx['backing_material_root_sha256']
    assert len(idx['artifacts'])==20 and len(blobs[INDEX])==9853<=variable[INDEX]
    for row in idx['artifacts']:
        assert row['sha256']==pins[row['path']] and row['bytes']==len(blobs[row['path']]) and not row['resource_verified']
        assert row['documentary_review']['sha256']==pins[row['documentary_review']['path']]
    assert idx['signed_resource_acceptance_record'] is None and not idx['independent_acceptance'] and not idx['E01_E05_verified'] and not idx['E06_satisfied']
    top=copy.deepcopy(b['top_metadata_model']['value']);initial_width=len(enc(top));assert initial_width==483286
    for key in ['capture_inputs_before','capture_inputs_after']:
        assert INDEX not in top[key];top[key][INDEX]=pins[INDEX]
    projected=len(enc(top));assert projected==483562 and projected-initial_width==276 and 524288-projected==40726
    assert o['top_metadata']['final_context_launch_package_binding_review_pending']
    return dict(schema='d5.i174-prp173-source-reconstruction.v1',increment='I174',date='2026-11-16',base_commit=REVIEW_BASE,input_pins=pins,
        method='Fresh Git blobs, set-derived future metadata graph, variable-envelope sum, inherited fresh-read subtraction, separate symbolic width pairs, source-loop ASTs and two-map reserialization.',
        methodologically_separate=True,actor_independent=False,organizationally_independent=False,
        graph_counts=dict(historical_prior_inputs=480,implementation_sources=6,proposed_prior_inputs=481,certificate_source_bindings=489,
            component_source_bindings=9,capture_manifest=494,union_with_authority=495,only_extra_physical_path=INDEX),
        fixed_pin_ledger=[dict(path=p,sha256=pins[p],bytes=len(blobs[p])) for p in sorted(fixed)],
        variable_envelopes=variable,closed_schema_widths=widths,source_anchor_checks=anchors,
        accounts=[dict(reader=name,fixed_bytes=fixed_bytes,variable_upper_bytes=sum(variable.values()),unique_upper_bytes=unique,
            physical_three_pass_upper_bytes=3*unique,inherited_additional_fresh_read_upper_bytes=fresh,total_read_upper_bytes=read_upper,
            read_limit=268435456,conditional_read_margin_bytes=1898969,file_upper_bytes=filemax,paths=495,
            conditional_fit=True,final_graph_accepted=False) for name in ['coordinator_input_Reader','worker_input_Reader']],
        backing_root_check=dict(pin_count=652,canonical_SHA256=digest(backing),real_index_bytes=len(blobs[INDEX]),resource_acceptance_supplied=False),
        top_metadata=dict(full_reserialization_bytes=projected,two_map_delta_bytes=276,conditional_margin_bytes=40726,
            same_other_fields_required=True,not_final_context_or_package_proof=True),
        confirmed_conditions=[
            'All486 fixed historical bodies remain identical; only the declared nine variable bodies/path set may differ.',
            'Every final body, including accepted successor index, must meet its proposed envelope; these are not changed product quotas or runtime enforcement.',
            'No implementation/runner/target/binding/source-path/source_revision change; pure new-index checks remain PhaseBytes; no extra physical dereference.',
            'Inherited directory listing stability and4096-entry cap remain required; no Reader resets, pooling or dropped fresh checks.',
            'Independent resource/packaging/binding review and competent signed approval precede actual exact rebind; current worker only hashes index.',
            'Current negative index is not a future accepted index; no signature, component PASS or source-capacity certificate is created.',
            'Final top metadata/context/launch/package must be revalidated; width-model delta is conditional only.'],
        counts=dict(input_pins=len(pins),source_anchors=9,backing_packages=20,fixed_members=486,variable_members=9,extra_input_paths=1),
        resource_obligations_closed=0,execution_count=0)


CHECKS=[
    ('R01','Concrete negative index bytes,20 artifact/review hashes and652-pin backing root','PASS_DOCUMENTARY_BINDING_ONLY'),
    ('R02','480 historical prior inputs retained; only index appended physically','PASS_CONDITIONAL_GRAPH_DESIGN'),
    ('R03','481/489/9/494/495 future binding counts and exact schemas','PASS_SET_ARITHMETIC_ONLY_NO_REBIND'),
    ('R04','486 frozen members plus nine bounded variable bodies, including authority/components','PASS_COMPLETE_DECLARED_ENVELOPE_SUM'),
    ('R05','Three same-Reader passes and unchanged inherited fresh-read schedule','PASS_CONDITIONAL_SOURCE_TRANSFER'),
    ('R06','266536487 read upper,1898969 margin per Input Reader under conditions','CONDITIONAL_READER_FIT_CONFIRMED'),
    ('R07','File/unique/path bounds, no pooling/reset and separate Evidence Reader','PASS_CONDITIONAL_ACCOUNTING'),
    ('R08','55142/327/417/1529 closed metadata widths without fake hashes/PASS records','PASS_SYMBOLIC_WIDTH_ARITHMETIC'),
    ('R09','Proposed byte envelopes not new product quotas, enforcement or actual final fit','PASS_SCOPE_DISCLOSURE'),
    ('R10','Index references not dereferenced or called fresh reads; worker does not validate resource semantics','PASS_SOURCE_AND_TRUST_LIMIT'),
    ('R11','Detached approval/binding order, separately versioned proofs and final cycle review required','PASS_PROPOSED_ORDER_ONLY'),
    ('R12','Top metadata483562 by full model reserialization; final output binding review pending','PASS_PARTIAL_WIDTH_ONLY'),
    ('R13','No accepted successor, resource evidence, independent role or E06 completion supplied','INSUFFICIENT_FOR_ADMISSION'),
    ('R14','P09 retained-extension negative result preserved for its original graph','PASS_DISTINCT_GRAPH_SCOPE'),
    ('R15','Same actor; packaging review not independent resource/custodian acceptance','PASS_PROVENANCE_DISCLOSURE'),
    ('R16','Prior bytes/no execution/no quotas/source changes/rebind/no admission','PASS_PRESERVATION_ONLY')]


def review_record(rec):
    o=rd(OUT)
    return dict(schema='d5.i174-prp173-documentary-review.v1',increment='I174',date='2026-11-16',base_commit=REVIEW_BASE,
        proposal_id='PRP173-INDEX-01',status='CONDITIONALLY_COHERENT_READER_FIT_CONFIRMED_NOT_APPLIED_NOT_ADMITTED',
        subject=o['subject'],input_pins={**rec['input_pins'],RECON:sha(RECON)},reconstruction=pin(RECON),
        provenance=dict(reviewer='Codex assistant in same chat; also prepared I173',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,independent_reviewer_identity=None,independent_acceptance=False,custodian_acceptance=False),
        checks=[dict(id=i,scope=s,result=r,resource_obligation_closed=False) for i,s,r in CHECKS],
        findings=dict(blocking_documentary_defects=[],conditional_reader_bound_confirmed=True,
            admission_blocks=[
                'Exact accepted E01-E05 proofs, target/custodian provenance and E06 remain absent.',
                'Independent approval of out-of-band evidence/index protocol and binding impact remains required; worker does not enforce resource semantics.',
                'Accepted successor index, detached approval, final registry/certificate/manifest/components/authority and their bytes/pins do not exist.',
                'Final bodies must meet all envelopes with the inherited physical read and directory graph unchanged.',
                'Final context/launch/package and scope/cycle validation remain pending; top-width result is a partial conditional model.'],
            nonclaim='No unconditional actual capture fit, resource/service/900 proof, source-capacity certificate or independent acceptance.'),
        counts=rec['counts'],confirmed_conditions=rec['confirmed_conditions'],
        verdict=dict(documentary_conformance=True,conditional_Input_Reader_upper_bytes=266536487,conditional_margin_bytes=1898969,
            actual_final_graph_accepted=False,independent_packaging_acceptance=False,resource_obligations_closed=0,
            accepted_successor_index_supplied=False,rebind_applied=False,proposal_enabled=False,D5_closed=False),
        decision=o['decision'],E06=o['E06'],
        next_evidence_required='Keep no admission. Obtain independent scoped resource/provenance/protocol review, accepted successor artifacts, final byte envelopes and exact acyclic rebind/output validation before separate authorized admission. No execution or quota/source change authorized here.',
        work_unit=dict(rollback_files=sorted(NEW_FILES),verification_command='python3 docs/validation/D5-I174-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary packaging review only; target execution prohibited.',over400_lines=True,
            reason='Self-contained historical validator, fresh graph/width reconstruction and pinned review evidence; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_not_admission=True))


def main():
    validate_preparation()
    rec=reconstruct();assert rd(RECON)==rec and rd(NEW_REVIEW)==review_record(rec)
    prior=rd(SEAL);preserved={**prior['preserved_published343'],**prior['artifacts'],SEAL:sha(SEAL)};seal=rd(NEW_SEAL)
    assert len(preserved)==349 and seal['preserved_published349']==preserved
    assert seal['schema']=='d5.i174-integrity.v1' and seal['base_commit']==REVIEW_BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==NEW_FILES-{NEW_SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    for k in ['resource_closure_verified','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert rec['counts']['input_pins']==658
    changes=set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changes==NEW_FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',REVIEW_BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=REVIEW_BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I174',proposal='PRP173-INDEX-01',documentary_conformance=True,
        conditional_reader_fit_confirmed=True,conditional_Input_Reader_upper_bytes=266536487,conditional_margin_bytes=1898969,
        actual_final_graph_accepted=False,prior_published_files_preserved=349,new_files=5,rebind_applied=False,
        product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,independent_acceptance=False,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':main()
