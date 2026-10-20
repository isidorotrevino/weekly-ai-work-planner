// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;

import io.github.isidorotrevino.planner.runtime.*;
import io.github.isidorotrevino.planner.runtime.AbsenceCheckpointAccounting.*;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;
import tools.jackson.databind.JsonNode;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;

/** Independent v2 ingress: actual sealed receiver + host stop + observed bytes.
 * SQL independently recomputes every account before committing any journal entry.
 */
@RestController @ConditionalOnProperty(name="lab.role",havingValue="verifier")
class MultiCheckpointVerifier {
 private final CheckpointVerifier artifacts;
 private final java.net.http.HttpClient client=LabSupport.client();
 MultiCheckpointVerifier(CheckpointVerifier artifacts) throws Exception {this.artifacts=artifacts;}
 static Map<UUID,BigDecimal> vector(JsonNode node){var out=new HashMap<UUID,BigDecimal>();for(var p:node.properties())out.put(UUID.fromString(p.getKey()),p.getValue().decimalValue());return out;}
 static Map<String,Applied> applied(JsonNode node){var out=new HashMap<String,Applied>();for(var p:node.properties()){var v=p.getValue();out.put(p.getKey(),new Applied(LabSupport.uuid(v,"attempt"),v.path("generation").asLong(),LabSupport.text(v,"payloadHash")));}return out;}
 static void fields(JsonNode b,String...names){if(b.size()!=names.length||Arrays.stream(names).anyMatch(n->!b.has(n)))throw new LabSupport.Denied("EXPLICIT_MULTI_FIELDS_REQUIRED");}
 static long version(JsonNode b){var v=b.path("expected_version");if(!v.isIntegralNumber()||!v.canConvertToLong()||v.asLong()<1)throw new LabSupport.Denied("EXACT_VERSION_REQUIRED");return v.asLong();}
 private Map<String,Object> proof(UUID delivery,UUID close,boolean terminal) throws Exception {
  var info=LabSupport.sql("SELECT d4.multi_inspect(?)::text",delivery);if(!info.path("multi_checkpoint").asBoolean())throw new LabSupport.Denied("V2_REQUIRED");
  var proof=artifacts.stoppedArtifact(info,terminal?"SUFFIX":"PARTIAL");var seal=artifacts.seal(delivery,close,info);var m=info.path("manifest");
  var accounts=new ArrayList<Account>();var original=new HashMap<UUID,BigDecimal>();
  for(var entry:m.path("accounts").properties()){var a=entry.getValue();var id=UUID.fromString(entry.getKey());accounts.add(new Account(id,LabSupport.text(a,"dimension"),Instant.parse(LabSupport.text(a,"start")),Instant.parse(LabSupport.text(a,"end")),a.path("original").decimalValue()));original.put(id,a.path("original").decimalValue());}
  var steps=new ArrayList<Step>();for(var s:m.path("steps"))steps.add(new Step(LabSupport.text(s,"id"),LabSupport.text(s,"effect_hash"),vector(s.path("cost"))));
  var manifest=new Manifest(LabSupport.uuid(info,"operation"),LabSupport.uuid(info,"resource"),LabSupport.text(m,"pool"),LabSupport.text(info,"context_hash"),LabSupport.text(info,"policy_hash"),accounts,steps,info.path("max_attempts").asInt());
  Settlement parent=null;
  for(var historical:info.path("history")){var e=historical.path("evaluation");parent=new Settlement(manifest.digest(),parent==null?null:parent.digest(),LabSupport.identity(e.path("identity")),e.path("attempt_count").asInt(),applied(e.path("applied")),vector(e.path("cumulative")),vector(e.path("consume")),vector(e.path("release")),false);}
  var receipts=new LinkedHashMap<String,Receipt>();
  for(var entry:seal.path("steps").properties()){
   var r=entry.getValue();if(r.path("generation").asLong()!=info.path("generation").asLong()||("ABSENT".equals(r.path("status").asText())&&!r.path("closed").asBoolean()))throw new LabSupport.Denied("BOUND_RECEIPTS_REQUIRED");
   var status=Status.valueOf(LabSupport.text(r,"status"));receipts.put(entry.getKey(),new Receipt(status,status==Status.APPLIED?LabSupport.text(r,"payloadHash"):null));
  }
  // Every inherited logical result is queried again independently. A historical
  // ABSENT cannot hide an APPLIED in a later authorized generation.
  if(parent!=null)for(var e:parent.applied().entrySet()){
   var receipt=LabSupport.request(client,"POST","https://effect-receiver:8443/lab/query",Map.of("operation",LabSupport.text(info,"operation"),"intent_hash",LabSupport.text(info,"context_hash"),"step",e.getKey(),"generation",info.path("generation").asLong()));
   if(!"APPLIED".equals(receipt.path("status").asText())||receipt.path("generation").asLong()!=e.getValue().generation()||!e.getValue().payloadHash().equals(receipt.path("payloadHash").asText()))throw new LabSupport.Denied("INHERITED_FACT_MISMATCH");
  }
  var journal=new HashMap<UUID,BigDecimal>();var pending=new HashMap<UUID,BigDecimal>();
  for(var a:info.path("accounts")){var id=LabSupport.uuid(a,"account_id");journal.put(id,a.path("consumed").decimalValue());pending.put(id,a.path("outstanding").decimalValue());}
  // CALLBACK has already settled the final attempt. Compute its expected vector
  // from the immutable parent and original TOP_UP, then compare the actual journal.
  var prior=new HashMap<UUID,BigDecimal>();for(var id:original.keySet())prior.put(id,parent==null?BigDecimal.ZERO:parent.cumulative().get(id));
  var lineage=new ArrayList<AbsenceLink>();for(var link:LabSupport.sql("SELECT d4.absence_lineage(?)::text",delivery)){if(!link.path("current").asBoolean())throw new LabSupport.Denied("CURRENT_ABSENCE_LINEAGE_REQUIRED");lineage.add(new AbsenceLink(LabSupport.identity(link.path("source")),LabSupport.identity(link.path("target")),link.path("source_count").asInt(),link.path("target_count").asInt(),LabSupport.text(link,"seal_hash")));}
  var expected=AbsenceCheckpointAccounting.prepare(manifest,parent,parent==null?null:parent.digest(),new ClosedAttempt(LabSupport.identity(info),seal.path("sequence").asLong(),receipts),info.path("attempt_count").asInt(),terminal?prior:journal,terminal?original:pending,Instant.parse(LabSupport.text(info,"database_now")),terminal,lineage);
  if(terminal)for(var id:original.keySet())if(journal.get(id).compareTo(expected.cumulative().get(id))!=0||pending.get(id).signum()!=0)throw new LabSupport.Denied("FINAL_JOURNAL_MISMATCH");
  proof.putAll(Map.of("schema","d4.checkpoint.proof.v2","parent_checkpoint",info.path("parent_checkpoint"),"receiver_closed",true,"close_sequence",seal.path("sequence").asLong(),"receiver_seal",seal,"receipts",seal.path("steps"),"calculator_hash",expected.digest()));
  return proof;
 }
 @PostMapping("/lab/multi/verify") Object checkpoint(HttpServletRequest r) throws Exception {
  LabSupport.require(r,"driver");var b=LabSupport.body(r);fields(b,"delivery_id","request_id","proof_id","commit_id");var delivery=LabSupport.uuid(b,"delivery_id");var request=LabSupport.uuid(b,"request_id");var proofId=LabSupport.uuid(b,"proof_id");var info=LabSupport.sql("SELECT d4.multi_inspect(?)::text",delivery);
  var previous=LabSupport.sql("SELECT d4.multi_proof_status(?,?,?)::text",proofId,delivery,request);
  if(previous.isNull()){var proof=proof(delivery,request,false);LabSupport.sql("SELECT d4.multi_record_proof(?,?,?,?::jsonb)::text",proofId,delivery,request,LabSupport.JSON.writeValueAsString(proof));}
  return LabSupport.request(client,"POST","https://control-plane:8443/lab/multi/commit",Map.of("command_id",LabSupport.text(b,"commit_id"),"request_id",request.toString(),"proof_id",proofId.toString(),"expected_version",previous.isNull()?info.path("row_version").asLong():previous.path("expected_version").asLong()));
 }
 @PostMapping("/lab/multi/finish") Object finish(HttpServletRequest r) throws Exception {
  LabSupport.require(r,"driver");var b=LabSupport.body(r);fields(b,"delivery_id","proof_id","command_id");var delivery=LabSupport.uuid(b,"delivery_id");var pid=LabSupport.uuid(b,"proof_id");var previous=LabSupport.sql("SELECT d4.multi_accept_status(?,?)::text",pid,delivery);
  if(previous.isNull()){var proof=proof(delivery,pid,true);LabSupport.sql("SELECT d4.multi_accept(?,?,?::jsonb)::text",pid,delivery,LabSupport.JSON.writeValueAsString(proof));}
  return LabSupport.request(client,"POST","https://control-plane:8443/lab/multi/finalize",Map.of("command_id",LabSupport.text(b,"command_id"),"delivery_id",delivery.toString()));
 }
}
@RestController @ConditionalOnProperty(name="lab.role",havingValue="control")
class MultiCheckpointControl {
 @PostMapping("/lab/multi/request") Object request(HttpServletRequest r) throws Exception {LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","delivery_id","expected_version");return LabSupport.sql("SELECT d4.multi_request(?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"delivery_id"),MultiCheckpointVerifier.version(b));}
 @PostMapping("/lab/multi/commit") Object commit(HttpServletRequest r) throws Exception {LabSupport.require(r,"verifier");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","request_id","proof_id","expected_version");return LabSupport.sql("SELECT d4.multi_commit(?,?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"request_id"),LabSupport.uuid(b,"proof_id"),MultiCheckpointVerifier.version(b));}
 @PostMapping("/lab/multi/authorize") Object authorize(HttpServletRequest r) throws Exception {LabSupport.require(r,"driver");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","checkpoint_id","expected_version","reason");return LabSupport.sql("SELECT d4.multi_authorize(?,?,?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"checkpoint_id"),MultiCheckpointVerifier.version(b),LabSupport.text(b,"reason"));}
 @PostMapping("/lab/multi/finalize") Object finish(HttpServletRequest r) throws Exception {LabSupport.require(r,"verifier");var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","delivery_id");return LabSupport.sql("SELECT d4.multi_finalize(?,?)::text",LabSupport.uuid(b,"command_id"),LabSupport.uuid(b,"delivery_id"));}
}
