# D5 I75 — matriz AT01–AT80

[Contrato](D5-I75-TYPED-ADAPTER-DESIGN.md) · [Selectores/pins](../validation/D5-I75-design-review.json) · [Integridad](../validation/D5-I75-integrity.json).

**Diseño solamente.** AT80 propuestos para I76 con suites/clases nuevas, sin imports de producto/runners históricos. Ningún caso se implementa o ejecuta en I75. I77/P01 requiere autorización posterior separada.

| ID | Familia | Estímulo | Oráculo exigido |
|---|---|---|---|
| AT01 | AUTHORITY | Falta autoridad humana I77 o existe sólo I74 | Bloquear antes de imports históricos/worker/destino; autorización I74 no se reutiliza. |
| AT02 | AUTHORITY | Pins del contrato, fuente, adaptadores o evidencia alterados | STALE_INPUTS/STALE_AUTHORITY; no aprender hashes nuevos para completar. |
| AT03 | AUTHORITY | Scope distinto de P01 o módulo/URL/root arbitrario | Rechazar; interfaz futura cerrada y registro nuevo fijo. |
| AT04 | AUTHORITY | Registro I73/I70 o evidencia I71/I74 modificados | Bloquear preservación; fuentes anteriores permanecen byte a byte. |
| AT05 | AUTHORITY | 29 IDs snapshot y DI28 confundidos por prefijo | Selectors exactos y conjuntos disjuntos; no nueva excepción por familia de tests. |
| AT06 | AUTHORITY | Cinco operand scopes/helper/roles mezclados | Aplicar sólo fila exacta; representación desconocida conserva NOT_RECORDED. |
| AT07 | AUTHORITY | Imports del componente o modo plan | Sólo stdlib y helpers puros pinneados; cero imports de producto/runners históricos. |
| AT08 | AUTHORITY | Clase de producto aún no cargada al resolver | Bloquear binding concreto; no importar módulos nuevos para descubrir clases. |
| AT09 | AUTHORITY | Manifest y código controlados juntos por caller | Puerta de coherencia, no atestación independiente ni aprobación humana por archivo. |
| AT10 | AUTHORITY | Gates PG64 históricos de ausencia I74 | No borrar autoridad I74 ni reejecutar PG64 para simular fase I73; AT ejercita regresión sintética nueva. |
| AT11 | SNAPSHOT | Snapshot exacto con schema/run_id/version/head_sha256 | Extraer sólo campos ya retornados; autoridad FIXTURE_DRIVE, no Store.store_id. |
| AT12 | SNAPSHOT | Genésis version0 y límite1023 | Aceptar enteros exactos0..1023; bool/negativo/1024 bloqueados sin coerción. |
| AT13 | SNAPSHOT | UUID o hash no canónicos | NOT_RECORDED/INCOMPLETE; no normalizar datos corruptos para aceptar. |
| AT14 | SNAPSHOT | Schema desconocido o diccionario subclass | No acceso genérico a propiedades ni heurística por nombres; metadata incompleta. |
| AT15 | SNAPSHOT | Snapshot no contiene store_id/scope_sha256 | No inventarlos ni recuperar datos leyendo root/disco. |
| AT16 | SNAPSHOT | Versión/head cambian con mismo run_id y objeto | Guardar observaciones distintas; cambio legítimo de head no es cambio de identidad. |
| AT17 | SNAPSHOT | run_id cambia para mismo objeto de fixture | Conservar autoridades en conflicto e invalidar; no sobrescribir identidad anterior. |
| AT18 | SNAPSHOT | Objetos distintos comparten run_id | Referencias de objeto separadas; no fusionar Stores/roots por UUID. |
| AT19 | SNAPSHOT | Snapshot original retorna objeto o lanza excepción | Una llamada original, misma identidad/exception; no snapshot extra como medición. |
| AT20 | SNAPSHOT | Snapshot Drive fuera de los29 IDs | Puede conservar digest anterior, pero no sustituye requisitos Store/otros grupos ni habilita N/A. |
| AT21 | NEGATIVE_DI28 | FixtureStore.__init__ retorna normalmente dentro de DI28 | Observar argumento run_id ligado tras retorno; declaración de construcción del padre, no head. |
| AT22 | NEGATIVE_DI28 | Constructor falla antes del retorno | Excepción original preservada y ninguna declaración exitosa inventada. |
| AT23 | NEGATIVE_DI28 | Argumentos root/scope/fault/ready | No publicarlos ni derivar scope_sha256; sólo UUID run_id observado y referencia de objeto. |
| AT24 | NEGATIVE_DI28 | Constructor fuera del frame DI28 | No enlazar por proximidad ni dar crédito a otra llamada/test. |
| AT25 | NEGATIVE_DI28 | DI28 tiene varios fixtures propios | Conservar declaraciones separadas y enlaces explícitos a su frame. |
| AT26 | NEGATIVE_DI28 | DI28 no llama snapshot | No exigir un head artificial ni declarar N/A de dominio; exige declaración y predicados originales. |
| AT27 | NEGATIVE_DI28 | Cleanup RuntimeError/ownership_changed/sentinel | No llamadas adicionales de close/cleanup/stat; preservar oráculos y excepciones originales. |
| AT28 | NEGATIVE_DI28 | Hijo spawn sin wrapper propio | Sólo metadata de protocolo existente; no atribuir constructor del padre al hijo. |
| AT29 | NEGATIVE_DI28 | Declaración de DI28 usada para otro ID | Rechazar crédito cruzado; los otros29 exigen snapshot retornado. |
| AT30 | NEGATIVE_DI28 | Reinicio/rebinding del mismo objeto con otro run_id | Invalidez con declaraciones observadas preservadas; sin reparación ni sustitución. |
| AT31 | PATH | Dos exact PosixPath con mismo valor lexical | HMAC-SHA256 real por captura sobre bytes lexicales etiquetados; tokens comparables sólo dentro de ese run. |
| AT32 | PATH | Paths distintos y assertNotEqual original exitoso | Conservar predicado retornado; no evaluar igualdad otra vez ni deducirla del digest. |
| AT33 | PATH | Tuple(Path,str) y list(Path) | Codificación tipada streaming de contenedores exactos; preservar tipos/orden y presupuesto16MiB. |
| AT34 | PATH | Path subclass con __str__/repr/fspath trampa | Rechazar antes de ejecutar métodos de objeto arbitrario; cero llamadas extra a traps. |
| AT35 | PATH | Binding stdlib PurePath.as_posix modificado | Bloquear projector; descriptor/firma/origen/identidad pinneados antes y después. |
| AT36 | PATH | Paths relativos, absolutos o Unicode | Representación lexical con UTF-8 surrogatepass acotada; no resolve/exists/stat/IO. |
| AT37 | PATH | Key opaca efímera por captura | 32 bytes generados localmente; nunca serializar key, ruta o lexical bytes ni enviar a hijos. |
| AT38 | PATH | Cambiar key entre capturas | Tokens no se comparan como IDs estables; registrar scope=capture_run_id y algoritmo explícito. |
| AT39 | PATH | Path demasiado grande o contenedor cíclico | NOT_RECORDED con razón; sin truncar, muestrear, recursión/custom iterators o digest ficticio. |
| AT40 | PATH | Paquete con tokens HMAC correctos de forma | Sólo verifica forma/enlaces del witness; sin key no recomputación independiente de ruta, no afirmar lo contrario. |
| AT41 | CLASS_EXCEPTION | Objeto clase dict exacto | Class ref builtins.dict y contexto de intérprete; no repr o nombre derivado de objeto arbitrario. |
| AT42 | CLASS_EXCEPTION | Clases PlaneError y EligibilityError exactas | Resolver identidad desde módulos ya cargados y fuente pinneada; no imports en componente. |
| AT43 | CLASS_EXCEPTION | Metaclass custom con __instancecheck__ | Observer no ejecuta isinstance/issubclass adicional; preservar única evaluación original. |
| AT44 | CLASS_EXCEPTION | Subclass/desconocido en clase o instancia | NOT_RECORDED, no aceptación por nombre coincidente o herencia aproximada. |
| AT45 | CLASS_EXCEPTION | Instancia exacta con BaseException.args tuple | Leer descriptor stdlib args; proyección type+args, no digest del objeto completo. |
| AT46 | CLASS_EXCEPTION | Exception args con un código mayúsculo≤80 | SHA256 canónico de tuple builtin, sin publicar args ni llamar str(exception). |
| AT47 | CLASS_EXCEPTION | Args custom, múltiples valores o payload no permitido | Bloquear proyección; no propiedades/repr/coerción ni filtrado para aparentar soporte. |
| AT48 | CLASS_EXCEPTION | Clase exportada/fuente cambia durante run | Detectar cambio e invalidar; metadata de origen no se actualiza automáticamente. |
| AT49 | CLASS_EXCEPTION | assertIsInstance retorna/lanza | Registrar outcome observado; no crear positivo desde source AST o tipo esperado. |
| AT50 | CLASS_EXCEPTION | Mezcla de builtin dict y class dict en operands | Builtin-only digest permanece byte idéntico I70; witness tipado sólo en rol permitido. |
| AT51 | OBSERVATION | Valores ya soportados por I70 | Mismos bytes/digest/status; sin alterar funciones o constantes globales I70/I73. |
| AT52 | OBSERVATION | Witness tipado nuevo anidado | Schema versionado y digest de representación tipada; nunca llamarlo serialización completa de Python. |
| AT53 | OBSERVATION | Helper assertEqual/assertNotEqual devuelve | Registrar retorno real y hashes observados, sin volver a llamar comparación/fixture. |
| AT54 | OBSERVATION | Assertion delegada/nidada y subTest | Depth/callbacks/resultados conservados; no assertions duplicadas como tests nuevos. |
| AT55 | OBSERVATION | Test con assertion fallida/error/skip | Preservar raw y outcome; no convertir incompletitud instrumental en PASS funcional. |
| AT56 | OBSERVATION | Fallo del projector en llamada/test | Latch fuera del stream, no excepción instrumental dentro de producto; parar entre tests si inválido. |
| AT57 | OBSERVATION | Nueva ausencia/tipo/schema en otra fila | INCOMPLETE/BLOCKED y ajuste concreto; sin expansión automática de whitelist. |
| AT58 | OBSERVATION | Constructor y snapshot de ámbitos distintos | Separar Store head/Drive snapshot/Drive construction; no aceptar cualquier run_id como autoridad genérica. |
| AT59 | OBSERVATION | Restauración tras éxito, exception o budget | Objetos exactos de callbacks/constructores/helpers previos; detectar sustitución ajena. |
| AT60 | OBSERVATION | Método factory/alias y raw record links previos | Bindings321 y mutación tardía de registros se conservan; sin cambiar oráculos funcionales. |
| AT61 | PAGES_BOUNDS | Evento tipado cruza página | Mismo formato paginado I72, índice/bytes/rangos/hash estrictos; no cortar evento. |
| AT62 | PAGES_BOUNDS | Frame atraviesa páginas o comparte página con otro | Vínculo exacto de IDs/lifecycle y referencias de snapshot/constructor/witness. |
| AT63 | PAGES_BOUNDS | 131072 eventos/campaña o2048/test excedidos | Bloquear, sin reset de counters al cambiar adaptador, frame o página. |
| AT64 | PAGES_BOUNDS | 32 páginas/2MiB por página/64MiB acumulados excedidos | Guardas independientes; no reset de cuota por kind de evidencia. |
| AT65 | PAGES_BOUNDS | Witness/evento>4KiB o operandos>16MiB | Bloquear sin resumen inventado ni muestreo; charging incluye representación y tags. |
| AT66 | PAGES_BOUNDS | Frames4096/ref16384/profundidad32/string4096 | Topes I72 sin cambio; referencias typed y constructor también consumen cuota. |
| AT67 | PAGES_BOUNDS | Raw/index/context/launch>12MiB o paquete>112MiB+4KiB | Rechazar; dimensiones nuevas no obtienen canal/presupuesto aparte. |
| AT68 | PAGES_BOUNDS | Lectura evidencia/input budget independiente y acumulada | 128MiB únicos/256MiB leídos por ámbito, sin reset entre validación y finish. |
| AT69 | PAGES_BOUNDS | Tiempo900s futuro o límite menor runner/hijo/hook | No ampliar alarmas/límites kernel ni añadir actores para completar. |
| AT70 | PAGES_BOUNDS | Metadato/control/TEST_END ausente tras agotar cuota | Propagar INVALID/INCOMPLETE, preservar páginas; no cierre ficticio del stream. |
| AT71 | EVIDENCE_OWNERSHIP | Destino futuro I77 existente o symlink/FIFO/traversal | Rechazar sin overwrite; no tocar I71/I74 ni seguir paths de manifest arbitrario. |
| AT72 | EVIDENCE_OWNERSHIP | READY/RELEASE sin correlación nonce/PID/PGID/fds/directorio | No liberar ni señalizar procesos ajenos; capacidad sólo propia. |
| AT73 | EVIDENCE_OWNERSHIP | Timeout/EOF con recursos propios pendientes | Parada ordenada y sólo grupo propio; no afirmar cero sin confirmación. |
| AT74 | EVIDENCE_OWNERSHIP | Sibling y dev/run_data/D4 operativo | Sentinel ajeno intacto; no inspección/limpieza de ámbito operativo o privado. |
| AT75 | EVIDENCE_OWNERSHIP | Origen fuente esperado comparado con tipo observado | Separar expectativa AST de witness runtime; no rellenar I74 desde fuente/digests. |
| AT76 | EVIDENCE_OWNERSHIP | Completitud de hijo snapshot/witness faltante | INCOMPLETE se propaga a test/grupo/campaña; conteo y checksum no la sustituyen. |
| AT77 | EVIDENCE_OWNERSHIP | I76 AT80 ejecutado sólo con clases/procesos sintéticos | Cero imports de producto/runners y cero ocurrencias funcionales; retiro de temporales/children propios. |
| AT78 | EVIDENCE_OWNERSHIP | Plan por defecto y autoridad I77 ausente | NOT_RUN sin crear aprobación, paquetes o procesos funcionales. |
| AT79 | EVIDENCE_OWNERSHIP | 321 PASS funcionales con metadata aún incompleta | Conservar raw PASS y captura BLOCKED; no aceptar Python321 por la suma. |
| AT80 | EVIDENCE_OWNERSHIP | Captura futura completa e íntegra | Como máximo TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW;81/3 y globales abiertos hasta revisión separada. |

