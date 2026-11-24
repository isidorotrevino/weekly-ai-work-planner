# I221 — CE12: slot diferido de claim y recibo

CE12 queda preparado como dossier documental negativo para PGO181 candidato 02 con estado **`DEFERRED_NOT_AUTHORIZED`**. No se crea claim, construcción protegida, worker o recibo real. No existen aquí autorización funcional separada, E06/payload/Q/root/admisión finales ni aceptación competente de CE11. PJC115-R2 mantiene la no admisión; E01–E05 siguen abiertas, D5 abierto e IR03 `NOT_READY`.

El [dossier CE12](../validation/D5-I193-CE12-CONDITIONAL-ACTUAL-CLAIM-RECEIPT-CANDIDATE.json) conserva las tres evidencias, tres comprobaciones, cinco reglas K12–K16 y frontera de autorización de [I193](../validation/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json). [La revisión de preparación](../validation/D5-I221-preparation-review.json) y [el sello](../validation/D5-I221-integrity.json) fijan la unidad sin alterar documentos anteriores. Fecha: 24 de noviembre de 2026; no es evidencia de reloj confiable del runtime.

## Prerrequisitos y orden condicional

| Antes del evento indicado | Evidencia que debe existir genuinamente | Estado actual |
| --- | --- | --- |
| Claim | Autorización explícita separada para la operación/scope real. | Ausente; no se concede aquí. |
| Claim | E06 final y payload reales. | Ausentes; componentes sin ejecutar. |
| Claim | Q y root final confiable reales. | Ausentes; no se emiten. |
| Claim | Admisión completa del root bajo hechos de custodia/recursos aceptados. | No admitido; checklist CE11 sin cerrar. |
| Recibo | Claim atómico real de un solo uso y construcción protegida real. | No ocurridos en esta unidad; no se simulan. |

El orden futuro exigido es: hechos CE01–CE11 genuinamente aceptados y prerrequisitos finales/autorización actuales; claim durable después de admisión completa y **antes de paths/spawn**; construcción protegida de exactamente un worker correlacionado; recibo privado sólo a partir de hechos reales y revisables. Cada frontera conserva los controles genuinos de currentness, scope y provenance.

El quinto prerrequisito es necesario antes del recibo; no convierte el claim en su propia precondición. CE11 no depende de CE12 ni de ejecutar claim, spawn o recibo. El mecanismo documental CE06 y la política de mapping CE10 no son evidencia de un claim ocurrido. El recibo no autoriza su propio claim ni aporta retrospectivamente confianza o recursos. No hay comando actual de ejecución en el dossier.

## Contrato del recibo, sin instancia positiva

El schema I191 de `launch_receipt` sigue cerrado y exige 21 campos de primer nivel: schema/record ID/epoch/validity, bundle, caller/dominio, imagen/runtime/source-root, digests C/Q e invocación, ledger/claim/claim epoch/status y constructor/evidencia/rol. El dossier conserva ese contrato y deja todos los slots de valores reales ausentes.

La constante positiva de `claim_status` del schema expresa qué tendría que probar un recibo real; **no es el estado de un claim actual**. Permanece dentro del fragmento de schema, nunca como afirmación de un evento en el wrapper. `actual_claim_status`, `actual_receipt_status`, hashes, tupla e IDs son `null` por ausencia. El dossier no es un recibo I191 aceptado con campos nulos, ceros o identidades inventadas; no se generan muestras positivas o nonces ficticios.

El cap candidato de recibo es 8 192 bytes y la referencia histórica de envelope ASCII de I192 es 2 702. No se verifica un cuerpo real, encoding/cap/digest/schema positivo ni ajuste de heap/CPU. Los campos y referencias requieren evidencia completa fuera de ese índice; el límite de bytes no demuestra disponibilidad o verdad de cuerpos ni admisión.

## Tupla global y evidencia genuina

La namespace de un solo uso es global para `(trust_context_sha256, runtime_request_sha256, invocation_id)` en todos los callers/dominios aprobados y reinicios. No se permite una partición local por caller/restart que habilite reutilización. El dominio de ledger debe concordar con el mapping global único y vigente de CE10.

Se conserva la regla de invocación única, no nula, de 32 octetos y como máximo una request pendiente por contexto. Deben existir pruebas de atomicidad/durabilidad, high-water epoch, protección frente a rollback, doble gasto y crash/replay; un archivo, firma o contador por sí solo no las prueba. Parent y child forman una única invocación correlacionada, no dos consumos independientes. Ningún backend, ledger, namespace, contexto o invocación real se selecciona o crea.

Los seis ámbitos pendientes de evidencia son:

- C/Q/invocación auténticos, con sus bytes/digests exactos y estado one-use aceptado.
- Imagen/runtime/source-root/manifest, caller/dominio y mapping concordantes.
- Mecanismo global durable y scope de ledger/epoch/rollback realmente aceptado.
- Claim ID/epoch/outcome y constructor protegido reales para un único child correlacionado.
- Reloj/epoch/vigencias/currentness/revocación genuinos en todas las fronteras.
- Cuerpo completo de `constructor_evidence` y revisión competente independiente de provenance del claim/recibo.

