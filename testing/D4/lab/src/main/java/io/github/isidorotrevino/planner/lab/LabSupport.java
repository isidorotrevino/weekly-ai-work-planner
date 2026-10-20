// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;

import io.github.isidorotrevino.planner.runtime.*;
import io.github.isidorotrevino.planner.worker.WorkerIdentityFilter;
import jakarta.servlet.http.HttpServletRequest;
import tools.jackson.core.*;
import tools.jackson.core.json.JsonFactory;
import tools.jackson.databind.*;
import tools.jackson.databind.json.JsonMapper;
import javax.net.ssl.*;
import java.io.*;
import java.net.*;
import java.net.http.*;
import java.nio.file.*;
import java.security.*;
import java.security.spec.*;
import java.sql.*;
import java.time.*;
import java.util.*;

final class LabSupport {
  static final JsonMapper JSON=JsonMapper.builder(JsonFactory.builder().enable(StreamReadFeature.STRICT_DUPLICATE_DETECTION).streamReadConstraints(StreamReadConstraints.builder().maxNestingDepth(32).maxStringLength(65536).build()).build()).build();
  static final Path CONFIG=Path.of(System.getenv().getOrDefault("LAB_CONFIG","/config/service"));
  static final Properties P=new Properties();
  static void load() throws Exception {try(var in=Files.newInputStream(CONFIG.resolve("service.properties"))){P.load(in);}}
  static String config(String key){return Objects.requireNonNull(P.getProperty(key),"Required laboratory setting: "+key);}
  static void require(HttpServletRequest r,String...kinds){if(!Set.of(kinds).contains(r.getAttribute(WorkerIdentityFilter.KIND)))throw new Denied("ROLE_REJECTED");}
  static UUID worker(HttpServletRequest r){require(r,"worker");return (UUID)r.getAttribute(WorkerIdentityFilter.PRINCIPAL);}
  static JsonNode body(HttpServletRequest r) throws Exception {var b=r.getInputStream().readNBytes(65537);if(b.length>65536)throw new Denied("BODY_TOO_LARGE");var node=JSON.readTree(b);if(node==null||!node.isObject())throw new Denied("OBJECT_REQUIRED");return node;}
  static String text(JsonNode n,String key){var v=n.path(key);if(!v.isTextual()||v.asText().isBlank())throw new Denied("FIELD_REQUIRED");return v.asText();}
  static UUID uuid(JsonNode n,String key){return UUID.fromString(text(n,key));}
  static String hash(byte[] b) throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));}
  static ExecutionIdentity identity(JsonNode n){return new ExecutionIdentity(uuid(n,"operation"),uuid(n,"attempt"),uuid(n,"worker"),uuid(n,"resource"),n.path("generation").asLong());}
  static Map<String,Object> identityMap(ExecutionIdentity i){return Map.of("operation",i.operation().toString(),"attempt",i.attempt().toString(),"worker",i.worker().toString(),"resource",i.resource().toString(),"generation",i.generation());}
  static Map<String,Object> grantMap(EffectJournal.SignedGrant s){var g=s.grant();var map=new LinkedHashMap<String,Object>(identityMap(g.identity()));map.putAll(Map.of("receiver_id",g.receiverId().toString(),"intent_hash",g.intentHash(),"context_hash",g.contextHash(),"policy_hash",g.policyHash(),"steps",g.steps(),"issued_at",g.issuedAt().toString(),"expires_at",g.expiresAt().toString(),"lease_expires_at",g.leaseExpiresAt().toString()));return Map.of("grant",map,"signature",s.signature());}
  static EffectJournal.SignedGrant grant(JsonNode n){var g=n.path("grant");var steps=new HashSet<String>();g.path("steps").forEach(v->steps.add(v.asText()));return new EffectJournal.SignedGrant(new EffectJournal.Grant(uuid(g,"receiver_id"),identity(g),text(g,"intent_hash"),text(g,"context_hash"),text(g,"policy_hash"),steps,Instant.parse(text(g,"issued_at")),Instant.parse(text(g,"expires_at")),Instant.parse(text(g,"lease_expires_at"))),text(n,"signature"));}
  static Map<String,Object> closeMap(EffectJournal.SignedClose s){var map=new LinkedHashMap<String,Object>(identityMap(s.identity()));map.putAll(Map.of("receiver_id",s.receiverId().toString(),"command",s.command().toString(),"signature",s.signature()));return map;}
  static EffectJournal.SignedClose close(JsonNode n){return new EffectJournal.SignedClose(uuid(n,"receiver_id"),identity(n),uuid(n,"command"),text(n,"signature"));}
  static PublicKey publicKey(String name) throws Exception{return KeyFactory.getInstance("Ed25519").generatePublic(new X509EncodedKeySpec(Files.readAllBytes(Path.of("/public/"+name+".pub.der"))));}
  static PrivateKey privateKey(String name) throws Exception{return KeyFactory.getInstance("Ed25519").generatePrivate(new PKCS8EncodedKeySpec(Files.readAllBytes(CONFIG.resolve(name+".der"))));}
  static Connection connection() throws Exception {var opts=new Properties();opts.setProperty("user",config("jdbc.user"));opts.setProperty("password",config("jdbc.password"));opts.setProperty("connectTimeout","4");opts.setProperty("socketTimeout","12");var c=DriverManager.getConnection(config("jdbc.url"),opts);c.setAutoCommit(true);c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);try(var s=c.createStatement()){s.execute("SET statement_timeout=10000;SET lock_timeout=5000");}return c;}
  static JsonNode sql(String query,Object...args) throws Exception {try(var c=connection();var p=c.prepareStatement(query)){for(int i=0;i<args.length;i++)p.setObject(i+1,args[i]);try(var rs=p.executeQuery()){rs.next();return JSON.readTree(rs.getString(1));}}}
  static HttpClient client() throws Exception {
    var keys=KeyStore.getInstance("PKCS12");try(var in=Files.newInputStream(CONFIG.resolve("identity.p12"))){keys.load(in,config("tls.password").toCharArray());}
    var km=KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());km.init(keys,config("tls.password").toCharArray());
    var trust=KeyStore.getInstance("PKCS12");try(var in=Files.newInputStream(Path.of("/public/trust.p12"))){trust.load(in,"synthetic-trust-only".toCharArray());}
    var tm=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());tm.init(trust);var ctx=SSLContext.getInstance("TLS");ctx.init(km.getKeyManagers(),tm.getTrustManagers(),new SecureRandom());
    return HttpClient.newBuilder().sslContext(ctx).version(HttpClient.Version.HTTP_1_1).connectTimeout(Duration.ofSeconds(3)).build();
  }
  static JsonNode request(HttpClient client,String method,String url,Object body) throws Exception {
    var b=HttpRequest.newBuilder(URI.create(url)).timeout(Duration.ofSeconds(8)).header("Content-Type","application/json");
    b.method(method,body==null?HttpRequest.BodyPublishers.noBody():HttpRequest.BodyPublishers.ofString(JSON.writeValueAsString(body)));
    var response=client.send(b.build(),HttpResponse.BodyHandlers.ofString());if(response.statusCode()/100!=2)throw new Rejected(response.statusCode());return JSON.readTree(response.body());
  }
  static void atomic(Path path,Object value) throws Exception {var next=path.resolveSibling(path.getFileName()+".next");Files.writeString(next,JSON.writeValueAsString(value));try(var c=java.nio.channels.FileChannel.open(next,StandardOpenOption.WRITE)){c.force(true);}Files.move(next,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
  static final class Denied extends RuntimeException {Denied(String code){super(code);}}
  static final class Rejected extends IOException {final int status;Rejected(int status){super("LAB_HTTP_"+status);this.status=status;}}
}
