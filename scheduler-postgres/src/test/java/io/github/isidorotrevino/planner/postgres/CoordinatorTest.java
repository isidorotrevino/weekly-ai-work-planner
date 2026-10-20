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

class CoordinatorTest {
  static final Path ROOT=Path.of(System.getProperty("planner.root","..")).toAbsolutePath().normalize();
  static final String URL=Objects.requireNonNull(System.getProperty("d3.url"),"Use testing/D3/run-postgres-tests.sh or supply d3.url for disposable PostgreSQL");
  static final PlanningStore STORE=new PlanningStore();
  String db; UUID project,task,operation,worker,resource,account;Instant observed;
  static Connection connect(String db) throws SQLException {return DriverManager.getConnection(URL+db,"d2_auditor","");}
  Connection owner() throws SQLException {return connect(db);}
  Connection runtime() throws SQLException {var c=owner();sql(c,"SET ROLE d3_coordinator_test;SET statement_timeout=10000");return c;}
  static UUID id(){return UUID.randomUUID();}
  static void sql(Connection c,String sql,Object...args) throws SQLException {try(var p=c.prepareStatement(sql)){bind(p,args);p.execute();}}
  static String value(Connection c,String sql,Object...args) throws SQLException {try(var p=c.prepareStatement(sql)){bind(p,args);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}}}
  static void bind(PreparedStatement p,Object...args) throws SQLException {for(int i=0;i<args.length;i++){var v=args[i];p.setObject(i+1,v instanceof Instant t?t.atOffset(ZoneOffset.UTC):v);}}
  static UUID insert(Connection c,String sql,Object...args) throws SQLException {return UUID.fromString(value(c,sql+" RETURNING id",args));}
  static final DispatchStore DISPATCH=new DispatchStore();
  static final PlanningCoordinator COORD=new PlanningCoordinator();
  @BeforeAll static void initializeCoordinatorTemplate() throws Exception {
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE d3_coordinator_template");}
    var fw=Flyway.configure().dataSource(URL+"d3_coordinator_template","d2_auditor","").cleanDisabled(true)
      .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-dispatch-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-coordinator-proposed")).load();
    fw.migrate();fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
    try(var c=connect("d3_coordinator_template")) {
      assertEquals("14",value(c,"SELECT count(*) FROM flyway_schema_history WHERE success"));
      sql(c,"CREATE ROLE d3_coordinator_test NOLOGIN;GRANT USAGE ON SCHEMA public,d3 TO d3_coordinator_test;GRANT EXECUTE ON FUNCTION d3.read_capture(uuid),d3.enqueue_planning(uuid,jsonb),d3.poll_planning(uuid),d3.take_planning(uuid,jsonb),d3.prepare_planning(jsonb),d3.publish_planning(jsonb),d3.fail_planning(jsonb),d3.read_planning_request(uuid) TO d3_coordinator_test");
    }
  }
  @BeforeEach void setup() throws Exception {
    db="d3_case_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+db+" TEMPLATE d3_coordinator_template");}
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
  UUID enqueue(ReplanPolicy.Kind kind) throws SQLException {
    try(var c=runtime()){return COORD.enqueue(c,id(),id(),kind,observed,Map.of("reason","synthetic"));}
  }
  void due(UUID request) throws SQLException {try(var c=owner()){sql(c,"UPDATE d3.planning_requests SET due_at=clock_timestamp()-interval '1 second' WHERE id=?",request);}}
  PlanningCoordinator.Outcome run() throws SQLException {try(var c=runtime()){return COORD.runOnce(c,id(),id());}}
  @Test void criticalRequestPublishesWithProtectionBrokenAndNoClaim() throws Exception {
    enqueue(ReplanPolicy.Kind.INCIDENT_CRITICAL);
    var flag=new java.util.concurrent.atomic.AtomicBoolean();
    var coordinator=new PlanningCoordinator((req,snapshot)->{flag.set(req.breakProtection());assertTrue(req.breakProtection());return new CapacityScheduler().plan(req,snapshot);});
    try(var c=runtime()){assertEquals(PlanningCoordinator.State.PUBLISHED,coordinator.runOnce(c,id(),id()).state());}
    assertTrue(flag.get());try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("0",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_attempts WHERE state='PUBLISHED'"));}
  }
  @Test void ordinaryEventsWaitThirtySecondsWithoutMovingFirstDeadline() throws Exception {
    var r=enqueue(ReplanPolicy.Kind.ORDINARY);String due;
    try(var c=owner()){due=value(c,"SELECT due_at::text FROM d3.planning_requests WHERE id=?",r);assertEquals("30.000000",value(c,"SELECT extract(epoch FROM due_at-first_received_at)::text FROM d3.planning_requests WHERE id=?",r));}
    assertEquals(PlanningCoordinator.State.IDLE,run().state());assertEquals(r,enqueue(ReplanPolicy.Kind.CAPACITY_CHANGED));
    try(var c=owner()){assertEquals(due,value(c,"SELECT due_at::text FROM d3.planning_requests WHERE id=?",r));}
    due(r);assertEquals(PlanningCoordinator.State.PUBLISHED,run().state());
  }
  @Test void criticalEventAcceleratesExistingOrdinaryRequest() throws Exception {
    var r=enqueue(ReplanPolicy.Kind.ORDINARY);assertEquals(r,enqueue(ReplanPolicy.Kind.APPROVAL_INVALID));
    try(var c=owner()){assertEquals("true",value(c,"SELECT break_protection::text FROM d3.planning_requests WHERE id=?",r));}
    assertEquals(PlanningCoordinator.State.PUBLISHED,run().state());
  }
  @Test void eventDeduplicationSurvivesCompletionAndConflictIsExplicit() throws Exception {
    var event=id();UUID request;
    try(var c=runtime()){request=COORD.enqueue(c,id(),event,ReplanPolicy.Kind.WORKER_LOST,observed,Map.of("a",1));}
    run();try(var c=runtime()) {
      assertEquals(request,COORD.enqueue(c,id(),event,ReplanPolicy.Kind.WORKER_LOST,observed,Map.of("a",1)));
      assertEquals("23505",assertThrows(SQLException.class,()->COORD.enqueue(c,id(),event,ReplanPolicy.Kind.WORKER_LOST,observed,Map.of("a",2))).getSQLState());
    }
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_events"));assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_requests"));}
  }
  @Test void calculationHoldsNoSqlLocksAndNewEventForcesFreshAttempt() throws Exception {
    enqueue(ReplanPolicy.Kind.INCIDENT_CRITICAL);var calls=new java.util.concurrent.atomic.AtomicInteger();
    var coordinator=new PlanningCoordinator((req,snapshot)->{
      // A separate connection mutates metadata while computation is in progress.
      // It would time out if capture kept the transaction/mutex open.
      if(calls.getAndIncrement()==0)try(var c=runtime()){COORD.enqueue(c,id(),id(),ReplanPolicy.Kind.PRIORITY_CHANGED,observed,Map.of());}
      return new CapacityScheduler().plan(req,snapshot);
    });
    try(var c=runtime()){var result=coordinator.runOnce(c,id(),id());assertEquals(PlanningCoordinator.State.PUBLISHED,result.state());assertEquals(1,result.recalculations());}
    assertEquals(2,calls.get());try(var c=owner()){assertEquals("STALE,PUBLISHED",value(c,"SELECT string_agg(state,',' ORDER BY attempt_no) FROM d3.planning_attempts"));assertEquals("1",value(c,"SELECT count(*) FROM planning_runs"));}
  }
  @Test void continuousConflictsEndStaleAfterOnlyTwoRecalculations() throws Exception {
    enqueue(ReplanPolicy.Kind.WORKER_LOST);var calls=new java.util.concurrent.atomic.AtomicInteger();
    var coordinator=new PlanningCoordinator((req,snapshot)->{calls.incrementAndGet();try(var c=runtime()){COORD.enqueue(c,id(),id(),ReplanPolicy.Kind.ORDINARY,observed,Map.of());}return new CapacityScheduler().plan(req,snapshot);});
    try(var c=runtime()){var result=coordinator.runOnce(c,id(),id());assertEquals(PlanningCoordinator.State.STALE,result.state());assertEquals(2,result.recalculations());assertTrue(COORD.read(c,result.requestId()).contains("STALE"));}
    assertEquals(3,calls.get());try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM planning_runs"));assertEquals("3",value(c,"SELECT count(*) FROM d3.planning_attempts"));assertEquals("4",value(c,"SELECT count(*) FROM d3.planning_events"));}
  }
  @Test void expiredLeaseCanBeRecoveredButOldProcessCannotPublish() throws Exception {
    enqueue(ReplanPolicy.Kind.WORKER_LOST);PlanningCoordinator.Lease old;PlanningCoordinator.Attempt original;
    try(var c=runtime()){old=COORD.take(c,id(),id()).orElseThrow();original=COORD.prepare(c,old);}
    try(var c=owner()){sql(c,"UPDATE d3.planning_requests SET lease_until=clock_timestamp()-interval '1 second' WHERE id=?",old.requestId());}
    try(var c=runtime()) {
      var successor=COORD.take(c,id(),id()).orElseThrow();assertEquals(old.generation()+1,successor.generation());
      var recovered=COORD.prepare(c,successor);assertEquals(original.captureId(),recovered.captureId());assertEquals(original.planId(),recovered.planId());
      var captured=STORE.read(c,recovered.captureId());var result=new CapacityScheduler().plan(captured.request(),captured.snapshot());
      assertEquals("55000",assertThrows(SQLException.class,()->COORD.publish(c,original,result)).getSQLState());
      COORD.publish(c,recovered,result);
    }
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM planning_runs"));}
  }
  @Test void publicationAndRequestConfirmationAreAtomicAndReplayableAfterLostResponse() throws Exception {
    enqueue(ReplanPolicy.Kind.WORKER_LOST);var cmd=id();var worker=id();PlanningCoordinator.Outcome result;
    try(var c=runtime()){result=COORD.runOnce(c,cmd,worker);assertEquals(result,COORD.runOnce(c,cmd,worker));}
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM planning_runs"));assertEquals("1",value(c,"SELECT count(*) FROM outbox_events WHERE event_type='PLAN_PUBLISHED'"));}
  }
  @Test void twoProcessesTakeOnlyOneLease() throws Exception {
    enqueue(ReplanPolicy.Kind.INCIDENT_CRITICAL);var gate=new CountDownLatch(1);
    try(var pool=Executors.newFixedThreadPool(2)) {
      var futures=new ArrayList<Future<Boolean>>();for(int i=0;i<2;i++)futures.add(pool.submit(()->{gate.await();try(var c=runtime()){return COORD.take(c,id(),id()).isPresent();}}));
      gate.countDown();int taken=0;for(var f:futures)if(f.get(15,TimeUnit.SECONDS))taken++;assertEquals(1,taken);
    }
  }
  @Test void pollingUsesIndependentDurableReceiptsAndNeverLoopsOnPublishedPlans() throws Exception {
    UUID source;try(var c=owner()){source=insert(c,"INSERT INTO outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('INCIDENT',?,'REPLAN_REQUIRED','{\"severity\":\"SEV1\"}')",project);}
    try(var c=runtime()){assertTrue(COORD.poll(c,id()).contains("true"));assertEquals(PlanningCoordinator.State.PUBLISHED,COORD.runOnce(c,id(),id()).state());COORD.poll(c,id());assertEquals(PlanningCoordinator.State.IDLE,COORD.runOnce(c,id(),id()).state());}
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_source_receipts WHERE outbox_id=? AND disposition='ACCEPTED'",source));assertNull(value(c,"SELECT delivered_at FROM outbox_events WHERE id=?",source));assertEquals("0",value(c,"SELECT count(*) FROM d2.delivery_receipts"));assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_requests"));}
  }
  @Test void sweepIsPersistedAndOnlyDueAfterSixtySeconds() throws Exception {
    try(var c=runtime()){COORD.poll(c,id());COORD.poll(c,id());}
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_events WHERE kind='SWEEP'"));sql(c,"UPDATE d3.planning_clock SET last_sweep_at=clock_timestamp()-interval '61 seconds'");}
    try(var c=runtime()){COORD.poll(c,id());}
    try(var c=owner()){assertEquals("2",value(c,"SELECT count(*) FROM d3.planning_events WHERE kind='SWEEP'"));assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_requests"));}
  }
  @Test void restrictedCoordinatorCannotClaimOrPublishOutsideItsLease() throws Exception {
    try(var c=runtime()) {
      for(var statement:List.of("SELECT d3.publish(gen_random_uuid(),'{}')","SELECT d3.dispatch(gen_random_uuid(),'{}')","SELECT d3.execution(gen_random_uuid(),'{}')","UPDATE d3.planning_requests SET recalculations=0","SELECT d3.enqueue_internal(gen_random_uuid(),'SWEEP',clock_timestamp(),'{}')"))
        assertEquals("42501",assertThrows(SQLException.class,()->sql(c,statement)).getSQLState(),statement);
      c.setAutoCommit(false);assertEquals("25001",assertThrows(SQLException.class,()->COORD.poll(c,id())).getSQLState());c.rollback();
    }
  }
  @Test void terminalStaleCanBeReplayedWithoutRestartingItsBudget() throws Exception {
    enqueue(ReplanPolicy.Kind.WORKER_LOST);var cmd=id();var worker=id();var calls=new java.util.concurrent.atomic.AtomicInteger();
    var coordinator=new PlanningCoordinator((req,snapshot)->{calls.incrementAndGet();try(var c=runtime()){COORD.enqueue(c,id(),id(),ReplanPolicy.Kind.ORDINARY,observed,Map.of());}return new CapacityScheduler().plan(req,snapshot);});
    try(var c=runtime()){var result=coordinator.runOnce(c,cmd,worker);assertEquals(PlanningCoordinator.State.STALE,result.state());assertEquals(result,coordinator.runOnce(c,cmd,worker));}
    assertEquals(3,calls.get());
  }
  @Test void invalidCalculationIsBlockedWithoutRetryOrChangingCurrentPlan() throws Exception {
    enqueue(ReplanPolicy.Kind.WORKER_LOST);var first=run();enqueue(ReplanPolicy.Kind.CAPACITY_DEFICIT);
    var calls=new java.util.concurrent.atomic.AtomicInteger();
    var coordinator=new PlanningCoordinator((req,snapshot)->{calls.incrementAndGet();return new CapacityScheduler().plan(new Request("unsupported",req.asOf(),req.timezone(),req.policyHash(),req.calibrationEpoch(),req.limits(),req.breakProtection()),snapshot);});
    var cmd=id();var worker=id();try(var c=runtime()){var result=coordinator.runOnce(c,cmd,worker);assertEquals(PlanningCoordinator.State.BLOCKED,result.state());assertEquals(0,result.recalculations());assertEquals(result,coordinator.runOnce(c,cmd,worker));}
    assertEquals(1,calls.get());try(var c=owner()){assertEquals(first.planId().toString(),value(c,"SELECT planning_run_id FROM d3.plan_head"));assertEquals("1",value(c,"SELECT count(*) FROM planning_runs"));}
  }
  @Test void physicalStateChangeCausesFreshCalculationInsteadOfPublishingOldQuota() throws Exception {
    enqueue(ReplanPolicy.Kind.WORKER_LOST);var calls=new java.util.concurrent.atomic.AtomicInteger();
    var coordinator=new PlanningCoordinator((req,snapshot)->{
      if(calls.getAndIncrement()==0)try(var c=owner()){value(c,"SELECT d2.recalibrate(?,?::jsonb)",id(),Json.write(Map.of("account_id",account,"capacity",1,"confidence",new java.math.BigDecimal(".95"),"evidence_sha256","c".repeat(64),"reason","Synthetic reduction")));}
      return new CapacityScheduler().plan(req,snapshot);
    });
    try(var c=runtime()){assertEquals(1,coordinator.runOnce(c,id(),id()).recalculations());}
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM schedule_entries"));assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("1",value(c,"SELECT count(*) FROM planning_runs"));}
  }
  @Test void expiredComputationLeaseCannotPublishOrMarkFailureUntilReclaimed() throws Exception {
    enqueue(ReplanPolicy.Kind.WORKER_LOST);PlanningCoordinator.Attempt attempt;
    try(var c=runtime()){attempt=COORD.prepare(c,COORD.take(c,id(),id()).orElseThrow());}
    try(var c=owner()){sql(c,"UPDATE d3.planning_requests SET lease_until=clock_timestamp()-interval '1 second' WHERE id=?",attempt.lease().requestId());}
    try(var c=runtime()) {
      var captured=STORE.read(c,attempt.captureId());var result=new CapacityScheduler().plan(captured.request(),captured.snapshot());
      assertEquals("55000",assertThrows(SQLException.class,()->COORD.publish(c,attempt,result)).getSQLState());
      assertEquals("55000",assertThrows(SQLException.class,()->COORD.fail(c,attempt,"40001")).getSQLState());
    }
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM planning_runs"));assertEquals("0",value(c,"SELECT recalculations FROM d3.planning_requests"));}
  }
  @Test void lateArrivingBackdatedOutboxEventIsNotSkippedAndAcksDoNotAlterContent() throws Exception {
    try(var c=runtime()){COORD.poll(c,id());}run();UUID source;
    try(var c=owner()){source=insert(c,"INSERT INTO outbox_events(aggregate_type,aggregate_id,event_type,payload,created_at) VALUES('OPERATION',?,'DEPENDENCY_INVALIDATED','{}',clock_timestamp()-interval '1 day')",operation);}
    try(var c=runtime()){COORD.poll(c,id());}
    String hash;try(var c=owner()) {
      hash=value(c,"SELECT content_sha256 FROM d3.planning_source_receipts WHERE outbox_id=?",source);
      assertEquals("ACCEPTED",value(c,"SELECT disposition FROM d3.planning_source_receipts WHERE outbox_id=?",source));
      value(c,"SELECT d2.ack_outbox(?,jsonb_build_object('outbox_id',?::uuid,'payload_sha256',encode(digest('{}'::jsonb::text,'sha256'),'hex')))",id(),source);
    }
    try(var c=runtime()){COORD.poll(c,id());}
    try(var c=owner()){assertEquals(hash,value(c,"SELECT content_sha256 FROM d3.planning_source_receipts WHERE outbox_id=?",source));assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_events WHERE id=?",source));}
  }
  @Test void boundedPollPrioritizesCriticalEventsAndExposesBacklog() throws Exception {
    UUID critical;try(var c=owner()) {
      sql(c,"INSERT INTO outbox_events(aggregate_type,aggregate_id,event_type,payload) SELECT 'OTHER',?,'UNHANDLED','{}'::jsonb FROM generate_series(1,101)",project);
      critical=insert(c,"INSERT INTO outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('INCIDENT',?,'REPLAN_REQUIRED','{\"severity\":\"SEV2\"}')",project);
    }
    try(var c=runtime()){var response=COORD.poll(c,id());assertTrue(response.contains("\"backlog\": true"));assertTrue(response.contains("\"received\": 100"));}
    try(var c=owner()){assertEquals("ACCEPTED",value(c,"SELECT disposition FROM d3.planning_source_receipts WHERE outbox_id=?",critical));assertEquals("100",value(c,"SELECT count(*) FROM d3.planning_source_receipts"));}
    try(var c=runtime()){COORD.poll(c,id());}
    try(var c=owner()){assertEquals("102",value(c,"SELECT count(*) FROM d3.planning_source_receipts"));}
  }
  @Test void priorityEventsMatchPurePolicyAndBreakProtectionWithoutImmediateDispatch() throws Exception {
    var r=enqueue(ReplanPolicy.Kind.PRIORITY_CHANGED);
    try(var c=owner()){assertEquals("true",value(c,"SELECT break_protection::text FROM d3.planning_requests WHERE id=?",r));assertEquals("30.000000",value(c,"SELECT extract(epoch FROM due_at-first_received_at)::text FROM d3.planning_requests WHERE id=?",r));}
    assertEquals(PlanningCoordinator.State.IDLE,run().state());
    assertEquals(Duration.ofSeconds(30),Duration.between(ReplanPolicy.batch(List.of(new ReplanPolicy.Delivery(new ReplanPolicy.Event(id(),ReplanPolicy.Kind.PRIORITY_CHANGED,observed),observed))).orElseThrow().firstReceivedAt(),ReplanPolicy.batch(List.of(new ReplanPolicy.Delivery(new ReplanPolicy.Event(id(),ReplanPolicy.Kind.PRIORITY_CHANGED,observed),observed))).orElseThrow().dueAt()));
  }
  @Test void futureEventAndRawUnknownKindLeaveNoPartialRequest() throws Exception {
    try(var c=runtime()) {
      assertEquals("23514",assertThrows(SQLException.class,()->COORD.enqueue(c,id(),id(),ReplanPolicy.Kind.ORDINARY,observed.plus(Duration.ofDays(1)),Map.of())).getSQLState());
      assertEquals("23514",assertThrows(SQLException.class,()->value(c,"SELECT d3.enqueue_planning(?,?::jsonb)",id(),Json.write(Map.of("action","ENQUEUE","event_id",id(),"kind","UNSUPPORTED","occurred_at",observed,"content",Map.of())))).getSQLState());
    }
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM d3.planning_requests"));}
  }
  @Test void databaseRollbackRemovesPublicationRequestConfirmationAndOutboxTogether() throws Exception {
    enqueue(ReplanPolicy.Kind.WORKER_LOST);PlanningCoordinator.Attempt attempt;
    try(var c=runtime()){attempt=COORD.prepare(c,COORD.take(c,id(),id()).orElseThrow());}
    try(var c=owner()) {
      var captured=STORE.read(c,attempt.captureId());var result=new CapacityScheduler().plan(captured.request(),captured.snapshot());
      c.setAutoCommit(false);value(c,"SELECT d3.publish_planning(?::jsonb)",Json.write(Map.of("request_id",attempt.lease().requestId(),"worker_id",attempt.lease().workerId(),"generation",attempt.lease().generation(),"attempt_no",attempt.number(),"result",result)));c.rollback();
    }
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM planning_runs"));assertEquals("RUNNING",value(c,"SELECT state FROM d3.planning_requests"));assertEquals("0",value(c,"SELECT count(*) FROM outbox_events WHERE event_type='PLAN_PUBLISHED'"));}
    try(var c=runtime()){var captured=STORE.read(c,attempt.captureId());COORD.publish(c,attempt,new CapacityScheduler().plan(captured.request(),captured.snapshot()));}
  }
  @Test void preparationAndPollingAreReplayableWithoutExtraEligibilitySamples() throws Exception {
    var poll=id();String response;
    try(var c=runtime()){response=COORD.poll(c,poll);assertEquals(response,COORD.poll(c,poll));var lease=COORD.take(c,id(),id()).orElseThrow();var a=COORD.prepare(c,lease);assertEquals(a,COORD.prepare(c,lease));}
    try(var c=owner()){assertEquals("2",value(c,"SELECT count(*) FROM d3.eligibility_ticks"));assertEquals("1",value(c,"SELECT count(*) FROM d3.captures"));}
  }
  @Test void realConsumptionDeficitIsImmediateAndPreservesPhysicalDebt() throws Exception {
    try(var c=owner()) {
      sql(c,"INSERT INTO d2.operation_accounts VALUES(?,?,10,'manual-v1')",operation,account);
      var claim=value(c,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","CLAIM","operation_id",operation,"resource_id",resource,"worker_id",worker)));
      var reservation=UUID.fromString(value(c,"SELECT id FROM d2.reservations WHERE operation_id=?",operation));
      value(c,"SELECT d2.capacity(?,?::jsonb)",id(),Json.write(Map.of("action","CONSUME","reservation_id",reservation,"reason","Synthetic measured overspend","entries",List.of(Map.of("account_id",account,"settled",10,"consumed",80)))));
      // Suppress only the scheduled sweep so this test proves deficit urgency.
      sql(c,"UPDATE d3.planning_clock SET last_sweep_at=clock_timestamp()");
    }
    try(var c=runtime()){COORD.poll(c,id());}
    try(var c=owner()) {
      assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_events e JOIN outbox_events o ON o.id=e.id WHERE e.kind='CAPACITY_DEFICIT' AND o.event_type='CONSUME'"));
      assertEquals("true",value(c,"SELECT (due_at<=clock_timestamp() AND break_protection)::text FROM d3.planning_requests"));
      assertEquals("-10.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
    }
    assertEquals(PlanningCoordinator.State.PUBLISHED,run().state());
    try(var c=owner()){assertEquals("80.0000",value(c,"SELECT consumed::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));assertEquals("20.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='INCIDENT'",account));}
  }
  @Test void ambiguousTransportErrorDoesNotInventARecalculationOrFailure() throws Exception {
    enqueue(ReplanPolicy.Kind.INCIDENT_CRITICAL);
    var coordinator=new PlanningCoordinator((req,snapshot)->{throw new SQLException("Synthetic connection lost","08006");});
    var cmd=id();var worker=id();try(var c=runtime()){assertEquals("08006",assertThrows(SQLException.class,()->coordinator.runOnce(c,cmd,worker)).getSQLState());}
    try(var c=owner()){assertEquals("RUNNING",value(c,"SELECT state FROM d3.planning_requests"));assertEquals("0",value(c,"SELECT recalculations FROM d3.planning_requests"));}
    try(var c=runtime()){assertEquals(PlanningCoordinator.State.PUBLISHED,COORD.runOnce(c,cmd,worker).state());}
  }
  @Test void upgradeV13PreservesDispatchJournalAndCanContinueExistingLease() throws Exception {
    var upgrade="d3_upgrade14_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+upgrade);}
    try {
      var locations=new String[]{"filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-dispatch-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-coordinator-proposed")};
      Flyway.configure().dataSource(URL+upgrade,"d2_auditor","").locations(locations).target("13").load().migrate();
      String journal,config,dispatch;UUID pid;DispatchStore.Claimed claimed;
      try(var source=owner();var c=connect(upgrade)) {
        for(var table:List.of("projects","tasks","workers","resources","operations","d2.accounts","d3.fairness_epochs","d3.settings","d3.estimates","d3.estimate_heads","d3.calendars","d3.calendar_heads")) {
          var json=value(source,"SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]')::text FROM "+table+" t");sql(c,"INSERT INTO "+table+" SELECT * FROM jsonb_populate_recordset(NULL::"+table+",?::jsonb)",json);
        }
        var captured=STORE.capture(c,id());pid=STORE.publish(c,id(),id(),captured,new CapacityScheduler().plan(captured.request(),captured.snapshot()));
        claimed=DISPATCH.claim(c,id(),pid,operation,resource,worker);
        journal=value(c,"SELECT jsonb_agg(to_jsonb(j) ORDER BY id)::text FROM d2.journal j");config=value(c,"SELECT config_snapshot::text FROM planning_runs WHERE id=?",pid);dispatch=value(c,"SELECT jsonb_agg(to_jsonb(d))::text FROM d3.dispatches d");
      }
      var fw=Flyway.configure().dataSource(URL+upgrade,"d2_auditor","").locations(locations).load();assertEquals(1,fw.migrate().migrationsExecuted);fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
      try(var c=connect(upgrade)) {
        assertEquals(journal,value(c,"SELECT jsonb_agg(to_jsonb(j) ORDER BY id)::text FROM d2.journal j"));assertEquals(config,value(c,"SELECT config_snapshot::text FROM planning_runs WHERE id=?",pid));assertEquals(dispatch,value(c,"SELECT jsonb_agg(to_jsonb(d))::text FROM d3.dispatches d"));
        DISPATCH.execute(c,id(),claimed,"START",Map.of());assertEquals("RUNNING",value(c,"SELECT state FROM operations WHERE id=?",operation));assertEquals("0",value(c,"SELECT count(*) FROM d3.planning_requests"));
      }
    } finally {try(var c=connect("postgres")){sql(c,"DROP DATABASE "+upgrade+" WITH (FORCE)");}}
  }
}
