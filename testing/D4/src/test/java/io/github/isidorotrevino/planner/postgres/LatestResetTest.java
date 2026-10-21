// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.util.*;
import java.time.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;
import static org.junit.jupiter.api.Assertions.*;
class LatestResetTest {
 PresenceStoreTest p;DeliveryStoreTest f;UUID delivery;
 @BeforeEach void setup()throws Exception{
  p=new PresenceStoreTest();p.setup();f=p.f;try(var c=f.owner()){
   sql(c,"UPDATE resources SET enabled=false WHERE id=?",f.resource);f.resource=insert(c,"INSERT INTO resources(resource_key,worker_id,provider,subscription,capabilities) VALUES(?,?,'SYNTHETIC','none','{\"tools\":{\"code\":true}}')",id().toString(),f.worker);
   f.account=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'execution','OPERATIONS','WEEKLY',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '68 seconds','SYNTHETIC',1,100)",f.resource,id().toString());var at=Instant.now();
   STORE.configure(c,id(),Map.of("action","CALENDAR","reason","Bounded reset fixture","resource_id",f.resource,"calendar_id",id(),"slots",List.of(Map.of("start",at.minusSeconds(3600),"end",at.plusSeconds(3600)))));
   STORE.configure(c,id(),Map.ofEntries(Map.entry("action","ESTIMATE"),Map.entry("reason","Near physical reset"),Map.entry("estimate_id",id()),Map.entry("operation_id",f.operation),Map.entry("resource_id",f.resource),Map.entry("units",Map.of(f.account,10)),Map.entry("duration_ms",1000),Map.entry("confidence",1),Map.entry("calibration_ref","fixture-v1"),Map.entry("provenance","SYNTHETIC"),Map.entry("observed_at",at.minusSeconds(1)),Map.entry("valid_until",at.plusSeconds(3600))));
   var store=new ReviewPlanningStore();store.observeEligibility(c,id());var captured=store.capture(c,id());var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(captured.request(),captured.snapshot());f.plan=store.publish(c,id(),id(),captured,result);delivery=id();f.call(c,"deliver_continuation",delivery,f.worker,f.request());f.call(c,"ack",id(),f.worker,Map.of("action","ACK","delivery_id",delivery));
  }
 }
 @AfterEach void cleanup()throws Exception{if(p!=null)p.cleanup();}
 void crossRenewalBoundary()throws Exception{try(var c=f.owner()){value(c,"SELECT pg_sleep(greatest(0,extract(epoch FROM (window_end-clock_timestamp()))-58))::text FROM d2.accounts WHERE id=?",f.account);}}
 @Test void startNearResetRequiresWholeLeaseAndRetainsReservation()throws Exception{crossRenewalBoundary();try(var c=f.owner()){assertThrows(java.sql.SQLException.class,()->f.call(c,"worker_execution",id(),f.worker,Map.of("action","START","delivery_id",delivery)));assertEquals("LEASED",value(c,"SELECT state FROM operations"));assertEquals("10",value(c,"SELECT outstanding::int FROM d2.reservation_balances"));assertEquals("1",value(c,"SELECT count(*) FROM operation_leases"));}}
 @Test void renewalCannotRollIntoAnotherWindowOrExtendLease()throws Exception{try(var c=f.owner()){f.call(c,"worker_execution",id(),f.worker,Map.of("action","START","delivery_id",delivery));}crossRenewalBoundary();try(var c=f.owner()){String lease=value(c,"SELECT expires_at FROM operation_leases");assertThrows(java.sql.SQLException.class,()->f.call(c,"worker_execution",id(),f.worker,Map.of("action","HEARTBEAT","delivery_id",delivery)));assertEquals(lease,value(c,"SELECT expires_at FROM operation_leases"));assertEquals("RUNNING",value(c,"SELECT state FROM operations"));assertEquals("10/0",value(c,"SELECT outstanding::int||'/'||consumed::int FROM d2.reservation_balances"));assertThrows(java.sql.SQLException.class,()->sql(c,"UPDATE d2.operation_accounts SET units=1 WHERE operation_id=?",f.operation));}}
}
