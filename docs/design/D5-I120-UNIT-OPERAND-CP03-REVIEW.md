# I120 — CP03 de los 179 casos unitarios

Fecha: 2026-11-11, Europe/Madrid. Base: `50c49678568bae2abeefbe5fec0285f26c628283`.

**CP03 queda resuelto en el alcance de fuentes originales fijadas:** se cierran
los179 roots pendientes, con498 sitios de aserción distintos y934 expresiones
de operandos. Se conservan las pruebas I119 de los restantes142 roots y de las
demás familias de operandos. No se ejecutó producto, candidata ni componentes.

La condición de operandos de PJC115-R2 queda satisfecha documentalmente. La
habilitación integral sigue pendiente de atomicidad correlacionada, componentes
y admisión exacta. D5/H07 y las brechas globales siguen abiertos; IR03 NOT_READY.
No se convierte una prueba de capacidad en autorización de captura.

## Resultado y alcance

| Grupo | Roots cerrados | Cota conservadora D por operando, bytes |
| --- | ---: | ---: |
| test_plane_reconciliation | 41 | 1.583.493 |
| test_profiles_quotas | 38 | 4.250.363 |
| test_relational_batch | 38 | 14.096.422 |
| test_offline_integration | 35 | 1.583.493 |
| test_register_comparison | 16 | 1.799.459 |
| test_register_compat | 11 | 1.799.459 |
| Total | 179 | máximo14.096.422 |

Las cotas de familia incluyen auxiliares comunes deliberadamente excesivos:
listas/tuplas y sets de128 escalares Unicode1024, bytes65536 y los tipos ya
permitidos. Plane no necesita saturar ese auxiliar: su vista pública completa es
mucho menor. No se confunden las cotas con medidas de valores ejecutados.

El máximo conjunto positivo sigue siendo **14.890.036** bytes, por DF44 de I119,
frente a16.777.216: margen **1.887.180**. La profundidad conjunta sigue acotada
por15, inferior a32; los modelos nuevos tienen profundidad máxima7 y los
auxiliares se revisan hasta12. Las dos entradas de assertEqual se digieren con
presupuestos independientes, conforme a Recorder.operand/digest_value; no se
suman dos operandos como si fueran un helper Store con presupuesto compartido.

No se afirma que todo original reciba digest positivo: DI24 conserva exactamente
la rama negativa NOT_RECORDED/OPERAND_BUDGET, hash nulo, de I118/I119. Tampoco se
infiere INVALID_CAPTURE de esa rama. Los argumentos de funciones dentro de
assertRaises/Regex siguen fuera del digest, por la regla original del observador.
No se añade ninguna exención ni se elimina una aserción.

## Prueba por productores y slots

El JSON de prueba incluye definiciones simbólicas reutilizables, sus tamaños,
premisas por familia, hashes de fuentes y fixtures, y catálogo de sitios con
las expresiones originales. Cada root referencia su índice del censo I119,
que está fijado por hash; la auditoría reconstruye todos sus sitios y slots a
partir del AST. Se conservan helpers compartidos, setUp/tearDown y funciones
anidadas de threads. La presencia lexical se usa para cubrir sitios; las formas
de los productores y las cuentas siguientes justifican los valores.

Cada escalar del modelo representa un majorante, no una conversión propuesta.
Se permiten hasta12 bytes JSON ASCII por carácter Unicode y4 en UTF8. Los
contadores originales caben en19 dígitos. Strings de UUID/hash/base64 se acotan
por su anchura y alfabeto; los textos generales incluyen escapes. Contenedores
exactos de JSON, deepcopy y comprehensions son acíclicos. Los únicos tipos
especiales son las autorizaciones originales de PlaneError, EligibilityError y
la clase dict, ya acotadas en I118; no se amplía la allowlist.

### Batch: grafo completo, baselines y procedencia

