#!/usr/bin/env python3
"""I190 documentary review: Git/JSON/schema/graph arithmetic only; no target/crypto/worker/channel execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='400f99d70b0a52d55737b4c7aa343ff16321d9b7'
SPEC=P+'D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.json'
GRAM=P+'D5-I189-BOOTSTRAP-TRANSPORT-GRAMMAR-CANDIDATE.json'
OLD_PREP=P+'D5-I189-preparation-review.json'
OLD_AUDIT=P+'D5-I189-audit.py'
PRIOR_SEAL=P+'D5-I189-integrity.json'
OLD_DOC='docs/design/D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.md'
PRIOR_FILES={SPEC,GRAM,OLD_PREP,OLD_AUDIT,PRIOR_SEAL,OLD_DOC}
RECON=P+'D5-I190-I189-source-reconstruction.json'
REVIEW=P+'D5-I190-I189-documentary-review.json'
AUDIT=P+'D5-I190-audit.py';SEAL=P+'D5-I190-integrity.json'
DOC='docs/design/D5-I190-I189-BOOTSTRAP-TRANSPORT-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def jlen(v):return len(json.dumps(v,ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(',',':')).encode('ascii'))
def pin(p,q):return dict(path=p,sha256=sha(p),json_pointer=q)


def transition_chain(machine):
    outgoing={}
    for row in machine['transitions']:
        assert row['state'] not in outgoing
        outgoing[row['state']]=row
    current=machine['initial'];order=[];events=[]
    while current!=machine['success']:
        assert current not in order and current in outgoing
        order.append(current);row=outgoing[current];events.append(row['event']);current=row['next']
    order.append(current)
    assert len(order)==len(outgoing)+1 and machine['failure'] not in order
    return order,events


def fixed_control_length(schema,defs):
    assert schema['type']=='object' and schema['additionalProperties'] is False
    fields=schema['properties'];assert set(schema['required'])==set(fields)
    total=2+max(0,len(fields)-1)
    for k,s in fields.items():
        if 'const' in s:n=jlen(s['const'])
        else:
            assert s=={'$ref':'#/$defs/sha256'}
            d=defs['sha256'];assert d['minLength']==d['maxLength']==64 and d['pattern']=='^[0-9a-f]{64}$'
            n=66 # quoted lowercase hex, no escaping; length exact for every valid value
        total+=jlen(k)+1+n
    return total


def reconstruct():
    spec=rd(SPEC);grammar=rd(GRAM);pins={**spec['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==745
    req=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    previous=runpy.run_path(str(ROOT/OLD_AUDIT));assert previous['build_review']()==rd(OLD_PREP)
    for b in spec['bindings'].values():assert sha(b['path'])==b['sha256']
    pack=rd(spec['bindings']['protocol_schemas02']['path']);defs=pack['$defs']
    frames={f['id']:f for f in grammar['frames']};assert set(frames)=={'C','Q','I','A','L'}
    exact={i:fixed_control_length(defs[frames[i]['definition']],defs) for i in ['I','A','L']}
    assert exact=={'I':408,'A':402,'L':406}
    frame_exact={i:n+1 for i,n in exact.items()}
    assert all(frame_exact[i]<=frames[i]['max_frame_bytes']==512 for i in exact)
    caps={i:f['max_frame_bytes'] for i,f in frames.items()}
    assert caps==dict(C=8193,Q=2049,I=512,A=512,L=512)
    nominal_down=sum(caps[i] for i in ['C','Q','I','L']);nominal_up=caps['A']
    nominal=nominal_down+nominal_up;assert nominal==11778 and nominal_down==11266
    conforming=caps['C']+caps['Q']+sum(frame_exact.values());assert conforming==11461
    # Static prefix sums. A rejected slot consumes <=body cap+1 LF/overflow sentinel;
    # previous control slots are schema-valid, hence exact length. EOF probes consume
    # at most1 unexpected byte; no parser or stream/schedule is implemented/executed.
    cases={
        'C_REJECTED':caps['C'],
        'Q_REJECTED_AFTER_C':caps['C']+caps['Q'],
        'I_REJECTED_AFTER_C_Q':caps['C']+caps['Q']+caps['I'],
        'A_REJECTED_AFTER_C_Q_I':caps['C']+caps['Q']+frame_exact['I']+caps['A'],
        'A_EXTRA_BYTE_AT_EOF_PROBE':caps['C']+caps['Q']+frame_exact['I']+frame_exact['A']+1,
        'L_REJECTED_AFTER_VALID_A_EOF':caps['C']+caps['Q']+frame_exact['I']+frame_exact['A']+caps['L'],
        'L_EXTRA_BYTE_AT_EOF_PROBE':conforming+1}
    assert max(cases.values())==11566 and max(cases.values())<nominal
    parent,pevents=transition_chain(grammar['parent_machine']);worker,wevents=transition_chain(grammar['worker_machine'])
    assert len(parent)==12 and len(worker)==11
    assert parent.index('P_ROOT_CHECK')<parent.index('P_RESERVED')<parent.index('P_SEND_C')
    assert parent.index('P_WAIT_A_EOF')<parent.index('P_RECHECK')<parent.index('P_SEND_L')<parent.index('P_RELEASED')
    assert worker.index('W_READ_I')<worker.index('W_ROOT_CHECK')<worker.index('W_SEND_A')
    assert worker.index('W_CLOSE_UP')<worker.index('W_WAIT_L')<worker.index('W_WAIT_L_EOF')<worker.index('W_RECHECK')<worker.index('W_RELEASED')
    assert 'I' in grammar['stream_eof'] and 'No EOF' in grammar['stream_eof']['I']
    assert len(grammar['joint_precedence_edges'])==3
    limits=grammar['transport_limits']
    assert limits['read_request_bytes']==1 and limits['write_request_bytes']==4096
    assert limits['max_io_or_readiness_attempts_per_endpoint']==65536
    assert limits['parent_total_handshake_seconds']==limits['worker_total_handshake_seconds']==20
    assert limits['reset_deadline_per_frame'] is False
    for k in ['additional_control_pipes','additional_repository_inputs','additional_processes']:assert limits[k]==0
    assert grammar['permissions']['worker_functional_import_after']=='W_RELEASED only'
    assert grammar['permissions']['current_execution_authorized'] is False
    assert grammar['any_failure_terminal_for_invocation'] and len(set(grammar['universal_rejections']))==18
    assert [e['role'] for e in spec['endpoint_ownership']]==['DOWN','UP','OTHER_INHERITED']
    assert spec['endpoint_ownership'][0]['payloads']==['C','Q','I','L'] and spec['endpoint_ownership'][1]['payloads']==['A']
    assert spec['current_effect']['trusted_entry_image_supplied'] is False and not spec['current_effect']['trust_anchor_established']
    assert spec['unchanged_numeric_candidates']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    assert spec['current_effect']['F183_01_documentary_repair_preserved']
    profile=rd(spec['bindings']['profile02']['path'])
    assert spec['decision']==profile['decision'] and spec['E06']==profile['E06']
    for s in profile['scope']['future_slots']:assert not (ROOT/s['path']).exists()
    assert not (ROOT/'testing/prospective_capture_joint_prp181').exists()
    return dict(schema='d5.i190-i189-source-reconstruction.v1',increment='I190',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs and separate local chain ordering/control-schema fixed-width/prefix-cost derivation; inherited documentary checks only, no runtime/channel parser or schedule.',
        frame_bounds=dict(published_frame_caps=caps,published_parent_to_worker_bytes=nominal_down,published_worker_to_parent_bytes=nominal_up,
            published_total_wire_bytes=nominal,exact_schema_control_body_bytes=exact,exact_schema_control_frame_bytes=frame_exact,
            valid_stream_upper_using_exact_controls=conforming,receiver_first_rejection_prefix_bounds=cases,
            largest_received_prefix_in_declared_failure_cases=11566,including_extra_EOF_probe_within_published_envelope=True,
            scope='Received-byte bounds for declared one-byte fail-stop parser/first rejected slot; not all bytes an arbitrary noncompliant sender may offer/queue, not actual syscalls/IO/CPU/heap or a hostile-host proof.'),
        state_scope=dict(parent_local_states=parent,worker_local_states=worker,parent_events=pevents,worker_events=wevents,
            local_state_nodes=23,not_joint_product_state_enumeration=True,
            no_EOF_wait_after_I=True,READY_EOF_before_parent_recheck_RELEASE=True,RELEASE_EOF_before_worker_recheck_import=True,
            happy_path_wait_obligations=[
                'Parent sends C/Q/I while worker reads; neither side waits READY/EOF to finish the bootstrap prefix.',
                'Worker validates then writes A/closes up; it does not wait for L before providing A EOF.',
                'Parent consumes A EOF/rechecks, writes L/closes down; it does not wait for functional completion before closing.',
                'Worker consumes L EOF/rechecks before functional import; no new reply is needed.'],
            no_declared_circular_channel_wait_in_success_order=True,
            actual_deadlock_freedom_scheduler_or_progress_verified=False),
        trust_and_failure=dict(accepted_caller_and_immutable_first_entry_required=True,fd_PID_key_id_not_trust_by_themselves=True,
            exact_platform_source_image_custody_and_one_use_unproved=True,parent_claim_precedes_reservation_spawn=True,
            child_is_correlated_use_not_second_consumption=True,first_failure_truthful_no_control_error_frames=True,
            partial_stream_terminal_no_retry_or_root_substitution=True,extra_bootstrap_processes_or_repository_files_not_authorized=True,
            existing_I187_outputs_and_profile02_unchanged=True),
        resource_scope=dict(byte_progress_caps_not_service_or_CPU_proof=True,independent_deadline_origins_no_reset=True,
            spawn_crypto_syscalls_and_clock_are_not_preemptively_bounded_by_a_deadline_check=True,
            attempts_both_endpoints=131072,all_setup_runtime_internal_descriptors_and_both_Reader_domains_need_global_bounds=True,
            actual_900_heap_CPU_Reader_fit_verified=False),
        verdict=dict(new_blocking_documentary_findings=0,documentary_contract_consistent_under_stated_platform_premises=True,
            adopted=False,implemented=False,independent_acceptance=False,trusted_image_or_caller_supplied=False,
            actual_runtime_security_or_progress_verified=False,F179_01_resolved=False,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    spec=rd(SPEC)
    return dict(schema='d5.i190-i189-documentary-review.v1',increment='I190',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal='PGO181-SPLIT-ROOT-01',profile_id=spec['profile_id'],contract_id=spec['contract_id'],
        status='BOOTSTRAP_TRANSPORT_DOCUMENTARY_CONTRACT_CONFIRMED_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        reconstruction=dict(path=RECON,sha256=sha(RECON)),
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I189 and prior candidates',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,independent_acceptance=False,custodian_acceptance=False),
        findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in [
            ('R01','Trust before mutable repository code; accepted image/source/loader/caller custody explicit','PASS_BOUNDARY_SPEC_NOT_PLATFORM_ATTESTATION'),
            ('R02','Exclusive inherited endpoints and four fd roles; no authenticity inferred from descriptors','PASS_OWNERSHIP_CONTRACT_NOT_OS_PROOF'),
            ('R03','Five exact schema refs, caps/LF/directions and no wrappers','PASS_FRAMING_SPEC_NOT_PARSER_CONFORMANCE'),
            ('R04','C/Q/I prefix before root/READY; no down EOF wait after I','PASS_DECLARED_ORDER'),
            ('R05','READY/EOF parent recheck RELEASE/EOF worker recheck before import','PASS_GUARD_ORDER_NOT_EXECUTED_TRACE'),
            ('R06','Published11778 envelope and rejected-prefix/EOF probe arithmetic','PASS_CONDITIONAL_RECEIVER_BOUND'),
            ('R07','Separate20-second origins, global counters and no per-frame resets','PASS_DECLARED_REJECTION_POLICY_NOT_LATENCY_BOUND'),
            ('R08','One-use claim before paths/spawn; worker correlated with same claim; failures spent','PASS_PERMISSION_MODEL_NOT_IMPLEMENTED_CUSTODY'),
            ('R09','Failure terminals, no new error frames/retries; diagnostics only on trusted owned channels','PASS_FAIL_CLOSED_SPEC'),
            ('R10','I187 outputs and profile02/eight S01 exclusions/CP07 preserved','PASS_NO_SCHEMA_OR_ADMISSION_CHANGE'),
            ('R11','All sources/runtime internals/two-process Reader/copy/crypto/IO resources still require proof','OPEN_RESOURCE_AND_IMPLEMENTATION_WORK'),
            ('R12','Same preparer/reviewer actor; no genuine trust/custody/image supplied','PASS_PROVENANCE_AND_NONADMISSION_DISCLOSURE')]],
        evidence=[pin(SPEC,'/trust_boundary'),pin(SPEC,'/framing'),pin(SPEC,'/one_use_and_permissions'),pin(GRAM,'/stream_eof'),pin(GRAM,'/transport_limits')],
        verdict=rec['verdict'],current_effect=spec['current_effect'],decision=spec['decision'],E06=spec['E06'],remaining_work=spec['remaining_work'],
        limitations=['Local23-node precedence and receiver-prefix arithmetic are not a joint concurrent-system model, parser implementation, cryptographic verification, real capability proof or general deadlock/security theorem.',
            'A deadline/counter is a fail-closed policy. Spawn, library, IO and scheduler service still need exact platform/source phase bounds; no guaranteed20/900-second completion.',
            'Malformed traffic prefix bound covers bytes actually consumed before terminal rejection. Arbitrary offered/queued bytes outside compliant sender/custody assumptions are not globally bounded by11778.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I190-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary bootstrap review; no product/component/crypto or protocol pipe/worker execution.',over400_lines=True,
            reason='Traceable trust/order/control-width/rejected-prefix reconstruction and preservation seal in one documentary review; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published431'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==437
    seal=rd(SEAL);assert seal['schema']=='d5.i190-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published437']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I190',new_blocking_documentary_findings=0,
        documentary_contract_consistent=True,historical_pins=745,prior_published_files_preserved=437,new_files=5,
        wire_envelope_bytes=11778,received_rejected_prefix_upper=11566,adopted=False,implemented=False,independent_acceptance=False,
        trusted_image_or_caller_supplied=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
