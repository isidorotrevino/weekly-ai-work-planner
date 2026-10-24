# D5 I47 — contrato de revisión de suficiencia tras I42/I44/I46

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base: `585c5e91c2072e656f7296fd2f04af3f1fc7d1c1`.
[Selección A](D5-I47-NEXT-CUT-SCOPE.md) ·
[Matriz propuesta](D5-I47-SUFFICIENCY-DELTA-REVIEW.md) ·
[Sello de diseño](../validation/D5-I47-design-review.json) ·
[Obligaciones UI](D5-I33-INTEGRATED-EVIDENCE-REVIEW.md).

La selección A autoriza preparar contrato/matriz, no ejecutar la revisión semántica.
Se propone I48 como revisión exclusivamente documental de GI33/GI34/GI38/GI39/GI40
incorporando I42/I44/I46 frente al snapshot histórico I40. La comprobación de
integridad de este diseño no emite dictámenes de suficiencia nuevos.

## Continuidad y prohibiciones

P0 mantiene I32, handoff y posteriores sin publicar. D1–D4 cerrados y el hito
D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado se conservan. D5 global, G01–G07 y revisión
global de los cinco GI siguen abiertos. Los siete criterios reales y Docs siguen
pendientes; no promover 30/35→35/35 ni emitir D5-approved/D5-CLOSURE globales.
Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue, D6 o inspección/limpieza de dev/run_data/D4.

Solo documentos/resultados nuevos I48. Producto, tests, helpers, runners, auditor/
registro fijo I38, I40/I42/I44/I46 y sus diseños anteriores quedan intactos.
No implementar correcciones, instrumentación o tests; no ejecutar/importar módulos
de producto/harness, descubrir tests mediante unittest o reejecutar HC/HF/IC/DF/DR/
EA/Python/SQL/Java/Docker. Si se detecta un defecto, registrar hallazgo y propuesta
de corte posterior, sin reproducirlo dinámicamente bajo esta aprobación documental.

Se permiten lectura de archivos públicos y objetos Git locales, parsing JSON/AST,
hashes/diff/ascendencia y validadores documentales ad hoc que no importen módulos
revisados. No ejecutar el auditor I38 como si inventariara automáticamente HC/HF/IC;
leer su código, registro y evidencia ya sellada. Sin fetch, búsqueda de raw perdido
en temporales o fallback silencioso a otro commit.

## Corpus y snapshots

| Grupo | Commit emisor | Lectura propuesta |
|---|---|---|
| Revisión I40 | `900e837edfdd97d0b85f1b8c8b455f5797f24fa0` | 40 UI, 84 subcláusulas, 14 SR, cinco GI y H01–H08 históricos |
| I42 HC | `98df91a05a43313e26c47dc8d80fd3c2f16018d5` | Contrato I41, código/harness, 24 HC, raw propio y regresión/contexto |
| I44 HF | `71d142898ecedb4f1c44fc89ecedaa5d31bb81f5` | Contrato I43, 40 HF, fronteras/estados, raw y regresiones HC/Python |
| I46 IC | `585c5e91c2072e656f7296fd2f04af3f1fc7d1c1` | Contrato I45, 30 IC, autoridad del ticket, raw y regresiones HC/HF/Python |
| T/R/I38 previos | Commits/catálogos fijados en I40 | Código y evidencia histórica solo como base con sus límites originales |

Los snapshots de código de HC/HF/IC se contrastarán contra el archivo/commit
emisor y sus hashes registrados. La fuente actual coincidente puede usarse para
lectura, pero se anotará qué snapshot sostiene cada observación. Si cambió,
registrar integridad histórica y aplicabilidad actual por separado; no rebaselinar.
Los contextos y raws de regresión nuevos no se confunden con la campaña emisora
original, aun cuando repitan los mismos IDs y bytes de código.

I34/I36 raw original sigue NOT_RECORDED. I42 conserva raw de desarrollo fallido/
PASS intermedio cuyos bytes antiguos de fuente no están todos versionados; no
usarlos como evidencia aplicable actual. Su contexto externo de regresión incluyó
tres archivos HC que luego cambiaron: el conjunto amplio no es CURRENT, aunque
los 78 inputs efectivamente ejecutados por esa regresión permanecieran idénticos.
I44/I46 separan los inventarios ejecutados por cada runner; revisar su selección,
no asumir exhaustividad por tener pre/post iguales.

