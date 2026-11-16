# I188 — Contrato de contexto/launch confirmado documentalmente

Fecha: 2026-11-16, Europe/Madrid. Base:
`aba30b317a820c63b8c4cf7c8664f97f2a874fd5`.

**La revisión no encuentra nuevos defectos documentales bloqueantes en I187.**
Confirma sus siete ramas cerradas, el binding conservado en fallback y la cota
estructural de 10.798.483 bytes por cuerpo. Las dos copias están cobradas y
los metadatos de fallo no se promueven a paquete de captura aceptado. No se
adopta ni implementa el contrato; I122/PJC115-R2 continúa sin admisión,
F179-01 y D5 abiertos.

## Ruta de revisión

1. Leer el [dictamen](../validation/D5-I188-I187-documentary-review.json).
2. Contrastar la [reconstrucción independiente del método de preparación](../validation/D5-I188-I187-source-reconstruction.json).
3. Revisar el [auditor](../validation/D5-I188-audit.py) y el
   [sello documental](../validation/D5-I188-integrity.json).

Se preservan los seis archivos I187 y el perfil/protocolo candidato 02. El
mismo asistente preparó I187 y hace esta reconstrucción metodológicamente
separada; no aporta independencia de actor/organización, custodia o aceptación
competente. No se crean cuerpos de contexto/launch, firmas o evidencia real.

## Schemas, ramas y observaciones

La estructura revisada tiene 55 definiciones locales acíclicas, siete ramas
con record_kind distintos y todos los campos fijos obligatorios/cerrados.
Los maps y arrays son finitos y tipados. context_record y launch_record
referencian el mismo final_record: ambos archivos futuros deben contener un
único cuerpo canónico idéntico, físicamente cobrado dos veces.

| Área | Resultado confirmado y límite |
| --- | --- |
| TRACE | Exige además de wait true un exit0 observado, diagnóstico completado, grupo desaparecido, rechecks y evidencia real completa |
| BLOCKED/INVALID | Estados de fallo con causa/observaciones reales; no autorizan captura ni cierre |
| WORKER_FAILURE | Diagnóstico FAILED auténtico preservado; errores del padre/artefacto permanecen separados |
| TIMEOUT | Representa el retorno false de wait_worker; no convierte ese retorno en una medición o prueba de salida física |
| LAUNCH_ABORTED | No inventa proceso, handshake o resultados ausentes |
| BUDGET_FALLBACK | Retiene binding, owner, flags abiertos, diagnóstico disponible y parent_error; omisiones explícitas |
| Diagnóstico sin par | Schema distinto, retorno sólo en memoria; no sustituye metadatos o autoriza paths antes de admisión |

Todas las ramas persistentes exigen el binding exacto de raíz/invocación/
contexto/solicitud y owner verificado, junto con closure, D5_closed y
publication_authorized false. El fallback no borra el vínculo ni cae en el
antiguo objeto mínimo sin evidencia de procedencia.

La revisión confirma que NOT_RECORDED no se interpreta como ausencia probada,
que los exit codes con signo se conservan mediante sign/magnitude sin null o
enteros JSON negativos, y que el primer diagnóstico del worker no queda
sustituido por errores del padre. La prioridad de ramas es un contrato escrito:
no acredita que un programa lo aplique correctamente ante excepciones reales.

## Cuerpo, par y paquete son niveles distintos

Los schemas definen la forma; las reglas semánticas exigen observaciones,
identidad/custodia, comparaciones y relaciones reales. El codec/cap canónico
es otro requisito. Un cuerpo con forma válida no demuestra esos hechos.

Un par de fallo completo puede conservarse sólo como diagnóstico. No acepta
un paquete incompleto/sobredimensionado o con artefactos no verificados. La
aceptación del paquete para una revisión posterior de suficiencia requiere
TRACE y todos los predicados O06, inventario físico y cotas reales.

PLANNED_PAIR_WITHIN_LIMITS_EXISTING_MEMBERS_VERIFIED no declara que las dos
copias hayan sido escritas: describe los miembros ya observados y el cuerpo
planeado. El consumidor posterior debe exigir ambos archivos completos,
iguales, sobre paths propios y con caps/relaciones válidos. Una copia parcial,
ausente, distinta o cuyo cierre falla invalida el par. No se permite añadir,
sobrescribir o reintentar sobre salida parcial para aparentar publicación.

Antes de admisión/reserva/owner seguros no se crea el par. Si binding/owner no
pueden mantenerse verazmente o faltan recursos para codificar, el contrato
permite que no exista un par válido. No obliga a fabricar metadata. La
verificación del owner y el control de las dos escrituras requieren código
y pruebas futuras; aquí sólo se confirma su obligación explícita.

