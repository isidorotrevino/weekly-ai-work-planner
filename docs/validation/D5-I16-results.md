# D5 I16 — resultado del laboratorio de adopción

Fecha: 2026-10-21. **PASS acotado; D5 abierto.**
[Implementación y autorización A40](../design/D5-I16-ADOPTION-LAB.md) ·
[Resumen portátil y hashes](D5-I16-results.json).

| Campaña nueva | Comando | Resultado |
|---|---|---|
| V30 + V31–V37, base nueva | `python3 -m testing.D5.run_adoption_lab` | 192 pruebas: 21 I4 + 15 I5 + 5 I6 + 27 I8 + 28 I10 + 30 I12 + 32 I14 + 34 A01–A34; cero fallos/errores |
| Python local | `python3 -m unittest discover -s testing/D5 -v` | 51 pruebas; cero fallos/errores |
| D2 independiente | `bash testing/D2/run-docker-audit.sh` | 157 pruebas; cero fallos/errores/omisiones |

PostgreSQL 16.15 (Debian 16.15-1.pgdg12+2), imagen local sin red ni puertos publicados.
El JSON registra imagen, hashes de entrada, tiempo y nombres completos de casos.
Los métodos A01–A34 corresponden a la matriz I15. D2 mantiene su target histórico;
no se atribuyen sus resultados a V30 ni a la campaña HTTPS/procesos D4.

## Matriz A01–A34 ejecutada

| Caso | Evidencia observada — PASS |
|---|---|
| A01 | Preparar/replay sin escribir tarea, intención, cabeza, destino o procedencia; proposed_intent_id visible |
| A02 | Dos propuestas revisadas sin reserva; rechazo no ocupa identidad y otra puede aplicarse |
| A03 | Ámbito/UUID/clave/perfil/política incorrectos y clave incompatible con límites I8 rechazados |
| A04 | Reserva v0 e identidad ya materializada bloquean; otro ID no permite volver a adoptar la misma tarea |
| A05 | Procedencia previa idéntica bloquea preparación/aplicación; borrado de hechos rechazado |
| A06 | Preparación y aplicación bloquean estado, operación y plan histórico CANCELLED; fixtures revertidas |
| A07 | ID largo y Unicode/Markdown/pipes íntegros, fila tachada/anotada y tarea local conservada |
| A08 | Fila ausente, duplicados y ambigüedad no seleccionada bloquean snapshot sin selección parcial |
| A09 | Perfil compatible y anotación conservados; solo una fila seleccionada materializa correspondencia |
| A10 | Referencia previa requerida y ABA de referencia invalida paquete anterior |
| A11 | Hashes fuente/preview/fila y bytes incorrectos rechazados; observación distinta con mismos bytes no sustituye el pin |
| A12 | Títulos inválidos bloqueados; descripción local NULL conservada y Objective guion literal |
| A13 | Fuente igual o distinta del texto local: trigger negativo comprueba ausencia de INSERT/UPDATE/DELETE tasks |
| A14 | Epic_id, urgencia, fecha, diferimientos y dependencia de fixture conservados |
| A15 | Claims DONE/approved/verified no alteran BACKLOG ni activan trabajo |
| A16 | Razón vacía/solo blancos Unicode, controles, exceso y tipos inválidos rechazados |
| A17 | Entrada cerrada y manifiesto inmutable; nueva razón exige revisión; lector detecta proyecciones/identidad alteradas |
| A18 | Manifiesto sin comparación/base previa ficticias; revisión propia requerida, no transferible a I8/I10 |
| A19 | Versión monotónica y revocación/reaceptación invalidan pins antiguos |
| A20 | Lista explícita, límites/duplicados, único origen/tarea y snapshot; paquetes I8/I10 separados |
| A21 | CAS completo detecta edición sin row_version, ABA observable y campos no mapeados |
| A22 | Dos paquetes concurrentes: un ganador, una intención y un vínculo; tarea v0 intacta |
| A23 | I8 sigue rechazando tarea ocupada; reserva v0 para mismo origen/otro destino bloquea adopción |
| A24 | Dos órdenes reales de FK: APPLY espera a procedencia previa y rechaza; insert externo posterior espera al commit de adopción |
| A25 | Revocación concurrente y cambio de referencia durante espera se serializan con validación vigente |
| A26 | Intención compartida coincide con manifiesto, FK al PREPARE real, cabeza v1/S y auditoría propia sin escritura de tarea |
| A27 | Paquete mixto inválido, aborto y fallo tardío revierten D2/D5/recibo; paquete válido aplica junto sin alterar textos |
| A28 | Replay histórico, ALREADY_APPLIED y command_id global sin restaurar texto posterior |
| A29 | Recuperación tras perder respuesta y reiniciar, CLI y JSON duplicado; tarea sin incremento de versión |
| A30 | Continuidad real I5/I8: PATCH, enlace de evidencia y ausencia con identidad conservada |
| A31 | Divergencia bloquea I8; I14 KEEP_LOCAL/USE_SOURCE funciona sobre base adoptada y exige cambio real |
| A32 | Ausencia aplicada/reaparición I12 funcionan; divergencia local y reinicialización I10 siguen bloqueadas |
| A33 | Permisos/READ COMMITTED/locks cruzados y captura D3; tarea y digest/readset de fixture conservados, plan publicado inmutable |
| A34 | Número de tareas conservado por adopción; eligible sin activación; cero operaciones/outbox/entregas/intentos/reservas y catálogo intacto |

