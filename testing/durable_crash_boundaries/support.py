# SPDX-License-Identifier: GPL-3.0-only
"""I44 owned process controls and file observations; existing public APIs only."""
import hashlib
import json
import multiprocessing
from pathlib import Path
import signal
import time
import uuid

from source_ingest.durable_store import DurableError
from testing.D5 import durable_support as T, relational_support as R
from testing.durable_concurrency.support import independent, canonical, digest, require

CTX = multiprocessing.get_context('spawn')
CHILDREN = []
RECORDS = []
EXTRA_ROOTS = []
WAIT_SECONDS, CASE_SECONDS, CAMPAIGN_SECONDS = 20, 120, 900
MAX_EVENTS, MAX_EVENT_BYTES, MAX_RAW_BYTES = 256, 16*1024, 8*1024*1024
OPS = [('CAPTURE', 'SOURCE'), ('SELECT_SOURCE', 'SOURCE'), ('PREPARE_SOURCE', 'SOURCE'),
       ('REVIEW', 'SOURCE'), ('PREPARE_BATCH', 'BATCH'), ('REVIEW', 'BATCH')]
POINTS = ('before_object', 'after_object', 'before_replace', 'after_head')


def uid():
    return str(uuid.uuid4())


def spec(lab, path):
    return dict(path=path, store=T.reopen_spec(lab) if path == 'T' else R.spec(lab))


def open_client(value, hook=None):
    return (T if value['path'] == 'T' else R).open_client(value['store'], hook)


def roots(value):
    store = value['store']
    return dict(client=Path(store['client_path'] if value['path'] == 'T' else store['client']),
                remote=Path(store['remote_path'] if value['path'] == 'T' else store['remote']))


def inspect_files(value):
    return {role: independent(path) for role, path in roots(value).items()}


def describe(value, path):
    """Public metadata only; physical objects never substitute reachable HEAD."""
    state = value['state']
    reachable = {digest(v) for v in value['chain']}
    objects = list((path/'objects').iterdir())
    require(all(p.is_file() and not p.is_symlink() for p in objects), 'ORACLE_OBJECT_TYPE')
    stored = {p.stem for p in objects if p.suffix == '.json'}
    return dict(head=value['head'], state_sha256=digest(state), receipts=len(state['receipts']),
                sources=len(state.get('sources', {})), manifests=len(state.get('manifests', {})),
                data_generation=state.get('data_generation'), source_generation=state.get('source_generation'),
                bindings=len(state.get('bindings', {})), pending=len(state.get('pending', {})),
                entities=len(state.get('data', {}).get('entities', state.get('tasks', state.get('entities', {})))),
                relations=len(state.get('data', {}).get('relations', {})), tickets=len(state.get('tickets', {})),
                sends=[dict(send_id=sid, status=v['status'], ledger_version=v['ledger_version'], queries=v['queries'],
                            attempts=v['attempts'], proof_sha256=digest(v['proof'])) for sid, v in state.get('sends', {}).items()],
                reviews={k:dict(version=v['version'], decision=v['decision']) for k,v in state.get('reviews', {}).items()},
                remote_versions=[dict(remote_id=rid, version=v['version'], payload_sha256=digest(v['payload']),
                                     foreign_sha256=digest(v['foreign'])) for rid,v in state.get('entities', {}).items()],
                reachable_objects=len(reachable), stored_objects=len(stored), unreachable_objects=len(stored-reachable),
                temporary_heads=sum(p.name.startswith('.head-') for p in path.iterdir()),
                temporary_objects=sum(p.name.startswith('.object-') for p in objects))


def receive(conn, timeout=WAIT_SECONDS):
    require(conn.poll(timeout), 'CONTROL_TIMEOUT')
    try:
        return conn.recv()
    except EOFError:
        raise AssertionError('CONTROL_EOF') from None


def validate_gate(event, job, value):
    require(event.get('event') == 'READY', 'MISSING_READY')
    for key in ('operation', 'stage', 'mode', 'point'):
        require(event.get(key) == job[key], 'WRONG_GATE')
    require(event.get('run_id') == value['store']['run_id'] and event.get('role') == 'CLIENT', 'GATE_IDENTITY')


