#!/usr/bin/env python3
"""Experimento D3 v0.2: aritmética/modelos pequeños, sin scheduler ni SQL.

SPDX-License-Identifier: GPL-3.0-only
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
from zoneinfo import ZoneInfo


def available(capacity, commitment=0, consumed=0, pool_fraction='0.7', loan=0):
    if capacity is None:
        return None
    return D(str(capacity)) * D(pool_fraction) + D(loan) - D(commitment) - D(consumed)


def fits(balances, demand):
    return bool(demand) and all(
        a in balances and balances[a] is not None and balances[a] >= n
        for a, n in demand.items()
    )


def select_weighted(weights, n):
    """Demanda unitaria ilimitada; solo hipótesis fair_finish, sin slots/lanes."""
    served = {p: 0 for p in weights}
    result = []
    for _ in range(n):
        p = min((p for p in weights if weights[p] > 0),
                key=lambda p: (F(served[p] + 1, weights[p]), p))
        served[p] += 1
        result.append(p)
    return served, result


def inherit(base, active_edges):
    """Oracle de punto fijo acotado para DAG sintético; no intérprete SemVer."""
    effective = dict(base)
    for _ in range(len(base)):
        changed = False
        for producer, consumer in active_edges:
            new = max(effective[producer], effective[consumer])
            changed |= new != effective[producer]
            effective[producer] = new
        if not changed:
            return effective
    raise ValueError('Fixture no convergente')


def estimate_ready(estimate, limit_confidence, as_of):
    """Oracle de política de datos: sin estimar cuotas ni ejecutar SQL."""
    required = ('vector', 'duration', 'confidence', 'calibration', 'provenance',
                'observed_at', 'valid_until')
    if any(estimate.get(k) is None for k in required):
        return False
    return (limit_confidence is not None and D('.8') <= limit_confidence <= 1
            and D('.8') <= estimate['confidence'] <= 1
            and bool(estimate['vector']) and all(n > 0 for n in estimate['vector'].values())
            and estimate['duration'] > 0 and bool(estimate['calibration'])
            and bool(estimate['provenance'])
            and estimate['observed_at'] <= as_of < estimate['valid_until'])


def incident_pool(severity, role, active_response):
    if role == 'FOLLOW_UP':
        return 'PLANNED'
    if severity in ('SEV1', 'SEV2') or active_response:
        return 'INCIDENT'
    return 'NEEDS_TRIAGE'


def overlaps(left, right):
    return left[0] < right[1] and right[0] < left[1]



def run():
    results = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        results.append({'id': name, 'result': 'PASS'})

    check('split_70_20_10', [available(100, pool_fraction=p) for p in ('.7', '.2', '.1')]
          == [D(70), D(20), D(10)])
    check('unknown_blocks', not fits({'week': None}, {'week': D(1)}))
    b = {'session': D(7), 'week': D(40)}
    original = b.copy()
    check('simultaneous_windows_block_atomically',
          not fits(b, {'session': D(8), 'week': D(8)}) and b == original)
    check('distinct_dimensions_all_bind',
          not fits({'tokens': D(50), 'seconds': D(2)}, {'tokens': D(10), 'seconds': D(3)}))
    check('overspend_preserved', available(100, consumed=72) == -2)
    check('recalibration_deficit_preserved', available(50, commitment=10, consumed=30) == -5)
    check('deficit_blocks_new_admission', not fits({'a': available(50, 10, 30)}, {'a': D(1)}))
    physical = available(100, commitment=20, consumed=10)
    reservation = {'id': 'stable', 'outstanding': 20}
    plans = [{'reservation_id': reservation['id']} for _ in range(10)]
    check('plan_links_no_new_commitment', physical == 40 and len({p['reservation_id'] for p in plans}) == 1)
    tentative = physical - 12
    after_claim = available(100, commitment=32, consumed=10)
    check('tentative_then_claim_charges_once', tentative == after_claim == 28)
    retry_delta = max(20 - 7, 0)
    check('retry_only_top_up', retry_delta == 13 and D(14) - retry_delta == 1)
    # Loan 10, total planned consumption 76: only 4 planned units are free.
    # Of that consumption, 6 belong to the borrower. Nothing restores spent quota.
    planned_free = available(100, consumed=76, loan=10)
    returned = min(D(10), planned_free)
    check('loan_return_bounded_by_free_and_debt', returned == 4 and 10 - returned == 6)
    check('incident_after_return_not_fully_restored', available(100, pool_fraction='.2', loan=-10) + returned == 14)
    check('uncertainty_unchanged', available(100, pool_fraction='.1') == 10)
    counts, sequence = select_weighted({'P0': 8, 'P1': 4, 'P3': 1}, 65)
    check('weighted_unit_hypothesis', counts == {'P0': 40, 'P1': 20, 'P3': 5})
    check('resource_independence', select_weighted({'P0': 8, 'P1': 4, 'P3': 1}, 13)[0]
          == {'P0': 8, 'P1': 4, 'P3': 1})
    check('zero_weight_excluded', select_weighted({'P0': 8, 'P4': 0}, 10)[0]['P4'] == 0)
    base = {'consumer': 8, 'capability': 0, 'producer': 1, 'ancestor': 2, 'sibling': 1}
    edges = [('ancestor', 'producer'), ('producer', 'capability'), ('capability', 'consumer')]
    expected = inherit(base, edges)
    check('blocking_path_only', expected == {'consumer': 8, 'capability': 8, 'producer': 8, 'ancestor': 8, 'sibling': 1}
          and base['producer'] == 1)
    check('unblocked_path_loses_inheritance', inherit(base, []) == base)
    rng = random.Random(20261018)
    stable = True
    for _ in range(100):
        pairs = list({'P0': 8, 'P1': 4, 'P3': 1}.items())
        rng.shuffle(pairs)
        permuted_edges = edges.copy()
        rng.shuffle(permuted_edges)
        stable &= select_weighted(dict(pairs), 65)[1] == sequence
        stable &= inherit(base, permuted_edges) == expected
    check('100_input_permutations', stable)
    # Internal age lane is bounded per physical account, not per publication.
    age_cap = D(70) * D('.05')
    already_charged = D(3)
    check('age_lane_cannot_reset_each_plan', age_cap - already_charged == D('.5'))
    check('large_aged_operation_has_no_guarantee', not fits({'age': age_cap}, {'age': D(4)}))
    check('incompatible_deadlines_do_not_create_capacity', not fits({'planned': D(7)}, {'planned': D(8)}))
    madrid = ZoneInfo('Europe/Madrid')
    start = datetime(2026, 10, 18, 12, tzinfo=madrid)
    end = start + timedelta(days=7)
    hours = (end.astimezone(timezone.utc) - start.astimezone(timezone.utc)).total_seconds() / 3600
    check('civil_week_dst_is_169_hours', hours == 169 and end.hour == start.hour)
    # Casos de política v0.2: oráculos deliberadamente pequeños, sin scheduler.
    now = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)
    estimate = {'vector': {'week': D(10)}, 'duration': D(30), 'confidence': D('.8'),
                'calibration': 'manual-v1', 'provenance': 'MANUAL',
                'observed_at': now - timedelta(minutes=1),
                'valid_until': now + timedelta(hours=1)}
    check('manual_documented_estimate_at_threshold', estimate_ready(estimate, D('.8'), now))
    check('low_limit_confidence_blocks', not estimate_ready(estimate, D('.79'), now))
    check('unknown_limit_confidence_blocks', not estimate_ready(estimate, None, now))
    check('low_estimate_confidence_blocks',
          not estimate_ready(dict(estimate, confidence=D('.79')), D('.9'), now))
    check('missing_calibration_blocks',
          not estimate_ready(dict(estimate, calibration=''), D('.9'), now))
    check('expired_estimate_blocks_at_boundary',
          not estimate_ready(dict(estimate, valid_until=now), D('.9'), now))
    check('future_observation_blocks',
          not estimate_ready(dict(estimate, observed_at=now + timedelta(seconds=1)), D('.9'), now))
    check('nonpositive_duration_blocks',
          not estimate_ready(dict(estimate, duration=D(0)), D('.9'), now))
    check('adjacent_slots_do_not_overlap', not overlaps((0, 30), (30, 60)))
    check('shared_worker_or_exclusive_workspace_conflicts', overlaps((0, 30), (29, 60)))
    # Aplicar el 10% a duración previa 30, no al instante absoluto del reloj.
    tolerance = D(30) * D('.1')
    check('keep_resource_at_three_minute_delay', D(33) - D(30) <= tolerance)
    check('switch_resource_above_three_minute_delay', not D('33.01') - D(30) <= tolerance)
    fresh = lambda age: age is not None and 0 <= age <= 90
    check('heartbeat_90_seconds_inclusive', fresh(90) and not fresh(91) and not fresh(-1) and not fresh(None))
    check('critical_incident_uses_incident_pool', incident_pool('SEV1', 'FIX', False) == 'INCIDENT')
    check('minor_incident_requires_active_triage',
          incident_pool('SEV3', 'FIX', False) == 'NEEDS_TRIAGE'
          and incident_pool('SEV3', 'FIX', True) == 'INCIDENT')
    check('follow_up_always_planned', incident_pool('SEV1', 'FOLLOW_UP', True) == 'PLANNED')
    check('incident_shortfall_does_not_use_planned',
          not fits({'INCIDENT': D(0), 'PLANNED': D(70)}, {'INCIDENT': D(1)}))
    # Reconstruir desde cantidades brutas al reducir la capacidad base.
    raw_service = {'consumed': D(14), 'outstanding': D(7)}
    before = sum(raw_service.values()) / D(70)
    after = sum(raw_service.values()) / D(35)
    check('recalibration_reconstructs_service_without_erasing_facts',
          before == D('.3') and after == D('.6') and raw_service == {'consumed': D(14), 'outstanding': D(7)})
    # Retry: cambia la cuenta dominante; max(delta/base) no es el incremento exacto.
    old_vector, delta_vector = [D(8), D(4)], [D(0), D(5)]
    base_vector = [D(10), D(10)]
    old_service = max(n / b for n, b in zip(old_vector, base_vector))
    projected_service = max((n + d) / b for n, d, b in zip(old_vector, delta_vector, base_vector))
    check('retry_service_uses_projected_increment', projected_service - old_service == D('.1'))
    lane_base, lane_consumed, lane_pending = D(70) * D('.2'), D(8), D(4)
    remaining_before = lane_base - lane_consumed - lane_pending
    remaining_after_settlement = lane_base - (lane_consumed + D(4))
    check('urgent_lane_settlement_does_not_double_charge', remaining_before == remaining_after_settlement == 2)
    check('urgent_lane_overspend_is_preserved', lane_base - D(15) == -1)
    return results


if __name__ == '__main__':
    cases = run()
    root = Path(__file__).resolve().parents[2]
    inputs = ['testing/D3/validate_design.py', 'docs/design/D3-capacity-scheduler-draft.md',
              'docs/design/D3-DECISIONS.md']
    report = {
        'recorded_date': '2026-10-18', 'timezone': 'Europe/Madrid',
        'stage': 'D3 v0.2 design experiment; design and implementation start approved; D3 closure pending', 'baseline_D2_commit': '69d71c3',
        'result': 'PASS', 'checks': len(cases), 'failures': 0, 'cases': cases,
        'input_sha256': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in inputs},
        'limitations': [
            'Arithmetic and small independent models only; not a complete scheduler.',
            'No PostgreSQL, publication concurrency, CLAIM, workers or provider integration executed.',
            'Only small interval and estimate-policy oracles; no complete scheduler, historical fairness proof or performance benchmark.',
            'Does not rerun or extend the recorded D2 audit; parameter approvals are scoped in D3-DECISIONS.md; D3 closure remains unapproved.'
        ]
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
