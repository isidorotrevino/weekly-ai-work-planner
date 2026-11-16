# I205 — CE04 preparado con fuentes, imagen y runtime ausentes

CE04 (IMAGE-SOURCE-BASELINE) queda **preparado como dossier documental de evidencia
faltante**, sin fuentes sucesoras, imagen, runtime, build o mapeos reales. No se
crea ni acepta un image_manifest. Su freeze final continúa en CE08; caller,
plataforma y recursos conservan sus fases propias. PGO181 candidato 02/PJC115-R2
mantienen la no admisión, D5 abierto e IR03 `NOT_READY`.

Fecha del cliente: 2026-11-16, Europe/Madrid. Base publicada I204:
`718387a5c0158931dac173ae75919befe482bb0a`.

## Entrega y dependencia pendiente

[CE04 candidato](../validation/D5-I193-CE04-IMAGE-SOURCE-BASELINE-CANDIDATE.json)
ocupa la ruta exacta de `/steps/3` de I193. Conserva tres requisitos de evidencia,
tres checks, frontera de autorización y K04/K05/K07/K15/K16. La checklist asigna
image_manifest a CE04/CE08 y su finalización a CE08. El wrapper tiene schema
documental propio; no es un registro positivo I191 rellenado con nulos.

CE03 quedó confirmado documentalmente como provisional en I204, sin identidades
ni aceptación competente. Esa dependencia real sigue insatisfecha. I205 permite
preparar una declaración de faltantes, sin aceptar CE01–CE04 ni obtener artefactos
por contacto, creación de fuentes, build, import, medición o ejecución.

El inventario fija 17 documentos por hash/tamaño: I193/checklist, I191/pack,
CE01/CE03/I204, I181, I122, las referencias de políticas y P02 histórico I135/I136.
Son fuentes documentales, no bytes de imagen ni evidencia del runtime sucesor.
Los 822 pins se contrastan con Git y disco.

## Seis fuentes y mapeos ausentes

Las seis rutas exactas siguen sin crear bajo
`testing/prospective_capture_joint_prp181/`. Cada fila conserva hash/tamaño de
fuente, miembro/digest/representación de imagen, evidencia de mapping y
observación de carga ausentes, sin aceptación.

| Ruta lógica, relativa al namespace | Restricción o estado |
| --- | --- |
| `capture.py` | Mapping auténtico pendiente; no código importado/ejecutado |
| `atomic.py` | Mapping auténtico pendiente; no prueba de atomicidad transferida |
| `worker.py` | Mapping auténtico pendiente; sin proceso worker |
| `test_joint_capture.py` | Membership no implica carga, ejecución o cualificación |
| `run_joint_lab.py` | Membership no implica carga o ejecución del runner |
| `README.md` | Debe ser `DOCUMENT`; representación real no suministrada |

El techo de diseño de las seis fuentes sigue en 262.144 bytes. El total real y
source-root commitment permanecen ausentes: no se suman fuentes desconocidas como
cero ni se reutilizan hashes I122 para el sucesor. No se amplían rutas/helper scope:
cualquier helper de repositorio debe estar ligado al histórico480 o a las seis
fuentes y correctamente contabilizado, sin lecturas runtime adicionales I122.

## Evidencia por consumidor y fase