def expect_error(code, call, *args, **kwargs):
    try:
        call(*args, **kwargs)
    except DurableError as ex:
        require(str(ex) == code, 'WRONG_PRODUCT_ERROR')
        return
    raise AssertionError('EXPECTED_ERROR_ABSENT')


def worker(value, job, conn):
    observed = dict(lookup=0, execute=0, proof_sha256=None, execute_proof_sha256=None)
    armed = True

    def hook(point):
        if not armed or point != job.get('point'):
            return
        if job['action'] == 'io_fault':
            raise OSError('SYNTHETIC_IO_FAULT')
        conn.send(dict(event='READY', role='CLIENT', run_id=value['store']['run_id'],
                       operation=job['operation'], mode=job['mode'], stage=job['stage'], point=point,
                       transport=dict(observed)))
        require(receive(conn) == 'UNREACHABLE_RELEASE', 'CONTROL_UNEXPECTED_RELEASE')

    try:
        action = job['action']
        if action == 'file_reader':
            out = inspect_files(value)
        else:
            c = open_client(value, hook if action in ('crash', 'io_fault') else None)
            lookup, execute = c.remote.lookup, c.remote.execute

            def seen_lookup(*args, **kwargs):
                observed['lookup'] += 1
                result = lookup(*args, **kwargs)
                observed['proof_sha256'] = digest(result)
                return result

            def seen_execute(*args, **kwargs):
                observed['execute'] += 1
                result = execute(*args, **kwargs)
                observed['execute_proof_sha256'] = digest(result)
                return result
            c.remote.lookup, c.remote.execute = seen_lookup, seen_execute
            if action == 'passive':
                out = dict(snapshot=c.snapshot(), summary=c.summary(), commands={})
                for command in job.get('commands', []):
                    out['commands'][command['cid']] = c.store.read_command(command['cid'], command['request_hash'])
            elif action == 'io_fault':
                if job['point'] == 'directory_fsync':
                    expect_error('COMMIT_UNKNOWN', c.perform, **job['command'])
                else:
                    expect_error('COMMIT_UNKNOWN', c.snapshot)
                expect_error('RECOVERY_REQUIRED', c.snapshot)
                out = dict(error='COMMIT_UNKNOWN', poisoned_error='RECOVERY_REQUIRED', point=job['point'])
            elif action in ('crash', 'replay'):
                if job.get('command'):
                    out = c.perform(**job['command'])
                elif job['operation'] == 'dispatch':
                    out = c.dispatch(job['mid'], 1, send_id=job['sid'])
                else:
                    out = c.reconcile(job['sid'])
            elif action == 'reconcile':
                out = c.reconcile(job['sid'])
            elif action == 'continue_gap':
                if value['path'] == 'R':
                    c.perform('SELECT_TASKS', dict(batch_command=job['cid'], batch_request=job['request_hash'], task_ids=[job['tid']]))
                c.perform('BIND', dict(binding_id=job['bid'], target_id=job['tid']))
                mid = c.prepare_projection(job['bid'])['result']['manifest_id']
                c.review('PROJECTION', mid)
                out = dict(manifest_id=mid)
            else:
                raise AssertionError('UNKNOWN_WORKER_ACTION')
        conn.send(dict(event='DONE', status='OK', value=out, transport=observed))
    except Exception as ex:
        code = str(ex) if isinstance(ex, (DurableError, AssertionError)) and str(ex).replace('_','').isalnum() else type(ex).__name__
        conn.send(dict(event='DONE', status='ERROR', code=code))
    finally:
        conn.close()


def held_child(conn):
    conn.send(dict(event='READY'))
    conn.recv()


def normal_child(conn):
    conn.send(dict(event='DONE'))
    conn.close()


def empty_child(conn):
    conn.close()


def start(target, args, label):
    require(sum(p.is_alive() for p,_ in CHILDREN) < 4, 'CHILD_BUDGET')
    parent, child = CTX.Pipe()
    p = CTX.Process(target=target, args=(*args, child))
    p.start(); child.close(); CHILDREN.append((p, label))
    return p, parent


def stop_owned(pairs):
    for p, conn in pairs:
        if p.is_alive():
            p.kill()
        p.join(WAIT_SECONDS); conn.close()
    require(all(not p.is_alive() for p,_ in pairs), 'CHILD_REMAINING')


