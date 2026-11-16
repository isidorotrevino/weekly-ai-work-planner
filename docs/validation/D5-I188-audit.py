#!/usr/bin/env python3
"""I188 documentary review: Git/JSON/schema DAG/AST relations only. No target or crypto execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='aba30b317a820c63b8c4cf7c8664f97f2a874fd5'
PACK=P+'D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.json'
SPEC=P+'D5-I187-CONTEXT-LAUNCH-CONTRACT-CANDIDATE.json'
OLD_PREP=P+'D5-I187-preparation-review.json'
OLD_AUDIT=P+'D5-I187-audit.py'
PRIOR_SEAL=P+'D5-I187-integrity.json'
OLD_DOC='docs/design/D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.md'
PRIOR_FILES={PACK,SPEC,OLD_PREP,OLD_AUDIT,PRIOR_SEAL,OLD_DOC}
RECON=P+'D5-I188-I187-source-reconstruction.json'
REVIEW=P+'D5-I188-I187-documentary-review.json'
AUDIT=P+'D5-I188-audit.py';SEAL=P+'D5-I188-integrity.json'
DOC='docs/design/D5-I188-I187-CONTEXT-LAUNCH-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('ascii')
def pin(p,pointer):return dict(path=p,sha256=sha(p),json_pointer=pointer)


def children(s):
    for key in ['properties','$defs']:
        yield from s.get(key,{}).values()
    for key in ['oneOf','anyOf']:
        yield from s.get(key,[])
    for key in ['items','propertyNames','additionalProperties']:
        if isinstance(s.get(key),dict):yield s[key]


def references(s):
    if '$ref' in s:
        assert s['$ref'].startswith('#/$defs/')
        yield s['$ref'][8:]
    for q in children(s):yield from references(q)


def schema_rows(s):
    yield s
    for q in children(s):yield from schema_rows(q)


def independent_bounds(defs):
    # Resolve the reference graph in dependency waves, then bound each local
    # tree using already completed references. Independent of I187 recursive resolution.
    deps={n:set(references(s)) for n,s in defs.items()};pending=set(defs);known={};waves=[]
    assert all(v<=set(defs) for v in deps.values())
    def bound(s):
        if '$ref' in s:return known[s['$ref'][8:]]
        if 'const' in s:return len(canonical(s['const']))
        if 'enum' in s:return max(len(canonical(x)) for x in s['enum'])
        if 'anyOf' in s or 'oneOf' in s:return max(bound(q) for q in s.get('anyOf',s.get('oneOf')))
        kind=s['type']
        if kind=='integer':
            assert 0<=s['minimum']<=s['maximum']<=9007199254740991
            return len(str(s['maximum']))
        if kind=='string':return 2*(s['maxLength']+1)
        if kind=='array':
            count=s['maxItems'];return 2+count*(bound(s['items'])+1)-(1 if count else 0)
        if kind=='object':
            if 'properties' in s:
                props=s['properties'];assert set(s['required'])==set(props) and s['additionalProperties'] is False
                return 2+sum(len(canonical(k))+1+bound(v) for k,v in props.items())+max(0,len(props)-1)
            count=s['maxProperties'];assert s['minProperties']<=count<=4096
            return 2+count*(bound(s['propertyNames'])+1+bound(s['additionalProperties'])+1)-(1 if count else 0)
        raise AssertionError(kind)
    while pending:
        ready=sorted(n for n in pending if deps[n]<=set(known));assert ready,'Schema reference cycle'
        for n in ready:known[n]=bound(defs[n]);pending.remove(n)
        waves.append(ready)
    return known,waves


def reconstruct():
    spec=rd(SPEC);pins={**spec['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==734
    req=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    prior=runpy.run_path(str(ROOT/OLD_AUDIT));assert prior['build_review']()==rd(OLD_PREP)
    pack=rd(PACK);defs=pack['$defs'];oldprep=rd(OLD_PREP)
    assert spec['schema_pack']['sha256']==sha(PACK) and len(defs)==55
    assert defs['context_record']==defs['launch_record']=={'$ref':'#/$defs/final_record'}
    assert pack['$ref']=='#/$defs/final_record'
    bounds,waves=independent_bounds(defs)
    rows=[];kinds=set();codes=set()
    old_protocol=rd(spec['protocol_pack_binding']['path'])['$defs']
    for n in ['capture_binding','worker_invocation','worker_ready','parent_release','sha256','identity']:assert defs[n]==old_protocol[n]
    for row in spec['branches']:
        name=row['definition'];s=defs[name];props=s['properties'];kind=props['record_kind']['const']
        assert kind==row['record_kind'] and props['capture_status']['const']==row['capture_status']
        assert kind not in kinds;kinds.add(kind)
        assert 'capture_binding' in s['required'] and props['capture_binding']=={'$ref':'#/$defs/capture_binding'}
        assert 'owner' in s['required'] and props['owner']=={'$ref':'#/$defs/owner'}
        for field in ['closure','D5_closed','publication_authorized']:assert props[field]=={'const':False}
        assert bounds[name]==oldprep['structural_wire_bound']['per_branch_upper_bytes'][kind]
        assert bounds[name]<=12582912
        rows.append(dict(kind=kind,capture_status=row['capture_status'],required_fields=len(s['required']),
            upper_bytes=bounds[name],required_binding_and_owner=True,closed=True))
    assert len(kinds)==7
    bound_values={r['kind']:r['upper_bytes'] for r in rows}
    assert max(bound_values.values())==10798483 and bound_values['BUDGET_FALLBACK']==2314
    assert bounds['no_pair_diagnostic']==315
    assert bound_values['BUDGET_FALLBACK']<=8192 and bounds['no_pair_diagnostic']<=8192
    fixed_objects=bounded_maps=bounded_arrays=0
    for s in schema_rows(pack):
        if s.get('type')=='object':
            if 'properties' in s:
                assert s['additionalProperties'] is False and set(s['required'])==set(s['properties']);fixed_objects+=1
            else:
                assert 'propertyNames' in s and s['maxProperties']<=4096;bounded_maps+=1
        if s.get('type')=='array':assert s['maxItems']<=4096;bounded_arrays+=1
    fall=defs['record_budget_fallback']['properties']['details']['properties']
    assert {'worker_diagnostic','parent_error','omitted_sections','reason','acceptance'}==set(fall)
    assert 'parent_error' not in fall['omitted_sections']['const']
    assert set(fall['omitted_sections']['const'])==set(defs['record_invalid']['properties']['details']['properties'])-{'parent_error'}
    assert defs['record_worker_failure']['properties']['details']['properties']['worker']=={'$ref':'#/$defs/failed_worker'}
    assert defs['failed_worker']['properties']['diagnostic']=={'$ref':'#/$defs/failed_diagnostic'}
    assert defs['successful_worker']['properties']['wait_outcome']=={'const':'WAIT_RETURNED_TRUE'}
    assert defs['successful_worker']['properties']['exit']['properties']['value']['properties']=={'sign':{'const':'NONNEGATIVE'},'magnitude':{'const':0}}
    assert defs['timed_out_worker']['properties']['wait_outcome']=={'const':'WAIT_RETURNED_FALSE'}
    assert defs['completed_reader_receipt']['properties']['completed_phases']=={'const':['BEFORE','AFTER','FINISH']}
    assert defs['completed_reader_receipt']['properties']['input_paths']=={'const':496}
    assert defs['no_pair_diagnostic']['properties']['schema']['const']!='d5.prp181-context-launch.v3'
    levels=spec['validation_levels'];assert set(levels)=={'body','pair','capture_package'}
    assert 'diagnostic only' in levels['capture_package'] or 'Failure metadata' in levels['capture_package']
    rule_ids=[r['id'] for r in spec['rules']];assert rule_ids==['O%02d'%i for i in range(1,14)]
    assert len(spec['branch_selection_order'])==7
    limits=spec['unchanged_numeric_candidates'];assert limits==rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    fixed_artifacts=32*limits['page_bytes']+limits['raw_bytes']+limits['index_sidecar_bytes']+4096
    assert fixed_artifacts+2*limits['context_bytes']==limits['package_bytes']==140513280
    assert fixed_artifacts+2*max(bound_values.values())==136944422
    assert len(oldprep['legacy_fields_covered'])==21 and len(spec['source_anchors'])==6
    assert not spec['output_locations']['created']
    for field in ['context','launch_copy']:assert not (ROOT/spec['output_locations'][field]).exists()
    profile=rd(spec['profile_binding']['path']);assert sha(spec['profile_binding']['path'])==spec['profile_binding']['sha256']
    assert spec['decision']==profile['decision'] and spec['E06']==profile['E06']
    assert spec['current_effect']['F183_01_documentary_repair_preserved'] and not spec['current_effect']['actual_output_fit_verified']
    return dict(schema='d5.i188-i187-source-reconstruction.v1',increment='I188',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git blob verification; independent dependency-wave schema width derivation, exact branch/mandatory-binding/fallback/type joins and inherited AST/projection reconstruction. No target/protocol/crypto run.',
        schema_structure=dict(definitions=55,branches=rows,fixed_object_nodes=fixed_objects,bounded_map_nodes=bounded_maps,bounded_array_nodes=bounded_arrays,
            reference_waves=waves,reference_graph_acyclic=True,identical_context_launch_contract=True),
        independent_wire_derivation=dict(per_branch_upper_bytes=bound_values,largest_body_upper_bytes=10798483,
            metadata_each_cap=12582912,fallback_upper_bytes=2314,no_pair_diagnostic_upper_bytes=315,
            fixed_artifact_caps_total_bytes=fixed_artifacts,conditional_package_upper_with_schema_bodies=136944422,
            unchanged_package_cap=140513280,conditional_package_margin=3568858,
            premise='ASCII/safe-integer canonical bodies, exact schemas and actual unique contiguous artifact/member caps; not a measurement, invocation, heap/CPU/IO proof or actual output fit.'),
        semantic_layers=dict(body_shape_not_actual_observation=True,failure_pair_not_accepted_capture_package=True,
            planned_pair_receipt_not_write_success=True,partial_or_mismatched_copy_invalidates_pair=True,
            pre_admission_no_persistent_pair=True,first_failed_worker_diagnostic_preserved=True,
            unrecorded_not_proof_of_absence=True,wait_return_not_physical_exit=True,
            no_self_or_backward_output_pin=True,signature_or_real_trust_verified=False),
        inherited_scope=dict(profile_id=spec['profile_id'],protocol_pack_preserved=True,legacy_fields_projected=21,AST_anchors=6,
            F183_01_documentary_repair_preserved=True,Reader_paths=496,Reader_design_bytes=266693693,actual_Reader_output_fit=False),
        verdict=dict(new_blocking_documentary_findings=0,documentary_contract_consistent=True,
            adopted=False,implemented=False,implementation_control_flow_verified=False,independent_acceptance=False,
            actual_output_fit_verified=False,F179_01_resolved=False,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    spec=rd(SPEC)
    return dict(schema='d5.i188-i187-documentary-review.v1',increment='I188',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal='PGO181-SPLIT-ROOT-01',profile_id=spec['profile_id'],
        status='CONTEXT_LAUNCH_DOCUMENTARY_CONTRACT_CONFIRMED_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        reconstruction=dict(path=RECON,sha256=sha(RECON)),
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I187 and profile candidates',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,independent_acceptance=False,custodian_acceptance=False),
        findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in [
            ('R01','Complete closed branches/finite maps and arrays/local acyclic refs','PASS_DOCUMENTARY_STRUCTURE'),
            ('R02','Same canonical body for two physically charged copies','PASS_PAIR_CONTRACT_NOT_WRITE_PROOF'),
            ('R03','Binding/owner and no-closure/publication flags in every branch including fallback','PASS_NO_BINDING_ERASURE'),
            ('R04','Seven branch discriminators/priority and truthful worker/parent observations','PASS_SPECIFICATION_NOT_CONTROL_FLOW_PROOF'),
            ('R05','wait return distinct from independently observed signed exit','PASS_TAGGED_OBSERVATION_MODEL'),
            ('R06','Immutable first worker failure separated from parent artifact error','PASS_DECLARED_DIAGNOSTIC_SCOPE'),
            ('R07','Pre-admission no-pair and missing/partial/mismatched/close failure','PASS_FAIL_CLOSED_OUTPUT_CONTRACT'),
            ('R08','Body/pair/capture-package validation levels distinct','PASS_NO_FAILURE_METADATA_PROMOTION'),
            ('R09','Independent55-definition bound10,798,483 and fallback2314/no-pair315','PASS_STRUCTURAL_BYTE_PROOF_NOT_RESOURCE_FIT'),
            ('R10','Two copies and unique capped35-existing-member inventory, no self hash','PASS_CONDITIONAL_PACKAGE_BUDGET'),
            ('R11','21 legacy fields/six AST anchors and complementary source-pinned output schema','PASS_DECLARED_PROJECTION_SOURCE_IMPLEMENTATION_PENDING'),
            ('R12','Profile02, eight S01 exclusions,9 CP07 predicates and unchanged caps','PRESERVED_NOT_ADOPTED'),
            ('R13','Same preparer/reviewer actor; no real signatures/roles/resources','PASS_PROVENANCE_AND_LIMITS_DISCLOSURE')]],
        evidence=[pin(PACK,'/$defs/final_record'),pin(PACK,'/$defs/record_budget_fallback'),pin(SPEC,'/validation_levels'),pin(SPEC,'/rules')],
        verdict=rec['verdict'],current_effect=spec['current_effect'],decision=spec['decision'],E06=spec['E06'],
        remaining_work=['Competent adoption and independent acceptance; actual actor/caller/custody/key/clock/replay evidence remains absent.',
            'Exact successor producer/consumer/guard/bootstrap transport/owner/IO/exception control flow and compiled output/profile packs, in separately authorized scope.',
            'Full179/321/12/30 source scope and E01-E05 requalification with all snapshots/maps/encode/hash/dual writes/fallback costs inside phases; actual Reader/output/heap/CPU and900-second proof.',
            'Actual final E06, payload/root/context/request/signatures and separate admission/execute decision; no positive evidence inferred from this review.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I188-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary output contract review; no runtime implementation/product/component/crypto execution.',over400_lines=True,
            reason='Traceable schema DAG/independent width/branch/projection reconstruction and review seal as one documentary deliverable; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    old=rd(PRIOR_SEAL);preserved={**old['preserved_published420'],**old['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==426
    seal=rd(SEAL);assert seal['schema']=='d5.i188-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published426']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for key in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[key] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I188',new_blocking_documentary_findings=0,
        documentary_contract_consistent=True,output_branches=7,wire_upper_bytes=10798483,historical_pins=734,
        prior_published_files_preserved=426,new_files=5,adopted=False,implemented=False,independent_acceptance=False,
        actual_output_fit_verified=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
