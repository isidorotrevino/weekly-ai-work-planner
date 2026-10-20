// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.scheduler;

import java.math.BigDecimal;
import java.time.*;
import java.util.*;

/** Immutable boundary DTOs. D2 eligibility/evidence is imported, never reinterpreted here. */
public final class PlanningModel {
  private PlanningModel() { }
  public static final String SCHEMA_VERSION = "d3.snapshot.v1";
  public static final String ALGORITHM_VERSION = "d3.greedy.v1";
  public enum Pool { PLANNED, INCIDENT, UNCERTAINTY }
  public enum Lane { INCIDENT, PRESERVED, AGED, URGENT, WEIGHTED }
  public enum ProjectState { ACTIVE, PAUSED, ARCHIVED }
  public enum State { READY, WAITING_CAPACITY, BLOCKED_APPROVAL, RETRY_PENDING, LEASED, RUNNING, VERIFYING, RECONCILING, COMPLETED, FAILED, CANCELLED }
  public enum Eligibility { ELIGIBLE, BLOCKED, NEEDS_DATA }
  public enum Disposition { TENTATIVE, CARRIED, BLOCKED, NEEDS_DATA, DEFERRED, CONFLICT }
  public enum Status { COMPLETE, PARTIAL, INVALID_INPUT, LIMIT_EXCEEDED }
  public enum Reason {
    SELECTED, ACTIVE_COMMITMENT, RECONCILIATION_REQUIRED, TERMINAL_STATE, PROJECT_PAUSED,
    P4_PAUSED, DEPENDENCY_NOT_READY, UNRESOLVED_BLOCKER, STALE_APPROVAL, CONTEXT_MISSING,
    ATTEMPTS_EXHAUSTED, RETRY_UNSAFE, STATE_TRANSITION_REQUIRED, D2_GUARD_BLOCKED,
    UNKNOWN_CAPACITY, CAPACITY_DEFICIT, INSUFFICIENT_POOL, INCIDENT_SHORTFALL,
    UNKNOWN_ESTIMATE, LOW_CONFIDENCE, STALE_ESTIMATE, MISSING_CALIBRATION,
    RESOURCE_UNAVAILABLE, CAPABILITY_MISMATCH, HEARTBEAT_STALE, NO_SLOT,
    MAPPING_FIXED, EXPIRED_MAPPING, NO_BINDING_ACCOUNTS, INCOMPLETE_ACCOUNT_VECTOR,
    FAIRNESS_BUDGET_EXHAUSTED, STARVATION_RISK, DEADLINE_AT_RISK, DEFERRAL_FORBIDDEN,
    INCIDENT_TRIAGE_REQUIRED, RESUME_CONTRACT_REQUIRED, SAFE_SETTLEMENT_REQUIRED,
    INPUT_INVALID, LIMIT_EXCEEDED, COMPUTE_BUDGET_EXCEEDED, FROZEN_INTENT,
    MOCK_INTEGRATION_REQUIRED, ALTERNATIVE_NOT_SELECTED, FAIRNESS_HISTORY_INCOMPLETE, DEADLINE_RISK_UNKNOWN
  }
  public record Interval(Instant start, Instant end) {
    public Interval { Objects.requireNonNull(start); Objects.requireNonNull(end); if (!end.isAfter(start)) throw new IllegalArgumentException("Empty interval"); }
    public boolean overlaps(Interval other) { return start.isBefore(other.end) && other.start.isBefore(end); }
    public boolean contains(Interval other) { return !other.start.isBefore(start) && !other.end.isAfter(end); }
  }
  public record Limits(int maxOperations, int maxEdges, int maxCandidates, Duration maxComputeTime) { }
  public record Request(String schemaVersion, Instant asOf, ZoneId timezone, String policyHash,
             String calibrationEpoch, Limits limits, boolean breakProtection) {
    public Instant horizonEnd() { return asOf.atZone(timezone).plusDays(7).toInstant(); }
  }
  public record Project(UUID id, ProjectState state, int priority, BigDecimal weightOverride, boolean deferralAllowed) {
    public BigDecimal weight() { return weightOverride != null ? weightOverride : new BigDecimal(new int[]{8, 4, 2, 1, 0}[priority]); }
  }
  public record Task(UUID id, UUID projectId, boolean terminal, Instant deadline) { }
  /** An active HARD edge from D2: task nodes use task:<uuid>, capability nodes cap:<uuid>. */
  public record Edge(String producer, String consumer) { }
  public static String taskNode(UUID id) { return "task:" + id; }
  public record Resource(UUID id, UUID workerId, boolean enabled, boolean online, Instant heartbeat,
             Set<String> capabilities, List<Interval> availability) {
    public Resource { capabilities = Set.copyOf(capabilities); availability = List.copyOf(availability); }
  }
  public record Balance(BigDecimal effectiveLimit, BigDecimal outstanding, BigDecimal consumed) {
    public BigDecimal available() { return effectiveLimit == null ? null : effectiveLimit.subtract(outstanding).subtract(consumed); }
  }
  public record Account(UUID id, UUID resourceId, String dimension, String unit, String windowKind,
             String windowKey, Interval window, BigDecimal basePlannedLimit,
             BigDecimal confidence, Map<Pool, Balance> pools) {
    public Account { pools = Map.copyOf(pools); }
  }
  public record Estimate(UUID operationId, UUID resourceId, Map<UUID, BigDecimal> units,
             Duration durationUpper, BigDecimal confidence, String calibrationRef,
             String provenance, Instant observedAt, Instant validUntil) {
    public Estimate { units = Map.copyOf(units); }
  }
  public record Operation(UUID id, UUID taskId, State state, Eligibility d2Eligibility,
              List<Reason> d2Reasons, int attempts, int maxAttempts, boolean retrySafe,
              boolean contextReady, boolean approvalRequired, Instant approvalUntil,
              Set<String> requiredCapabilities, Duration eligibleWait, boolean softSatisfied,
              int urgency, Instant createdAt, UUID previousResource, Instant previousStart,
              Set<String> exclusiveKeys, UUID incidentId, boolean followUp,
              boolean integrationPhase, boolean realIntegrationReady) {
    public Operation { d2Reasons = List.copyOf(d2Reasons); requiredCapabilities = Set.copyOf(requiredCapabilities); exclusiveKeys = Set.copyOf(exclusiveKeys); }
  }
  public record Incident(UUID id, int severity, Instant detectedAt, boolean activeResponse) { }
  /** Outstanding/consumption already occur in physical balances; estimate is the frozen mapping. */
  public record Reservation(UUID id, UUID operationId, UUID resourceId, Pool pool,
               Map<UUID, BigDecimal> estimate, Map<UUID, BigDecimal> outstanding,
               Map<UUID, BigDecimal> consumed, Duration remainingDuration, Lane originalLane) {
    public Reservation { estimate = Map.copyOf(estimate); outstanding = Map.copyOf(outstanding); consumed = Map.copyOf(consumed); }
  }
  public record LaneKey(UUID accountId, Lane lane) { }
  public record Occupancy(UUID workerId, Set<String> exclusiveKeys, Interval interval) {
    public Occupancy { exclusiveKeys = Set.copyOf(exclusiveKeys); }
  }
  public record Snapshot(List<Project> projects, List<Task> tasks, List<Operation> operations,
             List<Resource> resources, List<Account> accounts, List<Estimate> estimates,
             List<Reservation> reservations, List<Incident> incidents, List<Edge> activeHardEdges,
             Map<LaneKey, BigDecimal> laneUsage, List<Occupancy> occupied,
             boolean historyComplete) {
    public Snapshot {
      projects = List.copyOf(projects); tasks = List.copyOf(tasks); operations = List.copyOf(operations);
      resources = List.copyOf(resources); accounts = List.copyOf(accounts); estimates = List.copyOf(estimates);
      reservations = List.copyOf(reservations); incidents = List.copyOf(incidents); activeHardEdges = List.copyOf(activeHardEdges);
      laneUsage = Map.copyOf(laneUsage); occupied = List.copyOf(occupied);
    }
  }
  public record PoolKey(UUID accountId, Pool pool) { }
  public record Rejection(UUID resourceId, Reason reason, UUID accountId) { }
  public record Priority(BigDecimal baseWeight, BigDecimal effectiveWeight, List<String> inheritedPath) {
    public Priority { inheritedPath = List.copyOf(inheritedPath); }
  }
  public record Decision(UUID operationId, Disposition disposition, List<Reason> reasons,
             UUID resourceId, Pool pool, Lane lane, Interval slot, Priority priority,
             Map<UUID, BigDecimal> incrementalDemand, Map<UUID, BigDecimal> virtualBefore,
             Map<UUID, BigDecimal> virtualAfter, Rational fairFinish, Duration slack,
             List<Rejection> rejectedAlternatives, BigDecimal confidence) {
    public Decision {
      reasons = List.copyOf(reasons); incrementalDemand = Map.copyOf(incrementalDemand);
      virtualBefore = Map.copyOf(virtualBefore); virtualAfter = Map.copyOf(virtualAfter);
      rejectedAlternatives = List.copyOf(rejectedAlternatives);
    }
  }
  /** reviewOnly=true: neither COMPLETE nor TENTATIVE authorizes publication/CLAIM. */
  public record Result(String schemaVersion, String algorithmVersion, Status status, boolean reviewOnly,
            String policyHash, String calibrationEpoch, Instant asOf, Instant horizonEnd,
            List<Decision> decisions, Map<PoolKey, BigDecimal> knownVirtualBalances,
            Set<PoolKey> unknownBalances, List<Reason> diagnostics) {
    public Result {
      decisions = List.copyOf(decisions); knownVirtualBalances = Map.copyOf(knownVirtualBalances);
      unknownBalances = Set.copyOf(unknownBalances); diagnostics = List.copyOf(diagnostics);
    }
  }
}
