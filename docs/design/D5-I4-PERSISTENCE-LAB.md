# D5 I4 — laboratorio sintético de persistencia

Fecha: 2026-10-21. Implementación acotada del
[contrato aprobado](D5-PERSISTENCE-DESIGN.md), con
[matriz de revisión P01–P10](D5-PERSISTENCE-REVIEW.md).
[Uso del laboratorio](../../testing/D5/README.md#i4--laboratorio-postgresql-desechable)
· [Resultados propios](../validation/D5-I4-results.md).
D5 permanece abierto; D1–D4 cerrados; D6 pendiente.

## Aprobación D5-A09

Tras revisar el diseño publicado en `ee3ea67`, el usuario eligió expresamente:
«A: aprobar el diseño y autorizar implementar y validar un laboratorio PostgreSQL
D5 desechable, solo con fixtures sintéticas; separado de dev/D4, sin promoción ni
despliegue (recomendada)».

Esta decisión sustituye la espera de implementación de la revisión anterior.
No cambia A06/A07/A08 ni autoriza adopción de documentos históricos, ingesta del
corpus privado, activación de tareas, conexiones a proveedores o despliegue.

## Implementación y aislamiento

La propuesta [V31](../../migrations-d5-proposed/V31__local_source_observations.sql)
añade únicamente el schema D5 y permisos limitados para su propietario interno.
El harness usa V1–V11 históricos como base de fuentes D2, en transacciones por
archivo, y después aplica V31 directamente en su propia base sintética. No es
una cadena Flyway de producción ni aplica V12–V30. No modifica archivos, targets,
bootstrap, punteros o funciones D2/D3/D4. No hay backfill.

El contenedor usa la imagen local `postgres:16-bookworm`, `--network none`, sin
puertos publicados y PostgreSQL limitado a socket Unix. Un volumen anónimo propio
conserva la base durante el reinicio probado. La limpieza hace `docker rm -fv`
exclusivamente sobre el contenedor generado por el runner y comprueba que su
volumen ya no exista. Nunca monta `run_data`, datos de desarrollo o fuentes reales.
No recibe el socket Docker: es el harness host quien opera Docker.

Los roles de laboratorio son sintéticos: propietario NOLOGIN/NOSUPERUSER,
escritor y lector separados, sin contraseñas reales. La autenticación local trust
solo existe dentro de ese contenedor sin red. El propietario recibe SELECT,
INSERT y REFERENCES sobre las tablas de fuentes D2, y UPDATE de `id` exclusivamente
para el permiso requerido por FOR SHARE. El escritor y lector no heredan esos
permisos ni tienen DML directo. PUBLIC no puede ejecutar funciones D5. Las
funciones propietarias resuelven nombres calificados y ponen pg_temp al final.
Esto no define autenticación multiusuario ni autorización por proyecto de D6.

## Flujo implementado

1. `register` registra proyecto existente, documento y namespace/clave exactos;
   crea tres referencias vacías v0. Las colisiones no adoptan identidades ajenas.
2. `ingest` reconstruye el artefacto I1/I2/I3 y comprueba bytes, hash y ámbito en
   Python antes de SQL. La transacción SQL conserva revisión, contenido, artefacto,
   observación y recibo, sin seleccionar una referencia.
3. `reference` lee una instantánea de la cabeza del documento/perfil.
4. `select` exige observación del mismo ámbito/perfil y versión esperada. Solo un
   CAS coincidente cambia la cabeza y añade selección y recibo. Incluso volver a
   elegir la misma observación con otro comando incrementa la versión.
5. `receipt` recupera la respuesta histórica del comando. Repetir el comando
   exacto no duplica hechos ni restaura una cabeza antigua.

Un conflicto de negocio confirmado conserva recibo CONFLICT; cambiar su request
exige otro command_id. Un fallo estructural hace rollback y no produce recibo de
éxito. El cliente solo confirma al salir correctamente de la transacción de la
llamada. Un recibo puede describir una versión antigua; para saber la referencia
actual se hace una lectura nueva.

El mutex transaccional D5 `742005` serializa sus escrituras. No usa los mutex ni
las entradas de ejecución D2/D3/D4. READ COMMITTED y funciones VOLATILE permiten
consultar el estado confirmado después de esperar ese lock. Se bloquea la fila
SourceDocument con FOR SHARE durante una escritura, sin cambiar su head público.
No se promete escalabilidad ni convivencia con modificaciones arbitrarias del
propietario SQL. Un cambio externo de identidad o head bloquea nuevos ingresos.

## Bytes y confianza

Los límites son 2 MiB de fuente y 32 MiB de artefacto. Se conserva `bytea` exacto;
JSONB solo representa el request normalizado. El digest de request tiene su propio
dominio, distinto del hash canónico del artefacto. Contenido se deduplica por
documento/hash, artefacto por hash; cada nuevo comando de ingesta conserva su
recepción. Una etiqueta o fecha de ingreso no demuestra una nueva lectura física.

El adaptador no acepta flags del artefacto sin reconstruirlo. SQL comprueba límites,
digests, bytes embebidos, metadatos y FKs; no ejecuta el parser Markdown. Un usuario
con acceso directo como escritor SQL pertenece a esa frontera confiable y podría
inventar semántica consistente con los bytes. No se presenta esa capa como una
atestación independiente del parser o de la fuente.

La API de lectura puede recuperar bytes y artefacto por observación y comprobarlos
de nuevo contra la reconstrucción. No exporta esos bytes por el CLI ni los copia
a la evidencia pública. No hay retención/borrado automático. El laboratorio entero
se destruye al terminar; sus logs y resultados brutos quedan en `work/d5/postgres/`,
ignorado y privado. El corpus privado previo no se lee durante estas campañas.

## Límites de la evidencia

Se prueban sesiones concurrentes esperando realmente el mutex, aborto de sesiones
antes del commit, recuperación tras reinicio, permisos, bytea y CLI. La respuesta
perdida se modela descartando deliberadamente el resultado confirmado y recuperando
el recibo; no se afirma haber simulado una partición de red. El límite exacto de
32 MiB se comprueba como restricción de almacenamiento con padding del propietario
y rollback; no se afirma que ese padding sea un artefacto canónico del parser.

La base es V11 más V31 aislada. Los cierres D3/D4 se preservan por integridad de
archivos y manifiestos; no se ha ejecutado una integración D5 sobre V30 ni se
repiten sus campañas como si fueran evidencia nueva. La regresión D2 mantiene su
harness y resultados propios. D5 aún no publica propuestas, importa tareas ni
implementa revisión/aplicación operativa.
