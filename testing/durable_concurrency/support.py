# SPDX-License-Identifier: GPL-3.0-only
"""I42 owned spawn controls and independent file oracle; no product hooks added."""
import errno
import fcntl
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import stat
import time
import uuid

from source_ingest.durable_store import DurableError
from testing.D5 import durable_support as T, relational_support as R

CTX = multiprocessing.get_context('spawn')
CHILDREN = []
RECORDS = []
EXTRA_ROOTS = []
WAIT_SECONDS = 20
CASE_SECONDS = 120
MAX_EVENTS = 256
MAX_EVENT_BYTES = 16 * 1024
MAX_RAW_BYTES = 8 * 1024 * 1024


def require(condition, code):
    if not condition:
        raise AssertionError(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def uid():
    return str(uuid.uuid4())


def independent(path):
    """Read bytes/hash/chain/receipts independently; checks survive Python -O."""
    path = Path(path)
    marker = json.loads((path / 'marker.json').read_bytes())
    head = json.loads((path / 'head.json').read_bytes())
    keys = ('run_id', 'store_id', 'role')
    require(all(head[k] == marker[k] for k in keys), 'ORACLE_IDENTITY')
    current = head['commit_sha256']
    chain, seen = [], set()
    while current is not None:
        require(current not in seen, 'ORACLE_CYCLE')
        seen.add(current)
        raw = (path / 'objects' / (current + '.json')).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == current, 'ORACLE_OBJECT_HASH')
        value = json.loads(raw)
        require(all(value[k] == marker[k] for k in keys), 'ORACLE_OBJECT_IDENTITY')
        chain.append(value)
        current = value['parent_sha256']
    chain.reverse()
    require(len(chain) == head['seq'] + 1, 'ORACLE_CHAIN_LENGTH')
    prior_receipts = {}
    for seq, value in enumerate(chain):
        require(value['seq'] == seq, 'ORACLE_SEQ')
        receipts = value['state']['receipts']
        require(all(receipts.get(k) == v for k, v in prior_receipts.items()), 'ORACLE_RECEIPT_LOST')
        if seq:
            receipt = receipts[value['command_id']]
            require(receipt == value['receipt'], 'ORACLE_RECEIPT')
            require(receipt['request_sha256'] == value['request_sha256'], 'ORACLE_REQUEST')
            require(not receipt['grants_execution_authority'] and not receipt['activation_allowed'], 'ORACLE_AUTHORITY')
            require(receipt['quota_consumed'] == receipt['reservations_created'] == 0, 'ORACLE_RESOURCES')
        prior_receipts = receipts
    return dict(head=head, state=chain[-1]['state'], chain=chain)


def fingerprint(value):
    state = value['state']
    return dict(head=value['head'], state_sha256=digest(state), receipts=len(state['receipts']),
                entities=len(state.get('entities', state.get('tasks', state.get('data', {}).get('entities', {})))),
                tickets=len(state.get('tickets', {})), pending=len(state.get('pending', {})))


def spec(lab, path):
    return dict(path=path, store=T.reopen_spec(lab) if path == 'T' else R.spec(lab))


def open_client(value, hook=None, remote_hook=None):
    return (T if value['path'] == 'T' else R).open_client(value['store'], hook, remote_hook)


def probe_locked(path):
    fd = os.open(Path(path) / 'lock', os.O_RDWR | os.O_NOFOLLOW)
    try:
        require(stat.S_ISREG(os.fstat(fd).st_mode), 'PROBE_NOT_REGULAR')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as ex:
            require(ex.errno in (errno.EAGAIN, errno.EWOULDBLOCK), 'PROBE_UNEXPECTED_ERROR')
            return 'LOCK_HELD_OBSERVED'
        raise AssertionError('PROBE_NOT_HELD')
    finally:
        os.close(fd)


def receive(conn, timeout=WAIT_SECONDS):
    require(conn.poll(timeout), 'CONTROL_TIMEOUT')
    try:
        return conn.recv()
    except EOFError:
        raise AssertionError('CONTROL_EOF') from None


