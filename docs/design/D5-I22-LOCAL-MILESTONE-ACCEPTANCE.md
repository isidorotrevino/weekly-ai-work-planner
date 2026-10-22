# D5 I22 — propuesta de aceptación del hito local sintético

Fecha: 2026-10-22. Estado: **PREPARADO PARA REVISIÓN; aceptación pendiente**.
Hito propuesto: `D5-LOCAL-SYNTHETIC-I1-I20`. **D5 global sigue abierto.**
[Auditoría I21](D5-I21-SCOPE-AUDIT.md) ·
[Matriz documental I21](D5-I21-ACCEPTANCE-REVIEW.md) ·
[Comprobaciones I22](../validation/D5-I22-acceptance-review.json).

English: proposed acceptance of a bounded local synthetic source/BACKLOG lab
milestone. The user accepted the I21 classification and authorized preparing this
proposal, not accepting the milestone or closing global D5. No new SQL or runtime
execution; the executable baseline and recorded I20 evidence remain unchanged.

## Autoridad y unidad de decisión

D5-A51: el usuario acepta la clasificación I21 y autoriza preparar para revisión
la aceptación formal del hito local, con límites y continuidad global, **sin
declarar cierre**. También autoriza publicar exclusivamente `2b18d6c`, ya verificado
en `main`. Esa publicación no aprueba este documento ni su publicación futura.

Esta propuesta fija el siguiente perímetro para una decisión posterior:

| Elemento | Referencia propuesta |
|---|---|
| Hito parcial | Laboratorio local sintético de fuentes, revisión y correspondencias a tareas BACKLOG |
| Implementación | I1–I20; base ejecutable `d20f375f3eb45213d0d759f0530c056dd5ac251b` |
| Auditoría de alcance | I21, `2b18d6c40ee19217a3a95136a2cf0a7203b509a4`; clasificación aceptada por A51 |
| Evidencia de ejecución | [Informe I20](../validation/D5-I20-results.md) y [JSON I20](../validation/D5-I20-results.json), más antecedentes I1–I18 trazados en I21 |
| Entorno acreditado | Clientes Python/CLI locales y PostgreSQL sintético desechable; target integrado V30 + propuestas V31–V39 |
| Estado actual | Propuesta lista para revisión; hito todavía no aceptado, D5 global abierto |

La aceptación reconocerá exclusivamente esas capacidades y evidencias dentro del
entorno registrado. No convierte el laboratorio en servicio persistente, aplicación
para usuarios o integración de producción. No se modifica la arquitectura D1 ni
los contratos/cierres D2–D4.

## Capacidades y criterios de aceptación propuestos

Los criterios siguientes reúnen los contratos aprobados por incremento; no añaden
comportamientos. Cada resultado se refiere a la evidencia histórica citada, no a
una campaña I22. Los límites de tamaño, formatos y comandos siguen siendo los de
los contratos y guías enlazados desde I21.

