package audit;

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import java.nio.file.*;
import java.sql.*;
import java.util.*;
import java.util.stream.*;
import static org.junit.jupiter.api.Assertions.*;
import static audit.SchemaAuditTest.*;

/** V6 constraints, permitted cross-project work and transactional upgrade failures. */
class OwnershipAuditTest {
 @BeforeAll static void migrateOwnershipDatabases() throws Exception {
  for(String db:List.of("d2_hardened","d2_upgrade")){
   var config=Flyway.configure().dataSource(URL+db,"d2_auditor","").cleanDisabled(true)
    .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed"));
   config.target(db.equals("d2_upgrade")?"5":"6");
   var flyway=config.load();flyway.migrate();flyway.validate();
   assertEquals(0,flyway.migrate().migrationsExecuted);
   try(var c=open(db)){
    assertEquals(db.equals("d2_upgrade")?"5":"6",value(c,"SELECT count(*) FROM flyway_schema_history WHERE success"));
   }
  }
 }
 static String move(F f,String budget,String resource,String allocation,String operation,String attempt,String task,String project){
  return "INSERT INTO capacity_movements(budget_id,resource_id,allocation_id,operation_id,attempt_id,task_id,project_id,movement_type,source_pool,units,measurement,reason,correlation_key) VALUES("+
   q(budget)+","+q(resource)+","+allocation+","+operation+","+attempt+","+task+","+project+",'RESERVE','PLANNED',1,'ESTIMATED','audit',"+q(UUID.randomUUID().toString())+")";
 }
 static String good(F f){return move(f,f.b(),f.r(),q(f.a()),q(f.o()),q(f.attempt()),q(f.t()),q(f.p()));}
 static String epicLink(F f,String requirementProject){
  return "WITH e AS (INSERT INTO epics(project_id,epic_key,title) VALUES("+q(f.p())+",'e','e') RETURNING id),r AS (INSERT INTO requirements(project_id,requirement_key,title) VALUES("+
   q(requirementProject)+",'r','r') RETURNING id) INSERT INTO epic_requirements(epic_id,requirement_id,project_id) SELECT e.id,r.id,"+q(f.p())+"::uuid FROM e,r";
 }
 record Case(String name,String state,StatementFactory statement){}
 @TestFactory Stream<DynamicTest> rejectsInvalidOwnership(){
  return List.of(
   new Case("wrong_budget_resource","23503",f->move(f,f.b(),f.r2(),"NULL","NULL","NULL","NULL","NULL")),
   new Case("wrong_attempt_resource","23503",f->move(f,f.b3(),f.r2(),"NULL",q(f.o()),q(f.attempt()),q(f.t()),q(f.p()))),
   new Case("wrong_allocation_project","23503",f->move(f,f.b(),f.r(),q(f.a()),q(f.o2()),"NULL",q(f.t2()),q(f.p2()))),
   new Case("wrong_operation_task","23503",f->move(f,f.b(),f.r(),"NULL",q(f.o()),"NULL",q(f.t2()),q(f.p2()))),
   new Case("missing_task","23514",f->move(f,f.b(),f.r(),"NULL",q(f.o()),"NULL","NULL",q(f.p()))),
   new Case("missing_project","23514",f->move(f,f.b(),f.r(),q(f.a()),"NULL","NULL","NULL","NULL")),
   new Case("unscoped_project","23514",f->move(f,f.b(),f.r(),"NULL","NULL","NULL","NULL",q(f.p()))),
   new Case("epic_cross_project_requirement","23503",f->epicLink(f,f.p2())),
   new Case("reassign_attempt_resource","23503",f->good(f)+"; UPDATE execution_attempts SET resource_id="+q(f.r2())+" WHERE id="+q(f.attempt())),
   new Case("reassign_task_project","23503",f->good(f)+"; UPDATE tasks SET project_id="+q(f.p2())+" WHERE id="+q(f.t())),
   new Case("journal_stays_immutable","55000",f->good(f)+"; UPDATE capacity_movements SET units=2"),
   new Case("journal_delete_forbidden","55000",f->good(f)+"; DELETE FROM capacity_movements"),
   new Case("journal_truncate_forbidden","55000",f->"TRUNCATE capacity_movements")
  ).stream().map(test->DynamicTest.dynamicTest(test.name(),()->{
   try(var c=open("d2_hardened")){
    c.setAutoCommit(false);
    try{var f=fixture(c);var error=assertThrows(SQLException.class,()->sql(c,test.statement().make(f)));assertEquals(test.state(),error.getSQLState(),error.toString());}
    finally{c.rollback();}
   }
  }));
 }
 @TestFactory Stream<DynamicTest> preservesValidRelationships(){
  return List.<Case>of(
   new Case("complete_context",null,OwnershipAuditTest::good),
   new Case("budget_only",null,f->move(f,f.b(),f.r(),"NULL","NULL","NULL","NULL","NULL")),
   new Case("allocation_only",null,f->move(f,f.b(),f.r(),q(f.a()),"NULL","NULL","NULL",q(f.p()))),
   new Case("operation_only",null,f->move(f,f.b(),f.r(),"NULL",q(f.o()),q(f.attempt()),q(f.t()),q(f.p()))),
   new Case("same_project_epic_requirement",null,f->epicLink(f,f.p())),
   new Case("cross_project_task_dependency",null,f->"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES("+q(f.t())+","+q(f.t2())+",'HARD')"),
   new Case("cross_project_capability",null,f->"WITH cap AS (INSERT INTO capabilities(provider_project_id,capability_key) VALUES("+q(f.p())+",'cross') RETURNING id) INSERT INTO capability_requirements(consumer_task_id,capability_id,version_constraint,environment,kind) SELECT "+q(f.t2())+"::uuid,id,'1.x','test','HARD' FROM cap")
  ).stream().map(statement->DynamicTest.dynamicTest("valid_"+statement.name(),()->{
   try(var c=open("d2_hardened")){c.setAutoCommit(false);try{sql(c,statement.statement().make(fixture(c)));}finally{c.rollback();}}
  }));
 }
 static String migration() throws Exception {return Files.readString(ROOT.resolve("migrations-proposed/V6__movement_and_epic_ownership_draft.sql"));}
 @TestFactory Stream<DynamicTest> reproducesRemainingV5Gaps(){
  return List.<Case>of(
   new Case("attempt_resource",null,f->movement(f,f.b3(),"NULL",q(f.o()),q(f.attempt()),"CONSUME","PLANNED","NULL",10)),
   new Case("allocation_project",null,f->movement(f,f.b(),q(f.a()),q(f.o2()),"NULL","RESERVE","PLANNED","NULL",10))
  ).stream().map(statement->DynamicTest.dynamicTest("V5_gap_"+statement.name(),()->{
   try(var c=open("d2_upgrade")){c.setAutoCommit(false);try{sql(c,statement.statement().make(fixture(c)));}finally{c.rollback();}}
  }));
 }
 @Test void validUpgradeEnrichesContextWithoutChangingOriginalFact() throws Exception {
  try(var c=open("d2_upgrade")){
   c.setAutoCommit(false);
   try{
    var f=fixture(c);sql(c,movement(f,f.b(),q(f.a()),q(f.o()),q(f.attempt()),"RESERVE","PLANNED","NULL",10));
    String before=value(c,"SELECT to_jsonb(m)::text FROM capacity_movements m WHERE budget_id="+q(f.b()));
    sql(c,migration());
    assertEquals(before,value(c,"SELECT (to_jsonb(m)-'resource_id'-'project_id'-'task_id')::text FROM capacity_movements m WHERE budget_id="+q(f.b())));
   }finally{c.rollback();}
  }
 }
 @Test void incompatibleAttemptAbortsUpgradeAndRestoresTrigger() throws Exception {
  try(var c=open("d2_upgrade")){
   c.setAutoCommit(false);
   var f=fixture(c);sql(c,movement(f,f.b3(),"NULL",q(f.o()),q(f.attempt()),"CONSUME","PLANNED","NULL",10));
   var e=assertThrows(SQLException.class,()->sql(c,migration()));assertEquals("23503",e.getSQLState());c.rollback();
   assertEquals("0",value(c,"SELECT count(*) FROM information_schema.columns WHERE table_name='capacity_movements' AND column_name='resource_id'"));
   assertEquals("O",value(c,"SELECT tgenabled FROM pg_trigger WHERE tgrelid='capacity_movements'::regclass AND tgname='immutable_fact'"));
   c.rollback();
  }
 }
 @Test void incompatibleEpicAbortsUpgrade() throws Exception {
  try(var c=open("d2_upgrade")){
   c.setAutoCommit(false);var f=fixture(c);
   sql(c,"WITH e AS (INSERT INTO epics(project_id,epic_key,title) VALUES("+q(f.p())+",'e','e') RETURNING id),r AS (INSERT INTO requirements(project_id,requirement_key,title) VALUES("+q(f.p2())+",'r','r') RETURNING id) INSERT INTO epic_requirements SELECT e.id,r.id FROM e,r");
   var e=assertThrows(SQLException.class,()->sql(c,migration()));assertEquals("23503",e.getSQLState());c.rollback();
   assertEquals("0",value(c,"SELECT count(*) FROM information_schema.columns WHERE table_name='epic_requirements' AND column_name='project_id'"));c.rollback();
  }
 }
}
