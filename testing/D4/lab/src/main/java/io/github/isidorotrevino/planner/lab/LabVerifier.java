// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;
import tools.jackson.databind.JsonNode;
import java.net.http.*;
import java.nio.file.*;
import java.security.*;
import java.time.*;
import java.util.*;

@RestController @ConditionalOnProperty(name="lab.role",havingValue="verifier")
class LabVerifier {
 private final HttpClient client=LabSupport.client();
 private final CheckpointVerifier independent;
 LabVerifier(CheckpointVerifier independent) throws Exception {this.independent=independent;}
 private JsonNode admin(UUID delivery,String action,UUID proof) throws Exception {
  var body=new HashMap<String,Object>(Map.of("command_id",UUID.randomUUID().toString(),"delivery_id",delivery.toString(),"action",action));if(proof!=null)body.put("proof_id",proof.toString());return LabSupport.request(client,"POST","https://control-plane:8443/lab/admin",body);
 }
 @PostMapping("/lab/verify") Object verify(HttpServletRequest r) throws Exception {
  LabSupport.require(r,"driver");var request=LabSupport.body(r);var delivery=LabSupport.uuid(request,"delivery_id");var proofId=LabSupport.uuid(request,"proof_id");
  var info=LabSupport.sql("SELECT d4.lab_inspect(?)::text",delivery);TreeEvidence.verify(info,independent);var identity=LabSupport.identity(info);
  var observed=LabSupport.JSON.readTree(Files.readString(Path.of("/observations/"+identity.attempt()+".json")));
  var factsText=LabSupport.text(observed,"facts");var signature=Signature.getInstance("Ed25519");signature.initVerify(LabSupport.publicKey("observer"));signature.update(factsText.getBytes(java.nio.charset.StandardCharsets.UTF_8));if(!signature.verify(Base64.getDecoder().decode(LabSupport.text(observed,"signature"))))throw new LabSupport.Denied("HOST_PROOF_SIGNATURE_INVALID");
  var facts=LabSupport.JSON.readTree(factsText);if(!LabSupport.identity(facts).equals(identity)||!LabSupport.text(facts,"campaign").equals(LabSupport.config("campaign"))||Duration.between(Instant.parse(LabSupport.text(facts,"observed_at")),Instant.now()).abs().compareTo(Duration.ofSeconds(20))>0)throw new LabSupport.Denied("HOST_PROOF_STALE_OR_MISMATCH");
  boolean stopped=facts.path("process_stopped").asBoolean();
  byte[] context=Base64.getMimeDecoder().decode(LabSupport.text(info,"context_b64"));boolean contextValid=LabSupport.hash(context).equals(LabSupport.text(info,"context_hash"));
  var query=Map.of("operation",identity.operation().toString(),"intent_hash",LabSupport.text(info,"context_hash"),"step","step-1","generation",identity.generation());
  var receipt=LabSupport.request(client,"POST","https://effect-receiver:8443/lab/query",query);var receiverStatus=LabSupport.text(receipt,"status");
  var expectedEffect=LabSupport.hash(("synthetic-effect:"+identity.operation()).getBytes(java.nio.charset.StandardCharsets.UTF_8));
  if(receiverStatus.equals("APPLIED")&&!expectedEffect.equals(LabSupport.text(receipt,"payloadHash")))throw new LabSupport.Denied("EFFECT_PAYLOAD_MISMATCH");
  var work=Path.of(identity.worker().toString().equals(LabSupport.config("worker.a"))?"/worker-a":"/worker-b").resolve("supervisor/attempts").resolve(identity.attempt().toString());
  boolean fixtureValid=contextValid&&LabSupport.JSON.readTree(context).path("fixture").asText().equals("SUCCESS");
  boolean artifact=false;String stdoutHash="unavailable",stderrHash="unavailable";
  if(stopped && Files.isRegularFile(work.resolve("stdout.bin")) && Files.size(work.resolve("stdout.bin"))<=65536 && Files.size(work.resolve("stderr.bin"))<=65536){
   byte[] stdout=Files.readAllBytes(work.resolve("stdout.bin")),stderr=Files.readAllBytes(work.resolve("stderr.bin"));stdoutHash=LabSupport.hash(stdout);stderrHash=LabSupport.hash(stderr);
   var exited=new Properties();try(var in=Files.newInputStream(work.resolve("0003-EXITED.properties"))){exited.load(in);}
   artifact=fixtureValid && stdoutHash.equals(exited.getProperty("stdout_sha256")) && stderrHash.equals(exited.getProperty("stderr_sha256")) &&
     new String(stdout,java.nio.charset.StandardCharsets.UTF_8).strip().equals("{\"fixture\":\"SUCCESS\",\"candidate\":true}") && stderr.length==0 && !Boolean.parseBoolean(exited.getProperty("stdout_truncated","true")) && !Boolean.parseBoolean(exited.getProperty("stderr_truncated","true"));
  }
  boolean accounting=true;if(LabSupport.text(info,"state").equals("VERIFYING"))for(var a:info.path("accounts"))accounting &= a.path("outstanding").decimalValue().signum()==0 && a.path("consumed").decimalValue().compareTo(info.path("consumed_units").decimalValue())==0;
  boolean accepted=stopped&&artifact&&accounting&&!info.path("unresolved_evidence").asBoolean()&&receiverStatus.equals("APPLIED");
  long closeSequence=0;
  if(stopped){var token=LabSupport.request(client,"POST","https://control-plane:8443/lab/close-token",Map.of("command_id",proofId.toString(),"delivery_id",delivery.toString()));closeSequence=LabSupport.request(client,"POST","https://effect-receiver:8443/lab/close",token).path("sequence").asLong();}
  // No ABSENT ingestion or override of prior UNKNOWN/contradictory evidence.
  String status=receiverStatus.equals("APPLIED")&&!info.path("unresolved_evidence").asBoolean()?"APPLIED":"UNKNOWN";
  var proof=new LinkedHashMap<String,Object>();proof.putAll(Map.of("context_hash",LabSupport.text(info,"context_hash"),"process_stopped",stopped,"artifact_valid",artifact,"receiver_status",receiverStatus,"host_observation_hash",LabSupport.hash(factsText.getBytes(java.nio.charset.StandardCharsets.UTF_8)),"stdout_hash",stdoutHash,"stderr_hash",stderrHash,"receipt",receipt));
  proof.put("receiver_closed",closeSequence>0);proof.put("close_sequence",closeSequence);
  if(info.path("lease_expired").asBoolean()&&Set.of("LEASED","RUNNING","VERIFYING").contains(LabSupport.text(info,"state")))admin(delivery,"EXPIRE",null);
  LabSupport.sql("SELECT d4.lab_record_evidence(?,?,?,?,?::jsonb)::text",proofId,delivery,status,accepted,LabSupport.JSON.writeValueAsString(proof));
  info=LabSupport.sql("SELECT d4.lab_inspect(?)::text",delivery);boolean recovering=LabSupport.text(info,"state").equals("RECONCILING");
  if(recovering)admin(delivery,"RECONCILE",proofId);
  if(accepted)admin(delivery,recovering?"RECOVERY_VERIFY":"VERIFY",proofId);
  return Map.of("accepted",accepted,"status",status,"stopped",stopped,"state",LabSupport.sql("SELECT d4.lab_inspect(?)::text",delivery));
 }
}
