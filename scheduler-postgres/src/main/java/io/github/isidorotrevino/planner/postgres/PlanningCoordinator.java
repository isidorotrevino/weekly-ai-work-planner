// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import java.sql.*;
import java.time.Instant;
import java.util.*;
import io.github.isidorotrevino.planner.scheduler.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;

/** One explicit tick, no background threads, worker execution or external calls. */
public final class PlanningCoordinator {
  public enum State { IDLE, PUBLISHED, STALE, BLOCKED }
  public record Lease(UUID requestId,UUID workerId,long generation) { }
  public record Attempt(Lease lease,int number,UUID captureId,UUID planId,boolean breakProtection,State completed) { }
  public record Outcome(State state,UUID requestId,UUID planId,int recalculations) { }
  @FunctionalInterface interface Calculation { Result plan(Request request,Snapshot snapshot) throws SQLException; }
  private final Calculation calculation;
  private final PlanningStore store=new PlanningStore();
  public PlanningCoordinator(){this(new CapacityScheduler()::plan);}
  PlanningCoordinator(Calculation calculation){this.calculation=Objects.requireNonNull(calculation);}
  private static void autonomous(Connection c) throws SQLException {
    if(!c.getAutoCommit() || c.getTransactionIsolation()!=Connection.TRANSACTION_READ_COMMITTED)
      throw new SQLException("Coordinator needs autocommit READ COMMITTED; no SQL transaction may span calculation","25001");
  }
  private static Map<String,Object> identity(Lease lease) {
    var req=new LinkedHashMap<String,Object>();req.put("request_id",lease.requestId());req.put("worker_id",lease.workerId());req.put("generation",lease.generation());return req;
  }
  public UUID enqueue(Connection c,UUID commandId,UUID eventId,ReplanPolicy.Kind kind,Instant occurredAt,Map<String,?> content) throws SQLException {
    autonomous(c);
    try(var p=c.prepareStatement("SELECT (d3.enqueue_planning(?,?::jsonb)->>'request_id')::uuid")) {
      p.setObject(1,commandId);p.setString(2,Json.write(Map.of("action","ENQUEUE","event_id",eventId,"kind",kind,"occurred_at",occurredAt,"content",content)));
      try(var rs=p.executeQuery()){rs.next();return rs.getObject(1,UUID.class);}
    }
  }
  public String poll(Connection c,UUID commandId) throws SQLException {
    autonomous(c);try(var p=c.prepareStatement("SELECT d3.poll_planning(?)::text")) {
      p.setObject(1,commandId);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}
    }
  }
  public Optional<Lease> take(Connection c,UUID commandId,UUID workerId) throws SQLException {
    autonomous(c);try(var p=c.prepareStatement("""
      WITH response AS MATERIALIZED (SELECT d3.take_planning(?,?::jsonb) j)
      SELECT (j->>'request_id')::uuid request,(j->>'worker_id')::uuid worker,(j->>'generation')::bigint generation FROM response
      """)) {
      p.setObject(1,commandId);p.setString(2,Json.write(Map.of("action","TAKE","worker_id",workerId)));
      try(var rs=p.executeQuery()){rs.next();var id=rs.getObject("request",UUID.class);return id==null?Optional.empty():Optional.of(new Lease(id,rs.getObject("worker",UUID.class),rs.getLong("generation")));}
    }
  }
  public Attempt prepare(Connection c,Lease lease) throws SQLException {
    autonomous(c);try(var p=c.prepareStatement("""
      WITH response AS MATERIALIZED (SELECT d3.prepare_planning(?::jsonb) j)
      SELECT (j->>'attempt_no')::integer number,(j->>'capture_id')::uuid capture,(j->>'plan_id')::uuid plan,
        (j->>'break_protection')::boolean protection,j->>'request_state' state FROM response
      """)) {
      p.setString(1,Json.write(identity(lease)));try(var rs=p.executeQuery()) {
        rs.next();return new Attempt(lease,rs.getInt("number"),rs.getObject("capture",UUID.class),rs.getObject("plan",UUID.class),rs.getBoolean("protection"),rs.getString("state").equals("RUNNING")?null:State.valueOf(rs.getString("state")));
      }
    }
  }
  public UUID publish(Connection c,Attempt attempt,Result result) throws SQLException {
    autonomous(c);var req=identity(attempt.lease());req.put("attempt_no",attempt.number());req.put("result",result);
    try(var p=c.prepareStatement("SELECT (d3.publish_planning(?::jsonb)->>'plan_id')::uuid")) {
      p.setString(1,Json.write(req));try(var rs=p.executeQuery()){rs.next();return rs.getObject(1,UUID.class);}
    }
  }
  String fail(Connection c,Attempt attempt,String code) throws SQLException {
    autonomous(c);var req=identity(attempt.lease());req.put("attempt_no",attempt.number());req.put("failure_code",code);
    try(var p=c.prepareStatement("SELECT d3.fail_planning(?::jsonb)->>'state'")) {
      p.setString(1,Json.write(req));try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}
    }
  }
  public String read(Connection c,UUID requestId) throws SQLException {
    autonomous(c);try(var p=c.prepareStatement("SELECT d3.read_planning_request(?)::text")) {
      p.setObject(1,requestId);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}
    }
  }
  /** At most initial calculation plus two recalculations. Ambiguous SQL failures
   * propagate: replaying the persisted command/attempt resolves committed work. */
  public Outcome runOnce(Connection c,UUID takeCommandId,UUID workerId) throws SQLException {
    var lease=take(c,takeCommandId,workerId);
    if(lease.isEmpty())return new Outcome(State.IDLE,null,null,0);
    for(;;) {
      var attempt=prepare(c,lease.get());
      if(attempt.completed()!=null)return new Outcome(attempt.completed(),attempt.lease().requestId(),attempt.completed()==State.PUBLISHED?attempt.planId():null,attempt.number());
      var captured=store.read(c,attempt.captureId());var original=captured.request();
      var request=new Request(original.schemaVersion(),original.asOf(),original.timezone(),original.policyHash(),original.calibrationEpoch(),original.limits(),attempt.breakProtection());
      var result=calculation.plan(request,captured.snapshot());
      String failed;
      if(result.status()!=Status.COMPLETE && result.status()!=Status.PARTIAL) failed=fail(c,attempt,"INVALID_RESULT");
      else {
        try {
          var plan=publish(c,attempt,result);return new Outcome(State.PUBLISHED,attempt.lease().requestId(),plan,attempt.number());
        } catch(SQLException error) {
          if(!"40001".equals(error.getSQLState()) && !"23514".equals(error.getSQLState()))throw error;
          failed=fail(c,attempt,error.getSQLState());
        }
      }
      if(!failed.equals("RETRY"))return new Outcome(State.valueOf(failed),attempt.lease().requestId(),null,attempt.number());
    }
  }
  /** Poll is bounded (100 source events), then one durable request is processed. */
  public Outcome tick(Connection c,UUID pollCommandId,UUID takeCommandId,UUID workerId) throws SQLException {
    poll(c,pollCommandId);return runOnce(c,takeCommandId,workerId);
  }
}
