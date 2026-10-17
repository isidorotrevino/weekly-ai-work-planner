package audit;

import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
import static org.junit.jupiter.api.Assertions.*;
import static audit.SchemaAuditTest.*;
import static audit.ContractAuditTest.*;

class IntegrityContractAuditTest {
 @BeforeAll static void initialize() throws Exception{ContractAuditTest.migrate();}
 static String transition(String kind,String eid,String from,String to,int version){return "{\"entity_type\":\""+kind+"\",\"entity_id\":\""+eid+"\",\"from\":\""+from+"\",\"to\":\""+to+"\",\"expected_version\":"+version+",\"actor\":\"AUDITOR\",\"reason\":\"audit\"}";}
 static String cap(Connection c,F f) throws Exception {
  String cap=insert(c,"capabilities","provider_project_id,capability_key",q(f.p())+","+q(id()));
  return insert(c,"capability_versions","capability_id,version,environment,contract_sha256",q(cap)+",'1.2.3','test',repeat('a',64)");
 }
 static void verify(Connection c,String vid,int epoch) throws Exception {
  sql(c,"INSERT INTO d2.verifications(version_id,epoch,environment,contract_sha256,evidence_sha256,outcome) VALUES("+q(vid)+","+epoch+",'test',repeat('a',64),repeat('b',64),'PASS')");
 }
 static void makeAvailable(Connection c,String vid) throws Exception {
  call(c,"transition",id(),transition("CAPABILITY_VERSION",vid,"PLANNED","IMPLEMENTED",0));verify(c,vid,0);
  call(c,"transition",id(),transition("CAPABILITY_VERSION",vid,"IMPLEMENTED","VERIFIED",1));call(c,"transition",id(),transition("CAPABILITY_VERSION",vid,"VERIFIED","AVAILABLE",2));
 }
 static void approve(Connection c,F f,String expiry,String state,String context) throws Exception {
  sql(c,"INSERT INTO approvals(operation_id,state,reason,requested_at,decided_at,decided_by,expires_at,context_snapshot_sha256,policy_snapshot_sha256) SELECT id,"+q(state)+",'audit',now()-interval '2 hours',now()-interval '1 hour','AUDITOR',"+expiry+","+q(context)+",encode(digest(policy_snapshot::text,'sha256'),'hex') FROM operations WHERE id="+q(f.o()));
 }
 @TestFactory Stream<DynamicTest> integrityAndGuards(){
  return List.of(
   new Case("state_history_outbox_replay",(c,s)->{String cmd=id(),r=transition("TASK",s.f().t(),"BACKLOG","READY",0);call(c,"transition",cmd,r);call(c,"transition",cmd,r);assertEquals("1",value(c,"SELECT count(*) FROM state_transition_events WHERE entity_id="+q(s.f().t())));assertEquals("1",value(c,"SELECT count(*) FROM outbox_events WHERE aggregate_id="+q(s.f().t())));}),
   new Case("illegal_transition_and_version_conflict",(c,s)->{rejected(c,"23514",()->call(c,"transition",id(),transition("TASK",s.f().t(),"BACKLOG","DONE",0)));rejected(c,"40001",()->call(c,"transition",id(),transition("TASK",s.f().t(),"BACKLOG","READY",9)));}),
   new Case("sql_mutation_denied_to_runtime",(c,s)->{sql(c,"SET LOCAL ROLE d2_runtime");rejected(c,"42501",()->sql(c,"UPDATE tasks SET status='DONE' WHERE id="+q(s.f().t())));call(c,"transition",id(),transition("TASK",s.f().t(),"BACKLOG","READY",0));}),
   new Case("hard_predecessor_blocks_start",(c,s)->{sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES("+q(s.f().t2())+","+q(s.f().t())+",'HARD')");rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));}),
   new Case("hard_cycle_rejected_soft_cycle_allowed",(c,s)->{sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES("+q(s.f().t())+","+q(s.f().t2())+",'HARD')");rejected(c,"23514",()->sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES("+q(s.f().t2())+","+q(s.f().t())+",'HARD')"));sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES("+q(s.f().t2())+","+q(s.f().t())+",'SOFT')");}),
   new Case("capability_requires_fresh_evidence",(c,s)->{String v=cap(c,s.f());call(c,"transition",id(),transition("CAPABILITY_VERSION",v,"PLANNED","IMPLEMENTED",0));rejected(c,"23514",()->call(c,"transition",id(),transition("CAPABILITY_VERSION",v,"IMPLEMENTED","VERIFIED",1)));verify(c,v,0);call(c,"transition",id(),transition("CAPABILITY_VERSION",v,"IMPLEMENTED","VERIFIED",1));call(c,"transition",id(),transition("CAPABILITY_VERSION",v,"VERIFIED","AVAILABLE",2));call(c,"transition",id(),transition("CAPABILITY_VERSION",v,"AVAILABLE","INVALIDATED",3));call(c,"transition",id(),transition("CAPABILITY_VERSION",v,"INVALIDATED","IMPLEMENTED",4));rejected(c,"23514",()->call(c,"transition",id(),transition("CAPABILITY_VERSION",v,"IMPLEMENTED","VERIFIED",5)));verify(c,v,1);call(c,"transition",id(),transition("CAPABILITY_VERSION",v,"IMPLEMENTED","VERIFIED",5));}),
   new Case("invalidation_blocks_hard_consumer",(c,s)->{String v=cap(c,s.f());makeAvailable(c,v);String req=insert(c,"capability_requirements","consumer_task_id,capability_id,version_constraint,environment,kind",q(s.f().t())+",(SELECT capability_id FROM capability_versions WHERE id="+q(v)+"),'^1.2.0','test','HARD'");sql(c,"INSERT INTO d2.resolutions VALUES("+q(req)+","+q(v)+")");call(c,"execution",id(),exec(s.f(),"CLAIM"));call(c,"transition",id(),transition("CAPABILITY_VERSION",v,"AVAILABLE","INVALIDATED",3));assertEquals("RECONCILING",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));assertEquals("false",value(c,"SELECT d2.task_eligible("+q(s.f().t())+")::text"));}),
   new Case("published_parent_and_children_frozen",(c,s)->{sql(c,"UPDATE planning_runs SET status='PUBLISHED' WHERE id="+q(s.f().run()));rejected(c,"55000",()->sql(c,"UPDATE planning_runs SET config_snapshot='{\"x\":1}' WHERE id="+q(s.f().run())));rejected(c,"55000",()->sql(c,"UPDATE capacity_budgets SET estimated_capacity=999 WHERE id="+q(s.f().b())));rejected(c,"55000",()->sql(c,"DELETE FROM capacity_allocations WHERE id="+q(s.f().a())));rejected(c,"55000",()->sql(c,"INSERT INTO schedule_entries(planning_run_id,task_id,resource_id,pool,priority_snapshot) VALUES("+q(s.f().run())+","+q(s.f().t())+","+q(s.f().r())+",'PLANNED','{}')"));}),
   new Case("explicit_supersession_preserves_content",(c,s)->{String next=insert(c,"planning_runs","horizon_start,horizon_end,trigger_type,config_snapshot,config_sha256,solver_version","now(),now()+interval '7 days','AUDIT','{}',repeat('a',64),'audit'");sql(c,"UPDATE planning_runs SET status='PUBLISHED' WHERE id IN ("+q(s.f().run())+","+q(next)+")");sql(c,"UPDATE planning_runs SET status='SUPERSEDED',superseded_by="+q(next)+" WHERE id="+q(s.f().run()));assertEquals(next,value(c,"SELECT superseded_by FROM planning_runs WHERE id="+q(s.f().run())));}),
   new Case("source_project_mismatch_rejected",(c,s)->{String doc=insert(c,"source_documents","project_id,source_type,source_uri",q(s.f().p())+",'OTHER',"+q(id()));String rev=insert(c,"source_revisions","document_id,sha256,content_ref",q(doc)+",repeat('a',64),'synthetic'");String req=insert(c,"requirements","project_id,requirement_key,title",q(s.f().p2())+",'req','req'");rejected(c,"23503",()->sql(c,"INSERT INTO requirement_sources VALUES("+q(req)+","+q(rev)+",'',"+q(doc)+","+q(s.f().p2())+")"));}),
   new Case("external_namespace_and_target",(c,s)->{for(String ns:List.of("accountA","accountB"))sql(c,"INSERT INTO external_bindings(provider,external_namespace,external_type,external_id,internal_type,internal_id) VALUES('TEST',"+q(ns)+",'ticket','same','TASK',"+q(s.f().t())+")");rejected(c,"23503",()->sql(c,"INSERT INTO external_bindings(provider,external_namespace,external_type,external_id,internal_type,internal_id) VALUES('TEST','accountA','ticket','missing','TASK',gen_random_uuid())"));}),
   new Case("movement_pool_mismatch_rejected",(c,s)->rejected(c,"23503",()->sql(c,"INSERT INTO capacity_movements(budget_id,resource_id,project_id,allocation_id,movement_type,source_pool,units,measurement,reason,correlation_key) VALUES("+q(s.f().b())+","+q(s.f().r())+","+q(s.f().p())+","+q(s.f().a())+",'RESERVE','INCIDENT',1,'ESTIMATED','audit',"+q(id())+")"))),
   new Case("expired_approval_rejected",(c,s)->{sql(c,"UPDATE operations SET context_pack_sha256=repeat('a',64),policy_snapshot='{\"requires_approval\":true}' WHERE id="+q(s.f().o()));approve(c,s.f(),"now()-interval '1 minute'","APPROVED","a".repeat(64));rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));}),
   new Case("valid_approval_and_changed_context",(c,s)->{sql(c,"UPDATE operations SET context_pack_sha256=repeat('a',64),policy_snapshot='{\"requires_approval\":true}' WHERE id="+q(s.f().o()));approve(c,s.f(),"now()+interval '1 hour'","APPROVED","a".repeat(64));call(c,"execution",id(),exec(s.f(),"CLAIM"));sql(c,"UPDATE operations SET context_pack_sha256=repeat('b',64) WHERE id="+q(s.f().o()));rejected(c,"23514",()->call(c,"execution",id(),execFenced(c,s.f(),"START")));})
  ).stream().map(x->DynamicTest.dynamicTest(x.name(),()->{try(var c=open(DB)){c.setAutoCommit(false);try{x.action().run(c,setup(c,100));}finally{c.rollback();}}}));
 }
 @Test void oppositeConcurrentEdgesCannotBothCommit() throws Exception {
  Setup s;try(var c=open(DB)){s=setup(c,100);}
  var gate=new CountDownLatch(1);try(var pool=Executors.newFixedThreadPool(2)){
   var futures=new ArrayList<Future<Boolean>>();for(boolean reverse:List.of(false,true))futures.add(pool.submit(()->{gate.await();try(var c=open(DB)){String a=reverse?s.f().t2():s.f().t(),b=reverse?s.f().t():s.f().t2();sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES("+q(a)+","+q(b)+",'HARD')");return true;}catch(SQLException e){assertEquals("23514",e.getSQLState());return false;}}));gate.countDown();int ok=0;for(var f:futures)if(f.get(20,TimeUnit.SECONDS))ok++;assertEquals(1,ok);
  }
 }
}
