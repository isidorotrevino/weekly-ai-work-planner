// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import io.github.isidorotrevino.planner.runtime.*;
import io.github.isidorotrevino.planner.runtime.CheckpointAccounting.*;
import org.junit.jupiter.api.*;
import java.math.BigDecimal;
import java.time.*;
import java.util.*;
import java.nio.file.*;
import java.security.*;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.io.TempDir;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.runtime.CheckpointAccounting.prepare;

/** Pure proposal tests, not SQL/HTTPS integration or a replacement D2 ledger. */
class CheckpointAccountingTest {
 UUID operation=UUID.randomUUID(),resource=UUID.randomUUID(),worker=UUID.randomUUID(),a=UUID.randomUUID(),b=UUID.randomUUID();
 Instant at=Instant.parse("2026-10-20T10:00:00Z");
 Map<UUID,BigDecimal> v(String x,String y){return Map.of(a,new BigDecimal(x),b,new BigDecimal(y));}
 String h(int n){return String.valueOf(n).repeat(64);}
 List<Account> accounts(){return List.of(new Account(a,"tokens",at.minusSeconds(60),at.plusSeconds(600),new BigDecimal("10")),new Account(b,"requests",at.minusSeconds(60),at.plusSeconds(300),new BigDecimal("6")));}
 List<Step> steps(){return List.of(new Step("one",h(1),v("4","1")),new Step("two",h(2),v("3","2")),new Step("three",h(3),v("3","3")));}
 Manifest manifest(){return new Manifest(operation,resource,"PLANNED",h(4),h(5),accounts(),steps(),3);}
 ClosedAttempt closed(int gen,Map<String,Receipt> steps){return new ClosedAttempt(new ExecutionIdentity(operation,UUID.randomUUID(),worker,resource,gen),gen,steps);}
 Receipt applied(int n){return new Receipt(Status.APPLIED,h(n));}Receipt absent(){return new Receipt(Status.ABSENT,null);}
 ClosedAttempt first(){return closed(1,Map.of("one",applied(1),"two",absent(),"three",absent()));}
 Settlement prefix(){return prepare(manifest(),null,null,first(),1,v("0","0"),v("10","6"),at,false);}
 Settlement middle(Settlement p){return prepare(manifest(),p,p.digest(),closed(2,Map.of("two",applied(2),"three",absent())),2,v("4","1"),v("10","6"),at,false);}
 @Test void twoCheckpointsThreeAttemptsKeepPerAccountDeltasAndOriginalTopUp(){
  var p=prefix();var q=middle(p);var r=prepare(manifest(),q,q.digest(),closed(3,Map.of("three",applied(3))),3,v("7","3"),v("10","6"),at,true);
  assertEquals(v("4","1"),p.consume());assertEquals(v("6","5"),p.release());assertEquals(v("3","2"),q.consume());assertEquals(v("7","4"),q.release());assertEquals(v("3","3"),r.consume());assertEquals(v("7","3"),r.release());assertEquals(v("10","6"),r.cumulative());
  assertEquals(p.applied().get("one"),r.applied().get("one"));assertEquals(1,r.applied().get("one").generation());assertEquals(2,r.applied().get("two").generation());assertEquals(3,r.applied().get("three").generation());assertEquals(q.digest(),r.parentHash());assertTrue(r.terminal());
 }
 @TempDir Path temp;
 @Test void chainedProposalsComposeActualDurableReceiverSeals() throws Exception {
  var key=KeyPairGenerator.getInstance("Ed25519").generateKeyPair();var receiver=EffectJournal.create(temp.resolve("receiver"),key.getPublic(),Clock.fixed(at,ZoneOffset.UTC));
  var data=List.of("first","second","third");var ss=new ArrayList<Step>();for(int n=0;n<3;n++)ss.add(new Step(steps().get(n).id(),HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data.get(n).getBytes(StandardCharsets.UTF_8))),steps().get(n).cost()));
  var m=new Manifest(operation,resource,"PLANNED",h(4),h(5),accounts(),ss,3);Settlement previous=null;var seals=new ArrayList<EffectJournal.Seal>();var closes=new ArrayList<EffectJournal.SignedClose>();var committed=v("0","0");
  for(int n=0;n<3;n++){
   var identity=new ExecutionIdentity(operation,UUID.randomUUID(),worker,resource,n+1);var allowed=new HashSet<String>();for(int j=n;j<3;j++)allowed.add(ss.get(j).id());
   var grant=EffectJournal.sign(new EffectJournal.Grant(receiver.receiverId(),identity,m.contextHash(),m.contextHash(),m.policyHash(),allowed,at,at.plusSeconds(60),at.plusSeconds(60)),key.getPrivate());receiver.install(grant);receiver.apply(grant,ss.get(n).id(),data.get(n).getBytes(StandardCharsets.UTF_8));
   var close=EffectJournal.signClose(receiver.receiverId(),identity,UUID.randomUUID(),key.getPrivate());closes.add(close);var seal=receiver.seal(close);seals.add(seal);var receipts=new HashMap<String,Receipt>();
   seal.steps().forEach((name,r)->receipts.put(name,new Receipt(Status.valueOf(r.status().name()),r.status()==EffectJournal.Status.APPLIED?r.payloadHash():null)));
   previous=prepare(m,previous,previous==null?null:previous.digest(),new ClosedAttempt(identity,seal.sequence(),receipts),n+1,committed,v("10","6"),at,n==2);committed=previous.cumulative();
   receiver=EffectJournal.open(temp.resolve("receiver"),key.getPublic(),Clock.fixed(at,ZoneOffset.UTC));
   for(int j=0;j<=n;j++)assertEquals(seals.get(j),receiver.seal(closes.get(j)));
   if(n>0)assertEquals(EffectJournal.Status.APPLIED,receiver.query(operation,m.contextHash(),"one",n+1).status());
  }
  assertEquals(v("10","6"),previous.cumulative());assertEquals(1,previous.applied().get("one").generation());assertEquals(3,previous.applied().get("three").generation());
 }
 @Test void decimalAndZeroPerAccountCostsAreExact(){var ss=List.of(new Step("one",h(1),v("0.1","0")),new Step("two",h(2),v("0.2","1")));var m=new Manifest(operation,resource,"PLANNED",h(4),h(5),accounts(),ss,3);var p=prepare(m,null,null,closed(1,Map.of("one",applied(1),"two",absent())),1,v("0","0"),v("10","6"),at,false);assertEquals(v("0.1","0"),p.consume());}
 @Test void staleHeadCannotBranch(){var p=prefix();assertThrows(IllegalArgumentException.class,()->prepare(manifest(),p,h(9),closed(2,Map.of("two",applied(2),"three",absent())),2,v("4","1"),v("10","6"),at,false));}
 @Test void noNewProgressCannotConsumeAnotherAttempt(){var p=prefix();assertThrows(IllegalArgumentException.class,()->prepare(manifest(),p,p.digest(),closed(2,Map.of("two",absent(),"three",absent())),2,v("4","1"),v("10","6"),at,false));}
 @Test void unknownDoesNotProduceSettlement(){assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,closed(1,Map.of("one",applied(1),"two",new Receipt(Status.UNKNOWN,null),"three",absent())),1,v("0","0"),v("10","6"),at,false));}
 @Test void omittedStepRejected(){assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,closed(1,Map.of("one",applied(1),"two",absent())),1,v("0","0"),v("10","6"),at,false));}
 @Test void extraReceiptRejected(){var rows=new HashMap<>(first().steps());rows.put("extra",absent());assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,closed(1,rows),1,v("0","0"),v("10","6"),at,false));}
 @Test void applyingPastAbsentViolatesLinearOrder(){assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,closed(1,Map.of("one",absent(),"two",applied(2),"three",absent())),1,v("0","0"),v("10","6"),at,false));}
 @Test void wrongEffectHashRejected(){assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,closed(1,Map.of("one",applied(9),"two",absent(),"three",absent())),1,v("0","0"),v("10","6"),at,false));}
 @Test void inheritedStepCannotBeReappliedOrRebilled(){var p=prefix();assertThrows(IllegalArgumentException.class,()->prepare(manifest(),p,p.digest(),closed(2,Map.of("one",applied(1),"two",applied(2),"three",absent())),2,v("4","1"),v("10","6"),at,false));}
 @Test void journalMustMatchEveryInheritedAccount(){var p=prefix();assertThrows(IllegalArgumentException.class,()->prepare(manifest(),p,p.digest(),closed(2,Map.of("two",applied(2),"three",absent())),2,v("4","0"),v("10","6"),at,false));}
 @Test void missingJournalAccountRejected(){assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,first(),1,Map.of(a,BigDecimal.ZERO),v("10","6"),at,false));}
 @Test void extraJournalAccountRejected(){var j=new HashMap<>(v("0","0"));j.put(UUID.randomUUID(),BigDecimal.ZERO);assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,first(),1,j,v("10","6"),at,false));}
 @Test void residualTopUpRejected(){assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,first(),1,v("0","0"),v("6","5"),at,false));}
 @Test void oneExpiredAccountBlocksWholeProposal(){assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,first(),1,v("0","0"),v("10","6"),at.plusSeconds(300),false));}
 @Test void incompleteOrPrematureFinalityRejected(){assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,first(),1,v("0","0"),v("10","6"),at,true));}
 @Test void finalAttemptCannotCreateAnotherCheckpoint(){var p=prefix();var q=middle(p);assertThrows(IllegalArgumentException.class,()->prepare(manifest(),q,q.digest(),closed(3,Map.of("three",applied(3))),3,v("7","3"),v("10","6"),at,false));}
 @Test void terminalCannotBeContinued(){var p=prefix();var q=middle(p);var end=prepare(manifest(),q,q.digest(),closed(3,Map.of("three",applied(3))),3,v("7","3"),v("10","6"),at,true);assertThrows(IllegalArgumentException.class,()->prepare(manifest(),end,end.digest(),closed(4,Map.of()),4,v("10","6"),v("10","6"),at,true));}
 @Test void differentOperationOrResourceFenced(){var x=new ClosedAttempt(new ExecutionIdentity(UUID.randomUUID(),UUID.randomUUID(),worker,resource,1),1,first().steps());assertThrows(IllegalArgumentException.class,()->prepare(manifest(),null,null,x,1,v("0","0"),v("10","6"),at,false));}
 @Test void generationAndAttemptCountMustFollowD2Parent(){var p=prefix();assertThrows(IllegalArgumentException.class,()->prepare(manifest(),p,p.digest(),closed(3,Map.of("two",applied(2),"three",absent())),2,v("4","1"),v("10","6"),at,false));}
 @Test void manifestCannotChangeOnContinuation(){var p=prefix();var m=new Manifest(operation,resource,"PLANNED",h(4),h(6),accounts(),steps(),3);assertThrows(IllegalArgumentException.class,()->prepare(m,p,p.digest(),closed(2,Map.of("two",applied(2),"three",absent())),2,v("4","1"),v("10","6"),at,false));}
 @Test void completeCostVectorsAndUniqueIdsRequired(){assertThrows(IllegalArgumentException.class,()->new Manifest(operation,resource,"PLANNED",h(4),h(5),accounts(),List.of(new Step("one",h(1),Map.of(a,BigDecimal.ONE))),3));var duplicate=List.of(steps().get(0),steps().get(0));assertThrows(IllegalArgumentException.class,()->new Manifest(operation,resource,"PLANNED",h(4),h(5),accounts(),duplicate,3));}
 @Test void negativeAndExcessCostsRejected(){assertThrows(IllegalArgumentException.class,()->new Step("one",h(1),v("-1","0")));assertThrows(IllegalArgumentException.class,()->new Manifest(operation,resource,"PLANNED",h(4),h(5),accounts(),List.of(new Step("one",h(1),v("11","0"))),3));}
 @Test void manifestDigestCanonicalAcrossMapOrderAndDecimalScale(){var m=manifest();var aa=List.of(new Account(a,"tokens",at.minusSeconds(60),at.plusSeconds(600),new BigDecimal("10.00")),accounts().get(1));assertEquals(m.digest(),new Manifest(operation,resource,"PLANNED",h(4),h(5),aa,steps(),3).digest());}
 @Test void inputAndOutputAreImmutable(){var p=prefix();assertThrows(UnsupportedOperationException.class,()->p.consume().put(a,BigDecimal.ZERO));assertThrows(UnsupportedOperationException.class,()->p.applied().clear());}
}