## Scopes snapshot exactos

| ID real de test | Retornos snapshot observados I74 | Nueva obligación diseñada |
|---|---:|---|
| test_incremental_capture.IncrementalCaptureTest.test_DI01_scope_genesis_identity_and_no_reference | 1 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI02_anchor_before_inventory_and_observed_new_revision | 4 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI03_inventory_pages_preserve_anchor_until_explicit_end | 5 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI04_feed_continuation_and_terminal_are_separate | 7 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI05_duplicate_observations_keep_occurrences_not_duplicate_identity | 5 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI06_empty_pages_and_empty_poll_with_same_terminal_token | 5 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI07_fresh_process_recovers_state_from_disk | 2 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI08_bytes_diagnostics_receipt_and_cursor_share_one_commit | 1 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI08_docs_export_grade_survives_filesystem_recovery_without_reference | 2 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI09_transient_late_event_never_commits_a_prefix | 3 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI10_kill_before_object_does_not_authorize_partial_temporary | 4 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI11_kill_after_object_preserves_old_head_and_ignores_orphan | 5 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI12_kill_after_head_recovers_receipt_without_reapplying | 5 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI13_before_replace_or_uncertain_fsync_recovers_whole_state | 5 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI13_recovery_must_sync_visible_head_before_confirming_receipt | 1 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI14_two_writers_cas_and_command_content_conflict | 2 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI15_outside_allowlist_keeps_terminal_diagnostic_only | 4 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI16_unsupported_formats_and_size_limit_not_silent_truncation | 2 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI17_removal_and_file_access_loss_are_not_D2_absence_application | 2 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI18_global_auth_error_cannot_be_diagnosed_as_file_skip | 9 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI19_later_accessible_file_does_not_erase_terminal_history | 3 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI20_ambiguous_or_invalid_encoding_bytes_are_captured_blocked | 3 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI21_changed_source_scope_error_and_caller_terminal_override_block | 9 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI22_scope_changes_need_a_new_root | 3 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI23_malformed_pages_and_json_duplicate_keys_never_advance | 3 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI24_limits_reject_whole_page_and_history_without_truncation | 9 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI25_opaque_tokens_and_continuation_cycles | 8 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI26_corruption_blocks_without_selecting_orphans_or_repairing | 1 | Retorno tipado Drive; constructor no basta |
| test_incremental_capture.IncrementalCaptureTest.test_DI27_root_and_file_links_wrong_marks_and_other_roots_are_rejected | 1 | Retorno tipado Drive; constructor no basta |

