// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.scheduler;

import java.time.*;
import java.util.*;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.scheduler.ReplanPolicy.*;
import static io.github.isidorotrevino.planner.scheduler.CapacitySchedulerTest.*;

class ReplanPolicyTest {
  static Delivery delivery(long id,Kind kind,int seconds) { return new Delivery(new Event(id(id),kind,NOW.plusSeconds(seconds)),NOW.plusSeconds(seconds)); }
  @Test void continuousEventsCannotPostponeBatchBeyondThirtySeconds() {
    var deliveries=new ArrayList<Delivery>();for(int i=0;i<120;i++)deliveries.add(delivery(i+1,Kind.ORDINARY,i));
    var expected=batch(deliveries).orElseThrow();assertEquals(NOW.plusSeconds(30),expected.dueAt());
    Collections.shuffle(deliveries,new Random(41));assertEquals(expected,batch(deliveries).orElseThrow());
  }
  @Test void criticalEventAcceleratesOrdinaryBatchAndBreaksProtection() {
    var b=batch(List.of(delivery(1,Kind.ORDINARY,0),delivery(2,Kind.INCIDENT_CRITICAL,8))).orElseThrow();
    assertEquals(NOW.plusSeconds(8),b.dueAt());assertTrue(b.breakProtection());
  }
  @Test void priorityChangeBreaksProtectionWithoutPretendingItIsCriticalIncident() {
    var b=batch(List.of(delivery(1,Kind.PRIORITY_CHANGED,0))).orElseThrow();assertTrue(b.breakProtection());assertEquals(NOW.plusSeconds(30),b.dueAt());
  }
  @Test void repeatedDeliveryDoesNotDuplicateOrRescheduleAndConflictingPayloadIsRejected() {
    var event=delivery(1,Kind.ORDINARY,0);
    var repeat=new Delivery(event.event(),NOW.plusSeconds(25));
    assertEquals(batch(List.of(event)),batch(List.of(event,repeat)));
    assertThrows(IllegalArgumentException.class,()->batch(List.of(event,delivery(1,Kind.WORKER_LOST,1))));
  }
  @Test void sweepAndRecalculationLimitsAreIndependentOfProviderReset() {
    assertTrue(sweepDue(null,NOW));assertFalse(sweepDue(NOW,NOW.plusSeconds(59)));assertTrue(sweepDue(NOW,NOW.plusSeconds(60)));
    assertTrue(mayRecalculate(0));assertTrue(mayRecalculate(1));assertFalse(mayRecalculate(2));
    assertThrows(IllegalArgumentException.class,()->mayRecalculate(-1));
  }
  @Test void blockedGapsAndDuplicatedEligibleIntervalsCannotInflateWaitingTime() {
    var a=new PlanningModel.Interval(NOW,NOW.plusSeconds(60));var overlap=new PlanningModel.Interval(NOW.plusSeconds(30),NOW.plusSeconds(90));
    var b=new PlanningModel.Interval(NOW.plusSeconds(120),NOW.plusSeconds(180));
    assertEquals(Duration.ofSeconds(120),eligibleWait(List.of(b,a,overlap,a),NOW.plusSeconds(150)));
    assertEquals(Duration.ZERO,eligibleWait(List.of(a),NOW.minusSeconds(1)));
  }
}
