#!/usr/bin/env python3
"""I123 documentary audit. No candidate/product/component imports or execution."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
D='testing/prospective_capture_joint_i122/'
def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def enc(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).encode()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def fields(path,classes):
    out=set()
    for n in ast.parse((ROOT/path).read_text()).body:
        if isinstance(n,ast.ClassDef) and n.name in classes:
            init=next(x for x in n.body if isinstance(x,ast.FunctionDef) and x.name=='__init__')
            out.update(x.attr for x in ast.walk(init) if isinstance(x,ast.Attribute) and isinstance(x.ctx,ast.Store) and isinstance(x.value,ast.Name) and x.value.id=='self')
    return out

def main():
    x=rd(P+'D5-I123-transient-resource-envelope.json');g=rd(P+'D5-I123-gate-disposition.json');seal=rd(P+'D5-I123-integrity.json')
    assert git('rev-parse','HEAD')==x['base_commit']==seal['base_commit']=='50c49678568bae2abeefbe5fec0285f26c628283'
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    assert len(seal['prior_untracked92'])==92
    for pins in [seal['prior_untracked92'],seal['artifacts'],x['inputs']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert P+'D5-I123-integrity.json' not in seal['artifacts']
    expected=set(seal['prior_untracked92'])|set(seal['artifacts'])|{P+'D5-I123-integrity.json'}
    assert set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    # Keep inherited sealed evidence byte-identical; never run an older audit
    # that assumes the historical exact untracked set.
    old=rd(P+'D5-I122-integrity.json')
    for pins in [old['prior_untracked76'],old['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    for p,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==h,p
    t=ast.parse((ROOT/(D+'atomic.py')).read_text())
    allfn=[n for n in ast.walk(t) if isinstance(n,ast.FunctionDef)]
    for a in x['anchors']:
        n=next(n for n in allfn if n.name==a['name'] and n.lineno==a['line'])
        assert n.end_lineno==a['end_line']
        assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']
    roots=x['root_census']
    f=ast.literal_eval(next(n.value for n in t.body if isinstance(n,ast.Assign) and any(isinstance(z,ast.Name) and z.id=='FIELDS' for z in n.targets)))
    assert list(f)==roots['FIELDS']
    assert set(roots['causal'])==fields(D+'capture.py',['CausalState','ParentalState','DomainState'])|{'external_owner'}
    assert set(roots['pages'])==fields('testing/prospective_capture_typed/capture.py',['PageSink'])|{'_planning','_writes','_reference'}
    K=sum(len(roots[k]) for k in ['FIELDS','causal','pages','bindings']);assert K==62==roots['clone_root_calls']
    p115=rd(P+'D5-I115-refined-reference-envelope.json');p117=rd(P+'D5-I117-PJC115-R2-design.json')
    E=p115['global_event_upper_reused'];J=p115['witness_memberships_upper'];A=p115['owner_origins_upper'];T=p117['charging']['causal_key_upper'];S=p115['subcases_upper'];G=p115['group_keys_upper'];I=p115['normalized_vector_totals']['O']
    assert x['source_cardinalities']==dict(events=E,frames=321,owners=A,causal_keys=T,subcases=S,groups=G,witness_memberships=J,original_records=I,pages=32)
    envelope=rd(P+'D5-I122-CAPTURE-REGISTRY.json');profile=rd(envelope['base_registry']);profile.update(envelope['overrides'])
    fixed=sum(len(enc(profile[k])) for k in ['projection_schemas','parental_contract'])+2*len(enc(profile['limits']))
    assert [b['bytes'] for b in x['JSON_blocks']]==[p117['conditional_structural_sidecar_upper'],E*4096,J*512,5*4096,fixed,32*512]
    assert [b['units'] for b in x['auxiliary_units']]==[1+5*A,1+4*A,1+4*T,1+6*S,1+10*G,1+6*A,1+6*J,1+2*E,1+3*T+E,2+8*I,1+E,4096]
    B=sum(b['bytes'] for b in x['JSON_blocks']);U=sum(b['units'] for b in x['auxiliary_units'])
    c=x['structural_per_clone'];C=B+U;edges=2*B+U;V=K+edges
    assert (B,U,C,edges,V)==(159254395,671170,159925565,319179960,319180022)
    assert c['JSON_bytes']==B and c['auxiliary_units']==U and c['containers_upper']==C
    assert c['child_occurrences_upper']==edges and c['clone_invocations_upper']==V and c['memo_entries_upper']==C
    assert c['logical_memo_operations_upper']==2*V+C==798285609
    assert c['opaque_insert_attempts_upper']==2*I+4==1998
    assert c['container_clone_bound_conditional'] and not c['physical_hash_probes_bounded_as_constant']
    # These formulas are conditional structural results. Never infer resource
    # verification from this audit's arithmetic consistency.
    assert not x['memory']['global_byte_upper_verified']
    assert not x['memory']['ABI_allocation_coefficients_verified']
    assert not x['memory']['failure_and_GC_retention_verified']
    assert not x['memory']['shared_scalar_retention_bytes_verified']
    assert x['memory']['simultaneous_pending_page_bytes_upper']==32*2097152==67108864
    assert x['memory']['pending_page_phase_drafts_upper']==32
    assert x['memory']['all_historical_unique_chunk_payload_upper']==67108864
    assert x['memory']['bodies_plus_unique_chunks_payload_upper']==134217728
    assert x['memory']['payload_bound_is_not_heap_or_RSS_bound']
    assert not x['CPU']['seconds_upper_verified'] and not x['CPU']['whole_campaign_phase_count_verified'] and not x['CPU']['read_snapshot_count_verified']
    contract=rd(P+'D5-I122-CAPACITY-CONTRACT.json');cert=rd(P+'D5-I122-CAPACITY-CERTIFICATE.json')
    assert contract['numeric_candidates']['campaign_seconds']==x['CPU']['campaign_seconds_unchanged']==900
    assert cert['status']=='IMPLEMENTED_NOT_ADMITTED'
    b=rd(P+'D5-I122-binding-review.json')
    # The old plan is pinned, not expanded to new inputs by this review.
    reads=x['physical_file_reads'];assert reads['I122_upper']==266337791 and reads['limit']==268435456
    assert reads['limit']-reads['I122_upper']==reads['headroom']==2097665
    assert not reads['I123_automatically_admitted_as_input']
    assert x['non_execution']==dict(product=False,candidate_import_or_compile=False,components=False,benchmark=False)
    assert not x['limits_changed'] and not g['active_quotas_changed']
    for y in [x,g]:assert not y['proposal_enabled'] and not y['D5_closed'] and y['IR03']=='NOT_READY'
    assert not g['capture_enabled'] and not g['transient_memory_and_CPU_verified']
    assert g['prior_files_preserved']==92 and g['component_tests_executed']==g['functional_campaigns_executed']==0
    assert not g['authority_or_destination_created'] and not g['commit_or_push']
    # Scope excludes all run_data including D4. Only check known authority paths.
    for p in ['docs/validation/D5-JOINT-capture-authorization.json','docs/validation/D5-JOINT-P01','docs/validation/D5-JOINT-P01-launch.json']:
        assert not (ROOT/p).exists(),p
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',roots=K,conditional_clone_visits=V,prior_files_preserved=92,new_artifacts=len(seal['artifacts'])+1,product_or_components_executed=0,memory_global_verified=False,CPU_seconds_verified=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),sort_keys=True))
if __name__=='__main__':main()
