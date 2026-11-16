# I183 — Schemas exactos y confianza candidatos; continúa la no admisión

Fecha: 2026-11-16, Europe/Madrid. Base:
`6b5de0b9b72f69fa97580a5fcc0ba35aca2c6018`.

**I183 concreta los contratos de PGO181-SPLIT-ROOT-01 mediante 17 familias de
schemas cerrados y un perfil de confianza candidato Ed25519/JCS.** Define la
forma exacta, las relaciones que deben verificarse y el origen externo de la
confianza. No adopta el protocolo, implementa un guard o establece confianza
real. F179-01 sigue abierto; I122/PJC115-R2 permanece sin admisión y D5 abierto.

## Ruta de revisión

1. Leer el [perfil y sus 14 reglas C01–C14](../validation/D5-I183-PGO181-TRUST-PROFILE-CANDIDATE.json).
2. Contrastar el [paquete JSON Schema](../validation/D5-I183-PGO181-SCHEMAS-CANDIDATE.json):
   `oneOf` distingue las familias; `$defs` contiene las definiciones completas.
3. Revisar la [preparación y sus límites](../validation/D5-I183-preparation-review.json),
   el [auditor](../validation/D5-I183-audit.py) y el
   [sello documental](../validation/D5-I183-integrity.json).

Estos archivos I183 son definiciones candidatas para revisar. No son cuerpos
PRP181 de ejecución ni están instalados en los parsers actuales. Los diez slots
futuros y las seis fuentes sucesoras de I181 siguen sin existir. Los schemas
activos, el candidato I175 y sus cuatro bindings pendientes permanecen intactos.

## Contratos cerrados y orden de evidencia

El paquete usa JSON Schema 2020-12, referencias exclusivamente locales, todas
las claves obligatorias y rechazo de claves adicionales. Los mapas grandes
admiten exactamente sus nombres y cardinalidades; las reglas semánticas
comprueban además los hashes y relaciones entre cuerpos reales. Los schemas
no prueban la verdad de una derivación, identidad, ejecución o aceptación.

| Familias | Forma y frontera de afirmación |
| --- | --- |
| registry, capacity_contract | 480 inputs históricos exactos, seis fuentes, límites numéricos preservados y scope/runtime vinculados |
| resource_index | Siete derivaciones antecedentes E01–E05/CP03/atomicidad, revisores y cotas completas; sin descendientes finales |
| source_basis | Sólo base antecedente aceptada; 489 bindings; sin antiguo CP07, E06 final o permiso |
| component_manifest | Nueve fuentes, runtime, suite final congelada y digest de solicitud separada de componentes |
| component_raw/review/seal | Run real final, review con custodio y revisor distintos, y hashes exactos; sin autopin |
| authority_payload | 494 pins reales; fase BINDING_PAYLOAD_ONLY_NO_RUNTIME_PERMISSION; excluye payload y raíz |
| final_root | signed_core exacto y dos firmas; todos los antecedentes, scope, validez, contexto y solicitud fijados |
| trust_context | Ocho roles, dos claves públicas autorizadas, aprobaciones antecedentes y contexto externo auténtico |
| runtime_request/component_request | Permisos separados, con scope, validez y compromisos exactos; componentes preceden a la raíz |
| worker_invocation/worker_ready/parent_release/capture_binding | Identidad común de raíz, invocación, contexto y solicitud; el binding de captura sólo es consumidor posterior |

Las nuevas estructuras son incompatibles con el parser I122. Ningún archivo
puede declarar el antiguo CP07 como atajo. CP07 completo se computaría en la
decisión final, tras comprobar las nueve condiciones conservadas de I181.
Las propiedades BASIS/índice siguen excluyendo raw/review/seal, payload y raíz
futuros de sus antecedentes. El manifest no pinnea sus consumidores posteriores.

Cada revisión debe distinguir schema, regla semántica y evidencia. Por ejemplo,
`accepted=true` tiene una forma exacta, pero sólo se aceptaría con una revisión
real competente del argumento completo y del scope fuente/runtime. Las siete
derivaciones deben ser autocontenidas dentro del índice y sus referencias
históricas pertenecer a los 480 inputs. Si la evidencia completa no cabe, se
rechaza o revisa el grafo; no se trunca ni se añaden lecturas ocultas.

