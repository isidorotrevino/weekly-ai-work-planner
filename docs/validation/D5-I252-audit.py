#!/usr/bin/env python3
"""I252: source-only review of I251. No product/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '6520ef6ecb4083b96ba00126c75eb3bd815c8451'
DATE = '2026-11-25'
SUBJECT = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
PRIOR_AUDIT = P+'D5-I251-audit.py'
PRIOR_PREP = P+'D5-I251-preparation-review.json'
PRIOR_SEAL = P+'D5-I251-integrity.json'
PRIOR_DOC = 'docs/design/D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.md'
PRIOR_FILES = {SUBJECT, PRIOR_AUDIT, PRIOR_PREP, PRIOR_SEAL, PRIOR_DOC}
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
RECON = P+'D5-I252-I251-source-reconstruction.json'
REVIEW = P+'D5-I252-I251-documentary-review.json'
AUDIT = P+'D5-I252-audit.py'
SEAL = P+'D5-I252-integrity.json'
DOC = 'docs/design/D5-I252-I251-GENUINE-EVIDENCE-PLAN-REVIEW.md'
FILES = {RECON, REVIEW, AUDIT, SEAL, DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_I251_ACQUISITION_PLAN_REVIEW_GENUINE_EVIDENCE_AND_ACCEPTANCE_PENDING_NOT_ADMITTED'
OWNERS = [['W01'], ['W02'], ['W03'], ['W04'], ['W05','W06','W07','W08'], ['W09'], ['W10','W11','W12'], ['W13']]
GRAPH = {'A01':[], 'A02':['A01'], 'A03':['A01','A02'], 'A04':['A02','A03'], 'A05':['A03','A04'], 'A06':['A02','A03','A04','A05'], 'A07':['A02','A04','A06'], 'A08':['A01','A02','A03','A04','A05','A06','A07']}


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def pin(path, pointer=''):
    return dict(path=path, sha256=sha(path), json_pointer=pointer)


def fragment(ref):
    assert sha(ref['path']) == ref['sha256'], ref['path']
    value = rd(ref['path'])
    for token in ref.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def pointers(node):
    if isinstance(node,dict):
        if {'path','sha256','json_pointer'} <= set(node):
            fragment(node)
        for value in node.values():
            pointers(value)
    elif isinstance(node,list):
        for value in node:
            pointers(value)


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'], cwd=ROOT,
        input=''.join(BASE+':'+path+'\n' for path in sorted(pins)).encode()))
    for path,digest in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob', path
        body = stream.read(int(header[2]))
        assert stream.read(1)==b'\n' and hashlib.sha256(body).hexdigest()==digest==sha(path), path
    assert not stream.read()


def inspect(d):
    plan = rd(PLAN)
    works = {row['id']:row for row in plan['work_packages']}
    lots = d['acquisition_lots']
    assert [r['id'] for r in lots]==list(GRAPH)
    owner = {work:lot for lot,group in zip(GRAPH,OWNERS) for work in group}
    assert [r['covers_work_packages'] for r in lots]==OWNERS
    assert d['exact_I223_work_dependency_graph']=={key:r['depends_on'] for key,r in works.items()}
    assert d['lot_order']==dict(graph=GRAPH,topological_order=list(GRAPH),acyclic_documentarily_verified=True,actual_lots_accepted=0)
    def ancestors(node):
        result=set()
        pending=list(GRAPH[node])
        while pending:
            parent=pending.pop()
            assert parent != node
            if parent not in result:
                result.add(parent)
                pending.extend(GRAPH[parent])
        return result
    for lot,group in zip(lots,OWNERS):
        lid=lot['id']
        assert lot['depends_on_lots']==GRAPH[lid]
        assert len(lot['W_requirements'])==len(lot['W_documentary_checklists'])==len(group)
        for work,ref,checklist in zip(group,lot['W_requirements'],lot['W_documentary_checklists']):
            req=works[work]
            assert fragment(ref)==req
            assert checklist['path'].startswith(P+'D5-I223-'+work+'-')
            fragment(checklist)
            assert lot['internal_work_dependencies'][work]==req['depends_on']
            assert lot['required_primary_review_roles'][work]==req['primary_review_roles']
            assert lot['separate_acceptor_role']==req['separate_acceptor_role']=='R08'
            for parent in req['depends_on']:
                assert owner[parent]==lid or owner[parent] in ancestors(lid)
        draft=lot['unsent_request_draft']
        assert draft['id']=='RQ'+lid[1:] and draft['recipient']==lot['intended_recipient_role_kind']
        assert draft['text'] and lot['required_material_returns'] and lot['completion_predicate'] and lot['missing_or_failure_stop']
        assert draft['is_draft_only'] is True and draft['sent'] is False and draft['contact_authorized'] is False
        assert lot['accepted'] is False
        assert all(value is None for key,value in lot.items() if key.startswith('actual_'))
    coverage=d['work_package_coverage']
    assert [r['id'] for r in coverage]==list(works)
    for row in coverage:
        assert row['exact_work_requirement']==fragment(row['source'])==works[row['id']]
        assert row['collection_lot']==owner[row['id']] and row['accepted'] is False and row['actual_accepted_delivery_package'] is None
    rows=d['gate_to_collection_matrix']
    assert len(rows)==30 and [r['id'] for r in rows]==[r['id'] for r in plan['gate_closure_matrix']]
    for row,req in zip(rows,plan['gate_closure_matrix']):
        assert fragment(row['source'])==req and row['category']==req['category']
        assert row['required_work_package_ids']==req['producer_work_package_ids']
        assert row['required_collection_lots']==sorted({owner[w] for w in req['producer_work_package_ids']})
        assert row['exact_close_only_if']==req['close_only_if']
        assert row['accepted'] is False and row['actual_evidence_and_competent_decisions'] is None
    assert len(d['resource_acceptance_matrix'])==5
    for row,req in zip(d['resource_acceptance_matrix'],plan['resource_obligation_matrix']):
        assert row['id']==req['id'] and row['exact_requirement']==fragment(row['source'])==req
        assert row['producer_lots']==sorted({owner[w] for w in req['producer_work_package_ids']})
        assert row['accepted'] is False and row['closed'] is False
        assert row['actual_complete_bound_same_scope_assumptions_primary_review_and_R08_acceptance'] is None
    for key,child,source in [('evidence_delivery_contract','exact_contract','evidence_package_contract'),
        ('critical_order_rules','exact_order','scope_authentication_and_freeze_order'),
        ('stop_rules','exact_stop_points','stop_and_decision_points'),
        ('preserved_resource_and_cost_rules','exact_policy','resource_and_scope_policy'),
        ('final_route_boundary','exact_boundary','prelaunch_handoff_and_CE12'),
        ('authority_boundary','exact_inherited_boundary','authorization_boundary')]:
        assert d[key][child]==fragment(d[key]['source'])==plan[source]
    boundary=d['existing_material_boundary']
    assert boundary['exact_existing_material_rule']==fragment(boundary['source'])
    assert boundary['exact_entry_rule']==fragment(boundary['entry_authority_source'])
    assert boundary['actual_material_provider_body_or_own_authority'] is None
    assert boundary['no_external_material_received_or_accepted_by_plan'] is True
    assert d['first_handoff']['next_request_draft_ids']==['RQ01']
    assert d['first_handoff']['after_genuine_A01_acceptance_request_draft_ids']==['RQ02']
    assert d['first_handoff']['next_early_feasibility_request_draft_ids']==['RQ03','RQ04']
    assert d['first_handoff']['all_recipient_persons_addresses_channels_and_contact_authority'] is None
    assert [r['id'] for r in d['real_milestones']]==['M%02d'%i for i in range(1,8)]
    assert [r['lots'] for r in d['real_milestones']]==[['A01'],['A02'],['A03','A04'],['A05'],['A06'],['A07'],['A08']]
    assert len(d['future_authority_resolution_ledger'])==13
    for row,req in zip(d['future_authority_resolution_ledger'],works.values()):
        assert row['work_id']==req['id'] and row['collection_lot']==owner[req['id']]
        assert row['exact_separate_action_classes']==fragment(row['source'])==req['needs_separate_future_authority_for']
        assert row['authorized_now'] is False and row['actual_operational_authority'] is None
    flow=d['intake_and_review_workflow']
    assert flow['actual_received_inventory'] is None and flow['provided_real_bodies']==flow['rejected_real_bodies']==[]
    assert type(flow['actual_primary_decisions']) is int and flow['actual_primary_decisions']==0
    assert type(flow['actual_separate_acceptances']) is int and flow['actual_separate_acceptances']==0
    assert flow['actual_reference_completeness_verified'] is False
    assert flow['allowed_future_dispositions']==['MISSING','PROVIDED_NOT_ACCEPTED','REJECTED_WITH_TRACEABLE_REASON','ACCEPTED_ONLY_BY_GENUINE_AUTHORIZED_ROLES']
    assert d['final_route_boundary']['receipt_gate']==plan['deferred_gate']
    contract=rd(P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json')
    assert d['preserved_resource_and_cost_rules']['exact_candidate_reserve_rules']==contract['reserve_accounting']
    assert d['preserved_scope_and_gates']=={key:plan[key] for key in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']}
    w13=rd(P+'D5-I223-W13-PRELAUNCH-GATE-DECISION-CANDIDATE.json')
    assert d['current_no_admission']==w13['non_admission_record']
    expected={key:value for key,value in w13['current_effect'].items() if key!='W13_documentary_prepared'}
    expected.update(I251_acquisition_plan_and_unsent_drafts_prepared=True,actual_material_obtained_or_independent_acceptance_or_lot_completion=False,
        provider_contact_or_nomination_done=False,actual_sources_implementation_or_build_created=False,actual_acquisition_lots_accepted=0)
    assert d['current_effect']==expected
    assert d['producer']['actor_independent'] is False and d['producer']['competent_R06_review'] is False
    assert d['producer']['separate_R08_acceptance'] is False and d['producer']['external_contacts_made'] is False
    pointers(d)
    return dict(lot_to_work_packages={r['id']:r['covers_work_packages'] for r in lots},lot_graph=GRAPH,
        gate_producer_lots={r['id']:r['required_collection_lots'] for r in rows},
        resource_producer_lots={r['id']:r['producer_lots'] for r in d['resource_acceptance_matrix']},
        next_unsent_request='RQ01',next_after_genuine_A01_acceptance='RQ02',
        actual_material_packages=0,actual_lots_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0)


CRITERIA = [
    'Eight finite lots cover all thirteen W packages exactly once with eight unsent requests and seven genuine milestones.',
    'Every primary review role, separate R08, deliverable and rejection requirement remains bound to I223 and W checklists.',
    'Independent transitive graph check preserves all W edges including internal A05 and A07 order without backward authentication.',
    'A01 needs genuine preexisting scope/reviewer authority, never future A02 appointments or A07 signatures as its sole basis.',
    'A02 is provisional identity intake, retaining all exclusions and qualified R01/R02 overlap, not final author completeness.',
    'A03 distinguishes existing qualified genuine six-source/image/runtime material from separately authorized missing implementation/build/qualification.',
    'A04 requires enforceable exact caller/platform/capacity/service/clock/global-ledger premises before expensive derived proofs.',
    'W05 successor 179/321/12/30 and new routes need requalification; historical CP03 and written atomicity do not transfer.',
    'W06 requires all eleven heap/lifetime owners, overhead, compatible availability and real fit; budgets/reserves are not evidence.',
    'W07 requires all thirty work groups, compatible CPU/IO/service units and full global costs, not ten activities or scalar counts.',
    'W08 keeps t0/tR/exact-True tW/tF, successful cleanup and 60/750/60+30 with service/liveness proof, not watchdog success.',
    'A06 preserves five obligations/twenty criteria and seven index proof kinds plus separate BASIS review, with authentic authors/baseline before W09.',
    'A07 final freeze reconciles the same prior facts; changed scope/authority invalidates affected A01-A08 without retrospective acceptance.',
    'W10-W12 retain complete roster/caps, exact C and acceptance, three same-core domain approvals and intrinsic global mapping.',
    'Thirty gate mappings preserve every exact producer and close-only-if; W13 is current output, not its own accepted predecessor.',
    'Five resource rows preserve complete exact requirements and producer lots; no partial positive becomes joint closure.',
    'Mandatory returns include complete bodies, provenance, all assumptions, canonical roles, independent decisions and currentness.',
    'Unknown actual material/reference inventory remains null; templates, hashes, flags, signatures and budgets do not establish truth.',
    'Thirteen future operational action classes remain unauthorized; no selected people, contact channels, delivery facts or dates are invented.',
    'Four preclaim prerequisites and actual claim/construction before private receipt remain separate from prelaunch acceptance.',
    'Both Readers, new paths and failures retain complete global heap/work/IO/crypto/service/phase costs and unchanged reserves.',
    'SD01 and eight stop rules preserve no admission without asserting global material absence or infeasibility.',
    'Actual external evidence, canonical appointments, eligible independent review and acceptance remain absent despite publication.',
    'I122/CP07/component/PJC115-R2/D5/IR03 negative state is preserved with no authority, destination, quota or runtime changes.'
]


def reconstruct():
    d=rd(SUBJECT)
    result=inspect(d)
    pins={**d['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1057
    verify_blobs(pins)
    return dict(schema='d5.i252-source-reconstruction.v1',increment='I252',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),input_pins=pins,independent_reconstruction=result,
        criteria=[dict(id='RV%02d'%(i+1),criterion=text,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,text in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'I251_acquisition_plan_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('lot_omission',('acquisition_lots',),d['acquisition_lots'][:-1]),
        ('lot_dependency_removed',('acquisition_lots',6,'depends_on_lots'),['A02','A04']),
        ('work_coverage_duplicated',('acquisition_lots',4,'covers_work_packages'),['W05','W06','W06','W08']),
        ('primary_reviewer_removed',('acquisition_lots',3,'required_primary_review_roles','W04'),['R02','R06']),
        ('separate_role_substitution',('acquisition_lots',0,'separate_acceptor_role'),'R06'),
        ('request_sent',('acquisition_lots',7,'unsent_request_draft','sent'),True),
        ('contact_granted',('acquisition_lots',3,'unsent_request_draft','contact_authorized'),True),
        ('fabricated_provider',('acquisition_lots',5,'actual_provider_persons'),['UNVERIFIED_TEST_LABEL']),
        ('fabricated_duration',('acquisition_lots',2,'actual_date_or_duration_guarantee'),'UNVERIFIED_TEST_LABEL'),
        ('package_accepted',('work_package_coverage',8,'accepted'),True),
        ('coverage_source_substitution',('work_package_coverage',0,'exact_work_requirement','primary_review_roles'),['R01']),
        ('gate_omission',('gate_to_collection_matrix',),d['gate_to_collection_matrix'][:-1]),
        ('producer_lot_omitted',('gate_to_collection_matrix',0,'required_collection_lots'),[]),
        ('close_predicate_removed',('gate_to_collection_matrix',0,'exact_close_only_if'),[]),
        ('resource_omission',('resource_acceptance_matrix',),d['resource_acceptance_matrix'][:-1]),
        ('resource_accepted',('resource_acceptance_matrix',4,'accepted'),True),
        ('contact_before_authority',('first_handoff','next_request_draft_ids'),['RQ01','RQ02']),
        ('A02_authority_skipped',('first_handoff','after_genuine_A01_acceptance_request_draft_ids'),['RQ03']),
        ('milestone_omitted',('real_milestones',),d['real_milestones'][:-1]),
        ('future_operation_authorized',('future_authority_resolution_ledger',12,'authorized_now'),True),
        ('inventory_fabricated',('intake_and_review_workflow','actual_received_inventory'),[]),
        ('genuine_review_fabricated',('intake_and_review_workflow','actual_primary_decisions'),1),
        ('deferred_receipt_changed',('final_route_boundary','receipt_gate','status'),'ACCEPTED_TEST_LABEL'),
        ('reserve_applied',('preserved_resource_and_cost_rules','exact_candidate_reserve_rules','heap','allocated_total_bytes'),1),
        ('D5_promoted',('current_effect','D5_closed'),True),
        ('assistant_as_independent',('producer','actor_independent'),True)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d)
        node=mutant
        for key in path[:-1]:
            node=node[key]
        node[path[-1]]=value
        try:
            inspect(mutant)
        except AssertionError:
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review(rec):
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists=Path.exists
    assert previous['build_candidate']()==rd(SUBJECT)
    prep=previous['build_review']()
    assert prep==rd(PRIOR_PREP) and Path.exists is exists
    return dict(schema='d5.i252-documentary-review.v1',increment='I252',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_ACQUISITION_PLAN_CONSISTENT_GENUINE_EVIDENCE_AND_ACCEPTANCE_NOT_OBTAINED',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1057,acquisition_lots=8,unsent_requests=8,work_packages=13,milestones=7,prelaunch_gates=30,
            resource_obligations=5,resource_criteria=20,review_criteria=len(CRITERIA),future_authority_requirements=13,
            actual_material_packages=0,actual_lots_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I251_rejection_checks=prep['rejection_checks'],additional_I252_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'Review is methodological by the same assistant; no R06 or R08 decision, canonical appointment, material delivery or actual acceptance is made.',
            'Next real input is preexisting scope/reviewer authority for RQ01, then RQ02 only after genuine A01 acceptance. Requests remain local unsent drafts with no recipient or contact authority.',
            'A03 qualified existing artifacts and A04 enforceable platform premises are early feasibility decisions; missing material requires exact separate scope/authority, never synthetic evidence or an implicit run.',
            'Seven index proof kinds are E01-E05,CP03,ATOMICITY; BASIS has a separate R06 basis review. The A06 wording does not collapse BASIS into an eighth index proof or waive it.',
            'All actual authors and baseline facts must already be authenticated before A06/W09. A07 final freeze reconciles identical facts and cannot retroactively provide their sole authority.',
            'Thirty prelaunch gates and five resource obligations remain pending; CE12 and final execution authority remain separately deferred. Another documentary PASS is no substitute for genuine material.'],
        source_reconstruction=dict(primary_source_checks=True,I251_candidate_and_preparation_reproduced=True,
            prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I251',documentary_review_only=True,
            actor_independent=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I252-audit.py',expected_result=STATUS,
            runtime_harness='N/A: source-only documentary JSON/Git/hash/graph/roles/coverage checks and in-memory documentary mutations. No product/component import, compilation, execution, discovery, tests, build, benchmark, crypto, signing, provisioning, contact, platform/clock/ledger/CPU/IO/endpoint probes or active configuration.',
            over400_lines=True,reason='Single review unit with source pins, primary reconstruction, rejection checks and preservation; overage declared, no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_evidence_acceptance_authority_execution_or_D5_closure=True))


def main():
    rec=reconstruct()
    assert rec==rd(RECON)
    review=build_review(rec)
    assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published744'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==749
    seal=rd(SEAL)
    assert seal['schema']=='d5.i252-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published749']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,input_pins=1057,preserved_published_files=749,new_files=5,review_criteria=len(CRITERIA),
        inherited_rejections=len(review['inherited_I251_rejection_checks']),additional_rejections=len(review['additional_I252_rejection_checks']),
        findings=review['findings'],SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
