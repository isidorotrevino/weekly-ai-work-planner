// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import javax.net.ssl.*;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.security.cert.X509Certificate;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** Generated local PKI; no pre-existing certificates, external CA or credentials. */
final class TlsFixture {
  final Path dir,ca,trust,server;
  final String password=UUID.randomUUID().toString();
  int command;
  TlsFixture(Path dir) throws Exception {
    this.dir=dir;Files.createDirectories(dir);ca=dir.resolve("ca.p12");trust=dir.resolve("trust.p12");
    keytool("-genkeypair","-alias","ca","-dname","CN=Synthetic D4 CA","-keyalg","RSA","-keysize","2048",
      "-validity","2","-ext","BC=ca:true","-ext","KU=keyCertSign,cRLSign","-keystore",ca.toString());
    keytool("-exportcert","-alias","ca","-rfc","-keystore",ca.toString(),"-file",dir.resolve("ca.crt").toString());
    keytool("-importcert","-noprompt","-alias","ca","-keystore",trust.toString(),"-file",dir.resolve("ca.crt").toString());
    server=leaf("server","dns:localhost,ip:127.0.0.1","serverAuth",false);
  }
  Path worker(String name,UUID worker,boolean expired) throws Exception{return leaf(name,"uri:urn:weekly-ai-planner:worker:"+worker,"clientAuth",expired);}
  Path leaf(String name,String sans,String eku,boolean expired) throws Exception {
    var store=dir.resolve(name+".p12");var csr=dir.resolve(name+".csr");var signed=dir.resolve(name+".crt");
    keytool("-genkeypair","-alias","leaf","-dname","CN=Synthetic "+name,"-keyalg","RSA","-keysize","2048",
      "-validity","2","-keystore",store.toString());
    keytool("-certreq","-alias","leaf","-keystore",store.toString(),"-file",csr.toString());
    var args=new ArrayList<>(List.of("-gencert","-alias","ca","-keystore",ca.toString(),"-infile",csr.toString(),
      "-outfile",signed.toString(),"-rfc","-validity",expired?"1":"2","-ext","SAN="+sans,"-ext","EKU="+eku,"-ext","KU=digitalSignature"));
    if(expired)args.addAll(List.of("-startdate","-2d"));keytool(args.toArray(String[]::new));
    keytool("-importcert","-noprompt","-alias","ca","-keystore",store.toString(),"-file",dir.resolve("ca.crt").toString());
    keytool("-importcert","-noprompt","-alias","leaf","-keystore",store.toString(),"-file",signed.toString());
    return store;
  }
  Path untrusted() throws Exception {
    var store=dir.resolve("untrusted.p12");keytool("-genkeypair","-alias","leaf","-dname","CN=Synthetic untrusted",
      "-keyalg","RSA","-keysize","2048","-validity","2","-ext","EKU=clientAuth","-keystore",store.toString());return store;
  }
  void keytool(String...args) throws Exception {
    var cmd=new ArrayList<>(List.of(Path.of(System.getProperty("java.home"),"bin","keytool").toString()));
    cmd.addAll(Arrays.asList(args));cmd.addAll(List.of("-storetype","PKCS12","-storepass",password));
    var process=new ProcessBuilder(cmd).redirectErrorStream(true).redirectOutput(dir.resolve("keytool-"+(command++)+".log").toFile()).start();
    if(!process.waitFor(30,TimeUnit.SECONDS)){process.destroyForcibly();throw new IOException("Synthetic PKI command timeout");}
    if(process.exitValue()!=0)throw new IOException("Synthetic PKI generation failed; inspect private keytool logs");
  }
  KeyStore load(Path path) throws Exception {var keys=KeyStore.getInstance("PKCS12");try(var in=Files.newInputStream(path)){keys.load(in,password.toCharArray());}return keys;}
  String fingerprint(Path path) throws Exception {return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(load(path).getCertificate("leaf").getEncoded()));}
  SSLContext context(Path identity) throws Exception {
    KeyManager[] managers=null;
    if(identity!=null){var km=KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());km.init(load(identity),password.toCharArray());managers=km.getKeyManagers();}
    var tm=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());tm.init(load(trust));
    var context=SSLContext.getInstance("TLS");context.init(managers,tm.getTrustManagers(),new SecureRandom());return context;
  }
}
