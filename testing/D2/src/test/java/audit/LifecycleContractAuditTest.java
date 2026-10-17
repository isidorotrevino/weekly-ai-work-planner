package audit;

import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import java.util.stream.*;
import static org.junit.jupiter.api.Assertions.*;
import static audit.SchemaAuditTest.*;
import static audit.ContractAuditTest.*;
import static audit.IntegrityContractAuditTest.*;

class LifecycleContractAuditTest {
 @BeforeAll static void initialize() throws Exception{ContractAuditTest.migrate();}
 static void callback(Connection c,Setup s,int consumed) throws Exception {
  call(c,"execution",id(),execFenced(c,s.f(),"START"));String req=execFenced(c,s.f(),"CALLBACK");call(c,"execution",id(),req.substring(0,req.length()-1)+",\"entries\":"+entry(s.a(),10,consumed)+"}");
 }
 static void failAcceptance(Connection c,F f) throws Exception {
  String a=insert(c,"artifacts","artifact_ref,sha256,media_type",q(id())+",repeat('a',64),'application/json'");
  sql(c,"INSERT INTO execution_evidence SELECT attempt_id,"+q(a)+"::uuid,'ACCEPTANCE_FAIL' FROM operation_leases WHERE operation_id="+q(f.o()));
 }
 @TestFactory Stream<DynamicTest> completeLifecycles(){
  return List.of(
   new Case("task_completes_only_after_operation_acceptance",(c,s)->{call(c,"transition",id(),transition("TASK",s.f().t(),"BACKLOG","READY",0));call(c,"transition",id(),transition("TASK",s.f().t(),"READY","IN_PROGRESS",1));call(c,"execution",id(),exec(s.f(),"CLAIM"));callback(c,s,12);RecoveryContractAuditTest.acceptance(c,s.f());call(c,"execution",id(),execFenced(c,s.f(),"VERIFY"));call(c,"transition",id(),transition("TASK",s.f().t(),"IN_PROGRESS","VERIFYING",2));call(c,"transition",id(),transition("TASK",s.f().t(),"VERIFYING","DONE",3));assertEquals("DONE",value(c,"SELECT status FROM tasks WHERE id="+q(s.f().t())));assertEquals("12.0000",balance(c,s.a(),"consumed"));}),
   new Case("mocked_work_requires_real_integration_before_completion",(c,s)->{String v=cap(c,s.f());String r=insert(c,"capability_requirements","consumer_task_id,capability_id,version_constraint,environment,kind",q(s.f().t())+",(SELECT capability_id FROM capability_versions WHERE id="+q(v)+"),'1.x','test','MOCKABLE'");sql(c,"INSERT INTO d2.resolutions VALUES("+q(r)+","+q(v)+")");call(c,"execution",id(),exec(s.f(),"CLAIM"));callback(c,s,8);RecoveryContractAuditTest.acceptance(c,s.f());rejected(c,"23514",()->call(c,"execution",id(),execFenced(c,s.f(),"VERIFY")));makeAvailable(c,v);call(c,"execution",id(),execFenced(c,s.f(),"VERIFY"));assertEquals("COMPLETED",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));}),
   new Case("failed_acceptance_retries_with_new_capacity_not_new_quota",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));callback(c,s,8);failAcceptance(c,s.f());call(c,"execution",id(),execFenced(c,s.f(),"REJECT_VERIFICATION"));int ver=Integer.parseInt(value(c,"SELECT row_version FROM operations WHERE id="+q(s.f().o())));call(c,"transition",id(),transition("OPERATION",s.f().o(),"RETRY_PENDING","READY",ver));call(c,"execution",id(),exec(s.f(),"CLAIM"));assertEquals("3",value(c,"SELECT lease_generation FROM operations WHERE id="+q(s.f().o())));assertEquals("10.0000",balance(c,s.a(),"outstanding"));assertEquals("8.0000",balance(c,s.a(),"consumed"));assertEquals("52.0000",balance(c,s.a(),"available"));}),
   new Case("unknown_quota_can_be_calibrated_with_evidence",(c,s)->{sql(c,"ALTER TABLE d2.accounts DISABLE TRIGGER immutable_fact; UPDATE d2.accounts SET initial_capacity=NULL WHERE id="+q(s.a())+"; ALTER TABLE d2.accounts ENABLE TRIGGER immutable_fact");rejected(c,"23514",()->call(c,"capacity",id(),reserve(s.f())));call(c,"recalibrate",id(),"{\"account_id\":\""+s.a()+"\",\"capacity\":100,\"confidence\":0.8,\"reason\":\"observed\",\"evidence_sha256\":\""+"a".repeat(64)+"\"}");call(c,"capacity",id(),reserve(s.f()));assertEquals("60.0000",balance(c,s.a(),"available"));}),
   new Case("unsafe_checkpoint_never_releases_commitment",(c,s)->{sql(c,"UPDATE operations SET policy_snapshot='{\"interruptible\":true}' WHERE id="+q(s.f().o()));call(c,"execution",id(),exec(s.f(),"CLAIM"));String proof=insert(c,"d2.checkpoint_receipts","operation_id,generation,process_stopped,effects_resolved,evidence_sha256",q(s.f().o())+",2,false,true,repeat('a',64)");rejected(c,"23514",()->call(c,"preempt",id(),"{\"operation_id\":\""+s.f().o()+"\",\"checkpoint_receipt_id\":\""+proof+"\"}"));assertEquals("10.0000",balance(c,s.a(),"outstanding"));}),
   new Case("expired_approval_does_not_discard_observed_usage",(c,s)->{sql(c,"UPDATE operations SET policy_snapshot='{\"requires_approval\":true}' WHERE id="+q(s.f().o()));approve(c,s.f(),"now()+interval '1 hour'","APPROVED","a".repeat(64));call(c,"execution",id(),exec(s.f(),"CLAIM"));call(c,"execution",id(),execFenced(c,s.f(),"START"));sql(c,"UPDATE approvals SET expires_at=clock_timestamp()-interval '1 second' WHERE operation_id="+q(s.f().o()));rejected(c,"23514",()->call(c,"execution",id(),execFenced(c,s.f(),"HEARTBEAT")));String req=execFenced(c,s.f(),"CALLBACK");call(c,"execution",id(),req.substring(0,req.length()-1)+",\"entries\":"+entry(s.a(),10,12)+"}");assertEquals("12.0000",balance(c,s.a(),"consumed"));}),
   new Case("return_cannot_erase_borrowed_commitment",(c,s)->{sql(c,"UPDATE operations SET policy_snapshot='{\"interruptible\":true,\"checkpoint_verified\":true}' WHERE id="+q(s.f().o())+"; UPDATE d2.operation_accounts SET units=80 WHERE operation_id="+q(s.f().o()));String loan=id();call(c,"capacity",loan,"{\"action\":\"BORROW\",\"operation_id\":\""+s.f().o()+"\",\"account_id\":\""+s.a()+"\",\"units\":10,\"reason\":\"audit\"}");call(c,"capacity",id(),reserve(s.f()));rejected(c,"23514",()->call(c,"capacity",id(),"{\"action\":\"RETURN\",\"loan_id\":\""+loan+"\",\"units\":10,\"reason\":\"audit\"}"));assertEquals("80.0000",balance(c,s.a(),"outstanding"));})
  ).stream().map(x->DynamicTest.dynamicTest(x.name(),()->{try(var c=open(DB)){c.setAutoCommit(false);try{x.action().run(c,setup(c,100));}finally{c.rollback();}}}));
 }
}
