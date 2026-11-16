#!/usr/bin/env python3
"""I176 documentary candidate graph review; no target execution, imports or compilation."""
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


def validate_preparation():
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
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)


REVIEW_BASE='1ca7da0aa697ac88dc24271d86da861dd3e4d17e'
NEW_REVIEW=P+'D5-I176-I175-documentary-review.json'
RECON=P+'D5-I176-I175-source-reconstruction.json'
NEW_AUDIT=P+'D5-I176-audit.py'
NEW_SEAL=P+'D5-I176-integrity.json'
NEW_DESIGN='docs/design/D5-I176-PRP173-CANDIDATE-GRAPH-REVIEW.md'
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
    pins={**rd(OUT)['input_pins'],**{p:sha(p) for p in FILES}}
    blobs=review_blobs(pins)
    def doc(p):return json.loads(blobs[p])
    g=doc(OUT);old_r=doc(REG);r=doc(C_REG);cert=doc(C_CERT);man=doc(C_MAN);draft=doc(DRAFT)
    # Derive permitted metadata changes rather than accepting the preview labels.
    rcopy=copy.deepcopy(r);assert rcopy['overrides']['required_prior_inputs'].pop(INDEX)==pins[INDEX]
    assert rcopy==old_r
    ccopy=copy.deepcopy(cert)
    for k in ['source_bindings','source_binding_count']:ccopy[k]=doc(CERT)[k]
    assert ccopy==doc(CERT)
    mcopy=copy.deepcopy(man);mcopy['source_bindings']=doc(MAN)['source_bindings']
    assert mcopy==doc(MAN)
    prior=set(r['overrides']['required_prior_inputs']);impl=set(r['overrides']['implementation_sources'])
    known=prior|impl|{REG,CERT,CAP,MAN};capture=known|{RAW,RESULT,COMPSEAL};union=capture|{AUTH}
    assert len(prior)==481 and len(impl)==6 and len(known)==491 and len(capture)==494 and len(union)==495
    alias={REG:C_REG,CERT:C_CERT,MAN:C_MAN}
    candidates={p:dict(path=alias.get(p,p),sha256=pins[alias.get(p,p)],bytes=len(blobs[alias.get(p,p)])) for p in known}
    assert len({v['path'] for v in candidates.values()})==491
    rows={x['logical_runtime_path']:x for x in g['nodes']};assert len(rows)==len(g['nodes'])==495 and set(rows)==union
    for p in union:
        row=rows[p];assert row['in_capture_inputs']==(p!=AUTH) and row['in_Input_Reader_union']
        if p in known:
            assert (row['candidate_bytes_source'],row['sha256'],row['bytes'])==(candidates[p]['path'],candidates[p]['sha256'],candidates[p]['bytes'])
        else:
            assert row['candidate_bytes_source'] is row['sha256'] is row['bytes'] is None
    expected_c_sources=prior|impl|{REG,CAP}
    assert cert['source_bindings']=={p:candidates[p]['sha256'] for p in expected_c_sources}
    assert cert['source_binding_count']==len(expected_c_sources)==489 and CERT not in expected_c_sources
    expected_m_sources=impl|{REG,CAP,CERT}
    assert man['source_bindings']=={p:candidates[p]['sha256'] for p in expected_m_sources}
    assert man['source_binding_count']==len(expected_m_sources)==9
    assert all(man[k] is None for k in ['raw_sha256','result_sha256','seal_sha256'])
    assert draft['known_capture_inputs']=={p:v['sha256'] for p,v in candidates.items()}
    assert draft['registry_sha256']==pins[C_REG]
    assert {x['path'] for x in draft['unresolved_capture_inputs']}=={RAW,RESULT,COMPSEAL}
    assert all(x['sha256'] is None for x in draft['unresolved_capture_inputs'])
    assert draft['schema']=='d5.i175-authority-binding-draft.v1' and draft['phase']=='NOT_AUTHORIZED' and not draft['capture_authority']
    assert draft['authority_sha256'] is None and not draft['authority_body_materialized']
    # Independently rebuild packaging edges and use Kahn ordering, including
    # the raw->manifest protocol prerequisite separately from byte-hash edges.
    hash_edges={p:set() for p in union}
    hash_edges[INDEX]=impl|{CAP}
    hash_edges[REG]=prior|impl|{CAP,r['base_registry']}
    hash_edges[CERT]=expected_c_sources;hash_edges[MAN]=expected_m_sources
    hash_edges[RESULT]={RAW,MAN};hash_edges[COMPSEAL]=expected_m_sources|{RAW,RESULT,MAN};hash_edges[AUTH]=capture
    assert all(set(rows[p]['hash_dependencies'])==hash_edges[p] for p in union)
    combined={p:set(edges) for p,edges in hash_edges.items()};combined[RAW].add(MAN)
    assert all(q in union for edges in combined.values() for q in edges)
    pending={p:set(edges) for p,edges in combined.items()};order=[]
    while pending:
        ready=sorted(p for p,edges in pending.items() if not edges)
        assert ready,'candidate dependency cycle'
        order.extend(ready)
        for p in ready:del pending[p]
        for edges in pending.values():edges.difference_update(ready)
    provided=g['topological_candidate_order'];assert len(provided)==495 and set(provided)==union
    position={p:i for i,p in enumerate(provided)}
    assert all(position[q]<position[p] for p,edges in combined.items() for q in edges)
    envelopes={x['path']:x['max_serialized_bytes'] for x in doc(PROP)['byte_envelopes']['variable_members']}
    known_bytes=sum(v['bytes'] for v in candidates.values());unknown_upper=sum(envelopes[p] for p in union-known)
    unique=known_bytes+unknown_upper;reads=3*unique+4852460
    assert known_bytes==87114629 and unknown_upper==68864 and unique==87183493 and reads==266402939
    assert 268435456-reads==2032517 and reads<266536487<268435456
    assert g['candidate_state_Reader_bound']['known_real_unique_bytes']==known_bytes
    assert g['candidate_state_Reader_bound']['read_upper_bytes']==reads
    for p in [REG,CERT,CAP,MAN,INDEX]:assert candidates[p]['bytes']<=envelopes[p]
    assert cert['status']=='IMPLEMENTED_NOT_ADMITTED' and cert['component_validation']=='NOT_RUN'
    assert not cert['CP07_exact_admission_resolved'] and not cert['correlated_atomicity_verified']
    assert man['status']=='NOT_RUN_SOURCE_ONLY' and not man['component_execution_authorized'] and not man['functional_execution_authorized']
    assert r['overrides']['limits']==cert['numeric_candidates']==old_r['overrides']['limits']==doc(CONTRACT)['product_numeric_candidates']
    # Bind all nine inherited packaging witnesses afresh. No target invocation.
    proposal=doc(PROP);witnesses=proposal['source_evidence']['anchors']
    trees={p:ast.parse(blobs[p].decode()) for p in {a['path'] for a in witnesses}};anchors=[]
    for a in witnesses:
        n=trees[a['path']]
        for part in a['symbol'].split('.'):
            matches=[x for x in ast.iter_child_nodes(n) if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name==part]
            assert len(matches)==1;n=matches[0]
        h=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()
        assert (n.lineno,n.end_lineno,h)==(a['line'],a['end_line'],a['AST_sha256'])
        anchors.append(dict(path=a['path'],symbol=a['symbol'],source_sha256=pins[a['path']],line=n.lineno,end_line=n.end_lineno,AST_sha256=h))
    return dict(schema='d5.i176-i175-source-reconstruction.v1',increment='I176',date='2026-11-16',base_commit=REVIEW_BASE,input_pins=pins,
        method='Fresh Git blobs, permitted-field diffs, independent logical-path alias resolution, exact source-binding sets and Kahn order for hash+protocol edges.',
        methodologically_separate=True,actor_independent=False,organizationally_independent=False,
        metadata_checks=[dict(logical_path=p,candidate_path=q,sha256=pins[q],bytes=len(blobs[q]),original_sha256=pins[p],
            active_original_preserved=True) for p,q in alias.items()],
        binding_ledger=[dict(logical_path=p,bytes_source=candidates[p]['path'],sha256=candidates[p]['sha256'],bytes=candidates[p]['bytes']) for p in sorted(known)],
        unresolved=[dict(logical_path=p,sha256=None,bytes=None,reason='No real authorized component/authority record; no fabricated closing hash.') for p in sorted(union-known)],
        descriptor_check=dict(path=DRAFT,sha256=pins[DRAFT],bytes=len(blobs[DRAFT]),separate_non_authority_schema=True,not_in_physical_union=True),
        independent_topological_order=order,hash_edges_and_protocol_prerequisite_acyclic=True,
        graph_scope='Current packaging dependencies only; frozen historical nodes are opaque byte leaves and archive refs retain old commit/hash identities. Not a global resource/semantic proof.',
        manifest_late_output_nulls_intentional_to_avoid_cycle=True,
        accounts=[dict(reader=name,known_exact_bytes=known_bytes,unknown_four_upper_bytes=unknown_upper,unique_upper_bytes=unique,
            additional_fresh_upper_bytes=4852460,conditional_read_upper_bytes=reads,read_limit=268435456,conditional_margin_bytes=2032517,
            only_exact_negative_candidate_state=True,positive_successor_requires_new_hashes_and_checks=True)
            for name in ['coordinator_input_Reader','worker_input_Reader']],
        general_PRP173_upper_still_conditional=dict(read_upper_bytes=266536487,margin_bytes=1898969,actual_positive_graph_accepted=False),
        source_anchor_checks=anchors,
        counts=dict(input_pins=len(pins),physical_paths=495,known_bindings=491,unresolved_bindings=4,source_bindings_certificate=489,
            source_bindings_components=9,metadata_overrides=3,authority_descriptors=1,source_anchors=9),
        resource_obligations_closed=0,execution_count=0)


