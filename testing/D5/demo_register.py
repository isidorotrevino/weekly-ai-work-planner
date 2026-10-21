# SPDX-License-Identifier: GPL-3.0-only
"""Run from repository root; synthetic observations and comparison only."""
from pathlib import Path
import json
from source_ingest.preview import observe, save_preview
from source_ingest.compare import compare_previews


def main():
    paths = []
    for file, revision in [('register-before.md', 'fixture-v1'), ('register-after.md', 'fixture-v2')]:
        value = observe(Path(__file__).parent / 'fixtures', file,
                        '00000000-0000-4000-8000-000000000001',
                        '00000000-0000-4000-8000-000000000002', revision, 'task-register.v1')
        paths.append(save_preview('work/d5/register-demo/previews', value)[0])
    report = compare_previews(*paths)
    result, _ = save_preview('work/d5/register-demo/comparisons', report)
    print(json.dumps({'before': str(paths[0]), 'after': str(paths[1]), 'comparison': str(result), 'state': report['state']}))


if __name__ == '__main__':
    main()
