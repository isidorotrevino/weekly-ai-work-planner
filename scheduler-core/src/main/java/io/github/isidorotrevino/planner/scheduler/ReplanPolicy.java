// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.scheduler;

import java.time.*;
import java.util.*;

/** Pure batching decisions; persistence, outbox acknowledgements and timers belong to I2. */
public final class ReplanPolicy {
  private ReplanPolicy() { }
  public enum Kind {
    INCIDENT_CRITICAL, DEPENDENCY_INVALIDATED, CAPACITY_DEFICIT, WORKER_LOST, APPROVAL_INVALID,
    PRIORITY_CHANGED, CAPACITY_CHANGED, DEPENDENCY_CHANGED, INCIDENT_CHANGED, ORDINARY
  }
  public record Event(UUID id, Kind kind, Instant occurredAt) { }
  public record Delivery(Event event, Instant receivedAt) { }
  public record Batch(List<Event> events, Instant firstReceivedAt, Instant dueAt, boolean breakProtection) {
    public Batch { events = List.copyOf(events); }
  }
  private static boolean immediate(Kind kind) {
    return EnumSet.of(Kind.INCIDENT_CRITICAL,Kind.DEPENDENCY_INVALIDATED,Kind.CAPACITY_DEFICIT,
      Kind.WORKER_LOST,Kind.APPROVAL_INVALID).contains(kind);
  }
  private static boolean breaksProtection(Kind kind) { return immediate(kind) || kind == Kind.PRIORITY_CHANGED; }

  /** One unsent batch: continuous ordinary events cannot move its due time beyond first+30s. */
  public static Optional<Batch> batch(List<Delivery> deliveries) {
    if (deliveries.isEmpty()) return Optional.empty();
    var sorted = deliveries.stream().sorted(Comparator.comparing(Delivery::receivedAt)
      .thenComparing(d -> d.event().id().toString())).toList();
    var unique = new TreeMap<UUID,Event>(Comparator.comparing(UUID::toString));
    var first = sorted.getFirst().receivedAt(); var due = first.plusSeconds(30); boolean breakProtection = false;
    for (var delivery : sorted) {
      var event = delivery.event(); Objects.requireNonNull(event.kind()); Objects.requireNonNull(event.occurredAt());
      if (event.occurredAt().isAfter(delivery.receivedAt())) throw new IllegalArgumentException("Future event");
      var previous = unique.putIfAbsent(event.id(),event);
      if (previous != null) {
        if (!previous.equals(event)) throw new IllegalArgumentException("Idempotency payload conflict");
        continue;
      }
      if (immediate(event.kind()) && delivery.receivedAt().isBefore(due)) due = delivery.receivedAt();
      breakProtection |= breaksProtection(event.kind());
    }
    return Optional.of(new Batch(List.copyOf(unique.values()), first, due, breakProtection));
  }
  public static boolean sweepDue(Instant lastSweep, Instant now) {
    return lastSweep == null || !lastSweep.isAfter(now) && Duration.between(lastSweep,now).compareTo(Duration.ofSeconds(60)) >= 0;
  }
  /** Initial calculation is not a recalculation. Beyond two, preserve history and surface STALE. */
  public static boolean mayRecalculate(int recalculationsAlreadyPerformed) {
    if (recalculationsAlreadyPerformed < 0) throw new IllegalArgumentException("Negative recalculate count");
    return recalculationsAlreadyPerformed < 2;
  }

  /** Union measured eligible intervals; blocked gaps do not accrue, overlaps cannot double-count. */
  public static Duration eligibleWait(List<PlanningModel.Interval> intervals, Instant asOf) {
    var sorted = intervals.stream().filter(i -> i.start().isBefore(asOf)).sorted(Comparator.comparing(PlanningModel.Interval::start)).toList();
    Duration total = Duration.ZERO; Instant start = null, end = null;
    for (var interval : sorted) {
      var finish = interval.end().isBefore(asOf) ? interval.end() : asOf;
      if (start == null) { start = interval.start(); end = finish; }
      else if (!interval.start().isAfter(end)) { if (finish.isAfter(end)) end = finish; }
      else { total = total.plus(Duration.between(start,end)); start = interval.start(); end = finish; }
    }
    return start == null ? total : total.plus(Duration.between(start,end));
  }
}
