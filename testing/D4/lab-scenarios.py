#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Host orchestrator. Docker authority remains outside every lab container."""
import argparse,base64,concurrent.futures,datetime,hashlib,importlib.util,json,os,subprocess,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MAIN=['java','-Xmx80m','-cp','/app/classes:/app/lib/*','io.github.isidorotrevino.planner.lab.LabMain']
PG='postgres@sha256:0ea6700a3b4f0ae6ce746519073558aed4d88a79d8d07622a9a644946c7319c4'
spec=importlib.util.spec_from_file_location('lab_config',ROOT/'testing/D4/lab-config.py');config=importlib.util.module_from_spec(spec);spec.loader.exec_module(config)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def parse(t):return datetime.datetime.fromisoformat(t.replace('Z','+00:00'))
class Case:
 def __init__(self,run,scenario,image):
  self.run=run;self.scenario=scenario;self.path=run/scenario;self.campaign=str(uuid.uuid4());self.project=('d4lab-'+self.campaign[:12]+'-'+scenario).lower();self.checks=[];self.started=time.monotonic()
  self.participants=config.prepare(self.path,scenario,self.campaign)
  self.env=os.environ|{'LAB_IMAGE':image,'PG_IMAGE':PG,'LAB_UID':str(os.getuid()),'LAB_GID':str(os.getgid()),'LAB_CASE_DIR':str(self.path)}
  self.base=['docker','compose','-f',str(ROOT/'testing/D4/compose.yaml'),'-p',self.project]
 def cmd(self,args,timeout=60,check=True):
  r=subprocess.run(args,env=self.env,capture_output=True,text=True,timeout=timeout)
  if check and r.returncode:raise RuntimeError('Command failed '+str(args[:6])+': '+r.stderr[-1200:]+r.stdout[-1200:])
  return r
 def compose(self,*args,**kwargs):return self.cmd(self.base+list(args),**kwargs)
 def cli(self,service,*args):return self.compose('exec','-T',service,*MAIN,*args).stdout.strip()
 def jsoncli(self,service,*args):return json.loads(self.cli(service,*args))
 def api(self,service,path,body=None,caller='driver',expected=200):
  args=['request','https://'+service+':8443'+path]
  if body is not None:args.append(json.dumps(body,separators=(',',':')))
  value=self.jsoncli(caller,*args)
  if value['status']!=expected:raise AssertionError((service,path,'expected',expected,'actual',value))
  return value.get('body')
 def check(self,name,condition,detail=None):
  if not condition:raise AssertionError(name+': '+str(detail))
  self.checks.append(name)
 def audit(self):return self.jsoncli('driver','audit')
 def inspect(self,delivery):return self.jsoncli('driver','inspect',delivery)
 def state(self,worker='worker-a'):return self.api(worker,'/lab/state')
 def phase(self,phases,worker='worker-a',timeout=30):
  deadline=time.monotonic()+timeout
  while time.monotonic()<deadline:
   s=self.state(worker)
   if s['phase'] in phases:return s
   if s['phase'] in ['BLOCKED_UNKNOWN','NO_ASSIGNMENT']:raise AssertionError('Worker did not progress: '+json.dumps(s))
   time.sleep(.4)
  raise TimeoutError('Worker phase '+str(s))
 def cid(self,service):return self.compose('ps','-q',service).stdout.strip()
 def observation(self,state,worker='worker-a'):
  identity=state['identity'];attempt=identity['attempt'];raw=self.compose('exec','-T',worker,'cat','/state/supervisor/attempts/'+attempt+'/0002-RUNNING.properties').stdout
  props=dict(line.split('=',1) for line in raw.splitlines() if '=' in line and not line.startswith('#'))
  facts=self.jsoncli(worker,'probe',props['pid'],props['group'],props['ticks'],props['boot'])
  facts.update(identity,campaign=self.campaign,observed_at=now(),container_id=self.cid(worker))
  text=json.dumps(facts,sort_keys=True,separators=(',',':'));data=self.path/'private'/'observation.bytes';data.write_text(text)
  signed=subprocess.run(['openssl','pkeyutl','-sign','-rawin','-keyform','DER','-inkey',str(self.path/'private/observer.der'),'-in',str(data)],capture_output=True,check=True).stdout
  (self.path/'observations'/(attempt+'.json')).write_text(json.dumps({'facts':text,'signature':base64.b64encode(signed).decode()}))
  return facts
 def verify(self,state,worker='worker-a'):
  self.observation(state,worker)
  return self.api('verifier','/lab/verify',{'delivery_id':state['delivery_id'],'proof_id':str(uuid.uuid4())})
 def query(self,state):
  g=state['authorization']['grant'];return self.api('effect-receiver','/lab/query',{'operation':g['operation'],'intent_hash':g['intent_hash'],'step':'step-1','generation':g['generation']})
 def wait_expired(self,delivery):
  deadline=time.monotonic()+90
  while True:
   if time.monotonic()>deadline:raise TimeoutError("Execution lease did not expire within bounded observation")
   info=self.inspect(delivery)
   if info['lease_expired']:break
   remaining=(parse(info['lease_expires_at'])-parse(info['database_now'])).total_seconds()
   print(self.scenario+': esperando lease D2 real ('+str(round(remaining))+' s)',flush=True)
   time.sleep(min(15,max(.2,remaining+.1)))
  self.check('real_postgresql_lease_expiry',info['lease_expired'])
 def start(self):
  print(self.scenario+': arranque de Compose aislado',flush=True)
  r=self.compose('up','-d','--wait','--wait-timeout','160',timeout=180,check=False)
  (self.path/'startup.log').write_text(r.stdout+r.stderr)
  if r.returncode:raise RuntimeError('Compose startup failed; see '+str(self.path/'startup.log'))
  self.fixture=json.loads((self.path/'public/fixture.json').read_text())
  versions={'java':self.compose('exec','-T','driver','java','-version').stderr.strip(),'postgresql':self.compose('exec','-T','db','psql','-X','-U','d4_owner','-d','postgres','-At','-c','SHOW server_version').stdout.strip()}
  (self.path/'versions.json').write_text(json.dumps(versions,indent=2))
  self.check('auditor_minimal_sql_role',self.jsoncli('driver','rolecheck')['denied']==['42501']*5)
  self.check('control_plane_cannot_mint_evidence',self.jsoncli('control-plane','rolecheck')['denied']==['42501']*5)
  for worker in ['worker-a','worker-b']:
   self.check(worker+'_cannot_reach_database',not self.jsoncli(worker,'network-probe','db','5432')['reachable'])
   self.check(worker+'_cannot_reach_internet',not self.jsoncli(worker,'network-probe','1.1.1.1','443')['reachable'])
  rows=json.loads(self.cmd(['docker','inspect',*[self.cid(s) for s in ['control-plane','worker-a','worker-b','effect-receiver','verifier','driver']]]).stdout)
  safe=[]
  for row in rows:
   h=row['HostConfig'];mounts=row['Mounts']
   self.check(row['Name']+'_isolated',not h['Privileged'] and h['ReadonlyRootfs'] and 'ALL' in h['CapDrop'] and not h['PortBindings'] and not any('docker.sock' in m['Source'] for m in mounts))
   safe.append({k:row[k] for k in ['Id','Name','Image','Mounts','NetworkSettings']})
  (self.path/'isolation.json').write_text(json.dumps(safe,indent=2))
  self.api('control-plane','/lab/admin',{'action':'VERIFY','delivery_id':str(uuid.uuid4()),'command_id':str(uuid.uuid4())},expected=403)
  self.check('driver_cannot_self_verify',True)
 def ledger(self,audit,account,outstanding,consumed):
  rows={r['pool']:r for r in audit['balances'] if r['account_id']==account}
  self.check('physical_account_three_pools_'+account,set(rows)=={'PLANNED','INCIDENT','UNCERTAINTY'})
  for pool,limit in [('PLANNED',70),('INCIDENT',20),('UNCERTAINTY',10)]:
   row=rows[pool];o=outstanding if pool=='PLANNED' else 0;c=consumed if pool=='PLANNED' else 0
   self.check('accounting_'+account+'_'+pool,float(row['effective_limit'])==limit and float(row['outstanding'])==o and float(row['consumed'])==c and float(row['available'])==limit-o-c,row)
 def complete(self,state,worker='worker-a'):
  result=self.verify(state,worker);self.check('independent_verifier_completed_'+worker,result['accepted'] and result['stopped'] and result['state']['state']=='COMPLETED',result)
  self.check('receiver_durable_applied_'+worker,self.query(state)['status']=='APPLIED')
  return result
 def scenario1(self):
  self.api('worker-a','/lab/run',{});s=self.phase(['CALLBACK_CONFIRMED']);self.complete(s)
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,8);self.ledger(a,self.fixture['account_b'],0,0)
  self.check('single_attempt_reservation_effect',len(a['attempts'])==len(a['reservations'])==len(a['effects'])==1,a)
  cid=s['callback_command_id'];entries=[{'account_id':x['account_id'],'settled':x['units'],'consumed':s['info']['consumed_units']} for x in s['info']['accounts']]
  envelope={'schema_version':'d4.worker.v1','command_id':cid,'correlation_id':cid,'request':{'action':'CALLBACK','delivery_id':s['delivery_id'],'payload':{'entries':entries}}}
  original=self.api('control-plane','/d4/v1/commands/'+cid,caller='worker-a')
  replay=self.api('control-plane','/d4/v1/commands',envelope,caller='worker-a');self.check('callback_replay_returns_original_receipt',original==replay)
  envelope['correlation_id']=str(uuid.uuid4());self.api('control-plane','/d4/v1/commands',envelope,caller='worker-a',expected=409);self.check('command_changed_content_denied',True)
  self.api('worker-a','/lab/late-effect',{},expected=409);self.check('closed_receiver_rejects_previous_authority',True)
  self.api('worker-a','/lab/raw',{'action':'VERIFY','delivery_id':s['delivery_id']},expected=409)
  self.check('worker_cannot_self_verify',True)
 def scenario2(self):
  # Two independent driver calls cause two actual mTLS POLLs by the same worker.
  with concurrent.futures.ThreadPoolExecutor(2) as pool:
   values=list(pool.map(lambda _:self.api('worker-a','/lab/raw',{'action':'POLL'}),range(2)))
  assignments=[v['assignment'] for v in values];self.check('concurrent_poll_same_delivery',assignments[0]['delivery_id']==assignments[1]['delivery_id'],values)
  delivery=assignments[0]['delivery_id']
  for action in ['ACK','START']:
   self.api('worker-b','/lab/raw',{'action':action,'delivery_id':delivery},expected=403)
  self.check('foreign_worker_ack_start_denied',True)
  self.api('worker-a','/lab/run',{});s=self.phase(['PROCESS_RUNNING'])
  before=self.audit();reservation=next(r['id'] for r in before['reservations'] if r['operation_id']==self.fixture['operation_a'])
  self.api('control-plane','/lab/replan',{})
  after=self.audit();self.check('replan_successor_published',after['head']!=self.fixture['initial_plan'],after['head'])
  self.check('stable_reservation_between_plans',len([r for r in after['reservations'] if r['operation_id']==self.fixture['operation_a']])==1 and any(r['id']==reservation for r in after['reservations']))
  scheduled={r['operation_id'] for r in after['schedule']}
  current=next(m['result'] for m in after['manifests'] if m['plan']==after['head']);decisions={d['operationId']:d for d in current['decisions']}
  self.check('active_commitment_carried_in_successor',decisions[self.fixture['operation_a']]['disposition']=='CARRIED')
  self.check('shared_workspace_deferred_in_successor',decisions[self.fixture['shared_waiter']]['disposition']=='DEFERRED')
  self.check('blocking_path_p4_inherits_only_blocker',any(r['operation_id']==self.fixture['operation_a'] and r['priority_snapshot']['baseWeight']==0 and r['priority_snapshot']['effectiveWeight']==8 and r['priority_snapshot']['inheritedPath'] for r in after['schedule']))
  self.check('blocking_path_p4_admitted',self.fixture['operation_a'] in scheduled)
  self.check('hard_consumer_without_evidence_excluded',self.fixture['hard_consumer'] not in scheduled)
  self.check('unrelated_p4_excluded',self.fixture['unrelated_p4'] not in scheduled)
  # Shared workspace stays fenced while A runs, while independent B progresses.
  self.api('worker-b','/lab/run',{});b=self.phase(['CALLBACK_CONFIRMED'],'worker-b');self.complete(b,'worker-b')
  a=self.audit();self.ledger(a,self.fixture['account_a'],10,0);self.ledger(a,self.fixture['account_b'],0,8)
  self.check('shared_workspace_waiter_not_dispatched',all(d['response']['operation_id']!=self.fixture['shared_waiter'] for d in a['deliveries']))
  self.check('two_physical_accounts_not_per_plan',len({r['account_id'] for r in a['balances']})==2)
  self.api('worker-a','/lab/stop',{});facts=self.observation(self.state());self.check('held_fixture_stopped_before_cleanup',facts['process_stopped'])
 def scenario3(self):
  self.api('worker-a','/lab/run',{});s=self.phase(['WAITING_CALLBACK']);before=self.query(s)
  self.check('effect_precedes_lost_callback',before['status']=='APPLIED')
  network=self.project+'_workers';cid=self.cid('worker-a');self.cmd(['docker','network','disconnect',network,cid])
  try:
   self.api('worker-a','/lab/continue',{});s=self.phase(['CALLBACK_UNKNOWN'],timeout=30)
  finally:self.cmd(['docker','network','connect','--alias','worker-a',network,cid])
  self.api('control-plane','/d4/v1/commands/'+s['callback_command_id'],caller='worker-a',expected=403)
  self.check('callback_not_committed',True)
  self.compose('restart','control-plane','effect-receiver','worker-a',timeout=50);self.healthy(['control-plane','effect-receiver','worker-a'])
  self.check('worker_restart_no_respawn',self.state()['phase']=='RECOVERY_REQUIRED')
  receipt=self.query(s);self.check('receiver_restart_preserves_effect',receipt==before,(receipt,before))
  self.wait_expired(s['delivery_id']);self.complete(s)
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,8)
  self.check('recovery_no_second_attempt_or_effect',len(a['attempts'])==len(a['reservations'])==len(a['effects'])==1)
 def scenario4(self):
  self.api('worker-a','/lab/run',{});s=self.phase(['PROCESS_RUNNING']);self.wait_expired(s['delivery_id'])
  facts=self.observation(s);self.check('expired_lease_process_still_alive',not facts['process_stopped'] and len(facts['members'])>0,facts)
  self.api('worker-a','/lab/late-effect',{},expected=409);self.check('expired_grant_rejects_effect',True)
  result=self.verify(s);self.check('unknown_blocks_reconciliation',not result['accepted'] and not result['stopped'] and result['status']=='UNKNOWN' and result['state']['state']=='BLOCKED_APPROVAL',result)
  a=self.audit();self.ledger(a,self.fixture['account_a'],10,0)
  self.api('worker-a','/lab/stop',{});s=self.state();result=self.verify(s)
  self.check('confirmed_stop_does_not_erase_unknown',result['stopped'] and not result['accepted'] and result['state']['state']=='BLOCKED_APPROVAL',result)
  a=self.audit();self.ledger(a,self.fixture['account_a'],10,0)
  entries=[{'account_id':x['account_id'],'settled':x['units'],'consumed':8} for x in s['info']['accounts']]
  self.api('worker-a','/lab/raw',{'action':'CALLBACK','delivery_id':s['delivery_id'],'payload':{'entries':entries}},expected=409)
  self.check('expired_callback_cannot_mutate_blocked_attempt',self.inspect(s['delivery_id'])['state']=='BLOCKED_APPROVAL')
  self.check('unknown_exclusion_retained',len(a['leases'])==1 and a['leases'][0].get('released_at') is None and len(a['effects'])==1,a['leases'])
 def scenario5(self):
  self.api('worker-a','/lab/run',{})
  if self.scenario=='S08':
   first=self.phase(['PROCESS_RUNNING']);self.wait_renewed();first=self.state();facts=self.observation(first);self.check('checkpoint_requested_while_group_alive',not facts['process_stopped'] and bool(facts['members']))
  else:first=self.phase(['CHECKPOINT_READY'])
  info=self.inspect(first['delivery_id']);initial=self.audit();reservation=initial['reservations'][0]['id']
  request=str(uuid.uuid4());body={'command_id':request,'delivery_id':first['delivery_id'],'expected_version':info['row_version']}
  one=self.api('control-plane','/lab/checkpoint/request',body);two=self.api('control-plane','/lab/checkpoint/request',body);self.check('checkpoint_request_idempotent',one==two)
  if self.scenario=='S08':
   first=self.phase(['CHECKPOINT_READY']);self.check('worker_received_bound_cooperative_request',first.get('checkpoint_request_id')==request)
  self.observation(first);proof=str(uuid.uuid4());commit=str(uuid.uuid4());checkpoint=self.api('verifier','/lab/checkpoint/verify',{'request_id':request,'proof_id':proof,'commit_id':commit})
  self.check('sealed_checkpoint_cancelled',checkpoint['state']=='CANCELLED');a=self.audit();self.ledger(a,self.fixture['account_a'],0,4)
  self.check('checkpoint_not_final_acceptance',not a['acceptance'])
  self.check('checkpoint_retains_operation_reservation_counter',len(a['attempts'])==len(a['reservations'])==len(a['checkpoints'])==1 and a['reservations'][0]['id']==reservation and not a['leases'])
  # Receiver/worker reopen existing journals; no repeated spawn on restart.
  if self.scenario=='S08':self.check('cooperative_worker_waits_for_explicit_continuation',self.state()['phase']=='CHECKPOINT_READY')
  else:
   self.compose('restart','effect-receiver','worker-a',timeout=50);self.healthy(['effect-receiver','worker-a']);self.check('checkpoint_restart_requires_recovery',self.state()['phase']=='RECOVERY_REQUIRED')
  authorization={'command_id':str(uuid.uuid4()),'checkpoint_id':commit,'expected_version':checkpoint['row_version'],'reason':'Explicit synthetic suffix continuation'}
  one=self.api('control-plane','/lab/checkpoint/authorize',authorization);two=self.api('control-plane','/lab/checkpoint/authorize',authorization);self.check('continuation_authorization_idempotent',one==two)
  self.check('authorization_does_not_create_attempt',len(self.audit()['attempts'])==1)
  self.api('control-plane','/lab/checkpoint/replan',{});self.api('worker-a','/lab/next',{});self.api('worker-a','/lab/run',{});second=self.phase(['CALLBACK_CONFIRMED'])
  self.check('same_operation_new_attempt_generation',first['identity']['operation']==second['identity']['operation'] and first['identity']['attempt']!=second['identity']['attempt'] and second['identity']['generation']==first['identity']['generation']+1)
  self.check('grant_authorizes_suffix_only',second['authorization']['grant']['steps']==['step-2'])
  if self.scenario=='S08':
   time.sleep(2);current=self.state();self.check('retired_watchdog_does_not_mutate_successor',current['phase']=='CALLBACK_CONFIRMED' and current['identity']==second['identity'])
  self.api('worker-a','/lab/raw',{'action':'CALLBACK','delivery_id':first['delivery_id'],'payload':{'entries':[{'account_id':self.fixture['account_a'],'settled':10,'consumed':4}]}},expected=409)
  self.api('effect-receiver','/lab/install',first['authorization'],caller='worker-a',expected=409)
  self.check('old_callback_and_grant_remain_fenced',self.inspect(second['delivery_id'])['state']=='VERIFYING')
  self.observation(second);result=self.api('verifier','/lab/checkpoint/finish',{'delivery_id':second['delivery_id'],'proof_id':str(uuid.uuid4()),'command_id':str(uuid.uuid4())});self.check('suffix_independently_completed',result['state']=='COMPLETED',result)
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,10);self.ledger(a,self.fixture['account_b'],0,0)
  self.check('one_stable_reservation_two_attempts',len(a['reservations'])==1 and a['reservations'][0]['id']==reservation and len(a['attempts'])==2 and len(a['continuation_links'])==1)
  self.check('conservative_top_up_ten',sum(float(j['commitment_delta']) for j in a['journal'] if float(j['commitment_delta'])>0)==20)
  self.check('prefix_not_reapplied_or_refactured',sum(float(j['consumption_delta']) for j in a['journal'])==10 and len([e for e in a['effects'] if e['status']=='APPLIED'])==2)
  self.check('final_acceptance_only_after_suffix',len(a['acceptance'])==1 and a['acceptance'][0]['attempt_id']==second['identity']['attempt'] and a['acceptance'][0]['evidence_type']=='ACCEPTANCE_PASS' and not a['leases'])
 def wait_renewed(self):
  deadline=time.monotonic()+35
  while time.monotonic()<deadline:
   s=self.state()
   if s.get('renew_count',0)>=1:return s
   if s['phase']=='BLOCKED_UNKNOWN':raise AssertionError('Unexpected renewal failure '+json.dumps(s))
   time.sleep(.5)
  raise TimeoutError('No confirmed renewal')
 def scenario6(self):
  self.api('worker-a','/lab/run',{});first=self.phase(['PROCESS_RUNNING']);original=first['authorization']['grant'];self.check('long_fixture_initially_alive',not self.observation(first)['process_stopped'])
  print('S06: proceso real de 70 s con renovaciones D2/HTTPS',flush=True)
  final=self.phase(['CALLBACK_CONFIRMED'],timeout=100);info=self.inspect(final['delivery_id'])
  self.check('execution_outlived_initial_authority',parse(info['database_now'])>parse(original['expires_at']))
  self.check('multiple_confirmed_renewals',final.get('renew_count',0)>=3,final)
  self.check('renewal_preserves_identity_generation',first['identity']==final['identity'])
  self.check('renewal_extends_receiver_authority',parse(final['authorization']['grant']['expires_at'])>parse(original['expires_at']))
  self.complete(final);a=self.audit();self.ledger(a,self.fixture['account_a'],0,8);self.ledger(a,self.fixture['account_b'],0,0)
  self.check('renewals_do_not_claim_new_attempt_or_reservation',len(a['attempts'])==len(a['reservations'])==1)
 def scenario7(self):
  self.api('worker-a','/lab/run',{});self.phase(['PROCESS_RUNNING']);first=self.wait_renewed();network=self.project+'_workers';cid=self.cid('worker-a')
  self.cmd(['docker','network','disconnect',network,cid]);started=time.monotonic()
  try:stopped=self.phase(['BLOCKED_UNKNOWN'],timeout=35)
  finally:self.cmd(['docker','network','connect','--alias','worker-a',network,cid])
  self.check('failed_renewal_triggers_bounded_stop',time.monotonic()-started<35 and 'authority_failure' in stopped)
  self.check('watchdog_stops_group_independently',self.observation(stopped)['process_stopped'])
  info=self.inspect(first['delivery_id']);self.check('stop_does_not_wait_for_lease_expiry',not info['lease_expired'])
  a=self.audit();self.ledger(a,self.fixture['account_a'],10,0);self.check('stop_keeps_attempt_and_exclusion',len(a['attempts'])==len(a['leases'])==1)
  self.wait_expired(first['delivery_id']);self.api('worker-a','/lab/late-effect',{},expected=409)
  result=self.verify(stopped);self.check('renewal_loss_does_not_fabricate_absence',not result['accepted'] and result['status']=='UNKNOWN' and result['state']['state']=='BLOCKED_APPROVAL')
  self.ledger(self.audit(),self.fixture['account_a'],10,0)
 def scenario8(self):self.scenario5()
 def scenario9(self):
  self.api('worker-a','/lab/run',{});s=self.phase(['PROCESS_RUNNING']);self.check('uncooperative_process_initially_alive',not self.observation(s)['process_stopped'])
  info=self.inspect(s['delivery_id']);request=str(uuid.uuid4());self.api('control-plane','/lab/checkpoint/request',{'command_id':request,'delivery_id':s['delivery_id'],'expected_version':info['row_version']})
  stopped=self.phase(['BLOCKED_UNKNOWN'],timeout=35);self.check('cooperation_deadline_stops_process',stopped.get('checkpoint_request_id')==request and stopped.get('authority_failure')=='CHECKPOINT_COOPERATION_TIMEOUT',stopped)
  self.check('uncooperative_group_stop_proven',self.observation(stopped)['process_stopped'])
  self.api('verifier','/lab/checkpoint/verify',{'request_id':request,'proof_id':str(uuid.uuid4()),'commit_id':str(uuid.uuid4())},expected=403)
  a=self.audit();self.check('failed_cooperation_cannot_seal_checkpoint',not a['checkpoints'] and not a['acceptance'] and not a['effects'] and len(a['leases'])==1)
  self.ledger(a,self.fixture['account_a'],10,0);self.wait_expired(s['delivery_id']);result=self.verify(stopped)
  self.check('uncooperative_result_remains_unknown',not result['accepted'] and result['status']=='UNKNOWN' and result['state']['state']=='BLOCKED_APPROVAL')
  self.ledger(self.audit(),self.fixture['account_a'],10,0)
 def loop_phase(self,phases,timeout=40):
  limit=time.monotonic()+timeout
  while time.monotonic()<limit:
   s=self.api('worker-a','/lab/loop/state')
   if s.get('phase') in phases:return s
   if str(s.get('phase','')).startswith('PAUSED_'):raise AssertionError('Polling loop paused: '+json.dumps(s))
   time.sleep(.5)
  raise TimeoutError('Polling loop phase '+str(s))
 def scenario10(self):
  command={'command_id':str(uuid.uuid4()),'max_operations':2,'duration_seconds':180}
  ack=self.api('worker-a','/lab/loop/start',command);self.check('loop_start_replay_stable',ack==self.api('worker-a','/lab/loop/start',command))
  first=self.phase(['CALLBACK_CONFIRMED']);self.check('first_operation_priority',first['identity']['operation']==self.fixture['operation_a'])
  self.loop_phase(['WAITING_ACCEPTANCE']);time.sleep(2);a=self.audit();self.check('callback_waits_for_independent_acceptance',len(a['attempts'])==1 and self.state()['identity']==first['identity'])
  self.api('worker-a','/lab/run',{},expected=403);self.check('manual_run_cannot_race_loop',True)
  self.api('control-plane','/lab/execution/status',{'delivery_id':first['delivery_id']},expected=403)
  self.api('control-plane','/lab/execution/status',{'delivery_id':first['delivery_id']},caller='worker-b',expected=403);self.check('execution_status_is_owned_and_worker_only',True)
  self.complete(first);self.api('control-plane','/lab/plan',{})
  limit=time.monotonic()+40
  while time.monotonic()<limit:
   second=self.state()
   if second.get('identity',{}).get('operation')==self.fixture['operation_next'] and second['phase']=='CALLBACK_CONFIRMED':break
   if second['phase'] in ['BLOCKED_UNKNOWN','CALLBACK_UNKNOWN']:raise AssertionError(second)
   time.sleep(.5)
  else:raise TimeoutError('Second operation was not polled')
  self.check('one_worker_executes_distinct_operations',first['identity']['worker']==second['identity']['worker'] and first['identity']['operation']!=second['identity']['operation'])
  self.check('each_operation_uses_own_first_generation',first['identity']['generation']==second['identity']['generation']==1)
  self.complete(second);loop=self.loop_phase(['COMPLETED']);self.check('loop_budget_counts_verified_completions',loop['completed']==2)
  self.check('retired_worker_idle',self.state()['phase']=='IDLE')
  self.check('completed_start_replay_does_not_restart',ack==self.api('worker-a','/lab/loop/start',command))
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,16);self.ledger(a,self.fixture['account_b'],0,0)
  self.check('two_stable_reservations_two_attempts_no_lease',len(a['attempts'])==len(a['reservations'])==2 and not a['leases'])
  self.check('two_acceptances_on_two_attempts',len(a['acceptance'])==2 and len({e['attempt_id'] for e in a['acceptance']})==2)
  history=self.compose('exec','-T','worker-a','find','/state/history','-name','*.json').stdout.splitlines();self.check('retirements_archived_by_attempt',len(history)==2)
 def scenario11(self):
  command={'command_id':str(uuid.uuid4()),'max_operations':1,'duration_seconds':10}
  self.api('worker-a','/lab/loop/start',command,caller='worker-b',expected=403)
  self.api('worker-a','/lab/loop/start',command|{'duration_seconds':4294967306},expected=403)
  ack=self.api('worker-a','/lab/loop/start',command);self.api('worker-a','/lab/loop/start',command|{'max_operations':2},expected=403)
  self.check('loop_role_budget_and_command_content_enforced',True)
  loop=self.loop_phase(['BUDGET_EXHAUSTED'],timeout=25);self.check('empty_poll_backoff_is_bounded',2<=loop['empty_polls']<=8 and loop['completed']==0,loop)
  a=self.audit();self.check('empty_poll_never_claimed_unapproved_work',not a['attempts'] and not a['reservations'] and not a['leases']);self.ledger(a,self.fixture['account_a'],0,0)
  self.compose('restart','worker-a',timeout=50);self.healthy(['worker-a']);self.check('idle_loop_restart_requires_explicit_recovery',self.state()['phase']=='RECOVERY_REQUIRED' and self.api('worker-a','/lab/loop/state')['phase']=='RECOVERY_REQUIRED')
  self.check('durable_start_replay_does_not_rearm_after_restart',ack==self.api('worker-a','/lab/loop/start',command))
  self.api('worker-a','/lab/loop/start',command|{'command_id':str(uuid.uuid4())},expected=403);self.api('worker-a','/lab/run',{},expected=403)
  self.check('restart_does_not_poll_or_respawn',not self.audit()['attempts'])
  self.api('worker-a','/lab/next',{});self.check('empty_history_recovery_can_be_explicitly_rearmed',self.state()['phase']=='IDLE')
  self.api('worker-a','/lab/loop/start',command|{'command_id':str(uuid.uuid4())});self.loop_phase(['BUDGET_EXHAUSTED'],timeout=25)
  self.check('explicit_rearm_still_obeys_admission',not self.audit()['attempts'])
 def scenario12(self):
  self.api('worker-a','/lab/loop/start',{'command_id':str(uuid.uuid4()),'max_operations':2,'duration_seconds':180});s=self.phase(['WAITING_CALLBACK']);self.check('effect_precedes_loop_callback_fault',self.query(s)['status']=='APPLIED')
  network=self.project+'_workers';cid=self.cid('worker-a');self.cmd(['docker','network','disconnect',network,cid])
  try:self.api('worker-a','/lab/continue',{});s=self.phase(['CALLBACK_UNKNOWN'],timeout=30);loop=self.loop_phase(['PAUSED_CALLBACK_UNKNOWN'])
  finally:self.cmd(['docker','network','connect','--alias','worker-a',network,cid])
  self.check('uncertain_callback_pauses_polling',loop['completed']==0);time.sleep(2);a=self.audit();self.ledger(a,self.fixture['account_a'],10,0)
  self.check('uncertain_callback_does_not_retire_or_claim_again',len(a['attempts'])==len(a['reservations'])==len(a['leases'])==1 and not a['acceptance'])
  self.api('worker-a','/lab/loop/start',{'command_id':str(uuid.uuid4()),'max_operations':1,'duration_seconds':10},expected=403);self.check('uncertainty_requires_explicit_recovery',True)
 def scenario13(self):
  # A12: neither sealing nor explicit continuation authorization rearms polling.
  command={'command_id':str(uuid.uuid4()),'max_operations':2,'duration_seconds':180}
  ack=self.api('worker-a','/lab/loop/start',command);first=self.phase(['CHECKPOINT_READY'])
  loop=self.loop_phase(['PAUSED_CHECKPOINT_READY']);self.check('checkpoint_pauses_entire_loop_without_counting_completion',loop['completed']==0)
  initial=self.audit();reservation=initial['reservations'][0]['id'];self.ledger(initial,self.fixture['account_a'],10,0)
  self.check('prefix_has_one_attempt_and_no_acceptance',len(initial['attempts'])==len(initial['reservations'])==1 and not initial['acceptance'])
  self.check('paused_start_replay_is_ack_only',ack==self.api('worker-a','/lab/loop/start',command))
  rearm={'command_id':str(uuid.uuid4()),'max_operations':1,'duration_seconds':120}
  self.api('worker-a','/lab/loop/start',rearm,expected=403);self.check('unsealed_checkpoint_cannot_rearm',True)
  request=str(uuid.uuid4());info=self.inspect(first['delivery_id'])
  self.api('control-plane','/lab/checkpoint/request',{'command_id':request,'delivery_id':first['delivery_id'],'expected_version':info['row_version']})
  self.observation(first);commit=str(uuid.uuid4())
  checkpoint=self.api('verifier','/lab/checkpoint/verify',{'request_id':request,'proof_id':str(uuid.uuid4()),'commit_id':commit})
  self.check('independent_checkpoint_commit_cancelled_source',checkpoint['state']=='CANCELLED')
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,4)
  self.check('sealed_prefix_preserves_reservation_without_final_acceptance',len(a['attempts'])==len(a['reservations'])==len(a['checkpoints'])==1 and a['reservations'][0]['id']==reservation and not a['leases'] and not a['acceptance'])
  time.sleep(2)
  self.check('seal_does_not_resume_operation_or_loop',self.inspect(first['delivery_id'])['state']=='CANCELLED' and self.state()['phase']=='CHECKPOINT_READY' and self.api('worker-a','/lab/loop/state')['phase']=='PAUSED_CHECKPOINT_READY' and len(self.audit()['attempts'])==1)
  self.api('worker-a','/lab/loop/start',rearm,expected=403);self.check('sealed_checkpoint_still_requires_explicit_local_rearm',True)
  self.api('control-plane','/lab/checkpoint/authorize',{'command_id':str(uuid.uuid4()),'checkpoint_id':commit,'expected_version':checkpoint['row_version'],'reason':'Explicit synthetic A12 suffix continuation'})
  self.api('control-plane','/lab/checkpoint/replan',{});time.sleep(2)
  self.check('authorization_and_plan_do_not_rearm_paused_loop',self.state()['phase']=='CHECKPOINT_READY' and self.api('worker-a','/lab/loop/state')['phase']=='PAUSED_CHECKPOINT_READY' and len(self.audit()['attempts'])==1)
  self.api('worker-a','/lab/loop/start',rearm,expected=403)
  self.api('worker-a','/lab/next',{});self.check('explicit_checkpoint_retirement_returns_idle',self.state()['phase']=='IDLE')
  second_ack=self.api('worker-a','/lab/loop/start',rearm);second=self.phase(['CALLBACK_CONFIRMED']);self.loop_phase(['WAITING_ACCEPTANCE'])
  self.check('rearm_preserves_operation_and_increments_attempt_generation',first['identity']['operation']==second['identity']['operation'] and first['identity']['attempt']!=second['identity']['attempt'] and second['identity']['generation']==first['identity']['generation']+1)
  self.check('rearmed_grant_authorizes_only_suffix',second['authorization']['grant']['steps']==['step-2'])
  self.api('worker-a','/lab/raw',{'action':'CALLBACK','delivery_id':first['delivery_id'],'payload':{'entries':[{'account_id':self.fixture['account_a'],'settled':10,'consumed':4}]}},expected=409)
  self.api('effect-receiver','/lab/install',first['authorization'],caller='worker-a',expected=409)
  self.check('old_callback_and_grant_fenced_after_explicit_rearm',self.inspect(second['delivery_id'])['state']=='VERIFYING')
  self.check('suffix_waits_for_independent_acceptance',not self.audit()['acceptance'] and self.state()['phase']=='CALLBACK_CONFIRMED')
  self.observation(second);result=self.api('verifier','/lab/checkpoint/finish',{'delivery_id':second['delivery_id'],'proof_id':str(uuid.uuid4()),'command_id':str(uuid.uuid4())})
  self.check('suffix_verified_completed',result['state']=='COMPLETED')
  loop=self.loop_phase(['COMPLETED']);self.check('new_loop_counts_only_its_verified_completion',loop['completed']==1 and self.state()['phase']=='IDLE')
  self.check('old_and_new_start_replays_do_not_reexecute',ack==self.api('worker-a','/lab/loop/start',command) and second_ack==self.api('worker-a','/lab/loop/start',rearm))
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,10);self.ledger(a,self.fixture['account_b'],0,0)
  self.check('one_reservation_two_d2_attempts_one_continuation',len(a['reservations'])==1 and a['reservations'][0]['id']==reservation and len(a['attempts'])==2 and len(a['continuation_links'])==1)
  self.check('conservative_top_up_original_vector',sum(float(j['commitment_delta']) for j in a['journal'] if float(j['commitment_delta'])>0)==20)
  self.check('prefix_not_reapplied_or_double_charged',sum(float(j['consumption_delta']) for j in a['journal'])==10 and len([e for e in a['effects'] if e['status']=='APPLIED'])==2)
  self.check('acceptance_only_for_verified_suffix_no_lease',len(a['acceptance'])==1 and a['acceptance'][0]['attempt_id']==second['identity']['attempt'] and a['acceptance'][0]['evidence_type']=='ACCEPTANCE_PASS' and not a['leases'])
  history=self.compose('exec','-T','worker-a','find','/state/history','-name','*.json').stdout.splitlines();self.check('prefix_and_suffix_retirements_archived',len(history)==2)
 def scenario14(self):
  command={'command_id':str(uuid.uuid4()),'max_operations':1,'duration_seconds':180}
  self.api('worker-a','/lab/loop/start',command);first=self.phase(['CHECKPOINT_READY']);self.loop_phase(['PAUSED_CHECKPOINT_READY'])
  original=first['identity'];reservation=self.audit()['reservations'][0]['id'];checkpoints=[];states=[]
  for generation in [1,2]:
   state=self.state();states.append(state);info=self.inspect(state['delivery_id']);self.check('v2_allowed_suffix_'+str(generation),info['allowed_steps']==['step-'+str(n) for n in range(generation,4)])
   self.ledger(self.audit(),self.fixture['account_a'],10,0 if generation==1 else 4);self.ledger(self.audit(),self.fixture['account_a2'],6,0 if generation==1 else 1)
   request=str(uuid.uuid4());body={'command_id':request,'delivery_id':state['delivery_id'],'expected_version':info['row_version']}
   self.check('multi_request_replay_'+str(generation),self.api('control-plane','/lab/multi/request',body)==self.api('control-plane','/lab/multi/request',body))
   self.api('control-plane','/lab/multi/request',body|{'expected_version':2**64+info['row_version']},expected=403);self.api('control-plane','/lab/multi/request',body|{'extra':True},expected=403);self.check('strict_v2_fields_and_version_'+str(generation),True)
   self.api('control-plane','/lab/multi/commit',{'command_id':str(uuid.uuid4()),'request_id':request,'proof_id':str(uuid.uuid4()),'expected_version':info['row_version']},expected=403)
   self.api('verifier','/lab/multi/verify',{},caller='worker-a',expected=403);self.check('worker_and_driver_cannot_mint_checkpoint_'+str(generation),True)
   self.observation(state);commit=str(uuid.uuid4());pid=str(uuid.uuid4());verify_body={'delivery_id':state['delivery_id'],'request_id':request,'proof_id':pid,'commit_id':commit};sealed=self.api('verifier','/lab/multi/verify',verify_body)
   self.check('multi_commit_cancelled_'+str(generation),sealed['state']=='CANCELLED');checkpoints.append(commit)
   observation=self.path/'observations'/(state['identity']['attempt']+'.json');saved=observation.read_bytes();observation.write_text('{}')
   try:self.check('verified_http_replay_uses_persisted_proof_'+str(generation),sealed==self.api('verifier','/lab/multi/verify',verify_body))
   finally:observation.write_bytes(saved)
   replay={'command_id':commit,'request_id':request,'proof_id':pid,'expected_version':info['row_version']}
   self.check('multi_commit_replay_'+str(generation),sealed==self.api('control-plane','/lab/multi/commit',replay,caller='verifier'))
   a=self.audit();self.ledger(a,self.fixture['account_a'],0,4 if generation==1 else 7);self.ledger(a,self.fixture['account_a2'],0,1 if generation==1 else 3)
   self.check('checkpoint_keeps_single_reservation_no_pass_'+str(generation),len(a['reservations'])==1 and a['reservations'][0]['id']==reservation and len(a['attempts'])==generation and len(a['multi_checkpoints'])==generation and not a['acceptance'] and not a['leases'])
   time.sleep(1);self.check('sealing_never_rearms_loop_'+str(generation),self.state()['phase']=='CHECKPOINT_READY' and self.api('worker-a','/lab/loop/state')['phase']=='PAUSED_CHECKPOINT_READY')
   self.api('worker-a','/lab/loop/start',command|{'command_id':str(uuid.uuid4())},expected=403)
   if generation==1:
    self.compose('restart','effect-receiver',timeout=50);self.healthy(['effect-receiver']);self.check('receiver_prefix_survives_restart',self.query(state)['status']=='APPLIED')
   else:
    self.api('control-plane','/lab/multi/authorize',{'command_id':str(uuid.uuid4()),'checkpoint_id':checkpoints[0],'expected_version':sealed['row_version'],'reason':'Synthetic stale checkpoint fault'},expected=409);self.check('old_checkpoint_cannot_branch',True)
   authorization={'command_id':str(uuid.uuid4()),'checkpoint_id':commit,'expected_version':sealed['row_version'],'reason':'Explicit synthetic chained continuation'}
   self.check('multi_authorization_replay_'+str(generation),self.api('control-plane','/lab/multi/authorize',authorization)==self.api('control-plane','/lab/multi/authorize',authorization))
   self.api('control-plane','/lab/checkpoint/replan',{});self.check('authorization_and_plan_do_not_rearm_'+str(generation),len(self.audit()['attempts'])==generation and self.state()['phase']=='CHECKPOINT_READY')
   self.api('worker-a','/lab/next',{});self.api('worker-a','/lab/loop/start',command|{'command_id':str(uuid.uuid4())})
   successor=self.phase(['CHECKPOINT_READY'] if generation==1 else ['CALLBACK_CONFIRMED']);self.loop_phase(['PAUSED_CHECKPOINT_READY'] if generation==1 else ['WAITING_ACCEPTANCE'])
   self.check('same_identity_new_d2_attempt_generation_'+str(generation),successor['identity']['operation']==original['operation'] and successor['identity']['worker']==original['worker'] and successor['identity']['resource']==original['resource'] and successor['identity']['generation']==generation+1 and successor['identity']['attempt']!=state['identity']['attempt'])
   self.api('effect-receiver','/lab/install',state['authorization'],caller='worker-a',expected=409)
   self.api('worker-a','/lab/raw',{'action':'CALLBACK','delivery_id':state['delivery_id'],'payload':{'entries':[{'account_id':self.fixture['account_a'],'settled':10,'consumed':4},{'account_id':self.fixture['account_a2'],'settled':6,'consumed':1}]}},expected=409)
   self.check('prior_grant_callback_fenced_'+str(generation),True)
  final=self.state();self.check('final_callback_still_waits_for_independent_acceptance',not self.audit()['acceptance'] and final['phase']=='CALLBACK_CONFIRMED')
  if self.scenario=='S18':
   terminal=self.recovery_settle(final);self.check('v2_callback_already_settled_no_double_consume',terminal['state']=='VERIFYING' and not self.audit()['acceptance']);self.ledger(self.audit(),self.fixture['account_a'],0,10);self.ledger(self.audit(),self.fixture['account_a2'],0,6)
   self.check('v2_recovered_terminal_accepted',self.recovery_accept(terminal)['state']=='COMPLETED');loop=self.loop_phase(['PAUSED_UNKNOWN','COMPLETED'])
   if loop['phase']=='PAUSED_UNKNOWN':self.api('worker-a','/lab/next',{})
   self.check('v2_terminal_retirement_never_rearms_paused_loop',self.state()['phase']=='IDLE' and len(self.audit()['attempts'])==3);a=self.audit();self.check('v2_terminal_keeps_three_attempts_and_two_checkpoints',len(a['attempts'])==3 and len(a['multi_checkpoints'])==2 and len(a['acceptance'])==1 and not a['leases']);return
  self.observation(final);finish_body={'delivery_id':final['delivery_id'],'proof_id':str(uuid.uuid4()),'command_id':str(uuid.uuid4())};result=self.api('verifier','/lab/multi/finish',finish_body);self.check('independent_v2_finalization',result['state']=='COMPLETED')
  self.loop_phase(['COMPLETED']);self.check('final_v2_retirement_idle',self.state()['phase']=='IDLE')
  observation=self.path/'observations'/(final['identity']['attempt']+'.json');saved=observation.read_bytes();observation.write_text('{}')
  try:self.check('final_http_replay_uses_persisted_acceptance',result==self.api('verifier','/lab/multi/finish',finish_body))
  finally:observation.write_bytes(saved)
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,10);self.ledger(a,self.fixture['account_a2'],0,6);self.ledger(a,self.fixture['account_b'],0,0)
  self.check('one_reservation_three_attempts_two_checkpoints',len(a['reservations'])==1 and a['reservations'][0]['id']==reservation and len(a['attempts'])==3 and len(a['multi_checkpoints'])==len(a['multi_links'])==len(a['multi_authorizations'])==2 and not a['leases'])
  for account,expected in [(self.fixture['account_a'],30),(self.fixture['account_a2'],18)]:self.check('full_original_top_up_'+account,sum(float(j['commitment_delta']) for j in a['journal'] if j['account_id']==account and float(j['commitment_delta'])>0)==expected)
  self.check('logical_steps_applied_once_each',len([e for e in a['effects'] if e['status']=='APPLIED'])==3)
  self.check('single_pass_only_final_attempt',len(a['acceptance'])==1 and a['acceptance'][0]['attempt_id']==final['identity']['attempt'] and a['acceptance'][0]['evidence_type']=='ACCEPTANCE_PASS')
  history=self.compose('exec','-T','worker-a','find','/state/history','-name','*.json').stdout.splitlines();self.check('all_three_attempts_archived',len(history)==3)
 def scenario15(self):
  self.api('worker-a','/lab/loop/start',{'command_id':str(uuid.uuid4()),'max_operations':1,'duration_seconds':180})
  state=self.phase(['CHECKPOINT_READY']);self.loop_phase(['PAUSED_CHECKPOINT_READY']);info=self.inspect(state['delivery_id']);request=str(uuid.uuid4())
  self.check('compatible_v2_manifest_exposed_without_new_authority',info['manifest_compatible'] is True)
  self.api('control-plane','/lab/multi/request',{'command_id':request,'delivery_id':state['delivery_id'],'expected_version':info['row_version']})
  body={'delivery_id':state['delivery_id'],'request_id':request,'proof_id':str(uuid.uuid4()),'commit_id':str(uuid.uuid4())}
  self.observation(state);observation=self.path/'observations'/(state['identity']['attempt']+'.json');saved=observation.read_bytes();envelope=json.loads(saved);facts=json.loads(envelope['facts']);facts['campaign']=str(uuid.uuid4());envelope['facts']=json.dumps(facts,separators=(',',':'));observation.write_text(json.dumps(envelope))
  try:self.api('verifier','/lab/multi/verify',body,expected=403)
  finally:observation.write_bytes(saved)
  self.check('fresh_forged_observation_rejected_before_ingress',not self.audit()['multi_proofs'])
  remote='/state/supervisor/attempts/'+state['identity']['attempt']+'/stdout.bin';original=self.compose('exec','-T','worker-a','cat',remote).stdout.encode();candidate=self.path/'corrupted-stdout.bin';candidate.write_bytes(b'{"fixture":"FORGED","candidate":true}\n')
  self.compose('cp',str(candidate),'worker-a:'+remote)
  try:self.observation(state);self.api('verifier','/lab/multi/verify',body,expected=403)
  finally:candidate.write_bytes(original);self.compose('cp',str(candidate),'worker-a:'+remote)
  a=self.audit();self.ledger(a,self.fixture['account_a'],10,0);self.ledger(a,self.fixture['account_a2'],6,0)
  self.check('invalid_artifact_proof_retains_both_commitments',not a['multi_proofs'] and not a['multi_checkpoints'] and not a['acceptance'] and len(a['leases'])==1 and len(a['attempts'])==1)
  absent=self.api('effect-receiver','/lab/query',{'operation':state['identity']['operation'],'intent_hash':state['authorization']['grant']['intent_hash'],'step':'step-2','generation':state['identity']['generation']})
  self.check('invalid_proof_does_not_fabricate_sealed_absence',absent['status']=='UNKNOWN')
  self.observation(state);accepted=self.api('verifier','/lab/multi/verify',body);self.check('same_command_can_verify_after_correct_independent_observation',accepted['state']=='CANCELLED')
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,4);self.ledger(a,self.fixture['account_a2'],0,1)
  self.check('valid_prefix_does_not_create_final_pass_or_auto_continue',len(a['multi_proofs'])==len(a['multi_checkpoints'])==1 and not a['acceptance'] and not a['multi_authorizations'] and not a['leases'] and len(a['attempts'])==1 and self.api('worker-a','/lab/loop/state')['phase']=='PAUSED_CHECKPOINT_READY')
 def recovery_observe(self,state,step):
  return self.api('verifier','/lab/recovery/observe',{'command_id':str(uuid.uuid4()),'delivery_id':state['delivery_id'],'step':step})
 def recovery_settle(self,state):
  self.wait_expired(state['delivery_id']);self.observation(state)
  body={'delivery_id':state['delivery_id'],'proof_id':str(uuid.uuid4()),'command_id':str(uuid.uuid4())}
  result=self.api('verifier','/lab/recovery/settle',body)
  self.check('recovery_command_replay_'+str(state['identity']['generation']),result==self.api('verifier','/lab/recovery/settle',body))
  return result
 def recovery_accept(self,resolution):
  body={'command_id':str(uuid.uuid4()),'resolution_id':resolution['resolution_id']}
  result=self.api('verifier','/lab/recovery/accept',body);self.check('terminal_acceptance_replay',result==self.api('verifier','/lab/recovery/accept',body));return result
 def scenario16(self):
  self.api('worker-a','/lab/run',{});first=self.phase(['CHECKPOINT_READY']);reservation=self.audit()['reservations'][0]['id']
  unknown=self.recovery_observe(first,'step-2');self.check('actual_receiver_unknown_before_apply',unknown['status']=='UNKNOWN')
  payload=base64.b64encode(('synthetic-effect:'+first['identity']['operation']+':step-2').encode()).decode()
  self.api('effect-receiver','/lab/effect',{'authorization':first['authorization'],'step':'step-2','payload':payload},caller='worker-a')
  applied=self.recovery_observe(first,'step-2');self.check('same_journal_applied_after_unknown',applied['status']=='APPLIED')
  recovered=self.recovery_settle(first);self.check('reconciled_partial_becomes_cancelled',recovered['state']=='CANCELLED')
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,7);self.ledger(a,self.fixture['account_a2'],0,3)
  self.check('contradictory_facts_retained_no_pass_no_autocontinue',len(a['effects'])==2 and not a['acceptance'] and not a['leases'] and len(a['attempts'])==1 and len(a['recovery_settlements'])==1)
  self.api('control-plane','/lab/multi/authorize',{'command_id':str(uuid.uuid4()),'checkpoint_id':recovered['checkpoint_id'],'expected_version':recovered['row_version'],'reason':'Explicit recovered v2 suffix'})
  self.api('control-plane','/lab/checkpoint/replan',{});self.api('worker-a','/lab/next',{});self.api('worker-a','/lab/run',{});last=self.phase(['CALLBACK_CONFIRMED'])
  self.check('recovered_v2_new_attempt_same_operation',last['identity']['operation']==first['identity']['operation'] and last['identity']['generation']==2 and last['authorization']['grant']['steps']==['step-3'])
  self.api('effect-receiver','/lab/install',first['authorization'],caller='worker-a',expected=409);self.check('reconciled_old_grant_fenced',True)
  self.observation(last);done=self.api('verifier','/lab/multi/finish',{'delivery_id':last['delivery_id'],'proof_id':str(uuid.uuid4()),'command_id':str(uuid.uuid4())});self.check('recovered_v2_completed',done['state']=='COMPLETED')
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,10);self.ledger(a,self.fixture['account_a2'],0,6);self.check('one_reservation_two_attempts_one_acceptance',len(a['reservations'])==1 and a['reservations'][0]['id']==reservation and len(a['attempts'])==2 and len(a['acceptance'])==1)
 def scenario17(self):
  self.api('worker-a','/lab/run',{});first=self.phase(['CHECKPOINT_READY']);unknown=self.recovery_observe(first,'step-2');self.check('v1_unknown_retained_before_close',unknown['status']=='UNKNOWN')
  recovered=self.recovery_settle(first);self.check('v1_recovery_native_checkpoint',recovered['state']=='CANCELLED' and len(self.audit()['checkpoints'])==1);self.ledger(self.audit(),self.fixture['account_a'],0,4)
  self.api('control-plane','/lab/checkpoint/authorize',{'command_id':str(uuid.uuid4()),'checkpoint_id':recovered['checkpoint_id'],'expected_version':recovered['row_version'],'reason':'Explicit recovered v1 suffix'})
  self.api('control-plane','/lab/checkpoint/replan',{});self.api('worker-a','/lab/next',{});self.api('worker-a','/lab/run',{});last=self.phase(['WAITING_CALLBACK'])
  self.check('v1_only_suffix_new_generation',last['identity']['generation']==2 and last['identity']['operation']==first['identity']['operation'] and last['authorization']['grant']['steps']==['step-2'])
  terminal=self.recovery_settle(last);a=self.audit();self.check('v1_terminal_does_not_auto_accept',terminal['state']=='VERIFYING' and not a['acceptance'] and len(a['leases'])==1);self.ledger(a,self.fixture['account_a'],0,10)
  self.api('worker-a','/lab/recovery/retire',{},expected=403);self.check('v1_unaccepted_recovery_cannot_retire',True)
  self.check('v1_terminal_accepted_independently',self.recovery_accept(terminal)['state']=='COMPLETED');self.api('worker-a','/lab/recovery/retire',{});self.check('v1_explicit_retirement_idle_without_rearm',self.state()['phase']=='IDLE');a=self.audit();self.check('v1_two_attempts_same_reservation_retained_unknown',len(a['attempts'])==2 and len(a['reservations'])==1 and len(a['acceptance'])==1 and any(e['status']=='UNKNOWN' for e in a['effects']) and not a['leases'])
 def scenario18(self):self.scenario14()
 def scenario19(self):
  self.api('worker-a','/lab/run',{});state=self.phase(['WAITING_CALLBACK']);self.check('single_step_applied_observed',self.recovery_observe(state,'step-1')['status']=='APPLIED')
  terminal=self.recovery_settle(state);self.check('single_step_terminal_waits_for_acceptance',terminal['state']=='VERIFYING' and not self.audit()['acceptance']);self.ledger(self.audit(),self.fixture['account_a'],0,8)
  self.api('worker-a','/lab/recovery/retire',{},expected=403);self.check('single_step_unaccepted_recovery_cannot_retire',True)
  self.check('single_step_recovery_completed',self.recovery_accept(terminal)['state']=='COMPLETED');self.api('worker-a','/lab/recovery/retire',{});self.check('single_step_explicit_retirement_idle_without_rearm',self.state()['phase']=='IDLE');a=self.audit();self.check('no_new_attempt_for_applied_terminal',len(a['attempts'])==1 and len(a['reservations'])==1 and len(a['acceptance'])==1 and not a['leases'])
 def absence_first(self):
  self.api('worker-a','/lab/run',{});first=self.phase(['ABSENCE_READY']);reservation=self.audit()['reservations'][0]['id']
  self.check('no_effect_before_absence_seal',self.recovery_observe(first,'step-1')['status']=='UNKNOWN')
  self.api('worker-a','/lab/recovery/retire',{},expected=403);self.check('absence_without_independent_seal_cannot_retire',True)
  self.wait_expired(first['delivery_id']);self.observation(first)
  body={'delivery_id':first['delivery_id'],'proof_id':str(uuid.uuid4()),'command_id':str(uuid.uuid4())}
  result=self.api('verifier','/lab/absence/settle',body)
  self.check('absence_settlement_replay',result==self.api('verifier','/lab/absence/settle',body))
  a=self.audit();self.check('retry_pending_without_fake_checkpoint_or_acceptance',result['state']=='RETRY_PENDING' and not a['checkpoints'] and not a['multi_checkpoints'] and not a['acceptance'] and not a['leases'] and len(a['absence_seals'])==1 and len(a['attempts'])==1)
  self.ledger(a,self.fixture['account_a'],0,0)
  if 'account_a2' in self.fixture:self.ledger(a,self.fixture['account_a2'],0,0)
  self.check('absence_does_not_mint_consume',not any(float(x['consumption_delta']) for x in a['journal']))
  self.api('worker-a','/lab/late-effect',{},expected=409);self.check('closed_old_effect_channel',True)
  self.api('worker-a','/lab/recovery/retire',{});self.check('explicit_retirement_does_not_rearm',self.state()['phase']=='IDLE')
  self.api('control-plane','/lab/absence/authorize',{'command_id':str(uuid.uuid4()),'seal_id':result['seal_id'],'expected_version':result['row_version'],'reason':'Explicit A20 same-operation retry'})
  self.check('authorization_does_not_start_worker',self.state()['phase']=='IDLE')
  self.api('control-plane','/lab/checkpoint/replan',{});self.api('worker-a','/lab/run',{});second=self.phase(['CHECKPOINT_READY'])
  self.check('retry_same_operation_new_generation_all_steps',second['identity']['operation']==first['identity']['operation'] and second['identity']['generation']==2 and set(second['authorization']['grant']['steps'])==({'step-1','step-2','step-3'} if 'account_a2' in self.fixture else {'step-1','step-2'}))
  a=self.audit();self.ledger(a,self.fixture['account_a'],10,0)
  if 'account_a2' in self.fixture:self.ledger(a,self.fixture['account_a2'],6,0)
  self.check('retry_same_reservation_explicit_link',len(a['reservations'])==1 and a['reservations'][0]['id']==reservation and len(a['absence_links'])==1 and len(a['attempts'])==2)
  self.api('effect-receiver','/lab/install',first['authorization'],caller='worker-a',expected=409);self.check('absence_generation_fenced',True)
  return second
 def scenario20(self):
  second=self.absence_first()
  # Two applied steps in generation 2 leave one suffix for the final D2 attempt.
  payload=base64.b64encode(('synthetic-effect:'+second['identity']['operation']+':step-2').encode()).decode()
  self.api('effect-receiver','/lab/effect',{'authorization':second['authorization'],'step':'step-2','payload':payload},caller='worker-a')
  rid=str(uuid.uuid4());self.api('control-plane','/lab/multi/request',{'command_id':rid,'delivery_id':second['delivery_id'],'expected_version':self.inspect(second['delivery_id'])['row_version']})
  self.observation(second);cp=self.api('verifier','/lab/multi/verify',{'delivery_id':second['delivery_id'],'proof_id':str(uuid.uuid4()),'commit_id':str(uuid.uuid4()),'request_id':rid})
  self.check('real_checkpoint_after_absent_attempt',cp['state']=='CANCELLED')
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,7);self.ledger(a,self.fixture['account_a2'],0,3)
  self.api('control-plane','/lab/multi/authorize',{'command_id':str(uuid.uuid4()),'checkpoint_id':cp['checkpoint_id'],'expected_version':cp['row_version'],'reason':'Explicit final A20 suffix'})
  self.api('control-plane','/lab/checkpoint/replan',{});self.api('worker-a','/lab/next',{});self.api('worker-a','/lab/run',{});last=self.phase(['CALLBACK_CONFIRMED'])
  self.observation(last);done=self.api('verifier','/lab/multi/finish',{'delivery_id':last['delivery_id'],'proof_id':str(uuid.uuid4()),'command_id':str(uuid.uuid4())})
  self.check('absence_then_partial_then_final_completed',done['state']=='COMPLETED' and last['identity']['generation']==3)
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,10);self.ledger(a,self.fixture['account_a2'],0,6)
  self.check('three_attempts_one_pass_no_fake_checkpoint',len(a['attempts'])==3 and len(a['acceptance'])==1 and len(a['multi_checkpoints'])==1 and len(a['absence_seals'])==1 and not a['leases'])
 def scenario21(self):
  second=self.absence_first();request=self.api('control-plane','/lab/checkpoint/request',{'command_id':str(uuid.uuid4()),'delivery_id':second['delivery_id'],'expected_version':self.inspect(second['delivery_id'])['row_version']})
  self.observation(second);cp=self.api('verifier','/lab/checkpoint/verify',{'request_id':request['request_id'],'proof_id':str(uuid.uuid4()),'commit_id':str(uuid.uuid4())})
  self.check('v1_real_checkpoint_only_after_actual_progress',cp['state']=='CANCELLED');self.ledger(self.audit(),self.fixture['account_a'],0,4)
  self.api('control-plane','/lab/checkpoint/authorize',{'command_id':str(uuid.uuid4()),'checkpoint_id':cp['checkpoint_id'],'expected_version':cp['row_version'],'reason':'Explicit v1 suffix after A20'})
  self.api('control-plane','/lab/checkpoint/replan',{});self.api('worker-a','/lab/next',{});self.api('worker-a','/lab/run',{});last=self.phase(['CALLBACK_CONFIRMED'])
  self.observation(last);done=self.api('verifier','/lab/checkpoint/finish',{'delivery_id':last['delivery_id'],'proof_id':str(uuid.uuid4()),'command_id':str(uuid.uuid4())})
  self.check('v1_absence_checkpoint_suffix_complete',done['state']=='COMPLETED' and last['identity']['generation']==3)
  a=self.audit();self.ledger(a,self.fixture['account_a'],0,10);self.check('v1_one_reservation_three_attempts_one_real_checkpoint',len(a['reservations'])==1 and len(a['attempts'])==3 and len(a['checkpoints'])==1 and len(a['absence_seals'])==1 and len(a['acceptance'])==1 and not a['leases'])

 def healthy(self,services):
  deadline=time.monotonic()+90
  while time.monotonic()<deadline:
   rows=json.loads(self.cmd(['docker','inspect',*[self.cid(s) for s in services]]).stdout)
   if all(r['State'].get('Health',{}).get('Status')=='healthy' for r in rows):return
   time.sleep(2)
  raise TimeoutError('Restart health checks failed')
 def finish(self,error=None):
  try:
   (self.path/'containers.log').write_text(self.compose('logs','--no-color',check=False).stdout)
   if self.cid('driver'):
    (self.path/'audit-final.json').write_text(json.dumps(self.audit(),indent=2))
   for service,source in [('worker-a','/state'),('worker-b','/state'),('effect-receiver','/state')]:
    self.compose('cp',service+':'+source,str(self.path/(service+'-state')),check=False)
  except Exception as ex:(self.path/'collection-error.txt').write_text(str(ex))
  cleanup=self.compose('down','-v','--remove-orphans','--timeout','10',timeout=60,check=False);(self.path/'cleanup.log').write_text(cleanup.stdout+cleanup.stderr)
  remaining=self.cmd(['docker','ps','-aq','--filter','label=com.docker.compose.project='+self.project]).stdout.strip()
  networks=self.cmd(['docker','network','ls','-q','--filter','label=com.docker.compose.project='+self.project]).stdout.strip()
  volumes=self.cmd(['docker','volume','ls','-q','--filter','label=com.docker.compose.project='+self.project]).stdout.strip()
  residue={'containers':len(remaining.splitlines()),'networks':len(networks.splitlines()),'volumes':len(volumes.splitlines())}
  if any(residue.values()):error=RuntimeError('Project resources remain after selective cleanup: '+str(residue))
  report={'project':self.project,'scenario':self.scenario,'campaign':self.campaign,'status':'PASS' if error is None and cleanup.returncode==0 else 'FAIL','checks':self.checks,'cleanup_remaining':residue,'duration_seconds':round(time.monotonic()-self.started,3),'error':None if error is None else str(error)}
  (self.path/'result.json').write_text(json.dumps(report,indent=2)+'\n');return report

def main():
 parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);parser.add_argument('--scenarios',nargs='+',default=['S01','S02','S03','S04']);args=parser.parse_args();run=args.run.resolve();image=(run/'image-tag.txt').read_text().strip();results=[]
 for scenario in args.scenarios:
  case=Case(run,scenario,image);error=None
  try:
   case.start();getattr(case,'scenario'+str(int(scenario[1:])))()
  except Exception as ex:error=ex;print(scenario+': FAIL '+str(ex),flush=True)
  finally:result=case.finish(error);results.append(result)
  print(scenario+': '+result['status']+' ('+str(len(result['checks']))+' comprobaciones)',flush=True)
  if result['status']!='PASS':break
 (run/'scenario-results.json').write_text(json.dumps(results,indent=2)+'\n')
 if len(results)!=len(args.scenarios) or any(r['status']!='PASS' for r in results):raise SystemExit(1)
if __name__=='__main__':main()
