-- SPDX-License-Identifier: GPL-3.0-only
-- A23: trusted Java verifier ingress. No worker evidence minting and no external rollback.
CREATE TABLE d4.tree_requirements(operation_id uuid PRIMARY KEY REFERENCES public.operations(id),manifest jsonb NOT NULL,manifest_hash text NOT NULL CHECK(manifest_hash ~ '^[a-f0-9]{64}$'),restoration boolean NOT NULL,base_manifest jsonb NOT NULL);
CREATE TABLE d4.tree_proofs(id uuid PRIMARY KEY,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),attempt_id uuid NOT NULL REFERENCES public.execution_attempts(id),context_hash text NOT NULL,policy_hash text NOT NULL,manifest_hash text NOT NULL,proof jsonb NOT NULL,recorded_at timestamptz NOT NULL DEFAULT clock_timestamp());
DO $$ DECLARE n text;BEGIN FOREACH n IN ARRAY ARRAY['tree_requirements','tree_proofs'] LOOP EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',n);END LOOP;END $$;
CREATE FUNCTION d4.freeze_tree_requirement() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
BEGIN PERFORM d3.lock_state();IF EXISTS(SELECT 1 FROM public.execution_attempts WHERE operation_id=NEW.operation_id) OR jsonb_typeof(NEW.manifest) IS DISTINCT FROM 'object' OR jsonb_typeof(NEW.base_manifest) IS DISTINCT FROM 'object' OR (SELECT count(*) FROM jsonb_object_keys(NEW.manifest))>64 OR (SELECT count(*) FROM jsonb_object_keys(NEW.base_manifest))>64 THEN RAISE EXCEPTION 'Freeze bounded tree requirements before first CLAIM' USING ERRCODE='23514';END IF;RETURN NEW;END $$;
CREATE TRIGGER freeze_tree BEFORE INSERT ON d4.tree_requirements FOR EACH ROW EXECUTE FUNCTION d4.freeze_tree_requirement();
CREATE FUNCTION d4.tree_info(delivery uuid) RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT d4.lab_inspect(delivery)||jsonb_build_object('tree_requirement',(SELECT to_jsonb(r) FROM d4.tree_requirements r WHERE r.operation_id=(d4.lab_inspect(delivery)->>'operation')::uuid)); $$;
CREATE FUNCTION d4.tree_record(cid uuid,delivery uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d3,d4 AS $$
DECLARE i jsonb=d4.tree_info(delivery);r d4.tree_requirements;p d4.tree_proofs;result jsonb;
BEGIN PERFORM d3.lock_state();SELECT * INTO p FROM d4.tree_proofs WHERE id=cid;IF FOUND THEN IF p.delivery_id IS DISTINCT FROM delivery OR p.proof IS DISTINCT FROM proof THEN RAISE EXCEPTION 'Tree proof replay conflict' USING ERRCODE='23514';END IF;RETURN jsonb_build_object('proof_id',cid);END IF;
 SELECT * INTO r FROM d4.tree_requirements WHERE operation_id=(i->>'operation')::uuid;
 IF cid IS NULL OR r.operation_id IS NULL OR proof->>'schema' IS DISTINCT FROM 'd4.tree.proof.v1' OR proof->>'manifest_hash' IS DISTINCT FROM r.manifest_hash OR proof->'restoration' IS DISTINCT FROM to_jsonb(r.restoration) OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'files_verified' IS DISTINCT FROM 'true'::jsonb OR proof->'git_verified' IS DISTINCT FROM 'true'::jsonb
 OR coalesce(proof->>'base_oid','') !~ '^[a-f0-9]{40}$' OR coalesce(proof->>'commit_oid','') !~ '^[a-f0-9]{40}$' OR coalesce(proof->>'host_observation_hash','') !~ '^[a-f0-9]{64}$'
 OR EXISTS(SELECT 1 FROM jsonb_each(jsonb_build_object('operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation','context_hash',i->'context_hash','policy_hash',i->'policy_hash')) x WHERE proof->x.key IS DISTINCT FROM x.value)
 THEN RAISE EXCEPTION 'Independent bound file/Git verification required' USING ERRCODE='23514';END IF;
 INSERT INTO d4.tree_proofs VALUES(cid,delivery,(i->>'attempt')::uuid,i->>'context_hash',i->>'policy_hash',r.manifest_hash,proof,clock_timestamp());RETURN jsonb_build_object('proof_id',cid);
END $$;
CREATE FUNCTION d4.require_tree(attempt uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
BEGIN IF EXISTS(SELECT 1 FROM public.execution_attempts a JOIN d4.tree_requirements r ON r.operation_id=a.operation_id WHERE a.id=attempt) AND NOT EXISTS(SELECT 1 FROM d4.tree_proofs p JOIN public.execution_attempts a ON a.id=p.attempt_id JOIN public.operations o ON o.id=a.operation_id JOIN d4.tree_requirements r ON r.operation_id=o.id WHERE a.id=attempt AND p.manifest_hash=r.manifest_hash AND p.context_hash=o.context_pack_sha256 AND p.policy_hash=encode(public.digest(o.policy_snapshot::text,'sha256'),'hex') AND p.recorded_at BETWEEN clock_timestamp()-interval '20 seconds' AND clock_timestamp()) THEN RAISE EXCEPTION 'Fresh independent tree proof required before acceptance/checkpoint' USING ERRCODE='23514';END IF;END $$;
CREATE FUNCTION d4.tree_acceptance_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
BEGIN PERFORM d3.lock_state();IF NEW.evidence_type='ACCEPTANCE_PASS' THEN PERFORM d4.require_tree(NEW.attempt_id);END IF;RETURN NEW;END $$;
CREATE TRIGGER independent_tree BEFORE INSERT ON public.execution_evidence FOR EACH ROW EXECUTE FUNCTION d4.tree_acceptance_guard();
CREATE FUNCTION d4.tree_checkpoint_guard() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
DECLARE attempt uuid;
BEGIN PERFORM d3.lock_state();SELECT a.id INTO STRICT attempt FROM public.execution_attempts a WHERE a.operation_id=NEW.operation_id AND a.lease_generation=NEW.source_generation;PERFORM d4.require_tree(attempt);RETURN NEW;END $$;
CREATE TRIGGER independent_tree BEFORE INSERT ON d4.checkpoints FOR EACH ROW EXECUTE FUNCTION d4.tree_checkpoint_guard();
CREATE TRIGGER independent_tree BEFORE INSERT ON d4.multi_checkpoints FOR EACH ROW EXECUTE FUNCTION d4.tree_checkpoint_guard();
CREATE FUNCTION d4.tree_audit() RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT d4.session_audit()||jsonb_build_object('tree_requirements',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.tree_requirements t),'tree_proofs',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.tree_proofs t)); $$;
REVOKE ALL ON ALL TABLES IN SCHEMA d4 FROM PUBLIC;
REVOKE ALL ON FUNCTION d4.freeze_tree_requirement(),d4.tree_info(uuid),d4.tree_record(uuid,uuid,jsonb),d4.require_tree(uuid),d4.tree_acceptance_guard(),d4.tree_checkpoint_guard(),d4.tree_audit() FROM PUBLIC;

ALTER FUNCTION d3.state_relations() RENAME TO state_relations_before_tree;
CREATE FUNCTION d3.state_relations() RETURNS text[] LANGUAGE sql IMMUTABLE AS $$ SELECT d3.state_relations_before_tree()||ARRAY['d4.tree_requirements','d4.tree_proofs']; $$;
