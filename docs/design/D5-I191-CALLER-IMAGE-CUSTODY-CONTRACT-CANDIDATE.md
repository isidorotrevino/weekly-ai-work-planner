# I191 — Identidad y custodia de caller/imagen como contrato candidato

Fecha: 2026-11-16, Europe/Madrid. Base:
`3c301856df0e0b4af73fb97350618ead35062610`.

**I191 prepara PGO181-CALLER-IMAGE-CUSTODY-CANDIDATE-01 para el perfil 02.**
Define ocho familias de registros cerrados y las condiciones para acreditar
identidad humana/software, imagen/fuentes, dominio de protección y custodia.
No inscribe personas, servicios o claves ni crea una imagen/atestación real.
Continúan la no admisión de I122/PJC115-R2, F179-01 y D5 abiertos.

## Ruta de revisión

1. Leer el [contrato y reglas K01–K16](../validation/D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json).
2. Contrastar los [schemas de evidencia externa](../validation/D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json).
3. Revisar la [preparación](../validation/D5-I191-preparation-review.json),
   el [auditor](../validation/D5-I191-audit.py) y el
   [sello documental](../validation/D5-I191-integrity.json).

Son definiciones y obligaciones para revisión. No son registros positivos
instanciados, configuración activa, nuevas fuentes de confianza o un servicio
implementado. Los bytes de perfil/protocolo 02, schemas I187 y transporte I189
permanecen intactos. No cambian C/Q/I/A/L, los dos canales o los seis operandos.

## Ocho registros, con funciones distintas

| Familia | Qué debe acreditar realmente |
| --- | --- |
| anchor_registry | Autoridad/keys/purpose/epoch aceptados fuera de bundle, C y repositorio |
| actor_registry | Personas canónicas, aliases/competencia y preparación documental completa |
| image_manifest | Bytes de imagen, runtime exacto, seis fuentes y su mapeo, build/dependencias y entrada inmutable |
| caller_identity | Principal software, solicitante humano responsable, imagen, dominio y constructor exactos |
| platform_custody | Mismo caller/imagen/dominio, ocho garantías, clock y ledger one-use global |
| acceptance_record | Proyección y digest exactos de C, roles/claves y aceptación de custodia limitada |
| custody_bundle | Cinco registros anidados, sus hashes y tres aprobaciones sobre el mismo core |
| launch_receipt | Claim/construcción reales de una invocación, sólo en custodia privada del caller |

El registro de anclas sólo es confiable si su digest/epoch/keys/purposes se
seleccionaron de forma independiente en la configuración aceptada del dominio.
Un registro auto-firmado, un key_id o un hash suministrado por el bundle no
crean esa confianza. I191 no elige una autoridad o clave existentes ni afirma
que estén disponibles en el equipo actual.

## Persona, software y aliases no son intercambiables

canonical_actor_id identifica a una persona humana responsable. El
caller_principal_id identifica al principal software/proceso y se vincula al
solicitante humano responsable. Un servicio o segundo nombre de cuenta no puede
usarse como persona distinta para superar S01. La autoridad de identidad debe
resolver aliases, sujetos, competencia y scope de manera auténtica y común.

El registro de actores/preparadores debe ser completo, ordenado y único. Los
hashes de los registros individuales de preparación coinciden con las entradas
documentary_preparers de C y vinculan perfil/schema 02 y contribución real.
No pinnean C, aceptación, bundle o raíz futuros. Nombres, hashes o firmas no
sustituyen la existencia y revisión de los cuerpos de evidencia referenciados.
Los límites de arrays obligan a rechazar o revisar un perfil que no pueda
representar su scope completo; nunca a omitir personas/dependencias.

Se conservan las ocho exclusiones de S01 y las adicionales del perfil 02 sobre
autor de fuentes y claves. Para las nuevas aprobaciones de custodia se exige
además que R08 difiera en persona y clave tanto de R01 como de R02. R01/R02
pueden coincidir si la misma persona es genuinamente competente para ambos
roles, con aprobaciones de dominio distintas. No se modifica la matriz antigua
ni se añade una separación general entre todos los roles.

## Imagen y caller vinculados antes del primer código mutable