| ID | Criterio dentro del hito | Evidencia registrada y límite |
|---|---|---|
| H01 | Capturar bytes exactos, revisión etiquetada, hash y procedencia; reconstruir artefactos antes de usar datos | I1–I4, regresiones I20. Etiquetas/hashes no autentican autor, commit ni frescura externa |
| H02 | Mantener perfiles explícitos I1, task-register.v1 y task-register-compat.v1; conservar filas/estados/anotaciones como evidencia | I1–I3 y 51 pruebas locales I20. Duplicados o ambigüedad bloquean; sin parser Gentle-AI completo ni reparación silenciosa |
| H03 | Reutilizar SourceDocument/SourceRevision, almacenar bytes/observación/recibo atómicamente y seleccionar referencia explícita con CAS | 21 casos de persistencia I4 incluidos en I20; sin elegir por fecha ni cambiar punteros D2 existentes |
| H04 | Comparar por documento+ID y revisar el cambio íntegro por fila; simular sin fabricar autorización de efecto D2 | 15 casos I5 incluidos en I20; la aceptación de origen y la del manifiesto de aplicación son distintas |
| H05 | Crear/PATCH/enlazar evidencia mediante correspondencia explícita, solo sobre tareas propias BACKLOG elegibles | M01–M27; Item→title y Objective→description. Una ausencia conserva tarea e identidad; no borra ni cierra |
| H06 | Carga inicial de IDs elegidos con intención v0 y revisión propia, sin comparación ficticia | B01–B28; no importación implícita del documento completo |
| H07 | Reaparición con misma entidad declarada y recibo de ausencia aplicada/versionada, conservando el destino | R01–R30 y LR01–LR36; un ID reutilizado para otra entidad se bloquea |
| H08 | Resolver texto completo del origen o texto local completo con revisión propia, sin mezcla ni excepción permanente | L01–L32, LR01–LR36, IL01–IL36; resolución aislada exige base semántica íntegra idéntica y cabeza aplicada presente |
| H09 | Adoptar explícitamente una tarea existente elegible, preservando toda su fila | A01–A34; mismo proyecto/BACKLOG, sin correspondencia, task_sources o trabajo/planificación previos |
| H10 | Mantener CAS, replay, recibos, atomicidad, recuperación y fronteras de roles/bloqueo de las variantes implementadas | I20 incorpora las regresiones anteriores y sus casos de concurrencia, rollback, reinicio y respuesta perdida; sin garantía externa exactly-once |
| H11 | Preservar contratos previos y separación D3/D4, con laboratorio propio sin red/puertos y limpieza selectiva | Cinco casos de compatibilidad I6 incluidos en I20 y comprobaciones de catálogo/funciones anteriores; sin modificar dev/D4 |
| H12 | No activar trabajo; dejar contadores operativos finales en cero y publicar solo evidencia sintética saneada | I20: 259 tareas BACKLOG de fixtures/regresiones; cero operaciones, intentos, outbox, entregas y reservas; limpieza registrada |

Las matrices completas se consultan en los diseños I7/I9/I11/I13/I15/I17/I19
indexados por I21. El rechazo de variantes fuera del perfil forma parte del
contrato; no se convierte en criterio de implementar esas variantes.

## Evidencia que se propone aceptar

La última campaña integrada I20 registra **264 pruebas SQL**, compuestas por
21 I4 + 15 I5 + 5 I6 + 27 I8 + 28 I10 + 30 I12 + 32 I14 + 34 I16 + 36 I18 +
36 IL. Registra además **51 pruebas Python locales** y **157 D2 independientes**,
sin fallos ni errores en esos grupos. No se suman los totales acumulativos de los
informes anteriores ni se cuenta la campaña D4 como nueva evidencia D5.
D2 conserva su target histórico; las pruebas I4 originales tampoco se presentan
como si hubieran corrido originalmente sobre V30.

I20 identifica PostgreSQL 16.15 y la imagen exacta por digest, registra conservación
del catálogo de funciones/triggers V30 y funciones D5 anteriores dentro del alcance
comprobado, y limpieza de su contenedor/volumen. Estas comprobaciones no significan
invariancia de todas las tablas D2: crear/PATCH de tareas y task_sources está
expresamente autorizado en las variantes correspondientes. Tampoco prueban
resistencia frente a DDL hostil del propietario ni aislamiento de código no confiable.

I21 comprobó hashes históricos, trazabilidad y enlaces. I22 verifica el inventario
I21 en su commit publicado, los inputs ejecutables I20 y que solo cambie el índice
entre los archivos existentes. **No se inicia Docker ni se reejecuta SQL, parser,
D2 o D4**. No se ha detectado un fallo pendiente en el informe I20; esto no es una
garantía de ausencia de defectos ni una revisión exhaustiva de código/seguridad.
Los conteos y hashes nuevos figuran en el JSON I22, no en manifiestos históricos.

