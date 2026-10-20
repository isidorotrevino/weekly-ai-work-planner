// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;
class AbsenceV1StoreTest {
 RecoveryV1StoreTest r;
 @AfterEach void cleanup()throws Exception{if(r!=null)r.cleanup();}
 @Test void v1PriorResolvedUnknownCannotBlockActualLaterCheckpoint(TestInfo info)throws Exception{
  r=new RecoveryV1StoreTest();r.setup(info);var f=r.f;assertEquals(1,migrations(f.f.db,"27").migrate().migrationsExecuted);
  try(var c=f.f.owner()){
   sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) SELECT id,1,id||'/'||context_pack_sha256||'/step-1','UNKNOWN','prior-absence' FROM operations");
   var p=value(c,"SELECT (jsonb_set(jsonb_set(?::jsonb,'{schema}','\"d4.absence.proof.v1\"'),'{receipts}',rr)||jsonb_build_object('receiver_seal',(?::jsonb->'receiver_seal')||jsonb_build_object('steps',rr)))::text FROM (SELECT jsonb_object_agg(key,value||jsonb_build_object('status','ABSENT','payloadHash',NULL)) rr FROM jsonb_each(?::jsonb->'receipts')) x",r.proof(false),r.proof(false),r.proof(false));
   var pid=id();value(c,"SELECT d4.absence_record(?,?,?::jsonb)::text",pid,f.delivery,p);var seal=id();f.call(c,"absence_settle",seal,pid,Long.parseLong(value(c,"SELECT row_version FROM operations")));f.call(c,"absence_authorize",id(),seal,Long.parseLong(value(c,"SELECT row_version FROM operations")),"Explicit v1 absence retry");
   var store=new AbsencePlanningStore();store.observeEligibility(c,id());var captured=store.capture(c,id());var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(captured.request(),captured.snapshot());f.f.plan=store.publish(c,id(),id(),captured,result);
   f.delivery=id();f.f.call(c,"deliver_continuation",f.delivery,f.f.worker,f.f.request());f.f.call(c,"ack",id(),f.f.worker,Map.of("action","ACK","delivery_id",f.delivery));f.f.call(c,"worker_execution",id(),f.f.worker,Map.of("action","START","delivery_id",f.delivery));f.version=Long.parseLong(value(c,"SELECT row_version FROM operations"));
  }
  f.commit();try(var c=f.f.owner()){assertEquals("CANCELLED",value(c,"SELECT state FROM operations"));assertEquals("0/4",value(c,"SELECT outstanding::int||'/'||consumed::int FROM d2.reservation_balances"));assertEquals("1",value(c,"SELECT count(*) FROM d2.effect_receipts WHERE status='UNKNOWN'"));assertEquals("2",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("1",value(c,"SELECT count(*) FROM d4.checkpoints"));}
 }
}
