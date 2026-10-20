// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;

/** Historical V24 fault reproduction. A green test means BUG REPRODUCED,
 * not acceptance of V24 or proof that the boundary is safe. */
class V24BoundaryReproductionTest {
 MultiCheckpointStoreTest fixture;
 @BeforeEach void setup(TestInfo info)throws Exception{fixture=new MultiCheckpointStoreTest();fixture.setup(info);}
 @AfterEach void cleanup()throws Exception{if(fixture!=null)fixture.cleanup();}
 @Test void historicalV24AdmitsNumericStepId()throws Exception{
  try(var c=fixture.f.owner()){String manifest=value(c,"SELECT jsonb_set(?::jsonb,'{steps,0,id}','7')::text",fixture.manifest);UUID op=BoundaryFixture.newIntention(c,fixture,manifest);BoundaryFixture.insertIntention(c,op,manifest);assertEquals("1",value(c,"SELECT count(*) FROM d4.multi_intents WHERE operation_id=?",op));}
 }
 @Test void historicalV24CanExpireWhileWaitingForAccountLock()throws Exception{
  var result=BoundaryFixture.expireInsideCommit(fixture);assertNull(result.error());assertEquals("CANCELLED",result.state());fixture.balance("0","4","0","1");
 }
}
final class BoundaryFixture {
 record Result(SQLException error,String state){}
 static UUID newIntention(Connection c,MultiCheckpointStoreTest f,String manifest)throws Exception{
  String context="{\"fixture\":\"PARTIAL\",\"step_manifest\":"+manifest+"}";
  var op=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) SELECT task_id,'CODE',?,encode(digest(?,'sha256'),'hex'),'synthetic-boundary','{\"interruptible\":true}'::jsonb FROM operations WHERE id=?",id().toString(),context,f.f.operation);
  sql(c,"INSERT INTO d4.lab_intents VALUES(?,convert_to(?,'UTF8'),10)",op,context);return op;
 }
 static void insertIntention(Connection c,UUID op,String manifest)throws Exception{sql(c,"INSERT INTO d4.multi_intents VALUES(?,?::jsonb,encode(digest((?::jsonb)::text,'sha256'),'hex'))",op,manifest,manifest);}
 static Result expireInsideCommit(MultiCheckpointStoreTest f)throws Exception{
  var prepared=f.prepared();long version;String application="boundary_"+id().toString().replace("-","");
  try(var observer=f.f.owner();var locker=f.f.owner();var pool=Executors.newSingleThreadExecutor()){
   version=f.version(observer);locker.setAutoCommit(false);sql(locker,"SELECT id FROM d2.accounts ORDER BY id FOR UPDATE");
   sql(observer,"UPDATE operation_leases SET expires_at=clock_timestamp()+interval '2 seconds'");
   var future=pool.submit(()->{try(var c=f.f.owner()){sql(c,"SET statement_timeout=8000");value(c,"SELECT set_config('application_name',?,false)",application);f.call(c,"multi_commit",id(),prepared[0],prepared[1],version);return (SQLException)null;}catch(SQLException ex){return ex;}});
   long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(4);boolean blocked=false;
   while(System.nanoTime()<end){if("true".equals(value(observer,"SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE application_name=? AND wait_event_type='Lock')::text",application))){blocked=true;break;}Thread.sleep(20);}
   try{assertTrue(blocked,"Commit must actually reach the account lock before expiry");sql(observer,"SELECT pg_sleep(least(3,greatest(0,extract(epoch FROM (expires_at-clock_timestamp()))+0.05))) FROM operation_leases");}
   finally{locker.commit();}
   var error=future.get(10,TimeUnit.SECONDS);return new Result(error,value(observer,"SELECT state FROM operations WHERE id=?",f.f.operation));
  }
 }
}
