# D5 I4 — diseño de persistencia sintética de fuentes

Fecha: 2026-10-21. **Propuesta concreta para revisión; no implementada ni aplicada.**
Base: `fa333bc`, D5 I3 publicado. D5 sigue abierto; D1–D4 permanecen cerrados.
[Alcance I3](D5-REGISTER-COMPATIBILITY.md) · [Revisión y criterios](D5-PERSISTENCE-REVIEW.md).

## Autoridad y decisiones

El usuario eligió diseñar el contrato de fuentes, revisiones y observaciones, con
identidad y concurrencia, **sin aplicar migraciones todavía**. Después resolvió:

| ID | Elección expresa | Consecuencia del diseño |
|---|---|---|
| D5-A06 | A: reutilizar SourceDocument/SourceRevision y añadir observaciones D5 | Identidad registrada explícitamente; contratos y punteros D2 existentes intactos |
| D5-A07 | A: selección explícita con versión esperada | Ingerir no selecciona referencia ni decide frescura; otro comando hace CAS |
| D5-A08 | A: bytes en PostgreSQL, con límites | Contenido, artefacto, observación y recibo se confirman atómicamente |

Estas elecciones fijan el diseño. No aprueban todavía un DDL, su implementación,
una ejecución V31, importación de datos privados ni cambio del entorno Compose.
No se crean archivos `.sql`, roles, bases, servicios o conexiones en este corte.

## Frontera y hallazgos del contrato vigente

D2 ya tiene `public.source_documents`, `public.source_revisions`, ExternalBinding,
`d2.task_sources`, `d2.sync_source` y acuses de outbox. V7 exige coherencia de
proyecto/documento; V5 hace append-only las revisiones; V10 deduplica por
`(document_id, sha256)`. Se conservan sin redefinirlos.

`d2.sync_source` cambia el head público y el cursor del binding. **No se reutiliza
para el nuevo ingreso local**: mezclaría observación con selección. El nuevo
contrato no modifica `current_revision_id`, bindings, requisitos, tareas, planes,
cuentas, reservas, leases, checkpoints o autorizaciones. No genera eventos en el
outbox público ni llama a entradas D2/D3/D4 de ejecución o planificación.

La persistencia local propuesta guarda snapshots y afirmaciones, no la verdad de
una aprobación, una revisión Git, una fecha de captura ni una identidad del editor.
`PREVIEW_ONLY` nunca equivale a elegibilidad de trabajo.

## Identidad explícita

`REGISTER_SOURCE` recibe proyecto UUID **ya existente**, documento UUID, namespace
y clave lógica. Namespace/clave son etiquetas del operador, no rutas ni URLs: texto
UTF-8 no vacío, máximo 256 bytes cada uno, sin controles ni espacios exteriores.
Se comparan exactamente; no hay normalización de mayúsculas, Unicode o rutas.

- Un documento D5 pertenece a un solo proyecto y a una sola pareja namespace/clave.
- Un `(project_id, namespace, logical_key)` identifica un único documento.
- Una ruta relativa es procedencia de una observación; cambiarla no reasigna identidad.
- Los UUID de I1–I3 siguen siendo identidades declaradas por el llamante: antes de
  persistir deben corresponder exactamente al registro y proyecto solicitados.
- El rol de ingesta no crea proyectos, no busca identidades por nombre ni vincula
  documentos por hash, título o similitud.

Para una fuente nueva, la función propietaria crea `SourceDocument` con el UUID
explícito, `source_type = OTHER`, URI reservada
`urn:weekly-ai-work-planner:d5:source:<document_uuid>` y `current_revision_id = NULL`.
El detalle `LOCAL_MARKDOWN` queda en D5 y no amplía el enum D2. La URI con UUID
respeta el UNIQUE global D2 `(source_type, source_uri)` sin introducir rutas privadas.

Un documento ya registrado por D5 solo se reutiliza si coincide toda la identidad.
Una colisión con documentos/bindings históricos no se adopta automáticamente:
`ADOPTION_REQUIRED` o `IDENTITY_CONFLICT`, sin backfill ni reasignación. El primer
laboratorio admite fuentes nuevas administradas por D5; adoptar legados requerirá
un contrato posterior. Si cambia externamente la identidad/URI/tipo o aparece un
head público en un documento administrado, se bloquea el ingreso para revisión;
no se restaura ni sobrescribe ese estado ajeno.