def expect_event(message, expected):
    require(message.get('event') == expected, 'MISSING_'+expected)
    return message


def actor(value, job, conn):
    """No inherited client authority. Only existing hooks and public calls."""
    armed = job['action'] != 'reconcile'
    used = False
    proof_seen = None

    def hook(point):
        nonlocal armed, used
        if job['action'] == 'reconcile' and point == 'before_result':
            store = value['store']
            root = store['client_path'] if value['path'] == 'T' else store['client']
            pending = independent(root)['state']['pending']
            queries = [k for k, v in pending.items() if v['send_id'] == job['sid'] and not k.startswith('send:')]
            require(len(queries) == 1, 'QUERY_ID_NOT_UNIQUE')
            conn.send(dict(event='QUERY_OBSERVED', proof_sha256=digest(proof_seen), query_id=queries[0]))
            require(receive(conn) == 'CONTINUE', 'CONTROL_QUERY_ACK')
            armed = True
        if armed and not used and point == 'before_lock':
            used = True
            conn.send(dict(event='READY', point=point))
            command = receive(conn)
            require(command in ('WIN', 'CONTEND'), 'CONTROL_RELEASE')
            if command == 'CONTEND':
                store = value['store']
                root = (store['client_path'] if value['path'] == 'T' else store['client']) if job['role'] == 'CLIENT' else (store['remote_path'] if value['path'] == 'T' else store['remote'])
                conn.send(dict(event=probe_locked(root), point='probe_lock'))
        elif armed and used and point == 'before_object':
            conn.send(dict(event='LOCKED', point=point))
            require(receive(conn) == 'COMMIT', 'CONTROL_COMMIT_ACK')

    try:
        c = open_client(value, hook if job['role'] == 'CLIENT' else None,
                        hook if job['role'] == 'REMOTE' else None)
        if job['action'] == 'reconcile':
            original = c.remote.lookup

            def observed(ticket, manifest):
                nonlocal proof_seen
                proof_seen = original(ticket, manifest)
                return proof_seen
            c.remote.lookup = observed
            out = c.reconcile(job['sid'])
        elif job['action'] == 'perform':
            out = c.perform(job['operation'], job['args'])
        elif job['action'] == 'edit':
            out = c.remote.store.transact(job['cid'], 'EDIT', job['args'])
        elif job['action'] == 'execute':
            out = c.remote.execute(job['ticket'], job['manifest'])
        else:
            raise AssertionError('UNKNOWN_ACTION')
        conn.send(dict(event='DONE', status='OK', value=out))
    except DurableError as ex:
        conn.send(dict(event='DONE', status='ERROR', code=str(ex)))
    except Exception as ex:
        # Errors are identifiers only; never leak source, payload or temp path.
        conn.send(dict(event='DONE', status='HARNESS_ERROR', code=type(ex).__name__))
    finally:
        conn.close()


def reader(value, conn):
    try:
        store = value['store']
        client = store['client_path'] if value['path'] == 'T' else store['client']
        remote = store['remote_path'] if value['path'] == 'T' else store['remote']
        conn.send(dict(event='REOPEN', client=fingerprint(independent(client)), remote=fingerprint(independent(remote))))
    except Exception as ex:
        conn.send(dict(event='REOPEN_ERROR', code=type(ex).__name__))
    finally:
        conn.close()


def start(target, args, label):
    require(sum(p.is_alive() for p, _ in CHILDREN) < 4, 'CHILD_BUDGET')
    parent, child = CTX.Pipe()
    process = CTX.Process(target=target, args=(*args, child))
    process.start()
    child.close()
    CHILDREN.append((process, label))
    return process, parent


def finish(process, conn):
    process.join(WAIT_SECONDS)
    if process.is_alive():
        process.kill()
        process.join(WAIT_SECONDS)
        conn.close()
        raise AssertionError('CHILD_JOIN_TIMEOUT')
    conn.close()
    require(process.exitcode == 0, 'CHILD_EXIT')


