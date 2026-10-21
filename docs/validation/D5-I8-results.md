# D5 I8 — resultado del laboratorio de tareas sintéticas

Fecha: 2026-10-21. **PASS acotado; D5 abierto.**
[Contrato implementado y decisiones A17–A19](../design/D5-I8-SYNTHETIC-TASK-LAB.md) ·
[Resumen portátil y hashes](D5-I8-results.json).

| Campaña | Comando | Resultado |
|---|---|---|
| V30 + V31/V32/V33, base nueva | `python3 -m testing.D5.run_mapping_lab` | 68 pruebas: 21 I4 + 15 I5 + 5 I6 + 27 M01–M27; cero fallos/errores |
| Python local | `python3 -m unittest discover -s testing/D5 -v` | 51 pruebas; cero fallos/errores |
| D2 independiente | `bash testing/D2/run-docker-audit.sh` | 157 pruebas; cero fallos/errores/omisiones |

PostgreSQL 16.15, imagen local sin red ni puertos. El JSON registra ID de imagen,
hashes de entrada y nombres completos de las pruebas aprobadas. Los resultados D2
pertenecen a su target histórico independiente, no se atribuyen a V30 o D4.
Las 41 regresiones previas se ejecutaron antes de crear tareas en los casos M.

## Matriz ejecutada

| Caso | Evidencia observada — PASS |
|---|---|
| M01 | Intención sin tarea/FK de destino; replay y mismo ID en otro documento |
| M02 | UUID/clave/intención ocupados y scope/perfil incompatibles rechazados |
| M03 | ID de más de 5.000 caracteres y proyección literal Unicode/Markdown/pipe/tachado |
| M04 | Título vacío bloqueado; descripción vacía y guion conservados al aplicar |
| M05 | DONE/approved/anotación/tachado producen BACKLOG v0, sin inferir workflow |
| M06 | ACCEPT/simulación I5 no autorizan aplicación sin revisión del manifiesto |
| M07 | Hash alterado rechazado por adaptador/SQL; campos extra y mutación de manifiesto denegados |
| M08 | CREATE desde ADDED y CHANGED no materializado, tarea/vínculo/auditoría/recibo |
| M09 | PATCH conserva campos ajenos y created_at, incrementa versión una vez; fecha en D5 según A19 |
| M10 | Edición local con y sin incremento de versión bloquea, incluso al preparar de nuevo |
| M11 | Edición de urgencia tras preparar causa CAS completo; preparación nueva conserva ese valor |
| M12 | Estado BLOCKED, operación y entrada de planificación impiden aplicar; fixtures negativas revertidas |
| M13 | Cambio de campos ajenos/anotación añade evidencia sin reescribir tarea |
| M14 | Ausencia con/sin destino conserva identidad, base y vínculos; no crea fila después |
| M15 | Reaparición y bootstrap UNCHANGED pendientes explícitos, sin duplicar tareas |
| M16 | Nueva observación antes y posiciones distintas con semántica igual permiten PATCH |
| M17 | Diferencia semántica de estado de origen impide aplicar aunque el título coincida |
| M18 | ABA de referencia/revisiones y avance de correspondencia invalidan paquetes obsoletos |
| M19 | FK de ámbito, localizador exacto, vínculos inmutables y reutilización de vínculo idéntico |
| M20 | Replay histórico y ALREADY_APPLIED sin restaurar tarea ni repetir efecto |
| M21 | Aplicaciones concurrentes del mismo paquete y de paquetes distintos serializadas; clave ocupada entre preparación y aplicación rechazada |
| M22 | Backend terminado antes de commit revierte efectos; paquete mixto con manifiesto revocado aplica cero filas |
| M23 | Respuesta descartada después de commit, reinicio real y recuperación por recibo/CLI sin repetir efecto |
| M24 | APPLY espera en D3 sin bloquear flujo fuente; mientras espera en D5 mantiene 742001/742002; captura D3 concurrente completa tras liberar |
| M25 | Source/reviewer/reader sin APPLY/helper/DML; aplicador sin DML directo ni autoridad D3/D4; helper de administrador |
| M26 | CREATE/PATCH cambian digest D3, conservan plan publicado de fixture y su inmutabilidad |
| M27 | task_eligible=true en BACKLOG; cero operaciones, outbox, intentos y reservas |

M21/M24 observaron sesiones reales esperando locks. M22 terminó un backend con
transacción abierta; M23 reinició PostgreSQL tras commit. Ningún PASS se basa
únicamente en mocks o en la existencia de una función/grant.

La operación de M12 existe solo dentro de una transacción revertida autorizada por
A18; nunca se ejecuta ni deja entregas o reservas. El plan publicado M26 es una
fixture histórica creada por el propietario de la base, sin llamar a d3.publish,
sin outbox y sin despliegue. Se verifica su conservación e inmutabilidad, no una
campaña nueva de publicación/dispatch D3 o de procesos HTTPS D4.

## Conservación y límites

Se conservaron definiciones, propietarios, ACL y configuración de funciones y
triggers de aplicación antiguos public/D2/D3/D4. El resumen registra el digest del
catálogo. El esquema de tareas D2 no cambia. Su tabla carece de updated_at; A19
corrige esa expectativa del diseño I7 y guarda la fecha en D5.

Coinciden las 245 entradas de hash de cierre D3/D4, el documento canónico D4 y
las 20/27/47 entradas de ejecución anteriores I4/I5/I6. Los informes, migraciones,
adaptadores y runners previos siguen intactos. Los diagnósticos de desarrollo y
las ejecuciones fallidas previas se conservan privados; este PASS corresponde a
la campaña final registrada con sus hashes.

Al terminar se verificaron cero operaciones y outbox. Las tareas del laboratorio
son sintéticas; no hay workers activos ni conexiones a proveedores. El contenedor
y su volumen propio se eliminaron. Los logs brutos permanecen bajo
`work/d5/postgres/d5-pg-*/mapping-results.json`, con D2 en `work/docker-audit/`.

La reconstrucción del parser sigue siendo frontera del adaptador confiable I4/I5;
SQL directo privilegiado no acredita esa semántica. Se validan READ COMMITTED,
locks y concurrencia acotada, no DDL arbitrario de un administrador o escalabilidad.
Las etiquetas de revisión no autentican personas reales. Bootstrap, reaparición,
adopción y resolución de ediciones locales requieren decisiones posteriores.
D5 permanece abierto; D6 no se amplía. Sin datos/proveedores/credenciales reales,
activación, promoción o despliegue.
