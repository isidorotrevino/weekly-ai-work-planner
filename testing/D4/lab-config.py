#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Generate only disposable synthetic identities. Secrets stay under ignored work/."""
import hashlib,json,os,secrets,subprocess,sys,uuid
from pathlib import Path

def prepare(case,scenario,campaign):
    case=Path(case);case.mkdir(mode=0o700,parents=True);os.chmod(case,0o700)
    private=case/'private';private.mkdir(mode=0o700)
    public=case/'public';public.mkdir();(case/'observations').mkdir()
    def run(*args):
        result=subprocess.run(['openssl',*map(str,args)],capture_output=True)
        if result.returncode: raise RuntimeError('Synthetic PKI generation failed: '+result.stderr.decode()[-300:])
        return result.stdout
    ca=private/'ca.key'
    run('req','-x509','-newkey','rsa:2048','-nodes','-keyout',ca,'-out',public/'ca.crt','-days','2','-subj','/CN=D4 ephemeral synthetic CA','-addext','basicConstraints=critical,CA:TRUE','-addext','keyUsage=critical,keyCertSign,cRLSign')
    for name in ['control','observer','receiver']:
        key=private/(name+'.der');run('genpkey','-algorithm','ED25519','-outform','DER','-out',key)
        run('pkey','-inform','DER','-in',key,'-pubout','-outform','DER','-out',public/(name+'.pub.der'))
    ids={name:str(uuid.uuid4()) for name in ['control','receiver','worker-a','worker-b','verifier','driver']}
    participants=dict(ids,scenario=scenario,campaign=campaign);(public/'participants.json').write_text(json.dumps(participants))
    passwords={name:secrets.token_hex(24) for name in ['owner','control','verifier','auditor']}
    (case/'postgres.env').write_text('POSTGRES_USER=d4_owner\nPOSTGRES_PASSWORD='+passwords['owner']+'\nPOSTGRES_HOST_AUTH_METHOD=scram-sha-256\n')
    registry=[]
    for name in ids:
        folder=case/'config'/name;folder.mkdir(parents=True)
        kind='worker' if name.startswith('worker') else 'control' if name=='receiver' else name
        uri='urn:weekly-ai-planner:worker:'+ids[name] if kind=='worker' else 'urn:weekly-ai-planner:principal:'+kind+':'+ids[name]
        key=private/(name+'.key');csr=private/(name+'.csr');cert=private/(name+'.crt');ext=private/(name+'.ext')
        run('req','-newkey','rsa:2048','-nodes','-keyout',key,'-out',csr,'-subj','/CN=D4-'+name)
        dns='control-plane' if name=='control' else 'effect-receiver' if name=='receiver' else name
        ext.write_text('basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth,clientAuth\nsubjectAltName=DNS:'+dns+',DNS:localhost,URI:'+uri+'\n')
        run('x509','-req','-in',csr,'-CA',public/'ca.crt','-CAkey',ca,'-set_serial',str(uuid.uuid4().int),'-days','2','-extfile',ext,'-out',cert)
        tls=secrets.token_hex(24);pw=private/(name+'.password');pw.write_text(tls)
        run('pkcs12','-export','-inkey',key,'-in',cert,'-certfile',public/'ca.crt','-out',folder/'identity.p12','-passout','file:'+str(pw))
        fingerprint=hashlib.sha256(run('x509','-in',cert,'-outform','DER')).hexdigest();registry.append(fingerprint+'='+kind+':'+ids[name])
        props={'role':kind if name!='receiver' else 'receiver','tls.password':tls,'campaign':campaign}
        if kind=='worker':props['worker.id']=ids[name]
        if name in ['control','verifier','driver']:
            role='auditor' if name=='driver' else name
            props.update({'jdbc.url':'jdbc:postgresql://db:5432/postgres','jdbc.user':'lab_'+role,'jdbc.password':passwords[role]})
        if name=='verifier':props['worker.a']=ids['worker-a']
        (folder/'service.properties').write_text(''.join(k+'='+v+'\n' for k,v in props.items()))
    for name in ids:(case/'config'/name/'identities.properties').write_text('\n'.join(registry)+'\n')
    import shutil
    shutil.copyfile(private/'control.der',case/'config/control/signing.der')
    shutil.copyfile(private/'receiver.der',case/'config/receiver/sealing.der')
    bootstrap=case/'config/bootstrap';bootstrap.mkdir()
    props={'role':'bootstrap','jdbc.url':'jdbc:postgresql://db:5432/postgres','jdbc.user':'d4_owner','jdbc.password':passwords['owner']}
    props.update({name+'.password':passwords[name] for name in ['control','verifier','auditor']})
    (bootstrap/'service.properties').write_text(''.join(k+'='+v+'\n' for k,v in props.items()))
    # Newly created named volumes are owned by root. Bootstrap runs as root solely
    # to initialize and chown its four isolated writable destinations.
    os.chmod(public,0o770)
    for f in public.iterdir():os.chmod(f,0o640)
    for folder in (case/'config').rglob('*'):
        os.chmod(folder,0o750 if folder.is_dir() else 0o640)
    for f in private.iterdir():os.chmod(f,0o600)
    return participants
if __name__=='__main__':prepare(*sys.argv[1:])
