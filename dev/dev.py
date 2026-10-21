#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Local development lifecycle. No D4 campaign is run or rewritten."""
import argparse
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
PG = 'postgres@sha256:0ea6700a3b4f0ae6ce746519073558aed4d88a79d8d07622a9a644946c7319c4'
PROXY = 'python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1'
JAVA = 'maven@sha256:99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320'
SERVICES = ['db', 'control-plane', 'effect-receiver', 'worker-a', 'worker-b', 'verifier', 'driver', 'diagnostics']

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'up', 'status', 'logs', 'smoke', 'stop', 'restart', 'rebuild', 'reset', 'config'])
    parser.add_argument('--instance', help='isolated local instance (overrides .env)')
    parser.add_argument('--service', choices=SERVICES, help='limit logs or rebuild to one service')
    args = parser.parse_args()
    env = dict(os.environ)
    dotenv = ROOT / '.env'
    if dotenv.exists():
        for line in dotenv.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, sep, value = line.partition('=')
            if not sep or not re.fullmatch(r'DEV_[A-Z_]+', key) or any(c in value for c in '\n\r\"\'`$'):
                parser.error('.env supports literal DEV_KEY=value entries only; see .env.example')
            env.setdefault(key, value)
    name = args.instance or env.get('DEV_INSTANCE', 'local')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,30}', name):
        parser.error('instance must match [a-z][a-z0-9-]{0,30}')
    data = ROOT / 'run_data'
    data.mkdir(mode=0o700, exist_ok=True)
    path = data / name
    if data.is_symlink() or path.is_symlink():
        parser.error('run_data and instance must not be symlinks')
    lock = (data / (name + '.lock')).open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    path.mkdir(mode=0o700, exist_ok=True)
    state = path / 'state'
    case = path / 'identity'
    for folder in [state, case, path / 'logs']:
        if folder.is_symlink():
            parser.error('instance directories must not be symlinks')
    for folder in [state, path / 'logs']:
        folder.mkdir(mode=0o700, exist_ok=True)
    for key in ['DEV_STATE', 'LAB_CASE_DIR', 'LAB_IMAGE', 'PG_IMAGE', 'LAB_UID', 'LAB_GID']:
        env.pop(key, None)
    imagefile = path / 'image.txt'
    env.update(DEV_STATE=str(state), LAB_CASE_DIR=str(case), LAB_IMAGE=imagefile.read_text().strip() if imagefile.exists() else 'wap-dev:unbuilt', PG_IMAGE=PG, LAB_UID=str(os.getuid()), LAB_GID=str(os.getgid()))
    base = ['docker', 'compose', '--env-file', '/dev/null', '-f', str(ROOT / 'compose.dev.yaml'), '-p', 'wap-dev-' + name]

    def run(cmd, **kwargs):
        return subprocess.run(cmd, env=env, check=True, **kwargs)

    def compose(*cmd, **kwargs):
        return run(base + list(cmd), **kwargs)

    def build():
        run(['docker', 'pull', JAVA])
        run(['docker', 'pull', PG])
        run(['docker', 'pull', PROXY])
        buildpath = data / 'builds' / (time.strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8])
        buildpath.mkdir(parents=True)
        run(['bash', str(ROOT / 'dev/build.sh'), str(buildpath)])
        imagefile.write_text((buildpath / 'image-tag.txt').read_text())
        env['LAB_IMAGE'] = imagefile.read_text().strip()
        print('Build logs:', buildpath, flush=True)

    def up():
        if not imagefile.exists():
            raise RuntimeError('Run build first')
        if not case.exists():
            module('dev_config', ROOT / 'testing/D4/lab-config.py').prepare(case, 'DEV', str(uuid.uuid4()))
        run(['openssl', 'x509', '-checkend', '60', '-noout', '-in', str(case / 'public/ca.crt')], stdout=subprocess.DEVNULL)
        marker = path / 'bootstrapped'
        if not marker.exists():
            compose('up', '-d', '--wait', 'db')
            compose('run', '--rm', 'migrate')
            marker.write_text('Synthetic V30 bootstrap completed\n')
        compose('up', '-d', '--wait', '--wait-timeout', '180', *SERVICES)

    if args.command == 'build':
        build()
    elif args.command == 'up':
        up()
    elif args.command in ['config', 'status', 'logs']:
        commands = {'config': ['config', '--no-env-resolution', '--quiet'], 'status': ['ps', '--all'], 'logs': ['logs', '--tail', '80']}
        compose(*commands[args.command], *([args.service] if args.service and args.command == 'logs' else []))
    elif args.command == 'stop':
        # Preserve all state. Container exit is not acceptance or a stop proof.
        with (path / 'logs' / ('stop-' + str(time.time_ns()) + '.log')).open('w') as out:
            compose('logs', '--no-color', stdout=out, stderr=subprocess.STDOUT)
        compose('stop', '--timeout', '15')
    elif args.command == 'restart':
        compose('restart', *SERVICES)
        up()
    elif args.command == 'rebuild':
        if args.service == 'db':
            parser.error('db is pinned; use restart, not rebuild')
        build()
        compose('up', '-d', '--no-deps', '--force-recreate', '--wait', '--wait-timeout', '180', *([args.service] if args.service else SERVICES[1:]))
    elif args.command == 'reset':
        # Identity/config are removed only after the selected Compose project is down.
        compose('down', '--remove-orphans')
        run(['docker', 'run', '--rm', '--network', 'none', '--mount', 'type=bind,src=' + str(state) + ',dst=/reset', '--entrypoint', 'sh', JAVA, '-c', 'find /reset -mindepth 1 -delete'])
        if case.exists():
            shutil.rmtree(case)
        (path / 'bootstrapped').unlink(missing_ok=True)
        print('Reset only wap-dev-' + name + '; build cache and logs retained')
    elif args.command == 'smoke':
        lab = module('dev_helpers', ROOT / 'testing/D4/lab-scenarios.py')
        c = lab.Case.__new__(lab.Case)
        c.env, c.base, c.path, c.checks = env, base, case, []
        c.campaign = json.loads((case / 'public/participants.json').read_text())['campaign']
        c.fixture = json.loads((case / 'public/fixture.json').read_text())
        c.run, c.scenario = path, 'DEV'
        # Readiness and a repeatable read-only check after the first completed operation.
        for service in SERVICES[1:6]:
            c.cli(service, 'health')
        before = c.audit()
        if not before['attempts']:
            c.api('worker-a', '/lab/run', {})
            s = c.phase(['CALLBACK_CONFIRMED'])
            c.complete(s)  # Host-signed process observation + independent HTTPS verifier.
        audit = c.audit()
        c.ledger(audit, c.fixture['account_a'], 0, 8)
        c.ledger(audit, c.fixture['account_b'], 0, 0)
        c.check('one_attempt_reservation_effect', len(audit['attempts']) == len(audit['reservations']) == len(audit['effects']) == 1)
        c.check('independent_acceptance', len(audit['acceptance']) == 1)
        for worker in ['worker-a', 'worker-b']:
            c.check(worker + '_no_sql', not c.jsoncli(worker, 'network-probe', 'db', '5432')['reachable'])
            c.check(worker + '_no_internet', not c.jsoncli(worker, 'network-probe', '1.1.1.1', '443')['reachable'])
        report = {'scope': 'development smoke only', 'checks': c.checks, 'audit': audit}
        output = path / 'logs' / ('smoke-' + str(time.time_ns()) + '.json')
        output.write_text(json.dumps(report, indent=2) + '\n')
        print('PASS:', len(c.checks), 'checks;', output)

if __name__ == '__main__':
    try:
        main()
    except BlockingIOError:
        sys.exit('Another command is running for this instance; wait for it to finish')
    except (RuntimeError, subprocess.CalledProcessError) as ex:
        sys.exit(str(ex))
