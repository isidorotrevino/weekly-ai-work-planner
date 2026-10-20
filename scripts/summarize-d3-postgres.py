#!/usr/bin/env python3
"""Export current D3/D2 test counts and hashes without private logs or properties.

SPDX-License-Identifier: GPL-3.0-only
"""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
marker = ROOT / 'work/d3-postgres/latest-success.txt'
if not marker.exists():
    raise SystemExit('Run testing/D3/run-postgres-tests.sh successfully first.')
run_id = marker.read_text().strip()
if not re.fullmatch(r'd3-i2-[0-9]+-[0-9]+', run_id):
    raise SystemExit('Invalid local audit marker.')
audit_dir = marker.parent / run_id
all_reports = []
groups = {}
environment = {}
for group, directory, pattern in [('core', 'scheduler-core', 'TEST-*.xml'), ('scale_review', 'scheduler-core', 'TEST-*ScaleReviewTest.xml'), ('optimization_parity', 'scheduler-core', 'TEST-*OptimizationParityTest.xml'), ('postgres_I2', 'scheduler-postgres', 'TEST-*PlanningStoreTest.xml'), ('dispatch_I3', 'scheduler-postgres', 'TEST-*DispatchStoreTest.xml'), ('coordinator', 'scheduler-postgres', 'TEST-*CoordinatorTest.xml'), ('acceptance_V15', 'scheduler-postgres', 'TEST-*AcceptanceTest.xml'), ('D2_regression', 'testing/D2', 'TEST-*.xml')]:
    reports = sorted((ROOT / directory / 'target/surefire-reports').glob(pattern))
    if group == 'core':
        reports = [p for p in reports if 'ScaleReviewTest' not in p.name and 'OptimizationParityTest' not in p.name]
    if not reports:
        raise SystemExit(f'Missing current reports: {group}')
    all_reports.extend(reports)
    counts = dict(tests=0, failures=0, errors=0, skipped=0)
    classes = {}
    for path in reports:
        suite = ET.parse(path).getroot()
        classes[suite.attrib['name']] = {key: int(suite.get(key, '0')) for key in counts}
        for key, number in classes[suite.attrib['name']].items():
            counts[key] += number
        props = {p.get('name'): p.get('value') for p in suite.findall('./properties/property')}
        environment.update({key: props[key] for key in ('java.version', 'java.vendor') if key in props})
    if counts['tests'] == 0 or any(counts[key] for key in ('failures', 'errors', 'skipped')):
        raise SystemExit(f'Test group did not pass completely: {group} {counts}')
    groups[group] = dict(totals=counts, classes=classes)
inputs = sorted(set(
    [ROOT / 'pom.xml', ROOT / 'scheduler-core/pom.xml', ROOT / 'scheduler-postgres/pom.xml', ROOT / 'testing/D3/run-postgres-tests.sh']
    + list((ROOT / 'scheduler-core/src').rglob('*.java'))
    + list((ROOT / 'scheduler-postgres/src').rglob('*.java'))
    + list((ROOT / 'migrations-d3-proposed').glob('*.sql'))
    + list((ROOT / 'migrations-d3-dispatch-proposed').glob('*.sql'))
    + list((ROOT / 'migrations-d3-coordinator-proposed').glob('*.sql'))
    + list((ROOT / 'migrations-d3-review-proposed').glob('*.sql'))
))
if max(p.stat().st_mtime_ns for p in inputs) > min(p.stat().st_mtime_ns for p in all_reports):
    raise SystemExit('Executable inputs changed after these reports; rerun the audit.')
if max(p.stat().st_mtime_ns for p in all_reports) > marker.stat().st_mtime_ns:
    raise SystemExit('Reports are newer than the last complete successful audit; rerun it.')
legacy = json.loads((ROOT / 'docs/validation/semver-evidence.json').read_text())
if not all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in legacy['input_sha256'].items()):
    raise SystemExit('Historical D2 inputs changed; review explicitly before reporting unchanged regression.')
