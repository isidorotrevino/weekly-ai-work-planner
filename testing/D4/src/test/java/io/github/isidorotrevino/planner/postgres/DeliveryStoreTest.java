// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import java.nio.file.*;
import java.sql.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;
import io.github.isidorotrevino.planner.scheduler.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;

/** Persistence/ownership only; no HTTP/process/provider assertions. */
class DeliveryStoreTest {
  static final Path ROOT=Path.of(System.getProperty("planner.root")).toAbsolutePath();
  static final String URL=System.getProperty("d4.url");
  static final PlanningStore STORE=new PlanningStore();
  static final String TEMPLATE="d4_delivery_template";
  String db;UUID operation,worker,other,resource,account,plan;
  static UUID id(){return UUID.randomUUID();}
  static Connection connect(String name) throws SQLException {
    return DriverManager.getConnection(URL+name,System.getenv("PGUSER"),System.getenv("PGPASSWORD"));
  }
  Connection owner() throws SQLException{return connect(db);}
  Connection runtime() throws SQLException{var c=owner();sql(c,"SET ROLE d4_delivery_test;SET statement_timeout=10000");return c;}
  static void bind(PreparedStatement p,Object...args) throws SQLException{
    for(int i=0;i<args.length;i++)p.setObject(i+1,args[i] instanceof Instant t?t.atOffset(ZoneOffset.UTC):args[i]);
  }
  static void sql(Connection c,String text,Object...args) throws SQLException{try(var p=c.prepareStatement(text)){bind(p,args);p.execute();}}
  static String value(Connection c,String text,Object...args) throws SQLException{try(var p=c.prepareStatement(text)){bind(p,args);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}}}
  static UUID insert(Connection c,String text,Object...args) throws SQLException{return UUID.fromString(value(c,text+" RETURNING id",args));}
  static Flyway migrations(String database,String target){
    var cfg=Flyway.configure().dataSource(URL+database,System.getenv("PGUSER"),System.getenv("PGPASSWORD"))
      .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),
        "filesystem:"+ROOT.resolve("migrations-d3-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-dispatch-proposed"),
        "filesystem:"+ROOT.resolve("migrations-d3-coordinator-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-review-proposed"),
        "filesystem:"+ROOT.resolve("migrations-d4-proposed"));
    cfg.target(target==null?"16":target);return cfg.load();
  }
  @BeforeAll static void template() throws Exception {
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+TEMPLATE);}
    var fw=migrations(TEMPLATE,null);assertEquals(16,fw.migrate().migrationsExecuted);fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
    try(var c=connect(TEMPLATE)) {
      sql(c,"CREATE ROLE d4_delivery_test NOLOGIN;GRANT USAGE ON SCHEMA d4 TO d4_delivery_test;GRANT EXECUTE ON FUNCTION d4.deliver(uuid,uuid,jsonb),d4.ack(uuid,uuid,jsonb),d4.current_assignment(uuid),d4.worker_execution(uuid,uuid,jsonb) TO d4_delivery_test");
    }
  }
  @BeforeEach void setup() throws Exception {
    db="d4_case_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+db+" TEMPLATE "+TEMPLATE);}
    try(var c=owner()){fixture(c,true);}
  }
  void fixture(Connection c,boolean catalog) throws Exception {
      var at=OffsetDateTime.parse(value(c,"SELECT to_char(clock_timestamp() AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.US')||'+00:00'")).toInstant();
      var project=insert(c,"INSERT INTO projects(code,name,workflow_type) VALUES(?,'Synthetic D4','GENTLE_AI')",id().toString());
      var task=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'fixture','Synthetic delivery')",project);
      worker=insert(c,"INSERT INTO workers(worker_key,host_name,state,last_heartbeat_at,capabilities) VALUES(?,'synthetic','ONLINE',clock_timestamp(),'{\"tools\":{\"code\":true}}')",id().toString());
      other=insert(c,"INSERT INTO workers(worker_key,host_name,state,last_heartbeat_at) VALUES(?,'synthetic','ONLINE',clock_timestamp())",id().toString());
      resource=insert(c,"INSERT INTO resources(resource_key,worker_id,provider,subscription,capabilities) VALUES(?,?,'SYNTHETIC','none','{\"tools\":{\"code\":true}}')",id().toString(),worker);
      operation=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) VALUES(?,'CODE',?,repeat('a',64),'synthetic-context','{\"required_capabilities\":{\"tools\":{\"code\":true}}}')",task,id().toString());
      account=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'execution','OPERATIONS','WEEKLY',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '10 days','SYNTHETIC',1,100)",resource,id().toString());
      if(catalog)sql(c,"INSERT INTO d4.worker_catalog(worker_id) VALUES(?),(?)",worker,other);
      STORE.configure(c,id(),Map.of("action","PROFILE","reason","Synthetic D4","epoch_id",id(),"calibration_epoch","fixture-v1","policy",Map.of("schema_version",SCHEMA_VERSION,"timezone","Europe/Madrid","max_operations",10,"max_edges",20,"max_candidates",20,"max_compute_ms",5000)));
      STORE.configure(c,id(),Map.of("action","CALENDAR","reason","Synthetic D4","resource_id",resource,"calendar_id",id(),"slots",List.of(Map.of("start",at.minusSeconds(3600),"end",at.plus(Duration.ofDays(10))))));
      STORE.configure(c,id(),Map.ofEntries(Map.entry("action","ESTIMATE"),Map.entry("reason","Synthetic D4"),Map.entry("estimate_id",id()),Map.entry("operation_id",operation),Map.entry("resource_id",resource),Map.entry("units",Map.of(account,10)),Map.entry("duration_ms",900000),Map.entry("confidence",1),Map.entry("calibration_ref","fixture-v1"),Map.entry("provenance","SYNTHETIC"),Map.entry("observed_at",at.minusSeconds(1)),Map.entry("valid_until",at.plus(Duration.ofDays(10)))));
      var captured=STORE.capture(c,id());var result=new CapacityScheduler().plan(captured.request(),captured.snapshot());
      assertEquals(Disposition.TENTATIVE,result.decisions().getFirst().disposition());
      plan=STORE.publish(c,id(),id(),captured,result);
  }
  @AfterEach void cleanup() throws Exception{if(db!=null)try(var c=connect("postgres")){sql(c,"DROP DATABASE "+db+" WITH (FORCE)");}}
  Map<String,Object> request(){return Map.of("action","DELIVER","plan_id",plan,"operation_id",operation,"resource_id",resource);}
  String call(Connection c,String fn,UUID cid,UUID principal,Map<String,?> req) throws SQLException {
    return value(c,"SELECT d4."+fn+"(?,?,?::jsonb)::text",cid,principal,Json.write(req));
  }
  UUID deliver() throws SQLException {var cid=id();try(var c=runtime()){call(c,"deliver",cid,worker,request());}return cid;}
  void rejected(String code,SQLAction action){var e=assertThrows(SQLException.class,action::run);assertEquals(code,e.getSQLState(),e.getMessage());}
  @FunctionalInterface interface SQLAction{void run() throws SQLException;}
  @Test void responseLostRecoveredUnderNewPollCommandWithoutAnotherClaim() throws Exception {
    UUID first=id();String response;
    try(var c=runtime()){
      response=call(c,"deliver",first,worker,request());
      assertEquals(response,call(c,"deliver",first,worker,request()));
      assertEquals(response,call(c,"deliver",id(),worker,request()));
      assertEquals("true",value(c,"SELECT (d4.current_assignment(?)->>'requires_start')",worker));
    }
    try(var c=owner()){
      assertEquals(first.toString(),value(c,"SELECT id FROM d4.deliveries"));
      assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));
      assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));
      assertEquals("1",value(c,"SELECT count(*) FROM d2.journal WHERE commitment_delta>0"));
      assertEquals("60.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
      assertEquals("20.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='INCIDENT'",account));
      assertEquals("10.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='UNCERTAINTY'",account));
    }
  }
  @Test void ackIsIdempotentWithoutStartingOrRenewingLease() throws Exception {
    var delivery=deliver();String expiry;
    try(var c=owner()){expiry=value(c,"SELECT expires_at::text FROM operation_leases");}
    try(var c=runtime()){
      var req=Map.of("action","ACK","delivery_id",delivery);var cid=id();
      assertEquals(call(c,"ack",cid,worker,req),call(c,"ack",cid,worker,req));call(c,"ack",id(),worker,req);
    }
    try(var c=owner()){
      assertEquals("1",value(c,"SELECT count(*) FROM d4.delivery_acks"));
      assertEquals("LEASED",value(c,"SELECT state FROM operations"));assertEquals(expiry,value(c,"SELECT expires_at::text FROM operation_leases"));
    }
  }
  @Test void changedPayloadOrPrincipalConflictsWithoutExposingReceipt() throws Exception {
    var cid=id();try(var c=runtime()){
      call(c,"deliver",cid,worker,request());var changed=new HashMap<String,Object>(request());changed.put("plan_id",id());
      rejected("23514",()->call(c,"deliver",cid,worker,changed));
      rejected("23514",()->call(c,"deliver",cid,other,request()));
    }
  }
  @Test void foreignWorkerCannotDeliverAckExecuteOrReadAssignment() throws Exception {
    var delivery=deliver();try(var c=runtime()){
      rejected("42501",()->call(c,"deliver",id(),other,request()));
      rejected("42501",()->call(c,"ack",id(),other,Map.of("action","ACK","delivery_id",delivery)));
      rejected("42501",()->call(c,"worker_execution",id(),other,Map.of("action","START","delivery_id",delivery)));
      assertEquals("null",value(c,"SELECT d4.current_assignment(?)::text",other));
    }
  }
  @Test void disabledIdentityCannotReplayOrRead() throws Exception {
    var delivery=deliver();try(var c=owner()){sql(c,"UPDATE d4.worker_catalog SET enabled=false WHERE worker_id=?",worker);}
    try(var c=runtime()){
      rejected("42501",()->call(c,"deliver",delivery,worker,request()));
      rejected("42501",()->value(c,"SELECT d4.current_assignment(?)",worker));
    }
  }
  @Test void lifecyclePreservesFencingAndRejectsVerifierActionsAndIdentityOverrides() throws Exception {
    var delivery=deliver();try(var c=runtime()){
      rejected("23514",()->call(c,"worker_execution",id(),worker,Map.of("action","VERIFY","delivery_id",delivery)));
      rejected("23514",()->call(c,"worker_execution",id(),worker,Map.of("action","START","delivery_id",delivery,"payload",Map.of("generation",999))));
      call(c,"worker_execution",id(),worker,Map.of("action","START","delivery_id",delivery));
      call(c,"worker_execution",id(),worker,Map.of("action","HEARTBEAT","delivery_id",delivery));
    }
    try(var c=owner()){assertEquals("RUNNING",value(c,"SELECT state FROM operations"));assertEquals("1",value(c,"SELECT lease_generation FROM operations"));}
  }
  @Test void expiredStartReceiptDoesNotRenewAndNewStartIsRejected() throws Exception {
    var delivery=deliver();var cid=id();var req=Map.of("action","START","delivery_id",delivery);String response;
    try(var c=runtime()){response=call(c,"worker_execution",cid,worker,req);}
    // Persistence-only fixture. Real lease expiration is required in E2E D4-S04.
    try(var c=owner()){sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second'");}
    try(var c=runtime()){
      assertEquals(response,call(c,"worker_execution",cid,worker,req));
      assertEquals("true",value(c,"SELECT d4.current_assignment(?)->>'lease_expired'",worker));
      rejected("23514",()->call(c,"worker_execution",id(),worker,req));
    }
    try(var c=owner()){assertEquals("true",value(c,"SELECT (expires_at<clock_timestamp())::text FROM operation_leases"));assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));}
  }
  @Test void runtimeHasNoDirectSQLAccountingEvidenceOrD3Bypass() throws Exception {
    try(var c=runtime()){
      for(var query:List.of("SELECT * FROM d4.commands","SELECT * FROM workers","UPDATE d4.worker_catalog SET enabled=true","INSERT INTO d2.effect_receipts(operation_id) VALUES(NULL)","SELECT d3.dispatch(NULL,NULL)","SELECT d2.execution(NULL,NULL)","SELECT d4.require_worker(NULL)"))
        rejected("42501",()->sql(c,query));
    }
  }
  @Test void factualCallbackReplayConsumesOnlyOnceAndCannotVerify() throws Exception {
    var delivery=deliver();var cid=id();var req=Map.of("action","CALLBACK","delivery_id",delivery,
      "payload",Map.of("entries",List.of(Map.of("account_id",account,"settled",10,"consumed",8))));
    try(var c=runtime()){
      call(c,"worker_execution",id(),worker,Map.of("action","START","delivery_id",delivery));
      assertEquals(call(c,"worker_execution",cid,worker,req),call(c,"worker_execution",cid,worker,req));
      rejected("23514",()->call(c,"worker_execution",id(),worker,req));
      rejected("23514",()->call(c,"worker_execution",id(),worker,Map.of("action","VERIFY","delivery_id",delivery)));
    }
    try(var c=owner()){
      assertEquals("VERIFYING",value(c,"SELECT state FROM operations"));
      assertEquals("0",value(c,"SELECT count(*) FROM execution_evidence"));
      assertEquals("62.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
      assertEquals("8.0000",value(c,"SELECT consumed::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
    }
  }
  @Test void failedDispatchLeavesNoDeliveryCommandOrCommitment() throws Exception {
    try(var c=owner()){sql(c,"UPDATE workers SET state='OFFLINE' WHERE id=?",worker);}
    try(var c=runtime()){rejected("40001",()->call(c,"deliver",id(),worker,request()));}
    try(var c=owner()){
      for(var table:List.of("d4.deliveries","d4.commands","d3.dispatches","execution_attempts","d2.reservations","d2.journal"))
        assertEquals("0",value(c,"SELECT count(*) FROM "+table));
    }
  }
  @Test void unknownFieldsAndInvalidCommandsRollbackCompletely() throws Exception {
    try(var c=runtime()){
      var req=new HashMap<String,Object>(request());req.put("worker_id",other);
      rejected("23514",()->call(c,"deliver",id(),worker,req));
      rejected("23514",()->call(c,"deliver",null,worker,request()));
    }
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM d4.commands"));assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations"));}
  }
  @Test void twoConnectionsRecoverOneDurableAssignment() throws Exception {
    try(var pool=Executors.newFixedThreadPool(2)){
      var go=new CountDownLatch(1);Callable<String> task=()->{try(var c=runtime()){go.await();return call(c,"deliver",id(),worker,request());}};
      var a=pool.submit(task);var b=pool.submit(task);go.countDown();assertEquals(a.get(15,TimeUnit.SECONDS),b.get(15,TimeUnit.SECONDS));
    }
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("1",value(c,"SELECT count(*) FROM d4.deliveries"));}
  }
  @Test void repeatableReadCommandsAreRejected() throws Exception {
    try(var c=runtime()){c.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);rejected("25001",()->call(c,"deliver",id(),worker,request()));}
  }
  @Test void upgradePreservesActiveV15AttemptAndJournal() throws Exception {
    String upgrade="d4_upgrade_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+upgrade);}
    try {
      var before=migrations(upgrade,"15");assertEquals(15,before.migrate().migrationsExecuted);
      String original=db;db=upgrade;
      try {
        try(var c=owner()){
          fixture(c,false);
          var dispatch=new DispatchStore().claim(c,id(),plan,operation,resource,worker);
          new DispatchStore().execute(c,id(),dispatch,"START",Map.of());
          assertEquals("15",value(c,"SELECT count(*) FROM flyway_schema_history WHERE success"));
          String basis=value(c,"SELECT d3.state_body()::text");
          var fw=migrations(upgrade,null);assertEquals(1,fw.migrate().migrationsExecuted);fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
          assertEquals(basis,value(c,"SELECT d3.state_body()::text"));
          assertEquals(dispatch.attemptId().toString(),value(c,"SELECT attempt_id FROM operation_leases"));
          assertEquals("RUNNING",value(c,"SELECT state FROM operations"));
          assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));
          sql(c,"INSERT INTO d4.worker_catalog(worker_id) VALUES(?)",worker);
          rejected("40001",()->call(c,"deliver",id(),worker,request()));
          assertEquals("0",value(c,"SELECT count(*) FROM d4.deliveries"));
        }
      } finally{db=original;}
    } finally{try(var c=connect("postgres")){sql(c,"DROP DATABASE "+upgrade+" WITH (FORCE)");}}
  }
}
