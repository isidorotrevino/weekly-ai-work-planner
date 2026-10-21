// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.util.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;
import static org.junit.jupiter.api.Assertions.*;
/** Owner-supplied structural proofs. Java/HTTPS proof provenance is separate. */
class TreeStoreTest {
 PresenceStoreTest p;DeliveryStoreTest f;UUID delivery;
 @BeforeEach void setup(TestInfo info)throws Exception{p=new PresenceStoreTest();p.setup();f=p.f;try(var c=f.owner()){
  boolean partial=info.getTestMethod().orElseThrow().getName().equals("nativeCheckpointSettlementRequiresTreeProofAndRollsBack");boolean absent=info.getTestMethod().orElseThrow().getName().equals("absenceOfTreePolicyDoesNotInvokeRecoveryFixtureRestrictions");String context=partial?"{\"fixture\":\"PARTIAL\",\"step_manifest\":"+new CheckpointStoreTest().manifest+"}":absent?"{\"fixture\":\"SURVIVOR\"}":"{\"fixture\":\"SUCCESS\"}";sql(c,"UPDATE operations SET context_pack_sha256=encode(digest(?,'sha256'),'hex') WHERE id=?",context,f.operation);sql(c,"INSERT INTO d4.lab_intents VALUES(?,convert_to(?,'UTF8'),?)",f.operation,context,partial?10:8);if(partial){sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||'{\"interruptible\":true}'::jsonb WHERE id=?",f.operation);sql(c,"INSERT INTO d4.step_intents VALUES(?,?::jsonb,encode(digest((?::jsonb)::text,'sha256'),'hex'))",f.operation,new CheckpointStoreTest().manifest,new CheckpointStoreTest().manifest);}
  var store=new ReviewPlanningStore();store.observeEligibility(c,id());var captured=store.capture(c,id());var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(captured.request(),captured.snapshot());f.plan=store.publish(c,id(),id(),captured,result);
  if(!absent)sql(c,"INSERT INTO d4.tree_requirements VALUES(?,'{}',repeat('f',64),false,'{}')",f.operation);
  delivery=id();f.call(c,"deliver_continuation",delivery,f.worker,f.request());f.call(c,"ack",id(),f.worker,Map.of("action","ACK","delivery_id",delivery));f.call(c,"worker_execution",id(),f.worker,Map.of("action","START","delivery_id",delivery));
 }}
 @AfterEach void cleanup()throws Exception{if(p!=null)p.cleanup();}
 UUID artifact(java.sql.Connection c)throws Exception{return insert(c,"INSERT INTO artifacts(artifact_ref,sha256,media_type,byte_size) VALUES(?,repeat('a',64),'application/json',1)",id().toString());}
 void pass(java.sql.Connection c)throws Exception{sql(c,"INSERT INTO execution_evidence(attempt_id,artifact_id,evidence_type) SELECT id,?,'ACCEPTANCE_PASS' FROM execution_attempts",artifact(c));}
 String proof(java.sql.Connection c)throws Exception{return value(c,"SELECT jsonb_build_object('schema','d4.tree.proof.v1','operation',a.operation_id,'attempt',a.id,'worker',a.worker_id,'resource',a.resource_id,'generation',a.lease_generation,'context_hash',o.context_pack_sha256,'policy_hash',encode(digest(o.policy_snapshot::text,'sha256'),'hex'),'process_stopped',true,'files_verified',true,'git_verified',true,'restoration',false,'manifest_hash',repeat('f',64),'host_observation_hash',repeat('a',64),'base_oid',repeat('b',40),'commit_oid',repeat('c',40))::text FROM execution_attempts a JOIN operations o ON o.id=a.operation_id");}
 @Test void passRequiresFreshBoundProofAndDoesNotAccount()throws Exception{try(var c=f.owner()){assertThrows(java.sql.SQLException.class,()->pass(c));value(c,"SELECT d4.tree_record(?,?,?::jsonb)::text",id(),delivery,proof(c));pass(c);assertEquals("1",value(c,"SELECT count(*) FROM execution_evidence"));assertEquals("10/0",value(c,"SELECT outstanding::int||'/'||consumed::int FROM d2.reservation_balances"));}}
 @Test void proofIsAppendOnlyIdempotentAndRejectsWrongBinding()throws Exception{try(var c=f.owner()){var pid=id();String proof=proof(c);String response=value(c,"SELECT d4.tree_record(?,?,?::jsonb)::text",pid,delivery,proof);assertEquals(response,value(c,"SELECT d4.tree_record(?,?,?::jsonb)::text",pid,delivery,proof));assertThrows(java.sql.SQLException.class,()->value(c,"SELECT d4.tree_record(?,?,jsonb_set(?::jsonb,'{generation}','2'))::text",id(),delivery,proof));assertThrows(java.sql.SQLException.class,()->sql(c,"DELETE FROM d4.tree_proofs"));assertThrows(java.sql.SQLException.class,()->sql(c,"INSERT INTO d4.tree_requirements VALUES(?,'{}',repeat('f',64),false,'{}')",f.operation));}}
 @Test void missingOidOrManifestMismatchCannotProduceProof()throws Exception{try(var c=f.owner()){String proof=proof(c);for(var field:List.of("base_oid","commit_oid","process_stopped","git_verified","files_verified","manifest_hash"))assertThrows(java.sql.SQLException.class,()->value(c,"SELECT d4.tree_record(?,?,?::jsonb-?)::text",id(),delivery,proof,field));assertEquals("0",value(c,"SELECT count(*) FROM d4.tree_proofs"));}}
 @Test void workerRoleCannotMintProof()throws Exception{try(var c=f.owner()){String role="tree_caller_"+id().toString().replace("-","");sql(c,"CREATE ROLE "+role+" NOLOGIN;GRANT USAGE ON SCHEMA d4 TO "+role+";SET ROLE "+role);var error=assertThrows(java.sql.SQLException.class,()->value(c,"SELECT d4.tree_record(?,?,?::jsonb)::text",id(),delivery,"{}"));assertEquals("42501",error.getSQLState());}}
 @Test void absenceOfTreePolicyDoesNotInvokeRecoveryFixtureRestrictions()throws Exception{try(var c=f.owner()){assertEquals("true",value(c,"SELECT (d4.tree_info(?)->'tree_requirement'='null'::jsonb)::text",delivery));assertEquals("1",value(c,"SELECT count(*) FROM operation_leases"));}}

 @Test void nativeCheckpointSettlementRequiresTreeProofAndRollsBack()throws Exception{
  var h=new CheckpointStoreTest();h.f=f;h.delivery=delivery;try(var c=f.owner()){h.version=Long.parseLong(value(c,"SELECT row_version FROM operations"));}h.prepare();
  try(var c=f.owner()){
   var error=assertThrows(java.sql.SQLException.class,()->h.call(c,"commit_checkpoint",id(),h.request,h.proof,h.version));assertEquals("23514",error.getSQLState());assertTrue(error.getMessage().contains("tree proof"));assertEquals("RUNNING",value(c,"SELECT state FROM operations"));assertEquals("10/0",value(c,"SELECT outstanding::int||'/'||consumed::int FROM d2.reservation_balances"));assertEquals("0",value(c,"SELECT count(*) FROM d4.checkpoints"));
   value(c,"SELECT d4.tree_record(?,?,?::jsonb)::text",id(),delivery,proof(c));h.call(c,"commit_checkpoint",id(),h.request,h.proof,h.version);assertEquals("CANCELLED",value(c,"SELECT state FROM operations"));assertEquals("0/4",value(c,"SELECT outstanding::int||'/'||consumed::int FROM d2.reservation_balances"));assertEquals("1",value(c,"SELECT count(*) FROM d4.checkpoints"));assertEquals("0",value(c,"SELECT count(*) FROM execution_evidence WHERE evidence_type='ACCEPTANCE_PASS'"));
  }
 }

}
