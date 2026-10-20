// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.worker;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.security.cert.*;
import java.util.*;

/** Trust chain validated by Tomcat. Binding, validity and revocation per request. */
@Component @Order(Ordered.HIGHEST_PRECEDENCE)
public final class WorkerIdentityFilter extends OncePerRequestFilter {
  public static final String PRINCIPAL="d4.authenticated.worker";
  public static final String KIND="d4.authenticated.kind";
  private final Path identities;
  public WorkerIdentityFilter(Environment env){identities=Path.of(env.getRequiredProperty("d4.identities"));}
  @Override protected void doFilterInternal(HttpServletRequest req,HttpServletResponse res,FilterChain chain) throws IOException,ServletException {
    UUID worker;String kind;
    try {
      if(!req.isSecure())throw new GeneralSecurityException();
      var certs=(X509Certificate[])req.getAttribute("jakarta.servlet.request.X509Certificate");
      if(certs==null || certs.length==0)throw new GeneralSecurityException();
      var cert=certs[0];cert.checkValidity();
      if(cert.getExtendedKeyUsage()==null || !cert.getExtendedKeyUsage().contains("1.3.6.1.5.5.7.3.2"))throw new GeneralSecurityException();
      var registry=new Properties();
      // Reload on every request, including an existing authenticated TLS session.
      try(var in=Files.newInputStream(identities)){registry.load(in);}
      var fingerprint=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(cert.getEncoded()));
      var binding=registry.getProperty(fingerprint);
      if(binding==null)throw new GeneralSecurityException();
      var parts=binding.split(":",2);kind=parts.length==1?"worker":parts[0];worker=UUID.fromString(parts.length==1?binding:parts[1]);
      if(!Set.of("worker","control","verifier","driver").contains(kind))throw new GeneralSecurityException();
      if(req.getRequestURI().startsWith("/d4/")&&!kind.equals("worker"))throw new GeneralSecurityException();
      var expected=kind.equals("worker")?"urn:weekly-ai-planner:worker:"+worker:"urn:weekly-ai-planner:principal:"+kind+":"+worker;
      var sans=cert.getSubjectAlternativeNames();
      if(sans==null || sans.stream().noneMatch(s->s.size()==2 && Integer.valueOf(6).equals(s.get(0)) && expected.equals(s.get(1))))throw new GeneralSecurityException();
    }catch(GeneralSecurityException|IllegalArgumentException ex){deny(res,403,"IDENTITY_REJECTED");return;
    }catch(IOException ex){deny(res,503,"IDENTITY_REGISTRY_UNAVAILABLE");return;}
    req.setAttribute(PRINCIPAL,worker);req.setAttribute(KIND,kind);chain.doFilter(req,res);
  }
  static void deny(HttpServletResponse res,int status,String code) throws IOException {
    res.setStatus(status);res.setContentType("application/json");res.setHeader("Cache-Control","no-store");
    res.getWriter().write("{\"error\":\""+code+"\"}");
  }
}
