# SPDX-License-Identifier: GPL-3.0-only
"""Verified local previews -> disposable D5 PostgreSQL lab. No network connectors."""
import argparse
import base64
import hashlib
import json
import re
import subprocess
import uuid

from .compare import _unique_keys, load_preview
from .preview import MAX_BYTES, MAX_PREVIEW_BYTES, build_observation, canonical

PROFILES = ('markdown-structure.v1', 'task-register.v1', 'task-register-compat.v1')


def identity(value):
    if not isinstance(value, str) or str(uuid.UUID(value)) != value:
        raise ValueError('Canonical UUID required')
    return value


def envelope(command_id, action, project_id, document_id, **fields):
    return dict(schema='d5.source-command.v1', command_id=identity(command_id), action=action,
                project_id=identity(project_id), document_id=identity(document_id), **fields)


def ingest_request(command_id, preview_path):
    # Full existing deterministic reconstruction occurs before any SQL session.
    observation, digest = load_preview(preview_path)
    return (envelope(command_id, 'INGEST', observation['project_id'], observation['document_id'],
                     profile=observation['profile'], preview_sha256=digest,
                     content_sha256=observation['content_sha256']),
            base64.b64decode(observation['content_base64'], validate=True), canonical(observation))


def sql_text(value):
    """Only hex reaches SQL syntax; input is data and never a psql command."""
    return "convert_from(decode('" + value.encode('utf-8').hex() + "','hex'),'UTF8')"


def sql_bytes(value):
    return 'NULL::bytea' if value is None else "decode('" + value.hex() + "','hex')"


def submit_sql(request, source=None, artifact=None):
    if (source is not None and len(source) > MAX_BYTES) or (artifact is not None and len(artifact) > MAX_PREVIEW_BYTES):
        raise ValueError('Blob exceeds limits')
    return 'SELECT d5.submit(' + sql_text(json.dumps(request, ensure_ascii=True, allow_nan=False)) + '::json,' + sql_bytes(source) + ',' + sql_bytes(artifact) + ');'


class LabClient:
    """psql over Docker exec; exclusively targets a labelled networkless lab."""
    def __init__(self, container, role='d5_writer'):
        if not re.fullmatch(r'd5-pg-[a-z0-9-]+', container) or role not in ('d5_writer', 'd5_reader'):
            raise ValueError('Expected disposable D5 container and lab role')
        check = subprocess.run(['docker', 'inspect', container], check=True, capture_output=True, text=True)
        data = json.loads(check.stdout)[0]
        if data['Config'].get('Labels', {}).get('wap.d5.disposable') != 'true' or data['HostConfig']['NetworkMode'] != 'none':
            raise ValueError('Container is not an isolated D5 laboratory')
        self.container, self.role = container, role

    def query(self, sql):
        run = subprocess.run(['docker', 'exec', '-i', self.container, 'psql', '-X', '-qAt', '-U', self.role,
                              '-d', 'd5_lab', '-v', 'ON_ERROR_STOP=1'], input=sql, capture_output=True, text=True, timeout=60)
        if run.returncode:
            # SQL/psql error context may contain a private payload. Do not echo it.
            raise RuntimeError('D5 SQL request failed; transaction not acknowledged')
        return json.loads(run.stdout) if run.stdout.strip() else None

    def submit(self, request, source=None, artifact=None):
        if request.get('action') == 'INGEST':
            # Public API never accepts an unverified artifact, even if called without CLI.
            verify_payload(source, artifact, request)
        return self.query(submit_sql(request, source, artifact))

    def ingest(self, command_id, path):
        return self.submit(*ingest_request(command_id, path))

    def read_command(self, command_id):
        return self.query('SELECT d5.read_command(' + sql_text(identity(command_id)) + '::uuid);')

    def read_reference(self, project_id, document_id, profile):
        if profile not in PROFILES:
            raise ValueError('Unknown profile')
        return self.query('SELECT d5.read_reference(' + sql_text(identity(project_id)) + '::uuid,' +
                          sql_text(identity(document_id)) + '::uuid,' + sql_text(profile) + '::d5.profile);')

    def recover(self, project_id, document_id, observation_id):
        data = self.query('SELECT d5.read_observation(' + ','.join(sql_text(identity(x)) + '::uuid' for x in
                          (project_id, document_id, observation_id)) + ');')
        if data is None:
            return None
        source, artifact = bytes.fromhex(data['source_hex']), bytes.fromhex(data['preview_hex'])
        if hashlib.sha256(source).hexdigest() != data['content_sha256'] or hashlib.sha256(artifact).hexdigest() != data['preview_sha256']:
            raise ValueError('Stored bytes failed hash validation')
        value = verify_payload(source, artifact)
        if value['project_id'] != project_id or value['document_id'] != document_id:
            raise ValueError('Recovery scope mismatch')
        return source, artifact


