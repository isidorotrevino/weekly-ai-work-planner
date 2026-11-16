# I174 — PRP173 coherente bajo condiciones; sin admisión ni rebind

Fecha: 2026-11-16, Europe/Madrid. Base:
`7fece6cee8701a4ef6b2407ef7bdc28168d08579`.

La revisión no encuentra defectos documentales bloqueantes en PRP173-INDEX-01.
**Confirma la cota condicional de 266.536.487 bytes por Input Reader**, margen
1.898.969 frente al límite intacto 268.435.456. La propuesta no está aplicada:
faltan evidencia aceptada, índice sucesor, aprobación del protocolo y bindings
finales. E01–E05 siguen abiertos, E06 NOT_RUN y D5 sin cerrar; I122/PJC115-R2
mantienen la no admisión.

## Ruta de revisión y método

Leer el [dictamen](../validation/D5-I174-PRP173-documentary-review.json), con
dieciséis comprobaciones. La
[reconstrucción](../validation/D5-I174-PRP173-source-reconstruction.json) vuelve
a leer 658 entradas de Git y deriva los conjuntos desde el registry, las cotas
por miembro, el calendario y los anchos de metadatos. Incluye el ledger de los
486 miembros fijos y las condiciones de transferencia del coste fresco.

El [auditor](../validation/D5-I174-audit.py) conserva además las comprobaciones
semánticas I173, sustituyendo sus límites de publicación por los de I174.
Nueve anclas AST vinculan los loops de InputPlan/Reader, los checks de schema y
la admisión. No se ejecutan esas funciones ni un calendario real de lecturas.
La serialización de modelos documentales no es ejecución de producto.

El mismo asistente que preparó I173 realiza esta reconstrucción
metodológicamente separada. No es revisión de actor u organización independiente,
aceptación competente de recursos o del protocolo ni autoridad de custodio.
No se reclama que I174 cubra esos roles pendientes.

## Grafo y cota reconstruidos

| Objeto | Resultado de revisión |
| --- | --- |
| Índice real | 9.853 bytes, veinte artefactos/revisiones con SHA reales y root de 652 pins reconstruido |
| Inputs históricos | Se retienen 480 prior inputs y seis fuentes; sólo se añade físicamente el índice |
| Bindings propuestos | 481 prior inputs, 489 fuentes del certificado, nueve de componentes, 494 capture_inputs y 495 rutas con autoridad |
| Miembros fijos | 486 rutas, 86.983.017 bytes publicados |
| Cuerpos variables | Nueve, incluidos documentos de rebind, índice, autoridad y raw/result/seal; suma de máximos 244.992 bytes |
| Bytes únicos | Upper 87.228.009 bajo las condiciones declaradas |
| Lecturas | 3×87.228.009 + 4.852.460 = 266.536.487 por Reader |

La cuenta incluye los cuerpos de registry/certificado/contrato/manifest futuros
en lugar de sus tamaños actuales, y cobra hasta 32.768 bytes para el índice
sucesor, no sólo los 9.853 del candidato negativo. El límite individual mayor
es 9.755.833 frente a file16MiB; unique128MiB y 4096 rutas también se respetan
dentro del grafo propuesto. Coordinador y worker tienen cuentas separadas.

El factor tres se contrasta con los loops BEFORE/AFTER/finish y el mismo Reader.
La propuesta hereda los 4.852.460 bytes frescos del worker, calculados aparte
de las tres pasadas del grafo histórico. Los cobra también al coordinador como
sobreconteo. La transferencia requiere conservar implementación, runner,
targets, bindings, rutas y source_revision. El nuevo check de required_prior_inputs
usa PhaseBytes y añade las tres lecturas físicas de manifest; no sigue los
documentos referenciados por el índice.

No se juntan Readers, resetea el ledger o eliminan checks frescos. La estabilidad
de listings y su cap de 4096 entradas siguen siendo condiciones. Si cambian
esas premisas o el conjunto de rutas, se necesita una cota nueva.

Las cotas de cuerpos variables son condiciones revisables de serialización,
inferiores a las cuotas existentes. No son nuevas cuotas de producto,
enforcement runtime, reservas o pruebas de que una aprobación futura deba caber.
Un cuerpo final que no cumpla su condición no queda amparado por este margen.

## Metadatos y límites del índice

