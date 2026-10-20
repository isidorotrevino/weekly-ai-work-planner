// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.worker;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import tools.jackson.core.*;
import tools.jackson.core.json.JsonFactory;
import tools.jackson.databind.json.JsonMapper;
import java.io.IOException;
import java.sql.SQLException;
import java.util.*;

@RestController @RequestMapping("/d4/v1")
public final class WorkerController {
  private final TransportStore store;
  private final JsonMapper json=JsonMapper.builder(JsonFactory.builder()
    .enable(StreamReadFeature.STRICT_DUPLICATE_DETECTION)
    .streamReadConstraints(StreamReadConstraints.builder().maxNestingDepth(32).maxStringLength(65536).build()).build()).build();
  public WorkerController(TransportStore store){this.store=store;}
  private UUID principal(HttpServletRequest req){return (UUID)req.getAttribute(WorkerIdentityFilter.PRINCIPAL);}
  private ResponseEntity<byte[]> result(String body){return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).header("Cache-Control","no-store").body(body.getBytes(java.nio.charset.StandardCharsets.UTF_8));}
  @PostMapping("/commands") public ResponseEntity<byte[]> command(HttpServletRequest req) throws IOException,SQLException {
    if(!MediaType.APPLICATION_JSON.isCompatibleWith(MediaType.parseMediaType(Objects.requireNonNullElse(req.getContentType(),"application/octet-stream"))))throw new ApiFailure(415,"JSON_REQUIRED");
    var bytes=req.getInputStream().readNBytes(65537);if(bytes.length>65536)throw new ApiFailure(413,"ENVELOPE_TOO_LARGE");
    try {
      var envelope=json.readTree(bytes);
      if(envelope==null || !envelope.isObject() || envelope.size()!=4 || !envelope.has("schema_version") ||
        !envelope.has("command_id") || !envelope.has("correlation_id") || !envelope.has("request") ||
        !"d4.worker.v1".equals(envelope.path("schema_version").asText()) || !envelope.path("request").isObject())throw new IllegalArgumentException();
      var id=UUID.fromString(envelope.path("command_id").asText());UUID.fromString(envelope.path("correlation_id").asText());
      return result(store.command(id,principal(req),new String(bytes,java.nio.charset.StandardCharsets.UTF_8)));
    }catch(tools.jackson.core.JacksonException|IllegalArgumentException e){throw new ApiFailure(400,"INVALID_ENVELOPE");}
  }
  @GetMapping("/assignments/current") public ResponseEntity<byte[]> current(HttpServletRequest req) throws SQLException{return result(store.current(principal(req)));}
  @GetMapping("/commands/{id}") public ResponseEntity<byte[]> read(HttpServletRequest req,@PathVariable("id") String id) throws SQLException {
    try{return result(store.read(principal(req),UUID.fromString(id)));}catch(IllegalArgumentException e){throw new ApiFailure(400,"INVALID_COMMAND_ID");}
  }
  @ExceptionHandler(ApiFailure.class) ResponseEntity<byte[]> failure(ApiFailure error){return error(error.status,error.code);}
  @ExceptionHandler(SQLException.class) ResponseEntity<byte[]> database(SQLException ex){
    var state=Objects.requireNonNullElse(ex.getSQLState(),"");
    if(state.equals("42501"))return error(403,"ACCESS_DENIED");
    if(Set.of("23514","23505","40001","P0002").contains(state))return error(409,"COMMAND_CONFLICT_OR_GUARD");
    if(state.startsWith("22"))return error(400,"INVALID_COMMAND");
    if(state.startsWith("08") || Set.of("57014","55P03").contains(state))return error(503,"RESULT_UNCONFIRMED_QUERY_OR_REPLAY");
    return error(500,"RESULT_UNCONFIRMED_QUERY_OR_REPLAY");
  }
  @ExceptionHandler(org.springframework.http.InvalidMediaTypeException.class) ResponseEntity<byte[]> mediaType(){return error(415,"JSON_REQUIRED");}
  private ResponseEntity<byte[]> error(int status,String code){return ResponseEntity.status(status).contentType(MediaType.APPLICATION_JSON).header("Cache-Control","no-store").body(("{\"error\":\""+code+"\"}").getBytes(java.nio.charset.StandardCharsets.UTF_8));}
  private static final class ApiFailure extends RuntimeException {
    final int status;final String code;
    ApiFailure(int status,String code){super(code);this.status=status;this.code=code;}
  }
}
