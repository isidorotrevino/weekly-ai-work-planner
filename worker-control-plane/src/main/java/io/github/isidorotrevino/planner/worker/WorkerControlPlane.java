// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.worker;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.core.env.Environment;
import java.util.Objects;

/** Synthetic laboratory adapter. No timers, migration owner or effect grants. */
@SpringBootApplication
public class WorkerControlPlane {
  public static void main(String[] args){SpringApplication.run(WorkerControlPlane.class,args);}
  @Bean TransportStore transportStore(Environment env){
    if(!"true".equals(env.getProperty("server.ssl.enabled")) ||
       !"need".equals(env.getProperty("server.ssl.client-auth")) ||
       !"none".equals(env.getProperty("server.forward-headers-strategy")))
      throw new IllegalStateException("D4 requires direct HTTPS, mandatory client certificates and no forwarded identity");
    return new TransportStore(Objects.requireNonNull(env.getProperty("d4.jdbc.url")),
      Objects.requireNonNull(env.getProperty("d4.jdbc.user")),Objects.requireNonNull(env.getProperty("d4.jdbc.password")));
  }
}
