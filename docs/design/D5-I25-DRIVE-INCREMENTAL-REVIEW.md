# D5 I25 — matriz de captura incremental sintética

Fecha: 2026-10-22. **28 casos propuestos; ninguno ejecutado en I25.**
[Contrato A60–A62](D5-I25-DRIVE-INCREMENTAL-DESIGN.md) ·
[Inventario documental](../validation/D5-I25-design-review.json).

English: proposed tests for four synthetic I23 criteria only. Filesystem/process
recovery must be authorized separately before implementation. No real Drive
conformance, power-loss guarantee, D2 writes or global acceptance is implied.

Cada fila tiene estado `DESIGN_NOT_EXECUTED`. Un caso puede requerir varios tests
positivos/negativos. No se suma esta matriz a los 86 tests ejecutados en I24.

| Caso | Criterio I23 | Fixture/estímulo | Resultado exigido |
|---|---|---|---|
| DI01 | GI07 | Scope y mapa file→document/perfil explícitos, génesis con ancla | Identidad exacta, v0 y fase INVENTORY; no adopción por nombre ni referencia D5 seleccionada |
| DI02 | GI07 | Cambios de archivo mientras se enumera inventario | Reproducir feed desde ancla previa y conservar ocurrencias/revisiones observadas; sin prometer historial completo |
| DI03 | GI07 | Inventario de varias páginas y fin | Confirmar cada página completa; no pasar a CATCHUP antes del fin ni sustituir ancla por fecha |
| DI04 | GI07 | Feed con continuación y token terminal | Fases/tokens correctos hasta FOLLOWING; next y new-start incompatibles bloquean |
| DI05 | GI07 | Misma observación repetida en inventario/feed y otra revisión del mismo file_id | Vista lógica deduplicada con ambas ocurrencias; bytes/revisión nuevos se conservan sin adoptar por file_id solo |
| DI06 | GI07 | Página vacía válida y poll vacío con token terminal igual al consultado | Commit íntegro permitido según fase, cero efectos D2 y sin bucle/daemon ilimitado |
| DI07 | GI07 | Cerrar proceso y abrir la misma raíz entre páginas | Reanudar fase/ancla/tokens exactos desde cadena autorizada; no desde memoria, fecha o archivo de número mayor |
| DI08 | GI08 | Página mixta capturas/diagnósticos terminales | Un solo commit alcanzable contiene todos los resultados, bytes/recibo y cursor; no checkpoint independiente |
| DI09 | GI08 | Error transitorio en evento posterior a capturas preparadas | Ningún prefijo confirmado ni avance de head/cursor; retry acotado parte del estado previo |
| DI10 | GI08 | Matar proceso antes de publicar objeto completo | Temporal no es commit; head previo intacto, sin captura confirmada parcial |
| DI11 | GI08 | Matar proceso tras objeto/fsync y antes de cambiar head | Huérfano no adoptado; reinicio conserva head previo y retry no duplica observaciones lógicas |
| DI12 | GI08 | Matar proceso después de head confirmado y antes de respuesta | Recuperar recibo por command_id/request_hash; replay histórico no cambia versión/cursor actual |
| DI13 | GI08 | Fallo de fsync o respuesta incierta durante cambio de head | UNKNOWN_COMMIT; inspección decide según head/cadena verificables, sin presumir rollback ni reintentar a ciegas |
| DI14 | GI08 | Dos escritores con el mismo head esperado y replay con contenido distinto | Solo uno confirma bajo lock/CAS; conflicto sin prefijo; command_id confirmado con otro hash no se reutiliza |
| DI15 | GI09 | Evento de archivo fuera de allowlist | Diagnóstico OUTSIDE_ALLOWLIST durable, sin captura/referencia/elegibilidad implícitas; página puede confirmar |
| DI16 | GI09 | MIME PDF/DOCX no admitido o fuente demasiado grande | Código terminal explícito, sin truncar ni inventar hash de bytes no capturados; sin selección D5 |
| DI17 | GI09 | Removal, pérdida de acceso y archivo no disponible concluyente | Diagnóstico con autoridad limitada; no inferir borrado real, borrar/cerrar D2 o convertirlo en ausencia I8 aplicada |
| DI18 | GI09 | Denegación por archivo frente a fallo global de autorización | Solo el caso terminal de archivo admite confirmar; fallo global bloquea página/conector, no se disfraza de skip |
| DI19 | GI09 | Archivo antes diagnosticado reaparece accesible | Nueva ocurrencia/captura posible, diagnóstico histórico intacto; no exclusión permanente ni tarea nueva automática |
| DI20 | GI09 | Bytes disponibles con parser/perfil/encoding bloqueado | CAPTURED_BLOCKED con bytes acotados y diagnóstico; puede avanzar captura, nunca revisión/efecto |
| DI21 | GI09 | Fuente cambia durante lectura o drive invalida ámbito | Cambio incierto transitorio o scope bloqueado; ninguna bandera caller-terminal lo convierte en éxito |
| DI22 | GI11 | Abrir raíz con otra allowlist, documento/perfil/exportación, proyecto/corpus | Incompatible; no reinterpretar cursor. Raíz/ejecución nueva explícita para otro ámbito |
| DI23 | GI11 | JSON duplicado/campo extra, token/fase equivocados o respuesta mal formada | Rechazo completo, sin avanzar ni omitir eventos inválidos |
| DI24 | GI11 | Más de 16 eventos, JSON >32 MiB o cadena que supera 1.024 commits | Bloqueo antes de confirmar, sin truncamiento silencioso; límites son del laboratorio |
| DI25 | GI11 | Continuación cíclica/repetida y token opaco no numérico | Detectar ciclo de continuación sin ordenar tokens por fecha/número ni inventar expiración temporal |
| DI26 | GI11 | Head ausente/truncado, objeto/hash/parent/bytes/scope incoherentes | Bloqueo conservador; no reparar automáticamente ni escoger huérfano o snapshot viejo por fecha |
| DI27 | GI11 | Dos raíces propias y paths con symlink/hardlink o marca/run_id ajenos | Rechazo de enlace/raíz no válida; sin leer/escribir árbol ajeno o mezclar locks/capturas |
| DI28 | GI11 | Final normal, fallo y reinicio con sentinels hermanos que representan entornos ajenos | Finally limpia exclusivamente raíz creada por harness, sin seguir enlaces fuera ni borrar evidencia histórica |

## Frontera de aceptación

Si se autoriza implementar este contrato, el incremento siguiente deberá registrar
inputs, versiones, tests ejecutados, puntos de fallo y limpieza propios; conservar
los 86 casos Python I24 como regresión nueva identificada si se reejecutan. No
atribuirse ejecuciones SQL/D2/D3/D4 por comprobar sus hashes.

DI01–DI28 respaldarían solo GI07/GI08/GI09/GI11 **en laboratorio sintético**. GI12
real, GI38/GI39/GI40 generales y las demás brechas globales seguirían pendientes.
No existe efecto D2, selección de referencia, nuevo parser, Google SDK/HTTP, SQL,
Docker, proveedor real, promoción/despliegue o D6 en este alcance.

Decisión propuesta: aprobar I25 y autorizar implementar/validar DI01–DI28 con
fixtures públicas sintéticas, procesos locales del harness y su carpeta temporal
marcada, manteniendo los límites anteriores. Alternativa: aprobar solo el diseño
o pedir ajustes; ni publicar el commit ni A60–A62 autorizan automáticamente código.
