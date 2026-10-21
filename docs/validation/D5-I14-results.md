# D5 I14 — resultado del laboratorio de resolución local

Fecha: 2026-10-21. **PASS acotado; D5 abierto.**
[Implementación y autorización A34](../design/D5-I14-LOCAL-EDIT-LAB.md) ·
[Resumen portátil y hashes](D5-I14-results.json).

| Campaña nueva | Comando | Resultado |
|---|---|---|
| V30 + V31–V36, base nueva | `python3 -m testing.D5.run_local_edit_lab` | 158 pruebas: 21 I4 + 15 I5 + 5 I6 + 27 I8 + 28 I10 + 30 I12 + 32 L01–L32; cero fallos/errores |
| Python local | `python3 -m unittest discover -s testing/D5 -v` | 51 pruebas; cero fallos/errores |
| D2 independiente | `bash testing/D2/run-docker-audit.sh` | 157 pruebas; cero fallos/errores/omisiones |

PostgreSQL 16.15, imagen local sin red ni puertos publicados. El JSON registra
imagen, hashes de entrada, tiempo y nombres completos de los casos aprobados.
Los métodos LE01–LE32 corresponden a L01–L32. D2 mantiene su target histórico;
no se atribuyen sus resultados a V30 ni a la campaña HTTPS/procesos D4.

## Matriz L01–L32 ejecutada

| Caso | Evidencia observada — PASS |
|---|---|
| L01 | Preparación sobre tareas I8/I10 y tras I12, replay y estado protegido sin escritura |
| L02 | Ámbito/intención y clave incorrectos rechazados; intención inmutable |
| L03 | L=B rechazado; diferencia local detectada con/sin cambio de row_version |
| L04 | UNCHANGED sin fila, ADDED, ausencia y diagnóstico bloqueante rechazados |
| L05 | Base antes divergente bloqueada; misma fila con distinta observación/posición permitida |
| L06 | ACCEPT I5 requerido; revocación/reaceptación invalida pins |
| L07 | ABA de referencia detectado por versión sin avance implícito |
| L08 | Entradas cerradas, manifiesto inmutable y reconstrucción; razón de preparación distinta exige nueva revisión |
| L09 | Elección/razón inválidas, blancos Unicode, controles, longitud y tipos rechazados |
| L10 | USE_SOURCE escribe solo title/description, row_version +1; otros campos conservados |
| L11 | KEEP_LOCAL conserva tarea íntegra, registra resultado L y proyección de origen S |
| L12 | Convergencia con ambas elecciones sin UPDATE comprobada mediante trigger negativo |
| L13 | S=B con cambio de evidencia: manifiestos completos para ambas elecciones y aplicación KEEP_LOCAL |
| L14 | Cambios disjuntos derivan pareja completa origen/local sin merge |
| L15 | ID largo y texto Unicode/Markdown/pipes íntegros; tachado/anotación como evidencia |
| L16 | Títulos inválidos bloqueados; descripción local NULL conservada y strings fuente vacío/guion diferenciados |
| L17 | Claims DONE/verified/approved no cambian BACKLOG ni activan trabajo |
| L18 | Edición posterior sin cambio de row_version invalida contenido revisado |
| L19 | CAS de campos no mapeados/versiones; ABA observable y convergencia externa bloquean propuesta vieja |
| L20 | Ambas elecciones bloqueadas ante estado/trabajo/plan cancelado; fixtures negativas revertidas |
| L21 | Revisión propia separada, versionada y revocable; pins antiguos bloqueados |
| L22 | Paquetes explícitos, límites/duplicados y variantes I8/I10/I12 aisladas |
| L23 | Replay y ALREADY_APPLIED históricos; command_id global, sin restaurar texto posterior |
| L24 | Sesiones reales para dos paquetes y cambios de referencia/revisión; un avance de cabeza |
| L25 | Paquete con ambas elecciones: fallo de fila, aborto y error tardío revierten efectos D2/D5; aplicación válida conjunta |
| L26 | Commit con respuesta perdida, reinicio, recibo y CLI; JSON duplicado rechazado |
| L27 | Vínculo exacto existente reutilizado, procedencia append-only y lectura por ámbito |
| L28 | KEEP_LOCAL divergente exige otra resolución en el siguiente cambio; cabeza sigue guardando origen |
| L29 | USE_SOURCE y convergencia continúan por I8; edición posterior vuelve a bloquear |
| L30 | Ausencia I8 conservada; I12 bloquea reaparición con divergencia y nueva variante no admite ADDED |
| L31 | Roles/READ COMMITTED y locks cruzados observados; captura D3, cambio de digest y plan publicado inmutable |
| L32 | Número de tareas conservado por resolución; BACKLOG eligible sin operaciones ni activación; catálogo previo preservado |

La campaña final terminó sin fallos. El ensayo previo detectó una expectativa
incorrecta en L08: reason es válido en una revisión y no equivale a alterar la
razón del manifiesto preparado. Se corrigió la prueba para comprobar propuestas
distintas y aceptación propia; L08 se verificó aisladamente antes de esta campaña.
Se reforzó además la coherencia de la proyección histórica en el lector. Las
corridas previas/interrumpidas no se cuentan como evidencia aprobada.

L24/L31 usan sesiones simultáneas con espera observada. L25 comprueba rollback de
estado protegido y tablas D5 —excepto el recibo de conflicto esperado— tras una
fila inválida; un aborto/error estructural no deja recibo de éxito. L26 confirma
recuperación de commit tras perder respuesta y reiniciar. Las operaciones y entradas
CANCELLED son fixtures negativas transitorias con rollback, nunca ejecutadas.
Planes publicados son fixtures del propietario, sin despacho, d3.publish ni outbox.

## Conservación, limpieza y límites

El resumen registra 112 tareas sintéticas BACKLOG de fixture y cero operaciones,
entregas, outbox, intentos, reservas y reservas de plan al terminar. Resolver una
edición local no crea tareas; las de fixture se crean antes con I8/I10. Se eliminó
el contenedor/volumen propio, sin tocar dev/D4. Logs brutos privados en
`work/d5/postgres/d5-pg-*/local-edit-results.json`, con D2 en `work/docker-audit/`.

Coinciden cuerpos, propietarios, ACL/config de funciones D5 anteriores a V36 y
catálogo de funciones/triggers public/D2/D3/D4 respecto a V30. Se conservan
245 entradas de cierre D3/D4, el documento canónico D4 y las
20/27/47/51/55/60 entradas de ejecución I4/I5/I6/I8/I10/I12. I13 conserva su estado
histórico de diseño; A34 autoriza esta implementación. Los 66 hashes de entrada
nuevos corresponden a los archivos ejecutados, incluidos el contrato y su matriz.
Se verificaron 124 enlaces locales, formato correcto y revisión de publicación
sobre 374 archivos de texto sin patrones configurados detectados. No se publican
corpus privado, credenciales o logs brutos.

La semántica del parser sigue dependiendo del adaptador confiable; etiquetas de
revisión no autentican identidad D6. Se valida concurrencia acotada, no escalabilidad
ni DDL arbitrario de un administrador. Un ABA externo sin huella observable no se
presenta como detectable. KEEP_LOCAL conserva texto sin conceder excepción futura.

D5 sigue abierto. Adopción, ID reutilizado para otra entidad, resolución local de
reaparición o sin cambio presente, cambio de perfil/política, múltiples orígenes y
formato Gentle-AI/routing conservan pendientes. Sin proveedores/credenciales reales,
activación, promoción, despliegue o ampliación de D6.