def stop_owned(children):
    for process, conn in children:
        if process.is_alive():
            process.kill()
        process.join(WAIT_SECONDS)
        conn.close()
    require(all(not p.is_alive() for p, _ in children), 'CHILD_REMAINING')


class Scenario:
    def __init__(self, case, path):
        self.case, self.path = case, path
        self.events, self.oracles, self.children = [], [], []
        self.started = time.monotonic()
        self.lab = (T if path == 'T' else R).new_lab()
        self.value = spec(self.lab, path)
        self.record = dict(case=case, path=path, run_id=self.lab.run_id, status='RUNNING', events=self.events, oracles=self.oracles)
        RECORDS.append(self.record)

    def event(self, event, actor='parent', role='HARNESS', operation='CONTROL', mode='NONE', order='NONE', round=1, **fields):
        require(time.monotonic() - self.started < CASE_SECONDS, 'CASE_TIMEOUT')
        value = dict(event=event, case=self.case, path=self.path, actor=actor, role=role, operation=operation,
                     mode=mode, order=order, round=round, point=fields.pop('point', event), **fields)
        require(len(self.events) < MAX_EVENTS, 'EVENT_BUDGET')
        require(len(canonical(value)) <= MAX_EVENT_BYTES, 'EVENT_SIZE_BUDGET')
        self.events.append(value)

    def observe(self, label):
        values = {role: independent(self.lab.root / role) for role in ('client', 'remote')}
        summaries = {k: fingerprint(v) for k, v in values.items()}
        client_state, remote_state = values['client']['state'], values['remote']['state']
        summaries['client']['sends'] = [dict(send_id=sid, status=send['status'], ledger_version=send['ledger_version'],
             hard_conflict=send['hard_conflict'], proof_sha256=digest(send['proof'])) for sid, send in client_state.get('sends', {}).items()]
        summaries['client']['projection_reviews'] = {key:dict(version=value['version'], decision=value['decision'])
             for key, value in client_state.get('reviews', {}).items() if key.startswith('PROJECTION:')}
        summaries['remote']['entity_versions'] = [dict(remote_id=rid, version=entity['version'], payload_sha256=digest(entity['payload']),
             foreign_sha256=digest(entity['foreign'])) for rid, entity in remote_state['entities'].items()]
        self.oracles.append(dict(label=label, **summaries))
        self.event('ORACLE', operation='READ_FILES', point=label, state_hashes={k: digest(v['state']) for k, v in values.items()})
        return values

    def prepare(self, issue=True):
        if self.path == 'T':
            self.ids = T.ready(self.lab)
            self.mid, self.bid = self.ids['projection'], T.uid(40)
        else:
            raw, targets = R.source(tasks=1)
            self.ids = R.prepare(self.lab, raw, targets)
            self.mid, self.bid = self.ids['projections'][0], self.ids['bindings'][0]
        if issue:
            self.send = self.lab.client.dispatch(self.mid, 1, deliver=False)
            self.manifest = self.lab.client.snapshot()['state']['manifests'][self.mid]
            self.proof = self.lab.remote.execute(self.send['ticket'], self.manifest)
            self.event('REMOTE_EFFECT', role='REMOTE', operation='EXECUTE', mode='CREATE', proof_sha256=digest(self.proof))
        self.record['identities'] = dict(client_store_id=self.lab.client_id, remote_store_id=self.lab.remote_id, binding_id=self.bid, manifest_id=self.mid, review_version=1)
        if issue:
            self.record['identities'].update(send_id=self.send['send_id'], ticket=self.send['ticket'], target_id=self.manifest['target_id'], manifest_sha256=digest(self.manifest), payload_sha256=digest(self.manifest['payload']), proof_sha256=digest(self.proof))
        observed = self.observe('prepared')
        if issue:
            remote = observed['remote']['state']
            require(remote['tickets'][self.send['ticket']] == self.proof, 'SETUP_TICKET_PROOF')
            require(self.proof['manifest_hash'] == self.proof['request_hash'] == digest(self.manifest), 'SETUP_MANIFEST_PROOF')
            require(self.proof['creation_key'] == self.manifest['creation_key'], 'SETUP_CREATION_KEY')
            require(self.proof['run_id'] == self.lab.run_id and self.proof['store_id'] == self.lab.remote_id, 'SETUP_PROOF_IDENTITY')
            entity = remote['entities'][self.proof['remote_id']]
            require(entity['version'] == self.proof['applied_version'] == 1, 'SETUP_ENTITY_VERSION')
            require(entity['payload'] == self.manifest['payload'] and digest(entity['payload']) == self.proof['payload_hash'], 'SETUP_ENTITY_PAYLOAD')
            send = observed['client']['state']['sends'][self.send['send_id']]
            require(send['status'] == 'UNKNOWN' and send['ledger_version'] == 1, 'SETUP_CLIENT_LEDGER')
            require('send:'+self.send['ticket'] in observed['client']['state']['pending'], 'SETUP_PENDING_SEND')

    def result_args(self, proof=None, ledger=1):
        return dict(send_id=self.send['send_id'], ledger_version=ledger,
                    proof=self.proof if proof is None else proof, query_id=None)

    def update(self):
        self.prepare()
        self.lab.client.perform('RESULT', self.result_args())
        rid = self.proof['remote_id']
        self.lab.remote.edit(rid, foreign=dict(sentinel='keep'))
        self.mid = self.lab.client.prepare_projection(self.bid)['result']['manifest_id']
        self.lab.client.review('PROJECTION', self.mid)
        self.send = self.lab.client.dispatch(self.mid, 1, deliver=False)
        self.manifest = self.lab.client.snapshot()['state']['manifests'][self.mid]
        self.record['update_identities'] = dict(manifest_id=self.mid, send_id=self.send['send_id'], ticket=self.send['ticket'], binding_id=self.bid, target_id=self.manifest['target_id'], manifest_sha256=digest(self.manifest), payload_sha256=digest(self.manifest['payload']), review_version=1)
        self.base = self.manifest['remote_base']
        require(self.manifest['operation'] == 'UPDATE', 'SETUP_NOT_UPDATE')
        self.edit_args = dict(remote_id=rid, expected_version=self.base['version'],
                              payload=dict(name='Edited synthetic', description='Independent synthetic edit'),
                              foreign=self.base['foreign'])
        require(self.edit_args['payload'] != self.manifest['payload'], 'SETUP_PAYLOADS_EQUAL')
        self.event('UPDATE_PREPARED', role='REMOTE', operation='EDIT/EXECUTE', mode='UPDATE',
                   base_sha256=digest(self.base), version=self.base['version'], manifest_sha256=digest(self.manifest))
        self.before_update = self.observe('update_prepared')
        require(self.before_update['remote']['state']['entities'][self.base['id']] == self.base, 'SETUP_UPDATE_BASE')

    def spawn(self, job, actor_name):
        pair = start(actor, (self.value, job), dict(case=self.case, actor=actor_name, path=self.path))
        self.children.append(pair)
        self.event('SPAWN', actor=actor_name, role=job['role'], operation=job['operation'], mode=job.get('mode', 'CREATE'))
        return pair

    def race(self, jobs, winner):
        handles = []
        order = jobs[winner]['operation'] + '_FIRST'
        try:
            # reconcile creates QUERY and reaches before_result before D prepares.
            for index, job in enumerate(jobs):
                p, conn = self.spawn(job, str(index))
                handles.append((p, conn))
                if job['action'] == 'reconcile':
                    event = receive(conn)
                    require(event['event'] == 'QUERY_OBSERVED' and event['proof_sha256'] == digest(self.proof), 'QUERY_PROOF')
                    self.event(**event, actor=str(index), role='CLIENT', operation='QUERY', mode='CREATE', order=order)
                    conn.send('CONTINUE')
                event = receive(conn)
                expect_event(event, 'READY')
                self.event(**event, actor=str(index), role=job['role'], operation=job['operation'], mode=job.get('mode', 'CREATE'), order=order)
            self.observe('both_prepared')
            wp, wc = handles[winner]
            loser = 1 - winner
            lp, lc = handles[loser]
            wc.send('WIN')
            event = receive(wc)
            require(event['event'] == 'LOCKED', 'WINNER_NOT_LOCKED')
            self.event(**event, actor=str(winner), role=jobs[winner]['role'], operation=jobs[winner]['operation'], mode=jobs[winner].get('mode', 'CREATE'), order=order)
            self.observe('winner_lock_before_publish')
            lc.send('CONTEND')
            event = receive(lc)
            require(event['event'] == 'LOCK_HELD_OBSERVED', 'LOCK_NOT_OBSERVED')
            self.event(**event, actor=str(loser), role=jobs[loser]['role'], operation=jobs[loser]['operation'], mode=jobs[loser].get('mode', 'CREATE'), order=order)
            wc.send('COMMIT')
            outcomes = [None, None]
            for index in (winner, loser):
                p, conn = handles[index]
                event = receive(conn)
                # EDIT-first permits UPDATE's terminal NO_EFFECT ticket commit.
                if event['event'] == 'LOCKED':
                    require(index == loser, 'EXTRA_WINNER_COMMIT')
                    self.event(**event, actor=str(index), role=jobs[index]['role'], operation=jobs[index]['operation'], mode=jobs[index].get('mode', 'CREATE'), order=order)
                    conn.send('COMMIT')
                    event = receive(conn)
                require(event['event'] == 'DONE' and event['status'] != 'HARNESS_ERROR', 'ACTOR_FAILURE')
                outcomes[index] = event
                self.event('DONE', actor=str(index), role=jobs[index]['role'], operation=jobs[index]['operation'], mode=jobs[index].get('mode', 'CREATE'), order=order,
                           status=event['status'], code=event.get('code'), output_sha256=digest(event.get('value')))
                finish(p, conn)
            self.observe('race_complete')
            return outcomes
        finally:
            stop_owned(handles)

    def reopen(self):
        expected = self.observe('before_fresh_reader')
        pair = start(reader, (self.value,), dict(case=self.case, actor='reader', path=self.path))
        self.children.append(pair)
        try:
            event = receive(pair[1])
            require(event['event'] == 'REOPEN', 'REOPEN_FAILED')
            require(all(event[k] == fingerprint(v) for k, v in expected.items()), 'REOPEN_CHANGED')
            self.event('FRESH_REOPEN_MATCH', actor='reader', operation='READ_FILES', point='final', fingerprints_sha256=digest(event))
            finish(*pair)
        finally:
            stop_owned([pair])

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
            self.record['status'] = 'FAIL'
            raise
        finally:
            self.record['status'] = 'PASS' if successful and self.record.get('cleanup_verified') else 'FAIL'
            self.record['elapsed_seconds'] = round(time.monotonic() - self.started, 3)


def expect_error(code, call, *args, **kwargs):
    try:
        call(*args, **kwargs)
    except DurableError as ex:
        require(str(ex) == code, 'WRONG_PRODUCT_ERROR')
        return
    raise AssertionError('EXPECTED_ERROR_ABSENT')


def hash_inputs(paths):
    return {str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(paths)}


def validate_inventory(before, after):
    require(before == after, 'STALE_INPUTS')


def validate_report(passed, expected, skipped, remaining):
    require(len(passed) == len(set(passed)), 'DUPLICATE_TEST_IDS')
    require(set(passed) == set(expected) and not skipped, 'INCOMPLETE_CAMPAIGN')
    require(remaining == 0, 'RESOURCES_REMAINING')
