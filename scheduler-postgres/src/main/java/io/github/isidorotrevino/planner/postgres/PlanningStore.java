// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import java.math.*;
import java.sql.*;
import java.time.*;
import java.util.*;
import io.github.isidorotrevino.planner.scheduler.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;

/** JDBC boundary. Every read comes from an immutable capture; calculation holds no SQL locks. */
public final class PlanningStore {
  public record Captured(UUID id,String basisHash,UUID currentPlanId,UUID fairnessEpoch,String epochReason,Request request,Snapshot snapshot) { }
  private interface Row<T> {T map(ResultSet rs) throws SQLException;}
  private static final String PREFIX="WITH document AS (SELECT d3.read_capture(?) doc), snapshot AS (SELECT doc->'body' b,(doc->>'captured_at')::timestamptz observed_at FROM document) ";
  private static UUID uuid(ResultSet rs,String col) throws SQLException {return rs.getObject(col,UUID.class);}
  private static Instant instant(ResultSet rs,String col) throws SQLException {var v=rs.getObject(col,OffsetDateTime.class);return v==null?null:v.toInstant();}
  private static Set<String> strings(ResultSet rs,String col) throws SQLException {
    var a=rs.getArray(col);if(a==null)return Set.of();try{return Set.copyOf(Arrays.asList((String[])a.getArray()));}finally{a.free();}
  }
  private static Duration seconds(BigDecimal seconds) {
    var parts=seconds.divideAndRemainder(BigDecimal.ONE);
    return Duration.ofSeconds(parts[0].longValueExact(),parts[1].movePointRight(9).longValueExact());
  }
  private static void autonomous(Connection c) throws SQLException {
    if(!c.getAutoCommit() || c.getTransactionIsolation()!=Connection.TRANSACTION_READ_COMMITTED)
      throw new SQLException("Use an autocommit READ COMMITTED connection; calculation must hold no SQL locks","25001");
  }
  public String configure(Connection admin,UUID commandId,Map<String,?> request) throws SQLException {
    autonomous(admin);return command(admin,"configure",commandId,Json.write(request));
  }
  public Captured capture(Connection c,UUID commandId) throws SQLException {
    autonomous(c);command(c,"capture",commandId,"{\"action\":\"CAPTURE\"}");return read(c,commandId);
  }
  public UUID publish(Connection c,UUID commandId,UUID planId,Captured capture,Result result) throws SQLException {
    autonomous(c);
    if(result.status()!=Status.COMPLETE && result.status()!=Status.PARTIAL) throw new IllegalArgumentException("No incomplete/invalid result may be published");
    var req=new LinkedHashMap<String,Object>();req.put("action","PUBLISH");req.put("plan_id",planId);req.put("capture_id",capture.id());
    req.put("expected_current_plan_id",capture.currentPlanId());req.put("result",result);
    command(c,"publish",commandId,Json.write(req));return planId;
  }
  public String observeEligibility(Connection c,UUID commandId) throws SQLException {
    autonomous(c);try(var p=c.prepareStatement("SELECT d3.observe_eligibility(?)::text")){p.setObject(1,commandId);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}}
  }
  private static String command(Connection c,String fn,UUID id,String json) throws SQLException {
    // Function identifiers are private compile-time constants, never request input.
    try(var p=c.prepareStatement("SELECT d3."+fn+"(?,?::jsonb)::text")) {
      p.setObject(1,id);p.setString(2,json);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}
    }
  }
  private static <T> List<T> rows(Connection c,UUID id,String query,Row<T> mapper) throws SQLException {
    var result=new ArrayList<T>();
    try(var p=c.prepareStatement(PREFIX+query)){p.setObject(1,id);try(var rs=p.executeQuery()){while(rs.next())result.add(mapper.map(rs));}}
    return List.copyOf(result);
  }
  private record Meta(Instant asOf,String hash,UUID current,UUID epoch,String reason,String policyHash,String calibration,String schema,String zone,Limits limits) { }
  public Captured read(Connection c,UUID id) throws SQLException {
    autonomous(c);
    var metadata=rows(c,id,"""
      SELECT observed_at,doc->>'basis_hash' hash,(b->'d3.plan_head'->0->>'planning_run_id')::uuid current_plan,
        (b->'d3.settings'->0->>'fairness_epoch')::uuid epoch,b->'d3.settings'->0->>'calibration_epoch' calibration,
        e->>'reason' reason,encode(public.digest((b->'d3.settings'->0->'policy')::text,'sha256'),'hex') policy_hash,
        b->'d3.settings'->0->'policy'->>'schema_version' schema,b->'d3.settings'->0->'policy'->>'timezone' zone,
        (b->'d3.settings'->0->'policy'->>'max_operations')::int max_operations,
        (b->'d3.settings'->0->'policy'->>'max_edges')::int max_edges,
        (b->'d3.settings'->0->'policy'->>'max_candidates')::int max_candidates,
        (b->'d3.settings'->0->'policy'->>'max_compute_ms')::bigint max_compute_ms
      FROM snapshot,document,LATERAL jsonb_array_elements(b->'d3.fairness_epochs') e
      WHERE e->>'id'=b->'d3.settings'->0->>'fairness_epoch'
      """,rs->new Meta(instant(rs,"observed_at"),rs.getString("hash"),uuid(rs,"current_plan"),uuid(rs,"epoch"),rs.getString("reason"),rs.getString("policy_hash"),rs.getString("calibration"),rs.getString("schema"),rs.getString("zone"),new Limits(rs.getInt("max_operations"),rs.getInt("max_edges"),rs.getInt("max_candidates"),Duration.ofMillis(rs.getLong("max_compute_ms")))));
    if(metadata.size()!=1)throw new SQLException("Unknown capture or missing planning profile","02000");
    var meta=metadata.getFirst();
    var projects=rows(c,id,"""
      SELECT (x->>'id')::uuid id,x->>'status' status,x->>'priority' priority,(x->>'priority_weight_override')::numeric weight,(x->>'deferral_allowed')::boolean deferral
      FROM snapshot,LATERAL jsonb_array_elements(b->'public.projects') x ORDER BY x->>'id'
      """,rs->new Project(uuid(rs,"id"),ProjectState.valueOf(rs.getString("status")),Integer.parseInt(rs.getString("priority").substring(1)),rs.getBigDecimal("weight"),rs.getBoolean("deferral")));
    var tasks=rows(c,id,"""
      SELECT (x->>'id')::uuid id,(x->>'project_id')::uuid project,x->>'status' status,(x->>'deadline_at')::timestamptz deadline
      FROM snapshot,LATERAL jsonb_array_elements(b->'public.tasks') x ORDER BY x->>'id'
      """,rs->new Task(uuid(rs,"id"),uuid(rs,"project"),Set.of("DONE","CANCELLED","FAILED").contains(rs.getString("status")),instant(rs,"deadline")));
    record Calendar(UUID resource,Interval slot) { }
    var calendars=rows(c,id,"""
      SELECT (h->>'resource_id')::uuid resource,(s->>'start')::timestamptz start_at,(s->>'end')::timestamptz end_at
      FROM snapshot,LATERAL jsonb_array_elements(b->'d3.calendar_heads') h
      JOIN LATERAL jsonb_array_elements(b->'d3.calendars') cal ON cal->>'id'=h->>'calendar_id'
      CROSS JOIN LATERAL jsonb_array_elements(cal->'slots') s ORDER BY h->>'resource_id',s->>'start',s->>'end'
      """,rs->new Calendar(uuid(rs,"resource"),new Interval(instant(rs,"start_at"),instant(rs,"end_at"))));
    var byResource=new HashMap<UUID,List<Interval>>();calendars.forEach(cal->byResource.computeIfAbsent(cal.resource(),key->new ArrayList<>()).add(cal.slot()));
    var resources=rows(c,id,"""
      SELECT (r->>'id')::uuid id,coalesce(r->>'worker_id',r->>'id')::uuid worker,(r->>'enabled')::boolean enabled,
        coalesce(w->>'state','OFFLINE') state,(w->>'last_heartbeat_at')::timestamptz heartbeat,
        ARRAY(SELECT 'op:'||(v->>'operation_id') FROM jsonb_array_elements(b->'resource_compatibility') v WHERE v->>'resource_id'=r->>'id' ORDER BY v->>'operation_id') caps
      FROM snapshot,LATERAL jsonb_array_elements(b->'public.resources') r
      LEFT JOIN LATERAL jsonb_array_elements(b->'public.workers') w ON w->>'id'=r->>'worker_id' ORDER BY r->>'id'
      """,rs->new Resource(uuid(rs,"id"),uuid(rs,"worker"),rs.getBoolean("enabled"),"ONLINE".equals(rs.getString("state")),instant(rs,"heartbeat"),strings(rs,"caps"),byResource.getOrDefault(uuid(rs,"id"),List.of())));
    record Physical(UUID account,Pool pool,Balance balance) { }
    var physical=rows(c,id,"""
      SELECT (v->>'account_id')::uuid id,v->>'pool' pool,(v->>'effective_limit')::numeric effective_limit,(v->>'outstanding')::numeric outstanding,(v->>'consumed')::numeric consumed
      FROM snapshot,LATERAL jsonb_array_elements(b->'balances') v
      """,rs->new Physical(uuid(rs,"id"),Pool.valueOf(rs.getString("pool")),new Balance(rs.getBigDecimal("effective_limit"),rs.getBigDecimal("outstanding"),rs.getBigDecimal("consumed"))));
    var balances=new HashMap<UUID,Map<Pool,Balance>>();physical.forEach(p->balances.computeIfAbsent(p.account(),key->new EnumMap<>(Pool.class)).put(p.pool(),p.balance()));
    var accounts=rows(c,id,"""
      SELECT (a->>'id')::uuid id,(a->>'resource_id')::uuid resource,a->>'dimension' dimension,a->>'unit' unit,a->>'window_kind' kind,a->>'window_key' key,
        (a->>'window_start')::timestamptz start_at,(a->>'window_end')::timestamptz end_at,
        coalesce((l->>'capacity')::numeric,(a->>'initial_capacity')::numeric)*0.7 base,
        coalesce((l->>'confidence')::numeric,(a->>'confidence')::numeric) confidence
      FROM snapshot,LATERAL jsonb_array_elements(b->'d2.accounts') a LEFT JOIN LATERAL (
        SELECT v FROM jsonb_array_elements(b->'d2.capacity_limits') v WHERE v->>'account_id'=a->>'id' ORDER BY (v->>'id')::bigint DESC LIMIT 1
      ) latest(l) ON true ORDER BY a->>'id'
      """,rs->new Account(uuid(rs,"id"),uuid(rs,"resource"),rs.getString("dimension"),rs.getString("unit"),rs.getString("kind"),rs.getString("key"),new Interval(instant(rs,"start_at"),instant(rs,"end_at")),rs.getBigDecimal("base"),rs.getBigDecimal("confidence"),balances.get(uuid(rs,"id"))));
    record Vector(UUID owner,UUID account,BigDecimal units) { }
    var estimateVectors=rows(c,id,"""
      SELECT (e->>'id')::uuid owner,u.key::uuid account,u.value::text::numeric units FROM snapshot,LATERAL jsonb_array_elements(b->'d3.estimates') e CROSS JOIN LATERAL jsonb_each(e->'units') u
      """,rs->new Vector(uuid(rs,"owner"),uuid(rs,"account"),rs.getBigDecimal("units")));
    var vectors=new HashMap<UUID,Map<UUID,BigDecimal>>();estimateVectors.forEach(v->vectors.computeIfAbsent(v.owner(),key->new HashMap<>()).put(v.account(),v.units()));
    var estimates=rows(c,id,"""
      SELECT (e->>'id')::uuid id,(e->>'operation_id')::uuid operation,(e->>'resource_id')::uuid resource,
        (e->>'duration_ms')::bigint duration,(e->>'confidence')::numeric confidence,e->>'calibration_ref' calibration,e->>'provenance' provenance,
        (e->>'observed_at')::timestamptz observed,(e->>'valid_until')::timestamptz valid
      FROM snapshot,LATERAL jsonb_array_elements(b->'d3.estimate_heads') h JOIN LATERAL jsonb_array_elements(b->'d3.estimates') e ON e->>'id'=h->>'estimate_id' ORDER BY e->>'operation_id',e->>'resource_id'
      """,rs->new Estimate(uuid(rs,"operation"),uuid(rs,"resource"),vectors.get(uuid(rs,"id")),Duration.ofMillis(rs.getLong("duration")),rs.getBigDecimal("confidence"),rs.getString("calibration"),rs.getString("provenance"),instant(rs,"observed"),instant(rs,"valid")));
    var operations=rows(c,id,"""
      SELECT (o->>'id')::uuid id,(o->>'task_id')::uuid task,o->>'state' state,coalesce((g->>'eligible')::boolean,false) eligible,
        (SELECT count(*) FROM jsonb_array_elements(b->'public.execution_attempts') a WHERE a->>'operation_id'=o->>'id') attempts,
        coalesce((o->'policy_snapshot'->>'max_attempts')::int,3) max_attempts,
        EXISTS(SELECT 1 FROM jsonb_array_elements(b->'d2.effect_receipts') er WHERE er->>'operation_id'=o->>'id' AND er->>'generation'=o->>'lease_generation' AND er->>'status'='ABSENT') AND NOT EXISTS(SELECT 1 FROM jsonb_array_elements(b->'d2.effect_receipts') er WHERE er->>'operation_id'=o->>'id' AND er->>'generation'=o->>'lease_generation' AND er->>'status'<>'ABSENT') retry_safe,
        coalesce(o->>'context_pack_sha256','') ~ '^[a-f0-9]{64}$' AND nullif(o->>'context_pack_ref','') IS NOT NULL context_ready,
        coalesce((o->'policy_snapshot'->>'requires_approval')::boolean,false) approval_required,
        (SELECT max((a->>'expires_at')::timestamptz) FROM jsonb_array_elements(b->'public.approvals') a WHERE a->>'operation_id'=o->>'id' AND a->>'state'='APPROVED'
          AND a->>'context_snapshot_sha256'=o->>'context_pack_sha256' AND a->>'policy_snapshot_sha256'=encode(public.digest((o->'policy_snapshot')::text,'sha256'),'hex')) approval_until,
        coalesce((SELECT sum(greatest(extract(epoch FROM least(coalesce((i->>'end_at')::timestamptz,observed_at),observed_at)-(i->>'observed_at')::timestamptz),0))
          FROM jsonb_array_elements(b->'eligible_intervals') i WHERE i->>'operation_id'=o->>'id' AND (i->>'eligible')::boolean),0) wait_seconds,
        NOT EXISTS(SELECT 1 FROM jsonb_array_elements(b->'public.task_dependencies') dep JOIN LATERAL jsonb_array_elements(b->'public.tasks') pred ON pred->>'id'=dep->>'predecessor_task_id'
          WHERE dep->>'successor_task_id'=o->>'task_id' AND dep->>'kind'='SOFT' AND pred->>'status'<>'DONE') soft_satisfied,
        (t->>'urgency')::int urgency,(o->>'created_at')::timestamptz created,
        (prev->>'resource_id')::uuid previous_resource,(prev->>'planned_start')::timestamptz previous_start,
        ARRAY(SELECT jsonb_array_elements_text(coalesce(o->'policy_snapshot'->'exclusive_keys','[]'))) exclusive_keys,
        (inc->>'incident_id')::uuid incident,coalesce(inc->>'role'='FOLLOW_UP',false) follow_up,
        coalesce((o->'policy_snapshot'->>'integration_phase')::boolean,false) integration_phase,coalesce((g->>'integration')::boolean,false) real_integration
      FROM snapshot,LATERAL jsonb_array_elements(b->'public.operations') o
      JOIN LATERAL jsonb_array_elements(b->'public.tasks') t ON t->>'id'=o->>'task_id'
      LEFT JOIN LATERAL jsonb_array_elements(b->'task_guards') g ON g->>'task_id'=o->>'task_id'
      LEFT JOIN LATERAL (SELECT v FROM jsonb_array_elements(b->'public.schedule_entries') v WHERE v->>'operation_id'=o->>'id' AND v->>'planning_run_id'=b->'d3.plan_head'->0->>'planning_run_id' ORDER BY v->>'planned_start',v->>'id' LIMIT 1) p(prev) ON true
      LEFT JOIN LATERAL (SELECT l FROM jsonb_array_elements(b->'public.incident_task_links') l JOIN LATERAL jsonb_array_elements(b->'public.incidents') i ON i->>'id'=l->>'incident_id'
        WHERE l->>'task_id'=o->>'task_id' AND i->>'status'<>'RESOLVED' ORDER BY (l->>'role'='FOLLOW_UP'),i->>'severity',i->>'detected_at',i->>'id' LIMIT 1) selected(inc) ON true ORDER BY o->>'id'
      """,rs->{var eligible=rs.getBoolean("eligible");return new Operation(uuid(rs,"id"),uuid(rs,"task"),State.valueOf(rs.getString("state")),eligible?Eligibility.ELIGIBLE:Eligibility.BLOCKED,
        eligible?List.of():List.of(Reason.UNRESOLVED_BLOCKER),rs.getInt("attempts"),rs.getInt("max_attempts"),rs.getInt("attempts")==0||rs.getBoolean("retry_safe"),rs.getBoolean("context_ready"),rs.getBoolean("approval_required"),instant(rs,"approval_until"),Set.of("op:"+uuid(rs,"id")),seconds(rs.getBigDecimal("wait_seconds")),rs.getBoolean("soft_satisfied"),rs.getInt("urgency"),instant(rs,"created"),uuid(rs,"previous_resource"),instant(rs,"previous_start"),strings(rs,"exclusive_keys"),uuid(rs,"incident"),rs.getBoolean("follow_up"),rs.getBoolean("integration_phase"),rs.getBoolean("real_integration"));});
    var mapping=rows(c,id,"""
      SELECT (m->>'operation_id')::uuid owner,(m->>'account_id')::uuid account,(m->>'units')::numeric units FROM snapshot,LATERAL jsonb_array_elements(b->'d2.operation_accounts') m
      """,rs->new Vector(uuid(rs,"owner"),uuid(rs,"account"),rs.getBigDecimal("units")));
    var mappings=new HashMap<UUID,Map<UUID,BigDecimal>>();mapping.forEach(v->mappings.computeIfAbsent(v.owner(),key->new HashMap<>()).put(v.account(),v.units()));
    record ReservationBalance(UUID reservation,UUID account,BigDecimal outstanding,BigDecimal consumed) { }
    var reservationBalances=rows(c,id,"""
      SELECT (v->>'reservation_id')::uuid reservation,(v->>'account_id')::uuid account,(v->>'outstanding')::numeric outstanding,(v->>'consumed')::numeric consumed FROM snapshot,LATERAL jsonb_array_elements(b->'reservation_balances') v
      """,rs->new ReservationBalance(uuid(rs,"reservation"),uuid(rs,"account"),rs.getBigDecimal("outstanding"),rs.getBigDecimal("consumed")));
    var outstanding=new HashMap<UUID,Map<UUID,BigDecimal>>();var consumed=new HashMap<UUID,Map<UUID,BigDecimal>>();
    reservationBalances.forEach(v->{outstanding.computeIfAbsent(v.reservation(),key->new HashMap<>()).put(v.account(),v.outstanding());consumed.computeIfAbsent(v.reservation(),key->new HashMap<>()).put(v.account(),v.consumed());});
    var reservations=rows(c,id,"""
      SELECT (v->>'id')::uuid id,(v->>'operation_id')::uuid operation,(v->>'resource_id')::uuid resource,v->>'pool' pool,coalesce(a->>'lane',CASE WHEN v->>'pool'='INCIDENT' THEN 'INCIDENT' ELSE 'WEIGHTED' END) lane
      FROM snapshot,LATERAL jsonb_array_elements(b->'d2.reservations') v LEFT JOIN LATERAL jsonb_array_elements(b->'d3.lane_attributions') a ON a->>'reservation_id'=v->>'id' ORDER BY v->>'id'
      """,rs->new Reservation(uuid(rs,"id"),uuid(rs,"operation"),uuid(rs,"resource"),Pool.valueOf(rs.getString("pool")),mappings.getOrDefault(uuid(rs,"operation"),Map.of()),outstanding.getOrDefault(uuid(rs,"id"),Map.of()),consumed.getOrDefault(uuid(rs,"id"),Map.of()),null,Lane.valueOf(rs.getString("lane"))));
    var incidents=rows(c,id,"""
      SELECT (i->>'id')::uuid id,i->>'severity' severity,(i->>'detected_at')::timestamptz detected,coalesce((cl->>'active_response')::boolean,false) active
      FROM snapshot,LATERAL jsonb_array_elements(b->'public.incidents') i LEFT JOIN LATERAL jsonb_array_elements(b->'d3.incident_classifications') cl ON cl->>'incident_id'=i->>'id' WHERE i->>'status'<>'RESOLVED'
      """,rs->new Incident(uuid(rs,"id"),Integer.parseInt(rs.getString("severity").substring(3)),instant(rs,"detected"),rs.getBoolean("active")));
    var edges=rows(c,id,"SELECT e->>'a' a,e->>'b' b FROM snapshot,LATERAL jsonb_array_elements(b->'blocking_edges') e ORDER BY e->>'a',e->>'b'",rs->new Edge(node(rs.getString("a")),node(rs.getString("b"))));
    record Usage(LaneKey key,BigDecimal units) { }
    var laneRows=rows(c,id,"SELECT (u->>'account_id')::uuid account,u->>'lane' lane,(u->>'units')::numeric units FROM snapshot,LATERAL jsonb_array_elements(b->'lane_usage') u",rs->new Usage(new LaneKey(uuid(rs,"account"),Lane.valueOf(rs.getString("lane"))),rs.getBigDecimal("units")));
    var usage=new HashMap<LaneKey,BigDecimal>();laneRows.forEach(v->usage.put(v.key(),v.units()));
    var horizonEnd=meta.asOf().atZone(ZoneId.of(meta.zone())).plusDays(7).toInstant();
    var occupied=rows(c,id,"""
      SELECT (l->>'worker_id')::uuid worker,ARRAY(SELECT jsonb_array_elements_text(coalesce(o->'policy_snapshot'->'exclusive_keys','[]'))) keys
      FROM snapshot,LATERAL jsonb_array_elements(b->'public.operation_leases') l JOIN LATERAL jsonb_array_elements(b->'public.operations') o ON o->>'id'=l->>'operation_id'
      WHERE o->>'state' IN ('LEASED','RUNNING','VERIFYING','RECONCILING','BLOCKED_APPROVAL')
      """,rs->new Occupancy(uuid(rs,"worker"),strings(rs,"keys"),new Interval(meta.asOf(),horizonEnd)));
    boolean historyComplete=rows(c,id,"""
      SELECT NOT EXISTS(SELECT 1 FROM jsonb_array_elements(b->'d2.reservations') r WHERE NOT EXISTS(SELECT 1 FROM jsonb_array_elements(b->'d3.lane_attributions') a WHERE a->>'reservation_id'=r->>'id')) complete FROM snapshot
      """,rs->rs.getBoolean("complete")).getFirst();
    var request=new Request(meta.schema(),meta.asOf(),ZoneId.of(meta.zone()),meta.policyHash(),meta.calibration(),meta.limits(),false);
    var snapshot=new Snapshot(projects,tasks,operations,resources,accounts,estimates,reservations,incidents,edges,usage,occupied,historyComplete);
    return new Captured(id,meta.hash(),meta.current(),meta.epoch(),meta.reason(),request,snapshot);
  }
  private static String node(String node) {return node.startsWith("cap:")?node:"task:"+node;}
}
