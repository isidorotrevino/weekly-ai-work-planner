// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;
import java.nio.file.*;
import java.util.*;
/** Kernel-only observation invoked by the host, never a worker-supplied boolean. */
final class LabProbe {
 static Object run(String[] args) throws Exception {
  long pid=Long.parseLong(args[1]),group=Long.parseLong(args[2]);if(pid<2||group!=pid)throw new IllegalArgumentException("Invalid fixture process group");
  var boot=Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).strip();var members=new ArrayList<Map<String,Object>>();boolean identity=true;
  try(var paths=Files.list(Path.of("/proc"))){for(var p:paths.filter(v->v.getFileName().toString().matches("[0-9]+")).toList())try{
   var raw=Files.readString(p.resolve("stat"));var s=raw.substring(raw.lastIndexOf(')')+2).split(" ");long member=Long.parseLong(p.getFileName().toString());
   if(member==pid&&!s[19].equals(args[3]))identity=false;
   if(Long.parseLong(s[2])==group)members.add(Map.of("pid",member,"ticks",s[19],"state",s[0]));
  }catch(java.io.IOException ignored){}}
  return Map.of("pid",pid,"group",group,"boot_id",boot,"identity_match",identity&&boot.equals(args[4]),"members",members,"process_stopped",identity&&boot.equals(args[4])&&members.isEmpty());
 }
}
