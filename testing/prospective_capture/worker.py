# SPDX-License-Identifier: GPL-3.0-only
"""Isolated capture entrypoint; I71 guard precedes all historical imports."""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
from testing.prospective_capture import capture as c


def public_targets(reg,root=c.ROOT):
    targets=[];reader=c.Reader(root)
    for spec in reg['observer_specs']:
        module=sys.modules.get(spec['module'])
        if module is None:continue
        cls=module.__dict__.get(spec['class_name']);c.require(type(cls) is type,'UNSUPPORTED_OBSERVER_API')
        fn=cls.__dict__.get(spec['method']);c.require(type(fn) is c.types.FunctionType,'UNSUPPORTED_OBSERVER_API')
        c.require(c.sha(reader.read(spec['path']))==spec['sha256'],'STALE_OBSERVER_SOURCE')
        c.require(list(c.inspect.signature(fn,eval_str=False).parameters)==spec['parameters'],'UNSUPPORTED_OBSERVER_SIGNATURE')
        c.require(Path(fn.__code__.co_filename).resolve()==(Path(root)/spec['path']).resolve(),'UNEXPECTED_OBSERVER_IMPLEMENTATION')
        targets.append((cls,spec['method']))
    reader.finish();return targets


def exercise(entry,entrypoint,stdout,targets=(),limits=None):
    """Injectable entrypoint used by synthetic PF only; no module loading here."""
    lim=dict(c.LIMITS,**(limits or {}));rec=c.Recorder(entry,lim);sink=c.BoundedOutput(stdout,lim['raw_bytes']);exitcode=None
    try:
        rec.install(targets)
        with contextlib.redirect_stdout(sink):exitcode=entrypoint()
    except BaseException as ex:rec.invalid(ex.code if isinstance(ex,c.CaptureFault) else 'ENTRYPOINT_EXCEPTION')
    finally:rec.restore();sink.flush()
    # Worker captures stdout in memory as well as the caller-owned stream.
    raw=None
    if hasattr(stdout,'getvalue'):
        try:raw=c.strict_json(stdout.getvalue().encode(),lim)
        except (c.CaptureFault,ValueError):rec.invalid('RAW_UNAVAILABLE_OR_INVALID')
    side=rec.finish(raw)
    if raw is not None and 'frames' in side:
        if type(exitcode) is not int or exitcode!=(0 if raw.get('status')=='PASS' else 1):side['status']='INVALID_CAPTURE';side.setdefault('errors',[]).append('ENTRYPOINT_EXIT_MISMATCH')
        try:side=c.aggregate_capture(side,c.scenario_metadata(raw,entry),raw,entry)
        except c.CaptureFault as ex:side['status']='INVALID_CAPTURE';side.setdefault('errors',[]).append(ex.code)
    side['entrypoint_exit_code']=exitcode;side['raw_bytes']=sink.count;side['raw_sha256']=sink.hash.hexdigest();return side


class Tee(io.StringIO):
    def __init__(self,stream):super().__init__();self.stream=stream
    def write(self,s):out=self.stream.write(s);super().write(s);return out
    def flush(self):self.stream.flush()


def main(argv=None,root=c.ROOT):
    args=sys.argv[1:] if argv is None else argv
    try:
        c.require(len(args)==5,'INVALID_WORKER_ARGUMENTS');scope,sidearg,readyarg,releasearg,lease=args;c.authority_scope(scope)
        c.require(sys.flags.optimize==0 and __debug__,'OPTIMIZATION_NOT_SUPPORTED');reg=c.read_registry(root);approved=c.authority(root,scope,reg)
        c.require(all(s.isdigit() for s in (sidearg,readyarg,releasearg)),'INVALID_WORKER_CHANNEL');sidefd,readyfd,releasefd=map(int,(sidearg,readyarg,releasearg));c.require(len({sidefd,readyfd,releasefd})==3 and min(sidefd,readyfd,releasefd)>2,'INVALID_WORKER_CHANNEL')
        c.require(c.stat.S_ISREG(os.fstat(sidefd).st_mode) and c.stat.S_ISREG(os.fstat(sys.stdout.fileno()).st_mode),'INVALID_WORKER_CHANNEL')
        c.require(os.getpid()==os.getpgid(0),'INVALID_WORKER_GROUP');entry=next(e for e in reg['entries'] if e['id']==scope)
        message=dict(event='READY',scope=scope,lease=lease,pid=os.getpid(),pgid=os.getpgid(0),raw_inode=os.fstat(sys.stdout.fileno()).st_ino,sidecar_inode=os.fstat(sidefd).st_ino)
        c.write_json_fd(readyfd,message,4096);os.write(readyfd,b'\n');os.close(readyfd)
        release=c.receive_line(releasefd,c.LIMITS['wait_seconds']);os.close(releasefd);c.require(release==dict(event='RELEASE',lease=lease),'INVALID_WORKER_RELEASE')
        before=c.runner_files(root,entry);c.require(before==entry['runner_effective_inputs'],'STALE_INPUTS')
        # This is the only historical import site; unreachable in I70/PF.
        module=importlib.import_module(entry['runner_module']);c.require(Path(module.__file__).resolve()==(Path(root)/entry['runner_path']).resolve(),'UNEXPECTED_RUNNER_MODULE')
        side=exercise(entry,module.main,Tee(sys.stdout),public_targets(reg,root));after=c.runner_files(root,entry);side['runner_inputs_before']=before;side['runner_inputs_after']=after;side['input_comparison']=c.compare_inputs(before,after)
        if side['input_comparison']['status']!='MATCH':side['status']='INVALID_CAPTURE';side.setdefault('errors',[]).append('STALE_INPUTS')
        c.require(c.authority(root,scope,reg)==approved,'STALE_AUTHORITY');side['capture_inputs_before']=approved['capture_inputs'];side['capture_inputs_after']=approved['capture_inputs']
        side['worker_invocation']=c.invocation(scope,args);c.write_json_fd(sidefd,side,c.LIMITS['sidecar_bytes']);os.close(sidefd)
        return 0 if side['status']=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' else 1
    except BaseException as ex:
        # No traceback/source/exception text; functional bytes already emitted remain separate.
        sys.stderr.write((ex.code if isinstance(ex,c.CaptureFault) else 'SANITIZED_WORKER_ERROR')+'\n');return 2


if __name__=='__main__':raise SystemExit(main())
