// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.scheduler;

import org.junit.jupiter.api.Test;
import java.math.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;

class CapacitySchedulerTest {
  static final Instant NOW = Instant.parse("2026-10-18T10:00:00Z");
  static UUID id(long n) { return new UUID(0,n); }
  static BigDecimal d(String n) { return new BigDecimal(n); }
  static final UUID P=id(1), T=id(2), O=id(3), R=id(4), W=id(5), A=id(6);
  static final String HASH = "a".repeat(64);
  static Request request() { return new Request(SCHEMA_VERSION,NOW,ZoneId.of("Europe/Madrid"),HASH,"calibration-v1",new Limits(1000,5000,4000,Duration.ofSeconds(30)),false); }
  static class Op {
    UUID id=O, task=T, previousResource=null, incident=null;
    State state=State.READY; Eligibility eligibility=Eligibility.ELIGIBLE;
    List<Reason> reasons=List.of(); int attempts=0,max=3,urgency=0;
    boolean retry=true,context=true,approval=false,soft=true,followUp=false,integration=false,real=true;
    Instant approvalUntil=null,previousStart=null; Duration wait=Duration.ZERO;
    Set<String> required=Set.of(), exclusive=Set.of();
    Operation build() { return new Operation(id,task,state,eligibility,reasons,attempts,max,retry,context,approval,approvalUntil,
      required,wait,soft,urgency,NOW.minusSeconds(60),previousResource,previousStart,exclusive,incident,followUp,integration,real); }
  }
  static class Fixture {
    List<Project> projects=new ArrayList<>(List.of(new Project(P,ProjectState.ACTIVE,2,null,true)));
    List<Task> tasks=new ArrayList<>(List.of(new Task(T,P,false,null)));
    List<Operation> operations=new ArrayList<>();
    List<Resource> resources=new ArrayList<>(List.of(resource(R,W,NOW)));
    List<Account> accounts=new ArrayList<>(List.of(account(A,R,"WEEKLY",d("100"),d("0"),d("0"))));
    List<Estimate> estimates=new ArrayList<>(); List<Reservation> reservations=new ArrayList<>();
    List<Incident> incidents=new ArrayList<>(); List<Edge> edges=new ArrayList<>();
    Map<LaneKey,BigDecimal> usage=new HashMap<>(); List<Occupancy> occupied=new ArrayList<>();
    Fixture() { add(O,T,R,Map.of(A,d("10")),Duration.ofMinutes(30),x -> {}); }
    void add(UUID op,UUID task,UUID resource,Map<UUID,BigDecimal> units,Duration duration,Consumer<Op> edit) {
      var o=new Op();o.id=op;o.task=task;edit.accept(o);operations.add(o.build());
      estimates.add(estimate(op,resource,units,duration));
    }
    void edit(Consumer<Op> edit) {
      var o=new Op();edit.accept(o);operations.set(0,o.build());
    }
    Snapshot snapshot() { return new Snapshot(projects,tasks,operations,resources,accounts,estimates,reservations,incidents,edges,usage,occupied,true); }
    Result run() { return new CapacityScheduler().plan(request(),snapshot()); }
    Decision first() { return run().decisions().getFirst(); }
  }
  static Resource resource(UUID r, UUID worker, Instant heartbeat) {
    return new Resource(r,worker,true,true,heartbeat,Set.of("code"),List.of(new Interval(NOW,NOW.plus(Duration.ofDays(8)))));
  }
  static Account account(UUID a,UUID r,String kind,BigDecimal capacity,BigDecimal pending,BigDecimal consumed) {
    var planned=capacity==null?null:capacity.multiply(d(".7"));
    return new Account(a,r,"execution","OPERATIONS",kind,kind+"-real-window",new Interval(NOW.minusSeconds(60),NOW.plus(Duration.ofDays(8))),planned,d(".9"),
      Map.of(Pool.PLANNED,new Balance(planned,pending,consumed),Pool.INCIDENT,new Balance(capacity==null?null:capacity.multiply(d(".2")),d("0"),d("0")),
        Pool.UNCERTAINTY,new Balance(capacity==null?null:capacity.multiply(d(".1")),d("0"),d("0"))));
  }
  static Estimate estimate(UUID op,UUID r,Map<UUID,BigDecimal> units,Duration duration) {
    return new Estimate(op,r,units,duration,d(".9"),"manual-v1","SYNTHETIC",NOW.minusSeconds(1),NOW.plus(Duration.ofDays(8)));
  }
  static Decision decision(Result r,UUID id) { return r.decisions().stream().filter(x -> x.operationId().equals(id)).findFirst().orElseThrow(); }
  static void has(Decision d,Reason r) { assertTrue(d.reasons().contains(r),d.toString()); }
  static void amount(String expected,BigDecimal actual) { assertEquals(0,d(expected).compareTo(actual)); }