changed_core = 'scheduler-core/src/main/java/io/github/isidorotrevino/planner/scheduler/CapacityScheduler.java'
baseline_file = ROOT / 'scheduler-core/src/test/resources/d3-baseline/CapacityScheduler.java'
baseline_sha = hashlib.sha256(baseline_file.read_bytes()).hexdigest()
historical_comparison = {}
for label, filename in [('I1','D3-I1-results.json'),('I2','D3-I2-results.json'),('I3','D3-I3-results.json'),('coordinator','D3-COORDINATOR-results.json'),('review','D3-REVIEW-results.json')]:
    historical = json.loads((ROOT / 'docs/validation' / filename).read_text())
    differences = [name for name, digest in historical['input_sha256'].items() if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    if differences != [changed_core] or historical['input_sha256'][changed_core] != baseline_sha:
        raise SystemExit(f'Unreviewed changes beyond authorized core optimization or invalid baseline: {label} {differences}')
    historical_comparison[label] = dict(authorized_changes=differences, all_other_recorded_inputs_unchanged=True, original_core_sha256=baseline_sha)
before_review = json.loads((ROOT / 'docs/validation/D3-REVIEW-results.json').read_text())
scale_file = ROOT / 'scheduler-core/target/d3-scale-review.json'
if scale_file.stat().st_mtime_ns < max(p.stat().st_mtime_ns for p in inputs) or scale_file.stat().st_mtime_ns > marker.stat().st_mtime_ns:
    raise SystemExit('Scale measurements are stale or outside the successful audit.')
scale_measurements = json.loads(scale_file.read_text())
environment['postgresql'] = (audit_dir / 'postgresql-version.txt').read_text().strip()
environment['execution'] = 'Disposable Docker PostgreSQL 16 + Maven/Java 21; no published host ports'
# Approval is independent of test execution: report closure only for the exact
# executable snapshot approved by the human, never merely because tests pass.
current_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
closure_path = ROOT / 'docs/validation/D3-CLOSURE.json'
closure = json.loads(closure_path.read_text()) if closure_path.exists() else {}
approved_snapshot = closure.get('status') == 'APPROVED_CLOSED' and closure.get('verified_executable_input_sha256') == current_hashes
report = dict(
    recorded_date=datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat(), timezone='Europe/Madrid',
    stage='D3 conservative MVP 1.0 approved and closed' if approved_snapshot else 'D3 optimization snapshot; explicit closure not attested for these inputs', result='PASS_SAFETY_CHECKS',
    baseline_D2_commit='69d71c3877e79bdfef088956b090d4eb6b447be9',
    environment=environment, test_groups=groups,
    input_sha256=current_hashes,
    closure_attestation=dict(approved_snapshot=approved_snapshot, manifest='docs/validation/D3-CLOSURE.json' if approved_snapshot else None),
    D2_historical_inputs_unchanged=True, historical_input_comparison=historical_comparison,
    semver=dict(vectors=29829, included_within='D2 regression JUnit; not additional JUnit tests'),
    migrations=dict(D2='V1-V11, unchanged', D3='V12-V15 isolated proposals, not promoted; V15 replaces only D3 event classification and appends pending-reopening correction events'),
    scale_measurements=scale_measurements,
    scale_measurements_sha256=hashlib.sha256(scale_file.read_bytes()).hexdigest(),
    prior_scale_measurements=before_review['scale_measurements'],
    forecast_scope='1A accepted: currently eligible work only, lower-bound risk, no CONDITIONAL or full critical calendar',
    review_gate='CLOSED by explicit user approval for this executable snapshot; no deployment/promotion approval' if approved_snapshot else 'Closure approval not attested for these executable inputs',
    summary_generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    scope='Behavior-preserving core optimization, differential full-result comparisons against the exact saved baseline and the same bounded scale measurements; all PostgreSQL and D2 regression groups rerun.',
    limitations=[
        'D3 SQL/JDBC dispatch/lifecycle entrypoints exercised synthetically; no running service, real worker or provider executed.',
        'Publication validates safety and freshness, not a second implementation of greedy optimization.',
        'Eligibility is sampled on event receipt, scheduled sweep and preparation when explicit ticks run; no background daemon is running.',
        'Runtime role is NOLOGIN and test-only; production logins/scopes remain D6 work.',
        'The coordinator is callable SQL/JDBC only; hosting, checkpoint execution and HTTP worker authentication are not implemented.',
        'Blocked HARD consumers have no CONDITIONAL forecast slots; deadline propagation remains a lower bound, not a full critical calendar.',
        'Scale tests permit safe LIMIT_EXCEEDED aborts; inspect per-fixture status and tentative counts for completion.',
        'Before/after observations are separate audit runs with uncontrolled JIT/host effects, not a statistical speedup claim.',
        'Single measured execution per fixture; no throughput SLA, deployment approval or D3 closure is implied.'
    ],
    reproduce='bash testing/D3/run-postgres-tests.sh',
    raw_evidence='Local ignored work/d3-postgres/ and module target/surefire-reports/ directories'
)
print(json.dumps(report, indent=2, ensure_ascii=False))
