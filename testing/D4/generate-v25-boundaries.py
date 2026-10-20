#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Static additive derivation. Preserve the validated V24 input byte for byte."""
import hashlib,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'migrations-d4-proposed/V24__linear_multicount_checkpoints.sql'
text=source.read_text();start=text.index('CREATE FUNCTION d4.multi_freeze(');end=text.index('END $$;',start)+len('END $$;')
freeze=text[start:end].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1)
strict='''
 -- Validate required JSON types before text extraction/casts.
 -- Approved closed schema: reject unknown keys while preserving old facts.
 IF jsonb_typeof(m) IS DISTINCT FROM 'object' THEN RAISE EXCEPTION 'Typed v2 manifest object required' USING ERRCODE='23514';END IF;
 IF jsonb_typeof(m->'schema') IS DISTINCT FROM 'string' OR jsonb_typeof(m->'pool') IS DISTINCT FROM 'string' OR jsonb_typeof(m->'resource') IS DISTINCT FROM 'string'
 OR jsonb_typeof(m->'accounts') IS DISTINCT FROM 'object' OR jsonb_typeof(m->'steps') IS DISTINCT FROM 'array'
 THEN RAISE EXCEPTION 'Exact typed v2 manifest fields required' USING ERRCODE='23514';END IF;
 IF m - ARRAY['schema','pool','resource','accounts','steps'] <> '{}'::jsonb THEN RAISE EXCEPTION 'Closed v2 manifest required' USING ERRCODE='23514';END IF;
 IF jsonb_array_length(m->'steps') NOT BETWEEN 1 AND 32 OR (SELECT count(*) FROM jsonb_object_keys(m->'accounts')) NOT BETWEEN 1 AND 8 THEN RAISE EXCEPTION 'Bounded v2 manifest required' USING ERRCODE='23514';END IF;
 FOR s IN SELECT value FROM jsonb_array_elements(m->'steps') LOOP
  IF jsonb_typeof(s) IS DISTINCT FROM 'object' THEN RAISE EXCEPTION 'Typed step required' USING ERRCODE='23514';END IF;
  IF jsonb_typeof(s->'id') IS DISTINCT FROM 'string' OR jsonb_typeof(s->'effect_hash') IS DISTINCT FROM 'string' OR jsonb_typeof(s->'cost') IS DISTINCT FROM 'object'
  THEN RAISE EXCEPTION 'Exact typed step fields required' USING ERRCODE='23514';END IF;
  IF s - ARRAY['id','effect_hash','cost'] <> '{}'::jsonb THEN RAISE EXCEPTION 'Closed v2 step required' USING ERRCODE='23514';END IF;
  FOR a IN SELECT * FROM jsonb_each(s->'cost') LOOP
   IF jsonb_typeof(a.value) IS DISTINCT FROM 'number' THEN RAISE EXCEPTION 'Numeric exact cost required' USING ERRCODE='23514';END IF;
  END LOOP;
 END LOOP;
 FOR a IN SELECT * FROM jsonb_each(m->'accounts') LOOP
  IF jsonb_typeof(a.value) IS DISTINCT FROM 'object' THEN RAISE EXCEPTION 'Typed account required' USING ERRCODE='23514';END IF;
  IF jsonb_typeof(a.value->'original') IS DISTINCT FROM 'number' OR jsonb_typeof(a.value->'dimension') IS DISTINCT FROM 'string'
  OR jsonb_typeof(a.value->'unit') IS DISTINCT FROM 'string' OR jsonb_typeof(a.value->'start') IS DISTINCT FROM 'string' OR jsonb_typeof(a.value->'end') IS DISTINCT FROM 'string'
  THEN RAISE EXCEPTION 'Exact typed account fields required' USING ERRCODE='23514';END IF;
  IF a.value - ARRAY['original','dimension','unit','start','end'] <> '{}'::jsonb THEN RAISE EXCEPTION 'Closed v2 account required' USING ERRCODE='23514';END IF;
 END LOOP;
'''
def original(name):
 begin=text.index('CREATE FUNCTION d4.'+name+'(');finish=text.index('END $$;',begin)+len('END $$;')
 return text[begin:finish].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1)
