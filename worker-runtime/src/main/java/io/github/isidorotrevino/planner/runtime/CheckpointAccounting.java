// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.runtime;

import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;

/** Pure, bounded I8 accounting. No database, admission, evidence or authority grants.
 * Inputs must come from the independently verified frozen intention, closed receiver
 * and durable D2 journal. A caller cannot turn worker-supplied values into proof.
 */
public final class CheckpointAccounting {
 private CheckpointAccounting() {}
 public record Account(UUID id,String dimension,Instant start,Instant end,BigDecimal original) {
  public Account {Objects.requireNonNull(id);if(dimension==null||!dimension.matches("[A-Za-z0-9_.-]{1,64}")||start==null||end==null||!end.isAfter(start))throw bad("ACCOUNT_BINDING");original=units(original);if(original.signum()==0)throw bad("ORIGINAL_VECTOR");}
 }
 public record Step(String id,String effectHash,Map<UUID,BigDecimal> cost) {
  public Step {if(id==null||!id.matches("[A-Za-z0-9_-]{1,64}"))throw bad("STEP_ID");hash(effectHash);cost=vector(cost);}
 }
 public record Manifest(UUID operation,UUID resource,String pool,String contextHash,String policyHash,List<Account> accounts,List<Step> steps,int maxAttempts) {
  public Manifest {
   Objects.requireNonNull(operation);Objects.requireNonNull(resource);hash(contextHash);hash(policyHash);
   if(!Set.of("PLANNED","INCIDENT").contains(pool)||maxAttempts<1||maxAttempts>20||accounts==null||steps==null||accounts.isEmpty()||accounts.size()>8||steps.isEmpty()||steps.size()>32)throw bad("MANIFEST_BOUNDS");
   accounts=List.copyOf(accounts);steps=List.copyOf(steps);var ids=new HashSet<UUID>();for(var a:accounts)if(!ids.add(a.id()))throw bad("DUPLICATE_ACCOUNT");
   var names=new HashSet<String>();var total=zeros(ids);for(var s:steps){if(!names.add(s.id()))throw bad("DUPLICATE_STEP");if(!s.cost().keySet().equals(ids))throw bad("FULL_COST_VECTOR_REQUIRED");s.cost().forEach((k,v)->total.put(k,total.get(k).add(v)));}
   for(var a:accounts)if(total.get(a.id()).compareTo(a.original())>0)throw bad("COST_EXCEEDS_ORIGINAL");
  }
  public String digest(){
   var text=new StringBuilder("d4.steps.v2\n").append(operation).append('\n').append(resource).append('\n').append(pool).append('\n').append(contextHash).append('\n').append(policyHash).append('\n').append(maxAttempts).append('\n');
   accounts.stream().sorted(Comparator.comparing(a->a.id().toString())).forEach(a->text.append(a.id()).append('|').append(a.dimension()).append('|').append(a.start()).append('|').append(a.end()).append('|').append(a.original().toPlainString()).append('\n'));
   for(var s:steps){text.append(s.id()).append('|').append(s.effectHash()).append('\n');s.cost().entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(e->text.append(e.getKey()).append('=').append(e.getValue().toPlainString()).append('\n'));}return digestText(text.toString());
  }
 }
 public enum Status {APPLIED,ABSENT,UNKNOWN}
 public record Receipt(Status status,String payloadHash) {public Receipt {Objects.requireNonNull(status);if(status==Status.APPLIED)hash(payloadHash);else if(payloadHash!=null)throw bad("NON_APPLIED_HASH");}}
 /** Produced only after authentication/signature, full identity and stop checks outside this calculator. */
 public record ClosedAttempt(ExecutionIdentity identity,long closeSequence,Map<String,Receipt> steps) {
  public ClosedAttempt {Objects.requireNonNull(identity);if(closeSequence<=0)throw bad("DURABLE_CLOSE_REQUIRED");steps=Map.copyOf(steps);}
 }
 public record Applied(UUID attempt,long generation,String payloadHash) {public Applied {Objects.requireNonNull(attempt);if(generation<=0)throw bad("GENERATION");hash(payloadHash);}}
 public record Settlement(String manifestHash,String parentHash,ExecutionIdentity identity,int attemptCount,Map<String,Applied> applied,Map<UUID,BigDecimal> cumulative,Map<UUID,BigDecimal> consume,Map<UUID,BigDecimal> release,boolean terminal) {
  public Settlement {hash(manifestHash);if(parentHash!=null)hash(parentHash);Objects.requireNonNull(identity);applied=Map.copyOf(applied);cumulative=vector(cumulative);consume=vector(consume);release=vector(release);}
  public String digest(){
   var text=new StringBuilder("d4.settlement.v2\n").append(manifestHash).append('\n').append(parentHash).append('\n').append(identity).append('\n').append(attemptCount).append('\n').append(terminal).append('\n');
   applied.entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(e->text.append(e.getKey()).append('=').append(e.getValue()).append('\n'));
   for(var v:List.of(cumulative,consume,release)){text.append("vector\n");v.entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(e->text.append(e.getKey()).append('=').append(e.getValue().toPlainString()).append('\n'));}return digestText(text.toString());
  }
 }
 /** expectedHead and attemptCount are read under D2/D3 locks, never from a worker.
  * Every account is checked before returning; this is a proposal, not a ledger write.
  */
 public static Settlement prepare(Manifest m,Settlement parent,String expectedHead,ClosedAttempt closed,int attemptCount,Map<UUID,BigDecimal> consumed,Map<UUID,BigDecimal> outstanding,Instant now,boolean terminal){
  Objects.requireNonNull(m);Objects.requireNonNull(closed);Objects.requireNonNull(now);var identity=closed.identity();
  if(!m.operation().equals(identity.operation())||!m.resource().equals(identity.resource())||identity.generation()<=0)throw bad("FENCED_IDENTITY");
  if(attemptCount<1||attemptCount>m.maxAttempts()||(!terminal&&attemptCount>=m.maxAttempts()))throw bad("ATTEMPT_LIMIT");
  if(!Objects.equals(expectedHead,parent==null?null:parent.digest()))throw bad("STALE_CHECKPOINT_HEAD");
  var ids=new HashSet<UUID>();m.accounts().forEach(a->ids.add(a.id()));var journal=vector(consumed);var pending=vector(outstanding);
  if(!journal.keySet().equals(ids)||!pending.keySet().equals(ids))throw bad("COMPLETE_JOURNAL_VECTOR_REQUIRED");
  var inherited=new LinkedHashMap<String,Applied>();
  if(parent!=null){
   if(parent.terminal()||!parent.manifestHash().equals(m.digest())||!parent.identity().operation().equals(identity.operation())||!parent.identity().resource().equals(identity.resource())||!parent.identity().worker().equals(identity.worker())||parent.identity().attempt().equals(identity.attempt())||identity.generation()!=parent.identity().generation()+1||attemptCount!=parent.attemptCount()+1)throw bad("CHAIN_PROVENANCE");
   inherited.putAll(parent.applied());
  }else if(attemptCount!=1)throw bad("ROOT_REQUIRES_FIRST_ATTEMPT");
  if(!new HashSet<>(m.steps().stream().map(Step::id).toList()).containsAll(inherited.keySet()))throw bad("INHERITED_EXTRA_STEP");
  var previous=zeros(ids);boolean absent=false;
  for(var s:m.steps()){
   var fact=inherited.get(s.id());if(fact==null){absent=true;continue;}
   if(absent||!s.effectHash().equals(fact.payloadHash())||fact.generation()>parent.identity().generation())throw bad("INHERITED_PREFIX");
   s.cost().forEach((k,v)->previous.put(k,previous.get(k).add(v)));
  }
  if(inherited.size()>m.steps().size()||!equal(previous,journal)||(parent!=null&&!equal(previous,parent.cumulative())))throw bad("JOURNAL_PROVENANCE");
  for(var a:m.accounts())if(now.isBefore(a.start())||!now.isBefore(a.end())||pending.get(a.id()).compareTo(a.original())!=0)throw bad("ORIGINAL_MAPPING_WINDOW_OR_TOP_UP");
  var suffix=new LinkedHashSet<String>();for(var s:m.steps())if(!inherited.containsKey(s.id()))suffix.add(s.id());
  if(!closed.steps().keySet().equals(suffix))throw bad("COMPLETE_CLOSED_SUFFIX_REQUIRED");
  var all=new LinkedHashMap<>(inherited);var cumulative=new HashMap<>(previous);absent=false;int progress=0;
  for(var s:m.steps())if(suffix.contains(s.id())){
   var r=closed.steps().get(s.id());if(r.status()==Status.UNKNOWN)throw bad("UNKNOWN_RETAINS_COMMITMENT");
   if(r.status()==Status.ABSENT){absent=true;continue;}
   if(absent||!s.effectHash().equals(r.payloadHash()))throw bad("ORDER_OR_EFFECT_MISMATCH");
   all.put(s.id(),new Applied(identity.attempt(),identity.generation(),r.payloadHash()));progress++;
   s.cost().forEach((k,v)->cumulative.put(k,cumulative.get(k).add(v)));
  }
  if(progress==0||terminal!=(all.size()==m.steps().size()))throw bad("CHECKPOINT_PROGRESS_OR_FINALITY");
  var delta=zeros(ids);var release=zeros(ids);
  for(var id:ids){var d=cumulative.get(id).subtract(journal.get(id));if(d.signum()<0||d.compareTo(pending.get(id))>0)throw bad("INVALID_ACCOUNT_DELTA");delta.put(id,d);release.put(id,pending.get(id).subtract(d));}
  return new Settlement(m.digest(),expectedHead,identity,attemptCount,all,cumulative,delta,release,terminal);
 }
 private static boolean equal(Map<UUID,BigDecimal>a,Map<UUID,BigDecimal>b){return a.keySet().equals(b.keySet())&&a.entrySet().stream().allMatch(e->e.getValue().compareTo(b.get(e.getKey()))==0);}
 private static Map<UUID,BigDecimal> zeros(Set<UUID>ids){var out=new HashMap<UUID,BigDecimal>();ids.forEach(id->out.put(id,BigDecimal.ZERO));return out;}
 private static Map<UUID,BigDecimal> vector(Map<UUID,BigDecimal>raw){if(raw==null)throw bad("VECTOR_REQUIRED");var out=new HashMap<UUID,BigDecimal>();raw.forEach((k,v)->out.put(Objects.requireNonNull(k),units(v)));return Map.copyOf(out);}
 private static BigDecimal units(BigDecimal v){if(v==null||v.signum()<0||v.precision()>24||Math.abs(v.scale())>9)throw bad("DECIMAL_UNITS");var n=v.signum()==0?BigDecimal.ZERO:v.stripTrailingZeros();return n.scale()<0?n.setScale(0):n;}
 private static void hash(String v){if(v==null||!v.matches("[a-f0-9]{64}"))throw bad("HASH_REQUIRED");}
 private static String digestText(String v){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(v.getBytes(StandardCharsets.UTF_8)));}catch(Exception e){throw new IllegalStateException(e);}}
 private static IllegalArgumentException bad(String reason){return new IllegalArgumentException(reason);}
}
