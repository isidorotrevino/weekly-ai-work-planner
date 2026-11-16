#!/usr/bin/env python3
"""I189 documentary contract/grammar audit only. No target/crypto execution, protocol channels/workers or runtime sampling."""
import ast
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='faed688f34e0cda165f7630ca0ccb1fea973f4c3'
SPEC=P+'D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.json'
GRAM=P+'D5-I189-BOOTSTRAP-TRANSPORT-GRAMMAR-CANDIDATE.json'
PREP=P+'D5-I189-preparation-review.json';AUDIT=P+'D5-I189-audit.py';SEAL=P+'D5-I189-integrity.json'
DOC='docs/design/D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.md'
FILES={SPEC,GRAM,PREP,AUDIT,SEAL,DOC};PRIOR_SEAL=P+'D5-I188-integrity.json'


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def linear_machine(m):
    transitions=m['transitions'];states={m['initial'],m['success']};arcs={};events=set()
    for row in transitions:
        s,e,t=row['state'],row['event'],row['next'];assert s not in arcs and e not in events
        arcs[s]=t;events.add(e);states|={s,t}
    assert m['failure'] not in states
    order=[];cur=m['initial']
    while True:
        assert cur not in order;order.append(cur)
        if cur==m['success']:break
        assert cur in arcs;cur=arcs[cur]
    assert set(order)==states and len(order)==len(transitions)+1
    assert m['success'] not in arcs
    return order


def dependency_order(edges):
    pending={n:set() for e in edges for n in e}
    for a,b in edges:pending[b].add(a)
    order=[]
    while pending:
        ready=sorted(n for n,deps in pending.items() if not deps);assert ready,'Joint protocol dependency cycle'
        order+=ready
        for n in ready:del pending[n]
        for deps in pending.values():deps.difference_update(ready)
    return order


