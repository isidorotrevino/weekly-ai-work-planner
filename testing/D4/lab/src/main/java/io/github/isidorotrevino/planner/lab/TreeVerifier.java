// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;

import java.nio.file.*;
import java.nio.file.attribute.*;
import java.nio.channels.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import java.io.*;
import java.util.concurrent.*;

/** Bounded local observations. Never imports a worker Git repository or runs candidate code. */
public final class TreeVerifier {
 public record Artifact(int size,String sha256,boolean executable){
  public Artifact{if(size<0||size>65536||sha256==null||!sha256.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("ARTIFACT_BOUND");}
  public static Artifact of(byte[] b,boolean x){return new Artifact(b.length,hash(b),x);}
 }
 public record Verified(String method,String manifest,int files,long bytes){}
 public static String hash(byte[] b){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));}catch(Exception e){throw new IllegalStateException(e);}}
 public static void path(String name){if(name==null||name.length()>240)throw new IllegalArgumentException("PATH");for(var p:name.split("/",-1))if(!p.matches("[A-Za-z0-9_.-]{1,100}")||Set.of(".","..",".git").contains(p.toLowerCase(Locale.ROOT)))throw new IllegalArgumentException("PATH");}
 public static String manifest(Map<String,Artifact> expected){
  if(expected==null||expected.size()>64)throw new IllegalArgumentException("MANIFEST_BOUND");long bytes=0;var fields=new TreeMap<String,Object>();
  for(var e:expected.entrySet()){path(e.getKey());var a=Objects.requireNonNull(e.getValue());bytes+=a.size();var p=e.getKey();while(p.contains("/")){p=p.substring(0,p.lastIndexOf('/'));if(expected.containsKey(p))throw new IllegalArgumentException("FILE_DIRECTORY_COLLISION");}fields.put(e.getKey(),new TreeMap<>(Map.of("size",a.size(),"sha256",a.sha256(),"executable",a.executable())));}
  if(bytes>4*1024*1024)throw new IllegalArgumentException("TOTAL_BOUND");try{return hash(LabSupport.JSON.writeValueAsBytes(fields));}catch(Exception e){throw new IllegalArgumentException(e);}
 }
 public static Verified files(Path root,Map<String,Artifact> expected,boolean restoration)throws Exception{
  var digest=manifest(expected);var seen=new HashSet<String>();root=root.toAbsolutePath().normalize();for(var p=root;p!=null;p=p.getParent())if(Files.isSymbolicLink(p))throw new IOException("TREE_PARENT_ALIAS");
  try(var directory=Files.newDirectoryStream(root)){if(!(directory instanceof SecureDirectoryStream<Path> secure)||Files.isSymbolicLink(root))throw new IOException("SECURE_DIRECTORY_REQUIRED");walk(secure,"",expected,seen);}
  if(!seen.equals(expected.keySet()))throw new IOException("INCOMPLETE_TREE");return new Verified(restoration?"d4.local-restoration.v1":"d4.artifact-tree.v1",digest,seen.size(),expected.values().stream().mapToLong(Artifact::size).sum());
 }
 private static void walk(SecureDirectoryStream<Path> dir,String prefix,Map<String,Artifact> expected,Set<String> seen)throws Exception{
  for(Path item:dir){var leaf=item.getFileName();var name=prefix+leaf;path(name);var view=dir.getFileAttributeView(leaf,BasicFileAttributeView.class,LinkOption.NOFOLLOW_LINKS);var before=view.readAttributes();
   if(before.isDirectory()){if(expected.keySet().stream().noneMatch(x->x.startsWith(name+"/")))throw new IOException("EXTRA_DIRECTORY");try(var child=dir.newDirectoryStream(leaf,LinkOption.NOFOLLOW_LINKS)){walk(child,name+"/",expected,seen);}}
   else{
    var a=expected.get(name);if(a==null||!before.isRegularFile()||before.size()!=a.size())throw new IOException("EXTRA_OR_UNSAFE_FILE");
    // Linux fixture only. Resolve no-follow metadata through the opened directory's entry.
    if(((Number)Files.getAttribute(item,"unix:nlink",LinkOption.NOFOLLOW_LINKS)).intValue()!=1)throw new IOException("HARD_LINK");
    var perms=dir.getFileAttributeView(leaf,PosixFileAttributeView.class,LinkOption.NOFOLLOW_LINKS).readAttributes().permissions();boolean executable=perms.stream().anyMatch(x->x.name().endsWith("EXECUTE"));if(executable!=a.executable())throw new IOException("FILE_MODE");
    try(var channel=dir.newByteChannel(leaf,Set.of(StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS))){var bytes=ByteBuffer.allocate(a.size()+1);while(bytes.hasRemaining()&&channel.read(bytes)>0){}if(bytes.position()!=a.size()||!hash(Arrays.copyOf(bytes.array(),bytes.position())).equals(a.sha256()))throw new IOException("FILE_CONTENT");}
    var after=view.readAttributes();if(!Objects.equals(before.fileKey(),after.fileKey())||before.size()!=after.size()||!before.lastModifiedTime().equals(after.lastModifiedTime())||!before.creationTime().equals(after.creationTime()))throw new IOException("TREE_CHANGED");seen.add(name);
   }
  }
 }
 /** Verifier-owned bare fixture store. Fixed commands, empty environment, no network/config/hooks. */
 public static final class GitStore implements AutoCloseable{
  private final Path repo;private byte[] config;
  public GitStore(Path parent)throws Exception{repo=Files.createTempDirectory(parent,"d4-git-");run(null,"init","--bare","--object-format=sha1","--template=",repo.toString());config=Files.readAllBytes(repo.resolve("config"));}
  private byte[] run(byte[] input,String...args)throws Exception{
   var command=new ArrayList<String>(List.of("git","--no-optional-locks"));if(config!=null)command.addAll(List.of("--git-dir="+repo,"-c","core.hooksPath=/dev/null","-c","protocol.allow=never","-c","core.fsmonitor=false"));command.addAll(List.of(args));var b=new ProcessBuilder(command);var env=b.environment();env.clear();env.putAll(Map.of("PATH","/usr/bin:/bin","LANG","C","HOME",repo.toString(),"GIT_CONFIG_NOSYSTEM","1","GIT_CONFIG_GLOBAL","/dev/null","GIT_CONFIG_SYSTEM","/dev/null","GIT_NO_REPLACE_OBJECTS","1","GIT_TERMINAL_PROMPT","0"));env.putAll(Map.of("GIT_AUTHOR_NAME","Synthetic verifier","GIT_AUTHOR_EMAIL","fixture@example.invalid","GIT_COMMITTER_NAME","Synthetic verifier","GIT_COMMITTER_EMAIL","fixture@example.invalid","GIT_AUTHOR_DATE","2026-10-20T00:00:00Z","GIT_COMMITTER_DATE","2026-10-20T00:00:00Z"));
   var p=b.start();try{var out=CompletableFuture.supplyAsync(()->bounded(p.getInputStream()));var err=CompletableFuture.supplyAsync(()->bounded(p.getErrorStream()));var writer=CompletableFuture.runAsync(()->{try(var in=p.getOutputStream()){if(input!=null)in.write(input);}catch(IOException e){throw new CompletionException(e);}});if(!p.waitFor(5,TimeUnit.SECONDS)||p.exitValue()!=0)throw new IOException("GIT_OBJECT_ANCESTRY_OR_TIMEOUT");writer.get(1,TimeUnit.SECONDS);byte[] result=out.get(1,TimeUnit.SECONDS);err.get(1,TimeUnit.SECONDS);return result;}finally{p.destroyForcibly();}
  }
  private static byte[] bounded(InputStream in){try{var b=in.readNBytes(2*1024*1024+1);if(b.length>2*1024*1024)throw new IOException("GIT_OUTPUT_BOUND");return b;}catch(IOException e){throw new CompletionException(e);}}
  private String text(byte[] in,String...args)throws Exception{return new String(run(in,args),StandardCharsets.UTF_8).strip();}
  public String commit(Map<String,byte[]> files,Map<String,Artifact> expected,String parent)throws Exception{
   manifest(expected);if(!files.keySet().equals(expected.keySet()))throw new IOException("TREE_KEYS");var entries=new TreeMap<String,String>();
   for(var e:files.entrySet()){var a=expected.get(e.getKey());if(!Artifact.of(e.getValue(),a.executable()).equals(a))throw new IOException("BLOB_HASH");entries.put(e.getKey(),(a.executable()?"100755":"100644")+" blob "+text(e.getValue(),"hash-object","-w","--stdin"));}
   var tree=tree(entries,"");var args=new ArrayList<>(List.of("commit-tree",tree));if(parent!=null){if(!parent.matches("[a-f0-9]{40}"))throw new IOException("PARENT_OID");args.addAll(List.of("-p",parent));}return text("Synthetic fixture\n".getBytes(StandardCharsets.UTF_8),args.toArray(String[]::new));
  }
  private String tree(Map<String,String> entries,String prefix)throws Exception{var rows=new TreeMap<String,String>();var sub=new TreeSet<String>();for(var e:entries.entrySet()){if(!e.getKey().startsWith(prefix))continue;String tail=e.getKey().substring(prefix.length());if(tail.contains("/"))sub.add(tail.substring(0,tail.indexOf('/')));else rows.put(tail,e.getValue());}for(var name:sub)rows.put(name,"040000 tree "+tree(entries,prefix+name+"/"));var body=new ByteArrayOutputStream();for(var e:rows.entrySet())body.write((e.getValue()+"\t"+e.getKey()+"\0").getBytes(StandardCharsets.US_ASCII));return text(body.toByteArray(),"mktree","-z");}
  private void integrity()throws Exception{if(Files.isSymbolicLink(repo.resolve("config"))||!Arrays.equals(config,Files.readAllBytes(repo.resolve("config"))))throw new IOException("GIT_CONFIG_CHANGED");for(var p:List.of("objects/info/alternates","objects/info/http-alternates","info/grafts","shallow","refs/replace"))if(Files.exists(repo.resolve(p),LinkOption.NOFOLLOW_LINKS))throw new IOException("GIT_INDIRECTION");try(var paths=Files.walk(repo)){for(var p:paths.toList())if(Files.isSymbolicLink(p)||(Files.isRegularFile(p)&&((Number)Files.getAttribute(p,"unix:nlink")).intValue()!=1))throw new IOException("GIT_STORE_ALIAS");}}
  public Verified verify(String commit,String base,Map<String,Artifact> expected)throws Exception{
   var digest=manifest(expected);integrity();for(var oid:List.of(commit,base))if(!oid.matches("[a-f0-9]{40}")||!text(null,"cat-file","-t",oid).equals("commit"))throw new IOException("FULL_COMMIT_REQUIRED");run(null,"merge-base","--is-ancestor",base,commit);var rows=new String(run(null,"ls-tree","-r","-z","--full-tree",commit),StandardCharsets.US_ASCII).split("\0");if(rows.length>64)throw new IOException("TREE_BOUND");var seen=new HashSet<String>();for(var row:rows){if(row.isEmpty())continue;var fields=row.split("\t",-1);if(fields.length!=2)throw new IOException("GIT_ENTRY");String name=fields[1];path(name);var meta=fields[0].split(" ");var a=expected.get(name);if(a==null||!seen.add(name)||meta.length!=3||!meta[1].equals("blob")||!meta[0].equals(a.executable()?"100755":"100644"))throw new IOException("GIT_MODE_OR_ENTRY");if(!text(null,"cat-file","-s",meta[2]).equals(Integer.toString(a.size()))||!hash(run(null,"cat-file","blob",meta[2])).equals(a.sha256()))throw new IOException("GIT_BLOB");}if(!seen.equals(expected.keySet()))throw new IOException("GIT_INCOMPLETE");integrity();return new Verified("d4.fixture-git-tree.v1",digest,seen.size(),expected.values().stream().mapToLong(Artifact::size).sum());
  }
  @Override public void close()throws IOException{try(var paths=Files.walk(repo)){for(var p:paths.sorted(Comparator.reverseOrder()).toList())Files.delete(p);}}
 }
}
