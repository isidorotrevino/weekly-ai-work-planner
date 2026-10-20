-- SPDX-License-Identifier: GPL-3.0-only
-- Review correction: critical reopening uses STATE_CHANGED in D2, not always REPLAN_REQUIRED.
-- Preserve V1-V14 and the historical evidence. No deployment grants.
CREATE OR REPLACE FUNCTION d3.planning_event_kind(e public.outbox_events) RETURNS text LANGUAGE sql STABLE AS $$
  SELECT CASE
    WHEN e.event_type='STATE_CHANGED' AND e.aggregate_type='INCIDENT' AND e.payload->>'to'='REOPENED'
      AND EXISTS(SELECT 1 FROM public.incidents i WHERE i.id=e.aggregate_id AND i.status<>'RESOLVED' AND i.severity IN ('SEV1','SEV2')) THEN 'INCIDENT_CRITICAL'
    WHEN e.event_type='REPLAN_REQUIRED' AND e.aggregate_type='INCIDENT' AND e.payload->>'severity' IN ('SEV1','SEV2') THEN 'INCIDENT_CRITICAL'
    WHEN e.event_type='DEPENDENCY_INVALIDATED' OR (e.event_type='STATE_CHANGED' AND e.aggregate_type='CAPABILITY_VERSION' AND e.payload->>'to'='INVALIDATED') THEN 'DEPENDENCY_INVALIDATED'
    WHEN e.event_type='STATE_CHANGED' AND e.aggregate_type='OPERATION' AND e.payload->>'to'='RECONCILING' THEN 'WORKER_LOST'
    WHEN e.event_type='STATE_CHANGED' AND e.aggregate_type='OPERATION' AND e.payload->>'to'='BLOCKED_APPROVAL' THEN 'APPROVAL_INVALID'
    WHEN e.event_type IN ('RECALIBRATED','CONSUME','ADJUST','BORROW','RETURN','RESERVE','TOP_UP','RELEASE')
      AND EXISTS(SELECT 1 FROM d2.balances b WHERE b.available<0 AND
        (b.account_id=e.aggregate_id OR EXISTS(SELECT 1 FROM d2.reservation_balances rb WHERE rb.account_id=b.account_id AND rb.reservation_id::text=e.payload->>'reservation_id')
          OR EXISTS(SELECT 1 FROM d2.loans l WHERE l.account_id=b.account_id AND l.id::text=e.payload->>'loan_id'))) THEN 'CAPACITY_DEFICIT'
    WHEN e.event_type IN ('RECALIBRATED','RESERVE','TOP_UP','RELEASE','CONSUME','ADJUST','BORROW','RETURN') THEN 'CAPACITY_CHANGED'
    WHEN e.event_type='STATE_CHANGED' AND e.aggregate_type IN ('TASK','CAPABILITY_VERSION') THEN 'DEPENDENCY_CHANGED'
    WHEN e.event_type='STATE_CHANGED' AND e.aggregate_type='INCIDENT' THEN 'INCIDENT_CHANGED'
    WHEN e.event_type IN ('STATE_CHANGED','D3_REPLAN_REQUESTED','PREEMPTION_RESULT') THEN 'ORDINARY'
    ELSE NULL END;
$$;
REVOKE ALL ON FUNCTION d3.planning_event_kind(public.outbox_events) FROM PUBLIC;
-- Old inbox facts are immutable. If V14 already queued a critical reopening
-- with ordinary delay, append an explicit correction event to that same open
-- request; do not rely on re-reading an already receipted outbox row.
DO $$ DECLARE old_event record;BEGIN
  PERFORM d3.coordinator_lock();
  FOR old_event IN
    SELECT e.id FROM d3.planning_events e JOIN d3.planning_requests r ON r.id=e.request_id
      JOIN public.incidents i ON i.id::text=e.content->>'aggregate_id'
    WHERE r.state IN ('QUEUED','RUNNING') AND e.kind='INCIDENT_CHANGED'
      AND e.content->'payload'->>'to'='REOPENED' AND i.status<>'RESOLVED' AND i.severity IN ('SEV1','SEV2')
    ORDER BY e.id
  LOOP
    PERFORM d3.enqueue_internal(public.gen_random_uuid(),'INCIDENT_CRITICAL',clock_timestamp(),
      jsonb_build_object('action','V15_REOPENING_CORRECTION','original_event_id',old_event.id));
  END LOOP;
END $$;