## Contenido, artefacto y observación son entidades distintas

**Contenido/revisión:** los bytes exactos, hasta 2 MiB, identificados por SHA-256 y
documento. Un contenido nuevo crea una revisión D2 y su vínculo D5 en una sola
transacción. Para estas revisiones locales nuevas, `external_revision = NULL`:
la etiqueta del llamante no se convierte en una revisión de proveedor.
`content_ref = d5:content:<document_uuid>:sha256:<hash>` es una referencia opaca
al registro SQL; nunca una instrucción de lectura del filesystem o de red.
`source_revisions.observed_at` conserva su significado histórico de primera
inserción; no se reescribe con cada observación ni acredita frescura física.

**Artefacto:** JSON canónico exacto I1/I2/I3, hasta 32 MiB, guardado como `bytea`
con su hash. JSONB puede servir como proyección para consultas, pero no reemplaza
los bytes ni se usa para reconstruir su hash canónico. El perfil y sus anotaciones
se conservan exactamente; no se cambia de perfil durante el ingreso.

**Observación de ingreso:** hecho append-only de recibir un artefacto bajo un
comando. Conserva etiqueta del llamante, autoridad CALLER_LABEL_ONLY, ruta relativa,
perfil, revisión de contenido, hash de artefacto y `ingested_at` del reloj SQL.
Esa fecha prueba orden de ingreso observado por la base, no momento de captura
ni vigencia de la fuente. El ID de observación es el UUID del comando INGEST.

| Entrada | Revisiones de contenido | Artefactos | Observaciones |
|---|---|---|---|
| Replay exacto del mismo comando | Sin aumento | Sin aumento | Sin aumento |
| Otro comando con el mismo artefacto | Reutiliza | Reutiliza | Nueva recepción, sin fingir nueva lectura |
| Mismos bytes y nueva etiqueta | Reutiliza | Nuevo si cambia el JSON | Nueva |
| Mismos bytes bajo otro perfil | Reutiliza | Nuevo | Nueva, sin alias entre perfiles |
| Bytes nuevos del mismo documento | Nueva | Nuevo | Nueva |
| Mismos bytes de otro documento | Revisión propia | Artefacto propio | Recepción propia |

Una coincidencia de hash debe contrastar también bytes/identidad existentes antes
de reutilizar. Una discrepancia se rechaza, no reemplaza el blob. No se mezclan
contenidos ni procedencias de proyectos distintos. No hay retención/borrado automático.

## Modelo relacional propuesto — todavía sin DDL

Todos los nombres son una propuesta, en schema nuevo `d5`. Las tablas de hechos
rechazarán UPDATE, DELETE y TRUNCATE para roles de aplicación. El propietario de
DDL sigue siendo una autoridad confiable, como en D2.

| Relación | Claves y contenido | Restricciones relevantes |
|---|---|---|
| `source_registrations` | PK documento; proyecto, namespace, clave; comando de registro | UNIQUE proyecto/namespace/clave; FK compuesta documento/proyecto a D2; identidad inmutable |
| `revision_content` | PK documento/hash; revisión D2 y `source_bytes` | FK revisión/documento D2; FK registro; UNIQUE revisión/documento; longitud y digest; contraste de sha/content_ref con la revisión D2 |
| `preview_artifacts` | PK hash canónico; documento, proyecto, revisión, perfil; `preview_bytes` | FKs de ámbito; límite/digest; identidad/contenido extraídos iguales al registro y revisión; UNIQUE hash/documento/proyecto/revisión/perfil para FKs posteriores |
| `observations` | PK comando INGEST; artefacto, ámbito, perfil, etiqueta/ruta y fecha SQL | FKs compuestas a artefacto y registro; UNIQUE observación/documento/proyecto/perfil; comando diferible hasta COMMIT |
| `reference_heads` | PK documento/perfil; proyecto, observación nullable, versión bigint | FK registro; FK compuesta observación/documento/proyecto/perfil; versión inicial 0; actualización solo por SELECT_REFERENCE |
| `reference_selections` | PK comando; antes/después, versión anterior/nueva, motivo | Hecho append-only ligado al recibo y a la misma cabeza; cada éxito aumenta exactamente una versión |
| `commands` | PK UUID global D5; request normalizado, digest, respuesta y fecha SQL | Append-only; misma ID con cuerpo distinto no puede reutilizar resultado |