El ensayo aislado de 34 casos pasó antes de esta campaña. Un primer intento de
campaña completa se detuvo antes de ejecutar casos porque la imagen local no
estaba disponible; tras comprobar su disponibilidad se ejecutó la campaña completa.
No se cuentan ese intento ni resultados parciales como evidencia aprobada.

A22–A25/A33 usan sesiones reales y espera observada. En A24, FOR UPDATE bloquea
contra la FK de task_sources: una procedencia previa confirmada impide adoptar.
En el orden inverso, el insert externo espera al commit de adopción y después
puede confirmar: prueba del punto de serialización, no una prohibición eterna de
escrituras del administrador. Ese segundo vínculo es fixture externa explícita,
no una importación D5 de múltiples orígenes. Los dos hechos de espera se registran
en fk_wait_events del JSON.

A27 comprueba rollback de estado protegido y tablas D5, exceptuando el recibo de
conflicto de negocio esperado. Aborto/error estructural no deja recibo de éxito.
A29 confirma recuperación tras perder respuesta y reiniciar. Operación y planificación
CANCELLED son fixtures negativas con rollback, nunca ejecutadas; planes publicados
son fixtures de propietario, sin despacho, d3.publish ni outbox.

## Conservación, limpieza y límites

La campaña termina con 152 tareas BACKLOG sintéticas de fixture y cero operaciones,
entregas, outbox, intentos, reservas y reservas de plan. Las tareas de adopción son
fixtures creadas antes de invocar sus comandos; V37 no hace DML de tarea. Se eliminó
el contenedor/volumen propio sin tocar dev/D4. Logs brutos privados:
`work/d5/postgres/d5-pg-*/adoption-results.json`, con D2 en `work/docker-audit/`.

Se conservan cuerpos, propietarios, ACL/config de funciones D5 anteriores a V37
y catálogo de funciones/triggers public/D2/D3/D4 respecto a V30. Coinciden
245 entradas de cierre D3/D4, documento canónico D4 y las
20/27/47/51/55/60/66 entradas de ejecución I4/I5/I6/I8/I10/I12/I14. I15 conserva
su estado histórico; A40 autoriza esta implementación. Los 72 hashes de entrada
nuevos corresponden a los archivos ejecutados, incluidos contrato y matriz.
Se verificaron 130 enlaces locales, formato correcto y revisión de publicación
sobre 383 archivos de texto sin patrones configurados detectados. Los 91 archivos
históricos capturados y los cuatro archivos de código ejecutado siguen idénticos.
No se publican corpus privado, credenciales ni logs brutos.

La semántica del parser depende del adaptador confiable; etiquetas de revisión no
autentican identidad D6. Se valida concurrencia/recuperación acotada, no escalabilidad,
DDL arbitrario o ABA externo sin huella observable. El readset/digest D3 se conserva
en la fixture A33; no se extrapola invariancia global ante otros cambios concurrentes.

D5 sigue abierto: adopción con procedencia/trabajo previos, transferencias, IDs
reutilizados para otra entidad, resolución local de reaparición o sin cambio presente,
perfil/política, múltiples orígenes y Gentle-AI/routing completo conservan pendientes.
Sin proveedores/credenciales reales, activación, promoción, despliegue ni ampliación D6.
