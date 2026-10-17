-- SemVer 2.0.0 and npm range semantics, proposed D2 validation kernel.
-- Range expansion follows npm/node-semver 7.7.2 (ISC); see THIRD-PARTY-NOTICES.md.
-- Strict stored versions; npm-compatible range syntax. No loose/coerce mode.
CREATE FUNCTION d2.semver_parse(v text) RETURNS jsonb LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE m text[]; p text; parts text[];
BEGIN
 IF v IS NULL OR octet_length(v)>256 THEN RETURN NULL; END IF;
 m=regexp_match(v,'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$');
 IF m IS NULL THEN RETURN NULL; END IF;
 IF m[1]::numeric>9007199254740991 OR m[2]::numeric>9007199254740991 OR m[3]::numeric>9007199254740991 THEN RETURN NULL; END IF;
 parts=CASE WHEN m[4] IS NULL THEN ARRAY[]::text[] ELSE string_to_array(m[4],'.') END;
 FOREACH p IN ARRAY parts LOOP
  IF p ~ '^0[0-9]+$' THEN RETURN NULL; END IF;
 END LOOP;
 RETURN jsonb_build_object('core',ARRAY[m[1]::numeric,m[2]::numeric,m[3]::numeric],'pre',parts);
END $$;

CREATE FUNCTION d2.semver_compare(a jsonb,b jsonb) RETURNS integer LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE x numeric[]; y numeric[]; ap text[]; bp text[]; i integer; an boolean; bn boolean;
BEGIN
 IF a IS NULL OR b IS NULL THEN RAISE EXCEPTION 'Invalid parsed version' USING ERRCODE='22023'; END IF;
 SELECT array_agg(value::numeric ORDER BY ord) INTO x FROM jsonb_array_elements_text(a->'core') WITH ORDINALITY AS t(value,ord);
 SELECT array_agg(value::numeric ORDER BY ord) INTO y FROM jsonb_array_elements_text(b->'core') WITH ORDINALITY AS t(value,ord);
 IF x<>y THEN RETURN CASE WHEN x<y THEN -1 ELSE 1 END; END IF;
 SELECT coalesce(array_agg(value ORDER BY ord),ARRAY[]::text[]) INTO ap FROM jsonb_array_elements_text(a->'pre') WITH ORDINALITY AS t(value,ord);
 SELECT coalesce(array_agg(value ORDER BY ord),ARRAY[]::text[]) INTO bp FROM jsonb_array_elements_text(b->'pre') WITH ORDINALITY AS t(value,ord);
 IF cardinality(ap)=0 OR cardinality(bp)=0 THEN RETURN CASE WHEN ap=bp THEN 0 WHEN cardinality(ap)=0 THEN 1 ELSE -1 END; END IF;
 FOR i IN 1..least(cardinality(ap),cardinality(bp)) LOOP
  IF ap[i]=bp[i] THEN CONTINUE; END IF;
  an=ap[i]~'^[0-9]+$';bn=bp[i]~'^[0-9]+$';
  IF an AND bn THEN RETURN CASE WHEN length(ap[i])<length(bp[i]) OR (length(ap[i])=length(bp[i]) AND ap[i] COLLATE "C" < bp[i] COLLATE "C") THEN -1 ELSE 1 END; END IF;
  IF an<>bn THEN RETURN CASE WHEN an THEN -1 ELSE 1 END; END IF;
  RETURN CASE WHEN ap[i] COLLATE "C" < bp[i] COLLATE "C" THEN -1 ELSE 1 END;
 END LOOP;
 RETURN CASE WHEN cardinality(ap)=cardinality(bp) THEN 0 WHEN cardinality(ap)<cardinality(bp) THEN -1 ELSE 1 END;
END $$;

-- A partial is [major,minor,patch,prerelease]; null numeric fields are wildcards.
CREATE FUNCTION d2.semver_partial(v text) RETURNS text[] LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE m text[]; i integer; wildcard boolean=false; trial text;
BEGIN
 m=regexp_match(v,'^[v=]*(0|[1-9][0-9]*|[xX*])(?:\.(0|[1-9][0-9]*|[xX*]))?(?:\.(0|[1-9][0-9]*|[xX*]))?(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$');
 IF m IS NULL THEN RAISE EXCEPTION 'Invalid version range token' USING ERRCODE='22023'; END IF;
 FOR i IN 1..3 LOOP
  IF m[i] IS NULL OR m[i]~'^[xX*]$' THEN wildcard=true; END IF;
  IF wildcard THEN m[i]=NULL;
  ELSIF length(m[i])>16 OR m[i]::numeric>9007199254740991 THEN RAISE EXCEPTION 'Range numeric limit exceeded' USING ERRCODE='54000'; END IF;
 END LOOP;
 -- npm ignores suffixes on wildcard versions. Full versions must be valid.
 IF m[3] IS NOT NULL THEN
  trial=m[1]||'.'||m[2]||'.'||m[3]||CASE WHEN m[4] IS NULL THEN '' ELSE '-'||m[4] END||CASE WHEN m[5] IS NULL THEN '' ELSE '+'||m[5] END;
  IF d2.semver_parse(trial) IS NULL THEN RAISE EXCEPTION 'Invalid full range version' USING ERRCODE='22023'; END IF;
 ELSE m[4]=NULL; END IF;
 RETURN m[1:4];
