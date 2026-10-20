-- SPDX-License-Identifier: GPL-3.0-only
-- Read-only worker signal. No new domain transition or worker evidence authority.
CREATE FUNCTION d4.worker_checkpoint_signal(wid uuid,delivery uuid) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb;rid uuid;
BEGIN
 PERFORM d3.lock_state();PERFORM d4.require_worker(wid);
 IF wid IS NULL OR delivery IS NULL OR NOT EXISTS(SELECT 1 FROM d4.deliveries WHERE id=delivery AND worker_id=wid)
 THEN RAISE EXCEPTION 'Checkpoint signal ownership mismatch' USING ERRCODE='42501';END IF;
 info=d4.i5_inspect(delivery);
 IF info->>'state'<>'RUNNING' OR coalesce((info->>'lease_expired')::boolean,true)
  OR NOT EXISTS(SELECT 1 FROM public.operation_leases WHERE attempt_id=(info->>'attempt')::uuid AND worker_id=wid AND fencing_generation=(info->>'generation')::bigint)
 THEN RAISE EXCEPTION 'Live current execution required' USING ERRCODE='23514';END IF;
 SELECT r.id INTO rid FROM d4.checkpoint_requests r WHERE r.delivery_id=delivery
  AND r.attempt_id=(info->>'attempt')::uuid AND r.generation=(info->>'generation')::bigint
  AND r.expected_version=(info->>'row_version')::bigint ORDER BY r.id LIMIT 1;
 RETURN jsonb_build_object('request_id',rid,'operation',info->'operation','attempt',info->'attempt',
  'worker',info->'worker','resource',info->'resource','generation',info->'generation');
END $$;
REVOKE ALL ON FUNCTION d4.worker_checkpoint_signal(uuid,uuid) FROM PUBLIC;
