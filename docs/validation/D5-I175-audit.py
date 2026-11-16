#!/usr/bin/env python3
"""I175 documentary candidate binding graph. No target execution/import/compilation."""
import ast
import copy
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='2855bb0d117e38764efddacaa69a8194d341f6e4'
D=P+'D5-I175-candidate-bindings/'
C_REG=D+'registry.json'
C_CERT=D+'certificate.json'
C_MAN=D+'components-manifest.json'
DRAFT=D+'authority-binding-draft.json'
OUT=P+'D5-I175-PRP173-CANDIDATE-GRAPH.json'
REVIEW=P+'D5-I175-preparation-review.json'
AUDIT=P+'D5-I175-audit.py'
SEAL=P+'D5-I175-integrity.json'
DESIGN='docs/design/D5-I175-PRP173-CANDIDATE-GRAPH.md'
PROP=P+'D5-I173-READER-PACKAGING-PROPOSAL.json'
INDEX=P+'D5-PFC126-03-RESOURCE-ADMISSION-INDEX-CANDIDATE.json'
CONTRACT=P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
REG=P+'D5-I122-CAPTURE-REGISTRY.json'
CERT=P+'D5-I122-CAPACITY-CERTIFICATE.json'
CAP=P+'D5-I122-CAPACITY-CONTRACT.json'
MAN=P+'D5-I122-COMPONENTS-MANIFEST.json'
BIND=P+'D5-I122-binding-review.json'
AUTH=P+'D5-JOINT-capture-authorization.json'
RAW=P+'D5-JOINT-tests-raw.json'
RESULT=P+'D5-JOINT-results.json'
COMPSEAL=P+'D5-JOINT-integrity.json'
OLD_SEAL=P+'D5-I174-integrity.json'
FILES={C_REG,C_CERT,C_MAN,DRAFT,OUT,REVIEW,AUDIT,SEAL,DESIGN}
OVERRIDES={REG:C_REG,CERT:C_CERT,MAN:C_MAN}
PENDING={RAW,RESULT,COMPSEAL,AUTH}


def rd(p):return json.loads((ROOT/p).read_text())
def enc(x):return json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def size(p):return len((ROOT/p).read_bytes())
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p):return dict(path=p,sha256=sha(p))


def inputs():
    extras=[P+'D5-I174-PRP173-documentary-review.json',P+'D5-I174-PRP173-source-reconstruction.json',P+'D5-I174-audit.py',OLD_SEAL]
    return {**rd(P+'D5-I174-PRP173-source-reconstruction.json')['input_pins'],**{p:sha(p) for p in extras}}


def check_git_inputs():
    pins=inputs();req=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p


def registry():
    o=copy.deepcopy(rd(REG));o['overrides']['required_prior_inputs'][INDEX]=sha(INDEX)
    return o


def certificate():
    o=copy.deepcopy(rd(CERT));r=rd(C_REG)['overrides']
    sources={**r['required_prior_inputs'],**r['implementation_sources'],REG:sha(C_REG),CAP:sha(CAP)}
    o['source_bindings']={p:sources[p] for p in sorted(sources)};o['source_binding_count']=len(sources)
    return o


def manifest():
    o=copy.deepcopy(rd(MAN));sources={**rd(C_REG)['overrides']['implementation_sources'],REG:sha(C_REG),CAP:sha(CAP),CERT:sha(C_CERT)}
    o['source_bindings']={p:sources[p] for p in sorted(sources)};o['source_binding_count']=len(sources)
    # Late consumer hashes intentionally remain null: putting result/seal hashes
    # in a manifest those records themselves hash would introduce cycles.
    return o


def known_nodes():
    baseline=set(rd(BIND)['current_known_input_pins']);known=baseline|{INDEX}
    return {p:dict(source_path=OVERRIDES.get(p,p),sha256=sha(OVERRIDES.get(p,p)),bytes=size(OVERRIDES.get(p,p))) for p in sorted(known)}


def authority_draft():
    known=known_nodes()
    return dict(schema='d5.i175-authority-binding-draft.v1',status='DOCUMENTARY_BINDING_DESCRIPTOR_NOT_AUTHORITY',
        proposal='PRP173-INDEX-01',source_revision='I122-CANDIDATE-01',target_logical_authority_path=AUTH,
        registry_sha256=sha(C_REG),known_capture_inputs={p:v['sha256'] for p,v in known.items()},
        unresolved_capture_inputs=[dict(path=p,sha256=None,reason='E06 NOT_RUN; no real authorized component bytes exist.') for p in [RAW,RESULT,COMPSEAL]],
        authority_sha256=None,authority_body_materialized=False,
        functional_execution_authorized=False,component_execution_authorized=False,capture_authority=False,
        phase='NOT_AUTHORIZED',proposal_enabled=False,D5_closed=False,
        semantics='This separate schema and candidate path are not accepted by the runtime authority parser; never copy this descriptor to the authority path.')


