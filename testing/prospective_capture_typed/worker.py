# SPDX-License-Identifier: GPL-3.0-only
"""Typed worker. Only explicit I77 authority may reach historical import site."""
import contextlib
import importlib
import io
import os
from pathlib import Path
import sys
from testing.prospective_capture_typed import capture as p
c=p.c


def targets(reg,root=p.ROOT):
    reader=c.Reader(root);found=[];constructor=None
    specs=list(reg['observer_specs'])
    spec=reg['constructor_observer'];a=spec['source'];specs.append(dict(module=spec['module'],class_name=spec['class_name'],method=spec['method'],path=a['path'],sha256=a['sha256'],parameters=spec['signature_parameters']))
    for spec in specs:
        module=sys.modules.get(spec['module'])
        if module is None:continue
        cls=module.__dict__.get(spec['class_name']);c.require(type(cls) is type,'UNSUPPORTED_OBSERVER_API');fn=cls.__dict__.get(spec['method']);c.require(type(fn) is c.types.FunctionType,'UNSUPPORTED_OBSERVER_API')
        c.require(c.sha(reader.read(spec['path']))==spec['sha256'],'STALE_OBSERVER_SOURCE');c.require(list(c.inspect.signature(fn,eval_str=False).parameters)==spec['parameters'],'UNSUPPORTED_OBSERVER_SIGNATURE')
        c.require(Path(fn.__code__.co_filename).resolve()==(Path(root)/spec['path']).resolve(),'UNEXPECTED_OBSERVER_IMPLEMENTATION')
        if spec['method']=='__init__':
            c.require(c.inspect.signature(fn,eval_str=False).parameters['hook'].kind is c.inspect.Parameter.KEYWORD_ONLY,'UNSUPPORTED_OBSERVER_SIGNATURE');constructor=cls
        else:found.append((cls,spec['method']))
    c.require(constructor is not None,'CONSTRUCTOR_OBSERVER_UNAVAILABLE')
    spec=reg['negative_DI28']['constructor'];module=sys.modules.get(spec['module']);c.require(module is not None,'FIXTURE_MODULE_NOT_LOADED');fixture=module.__dict__.get(spec['class_name']);c.require(type(fixture) is type,'UNSUPPORTED_OBSERVER_API');fn=fixture.__dict__.get('__init__');c.require(type(fn) is c.types.FunctionType,'UNSUPPORTED_OBSERVER_API');a=spec['source']
    c.require(c.sha(reader.read(a['path']))==a['sha256'] and Path(fn.__code__.co_filename).resolve()==(Path(root)/a['path']).resolve(),'STALE_OBSERVER_SOURCE');sig=c.inspect.signature(fn,eval_str=False);c.require(list(sig.parameters)==spec['signature_parameters'] and all(sig.parameters[k].kind is c.inspect.Parameter.KEYWORD_ONLY for k in spec['keyword_only_parameters']),'UNSUPPORTED_OBSERVER_SIGNATURE')
    reader.finish();return found,constructor,fixture


class Tee(io.StringIO):
    def __init__(self,stream):super().__init__();self.stream=stream
    def write(self,s):n=self.stream.write(s);super().write(s);return n
    def flush(self):self.stream.flush()


def exercise(entry,entrypoint,stdout,owner,policies=(),observed=(),constructor=None,limits=None,profile=None,bindings=None,fixture_class=None):
    lim=dict(p.LIMITS,**(limits or {}));rec=p.Recorder(entry,owner,policies,lim,profile,bindings);sink=c.BoundedOutput(stdout,lim['raw_bytes']);exitcode=None
    try:
        rec.install(observed)
        if constructor is not None:rec.constructor(constructor)
        if fixture_class is not None:rec.fixture_constructor(fixture_class)
        with contextlib.redirect_stdout(sink):exitcode=entrypoint()
    except BaseException as ex:rec.invalid(ex.code if isinstance(ex,c.CaptureFault) else 'ENTRYPOINT_EXCEPTION')
    finally:
        rec.restore()
        try:sink.flush()
        except BaseException:rec.invalid('RAW_FLUSH_ERROR')
    raw=None
    if hasattr(stdout,'getvalue'):
        try:raw=c.strict_json(stdout.getvalue().encode())
        except BaseException:rec.invalid('RAW_UNAVAILABLE_OR_INVALID')
    side=rec.finish(raw)
    if raw is not None and 'frames' in side:
        try:
            c.require(type(exitcode) is int and exitcode==(0 if raw.get('status')=='PASS' else 1),'ENTRYPOINT_EXIT_MISMATCH')
            c.aggregate_capture(side,c.scenario_metadata(raw,entry),raw,entry)
        except c.CaptureFault as ex:side['status']='INVALID_CAPTURE';side.setdefault('errors',[]).append(ex.code)
    side.update(entrypoint_exit_code=exitcode,raw_bytes=sink.count,raw_sha256=sink.hash.hexdigest());return side


