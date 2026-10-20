# SPDX-License-Identifier: GPL-3.0-only
"""Independent LOCAL components. No evidence ingestion, SQL, network or acceptance.

Only verifier-owned fixture Git stores are supported. An expected manifest/base
comes from frozen trusted policy, never from the candidate. Stop, identity,
receiver closure and accounting remain separate acceptance requirements.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib,json,os,re,resource,stat,subprocess,tempfile

MAX_FILES=64
MAX_BLOB=65536
MAX_TOTAL=4*1024*1024

class Rejected(ValueError):pass

def path_parts(name):
 if not isinstance(name,str) or len(name)>240:raise Rejected('PATH')
 parts=name.split('/')
 if any(not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',p) or p in ('.','..') or p.casefold()=='.git' for p in parts):raise Rejected('PATH')
 return parts

@dataclass(frozen=True)
class Artifact:
 size:int
 sha256:str
 executable:bool=False
 def __post_init__(self):
  if type(self.size)!=int or not 0<=self.size<=MAX_BLOB or not isinstance(self.sha256,str) or not re.fullmatch('[0-9a-f]{64}',self.sha256) or type(self.executable)!=bool:raise Rejected('ARTIFACT')
 @classmethod
 def of(cls,data,executable=False):return cls(len(data),hashlib.sha256(data).hexdigest(),executable)

@dataclass(frozen=True)
class VerifiedTree:
 method:str
 manifest_sha256:str
 files:int
 bytes:int

def manifest_digest(expected):
 if not isinstance(expected,dict) or len(expected)>MAX_FILES:raise Rejected('MANIFEST_BOUND')
 for name,a in expected.items():
  path_parts(name)
  if not isinstance(a,Artifact):raise Rejected('ARTIFACT_TYPE')
  if any('/'.join(name.split('/')[:i]) in expected for i in range(1,len(name.split('/')))):raise Rejected('FILE_DIRECTORY_COLLISION')
 if sum(a.size for a in expected.values())>MAX_TOTAL:raise Rejected('TOTAL_BOUND')
 body={k:{'size':v.size,'sha256':v.sha256,'executable':v.executable} for k,v in sorted(expected.items())}
 return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def verify_files(root,expected,*,restoration=False):
 """Observe exact files via no-follow dirfds. Requires an independently stopped writer.

 This reads a snapshot; it cannot promise that another authorized writer will
 never alter it later. No callback, receipt or consumption is changed.
 """
 digest=manifest_digest(expected);seen=set();root=Path(root)
 flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC
 try:
  fd=os.open(root,flags|os.O_DIRECTORY)
  try:
   def walk(directory,prefix):
    with os.scandir(directory) as entries:
     for entry in entries:
      name=prefix+entry.name;path_parts(name)
      before=entry.stat(follow_symlinks=False)
      if stat.S_ISDIR(before.st_mode):
       if not any(p.startswith(name+'/') for p in expected):raise Rejected('EXTRA_DIRECTORY')
       child=os.open(entry.name,flags|os.O_DIRECTORY,dir_fd=directory)
       try:walk(child,name+'/')
       finally:os.close(child)
      else:
       if name not in expected or not stat.S_ISREG(before.st_mode) or before.st_nlink!=1:raise Rejected('EXTRA_OR_UNSAFE_FILE')
       item=expected[name];file=os.open(entry.name,flags|os.O_NONBLOCK,dir_fd=directory)
       try:
        opened=os.fstat(file)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink!=1 or (opened.st_dev,opened.st_ino)!=(before.st_dev,before.st_ino) or opened.st_size!=item.size or bool(opened.st_mode&0o111)!=item.executable:raise Rejected('FILE_METADATA')
        data=b''
        while len(data)<=item.size:
         chunk=os.read(file,min(8192,item.size+1-len(data)))
         if not chunk:break
         data+=chunk
        after=os.fstat(file)
        if (opened.st_size,opened.st_mtime_ns,opened.st_ctime_ns)!=(after.st_size,after.st_mtime_ns,after.st_ctime_ns) or len(data)!=item.size or hashlib.sha256(data).hexdigest()!=item.sha256:raise Rejected('FILE_CONTENT')
       finally:os.close(file)
       seen.add(name)
   walk(fd,'')
  finally:os.close(fd)
 except OSError as ex:raise Rejected('UNSAFE_OR_UNAVAILABLE_TREE') from ex
 if seen!=set(expected):raise Rejected('INCOMPLETE_TREE')
 return VerifiedTree('d4.local-restoration.v1' if restoration else 'd4.artifact-tree.v1',digest,len(seen),sum(a.size for a in expected.values()))

class FixtureGitStore:
 """New bare store owned exclusively by the verifier/fixture driver.

 Not an importer for a worker .git directory, bundle or arbitrary repository.
 Object publication by a candidate is deliberately not implemented here.
 """
 def __init__(self,path):
  self.path=Path(path).absolute();self.path.mkdir(mode=0o700)
  self.environment={'PATH':os.defpath,'LANG':'C','LC_ALL':'C','HOME':str(self.path),'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_SYSTEM':'/dev/null','GIT_CONFIG_GLOBAL':'/dev/null','GIT_NO_REPLACE_OBJECTS':'1','GIT_TERMINAL_PROMPT':'0','GIT_AUTHOR_NAME':'Synthetic verifier','GIT_AUTHOR_EMAIL':'fixture@example.invalid','GIT_COMMITTER_NAME':'Synthetic verifier','GIT_COMMITTER_EMAIL':'fixture@example.invalid','GIT_AUTHOR_DATE':'2026-10-20T00:00:00Z','GIT_COMMITTER_DATE':'2026-10-20T00:00:00Z'}
  self._run(['init','--bare','--object-format=sha1','--template=',str(self.path)],initial=True)
  self._config=(self.path/'config').read_bytes()
 def _run(self,args,data=None,initial=False):
  # Fixed commands only in this module; no shell, hooks, filters or network.
  command=['git','--no-optional-locks']
  if not initial:command+=['--git-dir='+str(self.path),'-c','core.hooksPath=/dev/null','-c','protocol.allow=never','-c','core.fsmonitor=false']
  def bound():resource.setrlimit(resource.RLIMIT_FSIZE,(2*1024*1024,2*1024*1024))
  with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
   try:r=subprocess.run(command+args,input=data,stdout=out,stderr=err,env=self.environment,timeout=5,preexec_fn=bound)
   except (OSError,subprocess.TimeoutExpired) as ex:raise Rejected('GIT_UNAVAILABLE_OR_TIMEOUT') from ex
   if r.returncode:raise Rejected('GIT_OBJECT_OR_ANCESTRY')
   if out.tell()>2*1024*1024:raise Rejected('GIT_OUTPUT_BOUND')
   out.seek(0);return out.read()
 def _integrity(self):
  if (self.path/'config').is_symlink() or (self.path/'config').read_bytes()!=self._config:raise Rejected('STORE_CONFIG_CHANGED')
  for forbidden in ['objects/info/alternates','objects/info/http-alternates','info/grafts','shallow','refs/replace']:
   if (self.path/forbidden).exists() or (self.path/forbidden).is_symlink():raise Rejected('STORE_INDIRECTION')
  for directory,dirs,files in os.walk(self.path,followlinks=False):
   for name in dirs+files:
    p=Path(directory)/name
    if p.is_symlink() or (p.is_file() and p.stat().st_nlink!=1):raise Rejected('STORE_ALIAS')
 def verify(self,commit,base,expected):
  digest=manifest_digest(expected);self._integrity()
  if any(not isinstance(x,str) or not re.fullmatch('[0-9a-f]{40}',x) for x in [commit,base]):raise Rejected('FULL_FIXTURE_OID_REQUIRED')
  for oid in [commit,base]:
   if self._run(['cat-file','-t',oid]).strip()!=b'commit':raise Rejected('COMMIT_REQUIRED')
  self._run(['merge-base','--is-ancestor',base,commit])
  raw=self._run(['ls-tree','-r','-z','--full-tree',commit]);rows=raw.split(b'\0');seen=set()
  if len(rows)>MAX_FILES+1:raise Rejected('TREE_BOUND')
  for row in rows:
   if not row:continue
   try:
    meta,rawname=row.split(b'\t',1);mode,kind,oid=meta.decode('ascii').split();name=rawname.decode('ascii')
   except (ValueError,UnicodeError) as ex:raise Rejected('GIT_ENTRY') from ex
   path_parts(name)
   if name not in expected or name in seen or kind!='blob' or mode not in ['100644','100755']:raise Rejected('UNEXPECTED_GIT_ENTRY')
   item=expected[name]
   if (mode=='100755')!=item.executable:raise Rejected('GIT_FILE_MODE')
   size=int(self._run(['cat-file','-s',oid]).strip())
   if size!=item.size:raise Rejected('GIT_BLOB_SIZE')
   data=self._run(['cat-file','blob',oid])
   if len(data)!=item.size or hashlib.sha256(data).hexdigest()!=item.sha256:raise Rejected('GIT_BLOB_HASH')
   seen.add(name)
  if seen!=set(expected):raise Rejected('INCOMPLETE_GIT_TREE')
  self._integrity()
  return VerifiedTree('d4.fixture-git-tree.v1',digest,len(seen),sum(a.size for a in expected.values()))