inspect devuelve el root completo con data/reviews/receipts. No devuelve los
catálogos privados _sources/_manifests. Se modelan128 entidades,128 mappings,
256 relaciones,128 baselines y128 recibos completos; las dos tablas de reviews
se rellenan conservadoramente hasta256 filas cada una. Se conserva claims
anidado en source_base, no se aplana ni se pierde su coste.

El mayor programa ordinario de publicaciones es RB08: cuatro seeds para los
cuatro DEPENDENCIES y un seed adicional. Con los límites originales32 elementos
y64 declaraciones por apply, los totales por lab son E<=160 y R<=320. El caso
especial de grafo grande hace cuatro seeds de32 elementos y cuatro de64
relaciones: E128/R256. El caso de128 recibos usa batches vacíos: E0/R0. Replays
retornan antes de publicar. Las ramas que hacen setUp generan otro lab físico.
La única fixture_add_relation aparece en el caso pequeño con un seed sin
relaciones: sigue dentro de R320, sin combinar programas incompatibles.

Cada declaración puede aportar una copia de relación a los baselines de sus dos
endpoints: **640 copias** para R320, además de256 relaciones actuales. Esta cota
incluye filas históricas que queden en un baseline tras una hipotética colisión
de clave digest; no presupone inyectividad de hashes. Las entidades de cada
baseline también se copian completas. No se usa128*256 ni se descuentan alias.

Los locators de entidades suman E+2R<=800; los de relaciones suman R<=320. Todo
registro persistido de procedencia tiene una lista no vacía, de modo que hay
como máximo **1.120 registros y1.120 strings locator** en total. Cada registro
conserva ambos hashes y ambas versiones de review. Se carga cada copia física
dentro del árbol devuelto, incluidas las historias retenidas tras deepcopy.

Los textos de los estados efectivamente publicados por estos38 roots tienen
hasta64 caracteres, incluidos títulos, descripciones y ediciones locales. El
caso de8192 emojis falla al preparar el manifest y sólo compara datos vacíos o
contadores; su payload no es operando de aserción. RB01 es la única igualdad de
raw completo: su gramática de tres elementos/dos relaciones, más whitespace,
produce una cota inferior a65536, calculada sin ejecutar el productor.

### Profiles/Quotas

Se conserva el árbol completo de inspect_facts:16 accounts,16 profiles,
128 observations, policies/selections del único proyecto P y el único mapping
registrado por PQ04. La segunda escritura de mapping es conflictiva y no lo
multiplica. Cada observation mantiene binding8, adapter identity3 y window5;
cada account mantiene card, selected y revoked completos, hasta128 cada uno.

La policy lleva16 constraints; la evaluación añade como máximo3 diagnósticos
globales y uno por constraint:19. El manifest conserva account/policy y hasta128
observaciones con sus hashes. Los captures y manifests privados no forman parte
de inspect_facts por su expresión de retorno. Los artifacts que sí se comparan
conservan preview y las dos copias pertinentes de base64. El preview markdown
PQ06 tiene una forma separada, con text/source_marker y diagnostic.message.

### Register, Compatibility, Offline y Plane

Las comparaciones completas de previews parten de los fixtures fijados y
variantes positivas finitas: hasta4 filas,4 headings,32 líneas y1024 bytes.
Cada fila conserva sus ocho fields, annotation completa y heading_lines hasta6.
La cota excesiva132 diagnostics por preview y264 por comparación cubre las
ramas del parser. Los reports conservan ambos locators, incluida annotation,
y las nueve posibles changed_fields. La entrada de2001 filas sólo es argumento
de un helper de excepción esperada.

Offline compara previews/proposals completos, entidades after, un remote item,
un provider card, el envelope válido de un elemento y recibos públicos. También
se modela el summary completo: assertNotIn recibe el contenedor entero. Los
campos foreign preservados incluyen state, labels y comments; no se generalizan
los extras arbitrarios de una API de trusted fixtures a estos callers fijos.
NaN/credenciales/envelopes grandes sólo aparecen en llamadas rechazadas. Los
mensajes capturados son códigos cerrados.