END $$;
CREATE FUNCTION d2.semver_bound(m text[],increment_at integer DEFAULT 0,zero_pre boolean DEFAULT false) RETURNS text LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE n numeric[]=ARRAY[coalesce(m[1],'0')::numeric,coalesce(m[2],'0')::numeric,coalesce(m[3],'0')::numeric];i integer;
BEGIN
 IF increment_at>0 THEN
  n[increment_at]=n[increment_at]+1;
  IF increment_at<3 THEN FOR i IN increment_at+1..3 LOOP n[i]=0; END LOOP; END IF;
 END IF;
 RETURN array_to_string(n,'.')||CASE WHEN zero_pre THEN '-0' WHEN increment_at=0 AND m[4] IS NOT NULL THEN '-'||m[4] ELSE '' END;
END $$;

-- Return normalized comparator strings for a single token.
CREATE FUNCTION d2.semver_expand(token text) RETURNS text[] LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE mt text[];m text[];op text;v text;lo text;hi text;inc integer;
BEGIN
 mt=regexp_match(token,'^(~>|~|\^|>=|<=|>|<|=)?(.*)$');op=coalesce(mt[1],'');v=mt[2];
 m=d2.semver_partial(v);
 IF m[1] IS NULL THEN
  IF op IN ('>','<') THEN RETURN ARRAY['<0.0.0-0']; END IF;
  RETURN ARRAY[]::text[];
 END IF;
 lo=d2.semver_bound(m);
 IF op IN ('^','~','~>') THEN
  inc=CASE WHEN m[2] IS NULL THEN 1 WHEN op IN ('~','~>') THEN 2 WHEN m[1]<>'0' THEN 1 WHEN m[3] IS NULL OR m[2]<>'0' THEN 2 ELSE 3 END;
  RETURN ARRAY['>='||lo,'<'||d2.semver_bound(m,inc,true)];
 END IF;
 IF m[3] IS NOT NULL THEN
  IF v !~ '^v?[0-9]' THEN RAISE EXCEPTION 'Invalid full comparator prefix' USING ERRCODE='22023'; END IF;
  RETURN ARRAY[op||lo];
 END IF;
 inc=CASE WHEN m[2] IS NULL THEN 1 ELSE 2 END;
 IF op='>' THEN RETURN ARRAY['>='||d2.semver_bound(m,inc)]; END IF;
 IF op='<=' THEN RETURN ARRAY['<'||d2.semver_bound(m,inc,true)]; END IF;
 IF op='<' THEN RETURN ARRAY['<'||d2.semver_bound(m,0,true)]; END IF;
 IF op='>=' THEN RETURN ARRAY['>='||lo]; END IF;
 RETURN ARRAY['>='||lo,'<'||d2.semver_bound(m,inc,true)];
END $$;

CREATE FUNCTION d2.semver_range(r text) RETURNS jsonb LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE arms text[];arm text;tok text;tokens text[]; comps text[];hy text[];a text[];b text[];i integer;mt text[];parsed jsonb;branch jsonb;result jsonb='[]'::jsonb;
BEGIN
 IF r IS NULL THEN RAISE EXCEPTION 'Missing range' USING ERRCODE='22023'; END IF;
 IF octet_length(r)>4096 THEN RAISE EXCEPTION 'Range length limit exceeded' USING ERRCODE='54000'; END IF;
 arms=CASE WHEN r='' THEN ARRAY['']::text[] ELSE string_to_array(r,'||') END;
 IF cardinality(arms)>32 THEN RAISE EXCEPTION 'Range union limit exceeded' USING ERRCODE='54000'; END IF;
 FOREACH arm IN ARRAY arms LOOP
  arm=btrim(regexp_replace(arm,U&'[\0009-\000D \00A0\1680\2000-\200A\2028\2029\202F\205F\3000\FEFF]+',' ','g'));comps=ARRAY[]::text[];branch='[]'::jsonb;
  hy=regexp_match(arm,'^(\S+) - (\S+)$');
  IF hy IS NOT NULL THEN
   a=d2.semver_partial(hy[1]);b=d2.semver_partial(hy[2]);
   IF a[1] IS NOT NULL THEN comps=array_append(comps,'>='||d2.semver_bound(a)); END IF;
   IF b[1] IS NOT NULL THEN
    IF b[3] IS NOT NULL THEN comps=array_append(comps,'<='||d2.semver_bound(b));
    ELSE comps=array_append(comps,'<'||d2.semver_bound(b,CASE WHEN b[2] IS NULL THEN 1 ELSE 2 END,true)); END IF;
   END IF;
  ELSE
   arm=regexp_replace(arm,'(>=|<=|>|<|=|~>|~|\^) +','\1','g');
   tokens=CASE WHEN arm='' THEN ARRAY[]::text[] ELSE string_to_array(arm,' ') END;
   IF cardinality(tokens)>128 THEN RAISE EXCEPTION 'Comparator limit exceeded' USING ERRCODE='54000'; END IF;
   FOREACH tok IN ARRAY tokens LOOP comps=comps||d2.semver_expand(tok); END LOOP;
  END IF;
  FOREACH tok IN ARRAY comps LOOP
   mt=regexp_match(tok,'^(>=|<=|>|<|=)?(.*)$');
   parsed=d2.semver_parse(mt[2]);
   IF parsed IS NULL THEN RAISE EXCEPTION 'Comparator exceeds supported bounds' USING ERRCODE='54000'; END IF;
   -- npm removes >=0.0.0, which must not opt prereleases into a range.
   IF tok='>=0.0.0' THEN CONTINUE; END IF;
   branch=branch||jsonb_build_array(jsonb_build_object('op',coalesce(mt[1],'='),'v',parsed));
  END LOOP;
  result=result||jsonb_build_array(branch);
 END LOOP;
 -- npm collapses a union containing ANY to ANY, after validating all arms.
 IF EXISTS(SELECT 1 FROM jsonb_array_elements(result) AS arms(value) WHERE arms.value='[]'::jsonb) THEN RETURN '[[]]'::jsonb; END IF;
 RETURN result;
