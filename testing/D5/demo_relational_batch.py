# SPDX-License-Identifier: GPL-3.0-only
"""One synthetic atomic batch and lost-response recovery; no source text output."""
import json

from source_ingest.batch_fixture import (BatchError,BatchLab,element,envelope,reference,declaration)


def fixture_id(n):
    return f'00000000-0000-4000-8000-{n:012d}'


def main():
    project,document=fixture_id(1),fixture_id(2)
    lab=BatchLab(project)
    rows=[element('R','REQUIREMENT','Synthetic requirement','Scope'),
          element('E','EPIC','Synthetic epic','Evidence only'),
          element('T','TASK','Synthetic task','Objective')]
    r=lambda key,kind: reference(project,document,key,kind)
    relations=[declaration('ER','EPIC_REQUIREMENT',r('E','EPIC'),r('R','REQUIREMENT')),
               declaration('TE','TASK_EPIC',r('T','TASK'),r('E','EPIC'))]
    sid=lab.capture(envelope(project,document,'fixture-1',rows,relations))
    lab.review('SOURCE',sid,expected_version=0,decision='ACCEPT',reason='Synthetic source review')
    choices=[dict(source_key=key,target_id=fixture_id(10+i),target_key='FIX-'+key)
             for i,key in enumerate(['R','E','T'])]
    mid=lab.prepare(sid,choices,source_review_version=1)
    lab.review('BATCH',mid,expected_version=0,decision='ACCEPT',reason='Synthetic whole-batch review')
    def lost(stage):
        if stage=='after_publish': raise BatchError('RESPONSE_LOST')
    lab.test_hook=lost
    cid=fixture_id(20)
    try:
        lab.apply(cid,mid,batch_review_version=1,data_generation=0)
    except BatchError as exc:
        if str(exc)!='RESPONSE_LOST': raise
    receipt=lab.apply(cid,mid,batch_review_version=1,data_generation=0)
    print(json.dumps(dict(schema='d5.batch-fixture-demo.v1',lost_response_recovered=True,
        historical_receipt_replayed=True,result=receipt['result'],
        created=receipt['created'],participants=receipt['participants'],
        **lab.summary()),indent=2,sort_keys=True))


if __name__=='__main__':
    main()
