// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import io.github.isidorotrevino.planner.runtime.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.runtime.EffectJournal.*;

/** Component tests: real Linux fixtures and durable synthetic effects, not D2 E2E. */
class ProcessRuntimeTest {
  @TempDir Path temp;
  KeyPair authority;EffectJournal receiver;ExecutionIdentity identity;
  final Clock fixed=Clock.fixed(Instant.parse("2026-10-19T10:00:00Z"),ZoneOffset.UTC);
  static UUID id(){return UUID.randomUUID();}
  @BeforeEach void setup() throws Exception {
    authority=KeyPairGenerator.getInstance("Ed25519").generateKeyPair();
    receiver=EffectJournal.create(temp.resolve("receiver"),authority.getPublic(),fixed);
    identity=new ExecutionIdentity(id(),id(),id(),id(),1);
  }
  SignedGrant grant(EffectJournal store,ExecutionIdentity execution,Clock clock,Duration duration) throws Exception {
    var now=clock.instant();return EffectJournal.sign(new Grant(store.receiverId(),execution,"a".repeat(64),"b".repeat(64),"c".repeat(64),Set.of("step-1","step-2"),now,now.plus(duration),now.plus(duration)),authority.getPrivate());
  }
  SignedGrant grant() throws Exception{return grant(receiver,identity,fixed,Duration.ofSeconds(30));}
  SignedClose close(EffectJournal store,ExecutionIdentity execution,UUID command) throws Exception{return EffectJournal.signClose(store.receiverId(),execution,command,authority.getPrivate());}
  @Test void completeSealIsStableAfterLostReplyRestartAndSuccessorEffect() throws Exception {
    var g1=grant();receiver.install(g1);receiver.apply(g1,"step-1","first".getBytes());var command=close(receiver,identity,id());receiver.close(command); // lost reply
    var reopened=EffectJournal.open(temp.resolve("receiver"),authority.getPublic(),fixed);var seal=reopened.seal(command);
    assertEquals(Set.of("step-1","step-2"),seal.steps().keySet());assertEquals(Status.APPLIED,seal.steps().get("step-1").status());assertEquals(Status.ABSENT,seal.steps().get("step-2").status());
    var next=new ExecutionIdentity(identity.operation(),id(),identity.worker(),identity.resource(),2);var g2=grant(reopened,next,fixed,Duration.ofSeconds(30));reopened.install(g2);reopened.apply(g2,"step-2","second".getBytes());
    assertEquals(seal,reopened.seal(command));assertEquals(seal,EffectJournal.open(temp.resolve("receiver"),authority.getPublic(),fixed).seal(command));
  }
  @Test void appliedEffectSurvivesReopenAndRedeliveryWithoutSecondApplication() throws Exception {
    var g=grant();assertEquals(1,receiver.install(g));var first=receiver.apply(g,"step-1","value".getBytes());assertEquals(2,first.sequence());
    var restarted=EffectJournal.open(temp.resolve("receiver"),authority.getPublic(),fixed);
    assertEquals(first,restarted.apply(g,"step-1","value".getBytes()));
    assertEquals(1,restarted.install(g));assertEquals(first,restarted.query(identity.operation(),g.grant().intentHash(),"step-1",1));
  }
  @Test void missingEffectIsUnknownUntilAuthoritativeCloseAndCannotApplyAfterClose() throws Exception {
    var g=grant();receiver.install(g);assertEquals(Status.UNKNOWN,receiver.query(identity.operation(),g.grant().intentHash(),"step-2",1).status());
    var command=close(receiver,identity,id());long sequence=receiver.close(command);assertEquals(sequence,receiver.close(command));
    var reopened=EffectJournal.open(temp.resolve("receiver"),authority.getPublic(),fixed);
    assertEquals(Status.ABSENT,reopened.query(identity.operation(),g.grant().intentHash(),"step-2",1).status());
    assertThrows(Unavailable.class,()->reopened.apply(g,"step-2","late".getBytes()));
    assertThrows(Unavailable.class,()->reopened.install(g));
  }
  @Test void logicalKeyIsStableAcrossAttemptsAndPartialAppliedStepsAreNotRepeated() throws Exception {
    var g1=grant();receiver.install(g1);var first=receiver.apply(g1,"step-1","first".getBytes());
    var next=new ExecutionIdentity(identity.operation(),id(),identity.worker(),identity.resource(),2);
    var g2=grant(receiver,next,fixed,Duration.ofSeconds(30));
    assertThrows(Unavailable.class,()->receiver.install(g2));
    receiver.close(close(receiver,identity,id()));receiver.install(g2);
    assertEquals(first,receiver.apply(g2,"step-1","first".getBytes()));
    assertEquals(Status.APPLIED,receiver.apply(g2,"step-2","second".getBytes()).status());
    assertThrows(Unavailable.class,()->receiver.apply(g1,"step-2","stale".getBytes()));
    assertThrows(Unavailable.class,()->receiver.apply(g2,"step-1","changed".getBytes()));
  }
  @Test void forgedHigherGenerationAndMismatchedBindingsCannotGrantAuthority() throws Exception {
    var g=grant();receiver.install(g);
    var high=new ExecutionIdentity(identity.operation(),id(),identity.worker(),identity.resource(),999);
    var unsigned=grant(receiver,high,fixed,Duration.ofSeconds(30)).grant();
    assertThrows(Unavailable.class,()->receiver.install(new SignedGrant(unsigned,g.signature())));
    var wrong=KeyPairGenerator.getInstance("Ed25519").generateKeyPair();
    assertThrows(Unavailable.class,()->receiver.install(EffectJournal.sign(unsigned,wrong.getPrivate())));
    var alien=new ExecutionIdentity(identity.operation(),id(),identity.worker(),identity.resource(),1);
    assertThrows(Unavailable.class,()->receiver.install(grant(receiver,alien,fixed,Duration.ofSeconds(30))));
    assertThrows(Unavailable.class,()->receiver.close(EffectJournal.signClose(receiver.receiverId(),identity,id(),wrong.getPrivate())));
  }
  @Test void closeCommandCannotBeReusedForAnotherExecution() throws Exception {
    var g=grant();receiver.install(g);var command=id();receiver.close(close(receiver,identity,command));
    var other=new ExecutionIdentity(id(),id(),id(),id(),1);receiver.install(grant(receiver,other,fixed,Duration.ofSeconds(30)));
    assertThrows(Unavailable.class,()->receiver.close(close(receiver,other,command)));
  }
  @Test void corruptionTruncationAndMissingJournalNeverBecomeAbsence() throws Exception {
    var g=grant();receiver.install(g);receiver.apply(g,"step-1","value".getBytes());receiver.close(close(receiver,identity,id()));
    var journal=temp.resolve("receiver/journal.bin");byte[] original=Files.readAllBytes(journal);
    Files.write(journal,Arrays.copyOf(original,original.length-1));assertEquals(Status.UNKNOWN,receiver.query(identity.operation(),g.grant().intentHash(),"step-2",1).status());
    assertThrows(IOException.class,()->receiver.install(g));
    Files.write(journal,new byte[0]);assertEquals(Status.UNKNOWN,receiver.query(identity.operation(),g.grant().intentHash(),"step-2",1).status());
    assertThrows(IOException.class,()->receiver.install(g));
    Files.delete(journal);assertEquals(Status.UNKNOWN,receiver.query(identity.operation(),g.grant().intentHash(),"step-2",1).status());
    assertFalse(Files.exists(journal));
  }
  @Test void anotherStoreEpochRejectsOldGrantsEvenWithSameAuthorityKey() throws Exception {
    var g=grant();receiver.install(g);receiver.apply(g,"step-1","value".getBytes());
    var replacement=EffectJournal.create(temp.resolve("replacement"),authority.getPublic(),fixed);
    assertThrows(Unavailable.class,()->replacement.install(g));
    assertEquals(Status.UNKNOWN,replacement.query(identity.operation(),g.grant().intentHash(),"step-1",1).status());
  }
  @Test void actualWallClockExpiryRejectsLateEffect() throws Exception {
    var real=Clock.systemUTC();var store=EffectJournal.create(temp.resolve("real-clock"),authority.getPublic(),real);
    var g=grant(store,identity,real,Duration.ofMillis(250));store.install(g);Thread.sleep(300);
    assertThrows(Unavailable.class,()->store.apply(g,"step-1","late".getBytes()));
    assertEquals(Status.UNKNOWN,store.query(identity.operation(),g.grant().intentHash(),"step-1",1).status());
  }
  @Test void concurrentAppliesHaveOneDurableEffect() throws Exception {
    var g=grant();receiver.install(g);
    try(var pool=Executors.newFixedThreadPool(4)){
      var tasks=new ArrayList<Future<Receipt>>();for(int i=0;i<16;i++)tasks.add(pool.submit(()->receiver.apply(g,"step-1","same".getBytes())));
      var first=tasks.getFirst().get(5,TimeUnit.SECONDS);for(var task:tasks)assertEquals(first,task.get(5,TimeUnit.SECONDS));assertEquals(2,first.sequence());
    }
  }
  @Test void grantCannotExceedLeaseOrSixtySeconds() throws Exception {
    var now=fixed.instant();assertThrows(IllegalArgumentException.class,()->new Grant(receiver.receiverId(),identity,"a".repeat(64),"b".repeat(64),"c".repeat(64),Set.of("step-1"),now,now.plusSeconds(61),now.plusSeconds(100)));
    assertThrows(IllegalArgumentException.class,()->new Grant(receiver.receiverId(),identity,"a".repeat(64),"b".repeat(64),"c".repeat(64),Set.of("step-1"),now,now.plusSeconds(30),now.plusSeconds(20)));
  }
  @Test void validGrantCannotInventAnotherEffectStep() throws Exception {
    var g=grant();receiver.install(g);assertThrows(Unavailable.class,()->receiver.apply(g,"unapproved-step","value".getBytes()));
    receiver.close(close(receiver,identity,id()));assertEquals(Status.UNKNOWN,receiver.query(identity.operation(),g.grant().intentHash(),"unapproved-step",1).status());
  }
  Path job(ExecutionIdentity id){return temp.resolve("supervisor/attempts").resolve(id.attempt().toString());}
  void ready(ExecutionIdentity id) throws Exception {
    long deadline=System.nanoTime()+Duration.ofSeconds(3).toNanos();while(!Files.exists(job(id).resolve("ready"))){if(System.nanoTime()>deadline)fail("Fixture readiness timeout");Thread.sleep(10);}
  }
  @Test void realFixtureSuccessIsRecordedAndAttemptCannotBeSpawnedAgain() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));
    assertFalse(supervisor.hasUnresolvedAttempts());
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.SUCCESS)){
      var outcome=running.await(Duration.ofSeconds(5));assertTrue(outcome.stoppedObserved());assertEquals(0,outcome.exitCode());assertFalse(outcome.timedOut());
    }
    assertEquals("EXITED",FixtureSupervisor.open(temp.resolve("supervisor")).observe(identity).phase());
    assertFalse(supervisor.hasUnresolvedAttempts());
    assertThrows(IOException.class,()->supervisor.start(identity,FixtureSupervisor.Fixture.SUCCESS));
  }
  @Test void timeoutStopsRealGroupAndConcurrentWorkspaceIsBlocked() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));long pid;
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.WAIT)){
      ready(identity);pid=running.pid();assertTrue(ProcessHandle.of(pid).orElseThrow().isAlive());
      var reopened=FixtureSupervisor.open(temp.resolve("supervisor"));assertEquals("RUNNING",reopened.observe(identity).phase());
      var other=new ExecutionIdentity(id(),id(),id(),id(),1);assertThrows(IOException.class,()->reopened.start(other,FixtureSupervisor.Fixture.SUCCESS));
      var outcome=running.await(Duration.ofMillis(20));assertTrue(outcome.timedOut());assertTrue(outcome.stoppedObserved());
    }
    assertFalse(ProcessHandle.of(pid).map(ProcessHandle::isAlive).orElse(false));
  }
  @Test void observationTimeoutDoesNotSignalFinalizeOrReleaseWorkspace() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.WAIT)){
      ready(identity);
      for(int i=0;i<3;i++)assertFalse(running.awaitExit(Duration.ofMillis(20)));
      assertTrue(ProcessHandle.of(running.pid()).orElseThrow().isAlive());
      assertEquals("RUNNING",supervisor.observe(identity).phase());
      try(var files=Files.list(job(identity))){assertFalse(files.anyMatch(p->p.getFileName().toString().startsWith("0003-")));}
      var other=new ExecutionIdentity(id(),id(),id(),id(),1);
      assertThrows(IOException.class,()->supervisor.start(other,FixtureSupervisor.Fixture.SUCCESS));
      assertTrue(running.stop().stoppedObserved());
    }
  }
  @Test void explicitStopCanRunWhileAnotherThreadObservesExit() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.WAIT);var pool=Executors.newSingleThreadExecutor()){
      ready(identity);var entered=new CountDownLatch(1);
      var observer=pool.submit(()->{entered.countDown();return running.awaitExit(Duration.ofSeconds(30));});
      assertTrue(entered.await(1,TimeUnit.SECONDS));
      // A monitor held by awaitExit would delay stop for the entire 30 s wait.
      var stopper=CompletableFuture.supplyAsync(()->{try{return running.stop();}catch(Exception e){throw new CompletionException(e);}});
      var outcome=stopper.get(10,TimeUnit.SECONDS);
      assertTrue(outcome.stoppedObserved());assertTrue(observer.get(2,TimeUnit.SECONDS));
      assertEquals("EXITED",supervisor.observe(identity).phase());
      assertEquals(outcome,running.stop());
    }
  }
  @Test void naturalExitCanBeObservedBeforeDurableFinalization() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.SUCCESS)){
      assertThrows(IllegalArgumentException.class,()->running.awaitExit(Duration.ofSeconds(31)));
      assertThrows(IllegalArgumentException.class,()->running.awaitExit(Duration.ofNanos(-1)));
      assertTrue(running.awaitExit(Duration.ofSeconds(5)));
      var outcome=running.await(Duration.ZERO);
      assertTrue(outcome.stoppedObserved());assertFalse(outcome.timedOut());assertEquals(0,outcome.exitCode());
      assertEquals("EXITED",supervisor.observe(identity).phase());
    }
  }
  @Test void cooperativeRequestIsDurableBoundAndExitsAtSafeBoundary() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));var request=id();
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.COOPERATIVE_PARTIAL)){
      ready(identity);assertFalse(running.awaitExit(Duration.ofMillis(50)));
      running.requestCheckpoint(request);running.requestCheckpoint(request);
      assertThrows(IOException.class,()->running.requestCheckpoint(id()));
      assertEquals(List.of("d4.fixture.checkpoint.v1",identity.key(),request.toString()),Files.readAllLines(job(identity).resolve("checkpoint.request")));
      assertTrue(running.awaitExit(Duration.ofSeconds(5)));var outcome=running.await(Duration.ZERO);
      assertTrue(outcome.stoppedObserved());assertEquals(0,outcome.exitCode());assertFalse(outcome.timedOut());
      assertEquals("{\"fixture\":\"PARTIAL\",\"candidate\":true}",Files.readString(job(identity).resolve("stdout.bin")).strip());
    }
  }
  @Test void singleCarrierConcurrentStopsCannotStarveSupervisor() throws Exception {
    var classes=Path.of(SupervisorStopProbe.class.getProtectionDomain().getCodeSource().getLocation().toURI());
    var runtime=Path.of(FixtureSupervisor.class.getProtectionDomain().getCodeSource().getLocation().toURI());
    var output=temp.resolve("probe.log");
    var process=new ProcessBuilder(Path.of(System.getProperty("java.home"),"bin/java").toString(),"-Djdk.virtualThreadScheduler.parallelism=1","-Djdk.virtualThreadScheduler.maxPoolSize=1","-cp",classes+File.pathSeparator+runtime,SupervisorStopProbe.class.getName(),temp.resolve("supervisor").toString()).redirectErrorStream(true).redirectOutput(output.toFile()).start();
    try{
      assertTrue(process.waitFor(12,TimeUnit.SECONDS),"Single-carrier stop deadlocked");
      assertEquals(0,process.exitValue(),Files.readString(output));assertTrue(Files.readString(output).contains("SINGLE_CARRIER_STOP_CONFIRMED"));
    }finally{process.descendants().forEach(p->p.destroyForcibly());process.destroyForcibly();process.waitFor(3,TimeUnit.SECONDS);}
  }
  @Test void uncooperativeRequestDoesNotBecomeSuccessfulCheckpoint() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.NONCOOPERATIVE_PARTIAL)){
      ready(identity);running.requestCheckpoint(id());assertFalse(running.awaitExit(Duration.ofMillis(100)));
      var outcome=running.stop();assertTrue(outcome.stoppedObserved());assertNotEquals(0,outcome.exitCode());
      assertEquals(0,Files.size(job(identity).resolve("stdout.bin")));
    }
  }
  @Test void logsAreBoundedAndDrainedWithoutBlockingFixture() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.NOISY)){
      var outcome=running.await(Duration.ofSeconds(5));assertTrue(outcome.stoppedObserved());assertEquals(0,outcome.exitCode());
      assertEquals(65536,outcome.stdoutBytes());assertEquals(65536,outcome.stderrBytes());assertTrue(outcome.stdoutTruncated());assertTrue(outcome.stderrTruncated());
      assertEquals(65536,Files.size(job(identity).resolve("stdout.bin")));assertEquals(64,outcome.stdoutHash().length());
    }
  }
  @Test void unconfirmedSpawnIntentBlocksRecoveryInsteadOfRelaunching() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));Files.createDirectory(job(identity));
    var data=new Properties();data.setProperty("phase","START_INTENT");data.setProperty("identity",identity.key());
    try(var out=Files.newOutputStream(job(identity).resolve("0001-START_INTENT.properties"))){data.store(out,"Synthetic crash gap fixture");}
    assertEquals("UNKNOWN",supervisor.observe(identity).phase());
    assertTrue(supervisor.hasUnresolvedAttempts());
    assertThrows(IOException.class,()->supervisor.start(new ExecutionIdentity(id(),id(),id(),id(),1),FixtureSupervisor.Fixture.SUCCESS));
  }
  @Test void nonresponsiveFixtureRequiresBoundedKill() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.IGNORE_TERM)){
      ready(identity);var outcome=running.await(Duration.ofMillis(20));assertTrue(outcome.timedOut());assertTrue(outcome.stoppedObserved());assertNotEquals(0,outcome.exitCode());
    }
  }
  @Test void descendantIsReapedBeforeObservedGroupStop() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.DESCENDANT)){
      ready(identity);var children=ProcessHandle.of(running.pid()).orElseThrow().descendants().toList();assertFalse(children.isEmpty());
      var outcome=running.await(Duration.ofMillis(20));assertTrue(outcome.stoppedObserved());for(var child:children)assertFalse(child.isAlive());
    }
  }
  @Test void missingOrChangedLogsMakeRecoveryUnknown() throws Exception {
    var supervisor=FixtureSupervisor.create(temp.resolve("supervisor"));
    try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.SUCCESS)){assertTrue(running.await(Duration.ofSeconds(5)).stoppedObserved());}
    Files.writeString(job(identity).resolve("stdout.bin"),"changed");assertEquals("UNKNOWN",supervisor.observe(identity).phase());
    assertTrue(supervisor.hasUnresolvedAttempts());
    assertThrows(IOException.class,()->supervisor.start(new ExecutionIdentity(id(),id(),id(),id(),1),FixtureSupervisor.Fixture.SUCCESS));
  }
}