## Codificación, hashes y firmas

Se propone JCS con strings ASCII imprimibles e integers no negativos seguros
hasta 9.007.199.254.740.991. Un cuerpo debe ser exactamente sus bytes UTF-8
canónicos: sin BOM, LF final, espacios adicionales, duplicados, floats, null,
controles o extensiones. La restricción es deliberada; no es un codec JCS general.
Los hashes son SHA-256 de bytes físicos exactos. Los compromisos de mapas son
SHA-256 de su JCS, con orden determinista.

El core firmado fija todos los hashes anteriores, scope, runtime, roles y
claves, validez, perfil/paquete, contexto externo, solicitud e invocation_id.
Excluye firmas, hash del propio archivo y resultado futuro. Cada rol firma el
mismo core bajo un dominio distinto terminado en un único octeto 0x00:
`D5/PGO181/v3/ISSUER` o `D5/PGO181/v3/ACCEPTOR`. No se firma un escape textual.
Ningún predecesor pinnea la raíz.

El perfil selecciona Ed25519 puro, claves de 32 octetos y firmas de 64 octetos,
ambas en hex minúsculo. Propone decodificación canónica, rechazo de identidades
y puntos fuera del subgrupo primo, S en rango y ecuación sin cofactor. Estas
restricciones adicionales y los dominios son decisiones candidatas locales;
requieren revisión y una biblioteca que demuestre su conformidad. No se aporta
implementación, selección de dependencia o verificación criptográfica ejecutada.