El manifest liga las seis rutas sucesoras exactas a sus bytes/miembros de
imagen mediante evidencia auténtica, incluida la representación DOCUMENT de
README cuando corresponda. Pertenecer al manifest no afirma que test/runner se
hayan cargado o ejecutado. El cierre de interpreter/loader/stdlib/frozen/nativo/
crypto y su build debe ser completo y corresponder al runtime exacto aceptado.
Un helper de repositorio adicional requiere scope/grafo/cotas nuevos.

image_bytes_sha256 no sustituye runtime_sha256 o la identidad completa P02.
Tampoco la imagen incrusta su propio hash futuro, el manifest o el bundle:
el expected identity lo selecciona la custodia externa aceptada. El manifest
y el core del bundle comprometen la política/schema I191 exactos, además de
los pins de perfil/protocolo/output/transporte; no negocian su política desde
el bundle recibido.

El caller vincula esa imagen y actor responsable con dominio de protección y
constructor de proceso concretos. La plataforma debe demostrar origen exclusivo
de canales, entrada inmutable, ausencia de shadowing/inyección/tracing/mutación,
owner/grupo y mapeo exacto antes de ejecutar código mutable del repositorio.
Un UID/PID/fd/hash o appointment no acredita esas propiedades ni concede permiso.

Los registros no implementan el mecanismo. R01/R02 deben identificar y acreditar
el backend real y su mapeo al constructor admitido por I189. Si necesita otro
helper, canal, fd, argumento, atestación o lectura para probar la procedencia,
la ruta sin cambios se rechaza o se versiona/revisa. No aparece un transporte
out-of-band gratuito oculto para el worker.

## Orden de aceptación sin préstamo desde evidencia futura

Los hechos de actor/imagen/caller/plataforma deben estar realmente autenticados
y aceptados como antecedentes antes de derivar C o aceptar recursos. Las
firmas posteriores del bundle finalizan su vínculo; no justifican esos hechos
con una aprobación futura aún no emitida. Falta de autenticación previa bloquea.

C se congela con sus campos exactos; acceptance_record compromete su digest y
las relaciones de roles, preparadores, requester, keys, perfil, source/runtime,
basis/index y scopes ya aceptados. Validez de C queda dentro de la de los
registros relevantes y su error de reloj cubre conservadoramente el de plataforma.
repository/root_path/offline_key_status conservan los literales del schema 02.
La aceptación es **sólo de identidad/imagen/custodia**, no cierre de E01–E05,
certificación positiva o permiso de captura.

El bundle incorpora cinco registros y hashes exactos sin autopin. Las tres
aprobaciones R01/R02/R08 usan Ed25519 estricto según perfil 02 sobre el mismo
core y dominios CUSTODY/v1/R01, R02 y R08, cada uno con un octeto NUL separador.
Las claves por purpose/actor vienen de las anclas externas aceptadas; las de C
no pasan a ser automáticamente anclas de custodia. No se firman hash propio,
receipt, Q o raíz futura. No se crean o verifican firmas reales aquí.

El grafo ordena imagen/plataforma, aceptación antecedente, C, bundle y su mapeo
externo; Q y raíz siguen la evidencia final real. El claim queda después de
raíz completa/mapeo/Q y antes de paths/spawn; receipt sólo después del claim.
Es un modelo acíclico de prerrequisitos unido a PGO181, no prueba de hechos
no realizados ni reemplazo de todo el grafo I181.

## Vínculo externo con C, vigencia y one-use

El dominio acepta un único mapeo actual para (configuration_epoch, SHA-256 de
C) entre caller/bundle/imagen/dominio/ledger autorizados. Mapeos conflictivos,
aliases, rollback o epoch desconocido rechazan. El caller resuelve ese mapeo
auténtico antes de P_ROOT_CHECK y congela C/Q y el constructor admitido.
No se añade bundle_sha256 a C/Q ni se toma de un archivo del repositorio.

El worker nace dentro del dominio protegido de esa construcción aceptada;
no recibe el bundle o receipt por un frame/fd nuevo ni los deduce de un PID.
Vuelve a comprobar C/Q/raíz como I189. Si la plataforma real no puede
establecer esa procedencia intrínseca, sigue NOT_ADMITTED.

Los snapshots tienen lifetime máximo 3.600 segundos, epoch vigente y checks
conservadores de tiempo/error del perfil 02. Revocación/supersesión conocida,
ambigüedad o falta de freshness rechazan antes de claim/spawn/release. La
vigencia offline limita exposición; no promete conocer instantáneamente toda
revocación. No se autorizan consultas de red/archivo o fallback TOFU ocultos.