El cálculo separado por pares clave/ancho confirma 55.142 bytes para autoridad,
327 para raw, 417 para resultado y 1.529 para sello, incluido newline opcional.
Los campos se contrastan con los schemas cerrados y cotas de contadores de la
fuente. No se crean hashes inventados, firmas, autoridades o componentes PASS.

Una segunda serialización del modelo de top metadata añade el SHA real del
índice a ambos mapas. Reproduce el delta 276 y total 483.562, margen 40.726
frente al allowance histórico 524.288, manteniendo iguales los demás campos.
No se incrustan los cuerpos del índice o de las pruebas en esos mapas.
El modelo sigue siendo parcial: contexto, launcher, paquete y bytes/pins
finales requieren revisión. Evidence Reader permanece separado, sin financiar
Input Reader con sus cuotas.

La fuente sólo hash-vincula el miembro extra. No interpreta la semántica de
recursos del índice ni verifica firmas o sigue sus referencias. La revisión
completa de backing material fuera del Reader debe declararse y obtener
aceptación independiente, sin llamarla lectura fresca de captura. El root de
hashes y los veinte documentos negativos no prueban recursos.

El índice actual continúa CANDIDATE_NEGATIVE_NOT_ADMITTED, con aprobación
firmada null, E01–E05 sin verificar y E06 pendiente. No puede promoverse por
existir o por caber. Haría falta evidencia aceptada en rutas versionadas e
índice sucesor real, sin sobrescribir o reclasificar inputs y resultados
históricos negativos.

## Ciclos, bindings y bloqueos de admisión

El orden propuesto es viable como diseño: aprobación separada sobre evidencia,
candidato y fuentes anteriores; después índice sucesor; registry/certificado;
manifest/componentes; autoridad al final y sin autopin. La aprobación no debe
referir hashes de documentos posteriores para cerrar un ciclo. La revisión
del grafo final sigue pendiente; no existe aquí una cadena aprobada y sellada.

La igualdad exacta de admisión exige un rebind explícito. Los cambios de hashes
en metadatos requieren revisar su impacto sobre el scope de las pruebas
PFC126/I122. No basta con activar flags del certificado, apuntar a un root o
mantener el mismo source_revision. El código no implementa por sí mismo el
nuevo proceso de confianza; su aceptación externa es una condición material.

Siguen pendientes: E01–E05 con cotas y atestaciones competentes; E06 por su vía
separada y autorizada; aceptación del protocolo de empaquetado/bindings;
sucesor, aprobación y metadatos reales dentro de los máximos; revisión final
de paths, lecturas, listings, outputs y ciclos. No se obtiene con I174
aceptación independiente o autorización para ejecutar, cambiar fuentes/cuotas
o realizar rebind.

El incumplimiento de P09 se conserva: 287.840.292 bytes como cota inferior de
su extensión retenida de 146 miembros. PRP173 cambia el grafo a un miembro
extra; no invalida aquella prueba ni demuestra que todos los otros empaquetados
sean inviables. Su nueva cota tampoco prueba heap, CPU, servicio o 900 segundos.

## Preservación y publicación

I122 sigue IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED, gate
actualizado, propuesta/captura habilitadas o autoridad/destino nuevos.
D5/H07 de cierre abiertos; IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/
1 PARTIAL UI04.1; D1–D4 e I1–I20/A52 intactos; brechas globales y reales
pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I174-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Comprueba bindings, aritmética, schemas, anclas y
serialización condicional; preserva 349 archivos publicados e inputs heredados.
No importa, compila o ejecuta producto/componentes ni mide runtime/plataforma.

Unidad de cinco archivos: este documento, dictamen, reconstrucción, auditor y
[sello](../validation/D5-I174-integrity.json). Rollback limitado a los cinco
archivos enumerados en work_unit. El diff supera 400 líneas por evidencia
trazable y auditor autocontenido; el exceso queda informado. Runtime harness
N/A: revisión documental sin cambio runtime. Auditoría antes del stage y tras
commit, push autorizado y comprobación de remoto/árbol limpio. Publicar no admite.

Sin tests, benchmarks, schedule, introspección o mediciones. No cambian fuentes,
cuotas, reservas, presupuestos, contratos, registry/certificado/manifest,
autoridad o capture_inputs. Sin inspeccionar ni limpiar dev/run_data/D4; sin
proveedores, credenciales, consumo, activación, promoción, despliegue o D6.