END $$;
CREATE FUNCTION d2.compatibility_result(version text,constraint_text text) RETURNS text LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE v jsonb;r jsonb;arm jsonb;comp jsonb;cmp integer;matches boolean;pre_allowed boolean;
BEGIN
 IF version IS NOT NULL AND octet_length(version)>256 THEN RETURN 'LIMIT_EXCEEDED'; END IF;
 v=d2.semver_parse(version);
 IF v IS NULL THEN RETURN 'INVALID_VERSION'; END IF;
 BEGIN r=d2.semver_range(constraint_text);
 EXCEPTION WHEN SQLSTATE '54000' THEN RETURN 'LIMIT_EXCEEDED'; WHEN SQLSTATE '22023' THEN RETURN 'INVALID_RANGE'; END;
 FOR arm IN SELECT value FROM jsonb_array_elements(r) LOOP
  matches=true;pre_allowed=jsonb_array_length(v->'pre')=0;
  FOR comp IN SELECT value FROM jsonb_array_elements(arm) LOOP
   cmp=d2.semver_compare(v,comp->'v');
   matches=matches AND CASE comp->>'op' WHEN '=' THEN cmp=0 WHEN '>' THEN cmp>0 WHEN '>=' THEN cmp>=0 WHEN '<' THEN cmp<0 WHEN '<=' THEN cmp<=0 ELSE false END;
   IF comp->'v'->'core'=v->'core' AND jsonb_array_length(comp->'v'->'pre')>0 THEN pre_allowed=true; END IF;
  END LOOP;
  IF matches AND pre_allowed THEN RETURN 'MATCH'; END IF;
 END LOOP;
 RETURN 'NO_MATCH';
END $$;
CREATE OR REPLACE FUNCTION d2.compatible(version text,constraint_text text) RETURNS boolean LANGUAGE sql IMMUTABLE AS $$
 SELECT d2.compatibility_result(version,constraint_text)='MATCH';
$$;
REVOKE ALL ON FUNCTION d2.semver_parse(text),d2.semver_compare(jsonb,jsonb),d2.semver_partial(text),d2.semver_bound(text[],integer,boolean),d2.semver_expand(text),d2.semver_range(text),d2.compatibility_result(text,text) FROM PUBLIC;

CREATE FUNCTION d2.semver_range_status(r text) RETURNS text LANGUAGE plpgsql IMMUTABLE AS $$
BEGIN
 PERFORM d2.semver_range(r);RETURN 'VALID';
EXCEPTION WHEN SQLSTATE '54000' THEN RETURN 'LIMIT_EXCEEDED'; WHEN SQLSTATE '22023' THEN RETURN 'INVALID_RANGE';
END $$;
-- Owner-only inventory for migration preflight; never rewrite existing values.
CREATE VIEW d2.semver_preflight AS
 SELECT 'CAPABILITY_VERSION'::text entity_type,id,version input,
 CASE WHEN d2.semver_parse(version) IS NULL THEN 'INVALID_VERSION' ELSE 'VALID' END status FROM public.capability_versions
 UNION ALL
 SELECT 'CAPABILITY_REQUIREMENT',id,version_constraint,d2.semver_range_status(version_constraint) FROM public.capability_requirements;
REVOKE ALL ON FUNCTION d2.semver_range_status(text) FROM PUBLIC;
REVOKE ALL ON d2.semver_preflight FROM PUBLIC;
