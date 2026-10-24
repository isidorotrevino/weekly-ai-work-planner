# D5 I40 — revisión conjunta de suficiencia

Fecha: **2026-10-24**, Europe/Madrid. **DOCUMENTARY_REVIEW_COMPLETED_WITH_GAPS**.
[Contrato I39](../design/D5-I39-SUFFICIENCY-REVIEW-DESIGN.md) ·
[Matriz de 40 UI y SR](D5-I40-matrix.md) ·
[Registro, fuentes y dictámenes](D5-I40-results.json) ·
[Auditoría de integridad de lectura](D5-I40-integrity.json).

English: documentary review completed with bounded support and specific gaps.
No tests rerun, runtime fixes, provider actions, publication or global closure.

## Autoridad y resultado

A aprueba I39 `286b3ebe8d8ca10cb7014da4063d87be968253f0` y autoriza ejecutar esta
revisión documental de UI01–UI40/subcláusulas/SR01–SR14. No autoriza modificar código,
repetir pruebas o cerrar criterios. El diseño I39 conserva su estado histórico;
este informe registra la aprobación y revisión posteriores.

Se leyeron implementación, harness, oráculos y métodos DF01–DF48, DR01–DR40 y
EA01–EA36, con dependencias públicas acotadas y referencias históricas pertinentes.
La matriz registra **40 UI, 84 subcláusulas y 14 controles SR**. En lectura:
71 SUPPORTS_BOUNDED, 11 PARTIAL y dos NOT_ESTABLISHED. **Cero tests ejecutados**.
Estas cuentas describen dictámenes documentales, no una campaña de 84 pruebas
ni una proporción de criterios GI cerrados. Cada cláusula conserva pendiente y límite.

No se emite un PASS único. Los tres ejes se distinguen: mapa declarado de UI,
lectura semántica y resultado de ejecución registrado. Que un método padre figure
PASS no acredita una subcláusula ausente de su cuerpo o registros. Las referencias
suplementarias halladas por lectura no modifican los mapas históricos.

| GI | Dictamen acotado | Lo sustentado y lo pendiente |
|---|---|---|
| GI33 | PARTIAL | Inventario e invalidación de inputs/config sustentados; mapa por subcláusula, contexto, pre/post de campaña y raw histórico limitados |
| GI34 | PARTIAL | Grupos/IDs/targets separados y preservación pública sustentados; no inventario exhaustivo de comandos/versiones D1–D4 |
| GI38 | PARTIAL | Autoridades durables y recuperación explícita T/R propias; faltan cortes/variantes concretos y detalle empírico individual |
| GI39 | PARTIAL | CAS/ABA y algunas carreras reales sustentados; varias carreras específicas solo tienen secuencias |
| GI40 | SUPPORTS_BOUNDED | Recursos/limpieza y ausencia de acciones reales dentro de campañas inspeccionadas; sin atestación del host/dev/D4 |

**Los cinco mantienen global_review OPEN y closure false.** D5 global/G01–G07
abiertos, sin promover automáticamente el 30/35 previo a 35/35. D1–D4 cerrados y
A52/D5-LOCAL-SYNTHETIC-I1-I20 aceptado se conservan. Docs y los siete criterios
reales GI06/12/18/24/30/36/42 permanecen pendientes.

## Hallazgos concretos

**H01 — Trazabilidad por cláusula.** El mapa UI03 cita DF01, que verifica inventario;
los apoyos pertinentes son DF32/DF33. UI13 cita DF03, que se complementa con
DF08/09/10/12 para fallos de IMPORT. La matriz distingue ese apoyo suplementario
de una corrección del mapa histórico. No basta que cuarenta filas tengan referencias.

