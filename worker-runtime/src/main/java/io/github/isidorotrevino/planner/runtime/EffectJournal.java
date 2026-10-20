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
import java.util.concurrent.locks.*;

/** Durable synthetic effect = one forced journal event. No real external API. */
public final class EffectJournal {
  public enum Status { APPLIED, ABSENT, UNKNOWN }
  public record Receipt(Status status,String payloadHash,long generation,long sequence,boolean closed) { }
  public record Grant(UUID receiverId,ExecutionIdentity identity,String intentHash,String contextHash,String policyHash,Set<String> steps,
                      Instant issuedAt,Instant expiresAt,Instant leaseExpiresAt) {
    public Grant {
      Objects.requireNonNull(receiverId);Objects.requireNonNull(identity);Objects.requireNonNull(issuedAt);Objects.requireNonNull(expiresAt);Objects.requireNonNull(leaseExpiresAt);
      for(var h:List.of(intentHash,contextHash,policyHash))if(!h.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("SHA-256 required");
      steps=Set.copyOf(steps);if(steps.isEmpty()||steps.size()>16||steps.stream().anyMatch(s->!s.matches("[a-zA-Z0-9._-]{1,64}")))throw new IllegalArgumentException("Bounded authorized step manifest required");
      if(!expiresAt.isAfter(issuedAt)||expiresAt.isAfter(leaseExpiresAt)||Duration.between(issuedAt,expiresAt).compareTo(Duration.ofSeconds(60))>0)throw new IllegalArgumentException("Grant must fit D2 lease and 60 seconds");
    }
    String binding(){return receiverId+"/"+identity.key()+"/"+intentHash+"/"+contextHash+"/"+policyHash+"/"+String.join(",",new TreeSet<>(steps));}
    String canonical(){return "d4.synthetic.grant.v1\n"+binding()+"\n"+issuedAt+"\n"+expiresAt+"\n"+leaseExpiresAt;}
  }
  public record SignedGrant(Grant grant,String signature) { }
  public record SignedClose(UUID receiverId,ExecutionIdentity identity,UUID command,String signature) { }
  public static final class Unavailable extends IOException {public Unavailable(String code){super(code);}}
  private static final Map<Path,ReentrantLock> LOCKS=new ConcurrentHashMap<>();
  private final Path root;private final PublicKey authority;private final Clock clock;
  private EffectJournal(Path root,PublicKey key,Clock clock){this.root=root.toAbsolutePath().normalize();authority=key;this.clock=clock;}
  public static EffectJournal create(Path root,PublicKey key,Clock clock) throws IOException {
    Files.createDirectory(root);Files.setPosixFilePermissions(root,java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
    var result=new EffectJournal(root,key,clock);
    result.forceFile(root.resolve("authority.sha256"),hash(key.getEncoded()).getBytes(java.nio.charset.StandardCharsets.US_ASCII),true);
    result.forceFile(root.resolve("receiver.id"),UUID.randomUUID().toString().getBytes(java.nio.charset.StandardCharsets.US_ASCII),true);
    result.forceFile(root.resolve("head"),("0:"+"00".repeat(32)).getBytes(java.nio.charset.StandardCharsets.US_ASCII),true);
    result.forceFile(root.resolve("journal.bin"),new byte[0],true);result.forceFile(root.resolve("lock"),new byte[0],true);result.forceDirectory();return result;
  }
  public static EffectJournal open(Path root,PublicKey key,Clock clock){return new EffectJournal(root,key,clock);}
  public static SignedGrant sign(Grant grant,PrivateKey key) throws GeneralSecurityException{return new SignedGrant(grant,signText(grant.canonical(),key));}
  public UUID receiverId() throws IOException {try{return UUID.fromString(Files.readString(root.resolve("receiver.id")));}catch(IllegalArgumentException e){throw new Unavailable("RECEIVER_ID_CORRUPT");}}
  public static SignedClose signClose(UUID receiver,ExecutionIdentity identity,UUID command,PrivateKey key) throws GeneralSecurityException{return new SignedClose(receiver,identity,command,signText(closeText(receiver,identity,command),key));}
  private static String closeText(UUID receiver,ExecutionIdentity id,UUID command){return "d4.synthetic.close.v1\n"+receiver+"\n"+id.key()+"\n"+command;}
  private static String signText(String text,PrivateKey key) throws GeneralSecurityException {
    var s=Signature.getInstance("Ed25519");s.initSign(key);s.update(text.getBytes(java.nio.charset.StandardCharsets.UTF_8));return Base64.getEncoder().encodeToString(s.sign());
  }
  private void verify(String text,String signature) throws Unavailable {
    try {var s=Signature.getInstance("Ed25519");s.initVerify(authority);s.update(text.getBytes(java.nio.charset.StandardCharsets.UTF_8));if(!s.verify(Base64.getDecoder().decode(signature)))throw new GeneralSecurityException();}
    catch(GeneralSecurityException|IllegalArgumentException e){throw new Unavailable("AUTHORITY_REJECTED");}
  }
  private void active(Grant g) throws Unavailable {var now=clock.instant();if(now.isBefore(g.issuedAt())||!now.isBefore(g.expiresAt()))throw new Unavailable("GRANT_EXPIRED_OR_FUTURE");}
  public long install(SignedGrant signed) throws IOException {
    var g=signed.grant();verify(g.canonical(),signed.signature());
    return transaction((state,channel)->{
      active(g);if(!receiverId().equals(g.receiverId()))throw new Unavailable("RECEIVER_EPOCH_MISMATCH");var current=state.grants.get(g.identity().operation());
      if(current==null && g.identity().generation()!=1)throw new Unavailable("MISSING_PRIOR_AUTHORITY_HISTORY");
      if(current!=null){
        var prior=current.grant();long old=prior.identity().generation(),next=g.identity().generation();
        if(next<old || state.closed.containsKey(g.identity().key()))throw new Unavailable("FENCED_OR_CLOSED");
        if(next==old && (!prior.binding().equals(g.binding())||g.expiresAt().isBefore(prior.expiresAt())))throw new Unavailable("GRANT_BINDING_CONFLICT");
        if(next>old && !state.closed.containsKey(prior.identity().key()))throw new Unavailable("PRIOR_GENERATION_NOT_CLOSED");
        if(prior.equals(g))return state.grantSequences.get(g.identity().operation());
      }
      var e=grantMap(g);e.put("type","GRANT");e.put("signature",signed.signature());append(state,channel,e);return state.sequence;
    });
  }
  public Receipt apply(SignedGrant signed,String step,byte[] payload) throws IOException {
    if(!step.matches("[a-zA-Z0-9._-]{1,64}")||payload.length>65536)throw new IllegalArgumentException("Bounded logical step and payload required");
    var g=signed.grant();verify(g.canonical(),signed.signature());
    if(!g.steps().contains(step))throw new Unavailable("STEP_NOT_AUTHORIZED");
    return transaction((state,channel)->{
      active(g);var current=state.grants.get(g.identity().operation());
      if(current==null || !current.grant().equals(g)||state.closed.containsKey(g.identity().key()))throw new Unavailable("FENCED_OR_CLOSED");
      var key=g.identity().operation()+"/"+g.intentHash()+"/"+step;String digest=hash(payload);var existing=state.effects.get(key);
      if(existing!=null){if(!existing.payloadHash().equals(digest))throw new Unavailable("LOGICAL_EFFECT_CONTENT_CONFLICT");return existing;}
      var e=grantMap(g);e.put("type","APPLY");e.put("step",step);e.put("payload",Base64.getEncoder().encodeToString(payload));
      append(state,channel,e);return new Receipt(Status.APPLIED,digest,g.identity().generation(),state.sequence,false);
    });
  }
  public long close(SignedClose close) throws IOException {
    verify(closeText(close.receiverId(),close.identity(),close.command()),close.signature());
    return transaction((state,channel)->{
      var binding=close.identity().key();var used=state.closeCommands.get(close.command());
      if(used!=null&&!used.equals(binding))throw new Unavailable("CLOSE_COMMAND_CONFLICT");
      if(!receiverId().equals(close.receiverId()))throw new Unavailable("RECEIVER_EPOCH_MISMATCH");
      var prior=state.closed.get(binding);if(prior!=null){if(used==null)throw new Unavailable("CLOSED_USE_ORIGINAL_COMMAND");return prior;}
      var current=state.grants.get(close.identity().operation());
      if(current==null||!current.grant().identity().equals(close.identity()))throw new Unavailable("CLOSE_IDENTITY_CONFLICT");
      var e=grantMap(current.grant());e.put("type","CLOSE");e.put("command",close.command().toString());e.put("signature",close.signature());
      append(state,channel,e);return state.sequence;
    });
  }
  public record Seal(UUID receiverId,ExecutionIdentity identity,UUID command,long sequence,Map<String,Receipt> steps) { }
  /** Stable complete authorized-step manifest, serialized with durable close. */
  public Seal seal(SignedClose close) throws IOException {
    close(close);
    return transaction((state,channel)->{
      var sealed=state.seals.get(close.identity().key());if(sealed==null)throw new Unavailable("SEAL_HISTORY_UNAVAILABLE");return sealed;
    });
  }
  public Receipt query(UUID operation,String intent,String step,long generation) {
    try{return transaction((state,channel)->{
      var effect=state.effects.get(operation+"/"+intent+"/"+step);if(effect!=null)return effect;
      var current=state.grants.get(operation);
      if(current!=null && current.grant().steps().contains(step) && current.grant().identity().generation()==generation && current.grant().intentHash().equals(intent) && state.closed.containsKey(current.grant().identity().key()))
        return new Receipt(Status.ABSENT,null,generation,state.sequence,true);
      return new Receipt(Status.UNKNOWN,null,generation,state.sequence,false);
    });}catch(IOException|RuntimeException e){return new Receipt(Status.UNKNOWN,null,generation,0,false);}
  }
  @FunctionalInterface private interface Work<T>{T run(State state,FileChannel channel) throws IOException;}
  private <T>T transaction(Work<T> work) throws IOException {
    var mutex=LOCKS.computeIfAbsent(root,p->new ReentrantLock());mutex.lock();
    try {
      if(!Files.readString(root.resolve("authority.sha256")).equals(hash(authority.getEncoded())))throw new Unavailable("AUTHORITY_STORE_MISMATCH");
      try(var lock=FileChannel.open(root.resolve("lock"),StandardOpenOption.WRITE);var held=lock.lock();
          var channel=FileChannel.open(root.resolve("journal.bin"),StandardOpenOption.READ,StandardOpenOption.WRITE)){
        State state;try{state=replay(channel);}catch(RuntimeException ex){throw new Unavailable("JOURNAL_CORRUPT");}
        if(!Files.readString(root.resolve("head")).equals(state.sequence+":"+HexFormat.of().formatHex(state.chain)))throw new Unavailable("JOURNAL_HEAD_MISMATCH");
        return work.run(state,channel);
      }
    }finally{mutex.unlock();}
  }
  private static final class State {
    long sequence;byte[] chain=new byte[32];Map<UUID,SignedGrant> grants=new HashMap<>();Map<UUID,Long> grantSequences=new HashMap<>();Map<String,Receipt> effects=new HashMap<>();
    Map<String,Long> closed=new HashMap<>();Map<UUID,String> closeCommands=new HashMap<>();Map<String,Seal> seals=new HashMap<>();
  }
  private State replay(FileChannel channel) throws IOException {
    var state=new State();channel.position(0);
    while(channel.position()<channel.size()){
      if(state.sequence>=2000)throw new Unavailable("JOURNAL_LIMIT");
      var length=ByteBuffer.allocate(4);readFully(channel,length);int count=length.flip().getInt();if(count<1||count>131072)throw new Unavailable("JOURNAL_CORRUPT");
      var data=ByteBuffer.allocate(count);readFully(channel,data);var checksum=ByteBuffer.allocate(32);readFully(channel,checksum);
      byte[] expected=chainHash(state.chain,data.array());if(!MessageDigest.isEqual(expected,checksum.array()))throw new Unavailable("JOURNAL_CORRUPT");
      state.chain=expected;state.sequence++;var e=decode(data.array());var g=mapGrant(e);var type=e.get("type");
      if("GRANT".equals(type)){verify(g.canonical(),e.get("signature"));state.grants.put(g.identity().operation(),new SignedGrant(g,e.get("signature")));state.grantSequences.put(g.identity().operation(),state.sequence);}
      else if("APPLY".equals(type))state.effects.put(g.identity().operation()+"/"+g.intentHash()+"/"+e.get("step"),new Receipt(Status.APPLIED,hash(Base64.getDecoder().decode(e.get("payload"))),g.identity().generation(),state.sequence,false));
      else if("CLOSE".equals(type)){var command=UUID.fromString(e.get("command"));verify(closeText(g.receiverId(),g.identity(),command),e.get("signature"));state.closed.put(g.identity().key(),state.sequence);state.closeCommands.put(command,g.identity().key());var receipts=new TreeMap<String,Receipt>();for(var step:g.steps()){var applied=state.effects.get(g.identity().operation()+"/"+g.intentHash()+"/"+step);receipts.put(step,applied!=null?applied:new Receipt(Status.ABSENT,null,g.identity().generation(),state.sequence,true));}state.seals.put(g.identity().key(),new Seal(g.receiverId(),g.identity(),command,state.sequence,Collections.unmodifiableMap(receipts)));}
      else throw new Unavailable("JOURNAL_CORRUPT");
    }
    return state;
  }
  private void append(State state,FileChannel channel,Map<String,String> e) throws IOException {
    if(state.sequence>=1999)throw new Unavailable("JOURNAL_LIMIT");var data=encode(e);var digest=chainHash(state.chain,data);
    var frame=ByteBuffer.allocate(4+data.length+32).putInt(data.length).put(data).put(digest);frame.flip();channel.position(channel.size());
    while(frame.hasRemaining())channel.write(frame);channel.force(true);state.sequence++;state.chain=digest;
    var next=root.resolve("head.next");forceFile(next,(state.sequence+":"+HexFormat.of().formatHex(digest)).getBytes(java.nio.charset.StandardCharsets.US_ASCII),false);
    Files.move(next,root.resolve("head"),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);forceDirectory();
  }
  private static void readFully(FileChannel c,ByteBuffer b) throws IOException {while(b.hasRemaining())if(c.read(b)<0)throw new Unavailable("JOURNAL_TRUNCATED");}
  private static byte[] encode(Map<String,String> e) throws IOException {
    var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){out.writeInt(e.size());for(var entry:new TreeMap<>(e).entrySet()){out.writeUTF(entry.getKey());byte[] value=entry.getValue().getBytes(java.nio.charset.StandardCharsets.UTF_8);out.writeInt(value.length);out.write(value);}}return bytes.toByteArray();
  }
  private static Map<String,String> decode(byte[] bytes) throws IOException {
    var result=new HashMap<String,String>();try(var in=new DataInputStream(new ByteArrayInputStream(bytes))){int count=in.readInt();if(count<1||count>32)throw new Unavailable("JOURNAL_CORRUPT");for(int i=0;i<count;i++){var key=in.readUTF();int size=in.readInt();if(size<0||size>90000)throw new Unavailable("JOURNAL_CORRUPT");var data=in.readNBytes(size);if(data.length!=size||result.put(key,new String(data,java.nio.charset.StandardCharsets.UTF_8))!=null)throw new Unavailable("JOURNAL_CORRUPT");}if(in.available()!=0)throw new Unavailable("JOURNAL_CORRUPT");}return result;
  }
  private static Map<String,String> grantMap(Grant g){
    var id=g.identity();return new HashMap<>(Map.ofEntries(Map.entry("receiver",g.receiverId().toString()),Map.entry("operation",id.operation().toString()),Map.entry("attempt",id.attempt().toString()),Map.entry("worker",id.worker().toString()),Map.entry("resource",id.resource().toString()),Map.entry("generation",Long.toString(id.generation())),Map.entry("intent",g.intentHash()),Map.entry("context",g.contextHash()),Map.entry("policy",g.policyHash()),Map.entry("steps",String.join(",",new TreeSet<>(g.steps()))),Map.entry("issued",g.issuedAt().toString()),Map.entry("expires",g.expiresAt().toString()),Map.entry("lease_expires",g.leaseExpiresAt().toString())));
  }
  private static Grant mapGrant(Map<String,String> e) throws Unavailable {
    try{return new Grant(UUID.fromString(e.get("receiver")),new ExecutionIdentity(UUID.fromString(e.get("operation")),UUID.fromString(e.get("attempt")),UUID.fromString(e.get("worker")),UUID.fromString(e.get("resource")),Long.parseLong(e.get("generation"))),e.get("intent"),e.get("context"),e.get("policy"),Set.of(e.get("steps").split(",")),Instant.parse(e.get("issued")),Instant.parse(e.get("expires")),Instant.parse(e.get("lease_expires")));}
    catch(RuntimeException ex){throw new Unavailable("JOURNAL_CORRUPT");}
  }
  private void forceFile(Path path,byte[] data,boolean create) throws IOException {try(var c=FileChannel.open(path,StandardOpenOption.WRITE,StandardOpenOption.CREATE,create?StandardOpenOption.CREATE_NEW:StandardOpenOption.TRUNCATE_EXISTING)){var b=ByteBuffer.wrap(data);while(b.hasRemaining())c.write(b);c.force(true);}}
  private void forceDirectory() throws IOException {try(var c=FileChannel.open(root,StandardOpenOption.READ)){c.force(true);}}
  private static byte[] chainHash(byte[] prior,byte[] data){try{var h=MessageDigest.getInstance("SHA-256");h.update(prior);return h.digest(data);}catch(GeneralSecurityException e){throw new IllegalStateException(e);}}
  private static String hash(byte[] bytes){return HexFormat.of().formatHex(chainHash(new byte[0],bytes));}
}
