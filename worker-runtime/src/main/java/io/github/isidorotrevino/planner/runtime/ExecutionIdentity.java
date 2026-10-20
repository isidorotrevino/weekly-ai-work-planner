// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.runtime;
import java.util.*;
/** Actual D2 identity; this module never allocates or increments authority. */
public record ExecutionIdentity(UUID operation,UUID attempt,UUID worker,UUID resource,long generation) {
  public ExecutionIdentity {Objects.requireNonNull(operation);Objects.requireNonNull(attempt);Objects.requireNonNull(worker);Objects.requireNonNull(resource);if(generation<1)throw new IllegalArgumentException("Positive D2 generation required");}
  public String key(){return operation+"/"+attempt+"/"+worker+"/"+resource+"/"+generation;}
}
