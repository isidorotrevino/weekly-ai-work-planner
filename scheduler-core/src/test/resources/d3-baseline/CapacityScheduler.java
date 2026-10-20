// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.scheduler;

import java.math.*;
import java.time.*;
import java.util.*;
import java.util.function.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;

/** Pure planning: no SQL, external calls, mutable global state or executable reservations. */
public final class CapacityScheduler {
  private static final BigDecimal MIN_CONFIDENCE = new BigDecimal("0.8");
  private static final Comparator<UUID> IDS = Comparator.comparing(UUID::toString);
  private static final Duration AGE = Duration.ofDays(7), URGENT = Duration.ofHours(24);
  private final LongSupplier ticks;

  public CapacityScheduler() { this(System::nanoTime); }
  public CapacityScheduler(LongSupplier monotonicTicks) { ticks = Objects.requireNonNull(monotonicTicks); }

  public Result plan(Request request, Snapshot snapshot) {
    Objects.requireNonNull(request); Objects.requireNonNull(snapshot);
    try {
      validateRequest(request);
      if (snapshot.operations().size() > request.limits().maxOperations()
        || snapshot.activeHardEdges().size() > request.limits().maxEdges()
        || snapshot.estimates().size() > request.limits().maxCandidates())
        return aborted(request, snapshot, Status.LIMIT_EXCEEDED, Reason.LIMIT_EXCEEDED);
      return new Run(request, snapshot).compute();
    } catch (BudgetExceeded e) {
      return aborted(request, snapshot, Status.LIMIT_EXCEEDED, Reason.COMPUTE_BUDGET_EXCEEDED);
    } catch (IllegalArgumentException | NullPointerException | ArithmeticException | DateTimeException e) {
      return aborted(request, snapshot, Status.INVALID_INPUT, Reason.INPUT_INVALID);
    }
  }

  private static void validateRequest(Request r) {
    Objects.requireNonNull(r.asOf()); Objects.requireNonNull(r.timezone());
    require(SCHEMA_VERSION.equals(r.schemaVersion()), "Schema version");
    require(r.policyHash() != null && r.policyHash().matches("[a-f0-9]{64}"), "Policy hash");
    require(r.calibrationEpoch() != null && !r.calibrationEpoch().isBlank(), "Epoch");
    var l = Objects.requireNonNull(r.limits());
    require(l.maxOperations() > 0 && l.maxEdges() > 0 && l.maxCandidates() > 0, "Size limits");
    require(l.maxComputeTime() != null && l.maxComputeTime().isPositive(), "Compute limit");
    l.maxComputeTime().toNanos();
  }

  private static Result aborted(Request r, Snapshot s, Status status, Reason why) {
    var decisions = s.operations().stream().filter(Objects::nonNull).map(Operation::id).filter(Objects::nonNull)
      .distinct().sorted(IDS).map(id -> new Decision(id, Disposition.BLOCKED, List.of(why), null, null, null,
        null, null, Map.of(), Map.of(), Map.of(), null, null, List.of(), null)).toList();
    return new Result(SCHEMA_VERSION, ALGORITHM_VERSION, status, true, r.policyHash(), r.calibrationEpoch(),
      r.asOf(), safeHorizon(r),
      decisions, Map.of(), Set.of(), List.of(why));
  }

  private static Instant safeHorizon(Request r) {
    try { return r.asOf() != null && r.timezone() != null ? r.horizonEnd() : null; }
    catch (DateTimeException | ArithmeticException e) { return null; }
  }

  private static void require(boolean condition, String message) { if (!condition) throw new IllegalArgumentException(message); }
  private static boolean active(State s) { return Set.of(State.LEASED, State.RUNNING, State.VERIFYING, State.RECONCILING).contains(s); }
  private static boolean terminal(State s) { return Set.of(State.COMPLETED, State.FAILED, State.CANCELLED).contains(s); }
  private static boolean confidence(BigDecimal c) { return c != null && c.compareTo(MIN_CONFIDENCE) >= 0 && c.compareTo(BigDecimal.ONE) <= 0; }
  private static BigDecimal rounded(BigDecimal n) { return n.setScale(4, RoundingMode.CEILING).stripTrailingZeros(); }
  private static <T> Map<UUID,T> index(List<T> list, Function<T,UUID> id) {
    var result = new TreeMap<UUID,T>(IDS);
    for (var item : list) require(result.put(Objects.requireNonNull(id.apply(item)), item) == null, "Duplicate identity");
    return result;
  }
  private record ServiceKey(UUID projectId, UUID resourceId) { }
  private record PhysicalKey(UUID resourceId, String dimension, String windowKind, String windowKey) { }
  private static final class BudgetExceeded extends RuntimeException { private static final long serialVersionUID = 1L; }