| Obligación | Consumidor | Alcance, actualmente faltante |
| --- | --- | --- |
| IM01 | CE04 | Seis cuerpos fuente exactos, hashes/bytes y source-root commitment real |
| IM02 | CE04 | Seis mappings auténticos fuente→miembro/representación/digest; README documento |
| IM03 | CE04 | Cierre completo interpreter/loader/stdlib/frozen/native/crypto/dependencias y procedencia de receta/toolchain/build |
| IM04 | CE04 | Digest de imagen separado de identidad runtime/P02 completa y aceptada |
| IM05 | CE04 | Evidencia de políticas compiladas exactas y ausencia de own future image/manifest/bundle hashes |
| IM06 | CE04 | Evidencia baseline auténtica de imagen/miembro/primera entrada inmutable, sin descargar selección caller o enforcement de plataforma |
| IM07 | CE05 diferido | Caller/constructor/dominio/loader y origen exclusivo de endpoints heredados |
| IM08 | CE06 diferido | Garantías completas por plataforma contra shadowing/tracing/mutación/inyección de fd y controles de origen |
| IM09 | CE07 diferido | Recursos/compatibilidad completos del sucesor, E01–E05,179/321/12/30, heap/CPU/IO/Reader/900 s |
| IM10 | CE08 diferido | Freeze final tras identidades/autores y antecedentes completos, actor registry antes de image/caller/platform y antes de C |

Las diez filas están `MISSING_NOT_EVALUATED`, sin proveedor, localizador,
nombramiento, cuerpo/hash/tamaño o aceptación reales ni permiso de contacto.
Hay seis obligaciones baseline CE04 y cuatro referencias diferidas a sus
consumidores propios. No se añade una dependencia inversa CE04 hacia CE05–CE08,
ni se declara aceptación implícita de sus pruebas por disponer de un baseline.

K07 permanece completo: la evidencia baseline de entrada de imagen no sustituye
el mecanismo real de constructor/enforcement que deben acreditar CE05/CE06.
No se selecciona ni invoca constructor aquí. Cualquier pipe/fd/argv/helper/file,
attestation o confianza ambiental adicional requiere revisión explícita de
scope/grafo/costes o rechazo de la ruta sin cambios; no aparece implícitamente.

## Imagen, runtime, políticas y cierre

`image_bytes_sha256` es el digest de la imagen externa final; no sustituye a
`runtime_sha256`, al P02 de identidad exacta o a la procedencia completa de
intérprete/stdlib/native/runtime. I136 rechazó la identidad runtime histórica de
I122 y la decisión `actual_runtime_identity_verified` continúa falsa. Sus bytes
ni sus hashes documentales califican al sucesor. El Python del auditor y el
entorno local tampoco se usan como evidencia de runtime; no se muestrean.

Las dependencias reales y su número siguen ausentes. Los seis fragmentos de
schema son exactos: image_manifest, image_member_binding, image_dependency,
source_bindings, evidence_reference y validity. La lista futura de dependencias
1–128 debe ser realmente completa y auténtica: no se trunca para caber ni se
confunde una lista con prueba de cierre. El cuerpo final image_manifest tiene
cap candidato de 98.304 bytes, ajeno a este wrapper y a todos los cuerpos de
prueba subyacentes. No se ejecuta codec/schema/crypto sobre un cuerpo real.

Se fijan siete requisitos de políticas compiladas: perfil02, protocolo, output,
contrato/gramática de transporte y pack/contrato de custodia. Cada pin documental
coincide con su fuente y con las constantes de schema que correspondan. Los valores
compilados reales y su aceptación independiente siguen ausentes: un pin del
repositorio no es prueba de que la imagen lo implemente ni selección externa real.

La política prohíbe incrustar los futuros digests propios de imagen/manifest/bundle;
la identidad esperada de imagen debe seleccionarse mediante custodia externa
aceptada. No se inspecciona código o imagen inexistente ni se afirma verificada
la ausencia de autoembedding. Los hechos de imagen/build deben ser antecedentes,
sin hashes predictivos post-run ni autenticación retrospectiva por bundle/root.

CE08 conserva actor_registry primero, luego image_manifest, caller_identity y
platform_custody, con todos los autores/evidencias reales antes de C. No hay
manifest final, registry de autores aceptado, epoch/validez o hash de freeze aquí.
Los cambios de contribuyentes, cuerpos, identidad/runtime/imagen, políticas o
scope invalidan dependientes según I193; ese refresh no aplica un rebind activo.

## Costes, permisos y preservación

