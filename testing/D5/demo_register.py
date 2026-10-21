# SPDX-License-Identifier: GPL-3.0-only
"""Run from repository root; synthetic observations and comparison only."""
from pathlib import Path
import argparse
import json
from source_ingest.preview import observe, save_preview
from source_ingest.compare import compare_previews


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=['task-register.v1', 'task-register-compat.v1'], default='task-register.v1')
    args = parser.parse_args()
    prefix = 'register-compat' if args.profile == 'task-register-compat.v1' else 'register'
    paths = []
    for file, revision in [(prefix + '-before.md', 'fixture-v1'), (prefix + '-after.md', 'fixture-v2')]:
        value = observe(Path(__file__).parent / 'fixtures', file,
                        '00000000-0000-4000-8000-000000000001',
                        '00000000-0000-4000-8000-000000000002', revision, args.profile)
        paths.append(save_preview('work/d5/register-demo/previews', value)[0])
    report = compare_previews(*paths)
    result, _ = save_preview('work/d5/register-demo/comparisons', report)
    counts = {}
    for item in report['changes']:
        counts[item['change']] = counts.get(item['change'], 0) + 1
    print(json.dumps({'counts': counts, 'before': str(paths[0]), 'after': str(paths[1]), 'comparison': str(result), 'state': report['state']}))


if __name__ == '__main__':
    main()
