# D5 I40 — matriz de suficiencia revisada

Fecha: **2026-10-24**, Europe/Madrid. **Revisión documental ejecutada; no tests nuevos.**
[Informe](D5-I40-results.md) · [Registro estructurado y catálogo de fuentes](D5-I40-results.json).

Los tres ejes se mantienen separados. MAPPED significa mapa de la UI padre; no
existía mapa histórico por subcláusula. REGISTERED_PASS es el resultado del método
padre en su informe, sin reejecución. Para NOT_ESTABLISHED, ejecución de esa
subcláusula = NOT_RECORDED aun cuando el método padre figure PASS. Los hashes y
commits de cada fuente/campaña están en el JSON. No son ochenta y cuatro tests.

Los recorridos no se intercambian: T sustituye las autoridades volátiles mediante
el contrato durable aprobado; R tiene BATCH/recibo/selección/PROJECTION propios.
R no hereda EVALUATION o captura I26 y T no adquiere lote relacional. I38 solo
apoya inventario/contabilidad/lectura; sus tests no acreditan recuperación T/R.

## UI01 — GI33 / modalidad original M

Inventario liga bytes de código/config/harness/perfil/esquema/entorno/comandos a run_id y resultados, incluyendo diff y archivos nuevos

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI01.1 — Bytes de código/config/harness/perfil/esquema | SUPPORTS_BOUNDED | REGISTERED_PASS | Los runners inventarían módulos/contratos; I38 comprueba blobs y conjunto descubierto; el hash de interfaz de perfil se distingue del de código. Preservar el límite de las reglas fijas, no inventario universal. |
| UI01.2 — Entorno/comando/run_id y resultado por escenario | PARTIAL | REGISTERED_PASS | Hay Python/plataforma y IDs de stores/run en oráculos; los runners registran parámetros de forma desigual. No constan sys.flags/optimización ni todos los modos por observación; I34/I36 sellan inputs al final sin comparación pre/post: H05. |

