// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;
import java.util.*;
/** A20: driver supplies IDs; verifier obtains actual stopped artifacts and closed receiver facts. */
@RestController @ConditionalOnProperty(name="lab.role",havingValue="verifier")
class AbsenceVerifier {
 private final CheckpointVerifier artifacts;private final java.net.http.HttpClient client=LabSupport.client();
 AbsenceVerifier(CheckpointVerifier artifacts)throws Exception{this.artifacts=artifacts;}
 @PostMapping("/lab/absence/settle") Object settle(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"delivery_id","proof_id","command_id");var delivery=LabSupport.uuid(b,"delivery_id");var pid=LabSupport.uuid(b,"proof_id");var cid=LabSupport.uuid(b,"command_id");
  var previous=LabSupport.sql("SELECT d4.absence_status(?,?,?)::text",pid,delivery,cid);if(!previous.isNull()){if(!previous.path("pending").asBoolean())return previous;return commit(cid,pid,previous.path("expected_version").asLong());}
  var i=LabSupport.sql("SELECT d4.absence_info(?)::text",delivery);
  if(Set.of("RUNNING","LEASED","VERIFYING").contains(LabSupport.text(i,"state"))&&i.path("lease_expired").asBoolean()){
   LabSupport.request(client,"POST","https://control-plane:8443/lab/admin",Map.of("command_id",UUID.randomUUID().toString(),"delivery_id",delivery.toString(),"action","EXPIRE"));i=LabSupport.sql("SELECT d4.absence_info(?)::text",delivery);
  }
  if(!i.has("manifest_hash"))((tools.jackson.databind.node.ObjectNode)i).put("manifest_hash",LabSupport.text(i,"recovery_manifest_hash"));
  var ctx=LabSupport.JSON.readTree(Base64.getMimeDecoder().decode(LabSupport.text(i,"context_b64")));String fixture=ctx.path("fixture").asText().equals("SUCCESS")?"SUCCESS":i.path("multi_checkpoint").asBoolean()?i.path("needs_checkpoint").asBoolean()?"PARTIAL":"SUFFIX":i.path("continuation").asBoolean()?"SUFFIX":"PARTIAL";
  var proof=artifacts.stoppedArtifact(i,fixture);var seal=artifacts.seal(delivery,pid,i);
  for(var receipt:seal.path("steps"))if(!receipt.path("status").asText().equals("ABSENT")||!receipt.path("closed").asBoolean())throw new LabSupport.Denied("CLOSED_ABSENCE_SUFFIX_REQUIRED");
  proof.put("row_version",i.path("row_version"));proof.putAll(Map.of("schema","d4.absence.proof.v1","recovery_manifest_hash",LabSupport.text(i,"recovery_manifest_hash"),"receipt_basis",i.path("receipt_basis"),"receiver_closed",true,"close_sequence",seal.path("sequence").asLong(),"receiver_seal",seal,"receipts",seal.path("steps"),"parent_checkpoint",i.path("parent_checkpoint")));
  LabSupport.sql("SELECT d4.absence_record(?,?,?::jsonb)::text",pid,delivery,LabSupport.JSON.writeValueAsString(proof));return commit(cid,pid,i.path("row_version").asLong());
 }
 private Object commit(UUID cid,UUID pid,long version)throws Exception{return LabSupport.request(client,"POST","https://control-plane:8443/lab/absence/commit",Map.of("command_id",cid.toString(),"proof_id",pid.toString(),"expected_version",version));}
}
@RestController @ConditionalOnProperty(name="lab.role",havingValue="control")
class AbsenceControl {
 @PostMapping("/lab/absence/commit") Object commit(HttpServletRequest r)throws Exception{LabSupport.require(r,"verifier");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","proof_id","expected_version");return LabSupport.sql("SELECT d4.absence_settle(?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"proof_id"),MultiCheckpointVerifier.version(b));}
 @PostMapping("/lab/absence/authorize") Object authorize(HttpServletRequest r)throws Exception{LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","seal_id","expected_version","reason");return LabSupport.sql("SELECT d4.absence_authorize(?,?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"seal_id"),MultiCheckpointVerifier.version(b),LabSupport.text(b,"reason"));}
}
