// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.scheduler;

import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.math.BigDecimal;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;
import static io.github.isidorotrevino.planner.scheduler.CapacitySchedulerTest.*;

/** Bounded synthetic measurements, not a latency target or provider benchmark. */
class ScaleReviewTest {
  static final Map<String,String> observations=new TreeMap<>();
  @AfterAll static void record() throws Exception {
    Files.createDirectories(Path.of("target"));Files.writeString(Path.of("target/d3-scale-review.json"),"{\"scope\":\"single measured run per synthetic fixture; no SLA; per-fixture 5 s or 30 s safety budget\",\"fixtures\":["+String.join(",",observations.values())+"]}\n");
  }
  static void measure(boolean dag,int count,int budgetSeconds) {
    var projects=new ArrayList<Project>();var tasks=new ArrayList<Task>();var ops=new ArrayList<Operation>();
    var resources=new ArrayList<Resource>();var accounts=new ArrayList<Account>();var estimates=new ArrayList<Estimate>();var edges=new ArrayList<Edge>();
    for(int j=0;j<4;j++) {
      projects.add(new Project(id(100+j),ProjectState.ACTIVE,j,null,true));
      resources.add(resource(id(200+j),id(300+j),NOW));accounts.add(account(id(400+j),id(200+j),"WEEKLY",new BigDecimal("1000000"),BigDecimal.ZERO,BigDecimal.ZERO));
    }
    for(int i=0;i<count;i++) {
      var task=id(10000+i);var operation=id(20000+i);tasks.add(new Task(task,projects.get(i%4).id(),false,null));
      var op=new Op();op.id=operation;op.task=task;
      if(dag && i>0){op.eligibility=Eligibility.BLOCKED;op.reasons=List.of(Reason.DEPENDENCY_NOT_READY);}
      ops.add(op.build());
      for(int j=0;j<4;j++)estimates.add(estimate(operation,id(200+j),Map.of(id(400+j),BigDecimal.ONE),Duration.ofMinutes(1)));
    }
    if(dag)outer:for(int distance=1;distance<count;distance++)for(int i=0;i+distance<count;i++) {
      edges.add(new Edge(taskNode(id(10000+i)),taskNode(id(10000+i+distance))));if(edges.size()==5000)break outer;
    }
    var snapshot=new Snapshot(projects,tasks,ops,resources,accounts,estimates,List.of(),List.of(),edges,Map.of(),List.of(),true);
    var request=new Request(SCHEMA_VERSION,NOW,ZoneId.of("Europe/Madrid"),"b".repeat(64),"manual-v1",new Limits(1000,5000,4000,Duration.ofSeconds(budgetSeconds)),false);
    long started=System.nanoTime();var result=new CapacityScheduler().plan(request,snapshot);long elapsed=System.nanoTime()-started;
    assertNotEquals(Status.INVALID_INPUT,result.status());assertEquals(count,result.decisions().size());assertTrue(result.reviewOnly());
    var tentative=result.decisions().stream().filter(d->d.disposition()==Disposition.TENTATIVE).count();
    if(result.status()==Status.LIMIT_EXCEEDED)assertEquals(0,tentative,"Never return a tentative prefix after exhaustion");
    else assertEquals(dag?1:count,tentative);
    observations.put(dag?"dag":"independent-"+count+"-"+budgetSeconds+"s","{\"name\":\""+(dag?"dag":"independent-"+count+"-"+budgetSeconds+"s")+"\",\"operations\":"+count+",\"resources\":4,\"candidates\":"+estimates.size()+",\"edges\":"+edges.size()+",\"compute_budget_s\":"+budgetSeconds+",\"elapsed_ns\":"+elapsed+",\"status\":\""+result.status()+"\",\"tentative\":"+tentative+"}");
  }
  @Test void smallerBaselineHasTwoHundredOperations(){measure(false,200,5);}
  @Test void independentThousandWithThirtySecondBudget(){measure(false,1000,30);}
  @Test void independentThousandOperationsAndFourResources(){measure(false,1000,5);}
  @Test void fiveThousandActiveEdgesPreserveBlockedConsumers(){measure(true,1000,5);}
}
