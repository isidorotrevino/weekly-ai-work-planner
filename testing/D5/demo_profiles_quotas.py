# SPDX-License-Identifier: GPL-3.0-only
"""Memory-only quota review, expiry and explicitly historical replay."""
import json
from source_ingest.eligibility_fixture import (EligibilityLab,account,adapter,constraint,
    descriptor,observation,policy)


def fixture_id(n):
    return f'00000000-0000-4000-8000-{n:012d}'


def main():
    lab=EligibilityLab(); project,document=fixture_id(1),fixture_id(2)
    desc=lab.register_profile(descriptor()); lab.select_profile(project,document,desc,expected_generation=0)
    content=(b'| ID | Item | Component(s) | Objective | Blocked on | Status | Verified | Source |\n'
             b'|---|---|---|---|---|---|---|---|\n'
             b'| FIX-1 | Synthetic item | fixture | Review only | - | CLOSED | claim | inert |\n')
    cap=lab.capture(content,project,document,'fixture-1')
    lab.review('SOURCE',cap,expected_version=0,decision='ACCEPT',reason='Synthetic source')
    binding=account(fixture_id(3),fixture_id(4),fixture_id(5),project)
    card=adapter(fixture_id(6)); bid=lab.bind_account(binding,card)
    rows=[constraint(cost=2),constraint('TOKENS','TOKEN','short',5)]
    lab.select_policy(project,policy(fixture_id(7),rows,horizon=5),expected_generation=0)
    gen=1
    for i,row in enumerate(rows):
        oid=fixture_id(20+i)
        gen=lab.publish_observation(bid,observation(oid,binding,card,row),expected_generation=gen)
        gen=lab.select_observation(bid,oid,expected_generation=gen)
    lab.advance_clock(10)
    mid=lab.prepare_evaluation(cap,bid,source_review_version=1)
    lab.review('EVALUATION',mid,expected_version=0,decision='ACCEPT',reason='Synthetic vector')
    cid=fixture_id(30); first=lab.validate_evaluation(cid,mid,evaluation_review_version=1)
    lab.advance_clock(100)
    old=lab.validate_evaluation(cid,mid,evaluation_review_version=1)
    current=lab.validate_evaluation(fixture_id(31),mid,evaluation_review_version=1)
    print(json.dumps(dict(schema='d5.eligibility-fixture-demo.v1',initial_result=first['result'],
        historical_result=old['result'],historical=old['historical'],new_command_result=current['result'],
        **lab.summary()),indent=2,sort_keys=True))


if __name__=='__main__':
    main()
