// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;
import tools.jackson.databind.JsonNode;
import java.nio.charset.StandardCharsets;
import java.util.*;
/** A21/A22: IDs-only ingress, observed facts, verified seal and independently observed stop. */
@RestController @ConditionalOnProperty(name="lab.role",havingValue="verifier")
class ReviewVerifier {
 private final CheckpointVerifier artifacts;private final java.net.http.HttpClient client=LabSupport.client();
 ReviewVerifier(CheckpointVerifier artifacts)throws Exception{this.artifacts=artifacts;}
 private JsonNode info(UUID delivery)throws Exception{return LabSupport.sql("SELECT d4.review_info(?)::text",delivery);}
 @PostMapping("/lab/review/info") Object inspect(HttpServletRequest r)throws Exception{LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"delivery_id");return info(LabSupport.uuid(b,"delivery_id"));}
 @PostMapping("/lab/review/capture") Object capture(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","delivery_id","step");var delivery=LabSupport.uuid(b,"delivery_id");var prior=LabSupport.sql("SELECT d4.review_candidate_info(?)::text",LabSupport.uuid(b,"command_id"));if(!prior.isNull()){if(!LabSupport.text(prior,"delivery_id").equals(delivery.toString())||!LabSupport.text(prior,"step").equals(LabSupport.text(b,"step")))throw new LabSupport.Denied("CANDIDATE_REPLAY_CONFLICT");return Map.of("candidate_id",LabSupport.text(b,"command_id"));}var i=LabSupport.sql("SELECT d4.recovery_info(?)::text",delivery);
  var meta=LabSupport.request(client,"GET","https://effect-receiver:8443/lab/meta",null);var receipt=LabSupport.request(client,"POST","https://effect-receiver:8443/lab/query",Map.of("operation",LabSupport.text(i,"operation"),"intent_hash",LabSupport.text(i,"context_hash"),"generation",i.path("generation").asLong(),"step",LabSupport.text(b,"step")));
  return LabSupport.sql("SELECT d4.review_candidate(?,?,?,?,?::jsonb)::text",LabSupport.uuid(b,"command_id"),delivery,LabSupport.uuid(meta,"receiver_id"),LabSupport.text(b,"step"),LabSupport.JSON.writeValueAsString(receipt));
 }
 @PostMapping("/lab/review/ingest") Object ingest(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","candidate_id");var result=LabSupport.sql("SELECT d4.review_ingest(?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"candidate_id"));for(var id:result.path("case_ids")){var caseId=UUID.fromString(id.asText());var c=LabSupport.sql("SELECT d4.review_case_info(?)::text",caseId);if(c.path("open").asBoolean())contain(caseId);}return result;
 }
 private JsonNode contain(UUID caseId)throws Exception{
  var c=LabSupport.sql("SELECT d4.review_case_info(?)::text",caseId);
  if(!c.path("open").asBoolean())throw new LabSupport.Denied("OPEN_REVIEW_REQUIRED");
  for(var a:c.path("affected")){
   var attempt=LabSupport.uuid(a,"attempt_id");var command=a.path("close_command").isNull()?UUID.nameUUIDFromBytes(("d4.review.close:"+caseId+":"+attempt).getBytes(StandardCharsets.UTF_8)):LabSupport.uuid(a,"close_command");
   var seal=artifacts.seal(LabSupport.uuid(a,"delivery_id"),command,a.path("info"));LabSupport.sql("SELECT d4.review_contained(?,?,?,?::jsonb)::text",UUID.nameUUIDFromBytes(("d4.containment.fact:"+caseId+":"+attempt).getBytes(StandardCharsets.UTF_8)),caseId,attempt,LabSupport.JSON.writeValueAsString(seal));
  }
  return c;
 }
 @PostMapping("/lab/review/contain") Object containment(HttpServletRequest r)throws Exception{LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"case_id");return contain(LabSupport.uuid(b,"case_id"));}
 @PostMapping("/lab/review/barriers") Object barriers(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"case_id");var caseId=LabSupport.uuid(b,"case_id");var c=contain(caseId);var results=new ArrayList<JsonNode>();
  for(var a:c.path("affected")){
   var attempt=LabSupport.uuid(a,"attempt_id");var command=a.path("close_command").isNull()?UUID.nameUUIDFromBytes(("d4.review.close:"+caseId+":"+attempt).getBytes(StandardCharsets.UTF_8)):LabSupport.uuid(a,"close_command");
   var prior=LabSupport.sql("SELECT d4.review_barrier_status(?,?)::text",caseId,attempt);if(!prior.isNull()){results.add(prior);continue;}
   var proof=artifacts.stoppedObservation(a.path("info"));var seal=artifacts.seal(LabSupport.uuid(a,"delivery_id"),command,a.path("info"));proof.putAll(Map.of("schema","d4.review.barrier.v1","receiver_closed",true,"receiver_seal",seal));
   var pid=UUID.nameUUIDFromBytes(("d4.review.barrier:"+caseId+":"+attempt).getBytes(StandardCharsets.UTF_8));results.add(LabSupport.sql("SELECT d4.review_barrier(?,?,?,?::jsonb)::text",pid,caseId,attempt,LabSupport.JSON.writeValueAsString(proof)));
  }
  return Map.of("barriers",results);
 }
 @PostMapping("/lab/review/expire") Object expire(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"case_id");var caseId=LabSupport.uuid(b,"case_id");var c=LabSupport.sql("SELECT d4.review_case_info(?)::text",caseId);if(!c.path("open").asBoolean())throw new LabSupport.Denied("OPEN_REVIEW_REQUIRED");
  var results=new ArrayList<JsonNode>();for(var a:c.path("affected")){var i=a.path("info");if(Set.of("LEASED","RUNNING","VERIFYING").contains(LabSupport.text(i,"state"))){if(!i.path("lease_expired").asBoolean())throw new LabSupport.Denied("ACTUAL_LEASE_EXPIRY_REQUIRED");var cid=UUID.nameUUIDFromBytes(("d4.review.expire:"+caseId+":"+LabSupport.text(a,"attempt_id")).getBytes(StandardCharsets.UTF_8));results.add(LabSupport.request(client,"POST","https://control-plane:8443/lab/admin",Map.of("command_id",cid.toString(),"delivery_id",LabSupport.text(a,"delivery_id"),"action","EXPIRE")));}}
  return Map.of("expired",results);
 }
 @PostMapping("/lab/review/revise") Object revise(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","delivery_id","expected_head","expected_version");var cid=LabSupport.uuid(b,"command_id");var delivery=LabSupport.uuid(b,"delivery_id");UUID parent=b.path("expected_head").isNull()?null:LabSupport.uuid(b,"expected_head");long version=MultiCheckpointVerifier.version(b);
  var previous=LabSupport.sql("SELECT d4.review_status(?,?,?,?)::text",cid,delivery,parent,version);if(!previous.isNull())return previous;
  var a=info(delivery);var i=a.path("info");if(!i.has("manifest_hash"))((tools.jackson.databind.node.ObjectNode)i).put("manifest_hash",LabSupport.text(i,"recovery_manifest_hash"));
  var ctx=LabSupport.JSON.readTree(Base64.getMimeDecoder().decode(LabSupport.text(i,"context_b64")));String fixture=ctx.path("fixture").asText().equals("SUCCESS")?"SUCCESS":a.path("receipts").size()==1?"SUFFIX":"PARTIAL";
  var proof=artifacts.stoppedArtifact(i,fixture);var seal=artifacts.seal(delivery,LabSupport.uuid(a,"close_command"),i);
  proof.putAll(Map.of("schema","d4.review.proof.v1","receipt_basis",a.path("current_basis"),"receiver_closed",true,"receiver_seal",seal,"receipts",seal.path("steps")));
  return LabSupport.sql("SELECT d4.review_revise(?,?,?,?,?::jsonb)::text",cid,delivery,parent,version,LabSupport.JSON.writeValueAsString(proof));
 }
}
@RestController @ConditionalOnProperty(name="lab.role",havingValue="control")
class ReviewControl {
 @PostMapping("/lab/review/close") Object close(HttpServletRequest r)throws Exception{LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","case_id","revision_id","reason");return LabSupport.sql("SELECT d4.review_close(?,?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"case_id"),LabSupport.uuid(b,"revision_id"),LabSupport.text(b,"reason"));}
 @PostMapping("/lab/review/authorize") Object authorize(HttpServletRequest r)throws Exception{LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","checkpoint_id","revision_id","expected_version","reason");return LabSupport.sql("SELECT d4.review_authorize(?,?,?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"checkpoint_id"),LabSupport.uuid(b,"revision_id"),MultiCheckpointVerifier.version(b),LabSupport.text(b,"reason"));}
}