El inventario omite context/launch y cualquier hash propio o pin tardío hacia
la raíz. Se suman los miembros reales más dos veces el cuerpo canónico. Eso
evita exigir un hash o tamaño propio recursivo dentro del registro.

## Cota reconstruida por otro recorrido

El auditor obtiene las dependencias del schema y las resuelve por oleadas,
en lugar del recorrido recursivo de I187. Usa longitudes exactas de literales,
máximos de cardinalidad y hasta dos bytes por carácter ASCII variable para
cubrir escapes; elige el máximo entre alternativas. Reproduce todas las cotas:

| record_kind | Upper de bytes canónicos |
| --- | ---: |
| TRACE | 4.457.699 |
| BLOCKED | 10.798.475 |
| WORKER_FAILURE | 10.798.372 |
| TIMEOUT | 10.798.440 |
| LAUNCH_ABORTED | 10.795.692 |
| INVALID | **10.798.483** |
| BUDGET_FALLBACK | 2.314 |
| Diagnóstico sin par | 315 |

El upper común es inferior al cap de 12.582.912 para cada copia. Fallback y
diagnóstico sin par caben en su techo propuesto de 8.192. Los caps de
OWNER/raw/sidecar/32 páginas suman 115.347.456 bytes; más ambas copias del
upper común dan **136.944.422**, con margen **3.568.858** al cap 140.513.280.

Esta última suma presupone artefactos reales únicos, páginas contiguas y
cumplimiento de todos los caps; no acepta archivos duplicados, oversized o
no observados. La cota es de serialización para cuerpos dentro de los dominios
declarados. No demuestra transitorios de heap, CPU, IO, lecturas/escrituras,
latencia, metadatos realmente observados o los 900 segundos. No se han medido
ni ejecutado fuentes, componentes, codec runtime o calendario de lecturas.

## Alcance heredado y pendientes

La preparación reproduce las seis anclas AST y la proyección de los 21 campos
legacy sin ejecutar esas funciones. El formato es incompatible y explícito:
los futuros productores/consumidores deben seleccionar el paquete I187 por
digest dentro de las seis fuentes revisadas, no descargar schemas o añadir
lecturas/helpers gratuitos. Las relaciones entre maps, digests, canales,
proceso/owner, fases y observaciones se verifican semánticamente, no por el
JSON Schema aislado.

Se preservan perfil 02, reparación documental de F183-01 y ocho exclusiones
de S01, nueve condiciones de CP07, 496 rutas y aritmética Reader condicionada
266.693.693. No se heredan automáticamente pruebas de compatibilidad/capacidad
para código nuevo. El caller/custodia, biblioteca, bootstrap transport, guard,
control de excepciones y owner/IO exactos siguen pendientes.

También quedan adopción y aceptación competentes, requalification de
179 casos/321 raíces/12 grupos/30 sitios y E01–E05 con todo el trabajo de
snapshot/map/encode/hash/copias/fallos/escrituras dentro de fase; evidencia
antecedente y E06 final reales, requests/contexto/raíces/firmas y decisiones
separadas de admisión/ejecución. El dictamen sobre el contrato no cierra
F179-01 o D5 ni establece confianza o capacidad runtime.

## Verificación y publicación

`python3 docs/validation/D5-I188-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Verifica 734 pins contra Git, preserva 426 archivos publicados, reproduce la
preparación sólo con funciones documentales y recompone por separado schema,
cotas y relaciones. El PASS confirma la integridad/reproducción de esta
revisión, no una implementación, seguridad, independencia o ejecución aceptadas.

La unidad consta de cinco archivos: este documento, dictamen, reconstrucción,
auditor y sello. work_unit.rollback_files enumera el rollback exacto. El diff
supera 400 líneas por evidencia trazable y auditoría; se informa el exceso.
Runtime harness N/A: revisión documental sin cambio runtime. Auditoría antes
de stage y tras commit; commit/push solicitados y comprobación de remoto/árbol
limpio. Publicar no adopta ni concede autoridad.

E01–E05 abiertos, E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07/correlación
false y cuatro bindings I175 pendientes. Sin SOURCE_CAPACITY_VERIFIED, rebind,
autoridad/destino nuevos, propuesta/captura habilitadas o D5/H07 cerrados;
IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e I1–I20/A52
intactos; brechas globales/reales pendientes. I86/I89/I92 INVALID_CAPTURE no
se reanudan ni mezclan.

Sin ejecutar/importar/compilar producto/componentes, tests, discovery,
benchmarks, criptografía o calendarios runtime ni medir plataforma. Sin cambiar
fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o inputs;
sin inspeccionar ni limpiar dev/run_data/D4. Sin cuerpos de captura/firmas/
autoridad/evidencia positiva reales creados; sin proveedores, credenciales,
consumo, activación, promoción, despliegue o D6.
