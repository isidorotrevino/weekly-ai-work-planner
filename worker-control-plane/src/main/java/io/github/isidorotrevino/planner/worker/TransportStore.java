// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.worker;

import java.sql.*;
import java.util.UUID;

/** One bounded SQL transaction per call; no connection held across HTTP work. */
public final class TransportStore {
  private final String url,user,password;
  private final boolean continuation;
  public TransportStore(String url,String user,String password){this(url,user,password,false);}
  public TransportStore(String url,String user,String password,boolean continuation){this.url=url;this.user=user;this.password=password;this.continuation=continuation;}
  private Connection connect() throws SQLException {
    var options=new java.util.Properties();options.setProperty("user",user);options.setProperty("password",password);
    options.setProperty("connectTimeout","5");options.setProperty("socketTimeout","8");
    var c=DriverManager.getConnection(url,options);
    try {
      c.setAutoCommit(true);c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      try(var p=c.createStatement()){p.execute("SET statement_timeout=5000; SET lock_timeout=4000");}
      return c;
    }catch(SQLException e){c.close();throw e;}
  }
  public String command(UUID id,UUID worker,String envelope) throws SQLException {
    try(var c=connect();var p=c.prepareStatement(continuation?"SELECT d4.transport_continuation(?,?,?::jsonb)::text":"SELECT d4.transport(?,?,?::jsonb)::text")){
      p.setObject(1,id);p.setObject(2,worker);p.setString(3,envelope);p.setQueryTimeout(6);
      try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}
    }
  }
  public String current(UUID worker) throws SQLException {
    try(var c=connect();var p=c.prepareStatement("SELECT d4.current_assignment(?)::text")){
      p.setObject(1,worker);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}
    }
  }
  public String read(UUID worker,UUID command) throws SQLException {
    try(var c=connect();var p=c.prepareStatement("SELECT d4.read_transport_command(?,?)::text")){
      p.setObject(1,worker);p.setObject(2,command);try(var rs=p.executeQuery()){rs.next();return rs.getString(1);}
    }
  }
}
