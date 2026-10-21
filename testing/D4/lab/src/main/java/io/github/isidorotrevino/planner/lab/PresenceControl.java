// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.lab;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.*;
@RestController @ConditionalOnProperty(name="lab.role",havingValue="control")
class PresenceControl {
 @GetMapping("/lab/presence") Object current(HttpServletRequest r)throws Exception{return LabSupport.sql("SELECT d4.presence_current(?)::text",LabSupport.worker(r));}
 @PostMapping("/lab/presence/open") Object open(HttpServletRequest r)throws Exception{var worker=LabSupport.worker(r);var b=LabSupport.body(r);MultiCheckpointVerifier.fields(b,"command_id","session_id","expected_session");return LabSupport.sql("SELECT d4.presence_open(?,?,?,?)::text",LabSupport.uuid(b,"command_id"),worker,LabSupport.uuid(b,"session_id"),b.path("expected_session").isNull()?null:LabSupport.uuid(b,"expected_session"));}
}
