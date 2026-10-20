// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import java.sql.*;
import java.util.*;

/** Control-plane boundary only: authenticating workers belongs to the transport. */
public final class DispatchStore {
  public record Claimed(UUID planId,UUID operationId,UUID attemptId,UUID reservationId,
                        UUID workerId,UUID resourceId,long generation) { }
  private static void autonomous(Connection c) throws SQLException {
    if(!c.getAutoCommit() || c.getTransactionIsolation()!=Connection.TRANSACTION_READ_COMMITTED)
      throw new SQLException("Use an autocommit READ COMMITTED control-plane connection","25001");
  }
  public Claimed claim(Connection c,UUID commandId,UUID planId,UUID operationId,UUID resourceId,UUID workerId) throws SQLException {
    autonomous(c);
    var request=Map.of("action","CLAIM","plan_id",planId,"operation_id",operationId,"resource_id",resourceId,"worker_id",workerId);
    try(var p=c.prepareStatement("""
      WITH response AS MATERIALIZED (SELECT d3.dispatch(?,?::jsonb) j)
      SELECT (j->>'attempt_id')::uuid attempt,(j->>'reservation_id')::uuid reservation,(j->>'generation')::bigint generation FROM response
      """)) {
      p.setObject(1,commandId);p.setString(2,Json.write(request));try(var rs=p.executeQuery()) {
        rs.next();return new Claimed(planId,operationId,rs.getObject("attempt",UUID.class),rs.getObject("reservation",UUID.class),workerId,resourceId,rs.getLong("generation"));
      }
    }
  }
  public String execute(Connection c,UUID commandId,Claimed claim,String action,Map<String,?> payload) throws SQLException {
    autonomous(c);
    var req=new LinkedHashMap<String,Object>(payload);
    for(var reserved:List.of("action","operation_id","attempt_id","generation","resource_id","worker_id"))
      if(req.containsKey(reserved))throw new IllegalArgumentException("Payload cannot override execution identity: "+reserved);
    req.put("action",action);req.put("operation_id",claim.operationId());req.put("attempt_id",claim.attemptId());req.put("generation",claim.generation());req.put("worker_id",claim.workerId());req.put("resource_id",claim.resourceId());
    try(var p=c.prepareStatement("SELECT d3.execution(?,?::jsonb)::text")) {
      p.setObject(1,commandId);p.setString(2,Json.write(req));try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}
    }
  }
}
