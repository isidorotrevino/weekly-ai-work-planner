# SPDX-License-Identifier: GPL-3.0-only
import argparse
import json
from .preview import observe, save_preview


def main():
    parser = argparse.ArgumentParser(description='D5 local Markdown preview; no task activation or provider access')
    parser.add_argument('--root', required=True, help='explicit source directory, read only')
    parser.add_argument('--file', required=True, help='relative Markdown path within root')
    parser.add_argument('--project-id', required=True, help='caller-selected project UUID; no database lookup')
    parser.add_argument('--document-id', required=True, help='stable caller-selected document UUID')
    parser.add_argument('--revision', required=True, help='caller-supplied observation label, not Git attestation')
    parser.add_argument('--store', default='work/d5/previews', help='private local artifact directory')
    args = parser.parse_args()
    try:
        observation = observe(args.root, args.file, args.project_id, args.document_id, args.revision)
        path, digest = save_preview(args.store, observation)
    except (OSError, ValueError, UnicodeError) as ex:
        parser.exit(1, 'Preview rejected: ' + str(ex) + '\n')
    print(json.dumps({'state': observation['state'], 'activation_allowed': False, 'preview': str(path), 'preview_sha256': digest,
                      'content_sha256': observation['content_sha256'], 'sections': len(observation['sections']),
                      'proposals': len(observation['proposals']), 'diagnostics': [d['code'] for d in observation['diagnostics']]}))


if __name__ == '__main__':
    main()
