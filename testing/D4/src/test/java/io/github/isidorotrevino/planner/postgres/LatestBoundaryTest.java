// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.util.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;
/** Re-execute the actual V25 boundary cases on the current V30 target. */
class LatestBoundaryTest extends V25BoundaryTest {
 @Override @BeforeEach void setup(TestInfo info)throws Exception{
  super.setup(info);migrations(f.f.db,"30").migrate();migrations(f.f.db,"30").validate();
  try(var c=f.f.owner()){
   var workers=new ArrayList<UUID>();try(var p=c.createStatement();var rows=p.executeQuery("SELECT worker_id FROM d4.worker_catalog")){while(rows.next())workers.add(rows.getObject(1,UUID.class));}
   for(var worker:workers)PresenceStoreTest.seed(c,worker);
   // Only fixture setup: existing V24 deliveries are bound explicitly for these
   // boundary tests. Production upgrade never fabricates incarnation bindings.
   sql(c,"INSERT INTO d4.presence_delivery SELECT d.id,h.session_id FROM d4.deliveries d JOIN d4.presence_heads h ON h.worker_id=d.worker_id");
  }
 }
}
