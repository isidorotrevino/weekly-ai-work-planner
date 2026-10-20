// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.scheduler;

import java.nio.file.*;
import java.net.*;
import java.util.*;
import javax.tools.ToolProvider;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.scheduler.CapacitySchedulerTest.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;

/** Compile the exact pre-optimization source in an isolated class loader, sharing DTOs. */
class OptimizationParityTest {
  static URLClassLoader loader;
  static java.lang.reflect.Constructor<?> constructor;
  static java.lang.reflect.Method plan;
  @BeforeAll static void baseline() throws Exception {
    var source=Path.of("target/baseline-source/io/github/isidorotrevino/planner/scheduler/CapacityScheduler.java");Files.createDirectories(source.getParent());
    try(var in=OptimizationParityTest.class.getResourceAsStream("/d3-baseline/CapacityScheduler.java")){Files.copy(Objects.requireNonNull(in),source,StandardCopyOption.REPLACE_EXISTING);}
    var classes=Path.of("target/baseline-classes");Files.createDirectories(classes);
    assertEquals(0,ToolProvider.getSystemJavaCompiler().run(null,null,null,"--release","21","-classpath",System.getProperty("java.class.path"),"-d",classes.toString(),source.toString()));
    loader=new URLClassLoader(new URL[]{classes.toUri().toURL()},OptimizationParityTest.class.getClassLoader()) {
      @Override protected Class<?> loadClass(String name,boolean resolve) throws ClassNotFoundException {
        if(name.equals(CapacityScheduler.class.getName()) || name.startsWith(CapacityScheduler.class.getName()+"$")) {
          synchronized(getClassLoadingLock(name)){var c=findLoadedClass(name);if(c==null)c=findClass(name);if(resolve)resolveClass(c);return c;}
        }
        return super.loadClass(name,resolve);
      }
    };
    var type=loader.loadClass(CapacityScheduler.class.getName());constructor=type.getConstructor(java.util.function.LongSupplier.class);plan=type.getMethod("plan",Request.class,Snapshot.class);
  }
  @AfterAll static void close() throws Exception {if(loader!=null)loader.close();}
  static void compare(Fixture f) throws Exception {
    var snapshot=f.snapshot();var expected=(Result)plan.invoke(constructor.newInstance((java.util.function.LongSupplier)()->0L),request(),snapshot);
    assertEquals(expected,new CapacityScheduler(()->0L).plan(request(),snapshot));
  }
  @Test void heterogeneousDurationsAccountsWorkersTasksAndProtectedSlotsRemainIdentical() throws Exception {
    for(int seed=0;seed<60;seed++) {
      var random=new Random(seed);var f=new Fixture();f.operations.clear();f.estimates.clear();
      f.resources.add(resource(id(401),W,NOW));f.accounts.add(account(id(402),id(401),"SESSION",d("100"),d("0"),d("0")));
      for(int i=0;i<14;i++) {
        var task=i%3==0?T:id(1000+i);if(!task.equals(T))f.tasks.add(new Task(task,P,false,i%2==0?NOW.plusSeconds(3600):null));
        final int n=i;var op=id(2000+i);
        f.add(op,task,R,Map.of(A,d(Integer.toString(1+random.nextInt(12)))) ,java.time.Duration.ofMinutes(1+random.nextInt(20)),o->{
          if(n%4==0)o.exclusive=Set.of("workspace");
          if(n%5==0){o.previousResource=R;o.previousStart=NOW.plusSeconds(300);}
          if(n%6==0)o.wait=java.time.Duration.ofDays(8);
        });
        f.estimates.add(estimate(op,id(401),Map.of(id(402),d("2")),java.time.Duration.ofMinutes(1+random.nextInt(20))));
      }
      if(seed%2==0)f.occupied.add(new Occupancy(W,Set.of("workspace"),new Interval(NOW.plusSeconds(30),NOW.plusSeconds(180))));
      Collections.shuffle(f.operations,random);Collections.shuffle(f.estimates,random);compare(f);
    }
  }
  @Test void homogeneousCacheKeysStillRecheckCapacityApprovalAndEstimateExpiry() throws Exception {
    for(int seed=0;seed<20;seed++) {
      var f=new Fixture();f.operations.clear();f.estimates.clear();var random=new Random(seed);
      for(int i=0;i<30;i++) {
        final int n=i;var task=i%4==0?T:id(5000+i);if(!task.equals(T))f.tasks.add(new Task(task,P,false,null));
        f.add(id(6000+i),task,R,Map.of(A,d(Integer.toString(1+random.nextInt(6)))),java.time.Duration.ofMinutes(1),o->{
          if(n%5==0){o.approval=true;o.approvalUntil=NOW.plusSeconds(150);}
        });
      }
      compare(f);
    }
  }
  @Test void busyEndsCalendarGapsAndCachedNoSlotHaveIdenticalFullExplanations() throws Exception {
    for(boolean blocked:List.of(false,true)) {
      var f=new Fixture();f.operations.clear();f.estimates.clear();
      f.resources.set(0,new Resource(R,W,true,true,NOW,Set.of("code"),List.of(new Interval(NOW,NOW.plusSeconds(200)),new Interval(NOW.plusSeconds(400),NOW.plusSeconds(2000)))));
      f.occupied.add(new Occupancy(W,Set.of(),new Interval(NOW.plusSeconds(20),blocked?NOW.plus(java.time.Duration.ofDays(8)):NOW.plusSeconds(100))));
      f.occupied.add(new Occupancy(id(9000),Set.of("shared"),new Interval(NOW.plusSeconds(150),NOW.plusSeconds(500))));
      for(int i=0;i<12;i++) {
        var task=id(7000+i);f.tasks.add(new Task(task,P,false,null));
        f.add(id(8000+i),task,R,Map.of(A,d("1")),java.time.Duration.ofSeconds(60),o->o.exclusive=Set.of("shared"));
      }
      compare(f);
    }
  }
}
