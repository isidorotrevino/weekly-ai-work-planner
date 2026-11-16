# I175 — Grafo candidato fijado; 491 bindings reales y cuatro pendientes

Fecha: 2026-11-16, Europe/Madrid. Base:
`2855bb0d117e38764efddacaa69a8194d341f6e4`.

I175 concreta PRP173-INDEX-01 en un grafo de **495 rutas y 491 bindings SHA
reales**, con registry, certificado y manifest candidatos materializados.
La pertenencia del grafo queda fijada; sus cuatro hashes restantes no pueden
finalizarse sin raw/result/seal reales de componentes y la autoridad posterior.
**No se fabrican esos resultados ni se aplica rebind.** E01–E05 abiertos,
E06 NOT_RUN, I122/PJC115-R2 sin admisión y D5 sin cerrar.

## Artefactos para revisión

1. [Grafo y ledger](../validation/D5-I175-PRP173-CANDIDATE-GRAPH.json): rutas
   lógicas, archivos que aportan los bytes candidatos, SHA, tamaños y dependencias.
2. [Registry candidato](../validation/D5-I175-candidate-bindings/registry.json),
   [certificado candidato](../validation/D5-I175-candidate-bindings/certificate.json)
   y [manifest candidato](../validation/D5-I175-candidate-bindings/components-manifest.json).
3. [Descriptor de bindings de autoridad](../validation/D5-I175-candidate-bindings/authority-binding-draft.json):
   schema documental propio; no es autoridad runtime ni debe copiarse a su ruta.
4. [Preparación](../validation/D5-I175-preparation-review.json),
   [auditor](../validation/D5-I175-audit.py) y [sello](../validation/D5-I175-integrity.json).

Las copias están en un directorio candidato separado. Dentro del grafo se
identifican por su futura ruta lógica original; los bytes proceden de las
copias y no de los documentos vigentes. No se cambian esas rutas runtime,
capture_inputs, fuentes, quotas o gates. Las rutas físicas de preview y del
descriptor tampoco se añaden al manifest de captura implícitamente.

## Bindings concretos

| Documento candidato | Bytes | Binding preparado |
| --- | ---: | --- |
| Registry | 57.659 | 480 prior inputs conservados más el índice real, total 481 |
| Certificado | 55.674 | 489 fuentes, incluidos SHA del registry candidato y del índice; excluye su propio hash |
| Manifest de componentes | 2.266 | Nueve fuentes, incluidos SHA reales del registry y certificado candidatos |
| Descriptor de autoridad | 55.792 | 491 capture_inputs conocidos y tres pendientes; no es cuerpo de autoridad |

El índice I173 conserva sus 9.853 bytes y su SHA publicado, con estado negativo.
No se sustituye por un supuesto índice aprobado ni se alteran su root y
referencias históricas. El contrato de capacidad conserva bytes y valores.
Schemas runtime y source_revision de las tres copias se mantienen; sólo se
concretan los mapas de bindings de la propuesta.

El certificado candidato permanece IMPLEMENTED_NOT_ADMITTED, CP07 false,
atomicidad correlacionada no verificada y componentes NOT_RUN. El manifest
continúa NOT_RUN_SOURCE_ONLY, sin autorización funcional o de componentes.
No se modifica el certificado activo ni se emite SOURCE_CAPACITY_VERIFIED.

## Pertenencia y cierre de hashes

| Conjunto | Cuenta |
| --- | ---: |
| required_prior_inputs candidatos | 481 |
| Fuentes de implementación | 6 |
| source_bindings del certificado | 489 |
| source_bindings de componentes | 9 |
| capture_inputs, sin autoridad | 494 |
| Unión física con autoridad | 495 |
| Rutas con bytes y SHA reales | 491 |
| Rutas pendientes de bytes/SHA | 4 |

Las pendientes son D5-JOINT-tests-raw.json, D5-JOINT-results.json,
D5-JOINT-integrity.json y D5-JOINT-capture-authorization.json. Ninguna existe
ahora. El descriptor usa un schema distinto de d5.joint-capture-authority.v2,
fase NOT_AUTHORIZED y capture_authority false. Expone los tres componentes
pendientes y la autoridad posterior sin valores hash de relleno.

Los campos raw_sha256/result_sha256/seal_sha256 del manifest permanecen null
intencionadamente: no pinnean consumidores posteriores que lo referencian.
Es una regla anticiclo diferente de las cuatro rutas físicas aún sin hash.
Los hashes tardíos corresponderían al resultado, sello y autoridad posteriores.