  private final class Run {
    final Request r; final Snapshot s; final long started;
    final Map<UUID,Project> projects; final Map<UUID,Task> tasks; final Map<UUID,Operation> operations;
    final Map<UUID,Resource> resources; final Map<UUID,Account> accounts;
    final Map<UUID,Incident> incidents; final Map<UUID,Reservation> reservations = new TreeMap<>(IDS);
    final Map<UUID,List<Estimate>> estimates = new HashMap<>();
    final Map<PoolKey,BigDecimal> balances = new HashMap<>(); final Set<PoolKey> unknown = new HashSet<>();
    final Map<LaneKey,BigDecimal> usage; final List<Occupancy> occupied;
    final Map<UUID,Decision> decided = new TreeMap<>(IDS);
    final Map<String,List<String>> outgoing = new TreeMap<>(), incoming = new TreeMap<>();
    final Map<String,BigDecimal> weights = new TreeMap<>(); final Map<String,List<String>> paths = new TreeMap<>();
    final Map<String,Instant> deadlines = new TreeMap<>(); final Map<String,Duration> durations = new TreeMap<>();
    final Map<ServiceKey,Rational> service = new HashMap<>(); final List<Reason> diagnostics = new ArrayList<>();
    final Set<String> unknownDuration = new HashSet<>(), unknownDownstream = new HashSet<>();
    List<String> topological;

    Run(Request request, Snapshot snapshot) {
      r = request; s = snapshot; started = ticks.getAsLong();
      projects = index(s.projects(), Project::id); tasks = index(s.tasks(), Task::id);
      operations = index(s.operations(), Operation::id); resources = index(s.resources(), Resource::id);
      accounts = index(s.accounts(), Account::id); incidents = index(s.incidents(), Incident::id);
      usage = new HashMap<>(s.laneUsage()); occupied = new ArrayList<>(s.occupied());
      validate(); graph();
    }

    void budget() { if (ticks.getAsLong() - started >= r.limits().maxComputeTime().toNanos()) throw new BudgetExceeded(); }

    void validate() {
      for (var p : projects.values()) {
        Objects.requireNonNull(p.state()); require(p.priority() >= 0 && p.priority() <= 4, "Priority");
        require(p.weight().signum() >= 0, "Weight");
      }
      for (var t : tasks.values()) require(projects.containsKey(t.projectId()), "Task owner");
      for (var o : operations.values()) {
        budget();
        require(tasks.containsKey(o.taskId()), "Operation owner");
        Objects.requireNonNull(o.state()); Objects.requireNonNull(o.d2Eligibility()); Objects.requireNonNull(o.createdAt());
        require(o.eligibleWait() != null && !o.eligibleWait().isNegative(), "Wait");
        require(o.maxAttempts() >= 1 && o.maxAttempts() <= 20 && o.attempts() >= 0, "Attempts");
        require(o.incidentId() == null || incidents.containsKey(o.incidentId()), "Incident");
      }
      for (var resource : resources.values()) {
        Objects.requireNonNull(resource.workerId());
        // overlapping availability is harmless; it is normalized by slot selection
        resource.availability().forEach(Objects::requireNonNull);
      }
      var physicalKeys = new HashSet<PhysicalKey>();
      for (var a : accounts.values()) {
        budget();
        require(physicalKeys.add(new PhysicalKey(a.resourceId(),a.dimension(),a.windowKind(),a.windowKey())), "Duplicate physical identity");
        require(resources.containsKey(a.resourceId()), "Account resource");
        require(a.dimension() != null && !a.dimension().isBlank() && a.unit() != null && !a.unit().isBlank(), "Dimension/unit");
        require(a.windowKind() != null && !a.windowKind().isBlank() && a.windowKey() != null && !a.windowKey().isBlank(), "Window identity");
        require(Set.of("OPERATIONS","SECONDS","TOKENS","CALIBRATED_QUOTA").contains(a.unit()), "Capacity unit");
        require(a.pools().keySet().equals(EnumSet.allOf(Pool.class)), "All pools");
        Objects.requireNonNull(a.window());
        require(a.basePlannedLimit() == null || a.basePlannedLimit().signum() >= 0, "Base limit");
        for (var p : Pool.values()) {
          var b = a.pools().get(p); Objects.requireNonNull(b);
          require(b.outstanding().signum() >= 0 && b.consumed().signum() >= 0, "Physical facts");
          var key = new PoolKey(a.id(), p);
          if (b.available() == null) unknown.add(key); else balances.put(key, b.available());
        }
      }
      // D2 prohibits overlapping windows of the same resource/dimension/kind.
      var ordered = accounts.values().stream().sorted(Comparator.comparing((Account a) -> a.resourceId().toString())
        .thenComparing(Account::dimension).thenComparing(Account::windowKind).thenComparing(a -> a.window().start())).toList();
      Account previous = null;
      for (var a : ordered) {
        if (previous != null && a.resourceId().equals(previous.resourceId()) && a.dimension().equals(previous.dimension())
          && a.windowKind().equals(previous.windowKind())) require(!a.window().overlaps(previous.window()), "Overlapping physical accounts");
        previous = a;
      }
      for (var e : s.estimates()) {
        require(operations.containsKey(e.operationId()) && resources.containsKey(e.resourceId()), "Estimate owner");
        var list = estimates.computeIfAbsent(e.operationId(), ignored -> new ArrayList<>());
        require(list.stream().noneMatch(old -> old.resourceId().equals(e.resourceId())), "Ambiguous alternative");
        list.add(e);
        for (var entry : e.units().entrySet()) {
          require(accounts.containsKey(entry.getKey()) && accounts.get(entry.getKey()).resourceId().equals(e.resourceId()), "Estimate account");
          require(entry.getValue().signum() > 0, "Estimate units");
        }
      }
      var commitmentTotals = new HashMap<PoolKey,BigDecimal>();
      var consumptionTotals = new HashMap<PoolKey,BigDecimal>();
      var minimumLaneUsage = new HashMap<LaneKey,BigDecimal>();
      var reservationIds = new HashSet<UUID>();
      for (var reservation : s.reservations()) {
        require(reservationIds.add(reservation.id()) && reservations.put(reservation.operationId(), reservation) == null, "Duplicate reservation");
        require(operations.containsKey(reservation.operationId()) && resources.containsKey(reservation.resourceId()), "Reservation owner");
        require(reservation.pool() != Pool.UNCERTAINTY, "Reserved uncertainty");
        require(reservation.originalLane() != null && reservation.originalLane() != Lane.PRESERVED
          && (reservation.pool() == Pool.INCIDENT) == (reservation.originalLane() == Lane.INCIDENT), "Reservation lane");
        require(!reservation.estimate().isEmpty() && reservation.estimate().keySet().equals(reservation.outstanding().keySet())
          && reservation.estimate().keySet().equals(reservation.consumed().keySet()), "Frozen mapping");
        for (var id : reservation.estimate().keySet()) {
          require(accounts.containsKey(id) && accounts.get(id).resourceId().equals(reservation.resourceId()), "Reservation resource");
          require(reservation.estimate().get(id).signum() > 0 && reservation.outstanding().get(id).signum() >= 0
            && reservation.consumed().get(id).signum() >= 0, "Reservation amounts");
          commitmentTotals.merge(new PoolKey(id, reservation.pool()), reservation.outstanding().get(id), BigDecimal::add);
          consumptionTotals.merge(new PoolKey(id, reservation.pool()), reservation.consumed().get(id), BigDecimal::add);
          if (reservation.originalLane() == Lane.AGED || reservation.originalLane() == Lane.URGENT)
            minimumLaneUsage.merge(new LaneKey(id,reservation.originalLane()),reservation.outstanding().get(id).add(reservation.consumed().get(id)),BigDecimal::add);
        }
        if (reservation.remainingDuration() != null) require(!reservation.remainingDuration().isNegative(), "Remaining duration");
      }
      for (var a : accounts.values()) for (var pool : Pool.values()) {
        var key = new PoolKey(a.id(),pool);
        require(a.pools().get(pool).outstanding().compareTo(commitmentTotals.getOrDefault(key,BigDecimal.ZERO)) == 0,
          "Every physical commitment must be attributed to its reservation");
        var attributed = consumptionTotals.getOrDefault(key,BigDecimal.ZERO);
        require(a.pools().get(pool).consumed().compareTo(attributed) >= 0,"Consumption must match physical evidence");
        if (a.pools().get(pool).consumed().compareTo(attributed) != 0) diagnostics.add(Reason.FAIRNESS_HISTORY_INCOMPLETE);
      }
      minimumLaneUsage.forEach((key,minimum) -> require(usage.getOrDefault(key,BigDecimal.ZERO).compareTo(minimum) >= 0,"Lane usage omits physical commitments or consumption"));
      usage.forEach((key, amount) -> require(accounts.containsKey(key.accountId()) && amount.signum() >= 0
        && (key.lane() == Lane.AGED || key.lane() == Lane.URGENT), "Lane attribution"));
      for (var i : incidents.values()) require(i.severity() >= 1 && i.severity() <= 4 && i.detectedAt() != null, "Severity");
    }

