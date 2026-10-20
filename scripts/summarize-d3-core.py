#!/usr/bin/env python3
"""Portable summary of current JUnit results; no raw properties, paths or logs exported.

SPDX-License-Identifier: GPL-3.0-only
"""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
report_dir = ROOT / 'scheduler-core/target/surefire-reports'
reports = sorted(report_dir.glob('TEST-*.xml'))
if not reports:
    raise SystemExit('No current JUnit reports. Run testing/D3/run-core-tests.sh first.')
counts = dict(tests=0, failures=0, errors=0, skipped=0)
suites = {}
environment = {}
for report in reports:
    suite = ET.parse(report).getroot()
    numbers = {key: int(suite.get(key, '0')) for key in counts}
    suites[suite.attrib['name']] = numbers
    for key, value in numbers.items():
        counts[key] += value
    props = {item.get('name'): item.get('value') for item in suite.findall('./properties/property')}
    environment = {key: props.get(key) for key in ('java.version', 'java.vendor')}
inputs = sorted(set(
    [ROOT / 'scheduler-core/pom.xml', Path(__file__).resolve()]
    + list((ROOT / 'scheduler-core/src').rglob('*.java'))
    + list((ROOT / 'testing/D3').glob('run-core*.sh'))
))
# Refuse to attest stale reports after editing executable inputs.
if max(p.stat().st_mtime_ns for p in inputs) > min(p.stat().st_mtime_ns for p in reports):
    raise SystemExit('Executable inputs changed after these reports. Rerun core tests before summarizing.')
summary = {
    'recorded_date': datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat(),
    'timezone': 'Europe/Madrid',
    'stage': 'D3 I1 initial Java implementation; D3 open; I2/I3 pending',
    'baseline_D2_commit': '69d71c3877e79bdfef088956b090d4eb6b447be9',
    'result': 'PASS' if counts['tests'] > 0 and not any(counts[k] for k in ('failures', 'errors', 'skipped')) else 'REVIEW_REQUIRED',
    'environment': environment, 'tests': counts, 'test_classes': suites,
    'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
    'scope': 'Pure Java planning and event-policy tests with synthetic snapshots. No SQL, provider calls or workers.',
    'limitations': [
        'No transactional publication/CLAIM, runtime service, deployment or real quota validation.',
        'D2 eligibility, evidence and compatibility enter as trusted snapshot diagnostics; adapter parity is pending.',
        'Fairness projections are local to a run; persistence/epochs/outbox acknowledgements remain I2 work.',
        'Only currently eligible work is assigned; HARD-dependent future work stays blocked, with no executable forecast.',
        'Downstream duration projection is a lower bound and does not prove deadline feasibility under contention.',
        'No performance SLA or D3 closure inferred from passing unit tests.'
    ],
    'reproduce': 'bash testing/D3/run-core-tests.sh',
    'raw_evidence': 'Generated under ignored scheduler-core/target/surefire-reports/'
}
print(json.dumps(summary, indent=2, ensure_ascii=False))
