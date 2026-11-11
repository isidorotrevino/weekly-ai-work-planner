#!/usr/bin/env python3
"""Read-only I122 structural audit: AST, hashes, JSON and arithmetic only.

Never import/compile/run candidate, product or component modules. PASS is source
integration/record consistency, not runtime atomicity, resource or capture PASS.
"""
import ast
import builtins
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/';D='testing/prospective_capture_joint_i122/'

def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def enc(x):return json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def node(path,symbol):
    root=ast.parse((ROOT/path).read_text())
    for part in symbol.split('.'):
        found=[]
        def visit(n):
            for c in ast.iter_child_nodes(n):
                if isinstance(c,(ast.ClassDef,ast.FunctionDef)):
                    if c.name==part:found.append(c)
                else:visit(c)
        visit(root);assert len(found)==1,(symbol,part,len(found));root=found[0]
    return root

def pos(n):return n.lineno,n.col_offset

def calls(n,expression):
    want=ast.dump(ast.parse(expression,mode='eval').body,include_attributes=False)
    return sorted([a for a in ast.walk(n) if isinstance(a,ast.expr) and ast.dump(a,include_attributes=False)==want],key=pos)

def one(n,expression):
    out=calls(n,expression);assert len(out)==1,(expression,len(out));return out[0]

def unbound_names(tree):
    def bound(body,args=None):
        out=set()
        if args:
            out.update(x.arg for x in args.posonlyargs+args.args+args.kwonlyargs)
            if args.vararg:out.add(args.vararg.arg)
            if args.kwarg:out.add(args.kwarg.arg)
        class V(ast.NodeVisitor):
            def visit_Name(self,n):
                if isinstance(n.ctx,ast.Store):out.add(n.id)
            def visit_FunctionDef(self,n):out.add(n.name)
            def visit_ClassDef(self,n):out.add(n.name)
            def visit_ExceptHandler(self,n):
                if n.name:out.add(n.name)
                self.generic_visit(n)
            def visit_Import(self,n):out.update(a.asname or a.name.split('.')[0] for a in n.names)
            def visit_ImportFrom(self,n):out.update(a.asname or a.name for a in n.names)
        v=V()
        for n in body:v.visit(n)
        return out
    missing=[]
    def scan(body,parents,path):
        available=parents|bound(body)
        class V(ast.NodeVisitor):
            def visit_Name(self,n):
                if isinstance(n.ctx,ast.Load) and n.id not in available:missing.append((path,n.lineno,n.id))
            def visit_FunctionDef(self,n):
                for x in n.decorator_list+n.args.defaults+[a for a in n.args.kw_defaults if a is not None]:self.visit(x)
                scan(n.body,available|bound([],n.args),path+'.'+n.name)
            def visit_ClassDef(self,n):
                for a in n.bases+n.decorator_list:self.visit(a)
                for a in n.body:
                    if isinstance(a,ast.FunctionDef):self.visit_FunctionDef(a)
                    else:self.visit(a)
            def visit_Lambda(self,n):scan([ast.Expr(n.body)],available|bound([],n.args),path+'.lambda')
        v=V()
        for n in body:v.visit(n)
    scan(tree.body,bound(tree.body)|set(dir(builtins))|{'__name__','__file__'},'atomic')
    return missing

