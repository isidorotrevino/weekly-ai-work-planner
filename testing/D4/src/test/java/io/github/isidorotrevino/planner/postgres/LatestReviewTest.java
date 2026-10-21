// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.sql.Connection;
import java.util.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;
import static org.junit.jupiter.api.Assertions.*;
/** All 19 A21/A22 SQL cases rerun on V30 plus resolved-capability propagation. */
class LatestReviewTest extends ReviewStoreTest {
 @Override @BeforeEach void setup(TestInfo info)throws Exception{super.setup(info);migrations(f.db,"30").migrate();try(var c=f.owner()){var workers=new ArrayList<UUID>();try(var p=c.createStatement();var rows=p.executeQuery("SELECT worker_id FROM d4.worker_catalog")){while(rows.next())workers.add(rows.getObject(1,UUID.class));}for(var worker:workers)PresenceStoreTest.seed(c,worker);sql(c,"INSERT INTO d4.presence_delivery SELECT d.id,h.session_id FROM d4.deliveries d JOIN d4.presence_heads h ON h.worker_id=d.worker_id");}}
 @Override void actorFixture(Connection c,DeliveryStoreTest actor)throws Exception{super.actorFixture(c,actor);PresenceStoreTest.seed(c,actor.worker);}
 @Override @Test void runtimeCannotMintRevisionOrCloseCase()throws Exception{settled(false);r.receipt("step-2","UNKNOWN");try(var c=f.owner()){String role="latest_review_"+id().toString().replace("-","");sql(c,"CREATE ROLE "+role+" NOLOGIN;GRANT USAGE ON SCHEMA d4 TO "+role+";SET ROLE "+role);m.reject("42501",()->value(c,"SELECT d4.review_revise(NULL,NULL,NULL,0,'{}')::text"));m.reject("42501",()->value(c,"SELECT d4.review_close(NULL,NULL,NULL,'x')::text"));m.reject("42501",()->sql(c,"SELECT * FROM d4.review_cases"));}}
 @Test void resolvedCapabilityKindsRemainSuspendedTransitivelyUntilExplicitClosure()throws Exception{
  var sid=settled(true);try(var c=f.owner()){
   m.call(c,"recovery_accept",id(),sid);sql(c,"UPDATE tasks SET status='DONE'");var source=UUID.fromString(value(c,"SELECT task_id FROM operations WHERE id=?",f.operation));
   var cap=insert(c,"INSERT INTO capabilities(provider_project_id,capability_key) SELECT project_id,? FROM tasks WHERE id=?",id().toString(),source);var version=insert(c,"INSERT INTO capability_versions(capability_id,version,environment,contract_sha256) VALUES(?,'1.2.3','test',repeat('a',64))",cap);sql(c,"INSERT INTO d2.capability_producers VALUES(?,?)",version,source);
   for(int step=0;step<3;step++){
    if(step==1)sql(c,"INSERT INTO d2.verifications(version_id,epoch,environment,contract_sha256,evidence_sha256,outcome) VALUES(?,0,'test',repeat('a',64),repeat('b',64),'PASS')",version);
    value(c,"SELECT d2.transition(?,?::jsonb)::text",id(),Json.write(Map.of("entity_type","CAPABILITY_VERSION","entity_id",version,"from",List.of("PLANNED","IMPLEMENTED","VERIFIED").get(step),"to",List.of("IMPLEMENTED","VERIFIED","AVAILABLE").get(step),"expected_version",step,"actor","SYNTHETIC_OWNER","reason","Resolved capability fixture")));
   }
   var tasks=new HashMap<String,UUID>();for(var kind:List.of("HARD","MOCKABLE","SOFT","OPTIONAL")){var task=insert(c,"INSERT INTO tasks(project_id,task_key,title) SELECT project_id,?,'Capability consumer' FROM tasks WHERE id=?",id().toString(),source);tasks.put(kind,task);var req=insert(c,"INSERT INTO capability_requirements(consumer_task_id,capability_id,version_constraint,environment,kind) VALUES(?,?,'^1.2.0','test',?)",task,cap,kind);sql(c,"INSERT INTO d2.resolutions VALUES(?,?)",req,version);assertEquals("true",value(c,"SELECT d2.task_eligible(?)::text",task));}
   r.receipt("step-1","UNKNOWN");for(var kind:tasks.keySet()){assertEquals(kind.equals("HARD")?"false":"true",value(c,"SELECT d2.task_eligible(?)::text",tasks.get(kind)));assertEquals(Set.of("HARD","MOCKABLE").contains(kind)?"false":"true",value(c,"SELECT d2.integration_eligible(?)::text",tasks.get(kind)));}
   var child=insert(c,"INSERT INTO tasks(project_id,task_key,title) SELECT project_id,?,'Transitive consumer' FROM tasks WHERE id=?",id().toString(),source);sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES(?,?,'HARD')",tasks.get("HARD"),child);assertEquals("true",value(c,"SELECT d4.review_task_blocked(?,true)::text",child));
   var rev=revise(null);close(rev);for(var task:tasks.values())assertEquals("true",value(c,"SELECT d2.integration_eligible(?)::text",task));assertEquals("false",value(c,"SELECT d4.review_task_blocked(?,true)::text",child));
  }
 }
}
