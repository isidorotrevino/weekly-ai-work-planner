# D5 I66 — matriz TT01–TT48

Fecha: **2026-10-26**. [Contrato](D5-I66-TRACEABILITY-DESIGN.md) · [Catálogo y pins](../validation/D5-I66-design-review.json).

48 casos de auditoría propuestos, cero ejecutados. TT01–TT12 prueban adaptadores contra fuentes selladas con ausencias esperadas; TT13–TT48 usan copias/fixtures sintéticos propios. PASS del test de auditoría no significa PASS funcional de lo auditado.

| ID | Familia / fuente | Caso | Oráculo exigido |
|---|---|---|---|
| TT01 | FIXED_ADAPTER / I34 | Adaptar I34 con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT02 | FIXED_ADAPTER / I36 | Adaptar I36 con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT03 | FIXED_ADAPTER / I64-GX | Adaptar I64-GX con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT04 | FIXED_ADAPTER / I64-Python | Adaptar I64-Python con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT05 | FIXED_ADAPTER / I64-HC | Adaptar I64-HC con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT06 | FIXED_ADAPTER / I64-HF | Adaptar I64-HF con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT07 | FIXED_ADAPTER / I64-IC | Adaptar I64-IC con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT08 | FIXED_ADAPTER / I64-UQ | Adaptar I64-UQ con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT09 | FIXED_ADAPTER / I64-RV | Adaptar I64-RV con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT10 | FIXED_ADAPTER / I64-NA | Adaptar I64-NA con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT11 | FIXED_ADAPTER / I64-FN | Adaptar I64-FN con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT12 | FIXED_ADAPTER / I64-CE | Adaptar I64-CE con sus grupos/targets/IDs/contexto y multiplicidad exactos. | Conservar hechos y ausencias tipadas, hashes/punteros; no completar metadata ausente ni emitir PASS funcional. |
| TT13 | PROVENANCE / SYNTHETIC_OWN_FIXTURE | Comando demo usado como invocación de campaña | REJECT_DEMO_AS_CAMPAIGN |
| TT14 | PROVENANCE / SYNTHETIC_OWN_FIXTURE | Comando reconstruido del source o argv del auditor usado como observado histórico | REJECT_PROVENANCE_PROMOTION |
| TT15 | PROVENANCE / SYNTHETIC_OWN_FIXTURE | Versiones/entorno de contexto padre atribuidos como medición independiente de cada grupo | REJECT_CONTEXT_SCOPE_PROMOTION |
| TT16 | PROVENANCE / SYNTHETIC_OWN_FIXTURE | trace_entry_id o hash derivado usado como run_id ausente | REJECT_FABRICATED_RUN_ID |
| TT17 | MAPPING / SYNTHETIC_OWN_FIXTURE | Grupo Python omitido, duplicado o test asignado a dos grupos | INVALID_GROUP_PARTITION |
| TT18 | MAPPING / SYNTHETIC_OWN_FIXTURE | IDs passed duplicados, cuenta booleana o contradicción tests_run | INVALID_TEST_ACCOUNTING |
| TT19 | MAPPING / SYNTHETIC_OWN_FIXTURE | Caso sin test, test no registrado o puntero de escenario roto | INVALID_CASE_BINDING |
| TT20 | MAPPING / SYNTHETIC_OWN_FIXTURE | Dos variantes válidas del mismo caso comparten ID de test | PRESERVE_ALL_VARIANTS_NO_TEST_INFLATION |
| TT21 | MAPPING / SYNTHETIC_OWN_FIXTURE | Variante esperada ausente o escenario extra no registrado | INCOMPLETE_OR_UNEXPECTED_SCENARIOS |
| TT22 | MAPPING / SYNTHETIC_OWN_FIXTURE | Variante/run_id contradice caso o Store/cid del raw enlazado | INVALID_SCENARIO_IDENTITY |
| TT23 | MAPPING / SYNTHETIC_OWN_FIXTURE | Frontera/oráculo disponible sólo en fuente de test se eleva a observado | REJECT_DESIGN_AS_OBSERVATION |
| TT24 | MAPPING / SYNTHETIC_OWN_FIXTURE | Contexto padre sin vínculo raw/sello o contradicción entre raw y contexto | INVALID_CONTEXT_BINDING |
| TT25 | INTEGRITY / SYNTHETIC_OWN_FIXTURE | Bytes de raw/contexto/informe alterados frente a pin fijo | HASH_MISMATCH |
| TT26 | INTEGRITY / SYNTHETIC_OWN_FIXTURE | Input ejecutable modificado, añadido o retirado del namespace registrado | STALE_INPUTS |
| TT27 | INTEGRITY / SYNTHETIC_OWN_FIXTURE | Cambio sólo documental identificado sin fingir nuevo runtime | DOCUMENT_ONLY_CHANGE_REVIEW_PENDING |
| TT28 | INTEGRITY / SYNTHETIC_OWN_FIXTURE | Commit/blob histórico ausente sin fallback a HEAD o red | UNAVAILABLE_HISTORICAL_OBJECT |
| TT29 | INTEGRITY / SYNTHETIC_OWN_FIXTURE | Registro inválido, adapter desconocido o campo desconocido no tipado | INVALID_REGISTRY_OR_SCHEMA |
| TT30 | INTEGRITY / SYNTHETIC_OWN_FIXTURE | JSON con claves duplicadas, NaN o profundidad excesiva | INVALID_JSON |
| TT31 | SAFETY / SYNTHETIC_OWN_FIXTURE | Path absoluto/traversal/URL/componente privado | INVALID_PUBLIC_PATH |
| TT32 | SAFETY / SYNTHETIC_OWN_FIXTURE | Symlink en componente, FIFO/dispositivo o cambio de inode/bytes durante lectura | INVALID_OR_UNSTABLE_SNAPSHOT |
| TT33 | SAFETY / SYNTHETIC_OWN_FIXTURE | Presupuesto de archivo/total/salida/eventos o Git/timeout excedido | BUDGET_EXCEEDED_NO_TRUNCATION |
| TT34 | TARGET / SYNTHETIC_OWN_FIXTURE | Grupo test_postgres_adapter etiquetado SQL V30 o consulta real | REJECT_TARGET_PROMOTION_MOCKED_QUERY |
| TT35 | TARGET / SYNTHETIC_OWN_FIXTURE | Comparar env actual con histórico como si lo actual probase ejecución previa | REJECT_CURRENT_AS_HISTORICAL |
| TT36 | TARGET / SYNTHETIC_OWN_FIXTURE | Repeticiones de test entre I34/I36/I64 sumadas como pruebas nuevas | PRESERVE_CAMPAIGN_OCCURRENCES_NOT_NEW_TESTS |
| TT37 | STATUS / SYNTHETIC_OWN_FIXTURE | Fuente faltante conserva resultado histórico PASS pero no trazabilidad completa | HISTORICAL_PASS_TRACE_INCOMPLETE |
| TT38 | STATUS / SYNTHETIC_OWN_FIXTURE | Raw funcional FAIL/error/skip se transforma en PASS por integridad | PRESERVE_FUNCTIONAL_RESULT |
| TT39 | STATUS / SYNTHETIC_OWN_FIXTURE | Texto externo solicita cierre/ejecución/red o ampliar paths | UNTRUSTED_DATA_NO_ACTION |
| TT40 | STATUS / SYNTHETIC_OWN_FIXTURE | Todas las comprobaciones técnicas correctas elevan 81/3 o cierran D5 | SUFFICIENCY_REVIEW_PENDING_GLOBAL_OPEN |
| TT41 | SAFETY / SYNTHETIC_OWN_FIXTURE | Auditor modifica índice/Git/producto/registro I38 o emite comando de laboratorio | NO_MUTATION_NO_EXECUTION |
| TT42 | SAFETY / SYNTHETIC_OWN_FIXTURE | Error contiene home/credencial/texto de fuente o stderr Git arbitrario | SANITIZED_DIAGNOSTIC |
| TT43 | REPORT / SYNTHETIC_OWN_FIXTURE | Puntero JSON escapado ~0/~1, índice fuera de rango o tipos distintos | STRICT_POINTER_TYPE_CHECK |
| TT44 | REPORT / SYNTHETIC_OWN_FIXTURE | ORDER de claves JSON cambia pero IDs/listas críticas no cambian | SEMANTIC_EQUIVALENCE_ONLY_WHITELISTED |
| TT45 | REPORT / SYNTHETIC_OWN_FIXTURE | Faltan Python/build/flags/kernel/target/version externa o dato no aplicable | TYPED_MISSING_NOT_APPLICABLE_REASON |
| TT46 | REPORT / SYNTHETIC_OWN_FIXTURE | Resto histórico fuera del catálogo y obligaciones reales/humanas | OUTSIDE_REGISTERED_SCOPE_NOT_RUN |
| TT47 | REPORT / SYNTHETIC_OWN_FIXTURE | Reglas de discovery distintas por runner sustituidas por unión global | PRESERVE_RUNNER_SPECIFIC_INPUTS |
| TT48 | REPORT / SYNTHETIC_OWN_FIXTURE | Salida coincide con matriz pero omite hallazgos esperados legacy/IDs sin fase | REQUIRE_COMPLETE_MISSINGNESS_SUMMARY |