Plane compara la vista cerrada de un comando y el recibo completo. El ledger
privado sólo llega a otras aserciones como contadores o listas de tipos; no se
observa todo el catálogo de comandos. Los roots de saturación comparan contadores
y la tupla de límites. El JSON público se acota desde la vista completa más sus
espacios y escapes, no a partir de un digest. Los tipos de error y dict conservan
sus bindings previos.

## Vinculación y capacidad tras añadir la prueba

Los60 archivos no versionados de partida y los477 inputs heredados permanecen
idénticos. También permanecen idénticos los cinco fuentes candidatos y los
cuatro JSON candidatos actuales. El sello I119 conserva sus hashes.

Se preparan **cuatro reemplazos concretos, sin aplicarlos**, dentro de
`docs/validation/D5-I120-candidate-bindings/`: contrato, registro, certificado y
manifiesto. El suplemento vincula sus bytes reales a sus paths lógicos exactos
y a los hashes de sus predecesores. El nuevo contrato apunta a esta prueba y
CP03=true; el certificado conserva DRAFT_NOT_ADMITTED, atomicidad false y CP07
de admisión false. Los diez componentes siguen NOT_RUN. Los números de cuota
propuestos son idénticos; no se aplica ningún valor.

La copia de revisión no se añade como otro input runtime: reemplazaría el JSON
existente en el mismo path lógico. Sólo el documento CP03 agrega un input al
plan. La unión propuesta tiene488 archivos conocidos; la autoridad futura
necesitaría491 capture_inputs más su propio archivo externo:492 archivos leídos.
No se crea esa autoridad ni ninguno de los tres resultados futuros.

| Término del plan propuesto | Bytes |
| --- | ---: |
| Unión conocida U, con los cuatro reemplazos | 87.788.211 |
| Metadatos futuros canónicos F, anchuras de hashes | 56.876 |
| Tres pasadas + rechecks heredados4.852.460 | 268.387.721 |
| Límite InputReader sin cambios | 268.435.456 |
| Margen del plan exacto | **47.735** |

El certificado propuesto usa U<=87.795.000 y F<=57.000: cota268.408.460, margen
26.996. El top metadata model mide482.757 frente a524.288. Se mantiene la regla
de tres pasadas del mismo Reader y las comprobaciones frescas heredadas; no hay
sitios de lectura nuevos. Los hashes futuros sólo se modelan por anchura64:
no son hashes reales ni evidencia PASS. Añadir más archivos o aumentar cuerpos
requiere recalcular este margen estrecho.

## Verificación y estado de D5

`python3 docs/validation/D5-I120-audit.py` sólo lee AST/JSON, calcula tamaños y
hashes, verifica los slots, los reemplazos, sus dependencias y el sello. No
importa ni ejecuta módulos de producto/candidata/componentes. Su PASS es
**DOCUMENTARY_ONLY**, no una prueba funcional ni una verificación automática
completa de todas las premisas semánticas revisadas arriba.

CP03 fuente queda cerrado; no se adopta ninguna de las hipótesis de bosques
NOT_ADMITTED de I119. La candidata PJC115-R2 conserva pendientes la atomicidad
correlacionada de los30 sitios y la evidencia/admisión exacta posterior. No se
simula su cumplimiento. Los snapshots constituyen una actualización revisable,
no una promoción ni una decisión de ejecución.

P0 permanece83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1). D1–D4 e I1–I20/A52 conservan
su aceptación. D5/H07/G01–G07 y GI globales siguen abiertos; GI06/12/18/24/30/36/42
humanos/reales siguen pendientes. I86/I89/I92 siguen INVALID_CAPTURE, sin
reanudación ni combinación. Sin consumo, reservas, activación, promoción,
despliegue ni D6. No se inspecciona ni limpia dev/run_data/D4. Sin producto,
componentes, cambios de cuotas, commit o push.