    void node(String n) {
      require(n != null && (n.startsWith("task:") || n.startsWith("cap:")), "Graph node");
      var id = UUID.fromString(n.substring(n.indexOf(':') + 1));
      require(!n.startsWith("task:") || tasks.containsKey(id), "Graph task");
      outgoing.computeIfAbsent(n, ignored -> new ArrayList<>()); incoming.computeIfAbsent(n, ignored -> new ArrayList<>());
      weights.putIfAbsent(n, BigDecimal.ZERO); paths.putIfAbsent(n, List.of(n)); durations.putIfAbsent(n, Duration.ZERO);
    }

    void graph() {
      for (var t : tasks.values()) {
        var n = taskNode(t.id()); node(n);
        var p = projects.get(t.projectId());
        weights.put(n, t.terminal() || p.state() != ProjectState.ACTIVE ? BigDecimal.ZERO : p.weight());
        if (t.deadline() != null && !t.terminal()) deadlines.put(n, t.deadline());
      }
      var edges = new HashSet<Edge>();
      for (var e : s.activeHardEdges()) {
        budget(); node(e.producer()); node(e.consumer()); require(edges.add(e), "Duplicate graph edge");
        outgoing.get(e.producer()).add(e.consumer()); incoming.get(e.consumer()).add(e.producer());
      }
      outgoing.values().forEach(Collections::sort); incoming.values().forEach(Collections::sort);
      var degree = new HashMap<String,Integer>(); var queue = new PriorityQueue<String>();
      incoming.forEach((n, parents) -> { degree.put(n, parents.size()); if (parents.isEmpty()) queue.add(n); });
      topological = new ArrayList<>();
      while (!queue.isEmpty()) {
        budget(); var n = queue.remove(); topological.add(n);
        for (var next : outgoing.get(n)) if (degree.compute(next, (key, old) -> old - 1) == 0) queue.add(next);
      }
      require(topological.size() == outgoing.size(), "HARD cycle");
      // Lower-bound downstream durations, not a promise of dependency completion.
      for (var o : operations.values()) if (!terminal(o.state())) {
        var duration = estimates.getOrDefault(o.id(), List.of()).stream().map(Estimate::durationUpper)
          .filter(Objects::nonNull).filter(Duration::isPositive).min(Duration::compareTo).orElse(null);
        if (duration != null) durations.merge(taskNode(o.taskId()), duration, Duration::plus);
        else unknownDuration.add(taskNode(o.taskId()));
      }
      for (int i = topological.size() - 1; i >= 0; i--) {
        budget(); var consumer = topological.get(i);
        for (var producer : incoming.get(consumer)) {
          if (weights.get(consumer).compareTo(weights.get(producer)) > 0) {
            weights.put(producer, weights.get(consumer));
            var path = new ArrayList<String>(); path.add(producer); path.addAll(paths.get(consumer)); paths.put(producer, List.copyOf(path));
          }
          var due = deadlines.get(consumer);
          if (unknownDuration.contains(consumer) || unknownDownstream.contains(consumer)) {
            if (due != null || unknownDownstream.contains(consumer)) unknownDownstream.add(producer);
          } else if (due != null) deadlines.merge(producer, due.minus(durations.get(consumer)), (a,b) -> a.isBefore(b) ? a : b);
        }
      }
    }

