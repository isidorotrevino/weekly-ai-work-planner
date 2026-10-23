# SPDX-License-Identifier: GPL-3.0-only
"""Atomic fixture batch, partial TASK projections and explicit process reconciliation."""
import json
from testing.D5.relational_support import new_lab,prepare,start,receive,finish


def child(lab,action,args):
    p,c=start(lab,action,args)
    try:
        status,value=receive(p,c)
        if status!='OK':raise RuntimeError('FIXTURE_CHILD_FAILED')
        return value
    finally:
        if finish(p,c)!=0:raise RuntimeError('FIXTURE_CHILD_EXIT')


def main():
    with new_lab() as lab:
        ids=prepare(lab)
        lab.client.dispatch(ids['projections'][0],1)
        lost=lab.client.dispatch(ids['projections'][1],1,deliver=False)
        partial=lab.client.summary()
        m=lab.client.snapshot()['state']['manifests'][ids['projections'][1]]
        child(lab,'remote',dict(ticket=lost['ticket'],m=m))
        before=child(lab,'snapshot',{})
        child(lab,'reconcile',dict(sid=lost['send_id']))
        after=lab.fresh().summary()
        output=dict(schema='d5.i36-relational-demo.v1',batch_applied=True,
             partial_statuses=[{x['target_id']:x['status'] for x in partial['sends']}[tid] for tid in ids['task_ids']],client_before_reconcile=[{x['target_id']:x['status'] for x in before['sends']}[tid] for tid in ids['task_ids']],
             reconciled_statuses=[{x['target_id']:x['status'] for x in after['sends']}[tid] for tid in ids['task_ids']],remote_fixture_TASKs=len(lab.remote.snapshot()['state']['entities']),
             distributed_atomicity_claimed=False,**{k:v for k,v in after.items() if k not in ('schema','sends')})
    output['own_cleanup_verified']=lab.closed
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=='__main__':main()