CHECKS=[
    ('R01','495-member candidate membership,491 real SHA bindings and four explicit missing bodies','PASS_CANDIDATE_MEMBERSHIP_AND_BYTES'),
    ('R02','Only permitted registry/certificate/manifest binding fields changed in separate previews','PASS_ALLOWED_DOCUMENTARY_DIFF'),
    ('R03','All480 historical prior inputs retained and one index appended','PASS_GRAPH_DESIGN_ONLY_NO_REBIND'),
    ('R04','489 certificate sources and nine manifest sources resolve to exact candidate bytes','PASS_EXACT_CANDIDATE_BINDINGS'),
    ('R05','Distinct non-authority descriptor with491 known pins and three unresolved components','PASS_DESCRIPTOR_SCOPE_ONLY'),
    ('R06','Four absent runtime bodies not replaced by fake hashes or PASS','PASS_NEGATIVE_EVIDENCE_DISCLOSURE'),
    ('R07','Kahn reconstruction of hash edges plus raw/manifest protocol prerequisite','PASS_SCOPED_ACYCLIC_ORDER'),
    ('R08','Manifest late-consumer nulls avoid cycles and certificate/authority do not self-pin','PASS_CURRENT_BINDING_RULE'),
    ('R09','Archive refs remain in historical commit, not candidate path aliases','PASS_DECLARED_ARCHIVE_SCOPE'),
    ('R10','Negative candidate read upper266402939 and margin2032517 per Reader','PASS_CONDITIONAL_BYTE_ACCOUNT'),
    ('R11','PRP173 general envelope and future positive bytes still need recheck','PASS_CONDITIONAL_SCOPE_ONLY'),
    ('R12','Negative certificate/manifest/index, E01-E05 and E06 NOT_RUN preserved','INSUFFICIENT_FOR_ADMISSION'),
    ('R13','Source schema/hash checks are not actual parser/component execution or trust acceptance','PASS_STATIC_METHOD_DISCLOSURE'),
    ('R14','Same actor and no independent resource/packaging/custodian acceptance','PASS_PROVENANCE_DISCLOSURE'),
    ('R15','Active metadata, gates, quotas, source, authority and capture unchanged','PASS_PRESERVATION_ONLY'),
    ('R16','Complete positive final graph remains unavailable until evidence and exact admission','NO_ACTUAL_FINAL_GRAPH_ACCEPTANCE')]


