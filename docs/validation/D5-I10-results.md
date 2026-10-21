# D5 I10 — resultado del laboratorio de carga inicial

Fecha: 2026-10-21. **PASS acotado; D5 abierto.**
[Implementación y autorización A23](../design/D5-I10-BOOTSTRAP-LAB.md) ·
[Resumen portátil y hashes](D5-I10-results.json).

| Campaña nueva | Comando | Resultado |
|---|---|---|
| V30 + V31–V34, base nueva | `python3 -m testing.D5.run_bootstrap_lab` | 96 pruebas: 21 I4 + 15 I5 + 5 I6 + 27 I8 + 28 B01–B28; cero fallos/errores |
| Python local | `python3 -m unittest discover -s testing/D5 -v` | 51 pruebas; cero fallos/errores |
| D2 independiente | `bash testing/D2/run-docker-audit.sh` | 157 pruebas; cero fallos/errores/omisiones |

PostgreSQL 16.15, imagen local `postgres:16-bookworm`, sin red ni puertos publicados.
El JSON registra imagen, 55 hashes de entrada y nombres de los 96 casos aprobados.
D2 mantiene su target histórico independiente; sus resultados no se atribuyen a V30
ni a la matriz HTTPS/procesos D4.

## Matriz B01–B28 ejecutada

| Caso | Evidencia observada — PASS |
|---|---|
| B01 | Preparación/replay conservan tablas protegidas, con cabeza v0 y fila íntegra |
| B02 | Scope/perfil/intención inválidos y clave ocupada rechazados sin adopción |
| B03 | Destino materializado o ausencia previa con cabeza avanzada no vuelven a cero |
| B04 | ID de más de 5.000 caracteres, texto Unicode/Markdown/pipe, tachado y anotación conservados |
| B05 | IDs duplicados y fila ambigua no seleccionada bloquean snapshot en adaptador y SQL |
| B06 | Título vacío bloqueado; descripción vacía/guion literal en manifiesto; avisos compatibles conservados |
| B07 | ID ausente, lista vacía, duplicada, >2.000, artefacto >2 MiB o pin desconocido rechazados |
| B08 | Solo fila seleccionada importada; fila no seleccionada sin intención y título vacío permanece fuera |
| B09 | ACCEPT I8 y comparación no sustituyen revisión bootstrap ni inventan before/decisión I5 |
| B10 | Hashes/bytes alterados y fila distinta del preview rechazados; ningún éxito reconocido |
| B11 | Manifiestos inmutables, hash alterado y campos extra rechazados; aceptación no transferible |
| B12 | Sin revisión o con pins obsoletos/ABA no se aplica; revisión monotónica permite paquete nuevo |
| B13 | Sin referencia, otra observación de iguales bytes o secuencia A→B→A causan conflicto |
| B14 | Lista exacta produce mismo hash; dos propuestas de una intención o mezcla con I8 se rechazan |
| B15 | Status=DONE/approved/tachado/anotación producen BACKLOG v0 con defaults I8 |
| B16 | FK de procedencia, localizador exacto, cabeza v1 y auditoría; vínculos anteriores inmutables |
| B17 | Entry points I5/I8 existentes continúan con PATCH, enlace de evidencia y ausencia sin borrado en la misma tarea |
| B18 | Persisten conflictos por base semántica distinta, CAS completo y edición local |
| B19 | Cambian solo tarea, procedencia y auditoría entre tablas protegidas; referencia/punteros/cursors ajenos conservados |
| B20 | Replay histórico, ALREADY_APPLIED y command_id global entre variantes, sin restaurar campos locales |
| B21 | Otro paquete sobre intención aplicada falla; nueva observación con más filas no amplía la selección |
| B22 | Dos paquetes bootstrap y bootstrap frente a CREATE I8 compiten en sesiones reales: un ganador y un conflicto |
| B23 | Clave ocupada tras preparar invalida paquete mixto completo, conserva tarea preexistente y registra conflicto |
| B24 | Backend terminado antes de commit y trigger de fallo después del INSERT revierten tareas, vínculos, cabeza, auditoría y recibo |
| B25 | Respuesta descartada tras commit, reinicio real y recibo/CLI recuperados sin repetir efecto |
| B26 | Source/reviewer/reader sin APPLY; callers sin DML; espera D3 no toma D5; espera D5 mantiene 742001/742002; captura D3 completa tras liberar |
| B27 | CREATE cambia digest D3; plan publicado de fixture permanece idéntico e inmutable |
| B28 | BACKLOG eligible sin activación; cero operaciones, entregas, intentos, outbox y reservas; catálogo y funciones anteriores conservados |

B22/B26 observaron esperas y resultados entre sesiones reales. B24 mata un backend
con transacción abierta y además inyecta un fallo de fixture tras insertar tarea;
el trigger y su función temporal también se revierten. B25 confirma commit con
stdout descartado y reinicia PostgreSQL antes de recuperar. No son solo mocks.
La operación negativa de M12, repetida como regresión autorizada A18, siempre se
revierte y nunca se ejecuta. Los planes publicados M26/B27 son fixtures del
propietario; no se llama a d3.publish ni se generan entregas o outbox.

## Conservación y limpieza

Al terminar había **43 tareas sintéticas BACKLOG**, cero operaciones, entregas,
intentos, outbox, reservas y reservas de plan. El contenedor y su volumen anónimo
propios se eliminaron. Los datos no se guardan en Compose dev/D4; los diagnósticos
privados quedan en `work/d5/postgres/d5-pg-*/bootstrap-results.json`, con D2 aparte
en `work/docker-audit/`. No se publican logs brutos, corpus privado o credenciales.

Se compararon definiciones, propietarios, ACL/configuración y triggers antiguos
public/D2/D3/D4 con el catálogo V30, además de todas las definiciones de función D5
anteriores a V34. Se conservaron migraciones, adaptadores y runners anteriores.
Coinciden las 245 entradas de cierre D3/D4, el documento canónico D4 y las
20/27/47/51 entradas de ejecución registradas I4/I5/I6/I8.

I9 permanece como contrato histórico de diseño; A23 autoriza esta implementación.
V34 sigue siendo propuesta para un laboratorio nuevo, sin promoción o despliegue.
Se comprueban enlaces, formato e higiene de publicación antes del commit.

La semántica del parser depende de la reconstrucción confiable del adaptador;
SQL privilegiado directo no autentica al autor ni sustituye esa verificación.
No se afirma escalabilidad, resistencia a DDL arbitrario del administrador o nueva
validación de procesos D4. Etiquetas de revisión no son identidad autenticada.
D5 sigue abierto: reaparición, adopción, resolución local, cambio de perfil/política,
múltiples orígenes y formato Gentle-AI/routing conservan sus pendientes. D6 y
proveedores/credenciales reales, activación, promoción y despliegue permanecen fuera.