    Priority priority(Operation o) {
      var base = projects.get(tasks.get(o.taskId()).projectId()).weight();
      var n = taskNode(o.taskId()); var path = paths.get(n);
      return new Priority(base, weights.get(n), path.size() > 1 ? path : List.of());
    }
    Pool pool(Operation o) { return o.incidentId() != null && !o.followUp() ? Pool.INCIDENT : Pool.PLANNED; }
    ServiceKey serviceKey(Operation o, UUID resource) { return new ServiceKey(tasks.get(o.taskId()).projectId(), resource); }

    Result compute() {
      initialiseServiceAndActiveWork();
      for (var o : operations.values()) {
        budget(); if (decided.containsKey(o.id())) continue;
        var why = hardBlock(o);
        if (why != null) decided.put(o.id(), unassigned(o, why == Reason.UNKNOWN_ESTIMATE || o.d2Eligibility() == Eligibility.NEEDS_DATA
          ? Disposition.NEEDS_DATA : Disposition.BLOCKED, o.d2Eligibility() != Eligibility.ELIGIBLE && !o.d2Reasons().isEmpty() ? o.d2Reasons() : List.of(why), List.of()));
      }
      if (!s.historyComplete()) diagnostics.add(Reason.FAIRNESS_HISTORY_INCOMPLETE);
      for (var lane : Lane.values()) {
        while (true) {
          budget(); var choices = new ArrayList<Choice>();
          for (var o : operations.values()) if (!decided.containsKey(o.id()) && inLane(o, lane)) {
            var evaluated = evaluate(o, lane);
            if (!evaluated.choices.isEmpty()) choices.add(bestResource(o, evaluated.choices));
          }
          if (choices.isEmpty()) break;
          choices.sort(comparator(lane)); accept(choices.getFirst(), lane);
        }
      }
      for (var o : operations.values()) if (!decided.containsKey(o.id())) {
        budget(); var evaluated = evaluate(o, pool(o) == Pool.INCIDENT ? Lane.INCIDENT : Lane.WEIGHTED);
        var reasons = evaluated.rejected.stream().map(Rejection::reason).distinct().toList();
        if (reasons.isEmpty()) reasons = List.of(Reason.NO_SLOT);
        var all = new ArrayList<>(reasons);
        if (pool(o) == Pool.INCIDENT && reasons.contains(Reason.INSUFFICIENT_POOL)) all.add(Reason.INCIDENT_SHORTFALL);
        if (o.eligibleWait().compareTo(AGE) >= 0) all.add(Reason.STARVATION_RISK);
        var p = projects.get(tasks.get(o.taskId()).projectId());
        boolean data = reasons.stream().anyMatch(why -> Set.of(Reason.UNKNOWN_CAPACITY, Reason.UNKNOWN_ESTIMATE, Reason.LOW_CONFIDENCE,
          Reason.STALE_ESTIMATE, Reason.MISSING_CALIBRATION, Reason.INCOMPLETE_ACCOUNT_VECTOR, Reason.NO_BINDING_ACCOUNTS).contains(why));
        var disposition = data ? Disposition.NEEDS_DATA : Disposition.DEFERRED;
        if (!data && reasons.stream().allMatch(why -> Set.of(Reason.STALE_APPROVAL,Reason.MAPPING_FIXED,Reason.EXPIRED_MAPPING,
          Reason.RESOURCE_UNAVAILABLE,Reason.HEARTBEAT_STALE,Reason.CAPABILITY_MISMATCH).contains(why))) disposition = Disposition.BLOCKED;
        if (!p.deferralAllowed() || reasons.contains(Reason.CAPACITY_DEFICIT)) {
          disposition = Disposition.CONFLICT;
          if (!p.deferralAllowed()) all.add(Reason.DEFERRAL_FORBIDDEN);
        }
        if (deadlines.containsKey(taskNode(o.taskId()))) all.add(Reason.DEADLINE_AT_RISK);
        decided.put(o.id(), unassigned(o, disposition, all, evaluated.rejected));
      }
      budget();
      var status = decided.values().stream().allMatch(d -> d.disposition() == Disposition.TENTATIVE || d.disposition() == Disposition.CARRIED)
        ? Status.COMPLETE : Status.PARTIAL;
      return new Result(SCHEMA_VERSION, ALGORITHM_VERSION, status, true, r.policyHash(), r.calibrationEpoch(), r.asOf(), r.horizonEnd(),
        List.copyOf(decided.values()), balances, unknown, diagnostics.stream().distinct().sorted().toList());
    }