def build_review():
    spec=rd(SPEC);grammar=rd(GRAM);pins=spec['input_pins'];assert len(pins)==739
    requests=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=requests))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    # Replay documentary reconstruction, never a predecessor publication-boundary main.
    previous=runpy.run_path(str(ROOT/(P+'D5-I188-audit.py')));r=previous['reconstruct']()
    assert rd(previous['RECON'])==r and rd(previous['REVIEW'])==previous['build_review'](r)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published426'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==431
    for p,h in preserved.items():assert sha(p)==h,p
    for name,binding in spec['bindings'].items():assert sha(binding['path'])==binding['sha256'],name
    profile=rd(spec['bindings']['profile02']['path']);pack=rd(spec['bindings']['protocol_schemas02']['path']);defs=pack['$defs']
    output=rd(spec['bindings']['output_schemas']['path'])
    assert spec['profile_id']==grammar['profile_id']==profile['profile_id']=='PGO181-TRUST-ED25519-JCS-CANDIDATE-02'
    assert spec['contract_id']==grammar['protocol'] and spec['base_commit']==grammar['base_commit']==BASE
    expected=[('C','trust_context','PARENT_TO_WORKER',8192,8193),('Q','runtime_request','PARENT_TO_WORKER',2048,2049),
              ('I','worker_invocation','PARENT_TO_WORKER',511,512),('A','worker_ready','WORKER_TO_PARENT',511,512),('L','parent_release','PARENT_TO_WORKER',511,512)]
    assert len(grammar['frames'])==5
    for f,w in zip(grammar['frames'],expected):
        assert (f['id'],f['definition'],f['direction'],f['max_body_bytes'],f['max_frame_bytes'])==w
        assert f['json_pointer']=='/$defs/'+f['definition'] and f['definition'] in defs
        assert f['schema_pack']==spec['bindings']['protocol_schemas02']
        assert f['delimiter_hex']=='0a' and not f['prefix_or_extra_tag_on_wire']
        assert f['max_frame_bytes']==f['max_body_bytes']+1 and f['body_must_be_existing_exact_schema_and_canonical_codec']
    assert profile['bootstrap']['context_limits']['serialized_bytes']==8192
    assert profile['bootstrap']['context_limits']['runtime_request_bytes']==2048
    assert grammar['parent_to_worker_stream_before_ready']==['C','Q','I']
    assert grammar['parent_to_worker_stream_after_ready']==['L'] and grammar['worker_to_parent_stream']==['A']
    parent=linear_machine(grammar['parent_machine']);worker=linear_machine(grammar['worker_machine'])
    assert len(parent)==12 and len(worker)==11
    for a,b in [('P_ROOT_CHECK','P_RESERVED'),('P_SEND_I','P_WAIT_A'),('P_WAIT_A_EOF','P_SEND_L'),('P_SEND_L','P_RELEASED')]:assert parent.index(a)<parent.index(b)
    for a,b in [('W_READ_I','W_ROOT_CHECK'),('W_ROOT_CHECK','W_SEND_A'),('W_CLOSE_UP','W_WAIT_L'),('W_WAIT_L_EOF','W_RELEASED')]:assert worker.index(a)<worker.index(b)
    edges=[[a,b] for machine in [parent,worker] for a,b in zip(machine,machine[1:])]+grammar['joint_precedence_edges']
    order=dependency_order(edges);assert len(order)==23
    assert order.index('W_ROOT_CHECK')<order.index('W_RELEASED')
    assert order.index('W_CLOSE_UP')<order.index('P_SEND_L')
    assert order.index('P_RECHECK')<order.index('W_RECHECK')
    # Guard-order exclusions over symbolic relations only, not an executable endpoint/state trace.
    forbidden=[('WORKER_READY_BEFORE_FULL_ROOT',worker.index('W_ROOT_CHECK')<worker.index('W_SEND_A')),
               ('PARENT_RELEASE_BEFORE_READY_EOF',parent.index('P_WAIT_A_EOF')<parent.index('P_SEND_L')),
               ('FUNCTIONAL_IMPORT_BEFORE_RELEASE_EOF',worker.index('W_WAIT_L_EOF')<worker.index('W_RELEASED')),
               ('CAPTURE_RESERVATION_BEFORE_ADMISSION',parent.index('P_ROOT_CHECK')<parent.index('P_RESERVED'))]
    assert all(ok for _,ok in forbidden)
    assert grammar['any_failure_terminal_for_invocation'] and not grammar['permissions']['current_execution_authorized']
    assert grammar['permissions']['worker_functional_import_after']=='W_RELEASED only'
    assert len(grammar['universal_rejections'])==18 and len(set(grammar['universal_rejections']))==18
    caps=grammar['transport_limits']
    assert caps==dict(read_request_bytes=1,write_request_bytes=4096,max_io_or_readiness_attempts_per_endpoint=65536,
        parent_total_handshake_seconds=20,worker_total_handshake_seconds=20,reset_deadline_per_frame=False,
        additional_control_pipes=0,additional_repository_inputs=0,additional_processes=0)
    frames={f['id']:f for f in grammar['frames']}
    down=sum(frames[i]['max_frame_bytes'] for i in ['C','Q','I','L']);up=frames['A']['max_frame_bytes']
    wire=down+up;transfers=2*wire;progress=transfers+2
    assert (down,up,wire,transfers,progress)==(11266,512,11778,23556,23558)
    arithmetic=spec['deadlines_and_cost']['wire_arithmetic']
    assert arithmetic==dict(C_frame=8193,Q_frame=2049,I_frame=512,A_frame=512,L_frame=512,parent_to_worker_total=down,
        worker_to_parent_total=up,both_streams_wire_bytes=wire,aggregate_positive_transferred_bytes_read_plus_write=transfers,
        terminal_EOF_reads=2,worst_positive_progress_calls_plus_EOF_both_endpoints=progress)
    assert wire+1<=65536 # per endpoint positive progress calls+one required EOF <= global attempts
    anchors=[]
    for a in spec['source_anchors']:
        assert sha(a['path'])==a['sha256'];tree=ast.parse((ROOT/a['path']).read_text())
        n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==a['symbol'])
        assert (n.lineno,n.end_lineno)==(a['line'],a['end_line'])
        assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256'];anchors.append(a)
    assert len(anchors)==2
    observed_args=output['$defs']['worker_arguments']['properties'];assert set(observed_args)=={'status','scope','sidecar_fd','ready_fd','release_fd','directory_fd','lease'}
    for n in ['worker_invocation','worker_ready','parent_release','capture_binding']:assert output['$defs'][n]==defs[n]
    assert [e['role'] for e in spec['endpoint_ownership']]==['DOWN','UP','OTHER_INHERITED']
    required_phrases={('trust_boundary','immutable_entry_choice'):['trusted runtime-image module entry','immutable','not an image supplied here','reject'],
       ('trust_boundary','initial_worker_trust'):['Fstat type, fd number, parent PID, key_id or bytes alone cannot establish','Platform custody'],
       ('framing','eof_and_order'):['without waiting for down EOF','EOF before recheck and L','EOF before final recheck/import'],
       ('one_use_and_permissions','parent_claim'):['before reserving paths/spawning','Failure spends the invocation'],
       ('one_use_and_permissions','worker_correlation'):['not a second independent request','same invocation/root/context/request'],
       ('deadlines_and_cost','Reader_scope'):['both existing coordinator and worker','same ledger','global resource composition'],
       ('failure_and_outputs','output_compatibility'):['unchanged I187','not new receipt fields or files']}
    for (section,field),phrases in required_phrases.items():assert all(s in spec[section][field] for s in phrases),(section,field)
    assert spec['unchanged_numeric_candidates']==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    assert spec['decision']==profile['decision'] and spec['E06']==profile['E06']
    for f in ['adopted','implemented','trusted_entry_image_supplied','trust_anchor_established','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert spec['current_effect'][f] is False
    for s in profile['scope']['future_slots']:assert not (ROOT/s['path']).exists()
    assert not (ROOT/'testing/prospective_capture_joint_prp181').exists()
    outspec=rd(spec['bindings']['output_contract']['path'])
    for f in ['context','launch_copy']:assert not (ROOT/outspec['output_locations'][f]).exists()
    assert set(spec['work_unit']['rollback_files'])==FILES
    return dict(schema='d5.i189-preparation-review.v1',increment='I189',date='2026-11-16',base_commit=BASE,
        status='BOOTSTRAP_TRANSPORT_CONTRACT_PREPARED_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        contract=dict(path=SPEC,sha256=sha(SPEC)),grammar=dict(path=GRAM,sha256=sha(GRAM)),input_pins=739,prior_published_files_preserved=len(preserved),
        grammar_checks=dict(frame_count=5,parent_states=12,worker_states=11,dependency_state_nodes=23,
            parent_order=parent,worker_order=worker,joint_acyclic_order=order,
            guarded_order_exclusions=[dict(case=n,ordering_required=ok) for n,ok in forbidden],
            universal_failure_classes=18,frame_caps_and_existing_schema_refs_exact=True,
            no_live_stream_parser_or_schedule_executed=True),
        arithmetic=dict(parent_to_worker_bytes=down,worker_to_parent_bytes=up,total_wire_bytes=wire,
            endpoint_transferred_bytes_read_plus_write=transfers,progress_calls_plus_terminal_EOF_reads=progress,
            max_attempts_both_endpoints=2*65536,actual_IO_call_count_or_service_verified=False),
        preservation=dict(profile02_and_output_bytes_unchanged=True,eight_S01_exclusions_and_F183_01_repair_preserved=True,
            no_extra_protocol_pipes_files_processes=True,actual_bootstrap_image_caller_clock_or_identity_verified=False,
            actual_resource_Reader_or_900_proof=False),source_anchors=anchors,
        provenance=dict(preparer='Same Codex assistant/chat; not a named independent approver',actor_independent=False,organizationally_independent=False,independent_acceptance=False),
        current_effect=spec['current_effect'],decision=spec['decision'],E06=spec['E06'],remaining_work=spec['remaining_work'],work_unit=spec['work_unit'])


def main():
    review=build_review();assert rd(PREP)==review
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published426'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    seal=rd(SEAL);assert seal['schema']=='d5.i189-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published431']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for p,h in seal['artifacts'].items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I189',frames=5,dependency_state_nodes=23,wire_bytes_upper=11778,
        historical_pins=739,prior_published_files_preserved=431,new_files=6,adopted=False,implemented=False,
        trusted_entry_image_supplied=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