def source_evidence():
    path='testing/prospective_capture_joint_i122/capture.py';tree=ast.parse((ROOT/path).read_text());rows=[]
    for name in ['checked_registry','require_admission','checked_component_metadata']:
        n=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
        rows.append(dict(path=path,symbol=name,sha256=sha(path),line=n.lineno,end_line=n.end_lineno,
            AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()))
    text=ast.unparse(tree)
    assert "required == set(a['capture_inputs'])" in text and "name != CERTIFICATE" in text
    assert "component_sources = set(reg['implementation_sources']) | {REGISTRY, CONTRACT, CERTIFICATE}" in text
    assert "cert.get('status') == 'SOURCE_CAPACITY_VERIFIED'" in text
    return dict(anchors=rows,syntax_only=True,admission_parser_or_components_not_executed=True)


def build_graph():
    nodes=known_nodes();r=rd(C_REG)['overrides'];cert=rd(C_CERT);man=rd(C_MAN)
    capture=set(r['required_prior_inputs'])|set(r['implementation_sources'])|{REG,CAP,CERT,MAN,RAW,RESULT,COMPSEAL}
    assert set(nodes)==capture-{RAW,RESULT,COMPSEAL} and len(capture)==494
    envelopes={x['path']:x['max_serialized_bytes'] for x in rd(PROP)['byte_envelopes']['variable_members']}
    for p in [REG,CERT,CAP,MAN,INDEX]:assert nodes[p]['bytes']<=envelopes[p]
    known_bytes=sum(v['bytes'] for v in nodes.values());unknown_upper=sum(envelopes[p] for p in PENDING)
    candidate_unique=known_bytes+unknown_upper;candidate_read=3*candidate_unique+4852460
    # Dependency direction: consumer -> current candidate dependencies. Historical
    # archival refs in INDEX remain in their old commit, not rebound by path.
    deps={p:[] for p in set(nodes)|PENDING}
    deps[INDEX]=sorted(set(r['implementation_sources'])|{CAP})
    deps[REG]=sorted(set(r['required_prior_inputs'])|set(r['implementation_sources'])|{CAP,rd(C_REG)['base_registry']})
    deps[CERT]=sorted(cert['source_bindings']);deps[MAN]=sorted(man['source_bindings'])
    deps[RAW]=[]  # Manifest is a protocol prerequisite, not a raw JSON hash field.
    deps[RESULT]=[RAW,MAN];deps[COMPSEAL]=sorted(set(man['source_bindings'])|{RAW,RESULT,MAN})
    deps[AUTH]=sorted(capture)
    done=set();order=[]
    def visit(p,active):
        assert p not in active,('binding cycle',p)
        if p in done:return
        for q in deps[p]:
            assert q in deps,(p,q)
            visit(q,active|{p})
        done.add(p);order.append(p)
    for p in sorted(deps):visit(p,set())
    rows=[]
    for p in sorted(set(nodes)|PENDING):
        exists=p in nodes
        rows.append(dict(logical_runtime_path=p,candidate_bytes_source=nodes[p]['source_path'] if exists else None,
            sha256=nodes[p]['sha256'] if exists else None,bytes=nodes[p]['bytes'] if exists else None,
            state='BOUND_REAL_CANDIDATE_BYTES' if exists else 'UNRESOLVED_NO_COMPONENT_OR_AUTHORITY_EVIDENCE',
            in_capture_inputs=p!=AUTH,in_Input_Reader_union=True,hash_dependencies=deps[p],
            max_pending_bytes=envelopes[p] if not exists else None))
    return dict(schema='d5.i175-prp173-candidate-graph.v1',increment='I175',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal_id='PRP173-INDEX-01',status='MEMBERSHIP_FIXED_CANDIDATE_BINDINGS_PARTIAL_NOT_APPLIED_NOT_ADMITTED',
        input_pins=inputs(),candidate_contract=pin(CONTRACT),negative_index=pin(INDEX),
        candidate_metadata=[dict(logical_runtime_path=p,**pin(q),bytes=size(q)) for p,q in OVERRIDES.items()],
        authority_binding_descriptor=dict(**pin(DRAFT),not_runtime_authority=True,not_a_physical_capture_manifest_member=True),
        membership=dict(prior_inputs=481,implementation_sources=6,certificate_source_bindings=489,component_source_bindings=9,
            capture_inputs=494,union_with_authority=495,known_real_bindings=491,unresolved_hashes=4,
            original480_prior_inputs_retained=True,only_extra_input_path=INDEX,membership_fixed_not_all_hashes_final=True),
        nodes=rows,topological_candidate_order=order,binding_dependency_graph_acyclic=True,
        dependency_scope='Current packaging hash edges only. Frozen historical members are immutable leaves; archival references retain historical byte identities/commit, not candidate aliases. Historical semantics/resource dependency closure is not reproved.',
        protocol_only_dependencies=[dict(consumer=RAW,prerequisite=MAN,reason='Authorized component validation uses the bound manifest; raw schema has no manifest hash field.')],
        manifest_late_consumer_policy=dict(raw_sha256=man['raw_sha256'],result_sha256=man['result_sha256'],seal_sha256=man['seal_sha256'],
            intentionally_null_not_fake_evidence=True,late_hashes_owned_by_result_seal_authority=True,no_manifest_result_seal_hash_cycle=True),
        binding_semantics=dict(logical_paths_not_installed=True,preview_paths_not_implicitly_added_to_runtime_manifest=True,
            candidate_overrides_apply_only_to_this_documentary_graph=True,
            archival_INDEX_refs_resolve_at_its_backing_commit_not_current_candidate_aliases=True,
            root_or_index_hash_not_truth_or_signature=True,no_fake_PASS_or_authority_created=True),
        candidate_state_Reader_bound=dict(known_real_unique_bytes=known_bytes,unknown_future_four_upper_bytes=unknown_upper,
            unique_upper_bytes=candidate_unique,read_upper_bytes=candidate_read,additional_fresh_read_upper_bytes=4852460,
            read_limit=268435456,conditional_read_margin_bytes=268435456-candidate_read,
            applies_to_exact_negative_candidate_bytes_plus_bounded_unknowns=True,
            accepted_positive_successor_requires_new_hashes_and_byte_check=True),
        general_PRP173_envelope=dict(read_upper_bytes=266536487,read_limit=268435456,conditional_margin_bytes=1898969,
            unique_upper_bytes=87228009,path_upper=495,all_nine_body_envelopes_still_required=True,
            inherited_fresh_read_graph_and_listing_preconditions_unchanged=True),
        unresolved=[dict(path=p,sha256=None,reason=('Needs all real component pins and separately authorized exact authority; descriptor is not authority.' if p==AUTH else 'E06 remains NOT_RUN; actual authorized raw/result/seal bytes cannot be fabricated.')) for p in sorted(PENDING)],
        activation_blockers=[
            'Negative index has no accepted E01-E05 evidence/signature, and certificate remains IMPLEMENTED_NOT_ADMITTED.',
            'Correlated atomicity/components and independent resource/provenance/packaging acceptance remain unverified; E06 NOT_RUN.',
            'Four final byte/hash bindings absent; no runtime authority or complete positive admission graph exists.',
            'Final approved successor, binding-impact/cycle/Reader/top-metadata/context/package review required before separate authorized rebind.'],
        source_evidence=source_evidence(),
        unchanged_state=dict(active_registry=pin(REG),active_certificate=pin(CERT),active_manifest=pin(MAN),
            active_capture_inputs_changed=False,rebind_applied=False,source_implementation_changed=False,quotas_changed=False,
            reserves_transferred=False,product_or_components_executed=False,resource_obligations_closed=0,
            independent_acceptance=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        decision=rd(PROP)['decision'],E06=rd(PROP)['E06'])


def build_review():
    g=rd(OUT)
    generated=[C_REG,C_CERT,C_MAN,DRAFT,OUT]
    return dict(schema='d5.i175-candidate-graph-preparation-review.v1',increment='I175',date='2026-11-16',base_commit=BASE,
        status='CONCRETE_NEGATIVE_CANDIDATE_GRAPH_PREPARED_FOUR_BINDINGS_UNRESOLVED_NOT_ADMITTED',
        input_pins={**inputs(),**{p:sha(p) for p in generated}},outputs=[pin(p) for p in generated],
        counts=dict(historical_input_pins=len(inputs()),known_bindings=491,unknown_bindings=4,physical_union_paths=495,
            concrete_metadata_overrides=3,authority_descriptors=1,source_anchors=3,new_files=9),
        preparation_checks=dict(original_inputs_retained=True,real_candidate_hashes_in_topological_order=True,
            certificate_self_pin_excluded=True,manifest_late_consumer_hashes_intentionally_excluded=True,
            no_fake_component_or_runtime_authority=True,all_candidate_bodies_within_PRP173_envelopes=True,
            negative_gates_and_resource_findings_preserved=True,active_metadata_untouched=True),
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I175-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary metadata previews and binding graph; product/component execution prohibited.',over400_lines=True,
            reason='Exact candidate metadata, full495-member binding ledger, explicit unresolved evidence and self-contained audit; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_not_admission=True))


def main():
    for path,build in [(C_REG,registry),(C_CERT,certificate),(C_MAN,manifest),(DRAFT,authority_draft)]:
        assert (ROOT/path).read_bytes()==enc(build())+b'\n'
    assert rd(OUT)==build_graph() and rd(REVIEW)==build_review();check_git_inputs()
    prior=rd(OLD_SEAL);preserved={**prior['preserved_published349'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)};seal=rd(SEAL)
    assert len(preserved)==354 and seal['preserved_published354']==preserved
    assert seal['schema']=='d5.i175-integrity.v1' and seal['base_commit']==BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts'],rd(P+'D5-I119-integrity.json')['inherited_inputs477']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert len(inputs())==662 and not FILES&set(inputs())
    r,c,m=rd(C_REG)['overrides'],rd(C_CERT),rd(C_MAN)
    assert set(r['required_prior_inputs'])==set(rd(REG)['overrides']['required_prior_inputs'])|{INDEX}
    assert len(c['source_bindings'])==c['source_binding_count']==489 and CERT not in c['source_bindings']
    assert c['source_bindings'][REG]==sha(C_REG) and c['source_bindings'][INDEX]==sha(INDEX)
    assert len(m['source_bindings'])==m['source_binding_count']==9 and m['source_bindings'][CERT]==sha(C_CERT)
    assert c['status']=='IMPLEMENTED_NOT_ADMITTED' and c['component_validation']=='NOT_RUN' and not c['CP07_exact_admission_resolved'] and not c['correlated_atomicity_verified']
    assert m['status']=='NOT_RUN_SOURCE_ONLY' and not m['component_execution_authorized'] and not m['functional_execution_authorized']
    assert rd(DRAFT)['schema']!='d5.joint-capture-authority.v2' and not rd(DRAFT)['capture_authority']
    g=rd(OUT);assert len(g['nodes'])==495 and sum(x['sha256'] is not None for x in g['nodes'])==491
    assert {x['logical_runtime_path'] for x in g['nodes'] if x['sha256'] is None}==PENDING
    assert set(g['topological_candidate_order'])=={x['logical_runtime_path'] for x in g['nodes']}
    pos={p:i for i,p in enumerate(g['topological_candidate_order'])}
    assert all(pos[q]<pos[row['logical_runtime_path']] for row in g['nodes'] for q in row['hash_dependencies'])
    assert all(pos[x['prerequisite']]<pos[x['consumer']] for x in g['protocol_only_dependencies'])
    assert all(row['sha256'] is None or sha(row['candidate_bytes_source'])==row['sha256'] for row in g['nodes'])
    assert g['candidate_state_Reader_bound']['read_upper_bytes']<266536487<268435456
    assert r['limits']==c['numeric_candidates']==rd(REG)['overrides']['limits']==rd(CONTRACT)['product_numeric_candidates']
    for p in PENDING|{P+'D5-JOINT-P01',P+'D5-JOINT-P01-launch.json'}:assert not (ROOT/p).exists()
    assert sha(CONTRACT)=='e7a873a2aea8648d225f2272854e0b15c3f21de5826df06f16dfb6e45aa54576'
    for k in ['resource_closure_verified','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    changes=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changes==FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I175',proposal='PRP173-INDEX-01',known_bindings=491,unresolved_bindings=4,
        candidate_membership_paths=495,candidate_conditional_read_upper_bytes=g['candidate_state_Reader_bound']['read_upper_bytes'],
        general_PRP173_conditional_read_upper_bytes=266536487,prior_published_files_preserved=354,new_files=9,
        rebind_applied=False,product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,
        independent_acceptance=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':main()