## DI28 y operandos

DI28: `test_incremental_capture.IncrementalCaptureTest.test_DI28_cleanup_finally_owns_only_created_root_and_preserves_sentinels`. Cero snapshot retornado I74. Constructor de fixture sólo como declaración del padre en caso negativo; no head, N/A o identidad retrospectiva.

| ID real de test | Helper | Roles/proyecciones diseñadas | Eventos I74 |
|---|---|---|---:|
| test_local_preview.LocalPreviewTest.test_new_revision_label_preserves_bytes_without_overwriting_observation | assertNotEqual | {"0": ["exact-posix-path"], "1": ["exact-posix-path"]} | 1 |
| test_local_preview.LocalPreviewTest.test_repeated_observation_and_save_are_idempotent | assertEqual | {"0": ["exact-tuple(exact-posix-path,builtin-str)", "exact-list(exact-posix-path)"], "1": ["exact-tuple(exact-posix-path,builtin-str)", "exact-list(exact-posix-path)"]} | 2 |
| test_plane_reconciliation.PlaneReconciliationTest.test_PC10_query_during_inflight_send_recovers_after_publish_CAS_conflict | assertIsInstance | {"0": ["exact-PlaneError-instance-args-projection"], "1": ["class-source_ingest.plane_fixture.PlaneError"]} | 1 |
| test_plane_reconciliation.PlaneReconciliationTest.test_PC10_two_local_senders_and_two_query_publishers_compete | assertIsInstance | {"0": ["builtin-only-original-digest"], "1": ["class-builtins.dict"]} | 1 |
| test_profiles_quotas.ProfilesQuotasTest.test_PQ26_fact_change_between_read_and_CAS_has_no_positive_receipt | assertIsInstance | {"0": ["exact-EligibilityError-instance-args-projection"], "1": ["class-source_ingest.eligibility_fixture.EligibilityError"]} | 1 |

Los cinco scopes reúnen seis eventos y11 slots UNSUPPORTED_OPERAND. Las proyecciones se comprobarán con tipos runtime reales; la fuente no rellena I74. Key HMAC por run no publicada, comparación sólo dentro de captura y sin recomputación independiente de ruta. Digests builtin-only byte idénticos a I70. Metadata de snapshot, constructor e instancia/clase son autoridades distintas.

Topes I72 intactos y propagación de INCOMPLETE. P0 y81/3; criterios globales abiertos. Sin implementación, campañas, publicación o cierre.
