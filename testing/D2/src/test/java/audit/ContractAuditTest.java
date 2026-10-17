package audit;

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
import static org.junit.jupiter.api.Assertions.*;
import static audit.SchemaAuditTest.*;

/** Executable D2 contracts, confined to a disposable database and synthetic effects. */
class ContractAuditTest {
 static final String DB="d2_contract";
 @BeforeAll static void migrate() throws Exception {
  var fw=Flyway.configure().dataSource(URL+DB,"d2_auditor","").cleanDisabled(true)
   .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed")).load();
  fw.migrate();fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
  try(var c=open(DB)){
   sql(c,"DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='d2_runtime') THEN CREATE ROLE d2_runtime NOLOGIN; END IF; END $$; GRANT USAGE ON SCHEMA public,d2 TO d2_runtime; GRANT EXECUTE ON FUNCTION d2.capacity_command(uuid,jsonb),d2.execution(uuid,jsonb),d2.transition(uuid,jsonb),d2.preempt(uuid,jsonb),d2.sync_source(uuid,jsonb),d2.ack_outbox(uuid,jsonb) TO d2_runtime");
  }
 }
 static String id(){return UUID.randomUUID().toString();}
 static String call(Connection c,String fn,String cid,String request) throws SQLException {return value(c,"SELECT d2."+fn+"("+q(cid)+"::uuid,"+q(request)+"::jsonb)::text");}
 static String account(Connection c,F f,String kind,int capacity) throws SQLException {
  return insert(c,"d2.accounts","resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,initial_capacity",q(f.r())+",'execution','OPERATIONS',"+q(kind)+","+q(id())+",now()-interval '1 hour',now()+interval '7 days','SYNTHETIC',"+capacity);
 }
 record Setup(F f,String a){}
 static Setup setup(Connection c,int capacity) throws SQLException {
  F f=fixture(c);sql(c,"UPDATE workers SET state='ONLINE' WHERE id="+q(f.w()));
  String a=account(c,f,"WEEKLY",capacity);bind(c,f.o(),a,10);return new Setup(f,a);
 }
 static void bind(Connection c,String op,String a,int units) throws SQLException {sql(c,"INSERT INTO d2.operation_accounts VALUES("+q(op)+","+q(a)+","+units+",'audit-calibration-v1')");}
 static String reserve(F f){return "{\"action\":\"RESERVE\",\"operation_id\":\""+f.o()+"\",\"pool\":\"PLANNED\",\"reason\":\"audit\"}";}
 static String entry(String a,int settled,int consumed){return "[{\"account_id\":\""+a+"\",\"settled\":"+settled+",\"consumed\":"+consumed+"}]";}
 static String consumption(String action,String res,String entries){return "{\"action\":\""+action+"\",\"reservation_id\":\""+res+"\",\"reason\":\"audit\",\"entries\":"+entries+"}";}
 static String exec(F f,String action){return "{\"action\":\""+action+"\",\"operation_id\":\""+f.o()+"\",\"worker_id\":\""+f.w()+"\",\"resource_id\":\""+f.r()+"\"}";}
 static String execFenced(Connection c,F f,String action) throws SQLException {
  String aid=value(c,"SELECT attempt_id FROM operation_leases WHERE operation_id="+q(f.o()));
  String gen=value(c,"SELECT lease_generation FROM operations WHERE id="+q(f.o()));
  return exec(f,action).replace("}",",\"attempt_id\":\""+aid+"\",\"generation\":"+gen+"}");
 }
 static void rejected(Connection c,String state,SqlAction action) throws Exception {
  Savepoint sp=c.setSavepoint();try{SQLException e=assertThrows(SQLException.class,action::run);assertEquals(state,e.getSQLState(),e.toString());}finally{c.rollback(sp);}
 }
 interface SqlAction{void run() throws Exception;}
 interface Scenario{void run(Connection c,Setup s) throws Exception;}
 record Case(String name,Scenario action){}
 static String balance(Connection c,String a,String field) throws SQLException {return value(c,"SELECT ("+field+")::numeric(18,4)::text FROM d2.balances WHERE account_id="+q(a)+" AND pool='PLANNED'");}
 @TestFactory Stream<DynamicTest> capacityContracts(){
  return List.of(
   new Case("reserve_replay_and_conflict",(c,s)->{String cmd=id(),r=reserve(s.f());String a=call(c,"capacity",cmd,r);assertEquals(a,call(c,"capacity",cmd,r));assertEquals("10.0000",balance(c,s.a(),"outstanding"));rejected(c,"23505",()->call(c,"capacity",cmd,r.replace("audit","different")));}),
   new Case("overrun_is_evidence_not_rejected",(c,s)->{String r=id();call(c,"capacity",r,reserve(s.f()));call(c,"capacity",id(),consumption("CONSUME",r,entry(s.a(),10,90)));assertEquals("0.0000",balance(c,s.a(),"outstanding"));assertEquals("90.0000",balance(c,s.a(),"consumed"));assertTrue(Double.parseDouble(balance(c,s.a(),"available"))<0);}),
   new Case("release_preserves_consumption",(c,s)->{String r=id();call(c,"capacity",r,reserve(s.f()));call(c,"capacity",id(),consumption("CONSUME",r,entry(s.a(),4,3)));call(c,"capacity",id(),consumption("RELEASE",r,entry(s.a(),6,0)));assertEquals("0.0000",balance(c,s.a(),"outstanding"));assertEquals("3.0000",balance(c,s.a(),"consumed"));}),
   new Case("provisional_correction_is_delta",(c,s)->{String r=id(),first=id();call(c,"capacity",r,reserve(s.f()));call(c,"capacity",first,consumption("CONSUME",r,entry(s.a(),10,8)));String correction=consumption("ADJUST",r,entry(s.a(),0,4)).replace("}","}");correction=correction.substring(0,correction.length()-1)+",\"corrects_command_id\":\""+first+"\"}";call(c,"capacity",id(),correction);assertEquals("12.0000",balance(c,s.a(),"consumed"));}),
   new Case("unknown_quota_blocks",(c,s)->{String a=account(c,s.f(),"SESSION",100);sql(c,"ALTER TABLE d2.accounts DISABLE TRIGGER immutable_fact; UPDATE d2.accounts SET initial_capacity=NULL WHERE id="+q(a)+"; ALTER TABLE d2.accounts ENABLE TRIGGER immutable_fact");bind(c,s.f().o(),a,1);rejected(c,"23514",()->call(c,"capacity",id(),reserve(s.f())));assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations WHERE operation_id="+q(s.f().o())));}),
   new Case("all_windows_atomic",(c,s)->{String a=account(c,s.f(),"SESSION",1);bind(c,s.f().o(),a,10);rejected(c,"23514",()->call(c,"capacity",id(),reserve(s.f())));assertEquals("0.0000",balance(c,s.a(),"outstanding"));}),
   new Case("same_kind_overlap_rejected",(c,s)->rejected(c,"23P01",()->account(c,s.f(),"WEEKLY",100))),
   new Case("mapping_frozen_after_reserve",(c,s)->{call(c,"capacity",id(),reserve(s.f()));rejected(c,"55000",()->sql(c,"DELETE FROM d2.operation_accounts WHERE operation_id="+q(s.f().o())));}),
   new Case("replan_reuses_reservation",(c,s)->{String r=id();call(c,"capacity",r,reserve(s.f()));String next=insert(c,"planning_runs","horizon_start,horizon_end,trigger_type,config_snapshot,config_sha256,solver_version","now(),now()+interval '7 days','AUDIT','{}',repeat('a',64),'audit'");sql(c,"INSERT INTO d2.plan_reservations VALUES("+q(s.f().run())+","+q(r)+"),("+q(next)+","+q(r)+")");assertEquals("10.0000",balance(c,s.a(),"outstanding"));rejected(c,"23505",()->call(c,"capacity",id(),reserve(s.f())));}),
   new Case("borrow_return_conserve_limit",(c,s)->{sql(c,"UPDATE operations SET policy_snapshot='{\"interruptible\":true,\"checkpoint_verified\":true}' WHERE id="+q(s.f().o()));String loan=id();call(c,"capacity",loan,"{\"action\":\"BORROW\",\"operation_id\":\""+s.f().o()+"\",\"account_id\":\""+s.a()+"\",\"units\":10,\"reason\":\"audit\"}");assertEquals("80.0000",balance(c,s.a(),"effective_limit"));call(c,"capacity",id(),"{\"action\":\"RETURN\",\"loan_id\":\""+loan+"\",\"units\":10,\"reason\":\"audit\"}");assertEquals("70.0000",balance(c,s.a(),"effective_limit"));rejected(c,"23514",()->call(c,"capacity",id(),"{\"action\":\"RETURN\",\"loan_id\":\""+loan+"\",\"units\":1,\"reason\":\"audit\"}"));}),
   new Case("noncheckpointable_borrow_rejected",(c,s)->rejected(c,"23514",()->call(c,"capacity",id(),"{\"action\":\"BORROW\",\"operation_id\":\""+s.f().o()+"\",\"account_id\":\""+s.a()+"\",\"units\":1,\"reason\":\"audit\"}"))),
   new Case("runtime_cannot_edit_ledger_or_adjust",(c,s)->{sql(c,"SET LOCAL ROLE d2_runtime");rejected(c,"42501",()->sql(c,"DELETE FROM d2.journal"));rejected(c,"42501",()->call(c,"capacity_command",id(),"{\"action\":\"ADJUST\"}"));call(c,"capacity_command",id(),reserve(s.f()));})
  ).stream().map(x->DynamicTest.dynamicTest(x.name(),()->{try(var c=open(DB)){c.setAutoCommit(false);try{x.action().run(c,setup(c,100));}finally{c.rollback();}}}));
 }
 @TestFactory Stream<DynamicTest> executionContracts(){
  return List.of(
   new Case("claim_has_attempt_lease_reservation_history",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));assertEquals("1",value(c,"SELECT count(*) FROM operation_leases WHERE operation_id="+q(s.f().o())));assertEquals("10.0000",balance(c,s.a(),"outstanding"));assertEquals("1",value(c,"SELECT count(*) FROM state_transition_events WHERE entity_id="+q(s.f().o())));}),
   new Case("stale_fencing_rejected",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));String req=execFenced(c,s.f(),"START");rejected(c,"23514",()->call(c,"execution",id(),req.replace("\"generation\":2","\"generation\":1")));}),
   new Case("callback_replay_consumes_once",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));call(c,"execution",id(),execFenced(c,s.f(),"START"));String r=execFenced(c,s.f(),"CALLBACK");r=r.substring(0,r.length()-1)+",\"entries\":"+entry(s.a(),10,12)+"}";String cmd=id();String first=call(c,"execution",cmd,r);assertEquals(first,call(c,"execution",cmd,r));assertEquals("12.0000",balance(c,s.a(),"consumed"));}),
   new Case("expiry_reconciles_without_releasing",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second' WHERE operation_id="+q(s.f().o()));call(c,"execution",id(),exec(s.f(),"EXPIRE"));assertEquals("RECONCILING",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));assertEquals("10.0000",balance(c,s.a(),"outstanding"));rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));}),
   new Case("ambiguous_effect_not_retried",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second' WHERE operation_id="+q(s.f().o()));call(c,"execution",id(),exec(s.f(),"EXPIRE"));String receipt=insert(c,"d2.effect_receipts","operation_id,generation,effect_key,status,evidence_ref",q(s.f().o())+",2,'audit','UNKNOWN','synthetic-inspection'");String req=exec(s.f(),"RECONCILE");call(c,"execution",id(),req.substring(0,req.length()-1)+",\"receipt_id\":\""+receipt+"\"}");assertEquals("BLOCKED_APPROVAL",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));assertEquals("10.0000",balance(c,s.a(),"outstanding"));}),
   new Case("approval_missing_blocks_claim",(c,s)->{sql(c,"UPDATE operations SET policy_snapshot='{\"requires_approval\":true}' WHERE id="+q(s.f().o()));rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));assertEquals("0.0000",balance(c,s.a(),"outstanding"));})
  ).stream().map(x->DynamicTest.dynamicTest(x.name(),()->{try(var c=open(DB)){c.setAutoCommit(false);try{x.action().run(c,setup(c,100));}finally{c.rollback();}}}));
 }
 @Test void twentyClaimsProduceOneCompleteClaim() throws Exception {
  Setup s;try(var c=open(DB)){s=setup(c,100);}
  var gate=new CountDownLatch(1);try(var pool=Executors.newFixedThreadPool(20)){
   List<Future<Boolean>> futures=new ArrayList<>();for(int i=0;i<20;i++)futures.add(pool.submit(()->{gate.await();try(var c=open(DB)){call(c,"execution",id(),exec(s.f(),"CLAIM"));return true;}catch(SQLException e){assertEquals("23514",e.getSQLState());return false;}}));
   gate.countDown();int ok=0;for(var f:futures)if(f.get(20,TimeUnit.SECONDS))ok++;assertEquals(1,ok);
  }
  try(var c=open(DB)){assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts WHERE operation_id="+q(s.f().o())+" AND lease_generation=2"));assertEquals("10.0000",balance(c,s.a(),"outstanding"));}
 }
 @Test void concurrentReservationsCannotOverbook() throws Exception {
  Setup s;String other;try(var c=open(DB)){s=setup(c,100);sql(c,"UPDATE d2.operation_accounts SET units=60 WHERE operation_id="+q(s.f().o()));other=insert(c,"operations","task_id,operation_type,idempotency_key",q(s.f().t())+",'AUDIT',"+q(id()));bind(c,other,s.a(),60);}
  var gate=new CountDownLatch(1);try(var pool=Executors.newFixedThreadPool(2)){
   List<Future<Boolean>> fs=new ArrayList<>();for(String op:List.of(s.f().o(),other))fs.add(pool.submit(()->{gate.await();try(var c=open(DB)){call(c,"capacity",id(),reserve(s.f()).replace(s.f().o(),op));return true;}catch(SQLException e){assertEquals("23514",e.getSQLState());return false;}}));gate.countDown();int ok=0;for(var f:fs)if(f.get(20,TimeUnit.SECONDS))ok++;assertEquals(1,ok);
  }
  try(var c=open(DB)){assertEquals("60.0000",balance(c,s.a(),"outstanding"));}
 }
}
