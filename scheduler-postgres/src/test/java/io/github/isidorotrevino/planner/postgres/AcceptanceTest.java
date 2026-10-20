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

class AcceptanceTest {
  static final Path ROOT=Path.of(System.getProperty("planner.root","..")).toAbsolutePath().normalize();
  static final String URL=Objects.requireNonNull(System.getProperty("d3.url"),"Use testing/D3/run-postgres-tests.sh or supply d3.url for disposable PostgreSQL");
  static final PlanningStore STORE=new PlanningStore();
  String db; UUID project,task,operation,worker,resource,account;Instant observed;
  static Connection connect(String db) throws SQLException {return DriverManager.getConnection(URL+db,"d2_auditor","");}
  Connection owner() throws SQLException {return connect(db);}
  Connection runtime() throws SQLException {var c=owner();sql(c,"SET ROLE d3_acceptance_test;SET statement_timeout=10000");return c;}
  static UUID id(){return UUID.randomUUID();}
  static void sql(Connection c,String sql,Object...args) throws SQLException {try(var p=c.prepareStatement(sql)){bind(p,args);p.execute();}}
  static String value(Connection c,String sql,Object...args) throws SQLException {try(var p=c.prepareStatement(sql)){bind(p,args);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}}}
  static void bind(PreparedStatement p,Object...args) throws SQLException {for(int i=0;i<args.length;i++){var v=args[i];p.setObject(i+1,v instanceof Instant t?t.atOffset(ZoneOffset.UTC):v);}}
  static UUID insert(Connection c,String sql,Object...args) throws SQLException {return UUID.fromString(value(c,sql+" RETURNING id",args));}
  static final DispatchStore DISPATCH=new DispatchStore();
  static final PlanningCoordinator COORD=new PlanningCoordinator();
  @BeforeAll static void initializeCoordinatorTemplate() throws Exception {
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE d3_acceptance_template");}
    var fw=Flyway.configure().dataSource(URL+"d3_acceptance_template","d2_auditor","").cleanDisabled(true)
      .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-dispatch-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-coordinator-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-review-proposed")).load();
    fw.migrate();fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
    try(var c=connect("d3_acceptance_template")) {
      assertEquals("15",value(c,"SELECT count(*) FROM flyway_schema_history WHERE success"));
      sql(c,"CREATE ROLE d3_acceptance_test NOLOGIN;GRANT USAGE ON SCHEMA public,d3 TO d3_acceptance_test;GRANT EXECUTE ON FUNCTION d3.read_capture(uuid),d3.enqueue_planning(uuid,jsonb),d3.poll_planning(uuid),d3.take_planning(uuid,jsonb),d3.prepare_planning(jsonb),d3.publish_planning(jsonb),d3.fail_planning(jsonb),d3.read_planning_request(uuid),d3.dispatch(uuid,jsonb),d3.execution(uuid,jsonb) TO d3_acceptance_test");
    }
  }
  @BeforeEach void setup() throws Exception {
    db="d3_case_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+db+" TEMPLATE d3_acceptance_template");}
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
  UUID transition(Connection c,String kind,UUID entity,String from,String to) throws SQLException {
    var table=kind.equals("INCIDENT")?"incidents":"tasks";
    var version=Integer.parseInt(value(c,"SELECT row_version FROM "+table+" WHERE id=?",entity));
    value(c,"SELECT d2.transition(?,?::jsonb)",id(),Json.write(Map.of("entity_type",kind,"entity_id",entity,"from",from,"to",to,"expected_version",version,"actor","SYNTHETIC","reason","Acceptance workflow")));return entity;
  }
  UUID reopen(Connection c,String severity) throws SQLException {
    var p=insert(c,"INSERT INTO projects(code,name,workflow_type) VALUES(?,'Synthetic incident','GENTLE_AI')",id().toString());
    var inc=insert(c,"INSERT INTO incidents(project_id,incident_key,severity) VALUES(?,'synthetic',?)",p,severity);
    String from="OPEN";for(var to:List.of("TRIAGED","INVESTIGATING","VERIFYING","RESOLVED","REOPENED")){transition(c,"INCIDENT",inc,from,to);from=to;}return inc;
  }
  @ParameterizedTest @ValueSource(strings={"SEV1","SEV2","SEV3","SEV4"})
  void reopeningUsesCurrentSeverityAndCriticalPathIsImmediate(String severity) throws Exception {
    UUID inc;UUID event;
    try(var c=owner()) {
      inc=reopen(c,severity);event=UUID.fromString(value(c,"SELECT id FROM outbox_events WHERE aggregate_id=? AND event_type='STATE_CHANGED' AND payload->>'to'='REOPENED'",inc));
      // Isolate the reopening from insertion's historical REPLAN_REQUIRED and SWEEP.
      sql(c,"INSERT INTO d3.planning_source_receipts(outbox_id,content_sha256,disposition) SELECT id,encode(digest(payload::text,'sha256'),'hex'),'IGNORED' FROM outbox_events WHERE id<>?",event);
      sql(c,"UPDATE d3.planning_clock SET last_sweep_at=clock_timestamp()");
    }
    try(var c=runtime()){COORD.poll(c,id());}
    var critical=severity.equals("SEV1")||severity.equals("SEV2");
    try(var c=owner()) {
      assertEquals(critical?"INCIDENT_CRITICAL":"INCIDENT_CHANGED",value(c,"SELECT kind FROM d3.planning_events WHERE id=?",event));
      assertEquals(Boolean.toString(critical),value(c,"SELECT (due_at<=clock_timestamp())::text FROM d3.planning_requests"));
      assertEquals(Boolean.toString(critical),value(c,"SELECT break_protection::text FROM d3.planning_requests"));
    }
    try(var c=runtime()){assertEquals(critical?PlanningCoordinator.State.PUBLISHED:PlanningCoordinator.State.IDLE,COORD.runOnce(c,id(),id()).state());}
  }
  @Test void integratedCoordinatorClaimVerifyAndSuccessorNeverDuplicateCapacity() throws Exception {
    UUID pid;try(var c=runtime()){pid=COORD.tick(c,id(),id(),id()).planId();assertNotNull(pid);}
    DispatchStore.Claimed d;try(var c=runtime()) {
      d=DISPATCH.claim(c,id(),pid,operation,resource,worker);DISPATCH.execute(c,id(),d,"START",Map.of());
      DISPATCH.execute(c,id(),d,"CALLBACK",Map.of("entries",List.of(Map.of("account_id",account,"settled",10,"consumed",8))));
    }
    try(var c=owner()){var artifact=insert(c,"INSERT INTO artifacts(artifact_ref,sha256,media_type) VALUES(?,repeat('a',64),'text/plain')",id().toString());sql(c,"INSERT INTO execution_evidence(attempt_id,artifact_id,evidence_type) VALUES(?,?,'ACCEPTANCE_PASS')",d.attemptId(),artifact);}
    try(var c=runtime()){DISPATCH.execute(c,id(),d,"VERIFY",Map.of());COORD.enqueue(c,id(),id(),ReplanPolicy.Kind.DEPENDENCY_CHANGED,observed,Map.of());}
    try(var c=owner()){sql(c,"UPDATE d3.planning_requests SET due_at=clock_timestamp()-interval '1 second' WHERE state='QUEUED'");}
    try(var c=runtime()){assertEquals(PlanningCoordinator.State.PUBLISHED,COORD.runOnce(c,id(),id()).state());}
    try(var c=owner()) {
      assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("1",value(c,"SELECT count(*) FROM d2.journal WHERE commitment_delta>0"));
      assertEquals("COMPLETED",value(c,"SELECT state FROM operations WHERE id=?",operation));assertEquals("SUPERSEDED",value(c,"SELECT status FROM planning_runs WHERE id=?",pid));
      assertEquals("62.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
      assertEquals("20.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='INCIDENT'",account));assertEquals("10.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='UNCERTAINTY'",account));
    }
  }
  @Test void inheritedP4UnlocksOnlyItsBlockingPathAndConsumerWaitsForEvidence() throws Exception {
    UUID consumer,consumerOp,sibling;
    try(var c=owner()) {
      sql(c,"UPDATE projects SET priority='P4' WHERE id=?",project);
      sibling=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'unrelated','unrelated')",project);
      var siblingOp=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) SELECT ?,'CODE',?,context_pack_sha256,context_pack_ref,policy_snapshot FROM operations WHERE id=?",sibling,id().toString(),operation);estimate(c,siblingOp,resource,account,10,null);
      var p0=insert(c,"INSERT INTO projects(code,name,workflow_type,priority) VALUES(?,'consumer','GENTLE_AI','P0')",id().toString());
      consumer=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'consumer','consumer')",p0);
      consumerOp=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) SELECT ?,'CODE',?,context_pack_sha256,context_pack_ref,policy_snapshot FROM operations WHERE id=?",consumer,id().toString(),operation);estimate(c,consumerOp,resource,account,10,null);
      sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES(?,?,'HARD')",task,consumer);
    }
    UUID pid;try(var c=runtime()){pid=COORD.tick(c,id(),id(),id()).planId();}
    try(var c=owner()) {
      assertEquals("1",value(c,"SELECT count(*) FROM schedule_entries WHERE planning_run_id=? AND operation_id=?",pid,operation));
      assertEquals("0",value(c,"SELECT count(*) FROM schedule_entries WHERE planning_run_id=? AND task_id IN (?,?)",pid,consumer,sibling));
      assertEquals("8",value(c,"SELECT reason->'priority'->>'effectiveWeight' FROM schedule_entries WHERE planning_run_id=? AND operation_id=?",pid,operation));
    }
    DispatchStore.Claimed d;try(var c=runtime()) {
      d=DISPATCH.claim(c,id(),pid,operation,resource,worker);DISPATCH.execute(c,id(),d,"START",Map.of());DISPATCH.execute(c,id(),d,"CALLBACK",Map.of("entries",List.of(Map.of("account_id",account,"settled",10,"consumed",8))));
    }
    try(var c=owner()) {
      var artifact=insert(c,"INSERT INTO artifacts(artifact_ref,sha256,media_type) VALUES(?,repeat('a',64),'text/plain')",id().toString());sql(c,"INSERT INTO execution_evidence(attempt_id,artifact_id,evidence_type) VALUES(?,?,'ACCEPTANCE_PASS')",d.attemptId(),artifact);
    }
    try(var c=runtime()){DISPATCH.execute(c,id(),d,"VERIFY",Map.of());}
    try(var c=owner()){String from="BACKLOG";for(var to:List.of("READY","IN_PROGRESS","VERIFYING","DONE")){transition(c,"TASK",task,from,to);from=to;}}
    try(var c=runtime()){COORD.enqueue(c,id(),id(),ReplanPolicy.Kind.DEPENDENCY_CHANGED,observed,Map.of());}
    try(var c=owner()){sql(c,"UPDATE d3.planning_requests SET due_at=clock_timestamp()-interval '1 second' WHERE state='QUEUED'");}
    try(var c=runtime()){var successor=COORD.runOnce(c,id(),id());assertEquals(PlanningCoordinator.State.PUBLISHED,successor.state());DISPATCH.claim(c,id(),successor.planId(),consumerOp,resource,worker);}
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM schedule_entries WHERE task_id=?",sibling));assertEquals("2",value(c,"SELECT count(*) FROM d2.reservations"));}
  }
  @Test void upgradeV14ToV15ChangesReopeningClassificationWithoutRewritingFacts() throws Exception {
    var upgrade="d3_review_upgrade_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+upgrade);}
    try {
      var locations=new String[]{"filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-dispatch-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-coordinator-proposed"),"filesystem:"+ROOT.resolve("migrations-d3-review-proposed")};
      Flyway.configure().dataSource(URL+upgrade,"d2_auditor","").locations(locations).target("14").load().migrate();
      UUID inc;String facts;
      try(var c=connect(upgrade)) {
        inc=reopen(c,"SEV1");assertEquals("INCIDENT_CHANGED",value(c,"SELECT d3.planning_event_kind(o) FROM outbox_events o WHERE aggregate_id=? AND payload->>'to'='REOPENED'",inc));
        sql(c,"INSERT INTO d3.planning_source_receipts(outbox_id,content_sha256,disposition) SELECT id,encode(digest(payload::text,'sha256'),'hex'),'IGNORED' FROM outbox_events WHERE NOT (aggregate_id=? AND payload->>'to'='REOPENED') OR payload->>'to' IS NULL",inc);
        sql(c,"UPDATE d3.planning_clock SET last_sweep_at=clock_timestamp()");value(c,"SELECT d3.poll_planning(?)",id());
        assertEquals("false",value(c,"SELECT break_protection::text FROM d3.planning_requests"));
        facts=value(c,"SELECT jsonb_agg(to_jsonb(o) ORDER BY id)::text FROM outbox_events o");
      }
      var fw=Flyway.configure().dataSource(URL+upgrade,"d2_auditor","").locations(locations).load();assertEquals(1,fw.migrate().migrationsExecuted);fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
      try(var c=connect(upgrade)) {
        assertEquals("INCIDENT_CRITICAL",value(c,"SELECT d3.planning_event_kind(o) FROM outbox_events o WHERE aggregate_id=? AND payload->>'to'='REOPENED'",inc));
        assertEquals(facts,value(c,"SELECT jsonb_agg(to_jsonb(o) ORDER BY id)::text FROM outbox_events o"));
        assertEquals("true",value(c,"SELECT (break_protection AND due_at<=clock_timestamp())::text FROM d3.planning_requests"));
        assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_events WHERE content->>'action'='V15_REOPENING_CORRECTION'"));
        assertEquals("1",value(c,"SELECT count(*) FROM d3.planning_events WHERE kind='INCIDENT_CHANGED'"));
      }
    } finally {try(var c=connect("postgres")){sql(c,"DROP DATABASE "+upgrade+" WITH (FORCE)");}}
  }
  @Test void simultaneousSessionAndWeeklyAccountsBlockWithoutPartialReservation() throws Exception {
    try(var c=owner()) {
      var session=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'execution','OPERATIONS','SESSION',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '1 day','test',.95,5)",resource,id().toString());
      var head=UUID.fromString(value(c,"SELECT estimate_id FROM d3.estimate_heads WHERE operation_id=? AND resource_id=?",operation,resource));
      STORE.configure(c,id(),Map.ofEntries(Map.entry("action","ESTIMATE"),Map.entry("reason","Two physical constraints"),Map.entry("estimate_id",id()),Map.entry("expected_estimate_id",head),Map.entry("operation_id",operation),Map.entry("resource_id",resource),Map.entry("units",Map.of(account,10,session,10)),Map.entry("duration_ms",900000),Map.entry("confidence",new java.math.BigDecimal(".95")),Map.entry("calibration_ref","manual-v1"),Map.entry("provenance","test"),Map.entry("observed_at",observed.minusSeconds(1)),Map.entry("valid_until",observed.plusSeconds(3600))));
    }
    UUID pid;try(var c=runtime()) {
      var result=COORD.tick(c,id(),id(),id());assertEquals(PlanningCoordinator.State.PUBLISHED,result.state());pid=result.planId();
      assertEquals("23514",assertThrows(SQLException.class,()->DISPATCH.claim(c,id(),pid,operation,resource,worker)).getSQLState());
    }
    try(var c=owner()){assertEquals("0",value(c,"SELECT count(*) FROM schedule_entries"));assertEquals("0",value(c,"SELECT count(*) FROM d2.journal"));assertEquals("0",value(c,"SELECT count(*) FROM d2.operation_accounts"));}
  }
  @Test void noninterruptibleLeaseIsCarriedWhileCriticalWorkWaitsWithoutForcedPreemption() throws Exception {
    DispatchStore.Claimed active;try(var c=runtime()) {
      var first=COORD.tick(c,id(),id(),id());active=DISPATCH.claim(c,id(),first.planId(),operation,resource,worker);DISPATCH.execute(c,id(),active,"START",Map.of());
    }
    UUID critical;
    try(var c=owner()) {
      var t=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,'critical','critical')",project);
      critical=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) SELECT ?,'FIX',?,context_pack_sha256,context_pack_ref,policy_snapshot FROM operations WHERE id=?",t,id().toString(),operation);estimate(c,critical,resource,account,10,null);
      var incident=insert(c,"INSERT INTO incidents(project_id,incident_key,severity) VALUES(?,'critical','SEV1')",project);sql(c,"INSERT INTO incident_task_links VALUES(?,?,'FIX')",incident,t);
    }
    try(var c=runtime()){assertEquals(PlanningCoordinator.State.PUBLISHED,COORD.tick(c,id(),id(),id()).state());}
    try(var c=owner()) {
      assertEquals("RUNNING",value(c,"SELECT state FROM operations WHERE id=?",operation));assertEquals(active.attemptId().toString(),value(c,"SELECT attempt_id FROM operation_leases WHERE operation_id=?",operation));
      assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("10.0000",value(c,"SELECT outstanding::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",account));
      assertEquals("0",value(c,"SELECT count(*) FROM schedule_entries e JOIN d3.plan_head h ON h.planning_run_id=e.planning_run_id WHERE e.operation_id=?",critical));
      assertEquals("0",value(c,"SELECT count(*) FROM d2.loans"));assertEquals("0",value(c,"SELECT count(*) FROM outbox_events WHERE event_type='PREEMPTION_RESULT'"));
    }
  }
}