def finish(p, conn, expected=0):
    p.join(WAIT_SECONDS)
    if p.is_alive():
        stop_owned([(p, conn)])
        raise AssertionError('CHILD_JOIN_TIMEOUT')
    conn.close()
    require(p.exitcode == expected, 'CHILD_EXIT')


class Scenario:
    def __init__(self, case, path):
        self.case, self.path = case, path
        self.started = time.monotonic()
        self.events, self.oracles, self.children = [], [], []
        self.lab = (T if path == 'T' else R).new_lab()
        self.value = spec(self.lab, path)
        self.record = dict(case=case, path=path, run_id=self.lab.run_id, client_store_id=self.lab.client_id,
                           remote_store_id=self.lab.remote_id, status='RUNNING', events=self.events, oracles=self.oracles)
        RECORDS.append(self.record)

    def event(self, name, *, actor='parent', role='HARNESS', operation='CONTROL', mode='NONE', stage='NONE', point=None, round=1, **fields):
        require(time.monotonic()-self.started < CASE_SECONDS, 'CASE_TIMEOUT')
        value = dict(event=name, case=self.case, path=self.path, actor=actor, role=role, operation=operation,
                     mode=mode, stage=stage, point=point or name, order='SERIAL_EXPLICIT', round=round, **fields)
        require(len(self.events) < MAX_EVENTS, 'EVENT_BUDGET')
        require(len(canonical(value)) <= MAX_EVENT_BYTES, 'EVENT_SIZE_BUDGET')
        self.events.append(value)

    def observe(self, label):
        values = inspect_files(self.value)
        self.oracles.append(dict(label=label, **{k:describe(v, roots(self.value)[k]) for k,v in values.items()}))
        self.event('ORACLE', operation='READ_FILES', point=label, hashes={k:digest(v['state']) for k,v in values.items()})
        return values

    def start_job(self, job, label):
        pair = start(worker, (self.value, job), dict(case=self.case, path=self.path, actor=label, action=job['action']))
        self.children.append(pair)
        self.event('SPAWN', actor=label, operation=job.get('operation', job['action']), mode=job.get('mode', 'NONE'), stage=job.get('stage', 'NONE'), point=job.get('point', 'START'))
        return pair

    def run_job(self, job, label):
        pair = self.start_job(job, label)
        try:
            event = receive(pair[1])
            require(event.get('event') == 'DONE' and event.get('status') == 'OK', event.get('code', 'WORKER_FAILURE'))
            finish(*pair)
            self.event('DONE', actor=label, role='CLIENT' if job['action'] != 'file_reader' else 'FILE_READER',
                       operation=job.get('operation', job['action']), mode=job.get('mode', 'NONE'), stage=job.get('stage', 'NONE'),
                       point=job.get('point', 'DONE'), output_sha256=digest(event['value']), transport=event['transport'])
            return event
        finally:
            stop_owned([pair])

    def crash(self, job, at_gate=None):
        job = dict(job, action='crash')
        pair = self.start_job(job, 'mutator')
        try:
            gate = receive(pair[1]); validate_gate(gate, job, self.value)
            at = self.observe('gate_'+job['point'])
            if at_gate:
                at_gate(at, gate)
            self.event('READY', actor='mutator', role='CLIENT', operation=job['operation'], mode=job['mode'], stage=job['stage'], point=job['point'], transport=gate['transport'])
            pair[0].kill(); finish(*pair, expected=-signal.SIGKILL)
            self.event('SIGKILL', actor='mutator', role='CLIENT', operation=job['operation'], mode=job['mode'], stage=job['stage'], point=job['point'], exitcode=pair[0].exitcode)
        finally:
            stop_owned([pair])
        return self.observe('after_sigkill')

    def passive(self, commands=()):
        before = self.observe('before_passive')
        reader = self.run_job(dict(action='file_reader'), 'independent_reader')['value']
        require(reader == before, 'FRESH_FILE_READER_CHANGED')
        opened = self.run_job(dict(action='passive', commands=list(commands)), 'public_passive')['value']
        require(opened['snapshot'] == dict(head=before['client']['head'], state=before['client']['state']), 'PUBLIC_REOPEN_CHANGED')
        require(self.observe('after_passive') == before, 'PASSIVE_MUTATION')
        self.event('PASSIVE_UNCHANGED', operation='SNAPSHOT/READ_COMMAND', round=2, receipt_reads={k:digest(v) for k,v in opened['commands'].items()})
        return opened

    def final_reader(self):
        before = self.observe('final')
        require(self.run_job(dict(action='file_reader'), 'final_reader')['value'] == before, 'FINAL_REOPEN_CHANGED')

    def command(self, operation, args):
        head = independent(self.lab.root/'client')['head']
        expected = {k:head[k] for k in ('seq','commit_sha256')}
        command = dict(kind=operation, args=args, cid=uid(), expected=expected)
        request_hash = digest(dict(kind=operation, args=args, expected=expected))
        self.record['command'] = dict(cid=command['cid'], operation=operation, args_sha256=digest(args), expected=expected, request_sha256=request_hash)
        return command, dict(cid=command['cid'], request_hash=request_hash)

    def early(self, index):
        """Only the required public setup; no operation under test during setup."""
        import base64
        self.raw, self.targets = R.source(tasks=1)
        self.sid = hashlib.sha256(self.raw).hexdigest()
        c = self.lab.client
        if index >= 1:
            c.capture(self.raw)
        if index >= 2:
            c.select_source(self.sid)
        if index >= 3:
            self.sm = c.perform('PREPARE_SOURCE', {})['result']['manifest_id']
        if index >= 4:
            c.review('SOURCE', self.sm)
        if index >= 5:
            self.bm = c.perform('PREPARE_BATCH', dict(source_manifest=self.sm, source_review=1, targets=self.targets))['result']['manifest_id']
        operation, self.stage = OPS[index]
        args = [dict(content_base64=base64.b64encode(self.raw).decode()), dict(source_id=self.sid), {},
                dict(stage='SOURCE', manifest_id=getattr(self,'sm',None), expected_version=0, decision='ACCEPT', reason_code='SYNTHETIC_REVIEW'),
                dict(source_manifest=getattr(self,'sm',None), source_review=1, targets=self.targets),
                dict(stage='BATCH', manifest_id=getattr(self,'bm',None), expected_version=0, decision='ACCEPT', reason_code='SYNTHETIC_REVIEW')][index]
        self.cmd, self.read = self.command(operation, args)
        self.before = self.observe('early_precondition')
        return dict(operation=operation, stage=self.stage, mode='LOCAL', command=self.cmd)

    def close(self, successful):
        try:
            stop_owned(self.children)
            self.lab.close()
            require(not self.lab.home.exists(), 'OWN_ROOT_REMAINS')
            if self.path == 'T':
                require(not self.lab.capture.root.exists(), 'OWN_CAPTURE_REMAINS')
            self.record['cleanup_verified'] = True
        except Exception:
            self.record['cleanup_verified'] = False
            raise
        finally:
            self.record['status'] = 'PASS' if successful and self.record.get('cleanup_verified') else 'FAIL'
            self.record['elapsed_seconds'] = round(time.monotonic()-self.started,3)


