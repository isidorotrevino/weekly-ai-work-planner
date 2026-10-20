// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;

import java.lang.reflect.*;
import java.math.*;
import java.time.*;
import java.util.*;
import io.github.isidorotrevino.planner.scheduler.*;
import static io.github.isidorotrevino.planner.scheduler.PlanningModel.*;

/** Serialization of the typed internal protocol only; SQL performs JSON parsing/validation. */
final class Json {
  private Json() { }
  static String write(Object value) {
    if (value == null) return "null";
    if (value instanceof BigDecimal d) return d.toPlainString();
    if (value instanceof BigInteger || value instanceof Integer || value instanceof Long || value instanceof Boolean) return value.toString();
    if (value instanceof String || value instanceof UUID || value instanceof Instant || value instanceof Duration || value instanceof Rational || value instanceof Enum<?>) return quote(value.toString());
    if (value instanceof Map<?,?> map) {
      var entries=new TreeMap<String,Object>();map.forEach((key,item)->entries.put(key(key),item));
      return "{"+String.join(",",entries.entrySet().stream().map(e->quote(e.getKey())+":"+write(e.getValue())).toList())+"}";
    }
    if (value instanceof Collection<?> collection) {
      var items=collection.stream().map(Json::write).toList();
      if (value instanceof Set<?>) items=items.stream().sorted().toList();
      return "["+String.join(",",items)+"]";
    }
    if (value.getClass().isRecord()) {
      var fields=new TreeMap<String,Object>();
      try {for (var c:value.getClass().getRecordComponents()) fields.put(c.getName(),c.getAccessor().invoke(value));}
      catch (ReflectiveOperationException e) {throw new IllegalArgumentException("Unsupported record",e);}
      return write(fields);
    }
    throw new IllegalArgumentException("Unsupported protocol value type: "+value.getClass().getName());
  }
  private static String key(Object key) {
    if (key instanceof String || key instanceof UUID) return key.toString();
    if (key instanceof PoolKey p) return p.accountId()+"/"+p.pool();
    if (key instanceof LaneKey l) return l.accountId()+"/"+l.lane();
    throw new IllegalArgumentException("Unsupported map key");
  }
  private static String quote(String text) {
    var out=new StringBuilder("\"");
    for (int i=0;i<text.length();i++) {
      char ch=text.charAt(i);
      switch(ch) {
        case '"' -> out.append("\\\"");case '\\' -> out.append("\\\\");
        case '\n' -> out.append("\\n");case '\r' -> out.append("\\r");case '\t' -> out.append("\\t");
        default -> {if(ch<32) out.append(String.format(Locale.ROOT,"\\u%04x",(int)ch));else out.append(ch);}
      }
    }
    return out.append('"').toString();
  }
}