`REGISTER_SOURCE` inicializa cabezas vacías, versión 0, para los tres perfiles
conocidos. Eso no selecciona una observación. No se crean perfiles desde un texto
arbitrario recibido del cliente; ampliar el catálogo requiere otro cambio revisado.

Los FKs usan los pares existentes `(document_id, project_id)` y
`(revision_id, document_id)`: no necesitan alterar restricciones D2. Donde un FK
no puede expresar el hash/content_ref entre tablas, la entrada propietaria y una
guarda de inserción deberán contrastarlo contra la revisión inmutable. Los vínculos
a comandos podrán ser DEFERRABLE para insertar el recibo al final de la transacción.
El DDL posterior debe demostrar estas propiedades, no darlas por cumplidas por esta tabla.

## Entradas y respuestas propuestas

Un envelope cerrado `d5.source-command.v1` contiene `command_id`, `action`,
`project_id`, `document_id` y los campos de su acción. Campos adicionales o tipos
incorrectos se rechazan; no se coercionan strings a números o booleanos. No hay SQL,
URI ejecutable, credencial, aprobación de tarea o función arbitraria en el request.

| Acción | Campos propios | Efecto autorizado |
|---|---|---|
| `REGISTER_SOURCE` | namespace, logical_key | Crear la identidad nueva y sus cabezas vacías, o confirmar la identidad idéntica |
| `INGEST` | preview_sha256, content_sha256, profile; blobs como parámetros binarios | Guardar contenido/revisión, artefacto y recepción; ninguna cabeza cambia |
| `SELECT_REFERENCE` | profile, observation_id, expected_version, reason | Elegir explícitamente una observación del mismo ámbito/perfil mediante CAS |

Las etiquetas y rutas proceden del artefacto reconstruido; no hay una segunda copia
editable en el envelope. El recibo es un resultado histórico, `receipt_only: true`.
`SELECT_REFERENCE` devuelve `version_at_commit`, no una promesa sobre la versión
actual. `READ_REFERENCE` consulta una instantánea nueva de cabeza+metadatos;
`READ_COMMAND` recupera el recibo sin releer un archivo perdido. Ninguna lectura
es un grant, una aprobación de trabajo ni un comando de ingesta.

Una captura bloqueada bajo el perfil estricto puede conservarse y elegirse como
referencia de diagnóstico. Su comparación **sigue BLOCKED**. Seleccionar no cambia
`comparison_eligible`, el perfil ni una propiedad del snapshot. Igual ocurre con
la vista estructural I1: puede referenciarse, pero no se convierte en registro
comparable. El comparador mantiene todas las fronteras I2/I3.

## Validación y confianza antes de SQL

El adaptador local confiable ejecutará la verificación de `load_preview`: nombre/hash,
JSON sin claves duplicadas, bytes base64 y reconstrucción exacta del perfil.
No confiará en flags enviados por un usuario/worker. Esa verificación ocurre antes
de adquirir locks SQL; la implementación del adaptador de conexión aún no existe.
El producto Java D1 no se sustituye ni se despliega por este diseño de laboratorio.

La base comprueba longitudes antes de conversiones costosas, digest de los `bytea`,
coherencia de metadatos y FKs. Debe comprobar que los bytes fuente concuerdan con
los bytes codificados en el artefacto. SQL no ejecuta el parser ni demuestra por
sí solo la semántica de sus resultados: el rol escritor corresponde al adaptador
confiable que los reconstruye. Las pruebas distinguirán esa frontera; no llamarán
"prueba independiente" a una bandera insertada por el propietario SQL.

Los blobs permanecen privados en una base sintética. Ninguna llave se guarda en un
request. El migrador/propietario se separa del escritor de ingesta y del lector;
PUBLIC no obtiene funciones ni DML. El escritor no hereda roles D2/D3/D4 ni obtiene
SELECT/DML directo sobre sus tablas. Las entradas SECURITY DEFINER usarán objetos
calificados, search_path fijo con pg_temp al final y ningún SQL dinámico del cliente.
No se añaden usuarios reales ni secretos: su despliegue pertenece a D6.

## Transacciones, idempotencia y concurrencia