def main():
    proof=rd(P+'D5-I122-atomicity-implementation.json');b=rd(P+'D5-I122-binding-review.json');g=rd(P+'D5-I122-gate-disposition.json');seal=rd(P+'D5-I122-integrity.json')
    assert git('rev-parse','HEAD')==proof['base_commit']==b['base_commit']==seal['base_commit']=='50c49678568bae2abeefbe5fec0285f26c628283'
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    assert len(seal['prior_untracked76'])==76
    for pins in (seal['prior_untracked76'],seal['artifacts'],proof['source_hashes'],b['source_pins'],b['current_known_input_pins']):
        for p,h in pins.items():assert sha(p)==h,p
    for name in ('D5-I119-integrity.json','D5-I120-integrity.json','D5-I121-integrity.json'):
        for p,h in rd(P+name)['artifacts'].items():assert sha(p)==h,p
    for p,h in rd(P+'D5-I119-integrity.json')['inherited_inputs477'].items():assert sha(p)==h,p
    assert P+'D5-I122-integrity.json' not in seal['artifacts']
    expected=set(seal['prior_untracked76'])|set(seal['artifacts'])|{P+'D5-I122-integrity.json'}
    assert set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    # Parsing is the ONLY inspection of the five candidate Python modules.
    for p in proof['source_hashes']:
        if p.endswith('.py'):ast.parse((ROOT/p).read_text())
    tree=ast.parse((ROOT/(D+'atomic.py')).read_text());assert not unbound_names(tree),unbound_names(tree)
    prior=rd(proof['predecessor']['path']);assert sha(proof['predecessor']['path'])==proof['predecessor']['sha256']
    assert {r['site'] for r in proof['rows']}=={r['site'] for r in prior['sites']} and len(proof['rows'])==30
    for r in proof['rows']:
        n=node(D+'atomic.py',r['phase'])
        assert (n.lineno,n.end_lineno)==(r['phase_line'],r['phase_end_line'])
        assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==r['phase_AST_sha256']
        assert r['status']=='IMPLEMENTED_DRAFT_COMMIT_PATH_NOT_EXECUTED' and r['common_dispatch']=='build.Recorder._atomic'
    export=(ROOT/(D+'capture.py')).read_text()
    assert 'Recorder,LateBindings=_atomic_build(sys.modules[__name__])' in export
    core=node(D+'atomic.py','build.Recorder._atomic')
    op=one(core,'operation(draft)');publish=one(core,'self._publish(draft)')
    assert pos(op)<pos(one(core,"p.fault(draft._rejection is None, draft._rejection or 'CAUSAL_SCHEMA_INVALID')"))<pos(publish)
    guard=one(core,"p.fault(type(draft.references) is int and self.references <= draft.references <= self.limits['refs'], 'REFERENCE_BUDGET')")
    assert pos(guard)<pos(publish)
    lock=next(n for n in ast.walk(core) if isinstance(n,ast.With) and ast.unparse(n.items[0].context_expr)=='self._state_lock')
    create=one(core,'self.events.owner.create(name)');write=one(core,'p.write_all(fd, body)')
    assert create.lineno>lock.end_lineno and write.lineno>lock.end_lineno
    assert 'not self._state_lock._is_owned()' in ast.unparse(core)
    assert sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='_publish' for n in ast.walk(tree))==1
    fork=node(D+'atomic.py','build.Recorder._fork')
    assert one(fork,'opaque_originals(self)') and one(fork,'clone_metadata(getattr(self, field), memo, opaque)')
    assert 'causal.charge = draft.reference' in ast.unparse(fork) and 'causal.external_owner = draft.owner' in ast.unparse(fork)
    assert not any(isinstance(n,ast.Attribute) and n.attr in ('read','read_bytes','prepare','check') for n in ast.walk(fork))
    clone=node(D+'atomic.py','clone_metadata');assert not any(isinstance(n,ast.Attribute) and n.attr in ('__deepcopy__','__copy__','deepcopy') for n in ast.walk(clone))
    assert 'if key in opaque' in ast.unparse(clone) and 'if key in memo' in ast.unparse(clone)
    opaque=node(D+'atomic.py','opaque_originals');text=ast.unparse(opaque)
    for field in ('record_refs','record_baselines','oracle_guards','causal_sources'):assert field in text
    fields=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='FIELDS' for x in n.targets)))
    assert len(fields)==len(set(fields)) and {'frames','active','record_refs','references','errors','owner_contexts','parent_snapshots','parent_assertions','parent_outcomes'}<=set(fields)
    # Local metadata writers are draft-only; no IO or original invocation in phases.
    phase_names=['build.Recorder.wrap_boundary.wrapped._prepare','build.Recorder.wrap_boundary.wrapped._publish_return','build.Recorder.wrap_boundary.wrapped._publish_exception','build.Recorder.constructor.wrapped.metadata','build.Recorder.fixture_constructor.wrapped._fixture_metadata','build.Recorder.start.metadata','build.Recorder.wrap_return.observed.before','build.Recorder.wrap_return.observed.after','build.Recorder.wrap_return.observed.failure','build.Recorder._stop_fields','build.Recorder._close_frame','build.Bindings.prepare.publish','build.Pages.flush']
    for name in phase_names:
        fn=node(D+'atomic.py',name)
        for n in ast.walk(fn):
            if not isinstance(n,ast.Call):continue
            spelling=ast.unparse(n.func)
            assert spelling not in ('old','os.open','p.os.open','p.write_all','self.events.owner.create','test.id','result.stop'),(name,spelling)
            assert not spelling.endswith('.read') and not spelling.endswith('.read_bytes'),(name,spelling)
    # Q15/Q16 were moved to publication, not charged twice or dropped.
    owner=node(D+'atomic.py','build.Recorder.owner')
    assert one(owner,"self.reference(len(self.active['owner_context_refs']) - before)")
    stop=node(D+'atomic.py','build.Recorder._stop_fields');assert one(stop,'self.reference(1)')
    assert not any(isinstance(n,ast.Call) and ast.unparse(n.func)=='self.reference' and n.args and isinstance(n.args[0],ast.BinOp) for n in ast.walk(stop))
    pages=node(D+'atomic.py','build.Pages.flush')
    assert pos(one(pages,'self._reference()'))<pos(one(pages,'self._writes.append((name, body))'))<pos(one(pages,"self.manifest.append(dict(name=name, sha256=p.c.sha(body), bytes=len(body), **{k: header[k] for k in ('page_index', 'first_sequence', 'last_sequence', 'event_count')}))"))
    assert 'owner.create' not in ast.unparse(pages) and 'write_all' not in ast.unparse(pages)
    finish=node(D+'atomic.py','build.Recorder._typed_finish')
    assert 'self.reference(len(self.events.manifest))' not in ast.unparse(finish)
    assert one(finish,'self._atomic(lambda draft: draft.events.close(), seal=True)')
    # Original exception/return forwarding: calls remain outside phase functions.
    for sym in ('build.Recorder.constructor.wrapped','build.Recorder.fixture_constructor.wrapped','build.Recorder.wrap_return.observed'):
        fn=node(D+'atomic.py',sym)
        originals=[n for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='old']
        assert len(originals)==1,sym
        assert any(isinstance(n,ast.Return) and isinstance(n.value,ast.Name) and n.value.id=='out' for n in ast.walk(fn))
        assert any(isinstance(n,ast.Raise) and n.exc is None for n in ast.walk(fn))
    boundary=node(D+'atomic.py','build.Recorder.wrap_boundary.wrapped')
    assert len([n for n in ast.walk(boundary) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='old'])==2 # mutually exclusive fast path / observed path
    init=node(D+'atomic.py','build.Recorder.__init__');s=ast.unparse(init)
    assert 'p.t.Recorder.__init__' in s and 'super().__init__' not in s
    assert s.index('self._atomic(')<s.index('bindings._owner = self')<s.index('bindings.on_reference = self.reference')
    bindings=node(D+'atomic.py','build.Bindings.check')
    assert 'owner is None or not owner._state_lock._is_owned()' in ast.unparse(bindings)
    assert 'refs = list(dict.fromkeys(refs))' in ast.unparse(node(D+'atomic.py','build.Bindings.prepare'))
    # No limits were changed, including the unapplied candidate defaults.
    def literal_limits(path):
        t=ast.parse((ROOT/path).read_text())
        return ast.literal_eval(next(n.value.args[0] for n in t.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='LIMITS.update'))
    assert literal_limits(D+'capture.py')==literal_limits('testing/prospective_capture_joint/capture.py')
    C=P+'D5-I122-CAPACITY-CONTRACT.json';R=P+'D5-I122-CAPTURE-REGISTRY.json';K=P+'D5-I122-CAPACITY-CERTIFICATE.json';M=P+'D5-I122-COMPONENTS-MANIFEST.json'
    c=rd(C);stored=rd(R);k=rd(K);m=rd(M)
    assert stored['schema']=='d5.joint-inherited-registry.v1' and set(stored)=={'schema','source_revision','base_registry','base_registry_sha256','overrides'}
    assert stored['base_registry_sha256']==sha(stored['base_registry'])
    base=rd(stored['base_registry']);reg=dict(base,**stored['overrides'])
    assert set(stored['overrides'])=={'schema','source_revision','contract_path','contract_sha256','legacy_registry_sha256','base_selector_registry_sha256','implementation_sources','limits','domain_schemas','required_prior_inputs','component_execution_authorized','joint_admission'}
    assert len(enc(reg))+1==b['materialized_registry_compact_bytes']==806944
    assert (ROOT/R).stat().st_size==b['stored_registry_bytes']==57521
    unchanged=set(base)-set(stored['overrides'])
    assert all(reg[key]==base[key] for key in unchanged)
    assert reg['entry']['expected_test_ids']==base['entry']['expected_test_ids'] and reg['inventory']==base['inventory']
    assert reg['contract_sha256']==sha(C) and reg['implementation_sources']==proof['source_hashes']==b['source_pins']
    assert c['numeric_candidates']==k['numeric_candidates']==reg['limits']==rd(P+'D5-I115-joint-capacity-proposal.json')['candidate_limits']
    for pins in (reg['required_prior_inputs'],k['source_bindings'],m['source_bindings']):
        for path,h in pins.items():assert sha(path)==h,path
    assert len(reg['required_prior_inputs'])==480 and len(k['source_bindings'])==488 and len(m['source_bindings'])==9
    assert set(k['source_bindings'])==set(reg['required_prior_inputs'])|set(reg['implementation_sources'])|{C,R}
    assert set(m['source_bindings'])==set(reg['implementation_sources'])|{C,R,K}
    known=set(reg['required_prior_inputs'])|set(reg['implementation_sources'])|{C,R,K,M}
    assert set(b['current_known_input_pins'])==known and len(known)==b['known_files']==490
    U=sum((ROOT/p).stat().st_size for p in known);F=sum(b['future_metadata_width_sizes'].values());read=3*(U+F)+4852460
    assert U==b['known_union_bytes']==87104500 and F==b['future_metadata_bytes_upper']==57277
    assert read==b['read_schedule']['worker_file_read_upper']==266337791<268435456
    assert b['read_schedule']['worker_file_read_margin']==268435456-read==2097665
    assert b['capture_inputs_with_future_components']==493 and b['union_with_authority']==494
    assert len(enc(b['top_metadata_model']['value']))==b['top_metadata_model']['encoded_bytes']==483286<=524288
    assert k['status']=='IMPLEMENTED_NOT_ADMITTED' and k['correlated_atomicity_implemented'] is True and k['correlated_atomicity_verified'] is False
    assert k['CP03_global_resolved'] is True and k['CP07_exact_admission_resolved'] is False
    cls=node(D+'test_joint_capture.py','R2CandidateTests');tests=['R2CandidateTests.'+n.name for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    assert tests==m['tests'] and len(tests)==10 and m['status']=='NOT_RUN_SOURCE_ONLY'
    assert proof['atomicity_repair_implemented'] is True and proof['atomicity_runtime_validated'] is False
    assert g['atomicity_repair_implemented'] is True and g['component_tests_executed']==0 and g['candidate_imported_or_compiled'] is False
    for doc in (proof,b,g,k):assert doc['proposal_enabled'] is False and doc['D5_closed'] is False and doc['IR03']=='NOT_READY' and doc['closure'] is False
    for name in ('D5-JOINT-tests-raw.json','D5-JOINT-results.json','D5-JOINT-integrity.json','D5-JOINT-capture-authorization.json','D5-JOINT-P01','D5-JOINT-P01-launch.json'):assert not (ROOT/P/name).exists()
    assert "cert.get('status')=='SOURCE_CAPACITY_VERIFIED'" in export and "cert.get('correlated_atomicity_verified') is True" in export
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',logical_sites_integrated=30,candidate_files=6,components_written=10,components_executed=0,product_executed=False,candidate_imported_or_compiled=False,prior_untracked_preserved=76,atomicity_repair_implemented=True,runtime_atomicity_validated=False,file_read_upper=read,file_read_margin=268435456-read,transient_capacity_complete=False,quota_changed=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY')))

if __name__=='__main__':main()
