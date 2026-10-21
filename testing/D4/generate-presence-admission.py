#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import sys,hashlib
R=Path(__file__).resolve().parents[2]
def fn(file,name):
 s=(R/file).read_text();a=s.index('FUNCTION '+name+'(');a=s.rfind('CREATE',0,a);b=s.index('$$;',a)+3;return s[a:b].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1)
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
v28='migrations-d4-proposed/V28__verified_revision_and_quarantine.sql';v20='migrations-d4-proposed/V20__continuation_admission_adapters.sql';v25='migrations-d4-proposed/V25__checkpoint_boundary_guards.sql'
parts=[(R/'testing/D4/sql/presence-active.sql').read_text()]
s=fn(v28,'d2.execution');s=once(s,' old_state=op.state;'," old_state=op.state;\n IF action IN ('CLAIM','START','HEARTBEAT') THEN PERFORM d4.require_presence(coalesce(wid,(SELECT worker_id FROM public.operation_leases WHERE operation_id=op.id)));END IF;");parts.append(s)
s=fn(v28,'d3.state_body');s=once(s,'WHERE NOT d4.review_blocked','WHERE d4.presence_live(w.id) AND NOT d4.review_blocked');parts.append(s)
s=fn(v28,'d4.observe_continuation_eligibility');s=once(s,'AND NOT d4.review_blocked','AND d4.presence_live(w.id) AND NOT d4.review_blocked');parts.append(s)
s=fn(v28,'d4.dispatch_continuation');s=once(s,' PERFORM d4.require_unheld'," PERFORM d4.require_presence((req->>'worker_id')::uuid);\n PERFORM d4.require_unheld");parts.append(s)
# Derive latest authorize wrapper, never alter V25.
s=fn(v25,'d4.lab_authorize');s=once(s,'BEGIN','BEGIN\n PERFORM d4.require_delivery_presence(delivery);');parts.append(s)
s=fn(v20,'d4.deliver_continuation');s=once(s,'  RETURN result;',"  INSERT INTO d4.presence_delivery SELECT (result->>'delivery_id')::uuid,session_id FROM d4.presence_heads WHERE worker_id=principal_worker ON CONFLICT DO NOTHING;\n  RETURN result;");parts.append(s)
s=fn('migrations-d4-proposed/V16__durable_worker_delivery.sql','d4.worker_execution');s=once(s,'BEGIN',"BEGIN\n IF action IN ('START','HEARTBEAT') THEN PERFORM d4.require_delivery_presence(delivery);END IF;");parts.append(s)
# Preserve the historic transport body privately; no bypass via ACL alias.
s=fn(v20,'d4.transport_continuation').replace('d4.transport_continuation(','d4.transport_before_presence(',1);parts.append(s)
parts.append('''CREATE OR REPLACE FUNCTION d4.transport_continuation(cid uuid,principal_worker uuid,envelope jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE wid uuid=principal_worker;req jsonb=envelope->'request';sid uuid;action text=req->>'action';p d4.session_transport_commands;result jsonb;clean jsonb;delivery uuid;
BEGIN
 PERFORM d3.lock_state();SELECT * INTO p FROM d4.session_transport_commands WHERE id=cid;
 IF FOUND THEN IF p.worker_id IS DISTINCT FROM wid OR p.request IS DISTINCT FROM envelope THEN RAISE EXCEPTION 'Session transport replay conflict' USING ERRCODE='23514';END IF;RETURN p.response;END IF;
 IF envelope-ARRAY['schema_version','command_id','correlation_id','request']<>'{}'::jsonb OR envelope->>'schema_version' IS DISTINCT FROM 'd4.worker.v1' OR (envelope->>'command_id')::uuid IS DISTINCT FROM cid OR (envelope->>'correlation_id')::uuid IS NULL THEN RAISE EXCEPTION 'Closed transport envelope required' USING ERRCODE='22023';END IF;
 sid=(req->>'session_id')::uuid;
 IF action='PRESENCE' THEN
  IF req-ARRAY['action','session_id','sequence']<>'{}'::jsonb OR jsonb_typeof(req->'sequence') IS DISTINCT FROM 'number' OR (req->>'sequence') !~ '^[1-9][0-9]{0,17}$' THEN RAISE EXCEPTION 'Closed presence request required' USING ERRCODE='23514';END IF;
  result=d4.presence_beat(cid,wid,sid,(req->>'sequence')::bigint);
 ELSE
  IF action='CALLBACK' THEN
   IF NOT EXISTS(SELECT 1 FROM d4.presence_delivery b JOIN d4.deliveries d ON d.id=b.delivery_id WHERE d.id=(req->>'delivery_id')::uuid AND d.worker_id=wid AND b.session_id=sid) THEN RAISE EXCEPTION 'Callback original session binding required' USING ERRCODE='23514';END IF;
  ELSE
   IF sid IS NULL OR NOT EXISTS(SELECT 1 FROM d4.presence_heads WHERE worker_id=wid AND session_id=sid) THEN RAISE EXCEPTION 'Current worker incarnation required' USING ERRCODE='23514';END IF;PERFORM d4.require_presence(wid);
   IF action IN ('START','HEARTBEAT') THEN SELECT id INTO delivery FROM d4.deliveries WHERE id=(req->>'delivery_id')::uuid;PERFORM d4.require_delivery_presence(delivery);END IF;
  END IF;
  clean=jsonb_set(envelope,'{request}',req-'session_id');result=d4.transport_before_presence(cid,wid,clean)->'result';
 END IF;
 result=jsonb_build_object('schema_version','d4.worker.v1','command_id',cid,'correlation_id',envelope->>'correlation_id','result',result);INSERT INTO d4.session_transport_commands VALUES(cid,wid,envelope,result);RETURN result;
END $$;''')
parts.append("REVOKE ALL ON ALL TABLES IN SCHEMA d4 FROM PUBLIC;\nREVOKE ALL ON FUNCTION d4.transport_before_presence(uuid,uuid,jsonb),d4.presence_current(uuid),d4.presence_open(uuid,uuid,uuid,uuid),d4.presence_beat(uuid,uuid,uuid,bigint),d4.presence_live(uuid),d4.require_presence(uuid),d4.require_delivery_presence(uuid),d4.session_audit() FROM PUBLIC;")
sources=['testing/D4/sql/presence-active.sql',v28,v20,v25];out='-- GENERATED by testing/D4/generate-presence-admission.py; A24 laboratory proposal.\n'+''.join('-- Source SHA256 '+f+' '+hashlib.sha256((R/f).read_bytes()).hexdigest()+'\n' for f in sources)+'\n\n'.join(parts)+'\n';p=R/'migrations-d4-proposed/V29__durable_worker_incarnation.sql'
if '--check' in sys.argv:assert p.read_text()==out
else:p.write_text(out)