def review_record(rec):
    g=rd(OUT)
    return dict(schema='d5.i176-i175-documentary-review.v1',increment='I176',date='2026-11-16',base_commit=REVIEW_BASE,
        proposal_id='PRP173-INDEX-01',status='DOCUMENTARY_CONFORMANT_NEGATIVE_CANDIDATE_GRAPH_FOUR_HASHES_UNRESOLVED_NOT_ADMITTED',
        input_pins={**rec['input_pins'],RECON:sha(RECON)},reconstruction=pin(RECON),
        provenance=dict(reviewer='Codex assistant in same chat; also prepared I175',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,independent_reviewer_identity=None,
            independent_acceptance=False,custodian_acceptance=False),
        checks=[dict(id=i,scope=s,result=r,resource_obligation_closed=False) for i,s,r in CHECKS],
        findings=dict(blocking_documentary_defects=[],confirmed_candidate_bindings=491,confirmed_unresolved_paths=4,
            admission_blocks=[
                'Raw/result/seal and final authority byte hashes remain absent; descriptor is not runtime authority.',
                'Current index and candidate certificate/manifest are negative; complete E01-E05 and E06 evidence not supplied.',
                'Independent resource/provenance/packaging approval, positive successor and final binding-impact review absent.',
                'Positive final bytes/pins, Reader/directory/output envelopes and exact separate admission still require review.'],
            scoped_acyclicity_not_global_semantic_or_resource_closure=True),
        counts=rec['counts'],
        verdict=dict(documentary_conformance=True,known_bindings=491,unresolved_bindings=4,
            conditional_negative_candidate_read_upper_bytes=266402939,conditional_margin_bytes=2032517,
            actual_positive_final_graph_accepted=False,independent_acceptance=False,resource_obligations_closed=0,
            rebind_applied=False,proposal_enabled=False,D5_closed=False),
        decision=g['decision'],E06=g['E06'],
        next_evidence_required='Keep no admission. Obtain competent accepted resource/packaging evidence and separately authorized E06, successor index and regenerated final metadata; bind actual component records and authority last, then review final scoped graph/bytes/cycles/outputs before separate rebind. No execution or quotas/source change authorized here.',
        work_unit=dict(rollback_files=sorted(NEW_FILES),verification_command='python3 docs/validation/D5-I176-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary candidate graph review; product/component execution prohibited.',over400_lines=True,
            reason='Self-contained historical checks,491-member byte reconstruction and explicit unresolved binding review; overage reported.'),
        git_publication=dict(commit_and_push_all_requested=True,publication_not_admission=True))


