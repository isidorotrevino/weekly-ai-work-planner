// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.postgres;
import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static io.github.isidorotrevino.planner.postgres.DeliveryStoreTest.*;
class PresenceStoreTest {
 DeliveryStoreTest f;UUID session;
 static void seed(Connection c,UUID worker)throws Exception{var sid=id();value(c,"SELECT d4.presence_open(?,?,?,NULL)::text",id(),worker,sid);value(c,"SELECT d4.presence_beat(?,?,?,1)::text",id(),worker,sid);}
 @BeforeEach void setup()throws Exception{
  f=new DeliveryStoreTest();f.db="d4_presence_"+id().toString().replace("-","");try(var c=connect("postgres")){sql(c,"CREATE DATABASE "+f.db);}assertEquals(30,migrations(f.db,"30").migrate().migrationsExecuted);
  try(var c=f.owner()){
   sql(c,"CREATE FUNCTION public.seed_fixture_presence() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE s uuid=gen_random_uuid();BEGIN PERFORM d4.presence_open(gen_random_uuid(),NEW.worker_id,s,NULL);PERFORM d4.presence_beat(gen_random_uuid(),NEW.worker_id,s,1);RETURN NEW;END $$;CREATE TRIGGER seed_fixture_presence AFTER INSERT ON d4.worker_catalog FOR EACH ROW EXECUTE FUNCTION public.seed_fixture_presence()");
   f.fixture(c,true);sql(c,"DROP TRIGGER seed_fixture_presence ON d4.worker_catalog;DROP FUNCTION public.seed_fixture_presence()");session=UUID.fromString(value(c,"SELECT session_id FROM d4.presence_heads WHERE worker_id=?",f.worker));
  }
 }
 @AfterEach void cleanup()throws Exception{if(f!=null)f.cleanup();}
 String beat(Connection c,UUID cid,UUID sid,long seq)throws Exception{return value(c,"SELECT d4.presence_beat(?,?,?,?)::text",cid,f.worker,sid,seq);}
 @Test void replayDoesNotRefreshTimeAndSequenceCannotGoBackOrSkip()throws Exception{try(var c=f.owner()){var cid=id();String response=beat(c,cid,session,2);String time=value(c,"SELECT observed_at FROM d4.presence_heads WHERE worker_id=?",f.worker);assertEquals(response,beat(c,cid,session,2));assertEquals(time,value(c,"SELECT observed_at FROM d4.presence_heads WHERE worker_id=?",f.worker));assertThrows(SQLException.class,()->beat(c,id(),session,2));assertThrows(SQLException.class,()->beat(c,id(),session,4));assertThrows(SQLException.class,()->beat(c,cid,session,3));}}
 @Test void replacementRejectsOldBeatAndRequiresFreshNewSequence()throws Exception{try(var c=f.owner()){var next=id();value(c,"SELECT d4.presence_open(?,?,?,?)::text",id(),f.worker,next,session);assertEquals("false",value(c,"SELECT d4.presence_live(?)::text",f.worker));assertThrows(SQLException.class,()->beat(c,id(),session,2));beat(c,id(),next,1);assertEquals("true",value(c,"SELECT d4.presence_live(?)::text",f.worker));assertThrows(SQLException.class,()->value(c,"SELECT d4.presence_open(?,?,?,?)::text",id(),f.worker,id(),session));}}
 @Test void stalePresenceBlocksDirectD2ClaimWithoutReserving()throws Exception{try(var c=f.owner()){sql(c,"UPDATE d4.presence_heads SET observed_at=clock_timestamp()-interval '91 seconds' WHERE worker_id=?",f.worker);var req=Json.write(Map.of("action","CLAIM","operation_id",f.operation,"resource_id",f.resource,"worker_id",f.worker,"pool","PLANNED"));assertThrows(SQLException.class,()->value(c,"SELECT d2.execution(?,?::jsonb)::text",id(),req));assertEquals("0",value(c,"SELECT count(*) FROM d2.reservations"));assertEquals("0",value(c,"SELECT count(*) FROM execution_attempts"));}}
 @Test void replacementCannotRebindRetainedDeliveryOrReleaseItsCommitment()throws Exception{try(var c=f.owner()){var delivery=id();f.call(c,"deliver_continuation",delivery,f.worker,f.request());f.call(c,"ack",id(),f.worker,Map.of("action","ACK","delivery_id",delivery));f.call(c,"worker_execution",id(),f.worker,Map.of("action","START","delivery_id",delivery));var next=id();value(c,"SELECT d4.presence_open(?,?,?,?)::text",id(),f.worker,next,session);beat(c,id(),next,1);assertThrows(SQLException.class,()->f.call(c,"worker_execution",id(),f.worker,Map.of("action","HEARTBEAT","delivery_id",delivery)));assertEquals("1",value(c,"SELECT count(*) FROM operation_leases"));assertEquals("10",value(c,"SELECT outstanding::int FROM d2.reservation_balances"));assertEquals("RUNNING",value(c,"SELECT state FROM operations"));}}
 @Test void disabledCatalogAndOfflineAdministrativeStateDoNotBecomeOnline()throws Exception{try(var c=f.owner()){sql(c,"UPDATE workers SET state='OFFLINE' WHERE id=?",f.worker);beat(c,id(),session,2);assertEquals("OFFLINE",value(c,"SELECT state FROM workers WHERE id=?",f.worker));assertEquals("false",value(c,"SELECT d4.presence_live(?)::text",f.worker));sql(c,"UPDATE d4.worker_catalog SET enabled=false WHERE worker_id=?",f.worker);assertThrows(SQLException.class,()->beat(c,id(),session,3));}}
}
