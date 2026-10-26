# D5 I68 — suficiencia de trazabilidad y pendientes

Fecha: **2026-10-26**. [Dictamen](D5-I68-results.md) · [388 filas y referencias](D5-I68-results.json).

| Entrada | Grupos | Tests registrados | Escenarios | Clasificación I67 | Dictamen I68 |
|---|---|---|---|---|---|
| I34 | 11 | 281 | 0 | INCOMPLETE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I36 | 12 | 321 | 0 | INCOMPLETE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-GX | 1 | 90 | 90 | COMPLETE_RECORDED_SCOPE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-Python | 12 | 321 | 0 | INCOMPLETE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-HC | 1 | 24 | 25 | INCOMPLETE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-HF | 1 | 40 | 41 | INCOMPLETE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-IC | 1 | 30 | 31 | INCOMPLETE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-UQ | 1 | 24 | 26 | INCOMPLETE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-RV | 1 | 20 | 20 | INCOMPLETE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-NA | 1 | 36 | 48 | INCOMPLETE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-FN | 1 | 64 | 64 | COMPLETE_RECORDED_SCOPE | Soporte reutilizable acotado; tres obligaciones globales parciales |
| I64-CE | 1 | 43 | 43 | COMPLETE_RECORDED_SCOPE | Soporte reutilizable acotado; tres obligaciones globales parciales |

| Parte | Soporte retenido | Pendiente | Dictamen |
|---|---|---|---|
| UI01.2 | Contexto registrado y run_id donde consta, identidad de expediente separada | Metadata/run_id por escenario ausentes no se regeneran; CP01/CP03/CP04/CP09/CP10/CP11 | PARTIAL |
| UI04.1 | Mapas/punteros/raw/oráculos existentes y etiquetas anidadas | Cadena completa y agregación por granularidad; CP03–CP10/CP12/CP13 | PARTIAL |
| UI09.2 | 21 grupos I64 con comando padre y targets propios;23 legados preservados | Comando/versiones/contexto faltantes y vigencia por grupo; CP01/CP02/CP10/CP11 | PARTIAL |

## Pendientes para contrato futuro, no autorización de ejecución

| ID | Tipo | Exigencia | Evidencia/límite |
|---|---|---|---|
| CP01 | CAPTURE_REQUIRED | Invocación nueva y contexto público de su campaña: argv registrado, intérprete/versión/build/flags/plataforma/kernel, exit y hash de stdout bruto; valores ausentes tipados. | I34/I36 no conservan comando de campaña o raw; nueva captura no los reconstruye. |
| CP02 | CAPTURE_OR_TYPED_SCOPE_REQUIRED | Cada grupo declara target, módulo y versiones/schemas/bytes pertinentes; hereda una referencia explícita al mismo comando padre si comparte invocación. | 21 grupos I64 tienen comando padre;23 grupos legados no. Mock SQL conserva su target; no proveedor real. |
| CP03 | CAPTURE_REQUIRED_OR_NOT_APPLICABLE | Lifecycle test/escenario→resultado registrado y verdadero run_id del dueño cuando existe; audit_run_id se distingue de Store/run_id. | 923 ocurrencias sin scenario_refs no se completan con UUID nuevo del expediente; test sin Store usa N/A motivado. |
| CP04 | CAPTURE_REQUIRED_FOR_SELECTED_NEW_SEQUENCES | Unir escenario, actor/autoridad, comando/cid/request/expected, Store/manifest/send/ticket y fase real cuando aplican. | Mantener variantes reales y no fijar un escenario por método si produce varios; controlar multiplicidades. |
| CP05 | REUSE_REVIEW_OR_NEW_CAPTURE | Clasificar punto/frontera/operación observados con oráculo de la misma secuencia; separar etiqueta lógica, gate físico y expectativa de diseño. | 191 escenarios ya contienen etiquetas point y189 operation en eventos; no justifican exigir su recaptura sólo por falta de campo superior. |
| CP06 | CAPTURE_REQUIRED_WHERE_ABSENT | Ligar input efectivo de campaña, expectativa explícita, observación/oráculo y resultado por escenario; señalar si se hereda inventario del runner. | No asignar oráculos Python321 compartidos por posición ni tomar assert/source como observación histórica. |
| CP07 | TYPED_SCOPE_REQUIRED | Controles y tests sin frontera/Store tienen NOT_APPLICABLE con razón revisable y sus propios oráculos; faltante no se convierte en N/A para pasar. | GX87–GX90 no son nuevas carreras ni tests de dominio. |
| CP08 | SOURCE_BINDING_REVIEW_NOT_AUTOMATIC_RECAPTURE | Métodos generados enlazan ID observado, factory/args/tabla de expansión y hash/ancla como derivación de fuente, sin ejecutar factories para reconstruir historia. | 30 HF y24 IC carecen de definición AST individual; fuentes de factories existen. |
| CP09 | CAPTURE_STATUS_REQUIRED | FAIL/error/skip/NOT_RUN/BLOCKED y faltantes conservan estado explícito; la auditoría no añade PASS funcional ni borra evidencia fallida. | Los48 PASS TT son de auditoría y no cubren la ejecución de pruebas de producto. |
| CP10 | CAPTURE_INPUT_BINDING_REQUIRED | Inputs/config/perfil/schema y reglas específicas de discovery pre/post; coherencia de bytes/contexto del nuevo run y cambios documentales aparte. | No unir namespaces de todos los runners para hacer vigente una campaña vieja; I34/I36 hoy CHANGED. |
| CP11 | HISTORICAL_GAP_IRREVERSIBLE_IN_THIS_REVIEW | Nueva campaña con identidad y fecha propias y raw independiente; vínculos a historia preservada, sin reescribir I34/I36/I64 ni atribuir contexto nuevo al pasado. | El kernel ausente de Python321 I64 no se deduce del host I67. |
| CP12 | NORMALIZATION_DESIGN_REQUIRED | Adapter/punteros pueden exponer metadata anidada existente, con schema explícito, autoridad y controles; nueva implementación requiere contrato y matriz. | I68 sólo añade referencias documentales; no cambia ni ejecuta el trazador/registro I67 o I38. |
| CP13 | AGGREGATION_DESIGN_REQUIRED | La suficiencia por test/grupo exige revisar escenarios hijos y entorno/comando/input pertinentes, distinguiendo N/A y carencias; no propagar un tag local como garantía completa. | 120 tests localmente COMPLETE_RECORDED_SCOPE enlazan escenarios INCOMPLETE;317 tags locales no son317 escenarios completos. |
| CP14 | GLOBAL_LIMITS_UNCHANGED | Catálogo futuro finito, límites y permisos propios, preservación D1–D4/hito local y requisitos reales/humanos; publicación separada. | Sin campañas nuevas ahora, acceso real/credenciales, consumo/reservas, activación, promoción, despliegue, D6 ni cierre automático. |

Los191 escenarios HC/HF/IC/UQ/RV/NA tienen point no nulo en eventos y189 tienen operation; son etiquetas de raw existentes, no191 fronteras físicas acreditadas. NA35/NA36 son controles de evidencia con operación no registrada en eventos; decidir N/A requiere oráculo/contrato propios.

317 clasificaciones locales COMPLETE por test incluyen120 que enlazan escenarios INCOMPLETE. El conteo no expresa suficiencia transitiva. GX/FN/CE conservan su alcance técnico I67, sin aceptación global. Ningún pendiente es test nuevo o campaña autorizada. Agregado81/3; P0 y cierres previos conservados.