Fuentes: [A_AUDIT](../../scripts/audit-d5-evidence.py#L498), [A_DISCOVER](../../scripts/audit-d5-evidence.py#L323), [T_RUNNER](../../testing/D5/run_durable_lab.py#L40), [R_RUNNER](../../testing/D5/run_relational_durable_lab.py#L28), [PROFILE_INTERFACE](../../source_ingest/eligibility_fixture.py#L79).
Pruebas leídas: [TEST_DF01](../../testing/D5/test_durable_integration.py#L45), [TEST_DR01](../../testing/D5/test_durable_relational.py#L41), [TEST_EA01](../../testing/evidence_audit/test_evidence_audit.py#L129), [TEST_EA06](../../testing/evidence_audit/test_evidence_audit.py#L162), [TEST_EA10](../../testing/evidence_audit/test_evidence_audit.py#L194), [TEST_EA11](../../testing/evidence_audit/test_evidence_audit.py#L201).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI02 — GI33 / modalidad original M

Cambiar código o config relevante marca evidencia actual STALE_INPUTS; informe histórico conserva sus bytes/hash

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI02.1 — Cambio de bytes/config o incorporación pertinente | SUPPORTS_BOUNDED | REGISTERED_PASS | Cambio/missing/add/remove produce estados distintos; un input nuevo invalida aunque coincidan los anteriores. Aplicable solo a namespaces registrados. |
| UI02.2 — Historia conservada y aplicabilidad separada | SUPPORTS_BOUNDED | REGISTERED_PASS | Los commits se leen sin fallback; I34 MATCH histórico y STALE actual coexisten. No rebaselinar para ocultar seis adiciones R. |

Fuentes: [A_APPLICABLE](../../scripts/audit-d5-evidence.py#L434), [A_DISCOVER](../../scripts/audit-d5-evidence.py#L323), [A_AUDIT](../../scripts/audit-d5-evidence.py#L498).
Pruebas leídas: [TEST_DF01](../../testing/D5/test_durable_integration.py#L45), [TEST_EA02](../../testing/evidence_audit/test_evidence_audit.py#L136), [TEST_EA04](../../testing/evidence_audit/test_evidence_audit.py#L149), [TEST_EA05](../../testing/evidence_audit/test_evidence_audit.py#L156), [TEST_EA06](../../testing/evidence_audit/test_evidence_audit.py#L162), [TEST_EA07](../../testing/evidence_audit/test_evidence_audit.py#L172), [TEST_EA08](../../testing/evidence_audit/test_evidence_audit.py#L180), [TEST_EA09](../../testing/evidence_audit/test_evidence_audit.py#L188).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI03 — GI33 / modalidad original M

Cambio de perfil/política/observación/versiones invalida paquete; etiqueta de versión o fecha reciente no sustituye hash/generación

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI03.1 — Perfil/política/observación y revisiones propias | SUPPORTS_BOUNDED | REGISTERED_PASS | T fija generaciones y digest de cuentas y revalida antes de ISSUE; DF32/33 cambian esos hechos. R no tiene EVALUATION; EXCLUDED en esa subobligación, sin conversión Markdown. |
| UI03.2 — Versión o fecha no reemplaza generación/hash | SUPPORTS_BOUNDED | REGISTERED_PASS | A→B→A y observación nueva no reviven paquetes; decoder_hash declara interfaz y el inventario liga bytes. El mapa original cita DF01; estos son apoyos suplementarios leídos, no mapa histórico corregido. |

Fuentes: [T_PINS](../../source_ingest/durable_task_fixture.py#L97), [T_EVAL](../../source_ingest/durable_task_fixture.py#L104), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [PROFILE_INTERFACE](../../source_ingest/eligibility_fixture.py#L79).
Pruebas leídas: [TEST_DF32](../../testing/D5/test_durable_integration.py#L345), [TEST_DF33](../../testing/D5/test_durable_integration.py#L357), [TEST_EA11](../../testing/evidence_audit/test_evidence_audit.py#L201).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI04 — GI33 / modalidad original M

Relación escenario→frontera→inputs→oráculo→resultado completa; input faltante/incompatible produce NOT_RUN/BLOCKED, sin PASS heredado

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI04.1 — Relación completa escenario/frontera/inputs/oráculo/resultado | PARTIAL | REGISTERED_PASS | Se resuelven IDs, cuerpos, snapshots y algunos índices de observación; UI→test no discrimina todas las cláusulas. Completar trazabilidad de modos/subcasos en evidencia futura, sin reconstruir raw. |
| UI04.2 — Faltante/incompatible no produce PASS heredado | SUPPORTS_BOUNDED | REGISTERED_PASS | Pin inválido bloquea; I38 rechaza mapas vacíos/IDs ausentes y diferencia NOT_RECORDED. La integridad no acredita semántica de un mapa válido. |

Fuentes: [A_DECLARE](../../scripts/audit-d5-evidence.py#L349), [A_AUDIT](../../scripts/audit-d5-evidence.py#L498), [T_ORACLE](../../testing/D5/durable_support.py#L65), [R_ORACLE](../../testing/D5/relational_support.py#L64).
Pruebas leídas: [TEST_DF04](../../testing/D5/test_durable_integration.py#L73), [TEST_DF46](../../testing/D5/test_durable_integration.py#L531), [TEST_DR36](../../testing/D5/test_durable_relational.py#L363), [TEST_EA15](../../testing/evidence_audit/test_evidence_audit.py#L229), [TEST_EA17](../../testing/evidence_audit/test_evidence_audit.py#L244).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI05 — GI33 / modalidad original M

Bytes/evento/commit I26 exactos alcanzables; cursor no acepta fuente; OBSERVED_EXPORT no se eleva y queda fuera del T Markdown inicial

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI05.1 — Bytes/evento/commit I26 alcanzables | SUPPORTS_BOUNDED | REGISTERED_PASS | _pin exige run/scope/commit/event/hash, IMPORT verifica bytes y el test conserva pin original. R usa captura JSON propia; no I26 ficticio. |
| UI05.2 — Cursor no acepta y OBSERVED_EXPORT no se eleva | SUPPORTS_BOUNDED | REGISTERED_PASS | Captura no tiene reviews/tasks; IMPORT exige Markdown y SYNTHETIC_OBSERVATION. DI08 muestra grado observado conservado. Docs durable unido queda fuera, aunque su captura I26 tenga regresión. |

Fuentes: [T_PIN](../../source_ingest/durable_task_fixture.py#L511), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [I26_ADVANCE](../../source_ingest/incremental_fixture.py#L455), [I26_INSPECT](../../source_ingest/incremental_fixture.py#L502).
Pruebas leídas: [TEST_DF03](../../testing/D5/test_durable_integration.py#L64), [TEST_DF04](../../testing/D5/test_durable_integration.py#L73), [TEST_DF05](../../testing/D5/test_durable_integration.py#L83).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI06 — GI33 / modalidad original M

Inventario distingue API de fixture, código real y versión declarada; ninguna capacidad Plane/Gentle-AI/proveedor real se deduce

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI06.1 — API de fixture frente a código y capacidades reales | SUPPORTS_BOUNDED | REGISTERED_PASS | Capacidades y schemas nuevos se declaran sintéticos; settle_or_close y unicidad pertenecen al doble. Ninguna capacidad Plane/Gentle-AI/proveedor real acreditada. |
| UI06.2 — Versión declarada no es atestación | SUPPORTS_BOUNDED | REGISTERED_PASS | Hash de interfaz y metadatos externos NOT_RECORDED están separados del SHA de los archivos. Mantener siete criterios reales pendientes. |

Fuentes: [T_REMOTE](../../source_ingest/durable_task_fixture.py#L426), [R_REMOTE](../../source_ingest/durable_relational_fixture.py#L398), [PROFILE_INTERFACE](../../source_ingest/eligibility_fixture.py#L79), [A_AUDIT](../../scripts/audit-d5-evidence.py#L498).
Pruebas leídas: [TEST_DF46](../../testing/D5/test_durable_integration.py#L531), [TEST_DR22](../../testing/D5/test_durable_relational.py#L206), [TEST_EA11](../../testing/evidence_audit/test_evidence_audit.py#L201).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI07 — GI33 / modalidad original M

Cambio solo de índice se explica por separado; se verifica evidencia sellada en commit y aplicabilidad ejecutable actual sin reescribirla

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI07.1 — Cambio de índice explicado aparte | SUPPORTS_BOUNDED | REGISTERED_PASS | Dos índices I34 y uno A52 difieren; los bytes emisores se comprueban en sus commits. No reabrir A52 por un índice posterior. |
| UI07.2 — Historia íntegra y aplicabilidad ejecutable | SUPPORTS_BOUNDED | REGISTERED_PASS | I36 coincide con alcance registrado; I34 STALE por discovery no por alteración de sus módulos. CURRENT_RECORDED_SCOPE no es ejecución reciente ni suficiencia. |

Fuentes: [A_AUDIT](../../scripts/audit-d5-evidence.py#L498), [A_APPLICABLE](../../scripts/audit-d5-evidence.py#L434).
Pruebas leídas: [TEST_EA07](../../testing/evidence_audit/test_evidence_audit.py#L172), [TEST_EA19](../../testing/evidence_audit/test_evidence_audit.py#L265), [TEST_EA22](../../testing/evidence_audit/test_evidence_audit.py#L295).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI08 — GI34 / modalidad original M

Cierres D1–D4, aceptación A52 y código/SQL/harness históricos preservados; diferencias documentales permitidas identificadas

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI08.1 — Cierres/A52 y entradas públicas preservados | SUPPORTS_BOUNDED | REGISTERED_PASS | Adapters explicitan hashes ejecutables/canónicos/evidencia y referencias D1/D2 incluidas en A52. Preservación acotada; no auditoría exhaustiva nueva de D1–D4. |
| UI08.2 — Cambios documentales permitidos identificados | SUPPORTS_BOUNDED | REGISTERED_PASS | I38 conserva el registro de diferencias y no modifica cierres ni índices. Dev/run_data/D4 operativo no inspeccionados. |

Fuentes: [A_REFS](../../scripts/audit-d5-evidence.py#L444), [A_AUDIT](../../scripts/audit-d5-evidence.py#L498).
Pruebas leídas: [TEST_DF02](../../testing/D5/test_durable_integration.py#L56), [TEST_DR02](../../testing/D5/test_durable_relational.py#L46), [TEST_EA19](../../testing/evidence_audit/test_evidence_audit.py#L265), [TEST_EA20](../../testing/evidence_audit/test_evidence_audit.py#L275), [TEST_EA21](../../testing/evidence_audit/test_evidence_audit.py#L289).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI09 — GI34 / modalidad original M

Cada grupo conserva target y comando/versiones propios; no etiquetar todas las regresiones como V30

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI09.1 — Grupos y targets separados | SUPPORTS_BOUNDED | REGISTERED_PASS | Los runners separan módulos Python; A52 distingue harness histórico D2 y D5 V30. No etiquetar todo como V30. |
| UI09.2 — Comandos/versiones propios para todos los grupos | PARTIAL | REGISTERED_PASS | Existen comandos documentados de campaña y Python/plataforma; targets ausentes aparecen NOT_RECORDED. No hay comprobación exhaustiva actual de todos los comandos/versiones D1–D4 por grupo; no completar por analogía. |

Fuentes: [T_RUNNER](../../testing/D5/run_durable_lab.py#L40), [R_RUNNER](../../testing/D5/run_relational_durable_lab.py#L28), [A_AUDIT](../../scripts/audit-d5-evidence.py#L498).
Pruebas leídas: [TEST_DF02](../../testing/D5/test_durable_integration.py#L56), [TEST_DR02](../../testing/D5/test_durable_relational.py#L46), [TEST_EA19](../../testing/evidence_audit/test_evidence_audit.py#L265), [TEST_EA21](../../testing/evidence_audit/test_evidence_audit.py#L289).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI10 — GI34 / modalidad original M

Suite acumulativa/IDs repetidos/filas/assertions no inflan tests distintos dentro de campaña; ejecuciones anteriores no se suman como nuevas

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI10.1 — IDs distintos dentro de campaña | SUPPORTS_BOUNDED | REGISTERED_PASS | Set de PASS, partición de grupos y contadores controlan duplicados. UI/DF/DR/EA son referencias, no tests adicionales. |
| UI10.2 — No sumar ejecuciones previas y subcasos | SUPPORTS_BOUNDED | REGISTERED_PASS | I34 281 e I36 321 comparten 281; I38 tiene 36 propios; intersección sin total acumulado. No convertir esa aritmética en recuperación integrada. |

Fuentes: [A_DECLARE](../../scripts/audit-d5-evidence.py#L349), [T_RUNNER](../../testing/D5/run_durable_lab.py#L40), [R_RUNNER](../../testing/D5/run_relational_durable_lab.py#L28).
Pruebas leídas: [TEST_DF48](../../testing/D5/test_durable_integration.py#L583), [TEST_DR40](../../testing/D5/test_durable_relational.py#L447), [TEST_EA12](../../testing/evidence_audit/test_evidence_audit.py#L207), [TEST_EA13](../../testing/evidence_audit/test_evidence_audit.py#L213), [TEST_EA18](../../testing/evidence_audit/test_evidence_audit.py#L255).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI11 — GI34 / modalidad original M

Históricos comprobados por hash, regresiones reejecutadas y escenarios nuevos en grupos separados; NOT_RUN SQL/D2–D4 explícito

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI11.1 — Nuevos, regresiones y verificaciones históricas | SUPPORTS_BOUNDED | REGISTERED_PASS | I34 48+233 e I36 40+281 se mantienen en sus campañas; I38 no reejecuta funcionales. Las cuentas son declaraciones registradas, no reejecuciones I40. |
| UI11.2 — SQL/D2–D4 no ejecutados visibles | SUPPORTS_BOUNDED | REGISTERED_PASS | Informes y auditor lo niegan expresamente y conservan targets históricos. No atribuir hashes a ejecución SQL nueva. |

Fuentes: [T_RUNNER](../../testing/D5/run_durable_lab.py#L40), [R_RUNNER](../../testing/D5/run_relational_durable_lab.py#L28), [A_AUDIT](../../scripts/audit-d5-evidence.py#L498).
Pruebas leídas: [TEST_DF02](../../testing/D5/test_durable_integration.py#L56), [TEST_DF48](../../testing/D5/test_durable_integration.py#L583), [TEST_DR02](../../testing/D5/test_durable_relational.py#L46), [TEST_DR40](../../testing/D5/test_durable_relational.py#L447), [TEST_EA19](../../testing/evidence_audit/test_evidence_audit.py#L265), [TEST_EA21](../../testing/evidence_audit/test_evidence_audit.py#L289).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI12 — GI34 / modalidad original M

Recursos/hijos/hilos de I26/I28/I30/I32 separados de los de unión; recuperación I26 no se atribuye a unión

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI12.1 — Recursos nuevos frente a regresiones | SUPPORTS_BOUNDED | REGISTERED_PASS | Los runners cuentan T, R, captura y threads de regresión separadamente. No sumar raíces o procesos como tests. |
| UI12.2 — Recuperación I26 no es persistencia de objetos volátiles | SUPPORTS_BOUNDED | REGISTERED_PASS | Los nuevos Store/clientes y capture root son autoridades distintas; ningún helper restaura privados I24/I28/I30/I32. Equivalencia solo en casos públicos comparados. |

Fuentes: [T_RUNNER](../../testing/D5/run_durable_lab.py#L40), [R_RUNNER](../../testing/D5/run_relational_durable_lab.py#L28), [T_WORKER](../../testing/D5/durable_support.py#L111), [R_WORKER](../../testing/D5/relational_support.py#L96).
Pruebas leídas: [TEST_DF42](../../testing/D5/test_durable_integration.py#L447), [TEST_DR38](../../testing/D5/test_durable_relational.py#L420), [TEST_EA33](../../testing/evidence_audit/test_evidence_audit.py#L390).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI13 — GI38 / modalidad original M

F0→F1: fallo tras commit I26 y antes/después de importación no acepta fuente ni duplica identidad al repetir; bytes/ámbito/grado exactos

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI13.1 — A confirmado, C reiniciado sin aceptación automática | SUPPORTS_BOUNDED | REGISTERED_PASS | DF03 importa desde pin estable tras proceso nuevo y observa reviews/tasks vacíos. No es Drive real. |
| UI13.2 — Fallos antes/después de importación y repetición | SUPPORTS_BOUNDED | REGISTERED_PASS | IMPORT está en los doce commits de DF08/09/10/12; antes no cambia estado y después devuelve recibo histórico. DF03 solo no cubre esos crashes: apoyo suplementario explícito, H01. |
| UI13.3 — Cursor/captura frente a referencia aceptada | SUPPORTS_BOUNDED | REGISTERED_PASS | El pin y los bytes sobreviven sin SOURCE ACCEPT; la selección/revisión es propia de CLIENT. No inferir aprobación desde cursor. |

Fuentes: [T_PIN](../../source_ingest/durable_task_fixture.py#L511), [T_PERFORM](../../source_ingest/durable_task_fixture.py#L523), [T_PHASES](../../testing/D5/test_durable_integration.py#L137), [K_COMMIT](../../source_ingest/durable_store.py#L312).
Pruebas leídas: [TEST_DF03](../../testing/D5/test_durable_integration.py#L64), [TEST_DF08](../../testing/D5/test_durable_integration.py#L152), [TEST_DF09](../../testing/D5/test_durable_integration.py#L153), [TEST_DF10](../../testing/D5/test_durable_integration.py#L154), [TEST_DF12](../../testing/D5/test_durable_integration.py#L172).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI14 — GI38 / modalidad original M

F1→F2: captura/perfil desconocido, fuente ambigua o discrepancia de hashes bloquea todos los efectos posteriores sin reparar datos

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI14.1 — Perfil/ámbito/pin/hash incompatibles | SUPPORTS_BOUNDED | REGISTERED_PASS | Negativos de alcance, evento, bytes, decoder y JSON bloquean sin efectos de dominio. Muestra de clases negativas, no fuzzing exhaustivo. |
| UI14.2 — Sin reparación o elección silenciosa | SUPPORTS_BOUNDED | REGISTERED_PASS | IMPORT bloquea o genera fuente blocked; R rechaza shape/tipo/duplicados sin aplicar prefijo. Narrativa y Docs no se promueven a TASK válida. |

Fuentes: [T_PIN](../../source_ingest/durable_task_fixture.py#L511), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_SOURCE](../../source_ingest/durable_relational_fixture.py#L62).
Pruebas leídas: [TEST_DF04](../../testing/D5/test_durable_integration.py#L73), [TEST_DF05](../../testing/D5/test_durable_integration.py#L83), [TEST_DR04](../../testing/D5/test_durable_relational.py#L59).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI15 — GI38 / modalidad original M

Revisiones SOURCE/EVALUATION/EFFECT/Plane independientes; falta/revocación/reemplazo de una no se cubre con otra aceptación

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI15.1 — Revisiones independientes y pins exactos | SUPPORTS_BOUNDED | REGISTERED_PASS | T separa SOURCE/EVALUATION/EFFECT/PROJECTION; R SOURCE/BATCH/PROJECTION con selección de recibo. R no inventa EVALUATION o esquema T. |
| UI15.2 — Revocación/reemplazo no transferibles | SUPPORTS_BOUNDED | REGISTERED_PASS | Se rechazan versiones viejas y revisión de una TASK no aprueba otra. La autoridad es de fixture; no permisos reales. |

Fuentes: [T_EVAL](../../source_ingest/durable_task_fixture.py#L104), [T_PROJECTION](../../source_ingest/durable_task_fixture.py#L136), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_PROJECTION](../../source_ingest/durable_relational_fixture.py#L133), [R_REDUCE](../../source_ingest/durable_relational_fixture.py#L157).
Pruebas leídas: [TEST_DF06](../../testing/D5/test_durable_integration.py#L94), [TEST_DF35](../../testing/D5/test_durable_integration.py#L380), [TEST_DR13](../../testing/D5/test_durable_relational.py#L134), [TEST_DR18](../../testing/D5/test_durable_relational.py#L174), [TEST_DR20](../../testing/D5/test_durable_relational.py#L188).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI16 — GI38 / modalidad original M

F2→F3: fallo previo conserva estado local; fallo posterior/respuesta perdida recupera recibo histórico exacto en memoria sin aplicar dos veces

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI16.1 — Efecto y evidencia local juntos o ninguno | SUPPORTS_BOUNDED | REGISTERED_PASS | Una raíz durable confirma tarea/mapping/base/procedencia/recibo, o lote R íntegro; los lectores comprueban grupos. No transacción SQL real. |
| UI16.2 — Respuesta perdida y replay sin duplicado/rewind | SUPPORTS_BOUNDED | REGISTERED_PASS | Command_id/request exactos recuperan histórico; cambios posteriores locales/remotos sobreviven. No exactly-once externo. |

Fuentes: [K_COMMIT](../../source_ingest/durable_store.py#L312), [K_CAS](../../source_ingest/durable_store.py#L360), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_REDUCE](../../source_ingest/durable_relational_fixture.py#L157).
Pruebas leídas: [TEST_DF13](../../testing/D5/test_durable_integration.py#L174), [TEST_DF22](../../testing/D5/test_durable_integration.py#L256), [TEST_DR14](../../testing/D5/test_durable_relational.py#L144), [TEST_DR16](../../testing/D5/test_durable_relational.py#L161).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI17 — GI38 / modalidad original M

F3→F4: fallo entre efecto local y binding conserva efecto local y fase pendiente; no inventa proyección ni recibo final exitoso

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI17.1 — Estado intermedio local sin binding/proyección/envío | SUPPORTS_BOUNDED | REGISTERED_PASS | DF14 prepara sin proyección, abre proceso nuevo y verifica tarea única, REMOTE y sends vacíos. Soporte de reapertura en ese estado. |
| UI17.2 — Caída abrupta precisamente entre F3 y F4 | NOT_ESTABLISHED | NOT_RECORDED | El cuerpo df14 no llama kill_at; reinicia un lector después de ready. Otros failpoints cubren APPLY y ISSUE, no ese corte como SIGKILL. Diseñar caso propio del corte si se mantiene la exigencia literal; no llamar DF14 crash demostrado. |

Fuentes: [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [T_DISPATCH](../../source_ingest/durable_task_fixture.py#L562), [K_COMMIT](../../source_ingest/durable_store.py#L312).
Pruebas leídas: [TEST_DF13](../../testing/D5/test_durable_integration.py#L174), [TEST_DF14](../../testing/D5/test_durable_integration.py#L184), [TEST_DF16](../../testing/D5/test_durable_integration.py#L194).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI18 — GI38 / modalidad original M

F4→F5: guardas fallidas antes de entrega producen NOT_SENT; entrega sin resultado concluyente preserva UNKNOWN, nunca retry ciego

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI18.1 — Guardas antes de ISSUE y ticket durable antes de entrega | SUPPORTS_BOUNDED | REGISTERED_PASS | ISSUE revalida revisión/snapshot y confirma UNKNOWN; dispatch sale de transact antes de execute. NOT_SENT se representa por rechazo antes de crear send, no por recibo exitoso. |
| UI18.2 — Intento posible conserva UNKNOWN y no retry ciego | SUPPORTS_BOUNDED | REGISTERED_PASS | Crash after_issue o deliver=False deja ticket; binding unresolved bloquea aun con otro manifest. No inferir ausencia de lookup vacío. |

Fuentes: [T_DISPATCH](../../source_ingest/durable_task_fixture.py#L562), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_DISPATCH](../../source_ingest/durable_relational_fixture.py#L489), [R_LEDGER](../../source_ingest/durable_relational_fixture.py#L284).
Pruebas leídas: [TEST_DF15](../../testing/D5/test_durable_integration.py#L188), [TEST_DF16](../../testing/D5/test_durable_integration.py#L194), [TEST_DF28](../../testing/D5/test_durable_integration.py#L308), [TEST_DR25](../../testing/D5/test_durable_relational.py#L248), [TEST_DR30](../../testing/D5/test_durable_relational.py#L291).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI19 — GI38 / modalidad original M

F5→F6→F7: efecto simulado con respuesta perdida se concilia por clave/ticket/hash; un destino, cero restauración del payload viejo

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI19.1 — Respuesta perdida y prueba correlacionada | SUPPORTS_BOUNDED | REGISTERED_PASS | Ticket/manifest/payload/identity se revalidan; proceso nuevo concilia y no incrementa destinos. La prueba pertenece al doble. |
| UI19.2 — Un efecto sin restaurar payload viejo | SUPPORTS_BOUNDED | REGISTERED_PASS | Antes/después REMOTE y replay histórico conservan ediciones posteriores; los casos cuentan destinos. R DR26 segunda caída before_result parte de efecto ya confirmado; no prueba por sí sola UNKNOWN en ese segundo corte. |

Fuentes: [T_REMOTE](../../source_ingest/durable_task_fixture.py#L426), [T_RECONCILE](../../source_ingest/durable_task_fixture.py#L578), [R_REMOTE](../../source_ingest/durable_relational_fixture.py#L398), [R_RECONCILE](../../source_ingest/durable_relational_fixture.py#L501), [T_ORACLE](../../testing/D5/durable_support.py#L65), [R_ORACLE](../../testing/D5/relational_support.py#L64).
Pruebas leídas: [TEST_DF17](../../testing/D5/test_durable_integration.py#L222), [TEST_DF18](../../testing/D5/test_durable_integration.py#L223), [TEST_DF19](../../testing/D5/test_durable_integration.py#L225), [TEST_DF20](../../testing/D5/test_durable_integration.py#L239), [TEST_DF21](../../testing/D5/test_durable_integration.py#L248), [TEST_DR26](../../testing/D5/test_durable_relational.py#L252), [TEST_DR27](../../testing/D5/test_durable_relational.py#L258).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI20 — GI38 / modalidad original M

Consulta eventual vacía/múltiple/incompatible y 429 ambiguo no prueban ausencia; conservar UNKNOWN/conflicto aunque cambie el paquete

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI20.1 — Lookup vacío conserva incertidumbre | SUPPORTS_BOUNDED | REGISTERED_PASS | proof None no eleva a NO_EFFECT y los reintentos/nuevos paquetes quedan bloqueados. Sin inferir consistencia eventual real. |
| UI20.2 — Prueba incompatible mantiene conflicto | SUPPORTS_BOUNDED | REGISTERED_PASS | Se alteran siete campos y CONFLICT persiste tras nueva consulta correcta. No revocar por fecha. |
| UI20.3 — Múltiples coincidencias y 429 ambiguo específicos en T/R | PARTIAL | REGISTERED_PASS | I28 tiene PC08/PC26 y T/R tienen guardas de UNKNOWN/shape; sus dobles durables devuelven una prueba por ticket. No hay escenario durable explícito de colección múltiple/AMBIGUOUS_429 en DF26/DR29; la regresión volátil no lo sustituye. |

Fuentes: [T_RECONCILE](../../source_ingest/durable_task_fixture.py#L578), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_RECONCILE](../../source_ingest/durable_relational_fixture.py#L501), [R_LEDGER](../../source_ingest/durable_relational_fixture.py#L284).
Pruebas leídas: [TEST_DF23](../../testing/D5/test_durable_integration.py#L270), [TEST_DF26](../../testing/D5/test_durable_integration.py#L290), [TEST_DF27](../../testing/D5/test_durable_integration.py#L300), [TEST_DF28](../../testing/D5/test_durable_integration.py#L308), [TEST_DR29](../../testing/D5/test_durable_relational.py#L285), [TEST_DR30](../../testing/D5/test_durable_relational.py#L291).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI21 — GI38 / modalidad original M

Mismo command_id/request_hash recupera hecho histórico; request distinto bloquea; replay después de cambios no rebobina cabeza/revisiones

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI21.1 — Mismo comando/hash histórico | SUPPORTS_BOUNDED | REGISTERED_PASS | El kernel retorna recibo previo antes de volver a reducer; cambia request y da COMMAND_CONFLICT. No nuevo permiso de ejecución. |
| UI21.2 — Replay tras cambios no restaura cabezas/datos | SUPPORTS_BOUNDED | REGISTERED_PASS | DF22 conserva payload remoto posterior y DR16 conserva título local editado. Resultado histórico no equivale a estado vigente. |

Fuentes: [K_CAS](../../source_ingest/durable_store.py#L360), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_REDUCE](../../source_ingest/durable_relational_fixture.py#L157).
Pruebas leídas: [TEST_DF22](../../testing/D5/test_durable_integration.py#L256), [TEST_DR16](../../testing/D5/test_durable_relational.py#L161).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI22 — GI38 / modalidad original F

Caída/reinicio de cliente antes/después de cada F1–F7 con doble remoto superviviente; restaurar estado/recibos/conflictos sin duplicar efectos

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI22.1 — Procesos nuevos y fallos antes/después de commits seleccionados | SUPPORTS_BOUNDED | REGISTERED_PASS | T parametriza doce operaciones CLIENT, APPLY separado y CREATE/UPDATE/CLOSE REMOTE; R seis operaciones y tres modos REMOTE. Tabla de fronteras conserva los puntos cubiertos. |
| UI22.2 — Cada frontera sin excepciones y toda parametrización empírica | PARTIAL | REGISTERED_PASS | Los cortes definidos tienen assertions y snapshots, pero R no parametriza CAPTURE/SELECT_SOURCE/PREPARE_SOURCE/PREPARE_BATCH/REVIEW; DF14 no es caída abrupta. Delimitar o ampliar contrato/matriz de fallos antes de afirmar cada frontera; no repetir ahora tests. |

Fuentes: [T_PHASES](../../testing/D5/test_durable_integration.py#L137), [T_REMOTE_PHASES](../../testing/D5/test_durable_integration.py#L200), [T_WORKER](../../testing/D5/durable_support.py#L111), [R_WORKER](../../testing/D5/relational_support.py#L96), [K_COMMIT](../../source_ingest/durable_store.py#L312).
Pruebas leídas: [TEST_DF07](../../testing/D5/test_durable_integration.py#L103), [TEST_DF08](../../testing/D5/test_durable_integration.py#L152), [TEST_DF09](../../testing/D5/test_durable_integration.py#L153), [TEST_DF10](../../testing/D5/test_durable_integration.py#L154), [TEST_DF12](../../testing/D5/test_durable_integration.py#L172), [TEST_DF13](../../testing/D5/test_durable_integration.py#L174), [TEST_DF16](../../testing/D5/test_durable_integration.py#L194), [TEST_DF17](../../testing/D5/test_durable_integration.py#L222), [TEST_DF20](../../testing/D5/test_durable_integration.py#L239), [TEST_DR23](../../testing/D5/test_durable_relational.py#L228), [TEST_DR27](../../testing/D5/test_durable_relational.py#L258).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI23 — GI38 / modalidad original F

Commit local incierto, intento durable previo al envío y respuesta perdida: recuperar raíz íntegra o bloquear; no inferir éxito de ACK local

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI23.1 — Commit incierto bloquea handle hasta reapertura validada/fsync | SUPPORTS_BOUNDED | REGISTERED_PASS | COMMIT_UNKNOWN tras replace, RECOVERY_REQUIRED en mismo handle y recovery_fsync puede seguir fallando. Modelo de proceso/Linux, no energía o disco averiado. |
| UI23.2 — ACK/excepción no deciden efecto o rollback | SUPPORTS_BOUNDED | REGISTERED_PASS | ISSUE pendiente y prueba REMOTE se resuelven explícitamente; head anterior/posterior se inspecciona independientemente. La ausencia de raw limita detalle histórico por modo. |

Fuentes: [K_COMMIT](../../source_ingest/durable_store.py#L312), [K_LOAD](../../source_ingest/durable_store.py#L248), [T_DISPATCH](../../source_ingest/durable_task_fixture.py#L562), [R_DISPATCH](../../source_ingest/durable_relational_fixture.py#L489).
Pruebas leídas: [TEST_DF11](../../testing/D5/test_durable_integration.py#L156), [TEST_DF15](../../testing/D5/test_durable_integration.py#L188), [TEST_DF19](../../testing/D5/test_durable_integration.py#L225), [TEST_DF21](../../testing/D5/test_durable_integration.py#L248), [TEST_DR23](../../testing/D5/test_durable_relational.py#L228), [TEST_DR24](../../testing/D5/test_durable_relational.py#L238), [TEST_DR27](../../testing/D5/test_durable_relational.py#L258).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI24 — GI38 / modalidad original F

Ledger/snapshot faltante/corrupto/incompatible y reloj reiniciado → bloqueo conservador, sin regenerar aceptación ni renovar frescura

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI24.1 — Corrupción/schema incompleto bloquea sin reconstruir | SUPPORTS_BOUNDED | REGISTERED_PASS | Se rechazan HEAD/objeto/marca/duplicados/enlaces; no promoción de huérfanos, padre o génesis nueva. Casos de corrupción seleccionados, no adversario hostil. |
| UI24.2 — Reloj no reinicia frescura | SUPPORTS_BOUNDED | REGISTERED_PASS | Tick persiste y debe avanzar explícitamente; vuelta atrás bloqueada y horizonte revalidado. No prueba de tiempo real comercial. |

Fuentes: [K_LOAD](../../source_ingest/durable_store.py#L248), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_REDUCE](../../source_ingest/durable_relational_fixture.py#L157).
Pruebas leídas: [TEST_DF07](../../testing/D5/test_durable_integration.py#L103), [TEST_DF23](../../testing/D5/test_durable_integration.py#L270), [TEST_DF29](../../testing/D5/test_durable_integration.py#L315), [TEST_DF30](../../testing/D5/test_durable_integration.py#L324), [TEST_DF31](../../testing/D5/test_durable_integration.py#L338), [TEST_DR35](../../testing/D5/test_durable_relational.py#L336).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI25 — GI38 / modalidad original R

Lote relacional completo o sin prefijo; TASK proyectada deriva del recibo/generación exactos; sin proyección de requisitos/épicas/relaciones ni conversión a perfil I32

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI25.1 — Lote íntegro, tipos, campos y relaciones explícitas | SUPPORTS_BOUNDED | REGISTERED_PASS | Plan y estado posterior se confirman juntos con guardas; requisito DRAFT, EPIC sin columna description, TASK BACKLOG. T excluido; no importación SQL real. |
| UI25.2 — Selección TASK desde recibo/generación exactos | SUPPORTS_BOUNDED | REGISTERED_PASS | BATCH_APPLIED y request/participants permiten solo TASK del recibo actual; proyección tiene revisión propia. No selección desde manifiesto sin recibo. |
| UI25.3 — Proyección permitida y resultado remoto parcial | SUPPORTS_BOUNDED | REGISTERED_PASS | Solo name/description; A confirmada/B UNKNOWN mantiene lote local y vector por TASK. No requisito/épica/vínculo proyectados, atomicidad distribuida o EVALUATION Markdown. |

Fuentes: [R_REDUCE](../../source_ingest/durable_relational_fixture.py#L157), [R_SELECTION](../../source_ingest/durable_relational_fixture.py#L125), [R_PROJECTION](../../source_ingest/durable_relational_fixture.py#L133), [R_PLAN](../../source_ingest/relational_planner.py#L79), [K_COMMIT](../../source_ingest/durable_store.py#L312).
Pruebas leídas: [TEST_DR03](../../testing/D5/test_durable_relational.py#L53), [TEST_DR04](../../testing/D5/test_durable_relational.py#L59), [TEST_DR06](../../testing/D5/test_durable_relational.py#L74), [TEST_DR07](../../testing/D5/test_durable_relational.py#L83), [TEST_DR08](../../testing/D5/test_durable_relational.py#L93), [TEST_DR10](../../testing/D5/test_durable_relational.py#L109), [TEST_DR13](../../testing/D5/test_durable_relational.py#L134), [TEST_DR14](../../testing/D5/test_durable_relational.py#L144), [TEST_DR16](../../testing/D5/test_durable_relational.py#L161), [TEST_DR17](../../testing/D5/test_durable_relational.py#L168), [TEST_DR18](../../testing/D5/test_durable_relational.py#L174), [TEST_DR21](../../testing/D5/test_durable_relational.py#L200), [TEST_DR22](../../testing/D5/test_durable_relational.py#L206), [TEST_DR23](../../testing/D5/test_durable_relational.py#L228), [TEST_DR27](../../testing/D5/test_durable_relational.py#L258).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI26 — GI39 / modalidad original M

Origen/selección/revisión cambia antes del efecto: puerta de unión invalida snapshot copiado; ningún efecto bajo paquete viejo

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI26.1 — Origen/selección/revisión antes del efecto invalidan copia | SUPPORTS_BOUNDED | REGISTERED_PASS | Generaciones y revisiones exactas se revalidan en reducer bajo CAS; ABA no revive aprobación. Interleavings explícitos, no todas las carreras de origen concurrente. |
| UI26.2 — Origen cambiante concurrente con efecto en proceso | PARTIAL | REGISTERED_PASS | DF38 fuerza revisión SOURCE frente a APPLY; cambios de fuente/selección de DF32/DR20 son secuenciales. Carrera multiproceso específica de origen/selección no establecida para ambos recorridos. |

Fuentes: [T_PINS](../../source_ingest/durable_task_fixture.py#L97), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_REDUCE](../../source_ingest/durable_relational_fixture.py#L157), [R_PROJECTION](../../source_ingest/durable_relational_fixture.py#L133).
Pruebas leídas: [TEST_DF32](../../testing/D5/test_durable_integration.py#L345), [TEST_DF35](../../testing/D5/test_durable_integration.py#L380), [TEST_DR05](../../testing/D5/test_durable_relational.py#L67), [TEST_DR20](../../testing/D5/test_durable_relational.py#L188).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI27 — GI39 / modalidad original M

Perfil/política/observación cambian o sufren ABA antes de confirmar: nuevas generaciones bloquean sin reutilizar revisión

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI27.1 — Perfil/política/observación/revocación/ABA invalida | SUPPORTS_BOUNDED | REGISTERED_PASS | Digest de cuentas y generaciones exactas bloquean snapshot anterior; no conversión de mapping. Subobligación de evaluación T; R excluida. |
| UI27.2 — Cambios durante confirmación durable | PARTIAL | REGISTERED_PASS | T integra chequeos; PQ26 aporta carrera en modelo volátil y DF38 otra revisión/efecto. No transferir la carrera PQ26 a confirmación durable T; falta escenario específico de esas cuentas/perfiles. |

Fuentes: [T_PINS](../../source_ingest/durable_task_fixture.py#L97), [T_EVAL](../../source_ingest/durable_task_fixture.py#L104), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150).
Pruebas leídas: [TEST_DF32](../../testing/D5/test_durable_integration.py#L345), [TEST_DF33](../../testing/D5/test_durable_integration.py#L357).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI28 — GI39 / modalidad original M

Reloj cruza caducidad/horizonte con generación igual: evaluación bloquea y no concede capacidad/permiso

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI28.1 — Caducidad/horizonte con generación igual | SUPPORTS_BOUNDED | REGISTERED_PASS | Tick95 permite horizonte y tick96 bloquea APPLY; comparación pública con modelo volátil también bloquea expirado. R no evalúa cuota, queda excluido de esta obligación. |
| UI28.2 — Sin capacidad, frescura o permiso operacional | SUPPORTS_BOUNDED | REGISTERED_PASS | Recibos/summary niegan ejecución y contadores no crean reservas; tiempo lógico requiere comando explícito. No medición de ventanas reales. |

Fuentes: [T_ELIGIBLE](../../source_ingest/durable_task_fixture.py#L114), [T_EVAL](../../source_ingest/durable_task_fixture.py#L104), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150).
Pruebas leídas: [TEST_DF31](../../testing/D5/test_durable_integration.py#L338), [TEST_DF33](../../testing/D5/test_durable_integration.py#L357), [TEST_DF46](../../testing/D5/test_durable_integration.py#L531).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI29 — GI39 / modalidad original M

Edición de entidad local tras copiar a I28 y antes de entregar ticket detectada por vínculo con almacén dueño, sin envío obsoleto

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI29.1 — Snapshot del dueño local obsoleto antes de envío | SUPPORTS_BOUNDED | REGISTERED_PASS | Edición foreign en T y requisito/relación/no-op en R incrementan generación y bloquean ISSUE antes del efecto. Estado dueño es el nuevo Store aprobado, no memoria I28 restaurada. |
| UI29.2 — Relación con el contrato original | SUPPORTS_BOUNDED | REGISTERED_PASS | La obligación de no enviar copia vieja se conserva bajo nueva autoridad con pins completos. Equivalencia demostrada solo en escenarios citados, no paridad universal I28. |

Fuentes: [T_PROJECTION](../../source_ingest/durable_task_fixture.py#L136), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_PROJECTION](../../source_ingest/durable_relational_fixture.py#L133), [R_SELECTION](../../source_ingest/durable_relational_fixture.py#L125).
Pruebas leídas: [TEST_DF34](../../testing/D5/test_durable_integration.py#L374), [TEST_DR19](../../testing/D5/test_durable_relational.py#L180).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI30 — GI39 / modalidad original M

Revocación/cambio local durante envío conserva efecto histórico + STALE/UNKNOWN y exige conciliación; no presume rollback remoto

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI30.1 — Revocación antes/después de ISSUE preserva hecho y STALE | SUPPORTS_BOUNDED | REGISTERED_PASS | Antes bloquea; después se ejecuta ticket y se concilia efecto histórico sin rollback. Efecto en vuelo posible aunque revisión ya no vigente. |
| UI30.2 — Revocación o edición intercalada realmente durante llamada remota | PARTIAL | REGISTERED_PASS | Los tests usan deliver=False y pasos secuenciales entre ISSUE/execute/reconcile. No hay proceso suspendido dentro del envío más escritor concurrente para ambas ordenaciones. |

Fuentes: [T_DISPATCH](../../source_ingest/durable_task_fixture.py#L562), [T_RECONCILE](../../source_ingest/durable_task_fixture.py#L578), [R_DISPATCH](../../source_ingest/durable_relational_fixture.py#L489), [R_RECONCILE](../../source_ingest/durable_relational_fixture.py#L501).
Pruebas leídas: [TEST_DF35](../../testing/D5/test_durable_integration.py#L380), [TEST_DR20](../../testing/D5/test_durable_relational.py#L188), [TEST_DR34](../../testing/D5/test_durable_relational.py#L322).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI31 — GI39 / modalidad original M

Edición Plane antes/durante CAS, incluido ABA, bloquea sobrescritura; campos ajenos/sentinels se conservan

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI31.1 — Edición remota previa, ABA y conservación de campos ajenos | SUPPORTS_BOUNDED | REGISTERED_PASS | REMOTE exige base completa/versionada; dos ediciones vuelven payload original pero versión cambia y NO_EFFECT prohíbe retry. Prueba con edit previo a dispatch. |
| UI31.2 — Edición durante UPDATE compitiendo en REMOTE | PARTIAL | REGISTERED_PASS | El lock y la comparación están juntos; tests de EDIT→UPDATE son secuenciales. La carrera EDIT vs UPDATE con barrera y resultados de ambas ordenaciones no está establecida por DF36/DR33. |

Fuentes: [T_REMOTE](../../source_ingest/durable_task_fixture.py#L426), [R_REMOTE](../../source_ingest/durable_relational_fixture.py#L398), [K_CAS](../../source_ingest/durable_store.py#L360).
Pruebas leídas: [TEST_DF36](../../testing/D5/test_durable_integration.py#L388), [TEST_DF37](../../testing/D5/test_durable_integration.py#L399), [TEST_DR22](../../testing/D5/test_durable_relational.py#L206), [TEST_DR33](../../testing/D5/test_durable_relational.py#L314).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI32 — GI39 / modalidad original M

Dos comandos/paquetes y respuesta vs conciliación compiten con barreras: CAS conserva un resultado coherente y todos los conflictos, sin elegir por fecha

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI32.1 — Paquetes/efecto/revisión y execute/cierre con procesos | SUPPORTS_BOUNDED | REGISTERED_PASS | DF38/DR31 usan mismo expected_head y barrera; DF25/DR28 execute y CLOSE compiten desde dos procesos y tienen prueba terminal común. El scheduler elige ganador; no se registran ambas ordenaciones obligatorias. |
| UI32.2 — Respuesta frente a conciliación/revisión con barreras propias | NOT_ESTABLISHED | NOT_RECORDED | DF39 y DR32 consultan y aplican RESULT/revisión en secuencia; CAS de ledger se comprueba, pero no hay workers/barrier en esos métodos. Diseñar carrera multiproceso de RESULT/QUERY/revocación y ambos resultados aceptables sin fecha. |

Fuentes: [K_CAS](../../source_ingest/durable_store.py#L360), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_LEDGER](../../source_ingest/durable_relational_fixture.py#L284), [T_WORKER](../../testing/D5/durable_support.py#L111), [R_WORKER](../../testing/D5/relational_support.py#L96).
Pruebas leídas: [TEST_DF25](../../testing/D5/test_durable_integration.py#L280), [TEST_DF38](../../testing/D5/test_durable_integration.py#L406), [TEST_DF39](../../testing/D5/test_durable_integration.py#L415), [TEST_DR28](../../testing/D5/test_durable_relational.py#L276), [TEST_DR31](../../testing/D5/test_durable_relational.py#L300), [TEST_DR32](../../testing/D5/test_durable_relational.py#L308).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI33 — GI39 / modalidad original F

Dos procesos sobre el estado durable no pierden revisiones/recibos ni duplican intento; CAS/locks y puntos de crash requieren contrato F previo

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI33.1 — Mismo estado durable: CAS y lock recuperado tras muerte | SUPPORTS_BOUNDED | REGISTERED_PASS | Un escritor HEAD confirma y otro falla; matar dueño de flock permite al siguiente validar cabeza y escribir tick2. Procesos spawn y pipe/barrera propios. |
| UI33.2 — Dos tickets CREATE/ISSUE simultáneos sin duplicar intento | PARTIAL | REGISTERED_PASS | Unicidad remota está bajo lock; DF37 repite tickets secuencialmente y DF25 combina execute/cierre. No tratar DF37 como prueba de dos CREATE concurrentes ni de dos ISSUE simultáneos. |

Fuentes: [K_CAS](../../source_ingest/durable_store.py#L360), [K_COMMIT](../../source_ingest/durable_store.py#L312), [T_WORKER](../../testing/D5/durable_support.py#L111), [R_WORKER](../../testing/D5/relational_support.py#L96).
Pruebas leídas: [TEST_DF25](../../testing/D5/test_durable_integration.py#L280), [TEST_DF37](../../testing/D5/test_durable_integration.py#L399), [TEST_DF38](../../testing/D5/test_durable_integration.py#L406), [TEST_DF39](../../testing/D5/test_durable_integration.py#L415), [TEST_DF40](../../testing/D5/test_durable_integration.py#L423), [TEST_DR28](../../testing/D5/test_durable_relational.py#L276), [TEST_DR31](../../testing/D5/test_durable_relational.py#L300), [TEST_DR38](../../testing/D5/test_durable_relational.py#L420).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI34 — GI39 / modalidad original R

Cambio local/relacional invalida lote y snapshot de TASK hacia I28; sin rebase parcial ni revisión I32 ficticia

Dictamen acotado: **PARTIAL**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI34.1 — Cambio de entidad/relación/no-op invalida lote/snapshot entero | SUPPORTS_BOUNDED | REGISTERED_PASS | Generación/hash de todo proyecto y bases completas impiden rebase parcial; endpoints y guardas se contrastan. Flags de trabajo son de fixture, no consultas a operaciones reales. |
| UI34.2 — Ticket previo incierto sobrevive a lote nuevo | SUPPORTS_BOUNDED | REGISTERED_PASS | Nuevo lote puede aplicar pero BINDING_UNRESOLVED bloquea envío; confirmación CREATE vieja invalida paquete CREATE nuevo y exige UPDATE nuevo. No atomicidad distribuida, T excluido y sin revisión I32 ficticia. |
| UI34.3 — Concurrencia de toda variación relacional con entrega | PARTIAL | REGISTERED_PASS | Hay dos BATCH con mismo expected_head y execute/cierre; edición/relación/revocación con envío son secuencias. Faltan carreras específicas de esas variaciones si se exige reproducción concurrente plena. |

Fuentes: [R_PLAN](../../source_ingest/relational_planner.py#L79), [R_GUARD](../../source_ingest/relational_planner.py#L19), [R_PROJECTION](../../source_ingest/durable_relational_fixture.py#L133), [R_LEDGER](../../source_ingest/durable_relational_fixture.py#L284).
Pruebas leídas: [TEST_DR11](../../testing/D5/test_durable_relational.py#L119), [TEST_DR12](../../testing/D5/test_durable_relational.py#L128), [TEST_DR19](../../testing/D5/test_durable_relational.py#L180), [TEST_DR20](../../testing/D5/test_durable_relational.py#L188), [TEST_DR28](../../testing/D5/test_durable_relational.py#L276), [TEST_DR31](../../testing/D5/test_durable_relational.py#L300), [TEST_DR32](../../testing/D5/test_durable_relational.py#L308), [TEST_DR33](../../testing/D5/test_durable_relational.py#L314), [TEST_DR34](../../testing/D5/test_durable_relational.py#L322).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI35 — GI40 / modalidad original M

Auditoría registra cero activación, operaciones/intentos operativos, consumo/reservas y permisos de ejecución; separa intentos Plane de fixture

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI35.1 — Cero ejecución/consumo/reservas dentro del alcance autorizado | SUPPORTS_BOUNDED | REGISTERED_PASS | Summary/recibos lo niegan y se ejercita flujo con socket/Popen prohibidos; no existen comandos de operaciones en reducers. Contadores summary son constantes de contrato, no telemetría externa. |
| UI35.2 — Separación de intentos de fixture | SUPPORTS_BOUNDED | REGISTERED_PASS | Ticket/queries/intentos son ledger sintético; no CLAIM D3 ni activación de workers. No extrapolar cero actividad a otros procesos/instancias. |

Fuentes: [T_SUMMARY](../../source_ingest/durable_task_fixture.py#L590), [R_SUMMARY](../../source_ingest/durable_relational_fixture.py#L511), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_REDUCE](../../source_ingest/durable_relational_fixture.py#L157).
Pruebas leídas: [TEST_DF41](../../testing/D5/test_durable_integration.py#L439), [TEST_DR39](../../testing/D5/test_durable_relational.py#L439), [TEST_EA33](../../testing/evidence_audit/test_evidence_audit.py#L390).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI36 — GI40 / modalidad original M

No HTTP/SDK/CLI real, SQL/Docker nuevos ni lecturas de credenciales/corpus/dev; salidas evitan texto crudo/errores privados

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI36.1 — Ausencia de red/SDK/CLI real en recorridos inspeccionados | SUPPORTS_BOUNDED | REGISTERED_PASS | Happy path bloquea socket/Popen y el auditor solo usa Git local sin protocolos; no imports de runtime durante auditoría. Negativos seleccionados, no prueba exhaustiva de todo entorno. |
| UI36.2 — Salida pública saneada | SUPPORTS_BOUNDED | REGISTERED_PASS | DF47/DR39 niegan texto fuente/home/base64; EA31 valida error sin valores inválidos; recibos y resúmenes públicos están separados de inspect. Cuerpos privados de inspect no se abrieron; workerstr(ex) no es canal para corpus real. |

Fuentes: [T_SUMMARY](../../source_ingest/durable_task_fixture.py#L590), [R_SUMMARY](../../source_ingest/durable_relational_fixture.py#L511), [A_READER](../../scripts/audit-d5-evidence.py#L111), [A_GIT](../../scripts/audit-d5-evidence.py#L200).
Pruebas leídas: [TEST_DF41](../../testing/D5/test_durable_integration.py#L439), [TEST_DF47](../../testing/D5/test_durable_integration.py#L576), [TEST_DR39](../../testing/D5/test_durable_relational.py#L439), [TEST_EA26](../../testing/evidence_audit/test_evidence_audit.py#L319), [TEST_EA27](../../testing/evidence_audit/test_evidence_audit.py#L326), [TEST_EA31](../../testing/evidence_audit/test_evidence_audit.py#L373), [TEST_EA32](../../testing/evidence_audit/test_evidence_audit.py#L380).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI37 — GI40 / modalidad original M

Hilos nuevos terminan; regresiones identifican sus propios recursos; limpieza solo de raíces creadas con sentinels sintéticos hermanos intactos

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI37.1 — Recursos e hilos propios y de regresión terminados | SUPPORTS_BOUNDED | REGISTERED_PASS | Los runners comprueban hijos/hilos y muestran cero restantes; el harness identifica propietarios. Son hechos registrados de campaña, no inventario actual del host. |
| UI37.2 — Limpieza solo de raíz propia y sentinel | SUPPORTS_BOUNDED | REGISTERED_PASS | Ownership/marca/inodo/enlaces y sentinel se validan antes de borrar; marker/symlink inválidos bloquean. No inspección/borrado operativo dev/D4. |

Fuentes: [T_CLEAN](../../source_ingest/durable_task_fixture.py#L638), [R_CLEAN](../../source_ingest/durable_relational_fixture.py#L546), [T_RUNNER](../../testing/D5/run_durable_lab.py#L40), [R_RUNNER](../../testing/D5/run_relational_durable_lab.py#L28).
Pruebas leídas: [TEST_DF42](../../testing/D5/test_durable_integration.py#L447), [TEST_DF43](../../testing/D5/test_durable_integration.py#L451), [TEST_DR38](../../testing/D5/test_durable_relational.py#L420), [TEST_EA33](../../testing/evidence_audit/test_evidence_audit.py#L390).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI38 — GI40 / modalidad original F

Hijos de crash/reinicio terminados y raíces cliente/remoto propias limpiadas tras conservar evidencia saneada; nada de dev/D4 afectado por comandos

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI38.1 — Hijos de caída/reinicio y raíces de CLIENT/REMOTE propios | SUPPORTS_BOUNDED | REGISTERED_PASS | Exitcodes y recuentos registrados; contexto spawn y cleanup selectivo se leen. No sumar 310 raíces T a 141 R como tests. |
| UI38.2 — Dev/D4 intactos dentro del alcance comprobado | SUPPORTS_BOUNDED | REGISTERED_PASS | No se invocan paths operativos; Git y referencias públicas se preservan. Ausencia de intervención autorizada y diffs públicos, no atestación dinámica de dev/D4. |

Fuentes: [T_WORKER](../../testing/D5/durable_support.py#L111), [R_WORKER](../../testing/D5/relational_support.py#L96), [T_KILL](../../testing/D5/durable_support.py#L170), [R_KILL](../../testing/D5/relational_support.py#L134), [T_CLEAN](../../source_ingest/durable_task_fixture.py#L638), [R_CLEAN](../../source_ingest/durable_relational_fixture.py#L546).
Pruebas leídas: [TEST_DF42](../../testing/D5/test_durable_integration.py#L447), [TEST_DF43](../../testing/D5/test_durable_integration.py#L451), [TEST_DR38](../../testing/D5/test_durable_relational.py#L420), [TEST_EA33](../../testing/evidence_audit/test_evidence_audit.py#L390).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI39 — GI40 / modalidad original M

Límites propios y del componente más restrictivo bloquean sin truncar ni efecto parcial; presupuesto reducido no se presenta a tamaño completo

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI39.1 — Límites y headroom bloquean antes de emisión/efecto | SUPPORTS_BOUNDED | REGISTERED_PASS | Pruebas reducen límites y comparan estado anterior; margen lógico de resultados pendientes no es reserva de cuota D3. Algunas ramas llaman reducer puro, no todas recorren filesystem. |
| UI39.2 — No presentar presupuestos reducidos como tamaño completo | SUPPORTS_BOUNDED | REGISTERED_PASS | DF44/DR37/EA29 etiquetan presupuestos reducidos; fuente >2MiB se prueba en frontera. Los reportes niegan benchmark y capacidad simultánea completa. Mantener la exclusión; ejecutar máximos completos sería otro alcance, no requisito añadido por I40. |

Fuentes: [K_COMMIT](../../source_ingest/durable_store.py#L312), [T_REDUCE](../../source_ingest/durable_task_fixture.py#L150), [R_REDUCE](../../source_ingest/durable_relational_fixture.py#L157), [R_PLAN](../../source_ingest/relational_planner.py#L79), [A_READER](../../scripts/audit-d5-evidence.py#L111).
Pruebas leídas: [TEST_DF44](../../testing/D5/test_durable_integration.py#L459), [TEST_DF45](../../testing/D5/test_durable_integration.py#L520), [TEST_DR37](../../testing/D5/test_durable_relational.py#L384), [TEST_EA29](../../testing/evidence_audit/test_evidence_audit.py#L357), [TEST_EA30](../../testing/evidence_audit/test_evidence_audit.py#L363).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## UI40 — GI40 / modalidad original M

Informe final enumera qué corrió/no corrió, recursos, exclusiones y aplicabilidad; 30/35 previo no se convierte en 35/35 ni cierra G01–G07 por sumar PASS

Dictamen acotado: **SUPPORTS_BOUNDED**; criterio global abierto.

| Parte | Lectura | Ejecución registrada | Hecho y límite |
|---|---|---|---|
| UI40.1 — Informe distingue lo ejecutado/no ejecutado y aplicabilidad | SUPPORTS_BOUNDED | REGISTERED_PASS | Reportes y auditor separan contexto, recursos, dobles, exclusiones y grupos; I38 raw anclado no cambia ausencia de raw T/R. No relabelar esas campañas como ejecutadas hoy. |
| UI40.2 — Conservación de pendientes globales y A52 | SUPPORTS_BOUNDED | REGISTERED_PASS | Los resúmenes niegan cierre, manteniendo siete gaps y criterios reales pendientes. No aceptar globalmente ni sumar PASS para 35/35; P0 independiente. |

Fuentes: [T_RUNNER](../../testing/D5/run_durable_lab.py#L40), [R_RUNNER](../../testing/D5/run_relational_durable_lab.py#L28), [A_RUNNER](../../testing/evidence_audit/run_audit_lab.py#L40), [A_AUDIT](../../scripts/audit-d5-evidence.py#L498).
Pruebas leídas: [TEST_DF47](../../testing/D5/test_durable_integration.py#L576), [TEST_DF48](../../testing/D5/test_durable_integration.py#L583), [TEST_DR40](../../testing/D5/test_durable_relational.py#L447), [TEST_EA18](../../testing/evidence_audit/test_evidence_audit.py#L255), [TEST_EA22](../../testing/evidence_audit/test_evidence_audit.py#L295), [TEST_EA36](../../testing/evidence_audit/test_evidence_audit.py#L412).
La lista histórica de candidatos UI queda intacta en el JSON; estos apoyos pueden ser suplementarios.

## SR01–SR14 — controles documentales

| Control | Lectura | Conclusión y límites |
|---|---|---|
| SR01 | SUPPORTS_BOUNDED | Namespaces/contratos y autoridad posterior se distinguen; no se reescriben diseños históricos. |
| SR02 | SUPPORTS_BOUNDED | Snapshot base y hashes de código leídos coinciden con sus commits emisores; I34 STALE actual se conserva. |
| SR03 | PARTIAL | Integridad de informes no reemplaza raw o detalle empírico ausente. |
| SR04 | SUPPORTS_BOUNDED | Las cuarenta UI se desglosan en 84 subcláusulas y mantienen estados/pendientes y exclusiones por recorrido. |
| SR05 | PARTIAL | Referencias resueltas a cuerpos/assertions y lectores de archivos; algunas etiquetas y contexto no se registraron. |
| SR06 | PARTIAL | Tabla de puntos registrados disponible; no amplía seis operaciones R a toda la fase previa ni convierte DF14 en SIGKILL. |
| SR07 | SUPPORTS_BOUNDED | UNKNOWN/CONFLICT no desaparecen por consulta vacía; cierre/no efecto es capacidad del doble y retry mantiene guardas. |
| SR08 | PARTIAL | Barreras reales en algunos casos; ledger/respuesta y cambios remotos están probados en secuencia. |
| SR09 | SUPPORTS_BOUNDED | BATCH local y proyección por TASK separados, vector parcial e incertidumbre previa conservados. |
| SR10 | SUPPORTS_BOUNDED | Elegibilidad/pins lógicos no conceden ejecución, cuota o reserva; R no inventa evaluación T. |
| SR11 | SUPPORTS_BOUNDED | 281/321/36 se conservan por campaña y grupos históricos no se suman; límite de targets desconocidos explícito. |
| SR12 | SUPPORTS_BOUNDED | Propiedad/marker/symlink/sentinel y cuentas finales sustentadas por pruebas y registros; no atestación operativa dev/D4. |
| SR13 | SUPPORTS_BOUNDED | Presupuestos reducidos, contexto de proceso/Linux y privacidad de salidas conservados sin elevarlos a garantías universales. |
| SR14 | SUPPORTS_BOUNDED | Los resúmenes enlazan subcláusulas/hallazgos y mantienen OPEN/closure false; no remediación o publicación implícita. |

Sus fuentes están identificadas en el JSON. No son tests adicionales ni cierres GI.

## Registro de fronteras y puntos de caída

El JSON conserva 85 filas de dimensiones existentes case/role/operation/point y
los índices de todos los registros: 70 entradas crash I34 y 43 I36. Es una
agrupación documental, no una ejecución ni 85 fallos nuevos. Los bucles leídos
explican los doce commits CLIENT T y seis CLIENT R; APPLY T y BATCH R se
contrastan también específicamente. REMOTE parametriza CREATE/UPDATE/CLOSE,
pero los registros operation=remote no etiquetan el modo de cada observación.

| Recorrido / frontera | Código y oráculo leídos | Estado acotado / pendiente |
|---|---|---|
| T captura I26 → IMPORT | DF03, DF08/09/10/12; pin/HEAD/recibo | Bytes/commit y crashes IMPORT sustentados; I26 aislado no sustituye unión |
| T SOURCE/EVALUATION/EFFECT/PROJECTION, ISSUE/QUERY/RESULT | commit_crashes y DF11 | Doce operaciones y cuatro puntos; fsync incierto separado; etiqueta por subcaso parcial |
| T APPLY → binding/proyección | DF13 y DF14 | APPLY antes/después sustentado; DF14 no mata proceso en el hueco |
| T/R ISSUE → REMOTE → RESULT | DF16/20/21; DR25/26 | UNKNOWN y efecto único recuperables; segunda caída DR26 ya parte de confirmado |
| R fuente/captura/revisión → BATCH | DR03/05/13; DR23/24 | Reglas/revisión presentes; no tabla SIGKILL de fases previas a APPLY_BATCH |
| R BATCH/SELECT_TASKS/PROJECTION/ISSUE/QUERY/RESULT | DR14/23/24 | Seis operaciones, cuatro puntos y fsync; atomicidad local propia |
| T/R REMOTE CREATE/UPDATE/CLOSE | DF17–20 y DR27 | Cuatro puntos y fsync incierto; modos en código, no en etiqueta individual de registros |
| T/R execute vs CLOSE y HEAD vs HEAD | DF25/38 y DR28/31 | Dos procesos/barrera; no garantía de haber observado ambos ganadores |
| Respuesta/consulta/revocación y EDIT/UPDATE | DF35/36/39; DR20/32/33 | Secuencias con CAS, carrera específica no establecida |

P0 vigente, D1–D4 cerrados y A52/I1–I20 aceptado sin ampliación. D5 global y G01–G07 abiertos.
