-- SPDX-License-Identifier: GPL-3.0-only
-- Read-only local retirement admission, not a domain transition or capacity release.
CREATE FUNCTION d4.worker_execution_status(wid uuid,delivery uuid) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb;safe boolean;
BEGIN
 PERFORM d3.lock_state();PERFORM d4.require_worker(wid);
 IF wid IS NULL OR delivery IS NULL OR NOT EXISTS(SELECT 1 FROM d4.deliveries WHERE id=delivery AND worker_id=wid)
 THEN RAISE EXCEPTION 'Execution status ownership mismatch' USING ERRCODE='42501';END IF;
 info=d4.lab_inspect(delivery);
 SELECT op.state='COMPLETED' AND a.state='COMPLETED' AND op.lease_generation=(info->>'generation')::bigint
  AND NOT EXISTS(SELECT 1 FROM public.operation_leases WHERE operation_id=op.id)
  AND NOT EXISTS(SELECT 1 FROM d2.reservations r JOIN d2.reservation_balances b ON b.reservation_id=r.id WHERE r.operation_id=op.id AND b.outstanding<>0)
  AND EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=a.id AND evidence_type='ACCEPTANCE_PASS')
  AND NOT EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=a.id AND evidence_type='ACCEPTANCE_FAIL')
  AND NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND status='UNKNOWN')
  AND NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id GROUP BY generation,effect_key HAVING count(DISTINCT status)>1)
  AND (EXISTS(SELECT 1 FROM d4.lab_evidence e WHERE e.delivery_id=delivery AND e.acceptance AND e.effect_status='APPLIED'
    AND e.proof->'process_stopped'='true'::jsonb AND e.proof->'receiver_closed'='true'::jsonb AND e.proof->'artifact_valid'='true'::jsonb)
   OR EXISTS(SELECT 1 FROM d4.checkpoint_commands c WHERE c.request->>'action'='ACCEPT_CONTINUATION' AND c.request->>'delivery'=delivery::text
    AND c.request->'proof'->'process_stopped'='true'::jsonb AND c.request->'proof'->'receiver_closed'='true'::jsonb
    AND c.request->'proof'->>'attempt'=a.id::text AND c.request->'proof'->>'generation'=info->>'generation'))
 INTO safe FROM public.operations op JOIN public.execution_attempts a ON a.id=(info->>'attempt')::uuid WHERE op.id=(info->>'operation')::uuid;
 RETURN jsonb_build_object('schema','d4.worker.execution-status.v1','delivery_id',delivery,'operation',info->'operation',
  'attempt',info->'attempt','worker',info->'worker','resource',info->'resource','generation',info->'generation',
  'state',info->'state','retirable',coalesce(safe,false));
END $$;
REVOKE ALL ON FUNCTION d4.worker_execution_status(uuid,uuid) FROM PUBLIC;
