// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;
import java.util.*;
/** Independent receiver observations and stopped-artifact recovery; driver supplies IDs only. */
@RestController @ConditionalOnProperty(name="lab.role",havingValue="verifier")
class RecoveryVerifier {
 private final CheckpointVerifier artifacts;private final java.net.http.HttpClient client=LabSupport.client();
 RecoveryVerifier(CheckpointVerifier artifacts)throws Exception{this.artifacts=artifacts;}
 @PostMapping("/lab/recovery/observe") Object observe(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","delivery_id","step");var delivery=LabSupport.uuid(b,"delivery_id");var i=LabSupport.sql("SELECT d4.recovery_info(?)::text",delivery);
  var meta=LabSupport.request(client,"GET","https://effect-receiver:8443/lab/meta",null);var receipt=LabSupport.request(client,"POST","https://effect-receiver:8443/lab/query",Map.of("operation",LabSupport.text(i,"operation"),"intent_hash",LabSupport.text(i,"context_hash"),"generation",i.path("generation").asLong(),"step",LabSupport.text(b,"step")));
  return LabSupport.sql("SELECT d4.recovery_observe(?,?,?,?,?::jsonb)::text",LabSupport.uuid(b,"command_id"),delivery,LabSupport.uuid(meta,"receiver_id"),LabSupport.text(b,"step"),LabSupport.JSON.writeValueAsString(receipt));
 }
 @PostMapping("/lab/recovery/settle") Object settle(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"delivery_id","proof_id","command_id");var delivery=LabSupport.uuid(b,"delivery_id");var pid=LabSupport.uuid(b,"proof_id");var cid=LabSupport.uuid(b,"command_id");
  var previous=LabSupport.sql("SELECT d4.recovery_status(?,?,?)::text",pid,delivery,cid);if(!previous.isNull()){if(!previous.path("pending").asBoolean())return previous;return LabSupport.request(client,"POST","https://control-plane:8443/lab/recovery/commit",Map.of("command_id",cid.toString(),"proof_id",pid.toString(),"expected_version",previous.path("expected_version").asLong()));}
  var i=LabSupport.sql("SELECT d4.recovery_info(?)::text",delivery);
  if(Set.of("RUNNING","LEASED","VERIFYING").contains(LabSupport.text(i,"state"))&&i.path("lease_expired").asBoolean()){
   LabSupport.request(client,"POST","https://control-plane:8443/lab/admin",Map.of("command_id",UUID.randomUUID().toString(),"delivery_id",delivery.toString(),"action","EXPIRE"));i=LabSupport.sql("SELECT d4.recovery_info(?)::text",delivery);
  }
  if(!i.has("manifest_hash"))((tools.jackson.databind.node.ObjectNode)i).put("manifest_hash",LabSupport.text(i,"recovery_manifest_hash"));
  var ctx=LabSupport.JSON.readTree(Base64.getMimeDecoder().decode(LabSupport.text(i,"context_b64")));String fixture=ctx.path("fixture").asText().equals("SUCCESS")?"SUCCESS":i.path("multi_checkpoint").asBoolean()?i.path("needs_checkpoint").asBoolean()?"PARTIAL":"SUFFIX":i.path("continuation").asBoolean()?"SUFFIX":"PARTIAL";
  var proof=artifacts.stoppedArtifact(i,fixture);var seal=artifacts.seal(delivery,pid,i);
  proof.put("row_version",i.path("row_version"));
  proof.putAll(Map.of("schema","d4.recovery.proof.v1","recovery_manifest_hash",LabSupport.text(i,"recovery_manifest_hash"),"receipt_basis",i.path("receipt_basis"),"receiver_closed",true,"close_sequence",seal.path("sequence").asLong(),"receiver_seal",seal,"receipts",seal.path("steps"),"parent_checkpoint",i.path("parent_checkpoint")));
  LabSupport.sql("SELECT d4.recovery_record(?,?,?::jsonb)::text",pid,delivery,LabSupport.JSON.writeValueAsString(proof));
  return LabSupport.request(client,"POST","https://control-plane:8443/lab/recovery/commit",Map.of("command_id",cid.toString(),"proof_id",pid.toString(),"expected_version",i.path("row_version").asLong()));
 }
 @PostMapping("/lab/recovery/accept") Object accept(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","resolution_id");return LabSupport.sql("SELECT d4.recovery_accept(?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"resolution_id"));
 }
}
@RestController @ConditionalOnProperty(name="lab.role",havingValue="control")
class RecoveryControl {
 @PostMapping("/lab/recovery/commit") Object commit(HttpServletRequest r)throws Exception{LabSupport.require(r,"verifier");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","proof_id","expected_version");return LabSupport.sql("SELECT d4.recovery_settle(?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"proof_id"),MultiCheckpointVerifier.version(b));}
}
