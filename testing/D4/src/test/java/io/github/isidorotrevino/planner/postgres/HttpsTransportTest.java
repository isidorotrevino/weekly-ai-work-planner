// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import io.github.isidorotrevino.planner.worker.WorkerControlPlane;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.boot.SpringApplication;
import org.springframework.context.ConfigurableApplicationContext;
import tools.jackson.databind.json.JsonMapper;
import java.io.*;
import java.net.*;
import java.net.http.*;
import java.nio.file.*;
import java.sql.*;
import java.time.Duration;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;

/** Real TLS/Tomcat/Spring and restricted JDBC; no worker subprocess/effect engine. */
class HttpsTransportTest {
  @TempDir Path temporary;
  static final String TEMPLATE="d4_http_template",LOGIN="d4_http_test";
  static final String RUNTIME_PASSWORD=UUID.randomUUID().toString();
  static final JsonMapper JSON=JsonMapper.builder().build();
  DeliveryStoreTest fixture;
  TlsFixture tls;Path workerKey,otherKey,registry;
  ConfigurableApplicationContext app;
  HttpClient client;String base;
  final Properties identities=new Properties();
  @BeforeAll static void initialize() throws Exception {
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+TEMPLATE);}
    var fw=migrations(TEMPLATE,"17");assertEquals(17,fw.migrate().migrationsExecuted);fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
    try(var c=connect(TEMPLATE)){
      sql(c,"CREATE ROLE "+LOGIN+" LOGIN PASSWORD '"+RUNTIME_PASSWORD+"';GRANT USAGE ON SCHEMA d4 TO "+LOGIN+";GRANT EXECUTE ON FUNCTION d4.transport(uuid,uuid,jsonb),d4.read_transport_command(uuid,uuid),d4.current_assignment(uuid) TO "+LOGIN);
    }
  }
  @BeforeEach void setup() throws Exception {
    fixture=new DeliveryStoreTest();fixture.db="d4_http_case_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+fixture.db+" TEMPLATE "+TEMPLATE);}
    try(var c=fixture.owner()){fixture.fixture(c,true);}
    tls=new TlsFixture(temporary.resolve("pki"));
    workerKey=tls.worker("worker-a",fixture.worker,false);otherKey=tls.worker("worker-b",fixture.other,false);
    registry=temporary.resolve("identities.properties");
    identities.setProperty(tls.fingerprint(workerKey),fixture.worker.toString());identities.setProperty(tls.fingerprint(otherKey),fixture.other.toString());saveRegistry();
    start();client=client(workerKey);
  }
  void saveRegistry() throws IOException {
    var next=registry.resolveSibling("identities.next");try(var out=Files.newOutputStream(next)){identities.store(out,"Synthetic bindings only");}
    Files.move(next,registry,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
  }
  void start(){
    var application=new SpringApplication(WorkerControlPlane.class);
    application.setDefaultProperties(Map.ofEntries(Map.entry("D4_SERVER_KEYSTORE",tls.server.toString()),Map.entry("D4_TRUSTSTORE",tls.trust.toString()),
      Map.entry("D4_KEYSTORE_PASSWORD",tls.password),Map.entry("D4_JDBC_URL",URL+fixture.db),Map.entry("D4_JDBC_USER",LOGIN),Map.entry("D4_JDBC_PASSWORD",RUNTIME_PASSWORD),Map.entry("D4_IDENTITIES",registry.toString())));
    app=application.run("--server.port=0","--logging.level.root=ERROR");base="https://localhost:"+app.getEnvironment().getRequiredProperty("local.server.port")+"/d4/v1";
  }
  HttpClient client(Path key) throws Exception {return HttpClient.newBuilder().sslContext(tls.context(key)).connectTimeout(Duration.ofSeconds(5)).version(HttpClient.Version.HTTP_1_1).build();}
  @AfterEach void cleanup() throws Exception {
    if(client!=null)client.close();if(app!=null)app.close();if(fixture!=null)fixture.cleanup();
  }
  String envelope(UUID cid,UUID correlation,Map<String,?> request){return JSON.writeValueAsString(Map.of("schema_version","d4.worker.v1","command_id",cid.toString(),"correlation_id",correlation.toString(),"request",request));}
  HttpResponse<String> post(HttpClient connection,String body,String contentType) throws Exception {
    return connection.send(HttpRequest.newBuilder(URI.create(base+"/commands")).timeout(Duration.ofSeconds(8)).header("Content-Type",contentType).POST(HttpRequest.BodyPublishers.ofString(body)).build(),HttpResponse.BodyHandlers.ofString());
  }
  HttpResponse<String> post(Map<String,?> request) throws Exception{return post(client,envelope(id(),id(),request),"application/json");}
  HttpResponse<String> get(HttpClient connection,String path) throws Exception{return connection.send(HttpRequest.newBuilder(URI.create(base+path)).timeout(Duration.ofSeconds(8)).GET().build(),HttpResponse.BodyHandlers.ofString());}
  UUID poll() throws Exception {
    var response=post(Map.of("action","POLL"));assertEquals(200,response.statusCode(),response.body());
    return UUID.fromString(JSON.readTree(response.body()).path("result").path("assignment").path("delivery_id").asText());
  }
  @Test void httpsPollAckStartCallbackAndRestrictedCommandRead() throws Exception {
    var delivery=poll();
    assertEquals(200,post(Map.of("action","ACK","delivery_id",delivery)).statusCode());
    try(var c=fixture.owner()){assertEquals("LEASED",value(c,"SELECT state FROM operations"));}
    assertEquals(200,post(Map.of("action","START","delivery_id",delivery)).statusCode());
    var cid=id();var body=envelope(cid,id(),Map.of("action","CALLBACK","delivery_id",delivery,"payload",Map.of("entries",List.of(Map.of("account_id",fixture.account,"settled",10,"consumed",8)))));
    var response=post(client,body,"application/json");assertEquals(200,response.statusCode(),response.body());
    assertEquals(response.body(),post(client,body,"application/json").body());
    assertEquals(response.body(),get(client,"/commands/"+cid).body());
    assertEquals(409,post(Map.of("action","VERIFY","delivery_id",delivery)).statusCode());
    try(var c=fixture.owner()){
      assertEquals("VERIFYING",value(c,"SELECT state FROM operations"));assertEquals("0",value(c,"SELECT count(*) FROM execution_evidence"));
      assertEquals("62.0000",value(c,"SELECT available::numeric(18,4)::text FROM d2.balances WHERE account_id=? AND pool='PLANNED'",fixture.account));
    }
  }
  @Test void fullEnvelopeReplayConflictsAndRestartRecoversAssignment() throws Exception {
    var cid=id();var correlation=id();var body=envelope(cid,correlation,Map.of("action","POLL"));
    var response=post(client,body,"application/json");assertEquals(200,response.statusCode(),response.body());
    assertEquals(409,post(client,envelope(cid,id(),Map.of("action","POLL")),"application/json").statusCode());
    client.close();app.close();start();client=client(workerKey);
    assertEquals(response.body(),post(client,body,"application/json").body());
    var newPoll=post(Map.of("action","POLL"));assertEquals(200,newPoll.statusCode());
    assertEquals(JSON.readTree(response.body()).at("/result/assignment/delivery_id"),JSON.readTree(newPoll.body()).at("/result/assignment/delivery_id"));
    try(var c=fixture.owner()){
      assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));
    }
  }
  @Test void missingAndUntrustedCertificatesCannotReachHttp() throws Exception {
    try(var noCert=client(null);var rogue=client(tls.untrusted())){
      assertThrows(IOException.class,()->get(noCert,"/assignments/current"));
      assertThrows(IOException.class,()->get(rogue,"/assignments/current"));
    }
    try(var c=fixture.owner()){assertEquals("0",value(c,"SELECT count(*) FROM d4.transport_commands"));}
  }
  @Test void registeredForeignWorkerCannotActOnOrReadAnotherAssignment() throws Exception {
    var cid=id();var response=post(client,envelope(cid,id(),Map.of("action","POLL")),"application/json");assertEquals(200,response.statusCode());
    var delivery=UUID.fromString(JSON.readTree(response.body()).at("/result/assignment/delivery_id").asText());
    try(var foreign=client(otherKey)){
      assertEquals(403,get(foreign,"/commands/"+cid).statusCode());
      assertEquals(403,post(foreign,envelope(id(),id(),Map.of("action","ACK","delivery_id",delivery)),"application/json").statusCode());
      var req=HttpRequest.newBuilder(URI.create(base+"/commands")).timeout(Duration.ofSeconds(8))
        .header("Content-Type","application/json").header("X-Worker-Id",fixture.worker.toString()).header("X-Forwarded-Client-Cert","synthetic-spoof")
        .POST(HttpRequest.BodyPublishers.ofString(envelope(id(),id(),Map.of("action","START","delivery_id",delivery)))).build();
      assertEquals(403,foreign.send(req,HttpResponse.BodyHandlers.ofString()).statusCode());
      assertEquals("null",get(foreign,"/assignments/current").body());
    }
    try(var c=fixture.owner()){assertEquals("LEASED",value(c,"SELECT state FROM operations"));}
  }
  @Test void revocationAndSanBindingAreCheckedOnReusedTlsClient() throws Exception {
    assertEquals(200,get(client,"/assignments/current").statusCode());
    identities.remove(tls.fingerprint(workerKey));saveRegistry();
    assertEquals(403,get(client,"/assignments/current").statusCode());
    identities.setProperty(tls.fingerprint(workerKey),fixture.other.toString());saveRegistry();
    assertEquals(403,get(client,"/assignments/current").statusCode());
    identities.setProperty(tls.fingerprint(workerKey),fixture.worker.toString());saveRegistry();
    assertEquals(200,get(client,"/assignments/current").statusCode());
  }
  @Test void unknownAndExpiredCertificatesAreRejected() throws Exception {
    var unknown=tls.worker("unknown",id(),false);try(var unknownClient=client(unknown)){assertEquals(403,get(unknownClient,"/assignments/current").statusCode());}
    var expired=tls.worker("expired",fixture.worker,true);identities.setProperty(tls.fingerprint(expired),fixture.worker.toString());saveRegistry();
    try(var expiredClient=client(expired)){
      try{assertEquals(403,get(expiredClient,"/assignments/current").statusCode());}catch(IOException expected){/* TLS validity rejection before HTTP is also required. */}
    }
  }
  @Test void malformedDuplicateOversizedAndUntrustedFieldsDoNotMutateDomain() throws Exception {
    assertEquals(400,post(client,"{}","application/json").statusCode());
    var body=envelope(id(),id(),Map.of("action","POLL"));
    assertEquals(400,post(client,body.replace("{\"", "{\"schema_version\":\"d4.worker.v1\",\""),"application/json").statusCode());
    assertEquals(400,post(client,body.replace("d4.worker.v1","unknown"),"application/json").statusCode());
    assertEquals(413,post(client," ".repeat(65537),"application/json").statusCode());
    assertEquals(415,post(client,body,"text/plain").statusCode());
    assertEquals(409,post(Map.of("action","POLL","worker_id",fixture.other)).statusCode());
    try(var c=fixture.owner()){assertEquals("0",value(c,"SELECT count(*) FROM d4.transport_commands"));assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations"));}
  }
  @Test void oldStartReceiptIsNotNewAuthority() throws Exception {
    var delivery=poll();var cid=id();var body=envelope(cid,id(),Map.of("action","START","delivery_id",delivery));
    var response=post(client,body,"application/json");assertEquals(200,response.statusCode(),response.body());
    // SQL-only time fixture; real process expiry belongs to later D4-S04.
    try(var c=fixture.owner()){sql(c,"UPDATE operation_leases SET expires_at=clock_timestamp()-interval '1 second'");}
    assertEquals(response.body(),post(client,body,"application/json").body());
    assertEquals(409,post(Map.of("action","START","delivery_id",delivery)).statusCode());
    assertTrue(JSON.readTree(get(client,"/assignments/current").body()).path("lease_expired").asBoolean());
  }
  @Test void presenceCannotSelfGrantCapabilitiesOrChangeAdministrativeState() throws Exception {
    String capabilities;try(var c=fixture.owner()){capabilities=value(c,"SELECT capabilities::text FROM workers WHERE id=?",fixture.worker);sql(c,"UPDATE workers SET state='OFFLINE' WHERE id=?",fixture.worker);}
    assertEquals(409,post(Map.of("action","PRESENCE","capabilities",Map.of("admin",true))).statusCode());
    assertEquals(200,post(Map.of("action","PRESENCE")).statusCode());
    try(var c=fixture.owner()){
      assertEquals(capabilities,value(c,"SELECT capabilities::text FROM workers WHERE id=?",fixture.worker));
      assertEquals("OFFLINE",value(c,"SELECT state FROM workers WHERE id=?",fixture.worker));
    }
  }
  @Test void runtimeLoginHasNoTablesOrUnderlyingClaimAndRegistryFailureClosesAccess() throws Exception {
    try(var c=DriverManager.getConnection(URL+fixture.db,LOGIN,RUNTIME_PASSWORD)){
      assertEquals(LOGIN,value(c,"SELECT current_user"));
      for(var statement:List.of("SELECT * FROM workers","SELECT * FROM d4.transport_commands","SELECT d4.deliver(NULL,NULL,NULL)","SELECT d3.dispatch(NULL,NULL)","SELECT d2.execution(NULL,NULL)"))
        assertEquals("42501",assertThrows(SQLException.class,()->sql(c,statement)).getSQLState());
    }
    Files.delete(registry);assertEquals(503,get(client,"/assignments/current").statusCode());
  }
  @Test void failedTransportReceiptRollsBackStartBeforeReplay() throws Exception {
    var delivery=poll();var cid=id();var body=envelope(cid,id(),Map.of("action","START","delivery_id",delivery));
    try(var c=fixture.owner()){
      sql(c,"CREATE FUNCTION d4.reject_fixture_receipt() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'Synthetic receipt failure' USING ERRCODE='23514'; END $$;CREATE TRIGGER reject_fixture BEFORE INSERT ON d4.transport_commands FOR EACH ROW EXECUTE FUNCTION d4.reject_fixture_receipt()");
    }
    assertEquals(409,post(client,body,"application/json").statusCode());
    try(var c=fixture.owner()){
      assertEquals("LEASED",value(c,"SELECT state FROM operations"));
      assertEquals("0",value(c,"SELECT count(*) FROM d4.commands WHERE id=?",cid));
      assertEquals("0",value(c,"SELECT count(*) FROM d3.commands WHERE id=?",cid));
      assertEquals("0",value(c,"SELECT count(*) FROM d4.transport_commands WHERE id=?",cid));
      sql(c,"DROP TRIGGER reject_fixture ON d4.transport_commands");
    }
    assertEquals(200,post(client,body,"application/json").statusCode());
    try(var c=fixture.owner()){assertEquals("RUNNING",value(c,"SELECT state FROM operations"));}
  }
  @Test void upgradeV16ToV17PreservesActiveDeliveryAndPollRecovery() throws Exception {
    var upgraded=new DeliveryStoreTest();upgraded.db="d4_http_upgrade_"+id().toString().replace("-","");
    try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+upgraded.db);}
    try {
      assertEquals(16,migrations(upgraded.db,"16").migrate().migrationsExecuted);
      UUID delivery=id();
      try(var c=upgraded.owner()){
        upgraded.fixture(c,true);upgraded.call(c,"deliver",delivery,upgraded.worker,upgraded.request());
        upgraded.call(c,"worker_execution",id(),upgraded.worker,Map.of("action","START","delivery_id",delivery));
        String before=value(c,"SELECT d3.state_body()::text");
        String deliveries=value(c,"SELECT jsonb_agg(to_jsonb(d) ORDER BY id)::text FROM d4.deliveries d");
        var fw=migrations(upgraded.db,"17");assertEquals(1,fw.migrate().migrationsExecuted);fw.validate();assertEquals(0,fw.migrate().migrationsExecuted);
        assertEquals(before,value(c,"SELECT d3.state_body()::text"));
        assertEquals(deliveries,value(c,"SELECT jsonb_agg(to_jsonb(d) ORDER BY id)::text FROM d4.deliveries d"));
        var cid=id();var response=value(c,"SELECT d4.transport(?,?,?::jsonb)::text",cid,upgraded.worker,envelope(cid,id(),Map.of("action","POLL")));
        assertEquals(delivery.toString(),JSON.readTree(response).at("/result/assignment/delivery_id").asText());
        assertEquals("RUNNING",value(c,"SELECT state FROM operations"));
        assertEquals("1",value(c,"SELECT count(*) FROM execution_attempts"));
        assertEquals("1",value(c,"SELECT count(*) FROM d2.reservations"));
      }
    }finally{upgraded.cleanup();}
  }
}
