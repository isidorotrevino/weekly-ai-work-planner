# D5 I7 — revisión y aceptación del mapeo a D2

Fecha: 2026-10-21. **Preparado para revisión; sin implementación operativa.**
[Contrato propuesto](D5-I7-TASK-MAPPING-DESIGN.md).
Base: `a76aa3c`. D5 abierto; D1–D4 cerrados; D6 pendiente.

## Decisiones ya tomadas y propuesta a revisar

A14 autoriza únicamente diseño/matriz; A15 fija Item → title y Objective → description;
A16 fija correspondencia explícita con UUID/clave interna. No se crean tareas,
SQL, roles o laboratorios en esta entrega.

El contrato concreta para el primer laboratorio futuro: destinos nuevos propiedad
de D5, perfil fijo por documento+ID, manifiesto de efecto D2 revisado por separado,
CREATE_BACKLOG y PATCH_BACKLOG acotados, evidencia sin reinterpretar workflow,
conflicto ante edición local y ausencia sin borrado/cierre. Esas reglas forman la
propuesta que habrá que aprobar antes de implementarla.

El laboratorio futuro debería arrancar sobre V30 y añadir propuestas D5 propias,
con fixtures sintéticas y evidencia nueva. No usaría datos privados ni modificaría
las campañas selladas. La creación de tareas de fixture/importación sería una
ampliación expresa respecto a I6, que terminó con cero tareas y operaciones.

## Matriz requerida — todavía no ejecutada

| Caso futuro | Situación | Resultado exigido |
|---|---|---|
| M01 | Registrar proyecto/documento/ID, UUID y clave interna | Intención explícita, sin crear tarea; scoped uniqueness |
| M02 | UUID/clave ocupados; otro proyecto/documento; perfil distinto | Conflicto sin adopción, duplicado o búsqueda por título |
| M03 | ID largo, fila tachada, Unicode/Markdown/pipes en Item/Objective | Identidad íntegra y proyección literal; sin renderizar/ejecutar |
| M04 | Item vacío; Objective vacío o guion | Título inválido bloquea; descripción conserva su string exacto |
| M05 | Fila Status=DONE/Verified=approved o anotación afirmativa | Nueva tarea BACKLOG v0; ninguna aprobación/operación inferida |
| M06 | Solo ACCEPT I5 o simulación I5, sin revisión del manifiesto | Aplicación denegada |
| M07 | Cambiar tarea/clave/política/proyección después de revisar | Revisión inválida; no sustituir campos ni destino |
| M08 | CREATE explícito desde ADDED o CHANGED no materializado | Una tarea nueva, trazabilidad y recibo atómicos; ninguna operación |
| M09 | PATCH de tarea propia BACKLOG, base y CAS coincidentes | Solo title/description, row_version +1 y updated_at explícitos |
| M10 | Edición local de campos mapeados, con/sin aumento de row_version | LOCAL_EDIT_CONFLICT, incluso tras preparar de nuevo; sin force |
| M11 | Campo local no mapeado, estado, operaciones o planificación cambian tras preparar | CAS completo falla; no sobrescribir ni aplicar parcialmente |
| M12 | Tarea ya en otro estado o con trabajo/plan asociado | Bloqueo antes de aplicar, sin alterar D2/D3/D4 operativo |
| M13 | Cambio solo de anotación/Status/Verified/otros campos no mapeados | Evidencia completa; no cambio de tarea ni versión de esa fila |
| M14 | ABSENT aceptado, con/sin destino materializado | Mantener tarea/identidad/base/vínculos; ningún enlace a una fila inexistente |
| M15 | Reaparición de un ID aplicado; bootstrap desde UNCHANGED | Revisión específica pendiente; no crear otra tarea ni una fuente vacía ficticia |
| M16 | «Antes» nuevo con fila semántica igual, pero otras filas/posiciones distintas | Actualización permitida si la base semántica, perfil, referencia y destino coinciden |
| M17 | «Antes» con base semántica distinta de la última aplicada | Conflicto de base; no resolver por fecha o por igualdad solo de título |
| M18 | Referencia/decisión/intención cambian, incluida secuencia A→B→A | CAS falla aunque reaparezca el mismo valor |
| M19 | Unicidad y vínculos SourceRevision/documento/proyecto/localizador | FK/coherencia exacta; preservar vínculos anteriores; sin duplicar iguales |
| M20 | Replay exacto y otro command_id del mismo paquete ya aplicado | Un efecto; recibo histórico o ALREADY_APPLIED; ninguna versión restaurada |
| M21 | Dos aplicaciones concurrentes, mismas bases o claves ocupadas entre preparación/commit | Serialización y rechazo sin adopción; ningún efecto parcial |
| M22 | Una fila inválida entre varias válidas; fallo antes del commit | Rollback íntegro de tareas, vínculos, bases y auditoría/recibo de éxito |
| M23 | Commit confirmado y respuesta perdida; reinicio | Recuperación del mismo resultado sin repetir efecto |
| M24 | Boundary D3/D2 y mutex D5, con sesiones cruzadas | Orden coherente; sin invertir locks ni ampliar entrypoints antiguos |
| M25 | Roles source/reviewer/reader frente a APPLY/helper/DML | Denegados; propietario de aplicación separado, sin permisos D3/D4 generales |
| M26 | Captura D3 previa a CREATE/PATCH | Base obsoleta detectada; snapshots publicados sin reescritura |
| M27 | task_eligible true en BACKLOG con dependencias satisfechas | No presentarlo como activación; comprobar cero operaciones/entregas/reservas nuevas |

M21/M24 requieren sesiones simultáneas y estado observado tras desbloqueo.
M22/M23 requieren transacciones reales y recuperación, no solo mocks del cliente.
M25 debe probar el helper privilegiado y sus grants: EXECUTE del helper invoker D3
por sí solo no demuestra permisos suficientes. Ninguno de estos casos se declara PASS hoy.

## Verificación de este corte documental

Se revisan V1 (tareas/fuentes), V9 (estado inicial y task_eligible), V10
(task_sources), V12 (readset/locks/capturas D3) y los contratos D5 I4–I6.
Se ejecutan comprobaciones de enlaces, publicación, formato e integridad histórica.
No cambian SQL, harness ni documentación consumida por pruebas; no se arrancan
servicios ni se repiten baterías SQL por este corte documental.

Resultado documental: enlaces de los tres documentos y formato correctos;
publicación revisada sobre 340 archivos de texto; 245 entradas de hash de cierre
D3/D4 más el hash canónico D4 correctos. También coinciden las 20, 27 y 47 entradas
de ejecución registradas en I4, I5 e I6 respectivamente. Esas comprobaciones no
validan la matriz M01–M27 ni acreditan implementación del contrato.

Quedan fuera de la propuesta inicial la adopción de tareas existentes, resolución
forzada de ediciones locales, bootstrap/reaparición, cambio de perfil, multi-origen,
identidades reales de revisores y activación. Gentle-AI/routing e integraciones
reales conservan sus pendientes y exclusiones; este diseño no cierra D5.