No se leerán labs privados, archivos operativos o stdout preliminares ausentes
del repositorio para rellenar un detalle empírico. La ausencia se conserva como
NOT_RECORDED; no reconstruirla desde tests, contadores o un snapshot posterior.

## Unidad de revisión y transición histórica

Conservar los IDs y texto de las **40 UI, 84 subcláusulas I40 y SR01–SR14**.
No borrar/simplificar una subcláusula difícil ni cambiar sus cuantificadores por
el perímetro de un test nuevo. Si es necesario dividir una faceta, vincularla al
ID original y distinguir inventario original de desglose derivado, sin inflar UI
u obligaciones. R significa fixture relacional, distinto de criterios reales.

La matriz de diseño copia el dictamen I40 solo como baseline histórico y presenta
candidatos HC/HF/IC a nivel UI. Cada candidato proviene de `UI_targets_partial`
de informes sellados; **no demuestra cobertura de ninguna subcláusula**. UI sin
candidato nuevo también se revisa: puede conservar soporte anterior, presentar
cambio transversal de inventario o seguir pendiente. No llamar UNCHANGED a una
fila simplemente porque no tenga etiquetas nuevas.

Para cada subcláusula, registrar:

- Obligación original, GI/modalidad, baseline I40 (dictamen/hallazgo/limitación) y
  nuevo resultado por recorrido/autoridad; mantener ambos snapshots inmutables.
- Declaración MAPPED/UNMAPPED/EXCLUDED, lectura SUPPORTS_BOUNDED/PARTIAL/
  NOT_ESTABLISHED/CONTRADICTED/NOT_REVIEWED y ejecución REGISTERED_PASS/
  REGISTERED_NONPASS/NOT_RECORDED/NOT_RUN como ejes independientes.
- Campaña emisora concreta, caso/test ID, función/factory/binding de parametrización,
  path/commit/símbolo/líneas/hash; localizar el oráculo real, no solo nombre/mapa.
- Frontera/rol/operación/modo/stage/punto/orden/ronda, estado previo y posterior,
  prueba/recibo/versión/HEAD y localizador exacto de observación raw/campo/índice.
- Comparación razonada con I40, parte nueva y residual, contradicción o ausencia,
  y pendiente/propuesta. Integridad/raw binding/aplicabilidad se anotan aparte.

Tipos de delta, que no son dictámenes de suficiencia: NEW_OBLIGATION_SUPPORT,
EXTENDED_ORACLE, REPEATED_CONTROL, CLARIFIED_LIMIT, NO_NEW_SUPPORT y CONTRADICTION.
Asignarlos solo al ejecutar la lectura; una misma subcláusula puede tener varios
con alcance explícito. SUPPORTS_BOUNDED no equivale a cierre GI o corrección
universal. PARTIAL conserva la parte pendiente; NOT_ESTABLISHED no se rellena con
PASS de un método padre. CONTRADICTED exige referencias y no dispara reparación.
Una exclusión local no elimina la obligación global.

Cada cambio de valoración debe justificar todos los componentes de la cláusula.
Una valoración conservada también lleva motivo/referencias. Resumir diferencias
por UI/GI desde las subcláusulas, sin mejora automática por contar PASS o filas.
Las 71 SUPPORTS_BOUNDED/11 PARTIAL/2 NOT_ESTABLISHED son cifras históricas I40,
no resultado actual ni objetivo numérico de la nueva revisión.

## Comprobaciones específicas del delta

**DC01 — Inventario y contexto:** contrastar discovery real del runner, entradas
pre/post y esquema/perfil/fixtures/helpers reutilizados; Python/build/optimize/
__debug__, comandos y omisiones de contexto. Hashes idénticos no acreditan que el
conjunto sea suficiente o que una declaración sea una medición independiente.

**DC02 — Procedencia y autoridad T/R:** T conserva captura I26; R SOURCE/BATCH y
TASK derivada del recibo. No convertir R en EVALUATION Markdown/I32, aceptar
fuente por cursor o trasladar evidencia I28 volátil al recorrido durable.

**DC03 — HC ledger y revocación:** distinguir misma HEAD/CONFLICT_HEAD, nueva
petición con ledger viejo/CONFLICT_LEDGER, y reconcile explícita. REVIEW perdedora
no revoca; EFFECT_CONFIRMED histórico + STALE exige revocación realmente confirmada.

**DC04 — HC EDIT/UPDATE y ABA:** separar versión fijada en Store.transact EDIT de
selección dinámica de versión de Remote.edit; ambas ordenaciones, HEAD frente a
versión de entidad y recibos NO_EFFECT; ABA/foreign seriales no son carreras ABA.