def verify_payload(source, artifact, request=None):
    if not isinstance(source, bytes) or not isinstance(artifact, bytes) or len(source) > MAX_BYTES or len(artifact) > MAX_PREVIEW_BYTES:
        raise ValueError('Missing bytes or limit exceeded')
    value = json.loads(artifact, object_pairs_hook=_unique_keys)
    expected = build_observation(source, value['source_path'], value['project_id'], value['document_id'],
                                 value['observed_revision'], value['profile'])
    if canonical(expected) != artifact:
        raise ValueError('Artifact differs from deterministic reconstruction')
    if request is not None:
        for key in ('project_id', 'document_id', 'profile', 'content_sha256'):
            if request.get(key) != expected[key]:
                raise ValueError('Request scope or content differs from artifact')
        if request.get('preview_sha256') != hashlib.sha256(artifact).hexdigest():
            raise ValueError('Request artifact digest mismatch')
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', required=True, help='Labelled isolated D5 lab container only')
    actions = parser.add_subparsers(dest='action', required=True)
    for name in ('register', 'ingest', 'select', 'reference', 'receipt'):
        p = actions.add_parser(name)
        if name not in ('reference',):
            p.add_argument('--command-id', required=True)
        if name in ('register', 'select', 'reference'):
            p.add_argument('--project-id', required=True)
            p.add_argument('--document-id', required=True)
        if name == 'register':
            p.add_argument('--namespace', required=True)
            p.add_argument('--logical-key', required=True)
        if name == 'ingest':
            p.add_argument('--preview', required=True)
        if name in ('select', 'reference'):
            p.add_argument('--profile', choices=PROFILES, required=True)
        if name == 'select':
            p.add_argument('--observation-id', required=True)
            p.add_argument('--expected-version', type=int, required=True)
            p.add_argument('--reason', required=True)
    args = parser.parse_args()
    try:
        client = LabClient(args.container, 'd5_reader' if args.action in ('reference', 'receipt') else 'd5_writer')
        if args.action == 'ingest':
            result = client.ingest(args.command_id, args.preview)
        elif args.action == 'receipt':
            result = client.read_command(args.command_id)
        elif args.action == 'reference':
            result = client.read_reference(args.project_id, args.document_id, args.profile)
        elif args.action == 'register':
            result = client.submit(envelope(args.command_id, 'REGISTER_SOURCE', args.project_id, args.document_id,
                                           namespace=args.namespace, logical_key=args.logical_key))
        else:
            result = client.submit(envelope(args.command_id, 'SELECT_REFERENCE', args.project_id, args.document_id,
                                           profile=args.profile, observation_id=identity(args.observation_id),
                                           expected_version=args.expected_version, reason=args.reason))
        print(json.dumps(result, sort_keys=True))
        return 2 if result and result.get('status') == 'CONFLICT' else 0
    except (ValueError, KeyError, TypeError, RuntimeError, OSError, subprocess.SubprocessError):
        print('D5 lab request failed; no success acknowledged', file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
