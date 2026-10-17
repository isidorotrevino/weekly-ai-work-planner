package audit;

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import java.nio.file.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
import static org.junit.jupiter.api.Assertions.*;

/** Schema audit only: acceptance of an invalid case is a reproduced finding. */
class SchemaAuditTest {
 static final Path ROOT=Path.of("../..").toAbsolutePath().normalize();
 static final String URL=System.getProperty("audit.url","jdbc:postgresql://127.0.0.1:55439/");
 static Connection open(String db) throws SQLException {return DriverManager.getConnection(URL+db,"d2_auditor","");}
 static void sql(Connection c,String s) throws SQLException {try(var st=c.createStatement()){st.execute(s);}}
 static String value(Connection c,String s) throws SQLException {try(var st=c.createStatement();var rs=st.executeQuery(s)){rs.next();return rs.getString(1);}}
 static String insert(Connection c,String table,String cols,String vals) throws SQLException {return value(c,"INSERT INTO "+table+"("+cols+") VALUES("+vals+") RETURNING id");}
 static String q(String s){return "'"+s+"'";}
 static final List<String> DBS=List.of("d2_baseline","d2_proposed");
 @BeforeAll static void migrate() throws Exception {
  for(String db:DBS){
   var config=Flyway.configure().dataSource(URL+db,"d2_auditor","").cleanDisabled(true);
   config.locations(db.equals("d2_baseline") ? new String[]{"filesystem:"+ROOT.resolve("migrations")}:
    new String[]{"filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed")});
   if(db.equals("d2_proposed"))config.target("5");
   var flyway=config.load();flyway.migrate();flyway.validate();assertEquals(0,flyway.migrate().migrationsExecuted);
   try(var c=open(db)){
    assertEquals("68",value(c,"SELECT count(*) FROM state_transition_rules"));
    assertEquals(db.equals("d2_baseline")?"4":"5",value(c,"SELECT count(*) FROM flyway_schema_history WHERE success"));
    assertTrue(Integer.parseInt(value(c,"SHOW server_version_num"))>=160000);
   }
  }
 }
 record F(String p,String p2,String t,String t2,String w,String w2,String r,String r2,
          String run,String b,String b2,String b3,String a,String o,String o2,String attempt){}
 static F fixture(Connection c) throws SQLException {
  String key=UUID.randomUUID().toString();
  String p=insert(c,"projects","code,name,workflow_type",q(key)+",'audit','GENTLE_AI'");
  String p2=insert(c,"projects","code,name,workflow_type",q(key+"b")+",'audit2','GENTLE_AI'");
  String t=insert(c,"tasks","project_id,task_key,title",q(p)+",'a','task'");
  String t2=insert(c,"tasks","project_id,task_key,title",q(p2)+",'b','task2'");
  String w=insert(c,"workers","worker_key,host_name",q(key)+",'audit'");
  String w2=insert(c,"workers","worker_key,host_name",q(key+"b")+",'audit2'");
  String r=insert(c,"resources","resource_key,worker_id,provider,subscription",q(key)+","+q(w)+",'audit','none'");
  String r2=insert(c,"resources","resource_key,worker_id,provider,subscription",q(key+"b")+","+q(w2)+",'audit','none'");
  String run=insert(c,"planning_runs","horizon_start,horizon_end,trigger_type,config_snapshot,config_sha256,solver_version","'2026-10-19Z','2026-10-26Z','AUDIT','{}',repeat('a',64),'audit'");
  String b=insert(c,"capacity_budgets","planning_run_id,resource_id,window_start,window_end,capacity_unit,estimated_capacity",q(run)+","+q(r)+",'2026-10-19Z','2026-10-20Z','OPERATIONS',100");
  String b2=insert(c,"capacity_budgets","planning_run_id,resource_id,window_start,window_end,capacity_unit,estimated_capacity",q(run)+","+q(r)+",'2026-10-20Z','2026-10-21Z','OPERATIONS',100");
  String b3=insert(c,"capacity_budgets","planning_run_id,resource_id,window_start,window_end,capacity_unit,estimated_capacity",q(run)+","+q(r2)+",'2026-10-19Z','2026-10-20Z','OPERATIONS',100");
  String a=insert(c,"capacity_allocations","planning_run_id,resource_id,project_id,pool,budget_id",q(run)+","+q(r)+","+q(p)+",'PLANNED',"+q(b));
  String o=insert(c,"operations","task_id,operation_type,idempotency_key,lease_generation",q(t)+",'AUDIT',"+q(key)+",1");
  String o2=insert(c,"operations","task_id,operation_type,idempotency_key",q(t2)+",'AUDIT',"+q(key+"b"));
  if(Set.of("d2_contract","d2_semver_upgrade").contains(c.getCatalog()))sql(c,"UPDATE operations SET context_pack_sha256=repeat('a',64),context_pack_ref='synthetic-context-v1' WHERE id="+q(o));
  String attempt=insert(c,"execution_attempts","operation_id,attempt_no,worker_id,resource_id,lease_generation,state",q(o)+",1,"+q(w)+","+q(r)+",1,'RUNNING'");
  return new F(p,p2,t,t2,w,w2,r,r2,run,b,b2,b3,a,o,o2,attempt);
 }
 interface StatementFactory{String make(F f);}
 record Scenario(String name,boolean baseAccept,boolean proposedAccept,StatementFactory statement){}
 static Scenario fixed(String name,StatementFactory s){return new Scenario(name,true,false,s);}
 static Scenario gap(String name,StatementFactory s){return new Scenario("OPEN_"+name,true,true,s);}
 static String movement(F f,String budget,String allocation,String operation,String attempt,String type,String source,String target,int units){
  return "INSERT INTO capacity_movements(budget_id,allocation_id,operation_id,attempt_id,movement_type,source_pool,target_pool,units,measurement,reason,correlation_key) VALUES("+
   q(budget)+","+allocation+","+operation+","+attempt+","+q(type)+","+q(source)+","+target+","+units+",'ESTIMATED','audit',"+q(UUID.randomUUID().toString())+")";
 }
 static List<Scenario> scenarios(){return List.of(
  fixed("allocation_without_budget",f->"INSERT INTO capacity_allocations(planning_run_id,resource_id,project_id,pool) VALUES("+q(f.run)+","+q(f.r)+","+q(f.p2)+",'PLANNED')"),
  fixed("movement_wrong_budget",f->movement(f,f.b3,q(f.a),"NULL","NULL","RESERVE","PLANNED","NULL",10)),
  fixed("movement_wrong_operation",f->movement(f,f.b,q(f.a),q(f.o2),q(f.attempt),"CONSUME","PLANNED","NULL",10)),
  fixed("lease_wrong_worker",f->"INSERT INTO operation_leases VALUES("+q(f.o)+","+q(f.attempt)+","+q(f.w2)+",1,now()+interval '1 minute')"),
  fixed("lease_wrong_generation",f->"INSERT INTO operation_leases VALUES("+q(f.o)+","+q(f.attempt)+","+q(f.w)+",2,now()+interval '1 minute')"),
  fixed("lease_negative_generation",f->"INSERT INTO operation_leases VALUES("+q(f.o)+","+q(f.attempt)+","+q(f.w)+",-1,now()+interval '1 minute')"),
  fixed("attempt_duplicate_generation",f->"INSERT INTO execution_attempts(operation_id,attempt_no,worker_id,resource_id,lease_generation,state) VALUES("+q(f.o)+",2,"+q(f.w)+","+q(f.r)+",1,'RUNNING')"),
  fixed("measurement_wrong_resource",f->"INSERT INTO capacity_measurements(resource_id,attempt_id,metric,value,provenance) VALUES("+q(f.r2)+","+q(f.attempt)+",'OPERATIONS',1,'LOCAL_METER')"),
  fixed("percentage_101",f->"INSERT INTO capacity_measurements(resource_id,metric,value,provenance) VALUES("+q(f.r)+",'QUOTA_REMAINING_PCT',101,'MANUAL')"),
  fixed("measurement_half_window",f->"INSERT INTO capacity_measurements(resource_id,metric,value,provenance,window_start) VALUES("+q(f.r)+",'OPERATIONS',1,'MANUAL',now())"),
  fixed("schedule_wrong_task",f->"INSERT INTO schedule_entries(planning_run_id,task_id,resource_id,operation_id,pool,priority_snapshot) VALUES("+q(f.run)+","+q(f.t2)+","+q(f.r)+","+q(f.o)+",'PLANNED','{}')"),
  fixed("approval_no_snapshot_or_expiry",f->"INSERT INTO approvals(operation_id,state,reason) VALUES("+q(f.o)+",'APPROVED','audit')"),
  fixed("resolved_without_timestamp",f->"INSERT INTO incidents(project_id,incident_key,severity,status) VALUES("+q(f.p)+",'a','SEV1','RESOLVED')"),
  new Scenario("multiple_allocation_windows",false,true,f->"INSERT INTO capacity_allocations(planning_run_id,resource_id,project_id,pool,budget_id) VALUES("+q(f.run)+","+q(f.r)+","+q(f.p)+",'PLANNED',"+q(f.b2)+")"),
  gap("arbitrary_task_transition",f->"UPDATE tasks SET status='DONE' WHERE id="+q(f.t)),
  gap("hard_dependency_cycle",f->"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES("+q(f.t)+","+q(f.t2)+",'HARD'),("+q(f.t2)+","+q(f.t)+",'HARD')"),
  gap("overreservation",f->movement(f,f.b,q(f.a),"NULL","NULL","RESERVE","PLANNED","NULL",1000)),
  gap("borrow_uncertainty",f->movement(f,f.b,"NULL","NULL","NULL","BORROW","UNCERTAINTY","'PLANNED'",10)),
  gap("phantom_transition_entity",f->"INSERT INTO state_transition_events(entity_type,entity_id,from_state,to_state,actor,reason) VALUES('TASK',gen_random_uuid(),'BACKLOG','READY','audit','audit')"),
  gap("available_without_evidence",f->"WITH c AS (INSERT INTO capabilities(provider_project_id,capability_key) VALUES("+q(f.p)+",'audit') RETURNING id) INSERT INTO capability_versions(capability_id,version,environment,state) SELECT id,'1.0.0','test','AVAILABLE' FROM c"),
  gap("cross_project_epic_requirement",f->"WITH e AS (INSERT INTO epics(project_id,epic_key,title) VALUES("+q(f.p)+",'e','e') RETURNING id),r AS (INSERT INTO requirements(project_id,requirement_key,title) VALUES("+q(f.p2)+",'r','r') RETURNING id) INSERT INTO epic_requirements SELECT e.id,r.id FROM e,r"),
  gap("mutate_published_snapshot",f->"UPDATE planning_runs SET status='PUBLISHED' WHERE id="+q(f.run)+"; UPDATE planning_runs SET config_snapshot='{\"changed\":true}' WHERE id="+q(f.run)),
  fixed("mutate_ledger",f->movement(f,f.b,q(f.a),"NULL","NULL","RESERVE","PLANNED","NULL",10)+"; UPDATE capacity_movements SET units=20 WHERE budget_id="+q(f.b)),
  gap("reserve_unknown_capacity",f->"UPDATE capacity_budgets SET estimated_capacity=NULL WHERE id="+q(f.b)+"; "+movement(f,f.b,q(f.a),"NULL","NULL","RESERVE","PLANNED","NULL",10))
 );}
 @TestFactory Stream<DynamicTest> characterize(){
  return DBS.stream().flatMap(db->scenarios().stream().map(s->DynamicTest.dynamicTest(db+"__"+s.name,()->{
   try(var c=open(db)){
    c.setAutoCommit(false);var f=fixture(c);boolean accepted=true;
    try{sql(c,s.statement.make(f));}catch(SQLException ex){accepted=false;assertTrue(Set.of("23502","23503","23505","23514","55000").contains(ex.getSQLState()),ex.toString());}
    finally{c.rollback();}
    assertEquals(db.equals("d2_baseline")?s.baseAccept:s.proposedAccept,accepted);
   }
  })));
 }
 @Test void twentyConcurrentLeaseInserts() throws Exception {
  for(String db:DBS){
   F f;try(var c=open(db)){f=fixture(c);}
   var start=new CountDownLatch(1);var results=new ArrayList<Future<Boolean>>();
   try(var pool=Executors.newFixedThreadPool(20)){
    for(int i=0;i<20;i++)results.add(pool.submit(()->{start.await();try(var c=open(db)){
     sql(c,"INSERT INTO operation_leases VALUES("+q(f.o)+","+q(f.attempt)+","+q(f.w)+",1,now()+interval '1 minute')");return true;
    }catch(SQLException e){assertEquals("23505",e.getSQLState());return false;}}));
    start.countDown();int successes=0;for(var result:results)if(result.get(15,TimeUnit.SECONDS))successes++;
    assertEquals(1,successes);
   }
  }
 }
 @Test void twoConcurrentReservationsCanOverbookWithoutGuard() throws Exception {
  for(String db:DBS){
   F f;try(var c=open(db)){f=fixture(c);}
   var start=new CountDownLatch(1);
   try(var pool=Executors.newFixedThreadPool(2)){
    var results=new ArrayList<Future<?>>();
    for(int i=0;i<2;i++)results.add(pool.submit(()->{start.await();try(var c=open(db)){
     sql(c,movement(f,f.b,q(f.a),"NULL","NULL","RESERVE","PLANNED","NULL",60));return null;}}));
    start.countDown();for(var result:results)result.get(15,TimeUnit.SECONDS);
   }
   try(var c=open(db)){assertEquals("120.0000",value(c,"SELECT sum(units) FROM capacity_movements WHERE budget_id="+q(f.b)));}
  }
 }
 @Test void transitionSeedMatchesDesignExactly() throws Exception {
  String doc=Files.readString(ROOT.resolve("docs/design/history/D2.4-transitions-integrity-tests.md"));
  var expected=new HashSet<String>();String type=null;
  var types=Map.of("### Task","TASK","### Operation","OPERATION","### Incident","INCIDENT","### Capability version","CAPABILITY_VERSION");
  for(String line:doc.lines().toList()){
   if(line.startsWith("## "))type=null;
   if(types.containsKey(line))type=types.get(line);
   if(type==null)continue;
   var matcher=java.util.regex.Pattern.compile("([A-Z_]+)→([A-Z_,]+)").matcher(line);
   while(matcher.find())for(String to:matcher.group(2).split(","))expected.add(type+":"+matcher.group(1)+">"+to);
  }
  assertEquals(68,expected.size());
  for(String db:DBS)try(var c=open(db);var st=c.createStatement();var rs=st.executeQuery("SELECT entity_type||':'||from_state||'>'||to_state FROM state_transition_rules")){
   var actual=new HashSet<String>();while(rs.next())actual.add(rs.getString(1));assertEquals(expected,actual);
  }
 }
 @Test void proposedBackfillRejectsAmbiguousWindow() throws Exception {
  try(var c=open("d2_baseline")){
   c.setAutoCommit(false);var f=fixture(c);
   sql(c,"UPDATE capacity_allocations SET budget_id=NULL WHERE id="+q(f.a));
   var e=assertThrows(SQLException.class,()->sql(c,Files.readString(ROOT.resolve("migrations-proposed/V5__relational_integrity_draft.sql"))));
   assertEquals("P0001",e.getSQLState());assertTrue(e.getMessage().contains("ambiguous"));c.rollback();
  }
 }
 @Test void proposedBackfillMapsOnlyUniqueCandidate() throws Exception {
  try(var c=open("d2_baseline")){
   c.setAutoCommit(false);var f=fixture(c);
   sql(c,"DELETE FROM capacity_budgets WHERE id="+q(f.b2));
   sql(c,"UPDATE capacity_allocations SET budget_id=NULL WHERE id="+q(f.a));
   sql(c,Files.readString(ROOT.resolve("migrations-proposed/V5__relational_integrity_draft.sql")));
   assertEquals(f.b,value(c,"SELECT budget_id FROM capacity_allocations WHERE id="+q(f.a)));
   assertEquals("NO",value(c,"SELECT is_nullable FROM information_schema.columns WHERE table_schema='public' AND table_name='capacity_allocations' AND column_name='budget_id'"));
   c.rollback();
  }
 }
}