Cada ámbito tiene ausentes cuerpo, hash, bytes, provider, custodia, reviewer y aceptación. Las cuatro plazas R01/R02/R06/R08 siguen sin persona ni appointment aceptado. El mismo asistente prepara y comprueba; no representa revisión independiente ni aceptación separada R08.

## Fallos y estado gastado: obligaciones sin pruebas ejecutadas

| Situación que debe cubrir la evidencia futura | Disposición exigida, no resultado observado |
| --- | --- |
| Prerrequisitos preclaim incompletos o caducados | Rechazar sin claim/construcción; la ausencia local de claim no demuestra estado global libre o reutilizable. |
| Conflicto, duplicado, epoch obsoleto o rollback | Rechazar; sin partición por caller ni fallback que permita reuse. |
| Claim incierto, parcial, fallido o interrumpido por crash | Gastar o rechazar según mecanismo genuino; no retry gratuito ni claim exitoso ficticio. |
| Reinicio, contexto/request expirados o currentness desconocida | Rechazar invocación/contexto antiguos; cualquier intento futuro exige nueva evidencia/contexto/request/root/autoridad auténticos y autorización separada. |
| Fallo tras claim aceptado o constructor no concordante | No revertir a invocación libre; conservar evidencia real de gasto/fallo y no emitir recibo exitoso sintético. |
| Recibo/body/hash/cap/schema/provenance ausentes o inverificables | Ningún recibo aceptado; sin workaround de output/canal ni autoridad derivada de la ausencia. |

La tabla sólo fija obligaciones. No se evalúan transiciones reales, estado gastado, replay/crash/restart, clocks/ledger o procesos para completar el plan. La falta de evidencia sigue bloqueando la aceptación; no habilita probar una operación prohibida.

## Privacidad, recursos y renovación

El recibo es caller-private y no constituye autoridad o permiso. No se añade campo C/Q/argv/frame, pipe, archivo, helper, Input Reader member, artefacto de captura o salida I187. Se mantienen todos los límites y schemas anteriores. Su custodia sólo podría proceder de memoria/constructor aceptados y acotados; no se elige un backend o canal oculto.

Lookup, freshness, identidad, crypto/measurement, copias, registry/recibo y native/IO por intento siguen dentro de launch/worker/finish y E01–E05, incluidos ambos Reader y el join global. No se convierten costes desconocidos en cero ni se hace gratuita verificación por llamarla offline. Heap/CPU/IO/servicio/reloj/fases/900 segundos y capacidad continúan sin prueba completa.

Se preservan reglas de lifetime <=3600, error conservador <=5, `not_before < expires_at` y checks trusted-now de perfil02 en cada frontera. No se mide reloj ni se crea snapshot. Fecha del cliente, reloj del host, schema o estado documental no acreditan trusted-now/currentness; no hay TOFU, cache obsoleto, lookup oculto ni garantía de revocación instantánea.

Cambios de contribuyente/cuerpo/scope/source/runtime/imagen/dominio/epoch/clave/política/currentness exigen nuevas revisiones de los candidatos afectados y CE11 antes de cualquier evento autorizado por separado. No hay transferencia automática de hashes, pruebas, aprobaciones, mapping, claim o recibo. No se aplica rebind, snapshot refresh, configuración de registry o servicio.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I221-audit.py`.

Resultado requerido: `PASS_STATIC_SOURCE_ONLY_CE12_DEFERRED_NOT_AUTHORIZED`. Contrasta 902 pins con blobs del commit base I220 `f60c5562607916c5f1e30bf4d82770817cf48a12`, preserva 594 archivos publicados y exige cinco archivos nuevos. Reproduce la reconstrucción/revisión documental I220 sin invocar mains históricos de publicación y rechaza doce mutaciones inseguras sólo en memoria. No es un PASS de claim, recibo real, recursos o cualificación.

El replay proyecta como ausente sólo la consulta exacta `Path.exists` de CE12, ausente en el commit base. Se restaura ante éxito y excepción sin cambiar blobs ni controles de otras rutas. Fuera del replay los doce slots documentales CE01–CE12 están presentes. Eso no modifica los estados históricos de I193 ni significa doce pasos aceptados: las aceptaciones reales siguen en cero y CE11 conserva 30 gates pendientes.

Harness runtime: N/A; sólo se revisan documentos/Git/hash, schema/contratos y grafos. No se importan, compilan ni ejecutan producto/componentes, crypto/codec positivos, builds, probes, clocks/ledger, claim/replay/crash/restart, paths/spawn/worker, benchmarks, enrollment, signing, provisioning, servicios o contactos. No cambian cuotas, reservas, presupuesto, bindings, autoridades, destinos o contratos activos.

Commit y push autorizados para una unidad documental; se declara el exceso de 400 líneas por sus contratos, requisitos, pins y preservación. Reversión exacta: retirar este documento, el dossier CE12, `D5-I221-preparation-review.json`, `D5-I221-audit.py` y `D5-I221-integrity.json`. Publicar no crea claim o recibo, no concede autoridad ni cierra recursos/D5. El dossier queda preparado para revisión posterior bajo `DEFERRED_NOT_AUTHORIZED`.
