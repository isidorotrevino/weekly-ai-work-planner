# D5 I27 — matriz de conciliación Plane sintética

Fecha: 2026-10-22. **32 casos propuestos; ninguno ejecutado en I27.**
[Contrato A64–A66](D5-I27-PLANE-RECONCILIATION-DESIGN.md) ·
[Inventario documental](../validation/D5-I27-design-review.json).

English: proposed bounded in-memory model tests for GI15–GI17; no real Plane
conformance, durable restart, D2 application or global D5 acceptance is claimed.
Todos los casos tienen estado `DESIGN_NOT_EXECUTED`. Una fila puede exigir varios
tests; no se suma a las 116 pruebas históricas de I26.

| Caso | Criterio | Fixture/estímulo | Resultado exigido |
|---|---|---|---|
| PC01 | GI15 | Binding y tarea/proyectos explícitos; variar payload, paquete y command_id | Clave estable por tupla; sin adoptar por nombre ni crear nueva identidad por cambiar paquete |
| PC02 | GI15 | Repetir binding_id distinto para misma tupla o ligar un remoto a dos tareas | Unicidad local; no elusión del conflicto pendiente |
| PC03 | GI15 | CREATE válido con capacidades de fixture explícitas | Un objeto, recibo de creación exacto y destino explícito; solo TASK de fixture |
| PC04 | GI15 | Respuesta perdida tras creación atómica | UNKNOWN local; un objeto remoto y ningún segundo envío automático |
| PC05 | GI15 | Conciliación exacta por clave/ticket/hash tras PC04 | EFFECT_CONFIRMED y mismo ID; cero creación adicional |
| PC06 | GI15 | Lecturas eventuales devuelven cero, incluso repetidas | UNKNOWN conservado; no presumir ausencia ni habilitar retry |
| PC07 | GI15 | Lectura fuerte vacía con ticket aún en vuelo | UNKNOWN, sin reenviar ni cancelar implícitamente |
| PC08 | GI15 | Misma clave produce múltiples coincidencias o ámbito ajeno | CONFLICT; no escoger resultado por fecha/orden ni adoptar |
| PC09 | GI15 | Misma clave y payload original, o misma clave con otro payload | Primero recupera recibo/ID; segundo bloquea creación, sin duplicado |
| PC10 | GI15 | Dos envíos compiten sobre una clave y dos conciliadores sobre ledger | Un ticket local consumido por intento; unicidad atómica del doble y CAS de recibo sin duplicados |
| PC11 | GI15 | Objeto encontrado por clave pero sin recibo/hash exacto, o texto editado después | No atribuir efecto sin prueba; con prueba conservar efecto histórico y edición actual, sin restaurar texto |
| PC12 | GI16 | D2 cambia entre preparar/revisar y enviar | Paquete obsoleto, cero llamadas al doble |
| PC13 | GI16 | Revocar/reemplazar ACCEPT antes de enviar | STALE_REVIEW; revisión de fuente/publicación no concede autorización |
| PC14 | GI16 | Binding/capacidad/política cambia antes de enviar | Paquete inválido; ni cambiar clave ni degradar precondición |
| PC15 | GI16 | Fuente/payload de manifiesto o request de command_id se altera | Hash/esquema/replay incompatible bloquean; sin envío parcial |
| PC16 | GI16 | D2 cambia durante llamada tras consumir ticket | Efecto remoto puede existir; registrar hecho y STALE_LOCAL sin compensación o nuevo envío |
| PC17 | GI16 | Revocar aprobación durante envío y perder respuesta | UNKNOWN + STALE_REVIEW; permitir solo conciliación histórica A66 |
| PC18 | GI16 | Conciliar PC16/17 con efecto exacto | Recibo histórico confirmado y conflicto de vigencia visibles; sin éxito vigente, PATCH o rollback fingido |
| PC19 | GI16 | Replay antiguo tras nuevo paquete/edición remota | Devuelve recibo histórico; cero escrituras y cero restauración de payload viejo |
| PC20 | GI16 | Callback remoto intenta adquirir lock local; otro hilo cambia estado | Llamada fuera de lock; revalidación posterior detecta cambio sin deadlock ni permiso implícito |
| PC21 | GI16 | CREATE confirmado seguido de nuevo texto y UPDATE revisado | Mismo destino; UPDATE exige base remota nueva, revisión y capacidades vigentes |
| PC22 | GI16 | UPDATE con edición remota antes/durante CAS, incluido A→B→A | Precondición monótona detecta cambio; sin sobrescritura ni pérdida de campos ajenos |
| PC23 | GI17 | Timeout/error incierto tras dispatch, respuesta malformada o ACK solo local | UNKNOWN, sin éxito ni rechazo concluyente inventados; bloquea nuevas escrituras del binding aunque haya otro paquete |
| PC24 | GI17 | UPDATE aplicado con respuesta perdida y luego otra edición remota | Conciliar recibo por ticket/hash; mantener edición actual y conflicto, no repetir PATCH |
| PC25 | GI17 | Rechazo explícito del doble con garantía atómica de no efecto | REJECTED_NO_EFFECT; retry solo explícito con todas las guardas y mismo payload/clave |
| PC26 | GI17 | 429 concluyente con retry_after válido frente a 429 ambiguo | Primero espera tick mínimo sin sleep; segundo UNKNOWN sin retry automático |
| PC27 | GI17 | retry_after inválido/ausente, cuota de intentos agotada o versiones cambiadas | Bloqueo; comando nuevo no reinicia presupuesto ni elude revisión |
| PC28 | GI17 | Reintento válido tras negativo concluyente | Attempt_id nuevo, presupuesto consumido y evidencia anterior intacta; sin fallback |
| PC29 | GI17 | Se agotan seis consultas con UNKNOWN o desaparece destino confirmado | Mantener incertidumbre/conflicto; no recrear ni borrar D2 por silencio |
| PC30 | GI17 | Reinicializar modelo perdiendo ledger, o falta de capacidades | No afirmar recuperación durable ni autorizar escritura; modelo nuevo no hereda bindings/derechos |
| PC31 | GI17 | Campos extra, modo real, tipos/UUID inválidos, tamaños/budgets excedidos | Rechazo cerrado, sin truncar, llamadas HTTP, secretos o payload crudo en recibos |
| PC32 | GI17 | Final de campaña y regresión I24/I26 separada | Evidencia propia, cero operaciones/activación/D2 persistente/HTTP/SQL/Docker y ninguna brecha global cerrada |

## Puerta de implementación

Propuesta: aprobar I27 y autorizar implementar PC01–PC32 exclusivamente con dobles
en memoria, reloj lógico y concurrencia controlada del harness, sin persistencia
ni reinicio de proceso. Informar tests realmente ejecutados, límites y regresiones
sin sumar filas de matriz a tests ni reutilizar resultados como ejecuciones nuevas.
GI15–GI17 seguirán etiquetados como evidencia de modelo; GI18 y las demás brechas
requieren sus evidencias/decisiones propias. Alternativa: aprobar solo diseño o
ajustarlo. A64–A66 y publicación Git no autorizan por sí solas la implementación.
