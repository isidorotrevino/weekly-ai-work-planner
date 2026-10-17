package audit;

import org.junit.jupiter.api.*;
import java.nio.charset.StandardCharsets;
import java.sql.*;
import java.util.*;
import java.util.stream.*;
import static org.junit.jupiter.api.Assertions.*;
import static audit.SchemaAuditTest.*;
import static audit.ContractAuditTest.*;
import static audit.IntegrityContractAuditTest.*;

/** Full grammar conformance is exercised independently of the SQL implementation. */
class SemverContractAuditTest {
 @BeforeAll static void initialize() throws Exception { ContractAuditTest.migrate(); }
 static String result(Connection c,String v,String r) throws Exception {
  try(var p=c.prepareStatement("SELECT d2.compatibility_result(?,?)")){
   p.setString(1,v);p.setString(2,r);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}
  }
 }
 @Test void pinnedNpmConformanceCorpus() throws Exception {
  int count=0;List<String> failures=new ArrayList<>();
  try(var c=open(DB);var paths=java.nio.file.Files.list(ROOT.resolve("testing/D2/src/test/resources/semver"));
      var p=c.prepareStatement("SELECT x.*,d2.compatibility_result(x.version,x.range) actual FROM jsonb_to_recordset(?::jsonb) x(version text,range text,expected text)")){
   for(var file:paths.filter(f->f.getFileName().toString().startsWith("conformance-")).sorted().toList()){
    p.setString(1,java.nio.file.Files.readString(file,StandardCharsets.UTF_8));
    try(var rs=p.executeQuery()){
     while(rs.next()){
      count++;
      if(!Objects.equals(rs.getString("expected"),rs.getString("actual")) && failures.size()<30)
       failures.add(rs.getString("version")+" :: "+rs.getString("range")+" expected="+rs.getString("expected")+" actual="+rs.getString("actual"));
     }
    }
   }
   assertEquals(29829,count);assertTrue(failures.isEmpty(),String.join("\n",failures));
  }
 }
 @Test void migrationFromV10PreservesInputsAndReportsIncompatibilities() throws Exception {
  String db="d2_semver_upgrade";
  var old=org.flywaydb.core.Flyway.configure().dataSource(URL+db,"d2_auditor","")
   .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed")).target("10").load();
  old.migrate();String invalid,range;
  try(var c=open(db)){
   var f=fixture(c);invalid=cap(c,f);sql(c,"UPDATE capability_versions SET version='01.2.3' WHERE id="+q(invalid));
   range=insert(c,"capability_requirements","consumer_task_id,capability_id,version_constraint,environment,kind",q(f.t())+",(SELECT capability_id FROM capability_versions WHERE id="+q(invalid)+"),'bad-range','test','HARD'");
   assertEquals("false",value(c,"SELECT d2.compatible('1.2.3','*')::text"));
  }
  var updated=org.flywaydb.core.Flyway.configure().dataSource(URL+db,"d2_auditor","")
   .locations("filesystem:"+ROOT.resolve("migrations"),"filesystem:"+ROOT.resolve("migrations-proposed")).load();
  assertEquals(1,updated.migrate().migrationsExecuted);updated.validate();assertEquals(0,updated.migrate().migrationsExecuted);
  try(var c=open(db)){
   assertEquals("01.2.3",value(c,"SELECT version FROM capability_versions WHERE id="+q(invalid)));
   assertEquals("INVALID_VERSION",value(c,"SELECT status FROM d2.semver_preflight WHERE id="+q(invalid)));
   assertEquals("INVALID_RANGE",value(c,"SELECT status FROM d2.semver_preflight WHERE id="+q(range)));
   assertEquals("true",value(c,"SELECT d2.compatible('1.2.3','*')::text"));
   assertEquals("11",value(c,"SELECT count(*) FROM flyway_schema_history WHERE success"));
  }
 }
 @Test void precedenceAndBuildMetadata() throws Exception {
  var ordered=List.of("1.0.0-alpha","1.0.0-alpha.1","1.0.0-alpha.beta","1.0.0-beta","1.0.0-beta.2","1.0.0-beta.11","1.0.0-rc.1","1.0.0");
  try(var c=open(DB);var p=c.prepareStatement("SELECT d2.semver_compare(d2.semver_parse(?),d2.semver_parse(?))")){
   for(int i=0;i<ordered.size();i++)for(int j=0;j<ordered.size();j++){
    p.setString(1,ordered.get(i));p.setString(2,ordered.get(j));try(var rs=p.executeQuery()){rs.next();assertEquals(Integer.signum(i-j),rs.getInt(1));}
   }
   p.setString(1,"1.2.3+build.001");p.setString(2,"1.2.3+other");try(var rs=p.executeQuery()){rs.next();assertEquals(0,rs.getInt(1));}
  }
 }
 @Test void explicitLimitsAndInvalidInputsFailClosed() throws Exception {
  try(var c=open(DB)){
   assertEquals("LIMIT_EXCEEDED",result(c,"1.2.3+"+"a".repeat(251),"*"));
   assertEquals("LIMIT_EXCEEDED",result(c,"1.2.3","*".repeat(4097)));
   assertEquals("LIMIT_EXCEEDED",result(c,"1.2.3",String.join("||",Collections.nCopies(33,"1"))));
   assertEquals("LIMIT_EXCEEDED",result(c,"1.2.3",String.join(" ",Collections.nCopies(129,"1"))));
   assertEquals("INVALID_VERSION",result(c,"9007199254740992.0.0","*"));
   assertEquals("MATCH",result(c,"9007199254740991.0.0","9007199254740991.0.0"));
   assertEquals("LIMIT_EXCEEDED",result(c,"1.2.3",">=9007199254740992.0.0"));
   assertEquals("INVALID_VERSION",result(c,null,"*"));assertEquals("INVALID_RANGE",result(c,"1.2.3",null));
   assertEquals("INVALID_RANGE",result(c,"1.2.3","* || invalid"));
   assertEquals("false",value(c,"SELECT d2.compatible(NULL,NULL)::text"));
   // No floating-point rounding for numeric prerelease identifiers.
   assertEquals("NO_MATCH",result(c,"1.0.0-99999999999999999999","<=1.0.0-99999999999999999998"));
  }
 }
 @TestFactory Stream<DynamicTest> sqlAdmissionAndCompletion(){
  return List.of(
   new Case("hard_range_claim_and_verify",(c,s)->{
    String v=cap(c,s.f());makeAvailable(c,v);
    String req=require(c,s,v,"HARD",">=1.2.0 <2 || ^3");
    call(c,"execution",id(),exec(s.f(),"CLAIM"));LifecycleContractAuditTest.callback(c,s,8);RecoveryContractAuditTest.acceptance(c,s.f());
    sql(c,"UPDATE capability_requirements SET version_constraint='>=2 <3' WHERE id="+q(req));
    rejected(c,"23514",()->call(c,"execution",id(),execFenced(c,s.f(),"VERIFY")));
    sql(c,"UPDATE capability_requirements SET version_constraint='1.2 - 1.3' WHERE id="+q(req));
    call(c,"execution",id(),execFenced(c,s.f(),"VERIFY"));
    assertEquals("COMPLETED",value(c,"SELECT state FROM operations WHERE id="+q(s.f().o())));
   }),
   new Case("hard_prerelease_requires_explicit_range",(c,s)->{
    String v=cap(c,s.f());sql(c,"UPDATE capability_versions SET version='1.2.3-rc.2+build.4' WHERE id="+q(v));makeAvailable(c,v);
    String req=require(c,s,v,"HARD","^1.2.0");
    rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));
    sql(c,"UPDATE capability_requirements SET version_constraint='>=1.2.3-rc.1 <2' WHERE id="+q(req));
    call(c,"execution",id(),exec(s.f(),"CLAIM"));
   }),
   new Case("mockable_invalid_range_cannot_complete",(c,s)->{
    String v=cap(c,s.f());makeAvailable(c,v);String req=require(c,s,v,"MOCKABLE","bad-range");
    call(c,"execution",id(),exec(s.f(),"CLAIM"));LifecycleContractAuditTest.callback(c,s,8);RecoveryContractAuditTest.acceptance(c,s.f());
    rejected(c,"23514",()->call(c,"execution",id(),execFenced(c,s.f(),"VERIFY")));
    sql(c,"UPDATE capability_requirements SET version_constraint='~1.2' WHERE id="+q(req));
    call(c,"execution",id(),execFenced(c,s.f(),"VERIFY"));
   }),
   new Case("equal_precedence_builds_do_not_share_evidence",(c,s)->{
    String a=cap(c,s.f());sql(c,"UPDATE capability_versions SET version='1.2.3+build.a' WHERE id="+q(a));makeAvailable(c,a);
    String b=insert(c,"capability_versions","capability_id,version,environment,contract_sha256","(SELECT capability_id FROM capability_versions WHERE id="+q(a)+"),'1.2.3+build.b','test',repeat('c',64)");
    call(c,"transition",id(),transition("CAPABILITY_VERSION",b,"PLANNED","IMPLEMENTED",0));
    rejected(c,"23514",()->call(c,"transition",id(),transition("CAPABILITY_VERSION",b,"IMPLEMENTED","VERIFIED",1)));
    require(c,s,b,"HARD","=1.2.3+build.a");
    assertEquals("MATCH",result(c,"1.2.3+build.b","=1.2.3+build.a"));
    rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));
   }),
   new Case("invalid_version_or_range_cannot_claim",(c,s)->{
    String v=cap(c,s.f());makeAvailable(c,v);String req=require(c,s,v,"HARD","* || invalid");
    rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));
    sql(c,"UPDATE capability_requirements SET version_constraint='*' WHERE id="+q(req));
    sql(c,"UPDATE capability_versions SET version='01.2.3' WHERE id="+q(v));
    rejected(c,"23514",()->call(c,"execution",id(),exec(s.f(),"CLAIM")));
   }),
   new Case("parser_helpers_are_not_public_entrypoints",(c,s)->{
    sql(c,"SET LOCAL ROLE d2_runtime");
    rejected(c,"42501",()->sql(c,"SELECT d2.semver_range('*')"));
    call(c,"execution",id(),exec(s.f(),"CLAIM"));
   })
  ).stream().map(x->DynamicTest.dynamicTest(x.name(),()->{try(var c=open(DB)){c.setAutoCommit(false);try{x.action().run(c,setup(c,100));}finally{c.rollback();}}}));
 }
 static String require(Connection c,Setup s,String v,String kind,String range) throws Exception {
  String req=insert(c,"capability_requirements","consumer_task_id,capability_id,version_constraint,environment,kind",q(s.f().t())+",(SELECT capability_id FROM capability_versions WHERE id="+q(v)+"),"+q(range)+",'test',"+q(kind));
  sql(c,"INSERT INTO d2.resolutions VALUES("+q(req)+","+q(v)+")");return req;
 }
}