El índice `docs/README.md` incorpora este enlace y es el único archivo previo
modificado en I22. Su hash anterior sigue siendo correcto para I21 en `2b18d6c`;
la comprobación histórica usa los bytes de ese commit, mientras el inventario I22
guarda el hash actual. Los 302 inputs restantes de I21 siguen coincidiendo también
en el árbol actual. No se actualiza el informe I21 para atribuirle contenido nuevo.

## Exclusiones que conserva la aceptación local

- Proveedores/credenciales reales, lectura de corpus privado en PostgreSQL y acceso
  a Drive/Plane. Las observaciones privadas I1–I3 son históricas; no se reproducen
  ni publican sus bytes aquí ni se atribuyen a las fixtures SQL.
- Operaciones ejecutadas, activación de tareas, reservas, planificación o entrega
  de trabajo. A18 solo autoriza una fixture negativa transitoria con rollback
  obligatorio; no autoriza operaciones persistentes o ejecutadas.
- IDs reutilizados/transferencias, adopción con trabajo/procedencia previos,
  conversiones de perfil/política, fusión de fuentes o mezcla de campos/texto nuevo.
  Son E01–E05 de I21; requieren caso, contrato y autorización nuevos si se necesitan.
- Integración SQL D5 en Compose dev persistente, daemon, UI o servicio de producto
  (E06). Sheets/Monday sigue opcional según D1 (E07).
- Promoción de propuestas a migraciones de producción, despliegue, cambios de
  secretos/permisos reales, retención operativa y ampliación de D6.

## Continuidad obligatoria de D5 global

Aceptar este hito no elimina ni da por satisfechas las brechas de I21:

| Brecha | Trabajo que permanece abierto | Siguiente evidencia que habría que acordar |
|---|---|---|
| G01 | Contrato Gentle-AI/routing completo | Muestras representativas y scripts, gramática/versiones y matriz aprobada antes de implementar |
| G02 | Ingesta incremental de Drive | Revisiones remotas, permisos, paginación, cursores y errores; contrato y alcance explícitos |
| G03 | Sincronización Plane | Identidad, conflictos, escritura condicionada, idempotencia y conciliación por proveedor |
| G04 | Adaptadores/CLI y cuotas comerciales reales | Autorización separada de proveedor/entorno y evidencia de comportamiento real, sin fallback de pago |
| G05 | Requisitos/épicas y grooming | Contrato y criterios que exceden la proyección Item/Objective→BACKLOG |
| G06 | Perímetro/aceptación global | Decisión integrada cuando existan contratos y evidencia suficientes; aceptar un hito parcial no la sustituye |
| G07 | Validación integrada real | Evidencia del ciclo acordado; los PASS locales/D4 no acreditan efectos externos |

La tabla conserva asignaciones D5; no traslada estas brechas a D6. Las prohibiciones
vigentes impiden ejecutar validación real bajo esta propuesta. Se puede preparar
un contrato documental posterior, pero aceptar este hito no autoriza nuevos
conectores, fixtures, SQL, proveedores o trabajo D6.

## Decisión propuesta al usuario

**Opción A — aceptar exclusivamente el hito local descrito (recomendada):**

> Acepto el hito D5-LOCAL-SYNTHETIC-I1-I20 sobre la base ejecutable d20f375,
> con los criterios H01–H12 y las evidencias y exclusiones descritas en I22.
> D5 global permanece abierto con G01–G07; no apruebo activación, proveedores
> reales, promoción, despliegue, ampliación D6 ni nuevas funciones mediante esta aceptación.

**Opción B — pedir ajustes concretos:** mantener el hito pendiente e indicar el
criterio, evidencia o límite que debe cambiar antes de aceptarlo. Si se solicita
una función nueva, preparar primero su contrato/matriz; no implementarla como
corrección documental implícita.

La decisión queda **pendiente** hasta una respuesta expresa. La conformidad A51
con la clasificación y la preparación de este texto no acepta el hito. Autorizar
publicar este commit tampoco lo acepta. Si se aprueba posteriormente, se registrará
la decisión con nombre de hito local y referencias exactas, conservando abiertos
D5 global y sus brechas; no se creará un cierre global D5 por inferencia.