def hash_inputs(paths):
    return {str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(paths)}


def validate_inventory(before, after):
    require(before == after, 'STALE_INPUTS')


def validate_report(passed, expected, skipped, remaining):
    require(len(passed) == len(set(passed)), 'DUPLICATE_TEST_IDS')
    require(set(passed) == set(expected) and not skipped, 'INCOMPLETE_CAMPAIGN')
    require(remaining == 0, 'RESOURCES_REMAINING')


def bounded_raw(value, maximum=MAX_RAW_BYTES):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    require(len(raw.encode()) <= maximum, 'RAW_BUDGET')
    return raw


def raw_binding(path, expected_sha256=None, maximum=MAX_RAW_BYTES):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'RAW_MISSING_OR_TYPE')
    require(path.stat().st_size <= maximum, 'RAW_BUDGET')
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None:
        require(sha == expected_sha256, 'RAW_HASH_MISMATCH')
    try:
        report = json.loads(raw)
    except (ValueError, UnicodeError):
        raise AssertionError('RAW_INCOMPATIBLE') from None
    require(type(report) is dict and report.get('status') == 'PASS' and
            type(report.get('passed')) is list and type(report.get('tests_run')) is int,
            'RAW_INCOMPATIBLE')
    require(report['tests_run'] == len(report['passed']) == len(set(report['passed'])), 'RAW_COUNTS')
    return dict(sha256=sha, bytes=len(raw), tests_run=report['tests_run'], schema=report.get('schema'))