K15 mantiene lookup/frescura/identidad, verificación de firma/medición necesaria,
copias/registry/recibo y todo trabajo nativo/IO dentro de launch/worker/finish,
t0 y composición global E01–E05. Enrollment/build previos no vuelven gratuita
la verificación por intento. Cuerpos/canales/helpers nuevos requieren bounds y
grafo revisados; el expediente no añade miembros Input Reader ni campos C/Q.
No se demuestra servicio, recursos, compatibilidad, heap o los 900 segundos.

R01/R06/R08 permanecen sin persona, identidad canónica, nombramiento, competencia,
clave/vigencia o aceptación. El mismo asistente/chat prepara el dossier, sin
independencia personal u organizativa acreditada ni adopción competente. Las
cuatro acciones documentales y 14 clases denegadas preservan la frontera; no hay
contacto, fuentes nuevas, build/import/medición, producto/componentes, claves,
cripto, claim, worker o autoridad creados para suplir carencias.

I122 sigue `IMPLEMENTED_NOT_ADMITTED`, CP03 verdadero sólo en su alcance heredado,
CP07 falso, atomicidad correlacionada no verificada y componentes `NOT_RUN`.
Siguen ocho exclusiones S01, cuatro separaciones extra, nueve condiciones CP07,
candidatos numéricos, E01–E05 abiertos y cero obligaciones cerradas; E06 separado
sin ejecutar y F179-01/S01 sin aceptación. Ocho cuerpos I191 y los otros ocho
dossiers planificados permanecen ausentes. No cambian cuotas/reservas/presupuestos,
schemas activos, Reader/canales, capture_inputs/bindings ni destino.

## Verificación documental y publicación

Crear CE04 ahora no reescribe los registros que lo describían ausente. La auditoría
prueba con `git ls-tree` su ausencia en la base I204 y sólo proyecta la consulta de
presencia de esta ruta exacta mientras reproduce funciones documentales I204.
Los guards CE03/CE02/CE01 originales permanecen anidados; `finally` restaura el
método. Fuera de esa reproducción se exige CE04 real y sus bytes correctos,
CE01–CE03 preservados y los otros ocho slots ausentes. Ningún histórico se edita
ni se ejecutan sus `main` de publicación.

```sh
python3 docs/validation/D5-I205-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_IMAGE_SOURCE_RUNTIME_MISSING`.
[La preparación reproducible](../validation/D5-I205-preparation-review.json)
comprueba nueve contraejemplos sólo en memoria: adelantar freeze a CE04; README
no documento; atribuir carga por membership; sustituir runtime por imagen; sumar
fuentes ausentes como cero; transferir prueba I122; afirmar cierre de dependencias;
tratar un pin documental como compilado; o aceptar CE04 desde documentación.
No son tests de producto/componentes. [El sello](../validation/D5-I205-integrity.json)
preserva 514 archivos publicados y fija los otros cuatro artefactos de la unidad.
Harness runtime: N/A, baseline documental sin creación de fuentes/build/import/
medición/producto/componentes/cripto/codec/claim/protocolo.

Unidad única superior a 400 líneas por pins, matrices y preservación; se declara
el exceso sin recortar evidencia. Commit/push publica para revisión estos cinco
archivos y limita la reversión a ellos:

- `docs/design/D5-I205-CE04-IMAGE-SOURCE-BASELINE.md`
- `docs/validation/D5-I193-CE04-IMAGE-SOURCE-BASELINE-CANDIDATE.json`
- `docs/validation/D5-I205-preparation-review.json`
- `docs/validation/D5-I205-audit.py`
- `docs/validation/D5-I205-integrity.json`

El siguiente alcance posible es revisar este dossier CE04 y sus fronteras de
baseline, runtime/política y fases diferidas. La evidencia auténtica y todas las
aceptaciones/finalizaciones reales siguen pendientes, sin liberar D5.
