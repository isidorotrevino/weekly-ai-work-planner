// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;

/** V22->V23 preserves live execution; retirement is a bound read, never release. */
class PollingStoreTest {
 LabBridgeTest bridge;DeliveryStoreTest f;UUID delivery;
 @BeforeEach void setup()throws Exception {
  bridge=new LabBridgeTest();bridge.setup();bridge.upgrade();f=bridge.f;delivery=bridge.delivery;
  assertEquals(4,migrations(f.db,"22").migrate().migrationsExecuted);
  String before;try(var c=f.owner()){before=facts(c);}
  assertEquals(1,migrations(f.db,"23").migrate().migrationsExecuted);migrations(f.db,"23").validate();assertEquals(0,migrations(f.db,"23").migrate().migrationsExecuted);
  try(var c=f.owner()){assertEquals(before,facts(c));}
 }
 @AfterEach void cleanup()throws Exception {if(bridge!=null)bridge.cleanup();}
 String facts(Connection c)throws SQLException {return value(c,"SELECT jsonb_build_array((SELECT jsonb_agg(to_jsonb(x)) FROM execution_attempts x),(SELECT jsonb_agg(to_jsonb(x)) FROM operation_leases x),(SELECT jsonb_agg(to_jsonb(x)) FROM d2.journal x))::text");}
 String status(Connection c,UUID worker,UUID d)throws SQLException {return value(c,"SELECT d4.worker_execution_status(?,?)::text",worker,d);}
 String retirable(Connection c)throws SQLException {return value(c,"SELECT d4.worker_execution_status(?,?)->>'retirable'",f.worker,delivery);}
 void callback(Connection c)throws SQLException {f.call(c,"worker_execution",id(),f.worker,Map.of("action","CALLBACK","delivery_id",delivery,"payload",Map.of("entries",List.of(Map.of("account_id",f.account,"settled",10,"consumed",8)))));}
 void complete(Connection c)throws SQLException {
  callback(c);var proof=Json.write(Map.of("context_hash",value(c,"SELECT context_pack_sha256 FROM operations WHERE id=?",f.operation),"process_stopped",true,"artifact_valid",true,"receiver_closed",true));var pid=id();
  value(c,"SELECT d4.lab_record_evidence(?,?,'APPLIED',true,?::jsonb)::text",pid,delivery,proof);
  value(c,"SELECT d4.lab_admin(?,?,'VERIFY',?)::text",id(),delivery,pid);
 }
 @Test void runningAndConfirmedCallbackAreNotRetirable()throws Exception {
  try(var c=f.owner()){assertEquals("false",retirable(c));callback(c);assertEquals("VERIFYING",value(c,"SELECT state FROM operations"));assertEquals("false",retirable(c));assertEquals("1",value(c,"SELECT count(*) FROM operation_leases"));}
 }
 @Test void acceptedClosedCompletedExecutionCanBeReadWithoutMutations()throws Exception {
  try(var c=f.owner()){complete(c);var before=facts(c);assertEquals("true",retirable(c));var response=status(c,f.worker,delivery);assertEquals(f.worker.toString(),value(c,"SELECT ?::jsonb->>'worker'",response));assertEquals(value(c,"SELECT id::text FROM execution_attempts"),value(c,"SELECT ?::jsonb->>'attempt'",response));assertEquals("1",value(c,"SELECT ?::jsonb->>'generation'",response));assertEquals(before,facts(c));assertEquals("0",value(c,"SELECT outstanding::int::text FROM d2.reservation_balances"));}
 }
 @Test void foreignWorkerUnknownDeliveryAndPublicAreDenied()throws Exception {
  try(var c=f.owner()){
   f.rejected("42501",()->status(c,f.other,delivery));f.rejected("42501",()->status(c,f.worker,id()));
   var role="poll_status_"+id().toString().replace("-","");sql(c,"CREATE ROLE "+role+";GRANT "+role+" TO CURRENT_USER;GRANT USAGE ON SCHEMA d4 TO "+role+";SET ROLE "+role);
   f.rejected("42501",()->status(c,f.worker,delivery));sql(c,"RESET ROLE;DROP OWNED BY "+role+";DROP ROLE "+role);
  }
 }
 @Test void unknownAfterCompletionCannotRetire()throws Exception {
  try(var c=f.owner()){complete(c);sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(?,1,'unexpected','UNKNOWN','synthetic')",f.operation);assertEquals("false",retirable(c));}
 }
 @Test void contradictoryReceiptAfterCompletionCannotRetire()throws Exception {
  try(var c=f.owner()){complete(c);sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) SELECT operation_id,generation,effect_key,'ABSENT','synthetic-contradiction' FROM d2.effect_receipts LIMIT 1");assertEquals("false",retirable(c));}
 }
 @Test void sealedContinuationRetiresOnlyTheVerifiedSuccessor(TestInfo test)throws Exception {
  var cp=new CheckpointStoreTest();cp.setup(test);
  try{
   assertEquals(2,migrations(cp.f.db,"23").migrate().migrationsExecuted);cp.resumedPlan();
   try(var c=cp.f.owner()){
    var next=id();cp.f.call(c,"deliver_continuation",next,cp.f.worker,cp.f.request());cp.f.call(c,"ack",id(),cp.f.worker,Map.of("action","ACK","delivery_id",next));cp.f.call(c,"worker_execution",id(),cp.f.worker,Map.of("action","START","delivery_id",next));
    cp.f.call(c,"worker_execution",id(),cp.f.worker,Map.of("action","CALLBACK","delivery_id",next,"payload",Map.of("entries",List.of(Map.of("account_id",cp.f.account,"settled",10,"consumed",6)))));
    var proof=value(c,"SELECT jsonb_build_object('attempt',info->'attempt','generation',info->'generation','context_hash',info->'context_hash','manifest_hash',info->'manifest_hash','process_stopped',true,'artifact_valid',true,'receiver_closed',true,'steps','{\"step-1\":\"APPLIED\",\"step-2\":\"APPLIED\"}'::jsonb)::text FROM (SELECT d4.i5_inspect(?) info) x",next);
    value(c,"SELECT d4.record_continuation_acceptance(?,?,?::jsonb)::text",id(),next,proof);value(c,"SELECT d4.finalize_continuation(?,?)::text",id(),next);
    assertEquals("true",value(c,"SELECT d4.worker_execution_status(?,?)->>'retirable'",cp.f.worker,next));assertEquals("false",value(c,"SELECT d4.worker_execution_status(?,?)->>'retirable'",cp.f.worker,cp.delivery));
   }
  }finally{cp.cleanup();}
 }
 @Test void changedGenerationAndRevokedCatalogCannotRetireOldDelivery()throws Exception {
  try(var c=f.owner()){complete(c);sql(c,"UPDATE operations SET lease_generation=lease_generation+1 WHERE id=?",f.operation);assertEquals("false",retirable(c));sql(c,"UPDATE d4.worker_catalog SET enabled=false WHERE worker_id=?",f.worker);f.rejected("42501",()->status(c,f.worker,delivery));}
 }
 @Test void acceptancePassWithoutBoundClosedProofIsNotEnough()throws Exception {
  try(var c=f.owner()){
   callback(c);var artifact=insert(c,"INSERT INTO artifacts(artifact_ref,sha256,media_type,byte_size) VALUES(?,repeat('b',64),'application/json',2)",id().toString());
   sql(c,"INSERT INTO execution_evidence(attempt_id,artifact_id,evidence_type) SELECT id,?,'ACCEPTANCE_PASS' FROM execution_attempts",artifact);
   var info=value(c,"SELECT jsonb_build_object('action','VERIFY','operation_id',o.id,'attempt_id',a.id,'worker_id',a.worker_id,'resource_id',a.resource_id,'generation',o.lease_generation)::text FROM operations o JOIN execution_attempts a ON a.operation_id=o.id");
   value(c,"SELECT d3.execution(?,?::jsonb)::text",id(),info);assertEquals("COMPLETED",value(c,"SELECT state FROM operations"));assertEquals("false",retirable(c));
  }
 }
}
