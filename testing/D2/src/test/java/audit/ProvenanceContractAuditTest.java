package audit;

import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import java.util.stream.*;
import static org.junit.jupiter.api.Assertions.*;
import static audit.SchemaAuditTest.*;
import static audit.ContractAuditTest.*;

class ProvenanceContractAuditTest {
 @BeforeAll static void initialize() throws Exception{ContractAuditTest.migrate();}
 @TestFactory Stream<DynamicTest> provenanceAndDelivery(){
  return List.of(
   new Case("outbox_redelivery_ack_is_idempotent",(c,s)->{String cmd=id();call(c,"capacity",cmd,reserve(s.f()));String event=value(c,"SELECT id FROM outbox_events WHERE aggregate_id="+q(cmd));String hash=value(c,"SELECT encode(digest(payload::text,'sha256'),'hex') FROM outbox_events WHERE id="+q(event));String req="{\"outbox_id\":\""+event+"\",\"payload_sha256\":\""+hash+"\"}";call(c,"ack_outbox",id(),req);call(c,"ack_outbox",id(),req);assertEquals("1",value(c,"SELECT count(*) FROM d2.delivery_receipts WHERE outbox_id="+q(event)));rejected(c,"23514",()->call(c,"ack_outbox",id(),req.replace(hash,"b".repeat(64))));rejected(c,"55000",()->sql(c,"UPDATE outbox_events SET payload='{}' WHERE id="+q(event)));}),
   new Case("source_conflict_does_not_overwrite_local_edit",(c,s)->{String doc=insert(c,"source_documents","project_id,source_type,source_uri",q(s.f().p())+",'GOOGLE_DRIVE',"+q(id()));String rev=insert(c,"source_revisions","document_id,sha256,content_ref",q(doc)+",repeat('a',64),'original'");sql(c,"UPDATE source_documents SET current_revision_id="+q(rev)+" WHERE id="+q(doc));String binding=insert(c,"external_bindings","provider,external_namespace,external_type,external_id,internal_type,internal_id,last_revision","'DRIVE','account','document',"+q(id())+",'SOURCE_DOCUMENT',"+q(doc)+",'remote-1'");String req="{\"binding_id\":\""+binding+"\",\"expected_external_revision\":\"remote-1\",\"expected_local_sha256\":\""+"b".repeat(64)+"\",\"sha256\":\""+"c".repeat(64)+"\",\"observed_revision\":\"remote-2\",\"content_ref\":\"new\"}";assertTrue(call(c,"sync_source",id(),req).contains("CONFLICT"));assertEquals(rev,value(c,"SELECT current_revision_id FROM source_documents WHERE id="+q(doc)));assertEquals("remote-1",value(c,"SELECT last_revision FROM external_bindings WHERE id="+q(binding)));}),
   new Case("successful_sync_preserves_revisions_and_replays",(c,s)->{String doc=insert(c,"source_documents","project_id,source_type,source_uri",q(s.f().p())+",'PLANE',"+q(id()));String binding=insert(c,"external_bindings","provider,external_namespace,external_type,external_id,internal_type,internal_id","'PLANE','workspace','document',"+q(id())+",'SOURCE_DOCUMENT',"+q(doc));String req="{\"binding_id\":\""+binding+"\",\"sha256\":\""+"a".repeat(64)+"\",\"observed_revision\":\"remote-1\",\"content_ref\":\"versioned-object\"}";String cmd=id();assertTrue(call(c,"sync_source",cmd,req).contains("SYNCED"));call(c,"sync_source",cmd,req);assertEquals("1",value(c,"SELECT count(*) FROM source_revisions WHERE document_id="+q(doc)));}),
   new Case("attempt_context_is_immutable",(c,s)->{call(c,"execution",id(),exec(s.f(),"CLAIM"));String aid=value(c,"SELECT attempt_id FROM operation_leases WHERE operation_id="+q(s.f().o()));rejected(c,"55000",()->sql(c,"UPDATE d2.execution_snapshots SET context_ref='changed' WHERE attempt_id="+q(aid)));sql(c,"UPDATE operations SET context_pack_sha256=repeat('b',64) WHERE id="+q(s.f().o()));rejected(c,"23514",()->call(c,"execution",id(),execFenced(c,s.f(),"START")));assertEquals("a".repeat(64),value(c,"SELECT context_sha256 FROM d2.execution_snapshots WHERE attempt_id="+q(aid)));}),
   new Case("budget_snapshot_references_physical_account",(c,s)->{sql(c,"INSERT INTO d2.budget_accounts VALUES("+q(s.f().b())+","+q(s.f().run())+","+q(s.f().r())+","+q(s.a())+",100,0.8,'audit-v1')");sql(c,"UPDATE planning_runs SET status='PUBLISHED' WHERE id="+q(s.f().run()));rejected(c,"55000",()->sql(c,"DELETE FROM d2.budget_accounts WHERE budget_id="+q(s.f().b())));assertEquals("70.0000",balance(c,s.a(),"available"));}),
   new Case("wrong_environment_cannot_unlock",(c,s)->{String v=IntegrityContractAuditTest.cap(c,s.f());IntegrityContractAuditTest.makeAvailable(c,v);String r=insert(c,"capability_requirements","consumer_task_id,capability_id,version_constraint,environment,kind",q(s.f().t())+",(SELECT capability_id FROM capability_versions WHERE id="+q(v)+"),'1.x','production','HARD'");sql(c,"INSERT INTO d2.resolutions VALUES("+q(r)+","+q(v)+")");rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));}),
   new Case("mockable_can_start_but_not_finish_without_real_verification",(c,s)->{String v=IntegrityContractAuditTest.cap(c,s.f());String r=insert(c,"capability_requirements","consumer_task_id,capability_id,version_constraint,environment,kind",q(s.f().t())+",(SELECT capability_id FROM capability_versions WHERE id="+q(v)+"),'1.x','test','MOCKABLE'");sql(c,"INSERT INTO d2.resolutions VALUES("+q(r)+","+q(v)+")");call(c,"execution",id(),exec(s.f(),"CLAIM"));assertEquals("LEASED",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));}),
   new Case("gentle_ai_task_has_direct_source_lineage",(c,s)->{String doc=insert(c,"source_documents","project_id,source_type,source_uri",q(s.f().p())+",'GENTLE_AI',"+q(id()));String rev=insert(c,"source_revisions","document_id,sha256,content_ref",q(doc)+",repeat('a',64),'plan-v1'");sql(c,"INSERT INTO d2.task_sources VALUES("+q(s.f().t())+","+q(rev)+",'line:1',"+q(doc)+","+q(s.f().p())+")");rejected(c,"23503",()->sql(c,"INSERT INTO d2.task_sources VALUES("+q(s.f().t2())+","+q(rev)+",'line:1',"+q(doc)+","+q(s.f().p2())+")"));}),
   new Case("technical_capability_is_hard_filter",(c,s)->{sql(c,"UPDATE operations SET policy_snapshot='{\"required_capabilities\":{\"java21\":true}}' WHERE id="+q(s.f().o()));rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));sql(c,"UPDATE resources SET capabilities='{\"java21\":true}' WHERE id="+q(s.f().r())+"; UPDATE workers SET capabilities='{\"java21\":true}' WHERE id="+q(s.f().w()));call(c,"execution",id(),exec(s.f(),"CLAIM"));}),
   new Case("legacy_namespaces_require_mapping",(c,s)->{rejected(c,"23502",()->sql(c,"INSERT INTO external_bindings(provider,external_type,external_id,internal_type,internal_id) VALUES('TEST','ticket','x','TASK',"+q(s.f().t())+")"));})
  ).stream().map(x->DynamicTest.dynamicTest(x.name(),()->{try(var c=open(DB)){c.setAutoCommit(false);try{x.action().run(c,setup(c,100));}finally{c.rollback();}}}));
 }
 @Test void externalCommitSurvivesControllerCrashAndIsReconciled() throws Exception {
  Setup s;String proof;
  try(var c=open(DB)){s=setup(c,100);call(c,"execution",id(),exec(s.f(),"CLAIM"));}
  // Separate committed connection stands in for a trusted adapter's durable
  // receipt after the external commit. No callback is sent before lease expiry.
  try(var external=open(DB)){proof=RecoveryContractAuditTest.receipt(external,s.f(),"APPLIED");}
  try(var recovered=open(DB)){
   RecoveryContractAuditTest.expire(recovered,s.f());call(recovered,"execution",id(),RecoveryContractAuditTest.withReceipt(s.f(),"RECONCILE",proof));
   assertEquals("VERIFYING",value(recovered,"SELECT state FROM operations WHERE id="+q(s.f().o())));
   assertEquals("1",value(recovered,"SELECT count(*) FROM d2.effect_receipts WHERE operation_id="+q(s.f().o())+" AND status='APPLIED'"));
   assertEquals("10.0000",balance(recovered,s.a(),"outstanding"));
  }
 }
 @Test void catalogAndIncidentInvariants() throws Exception {
  try(var c=open(DB)){
   c.setAutoCommit(false);
   try{
    assertEquals("0",value(c,"SELECT count(*) FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace WHERE n.nspname IN ('public','d2') AND c.contype='f' AND NOT c.convalidated"));
    assertEquals("69",value(c,"SELECT count(*) FROM state_transition_rules"));
    assertEquals("false",value(c,"SELECT has_table_privilege('d2_runtime','public.operations','UPDATE')::text"));
    assertEquals("false",value(c,"SELECT has_function_privilege('d2_runtime','d2.capacity(uuid,jsonb)','EXECUTE')::text"));
    assertEquals("3",value(c,"SELECT count(*) FROM pg_indexes WHERE schemaname='public' AND indexname IN ('idx_operations_ready','idx_outbox_pending','idx_leases_expiry')"));
    var s=setup(c,100);
    String requirement=insert(c,"requirements","project_id,requirement_key,title",q(s.f().p())+",'state-check','state-check'");
    rejected(c,"23514",()->sql(c,"UPDATE requirements SET status='MADE_UP' WHERE id="+q(requirement)));
    String incident=insert(c,"incidents","project_id,incident_key,severity",q(s.f().p())+","+q(id())+",'SEV1'");
    assertEquals("1",value(c,"SELECT count(*) FROM outbox_events WHERE aggregate_id="+q(incident)+" AND event_type='REPLAN_REQUIRED'"));
   }finally{c.rollback();}
  }
 }

}