    void initialiseServiceAndActiveWork() {
      for (var res : reservations.values()) {
        budget(); var o = operations.get(res.operationId());
        if (res.pool() == Pool.PLANNED) service.merge(serviceKey(o,res.resourceId()), reservationService(res, Map.of()), Rational::add);
      }
      for (var o : operations.values()) if (active(o.state()) || o.state() == State.BLOCKED_APPROVAL && reservations.containsKey(o.id())) {
        var res = reservations.get(o.id()); require(res != null, "Active work without reservation");
        var end = res.remainingDuration() == null || res.remainingDuration().isZero()
          ? r.horizonEnd() : r.asOf().plus(res.remainingDuration());
        if (end.isAfter(r.horizonEnd())) end = r.horizonEnd();
        var slot = new Interval(r.asOf(), end);
        occupied.add(new Occupancy(resources.get(res.resourceId()).workerId(), o.exclusiveKeys(), slot));
        var reasons = o.state() == State.RECONCILING || o.state() == State.BLOCKED_APPROVAL
          ? List.of(Reason.ACTIVE_COMMITMENT, Reason.RECONCILIATION_REQUIRED) : List.of(Reason.ACTIVE_COMMITMENT);
        decided.put(o.id(), new Decision(o.id(), Disposition.CARRIED, reasons, res.resourceId(), res.pool(), null, slot,
          priority(o), Map.of(), Map.of(), Map.of(), null, null, List.of(), null));
      }
    }

    Reason hardBlock(Operation o) {
      var t = tasks.get(o.taskId()); var p = projects.get(t.projectId());
      if (terminal(o.state()) || t.terminal()) return o.state() == State.CANCELLED ? Reason.RESUME_CONTRACT_REQUIRED : Reason.TERMINAL_STATE;
      if (p.state() != ProjectState.ACTIVE) return Reason.PROJECT_PAUSED;
      if (!incoming.get(taskNode(t.id())).isEmpty()) return Reason.DEPENDENCY_NOT_READY;
      if (o.d2Eligibility() != Eligibility.ELIGIBLE) return o.d2Reasons().isEmpty() ? Reason.D2_GUARD_BLOCKED : o.d2Reasons().getFirst();
      if (!o.contextReady()) return Reason.CONTEXT_MISSING;
      if (o.approvalRequired() && (o.approvalUntil() == null || !o.approvalUntil().isAfter(r.asOf()))) return Reason.STALE_APPROVAL;
      if (o.attempts() >= o.maxAttempts()) return Reason.ATTEMPTS_EXHAUSTED;
      if (o.attempts() > 0 && !o.retrySafe()) return Reason.RETRY_UNSAFE;
      if (o.integrationPhase() && !o.realIntegrationReady()) return Reason.MOCK_INTEGRATION_REQUIRED;
      if (o.state() != State.READY) return Reason.STATE_TRANSITION_REQUIRED;
      if (pool(o) == Pool.PLANNED && (priority(o).effectiveWeight().signum() == 0
        || p.priority() == 4 && priority(o).inheritedPath().isEmpty())) return Reason.P4_PAUSED;
      if (pool(o) == Pool.INCIDENT) {
        var i = incidents.get(o.incidentId());
        if (i.severity() > 2 && !i.activeResponse()) return Reason.INCIDENT_TRIAGE_REQUIRED;
      }
      return null;
    }

    Lane chargedLane(Operation o, Lane selectedLane) {
      var res = reservations.get(o.id());
      return res != null ? res.originalLane() : selectedLane == Lane.PRESERVED ? Lane.WEIGHTED : selectedLane;
    }

    boolean inLane(Operation o, Lane lane) {
      if (pool(o) == Pool.INCIDENT) return lane == Lane.INCIDENT;
      var res = reservations.get(o.id());
      if (res != null && (lane == Lane.AGED || lane == Lane.URGENT) && res.originalLane() != lane) return false;
      return switch (lane) {
        case INCIDENT -> false;
        case PRESERVED -> !protectionBroken() && o.previousResource() != null && o.previousStart() != null
          && !o.previousStart().isBefore(r.asOf()) && o.previousStart().isBefore(r.asOf().plus(Duration.ofMinutes(15)));
        case AGED -> o.eligibleWait().compareTo(AGE) >= 0;
        case URGENT -> deadlines.containsKey(taskNode(o.taskId()));
        case WEIGHTED -> true;
      };
    }

