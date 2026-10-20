// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import java.nio.file.*;
import java.sql.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;
import io.github.isidorotrevino.planner.scheduler.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;

class DispatchStoreTest {
  static final Path ROOT=Path.of(System.getProperty("planner.root","..")).toAbsolutePath().normalize();
  static final String URL=Objects.requireNonNull(System.getProperty("d3.url"),"Use testing/D3/run-postgres-tests.sh or supply d3.url for disposable PostgreSQL");
  static final PlanningStore STORE=new PlanningStore();
  String db; UUID project,task,operation,worker,resource,account;Instant observed;
  static Connection connect(String db) throws SQLException {return DriverManager.getConnection(URL+db,"d2_auditor","");}
  Connection owner() throws SQLException {return connect(db);}
  Connection runtime() throws SQLException {var c=owner();sql(c,"SET ROLE d3_dispatch_test;SET statement_timeout=10000");return c;}
  static UUID id(){return UUID.randomUUID();}
  static void sql(Connection c,String sql,Object...args) throws SQLException {try(var p=c.prepareStatement(sql)){bind(p,args);p.execute();}}
  static String value(Connection c,String sql,Object...args) throws SQLException {try(var p=c.prepareStatement(sql)){bind(p,args);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}}}
  static void bind(PreparedStatement p,Object...args) throws SQLException {for(int i=0;i<args.length;i++){var v=args[i];p.setObject(i+1,v instanceof Instant t?t.atOffset(ZoneOffset.UTC):v);}}
  static UUID insert(Connection c,String sql,Object...args) throws SQLException {return UUID.fromString(value(c,sql+" RETURNING id",args));}
  static final DispatchStore DISPATCH=new DispatchStore();
  @BeforeAll static void initializeDispatchTemplate() throws Exception {
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE d3_dispatch_template");}
    var fw=Flyway.configure().dataSource(URL+"d3_dispatch_template","d2_auditor","").cleanDisabled(true)
      .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-dispatch-proposed")).load();
    fw.migrate();fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
    try(var c=connect("d3_dispatch_template")) {
      assertEquals("13",value(c,"SELECT count(*) FROM flyway_schema_history WHERE success"));
      sql(c,"CREATE ROLE d3_dispatch_test NOLOGIN;GRANT USAGE ON SCHEMA public,d3 TO d3_dispatch_test;GRANT EXECUTE ON FUNCTION d3.capture(uuid,jsonb),d3.read_capture(uuid),d3.publish(uuid,jsonb),d3.observe_eligibility(uuid),d3.dispatch(uuid,jsonb),d3.execution(uuid,jsonb) TO d3_dispatch_test");
    }
  }
  @BeforeEach void setup() throws Exception {
    db="d3_case_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+db+" TEMPLATE d3_dispatch_template");}
    try(var c=owner()) {
      observed=OffsetDateTime.parse(value(c,"SELECT clock_timestamp()::text").replace(" ","T").replaceAll("\\+00$","+00:00")).toInstant();
      project=insert(c,"INSERT INTO projects(code,name,workflow_type) VALUES(?,'Synthetic project','GENTLE_AI')",id().toString());
      task=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'task','Synthetic task')",project);
      worker=insert(c,"INSERT INTO workers(worker_key,host_name,state,last_heartbeat_at,capabilities) VALUES(?,'synthetic','ONLINE',clock_timestamp(),'{\"tools\":{\"code\":true}}')",id().toString());
      resource=insert(c,"INSERT INTO resources(resource_key,worker_id,provider,subscription,capabilities) VALUES(?,?,'SYNTHETIC','none','{\"tools\":{\"code\":true}}')",id().toString(),worker);
      operation=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) VALUES(?,'CODE',?,repeat('a',64),'synthetic-context','{\"required_capabilities\":{\"tools\":{\"code\":true}}}')",task,id().toString());
      account=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'execution','OPERATIONS','WEEKLY',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '10 days','SYNTHETIC',0.95,100)",resource,id().toString());
      STORE.configure(c,id(),Map.of("action","PROFILE","reason","Synthetic initial fairness epoch","epoch_id",id(),"calibration_epoch","manual-v1","policy",Map.of("schema_version",SCHEMA_VERSION,"timezone","Europe/Madrid","max_operations",1000,"max_edges",5000,"max_candidates",4000,"max_compute_ms",30000)));
      STORE.configure(c,id(),Map.of("action","CALENDAR","reason","Synthetic availability","resource_id",resource,"calendar_id",id(),"slots",List.of(Map.of("start",observed.minusSeconds(3600),"end",observed.plus(Duration.ofDays(10))))));
      estimate(c,operation,resource,account,10,null);
    }
  }
  @AfterEach void dropDatabase() throws Exception {
    if(db!=null)try(var c=connect("postgres")){sql(c,"DROP DATABASE "+db+" WITH (FORCE)");}
  }
  void estimate(Connection c,UUID op,UUID r,UUID a,int units,UUID expected) throws SQLException {
    var req=new HashMap<String,Object>(Map.of("action","ESTIMATE","reason","Synthetic estimate","estimate_id",id(),"operation_id",op,"resource_id",r,"units",Map.of(a,units),"duration_ms",900000,"confidence",new java.math.BigDecimal(".95"),"calibration_ref","manual-v1","provenance","SYNTHETIC"));
    req.put("observed_at",observed.minusSeconds(1));req.put("valid_until",observed.plus(Duration.ofDays(10)));req.put("expected_estimate_id",expected);STORE.configure(c,id(),req);
  }
  record Plan(PlanningStore.Captured capture,Result result) { }
  Plan plan() throws SQLException {try(var c=runtime()){var capture=STORE.capture(c,id());var result=new CapacityScheduler().plan(capture.request(),capture.snapshot());assertNotEquals(Status.INVALID_INPUT,result.status(),result.toString());return new Plan(capture,result);}}
  UUID publish(Plan plan) throws SQLException {try(var c=runtime()){return STORE.publish(c,id(),id(),plan.capture(),plan.result());}}
  String rawRequest(UUID plan,PlanningStore.Captured c,Result result) {
    var request=new LinkedHashMap<String,Object>();request.put("action","PUBLISH");request.put("plan_id",plan);request.put("capture_id",c.id());request.put("expected_current_plan_id",c.currentPlanId());request.put("result",result);return Json.write(request);
  }
  void rejectedPublication(Plan plan,String state) throws SQLException {
    try(var c=runtime()){var e=assertThrows(SQLException.class,()->STORE.publish(c,id(),id(),plan.capture(),plan.result()));assertEquals(state,e.getSQLState(),e.getMessage());}
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM planning_runs"));assertNull(value(c,"SELECT planning_run_id FROM d3.plan_head"));}
  }
  DispatchStore.Claimed claim(UUID pid) throws SQLException {try(var c=runtime()){return DISPATCH.claim(c,id(),pid,operation,resource,worker);}}
  String run(DispatchStore.Claimed d,String action,Map<String,?> payload) throws SQLException {try(var c=runtime()){return DISPATCH.execute(c,id(),d,action,payload);}}
  void assertClean() throws SQLException {try(var c=owner()) {
    assertEquals("0",value(c,"SELECT count(*) FROM d3.dispatches"));assertEquals("0",value(c,"SELECT count(*) FROM execution_attempts"));
    assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("0",value(c,"SELECT count(*) FROM d2.operation_accounts"));
  }}
  @Test void claimCommitsMappingReservationAttemptAndLaneAtomicallyWithoutEditingPlan() throws Exception {
    var pid=publish(plan());String config;try(var c=owner()){config=value(c,"SELECT config_snapshot::text FROM planning_runs WHERE id=?",pid);}
    var d=claim(pid);assertEquals(1,d.generation());
    try(var c=owner()) {
      assertEquals("LEASED",value(c,"SELECT state FROM operations WHERE id=?",operation));
      assertEquals("10.0000",value(c,"SELECT outstanding::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
      assertEquals("WEIGHTED",value(c,"SELECT lane FROM d3.lane_attributions WHERE reservation_id=?",d.reservationId()));
      assertEquals("1",value(c,"SELECT count(*) FROM d3.dispatches WHERE planning_run_id=?",pid));
      assertEquals("0",value(c,"SELECT count(*) FROM d2.plan_reservations"));
      assertEquals(config,value(c,"SELECT config_snapshot::text FROM planning_runs WHERE id=?",pid));
    }
  }
  @Test void replayIsStableAcrossSupersessionAndDifferentPayloadConflicts() throws Exception {
    var pid=publish(plan());var command=id();DispatchStore.Claimed first;
    try(var c=runtime()){first=DISPATCH.claim(c,command,pid,operation,resource,worker);}
    publish(plan());
    try(var c=runtime()) {
      assertEquals(first,DISPATCH.claim(c,command,pid,operation,resource,worker));
      assertEquals("23505",assertThrows(SQLException.class,()->DISPATCH.claim(c,command,id(),operation,resource,worker)).getSQLState());
    }
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));}
  }
  @Test void supersededPlanCannotClaim() throws Exception {
    var old=publish(plan());publish(plan());assertEquals("40001",assertThrows(SQLException.class,()->claim(old)).getSQLState());assertClean();
  }
  @ParameterizedTest @ValueSource(strings={"priority","paused","context","estimate","heartbeat","confidence","quota","calendar","newWindow"})
  void postPublicationChangesRejectWithoutPartialCommit(String change) throws Exception {
    var pid=publish(plan());
    try(var c=owner()) {
      switch(change) {
        case "priority" -> sql(c,"UPDATE projects SET priority='P0' WHERE id=?",project);
        case "paused" -> sql(c,"UPDATE projects SET status='PAUSED' WHERE id=?",project);
        case "context" -> sql(c,"UPDATE operations SET context_pack_sha256=repeat('b',64) WHERE id=?",operation);
        case "estimate" -> estimate(c,operation,resource,account,11,UUID.fromString(value(c,"SELECT estimate_id FROM d3.estimate_heads WHERE operation_id=? AND resource_id=?",operation,resource)));
        case "heartbeat" -> sql(c,"UPDATE workers SET last_heartbeat_at=clock_timestamp()-interval '91 seconds' WHERE id=?",worker);
        case "confidence" -> value(c,"SELECT d2.recalibrate(?,?::jsonb)",id(),Json.write(Map.of("account_id",account,"capacity",100,"confidence",new java.math.BigDecimal(".7"),"evidence_sha256","c".repeat(64),"reason","test")));
        case "quota" -> value(c,"SELECT d2.recalibrate(?,?::jsonb)",id(),Json.write(Map.of("account_id",account,"capacity",1,"confidence",new java.math.BigDecimal(".95"),"evidence_sha256","c".repeat(64),"reason","test")));
        case "calendar" -> STORE.configure(c,id(),Map.of("action","CALENDAR","reason","test","resource_id",resource,"calendar_id",id(),"expected_calendar_id",UUID.fromString(value(c,"SELECT calendar_id FROM d3.calendar_heads WHERE resource_id=?",resource)),"slots",List.of()));
        case "newWindow" -> sql(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'tokens','TOKENS','SESSION',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '1 day','test',.95,100)",resource,id().toString());
        default -> throw new AssertionError(change);
      }
    }
    assertEquals("40001",assertThrows(SQLException.class,()->claim(pid)).getSQLState());assertClean();
  }
  @Test void twoDispatchersProduceOneAttemptAndOneReservation() throws Exception {
    var pid=publish(plan());var gate=new CountDownLatch(1);
    try(var pool=Executors.newFixedThreadPool(2)) {
      var futures=new ArrayList<Future<String>>();for(int i=0;i<2;i++)futures.add(pool.submit(()->{gate.await();try{claim(pid);return "CLAIMED";}catch(SQLException e){return e.getSQLState();}}));
      gate.countDown();var outcomes=new ArrayList<String>();for(var f:futures)outcomes.add(f.get(15,TimeUnit.SECONDS));Collections.sort(outcomes);assertEquals(List.of("40001","CLAIMED"),outcomes);
    }
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM d2.journal WHERE commitment_delta>0"));assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));}
  }
  @Test void fencedLifecyclePreservesEvidenceAndCannotForgeAcceptance() throws Exception {
    var d=claim(publish(plan()));run(d,"START",Map.of());run(d,"HEARTBEAT",Map.of());
    run(d,"CALLBACK",Map.of("entries",List.of(Map.of("account_id",account,"settled",10,"consumed",8))));
    assertThrows(SQLException.class,()->run(d,"VERIFY",Map.of()));
    try(var c=owner()){var artifact=insert(c,"INSERT INTO artifacts(artifact_ref,sha256,media_type) VALUES(?,repeat('a',64),'text/plain')",id().toString());sql(c,"INSERT INTO execution_evidence(attempt_id,artifact_id,evidence_type) VALUES(?,?,'ACCEPTANCE_PASS')",d.attemptId(),artifact);}
    run(d,"VERIFY",Map.of());
    try(var c=owner()){assertEquals("COMPLETED",value(c,"SELECT state FROM operations WHERE id=?",operation));assertEquals("8.0000",value(c,"SELECT consumed::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));}
  }
  @Test void identityAndPayloadCannotBypassFencing() throws Exception {
    var d=claim(publish(plan()));var forged=new DispatchStore.Claimed(d.planId(),d.operationId(),d.attemptId(),d.reservationId(),d.workerId(),d.resourceId(),d.generation()+1);
    assertEquals("23514",assertThrows(SQLException.class,()->run(forged,"START",Map.of())).getSQLState());
    try(var c=runtime()){assertThrows(IllegalArgumentException.class,()->DISPATCH.execute(c,id(),d,"START",Map.of("generation",99)));}
    assertEquals("23514",assertThrows(SQLException.class,()->run(d,"CLAIM",Map.of())).getSQLState());
  }
  @Test void currentCarriedPlanCanRenewOriginalAttemptWithoutNewQuota() throws Exception {
    var d=claim(publish(plan()));run(d,"START",Map.of());publish(plan());run(d,"HEARTBEAT",Map.of());
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM d2.journal WHERE commitment_delta>0"));}
  }
  @Test void lostHeartbeatBlocksRenewalButFactualCallbackStillSettles() throws Exception {
    var d=claim(publish(plan()));run(d,"START",Map.of());
    try(var c=owner()){sql(c,"UPDATE workers SET last_heartbeat_at=clock_timestamp()-interval '91 seconds' WHERE id=?",worker);}
    assertEquals("40001",assertThrows(SQLException.class,()->run(d,"HEARTBEAT",Map.of())).getSQLState());
    run(d,"CALLBACK",Map.of("entries",List.of(Map.of("account_id",account,"settled",10,"consumed",12))));
    try(var c=owner()){assertEquals("12.0000",value(c,"SELECT consumed::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));}
  }
  @Test void restrictedRoleCannotBypassD3WithD2CallsOrInsertEvidence() throws Exception {
    try(var c=runtime()) {
      for(var statement:List.of("SELECT d2.execution(gen_random_uuid(),'{}')","SELECT d2.capacity_command(gen_random_uuid(),'{}')","INSERT INTO d3.dispatches DEFAULT VALUES","SELECT d3.state_relations_i2()","INSERT INTO execution_evidence(attempt_id,evidence_type) VALUES(gen_random_uuid(),'ACCEPTANCE_PASS')"))
        assertEquals("42501",assertThrows(SQLException.class,()->sql(c,statement)).getSQLState(),statement);
      c.setAutoCommit(false);assertEquals("25001",assertThrows(SQLException.class,()->DISPATCH.claim(c,id(),id(),operation,resource,worker)).getSQLState());c.rollback();
    }
  }
  void readyAfterAbsence(DispatchStore.Claimed d,String status) throws Exception {
    try(var c=owner()){sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second' WHERE operation_id=?",operation);}
    run(d,"EXPIRE",Map.of());UUID receipt;
    try(var c=owner()){receipt=insert(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(?,?,'synthetic',?,'proof')",operation,d.generation(),status);}
    run(d,"RECONCILE",Map.of("receipt_id",receipt));
    if(status.equals("ABSENT"))try(var c=owner()) {
      value(c,"SELECT d2.transition(?,?::jsonb)",id(),Json.write(Map.of("entity_type","OPERATION","entity_id",operation,"from","RETRY_PENDING","to","READY","expected_version",Integer.parseInt(value(c,"SELECT row_version FROM operations WHERE id=?",operation)),"actor","SYNTHETIC","reason","Confirmed absent effect")));
    }
  }
  @Test void retryUsesFrozenReservationAndOnlyTopsUpDeltaWithoutResettingAttempts() throws Exception {
    var first=claim(publish(plan()));run(first,"START",Map.of());
    run(first,"CALLBACK",Map.of("entries",List.of(Map.of("account_id",account,"settled",6,"consumed",4))));
    readyAfterAbsence(first,"ABSENT");
    var second=claim(publish(plan()));assertEquals(first.reservationId(),second.reservationId());assertEquals(2,second.generation());
    try(var c=owner()) {
      assertEquals("2",value(c,"SELECT count(*) FROM execution_attempts"));
      assertEquals("6.0000",value(c,"SELECT max(commitment_delta)::numeric(18,4)::text FROM d2.journal WHERE reservation_id=? AND commitment_delta>0 AND commitment_delta<10",first.reservationId()));
      assertEquals("10.0000",value(c,"SELECT outstanding::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
      assertEquals("4.0000",value(c,"SELECT consumed::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
      assertEquals("1",value(c,"SELECT count(*) FROM d3.lane_attributions"));
    }
    assertThrows(SQLException.class,()->run(first,"START",Map.of()));run(second,"START",Map.of());
  }
  @Test void unknownEffectRetainsCommitmentsAndCannotReclaim() throws Exception {
    var first=claim(publish(plan()));readyAfterAbsence(first,"UNKNOWN");
    var p=plan();assertEquals(Disposition.CARRIED,p.result().decisions().getFirst().disposition());var pid=publish(p);
    assertEquals("23514",assertThrows(SQLException.class,()->claim(pid)).getSQLState());
    try(var c=owner()){assertEquals("BLOCKED_APPROVAL",value(c,"SELECT state FROM operations WHERE id=?",operation));assertEquals("10.0000",value(c,"SELECT outstanding::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));}
  }
  @Test void contradictionAfterPublishingRetryCannotBeHiddenByAbsence() throws Exception {
    var first=claim(publish(plan()));readyAfterAbsence(first,"ABSENT");var pid=publish(plan());
    try(var c=owner()){sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(?,?,'synthetic','UNKNOWN','new-proof')",operation,first.generation());}
    assertEquals("23514",assertThrows(SQLException.class,()->claim(pid)).getSQLState());
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));}
  }
  @Test void attemptBoundIsNotResetByPublishingNewPlans() throws Exception {
    try(var c=owner()){sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||'{"+"\"max_attempts\":1}' WHERE id=?",operation);}
    var first=claim(publish(plan()));readyAfterAbsence(first,"ABSENT");var p=plan();assertEquals(Disposition.BLOCKED,p.result().decisions().getFirst().disposition());
    assertEquals("23514",assertThrows(SQLException.class,()->claim(publish(p))).getSQLState());
  }
  @Test void urgentLaneIsAttributedAndPersistsAcrossPlans() throws Exception {
    try(var c=owner()){sql(c,"UPDATE tasks SET deadline_at=clock_timestamp()+interval '1 hour' WHERE id=?",task);}
    var p=plan();assertEquals(Lane.URGENT,p.result().decisions().getFirst().lane());var d=claim(publish(p));publish(plan());
    try(var c=owner()){assertEquals("URGENT",value(c,"SELECT lane FROM d3.lane_attributions WHERE reservation_id=?",d.reservationId()));assertEquals("10.0000",value(c,"SELECT units::numeric(18,4)::text FROM d3.lane_usage WHERE account_id=? AND lane='URGENT'",account));}
  }
  @Test void twoIndependentWorkersCanClaimFromSamePlanDespiteFirstClaimChangingJournal() throws Exception {
    UUID op2,w2,r2,a2;
    try(var c=owner()) {
      var t2=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'second','second')",project);
      w2=insert(c,"INSERT INTO workers(worker_key,host_name,state,last_heartbeat_at,capabilities) VALUES(?,'synthetic','ONLINE',clock_timestamp(),'{"+"\"tools\":{\"code\":true}}')",id().toString());
      r2=insert(c,"INSERT INTO resources(resource_key,worker_id,provider,subscription,capabilities) SELECT ?,?,'SYNTHETIC','none',capabilities FROM resources WHERE id=?",id().toString(),w2,resource);
      op2=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) SELECT ?,'CODE',?,context_pack_sha256,context_pack_ref,policy_snapshot FROM operations WHERE id=?",t2,id().toString(),operation);
      a2=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) SELECT ?,dimension,unit,window_kind,?,window_start,window_end,provenance,confidence,initial_capacity FROM d2.accounts WHERE id=?",r2,id().toString(),account);
      estimate(c,op2,r2,a2,10,null);
      STORE.configure(c,id(),Map.of("action","CALENDAR","reason","Synthetic","resource_id",r2,"calendar_id",id(),"slots",List.of(Map.of("start",observed.minusSeconds(3600),"end",observed.plus(Duration.ofDays(10))))));
    }
    var pid=publish(plan());claim(pid);
    try(var c=runtime()){DISPATCH.claim(c,id(),pid,op2,r2,w2);}
    try(var c=owner()){assertEquals("2",value(c,"SELECT count(*) FROM d3.dispatches"));}
  }
  @Test void sharedWorkspaceBlocksConcurrentWorkOnDifferentWorkers() throws Exception {
    try(var c=owner()){sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||'{"+"\"exclusive_keys\":[\"shared-workspace\"]}' WHERE id=?",operation);}
    var pid=publish(plan());UUID active;
    try(var c=owner()) {
      var t2=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'active','active')",project);
      var w2=insert(c,"INSERT INTO workers(worker_key,host_name,state,last_heartbeat_at) VALUES(?,'other','ONLINE',clock_timestamp())",id().toString());
      var r2=insert(c,"INSERT INTO resources(resource_key,worker_id,provider,subscription) VALUES(?,?,'SYNTHETIC','none')",id().toString(),w2);
      active=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) VALUES(?,'CODE',?,repeat('a',64),'synthetic-context','{"+"\"exclusive_keys\":[\"shared-workspace\"]}')",t2,id().toString());
      var a2=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'execution','OPERATIONS','WEEKLY',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '1 day','test',.95,100)",r2,id().toString());
      sql(c,"INSERT INTO d2.operation_accounts VALUES(?,?,10,'test')",active,a2);
      value(c,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","CLAIM","operation_id",active,"resource_id",r2,"worker_id",w2)));
    }
    assertEquals("40001",assertThrows(SQLException.class,()->claim(pid)).getSQLState());
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations WHERE operation_id=?",operation));}
  }
  @Test void explicitTransactionRollbackAlsoUndoesD2CommandsAndOutbox() throws Exception {
    var pid=publish(plan());try(var c=owner()) {
      c.setAutoCommit(false);value(c,"SELECT d3.dispatch(?,?::jsonb)",id(),Json.write(Map.of("action","CLAIM","plan_id",pid,"operation_id",operation,"resource_id",resource,"worker_id",worker)));c.rollback();
    }
    assertClean();try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM outbox_events WHERE aggregate_id=?",operation));}
  }
  @Test void dependencyMutationWhileDispatcherWaitsIsRevalidatedAfterLock() throws Exception {
    var pid=publish(plan());try(var modifier=owner()) {
      modifier.setAutoCommit(false);sql(modifier,"SELECT pg_advisory_xact_lock(742002)");
      var predecessor=insert(modifier,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'blocking','blocking')",project);
      sql(modifier,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES(?,?,'HARD')",predecessor,task);
      try(var pool=Executors.newSingleThreadExecutor()) {
        var backend=new java.util.concurrent.atomic.AtomicInteger();var ready=new CountDownLatch(1);
        var f=pool.submit(()->{try(var c=runtime()){backend.set(Integer.parseInt(value(c,"SELECT pg_backend_pid()")));ready.countDown();DISPATCH.claim(c,id(),pid,operation,resource,worker);return "CLAIMED";}catch(SQLException e){return e.getSQLState();}});
        assertTrue(ready.await(5,TimeUnit.SECONDS));boolean waiting=false;
        for(int i=0;i<1000;i++){try(var c=owner()){waiting="true".equals(value(c,"SELECT EXISTS(SELECT 1 FROM pg_locks WHERE pid=? AND NOT granted)::text",backend.get()));}if(waiting)break;Thread.sleep(5);}
        assertTrue(waiting,"Dispatcher must actually wait for held mutex");modifier.commit();assertEquals("40001",f.get(15,TimeUnit.SECONDS));
      }
    }
    assertClean();
  }
  @ParameterizedTest @ValueSource(strings={"CLAIM","HEARTBEAT"})
  void approvalExpirationIsCheckedAgainstClockWithoutRowMutation(String action) throws Exception {
    try(var c=owner()) {
      sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||'{\"requires_approval\":true}' WHERE id=?",operation);
      sql(c,"INSERT INTO approvals(operation_id,state,reason,requested_at,decided_at,decided_by,expires_at,context_snapshot_sha256,policy_snapshot_sha256) SELECT id,'APPROVED','Synthetic',clock_timestamp()-interval '5 seconds',clock_timestamp()-interval '1 second','SYNTHETIC',clock_timestamp()+interval '2 seconds',context_pack_sha256,encode(digest(policy_snapshot::text,'sha256'),'hex') FROM operations WHERE id=?",operation);
    }
    var pid=publish(plan());var d=action.equals("HEARTBEAT")?claim(pid):null;
    if(d!=null)run(d,"START",Map.of());
    try(var c=owner()){sql(c,"SELECT pg_sleep(2.1)");}
    if(d==null){assertEquals("23514",assertThrows(SQLException.class,()->claim(pid)).getSQLState());assertClean();}
    else {assertEquals("23514",assertThrows(SQLException.class,()->run(d,"HEARTBEAT",Map.of())).getSQLState());try(var c=owner()){assertEquals("10.0000",value(c,"SELECT outstanding::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));}}
  }
  @Test void expiredPhysicalWindowBlocksRetryTopUpEvenWithExistingReservation() throws Exception {
    UUID session;
    try(var c=owner()) {
      session=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'execution','OPERATIONS','SESSION',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '5 seconds','test',.95,100)",resource,id().toString());
      var head=UUID.fromString(value(c,"SELECT estimate_id FROM d3.estimate_heads WHERE operation_id=? AND resource_id=?",operation,resource));
      STORE.configure(c,id(),Map.ofEntries(Map.entry("action","ESTIMATE"),Map.entry("reason","Short synthetic physical window"),Map.entry("estimate_id",id()),Map.entry("expected_estimate_id",head),Map.entry("operation_id",operation),Map.entry("resource_id",resource),Map.entry("units",Map.of(account,10,session,10)),Map.entry("duration_ms",4000),Map.entry("confidence",new java.math.BigDecimal(".95")),Map.entry("calibration_ref","manual-v1"),Map.entry("provenance","test"),Map.entry("observed_at",observed.minusSeconds(1)),Map.entry("valid_until",observed.plusSeconds(3600))));
    }
    var first=claim(publish(plan()));readyAfterAbsence(first,"ABSENT");var pid=publish(plan());
    try(var c=owner()){sql(c,"SELECT pg_sleep(greatest(extract(epoch FROM window_end-clock_timestamp())-3,0)) FROM d2.accounts WHERE id=?",session);}
    var error=assertThrows(SQLException.class,()->claim(pid));assertEquals("40001",error.getSQLState());assertTrue(error.getMessage().contains("Physical account window"),error.getMessage());
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("2",value(c,"SELECT count(*) FROM d2.journal WHERE commitment_delta>0"));}
  }
  @Test void mockDevelopmentCanRunButCannotVerifyWithoutRealTaskIntegration() throws Exception {
    try(var c=owner()) {
      var pre=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'mock-provider','mock-provider')",project);
      sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES(?,?,'MOCKABLE')",pre,task);
    }
    var d=claim(publish(plan()));run(d,"START",Map.of());run(d,"CALLBACK",Map.of("entries",List.of(Map.of("account_id",account,"settled",10,"consumed",8))));
    try(var c=owner()){var artifact=insert(c,"INSERT INTO artifacts(artifact_ref,sha256,media_type) VALUES(?,repeat('a',64),'text/plain')",id().toString());sql(c,"INSERT INTO execution_evidence(attempt_id,artifact_id,evidence_type) VALUES(?,?,'ACCEPTANCE_PASS')",d.attemptId(),artifact);}
    assertEquals("23514",assertThrows(SQLException.class,()->run(d,"VERIFY",Map.of())).getSQLState());
    try(var c=owner()){assertEquals("VERIFYING",value(c,"SELECT state FROM operations WHERE id=?",operation));}
  }
  @Test void realCapabilityInvalidationAfterPublicationBlocksDispatch() throws Exception {
    UUID version;
    try(var c=owner()) {
      var cap=insert(c,"INSERT INTO capabilities(provider_project_id,capability_key) VALUES(?,'dispatch-cap')",project);
      version=insert(c,"INSERT INTO capability_versions(capability_id,version,environment,contract_sha256) VALUES(?,'1.2.3','test',repeat('b',64))",cap);
      sql(c,"INSERT INTO d2.capability_epochs(version_id) VALUES(?)",version);
      sql(c,"INSERT INTO d2.verifications(version_id,epoch,environment,contract_sha256,evidence_sha256,outcome) VALUES(?,0,'test',repeat('b',64),repeat('c',64),'PASS')",version);
      int v=0;String current="PLANNED";for(var next:List.of("IMPLEMENTED","VERIFIED","AVAILABLE")) {
        value(c,"SELECT d2.transition(?,?::jsonb)",id(),Json.write(Map.of("entity_type","CAPABILITY_VERSION","entity_id",version,"from",current,"to",next,"expected_version",v++,"actor","SYNTHETIC","reason","test")));current=next;
      }
      var req=insert(c,"INSERT INTO capability_requirements(consumer_task_id,capability_id,version_constraint,environment,kind) VALUES(?,?,'^1.0.0','test','HARD')",task,cap);sql(c,"INSERT INTO d2.resolutions VALUES(?,?)",req,version);
    }
    var pid=publish(plan());
    try(var c=owner()){value(c,"SELECT d2.transition(?,?::jsonb)",id(),Json.write(Map.of("entity_type","CAPABILITY_VERSION","entity_id",version,"from","AVAILABLE","to","INVALIDATED","expected_version",3,"actor","SYNTHETIC","reason","test")));}
    assertEquals("40001",assertThrows(SQLException.class,()->claim(pid)).getSQLState());assertClean();
  }
  @Test void installationUpgradeFromV12PreservesPhysicalHistoryAndPublishedSnapshot() throws Exception {
    var upgrade="d3_upgrade13_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+upgrade);}
    try {
      var locations=new String[]{"filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-dispatch-proposed")};
      Flyway.configure().dataSource(URL+upgrade,"d2_auditor","").locations(locations).target("12").load().migrate();
      String journal,config;UUID pid;
      try(var source=owner();var c=connect(upgrade)) {
        // Copy only the synthetic fixture metadata in foreign-key order, then
        // create a genuine V12 published plan and D2 claim before upgrade.
        for(var table:List.of("projects","tasks","workers","resources","operations","d2.accounts","d3.fairness_epochs","d3.settings","d3.estimates","d3.estimate_heads","d3.calendars","d3.calendar_heads")) {
          var json=value(source,"SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]')::text FROM "+table+" t");
          sql(c,"INSERT INTO "+table+" SELECT * FROM jsonb_populate_recordset(NULL::"+table+",?::jsonb)",json);
        }
        var captured=STORE.capture(c,id());var result=new CapacityScheduler().plan(captured.request(),captured.snapshot());pid=STORE.publish(c,id(),id(),captured,result);
        sql(c,"INSERT INTO d2.operation_accounts VALUES(?,?,10,'manual-v1')",operation,account);
        value(c,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","CLAIM","operation_id",operation,"resource_id",resource,"worker_id",worker)));
        journal=value(c,"SELECT jsonb_agg(to_jsonb(j) ORDER BY id)::text FROM d2.journal j");config=value(c,"SELECT config_snapshot::text FROM planning_runs WHERE id=?",pid);
      }
      var fw=Flyway.configure().dataSource(URL+upgrade,"d2_auditor","").locations(locations).load();assertEquals(1,fw.migrate().migrationsExecuted);fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
      try(var c=connect(upgrade)) {
        assertEquals(journal,value(c,"SELECT jsonb_agg(to_jsonb(j) ORDER BY id)::text FROM d2.journal j"));assertEquals(config,value(c,"SELECT config_snapshot::text FROM planning_runs WHERE id=?",pid));
        assertEquals("0",value(c,"SELECT count(*) FROM d3.dispatches"));
        assertThrows(SQLException.class,()->DISPATCH.claim(c,id(),pid,operation,resource,worker));
      }
    } finally {try(var c=connect("postgres")){sql(c,"DROP DATABASE "+upgrade+" WITH (FORCE)");}}
  }
  @Test void contiguousTentativeSlotsDoNotPreventFirstClaimButActualLeaseBlocksSecond() throws Exception {
    try(var c=owner()) {
      var next=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) SELECT task_id,'CODE',?,context_pack_sha256,context_pack_ref,policy_snapshot FROM operations WHERE id=?",id().toString(),operation);
      estimate(c,next,resource,account,10,null);
    }
    var p=plan();var decisions=p.result().decisions().stream().filter(d->d.disposition()==Disposition.TENTATIVE).sorted(Comparator.comparing(d->d.slot().start())).toList();assertEquals(2,decisions.size());
    var pid=publish(p);
    try(var c=runtime()){DISPATCH.claim(c,id(),pid,decisions.getFirst().operationId(),resource,worker);}
    try(var c=owner()) {
      assertEquals("1",value(c,"SELECT count(*) FROM d3.dispatches"));assertEquals("1",value(c,"SELECT count(*) FROM outbox_events WHERE event_type='D3_REPLAN_REQUESTED'"));
      assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));
    }
    try(var c=runtime()){assertEquals("40001",assertThrows(SQLException.class,()->DISPATCH.claim(c,id(),pid,decisions.getLast().operationId(),resource,worker)).getSQLState());}
  }
  @Test void recalibratedEstimateStopsContinuationWithoutDiscardingCommitment() throws Exception {
    var d=claim(publish(plan()));run(d,"START",Map.of());
    try(var c=owner()){estimate(c,operation,resource,account,20,UUID.fromString(value(c,"SELECT estimate_id FROM d3.estimate_heads WHERE operation_id=? AND resource_id=?",operation,resource)));}
    assertEquals("40001",assertThrows(SQLException.class,()->run(d,"HEARTBEAT",Map.of())).getSQLState());
    try(var c=owner()){assertEquals("10.0000",value(c,"SELECT outstanding::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));}
  }
  UUID incident(Connection c) throws SQLException {
    var inc=insert(c,"INSERT INTO incidents(project_id,incident_key,severity) VALUES(?,'synthetic-incident','SEV1')",project);
    sql(c,"INSERT INTO incident_task_links VALUES(?,?,'FIX')",inc,task);return inc;
  }
  @ParameterizedTest @ValueSource(strings={"CLAIM","HEARTBEAT"})
  void incidentEscalationNeverSilentlyTakesPlannedCapacity(String action) throws Exception {
    var pid=publish(plan());var d=action.equals("HEARTBEAT")?claim(pid):null;if(d!=null)run(d,"START",Map.of());
    try(var c=owner()){incident(c);}
    if(d==null){assertEquals("40001",assertThrows(SQLException.class,()->claim(pid)).getSQLState());assertClean();}
    else assertEquals("40001",assertThrows(SQLException.class,()->run(d,"HEARTBEAT",Map.of())).getSQLState());
  }
  @Test void incidentCommitmentUsesOnlyIncidentAndShortfallRollsBack() throws Exception {
    try(var c=owner()){incident(c);}
    var p=plan();assertEquals(Pool.INCIDENT,p.result().decisions().getFirst().pool());var pid=publish(p);
    try(var c=owner()){value(c,"SELECT d2.recalibrate(?,?::jsonb)",id(),Json.write(Map.of("account_id",account,"capacity",40,"confidence",new java.math.BigDecimal(".95"),"evidence_sha256","c".repeat(64),"reason","Incident cannot fit, planned can")));}
    assertEquals("40001",assertThrows(SQLException.class,()->claim(pid)).getSQLState());assertClean();
    try(var c=owner()) {
      assertEquals("28.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
      value(c,"SELECT d2.recalibrate(?,?::jsonb)",id(),Json.write(Map.of("account_id",account,"capacity",100,"confidence",new java.math.BigDecimal(".95"),"evidence_sha256","c".repeat(64),"reason","Restore synthetic quota")));
    }
    var d=claim(pid);try(var c=owner()) {
      assertEquals("INCIDENT",value(c,"SELECT pool FROM d2.reservations WHERE id=?",d.reservationId()));
      assertEquals("70.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
      assertEquals("10.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='UNCERTAINTY'",account));
    }
  }
  @Test void contradictoryAbsenceCannotRemoveUnknownPhysicalExclusion() throws Exception {
    var d=claim(publish(plan()));readyAfterAbsence(d,"UNKNOWN");UUID absence;
    try(var c=owner()){absence=insert(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(?,?,'synthetic','ABSENT','new-proof')",operation,d.generation());}
    run(d,"RESUME_RECONCILIATION",Map.of("receipt_id",absence));
    assertEquals("23514",assertThrows(SQLException.class,()->run(d,"RECONCILE",Map.of("receipt_id",absence))).getSQLState());
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM operation_leases WHERE operation_id=?",operation));assertEquals("RECONCILING",value(c,"SELECT state FROM operations WHERE id=?",operation));}
  }
}