def main(argv=None,root=p.ROOT):
    args=sys.argv[1:] if argv is None else argv
    try:
        c.require(len(args)==6,'INVALID_WORKER_ARGUMENTS');requested,sidearg,readyarg,releasearg,dirarg,lease=args;p.scope(requested)
        c.require(sys.flags.optimize==0 and __debug__,'OPTIMIZATION_NOT_SUPPORTED');reg=p.read_registry(root);approved=p.authority(root,requested,reg)
        c.require(all(v.isdigit() for v in (sidearg,readyarg,releasearg,dirarg)),'INVALID_WORKER_CHANNEL');sidefd,readyfd,releasefd,dirfd=map(int,(sidearg,readyarg,releasearg,dirarg));c.require(len({sidefd,readyfd,releasefd,dirfd})==4 and min(sidefd,readyfd,releasefd,dirfd)>2,'INVALID_WORKER_CHANNEL')
        c.require(c.stat.S_ISREG(os.fstat(sidefd).st_mode) and c.stat.S_ISREG(os.fstat(sys.stdout.fileno()).st_mode),'INVALID_WORKER_CHANNEL');c.require(os.getpid()==os.getpgid(0),'INVALID_WORKER_GROUP')
        owner=p.ChannelRoot(dirfd,lease);st=os.fstat(dirfd)
        message=dict(event='READY',scope='P01',lease=lease,pid=os.getpid(),pgid=os.getpgid(0),raw_inode=os.fstat(sys.stdout.fileno()).st_ino,sidecar_inode=os.fstat(sidefd).st_ino,directory_device=st.st_dev,directory_inode=st.st_ino)
        c.write_json_fd(readyfd,message,4096);p.write_all(readyfd,b'\n');os.close(readyfd)
        release=c.receive_line(releasefd,p.LIMITS['wait_seconds']);os.close(releasefd);p.verify_release(release,lease)
        entry=reg['entry'];before=c.runner_files(root,entry);c.require(before==entry['runner_effective_inputs'],'STALE_INPUTS')
        # The sole historical import is AFTER independent I77 guards and release.
        module=importlib.import_module(entry['runner_module']);c.require(Path(module.__file__).resolve()==(Path(root)/entry['runner_path']).resolve(),'UNEXPECTED_RUNNER_MODULE')
        observed,constructor,fixture=targets(reg,root);bindings=p.loaded_bindings(reg,root);side=exercise(entry,module.main,Tee(sys.stdout),owner,reg['policies'],observed,constructor,profile=reg,bindings=bindings,fixture_class=fixture);after=c.runner_files(root,entry)
        side['runner_inputs_before']=before;side['runner_inputs_after']=after;side['input_comparison']=c.compare_inputs(before,after)
        if side['input_comparison']['status']!='MATCH':side['status']='INVALID_CAPTURE';side.setdefault('errors',[]).append('STALE_INPUTS')
        c.require(p.authority(root,'P01',reg)==approved,'STALE_AUTHORITY');side['capture_inputs_before']=approved['capture_inputs'];side['capture_inputs_after']=approved['capture_inputs'];side['worker_invocation']=p.invocation(args)
        owner.verify();c.write_json_fd(sidefd,side,p.LIMITS['index_sidecar_bytes']);os.close(sidefd);os.close(dirfd)
        return 0 if side['status']=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' else 1
    except BaseException as ex:sys.stderr.write((ex.code if isinstance(ex,c.CaptureFault) else 'SANITIZED_WORKER_ERROR')+'\n');return 2


if __name__=='__main__':raise SystemExit(main())
