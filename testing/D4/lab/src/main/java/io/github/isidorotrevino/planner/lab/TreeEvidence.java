// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;
import tools.jackson.databind.JsonNode;
import java.nio.file.*;
import java.util.*;

/** Java port ingress; trusted SQL requirements, independently stopped writer, no candidate expectations. */
final class TreeEvidence {
 static Map<String,TreeVerifier.Artifact> manifest(JsonNode node){
  if(!node.isObject()||node.size()>64)throw new LabSupport.Denied("BOUNDED_MANIFEST_REQUIRED");var m=new TreeMap<String,TreeVerifier.Artifact>();for(var e:node.properties()){var a=e.getValue();if(a.size()!=3||!a.path("size").isIntegralNumber()||!a.path("size").canConvertToInt()||!a.path("sha256").isString()||!a.path("executable").isBoolean())throw new LabSupport.Denied("CLOSED_ARTIFACT_SCHEMA");m.put(e.getKey(),new TreeVerifier.Artifact(a.path("size").asInt(),a.path("sha256").asText(),a.path("executable").asBoolean()));}TreeVerifier.manifest(m);return m;
 }
 static void verify(JsonNode info,CheckpointVerifier stop)throws Exception{
  var delivery=LabSupport.uuid(info,"delivery_id");var trusted=LabSupport.sql("SELECT d4.tree_info(?)::text",delivery);var requirement=trusted.path("tree_requirement");if(requirement.isNull())return;
  var proof=stop.stoppedObservation(trusted);var identity=LabSupport.identity(trusted);var expected=manifest(requirement.path("manifest"));if(!TreeVerifier.manifest(expected).equals(LabSupport.text(requirement,"manifest_hash")))throw new LabSupport.Denied("FROZEN_TREE_HASH");
  var baseManifest=manifest(requirement.path("base_manifest"));var context=LabSupport.JSON.readTree(Base64.getMimeDecoder().decode(LabSupport.text(trusted,"context_b64")));var base=new TreeMap<String,byte[]>();for(var e:context.path("tree_fixture").path("base_files").properties())base.put(e.getKey(),Base64.getDecoder().decode(e.getValue().asText()));
  var root=Path.of(identity.worker().toString().equals(LabSupport.config("worker.a"))?"/worker-a":"/worker-b").resolve("trees/"+identity.attempt());TreeVerifier.files(root,expected,requirement.path("restoration").asBoolean());var actual=new TreeMap<String,byte[]>();for(var e:expected.entrySet()){try(var in=Files.newInputStream(root.resolve(e.getKey()),LinkOption.NOFOLLOW_LINKS)){var bytes=in.readNBytes(e.getValue().size()+1);if(!TreeVerifier.Artifact.of(bytes,e.getValue().executable()).equals(e.getValue()))throw new LabSupport.Denied("TREE_CHANGED");actual.put(e.getKey(),bytes);}}
  try(var store=new TreeVerifier.GitStore(Path.of("/tmp"))){var baseOid=store.commit(base,baseManifest,null);var commit=store.commit(actual,expected,baseOid);store.verify(commit,baseOid,expected);TreeVerifier.files(root,expected,requirement.path("restoration").asBoolean());var after=stop.stoppedObservation(trusted);if(!Objects.equals(proof.get("host_observation_hash"),after.get("host_observation_hash")))throw new LabSupport.Denied("STOP_OBSERVATION_CHANGED");proof.putAll(Map.of("schema","d4.tree.proof.v1","manifest_hash",TreeVerifier.manifest(expected),"files_verified",true,"git_verified",true,"restoration",requirement.path("restoration").asBoolean(),"base_oid",baseOid,"commit_oid",commit));LabSupport.sql("SELECT d4.tree_record(?,?,?::jsonb)::text",UUID.randomUUID(),delivery,LabSupport.JSON.writeValueAsString(proof));}
 }
}