    Rational reservationService(Reservation res, Map<UUID,BigDecimal> delta) {
      Rational largest = Rational.ZERO;
      for (var id : res.estimate().keySet()) {
        var base = accounts.get(id).basePlannedLimit();
        if (!accounts.get(id).window().end().isAfter(r.asOf()) || accounts.get(id).window().start().isAfter(r.asOf())) continue;
        if (base == null || base.signum() <= 0) { diagnostics.add(Reason.UNKNOWN_CAPACITY); continue; }
        var total = res.outstanding().get(id).add(res.consumed().get(id)).add(delta.getOrDefault(id, BigDecimal.ZERO));
        var share = Rational.of(total).divide(Rational.of(base));
        if (share.compareTo(largest) > 0) largest = share;
      }
      return largest;
    }

    record Choice(Operation operation, Resource resource, Estimate estimate, Interval slot, Map<UUID,BigDecimal> delta,
           Rational serviceIncrement, Rational score, Duration slack, boolean frozen) { }
    record Evaluation(List<Choice> choices, List<Rejection> rejected) { }

    Evaluation evaluate(Operation o, Lane lane) {
      var choices = new ArrayList<Choice>(); var rejected = new ArrayList<Rejection>();
      var list = estimates.getOrDefault(o.id(), List.of()).stream().sorted(Comparator.comparing(e -> e.resourceId().toString())).toList();
      if (list.isEmpty()) rejected.add(new Rejection(null, Reason.UNKNOWN_ESTIMATE, null));
      for (var e : list) {
        budget(); var resource = resources.get(e.resourceId());
        var why = resourceGuard(o, e, resource);
        if (why != null) { rejected.add(new Rejection(resource.id(), why, null)); continue; }
        var slot = findSlot(o, e, resource);
        if (slot == null) { rejected.add(new Rejection(resource.id(), Reason.NO_SLOT, null)); continue; }
        var res = reservations.get(o.id());
        if (res != null && (!res.resourceId().equals(e.resourceId()) || res.pool() != pool(o)
          || !sameAmounts(res.estimate(), e.units()))) {
          rejected.add(new Rejection(resource.id(), Reason.MAPPING_FIXED, null)); continue;
        }
        if (o.approvalRequired() && !o.approvalUntil().isAfter(slot.start())) {
          rejected.add(new Rejection(resource.id(), Reason.STALE_APPROVAL, null)); continue;
        }
        if (!e.validUntil().isAfter(slot.start())) { rejected.add(new Rejection(resource.id(), Reason.STALE_ESTIMATE, null)); continue; }
        var bindings = accounts.values().stream().filter(a -> a.resourceId().equals(resource.id()) && a.window().overlaps(slot))
          .map(Account::id).collect(java.util.stream.Collectors.toSet());
        if (bindings.isEmpty()) { rejected.add(new Rejection(resource.id(), Reason.NO_BINDING_ACCOUNTS, null)); continue; }
        if (!bindings.equals(e.units().keySet())) { rejected.add(new Rejection(resource.id(), Reason.INCOMPLETE_ACCOUNT_VECTOR, null)); continue; }
        var delta = new TreeMap<UUID,BigDecimal>(IDS); boolean okay = true;
        for (var id : bindings.stream().sorted(IDS).toList()) {
          var a = accounts.get(id); var demand = rounded(e.units().get(id));
          if (res != null) demand = demand.subtract(res.outstanding().get(id)).max(BigDecimal.ZERO);
          delta.put(id, demand);
          var key = new PoolKey(id, pool(o)); var available = balances.get(key);
          Reason failure = null;
          if (!a.window().contains(slot)) failure = res != null ? Reason.EXPIRED_MAPPING : Reason.NO_SLOT;
          else if (!confidence(a.confidence())) failure = Reason.LOW_CONFIDENCE;
          else if (unknown.contains(key) || a.basePlannedLimit() == null) failure = Reason.UNKNOWN_CAPACITY;
          else if (available.signum() < 0) failure = Reason.CAPACITY_DEFICIT;
          else if (available.compareTo(demand) < 0) failure = Reason.INSUFFICIENT_POOL;
          else if (a.basePlannedLimit().signum() <= 0) failure = Reason.INSUFFICIENT_POOL;
          else if (chargedLane(o,lane) == Lane.AGED || chargedLane(o,lane) == Lane.URGENT) {
            var fraction = chargedLane(o,lane) == Lane.AGED ? new BigDecimal(".05") : new BigDecimal(".20");
            var used = usage.getOrDefault(new LaneKey(id,chargedLane(o,lane)), BigDecimal.ZERO);
            if (used.add(demand).compareTo(a.basePlannedLimit().multiply(fraction)) > 0) failure = Reason.FAIRNESS_BUDGET_EXHAUSTED;
          }
          if (failure != null) { rejected.add(new Rejection(resource.id(), failure, id)); okay = false; }
        }
        if (!okay) continue;
        var deadline = deadlines.get(taskNode(o.taskId()));
        var slack = deadline == null || unknownDuration.contains(taskNode(o.taskId())) || unknownDownstream.contains(taskNode(o.taskId()))
          ? null : Duration.between(slot.end(), deadline);
        if (lane == Lane.URGENT && (slack == null || slack.compareTo(URGENT) > 0)) continue;
        Rational increment = Rational.ZERO;
        if (res != null) increment = reservationService(res, delta).subtract(reservationService(res, Map.of()));
        else for (var entry : delta.entrySet()) {
          var value = Rational.of(entry.getValue()).divide(Rational.of(accounts.get(entry.getKey()).basePlannedLimit()));
          if (value.compareTo(increment) > 0) increment = value;
        }
        var weight = priority(o).effectiveWeight();
        var score = pool(o) == Pool.INCIDENT ? Rational.ZERO : service.getOrDefault(serviceKey(o,resource.id()), Rational.ZERO)
          .add(increment).divide(Rational.of(weight));
        boolean frozen = !protectionBroken() && resource.id().equals(o.previousResource()) && slot.start().equals(o.previousStart())
          && slot.start().isBefore(r.asOf().plus(Duration.ofMinutes(15)));
        if (lane != Lane.PRESERVED || frozen) choices.add(new Choice(o, resource, e, slot, delta, increment, score, slack, frozen));
      }
      return new Evaluation(choices, rejected);
    }

