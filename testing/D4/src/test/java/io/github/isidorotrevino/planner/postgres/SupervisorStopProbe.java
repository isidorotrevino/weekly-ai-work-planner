// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import io.github.isidorotrevino.planner.runtime.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;

/** Separate JVM so a single-carrier starvation regression cannot hang JUnit. */
public final class SupervisorStopProbe {
 public static void main(String[] args)throws Exception {
  var root=Path.of(args[0]);var supervisor=FixtureSupervisor.create(root);
  var identity=new ExecutionIdentity(UUID.randomUUID(),UUID.randomUUID(),UUID.randomUUID(),UUID.randomUUID(),1);
  try(var running=supervisor.start(identity,FixtureSupervisor.Fixture.IGNORE_TERM)){
   var ready=root.resolve("attempts/"+identity.attempt()+"/ready");long limit=System.nanoTime()+Duration.ofSeconds(5).toNanos();
   while(!Files.exists(ready)){if(System.nanoTime()>limit)throw new IllegalStateException("NOT_READY");Thread.sleep(10);}
   var first=new CompletableFuture<FixtureSupervisor.Outcome>();
   Thread.startVirtualThread(()->{try{first.complete(running.stop());}catch(Exception e){first.completeExceptionally(e);}});
   Thread.sleep(400); // first stop is waiting for the fixture's delayed shutdown hook
   var second=new CompletableFuture<FixtureSupervisor.Outcome>();
   Thread.startVirtualThread(()->{try{second.complete(running.stop());}catch(Exception e){second.completeExceptionally(e);}});
   var one=first.get(8,TimeUnit.SECONDS);var two=second.get(2,TimeUnit.SECONDS);
   if(!one.stoppedObserved()||!one.equals(two))throw new IllegalStateException("STOP_NOT_CONFIRMED");
   System.out.println("SINGLE_CARRIER_STOP_CONFIRMED");
  }
 }
}