def main():
    validate_preparation()
    rec=reconstruct();assert rd(RECON)==rec and rd(NEW_REVIEW)==review_record(rec)
    prior=rd(SEAL);preserved={**prior['preserved_published354'],**prior['artifacts'],SEAL:sha(SEAL)};seal=rd(NEW_SEAL)
    assert len(preserved)==363 and seal['preserved_published363']==preserved
    assert seal['schema']=='d5.i176-integrity.v1' and seal['base_commit']==REVIEW_BASE and seal['date']=='2026-11-16'
    assert set(seal['artifacts'])==NEW_FILES-{NEW_SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    for k in ['resource_closure_verified','independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    assert rec['counts']['input_pins']==671
    changes=set(git('diff',REVIEW_BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changes==NEW_FILES,changes
    subprocess.check_call(['git','merge-base','--is-ancestor',REVIEW_BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=REVIEW_BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I176',proposal='PRP173-INDEX-01',documentary_conformance=True,
        physical_paths=495,known_bindings=491,unresolved_bindings=4,conditional_negative_candidate_read_upper_bytes=266402939,
        actual_positive_final_graph_accepted=False,prior_published_files_preserved=363,new_files=5,rebind_applied=False,
        product_or_components_executed=0,quotas_changed=False,resource_obligations_closed=0,independent_acceptance=False,
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':main()
