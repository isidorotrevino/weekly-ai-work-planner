// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;

import io.github.isidorotrevino.planner.runtime.*;
import io.github.isidorotrevino.planner.postgres.*;
import io.github.isidorotrevino.planner.scheduler.*;
import org.flywaydb.core.Flyway;
import java.nio.file.*;
import java.security.*;
import java.security.cert.CertificateFactory;
import java.sql.*;
import java.time.*;
import java.util.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;

final class LabBootstrap {
 static UUID id(){return UUID.randomUUID();}
 static void sql(Connection c,String text,Object...args) throws Exception {try(var p=c.prepareStatement(text)){bind(p,args);p.execute();}}
 static void bind(PreparedStatement p,Object...args) throws Exception {for(int i=0;i<args.length;i++)p.setObject(i+1,args[i] instanceof Instant t?t.atOffset(ZoneOffset.UTC):args[i]);}
 static UUID insert(Connection c,String text,Object...args) throws Exception {try(var p=c.prepareStatement(text+" RETURNING id")){bind(p,args);try(var r=p.executeQuery()){r.next();return r.getObject(1,UUID.class);}}}
 static void run() throws Exception {
  var trust=KeyStore.getInstance("PKCS12");trust.load(null,null);try(var in=Files.newInputStream(Path.of("/public/ca.crt"))){trust.setCertificateEntry("ca",CertificateFactory.getInstance("X.509").generateCertificate(in));}
  try(var out=Files.newOutputStream(Path.of("/public/trust.p12"))){trust.store(out,"synthetic-trust-only".toCharArray());}
  var receiver=EffectJournal.create(Path.of("/receiver-state/receiver"),LabSupport.publicKey("control"),Clock.systemUTC());Files.writeString(Path.of("/public/receiver.id"),receiver.receiverId().toString());
  FixtureSupervisor.create(Path.of("/worker-a-state/supervisor"));FixtureSupervisor.create(Path.of("/worker-b-state/supervisor"));
  var locations=List.of("migrations","migrations-proposed","migrations-d3-proposed","migrations-d3-dispatch-proposed","migrations-d3-coordinator-proposed","migrations-d3-review-proposed","migrations-d4-proposed").stream().map(n->"filesystem:/sql/"+n).toArray(String[]::new);
  var flyway=Flyway.configure().dataSource(LabSupport.config("jdbc.url"),LabSupport.config("jdbc.user"),LabSupport.config("jdbc.password")).locations(locations).target("30").load();
  if(flyway.migrate().migrationsExecuted!=30)throw new IllegalStateException("CLEAN_DISPOSABLE_DATABASE_REQUIRED");flyway.validate();
  var participants=LabSupport.JSON.readTree(Files.readString(Path.of("/public/participants.json")));String scenario=LabSupport.text(participants,"scenario");
  var summary=new LinkedHashMap<String,Object>();summary.put("scenario",scenario);summary.put("campaign",LabSupport.text(participants,"campaign"));
  var store=new PlanningStore();var at=Instant.now();
  try(var c=LabSupport.connection()){
   for(var role:List.of("control","verifier","auditor")){var password=LabSupport.config(role+".password");if(!password.matches("[a-f0-9]{48}"))throw new IllegalStateException("SYNTHETIC_PASSWORD_REQUIRED");sql(c,"CREATE ROLE lab_"+role+" LOGIN PASSWORD '"+password+"'");}
   sql(c,"GRANT USAGE ON SCHEMA public,d3,d4 TO lab_control;GRANT EXECUTE ON FUNCTION d4.transport(uuid,uuid,jsonb),d4.read_transport_command(uuid,uuid),d4.current_assignment(uuid),d4.lab_authorize(uuid,uuid,uuid,uuid),d4.lab_inspect(uuid),d4.lab_admin(uuid,uuid,text,uuid) TO lab_control");
   sql(c,"GRANT EXECUTE ON FUNCTION d3.read_capture(uuid),d3.enqueue_planning(uuid,jsonb),d3.poll_planning(uuid),d3.take_planning(uuid,jsonb),d3.prepare_planning(jsonb),d3.publish_planning(jsonb),d3.fail_planning(jsonb),d3.read_planning_request(uuid) TO lab_control");
   sql(c,"GRANT USAGE ON SCHEMA d4 TO lab_verifier,lab_auditor;GRANT EXECUTE ON FUNCTION d4.lab_inspect(uuid) TO lab_verifier,lab_auditor;GRANT EXECUTE ON FUNCTION d4.lab_record_evidence(uuid,uuid,text,boolean,jsonb) TO lab_verifier;GRANT EXECUTE ON FUNCTION d4.lab_audit() TO lab_auditor");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.transport_continuation(uuid,uuid,jsonb),d4.i5_inspect(uuid),d4.checkpoint_request(uuid,uuid,bigint),d4.commit_checkpoint(uuid,uuid,uuid,bigint),d4.authorize_continuation(uuid,uuid,bigint,text),d4.observe_continuation_eligibility(uuid),d4.publish_continuation(uuid,jsonb),d4.finalize_continuation(uuid,uuid) TO lab_control");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.worker_checkpoint_signal(uuid,uuid) TO lab_control");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.worker_execution_status(uuid,uuid) TO lab_control");
   sql(c,"GRANT EXECUTE ON FUNCTION d3.capture(uuid,jsonb) TO lab_control;GRANT EXECUTE ON FUNCTION d4.checkpoint_inspect(uuid),d4.i5_inspect(uuid),d4.record_checkpoint_proof(uuid,uuid,jsonb),d4.record_continuation_acceptance(uuid,uuid,jsonb) TO lab_verifier;GRANT EXECUTE ON FUNCTION d4.i5_audit(),d4.i5_inspect(uuid) TO lab_auditor");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.multi_inspect(uuid) TO lab_control,lab_verifier,lab_auditor;GRANT EXECUTE ON FUNCTION d4.multi_audit() TO lab_auditor");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.multi_request(uuid,uuid,bigint),d4.multi_commit(uuid,uuid,uuid,bigint),d4.multi_authorize(uuid,uuid,bigint,text),d4.multi_finalize(uuid,uuid) TO lab_control");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.multi_record_proof(uuid,uuid,uuid,jsonb),d4.multi_accept(uuid,uuid,jsonb),d4.multi_proof_status(uuid,uuid,uuid),d4.multi_accept_status(uuid,uuid) TO lab_verifier");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.recovery_info(uuid),d4.recovery_status(uuid,uuid,uuid) TO lab_verifier;GRANT EXECUTE ON FUNCTION d4.recovery_record(uuid,uuid,jsonb),d4.recovery_observe(uuid,uuid,uuid,text,jsonb),d4.recovery_accept(uuid,uuid) TO lab_verifier;GRANT EXECUTE ON FUNCTION d4.recovery_settle(uuid,uuid,bigint) TO lab_control;GRANT EXECUTE ON FUNCTION d4.recovery_audit() TO lab_auditor");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.absence_lineage(uuid),d4.absence_info(uuid),d4.absence_status(uuid,uuid,uuid),d4.absence_record(uuid,uuid,jsonb) TO lab_verifier;GRANT EXECUTE ON FUNCTION d4.absence_settle(uuid,uuid,bigint),d4.absence_authorize(uuid,uuid,bigint,text) TO lab_control;GRANT EXECUTE ON FUNCTION d4.absence_audit() TO lab_auditor");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.review_barrier_status(uuid,uuid),d4.review_info(uuid),d4.review_case_info(uuid),d4.review_existing_close(uuid),d4.review_status(uuid,uuid,uuid,bigint),d4.review_revise(uuid,uuid,uuid,bigint,jsonb),d4.review_candidate(uuid,uuid,uuid,text,jsonb),d4.review_candidate_info(uuid),d4.review_ingest(uuid,uuid),d4.review_contained(uuid,uuid,uuid,jsonb),d4.review_barrier(uuid,uuid,uuid,jsonb) TO lab_verifier;GRANT EXECUTE ON FUNCTION d4.review_close(uuid,uuid,uuid,text),d4.review_authorize(uuid,uuid,uuid,bigint,text) TO lab_control;GRANT EXECUTE ON FUNCTION d4.review_audit() TO lab_auditor");
   sql(c,"GRANT EXECUTE ON FUNCTION d4.presence_current(uuid),d4.presence_open(uuid,uuid,uuid,uuid) TO lab_control;GRANT EXECUTE ON FUNCTION d4.tree_info(uuid),d4.tree_record(uuid,uuid,jsonb) TO lab_verifier;GRANT EXECUTE ON FUNCTION d4.tree_audit() TO lab_auditor");
   store.configure(c,id(),Map.of("action","PROFILE","reason","D4 synthetic laboratory","epoch_id",id(),"calibration_epoch","fixture-v1","policy",Map.of("schema_version",SCHEMA_VERSION,"timezone","Europe/Madrid","max_operations",20,"max_edges",40,"max_candidates",40,"max_compute_ms",10000)));
   var projectA=insert(c,"INSERT INTO projects(code,name,workflow_type,priority) VALUES(?,'Synthetic A','GENTLE_AI',?)",id().toString(),scenario.equals("S02")?"P4":"P1");
   var projectB=insert(c,"INSERT INTO projects(code,name,workflow_type,priority) VALUES(?,'Synthetic B','GENTLE_AI','P0')",id().toString());
   var wa=LabSupport.uuid(participants,"worker-a");var wb=LabSupport.uuid(participants,"worker-b");
   var resources=new HashMap<UUID,UUID>();var accounts=new HashMap<UUID,UUID>();
   for(var w:List.of(wa,wb)){
    sql(c,"INSERT INTO workers(id,worker_key,host_name,state,last_heartbeat_at,capabilities) VALUES(?,?,'synthetic','ONLINE',clock_timestamp(),'{\"tools\":{\"code\":true}}')",w,w.toString());
    sql(c,"INSERT INTO d4.worker_catalog(worker_id) VALUES(?)",w);
    var session=id();sql(c,"SELECT d4.presence_open(?,?,?,NULL)",id(),w,session);sql(c,"SELECT d4.presence_beat(?,?,?,1)",id(),w,session);
    var resource=insert(c,"INSERT INTO resources(resource_key,worker_id,provider,subscription,capabilities) VALUES(?,?,'SYNTHETIC','none','{\"tools\":{\"code\":true}}')",id().toString(),w);resources.put(w,resource);
    var account=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'execution','OPERATIONS','WEEKLY',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '10 days','SYNTHETIC',1,100)",resource,id().toString());accounts.put(w,account);
    store.configure(c,id(),Map.of("action","CALENDAR","reason","Synthetic availability","resource_id",resource,"calendar_id",id(),"slots",List.of(Map.of("start",at.minusSeconds(3600),"end",at.plus(Duration.ofDays(10))))));
   }
   var a=operation(c,store,projectA,resources.get(wa),accounts.get(wa),at,Set.of("S14","S15","S16","S18","S20","S22").contains(scenario)?"MULTI":Set.of("S05","S08","S09","S13","S17","S21","S25","S28").contains(scenario)?"PARTIAL":scenario.equals("S02")||scenario.equals("S04")?"SURVIVOR":"SUCCESS",Set.of("S03","S12","S17","S19").contains(scenario),"shared",Set.of("S06","S07","S08","S09").contains(scenario),scenario.equals("S09"),scenario.equals("S10")?60000:900000,Set.of("S20","S21").contains(scenario));summary.put("operation_a",a.get("operation"));summary.put("task_a",a.get("task"));
   if(Set.of("S14","S15","S16","S18","S20","S22").contains(scenario)){
    var second=insert(c,"INSERT INTO d2.accounts(resource_id,dimension,unit,window_kind,window_key,window_start,window_end,provenance,confidence,initial_capacity) VALUES(?,'tokens','TOKENS','WEEKLY',?,clock_timestamp()-interval '1 hour',clock_timestamp()+interval '10 days','SYNTHETIC',1,100)",resources.get(wa),id().toString());
    multi(c,store,a.get("operation"),resources.get(wa),accounts.get(wa),second,at,scenario.equals("S20"));summary.put("account_a2",second.toString());
   }
   if(scenario.equals("S24")){
    var low=insert(c,"INSERT INTO projects(code,name,workflow_type,priority) VALUES(?,'Synthetic quarantined actor','GENTLE_AI','P3')",id().toString());
    var actor=operation(c,store,low,resources.get(wb),accounts.get(wb),at,"SUCCESS",false,"actor-shared",true,false,900000);summary.put("actor",actor.get("operation"));
    sql(c,"UPDATE operations SET policy_snapshot=jsonb_set(policy_snapshot,'{exclusive_keys}','[\"workspace:shared\"]'::jsonb) WHERE id=?",actor.get("operation"));sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES(?,?,'HARD')",a.get("task"),actor.get("task"));
   }
   if(Set.of("S10","S29").contains(scenario)){
    var low=insert(c,"INSERT INTO projects(code,name,workflow_type,priority) VALUES(?,'Synthetic polling successor','GENTLE_AI','P3')",id().toString());
    var next=operation(c,store,low,resources.get(wa),accounts.get(wa),at,"SUCCESS",false,scenario.equals("S29")?"next":"shared",false,false,60000);summary.put("operation_next",next.get("operation"));
   }
   if(scenario.equals("S11"))sql(c,"UPDATE operations SET policy_snapshot=policy_snapshot||'{\"requires_approval\":true}'::jsonb WHERE id=?",a.get("operation"));
   if(scenario.equals("S02")){
    var independent=operation(c,store,projectB,resources.get(wb),accounts.get(wb),at,"SUCCESS",false,"independent");summary.put("operation_b",independent.get("operation"));
    var blocked=operation(c,store,projectB,resources.get(wa),accounts.get(wa),at,"SUCCESS",false,"consumer");summary.put("hard_consumer",blocked.get("operation"));sql(c,"INSERT INTO task_dependencies(predecessor_task_id,successor_task_id,kind) VALUES(?,?,'HARD')",a.get("task"),blocked.get("task"));
    var sibling=operation(c,store,projectA,resources.get(wa),accounts.get(wa),at,"SUCCESS",false,"sibling");summary.put("unrelated_p4",sibling.get("operation"));
    var low=insert(c,"INSERT INTO projects(code,name,workflow_type,priority) VALUES(?,'Synthetic shared wait','GENTLE_AI','P3')",id().toString());
    var shared=operation(c,store,low,resources.get(wb),accounts.get(wb),at,"SUCCESS",false,"shared");summary.put("shared_waiter",shared.get("operation"));
   }
   var capture=store.capture(c,id());var result=new CapacityScheduler().plan(capture.request(),capture.snapshot());if(result.status()!=Status.COMPLETE&&result.status()!=Status.PARTIAL)throw new IllegalStateException("FIXTURE_PLAN_INVALID");
   var plan=store.publish(c,id(),id(),capture,result);summary.put("initial_plan",plan.toString());summary.put("account_a",accounts.get(wa).toString());summary.put("account_b",accounts.get(wb).toString());summary.put("worker_a",wa.toString());summary.put("worker_b",wb.toString());
  }
  Files.writeString(Path.of("/public/fixture.json"),LabSupport.JSON.writeValueAsString(summary));
  for(var root:List.of("/receiver-state","/worker-a-state","/worker-b-state"))try(var paths=Files.walk(Path.of(root))){for(var path:paths.sorted(Comparator.comparingInt(Path::getNameCount).reversed()).toList()){Files.setAttribute(path,"unix:uid",Integer.parseInt(System.getenv("LAB_UID")));Files.setAttribute(path,"unix:gid",Integer.parseInt(System.getenv("LAB_GID")));}}
  System.out.println("D4 synthetic bootstrap complete at V30");
 }
 private static Map<String,UUID> operation(Connection c,PlanningStore store,UUID project,UUID resource,UUID account,Instant at,String fixture,boolean pause,String workspace) throws Exception {
  return operation(c,store,project,resource,account,at,fixture,pause,workspace,false,false,900000);
 }
 private static Map<String,UUID> operation(Connection c,PlanningStore store,UUID project,UUID resource,UUID account,Instant at,String fixture,boolean pause,String workspace,boolean prolonged,boolean ignoreCheckpoint,long durationMs) throws Exception {
  return operation(c,store,project,resource,account,at,fixture,pause,workspace,prolonged,ignoreCheckpoint,durationMs,false);
 }
 private static Map<String,UUID> operation(Connection c,PlanningStore store,UUID project,UUID resource,UUID account,Instant at,String fixture,boolean pause,String workspace,boolean prolonged,boolean ignoreCheckpoint,long durationMs,boolean absentFirst) throws Exception {
  String stepManifest="{\"schema\":\"d4.steps.v1\",\"steps\":[{\"id\":\"step-1\",\"units\":4},{\"id\":\"step-2\",\"units\":6}]}";
  var ctx=new LinkedHashMap<String,Object>(Map.of("schema","d4.fixture.v1","fixture",fixture,"fault_pause_callback",pause,"fault_survive_lease",fixture.equals("SURVIVOR")));if(fixture.equals("PARTIAL"))ctx.put("step_manifest",LabSupport.JSON.readTree(stepManifest));
  if(Set.of("S23","S24","S29").contains(LabSupport.JSON.readTree(Files.readString(Path.of("/public/participants.json"))).path("scenario").asText())&&workspace.equals("shared"))ctx.put("fault_pause_effect_first",true);
  if(absentFirst)ctx.put("fault_absent_first_generation",true);
  if(prolonged)ctx.put("long_running",true);if(ignoreCheckpoint)ctx.put("fault_ignore_checkpoint",true);
  var scenario=LabSupport.JSON.readTree(Files.readString(Path.of("/public/participants.json"))).path("scenario").asText();
  if(Set.of("S26","S27").contains(scenario))ctx.put("tree_fixture",Map.of("base_files",Map.of("result.txt",Base64.getEncoder().encodeToString("base\n".getBytes(java.nio.charset.StandardCharsets.UTF_8))),"candidate_files",Map.of("result.txt",Base64.getEncoder().encodeToString("candidate\n".getBytes(java.nio.charset.StandardCharsets.UTF_8)))));
  byte[] context=LabSupport.JSON.writeValueAsBytes(ctx);
  var task=insert(c,"INSERT INTO tasks(project_id,task_key,title) VALUES(?,?,'Synthetic fixture')",project,id().toString());
  String policy=LabSupport.JSON.writeValueAsString(Map.of("interruptible",fixture.equals("PARTIAL"),"required_capabilities",Map.of("tools",Map.of("code",true)),"exclusive_keys",List.of("workspace:"+workspace)));
  var operation=insert(c,"INSERT INTO operations(task_id,operation_type,idempotency_key,context_pack_sha256,context_pack_ref,policy_snapshot) VALUES(?,'CODE',?,?,'synthetic-lab-context',?::jsonb)",task,id().toString(),LabSupport.hash(context),policy);
  if(Set.of("S26","S27").contains(scenario)){
   byte[] base="base\n".getBytes(java.nio.charset.StandardCharsets.UTF_8),target=(scenario.equals("S27")?"base\n":"candidate\n").getBytes(java.nio.charset.StandardCharsets.UTF_8);
   var expected=Map.of("result.txt",TreeVerifier.Artifact.of(target,false));String manifest=LabSupport.JSON.writeValueAsString(Map.of("result.txt",Map.of("size",target.length,"sha256",LabSupport.hash(target),"executable",false)));String bm=LabSupport.JSON.writeValueAsString(Map.of("result.txt",Map.of("size",base.length,"sha256",LabSupport.hash(base),"executable",false)));
   sql(c,"INSERT INTO d4.tree_requirements VALUES(?,?::jsonb,?,?,?::jsonb)",operation,manifest,TreeVerifier.manifest(expected),scenario.equals("S27"),bm);
  }
  if(!fixture.equals("MULTI"))sql(c,"INSERT INTO d4.lab_intents(operation_id,context_bytes,consumed_units) VALUES(?,?,?)",operation,context,fixture.equals("PARTIAL")?10:8);
  if(fixture.equals("PARTIAL")){String manifest="{\"schema\":\"d4.steps.v1\",\"steps\":[{\"id\":\"step-1\",\"units\":4},{\"id\":\"step-2\",\"units\":6}]}";sql(c,"INSERT INTO d4.step_intents VALUES(?,?::jsonb,encode(digest((?::jsonb)::text,'sha256'),'hex'))",operation,manifest,manifest);}
  store.configure(c,id(),Map.ofEntries(Map.entry("action","ESTIMATE"),Map.entry("reason","D4 synthetic calibrated units"),Map.entry("estimate_id",id()),Map.entry("operation_id",operation),Map.entry("resource_id",resource),Map.entry("units",Map.of(account,10)),Map.entry("duration_ms",durationMs),Map.entry("confidence",1),Map.entry("calibration_ref","fixture-v1"),Map.entry("provenance","SYNTHETIC"),Map.entry("observed_at",at.minusSeconds(1)),Map.entry("valid_until",at.plus(Duration.ofDays(10)))));
  return Map.of("operation",operation,"task",task);
 }
 static void multi(Connection c,PlanningStore store,UUID operation,UUID resource,UUID a,UUID b,Instant at) throws Exception {
  multi(c,store,operation,resource,a,b,at,false);
 }
 static void multi(Connection c,PlanningStore store,UUID operation,UUID resource,UUID a,UUID b,Instant at,boolean absentFirst) throws Exception {
  var accounts=new TreeMap<String,Object>();for(var account:List.of(a,b))try(var p=c.prepareStatement("SELECT dimension,unit,window_start,window_end FROM d2.accounts WHERE id=?")){p.setObject(1,account);try(var r=p.executeQuery()){r.next();accounts.put(account.toString(),Map.of("dimension",r.getString(1),"unit",r.getString(2),"start",r.getTimestamp(3).toInstant().toString(),"end",r.getTimestamp(4).toInstant().toString(),"original",account.equals(a)?10:6));}}
  var steps=new ArrayList<Map<String,Object>>();int[] ca={4,3,3},cb={1,2,3};for(int n=0;n<3;n++){String step="step-"+(n+1);steps.add(Map.of("id",step,"effect_hash",LabSupport.hash(("synthetic-effect:"+operation+":"+step).getBytes(java.nio.charset.StandardCharsets.UTF_8)),"cost",Map.of(a.toString(),ca[n],b.toString(),cb[n])));}
  var manifest=Map.of("schema","d4.steps.v2","resource",resource.toString(),"pool","PLANNED","accounts",accounts,"steps",steps);
  var ctx=new LinkedHashMap<String,Object>(Map.of("schema","d4.fixture.v2","fixture","PARTIAL","step_manifest",manifest));if(absentFirst)ctx.put("fault_absent_first_generation",true);
  byte[] context=LabSupport.JSON.writeValueAsBytes(ctx);
  sql(c,"UPDATE operations SET context_pack_sha256=?,policy_snapshot=policy_snapshot||'{\"interruptible\":true,\"max_attempts\":3}'::jsonb WHERE id=?",LabSupport.hash(context),operation);
  sql(c,"INSERT INTO d4.lab_intents(operation_id,context_bytes,consumed_units) VALUES(?,?,10)",operation,context);
  String text=LabSupport.JSON.writeValueAsString(manifest);sql(c,"INSERT INTO d4.multi_intents VALUES(?,?::jsonb,encode(digest((?::jsonb)::text,'sha256'),'hex'))",operation,text,text);
  UUID previous;try(var p=c.prepareStatement("SELECT estimate_id FROM d3.estimate_heads WHERE operation_id=? AND resource_id=?")){p.setObject(1,operation);p.setObject(2,resource);try(var r=p.executeQuery()){r.next();previous=r.getObject(1,UUID.class);}}
  store.configure(c,id(),Map.ofEntries(Map.entry("action","ESTIMATE"),Map.entry("reason","Exact synthetic multicount vector"),Map.entry("expected_estimate_id",previous),Map.entry("estimate_id",id()),Map.entry("operation_id",operation),Map.entry("resource_id",resource),Map.entry("units",Map.of(a,10,b,6)),Map.entry("duration_ms",60000),Map.entry("confidence",1),Map.entry("calibration_ref","fixture-v1"),Map.entry("provenance","SYNTHETIC"),Map.entry("observed_at",at.minusSeconds(1)),Map.entry("valid_until",at.plus(Duration.ofDays(10)))));
 }

}