**H02 — Cortes de fallo.** [DF14](../../testing/D5/test_durable_integration.py#L184)
abrió un lector en proceso nuevo tras `ready(projection=False)`; su cuerpo no
mata al proceso entre efecto y binding/proyección. Esa reapertura sí tiene soporte,
la caída abrupta precisa no queda establecida. R DR23/24 parametrizan seis operaciones
CLIENT desde APPLY_BATCH; no CAPTURE/SELECT_SOURCE/PREPARE_SOURCE/PREPARE_BATCH/REVIEW.
En DR26 la segunda caída before_result sucede tras confirmar ya el efecto en la
primera conciliación: no añade por sí misma un caso UNKNOWN en ese segundo corte.
Nada de ello demuestra un fallo de recuperación del runtime; limita la cobertura.

**H03 — Carreras pendientes.** [DF39](../../testing/D5/test_durable_integration.py#L415)
y [DR32](../../testing/D5/test_durable_relational.py#L308) comprueban ledger CAS
secuencialmente. DF36/DR33 editan REMOTE antes de UPDATE; DF35/DR20 intercalan
revocación usando deliver=False. DF37 repite CREATE en secuencia. No acreditan
sus carreras específicas entre procesos. Sí hay barreras/workers para execute
frente a cierre (DF25/DR28) y misma HEAD frente a HEAD (DF38/DR31); matar al dueño
de flock también está controlado. No se transfieren esos PASS a carreras distintas
ni se afirma que el scheduler haya producido ambos ganadores.

**H04 — Evidencia bruta.** Raw I34/I36 = NOT_RECORDED. Sus informes registrados y
snapshots/hashes siguen siendo hechos históricos preservados, con ese límite.
I38 sí tiene raw propio anclado. No se busca o reconstruye raw histórico en /tmp,
ni se sustituye por el de otra campaña.

**H05 — Contexto y parametrización.** Los [runners](../../testing/D5/run_durable_lab.py#L67)
T/R calculan inputs al final; no hay comparación pre/post como la de los siete
inputs propios de I38. Python/plataforma no registran sys.flags/optimización o
el contexto completo de build/mount. Los lectores independientes usan `assert`;
no se afirma que se usara optimización, pero ese dato no está registrado. Los
registros crash con operation=remote no identifican CREATE/UPDATE/CLOSE por fila;
los bucles están en código y sus métodos figuran PASS, sin inventar etiquetas
empíricas para cada observación. No se detectó alteración de los bytes actuales.

**H06 — Límite de preservación.** D3/D4/A52 y referencias públicas D1/D2 se comprueban
en su alcance explícito. No se inventa un manifiesto homogéneo de D1/D2, no se
reabren cierres y no se presenta como exhaustiva la trazabilidad de todos sus
comandos/versiones. A52 distingue el harness D2 independiente de D5 V30; lo no
declarado conserva NOT_RECORDED.

**H07 — Múltiples coincidencias/429 ambiguo.** PC08/PC26 ejercitan esas clases en
I28 volátil. T/R durables prueban ausencia/prueba incompatible, rate limit
concluyente y bloqueo de binding incierto, pero no se encontró la colección
múltiple/AMBIGUOUS_429 como escenario durable explícito. Decidir si la abstracción
aprobada de prueba única/UNKNOWN basta para esa cláusula o preparar negativos
propios; no asumir que la regresión volátil ya lo integró.

**H08 — Límites conservados.** Los presupuestos reducidos se etiquetan correctamente;
no ensayar máximos simultáneos o benchmark no se convierte aquí en defecto o
requisito nuevo. El modelo es de proceso/Linux/filesystem local; no prueba energía,
disco averiado, NFS/Windows o caller hostil. Limpieza propia no equivale a inspección
operativa o atestación de dev/D4, que no se ha hecho.

## Fuerza de evidencia y fronteras

El JSON cita path/commit/símbolo/líneas y SHA de 179 fuentes, incluidos los cuerpos
de los 124 métodos principales y cuatro apoyos legacy seleccionados. Los alias
`test_DFxx`/`test_DRxx` se ligan a `dfxx`/`drxx` por los bucles setattr existentes;
no se fabrican métodos o PASS. No es revisión exhaustiva de los 233 tests anteriores.
Las referencias a métodos y oráculos no son pruebas ejecutadas por I40.

El inventario agrupa las dimensiones de 70 registros de crash I34 y 43 I36 en
85 filas documentales y conserva todos sus índices originales. También enlaza
las observaciones independientes registradas por caso. La tabla de fronteras
separa el protocolo de commit compartido, las operaciones concretas y las
variantes no establecidas; no multiplica un PASS por el número de combinaciones
que el código permite. Fsync incierto y SIGKILL son mecanismos distintos.

T es captura I26 más CLIENT/REMOTE nuevos, con EVALUATION propia; R es captura
JSON/lote/selección/proyección propios, sin EVALUATION Markdown. La igualdad de
payload no iguala generación/revisión ni transfiere autoridad. El lote R local
es atómico; las TASK remotas tienen vector independiente y no rollback distribuido.
No se infiere persistencia integrada de I24/I28/I30/I32 por sus regresiones aisladas.

I34 registra 281 tests e I36 321, con 281 IDs compartidos; I38 registra 36 propios.
No se suman 602, 357 u otra cifra como campaña funcional integrada. Los grupos
SQL/Java siguen históricos y separados. P0 continúa: publicación requiere SHA
concreto y decisión independiente; no se ha publicado o creado PR.

## Verificación documental y siguiente trabajo propuesto

La auditoría fija de lectura se capturó separadamente en I40-integrity.json:
FINDINGS/exit 1 con nueve hallazgos conocidos, once entradas históricas MATCH,
I34 STALE por seis inputs R nuevos e índices cambiados, I36 CURRENT_RECORDED_SCOPE.
Eso no reejecuta DF/DR/EA. Se conservan hashes I39/I38 e inputs y documentos propios
sellados aparte, con enlaces/IDs/estados/referencias comprobados. Solo documentos
I40 nuevos, sin cambios en código, tests, runners, registro o evidencia anterior.

Próximo corte recomendado para decisión: **contrato y matriz de las carreras
pendientes H03**, priorizando respuesta/consulta/revocación y EDIT/UPDATE con
barreras y resultados de ambas ordenaciones. H02 permite otro corte de fallos;
H04/H05 otro de trazabilidad futura. Son propuestas, no autorización para implementar,
repetir campañas o cambiar el auditor. Cualquier corrección exige su alcance concreto.

Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue o D6. No lectura/limpieza de dev/run_data/D4
operativo. Esta revisión se completa con lagunas explícitas y conserva todos los
cierres y límites vigentes.