Primer laboratorio conservador: un mutex transaccional **propio de D5** serializa
sus comandos de escritura. No se afirma escalabilidad ni se adquieren los mutex
D3/D2, porque no se invocan esas operaciones. Orden propuesto: mutex D5 → comprobación
de recibo → registro/SourceDocument → cabeza si procede → hechos → recibo.
Las funciones escritoras serán VOLATILE y exigirán READ COMMITTED para consultar
el estado confirmado después de esperar el lock. Una conexión/llamada por comando;
sin I/O, parsing, llamadas externas o espera de procesos bajo locks.

1. Validar y reconstruir los blobs fuera de la transacción; preparar request cerrado.
2. En SQL, comprobar límites/coherencia y tomar el mutex D5. Releer el recibo.
3. Si existe, exigir el mismo request normalizado y la identidad de blobs recibidos.
   Devolver la respuesta anterior sin mutar hechos ni cabeza. Un cuerpo distinto
   devuelve COMMAND_CONTENT_CONFLICT y no reemplaza el recibo.
4. Sin recibo, contrastar registro/ámbito. INGEST reutiliza o crea contenido y
   artefacto, añade observación y recibo en **la misma transacción**. No selecciona.
5. SELECT_REFERENCE comprueba ámbito/perfil y `expected_version`. Coincidencia:
   incrementar versión, actualizar cabeza y añadir selección+recibo atómicamente.
   Incluso elegir de nuevo la misma observación con un comando nuevo aumenta la
   versión; solo el replay exacto es neutro.
6. Desajuste de versión o identidad lógica: registrar un recibo de CONFLICT y no
   alterar cabeza ni registrar una selección exitosa. El conflicto se devuelve
   como resultado, no como excepción que borre su recibo al hacer rollback.
7. COMMIT antes de confirmar al llamante. Fallos estructurales, de blobs o FKs hacen
   rollback completo; no se presenta un recibo de éxito de una transacción abortada.

El digest de request se define sobre su representación JSONB normalizada en SQL,
con dominio/versionado propio; **no es el hash canónico de artefacto I1/I2/I3**.
La igualdad del request guardado también se contrasta, no solo su digest. El
adaptador rechaza claves duplicadas del envelope antes de convertirlo a JSONB.

Cada versión bigint debe ser no negativa, aumentar sin overflow y nunca reiniciarse.
Un cambio A→B→A no valida un request que todavía espere la versión del primer A.
Un conflicto confirmado requiere lectura nueva y **otro command_id**; cambiar la
versión esperada del comando ya recibido es conflicto de contenido. Un timeout o
rollback sin recibo permite repetir el mismo comando exacto, sin deducir éxito.

| Traza razonada, no ejecutada | Resultado previsto |
|---|---|
| Dos INGEST simultáneos, distinto comando, mismos bytes | Una revisión, artefacto reutilizado si idéntico, dos recepciones |
| Dos SELECT_REFERENCE con expected_version=0 | Un éxito v1; un CONFLICT; ninguna selección silenciosa del perdedor |
| Éxito v1, después otro comando lleva a v2, luego replay del primero | Recibo histórico v1; la cabeza sigue v2 |
| Referencia contenido A v1 → B v2 → A v3; llega CAS esperado v1 | CONFLICT aunque vuelva a coincidir el hash A |
| Fallo antes de COMMIT | Nada nuevo de ese comando; deduplicados ya existentes permanecen |
| COMMIT y respuesta perdida | READ_COMMAND/replay recupera el mismo recibo; no duplica observación/selección |

El futuro harness deberá demostrar esas trazas con sesiones concurrentes y fallos
reales. Esta revisión de diseño no es evidencia de aislamiento PostgreSQL ejecutado.

## Compatibilidad, futura migración y aprobación pendiente

No se renombra ni modifica V1–V30. Un futuro DDL se propondría en ubicación D5
separada, con target propio posiblemente V31 y harness sintético independiente.
Ese número no está reservado ni aplicado por esta sesión. No se modifica el
bootstrap D4 V30, `compose.dev.yaml`, sus datos persistentes ni campañas anteriores.
No hay backfill de fuentes o snapshots locales existentes; el primer laboratorio
usaría únicamente fixtures sintéticas y datos de proyecto preparados por su dueño.

El estado inicial esperado tras ese futuro DDL es D5 vacío, sin fuentes adoptadas,
sin heads seleccionados y sin eventos que activen trabajo. La aprobación para
implementar/ejecutar ese laboratorio será una decisión distinta de D5-A06/A07/A08.
[Revisión para esa decisión](D5-PERSISTENCE-REVIEW.md).