Referencias primarias: [JSON Schema Core](https://json-schema.org/draft/2020-12/json-schema-core)
y [Validation](https://json-schema.org/draft/2020-12/json-schema-validation)
para estructura; [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) para JCS;
[RFC 8032, §§5.1.7 y 8.8](https://www.rfc-editor.org/rfc/rfc8032) para Ed25519
y la distinción de cofactor. Las reglas de custodia y admisión son propuestas
de I183, no garantías aportadas por esos documentos.

## La confianza llega del caller aceptado

El caller debe proporcionar un contexto inmutable desde custodia de runtime y
plataforma aceptada, antes de leer la raíz. El contexto fija repositorio, ruta,
fuentes/runtime, perfil, roles, dos claves y las aprobaciones exactas de BASIS
e índice. El archivo raíz no elige sus propias claves o algoritmos confiables.
El perfil y paquete se usarían con digests compilados en las seis fuentes
sucesoras revisadas, sin descargar schemas o claves.

R04 custodio y R05 revisor de componentes deben ser distintos; también R07
emisor y R08 aceptante separado. R08 debe diferir del autor de fuentes y del
custodio; las dos claves públicas deben diferir. Las firmas de ambos roles
fijan el mismo core, pero no sustituyen revisión de verdad, procedencia,
independencia y recursos. Ninguna persona, organización o clave queda nombrada
por I183. El mismo asistente preparó I181 y este contrato; no hay independencia
de actor, aceptación competente o custodia acreditada.

La vigencia candidata máxima es 3.600 segundos y el error de reloj máximo es
5 segundos. Cada frontera exige validez conservadora usando now±error; la raíz
debe quedar dentro del contexto y solicitud runtime. El caller rechaza epochs
superados, claves revocadas o freshness no acreditada. El estado offline tiene
la vigencia del contexto y no acredita revocación instantánea.

La solicitud runtime debe ser auténtica, de un solo uso y ligada a una
invocación única no nula. La procedencia de esa unicidad, el reinicio y el
estado acotado de consumo requieren prueba. Las solicitudes de componentes
son separadas y su autorización/procedencia debe quedar realmente aceptada
antes de emitir la raíz; su digest no demuestra esa autorización por sí solo.
El manifest sucede a esa solicitud y el componente final sucede al manifest.

## Fronteras runtime y costes aún pendientes

El caller entrega contexto y solicitudes como memoria acotada: contexto hasta
8.192 bytes y cada solicitud hasta 2.048. No son nuevos archivos gratuitos.
Toda copia, parsing, reloj, estado, firma, hash, GC/nativo y verificación entra
en E01–E05 y las ventanas reales de launch/worker/finish. Una dependencia de
archivo, red, helper o key adicional obliga a revisar el grafo y presupuesto.

Se conserva el mismo Input Reader para BEFORE, AFTER y finish, cobrando raíz,
payload y 494 miembros: 496 rutas. Los diez techos de cuerpos suman 253.184
bytes; las seis fuentes tienen techo de diseño 262.144. Los límites actuales
no cambian. 266.693.693 bytes sigue siendo aritmética condicionada: el techo
fresco 4.852.460 y toda la evidencia nueva necesitan demostración propia.
No se acredita fit Reader, heap, CPU o el objetivo de 900 segundos.

Los mensajes tienen cuerpo canónico más un LF de transporte y un máximo de
512 bytes incluida esa terminación; sólo el cuerpo entra en sus hashes.
INVOKE/READY/RELEASE y el binding posterior deben coincidir exactamente y
provenir del peer legítimo. El worker comprueba raíz/contexto/solicitud antes
de READY/import funcional; el padre valida READY antes de RELEASE y el worker
valida RELEASE antes de actuar. La admisión del padre precede a reservar paths.
Estas son reglas de control de flujo por implementar y demostrar.

`capture_binding` define el fragmento exacto que debe incluir la futura
evidencia. Los schemas completos de contexto/launch que lo contendrán, sus
excepciones y límites son trabajo posterior de implementación/requalification.
No se añade el fragmento a outputs legacy ni se considera completo su contrato
por fijar sólo el fragmento. La suite final debe cubrir los diez casos
originales y las obligaciones nuevas; un conteo aislado no acredita cobertura.

## Verificación, límites y siguiente decisión

`python3 docs/validation/D5-I183-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
El auditor recompone la revisión anterior mediante herramientas documentales,
contrasta 706 pins con Git y preserva 398 archivos publicados. Comprueba
referencias/discriminadores, claves/cotas, orden antecedente, presupuestos
intactos y casos léxicos/estructurales negativos. Usa un evaluador pequeño del
subconjunto JSON Schema empleado, no acredita conformidad completa del estándar.

Los placeholders de forma existen sólo en memoria. Sus anchuras se registran
para detectar contradicciones elementales con los techos; no son cuerpos
positivos, pruebas de todas las instancias posibles o cotas de evidencia real.
La conformidad futura exige conjuntamente schema, codificación/cap de bytes,
reglas semánticas y evidencia/aceptación verdadera. No se ejecuta el protocolo,
el guard, firmas, componentes, tests del producto o un calendario de lecturas.

Sigue pendiente revisión/adopción competente del contrato, custodia/roles,
implementación autorizada y biblioteca exacta; requalification del scope de
179 casos, 321 raíces/12 grupos y 30 sitios; E01–E05 completos; E06 real final;
solicitudes/contexto auténticos, todos los cuerpos y firmas reales, y decisión
separada de admisión/ejecución. I183 no cierra F179-01 ni acepta S01.

E01–E05 abiertos, E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07 y correlación
false. Cuatro bindings I175 pendientes. Sin SOURCE_CAPACITY_VERIFIED,
rebind, autoridad o destino nuevos, propuesta/captura habilitadas o D5/H07
cerrados; IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e
I1–I20/A52 intactos; brechas globales/reales pendientes. I86/I89/I92
INVALID_CAPTURE no se reanudan ni mezclan.

La unidad son exactamente los seis archivos de work_unit.rollback_files:
este documento, paquete, perfil, preparación, auditor y sello. El diff supera
400 líneas por schemas y evidencia trazable; se informa el exceso. Runtime
harness N/A: sólo preparación documental, sin implementación runtime. Rollback
limitado a esos seis archivos. Auditoría antes de stage y tras commit; commit,
push y comprobación de remoto/árbol limpio autorizados. Publicar no adopta.

Sin ejecutar/importar/compilar producto/componentes ni discovery, benchmarks,
mediciones de plataforma o campañas. Sin cambiar fuentes, schemas/contratos
activos, cuotas, presupuestos, reservas o inputs; sin inspeccionar ni limpiar
dev/run_data/D4. Sin claves, firmas o PASS emitidos; sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6.
