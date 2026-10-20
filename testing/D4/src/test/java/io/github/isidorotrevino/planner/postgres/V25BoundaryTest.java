// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;

/** Additive correction of reproduced V24 boundaries, not new lifecycle authority. */
class V25BoundaryTest {
 MultiCheckpointStoreTest f;UUID sealed,legacy;String role;
 @BeforeEach void setup(TestInfo info)throws Exception{
  f=new MultiCheckpointStoreTest();f.setup(info);role="boundary_caller_"+id().toString().replace("-","");
  if(info.getTestMethod().orElseThrow().getName().equals("upgradeWithSealedV24HeadCompletesSameOperation"))sealed=f.commit();
  if(info.getTestMethod().orElseThrow().getName().equals("legacyNumericIntentionIsPreservedButCannotEnterClaim"))try(var c=f.f.owner()){String m=value(c,"SELECT jsonb_set(?::jsonb,'{steps,0,id}','7')::text",f.manifest);legacy=BoundaryFixture.newIntention(c,f,m);BoundaryFixture.insertIntention(c,legacy,m);}
  if(info.getTestMethod().orElseThrow().getName().equals("legacyExtraIntentionIsPreservedButCannotEnterClaim"))try(var c=f.f.owner()){String m=value(c,"SELECT (?::jsonb||'{\"note\":\"legacy\"}'::jsonb)::text",f.manifest);legacy=BoundaryFixture.newIntention(c,f,m);BoundaryFixture.insertIntention(c,legacy,m);}
  String before;try(var c=f.f.owner()){
   before=f.state(c);sql(c,"CREATE ROLE "+role+" NOLOGIN;GRANT USAGE ON SCHEMA d4 TO "+role+";GRANT EXECUTE ON FUNCTION d4.multi_commit(uuid,uuid,uuid,bigint) TO "+role);
  }
  assertEquals(1,migrations(f.f.db,"25").migrate().migrationsExecuted);migrations(f.f.db,"25").validate();assertEquals(0,migrations(f.f.db,"25").migrate().migrationsExecuted);
  try(var c=f.f.owner()){assertEquals(before,f.state(c),"Upgrade must not mutate operation/lease/attempt/journal");}
 }
 @AfterEach void cleanup()throws Exception{if(f!=null)f.cleanup();}
 void rejectManifest(String expression)throws Exception{try(var c=f.f.owner()){String manifest=value(c,"SELECT ("+expression+")::text",f.manifest);UUID op=BoundaryFixture.newIntention(c,f,manifest);f.reject("23514",()->BoundaryFixture.insertIntention(c,op,manifest));assertEquals("0",value(c,"SELECT count(*) FROM d4.multi_intents WHERE operation_id=?",op));assertEquals("0",value(c,"SELECT count(*) FROM execution_attempts WHERE operation_id=?",op));}}
 @Test void numericStepIdCannotFreeze(){assertDoesNotThrow(()->rejectManifest("jsonb_set(?::jsonb,'{steps,0,id}','7')"));}
 @Test void numericHashCannotFreeze(){assertDoesNotThrow(()->rejectManifest("jsonb_set(?::jsonb,'{steps,0,effect_hash}',to_jsonb(repeat('1',64)::numeric))"));}
 @Test void extraManifestMetadataCannotFreeze()throws Exception{rejectManifest("?::jsonb||'{\"note\":\"synthetic metadata\"}'::jsonb");}
 @Test void extraStepMetadataCannotFreeze()throws Exception{rejectManifest("jsonb_set(?::jsonb,'{steps,0,note}','\"metadata\"')");}
 @Test void missingStepIdCannotFreeze()throws Exception{rejectManifest("?::jsonb#-'{steps,0,id}'");}
 @Test void textualCostCannotFreeze()throws Exception{rejectManifest("jsonb_set(?::jsonb,ARRAY['steps','0','cost','"+f.f.account+"'],'\"4\"')");}
 @Test void extraAccountMetadataCannotFreeze()throws Exception{rejectManifest("jsonb_set(?::jsonb,ARRAY['accounts','"+f.b+"','note'],'\"metadata\"')");}
 @Test void validTypedManifestStillFreezesBeforeClaim()throws Exception{try(var c=f.f.owner()){UUID op=BoundaryFixture.newIntention(c,f,f.manifest);BoundaryFixture.insertIntention(c,op,f.manifest);assertEquals("1",value(c,"SELECT count(*) FROM d4.multi_intents WHERE operation_id=?",op));}}
 @Test void expiryInsideSettlementRollsBackAllEffectsAndRetainsCommitment()throws Exception{
  var result=BoundaryFixture.expireInsideCommit(f);assertNotNull(result.error());assertEquals("23514",result.error().getSQLState());assertEquals("RUNNING",result.state());f.balance("10","0","6","0");
  try(var c=f.f.owner()){assertEquals("1",value(c,"SELECT count(*) FROM d4.multi_proofs"));assertEquals("0",value(c,"SELECT count(*) FROM d4.multi_checkpoints"));assertEquals("1",value(c,"SELECT count(*) FROM operation_leases WHERE expires_at<clock_timestamp()"));assertEquals("0",value(c,"SELECT count(*) FROM d4.checkpoint_commands WHERE request->>'action'='MULTI_COMMIT'"));assertEquals("0",value(c,"SELECT count(*) FROM outbox_events WHERE event_type='D4_MULTI_CHECKPOINT_COMMITTED'"));}
 }
 @Test void serviceGrantMovesToGuardedWrapperAndOldAliasIsPrivate()throws Exception{
  var p=f.prepared();try(var c=f.f.owner()){
   long version=f.version(c);assertEquals("true",value(c,"SELECT has_function_privilege(?, 'd4.multi_commit(uuid,uuid,uuid,bigint)','EXECUTE')::text",role));assertEquals("false",value(c,"SELECT has_function_privilege(?, 'd4.multi_commit_before_v25(uuid,uuid,uuid,bigint)','EXECUTE')::text",role));
   sql(c,"SET ROLE "+role);f.reject("42501",()->f.call(c,"multi_commit_before_v25",id(),p[0],p[1],version));assertTrue(f.call(c,"multi_commit",id(),p[0],p[1],version).contains("CANCELLED"));
  }f.balance("0","4","0","1");
 }
 @Test void committedCommandReplaysWithoutLeaseAndRejectsChangedBody()throws Exception{
  var cp=f.commit();try(var c=f.f.owner()){
   String request=value(c,"SELECT request_id FROM d4.multi_proofs WHERE id=(SELECT proof_id FROM d4.multi_checkpoints WHERE id=?)",cp);UUID pid=UUID.fromString(value(c,"SELECT proof_id FROM d4.multi_checkpoints WHERE id=?",cp));long version=f.version(c)-1;
   assertEquals("0",value(c,"SELECT count(*) FROM operation_leases"));assertEquals(f.call(c,"multi_commit",cp,UUID.fromString(request),pid,version),f.call(c,"multi_commit",cp,UUID.fromString(request),pid,version));f.reject("23514",()->f.call(c,"multi_commit",cp,UUID.fromString(request),pid,version+1));
  }f.balance("0","4","0","1");
 }
 @Test void upgradeWithSealedV24HeadCompletesSameOperation()throws Exception{
  f.next(sealed);var next=f.commit();f.next(next);f.callback();try(var c=f.f.owner()){
   value(c,"SELECT d4.multi_accept(?,?,?::jsonb)::text",id(),f.delivery,f.proof(c,true));f.call(c,"multi_finalize",id(),f.delivery);assertEquals("COMPLETED",value(c,"SELECT state FROM operations"));assertEquals("3",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("2",value(c,"SELECT count(*) FROM d4.multi_checkpoints"));
  }f.balance("0","10","0","6");
 }

 @Test void legacyNumericIntentionIsPreservedButCannotEnterClaim()throws Exception{try(var c=f.f.owner()){
  assertEquals("1",value(c,"SELECT count(*) FROM d4.multi_intents WHERE operation_id=?",legacy));assertEquals("false",value(c,"SELECT d4.multi_manifest_typed(manifest)::text FROM d4.multi_intents WHERE operation_id=?",legacy));
  var ex=assertThrows(SQLException.class,()->value(c,"SELECT d4.dispatch_continuation(?,?::jsonb)::text",id(),Json.write(Map.of("action","CLAIM","plan_id",f.f.plan,"operation_id",legacy,"resource_id",f.f.resource,"worker_id",f.f.worker))));assertEquals("23514",ex.getSQLState());assertTrue(ex.getMessage().contains("Typed compatible"));assertEquals("0",value(c,"SELECT count(*) FROM execution_attempts WHERE operation_id=?",legacy));
 }}

 @Test void legacyExtraIntentionIsPreservedButCannotEnterClaim()throws Exception{legacyNumericIntentionIsPreservedButCannotEnterClaim();}
 @Test void legacyRunningExtraIntentionCannotRenewGrant()throws Exception{legacyRunningNumericIntentionCannotRenewGrant();}
 @Test void legacyRunningNumericIntentionCannotRenewGrant()throws Exception{try(var c=f.f.owner()){
  assertEquals("false",value(c,"SELECT d4.multi_inspect(?)->>'manifest_compatible'",f.delivery));String before=f.state(c);
  f.reject("23514",()->f.call(c,"lab_authorize",id(),f.f.worker,f.delivery,id()));assertEquals(before,f.state(c));assertEquals("0",value(c,"SELECT count(*) FROM d4.lab_grants"));
 }}

}
