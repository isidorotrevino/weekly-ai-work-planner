// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;

/** V21->V22 live upgrade and authenticated read-only checkpoint signal. */
class LongRunningStoreTest {
 CheckpointStoreTest fixture;
 @BeforeEach void setup(TestInfo test)throws Exception {
  fixture=new CheckpointStoreTest();fixture.setup(test);
  String before;try(var c=fixture.f.owner()){before=unchanged(c);}
  assertEquals(1,migrations(fixture.f.db,"22").migrate().migrationsExecuted);
  migrations(fixture.f.db,"22").validate();assertEquals(0,migrations(fixture.f.db,"22").migrate().migrationsExecuted);
  try(var c=fixture.f.owner()){assertEquals(before,unchanged(c));}
 }
 @AfterEach void cleanup()throws Exception {if(fixture!=null)fixture.cleanup();}
 String unchanged(Connection c)throws Exception {return value(c,"SELECT jsonb_build_array((SELECT jsonb_agg(to_jsonb(x)) FROM execution_attempts x),(SELECT jsonb_agg(to_jsonb(x)) FROM operation_leases x),(SELECT jsonb_agg(to_jsonb(x)) FROM d2.journal x))::text");}
 String signal(Connection c,UUID worker,UUID delivery)throws SQLException {return value(c,"SELECT d4.worker_checkpoint_signal(?,?)::text",worker,delivery);}
 @Test void liveSignalIsReadOnlyAndBindsExactRequestAndIdentity()throws Exception {
  try(var c=fixture.f.owner()){
   var initial=signal(c,fixture.f.worker,fixture.delivery);
   assertEquals("null",value(c,"SELECT (?::jsonb->'request_id')::text",initial));
   fixture.prepare();var before=unchanged(c);var result=signal(c,fixture.f.worker,fixture.delivery);
   assertEquals(fixture.request.toString(),value(c,"SELECT ?::jsonb->>'request_id'",result));
   assertEquals(fixture.f.worker.toString(),value(c,"SELECT ?::jsonb->>'worker'",result));
   assertEquals(value(c,"SELECT attempt_id::text FROM operation_leases"),value(c,"SELECT ?::jsonb->>'attempt'",result));
   assertEquals(before,unchanged(c));
  }
 }
 @Test void foreignWorkerAndUnknownDeliveryCannotReadSignal()throws Exception {
  try(var c=fixture.f.owner()){
   fixture.rejected("42501",()->signal(c,fixture.f.worker,id()));
   fixture.rejected("42501",()->signal(c,fixture.f.other,fixture.delivery));
  }
 }
 @Test void expiredOrSealedExecutionCannotObtainSignal()throws Exception {
  fixture.commit();try(var c=fixture.f.owner()){fixture.rejected("23514",()->signal(c,fixture.f.worker,fixture.delivery));}
 }
 @Test void expiryRetainsCommitmentAndDeniesSignal()throws Exception {
  fixture.prepare();try(var c=fixture.f.owner()){sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second'");fixture.rejected("23514",()->signal(c,fixture.f.worker,fixture.delivery));}
  fixture.balance("10","0","60");
 }
 @Test void publicCannotReadRequestsOrInvokeSignal()throws Exception {
  try(var c=fixture.f.owner()){
   sql(c,"CREATE ROLE signal_reader;GRANT signal_reader TO CURRENT_USER;GRANT USAGE ON SCHEMA d4 TO signal_reader");
   sql(c,"SET ROLE signal_reader");
   fixture.rejected("42501",()->signal(c,fixture.f.worker,fixture.delivery));
   fixture.rejected("42501",()->value(c,"SELECT count(*) FROM d4.checkpoint_requests"));
   sql(c,"RESET ROLE");sql(c,"DROP OWNED BY signal_reader;DROP ROLE signal_reader");
  }
 }
}