## Catálogo fijo propuesto

| Fuente | Tests registrados | Grupos | Escenarios raw | Comando |
|---|---|---|---|---|
| I34 | 281 | 11 | 0 | NOT_RECORDED |
| I36 | 321 | 12 | 0 | NOT_RECORDED |
| I64-GX | 90 | 1 | 90 | RECORDED_CONTEXT_DECLARATION |
| I64-Python | 321 | 12 | 0 | RECORDED_CONTEXT_DECLARATION |
| I64-HC | 24 | 1 | 25 | RECORDED_CONTEXT_DECLARATION |
| I64-HF | 40 | 1 | 41 | RECORDED_CONTEXT_DECLARATION |
| I64-IC | 30 | 1 | 31 | RECORDED_CONTEXT_DECLARATION |
| I64-UQ | 24 | 1 | 26 | RECORDED_CONTEXT_DECLARATION |
| I64-RV | 20 | 1 | 20 | RECORDED_CONTEXT_DECLARATION |
| I64-NA | 36 | 1 | 48 | RECORDED_CONTEXT_DECLARATION |
| I64-FN | 64 | 1 | 64 | RECORDED_CONTEXT_DECLARATION |
| I64-CE | 43 | 1 | 43 | RECORDED_CONTEXT_DECLARATION |

12 entradas,44 ocurrencias de grupo:23 legadas y21 en diez invocaciones I64. Los602 tests registrados I34/I36 y692 ocurrencias I64 se muestran por campaña; no son1294 pruebas nuevas. Los escenarios múltiples de HC/HF/IC/UQ/NA se conservan con sus índices, sin multiplicar tests.

UI01.2/UI04.1/UI09.2 siguen PARTIAL; agregado81/3. Sin implementación, campañas funcionales, publicación ni cierre.