    Reason resourceGuard(Operation o, Estimate e, Resource resource) {
      if (!resource.enabled() || !resource.online()) return Reason.RESOURCE_UNAVAILABLE;
      if (resource.heartbeat() == null || resource.heartbeat().isAfter(r.asOf())
        || Duration.between(resource.heartbeat(), r.asOf()).compareTo(Duration.ofSeconds(90)) > 0) return Reason.HEARTBEAT_STALE;
      if (!resource.capabilities().containsAll(o.requiredCapabilities())) return Reason.CAPABILITY_MISMATCH;
      if (e.durationUpper() == null || !e.durationUpper().isPositive() || e.units().isEmpty()) return Reason.UNKNOWN_ESTIMATE;
      if (!confidence(e.confidence())) return Reason.LOW_CONFIDENCE;
      if (e.calibrationRef() == null || e.calibrationRef().isBlank() || e.provenance() == null || e.provenance().isBlank()) return Reason.MISSING_CALIBRATION;
      if (e.observedAt() == null || e.observedAt().isAfter(r.asOf()) || e.validUntil() == null || !e.validUntil().isAfter(r.asOf())) return Reason.STALE_ESTIMATE;
      var res = reservations.get(o.id());
      if (res != null && res.estimate().keySet().stream().anyMatch(id -> !accounts.get(id).window().end().isAfter(r.asOf()))) return Reason.EXPIRED_MAPPING;
      return null;
    }

    boolean protectionBroken() {
      return r.breakProtection() || incidents.values().stream().anyMatch(i -> i.severity() <= 2);
    }
    boolean estimateWindowsContain(Estimate e, Interval slot) {
      return e.units().keySet().stream().allMatch(id -> accounts.get(id).window().contains(slot));
    }
    boolean sameAmounts(Map<UUID,BigDecimal> a, Map<UUID,BigDecimal> b) {
      return a.keySet().equals(b.keySet()) && a.entrySet().stream().allMatch(e -> e.getValue().compareTo(b.get(e.getKey())) == 0);
    }

    Interval findSlot(Operation o, Estimate e, Resource resource) {
      var candidates = new TreeSet<Instant>(); candidates.add(r.asOf());
      resource.availability().forEach(i -> candidates.add(i.start()));
      for (var a : accounts.values()) if (a.resourceId().equals(resource.id())) candidates.add(a.window().start());
      occupied.forEach(i -> candidates.add(i.interval().end()));
      if (!protectionBroken() && resource.id().equals(o.previousResource()) && o.previousStart() != null
        && !o.previousStart().isBefore(r.asOf()) && o.previousStart().isBefore(r.asOf().plus(Duration.ofMinutes(15)))) {
        var protectedSlot = new Interval(o.previousStart(), o.previousStart().plus(e.durationUpper()));
        if (slotFree(o, resource, protectedSlot) && estimateWindowsContain(e,protectedSlot)) return protectedSlot;
      }
      for (var start : candidates) {
        budget(); if (start.isBefore(r.asOf())) continue;
        var slot = new Interval(start, start.plus(e.durationUpper()));
        if (slotFree(o, resource, slot) && estimateWindowsContain(e,slot)) return slot;
      }
      return null;
    }

    boolean slotFree(Operation o, Resource resource, Interval slot) {
      if (slot.end().isAfter(r.horizonEnd()) || resource.availability().stream().noneMatch(i -> i.contains(slot))) return false;
      for (var busy : occupied) if (busy.interval().overlaps(slot) && (busy.workerId().equals(resource.workerId())
        || !Collections.disjoint(busy.exclusiveKeys(), o.exclusiveKeys()))) return false;
      // No DAG between operations of the same task: serialize their tentative slots.
      return decided.values().stream().filter(d -> d.slot() != null && operations.get(d.operationId()).taskId().equals(o.taskId()))
        .noneMatch(d -> d.slot().overlaps(slot));
    }