La tupla C-digest/Q-digest/invocation_id usa un único namespace de claim atómico
autoritativo entre todos los callers/dominios y reinicios admitidos. No puede
reutilizarse por crash, rollback o cambio de caller. El hijo es correlacionado,
no otro consumo. La incertidumbre de claim gasta o rechaza la invocación;
el receipt privado no autoriza por sí solo. La durabilidad/atomicidad reales
siguen pendientes, sin servicio, ledger o estado desplegados por I191.

## Cotas de evidencia y costes aún abiertos

| Registro/familia | Cap serializado propuesto |
| --- | ---: |
| Anclas | 65.536 bytes |
| Actores / imagen | 98.304 cada uno |
| Caller / receipt | 8.192 cada uno |
| Plataforma / aceptación | 16.384 cada uno |
| Bundle | 262.144 |

Estos caps acotan registros/índices tipados de custodia, no todo el contenido
de prueba referenciado ni heap/CPU. Schema, codec, cap y verdad/aceptación se
cumplen conjuntamente. Los placeholders de forma usados por el auditor no
acreditan que un bundle real completo quepa o que exista evidencia auténtica.

Son registros externos de custodia aceptada, no nuevos miembros Input Reader,
paquetes de captura o frames. Sólo pueden intervenir mediante memoria/custodia
acotadas e independientes del caller. Todo trabajo automático necesario para
el intento —resolución, freshness, firmas/medición, copia, registry/receipt,
clock/IO/nativo— debe incluirse en t0/fases/E01–E05 y composición global.
Antecedentes humanos/build no permiten trasladar verificación operativa fuera
del launch. Datos/mecanismos extra necesitan cotas y scope/grafo revisados.

C8192/Q2048, I/A/L512 con LF, dos pipes, seis argumentos, output I187 y todos
los números anteriores quedan intactos. Tampoco se infiere fit de las 496
rutas/266.693.693 bytes Reader o de los 900 segundos. La no admisión se mantiene.

## Verificación, pendientes y publicación

`python3 docs/validation/D5-I191-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Contrasta 750 pins con Git y preserva 442 archivos publicados. Comprueba ocho
familias/24 definiciones cerradas, referencias, keys obligatorias/rechazos,
tipos de proyección C, exclusiones simbólicas y orden acíclico. No crea
registros positivos ni ejecuta resolvedor de identidad, firmas, imágenes,
canales o componentes. Reproduce sólo verificaciones documentales anteriores.

El mismo asistente preparó las etapas anteriores y ésta; no hay independencia
de actor/organización, aceptación competente o autoridad de custodia real.
Siguen pendientes revisión/adopción, anclas/identidades/imagen/backend reales,
evidencia completa de mapeo/source/runtime/plataforma/clock/one-use, implementación
autorizada y requalification 179/321/12/30, E01–E05 y fases/heap/CPU/IO/Reader/900;
E06 final, contexto/requests/payload/raíces/firmas y admisión/ejecución separadas.

La unidad tiene seis archivos de work_unit.rollback_files: documento,
schemas, contrato, preparación, auditor y sello. Rollback limitado a ellos.
El diff supera 400 líneas por contratos/evidencia trazables; se informa el exceso.
Runtime harness N/A: sólo preparación documental. Auditoría antes de stage
y tras commit, commit/push solicitados y comprobación remoto/árbol limpio.
Publicar no adopta, inscribe identidades o concede autoridad.

F183-01 conserva reparación documental/ocho exclusiones. E01–E05 abiertos,
E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07/correlación false y cuatro
bindings I175 pendientes. Sin SOURCE_CAPACITY_VERIFIED, rebind, autoridad/
destino nuevos, propuesta/captura habilitadas o D5/H07 cerrados; IR03 NOT_READY.
P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e I1–I20/A52 intactos; brechas
globales/reales pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

Sin ejecutar/importar/compilar producto/componentes, tests, discovery,
benchmarks, criptografía o calendarios runtime ni medir plataforma. Sin cambiar
fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o inputs;
sin inspeccionar ni limpiar dev/run_data/D4. Sin identidades/anclas/registros/
imagen/ledger/canales/firmas/autoridad/evidencia positiva reales creados; sin
proveedores, credenciales, consumo, activación, promoción, despliegue o D6.
