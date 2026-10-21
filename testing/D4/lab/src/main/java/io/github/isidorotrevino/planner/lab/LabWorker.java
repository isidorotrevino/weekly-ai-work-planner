// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;

import io.github.isidorotrevino.planner.runtime.*;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;
import tools.jackson.databind.JsonNode;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.concurrent.locks.ReentrantLock;

@RestController @ConditionalOnProperty(name="lab.role",havingValue="worker")
class LabWorker {
 static final AtomicBoolean presenceInitialized=new AtomicBoolean();
 private final HttpClient client=LabSupport.client();
 private final FixtureSupervisor supervisor=FixtureSupervisor.open(Path.of("/state/supervisor"));
 private final Map<String,Object> state=new ConcurrentHashMap<>();
 private final AtomicBoolean launched=new AtomicBoolean();private volatile CountDownLatch continueCallback=new CountDownLatch(1);
 private final AtomicInteger executing=new AtomicInteger();private final AtomicBoolean recoveredTerminal=new AtomicBoolean();
 private volatile FixtureSupervisor.Running running;private volatile EffectJournal.SignedGrant grant;
 private volatile AuthoritySession authority;
 private final ReentrantLock lifecycle=new ReentrantLock();
 private final Map<String,Object> loopState=new ConcurrentHashMap<>();
 private volatile LoopSession loop;
 private final UUID presenceSession=UUID.randomUUID();private final AtomicLong presenceSequence=new AtomicLong();private final AtomicBoolean presenceReady=new AtomicBoolean();private Map<String,Object> openingPresence;
 LabWorker() throws Exception {
  var path=Path.of("/state/job.json");if(Files.exists(path)){state.putAll(LabSupport.JSON.convertValue(LabSupport.JSON.readTree(Files.readString(path)),Map.class));state.put("phase","RECOVERY_REQUIRED");launched.set(true);}else state.put("phase","IDLE");
  var loopPath=Path.of("/state/loop.json");if(Files.exists(loopPath)){loopState.putAll(LabSupport.JSON.convertValue(LabSupport.JSON.readTree(Files.readString(loopPath)),Map.class));loopState.put("phase","RECOVERY_REQUIRED");state.put("phase","RECOVERY_REQUIRED");launched.set(true);}
  if(Files.isDirectory(Path.of("/state/loop-commands"))){state.put("phase","RECOVERY_REQUIRED");launched.set(true);}
  Thread.startVirtualThread(()->{for(;;){try{presence();Thread.sleep(15000);}catch(Exception e){try{Thread.sleep(1000);}catch(InterruptedException stop){return;}}}});
 }
 private synchronized void presence() throws Exception {
  if(!presenceReady.get()){
   if(openingPresence==null){var head=LabSupport.request(client,"GET","https://control-plane:8443/lab/presence",null);openingPresence=new HashMap<>();openingPresence.put("command_id",presenceSession.toString());openingPresence.put("session_id",presenceSession.toString());openingPresence.put("expected_session",head.isNull()?null:LabSupport.text(head,"session_id"));}
   retry("https://control-plane:8443/lab/presence/open",openingPresence);presenceReady.set(true);
  }
  long next=presenceSequence.get()+1;var cid=UUID.nameUUIDFromBytes((presenceSession+":"+next).getBytes(java.nio.charset.StandardCharsets.UTF_8));
  var response=retry("https://control-plane:8443/d4/v1/commands",Map.of("schema_version","d4.worker.v1","command_id",cid.toString(),"correlation_id",cid.toString(),"request",Map.of("action","PRESENCE","session_id",presenceSession.toString(),"sequence",next))).path("result");
  if(response.path("sequence").asLong()!=next)throw new IllegalStateException("PRESENCE_SEQUENCE_MISMATCH");presenceSequence.set(next);presenceInitialized.set(true);
 }
 private void fixtureTree(JsonNode context,boolean restore) throws Exception {
  if(!context.has("tree_fixture"))return;var identity=LabSupport.identity(LabSupport.JSON.valueToTree(state.get("identity")));if(!"EXITED".equals(supervisor.observe(identity).phase()))throw new LabSupport.Denied("EXITED_TREE_WRITER_REQUIRED");var root=Path.of("/state/trees/"+identity.attempt());Files.createDirectories(root);
  for(var e:context.path("tree_fixture").path(restore?"base_files":"candidate_files").properties()){TreeVerifier.path(e.getKey());var p=root.resolve(e.getKey());Files.createDirectories(p.getParent());Files.write(p,Base64.getDecoder().decode(e.getValue().asText()));}forceDirectory(root);
 }
 @PostMapping("/lab/tree/restore") Object restoreTree(HttpServletRequest r)throws Exception{LabSupport.require(r,"driver");lifecycle.lock();try{if(!"CALLBACK_CONFIRMED".equals(state.get("phase")))throw new LabSupport.Denied("CONFIRMED_EXIT_REQUIRED");var i=LabSupport.JSON.valueToTree(state.get("info"));var ctx=LabSupport.JSON.readTree(Base64.getMimeDecoder().decode(LabSupport.text(i,"context_b64")));fixtureTree(ctx,true);return Map.of("candidate_restored",true);}finally{lifecycle.unlock();}}
 private static void forceDirectory(Path path) throws Exception {try(var c=java.nio.channels.FileChannel.open(path,StandardOpenOption.READ)){c.force(true);}}
 private void save(String phase) throws Exception {lifecycle.lock();try{state.put("phase",phase);LabSupport.atomic(Path.of("/state/job.json"),new TreeMap<>(state));forceDirectory(Path.of("/state"));}finally{lifecycle.unlock();}}
 private JsonNode command(Map<String,?> request,boolean persist) throws Exception {
  if(!presenceReady.get())throw new LabSupport.Denied("PRESENCE_SESSION_NOT_READY");
  var sessionRequest=new HashMap<String,Object>(request);sessionRequest.put("session_id",presenceSession.toString());
  var id=UUID.randomUUID();var envelope=Map.of("schema_version","d4.worker.v1","command_id",id.toString(),"correlation_id",id.toString(),"request",sessionRequest);
  if(persist){state.put("command_id",id.toString());if("CALLBACK".equals(request.get("action")))state.put("callback_command_id",id.toString());save(state.get("phase").toString());}
  Exception failure=null;for(int i=0;i<2;i++){try{return LabSupport.request(client,"POST","https://control-plane:8443/d4/v1/commands",envelope).path("result");}catch(Exception ex){failure=ex;Thread.sleep(200);}}throw failure;
 }
 @PostMapping("/lab/run") Object run(HttpServletRequest r){LabSupport.require(r,"driver");if(!launched.compareAndSet(false,true))throw new LabSupport.Denied("ALREADY_LAUNCHED");Thread.startVirtualThread(this::execute);return Map.of("accepted",true);}
 private void saveLoop(String phase) throws Exception {lifecycle.lock();try{loopState.put("phase",phase);LabSupport.atomic(Path.of("/state/loop.json"),new TreeMap<>(loopState));forceDirectory(Path.of("/state"));}finally{lifecycle.unlock();}}
 @GetMapping("/lab/loop/state") Object loopState(HttpServletRequest r){LabSupport.require(r,"driver","verifier");return new TreeMap<>(loopState);}
 @PostMapping("/lab/loop/start") Object startLoop(HttpServletRequest r) throws Exception {
  LabSupport.require(r,"driver");var b=LabSupport.body(r);if(b.size()!=3||!b.has("command_id")||!b.path("max_operations").isIntegralNumber()||!b.path("duration_seconds").isIntegralNumber())throw new LabSupport.Denied("EXPLICIT_LOOP_BUDGET_REQUIRED");
  var id=LabSupport.uuid(b,"command_id");if(!b.path("max_operations").canConvertToInt()||!b.path("duration_seconds").canConvertToInt())throw new LabSupport.Denied("BOUNDED_LOOP_REQUIRED");int max=b.path("max_operations").asInt(),seconds=b.path("duration_seconds").asInt();if(max<1||max>4||seconds<10||seconds>240)throw new LabSupport.Denied("BOUNDED_LOOP_REQUIRED");
  lifecycle.lock();try{
   var commands=Path.of("/state/loop-commands");var receipt=commands.resolve(id+".json");var accepted=Map.of("command_id",id.toString(),"accepted",true);
   if(Files.exists(receipt)){if(!LabSupport.JSON.readTree(Files.readString(receipt)).equals(b))throw new LabSupport.Denied("LOOP_COMMAND_CONFLICT");return accepted;}
   if((loop!=null&&loop.active.get())||!"IDLE".equals(state.get("phase"))||!launched.compareAndSet(false,true))throw new LabSupport.Denied("EXPLICIT_IDLE_REQUIRED");
   try{
    Files.createDirectories(commands);Files.writeString(receipt,LabSupport.JSON.writeValueAsString(b),StandardOpenOption.CREATE_NEW);
    try(var c=java.nio.channels.FileChannel.open(receipt,StandardOpenOption.WRITE)){c.force(true);}for(var path:List.of(commands,commands.getParent()))try(var c=java.nio.channels.FileChannel.open(path,StandardOpenOption.READ)){c.force(true);}
    loopState.clear();loopState.putAll(Map.of("command_id",id.toString(),"max_operations",max,"duration_seconds",seconds,"completed",0,"empty_polls",0));saveLoop("STARTING");loop=new LoopSession(max,seconds);Thread.startVirtualThread(loop::run);return accepted;
   }catch(Exception ex){state.put("phase","RECOVERY_REQUIRED");throw ex;}
  }finally{lifecycle.unlock();}
 }
 private void resetIdle(boolean archive) throws Exception {
  if(archive){var history=Path.of("/state/history");Files.createDirectories(history);LabSupport.atomic(history.resolve(((Map<?,?>)state.get("identity")).get("attempt")+".json"),new TreeMap<>(state));forceDirectory(history);forceDirectory(history.getParent());}
  if(authority!=null)authority.active.set(false);authority=null;state.clear();state.put("phase","IDLE");grant=null;running=null;save("IDLE");
 }
 private boolean retireCompleted() throws Exception {
  lifecycle.lock();try{
   if(!"CALLBACK_CONFIRMED".equals(state.get("phase")))throw new LabSupport.Denied("CONFIRMED_CALLBACK_REQUIRED");
   var status=LabSupport.request(client,"POST","https://control-plane:8443/lab/execution/status",Map.of("delivery_id",state.get("delivery_id")));
   var identity=LabSupport.identity(LabSupport.JSON.valueToTree(state.get("identity")));
   if(!identity.equals(LabSupport.identity(status))||!"d4.worker.execution-status.v1".equals(status.path("schema").asText()))throw new IllegalStateException("RETIREMENT_IDENTITY_MISMATCH");
   if(!status.path("retirable").asBoolean()){
    if(!"VERIFYING".equals(status.path("state").asText()))throw new LabSupport.Denied("EXECUTION_NOT_RETIRABLE");return false;
   }
   if(!Set.of("COMPLETED","RETRY_PENDING").contains(status.path("state").asText())||!"EXITED".equals(supervisor.observe(identity).phase()))throw new LabSupport.Denied("DURABLE_LOCAL_EXIT_REQUIRED");
   state.put("retirement",status);resetIdle(true);return true;
  }finally{lifecycle.unlock();}
 }
 private final class LoopSession {
  final int max;final long deadline;final AtomicBoolean active=new AtomicBoolean(true);int completed,empty,totalEmpty;
  LoopSession(int max,int seconds){this.max=max;deadline=System.nanoTime()+Duration.ofSeconds(seconds).toNanos();}
  void run(){
   try{
    while(System.nanoTime()<deadline&&completed<max){
     saveLoop("POLLING");state.put("loop_command_id",loopState.get("command_id"));execute();var phase=state.get("phase").toString();
     if("NO_ASSIGNMENT".equals(phase)){
      lifecycle.lock();try{resetIdle(false);empty++;loopState.put("empty_polls",++totalEmpty);saveLoop("IDLE_BACKOFF");}finally{lifecycle.unlock();}
      long delay=Math.min(5000,250L<<Math.min(empty-1,5))+ThreadLocalRandom.current().nextLong(101);Thread.sleep(Math.min(delay,Math.max(1,(deadline-System.nanoTime())/1000000)));continue;
     }
     if(!"CALLBACK_CONFIRMED".equals(phase)){saveLoop("PAUSED_"+phase);return;}
     saveLoop("WAITING_ACCEPTANCE");boolean retired=false;
     while(System.nanoTime()<deadline){if(retireCompleted()){retired=true;break;}Thread.sleep(1000);}
     if(!retired){saveLoop("PAUSED_BUDGET");return;}
     loopState.put("completed",++completed);saveLoop("RETIRED");empty=0;
    }
    saveLoop(completed==max?"COMPLETED":"BUDGET_EXHAUSTED");
   }catch(Exception ex){loopState.put("error",ex.getClass().getSimpleName());try{saveLoop("PAUSED_UNKNOWN");}catch(Exception ignored){}}
   finally{lifecycle.lock();try{active.set(false);if(loop==this&&"IDLE".equals(state.get("phase")))launched.set(false);}finally{lifecycle.unlock();}}
  }
 }
 private void execute(){
  executing.incrementAndGet();recoveredTerminal.set(false);continueCallback=new CountDownLatch(1);
  try {
   save("POLLING");var assignment=command(Map.of("action","POLL"),true).path("assignment");if(assignment.isNull()){save("NO_ASSIGNMENT");return;}
   var delivery=LabSupport.uuid(assignment,"delivery_id");state.put("delivery_id",delivery.toString());
   command(Map.of("action","ACK","delivery_id",delivery.toString()),true);save("ACKED");
   command(Map.of("action","START","delivery_id",delivery.toString()),true);save("STARTED");
   var grantCommand=UUID.randomUUID();state.put("grant_command_id",grantCommand.toString());save("GRANT_REQUESTED");
   long requestedAt=System.nanoTime();var response=retry("https://control-plane:8443/lab/grant",Map.of("command_id",grantCommand.toString(),"delivery_id",delivery.toString()));
   grant=LabSupport.grant(response.path("authorization"));var info=response.path("info");
   byte[] context=Base64.getMimeDecoder().decode(LabSupport.text(info,"context_b64"));if(!LabSupport.hash(context).equals(grant.grant().contextHash()))throw new IllegalStateException("CONTEXT_HASH_MISMATCH");
   if(!grant.grant().identity().worker().toString().equals(LabSupport.config("worker.id")))throw new IllegalStateException("WORKER_ASSIGNMENT_MISMATCH");
   state.put("identity",LabSupport.identityMap(grant.grant().identity()));state.put("authorization",LabSupport.grantMap(grant));state.put("info",info);
   LabSupport.request(client,"POST","https://effect-receiver:8443/lab/install",LabSupport.grantMap(grant));
   var manifest=LabSupport.JSON.readTree(context);var fixture=info.path("continuation").asBoolean()?FixtureSupervisor.Fixture.SUFFIX:FixtureSupervisor.Fixture.valueOf(LabSupport.text(manifest,"fixture"));
   if(info.path("multi_checkpoint").asBoolean())fixture=info.path("needs_checkpoint").asBoolean()?FixtureSupervisor.Fixture.PARTIAL:FixtureSupervisor.Fixture.SUFFIX;
   boolean prolonged=manifest.path("long_running").asBoolean()&&!info.path("continuation").asBoolean();
   if(prolonged)fixture=fixture==FixtureSupervisor.Fixture.PARTIAL?(manifest.path("fault_ignore_checkpoint").asBoolean()?FixtureSupervisor.Fixture.NONCOOPERATIVE_PARTIAL:FixtureSupervisor.Fixture.COOPERATIVE_PARTIAL):FixtureSupervisor.Fixture.LONG_SUCCESS;
   // This is the laboratory's deliberate missing-watchdog fault for S02/S04.
   if(fixture==FixtureSupervisor.Fixture.SURVIVOR && !manifest.path("fault_survive_lease").asBoolean())throw new IllegalStateException("SURVIVOR_REQUIRES_EXPLICIT_FIXTURE_FAULT");
   if(prolonged){authority=new AuthoritySession(delivery,requestedAt);authority.check();}
   running=supervisor.start(grant.grant().identity(),fixture);state.put("pid",running.pid());save("PROCESS_RUNNING");
   if(fixture==FixtureSupervisor.Fixture.SURVIVOR)return;
   if(prolonged){authority.start();long limit=System.nanoTime()+Duration.ofSeconds(120).toNanos();while(!running.awaitExit(Duration.ofMillis(200))){authority.check();if(System.nanoTime()>limit)throw new IllegalStateException("LAB_EXECUTION_LIMIT");}authority.check();}
   var outcome=running.await(prolonged?Duration.ZERO:Duration.ofSeconds(15));state.put("outcome",outcome);if(!outcome.stoppedObserved()||outcome.exitCode()!=0)throw new IllegalStateException("FIXTURE_FAILED");save("PROCESS_EXITED");fixtureTree(manifest,false);
   if(manifest.path("fault_absent_first_generation").asBoolean()&&grant.grant().identity().generation()==1){save("ABSENCE_READY");return;}
   if(manifest.path("fault_pause_effect_first").asBoolean()&&grant.grant().identity().generation()==1){save("WAITING_EFFECT");if(!continueCallback.await(90,TimeUnit.SECONDS))throw new IllegalStateException("EFFECT_BARRIER_TIMEOUT");}
   effect();save("EFFECT_APPLIED");
   if(info.path("multi_checkpoint").asBoolean()?info.path("needs_checkpoint").asBoolean():info.path("is_checkpoint_fixture").asBoolean()&&!info.path("continuation").asBoolean()){if(authority!=null)authority.check();save("CHECKPOINT_READY");return;}
   if(authority!=null)authority.active.set(false); // no more process/effects; callback hands off to verification
   if(manifest.path("fault_pause_callback").asBoolean()){save("WAITING_CALLBACK");if(!continueCallback.await(180,TimeUnit.SECONDS))throw new IllegalStateException("CALLBACK_BARRIER_TIMEOUT");}
   if(recoveredTerminal.get())return;
   var entries=new ArrayList<Map<String,Object>>();for(var account:info.path("accounts"))entries.add(Map.of("account_id",LabSupport.text(account,"account_id"),"settled",account.path("units").decimalValue(),"consumed",info.path("multi_checkpoint").asBoolean()?info.path("incremental_vector").path(LabSupport.text(account,"account_id")).decimalValue():info.path("incremental_units").isNumber()?info.path("incremental_units").decimalValue():info.path("consumed_units").decimalValue()));
   try{command(Map.of("action","CALLBACK","delivery_id",delivery.toString(),"payload",Map.of("entries",entries)),true);save("CALLBACK_CONFIRMED");}
   catch(Exception lost){state.put("error","CALLBACK_RESULT_UNCONFIRMED");save("CALLBACK_UNKNOWN");}
  }catch(Exception e){if(authority!=null){authority.active.set(false);if(running!=null)try{state.put("outcome",running.stop());}catch(Exception ignored){state.put("stop_unconfirmed",true);}}state.put("error",e.getClass().getSimpleName());try{save("BLOCKED_UNKNOWN");}catch(Exception ignored){}}finally{executing.decrementAndGet();}
 }
 private JsonNode retry(String url,Object body) throws Exception {
  Exception failure=null;for(int i=0;i<2;i++){try{return LabSupport.request(client,"POST",url,body);}catch(LabSupport.Rejected rejected){throw rejected;}catch(Exception ex){failure=ex;if(i==0)Thread.sleep(200);}}throw failure;
 }
 private static long deadline(EffectJournal.Grant g,long requestStarted){return requestStarted+Duration.between(g.issuedAt(),g.expiresAt()).minusSeconds(10).toNanos();}
 private final class AuthoritySession {
  final UUID delivery;final ExecutionIdentity identity=grant.grant().identity();final AtomicBoolean active=new AtomicBoolean(true),lost=new AtomicBoolean();
  volatile long expires;volatile UUID checkpoint;volatile long checkpointDeadline;FixtureSupervisor.Running process;
  AuthoritySession(UUID delivery,long requestStarted){this.delivery=delivery;expires=deadline(grant.grant(),requestStarted);}
  void check(){if(!active.get()||lost.get()||System.nanoTime()>=expires||!Instant.now().isBefore(grant.grant().expiresAt().minusSeconds(10)))throw new IllegalStateException("AUTHORITY_UNCONFIRMED");}
  void fail(String reason){
   if(!active.get()||!lost.compareAndSet(false,true))return;active.set(false);
   FixtureSupervisor.Outcome outcome=null;try{outcome=process.stop();}catch(Exception ignored){}
   lifecycle.lock();try{if(authority!=this)return;state.put("authority_failure",Objects.requireNonNullElse(reason,"AUTHORITY_UNCONFIRMED"));if(outcome!=null)state.put("outcome",outcome);else state.put("stop_unconfirmed",true);try{save(outcome!=null&&outcome.stoppedObserved()&&"CHECKPOINT_READY".equals(state.get("phase"))?"CHECKPOINT_READY":"BLOCKED_UNKNOWN");}catch(Exception ignored){}}finally{lifecycle.unlock();}
  }
  void start(){
   process=running;
   Thread.ofPlatform().daemon(true).name("execution-watchdog").start(()->{while(active.get()){try{check();if(checkpoint!=null&&System.nanoTime()>checkpointDeadline&&!process.awaitExit(Duration.ZERO))throw new IllegalStateException("CHECKPOINT_COOPERATION_TIMEOUT");Thread.sleep(100);}catch(Exception ex){fail(ex.getMessage());return;}}});
   Thread.startVirtualThread(()->{long next=System.nanoTime()+Duration.ofSeconds(10).toNanos();while(active.get()){try{
    if(System.nanoTime()>=next){renew(this);next=System.nanoTime()+Duration.ofSeconds(10).toNanos();}
    if(checkpoint==null&&LabSupport.JSON.valueToTree(state.get("info")).path("is_checkpoint_fixture").asBoolean())signal();
    Thread.sleep(1000);
   }catch(Exception ex){fail(ex.getClass().getSimpleName());return;}}});
  }
  void signal() throws Exception {
   var signal=LabSupport.request(client,"POST","https://control-plane:8443/lab/checkpoint/signal",Map.of("delivery_id",delivery.toString()));
   if(!identity.equals(LabSupport.identity(signal)))throw new IllegalStateException("CHECKPOINT_SIGNAL_IDENTITY_MISMATCH");
   if(!signal.path("request_id").isNull()){lifecycle.lock();try{if(!active.get()||authority!=this)return;var id=LabSupport.uuid(signal,"request_id");process.requestCheckpoint(id);checkpointDeadline=System.nanoTime()+Duration.ofSeconds(15).toNanos();checkpoint=id;state.put("checkpoint_request_id",id.toString());save("CHECKPOINT_REQUESTED");}finally{lifecycle.unlock();}}
  }
 }
 private void renew(AuthoritySession session) throws Exception {
  lifecycle.lock();try{
  session.check();long started=System.nanoTime();var command=UUID.randomUUID();state.put("renew_command_id",command.toString());save(state.get("phase").toString());
  var response=retry("https://control-plane:8443/lab/grant",Map.of("command_id",command.toString(),"delivery_id",session.delivery.toString()));var next=LabSupport.grant(response.path("authorization"));var old=grant.grant();var g=next.grant();
  if(!old.identity().equals(g.identity())||!old.receiverId().equals(g.receiverId())||!old.intentHash().equals(g.intentHash())||!old.contextHash().equals(g.contextHash())||!old.policyHash().equals(g.policyHash())||!old.steps().equals(g.steps())||g.expiresAt().isBefore(old.expiresAt()))throw new IllegalStateException("RENEWAL_BINDING_MISMATCH");
  session.check(); // a late response cannot reactivate a stopped session
  retry("https://effect-receiver:8443/lab/install",LabSupport.grantMap(next));
  session.check();if(!session.active.get())throw new IllegalStateException("RENEWAL_AFTER_STOP");grant=next;session.expires=deadline(g,started);session.check();state.put("authorization",LabSupport.grantMap(next));state.put("renew_count",((Number)state.getOrDefault("renew_count",0)).intValue()+1);save(state.get("phase").toString());
  }finally{lifecycle.unlock();}
 }
 private Object effect() throws Exception {
  lifecycle.lock();try{
  if(authority!=null)authority.check();
  var currentInfo=LabSupport.JSON.valueToTree(state.get("info"));var step=currentInfo.path("multi_checkpoint").asBoolean()?LabSupport.text(currentInfo,"current_step"):grant.grant().steps().contains("step-1")?"step-1":"step-2";
  boolean checkpoint=LabSupport.JSON.valueToTree(state.get("info")).path("is_checkpoint_fixture").asBoolean();
  var value="synthetic-effect:"+grant.grant().identity().operation()+(checkpoint?":"+step:"");
  return LabSupport.request(client,"POST","https://effect-receiver:8443/lab/effect",Map.of("authorization",LabSupport.grantMap(grant),"step",step,"payload",Base64.getEncoder().encodeToString(value.getBytes(java.nio.charset.StandardCharsets.UTF_8))));
  }finally{lifecycle.unlock();}
 }
 @GetMapping("/lab/state") Object state(HttpServletRequest r){LabSupport.require(r,"driver","verifier");return new TreeMap<>(state);}
 @PostMapping("/lab/next") Object next(HttpServletRequest r) throws Exception {
  lifecycle.lock();try{
  LabSupport.require(r,"driver");if(loop!=null&&loop.active.get())throw new LabSupport.Denied("LOOP_STILL_ACTIVE");
  if("CALLBACK_CONFIRMED".equals(state.get("phase"))){if(!retireCompleted())throw new LabSupport.Denied("ACCEPTANCE_STILL_PENDING");launched.set(false);return Map.of("ready",true);}
  if(!Set.of("CHECKPOINT_READY","RECOVERY_REQUIRED").contains(state.get("phase")))throw new LabSupport.Denied("NO_CHECKPOINT_PROCESS");
  var current=LabSupport.request(client,"GET","https://control-plane:8443/d4/v1/assignments/current",null);
  if(!current.isNull())throw new LabSupport.Denied("OLD_ASSIGNMENT_STILL_ACTIVE");
  if(!state.containsKey("identity")){if(supervisor.hasUnresolvedAttempts())throw new LabSupport.Denied("LOCAL_HISTORY_UNRESOLVED");resetIdle(false);launched.set(false);return Map.of("ready",true);}
  resetIdle(true);launched.set(false);return Map.of("ready",true);
  }finally{lifecycle.unlock();}
 }
 private JsonNode recoveredStatus()throws Exception{
  var status=LabSupport.request(client,"POST","https://control-plane:8443/lab/execution/status",Map.of("delivery_id",state.get("delivery_id")));
  var identity=LabSupport.identity(LabSupport.JSON.valueToTree(state.get("identity")));
  if(!identity.equals(LabSupport.identity(status))||!"d4.worker.execution-status.v1".equals(status.path("schema").asText())||!status.path("retirable").asBoolean()||!Set.of("COMPLETED","RETRY_PENDING").contains(status.path("state").asText())||!"EXITED".equals(supervisor.observe(identity).phase()))throw new LabSupport.Denied("RECOVERED_TERMINAL_EXIT_REQUIRED");return status;
 }
 @PostMapping("/lab/recovery/retire") Object retireRecovered(HttpServletRequest r)throws Exception{
  LabSupport.require(r,"driver");lifecycle.lock();try{
   if(loop!=null&&loop.active.get())throw new LabSupport.Denied("LOOP_STILL_ACTIVE");
   if(!Set.of("WAITING_CALLBACK","CALLBACK_UNKNOWN","BLOCKED_UNKNOWN","RECOVERY_REQUIRED","ABSENCE_READY").contains(state.get("phase")))throw new LabSupport.Denied("EXPLICIT_RECOVERY_RETIREMENT_REQUIRED");
   recoveredStatus();recoveredTerminal.set(true);continueCallback.countDown();
  }finally{lifecycle.unlock();}
  long until=System.nanoTime()+TimeUnit.SECONDS.toNanos(4);while(executing.get()!=0&&System.nanoTime()<until)Thread.sleep(25);
  lifecycle.lock();try{if(executing.get()!=0)throw new LabSupport.Denied("LOCAL_EXECUTION_NOT_QUIESCENT");state.put("retirement",recoveredStatus());resetIdle(true);launched.set(false);return Map.of("ready",true);}finally{lifecycle.unlock();}
 }
 @PostMapping("/lab/continue") Object resume(HttpServletRequest r){LabSupport.require(r,"driver");continueCallback.countDown();return Map.of("released",true);}
 @PostMapping("/lab/late-effect") Object late(HttpServletRequest r) throws Exception {LabSupport.require(r,"driver");if(grant==null)throw new LabSupport.Denied("NO_GRANT");return effect();}
 @PostMapping("/lab/stop") Object stop(HttpServletRequest r) throws Exception {LabSupport.require(r,"driver");if(running==null)throw new LabSupport.Denied("NO_ACTIVE_PROCESS");if(authority!=null)authority.active.set(false);var result=running.stop();state.put("outcome",result);save("STOPPED");return result;}
 @PostMapping("/lab/raw") Object raw(HttpServletRequest r) throws Exception {LabSupport.require(r,"driver");var body=LabSupport.body(r);return command(LabSupport.JSON.convertValue(body,Map.class),false);}
}
