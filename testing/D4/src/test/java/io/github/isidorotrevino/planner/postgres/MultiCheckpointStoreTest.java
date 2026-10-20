// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;

/** V24 persistence/upgrade tests; proofs are supplied by the owner fixture.
 * Signature/process/receiver verification belongs to the separate Compose campaign.
 */
class MultiCheckpointStoreTest {
 DeliveryStoreTest f;UUID b,delivery;String manifest;int generation=1;
 @BeforeEach void setup(TestInfo test)throws Exception{
  boolean late=test.getTestMethod().orElseThrow().getName().equals("initialCaptureMustIncludeV2Intention");
  f=new DeliveryStoreTest();f.db="d4_multi_"+id().toString().replace("-","");try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+f.db);}
  assertEquals(24,migrations(f.db,"24").migrate().migrationsExecuted);migrations(f.db,"24").validate();assertEquals(0,migrations(f.db,"24").migrate().migrationsExecuted);
  try(var c=f.owner()){
   f.fixture(c,true);b=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'tokens','TOKENS','WEEKLY',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '10 days','SYNTHETIC',1,100)",f.resource,id().toString());
   manifest=value(c,"SELECT jsonb_build_object('schema','d4.steps.v2','resource',?::uuid,'pool','PLANNED','accounts',(SELECT jsonb_object_agg(id,jsonb_build_object('original',CASE WHEN id=? THEN 10 ELSE 6 END,'dimension',dimension,'unit',unit,'start',window_start,'end',window_end)) FROM d2.accounts WHERE resource_id=?),'steps',jsonb_build_array(jsonb_build_object('id','step-1','effect_hash',repeat('1',64),'cost',jsonb_build_object(?::text,4,?::text,1)),jsonb_build_object('id','step-2','effect_hash',repeat('2',64),'cost',jsonb_build_object(?::text,3,?::text,2)),jsonb_build_object('id','step-3','effect_hash',repeat('3',64),'cost',jsonb_build_object(?::text,3,?::text,3))))::text",f.resource,f.account,f.resource,f.account,b,f.account,b,f.account,b);
   if(test.getTestMethod().orElseThrow().getName().equals("legacyRunningNumericIntentionCannotRenewGrant"))manifest=value(c,"SELECT jsonb_set(?::jsonb,'{steps,0,id}','7')::text",manifest);
   if(test.getTestMethod().orElseThrow().getName().equals("legacyRunningExtraIntentionCannotRenewGrant"))manifest=value(c,"SELECT (?::jsonb||'{\"note\":\"legacy\"}'::jsonb)::text",manifest);
   String context="{\"fixture\":\"PARTIAL\",\"step_manifest\":"+manifest+"}";
   sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||jsonb_build_object('interruptible',true,'max_attempts',?),context_pack_sha256=encode(digest(?,'sha256'),'hex') WHERE id=?",test.getTestMethod().orElseThrow().getName().equals("exhaustedAttemptsBlockPartialButAllowTerminalRecovery")?1:3,context,f.operation);
   sql(c,"INSERT INTO d4.lab_intents VALUES(?,convert_to(?,'UTF8'),10)",f.operation,context);if(!late)sql(c,"INSERT INTO d4.multi_intents VALUES(?,?::jsonb,encode(digest((?::jsonb)::text,'sha256'),'hex'))",f.operation,manifest,manifest);
   var at=java.time.Instant.parse(value(c,"SELECT to_char(clock_timestamp() AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.US\"Z\"')"));
   STORE.configure(c,id(),Map.ofEntries(Map.entry("action","ESTIMATE"),Map.entry("reason","Synthetic multicount"),Map.entry("expected_estimate_id",UUID.fromString(value(c,"SELECT estimate_id FROM d3.estimate_heads WHERE operation_id=? AND resource_id=?",f.operation,f.resource))),Map.entry("estimate_id",id()),Map.entry("operation_id",f.operation),Map.entry("resource_id",f.resource),Map.entry("units",Map.of(f.account,10,b,6)),Map.entry("duration_ms",60000),Map.entry("confidence",1),Map.entry("calibration_ref","fixture-v1"),Map.entry("provenance","SYNTHETIC"),Map.entry("observed_at",at.minusSeconds(1)),Map.entry("valid_until",at.plusSeconds(86400))));
  }replan();if(!late)launch();
 }
 @AfterEach void cleanup()throws Exception{if(f!=null)f.cleanup();}
 String call(Connection c,String name,Object...args)throws SQLException{return value(c,"SELECT d4."+name+"("+String.join(",",Collections.nCopies(args.length,"?"))+")::text",args);}
 void replan()throws Exception{var store=new ContinuationPlanningStore();try(var c=f.owner()){store.observeEligibility(c,id());var capture=store.capture(c,id());var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(capture.request(),capture.snapshot());f.plan=store.publish(c,id(),id(),capture,result);}}
 void launch()throws Exception{delivery=id();try(var c=f.owner()){f.call(c,"deliver_continuation",delivery,f.worker,f.request());f.call(c,"ack",id(),f.worker,Map.of("action","ACK","delivery_id",delivery));f.call(c,"worker_execution",id(),f.worker,Map.of("action","START","delivery_id",delivery));}}
 long version(Connection c)throws Exception{return Long.parseLong(value(c,"SELECT row_version FROM operations WHERE id=?",f.operation));}
 String proof(Connection c,boolean terminal)throws Exception{
  var receipts=new TreeMap<String,Object>();for(int n=generation;n<=3;n++)receipts.put("step-"+n,Map.of("status",n==generation?"APPLIED":"ABSENT","generation",generation,"closed",true,"payloadHash",String.valueOf(n).repeat(64)));
  return value(c,"SELECT jsonb_build_object('schema','d4.checkpoint.proof.v2','operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation','context_hash',i->'context_hash','policy_hash',i->'policy_hash','manifest_hash',i->'manifest_hash','parent_checkpoint',i->'parent_checkpoint','process_stopped',true,'artifact_valid',true,'receiver_closed',true,'close_sequence',10,'host_observation_hash',repeat('a',64),'stdout_hash',repeat('b',64),'stderr_hash',repeat('c',64),'receipts',?::jsonb)::text FROM (SELECT d4.multi_inspect(?) i) x",Json.write(receipts),delivery);
 }
 UUID[] prepared()throws Exception{try(var c=f.owner()){var rid=id();call(c,"multi_request",rid,delivery,version(c));var pid=id();value(c,"SELECT d4.multi_record_proof(?,?,?,?::jsonb)::text",pid,delivery,rid,proof(c,false));return new UUID[]{rid,pid};}}
 UUID commit()throws Exception{var p=prepared();var cid=id();try(var c=f.owner()){call(c,"multi_commit",cid,p[0],p[1],version(c));}return cid;}
 UUID authorize(UUID cp)throws Exception{var cid=id();try(var c=f.owner()){call(c,"multi_authorize",cid,cp,version(c),"Explicit synthetic v2 continuation");}return cid;}
 void next(UUID cp)throws Exception{authorize(cp);replan();generation++;launch();}
 void balance(String pendingA,String consumedA,String pendingB,String consumedB)throws Exception{try(var c=f.owner()){assertEquals(pendingA+"/"+consumedA,value(c,"SELECT outstanding::int||'/'||consumed::int FROM d2.reservation_balances WHERE account_id=?",f.account));assertEquals(pendingB+"/"+consumedB,value(c,"SELECT outstanding::int||'/'||consumed::int FROM d2.reservation_balances WHERE account_id=?",b));}}
 void reject(String state,SQLAction action){var ex=assertThrows(SQLException.class,action::run);assertEquals(state,ex.getSQLState(),ex.getMessage());}
 @FunctionalInterface interface SQLAction{void run()throws Exception;}
 void callback()throws Exception{try(var c=f.owner()){f.call(c,"worker_execution",id(),f.worker,Map.of("action","CALLBACK","delivery_id",delivery,"payload",Map.of("entries",List.of(Map.of("account_id",f.account,"settled",10,"consumed",3),Map.of("account_id",b,"settled",6,"consumed",3)))));}}
 @Test void chainSettlesBothAccountsAndFinalAcceptanceOnce()throws Exception{
  var first=commit();balance("0","4","0","1");next(first);balance("10","4","6","1");var second=commit();balance("0","7","0","3");next(second);balance("10","7","6","3");callback();balance("0","10","0","6");
  try(var c=f.owner()){
   var pid=id();var proof=proof(c,true);assertEquals(value(c,"SELECT d4.multi_accept(?,?,?::jsonb)::text",pid,delivery,proof),value(c,"SELECT d4.multi_accept(?,?,?::jsonb)::text",pid,delivery,proof));var command=id();assertEquals(call(c,"multi_finalize",command,delivery),call(c,"multi_finalize",command,delivery));
   assertEquals("COMPLETED",value(c,"SELECT state FROM operations"));assertEquals("3",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("2",value(c,"SELECT count(*) FROM d4.multi_links"));assertEquals("1",value(c,"SELECT count(*) FROM execution_evidence"));assertEquals("true",value(c,"SELECT (d4.worker_execution_status(?,?)->>'retirable')",f.worker,delivery));
   assertEquals("30/18",value(c,"SELECT sum(commitment_delta) FILTER(WHERE account_id=? AND commitment_delta>0)::int||'/'||sum(commitment_delta) FILTER(WHERE account_id=? AND commitment_delta>0)::int FROM d2.journal",f.account,b));
  }
 }
 @Test void commitReplayAndConcurrentSameCommandDoNotDoubleConsume()throws Exception{
  var p=prepared();var cid=id();long ver;try(var c=f.owner()){ver=version(c);}try(var pool=java.util.concurrent.Executors.newFixedThreadPool(2)){
   java.util.concurrent.Callable<String> action=()->{try(var c=f.owner()){return call(c,"multi_commit",cid,p[0],p[1],ver);}};var results=pool.invokeAll(List.of(action,action));assertEquals(results.get(0).get(),results.get(1).get());
  }balance("0","4","0","1");
 }
 @Test void oldCheckpointCannotBeAuthorizedAfterSecondCheckpoint()throws Exception{var cp=commit();next(cp);var cp2=commit();try(var c=f.owner()){reject("P0002",()->call(c,"multi_authorize",id(),cp,version(c),"stale parent"));assertEquals("1",value(c,"SELECT count(*) FROM d4.multi_heads WHERE id=?",cp2));}}
 @Test void expiryBeforeCommitRollsBackEveryAccount()throws Exception{var p=prepared();try(var c=f.owner()){sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second'");reject("23514",()->call(c,"multi_commit",id(),p[0],p[1],version(c)));assertEquals("0",value(c,"SELECT count(*) FROM d4.multi_checkpoints"));assertEquals("1",value(c,"SELECT count(*) FROM operation_leases"));}balance("10","0","6","0");}
 @Test void unknownAndUnexpectedFactRetainAllCommitments()throws Exception{try(var c=f.owner()){sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(?,1,'extra','UNKNOWN','synthetic')",f.operation);reject("23514",()->prepared());}balance("10","0","6","0");}
 @Test void malformedAndWrongParentProofDoNotEnterLedger()throws Exception{try(var c=f.owner()){var r=id();call(c,"multi_request",r,delivery,version(c));var p=proof(c,false);for(var expression:List.of("jsonb_set(?::jsonb,'{receipts,step-2,status}','\"UNKNOWN\"')","?::jsonb-'receipts'","jsonb_set(?::jsonb,'{parent_checkpoint}','\""+id()+"\"')")){String changed=value(c,"SELECT ("+expression+")::text",p);reject("23514",()->value(c,"SELECT d4.multi_record_proof(?,?,?,?::jsonb)::text",id(),delivery,r,changed));}}balance("10","0","6","0");}
 @Test void proofAddedAfterCaptureInvalidatesPublication()throws Exception{var cp=commit();authorize(cp);var store=new ContinuationPlanningStore();try(var c=f.owner()){store.observeEligibility(c,id());var capture=store.capture(c,id());var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(capture.request(),capture.snapshot());sql(c,"INSERT INTO d4.multi_proofs SELECT ?,delivery_id,request_id,proof,evaluation FROM d4.multi_proofs LIMIT 1",id());reject("40001",()->store.publish(c,id(),id(),capture,result));}}
 @Test void frozenManifestAndHeadHistoryAreAppendOnly()throws Exception{try(var c=f.owner()){reject("55000",()->sql(c,"UPDATE d4.multi_intents SET manifest=manifest"));reject("55000",()->sql(c,"TRUNCATE d4.multi_proofs CASCADE"));}balance("10","0","6","0");}
 @Test void runtimeRoleCannotMintV2ProofOrReadTables()throws Exception{try(var c=f.owner()){sql(c,"CREATE ROLE multi_runtime NOLOGIN;GRANT USAGE ON SCHEMA d4 TO multi_runtime;SET ROLE multi_runtime");reject("42501",()->value(c,"SELECT d4.multi_record_proof(NULL,NULL,NULL,'{}')::text"));reject("42501",()->sql(c,"SELECT * FROM d4.multi_checkpoints"));}}
 @Test void firstClaimStillFreezesBothAccountMappings()throws Exception{try(var c=f.owner()){assertEquals("2",value(c,"SELECT count(*) FROM d2.operation_accounts"));assertEquals("2",value(c,"SELECT count(*) FROM d2.reservation_balances"));reject("55000",()->sql(c,"UPDATE d2.operation_accounts SET units=units+1 WHERE account_id=?",b));}balance("10","0","6","0");}
 @Test void v23UpgradeWithRunningV1PreservesLeaseJournalAndAttempts()throws Exception{
  var old=new DeliveryStoreTest();old.db="d4_upgrade_"+id().toString().replace("-","");try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+old.db);}
  try{assertEquals(23,migrations(old.db,"23").migrate().migrationsExecuted);String before;
   try(var c=old.owner()){old.fixture(c,true);var d=id();old.call(c,"deliver_continuation",d,old.worker,old.request());old.call(c,"ack",id(),old.worker,Map.of("action","ACK","delivery_id",d));old.call(c,"worker_execution",id(),old.worker,Map.of("action","START","delivery_id",d));before=state(c);}
   assertEquals(1,migrations(old.db,"24").migrate().migrationsExecuted);try(var c=old.owner()){assertEquals(before,state(c));assertEquals("0",value(c,"SELECT count(*) FROM d4.multi_intents"));}
  }finally{old.cleanup();}
 }
 String state(Connection c)throws Exception{return value(c,"SELECT jsonb_build_object('operations',(SELECT jsonb_agg(to_jsonb(t)) FROM operations t),'leases',(SELECT jsonb_agg(to_jsonb(t)) FROM operation_leases t),'attempts',(SELECT jsonb_agg(to_jsonb(t)) FROM execution_attempts t),'journal',(SELECT jsonb_agg(to_jsonb(t) ORDER BY id) FROM d2.journal t))::text");}
 @Test void thirdAttemptCannotSealAnotherCheckpoint()throws Exception{var first=commit();next(first);var second=commit();next(second);reject("23514",()->prepared());balance("10","7","6","3");}
 @Test void proofAddedAfterPublicationInvalidatesClaimReadset()throws Exception{var cp=commit();authorize(cp);replan();try(var c=f.owner()){sql(c,"INSERT INTO d4.multi_proofs SELECT ?,delivery_id,request_id,proof,evaluation FROM d4.multi_proofs LIMIT 1",id());reject("40001",()->value(c,"SELECT d4.dispatch_continuation(?,?::jsonb)::text",id(),Json.write(Map.of("action","CLAIM","plan_id",f.plan,"operation_id",f.operation,"resource_id",f.resource,"worker_id",f.worker))));assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));}balance("0","4","0","1");}
 @Test void secondAccountCapacityDeficitCannotPartiallyTopUp()throws Exception{var cp=commit();authorize(cp);replan();try(var c=f.owner()){value(c,"SELECT d2.recalibrate(?,?::jsonb)::text",id(),Json.write(Map.of("account_id",b,"capacity",9,"confidence",1,"evidence_sha256","d".repeat(64),"reason","Synthetic capacity deficit")));var ex=assertThrows(SQLException.class,()->value(c,"SELECT d4.dispatch_continuation(?,?::jsonb)::text",id(),Json.write(Map.of("action","CLAIM","plan_id",f.plan,"operation_id",f.operation,"resource_id",f.resource,"worker_id",f.worker))));assertTrue(Set.of("23514","40001").contains(ex.getSQLState()));assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("0",value(c,"SELECT count(*) FROM d4.multi_links"));}balance("0","4","0","1");}

 @Test void missingLeaseCannotCommitAStoredProof()throws Exception{var p=prepared();try(var c=f.owner()){sql(c,"DELETE FROM operation_leases");reject("23514",()->call(c,"multi_commit",id(),p[0],p[1],version(c)));assertEquals("0",value(c,"SELECT count(*) FROM d4.multi_checkpoints"));}balance("10","0","6","0");}
 @Test void correctedJournalCannotAuthorizeAnOldCheckpointVector()throws Exception{var cp=commit();try(var c=f.owner()){
  var original=UUID.fromString(value(c,"SELECT id FROM d2.commands WHERE request->>'action'='CONSUME' LIMIT 1"));var reservation=UUID.fromString(value(c,"SELECT id FROM d2.reservations"));
  value(c,"SELECT d2.capacity(?,?::jsonb)::text",id(),Json.write(Map.of("action","ADJUST","reservation_id",reservation,"corrects_command_id",original,"entries",List.of(Map.of("account_id",f.account,"consumed",0),Map.of("account_id",b,"consumed",-1)),"reason","Synthetic legitimate correction invalidates old checkpoint basis")));
  reject("23514",()->call(c,"multi_authorize",id(),cp,version(c),"stale journal"));assertEquals("0",value(c,"SELECT count(*) FROM d4.multi_authorizations"));
 }balance("0","4","0","0");}
 @Test void precisionBeyondD2JournalIsRejectedBeforeFirstClaim()throws Exception{try(var c=f.owner()){
  String m=value(c,"SELECT jsonb_set(?::jsonb,ARRAY['steps','0','cost',?::text],'0.00001')::text",manifest,f.account);String context="{\"fixture\":\"PARTIAL\",\"step_manifest\":"+m+"}";
  UUID op=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) SELECT task_id,'CODE',?,encode(digest(?,'sha256'),'hex'),'synthetic-new','{\"interruptible\":true}'::jsonb FROM operations WHERE id=?",id().toString(),context,f.operation);
  sql(c,"INSERT INTO d4.lab_intents VALUES(?,convert_to(?,'UTF8'),10)",op,context);reject("23514",()->sql(c,"INSERT INTO d4.multi_intents VALUES(?,?::jsonb,encode(digest((?::jsonb)::text,'sha256'),'hex'))",op,m,m));
  assertEquals("0",value(c,"SELECT count(*) FROM execution_attempts WHERE operation_id=?",op));
 }}
 @Test void proofReplayLookupRejectsAnotherDeliveryOrRequest()throws Exception{var p=prepared();try(var c=f.owner()){
  assertEquals("null",call(c,"multi_proof_status",id(),delivery,p[0]));reject("23514",()->call(c,"multi_proof_status",p[1],id(),p[0]));reject("23514",()->call(c,"multi_proof_status",p[1],delivery,id()));
 }}

 @Test void initialCaptureMustIncludeV2Intention()throws Exception{try(var c=f.owner()){
  sql(c,"INSERT INTO d4.multi_intents VALUES(?,?::jsonb,encode(digest((?::jsonb)::text,'sha256'),'hex'))",f.operation,manifest,manifest);
  reject("40001",()->value(c,"SELECT d4.dispatch_continuation(?,?::jsonb)::text",id(),Json.write(Map.of("action","CLAIM","plan_id",f.plan,"operation_id",f.operation,"resource_id",f.resource,"worker_id",f.worker))));
  assertEquals("0",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations"));
 }replan();launch();balance("10","0","6","0");}

}