  @Test void tentativePlanDoesNotMutatePhysicalSnapshot() {
    var f=new Fixture();var s=f.snapshot();var result=new CapacityScheduler().plan(request(),s);
    assertEquals(Status.COMPLETE,result.status());assertTrue(result.reviewOnly());
    amount("60",result.knownVirtualBalances().get(new PoolKey(A,Pool.PLANNED)));
    amount("70",s.accounts().getFirst().pools().get(Pool.PLANNED).available());
    amount("10",result.decisions().getFirst().incrementalDemand().get(A));
    assertEquals(result,new CapacityScheduler().plan(request(),s));
  }
  @Test void unknownQuotaBlocksWithoutUsingAnotherPool() {
    var f=new Fixture();f.accounts.set(0,account(A,R,"WEEKLY",null,d("0"),d("0")));
    var result=f.run();has(result.decisions().getFirst(),Reason.UNKNOWN_CAPACITY);
    assertEquals(Disposition.NEEDS_DATA,result.decisions().getFirst().disposition());
    assertTrue(result.unknownBalances().contains(new PoolKey(A,Pool.PLANNED)));
  }
  @Test void allSimultaneousWindowsMustFitAtomically() {
    var f=new Fixture();var session=id(7);
    f.accounts.add(account(session,R,"SESSION",d("10"),d("0"),d("0")));
    f.estimates.set(0,estimate(O,R,Map.of(A,d("8"),session,d("8")),Duration.ofMinutes(30)));
    var result=f.run();has(result.decisions().getFirst(),Reason.INSUFFICIENT_POOL);
    amount("70",result.knownVirtualBalances().get(new PoolKey(A,Pool.PLANNED)));
  }
  @Test void cannotOmitBindingAccountToAppearAffordable() {
    var f=new Fixture();f.accounts.add(account(id(7),R,"SESSION",d("100"),d("0"),d("0")));
    has(f.first(),Reason.INCOMPLETE_ACCOUNT_VECTOR);
  }
  @Test void deficitsRemainNegative() {
    var f=new Fixture();f.accounts.set(0,account(A,R,"WEEKLY",d("50"),d("0"),d("40")));
    var result=f.run();has(result.decisions().getFirst(),Reason.CAPACITY_DEFICIT);
    assertEquals(Disposition.CONFLICT,result.decisions().getFirst().disposition());
    amount("-5",result.knownVirtualBalances().get(new PoolKey(A,Pool.PLANNED)));
  }
  @Test void carriedReservationIsNotChargedAgain() {
    var f=new Fixture();f.edit(o -> o.state=State.RUNNING);
    f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("20"),d("10")));
    f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,Map.of(A,d("20")),Map.of(A,d("20")),Map.of(A,d("10")),Duration.ofMinutes(10),Lane.WEIGHTED));
    var result=f.run();assertEquals(Disposition.CARRIED,result.decisions().getFirst().disposition());
    assertTrue(result.decisions().getFirst().incrementalDemand().isEmpty());
    amount("40",result.knownVirtualBalances().get(new PoolKey(A,Pool.PLANNED)));
  }
  @Test void retryOnlyAddsTopUpAndPreservesPreviousConsumption() {
    var f=new Fixture();f.edit(o -> o.attempts=1);
    f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("7"),d("9")));
    f.estimates.set(0,estimate(O,R,Map.of(A,d("20.0")),Duration.ofMinutes(30)));
    f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,Map.of(A,d("20.0")),Map.of(A,d("7")),Map.of(A,d("9")),null,Lane.WEIGHTED));
    var result=f.run();var selected=result.decisions().getFirst();
    amount("13",selected.incrementalDemand().get(A));amount("41",result.knownVirtualBalances().get(new PoolKey(A,Pool.PLANNED)));
    amount("9",f.accounts.getFirst().pools().get(Pool.PLANNED).consumed());
  }
  @Test void retryMappingCannotMoveToAnotherResource() {
    var f=new Fixture();var r=id(14);var a=id(16);f.resources.add(resource(r,id(15),NOW));
    f.accounts.add(account(a,r,"WEEKLY",d("100"),d("0"),d("0")));
    f.estimates.add(estimate(O,r,Map.of(a,d("10")),Duration.ofMinutes(1)));
    f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("0"),d("4")));
    f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,Map.of(A,d("10")),Map.of(A,d("0")),Map.of(A,d("4")),null,Lane.WEIGHTED));
    assertEquals(R,f.first().resourceId());
    assertTrue(f.first().rejectedAlternatives().stream().anyMatch(x -> x.reason()==Reason.MAPPING_FIXED));
  }
  @Test void expiredRetryMappingIsBlockedEvenWithZeroTopUp() {
    var f=new Fixture();var old=f.accounts.getFirst();
    f.accounts.set(0,new Account(A,R,old.dimension(),old.unit(),old.windowKind(),old.windowKey(),new Interval(NOW.minusSeconds(100),NOW),old.basePlannedLimit(),old.confidence(),account(A,R,"WEEKLY",d("100"),d("0"),d("2")).pools()));
    f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,Map.of(A,d("10")),Map.of(A,d("0")),Map.of(A,d("2")),null,Lane.WEIGHTED));
    has(f.first(),Reason.EXPIRED_MAPPING);
  }
  @Test void retryDoesNotResetAttemptLimit() {var f=new Fixture();f.edit(o -> o.attempts=3);has(f.first(),Reason.ATTEMPTS_EXHAUSTED);}
  @Test void unsafeRetryDoesNotRun() {var f=new Fixture();f.edit(o -> {o.attempts=1;o.retry=false;});has(f.first(),Reason.RETRY_UNSAFE);}
  @Test void cancelledCheckpointDoesNotCreateReplacementOperation() {var f=new Fixture();f.edit(o -> o.state=State.CANCELLED);has(f.first(),Reason.RESUME_CONTRACT_REQUIRED);}
  @Test void reconcilingOccupiesWholeHorizonIfDurationUnknown() {
    var f=new Fixture();f.edit(o -> o.state=State.RECONCILING);
    f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("10"),d("0")));
    f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,Map.of(A,d("10")),Map.of(A,d("10")),Map.of(A,d("0")),null,Lane.WEIGHTED));
    f.add(id(10),T,R,Map.of(A,d("1")),Duration.ofMinutes(1),o -> {});
    var result=f.run();has(decision(result,O),Reason.RECONCILIATION_REQUIRED);
    has(decision(result,id(10)),Reason.NO_SLOT);amount("60",result.knownVirtualBalances().get(new PoolKey(A,Pool.PLANNED)));
  }
  @Test void unknownPhysicalCommitmentCannotDisappearThroughPartialActiveSnapshot() {
    var f=new Fixture();f.edit(o -> o.state=State.RUNNING);
    assertEquals(Status.INVALID_INPUT,f.run().status());
  }
  @Test void inheritedPriorityOnlyFollowsBlockingPath() {
    var f=new Fixture();var consumerTask=id(12);var consumerProject=id(11);var cap="cap:"+id(17);
    f.projects.set(0,new Project(P,ProjectState.ACTIVE,3,null,true));
    f.projects.add(new Project(consumerProject,ProjectState.ACTIVE,0,null,true));f.tasks.add(new Task(consumerTask,consumerProject,false,NOW.plus(Duration.ofHours(2))));
    f.add(id(13),consumerTask,R,Map.of(A,d("1")),Duration.ofMinutes(5),o -> {});
    var sibling=id(18);f.tasks.add(new Task(sibling,P,false,null));f.add(id(19),sibling,R,Map.of(A,d("1")),Duration.ofMinutes(5),o -> {});
    f.edges.add(new Edge(taskNode(T),cap));f.edges.add(new Edge(cap,taskNode(consumerTask)));
    var result=f.run();amount("8",decision(result,O).priority().effectiveWeight());amount("1",decision(result,O).priority().baseWeight());
    amount("1",decision(result,id(19)).priority().effectiveWeight());
    assertEquals(List.of(taskNode(T),cap,taskNode(consumerTask)),decision(result,O).priority().inheritedPath());
    has(decision(result,id(13)),Reason.DEPENDENCY_NOT_READY);
  }
  @Test void hardCycleRejectsWholeResultWithoutAPartialPlan() {
    var f=new Fixture();var cap="cap:"+id(17);f.edges.add(new Edge(taskNode(T),cap));f.edges.add(new Edge(cap,taskNode(T)));
    var result=f.run();assertEquals(Status.INVALID_INPUT,result.status());assertTrue(result.knownVirtualBalances().isEmpty());
  }
  @Test void p4CanOnlyEnterAsBlockingPathException() {
    var f=new Fixture();f.projects.set(0,new Project(P,ProjectState.ACTIVE,4,null,true));has(f.first(),Reason.P4_PAUSED);
    var ct=id(12);f.projects.add(new Project(id(11),ProjectState.ACTIVE,0,null,true));f.tasks.add(new Task(ct,id(11),false,null));
    f.edges.add(new Edge(taskNode(T),taskNode(ct)));
    assertEquals(Disposition.TENTATIVE,f.first().disposition());
    f.projects.set(0,new Project(P,ProjectState.PAUSED,4,null,true));has(f.first(),Reason.PROJECT_PAUSED);
  }
  @Test void mocksDoNotPermitRealIntegrationCompletion() {
    var f=new Fixture();f.edit(o -> {o.integration=true;o.real=false;});has(f.first(),Reason.MOCK_INTEGRATION_REQUIRED);
    f.edit(o -> {o.integration=false;o.real=false;});assertEquals(Disposition.TENTATIVE,f.first().disposition());
  }
  @Test void importedD2EligibilityIsNeverOverriddenByDeadline() {
    var f=new Fixture();f.tasks.set(0,new Task(T,P,false,NOW.plusSeconds(1)));
    f.edit(o -> {o.eligibility=Eligibility.BLOCKED;o.reasons=List.of(Reason.UNRESOLVED_BLOCKER);});has(f.first(),Reason.UNRESOLVED_BLOCKER);
  }
  @Test void missingCalibrationAndLowConfidenceAreNotCapacity() {
    var f=new Fixture();var e=f.estimates.getFirst();
    f.estimates.set(0,new Estimate(O,R,e.units(),e.durationUpper(),d(".9"),null,"MANUAL",NOW,NOW.plusSeconds(60)));has(f.first(),Reason.MISSING_CALIBRATION);
    f.estimates.set(0,new Estimate(O,R,e.units(),e.durationUpper(),d(".79"),"manual","MANUAL",NOW,NOW.plusSeconds(60)));has(f.first(),Reason.LOW_CONFIDENCE);
  }
  @Test void lowConfidenceLimitBlocksEvenWithConfidentEstimate() {
    var f=new Fixture();var a=f.accounts.getFirst();
    f.accounts.set(0,new Account(A,R,a.dimension(),a.unit(),a.windowKind(),a.windowKey(),a.window(),a.basePlannedLimit(),d(".79"),a.pools()));has(f.first(),Reason.LOW_CONFIDENCE);
  }
  @Test void estimateMustStillBeFreshAtPlannedStart() {
    var f=new Fixture();f.occupied.add(new Occupancy(W,Set.of(),new Interval(NOW,NOW.plusSeconds(120))));
    f.estimates.set(0,new Estimate(O,R,Map.of(A,d("10")),Duration.ofMinutes(30),d(".9"),"manual","MANUAL",NOW,NOW.plusSeconds(120)));has(f.first(),Reason.STALE_ESTIMATE);
  }
  @Test void approvalMustStillBeFreshAtPlannedStart() {
    var f=new Fixture();f.occupied.add(new Occupancy(W,Set.of(),new Interval(NOW,NOW.plusSeconds(120))));
    f.edit(o -> {o.approval=true;o.approvalUntil=NOW.plusSeconds(120);});has(f.first(),Reason.STALE_APPROVAL);
  }
  @Test void heartbeatExpiryDoesNotPretendLeaseRenewal() {
    var f=new Fixture();f.resources.set(0,resource(R,W,NOW.minusSeconds(90)));assertEquals(Disposition.TENTATIVE,f.first().disposition());
    f.resources.set(0,resource(R,W,NOW.minusSeconds(91)));has(f.first(),Reason.HEARTBEAT_STALE);
    f.resources.set(0,resource(R,W,NOW.plusSeconds(1)));has(f.first(),Reason.HEARTBEAT_STALE);
  }
  @Test void resourceCapabilitiesAreHardConstraints() {var f=new Fixture();f.edit(o -> o.required=Set.of("unavailable"));has(f.first(),Reason.CAPABILITY_MISMATCH);}
  @Test void incidentShortfallCannotTakePlannedOrUncertainty() {
    var f=new Fixture();f.incidents.add(new Incident(id(21),1,NOW,false));f.edit(o -> o.incident=id(21));
    f.estimates.set(0,estimate(O,R,Map.of(A,d("21")),Duration.ofMinutes(30)));
    var result=f.run();has(result.decisions().getFirst(),Reason.INCIDENT_SHORTFALL);
    amount("70",result.knownVirtualBalances().get(new PoolKey(A,Pool.PLANNED)));
    amount("10",result.knownVirtualBalances().get(new PoolKey(A,Pool.UNCERTAINTY)));
  }
  @Test void minorIncidentsNeedTriageAndFollowUpUsesPlanned() {
    var f=new Fixture();f.incidents.add(new Incident(id(21),3,NOW,false));f.edit(o -> o.incident=id(21));has(f.first(),Reason.INCIDENT_TRIAGE_REQUIRED);
    f.incidents.set(0,new Incident(id(21),3,NOW,true));assertEquals(Pool.INCIDENT,f.first().pool());
    f.edit(o -> {o.incident=id(21);o.followUp=true;});assertEquals(Pool.PLANNED,f.first().pool());
  }
  @Test void incidentSeverityDeterminesWhoFits() {
    var f=new Fixture();f.incidents.addAll(List.of(new Incident(id(21),2,NOW.minusSeconds(30),true),new Incident(id(22),1,NOW,true)));
    f.edit(o -> o.incident=id(21));f.estimates.set(0,estimate(O,R,Map.of(A,d("15")),Duration.ofMinutes(30)));
    f.add(id(23),T,R,Map.of(A,d("15")),Duration.ofMinutes(30),o -> o.incident=id(22));
    var result=f.run();assertEquals(Disposition.TENTATIVE,decision(result,id(23)).disposition());has(decision(result,O),Reason.INCIDENT_SHORTFALL);
  }
  @Test void ageLaneIsBoundedPerPhysicalAccountAcrossPlans() {
    var f=new Fixture();f.edit(o -> o.wait=Duration.ofDays(7));f.estimates.set(0,estimate(O,R,Map.of(A,d("3")),Duration.ofMinutes(30)));
    assertEquals(Lane.AGED,f.first().lane());f.usage.put(new LaneKey(A,Lane.AGED),d("3"));
    assertEquals(Lane.WEIGHTED,f.first().lane());amount("3",f.usage.get(new LaneKey(A,Lane.AGED)));
  }
  @Test void urgentLaneOnlyUsesTwentyPercentAndUnusedCapacityReturnsToWeighted() {
    var f=new Fixture();f.tasks.set(0,new Task(T,P,false,NOW.plus(Duration.ofHours(1))));
    assertEquals(Lane.URGENT,f.first().lane());f.usage.put(new LaneKey(A,Lane.URGENT),d("5"));
    assertEquals(Lane.WEIGHTED,f.first().lane());
  }
  @Test void agedLanePrecedesUrgentLaneAndDoesNotDoubleSpend() {
    var f=new Fixture();f.edit(o -> o.wait=Duration.ofDays(7));f.tasks.set(0,new Task(T,P,false,NOW.plus(Duration.ofHours(1))));
    f.estimates.set(0,estimate(O,R,Map.of(A,d("3")),Duration.ofMinutes(30)));
    var result=f.run();assertEquals(Lane.AGED,result.decisions().getFirst().lane());amount("67",result.knownVirtualBalances().get(new PoolKey(A,Pool.PLANNED)));
  }
  @Test void deadlinesCannotOverrideCapacityOrProhibitionOnDeferral() {
    var f=new Fixture();f.projects.set(0,new Project(P,ProjectState.ACTIVE,0,null,false));
    f.tasks.set(0,new Task(T,P,false,NOW.plusSeconds(1)));f.estimates.set(0,estimate(O,R,Map.of(A,d("71")),Duration.ofMinutes(30)));
    var result=f.run();has(result.decisions().getFirst(),Reason.DEFERRAL_FORBIDDEN);has(result.decisions().getFirst(),Reason.DEADLINE_AT_RISK);
    assertEquals(Disposition.CONFLICT,result.decisions().getFirst().disposition());amount("70",result.knownVirtualBalances().get(new PoolKey(A,Pool.PLANNED)));
  }
  @Test void lateButUsefulSlotReportsDeadlineRisk() {
    var f=new Fixture();f.tasks.set(0,new Task(T,P,false,NOW.plusSeconds(1)));has(f.first(),Reason.DEADLINE_AT_RISK);
    assertEquals(Disposition.TENTATIVE,f.first().disposition());
  }
  @Test void workerWithTwoResourcesStillOnlyRunsOneOperation() {
    var f=new Fixture();var r=id(14);var a=id(16);f.resources.add(resource(r,W,NOW));f.accounts.add(account(a,r,"WEEKLY",d("100"),d("0"),d("0")));
    var task=id(12);f.tasks.add(new Task(task,P,false,null));f.add(id(13),task,r,Map.of(a,d("1")),Duration.ofMinutes(30),o -> {});
    var result=f.run();assertFalse(decision(result,O).slot().overlaps(decision(result,id(13)).slot()));
  }
  @Test void exclusiveWorkspacePreventsOverlapAcrossWorkers() {
    var f=new Fixture();f.edit(o -> o.exclusive=Set.of("workspace:a"));var r=id(14);var a=id(16);
    f.resources.add(resource(r,id(15),NOW));f.accounts.add(account(a,r,"WEEKLY",d("100"),d("0"),d("0")));
    var task=id(12);f.tasks.add(new Task(task,P,false,null));f.add(id(13),task,r,Map.of(a,d("1")),Duration.ofMinutes(30),o -> o.exclusive=Set.of("workspace:a"));
    var result=f.run();assertFalse(decision(result,O).slot().overlaps(decision(result,id(13)).slot()));
  }
  @Test void independentWorkspacesCanOverlapAcrossWorkers() {
    var f=new Fixture();f.edit(o -> o.exclusive=Set.of("workspace:a"));var r=id(14);var a=id(16);
    f.resources.add(resource(r,id(15),NOW));f.accounts.add(account(a,r,"WEEKLY",d("100"),d("0"),d("0")));
    var task=id(12);f.tasks.add(new Task(task,P,false,null));f.add(id(13),task,r,Map.of(a,d("1")),Duration.ofMinutes(30),o -> o.exclusive=Set.of("workspace:b"));
    var result=f.run();assertTrue(decision(result,O).slot().overlaps(decision(result,id(13)).slot()));
  }
  @Test void oldResourceIsKeptWithinTenPercentOfItsDuration() {
    var f=new Fixture();var r=id(14);var a=id(16);f.resources.add(resource(r,id(15),NOW));f.accounts.add(account(a,r,"WEEKLY",d("100"),d("0"),d("0")));
    f.estimates.add(estimate(O,r,Map.of(a,d("10")),Duration.ofMinutes(30)));f.edit(o -> o.previousResource=R);
    f.occupied.add(new Occupancy(W,Set.of(),new Interval(NOW,NOW.plus(Duration.ofMinutes(3)))));assertEquals(R,f.first().resourceId());
    f.occupied.set(0,new Occupancy(W,Set.of(),new Interval(NOW,NOW.plusSeconds(181))));assertEquals(r,f.first().resourceId());
  }
  @Test void validNearTermIntentIsPreservedUnlessExplicitlyBroken() {
    var f=new Fixture();f.edit(o -> {o.previousResource=R;o.previousStart=NOW.plusSeconds(600);});
    assertEquals(Lane.WEIGHTED,f.first().lane());has(f.first(),Reason.FROZEN_INTENT);
    var r=request();var broken=new Request(r.schemaVersion(),r.asOf(),r.timezone(),r.policyHash(),r.calibrationEpoch(),r.limits(),true);
    assertEquals(NOW,new CapacityScheduler().plan(broken,f.snapshot()).decisions().getFirst().slot().start());
  }
  @Test void estimatesAreRoundedUpForAdmission() {
    var f=new Fixture();f.estimates.set(0,estimate(O,R,Map.of(A,d("0.00001")),Duration.ofMinutes(30)));
    amount("0.0001",f.first().incrementalDemand().get(A));
  }
  @Test void civilHorizonDoesNotInventProviderReset() {
    var f=new Fixture();var result=f.run();assertEquals(Duration.ofHours(169),Duration.between(NOW,result.horizonEnd()));
    assertEquals(3,result.knownVirtualBalances().size());
  }
  @Test void crossingAccountResetDoesNotFitEvenWhenCalendarAllowsIt() {
    var f=new Fixture();var a=f.accounts.getFirst();f.accounts.set(0,new Account(A,R,a.dimension(),a.unit(),a.windowKind(),a.windowKey(),
      new Interval(NOW.minusSeconds(60),NOW.plusSeconds(600)),a.basePlannedLimit(),a.confidence(),a.pools()));has(f.first(),Reason.NO_SLOT);
  }
  @Test void explicitFuturePhysicalAccountCanBePlannedWithoutCalendarResetInference() {
    var f=new Fixture();var a=f.accounts.getFirst();var later=NOW.plus(Duration.ofHours(1));
    f.accounts.set(0,new Account(A,R,a.dimension(),a.unit(),a.windowKind(),a.windowKey(),new Interval(later,later.plus(Duration.ofDays(1))),a.basePlannedLimit(),a.confidence(),a.pools()));
    assertEquals(later,f.first().slot().start());
  }
  @Test void missingOrExceededSafetyLimitsNeverReturnTentativePrefix() {
    var f=new Fixture();var r=request();var bad=new Request(r.schemaVersion(),NOW,r.timezone(),HASH,r.calibrationEpoch(),null,false);
    assertEquals(Status.INVALID_INPUT,new CapacityScheduler().plan(bad,f.snapshot()).status());
    f.add(id(13),T,R,Map.of(A,d("1")),Duration.ofMinutes(1),o -> {});
    var small=new Request(r.schemaVersion(),NOW,r.timezone(),HASH,r.calibrationEpoch(),new Limits(1,10,10,Duration.ofSeconds(1)),false);
    var result=new CapacityScheduler().plan(small,f.snapshot());assertEquals(Status.LIMIT_EXCEEDED,result.status());
    assertEquals(2,result.decisions().size());assertTrue(result.decisions().stream().noneMatch(x -> x.disposition()==Disposition.TENTATIVE));
  }
  @Test void computeBudgetIsCheckedWithoutWallClockInSchedulingLogic() {
    var clock=new AtomicLong();var scheduler=new CapacityScheduler(() -> clock.getAndAdd(1_000_000_000L));
    var r=request();var small=new Request(r.schemaVersion(),NOW,r.timezone(),HASH,r.calibrationEpoch(),new Limits(100,100,100,Duration.ofSeconds(1)),false);
    var result=scheduler.plan(small,new Fixture().snapshot());assertEquals(Status.LIMIT_EXCEEDED,result.status());
    assertEquals(List.of(Reason.COMPUTE_BUDGET_EXCEEDED),result.diagnostics());
  }
  @Test void duplicateOperationsAndOverlappingAccountWindowsAreInvalid() {
    var f=new Fixture();f.operations.add(f.operations.getFirst());assertEquals(Status.INVALID_INPUT,f.run().status());
    f.operations.removeLast();f.accounts.add(account(id(7),R,"WEEKLY",d("100"),d("0"),d("0")));assertEquals(Status.INVALID_INPUT,f.run().status());
  }
  @Test void weightedAllocationAndCompleteExplanationsArePermutationInvariant() {
    var f=new Fixture();f.operations.clear();f.estimates.clear();f.projects.clear();f.tasks.clear();
    int[] priorities={0,1,3};
    for(int p=0;p<3;p++) {
      var project=id(100+p);var task=id(200+p);f.projects.add(new Project(project,ProjectState.ACTIVE,priorities[p],null,true));f.tasks.add(new Task(task,project,false,null));
      for(int n=0;n<70;n++) f.add(id(1000+p*100+n),task,R,Map.of(A,d("1")),Duration.ofMinutes(1),o -> {});
    }
    // 65 physical planned units gives exactly 40/20/5 unitary allocations.
    f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("0"),d("5")));
    var expected=f.run();assertEquals(Status.PARTIAL,expected.status());
    long[] counts=new long[3];for(int p=0;p<3;p++) {var task=id(200+p);counts[p]=expected.decisions().stream()
      .filter(x -> x.disposition()==Disposition.TENTATIVE && f.operations.stream().anyMatch(o -> o.id().equals(x.operationId()) && o.taskId().equals(task))).count();}
    assertArrayEquals(new long[]{40,20,5},counts);
    var rng=new Random(20261018);
    for(int i=0;i<10;i++) {
      Collections.shuffle(f.operations,rng);Collections.shuffle(f.estimates,rng);Collections.shuffle(f.projects,rng);Collections.shuffle(f.tasks,rng);
      assertEquals(expected,f.run(),"Complete result including explanations must be identical");
    }
  }
  @Test void unattributedCommitmentRejectsSnapshotInsteadOfGuessingWorkerAvailability() {
    var f=new Fixture();f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("1"),d("0")));
    assertEquals(Status.INVALID_INPUT,f.run().status());
  }
  @Test void duplicatedReservationConsumptionCannotExceedPhysicalEvidence() {
    var f=new Fixture();f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,Map.of(A,d("10")),Map.of(A,d("0")),Map.of(A,d("4")),null,Lane.WEIGHTED));
    assertEquals(Status.INVALID_INPUT,f.run().status());
  }
  @Test void retryScoreUsesProjectedServiceWhenDominantAccountChanges() {
    var f=new Fixture();var session=id(7);f.edit(o -> o.attempts=1);
    f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("8"),d("0")));
    f.accounts.add(account(session,R,"SESSION",d("100"),d("4"),d("0")));
    var mapping=Map.of(A,d("8"),session,d("9"));
    f.estimates.set(0,estimate(O,R,mapping,Duration.ofMinutes(30)));
    f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,mapping,Map.of(A,d("8"),session,d("4")),Map.of(A,d("0"),session,d("0")),null,Lane.WEIGHTED));
    var selected=f.first();amount("0",selected.incrementalDemand().get(A));amount("5",selected.incrementalDemand().get(session));
    assertEquals(Rational.of(d("9")).divide(Rational.of(d("140"))),selected.fairFinish());
  }
  @Test void unknownDownstreamDurationDoesNotBecomeZeroSlackEstimate() {
    var f=new Fixture();var consumer=id(12);f.tasks.add(new Task(consumer,P,false,NOW.plus(Duration.ofHours(1))));
    f.add(id(13),consumer,R,Map.of(A,d("1")),Duration.ofMinutes(1),o -> {});
    f.estimates.removeLast();f.edges.add(new Edge(taskNode(T),taskNode(consumer)));
    var result=f.run();var producer=decision(result,O);assertNull(producer.slack());has(producer,Reason.DEADLINE_RISK_UNKNOWN);
    assertEquals(Lane.WEIGHTED,producer.lane());
  }
  @Test void outOfRangeClockReturnsInvalidInputInsteadOfThrowingWhileBuildingErrorResult() {
    var r=request();var invalid=new Request(r.schemaVersion(),Instant.MAX,r.timezone(),HASH,r.calibrationEpoch(),r.limits(),false);
    var result=new CapacityScheduler().plan(invalid,new Fixture().snapshot());
    assertEquals(Status.INVALID_INPUT,result.status());assertNull(result.horizonEnd());
  }
  @Test void retryCannotEscapeOriginalAgedLaneCapByFallingBackToWeighted() {
    var f=new Fixture();f.edit(o -> o.attempts=1);
    f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("3"),d("0")));
    f.estimates.set(0,estimate(O,R,Map.of(A,d("5")),Duration.ofMinutes(30)));
    f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,Map.of(A,d("5")),Map.of(A,d("3")),Map.of(A,d("0")),null,Lane.AGED));
    f.usage.put(new LaneKey(A,Lane.AGED),d("3"));
    has(f.first(),Reason.FAIRNESS_BUDGET_EXHAUSTED);assertNotEquals(Disposition.TENTATIVE,f.first().disposition());
  }
  @Test void retryPreservesOriginalLaneAndOnlyUsesRemainingHeadroom() {
    var f=new Fixture();f.edit(o -> o.attempts=1);
    f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("3"),d("0")));
    f.estimates.set(0,estimate(O,R,Map.of(A,d("3.2")),Duration.ofMinutes(30)));
    f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,Map.of(A,d("3.2")),Map.of(A,d("3")),Map.of(A,d("0")),null,Lane.AGED));
    f.usage.put(new LaneKey(A,Lane.AGED),d("3"));
    var selected=f.first();assertEquals(Lane.AGED,selected.lane());amount(".2",selected.incrementalDemand().get(A));
  }
  @Test void snapshotCannotHideUsageAlreadyAttributedToAnAgedReservation() {
    var f=new Fixture();f.accounts.set(0,account(A,R,"WEEKLY",d("100"),d("3"),d("0")));
    f.reservations.add(new Reservation(id(9),O,R,Pool.PLANNED,Map.of(A,d("10")),Map.of(A,d("3")),Map.of(A,d("0")),null,Lane.AGED));
    assertEquals(Status.INVALID_INPUT,f.run().status());
  }
  @Test void positiveOverrideAloneCannotUnpauseP4() {
    var f=new Fixture();f.projects.set(0,new Project(P,ProjectState.ACTIVE,4,d("8"),true));
    has(f.first(),Reason.P4_PAUSED);
  }
  @Test void exactScoresDoNotCollapseCloseRationalValues() {
    var a=Rational.of(d("1")).divide(Rational.of(d("3")));
    var b=Rational.of(d("0.33333333333333333333333333333333333333333333333333"));
    assertTrue(a.compareTo(b)>0);assertEquals(Rational.of(d("1")),a.add(a).add(a));
  }
}
