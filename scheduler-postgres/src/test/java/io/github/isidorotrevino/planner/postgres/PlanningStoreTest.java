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

class PlanningStoreTest {
  static final Path ROOT=Path.of(System.getProperty("planner.root","..")).toAbsolutePath().normalize();
  static final String URL=Objects.requireNonNull(System.getProperty("d3.url"),"Use testing/D3/run-postgres-tests.sh or supply d3.url for disposable PostgreSQL");
  static final PlanningStore STORE=new PlanningStore();
  String db; UUID project,task,operation,worker,resource,account;Instant observed;
  static Connection connect(String db) throws SQLException {return DriverManager.getConnection(URL+db,"d2_auditor","");}
  Connection owner() throws SQLException {return connect(db);}
  Connection runtime() throws SQLException {var c=owner();sql(c,"SET ROLE d3_planner_test;SET statement_timeout=10000");return c;}
  static UUID id(){return UUID.randomUUID();}
  static void sql(Connection c,String sql,Object...args) throws SQLException {try(var p=c.prepareStatement(sql)){bind(p,args);p.execute();}}
  static String value(Connection c,String sql,Object...args) throws SQLException {try(var p=c.prepareStatement(sql)){bind(p,args);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}}}
  static void bind(PreparedStatement p,Object...args) throws SQLException {for(int i=0;i<args.length;i++){var v=args[i];p.setObject(i+1,v instanceof Instant t?t.atOffset(ZoneOffset.UTC):v);}}
  static UUID insert(Connection c,String sql,Object...args) throws SQLException {return UUID.fromString(value(c,sql+" RETURNING id",args));}
  @BeforeAll static void initializeTemplate() throws Exception {
    var fw=Flyway.configure().dataSource(URL+"d3_template","d2_auditor","").cleanDisabled(true)
      .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-proposed")).load();
    fw.migrate();fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
    try(var c=connect("d3_template")) {
      assertEquals("12",value(c,"SELECT count(*) FROM flyway_schema_history WHERE success"));
      sql(c,"CREATE ROLE d3_planner_test NOLOGIN;GRANT USAGE ON SCHEMA public,d3 TO d3_planner_test;GRANT EXECUTE ON FUNCTION d3.capture(uuid,jsonb),d3.read_capture(uuid),d3.publish(uuid,jsonb),d3.observe_eligibility(uuid) TO d3_planner_test");
    }
  }
  @BeforeEach void setup() throws Exception {
    db="d3_case_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+db+" TEMPLATE d3_template");}
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
  @Test void typedSnapshotUsesD2GuardsAndNestedJsonCapabilities() throws Exception {
    var plan=plan();assertEquals(Status.COMPLETE,plan.result().status());assertEquals(1,plan.result().decisions().size());
    assertEquals(Disposition.TENTATIVE,plan.result().decisions().getFirst().disposition());
    assertTrue(plan.capture().snapshot().resources().getFirst().capabilities().contains("op:"+operation));
    try(var c=runtime()){assertEquals(plan.capture(),STORE.read(c,plan.capture().id()));}
  }
  @Test void publishCreatesFrozenSnapshotAndNoPhysicalReservation() throws Exception {
    var plan=plan();var published=publish(plan);
    try(var c=owner()) {
      assertEquals("PUBLISHED",value(c,"SELECT status FROM planning_runs WHERE id=?",published));
      assertEquals(published.toString(),value(c,"SELECT planning_run_id FROM d3.plan_head"));
      assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("0",value(c,"SELECT count(*) FROM d2.journal"));
      assertEquals("1",value(c,"SELECT count(*) FROM d2.budget_accounts WHERE planning_run_id=?",published));
      assertNull(value(c,"SELECT estimated_capacity FROM capacity_budgets WHERE planning_run_id=?",published));
      assertEquals("1",value(c,"SELECT count(*) FROM outbox_events WHERE event_type='PLAN_PUBLISHED' AND aggregate_id=?",published));
      var e=assertThrows(SQLException.class,()->sql(c,"UPDATE d3.plan_manifests SET result='{}' WHERE planning_run_id=?",published));assertEquals("55000",e.getSQLState());
      assertEquals("55000",assertThrows(SQLException.class,()->sql(c,"UPDATE schedule_entries SET reason='{}' WHERE planning_run_id=?",published)).getSQLState());
    }
  }
  @Test void successorIsAtomicAndHistoricalSnapshotRemainsImmutable() throws Exception {
    var first=publish(plan());String oldConfig;try(var c=owner()){oldConfig=value(c,"SELECT config_snapshot::text FROM planning_runs WHERE id=?",first);}
    var second=publish(plan());
    try(var c=owner()){assertEquals("SUPERSEDED",value(c,"SELECT status FROM planning_runs WHERE id=?",first));assertEquals(second.toString(),value(c,"SELECT superseded_by FROM planning_runs WHERE id=?",first));assertEquals(oldConfig,value(c,"SELECT config_snapshot::text FROM planning_runs WHERE id=?",first));assertEquals("1",value(c,"SELECT count(*) FROM planning_runs WHERE status='PUBLISHED'"));}
  }
  @Test void publishReplayIsIdempotentAndConflictingPayloadRejected() throws Exception {
    var plan=plan();var cmd=id();var pid=id();
    try(var c=runtime()) {assertEquals(pid,STORE.publish(c,cmd,pid,plan.capture(),plan.result()));assertEquals(pid,STORE.publish(c,cmd,pid,plan.capture(),plan.result()));assertEquals("23505",assertThrows(SQLException.class,()->STORE.publish(c,cmd,id(),plan.capture(),plan.result())).getSQLState());}
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM planning_runs"));}
  }
  @Test void phantomOperationInsertionInvalidatesEntireSnapshot() throws Exception {
    var p=plan();try(var c=owner()){sql(c,"INSERT INTO operations(task_id,operation_type,idempotency_key) VALUES(?,'NEW',?)",task,id().toString());}rejectedPublication(p,"40001");
  }
  @Test void phantomDependencyDeletionInvalidatesSnapshot() throws Exception {
    UUID predecessor;try(var c=owner()){predecessor=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'pre','pre')",project);sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES(?,?,'SOFT')",predecessor,task);}
    var p=plan();try(var c=owner()){sql(c,"DELETE FROM task_dependencies WHERE predecessor_task_id=?",predecessor);}rejectedPublication(p,"40001");
  }
  @Test void priorityChangedWithoutVersionBumpStillInvalidatesHash() throws Exception {
    var p=plan();try(var c=owner()){sql(c,"UPDATE projects SET priority='P0' WHERE id=?",project);}rejectedPublication(p,"40001");
  }
  @Test void recalibrationKeepsConsumptionAndForcesRecalculation() throws Exception {
    var p=plan();try(var c=owner()){value(c,"SELECT d2.recalibrate(?,?::jsonb)",id(),Json.write(Map.of("account_id",account,"capacity",5,"confidence",new java.math.BigDecimal(".95"),"evidence_sha256","a".repeat(64),"reason","Synthetic reduction")));}rejectedPublication(p,"40001");
    assertEquals(Disposition.DEFERRED,plan().result().decisions().getFirst().disposition());
  }
  @Test void changedApprovalOrCapabilityEvidenceCannotPublishAnOldCalculation() throws Exception {
    var p=plan();try(var c=owner()){sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||'{\"requires_approval\":true}' WHERE id=?",operation);}rejectedPublication(p,"40001");
    assertTrue(plan().result().decisions().getFirst().reasons().contains(Reason.STALE_APPROVAL));
  }
  @Test void newCapabilityInvalidationEvidenceInvalidatesCapture() throws Exception {
    var p=plan();try(var c=owner()){
      var cap=insert(c,"INSERT INTO capabilities(provider_project_id,capability_key) VALUES(?,'cap')",project);
      var version=insert(c,"INSERT INTO capability_versions(capability_id,version,environment,contract_sha256) VALUES(?,'1.0.0','test',repeat('b',64))",cap);
      sql(c,"INSERT INTO d2.capability_epochs(version_id,epoch) VALUES(?,1)",version);
    }rejectedPublication(p,"40001");
  }
  @Test void carriedReservationsAreLinkedAcrossPlansWithoutReservingAgain() throws Exception {
    try(var c=owner()){sql(c,"INSERT INTO d2.operation_accounts VALUES(?,?,10,'manual-v1')",operation,account);value(c,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","CLAIM","operation_id",operation,"worker_id",worker,"resource_id",resource)));}
    var p=plan();assertEquals(Disposition.CARRIED,p.result().decisions().getFirst().disposition());publish(p);publish(plan());
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("1",value(c,"SELECT count(*) FROM d2.journal WHERE commitment_delta>0"));assertEquals("2",value(c,"SELECT count(*) FROM d2.plan_reservations"));assertEquals("10.0000",value(c,"SELECT outstanding::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));}
  }
  @Test void tamperedIncrementalDemandRollsBackAllPlanChildren() throws Exception {
    var p=plan();try(var c=runtime()){
      var request=rawRequest(id(),p.capture(),p.result());
      var e=assertThrows(SQLException.class,()->value(c,"SELECT d3.publish(?,jsonb_set(?::jsonb,ARRAY['result','decisions','0','incrementalDemand',?::text],'0'::jsonb))",id(),request,account.toString()));assertEquals("23514",e.getSQLState(),e.getMessage());
    }
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM planning_runs"));assertEquals("0",value(c,"SELECT count(*) FROM capacity_budgets"));assertEquals("0",value(c,"SELECT count(*) FROM d3.plan_manifests"));}
  }
  @Test void runtimeHasNoAccountingConfigurationOrDirectDmlBypass() throws Exception {
    try(var c=runtime()) {
      for(var statement:List.of("SELECT * FROM d2.journal","UPDATE projects SET priority='P0'","UPDATE d3.settings SET calibration_epoch='unsafe'","SELECT d2.execution(gen_random_uuid(),'{}')","SELECT d3.configure(gen_random_uuid(),'{}')","SELECT d3.state_body()"))
        assertEquals("42501",assertThrows(SQLException.class,()->value(c,statement)).getSQLState(),statement);
    }
  }
  @Test void failedLaterStatementCanRollbackPublicationAndOutboxTogether() throws Exception {
    var p=plan();try(var c=owner()){c.setAutoCommit(false);value(c,"SELECT d3.publish(?,?::jsonb)",id(),rawRequest(id(),p.capture(),p.result()));sql(c,"SELECT 1");c.rollback();}
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM planning_runs"));assertEquals("0",value(c,"SELECT count(*) FROM outbox_events WHERE event_type='PLAN_PUBLISHED'"));}
  }
  @Test void adapterRefusesTransactionsThatWouldHoldLocksAcrossCalculation() throws Exception {
    try(var c=runtime()){c.setAutoCommit(false);assertEquals("25001",assertThrows(SQLException.class,()->STORE.capture(c,id())).getSQLState());c.rollback();}
  }
  @Test void twoConcurrentPublishersHaveOneCommittedSuccessor() throws Exception {
    var p=plan();var gate=new CountDownLatch(1);
    try(var pool=Executors.newFixedThreadPool(2)){
      var calls=new ArrayList<Future<String>>();for(int i=0;i<2;i++)calls.add(pool.submit(()->{gate.await();try(var c=runtime()){STORE.publish(c,id(),id(),p.capture(),p.result());return "PUBLISHED";}catch(SQLException e){return e.getSQLState();}}));
      gate.countDown();var results=new ArrayList<String>();for(var call:calls)results.add(call.get(15,TimeUnit.SECONDS));Collections.sort(results);assertEquals(List.of("40001","PUBLISHED"),results);
    }
    try(var c=owner()){assertEquals("1",value(c,"SELECT count(*) FROM planning_runs WHERE status='PUBLISHED'"));}
  }
  @Test void publicationWaitingForAClaimRevalidatesAfterClaimCommits() throws Exception {
    var p=plan();try(var claimant=owner()){
      claimant.setAutoCommit(false);sql(claimant,"SELECT pg_advisory_xact_lock(742002)");
      sql(claimant,"INSERT INTO d2.operation_accounts VALUES(?,?,10,'manual-v1')",operation,account);
      value(claimant,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","CLAIM","operation_id",operation,"worker_id",worker,"resource_id",resource)));
      try(var pool=Executors.newSingleThreadExecutor()){
        var submitted=new CountDownLatch(1);var backend=new java.util.concurrent.atomic.AtomicInteger();var pending=pool.submit(()->{try(var c=runtime()){backend.set(Integer.parseInt(value(c,"SELECT pg_backend_pid()")));submitted.countDown();STORE.publish(c,id(),id(),p.capture(),p.result());return "PUBLISHED";}catch(SQLException e){return e.getSQLState();}});
        assertTrue(submitted.await(5,TimeUnit.SECONDS));awaitLock(backend.get());claimant.commit();assertEquals("40001",pending.get(15,TimeUnit.SECONDS));
      }
    }
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM planning_runs"));assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));}
  }
  void awaitLock(int backend) throws Exception {
    long deadline=System.nanoTime()+Duration.ofSeconds(5).toNanos();
    try(var c=owner()) {
      while(System.nanoTime()<deadline) {
        if("true".equals(value(c,"SELECT EXISTS(SELECT 1 FROM pg_locks WHERE pid=? AND NOT granted)::text",backend)))return;
        Thread.sleep(5);
      }
    }
    fail("Publication backend never reached the expected lock wait");
  }
  void waitsForMutation(java.util.function.Consumer<Connection> mutation) throws Exception {
    var p=plan();
    try(var modifier=owner()) {
      modifier.setAutoCommit(false);sql(modifier,"SELECT pg_advisory_xact_lock(742002)");mutation.accept(modifier);
      try(var pool=Executors.newSingleThreadExecutor()) {
        var ready=new CountDownLatch(1);var backend=new java.util.concurrent.atomic.AtomicInteger();
        var publication=pool.submit(()->{try(var c=runtime()){backend.set(Integer.parseInt(value(c,"SELECT pg_backend_pid()")));ready.countDown();STORE.publish(c,id(),id(),p.capture(),p.result());return "PUBLISHED";}catch(SQLException e){return e.getSQLState();}});
        assertTrue(ready.await(5,TimeUnit.SECONDS));awaitLock(backend.get());modifier.commit();assertEquals("40001",publication.get(15,TimeUnit.SECONDS));
      }
    }
  }
  @Test void concurrentRecalibrationIsRevalidatedAfterMutexWait() throws Exception {
    waitsForMutation(c->{try{value(c,"SELECT d2.recalibrate(?,?::jsonb)",id(),Json.write(Map.of("account_id",account,"capacity",5,"confidence",new java.math.BigDecimal(".95"),"evidence_sha256","a".repeat(64),"reason","Synthetic concurrent reduction")));}catch(SQLException e){throw new RuntimeException(e);}});
  }
  @Test void concurrentCapabilityInvalidationBlocksOldPublicationAndNewAdmission() throws Exception {
    UUID version;try(var c=owner()) {
      var cap=insert(c,"INSERT INTO capabilities(provider_project_id,capability_key) VALUES(?,'compatible-cap')",project);
      version=insert(c,"INSERT INTO capability_versions(capability_id,version,environment,contract_sha256) VALUES(?,'1.2.3','test',repeat('b',64))",cap);
      sql(c,"INSERT INTO d2.capability_epochs(version_id) VALUES(?)",version);
      sql(c,"INSERT INTO d2.verifications(version_id,epoch,environment,contract_sha256,evidence_sha256,outcome) VALUES(?,0,'test',repeat('b',64),repeat('c',64),'PASS')",version);
      int rowVersion=0;String current="PLANNED";for(var next:List.of("IMPLEMENTED","VERIFIED","AVAILABLE")) {
        value(c,"SELECT d2.transition(?,?::jsonb)",id(),Json.write(Map.of("entity_type","CAPABILITY_VERSION","entity_id",version,"from",current,"to",next,"expected_version",rowVersion,"actor","SYNTHETIC","reason","Synthetic verified capability")));current=next;rowVersion++;
      }
      var requirement=insert(c,"INSERT INTO capability_requirements(consumer_task_id,capability_id,version_constraint,environment,kind) VALUES(?,?,'^1.0.0','test','HARD')",task,cap);
      sql(c,"INSERT INTO d2.resolutions VALUES(?,?)",requirement,version);
    }
    waitsForMutation(c->{try{value(c,"SELECT d2.transition(?,?::jsonb)",id(),Json.write(Map.of("entity_type","CAPABILITY_VERSION","entity_id",version,"from","AVAILABLE","to","INVALIDATED","expected_version",3,"actor","SYNTHETIC","reason","Synthetic invalidation")));}catch(SQLException e){throw new RuntimeException(e);}});
    assertEquals(Disposition.BLOCKED,plan().result().decisions().getFirst().disposition());
  }
  @Test void directWriterWithoutMutexIsCoveredByRelationLocksAndFullHash() throws Exception {
    var p=plan();try(var writer=owner()) {
      writer.setAutoCommit(false);sql(writer,"UPDATE projects SET priority='P0' WHERE id=?",project);
      try(var pool=Executors.newSingleThreadExecutor()) {
        var ready=new CountDownLatch(1);var backend=new java.util.concurrent.atomic.AtomicInteger();
        var publication=pool.submit(()->{try(var c=runtime()){backend.set(Integer.parseInt(value(c,"SELECT pg_backend_pid()")));ready.countDown();STORE.publish(c,id(),id(),p.capture(),p.result());return "PUBLISHED";}catch(SQLException e){return e.getSQLState();}});
        assertTrue(ready.await(5,TimeUnit.SECONDS));awaitLock(backend.get());writer.commit();assertEquals("40001",publication.get(15,TimeUnit.SECONDS));
      }
    }
  }
  @Test void expiredEligibilitySampleCannotAccrueUnobservedWaitingTime() throws Exception {
    try(var c=owner()) {
      sql(c,"INSERT INTO d3.eligibility_ticks(operation_id,eligible,observed_at,valid_until,command_id) VALUES(?,true,clock_timestamp()-interval '10 minutes',clock_timestamp()-interval '9 minutes',(SELECT id FROM d3.commands LIMIT 1))",operation);
    }
    var waited=plan().capture().snapshot().operations().getFirst().eligibleWait();assertTrue(waited.compareTo(Duration.ofSeconds(59))>=0);assertTrue(waited.compareTo(Duration.ofSeconds(61))<0);
  }
  @Test void eligibilityObservationStopsAtHeartbeatValidityAndIsIdempotent() throws Exception {
    try(var c=runtime()) {var cmd=id();var first=STORE.observeEligibility(c,cmd);assertEquals(first,STORE.observeEligibility(c,cmd));}
    try(var c=owner()) {
      assertEquals("1",value(c,"SELECT count(*) FROM d3.eligibility_ticks"));
      assertEquals("true",value(c,"SELECT bool_and(valid_until<=w.last_heartbeat_at+interval '90 seconds')::text FROM d3.eligibility_ticks t CROSS JOIN workers w WHERE w.id=?",worker));
      sql(c,"UPDATE workers SET last_heartbeat_at=clock_timestamp()-interval '2 minutes' WHERE id=?",worker);
    }
    try(var c=runtime()){STORE.observeEligibility(c,id());}
    try(var c=owner()){assertEquals("false",value(c,"SELECT eligible::text FROM d3.eligibility_ticks ORDER BY id DESC LIMIT 1"));}
  }
  @Test void immutableCaptureCanBeReadAfterLiveDataChanges() throws Exception {
    var p=plan();try(var c=owner()){sql(c,"UPDATE projects SET priority='P0' WHERE id=?",project);}
    try(var c=runtime()){assertEquals(p.capture(),STORE.read(c,p.capture().id()));}
  }
  @Test void newEpochPreservesJournalAndEligibleHistory() throws Exception {
    try(var c=owner()){
      STORE.observeEligibility(c,id());var ticks=value(c,"SELECT count(*) FROM d3.eligibility_ticks");
      STORE.configure(c,id(),Map.of("action","PROFILE","reason","Synthetic recalibration epoch","epoch_id",id(),"calibration_epoch","manual-v2","policy",Map.of("schema_version",SCHEMA_VERSION,"timezone","Europe/Madrid","max_operations",1000,"max_edges",5000,"max_candidates",4000,"max_compute_ms",30000)));
      assertEquals(ticks,value(c,"SELECT count(*) FROM d3.eligibility_ticks"));assertEquals("2",value(c,"SELECT count(*) FROM d3.fairness_epochs"));
    }
    assertEquals("manual-v2",plan().capture().request().calibrationEpoch());
  }
  @Test void sessionTimezoneDoesNotChangeBasisHashOrCapturedInstants() throws Exception {
    PlanningStore.Captured captured;try(var c=runtime()){sql(c,"SET TIME ZONE 'Europe/Madrid'");captured=STORE.capture(c,id());}
    try(var c=runtime()) {
      sql(c,"SET TIME ZONE 'America/New_York'");assertEquals(captured,STORE.read(c,captured.id()));
      var result=new CapacityScheduler().plan(captured.request(),captured.snapshot());STORE.publish(c,id(),id(),captured,result);
    }
  }
  @Test void approvalCanExpireWithoutChangingAnyRowAndPublicationStillRejectsIt() throws Exception {
    try(var c=owner()) {
      sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||'{\"requires_approval\":true}' WHERE id=?",operation);
      sql(c,"INSERT INTO approvals(operation_id,state,reason,requested_at,decided_at,decided_by,expires_at,context_snapshot_sha256,policy_snapshot_sha256) SELECT id,'APPROVED','Synthetic approval',clock_timestamp()-interval '5 seconds',clock_timestamp()-interval '1 second','SYNTHETIC',clock_timestamp()+interval '2 seconds',context_pack_sha256,encode(digest(policy_snapshot::text,'sha256'),'hex') FROM operations WHERE id=?",operation);
    }
    var p=plan();assertEquals(Disposition.TENTATIVE,p.result().decisions().getFirst().disposition());
    try(var c=owner()){sql(c,"SELECT pg_sleep(2.1)");}rejectedPublication(p,"40001");
  }
  @Test void reservationLaneUsageSurvivesEpochChanges() throws Exception {
    try(var c=owner()) {
      sql(c,"INSERT INTO d2.operation_accounts VALUES(?,?,10,'manual-v1')",operation,account);
      value(c,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","CLAIM","operation_id",operation,"worker_id",worker,"resource_id",resource)));
      var reservation=UUID.fromString(value(c,"SELECT id FROM d2.reservations WHERE operation_id=?",operation));
      STORE.configure(c,id(),Map.of("action","ATTRIBUTE_LEGACY","reservation_id",reservation,"lane","URGENT","reason","Synthetic historical attribution"));
      var before=value(c,"SELECT units::text FROM d3.lane_usage WHERE account_id=? AND lane='URGENT'",account);
      STORE.configure(c,id(),Map.of("action","PROFILE","reason","Synthetic epoch keeps physical lane usage","epoch_id",id(),"calibration_epoch","manual-v2","policy",Map.of("schema_version",SCHEMA_VERSION,"timezone","Europe/Madrid","max_operations",1000,"max_edges",5000,"max_candidates",4000,"max_compute_ms",30000)));
      assertEquals(before,value(c,"SELECT units::text FROM d3.lane_usage WHERE account_id=? AND lane='URGENT'",account));
    }
    assertEquals(Lane.URGENT,plan().capture().snapshot().reservations().getFirst().originalLane());
  }
  @ParameterizedTest @ValueSource(strings={"APPLIED","UNKNOWN"})
  void contradictoryEffectReceiptCannotBeMaskedByAnEarlierAbsence(String contradiction) throws Exception {
    try(var c=owner()) {
      sql(c,"INSERT INTO d2.operation_accounts VALUES(?,?,10,'manual-v1')",operation,account);
      value(c,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","CLAIM","operation_id",operation,"worker_id",worker,"resource_id",resource)));
      sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second' WHERE operation_id=?",operation);
      value(c,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","EXPIRE","operation_id",operation,"worker_id",worker,"resource_id",resource)));
      var receipt=insert(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) SELECT id,lease_generation,'synthetic','ABSENT','synthetic-proof' FROM operations WHERE id=?",operation);
      value(c,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","RECONCILE","operation_id",operation,"receipt_id",receipt,"worker_id",worker,"resource_id",resource)));
      value(c,"SELECT d2.transition(?,?::jsonb)",id(),Json.write(Map.of("entity_type","OPERATION","entity_id",operation,"from","RETRY_PENDING","to","READY","expected_version",Integer.parseInt(value(c,"SELECT row_version FROM operations WHERE id=?",operation)),"actor","SYNTHETIC","reason","Synthetic retry after absence")));
      sql(c,"INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) SELECT id,lease_generation,'synthetic',?,'synthetic-new-proof' FROM operations WHERE id=?",contradiction,operation);
    }
    var result=plan().result();assertEquals(Disposition.BLOCKED,result.decisions().getFirst().disposition());assertTrue(result.decisions().getFirst().reasons().contains(Reason.RETRY_UNSAFE));
  }
  @Test void upgradeFromV11KeepsLegacyReservationAndJournalIntact() throws Exception {
    var upgrade="d3_upgrade_"+id().toString().replace("-","");
    try(var admin=connect("postgres")){sql(admin,"CREATE DATABASE "+upgrade);}
    try {
      var config=Flyway.configure().dataSource(URL+upgrade,"d2_auditor","").cleanDisabled(true)
        .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-proposed"));
      config.target("11").load().migrate();String journal;
      try(var c=connect(upgrade)) {
        var p=insert(c,"INSERT INTO projects(code,name,workflow_type) VALUES(?,'Legacy synthetic','GENTLE_AI')",id().toString());
        var t=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'legacy','Legacy task')",p);
        var w=insert(c,"INSERT INTO workers(worker_key,host_name,state,last_heartbeat_at) VALUES(?,'synthetic','ONLINE',clock_timestamp())",id().toString());
        var r=insert(c,"INSERT INTO resources(resource_key,worker_id,provider,subscription) VALUES(?,?,'SYNTHETIC','none')",id().toString(),w);
        var o=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref) VALUES(?,'CODE',?,repeat('a',64),'synthetic-context')",t,id().toString());
        var a=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'execution','OPERATIONS','WEEKLY','legacy',clock_timestamp()-interval '1 hour',clock_timestamp()+interval '10 days','SYNTHETIC',0.95,100)",r);
        sql(c,"INSERT INTO d2.operation_accounts VALUES(?,?,10,'manual-v1')",o,a);
        value(c,"SELECT d2.execution(?,?::jsonb)",id(),Json.write(Map.of("action","CLAIM","operation_id",o,"worker_id",w,"resource_id",r)));
        journal=value(c,"SELECT jsonb_agg(to_jsonb(j) ORDER BY id)::text FROM d2.journal j");
      }
      var updated=Flyway.configure().dataSource(URL+upgrade,"d2_auditor","").cleanDisabled(true)
        .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-proposed")).load();
      assertEquals(1,updated.migrate().migrationsExecuted);updated.validate();
      try(var c=connect(upgrade)) {
        assertEquals(journal,value(c,"SELECT jsonb_agg(to_jsonb(j) ORDER BY id)::text FROM d2.journal j"));
        STORE.configure(c,id(),Map.of("action","PROFILE","reason","Explicit legacy unattributed epoch","epoch_id",id(),"calibration_epoch","manual-v1","policy",Map.of("schema_version",SCHEMA_VERSION,"timezone","Europe/Madrid","max_operations",1000,"max_edges",5000,"max_candidates",4000,"max_compute_ms",30000)));
        var captured=STORE.capture(c,id());var result=new CapacityScheduler().plan(captured.request(),captured.snapshot());
        assertEquals(Disposition.CARRIED,result.decisions().getFirst().disposition());assertTrue(result.diagnostics().contains(Reason.FAIRNESS_HISTORY_INCOMPLETE));
        STORE.publish(c,id(),id(),captured,result);
        assertEquals(journal,value(c,"SELECT jsonb_agg(to_jsonb(j) ORDER BY id)::text FROM d2.journal j"));assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));
      }
    } finally {try(var c=connect("postgres")){sql(c,"DROP DATABASE "+upgrade+" WITH (FORCE)");}}
  }
  @ParameterizedTest @ValueSource(booleans={false,true})
  void p4ExceptionRequiresAnActiveHigherPriorityConsumer(boolean active) throws Exception {
    UUID consumer;try(var c=owner()) {
      sql(c,"UPDATE projects SET priority='P4' WHERE id=?",project);
      var p=insert(c,"INSERT INTO projects(code,name,workflow_type,priority,status) VALUES(?,'Synthetic consumer','GENTLE_AI','P0',?)",id().toString(),active?"ACTIVE":"PAUSED");
      consumer=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'consumer','consumer')",p);
      sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES(?,?,'HARD')",task,consumer);
    }
    var p=plan();if(active){assertEquals(Disposition.TENTATIVE,p.result().decisions().getFirst().disposition());publish(p);return;}
    assertEquals(Disposition.BLOCKED,p.result().decisions().getFirst().disposition());
    var forged=new Decision(operation,Disposition.TENTATIVE,List.of(Reason.SELECTED),resource,Pool.PLANNED,Lane.WEIGHTED,
      new Interval(p.capture().request().asOf(),p.capture().request().asOf().plusSeconds(900)),new Priority(java.math.BigDecimal.ZERO,new java.math.BigDecimal("8"),List.of(taskNode(task),taskNode(consumer))),
      Map.of(account,new java.math.BigDecimal("10")),Map.of(),Map.of(),Rational.ZERO,null,List.of(),new java.math.BigDecimal(".95"));
    var old=p.result();var result=new Result(old.schemaVersion(),old.algorithmVersion(),Status.COMPLETE,true,old.policyHash(),old.calibrationEpoch(),old.asOf(),old.horizonEnd(),List.of(forged),old.knownVirtualBalances(),old.unknownBalances(),old.diagnostics());
    rejectedPublication(new Plan(p.capture(),result),"40001");
  }
  @Test void jsonSerializationEscapesControlCharactersAndPreservesDecimals() throws Exception {
    var text="quoted \" text \\ line\n\t\u0001 á";var encoded=Json.write(Map.of("text",text,"decimal",new java.math.BigDecimal("0.0001")));
    try(var c=owner()){assertEquals(text,value(c,"SELECT (?::jsonb)->>'text'",encoded));assertEquals("0.0001",value(c,"SELECT (?::jsonb)->>'decimal'",encoded));}
  }
}
