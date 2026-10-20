// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;
import io.github.isidorotrevino.planner.runtime.*;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;
import tools.jackson.databind.JsonNode;
import java.net.http.*;
import java.nio.file.*;
import java.security.*;
import java.time.*;
import java.util.*;

/** Independent two-step synthetic verifier, never trusts worker acceptance. */
@RestController @ConditionalOnProperty(name="lab.role",havingValue="verifier")
class CheckpointVerifier {
 private final HttpClient client=LabSupport.client();
 CheckpointVerifier() throws Exception {}
 private JsonNode signed(JsonNode envelope,String authority) throws Exception {
  var text=LabSupport.text(envelope,"facts");var signature=Signature.getInstance("Ed25519");signature.initVerify(LabSupport.publicKey(authority));signature.update(text.getBytes(java.nio.charset.StandardCharsets.UTF_8));if(!signature.verify(Base64.getDecoder().decode(LabSupport.text(envelope,"signature"))))throw new LabSupport.Denied("SIGNED_FACTS_REQUIRED");return LabSupport.JSON.readTree(text);
 }
 Map<String,Object> stoppedArtifact(JsonNode info,String fixture) throws Exception {
  var identity=LabSupport.identity(info);var envelope=LabSupport.JSON.readTree(Files.readString(Path.of("/observations/"+identity.attempt()+".json")));var facts=signed(envelope,"observer");
  if(!LabSupport.identity(facts).equals(identity)||!facts.path("process_stopped").asBoolean()||!facts.path("identity_match").asBoolean()||!LabSupport.text(facts,"campaign").equals(LabSupport.config("campaign"))||Duration.between(Instant.parse(LabSupport.text(facts,"observed_at")),Instant.now()).abs().compareTo(Duration.ofSeconds(20))>0)throw new LabSupport.Denied("FRESH_STOP_OBSERVATION_REQUIRED");
  byte[] context=Base64.getMimeDecoder().decode(LabSupport.text(info,"context_b64"));if(!LabSupport.hash(context).equals(LabSupport.text(info,"context_hash"))||!Set.of("PARTIAL","SUCCESS").contains(LabSupport.JSON.readTree(context).path("fixture").asText()))throw new LabSupport.Denied("FROZEN_CHECKPOINT_CONTEXT_REQUIRED");
  Path work=Path.of(identity.worker().toString().equals(LabSupport.config("worker.a"))?"/worker-a":"/worker-b").resolve("supervisor/attempts/"+identity.attempt());
  for(var file:List.of("stdout.bin","stderr.bin"))if(Files.size(work.resolve(file))>65536)throw new LabSupport.Denied("ARTIFACT_TOO_LARGE");
  byte[] out=Files.readAllBytes(work.resolve("stdout.bin")),err=Files.readAllBytes(work.resolve("stderr.bin"));var exited=new Properties();try(var in=Files.newInputStream(work.resolve("0003-EXITED.properties"))){exited.load(in);}
  if(!new String(out,java.nio.charset.StandardCharsets.UTF_8).strip().equals("{\"fixture\":\""+fixture+"\",\"candidate\":true}")||err.length!=0||!LabSupport.hash(out).equals(exited.getProperty("stdout_sha256"))||!LabSupport.hash(err).equals(exited.getProperty("stderr_sha256"))||!"false".equals(exited.getProperty("stdout_truncated"))||!"false".equals(exited.getProperty("stderr_truncated")))throw new LabSupport.Denied("INDEPENDENT_ARTIFACT_MISMATCH");
  var proof=new LinkedHashMap<String,Object>(LabSupport.identityMap(identity));proof.putAll(Map.of("schema","d4.checkpoint.proof.v1","context_hash",LabSupport.text(info,"context_hash"),"policy_hash",LabSupport.text(info,"policy_hash"),"manifest_hash",LabSupport.text(info,"manifest_hash"),"process_stopped",true,"artifact_valid",true,"host_observation_hash",LabSupport.hash(LabSupport.text(envelope,"facts").getBytes(java.nio.charset.StandardCharsets.UTF_8)),"stdout_hash",LabSupport.hash(out),"stderr_hash",LabSupport.hash(err)));return proof;
 }
 JsonNode seal(UUID delivery,UUID command,JsonNode info) throws Exception {
  var token=LabSupport.request(client,"POST","https://control-plane:8443/lab/close-token",Map.of("delivery_id",delivery.toString(),"command_id",command.toString()));
  var envelope=LabSupport.request(client,"POST","https://effect-receiver:8443/lab/seal",token);var facts=signed(envelope,"receiver");
  if(!LabSupport.identity(facts.path("identity")).equals(LabSupport.identity(info))||!LabSupport.text(facts,"command").equals(command.toString())||!LabSupport.text(facts,"receiverId").equals(Files.readString(Path.of("/public/receiver.id")).strip())||facts.path("sequence").asLong()<=0)throw new LabSupport.Denied("BOUND_RECEIVER_SEAL_REQUIRED");var preserved=(tools.jackson.databind.node.ObjectNode)facts.deepCopy();preserved.set("signed_envelope",envelope);return preserved;
 }
 private void applied(JsonNode receipt,JsonNode info,String step,long generation) throws Exception {
  var expected=LabSupport.hash(("synthetic-effect:"+LabSupport.text(info,"operation")+":"+step).getBytes(java.nio.charset.StandardCharsets.UTF_8));
  if(!receipt.path("status").asText().equals("APPLIED")||!expected.equals(receipt.path("payloadHash").asText())||receipt.path("generation").asLong()!=generation)throw new LabSupport.Denied("EXPECTED_APPLIED_STEP_REQUIRED");
 }
 @PostMapping("/lab/checkpoint/verify") Object checkpoint(HttpServletRequest r) throws Exception {
  LabSupport.require(r,"driver");var b=LabSupport.body(r);var request=LabSupport.uuid(b,"request_id");var proofId=LabSupport.uuid(b,"proof_id");var checkpoint=LabSupport.uuid(b,"commit_id");
  var requestInfo=LabSupport.sql("SELECT d4.checkpoint_inspect(?)::text",request);var delivery=LabSupport.uuid(requestInfo,"delivery_id");var info=LabSupport.sql("SELECT d4.i5_inspect(?)::text",delivery);
  var proof=stoppedArtifact(info,"PARTIAL");var sealed=seal(delivery,request,info);var receipts=sealed.path("steps");
  if(receipts.size()!=2||!receipts.has("step-1")||!receipts.has("step-2"))throw new LabSupport.Denied("COMPLETE_STEP_MANIFEST_REQUIRED");
  applied(receipts.path("step-1"),info,"step-1",info.path("generation").asLong());
  if(!receipts.path("step-2").path("status").asText().equals("ABSENT")||!receipts.path("step-2").path("closed").asBoolean())throw new LabSupport.Denied("SEALED_ABSENCE_REQUIRED");
  proof.putAll(Map.of("receiver_closed",true,"close_sequence",sealed.path("sequence").asLong(),"receiver_seal",sealed,"steps",Map.of("step-1","APPLIED","step-2","ABSENT"),"consumed_units",4));
  LabSupport.sql("SELECT d4.record_checkpoint_proof(?,?,?::jsonb)::text",proofId,request,LabSupport.JSON.writeValueAsString(proof));
  return LabSupport.request(client,"POST","https://control-plane:8443/lab/checkpoint/commit",Map.of("command_id",checkpoint.toString(),"request_id",request.toString(),"proof_id",proofId.toString(),"expected_version",requestInfo.path("expected_version").asLong()));
 }
 @PostMapping("/lab/checkpoint/finish") Object finish(HttpServletRequest r) throws Exception {
  LabSupport.require(r,"driver");var b=LabSupport.body(r);var delivery=LabSupport.uuid(b,"delivery_id");var proofId=LabSupport.uuid(b,"proof_id");var info=LabSupport.sql("SELECT d4.i5_inspect(?)::text",delivery);
  var proof=stoppedArtifact(info,"SUFFIX");var sealed=seal(delivery,proofId,info);if(sealed.path("steps").size()!=1||!sealed.path("steps").has("step-2"))throw new LabSupport.Denied("SUFFIX_ONLY_AUTHORITY_REQUIRED");
  applied(sealed.path("steps").path("step-2"),info,"step-2",info.path("generation").asLong());
  var old=LabSupport.request(client,"POST","https://effect-receiver:8443/lab/query",Map.of("operation",LabSupport.text(info,"operation"),"intent_hash",LabSupport.text(info,"context_hash"),"step","step-1","generation",info.path("generation").asLong()));applied(old,info,"step-1",info.path("generation").asLong()-1);
  proof.putAll(Map.of("receiver_closed",true,"close_sequence",sealed.path("sequence").asLong(),"receiver_seal",sealed,"previous_step",old,"steps",Map.of("step-1","APPLIED","step-2","APPLIED")));
  LabSupport.sql("SELECT d4.record_continuation_acceptance(?,?,?::jsonb)::text",proofId,delivery,LabSupport.JSON.writeValueAsString(proof));
  return LabSupport.request(client,"POST","https://control-plane:8443/lab/checkpoint/finalize",Map.of("command_id",LabSupport.uuid(b,"command_id").toString(),"delivery_id",delivery.toString()));
 }
}