    Choice bestResource(Operation o, List<Choice> alternatives) {
      var order = Comparator.comparing((Choice c) -> c.slot().end()).thenComparing(Choice::serviceIncrement)
        .thenComparing(c -> c.resource().id().toString());
      var best = alternatives.stream().min(order).orElseThrow();
      var previous = alternatives.stream().filter(c -> c.resource().id().equals(o.previousResource())).findFirst().orElse(null);
      if (previous != null) {
        if (previous.frozen()) return previous;
        var delay = Duration.between(best.slot().end(), previous.slot().end());
        if (!delay.isNegative() && Rational.of(new BigDecimal(delay.toNanos())).compareTo(
          Rational.of(new BigDecimal(previous.estimate().durationUpper().toNanos())).divide(Rational.of(BigDecimal.TEN))) <= 0) return previous;
      }
      return best;
    }

    Comparator<Choice> comparator(Lane lane) {
      return (a,b) -> {
        var ao = a.operation(); var bo = b.operation(); int c;
        if (lane == Lane.INCIDENT) {
          var ai = incidents.get(ao.incidentId()); var bi = incidents.get(bo.incidentId());
          c = Integer.compare(ai.severity(),bi.severity()); if (c != 0) return c;
          c = ai.detectedAt().compareTo(bi.detectedAt()); if (c != 0) return c;
        } else {
          c = Boolean.compare(b.frozen(),a.frozen()); if (c != 0) return c;
          if (lane == Lane.AGED) {
            c = bo.eligibleWait().compareTo(ao.eligibleWait()); if (c != 0) return c;
            c = priority(bo).effectiveWeight().compareTo(priority(ao).effectiveWeight()); if (c != 0) return c;
          } else if (lane == Lane.URGENT) {
            c = a.slack().compareTo(b.slack()); if (c != 0) return c;
            c = priority(bo).effectiveWeight().compareTo(priority(ao).effectiveWeight()); if (c != 0) return c;
          } else { c = a.score().compareTo(b.score()); if (c != 0) return c; }
          c = Comparator.nullsLast(Duration::compareTo).compare(a.slack(),b.slack()); if (c != 0) return c;
          c = bo.eligibleWait().compareTo(ao.eligibleWait()); if (c != 0) return c;
          c = Boolean.compare(bo.softSatisfied(),ao.softSatisfied()); if (c != 0) return c;
          c = Integer.compare(bo.urgency(),ao.urgency()); if (c != 0) return c;
        }
        c = ao.createdAt().compareTo(bo.createdAt()); if (c != 0) return c;
        c = IDS.compare(tasks.get(ao.taskId()).projectId(),tasks.get(bo.taskId()).projectId()); if (c != 0) return c;
        c = IDS.compare(ao.taskId(),bo.taskId()); if (c != 0) return c;
        c = IDS.compare(ao.id(),bo.id()); if (c != 0) return c;
        return IDS.compare(a.resource().id(),b.resource().id());
      };
    }

    void accept(Choice choice, Lane lane) {
      var o = choice.operation();
      var evaluation = evaluate(o,lane);
      var rejected = new ArrayList<>(evaluation.rejected());
      for (var other : evaluation.choices()) if (!other.resource().id().equals(choice.resource().id()))
        rejected.add(new Rejection(other.resource().id(),Reason.ALTERNATIVE_NOT_SELECTED,null));
      var before = new TreeMap<UUID,BigDecimal>(IDS); var after = new TreeMap<UUID,BigDecimal>(IDS);
      for (var entry : choice.delta().entrySet()) {
        var key = new PoolKey(entry.getKey(),pool(o)); before.put(entry.getKey(),balances.get(key));
        var next = balances.get(key).subtract(entry.getValue()); require(next.signum() >= 0, "Virtual overspend");
        balances.put(key,next); after.put(entry.getKey(),next);
        if (chargedLane(o,lane) == Lane.AGED || chargedLane(o,lane) == Lane.URGENT) usage.merge(new LaneKey(entry.getKey(),chargedLane(o,lane)), entry.getValue(),BigDecimal::add);
      }
      if (pool(o) == Pool.PLANNED) service.merge(serviceKey(o,choice.resource().id()),choice.serviceIncrement(),Rational::add);
      occupied.add(new Occupancy(choice.resource().workerId(),o.exclusiveKeys(),choice.slot()));
      var reasons = new ArrayList<Reason>(); reasons.add(Reason.SELECTED);
      if (choice.frozen()) reasons.add(Reason.FROZEN_INTENT);
      if (choice.slack() != null && choice.slack().isNegative()) reasons.add(Reason.DEADLINE_AT_RISK);
      if (choice.slack() == null && (unknownDownstream.contains(taskNode(o.taskId()))
        || unknownDuration.contains(taskNode(o.taskId())) && deadlines.containsKey(taskNode(o.taskId())))) reasons.add(Reason.DEADLINE_RISK_UNKNOWN);
      var confidence = choice.estimate().confidence();
      for (var id : choice.delta().keySet()) confidence = confidence.min(accounts.get(id).confidence());
      decided.put(o.id(), new Decision(o.id(),Disposition.TENTATIVE,reasons,choice.resource().id(),pool(o),chargedLane(o,lane),choice.slot(),priority(o),
        choice.delta(),before,after,choice.score(),choice.slack(),rejected,confidence));
    }

    Decision unassigned(Operation o, Disposition disposition, List<Reason> reasons, List<Rejection> rejected) {
      return new Decision(o.id(),disposition,reasons,null,null,null,null,priority(o),Map.of(),Map.of(),Map.of(),null,null,rejected,null);
    }
  }
}
