// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;

import io.github.isidorotrevino.planner.runtime.*;
import io.github.isidorotrevino.planner.postgres.PlanningCoordinator;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.*;
import tools.jackson.databind.JsonNode;
import java.nio.file.*;
import java.time.*;
import java.util.*;

@RestController
class LabHealth {
 @GetMapping("/lab/health") Map<String,Object> health(){return Map.of("ready",true,"role",LabSupport.config("role"));}
}
@RestControllerAdvice
class LabErrors {
 @ExceptionHandler(Exception.class) ResponseEntity<Map<String,String>> error(Exception ex){int status=ex instanceof LabSupport.Denied?403:ex instanceof EffectJournal.Unavailable?409:ex instanceof LabSupport.Rejected r?r.status:ex instanceof java.sql.SQLException s&&"42501".equals(s.getSQLState())?403:409;return ResponseEntity.status(status).header("Cache-Control","no-store").body(Map.of("error","LAB_REJECTED_QUERY_OR_REPLAY"));}
}
@RestController @ConditionalOnProperty(name="lab.role",havingValue="control")
class LabControl {
 @PostMapping("/lab/grant") Object grant(HttpServletRequest r) throws Exception {
  var wid=LabSupport.worker(r);var b=LabSupport.body(r);if(b.size()!=2||!b.has("command_id")||!b.has("delivery_id"))throw new LabSupport.Denied("EXPLICIT_GRANT_FIELDS_REQUIRED");var receiver=UUID.fromString(Files.readString(Path.of("/public/receiver.id")).strip());
  var info=LabSupport.sql("SELECT d4.lab_authorize(?,?,?,?)::text",LabSupport.uuid(b,"command_id"),wid,LabSupport.uuid(b,"delivery_id"),receiver);
  info=d4Info(info,LabSupport.uuid(b,"delivery_id"));
  var expires=Instant.parse(LabSupport.text(info,"lease_expires_at"));var g=new EffectJournal.Grant(receiver,LabSupport.identity(info),LabSupport.text(info,"context_hash"),LabSupport.text(info,"context_hash"),LabSupport.text(info,"policy_hash"),allowed(info),Instant.parse(LabSupport.text(info,"issued_at")),expires,expires);
  return Map.of("authorization",LabSupport.grantMap(EffectJournal.sign(g,LabSupport.privateKey("signing"))),"info",info);
 }
 private static tools.jackson.databind.JsonNode d4Info(tools.jackson.databind.JsonNode authorization,UUID delivery) throws Exception {var current=LabSupport.sql("SELECT d4.multi_inspect(?)::text",delivery);if(current.has("manifest_compatible")&&!current.path("manifest_compatible").asBoolean())throw new LabSupport.Denied("INCOMPATIBLE_V2_INTENTION");var merged=(tools.jackson.databind.node.ObjectNode)authorization.deepCopy();for(var key:List.of("is_checkpoint_fixture","manifest","manifest_hash","allowed_steps","incremental_units","continuation","row_version","multi_checkpoint","needs_checkpoint","current_step","incremental_vector"))if(current.has(key))merged.set(key,current.path(key));return merged;}
 private static Set<String> allowed(tools.jackson.databind.JsonNode info){if(!info.has("allowed_steps"))return Set.of("step-1");var steps=new TreeSet<String>();info.path("allowed_steps").forEach(n->steps.add(n.asText()));return steps;}
 @PostMapping("/lab/checkpoint/request") Object checkpointRequest(HttpServletRequest r) throws Exception {LabSupport.require(r,"driver");var b=LabSupport.body(r);return LabSupport.sql("SELECT d4.checkpoint_request(?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"delivery_id"),b.path("expected_version").asLong());}
 @PostMapping("/lab/checkpoint/signal") Object checkpointSignal(HttpServletRequest r) throws Exception {var wid=LabSupport.worker(r);var b=LabSupport.body(r);if(b.size()!=1||!b.has("delivery_id"))throw new LabSupport.Denied("EXPLICIT_DELIVERY_REQUIRED");return LabSupport.sql("SELECT d4.worker_checkpoint_signal(?,?)::text",wid,LabSupport.uuid(b,"delivery_id"));}
 @PostMapping("/lab/execution/status") Object executionStatus(HttpServletRequest r) throws Exception {var wid=LabSupport.worker(r);var b=LabSupport.body(r);if(b.size()!=1||!b.has("delivery_id"))throw new LabSupport.Denied("EXPLICIT_DELIVERY_REQUIRED");return LabSupport.sql("SELECT d4.worker_execution_status(?,?)::text",wid,LabSupport.uuid(b,"delivery_id"));}
 @PostMapping("/lab/checkpoint/commit") Object checkpointCommit(HttpServletRequest r) throws Exception {LabSupport.require(r,"verifier");var b=LabSupport.body(r);return LabSupport.sql("SELECT d4.commit_checkpoint(?,?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"request_id"),LabSupport.uuid(b,"proof_id"),b.path("expected_version").asLong());}
 @PostMapping("/lab/checkpoint/authorize") Object authorize(HttpServletRequest r) throws Exception {LabSupport.require(r,"driver");var b=LabSupport.body(r);return LabSupport.sql("SELECT d4.authorize_continuation(?,?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"checkpoint_id"),b.path("expected_version").asLong(),LabSupport.text(b,"reason"));}
 @PostMapping({"/lab/checkpoint/replan","/lab/plan"}) Object continuationPlan(HttpServletRequest r) throws Exception {
  LabSupport.require(r,"driver");var store=new io.github.isidorotrevino.planner.postgres.AbsencePlanningStore();
  for(int retry=0;;retry++)try(var c=LabSupport.connection()){
   store.observeEligibility(c,UUID.randomUUID());var capture=store.capture(c,UUID.randomUUID());var result=new io.github.isidorotrevino.planner.scheduler.CapacityScheduler().plan(capture.request(),capture.snapshot());var plan=store.publish(c,UUID.randomUUID(),UUID.randomUUID(),capture,result);return Map.of("schema","d4.continuation.snapshot.v1","plan",plan.toString(),"cas_retries",retry);
  }catch(java.sql.SQLException ex){if(!"40001".equals(ex.getSQLState())||retry>=2)throw ex;}
 }
 @PostMapping("/lab/checkpoint/finalize") Object finish(HttpServletRequest r) throws Exception {LabSupport.require(r,"verifier");var b=LabSupport.body(r);return LabSupport.sql("SELECT d4.finalize_continuation(?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"delivery_id"));}
 @PostMapping("/lab/admin") Object admin(HttpServletRequest r) throws Exception {LabSupport.require(r,"verifier");var b=LabSupport.body(r);return LabSupport.sql("SELECT d4.lab_admin(?,?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"delivery_id"),LabSupport.text(b,"action"),b.has("proof_id")?LabSupport.uuid(b,"proof_id"):null);}
 @PostMapping("/lab/close-token") Object close(HttpServletRequest r) throws Exception {LabSupport.require(r,"verifier");var b=LabSupport.body(r);var info=LabSupport.sql("SELECT d4.lab_inspect(?)::text",LabSupport.uuid(b,"delivery_id"));return LabSupport.closeMap(EffectJournal.signClose(UUID.fromString(Files.readString(Path.of("/public/receiver.id")).strip()),LabSupport.identity(info),LabSupport.uuid(b,"command_id"),LabSupport.privateKey("signing")));}
 @PostMapping("/lab/replan") Object replan(HttpServletRequest r) throws Exception {LabSupport.require(r,"driver");try(var c=LabSupport.connection()){var o=new PlanningCoordinator().tick(c,UUID.randomUUID(),UUID.randomUUID(),UUID.randomUUID());return Map.of("state",o.state().name(),"plan",Objects.toString(o.planId(),""));}}
}
@RestController @ConditionalOnProperty(name="lab.role",havingValue="receiver")
class LabReceiver {
 private final EffectJournal journal;
 LabReceiver() throws Exception {journal=EffectJournal.open(Path.of("/state/receiver"),LabSupport.publicKey("control"),Clock.systemUTC());if(!journal.receiverId().toString().equals(Files.readString(Path.of("/public/receiver.id")).strip()))throw new IllegalStateException("RECEIVER_HISTORY_MISMATCH");}
 @GetMapping("/lab/meta") Object meta(HttpServletRequest r) throws Exception {LabSupport.require(r,"driver","control","verifier");return Map.of("receiver_id",journal.receiverId().toString());}
 @PostMapping("/lab/install") Object install(HttpServletRequest r) throws Exception {var wid=LabSupport.worker(r);var g=LabSupport.grant(LabSupport.body(r));if(!wid.equals(g.grant().identity().worker()))throw new LabSupport.Denied("WORKER_MISMATCH");return Map.of("sequence",journal.install(g));}
 @PostMapping("/lab/effect") Object effect(HttpServletRequest r) throws Exception {var wid=LabSupport.worker(r);var b=LabSupport.body(r);var g=LabSupport.grant(b.path("authorization"));if(!wid.equals(g.grant().identity().worker()))throw new LabSupport.Denied("WORKER_MISMATCH");return journal.apply(g,LabSupport.text(b,"step"),Base64.getDecoder().decode(LabSupport.text(b,"payload")));}
 @PostMapping("/lab/query") Object query(HttpServletRequest r) throws Exception {LabSupport.require(r,"verifier","driver");var b=LabSupport.body(r);return journal.query(LabSupport.uuid(b,"operation"),LabSupport.text(b,"intent_hash"),LabSupport.text(b,"step"),b.path("generation").asLong());}
 @PostMapping("/lab/close") Object close(HttpServletRequest r) throws Exception {LabSupport.require(r,"verifier");return Map.of("sequence",journal.close(LabSupport.close(LabSupport.body(r))));}
 @PostMapping("/lab/seal") Object seal(HttpServletRequest r) throws Exception {LabSupport.require(r,"verifier");var sealed=journal.seal(LabSupport.close(LabSupport.body(r)));String facts=LabSupport.JSON.writeValueAsString(sealed);var signer=java.security.Signature.getInstance("Ed25519");signer.initSign(LabSupport.privateKey("sealing"));signer.update(facts.getBytes(java.nio.charset.StandardCharsets.UTF_8));return Map.of("facts",facts,"signature",Base64.getEncoder().encodeToString(signer.sign()));}

}
