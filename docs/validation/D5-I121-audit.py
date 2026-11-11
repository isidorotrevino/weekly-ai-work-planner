#!/usr/bin/env python3
"""I121 read-only documentary audit. PASS verifies a rejection, not atomicity.

Uses AST/JSON/hash/arithmetic only. No candidate/product/component imports,
compilation, execution, captures, quota mutations or external actions.
"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
J='testing/prospective_capture_joint/capture.py'
T='testing/prospective_capture_typed/capture.py'
L='testing/prospective_capture_late/capture.py'

def rd(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def symbol(path,name):
    ns=ast.parse((ROOT/path).read_text()).body
    for part in name.split('.'):
        out=next(n for n in ns if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name==part);ns=out.body
    return out

def pos(n):return n.lineno,n.col_offset

def matches(n,text):
    wanted=ast.dump(ast.parse(text,mode='eval').body,include_attributes=False)
    return sorted([x for x in ast.walk(n) if isinstance(x,ast.expr) and ast.dump(x,include_attributes=False)==wanted],key=pos)

def assignment(n,target):
    return sorted([x for x in ast.walk(n) if isinstance(x,ast.Assign) and any(ast.unparse(t)==target for t in x.targets)],key=pos)

def one(n,text):
    rows=matches(n,text);assert len(rows)==1,(text,len(rows));return rows[0]

def main():
    r=rd(P+'D5-I121-atomicity-review.json');a=rd(P+'D5-I121-admission-decision.json');g=rd(P+'D5-I121-gate-disposition.json');seal=rd(P+'D5-I121-integrity.json')
    assert git('rev-parse','HEAD')==r['base_commit']==a['base_commit']==seal['base_commit']=='50c49678568bae2abeefbe5fec0285f26c628283'
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    assert len(seal['prior_untracked70'])==70
    for pins in (seal['prior_untracked70'],seal['artifacts'],r['source_hashes'],r['predecessors'],a['current_candidate_pins'],a['I120_proposed_snapshot_pins']):
        for p,h in pins.items():assert sha(p)==h,p
    for name in ('D5-I119-integrity.json','D5-I120-integrity.json'):
        prior=rd(P+name)
        for p,h in prior['artifacts'].items():assert sha(p)==h,p
    prior119=rd(P+'D5-I119-integrity.json')
    for p,h in prior119['inherited_inputs477'].items():assert sha(p)==h,p
    assert P+'D5-I121-integrity.json' not in seal['artifacts']
    expected=set(seal['prior_untracked70'])|set(seal['artifacts'])|{P+'D5-I121-integrity.json'}
    assert set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    legacy=rd(P+'D5-I114-reference-source-envelope.json');weights=rd(P+'D5-I115-refined-reference-envelope.json')['site_charge_upper']
    assert len(r['sites'])==r['site_count']==30
    assert {s['site'] for s in r['sites']}=={s['site'] for s in legacy['active_sites']}
    assert r['inactive_historical_sites']==legacy['inactive_sites']==['Q01','Q02','Q03','Q04','Q05','Q06','Q21','Q22']
    for row in r['sites']:
        n=symbol(row['source'],row['symbol'])
        assert (n.lineno,n.end_lineno)==(row['line'],row['end_line'])
        assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==row['AST_sha256']
        assert row['I115_charge_upper']==weights[row['site']]
        assert row['required_correction'] and (row['witness'] is None or row['witness'] in r['witnesses'])
        assert 'COMPOSITE_NOT_PROVEN' in row['status'] or row['status'] in ('CORRELATED_QUOTA_COUNTEREXAMPLE','CORRELATED_PUBLICATION_ORDER_NOT_CERTIFIABLE')
    # Scalar primitive is correctly guarded; do not falsely reject that local fact.
    n=symbol(J,'Recorder.reference');guard=one(n,"fault(proposed <= self.limits['refs'], 'REFERENCE_BUDGET')")
    write=assignment(n,'self.references')[0];assert pos(guard)<pos(write)
    assert any(isinstance(x,ast.With) and ast.unparse(x.items[0].context_expr)=='self._ref_lock' for x in ast.walk(n))
    n=symbol(J,'CausalState.ref');charge=one(n,'self.charge()')
    increment=next(x for x in ast.walk(n) if isinstance(x,ast.AugAssign) and ast.unparse(x.target)=='self.counter')
    assert pos(charge)<pos(increment)
    # W01/W02: existing grouped first publication followed by a failing charge.
    n=symbol(T,'Recorder.owner');drive=assignment(n,'self.drive_identities[ref]')[0];obscharge=one(n,'self.reference(2)')
    assert pos(drive)<pos(obscharge)
    n=symbol(T,'Recorder.constructor');decl=assignment(n,'capture.declarations[ref]')[0]
    charges=matches(n,'capture.reference()');assert len(charges)==2 and pos(charges[0])<pos(decl)<pos(charges[1])
    n=symbol(T,'Recorder.fixture_constructor');decl=assignment(n,'capture.fixture_declarations[ref]')[0]
    charges=matches(n,'capture.reference()');assert len(charges)==2 and pos(charges[0])<pos(decl)<pos(charges[1])
    # W03/W05: an enclosing lock on charge does not enclose the full dependency.
    n=symbol(J,'CausalState.object_ref');assert pos(one(n,'self.external_owner(obj, None)'))<pos(one(n,'self.charge()'))
    n=symbol(J,'CausalState.subcase');assert pos(one(n,'self.thread()'))<pos(one(n,"self.ref('S')"))
    # W04 and the local normalized preflight are both represented honestly.
    n=symbol(J,'DomainState.declaration')
    assert pos(one(n,'super().declaration(obj, identity)'))<pos(one(n,'self.charge(units)'))
    assert pos(one(n,'self.row_budget(group)'))<pos(one(n,'self.charge(units)'))
    assert pos(one(n,'self.row_budget(record)'))<pos(one(n,'self.charge(units)'))
    assert pos(one(n,'self.charge(units)'))<pos(assignment(n,'records[y]')[0])
    base=symbol(J,'CausalState.declaration');assert assignment(base,"self.domains[ctx['test_frame_id'], ctx['subcase_ref'], key]")
    assert 'units = 6' in ast.unparse(n) and 'int(prior is None) + 2 * int(group_new)' in ast.unparse(n)
    # W06/W07/W08/W09: nested methods or mandatory links have later charges.
    n=symbol(J,'Recorder.emit');assert one(n,"self.parent_outcomes.append(dict(context=self.causal.context(), outcome=data.get('outcome')))")
    assert one(n,'super().emit(kind, **data)')
    base=symbol(J,'BaseRecorder.emit');assert one(base,"row['result_refs'].append(len(self.events))")
    n=symbol(J,'DomainState.link');assert pos(one(n,"self.ref('L')"))<pos(one(n,'self.charge(2)'))
    assert pos(one(n,'self.charge(2)'))<pos(one(n,'self.charge(1 + len(witnesses))'))
    n=symbol(J,'DomainState.retain');assert pos(one(n,'super().retain(*args, **kwargs)'))<pos(one(n,'self.charge(1 + len(witnesses))'))
    n=symbol(J,'BaseRecorder.wrap_boundary');assert pos(one(n,'rec.causal.close_call(key, out=projected)'))<pos(one(n,"rec.causal.link(row['parent_call_ref'], key, 'SAME_THREAD_NESTED_CALL')"))
    # W10: actual table insertion precedes its OWN charge on the same source line.
    n=symbol(J,'ParentalState.pipe_return');table=assignment(n,"self.tables['parental_registrations'][key]")[0]
    assert pos(table)<pos(one(n,'self.charge()'))<pos(one(n,'self.pairs.append((key, context, pair[0], pair[1]))'))
    # W11: physical flush/close precedes page-manifest charge.
    n=symbol(T,'Recorder.finish');assert pos(one(n,'self.events.close()'))<pos(one(n,'self.reference(len(self.events.manifest))'))
    sink=symbol(T,'PageSink.flush');assert pos(one(sink,'self.owner.create(name)'))<pos(one(sink,'write_all(fd, b)'))
    # W12: ORACLES binding publication precedes aggregate frame-close charge.
    n=symbol(T,'Recorder.stop');assert pos(one(n,"f['record_links'].append(binding)"))<pos(one(n,"self.reference(len(f['owner_context_refs']) + 1)"))
    # Exit/message row validation is after mutation, not a prospective check.
    n=symbol(J,'CausalState.exit');assert pos(one(n,"row['exit_observations'].append(dict(status='PENDING_PROCESS_EXIT' if code is None else 'OBSERVED_PARENT_RETURN', returncode=code))"))<pos(one(n,'self.row_budget(row)'))
    n=symbol(J,'ParentalState.message');assert pos(one(n,"row['observed_messages'].append(message)"))<pos(one(n,'self.row_budget(row)'))
    # Arithmetic over documentary source traces, never candidate code or fake objects.
    assert len(r['witnesses'])==12
    for name,w in r['witnesses'].items():
        free=w['initial_free'];used=442305-free;pub=[];failure=None
        for i,(op,arg) in enumerate(w['steps']):
            if op=='publish':pub.append(arg);continue
            assert op in ('charge','charge_at_least') and type(arg) is int and arg>=0
            if used+arg>442305:failure=i;break
            used+=arg
        result=w['source_model_result']
        assert failure is not None and pub
        assert result['initial_used']==442305-free and result['used_before_rejection']==used
        assert result['first_rejected_step']==failure and result['published_prefix']==pub
        assert result['unchanged_on_rejection'] is False and result['actual_candidate_executed'] is False
        assert result['reachable_in_fixed_P01_claimed'] is False
    charging=rd(P+'D5-I117-PJC115-R2-design.json')['charging']
    assert charging['old_upper']-charging['copy_weight_refinement_saving']+charging['extra_upper']==r['normal_source_reference_upper_preserved']==333109
    assert r['proposed_reference_quota_unchanged']==442305
    assert r['all30_reviewed'] is True and r['correlated30_site_atomicity_verified'] is False
    assert r['repair_protocol']['status']=='REVIEWED_REQUIREMENT_NOT_IMPLEMENTED'
    assert r['status']=='REJECTED_CURRENT_ATOMICITY_NO_ADMISSION'
    assert a['atomicity_review']['sha256']==sha(a['atomicity_review']['path'])
    assert a['status']=='NO_ADMITIR' and a['decision_complete'] is True
    assert a['current_capacity_status']==a['I120_proposed_capacity_status']=='DRAFT_NOT_ADMITTED'
    assert a['CP03_source_verified'] is True and a['correlated_atomicity_verified'] is False
    assert a['atomicity_repaired'] is False and a['CP07_actual_admission'] is False and a['proposal_enabled'] is False
    current=rd(P+'D5-JOINT-CAPACITY-CERTIFICATE.json');manifest=rd(P+'D5-JOINT-COMPONENTS-MANIFEST.json')
    assert current['CP03_global_resolved'] is False and manifest['status']=='NOT_RUN_SOURCE_ONLY' and manifest['expected_tests']==10
    old=rd(P+'D5-I120-binding-supplement.json')
    cp=old['proposed_replacements'][P+'D5-JOINT-CAPACITY-CERTIFICATE.json']['snapshot']
    assert rd(cp)['CP03_global_resolved'] is True and rd(cp)['correlated_atomicity_verified'] is False
    for missing in a['absent_files']:assert missing['exists'] is False and missing['sha256'] is None and not (ROOT/missing['path']).exists()
    for name in ('D5-JOINT-P01','D5-JOINT-P01-launch.json'):assert not (ROOT/P/name).exists()
    # Admission checks remain before import and fixed capture-path reservation.
    n=symbol(J,'require_admission');text=ast.unparse(n)
    assert "cert.get('status') == 'SOURCE_CAPACITY_VERIFIED'" in text
    assert "cert.get('correlated_atomicity_verified') is True" in text
    assert 'checked_component_metadata(view, reg, manifest)' in text
    launch=symbol(J,'launch');assert pos(one(launch,'authority(root, requested, reg, inputs)'))<pos(one(launch,"reader.directory('docs/validation')"))
    worker=symbol('testing/prospective_capture_joint/worker.py','main')
    assert pos(one(worker,'p.authority(root, requested, reg, inputs)'))<pos(one(worker,"importlib.import_module(entry['runner_module'])"))
    growth=a['append_only_read_growth'];n=(ROOT/(P+'D5-I121-atomicity-review.json')).stat().st_size
    assert n==growth['new_document_bytes']==23939
    assert growth['additional_three_pass_bytes_lower']==3*n==71817
    lo=old['read_schedule']['worker_upper']+3*n
    assert growth['worker_read_lower']==lo==268459538
    assert lo-268435456==growth['over_limit_by_at_least']==24082
    assert growth['review_actually_added_to_runtime'] is False and growth['quota_increase_proposed'] is False
    assert len(a['gates'])==8 and len({x['id'] for x in a['gates']})==8
    assert g['atomicity_verified'] is False and g['admission_decision']=='NO_ADMITIR' and g['requested_positive_objective_achieved'] is False
    for d in (r,a,g):
        assert d['proposal_enabled'] is False and d['D5_closed'] is False and d['IR03']=='NOT_READY' and d['closure'] is False
    assert r['component_tests_executed']==r['functional_campaigns_executed']==0
    assert a['components_executed']==a['functional_campaigns_executed']==0
    print(json.dumps(dict(status='PASS_DOCUMENTARY_REJECTION_ONLY',logical_sites_reviewed=30,abstract_counterexamples=12,atomicity_verified=False,atomicity_repaired=False,admission='NO_ADMITIR',CP03_source_preserved=True,prior_untracked_preserved=70,product_or_components_executed=False,quota_changed=False,naive_append_read_lower=lo,naive_append_over_limit=24082,proposal_enabled=False,D5_closed=False,IR03='NOT_READY')))

if __name__=='__main__':main()
