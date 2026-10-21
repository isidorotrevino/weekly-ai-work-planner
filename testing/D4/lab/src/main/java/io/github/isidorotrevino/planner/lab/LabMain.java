// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;

import io.github.isidorotrevino.planner.worker.*;
import org.springframework.boot.*;
import org.springframework.boot.autoconfigure.*;
import org.springframework.boot.autoconfigure.condition.*;
import org.springframework.context.annotation.*;
import java.nio.file.*;
import java.util.*;

@SpringBootApplication
@Import(WorkerIdentityFilter.class)
public class LabMain {
  public static void main(String[] args) throws Exception {
    if(args.length>0&&args[0].equals("probe")){System.out.println(LabSupport.JSON.writeValueAsString(LabProbe.run(args)));return;}
    LabSupport.load();String mode=args.length==0?"serve":args[0];
    if(mode.equals("bootstrap")){LabBootstrap.run();return;}
    if(mode.equals("audit")){System.out.println(LabSupport.sql("SELECT d4.tree_audit()::text"));return;}
    if(mode.equals("inspect")){System.out.println(LabSupport.sql("SELECT d4.multi_inspect(?)::text",UUID.fromString(args[1])));return;}
    if(mode.equals("request")){
      try(var client=LabSupport.client()){
        var body=args.length>2?LabSupport.JSON.readTree(args[2]):null;
        try{System.out.println(LabSupport.JSON.writeValueAsString(Map.of("status",200,"body",LabSupport.request(client,body==null?"GET":"POST",args[1],body))));}
        catch(LabSupport.Rejected ex){System.out.println(LabSupport.JSON.writeValueAsString(Map.of("status",ex.status)));}
      }return;
    }
    if(mode.equals("health")){try(var c=LabSupport.client()){LabSupport.request(c,"GET","https://localhost:8443/lab/health",null);}return;}
    if(mode.equals("driver")){Thread.sleep(1200000);return;}
    if(mode.equals("network-probe")){boolean reachable=false;try(var socket=new java.net.Socket()){socket.connect(new java.net.InetSocketAddress(args[1],Integer.parseInt(args[2])),1500);reachable=true;}catch(Exception ignored){}System.out.println("{\"reachable\":"+reachable+"}");return;}
    if(mode.equals("rolecheck")){var denied=new ArrayList<String>();for(var q:List.of("SELECT * FROM public.operations","SELECT d2.execution(NULL,NULL)","SELECT d4.lab_record_evidence(NULL,NULL,'APPLIED',true,'{}')","SELECT d4.record_checkpoint_proof(NULL,NULL,'{}')","SELECT d4.record_continuation_acceptance(NULL,NULL,'{}')"))try(var c=LabSupport.connection();var s=c.createStatement()){s.execute(q);throw new IllegalStateException("AUDITOR_PRIVILEGE_LEAK");}catch(java.sql.SQLException ex){if(!"42501".equals(ex.getSQLState()))throw ex;denied.add(ex.getSQLState());}System.out.println(LabSupport.JSON.writeValueAsString(Map.of("denied",denied)));return;}
    var app=new SpringApplication(LabMain.class);
    app.setDefaultProperties(Map.ofEntries(Map.entry("lab.role",LabSupport.config("role")),Map.entry("server.ssl.key-store",LabSupport.CONFIG.resolve("identity.p12").toString()),Map.entry("server.ssl.key-store-type","PKCS12"),Map.entry("server.ssl.key-store-password",LabSupport.config("tls.password")),Map.entry("server.ssl.trust-store","/public/trust.p12"),Map.entry("server.ssl.trust-store-type","PKCS12"),Map.entry("server.ssl.trust-store-password","synthetic-trust-only"),Map.entry("d4.identities",LabSupport.CONFIG.resolve("identities.properties").toString())));
    app.run("--spring.config.name=lab");
  }
  @Bean org.springframework.beans.factory.InitializingBean directTlsOnly(org.springframework.core.env.Environment env){return ()->{if(!"true".equals(env.getProperty("server.ssl.enabled"))||!"need".equals(env.getProperty("server.ssl.client-auth"))||!"none".equals(env.getProperty("server.forward-headers-strategy")))throw new IllegalStateException("DIRECT_MTLS_REQUIRED");};}
  @Bean @ConditionalOnProperty(name="lab.role",havingValue="control") TransportStore transportStore(){return new TransportStore(LabSupport.config("jdbc.url"),LabSupport.config("jdbc.user"),LabSupport.config("jdbc.password"),true);}
  @Bean @ConditionalOnProperty(name="lab.role",havingValue="control") WorkerController workerController(TransportStore store){return new WorkerController(store);}
}
