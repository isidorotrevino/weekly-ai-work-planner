# SPDX-License-Identifier: GPL-3.0-only
"""Synthetic durable intent, independent remote effect and explicit reconciliation."""
import json
from testing.D5.durable_support import new_lab,ready,start,receive,finish


def child(lab,action,args):
    process,connection=start(lab,action,args)
    try:
        status,value=receive(process,connection)
        if status!='OK':raise RuntimeError('FIXTURE_CHILD_FAILED')
        return value
    finally:
        if finish(process,connection)!=0:raise RuntimeError('FIXTURE_CHILD_EXIT')


def main():
    with new_lab() as lab:
        ids=ready(lab);sent=lab.client.dispatch(ids['projection'],1,deliver=False)
        manifest=lab.client.snapshot()['state']['manifests'][ids['projection']]
        # Separate process confirms remote state; no result is written to CLIENT yet.
        child(lab,'remote',dict(ticket=sent['ticket'],m=manifest))
        initial=child(lab,'snapshot',{})['sends'][0]['status']
        child(lab,'reconcile',dict(sid=sent['send_id']))
        current=lab.fresh().summary()
        lab.client.review('PROJECTION',ids['projection'],'REVOKE',1)
        historical=lab.fresh().summary()['sends'][0]
        output=dict(schema='d5.i34-durable-demo.v1',initial_client_status=initial,
                    reconciled_status=current['sends'][0]['status'],after_revocation=historical,
                    remote_fixture_effects=len(lab.remote.snapshot()['state']['entities']),
                    **{k:v for k,v in current.items() if k not in ('schema','sends')})
    output['own_cleanup_verified']=lab.closed
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=='__main__':main()
