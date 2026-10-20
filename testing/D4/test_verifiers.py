# SPDX-License-Identifier: GPL-3.0-only
import os,tempfile,unittest
from pathlib import Path
from verifiers import Artifact,FixtureGitStore,Rejected,manifest_digest,verify_files

class VerifierTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.files=self.root/'files';self.files.mkdir();self.expected={'a.txt':Artifact.of(b'base\n')};(self.files/'a.txt').write_bytes(b'base\n')
 def store(self):return FixtureGitStore(self.root/'repo')
 def commit(self,store,files,parent=None):
  # Driver-only fixture creation; no worker-controlled path or repository is read.
  rows=[]
  for name,value in sorted(files.items()):
   mode,data=value if isinstance(value,tuple) else ('100644',value)
   if mode=='160000':oid=data
   else:oid=store._run(['hash-object','-w','--stdin'],data).strip().decode()
   rows.append(f'{mode} '+('commit' if mode=='160000' else 'blob')+' '+oid+'\t'+name+'\n')
  tree=store._run(['mktree'],''.join(rows).encode()).strip().decode()
  args=['commit-tree',tree]+(['-p',parent] if parent else [])
  return store._run(args,b'Synthetic fixture\n').strip().decode()
 def test_complete_artifact_tree(self):
  v=verify_files(self.files,self.expected);self.assertEqual(v.files,1);self.assertEqual(v.bytes,5);self.assertEqual(v.manifest_sha256,manifest_digest(self.expected))
 def test_changed_bytes_same_size(self):
  (self.files/'a.txt').write_bytes(b'fake\n')
  with self.assertRaises(Rejected):verify_files(self.files,self.expected)
 def test_missing_file(self):
  (self.files/'a.txt').unlink()
  with self.assertRaises(Rejected):verify_files(self.files,self.expected)
 def test_extra_file(self):
  (self.files/'extra').write_text('extra')
  with self.assertRaises(Rejected):verify_files(self.files,self.expected)
 def test_extra_empty_directory(self):
  (self.files/'empty').mkdir()
  with self.assertRaises(Rejected):verify_files(self.files,self.expected)
 def test_nested_exact_manifest(self):
  (self.files/'sub').mkdir();(self.files/'sub/b').write_bytes(b'next');e=self.expected|{'sub/b':Artifact.of(b'next')};self.assertEqual(verify_files(self.files,e).files,2)
 def test_symlink_file(self):
  (self.files/'a.txt').unlink();(self.files/'a.txt').symlink_to(self.root/'outside');(self.root/'outside').write_bytes(b'base\n')
  with self.assertRaises(Rejected):verify_files(self.files,self.expected)
 def test_symlink_root(self):
  p=self.root/'alias';p.symlink_to(self.files)
  with self.assertRaises(Rejected):verify_files(p,self.expected)
 def test_symlink_directory(self):
  (self.root/'external').mkdir();(self.root/'external/b').write_bytes(b'next');(self.files/'sub').symlink_to(self.root/'external')
  with self.assertRaises(Rejected):verify_files(self.files,self.expected|{'sub/b':Artifact.of(b'next')})
 def test_hardlink_rejected(self):
  os.link(self.files/'a.txt',self.root/'hardlink')
  with self.assertRaises(Rejected):verify_files(self.files,self.expected)
 def test_fifo_rejected_without_blocking(self):
  (self.files/'a.txt').unlink();os.mkfifo(self.files/'a.txt')
  with self.assertRaises(Rejected):verify_files(self.files,self.expected)
 def test_mode_mismatch(self):
  (self.files/'a.txt').chmod(0o755)
  with self.assertRaises(Rejected):verify_files(self.files,self.expected)
 def test_executable_verified(self):
  (self.files/'a.txt').chmod(0o755);self.assertEqual(verify_files(self.files,{'a.txt':Artifact.of(b'base\n',True)}).files,1)
 def test_paths_and_manifest_bounds(self):
  for p in ['../outside','/absolute','a//b','.git/config','a/../b','a\nb']:
   with self.subTest(p=p),self.assertRaises(Rejected):manifest_digest({p:Artifact.of(b'x')})
  with self.assertRaises(Rejected):manifest_digest({f'f{i}':Artifact.of(b'x') for i in range(65)})
  with self.assertRaises(Rejected):Artifact.of(b'x'*65537)
  with self.assertRaises(Rejected):manifest_digest({'a':Artifact.of(b'x'),'a/b':Artifact.of(b'y')})
 def test_git_objects_ancestry_and_complete_tree(self):
  s=self.store();base=self.commit(s,{'a.txt':b'base\n'});head=self.commit(s,{'a.txt':b'next\n'},base)
  self.assertEqual(s.verify(head,base,{'a.txt':Artifact.of(b'next\n')}).files,1)
 def test_git_wrong_hash(self):
  s=self.store();base=self.commit(s,{'a.txt':b'base\n'})
  with self.assertRaises(Rejected):s.verify(base,base,{'a.txt':Artifact.of(b'fake\n')})
 def test_git_unrelated_base(self):
  s=self.store();base=self.commit(s,{'a.txt':b'base\n'});other=self.commit(s,{'a.txt':b'other'})
  with self.assertRaises(Rejected):s.verify(other,base,{'a.txt':Artifact.of(b'other')})
 def test_git_extra_and_missing_files(self):
  s=self.store();base=self.commit(s,{'a.txt':b'base\n','extra':b'x'})
  with self.assertRaises(Rejected):s.verify(base,base,self.expected)
  with self.assertRaises(Rejected):s.verify(base,base,self.expected|{'extra':Artifact.of(b'x'),'missing':Artifact.of(b'x')})
 def test_git_symlink_rejected(self):
  s=self.store();base=self.commit(s,{'a.txt':('120000',b'target')})
  with self.assertRaises(Rejected):s.verify(base,base,{'a.txt':Artifact.of(b'target')})
 def test_git_submodule_rejected(self):
  s=self.store();base=self.commit(s,{'a.txt':b'base\n'});head=self.commit(s,{'sub':('160000',base)},base)
  with self.assertRaises(Rejected):s.verify(head,base,{'sub':Artifact.of(b'')})
 def test_git_requires_full_commit_oid(self):
  s=self.store();base=self.commit(s,{'a.txt':b'base\n'})
  for candidate in ['HEAD',base[:8],base+'^{tree}','--help']:
   with self.subTest(candidate=candidate),self.assertRaises(Rejected):s.verify(candidate,base,self.expected)
  blob=s._run(['hash-object','-w','--stdin'],b'base\n').strip().decode()
  with self.assertRaises(Rejected):s.verify(blob,base,self.expected)
 def test_git_changed_config_rejected_before_use(self):
  s=self.store();base=self.commit(s,{'a.txt':b'base\n'});(s.path/'config').write_text('[include]\npath=/nonexistent\n')
  with self.assertRaises(Rejected):s.verify(base,base,self.expected)
 def test_git_alternate_and_replace_store_rejected(self):
  s=self.store();base=self.commit(s,{'a.txt':b'base\n'});p=s.path/'objects/info/alternates';p.write_text('/nonexistent\n')
  with self.assertRaises(Rejected):s.verify(base,base,self.expected)
  p.unlink();(s.path/'refs/replace').mkdir()
  with self.assertRaises(Rejected):s.verify(base,base,self.expected)
 def test_git_does_not_execute_hooks_or_candidate_scripts(self):
  s=self.store();marker=self.root/'executed';script=b'#!/bin/sh\nexit 93\n';base=self.commit(s,{'run.sh':('100755',script)})
  hooks=s.path/'hooks';hooks.mkdir();hook=hooks/'pre-commit';hook.write_text('#!/bin/sh\ntouch '+str(marker)+'\n');hook.chmod(0o755)
  self.assertEqual(s.verify(base,base,{'run.sh':Artifact.of(script,True)}).files,1);self.assertFalse(marker.exists())
 def test_restore_files_requires_baseline_and_confers_no_acceptance(self):
  (self.files/'a.txt').write_bytes(b'next\n')
  with self.assertRaises(Rejected):verify_files(self.files,self.expected,restoration=True)
  (self.files/'a.txt').write_bytes(b'base\n');proof=verify_files(self.files,self.expected,restoration=True)
  self.assertEqual(proof.method,'d4.local-restoration.v1');self.assertFalse(hasattr(proof,'accepted'))

if __name__=='__main__':unittest.main()