**DC05 — HF fronteras y fsync:** seis operaciones/stages tempranos R × cuatro
puntos, objeto huérfano/HEAD temporal frente a estado alcanzable; dos OSError por
fila no son dos tests o SIGKILL. Commit visible/reopen/fsync no demuestra energía.

**DC06 — HF hueco y UNKNOWN:** after_head APPLY no es hook dentro de BIND; no hay
indicador durable inventado. BIND T incrementa generación por sí mismo. Primera
reconcile R parte UNKNOWN; after_query no observó P, before_result sí; ledger y
queries distintos. Repeticiones DF20/DF21/DR26 no son lagunas inéditas.

**DC07 — IC precedencia e historia:** misma orden/cid frente a negocio repetido;
COMMAND_CONFLICT antes de CAS, CONFLICT_HEAD y petición nueva con HEAD fresca/
BINDING_UNRESOLVED. Recibo histórico UNKNOWN no rebobina EFFECT_CONFIRMED/2 ni
concede ejecución o nuevo envío. Remote.execute no devuelve flag historical.

**DC08 — IC frontera del ticket:** IC17–IC20 usan ticket emitido; IC21–IC24 añaden
uno nunca emitido solo como negativo REMOTE. CLIENT permanece UNKNOWN/1 y no
reconcile/adopta esa prueba. Entidad única no prueba autenticación/dos emisiones
autorizadas; raw/meta se contrastan con código, no solo con booleanos del informe.

**DC09 — Barreras y fuerza del oráculo:** ambos READY, ganador bajo lock, probe,
liberación causal y retornos; el probe no demuestra entrada al flock bloqueante.
Lector independiente/cadena/recibos, observación estable y reapertura pasiva no
se atribuyen como crash nuevo o representación de todos los fallos posibles.

**DC10 — Contabilidad y recursos:** HC/HF/IC propios frente a regresiones repetidas
por campaña, escenarios duplicados por control T/R, SIGKILL positivo frente a
timeout negativo y OSError. Contar IDs distintos/intersecciones, nunca sumar
actores/probes/recibos como tests. Zeros/exitcodes/ownership/limpieza propios no
certifican dev/D4 o host operativo; distinguir guardas, observaciones y declaraciones.

**DC11 — Límites residuales:** H02/H03 restantes, modos/paquetes/targets no cubiertos,
SOURCE/EVALUATION/BATCH/cuenta/perfil/origen/grooming, H07, raw/contexto histórico,
energía/disco/NFS/Windows/caller hostil. No exigir probar toda permutación imaginable;
explicar el cuantificador original y el perímetro acotado pendiente de decisión.

**DC12 — Dictamen y continuidad:** H01–H08 originales conservan su evidencia I40;
clasificar por parte lo ampliado y residual, sin reemplazar un hallazgo entero
por «resuelto» a partir de otra autoridad. Resumen de cinco GI trazable a cada
subcláusula, SR y DC; D5/G01–G07/closure/global_review conservan apertura.

## Entregables, validación y decisión posterior

Se propone I48 con `docs/validation/D5-I48-results.md`, `D5-I48-matrix.md` y
`D5-I48-results.json`; artefacto de integridad documental separado si resulta útil.
Solo documentos nuevos. Resultado estructurado completo: 40 UI/84 subcláusulas,
14 SR/12 DC, dictámenes por cinco GI, transición desde I40, hallazgos y catálogo
resoluble de código/tests/campos raw/inputs. Los doce DC son controles de revisión,
no tests o nuevas cláusulas originales. No un PASS global que oculte parciales.

Validar IDs, estados, cobertura de todos los IDs originales, hashes de código y
raw/commits, referencias/indexadores resolubles y coherencia de agregados. Los
tests dinámicos HF/IC requieren factory y parámetros/binding de generación
identificados por AST/lectura; no importarlos para descubrirlos. Registrar inputs
leídos y comandos/checks documentales, source/record counts y exclusiones.
Cero nuevas ejecuciones de tests; registrar los PASS anteriores como históricos
por campaña. Integridad documental no es resultado de una campaña nueva.

**Decisión A posterior:** aprobar I47 y ejecutar esta revisión documental I48,
mediante lectura/AST/JSON/Git/hashes, sin código nuevo de producto/harness ni
reejecución de campañas o cierres. **B:** aprobar solo diseño. **C:** ajustar
contrato/matriz. P0 y exclusiones permanentes siguen en las tres opciones.
