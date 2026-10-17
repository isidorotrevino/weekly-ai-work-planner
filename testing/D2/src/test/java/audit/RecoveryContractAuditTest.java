package audit;

import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
import static org.junit.jupiter.api.Assertions.*;
import static audit.SchemaAuditTest.*;
import static audit.ContractAuditTest.*;
import static audit.IntegrityContractAuditTest.*;

class RecoveryContractAuditTest {
 @BeforeAll static void initialize() throws Exception{ContractAuditTest.migrate();}
 static String receipt(Connection c,F f,String status) throws Exception {
  String gen=value(c,"SELECT lease_generation FROM operations WHERE id="+q(f.o()));
  return insert(c,"d2.effect_receipts","operation_id,generation,effect_key,status,evidence_ref",q(f.o())+","+gen+",'external-effect',"+q(status)+",'synthetic-reconciliation-evidence'");
 }
 static String withReceipt(F f,String action,String receipt){String req=exec(f,action);return req.substring(0,req.length()-1)+",\"receipt_id\":\""+receipt+"\"}";}
 static void expire(Connection c,F f) throws Exception {sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second' WHERE operation_id="+q(f.o()));call(c,"execution",id(),exec(f,"EXPIRE"));}
 static void acceptance(Connection c,F f) throws Exception {
  String a=insert(c,"artifacts","artifact_ref,sha256,media_type",q(id())+",repeat('a',64),'application/json'");
  sql(c,"INSERT INTO execution_evidence SELECT attempt_id,"+q(a)+"::uuid,'ACCEPTANCE_PASS' FROM operation_leases WHERE operation_id="+q(f.o()));
 }
 @TestFactory Stream<DynamicTest> recoveryAndBoundaries(){
  return List.of(
   new Case("known_absent_effect_can_retry_with_new_fence",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));String old=execFenced(c,s.f(),"START");expire(c,s.f());call(c,"execution",id(),withReceipt(s.f(),"RECONCILE",receipt(c,s.f(),"ABSENT")));int ver=Integer.parseInt(value(c,"SELECT row_version FROM operations WHERE id="+q(s.f().o())));call(c,"transition",id(),transition("OPERATION",s.f().o(),"RETRY_PENDING","READY",ver));call(c,"execution",id(),exec(s.f(),"CLAIM"));assertEquals("3",value(c,"SELECT lease_generation FROM operations WHERE id="+q(s.f().o())));rejected(c,"23514",()->call(c,"execution",id(),old));assertEquals("10.0000",balance(c,s.a(),"outstanding"));}),
   new Case("applied_external_effect_recovered_without_second_effect",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));String proof=receipt(c,s.f(),"APPLIED");expire(c,s.f());call(c,"execution",id(),withReceipt(s.f(),"RECONCILE",proof));acceptance(c,s.f());String req=withReceipt(s.f(),"RECOVERY_VERIFY",proof);req=req.substring(0,req.length()-1)+",\"entries\":"+entry(s.a(),10,12)+"}";call(c,"execution",id(),req);assertEquals("COMPLETED",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));assertEquals("1",value(c,"SELECT count(*) FROM d2.effect_receipts WHERE operation_id="+q(s.f().o())+" AND status='APPLIED'"));assertEquals("12.0000",balance(c,s.a(),"consumed"));}),
   new Case("unknown_effect_requires_new_evidence_to_resume",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));expire(c,s.f());String unknown=receipt(c,s.f(),"UNKNOWN");call(c,"execution",id(),withReceipt(s.f(),"RECONCILE",unknown));rejected(c,"23514",()->call(c,"execution",id(),withReceipt(s.f(),"RESUME_RECONCILIATION",unknown)));String known=receipt(c,s.f(),"ABSENT");call(c,"execution",id(),withReceipt(s.f(),"RESUME_RECONCILIATION",known));call(c,"execution",id(),withReceipt(s.f(),"RECONCILE",known));assertEquals("RETRY_PENDING",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));}),
   new Case("retry_limit_is_bounded",(c,s)->{sql(c,"UPDATE operations SET policy_snapshot='{\"max_attempts\":1}' WHERE id="+q(s.f().o()));rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));}),
   new Case("noninterruptible_work_is_not_cancelled",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));String r=call(c,"preempt",id(),"{\"operation_id\":\""+s.f().o()+"\"}");assertTrue(r.contains("DEFERRED_NONINTERRUPTIBLE"));assertEquals("LEASED",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));assertEquals("10.0000",balance(c,s.a(),"outstanding"));}),
   new Case("verified_checkpoint_required_before_release",(c,s)->{sql(c,"UPDATE operations SET policy_snapshot='{\"interruptible\":true}' WHERE id="+q(s.f().o()));call(c,"execution",id(),exec(s.f(),"CLAIM"));String request="{\"operation_id\":\""+s.f().o()+"\"}";assertTrue(call(c,"preempt",id(),request).contains("CHECKPOINT_REQUESTED"));assertEquals("10.0000",balance(c,s.a(),"outstanding"));String proof=insert(c,"d2.checkpoint_receipts","operation_id,generation,process_stopped,effects_resolved,evidence_sha256",q(s.f().o())+",2,true,true,repeat('a',64)");call(c,"preempt",id(),request.substring(0,request.length()-1)+",\"checkpoint_receipt_id\":\""+proof+"\"}");assertEquals("CANCELLED",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));assertEquals("0.0000",balance(c,s.a(),"outstanding"));}),
   new Case("recalibration_records_deficit",(c,s)->{String r=id();call(c,"capacity",r,reserve(s.f()));call(c,"capacity",id(),consumption("CONSUME",r,entry(s.a(),10,12)));call(c,"recalibrate",id(),"{\"account_id\":\""+s.a()+"\",\"capacity\":10,\"confidence\":0.8,\"reason\":\"new observation\",\"evidence_sha256\":\""+"a".repeat(64)+"\"}");assertEquals("12.0000",balance(c,s.a(),"consumed"));assertEquals("-5.0000",balance(c,s.a(),"available"));}),
   new Case("priority_inherits_only_blocking_path",(c,s)->{sql(c,"UPDATE projects SET priority='P3' WHERE id="+q(s.f().p())+"; UPDATE projects SET priority='P0' WHERE id="+q(s.f().p2()));String extra=insert(c,"tasks","project_id,task_key,title",q(s.f().p())+",'extra','extra'");sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES("+q(s.f().t())+","+q(s.f().t2())+",'HARD')");assertEquals("8",value(c,"SELECT effective_weight FROM d2.effective_priorities WHERE task_id="+q(s.f().t())));assertEquals("1",value(c,"SELECT effective_weight FROM d2.effective_priorities WHERE task_id="+q(extra)));assertEquals("P3",value(c,"SELECT priority FROM projects WHERE id="+q(s.f().p())));}),
   new Case("available_cannot_be_inserted_without_workflow",(c,s)->{String cap=insert(c,"capabilities","provider_project_id,capability_key",q(s.f().p())+",'bad'");rejected(c,"23514",()->sql(c,"INSERT INTO capability_versions(capability_id,version,environment,state) VALUES("+q(cap)+",'1.0.0','test','AVAILABLE')"));}),
   new Case("capability_task_cycle_rejected",(c,s)->{String v=cap(c,s.f());String r=insert(c,"capability_requirements","consumer_task_id,capability_id,version_constraint,environment,kind",q(s.f().t())+",(SELECT capability_id FROM capability_versions WHERE id="+q(v)+"),'1.x','test','HARD'");sql(c,"INSERT INTO d2.capability_producers VALUES("+q(v)+","+q(s.f().t())+")");rejected(c,"23514",()->sql(c,"INSERT INTO d2.resolutions VALUES("+q(r)+","+q(v)+")"));}),
   new Case("soft_project_cycle_is_not_a_hard_cycle",(c,s)->{sql(c,"INSERT INTO project_dependencies(provider_project_id,consumer_project_id,kind) VALUES("+q(s.f().p())+","+q(s.f().p2())+",'HARD'),("+q(s.f().p2())+","+q(s.f().p())+",'SOFT')");rejected(c,"23514",()->sql(c,"UPDATE project_dependencies SET kind='HARD' WHERE provider_project_id="+q(s.f().p2())));}),
   new Case("project_cycle_rejected",(c,s)->{sql(c,"INSERT INTO project_dependencies(provider_project_id,consumer_project_id) VALUES("+q(s.f().p())+","+q(s.f().p2())+")");rejected(c,"23514",()->sql(c,"INSERT INTO project_dependencies(provider_project_id,consumer_project_id) VALUES("+q(s.f().p2())+","+q(s.f().p())+")"));}),
   new Case("version_range_grammar_and_fail_closed",(c,s)->{assertEquals("false",value(c,"SELECT d2.compatible('1.2.3','not-a-range')::text"));assertEquals("true",value(c,"SELECT d2.compatible('1.2.3','^1.2.0')::text"));assertEquals("false",value(c,"SELECT d2.compatible('2.0.0','^1.2.0')::text"));}),
   new Case("task_done_requires_completed_operations",(c,s)->{call(c,"transition",id(),transition("TASK",s.f().t(),"BACKLOG","READY",0));call(c,"transition",id(),transition("TASK",s.f().t(),"READY","IN_PROGRESS",1));call(c,"transition",id(),transition("TASK",s.f().t(),"IN_PROGRESS","VERIFYING",2));rejected(c,"23514",()->call(c,"transition",id(),transition("TASK",s.f().t(),"VERIFYING","DONE",3)));})
  ).stream().map(x->DynamicTest.dynamicTest(x.name(),()->{try(var c=open(DB)){c.setAutoCommit(false);try{x.action().run(c,setup(c,100));}finally{c.rollback();}}}));
 }
 @Test void publicationWinsAgainstConcurrentChildMutation() throws Exception {
  Setup s;try(var c=open(DB)){s=setup(c,100);}
  try(var publisher=open(DB);var pool=Executors.newSingleThreadExecutor()){
   publisher.setAutoCommit(false);sql(publisher,"UPDATE planning_runs SET status='PUBLISHED' WHERE id="+q(s.f().run()));
   var started=new CountDownLatch(1);var update=pool.submit(()->{try(var c=open(DB)){started.countDown();sql(c,"UPDATE capacity_budgets SET estimated_capacity=999 WHERE id="+q(s.f().b()));return true;}catch(SQLException e){assertEquals("55000",e.getSQLState());return false;}});
   assertTrue(started.await(5,TimeUnit.SECONDS));publisher.commit();assertFalse(update.get(15,TimeUnit.SECONDS));
  }
  try(var c=open(DB)){assertEquals("100.0000",value(c,"SELECT estimated_capacity FROM capacity_budgets WHERE id="+q(s.f().b())));}
 }
}