El grafo lista un orden topológico: miembros fijos y contrato; índice; registry;
certificado; manifest; raw autorizado; resultado; sello; autoridad al final.
El raw tiene una dependencia de protocolo del manifest, aunque su schema no
contenga un campo hash del manifest. Resultado y sello sí fijan sus precedentes.
No hay autopin de certificado o autoridad ni ciclo manifest/resultado/sello.

La prueba de aciclicidad cubre las dependencias de hash del empaquetado actual.
Los documentos históricos congelados se tratan como hojas con identidad de
bytes fija; no se vuelve a demostrar toda su semántica o cierre de recursos.
Las referencias archivadas del índice se resuelven en su commit de respaldo,
sin remapear un hash antiguo a los bytes del registry/certificado candidatos.

## Cotas para este estado candidato

| Cuenta | Bytes |
| --- | ---: |
| Unión conocida de 491 cuerpos reales | 87.114.629 |
| Upper de autoridad/raw/result/seal aún ausentes | 68.864 |
| Upper único condicionado | 87.183.493 |
| Tres pasadas más 4.852.460 frescos heredados | **266.402.939** |
| Límite intacto de lectura por Input Reader | 268.435.456 |
| Margen condicionado | **2.032.517** |

El descriptor documental de autoridad no se cobra como cuerpo de autoridad:
se reserva para ésta su cota PRP173, junto con las tres de componentes. Cada
uno de los dos Input Readers conserva su ledger separado y calendario
BEFORE/AFTER/finish; no hay pooling, resets o eliminación de checks frescos.

Esta cota usa los bytes exactos de las copias negativas actuales. No se
transfiere sin recálculo a una versión positiva con otros hashes/bytes.
El envelope general PRP173 sigue siendo 266.536.487, margen 1.898.969, sólo si
los nueve cuerpos futuros respetan sus máximos y se conserva el mismo grafo
de lectura, targets/bindings, implementación y listings. Las copias cumplen
sus máximos publicados; las cuotas de producto no cambian.

Una autoridad final del schema cerrado tendría los 494 pins reales completos;
su longitud puede acotarse, pero no su SHA sin los tres cuerpos faltantes.
La autoridad no se autopinnea. Metadata/contexto/launcher/paquete y el alcance
de las pruebas aún necesitan revisión sobre sus bytes finales. Ninguna cota
de Reader acredita heap/CPU/servicio o éxito en 900 segundos.

## Bloqueos y paso siguiente

La membresía candidata no es un grafo positivo final aceptado. Faltan pruebas
competentes de E01–E05 y aceptación independiente del protocolo/impacto de
bindings. E06 no se obtiene con un índice, un descriptor o auditoría estática.
Tampoco se simulan componentes PASS para cerrar sus hashes.

Una eventual versión aceptada exigiría evidencia en rutas versionadas,
aprobación independiente sobre el root/fuentes/candidato, índice sucesor y
metadatos regenerados en orden, E06 real por una vía separada y autorizada,
autoridad completa al final y revisión de cotas/ciclos/output bindings. No
se autoriza aquí ejecución, rebind, cambios de cuotas o reparación de fuentes.
Las pruebas y metadatos históricos no se sobrescriben o reclasifican.

## Preservación y publicación

E01–E05 abiertas; E06 NOT_RUN; sin propuesta/captura habilitadas, nueva autoridad
o destino o gate actualizado. D5/H07 de cierre abiertos e IR03 NOT_READY.
P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e I1–I20/A52 intactos;
brechas globales y reales pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan
ni mezclan. No cambia el scope condicional de la negativa P09 sobre su grafo
anterior de 146 miembros añadidos.

`python3 docs/validation/D5-I175-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Verifica 662 pins históricos contra Git, los cuerpos
candidatos, 495 rutas/491 bindings, orden topológico, schemas/flags, tamaños y
cuatro ausencias reales. Preserva 354 archivos publicados e inputs heredados.
Sólo JSON/Git/AST/bytes; no invoca los parsers del producto o componentes.

Unidad de nueve archivos: tres copias, descriptor, grafo, preparación, este
documento, auditor y sello. Rollback limitado a esos nueve archivos enumerados
en work_unit. El diff supera 400 líneas por el ledger completo y auditor
autocontenido; el exceso queda informado. Runtime harness N/A: preparación
documental sin cambio runtime. Auditoría antes del stage y tras commit, push
autorizado y comprobación de remoto/árbol limpio. Publicar no admite ni instala.

Sin ejecutar/importar/compilar producto o componentes, tests, benchmarks,
schedule, introspección o mediciones. Sin cambiar cuotas, reservas, presupuestos,
contratos o inputs vigentes; sin inspeccionar ni limpiar dev/run_data/D4.
Sin proveedores, credenciales, consumo, activación, promoción, despliegue o D6.
