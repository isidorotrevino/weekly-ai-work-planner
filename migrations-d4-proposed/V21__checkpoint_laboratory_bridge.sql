-- SPDX-License-Identifier: GPL-3.0-only
-- Minimal synthetic bridge for the two-step checkpoint campaign.
CREATE FUNCTION d4.checkpoint_inspect(request_id uuid) RETURNS jsonb LANGUAGE sql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT to_jsonb(r)||jsonb_build_object('info',d4.lab_inspect(r.delivery_id),'manifest',i.manifest,'manifest_hash',i.manifest_hash)
 FROM d4.checkpoint_requests r JOIN d4.step_intents i ON i.operation_id=r.operation_id WHERE r.id=request_id;
$$;
CREATE FUNCTION d4.i5_inspect(delivery uuid) RETURNS jsonb LANGUAGE sql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT d4.lab_inspect(delivery)||jsonb_build_object('row_version',op.row_version)||
 CASE WHEN i.operation_id IS NULL THEN '{}'::jsonb ELSE jsonb_build_object('is_checkpoint_fixture',true,'manifest',i.manifest,'manifest_hash',i.manifest_hash,
 'allowed_steps',CASE WHEN l.attempt_id IS NULL THEN '["step-1","step-2"]'::jsonb ELSE '["step-2"]'::jsonb END,
 'incremental_units',CASE WHEN l.attempt_id IS NULL THEN 4 ELSE 6 END,'continuation',l.attempt_id IS NOT NULL) END
 FROM d4.deliveries d JOIN d3.dispatches ds ON ds.command_id=d.dispatch_command_id JOIN public.operations op ON op.id=ds.operation_id
 LEFT JOIN d4.step_intents i ON i.operation_id=op.id LEFT JOIN d4.continuation_links l ON l.attempt_id=ds.attempt_id WHERE d.id=delivery;
$$;
CREATE FUNCTION d4.record_continuation_acceptance(cid uuid,delivery uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb;op public.operations;link d4.continuation_links;cp d4.checkpoints;artifact uuid;result jsonb;req jsonb=jsonb_build_object('action','ACCEPT_CONTINUATION','delivery',delivery,'proof',proof);prior jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 info=d4.i5_inspect(delivery);SELECT * INTO STRICT op FROM public.operations WHERE id=(info->>'operation')::uuid;
 SELECT * INTO STRICT link FROM d4.continuation_links WHERE attempt_id=(info->>'attempt')::uuid;
 SELECT * INTO STRICT cp FROM d4.checkpoints WHERE id=link.checkpoint_id;
 IF op.state<>'VERIFYING' OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'artifact_valid' IS DISTINCT FROM 'true'::jsonb
  OR proof->'receiver_closed' IS DISTINCT FROM 'true'::jsonb OR proof->'steps' IS DISTINCT FROM '{"step-1":"APPLIED","step-2":"APPLIED"}'::jsonb
  OR proof->>'context_hash' IS DISTINCT FROM op.context_pack_sha256 OR proof->>'manifest_hash' IS DISTINCT FROM cp.manifest_hash
  OR proof->>'attempt' IS DISTINCT FROM info->>'attempt' OR proof->>'generation' IS DISTINCT FROM info->>'generation'
  OR EXISTS(SELECT 1 FROM d2.reservation_balances WHERE reservation_id=cp.reservation_id AND (outstanding<>0 OR consumed<>10))
  OR EXISTS(SELECT 1 FROM d2.effect_receipts er WHERE er.operation_id=op.id AND NOT
    ((er.generation=cp.source_generation AND er.effect_key=op.id||'/'||cp.context_hash||'/step-1' AND er.status='APPLIED') OR
     (er.generation=cp.source_generation AND er.effect_key=op.id||'/'||cp.context_hash||'/step-2' AND er.status='ABSENT') OR
     (er.generation=link.generation AND er.effect_key=op.id||'/'||cp.context_hash||'/step-2' AND er.status='APPLIED')))
  OR EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND status='UNKNOWN')
  OR EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id GROUP BY generation,effect_key HAVING count(DISTINCT status)>1)
 THEN RAISE EXCEPTION 'Complete sealed continuation and cumulative settlement required' USING ERRCODE='23514';END IF;
 INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(op.id,link.generation,op.id||'/'||op.context_pack_sha256||'/step-2','APPLIED','continuation-proof/'||cid);
 INSERT INTO public.artifacts(artifact_ref,sha256,media_type,byte_size) VALUES('continuation-proof/'||cid,encode(public.digest(proof::text,'sha256'),'hex'),'application/json',octet_length(proof::text)) RETURNING id INTO artifact;
 INSERT INTO public.execution_evidence(attempt_id,artifact_id,evidence_type) VALUES(link.attempt_id,artifact,'ACCEPTANCE_PASS');
 result=jsonb_build_object('proof_id',cid);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d4.i5_audit() RETURNS jsonb LANGUAGE sql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$ SELECT d4.lab_audit()||jsonb_build_object(
 'acceptance',(SELECT coalesce(jsonb_agg(to_jsonb(x)),'[]') FROM public.execution_evidence x),
 'checkpoints',(SELECT coalesce(jsonb_agg(to_jsonb(x)),'[]') FROM d4.checkpoints x),
 'authorizations',(SELECT coalesce(jsonb_agg(to_jsonb(x)),'[]') FROM d4.continuation_authorizations x),
 'continuation_links',(SELECT coalesce(jsonb_agg(to_jsonb(x)),'[]') FROM d4.continuation_links x)); $$;
REVOKE ALL ON FUNCTION d4.checkpoint_inspect(uuid),d4.i5_inspect(uuid),d4.record_continuation_acceptance(uuid,uuid,jsonb),d4.i5_audit() FROM PUBLIC;
CREATE FUNCTION d4.finalize_continuation(cid uuid,delivery uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','FINALIZE_CONTINUATION','delivery',delivery);prior jsonb;info jsonb;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 info=d4.i5_inspect(delivery);
 IF NOT EXISTS(SELECT 1 FROM d4.continuation_links WHERE attempt_id=(info->>'attempt')::uuid)
  OR NOT EXISTS(SELECT 1 FROM d4.checkpoint_commands WHERE request->>'action'='ACCEPT_CONTINUATION' AND request->>'delivery'=delivery::text)
 THEN RAISE EXCEPTION 'Independent continuation acceptance required' USING ERRCODE='23514';END IF;
 result=d3.execution(cid,jsonb_build_object('action','VERIFY','operation_id',info->>'operation','attempt_id',info->>'attempt','worker_id',info->>'worker','resource_id',info->>'resource','generation',info->'generation'));
 INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;
REVOKE ALL ON FUNCTION d4.finalize_continuation(uuid,uuid) FROM PUBLIC;
