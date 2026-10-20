// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.runtime;
import java.nio.file.*;
import java.time.*;
/** Trusted finite fixtures only. Never accepts a shell command or provider key. */
public final class SyntheticFixtureMain {
  public static void main(String[] args) throws Exception {
    var fixture=FixtureSupervisor.Fixture.valueOf(args[0]);var gate=Path.of(args[1]);
    long deadline=System.nanoTime()+Duration.ofSeconds(5).toNanos();
    while(!Files.exists(gate)){if(System.nanoTime()>deadline)System.exit(4);Thread.sleep(10);}
    switch(fixture){
      case SUCCESS -> System.out.println("{\"fixture\":\"SUCCESS\",\"candidate\":true}");
      case PARTIAL, SUFFIX -> System.out.println("{\"fixture\":\""+fixture.name()+"\",\"candidate\":true}");
      case LONG_SUCCESS -> {Files.createFile(gate.resolveSibling("ready"));Thread.sleep(70000);System.out.println("{\"fixture\":\"SUCCESS\",\"candidate\":true}");}
      case COOPERATIVE_PARTIAL, NONCOOPERATIVE_PARTIAL -> {
        Files.createFile(gate.resolveSibling("ready"));var request=gate.resolveSibling("checkpoint.request");
        long limit=System.nanoTime()+Duration.ofSeconds(150).toNanos();
        for(;;){
          if(System.nanoTime()>limit)throw new IllegalStateException("CHECKPOINT_NOT_REQUESTED");
          if(fixture==FixtureSupervisor.Fixture.COOPERATIVE_PARTIAL && Files.exists(request)){
            var lines=Files.readAllLines(request);
            if(lines.size()!=3||!lines.get(0).equals("d4.fixture.checkpoint.v1")||!lines.get(1).equals(args[3]))throw new IllegalStateException("CHECKPOINT_BINDING_MISMATCH");
            java.util.UUID.fromString(lines.get(2));Thread.sleep(500); // finite safe boundary
            System.out.println("{\"fixture\":\"PARTIAL\",\"candidate\":true}");break;
          }
          Thread.sleep(20);
        }
      }
      case WAIT -> {Files.createFile(gate.resolveSibling("ready"));Thread.sleep(30000);}
      case SURVIVOR -> {Files.createFile(gate.resolveSibling("ready"));Thread.sleep(180000);}
      case NOISY -> {for(int i=0;i<10000;i++){System.out.println("synthetic bounded-log fixture");System.err.println("synthetic stderr fixture");}}
      case IGNORE_TERM -> {Runtime.getRuntime().addShutdownHook(new Thread(()->{try{Thread.sleep(30000);}catch(InterruptedException ignored){}}));Files.createFile(gate.resolveSibling("ready"));Thread.sleep(30000);}
      case DESCENDANT -> {
        var child=new ProcessBuilder(Path.of(System.getProperty("java.home"),"bin","java").toString(),"-cp",args[2],SyntheticFixtureMain.class.getName(),"WAIT",args[1],args[2]).inheritIO().start();
        Runtime.getRuntime().addShutdownHook(new Thread(()->{try{child.waitFor();}catch(InterruptedException ignored){}}));child.waitFor();
      }
    }
  }
}