validator_body=re.sub(r"THEN RAISE EXCEPTION '[^']*' USING ERRCODE='23514';END IF;",'THEN RETURN false;END IF;',strict)
assert 'RAISE' not in validator_body
validator="CREATE FUNCTION d4.multi_manifest_typed(m jsonb) RETURNS boolean LANGUAGE plpgsql IMMUTABLE STRICT SET search_path=pg_catalog AS $$\nDECLARE s jsonb;a record;\nBEGIN\n"+validator_body+"\n RETURN true;\nEND $$;"
freeze=original('multi_freeze').replace('\nBEGIN\n',"\nBEGIN\n IF NOT d4.multi_manifest_typed(m) THEN RAISE EXCEPTION 'Typed compatible v2 intention required' USING ERRCODE='23514';END IF;\n",1)
inspect=original('multi_inspect').replace("'multi_checkpoint',true,'is_checkpoint_fixture',true", "'multi_checkpoint',true,'manifest_compatible',d4.multi_manifest_typed(m.manifest),'is_checkpoint_fixture',true")
evaluate=original('multi_evaluate').replace('\nBEGIN\n',"\nBEGIN\n IF NOT d4.multi_manifest_typed(m) THEN RAISE EXCEPTION 'Typed compatible v2 intention required' USING ERRCODE='23514';END IF;\n",1)
settled_start=text.index('CREATE FUNCTION d4.multi_head_settled(');settled_end=text.index('$$;',settled_start)+3
settled=text[settled_start:settled_end].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1).replace('WHERE cp.operation_id=oid AND','WHERE cp.operation_id=oid AND d4.multi_manifest_typed(i.manifest) AND',1)
dispatch=original('dispatch_continuation');needle=" SELECT * INTO mi FROM d4.multi_intents WHERE operation_id=(req->>'operation_id')::uuid;"
assert dispatch.count(needle)==1
dispatch=dispatch.replace(needle,needle+"\n IF mi.operation_id IS NOT NULL AND NOT d4.multi_manifest_typed(mi.manifest) THEN RAISE EXCEPTION 'Typed compatible v2 intention required' USING ERRCODE='23514';END IF;")
bridge=ROOT/'migrations-d4-proposed/V18__synthetic_lab_bridge.sql';bridge_text=bridge.read_text();begin=bridge_text.index('CREATE FUNCTION d4.lab_authorize(');finish=bridge_text.index('END $$;',begin)+len('END $$;')
authorize=bridge_text[begin:finish].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1)
needle='  info=d4.lab_inspect(delivery);';assert authorize.count(needle)==1
authorize=authorize.replace(needle,needle+"\n  IF EXISTS(SELECT 1 FROM d4.multi_intents i WHERE i.operation_id=(info->>'operation')::uuid AND NOT d4.multi_manifest_typed(i.manifest)) THEN RAISE EXCEPTION 'Typed compatible v2 intention required' USING ERRCODE='23514';END IF;")
wrapper='''
-- The old implementation remains owner-only; service grants move to the wrapper.
ALTER FUNCTION d4.multi_commit(uuid,uuid,uuid,bigint) RENAME TO multi_commit_before_v25;
CREATE FUNCTION d4.multi_commit(cid uuid,rid uuid,pid uuid,expected_version bigint) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','MULTI_COMMIT','request',rid,'proof',pid,'version',expected_version);prior jsonb;lease_until timestamptz;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT l.expires_at INTO STRICT lease_until FROM d4.multi_proofs pr JOIN d4.checkpoint_requests r ON r.id=pr.request_id
 LEFT JOIN public.operation_leases l ON l.attempt_id=r.attempt_id AND l.operation_id=r.operation_id
 WHERE pr.id=pid AND r.id=rid AND pr.delivery_id=r.delivery_id;
 IF lease_until IS NULL OR clock_timestamp()>=lease_until THEN RAISE EXCEPTION 'Live exact checkpoint lease required' USING ERRCODE='23514';END IF;
 result=d4.multi_commit_before_v25(cid,rid,pid,expected_version);
 -- Account locks and ledger work may have waited after V24's initial check.
 -- Raising here rolls back consumption, release, cancellation, lease deletion,
 -- checkpoint, command, history and outbox together. Proof ingress stays factual.
 IF clock_timestamp()>=lease_until THEN RAISE EXCEPTION 'Checkpoint lease expired during settlement' USING ERRCODE='23514';END IF;
 RETURN result;
END $$;
REVOKE ALL ON FUNCTION d4.multi_commit(uuid,uuid,uuid,bigint),d4.multi_commit_before_v25(uuid,uuid,uuid,bigint) FROM PUBLIC;
DO $$ DECLARE permission record;BEGIN
 FOR permission IN SELECT r.rolname,a.is_grantable FROM pg_proc p
 CROSS JOIN LATERAL aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a JOIN pg_roles r ON r.oid=a.grantee
 WHERE p.oid='d4.multi_commit_before_v25(uuid,uuid,uuid,bigint)'::regprocedure AND a.grantee<>p.proowner AND a.privilege_type='EXECUTE' LOOP
  EXECUTE format('GRANT EXECUTE ON FUNCTION d4.multi_commit(uuid,uuid,uuid,bigint) TO %I%s',permission.rolname,CASE WHEN permission.is_grantable THEN ' WITH GRANT OPTION' ELSE '' END);
  EXECUTE format('REVOKE ALL ON FUNCTION d4.multi_commit_before_v25(uuid,uuid,uuid,bigint) FROM %I CASCADE',permission.rolname);
 END LOOP;
END $$;
'''
out='-- SPDX-License-Identifier: GPL-3.0-only\n-- GENERATED by testing/D4/generate-v25-boundaries.py; no runtime rewriting.\n-- V24 source SHA256: '+hashlib.sha256(source.read_bytes()).hexdigest()+'\n\n'+'\n\n'.join([validator,freeze,inspect,evaluate,settled,dispatch,authorize])+'\n'+wrapper+\
 'REVOKE ALL ON FUNCTION d4.multi_manifest_typed(jsonb) FROM PUBLIC;\n'
p=ROOT/'migrations-d4-proposed/V25__checkpoint_boundary_guards.sql'
if '--check' in sys.argv:assert p.read_text()==out,'V25 derivation differs'
else:p.write_text(out)
