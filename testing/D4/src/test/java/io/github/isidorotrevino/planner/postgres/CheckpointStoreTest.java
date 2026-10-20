// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;

/** Additive live sealed checkpoint, fixed two-step calibrated SQL fixture. */
class CheckpointStoreTest {
 DeliveryStoreTest f;UUID delivery,request,proof;long version;
 final String manifest="{\"schema\":\"d4.steps.v1\",\"steps\":[{\"id\":\"step-1\",\"units\":4},{\"id\":\"step-2\",\"units\":6}]}";
 @BeforeEach void setup(TestInfo test)throws Exception {
  f=new DeliveryStoreTest();f.db="d4_checkpoint_"+id().toString().replace("-","");
  try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+f.db);}
  assertEquals(21,migrations(f.db,"21").migrate().migrationsExecuted);migrations(f.db,"21").validate();assertEquals(0,migrations(f.db,"21").migrate().migrationsExecuted);
  try(var c=f.owner()){
   f.fixture(c,true);String method=test.getTestMethod().orElseThrow().getName();String initialPolicy="{\"interruptible\":"+!method.equals("noninterruptibleRequestDefersWithoutSettlement")+",\"max_attempts\":"+(method.equals("attemptLimitIsNotResetByCheckpoint")?1:3)+"}";String context="{\"fixture\":\"PARTIAL\",\"step_manifest\":"+manifest+"}";
   sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||?::jsonb,context_pack_sha256=encode(digest(?,'sha256'),'hex') WHERE id=?",initialPolicy,context,f.operation);
   sql(c,"INSERT INTO d4.lab_intents VALUES(?,convert_to(?,'UTF8'),10)",f.operation,context);
   sql(c,"INSERT INTO d4.step_intents VALUES(?,?::jsonb,encode(digest((?::jsonb)::text,'sha256'),'hex'))",f.operation,manifest,manifest);
   var captured=STORE.capture(c,id());var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(captured.request(),captured.snapshot());f.plan=STORE.publish(c,id(),id(),captured,result);
   delivery=id();f.call(c,"deliver",delivery,f.worker,f.request());f.call(c,"ack",id(),f.worker,Map.of("action","ACK","delivery_id",delivery));f.call(c,"worker_execution",id(),f.worker,Map.of("action","START","delivery_id",delivery));
   version=Long.parseLong(value(c,"SELECT row_version FROM operations WHERE id=?",f.operation));
  }
 }
 @AfterEach void cleanup()throws Exception{if(f!=null)f.cleanup();}
 String call(Connection c,String name,Object...args)throws SQLException {
  String placeholders=String.join(",",Collections.nCopies(args.length,"?"));return value(c,"SELECT d4."+name+"("+placeholders+")::text",args);
 }
 void prepare()throws Exception {
  try(var c=f.owner()){
   request=id();call(c,"checkpoint_request",request,delivery,version);
   var info=value(c,"SELECT d4.lab_inspect(?)::text",delivery);var props=new Properties();
   String p=value(c,"SELECT jsonb_build_object('schema','d4.checkpoint.proof.v1','manifest_hash',i.manifest_hash,'context_hash',o.context_pack_sha256,'policy_hash',encode(digest(o.policy_snapshot::text,'sha256'),'hex'),'attempt',l.attempt_id,'generation',l.fencing_generation,'process_stopped',true,'artifact_valid',true,'receiver_closed',true,'close_sequence',3,'steps','{\"step-1\":\"APPLIED\",\"step-2\":\"ABSENT\"}'::jsonb,'consumed_units',4)::text FROM operations o JOIN operation_leases l ON l.operation_id=o.id JOIN d4.step_intents i ON i.operation_id=o.id WHERE o.id=?",f.operation);
   proof=id();value(c,"SELECT d4.record_checkpoint_proof(?,?,?::jsonb)::text",proof,request,p);
  }
 }
 UUID commit()throws Exception {prepare();var cid=id();try(var c=f.owner()){call(c,"commit_checkpoint",cid,request,proof,version);}return cid;}
 void rejected(String state,DeliveryStoreTest.SQLAction action){var e=assertThrows(SQLException.class,action::run);assertEquals(state,e.getSQLState(),e.getMessage());}
 void balance(String pending,String consumed,String available)throws Exception {try(var c=f.owner()){assertEquals(pending,value(c,"SELECT outstanding::int::text FROM d2.reservation_balances"));assertEquals(consumed,value(c,"SELECT consumed::int::text FROM d2.reservation_balances"));assertEquals(available,value(c,"SELECT available::int::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",f.account));}}
 @Test void commitSettlesPartialThenReleasesRemainderIdempotently()throws Exception{
  var cp=commit();balance("0","4","66");try(var c=f.owner()){
   assertEquals(call(c,"commit_checkpoint",cp,request,proof,version),call(c,"commit_checkpoint",cp,request,proof,version));
   assertEquals("CANCELLED",value(c,"SELECT state FROM operations"));assertEquals("0",value(c,"SELECT count(*) FROM operation_leases"));assertEquals("1",value(c,"SELECT count(*) FROM d4.checkpoints"));assertEquals("0",value(c,"SELECT count(*) FROM execution_evidence"));
   rejected("23514",()->call(c,"commit_checkpoint",id(),request,proof,version));
  }balance("0","4","66");
 }
 @Test void authorizePreservesReservationCounterAndDoesNotClaim()throws Exception{
  var cp=commit();try(var c=f.owner()){
   var cid=id();assertEquals(call(c,"authorize_continuation",cid,cp,version+1,"explicit synthetic continuation"),call(c,"authorize_continuation",cid,cp,version+1,"explicit synthetic continuation"));
   assertEquals("READY",value(c,"SELECT state FROM operations"));assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("true",value(c,"SELECT d4.continuation_safe(?,1)::text",f.operation));
   rejected("23514",()->call(c,"authorize_continuation",id(),cp,version+1,"second"));
  }balance("0","4","66");
 }
 @Test void leaseExpiresBeforeCommitRollsBackAllSettlement()throws Exception{
  prepare();try(var c=f.owner()){sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second'");rejected("23514",()->call(c,"commit_checkpoint",id(),request,proof,version));assertEquals("0",value(c,"SELECT count(*) FROM d4.checkpoints"));assertEquals("RUNNING",value(c,"SELECT state FROM operations"));}balance("10","0","60");
 }
 @Test void wrongVersionAndProofCannotCommit()throws Exception{
  prepare();try(var c=f.owner()){rejected("23514",()->call(c,"commit_checkpoint",id(),request,proof,version+1));rejected("P0002",()->call(c,"commit_checkpoint",id(),request,id(),version));}balance("10","0","60");
 }
 @Test void unknownOrUnexpectedAppliedPreservesExclusion()throws Exception{
  prepare();try(var c=f.owner()){sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(?,1,'unexpected','APPLIED','synthetic')",f.operation);rejected("23514",()->call(c,"commit_checkpoint",id(),request,proof,version));assertEquals("1",value(c,"SELECT count(*) FROM operation_leases"));}balance("10","0","60");
 }
 @Test void genericCancelCannotAcquireCheckpointProvenance()throws Exception{
  try(var c=f.owner()){rejected("P0002",()->call(c,"authorize_continuation",id(),id(),version,"generic cancel"));rejected("23514",()->value(c,"SELECT d2.transition(?,?::jsonb)::text",id(),Json.write(Map.of("entity_type","OPERATION","entity_id",f.operation,"expected_version",version,"to","READY","from","RUNNING","actor","CONTROL_PLANE","reason","synthetic generic transition"))));}balance("10","0","60");
 }
 @Test void concurrentCommitsProduceOneSettlement()throws Exception{
  prepare();var cid=id();try(var pool=Executors.newFixedThreadPool(2)){
   Callable<String> action=()->{try(var c=f.owner()){return call(c,"commit_checkpoint",cid,request,proof,version);}};
   var values=pool.invokeAll(List.of(action,action));assertEquals(values.get(0).get(),values.get(1).get());
  }balance("0","4","66");
 }
 UUID authorize(UUID cp)throws Exception {var cid=id();try(var c=f.owner()){call(c,"authorize_continuation",cid,cp,version+1,"explicit fixture continuation");}return cid;}
 UUID resumedPlan()throws Exception {
  var cp=commit();authorize(cp);var adapter=new ContinuationPlanningStore();
  try(var c=f.owner()){
   adapter.observeEligibility(c,id());var captured=adapter.capture(c,id());
   assertFalse(STORE.read(c,captured.id()).snapshot().operations().getFirst().retrySafe());assertTrue(captured.snapshot().operations().getFirst().retrySafe());
   var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(captured.request(),captured.snapshot());
   assertEquals(io.github.isidorotrevino.planner.scheduler.PlanningModel.Disposition.TENTATIVE,result.decisions().getFirst().disposition());
   rejected("23514",()->STORE.publish(c,id(),id(),STORE.read(c,captured.id()),result));
   f.plan=adapter.publish(c,id(),id(),captured,result);return cp;
  }
 }
 @Test void qualifiedPlanningAndClaimCreateOneNewGenerationWithOriginalTopUp()throws Exception {
  var cp=resumedPlan();try(var c=f.owner()){
   var req=Json.write(Map.of("action","CLAIM","plan_id",f.plan,"operation_id",f.operation,"resource_id",f.resource,"worker_id",f.worker));
   rejected("23514",()->value(c,"SELECT d3.dispatch(?,?::jsonb)::text",id(),req));var cid=id();
   assertEquals(value(c,"SELECT d4.dispatch_continuation(?,?::jsonb)::text",cid,req),value(c,"SELECT d4.dispatch_continuation(?,?::jsonb)::text",cid,req));
   assertEquals("2",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("2",value(c,"SELECT lease_generation FROM operations"));assertEquals("1",value(c,"SELECT count(*) FROM d4.continuation_links WHERE checkpoint_id=?",cp));
  }balance("10","4","56");
 }
 @Test void newProofBetweenCaptureAndPublishInvalidatesCas()throws Exception {
  var cp=commit();authorize(cp);var adapter=new ContinuationPlanningStore();try(var c=f.owner()){
   adapter.observeEligibility(c,id());var captured=adapter.capture(c,id());var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(captured.request(),captured.snapshot());
   sql(c,"INSERT INTO d4.checkpoint_proofs SELECT ?,request_id,proof FROM d4.checkpoint_proofs LIMIT 1",id());
   rejected("40001",()->adapter.publish(c,id(),id(),captured,result));
  }balance("0","4","66");
 }
 @Test void unknownAfterAuthorizationBlocksClaimAndPreservesCounter()throws Exception {
  resumedPlan();try(var c=f.owner()){
   sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(?,1,'late-unknown','UNKNOWN','synthetic')",f.operation);
   rejected("23514",()->value(c,"SELECT d4.dispatch_continuation(?,?::jsonb)::text",id(),Json.write(Map.of("action","CLAIM","plan_id",f.plan,"operation_id",f.operation,"resource_id",f.resource,"worker_id",f.worker))));assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));
  }balance("0","4","66");
 }
 @Test void sixAvailableCannotFinanceConservativeTopUpTen()throws Exception {
  resumedPlan();try(var c=f.owner()){
   var task=insert(c,"INSERT INTO tasks(project_id,task_key,title) SELECT project_id,?,'buffer' FROM tasks WHERE id=(SELECT task_id FROM operations WHERE id=?)",id().toString(),f.operation);
   var buffer=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref) VALUES(?,'CODE',?,repeat('b',64),'synthetic')",task,id().toString());
   sql(c,"INSERT INTO d2.operation_accounts VALUES(?,?,60,'fixture')",buffer,f.account);
   value(c,"SELECT d2.capacity(?,?::jsonb)::text",id(),Json.write(Map.of("action","RESERVE","operation_id",buffer,"pool","PLANNED","reason","synthetic competing capacity")));
   assertEquals("6",value(c,"SELECT available::int::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",f.account));
   rejected("40001",()->value(c,"SELECT d4.dispatch_continuation(?,?::jsonb)::text",id(),Json.write(Map.of("action","CLAIM","plan_id",f.plan,"operation_id",f.operation,"resource_id",f.resource,"worker_id",f.worker))));assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));
  }
 }
 @Test void intentCannotBeRetrofittedAfterFirstClaim()throws Exception {try(var c=f.owner()){rejected("23514",()->sql(c,"INSERT INTO d4.step_intents VALUES(?,?::jsonb,encode(digest((?::jsonb)::text,'sha256'),'hex'))",f.operation,manifest,manifest));}}
 @Test void missingStepOrLiveProcessProofCannotFreeCapacity()throws Exception {
  prepare();try(var c=f.owner()){
   var bad=value(c,"SELECT (proof||'{\"process_stopped\":false}')::text FROM d4.checkpoint_proofs LIMIT 1");rejected("23514",()->value(c,"SELECT d4.record_checkpoint_proof(?,?,?::jsonb)::text",id(),request,bad));
   var missing=value(c,"SELECT (proof||'{\"steps\":{\"step-1\":\"APPLIED\"}}')::text FROM d4.checkpoint_proofs LIMIT 1");rejected("23514",()->value(c,"SELECT d4.record_checkpoint_proof(?,?,?::jsonb)::text",id(),request,missing));
  }balance("10","0","60");
 }
 @Test void contextPolicyChangedSinceStartCannotCommitCheckpoint()throws Exception {
  prepare();try(var c=f.owner()){sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||'{\"changed\":true}' WHERE id=?",f.operation);rejected("23514",()->call(c,"commit_checkpoint",id(),request,proof,version));}balance("10","0","60");
 }

 @Test void v18ActiveLeaseUpgradePreservesIdentityAndLedger()throws Exception {
  var legacy=new DeliveryStoreTest();legacy.db="d4_upgrade_"+id().toString().replace("-","");try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+legacy.db);}
  try{
   assertEquals(18,migrations(legacy.db,"18").migrate().migrationsExecuted);
   String before;try(var c=legacy.owner()){
    legacy.fixture(c,true);var d=id();legacy.call(c,"deliver",d,legacy.worker,legacy.request());legacy.call(c,"ack",id(),legacy.worker,Map.of("action","ACK","delivery_id",d));legacy.call(c,"worker_execution",id(),legacy.worker,Map.of("action","START","delivery_id",d));
    before=value(c,"SELECT jsonb_build_array((SELECT jsonb_agg(to_jsonb(x)) FROM execution_attempts x),(SELECT jsonb_agg(to_jsonb(x)) FROM operation_leases x),(SELECT jsonb_agg(to_jsonb(x)) FROM d2.journal x))::text");
   }
   assertEquals(3,migrations(legacy.db,"21").migrate().migrationsExecuted);migrations(legacy.db,"21").validate();
   try(var c=legacy.owner()){assertEquals(before,value(c,"SELECT jsonb_build_array((SELECT jsonb_agg(to_jsonb(x)) FROM execution_attempts x),(SELECT jsonb_agg(to_jsonb(x)) FROM operation_leases x),(SELECT jsonb_agg(to_jsonb(x)) FROM d2.journal x))::text"));}
  }finally{legacy.cleanup();}
 }
 @Test void genericTransitionStillCannotResumeCheckpointCancellation()throws Exception {
  commit();try(var c=f.owner()){
   rejected("23514",()->value(c,"SELECT d2.transition(?,?::jsonb)::text",id(),Json.write(Map.of("entity_type","OPERATION","entity_id",f.operation,"from","CANCELLED","to","READY","expected_version",version+1,"actor","CONTROL_PLANE","reason","generic bypass"))));
   assertEquals("CANCELLED",value(c,"SELECT state FROM operations"));
  }
 }
 @Test void unknownBeforeCommitRetainsLeaseAndCommitment()throws Exception {
  prepare();try(var c=f.owner()){sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(?,1,'unknown','UNKNOWN','synthetic')",f.operation);rejected("23514",()->call(c,"commit_checkpoint",id(),request,proof,version));assertEquals("1",value(c,"SELECT count(*) FROM operation_leases"));}balance("10","0","60");
 }
 @Test void ordinaryCancellationWithoutProofCannotBeAuthorized()throws Exception {
  try(var c=f.owner()){
   sql(c,"UPDATE operations SET state='CANCELLED',row_version=row_version+1 WHERE id=?",f.operation);
   rejected("P0002",()->call(c,"authorize_continuation",id(),id(),version+1,"ordinary cancellation"));assertEquals("0",value(c,"SELECT count(*) FROM d4.continuation_authorizations"));
  }
 }

 @Test void attemptLimitIsNotResetByCheckpoint()throws Exception {
  var cp=commit();try(var c=f.owner()){rejected("23514",()->call(c,"authorize_continuation",id(),cp,version+1,"limit must hold"));assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("CANCELLED",value(c,"SELECT state FROM operations"));}balance("0","4","66");
 }
 @Test void noninterruptibleRequestDefersWithoutSettlement()throws Exception {
  try(var c=f.owner()){var cid=id();assertTrue(call(c,"checkpoint_request",cid,delivery,version).contains("DEFERRED_NONINTERRUPTIBLE"));assertEquals("0",value(c,"SELECT count(*) FROM d4.checkpoint_requests"));assertEquals("RUNNING",value(c,"SELECT state FROM operations"));}balance("10","0","60");
 }
 @Test void controlRoleCannotMintCheckpointOrFinalEvidence()throws Exception {
  prepare();try(var c=f.owner()){
   String role="d4_control_"+id().toString().replace("-","");sql(c,"CREATE ROLE "+role+" NOLOGIN;GRANT USAGE ON SCHEMA d4 TO "+role+";GRANT EXECUTE ON FUNCTION d4.commit_checkpoint(uuid,uuid,uuid,bigint) TO "+role+";SET ROLE "+role);
   rejected("42501",()->value(c,"SELECT d4.record_checkpoint_proof(?,?,'{}')::text",id(),request));rejected("42501",()->value(c,"SELECT d4.record_continuation_acceptance(?,?,'{}')::text",id(),delivery));
   rejected("42501",()->value(c,"SELECT count(*) FROM d4.checkpoint_proofs"));
  }
 }

 @Test void unexpectedAppliedAfterAuthorizationCannotBeIgnored()throws Exception {
  resumedPlan();try(var c=f.owner()){
   sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(?,1,'unexpected-late','APPLIED','synthetic')",f.operation);
   assertEquals("false",value(c,"SELECT d4.continuation_safe(?,1)::text",f.operation));
   rejected("23514",()->value(c,"SELECT d4.dispatch_continuation(?,?::jsonb)::text",id(),Json.write(Map.of("action","CLAIM","plan_id",f.plan,"operation_id",f.operation,"resource_id",f.resource,"worker_id",f.worker))));
  }balance("0","4","66");
 }

}
