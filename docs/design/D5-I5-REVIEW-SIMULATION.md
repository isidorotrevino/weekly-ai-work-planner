# D5 I5 — comparaciones persistidas, revisión y simulación

Fecha: 2026-10-21. **Implementado y validado en laboratorio sintético; D5 abierto.**
Continuación posterior: [I6 valida coexistencia SQL sobre V30](D5-I6-V30-COMPATIBILITY.md).
[I4 y sus límites](D5-I4-PERSISTENCE-LAB.md) ·
[Uso](../../testing/D5/README.md#i5--comparación-persistida-revisión-y-simulación) ·
[Evidencia propia](../validation/D5-I5-results.md).

## Decisiones expresas

El usuario pidió continuar los puntos 1 (comparación de observaciones SQL) y 2
(revisión/aplicación de propuestas), y concretó:

| ID | Decisión | Efecto |
|---|---|---|
| D5-A10 | A: revisión y simulación en D5, con decisiones persistidas y recibos; sin escribir requisitos o tareas D2 | Ninguna aplicación operativa, importación o activación |
| D5-A11 | A: cada fila por documento+ID, cambio completo y hashes; sin elegir campos sueltos | Una decisión apunta a un cambio íntegro e inmutable |
| D5-A12 | A: la referencia debe seguir siendo la observación «antes» y coincidir su versión esperada | Un cambio de referencia produce conflicto, incluso A→B→A con versión distinta |

Se mantienen A03 (ausencia nunca borra/cierra), A05 (anotaciones sin autoridad),
A06–A08 (fuentes D2, selección explícita y bytes SQL), los cierres D1–D4 y D6 pendiente.

## Comparación reproducible desde PostgreSQL

El llamante especifica proyecto, documento, observación «antes» y «después».
No se elige por fecha ni se mueve una referencia al comparar. SQL devuelve ambas
capturas del mismo ámbito/perfil en una lectura; Python verifica hashes y bytes,
reconstruye sus perfiles y reutiliza **sin modificar** el comparador I2/I3.
Los temporales privados se eliminan al salir, también ante fallo.

El artefacto `d5.persisted-comparison.v1` conserva el informe original, los IDs
concretos de observación, hashes de fuente/previsualización y cambios revisables.
Se guarda como bytes canónicos exactos, hasta 32 MiB. Su digest identifica todo el
informe; otra recepción del mismo artefacto tiene otro ID de observación y queda
vinculada expresamente. Un informe BLOCKED puede conservarse para diagnóstico,
pero no genera filas revisables. Una comparación consigo misma no crea propuestas. El laboratorio admite hasta 2.000
cambios revisables por informe y 2 MiB de bytes por cambio completo. Exceder un
límite rechaza el comando entero, sin truncar filas o guardar resultados parciales;
no amplía ni altera los límites de los perfiles I1–I3.

Cada cambio ADDED, CHANGED o ABSENT_IN_OBSERVATION lleva bytes canónicos propios
`d5.source-change.v1`, con su hash, fila completa antes/después y referencias a
ambas capturas. El cuerpo incluye campos, marcadores, anotaciones y posiciones
originales. No se deduce un workflow de Status/Verified/Source. UNCHANGED y sus
movimientos siguen en el informe comparativo y no originan una propuesta nueva.

El hash de fila no incluye el hash final del informe: ambos apuntan a las capturas,
y el informe incluye los hashes de sus filas, sin dependencia circular. La decisión
identifica comparación, hash del informe, ID de fila y hash de fila; no basta con
repetir un título o nombre. Los IDs largos se conservan íntegros; las claves de
índice SQL usan un digest derivado, sin truncar el texto. Una colisión no reasigna
identidad: falla la inserción y se revierte el comando.

## Revisión por fila, con versión

`DECIDE_ROW` acepta ACCEPT o REJECT, versión esperada, etiqueta del revisor y motivo.
La cabeza de cada fila empieza vacía en v0. Una decisión exitosa añade un hecho
inmutable y avanza su versión; se puede sustituir con otro comando y CAS correcto.
El comando no admite máscaras de campos ni modifica el cambio revisado.

La etiqueta del revisor es una afirmación del llamante dentro del laboratorio;
no es autenticación humana, firma, permiso D2 ni aprobación de ejecución. ACCEPT
solo permite solicitar una simulación de esa fila. Una decisión no mueve la
referencia de fuente ni se propaga a otra comparación del mismo documento/ID.

`READ_ROW_REVIEW` lee estado actual. `READ_COMMAND` recupera recibos históricos:
repetir un ACCEPT antiguo devuelve su recibo sin reemplazar un REJECT posterior.
Los conflictos confirmados conservan recibo; cambiar su request requiere otro
command_id. Fallos estructurales hacen rollback sin un recibo de éxito.

## Simulación atómica y explícita

`SIMULATE_APPLICATION` recibe la comparación y su hash, versión esperada de la
referencia y una lista no vacía de filas elegidas. Cada entrada fija ID/hash de
fila, comando de decisión y versión. No usa automáticamente «todas las aceptadas».
Se rechazan duplicados y campos adicionales; el orden canónico es por ID de fila.

Bajo el mutex D5, SQL comprueba ámbito, informe no bloqueado, referencia igual al
«antes» con versión exacta y decisiones actuales ACCEPT para **todas** las filas.
Si falla una, guarda un recibo CONFLICT sin resultados parciales ni simulación
exitosa. Una ingesta nueva sin selección no cambia la referencia ni su versión.

| Cambio aceptado | Operación descriptiva simulada | Efecto operativo |
|---|---|---|
| ADDED | STAGE_SOURCE_ADDITION | Ninguno |
| CHANGED | STAGE_SOURCE_CHANGE | Ninguno |
| ABSENT_IN_OBSERVATION | KEEP_EXISTING_NO_DELETE | Ninguno; nunca borrar/cerrar |

El resultado conserva las versiones y decisiones utilizadas, con
`simulation_only: true`, `writes_d2: false` y `activation_allowed: false`. Solo se
escriben hechos de auditoría y recibos D5: no hay estado D2 aplicado, cola, tarea,
requisito, enlace de tarea, evento de outbox, plan o autorización nuevos.
Tampoco se selecciona automáticamente la observación «después».

Un replay exacto de una simulación exitosa sigue siendo un recibo histórico si
posteriormente cambia la referencia o se rechaza la fila. Una simulación nueva
con esos pins obsoletos da conflicto. La vigencia comprobada es la referencia
registrada; no acredita que un archivo externo siga sin cambios o sea auténtico.

## SQL, permisos y frontera de confianza

[V32 propuesta](../../migrations-d5-proposed/V32__comparison_review_simulation.sql)
es aditiva sobre V11+V31 en un laboratorio D5 separado. Añade informes, comparaciones,
filas, decisiones, cabezas de revisión y simulaciones. No cambia V1–V31, el runner
I4, `compose.dev.yaml`, `run_data` o las entradas D4. No hay backfill ni promoción.

Los comandos comparten IDs globales y recibos D5, con el mutex `742005` y READ
COMMITTED. Las funciones nuevas son entradas separadas; no se amplía implícitamente
el envelope aceptado por el submit de fuentes V31. Los hechos rechazan UPDATE,
DELETE y TRUNCATE; solo las cabezas de revisión cambian mediante CAS.

El escritor de ingesta puede guardar comparaciones, el rol sintético reviewer
puede decidir/simular y el lector puede consultar. Reviewer no obtiene DML directo,
submit de fuentes o autoridad sobre D2. PUBLIC no ejecuta funciones D5. Las entradas
propietarias usan nombres calificados y pg_temp al final.

SQL comprueba límites, hashes, ámbito, pins, FKs y versiones. Python reconstruye
comparaciones y cambios antes de revisar/simular y al recuperar informes. Un
escritor SQL directo confiable todavía puede inventar semántica de parser; la
prueba R05 lo demuestra y exige rechazar ese informe al reconstruirlo. Esto no es
una segunda implementación SQL del parser ni una atestación independiente.

## Entrega y frontera siguiente

El runner I5 ejecuta las 21 pruebas PostgreSQL I4 y 15 nuevas sobre V11+V31+V32,
con contenedor sin red/puertos, volumen propio y limpieza comprobada. Se verifican
51 pruebas locales y regresión D2 independiente; resultados en su informe nuevo.
Los artefactos privados y la evidencia histórica I1–I4 permanecen intactos.

El punto 1 queda implementado y el punto 2 cubierto hasta el alcance A10 aprobado.
Siguen pendientes la aplicación operativa y su mapeo a entidades D2, identidades
reales de revisores y cualquier integración D5/V30 o proveedor real. Este corte no
los autoriza ni cierra D5.
