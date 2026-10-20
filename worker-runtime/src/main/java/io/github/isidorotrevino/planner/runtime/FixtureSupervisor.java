// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.runtime;

import java.io.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.security.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.ReentrantLock;

/** Linux trusted-fixture supervisor. Facts are candidates, not verifier evidence. */
public final class FixtureSupervisor {
  public enum Fixture { SUCCESS, WAIT, NOISY, IGNORE_TERM, DESCENDANT, SURVIVOR, PARTIAL, SUFFIX, LONG_SUCCESS, COOPERATIVE_PARTIAL, NONCOOPERATIVE_PARTIAL }
  public record Observation(String phase,long pid,long group,String bootId,String startTicks) { }
  public record Outcome(boolean stoppedObserved,boolean timedOut,Integer exitCode,long stdoutBytes,long stderrBytes,boolean stdoutTruncated,boolean stderrTruncated,String stdoutHash,String stderrHash) { }
  private final Path root;
  private FixtureSupervisor(Path root){this.root=root.toAbsolutePath().normalize();}
  public static FixtureSupervisor create(Path root) throws IOException {
    Files.createDirectory(root);Files.setPosixFilePermissions(root,java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
    Files.createDirectory(root.resolve("attempts"));Files.createFile(root.resolve("lock"));Files.writeString(root.resolve("initialized"),UUID.randomUUID().toString());forceDirectory(root);return new FixtureSupervisor(root);
  }
  public static FixtureSupervisor open(Path root) throws IOException {if(!Files.isRegularFile(root.resolve("initialized")))throw new IOException("SUPERVISOR_HISTORY_UNAVAILABLE");return new FixtureSupervisor(root);}
  private Path job(ExecutionIdentity identity){return root.resolve("attempts").resolve(identity.attempt().toString());}
  /** Local recovery candidate only. Missing/corrupt history remains unresolved. */
  public boolean hasUnresolvedAttempts() {
    try(var jobs=Files.list(root.resolve("attempts"))){for(var path:jobs.toList()){var data=latest(path);if(data==null||!resolved(path,data))return true;}return false;}
    catch(IOException|RuntimeException ex){return true;}
  }
  public Observation observe(ExecutionIdentity identity) {
    try {
      var data=latest(job(identity));if(data==null||!identity.key().equals(data.getProperty("identity")))return new Observation("UNKNOWN",0,0,null,null);
      var phase=data.getProperty("phase");long pid=Long.parseLong(data.getProperty("pid","0")),group=Long.parseLong(data.getProperty("group","0"));
      if("RUNNING".equals(phase) && (!boot().equals(data.getProperty("boot"))||!matches(pid,data.getProperty("ticks"),group)))phase="UNKNOWN";
      if("START_INTENT".equals(phase))phase="UNKNOWN";
      if("EXITED".equals(phase)&&!resolved(job(identity),data))phase="UNKNOWN";
      return new Observation(phase,pid,group,data.getProperty("boot"),data.getProperty("ticks"));
    }catch(IOException|RuntimeException e){return new Observation("UNKNOWN",0,0,null,null);}
  }
  public Running start(ExecutionIdentity identity,Fixture fixture) throws Exception {
    if(!Files.isExecutable(Path.of("/usr/bin/setsid"))||!Files.isExecutable(Path.of("/bin/kill")))throw new IOException("LINUX_FIXTURE_TOOLS_UNAVAILABLE");
    var channel=FileChannel.open(root.resolve("lock"),StandardOpenOption.WRITE);FileLock held;
    try{held=channel.tryLock();}catch(OverlappingFileLockException ex){channel.close();throw new IOException("WORKSPACE_BUSY");}
    if(held==null){channel.close();throw new IOException("WORKSPACE_BUSY");}
    Process process=null;boolean handedOff=false;
    try {
      try(var jobs=Files.list(root.resolve("attempts"))){for(var p:jobs.toList()){var prior=latest(p);if(prior==null||!resolved(p,prior))throw new IOException("PRIOR_PROCESS_UNRESOLVED");}}
      var work=job(identity);Files.createDirectory(work);forceDirectory(work.getParent());var data=new Properties();data.setProperty("identity",identity.key());data.setProperty("fixture",fixture.name());data.setProperty("phase","START_INTENT");event(work,data,1);
      var classes=Path.of(SyntheticFixtureMain.class.getProtectionDomain().getCodeSource().getLocation().toURI()).toString();
      var builder=new ProcessBuilder("/usr/bin/setsid",Path.of(System.getProperty("java.home"),"bin","java").toString(),"-cp",classes,SyntheticFixtureMain.class.getName(),fixture.name(),work.resolve("go").toString(),classes,identity.key()).directory(work.toFile());
      builder.environment().clear();builder.environment().put("LC_ALL","C");process=builder.start();
      long pid=process.pid();String[] stat=null;long deadline=System.nanoTime()+Duration.ofSeconds(2).toNanos();
      while(System.nanoTime()<deadline){stat=stat(pid);if(Long.parseLong(stat[2])==pid)break;Thread.sleep(10);}
      if(stat==null||Long.parseLong(stat[2])!=pid)throw new IOException("PROCESS_GROUP_NOT_CONFIRMED");
      data.setProperty("phase","RUNNING");data.setProperty("pid",Long.toString(pid));data.setProperty("group",Long.toString(pid));data.setProperty("boot",boot());data.setProperty("ticks",stat[19]);event(work,data,2);
      var result=new Running(work,data,process,channel,held);Files.createFile(work.resolve("go"));handedOff=true;return result;
    }finally{if(!handedOff){if(process!=null){process.destroyForcibly();process.waitFor(2,TimeUnit.SECONDS);}held.release();channel.close();}}
  }
  public final class Running implements AutoCloseable {
    private final Path work;private final Properties data;private final Process process;private final FileChannel lockChannel;private final FileLock held;
    private final Capture stdout,stderr;private final Thread outThread,errThread;private volatile Outcome outcome;
    private final ReentrantLock control=new ReentrantLock();
    Running(Path work,Properties data,Process process,FileChannel channel,FileLock held) throws IOException {
      this.work=work;this.data=data;this.process=process;lockChannel=channel;this.held=held;
      stdout=new Capture(process.getInputStream(),work.resolve("stdout.bin"));stderr=new Capture(process.getErrorStream(),work.resolve("stderr.bin"));
      // Java 21 process pipes may pin a virtual carrier in native blocking reads.
      // Exactly two dedicated drainers per active process, bounded by workspace lock.
      outThread=Thread.ofPlatform().daemon(true).name("fixture-stdout").start(stdout);
      errThread=Thread.ofPlatform().daemon(true).name("fixture-stderr").start(stderr);
    }
    public long pid(){return process.pid();}
    /** Waits only for the leader. A timeout neither signals nor proves group stop.
     * Does not hold the finalization monitor: a watchdog may call stop concurrently. */
    public boolean awaitExit(Duration timeout) throws InterruptedException {
      checkTimeout(timeout);
      return process.waitFor(timeout.toMillis(),TimeUnit.MILLISECONDS);
    }
    /** Bounded explicit group stop and durable candidate observation. */
    public Outcome stop() throws Exception {return await(Duration.ZERO);}
    /** Fixed local channel for trusted checkpoint fixtures; never a shell command. */
    public void requestCheckpoint(UUID request) throws IOException {
      control.lock();try {
      Objects.requireNonNull(request,"request");
      if(!Set.of("COOPERATIVE_PARTIAL","NONCOOPERATIVE_PARTIAL").contains(data.getProperty("fixture")))throw new IOException("FIXTURE_NOT_COOPERATIVE");
      var path=work.resolve("checkpoint.request");var bytes=("d4.fixture.checkpoint.v1\n"+data.getProperty("identity")+"\n"+request+"\n").getBytes(java.nio.charset.StandardCharsets.UTF_8);
      if(Files.exists(path)){if(!Arrays.equals(bytes,Files.readAllBytes(path)))throw new IOException("CHECKPOINT_REQUEST_CONFLICT");return;}
      if(outcome!=null||!process.isAlive())throw new IOException("PROCESS_NOT_RUNNING");
      var pending=work.resolve("checkpoint.request.pending");
      try(var c=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){var b=ByteBuffer.wrap(bytes);while(b.hasRemaining())c.write(b);c.force(true);}
      Files.move(pending,path,StandardCopyOption.ATOMIC_MOVE);forceDirectory(work);
      }finally{control.unlock();}
    }
    public Outcome await(Duration timeout) throws Exception {
      control.lock();try {
      if(outcome!=null)return outcome;
      checkTimeout(timeout);
      boolean timedOut=!process.waitFor(timeout.toMillis(),TimeUnit.MILLISECONDS);
      if(timedOut && process.isAlive()){
        signal("TERM");process.waitFor(1500,TimeUnit.MILLISECONDS);
        if(process.isAlive()){signal("KILL");process.waitFor(2,TimeUnit.SECONDS);}
      }
      boolean stopped=!process.isAlive() && absent(process.pid());
      outThread.join(2000);errThread.join(2000);
      if(outThread.isAlive()||errThread.isAlive()||stdout.failure!=null||stderr.failure!=null)stopped=false;
      for(var path:List.of(work.resolve("stdout.bin"),work.resolve("stderr.bin")))try(var c=FileChannel.open(path,StandardOpenOption.WRITE)){c.force(true);}
      var outHash=hash(work.resolve("stdout.bin"));var errHash=hash(work.resolve("stderr.bin"));
      data.setProperty("phase",stopped?"EXITED":"UNKNOWN");data.setProperty("timed_out",Boolean.toString(timedOut));
      data.setProperty("stdout_sha256",outHash);data.setProperty("stderr_sha256",errHash);data.setProperty("stdout_truncated",Boolean.toString(stdout.truncated));data.setProperty("stderr_truncated",Boolean.toString(stderr.truncated));event(work,data,3);
      outcome=new Outcome(stopped,timedOut,process.isAlive()?null:process.exitValue(),stdout.written,stderr.written,stdout.truncated,stderr.truncated,outHash,errHash);
      if(stopped){held.release();lockChannel.close();}return outcome;
      }finally{control.unlock();}
    }
    private void signal(String signal) throws Exception {
      if(!boot().equals(data.getProperty("boot"))||!matches(process.pid(),data.getProperty("ticks"),process.pid()))throw new IOException("PROCESS_IDENTITY_UNKNOWN");
      var kill=new ProcessBuilder("/bin/kill","-"+signal,"--","-"+process.pid()).start();if(!kill.waitFor(2,TimeUnit.SECONDS)||kill.exitValue()!=0)throw new IOException("PROCESS_STOP_UNCONFIRMED");
    }
    @Override public void close() throws Exception {if(outcome==null)await(Duration.ZERO);if(!outcome.stoppedObserved())throw new IOException("PROCESS_STOP_UNCONFIRMED");}
  }
  private static void checkTimeout(Duration timeout){
    Objects.requireNonNull(timeout,"timeout");
    if(timeout.isNegative()||timeout.compareTo(Duration.ofSeconds(30))>0)throw new IllegalArgumentException("Fixture timeout must be 0..30 seconds");
  }
  private static final class Capture implements Runnable {
    final InputStream input;final Path output;long written;boolean truncated;IOException failure;
    Capture(InputStream input,Path output){this.input=input;this.output=output;}
    @Override public void run(){try(var in=input;var out=Files.newOutputStream(output,StandardOpenOption.CREATE_NEW)){
      byte[] buffer=new byte[4096];int count;while((count=in.read(buffer))!=-1){int keep=(int)Math.min(count,65536-written);if(keep>0){out.write(buffer,0,keep);written+=keep;}if(keep<count)truncated=true;}
    }catch(IOException e){failure=e;}}
  }
  private static boolean absent(long group) throws Exception {
    var builder=new ProcessBuilder("/bin/kill","-0","--","-"+group).redirectErrorStream(true);builder.environment().put("LC_ALL","C");var p=builder.start();
    if(!p.waitFor(2,TimeUnit.SECONDS)){p.destroyForcibly();return false;}
    var message=new String(p.getInputStream().readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);
    return p.exitValue()!=0 && message.contains("No such process");
  }
  private static String boot() throws IOException{return Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).strip();}
  private static String[] stat(long pid) throws IOException{var text=Files.readString(Path.of("/proc/"+pid+"/stat"));return text.substring(text.lastIndexOf(')')+2).split(" ");}
  private static boolean matches(long pid,String ticks,long group){try{var s=stat(pid);return s[19].equals(ticks)&&Long.parseLong(s[2])==group;}catch(IOException|RuntimeException e){return false;}}
  private static void event(Path work,Properties data,int sequence) throws IOException {
    var path=work.resolve(String.format("%04d-%s.properties",sequence,data.getProperty("phase")));
    var bytes=new ByteArrayOutputStream();data.store(bytes,"Synthetic supervisor observation; not verifier evidence");
    var next=path.resolveSibling(path.getFileName()+".pending");
    try(var c=FileChannel.open(next,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){var b=ByteBuffer.wrap(bytes.toByteArray());while(b.hasRemaining())c.write(b);c.force(true);}
    Files.move(next,path,StandardCopyOption.ATOMIC_MOVE);forceDirectory(work);
  }
  private static Properties latest(Path work) throws IOException {
    if(!Files.isDirectory(work))return null;
    try(var paths=Files.list(work)){var path=paths.filter(p->p.getFileName().toString().matches("[0-9]{4}-[A-Z_]+\\.properties")).max(Comparator.comparing(Path::toString));if(path.isEmpty())return null;var p=new Properties();try(var in=Files.newInputStream(path.get())){p.load(in);}return p;}
  }
  private static boolean resolved(Path work,Properties data){
    try{return "EXITED".equals(data.getProperty("phase")) && hash(work.resolve("stdout.bin")).equals(data.getProperty("stdout_sha256")) && hash(work.resolve("stderr.bin")).equals(data.getProperty("stderr_sha256"));}
    catch(Exception e){return false;}
  }
  private static void forceDirectory(Path path) throws IOException{try(var c=FileChannel.open(path,StandardOpenOption.READ)){c.force(true);}}
  private static String hash(Path path) throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(path)));}
}
