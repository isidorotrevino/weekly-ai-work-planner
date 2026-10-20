// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import io.github.isidorotrevino.planner.runtime.*;
import io.github.isidorotrevino.planner.runtime.AbsenceCheckpointAccounting.*;
import org.junit.jupiter.api.*;
import java.math.BigDecimal;
import java.time.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.runtime.AbsenceCheckpointAccounting.prepare;
class AbsenceAccountingTest {
 UUID op=UUID.randomUUID(),worker=UUID.randomUUID(),resource=UUID.randomUUID(),account=UUID.randomUUID();Instant at=Instant.parse("2026-10-20T10:00:00Z");
 Map<UUID,BigDecimal> v(int n){return Map.of(account,BigDecimal.valueOf(n));}
 Manifest m(){return new Manifest(op,resource,"PLANNED","a".repeat(64),"b".repeat(64),List.of(new Account(account,"tokens",at.minusSeconds(60),at.plusSeconds(600),BigDecimal.TEN)),List.of(new Step("one","1".repeat(64),v(4)),new Step("two","2".repeat(64),v(6))),3);}
 ExecutionIdentity identity(int g){return new ExecutionIdentity(op,UUID.randomUUID(),worker,resource,g);}
 ClosedAttempt first(ExecutionIdentity i){return new ClosedAttempt(i,10,Map.of("one",new Receipt(Status.APPLIED,"1".repeat(64)),"two",new Receipt(Status.ABSENT,null)));}
 AbsenceLink link(ExecutionIdentity from,ExecutionIdentity to,int count){return new AbsenceLink(from,to,count,count+1,"c".repeat(64));}
 @Test void explicitAbsenceAllowsRootInSecondAttemptWithoutFakeCheckpoint(){var source=identity(1);var target=identity(2);var result=prepare(m(),null,null,first(target),2,v(0),v(10),at,false,List.of(link(source,target,1)));assertEquals(v(4),result.consume());assertNull(result.parentHash());assertEquals(2,result.identity().generation());assertEquals(2,result.attemptCount());}
 @Test void absentSuffixAfterPrefixPreservesActualGenerationAndCosts(){var parent=prepare(m(),null,null,first(identity(1)),1,v(0),v(10),at,false,List.of());var absent=identity(2);var target=identity(3);var closed=new ClosedAttempt(target,11,Map.of("two",new Receipt(Status.APPLIED,"2".repeat(64))));var result=prepare(m(),parent,parent.digest(),closed,3,v(4),v(10),at,true,List.of(link(absent,target,2)));assertEquals(v(6),result.consume());assertEquals(v(10),result.cumulative());assertEquals(parent.applied().get("one"),result.applied().get("one"));}
 @Test void missingOrForgedLineageCannotSkipFirstAttempt(){var target=identity(2);assertThrows(IllegalArgumentException.class,()->prepare(m(),null,null,first(target),2,v(0),v(10),at,false,List.of()));var wrong=link(identity(1),identity(2),1);assertThrows(IllegalArgumentException.class,()->prepare(m(),null,null,first(target),2,v(0),v(10),at,false,List.of(wrong)));}
 @Test void lineageCannotChangeWorkerOrResetCounter(){var target=identity(2);var foreign=new ExecutionIdentity(op,UUID.randomUUID(),UUID.randomUUID(),resource,1);assertThrows(IllegalArgumentException.class,()->prepare(m(),null,null,first(target),2,v(0),v(10),at,false,List.of(link(foreign,target,1))));assertThrows(IllegalArgumentException.class,()->prepare(m(),null,null,first(target),1,v(0),v(10),at,false,List.of(link(identity(1),target,1))));}
 @Test void orderedMultipleAbsencesConsumeRealD2AttemptBudget(){var a=identity(1);var b=identity(2);var target=identity(3);var links=List.of(link(a,b,1),link(b,target,2));assertThrows(IllegalArgumentException.class,()->prepare(m(),null,null,first(target),3,v(0),v(10),at,false,links));var closed=new ClosedAttempt(target,12,Map.of("one",new Receipt(Status.APPLIED,"1".repeat(64)),"two",new Receipt(Status.APPLIED,"2".repeat(64))));var result=prepare(m(),null,null,closed,3,v(0),v(10),at,true,links);assertEquals(3,result.attemptCount());assertEquals(v(10),result.consume());assertThrows(IllegalArgumentException.class,()->prepare(m(),null,null,closed,3,v(0),v(10),at,true,List.of(links.get(1),links.get(0))));}
 @Test void lineageDoesNotRelaxUnknownOrResidualTopUp(){var source=identity(1);var target=identity(2);var links=List.of(link(source,target,1));var unknown=new ClosedAttempt(target,10,Map.of("one",new Receipt(Status.UNKNOWN,null),"two",new Receipt(Status.ABSENT,null)));assertThrows(IllegalArgumentException.class,()->prepare(m(),null,null,unknown,2,v(0),v(10),at,false,links));assertThrows(IllegalArgumentException.class,()->prepare(m(),null,null,first(target),2,v(0),v(6),at,false,links));}
}
