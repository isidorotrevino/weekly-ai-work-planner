// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;

/** Additive V17->V18 compatibility and evidence authority, separate from E2E. */
class LabBridgeTest {
 DeliveryStoreTest f;UUID delivery;
 @BeforeEach void setup() throws Exception {
  f=new DeliveryStoreTest();f.db="d4_bridge_"+id().toString().replace("-","");
  try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+f.db);}
  assertEquals(17,migrations(f.db,"17").migrate().migrationsExecuted);
  try(var c=f.owner()){
   f.fixture(c,true);
   sql(c,"UPDATE operations SET context_pack_sha256=encode(digest('{}','sha256'),'hex') WHERE id=?",f.operation);
   var capture=STORE.capture(c,id());var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(capture.request(),capture.snapshot());f.plan=STORE.publish(c,id(),id(),capture,result);
   delivery=id();f.call(c,"deliver",delivery,f.worker,f.request());
   f.call(c,"ack",id(),f.worker,Map.of("action","ACK","delivery_id",delivery));
   f.call(c,"worker_execution",id(),f.worker,Map.of("action","START","delivery_id",delivery));
  }
 }
 @AfterEach void cleanup() throws Exception {if(f!=null)f.cleanup();}
 void upgrade()throws Exception {
  assertEquals(1,migrations(f.db,"18").migrate().migrationsExecuted);
  migrations(f.db,"18").validate();assertEquals(0,migrations(f.db,"18").migrate().migrationsExecuted);
  try(var c=f.owner()){sql(c,"INSERT INTO d4.lab_intents VALUES(?,'{}'::bytea,8)",f.operation);}
 }
 @Test void upgradePreservesActiveIdentityReservationAndLedger()throws Exception {
  String before;try(var c=f.owner()){before=value(c,"SELECT jsonb_build_array((SELECT jsonb_agg(to_jsonb(x)) FROM execution_attempts x),(SELECT jsonb_agg(to_jsonb(x)) FROM operation_leases x),(SELECT jsonb_agg(to_jsonb(x)) FROM d2.reservations x),(SELECT jsonb_agg(to_jsonb(x)) FROM d2.journal x))::text");}
  upgrade();try(var c=f.owner()){
   assertEquals(before,value(c,"SELECT jsonb_build_array((SELECT jsonb_agg(to_jsonb(x)) FROM execution_attempts x),(SELECT jsonb_agg(to_jsonb(x)) FROM operation_leases x),(SELECT jsonb_agg(to_jsonb(x)) FROM d2.reservations x),(SELECT jsonb_agg(to_jsonb(x)) FROM d2.journal x))::text"));
   assertEquals("RUNNING",value(c,"SELECT d4.lab_inspect(?)->>'state'",delivery));
  }
 }
 @Test void signedGrantSourceIsLeaseBoundAndCommandIdempotent()throws Exception {
  upgrade();try(var c=f.owner()){
   var cid=id();var receiver=id();String q="SELECT d4.lab_authorize(?,?,?,?)::text";
   var first=value(c,q,cid,f.worker,delivery,receiver);assertEquals(first,value(c,q,cid,f.worker,delivery,receiver));
   assertEquals("1",value(c,"SELECT count(*) FROM d4.lab_grants"));
   var ex=assertThrows(SQLException.class,()->value(c,q,cid,f.worker,delivery,id()));assertEquals("23514",ex.getSQLState());
   ex=assertThrows(SQLException.class,()->value(c,q,id(),f.other,delivery,receiver));assertEquals("42501",ex.getSQLState());
  }
 }
 @Test void acceptanceRequiresBoundProcessArtifactAndAppliedFacts()throws Exception {
  upgrade();try(var c=f.owner()){
   String hash=value(c,"SELECT context_pack_sha256 FROM operations WHERE id=?",f.operation);
   String proof=Json.write(Map.of("context_hash",hash,"process_stopped",false,"artifact_valid",true,"receiver_closed",true));
   String q="SELECT d4.lab_record_evidence(?,?,?,true,?::jsonb)::text";
   var ex=assertThrows(SQLException.class,()->value(c,q,id(),delivery,"APPLIED",proof));assertEquals("23514",ex.getSQLState());
   assertEquals("0",value(c,"SELECT count(*) FROM execution_evidence"));
  }
 }
 @Test void unknownEvidenceIsAppendOnlyAndDoesNotSelfApprove()throws Exception {
  upgrade();try(var c=f.owner()){
   String hash=value(c,"SELECT context_pack_sha256 FROM operations WHERE id=?",f.operation);
   String proof=Json.write(Map.of("context_hash",hash,"process_stopped",false,"artifact_valid",false));
   String q="SELECT d4.lab_record_evidence(?,?,?,false,?::jsonb)::text";var cid=id();
   assertEquals(value(c,q,cid,delivery,"UNKNOWN",proof),value(c,q,cid,delivery,"UNKNOWN",proof));
   assertEquals("1",value(c,"SELECT count(*) FROM d2.effect_receipts WHERE status='UNKNOWN'"));
   assertEquals("0",value(c,"SELECT count(*) FROM execution_evidence"));
   var ex=assertThrows(SQLException.class,()->sql(c,"DELETE FROM d4.lab_evidence"));assertEquals("55000",ex.getSQLState());
  }
 }
 @Test void appliedProofCannotOverridePriorUnknown()throws Exception {
  upgrade();try(var c=f.owner()){
   String hash=value(c,"SELECT context_pack_sha256 FROM operations WHERE id=?",f.operation);
   var proof=Json.write(Map.of("context_hash",hash,"process_stopped",true,"artifact_valid",true,"receiver_closed",true));
   value(c,"SELECT d4.lab_record_evidence(?,?,'UNKNOWN',false,?::jsonb)::text",id(),delivery,proof);
   var ex=assertThrows(SQLException.class,()->value(c,"SELECT d4.lab_record_evidence(?,?,'APPLIED',true,?::jsonb)::text",id(),delivery,proof));assertEquals("23514",ex.getSQLState());
   assertEquals("0",value(c,"SELECT count(*) FROM execution_evidence"));
  }
 }
 @Test void unprivilegedRoleCannotMintEvidenceOrUseRawTables()throws Exception {
  upgrade();try(var c=f.owner()){
   String role="lab_bridge_"+id().toString().replace("-","");sql(c,"CREATE ROLE "+role+" NOLOGIN;GRANT USAGE ON SCHEMA d4 TO "+role+";SET ROLE "+role);
   var ex=assertThrows(SQLException.class,()->value(c,"SELECT d4.lab_record_evidence(?,?,'APPLIED',true,'{}')::text",id(),delivery));assertEquals("42501",ex.getSQLState());
   ex=assertThrows(SQLException.class,()->value(c,"SELECT count(*) FROM public.operations"));assertEquals("42501",ex.getSQLState());
  }
 }
}
