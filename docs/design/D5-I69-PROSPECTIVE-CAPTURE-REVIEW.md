# D5 I69 — captura prospectiva y PF01–PF60

Fecha: **2026-10-26**. [Contrato](D5-I69-PROSPECTIVE-CAPTURE-DESIGN.md) · [Pins, fases y oráculos](../validation/D5-I69-design-review.json).

60 tests del capturador propuestos; cero ejecutados. I70 propuesto sólo implementa y valida componentes sintéticos. P01–P10 requieren aprobación de ejecución posterior I71; no son pruebas ya corridas.

| ID | Runner futuro / scope | Tests esperados | Grupos | Escenarios originales esperados |
|---|---|---|---|---|
| P01 | testing.D5.run_relational_durable_lab | 321 | 12 | 0 |
| P02 | testing.gi39_interleavings.run_gi39_interleavings_lab | 90 | 1 | 90 |
| P03 | testing.durable_concurrency.run_concurrency_lab | 24 | 1 | 25 |
| P04 | testing.durable_crash_boundaries.run_crash_boundaries_lab | 40 | 1 | 41 |
| P05 | testing.durable_issue_create.run_issue_create_lab | 30 | 1 | 31 |
| P06 | testing.durable_uncertainty.run_uncertainty_lab | 24 | 1 | 26 |
| P07 | testing.durable_inflight_revocation.run_inflight_revocation_lab | 20 | 1 | 20 |
| P08 | testing.durable_native_ambiguity.run_native_ambiguity_lab | 36 | 1 | 48 |
| P09 | testing.durable_frontier_gaps.run_frontier_gaps_lab | 64 | 1 | 64 |
| P10 | testing.causal_frontier_cells.run_causal_cells_lab | 43 | 1 | 43 |

692 ocurrencias futuras repartidas en diez campañas y21 grupos; Python321 contiene12 grupos. Las388 filas originales esperadas sólo describen cardinalidad de schema/variantes, no un límite a nuevos frames unitarios ni aceptación global. I34/I36 se conservan como historia y no se ejecutan en sus commits ni se completan retrospectivamente.

| Caso | Familia / alcance | Situación | Oráculo exigido |
|---|---|---|---|
| PF01 | FIXED_MANIFEST / P01 | Validar manifiesto P01/Python contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF02 | FIXED_MANIFEST / P02 | Validar manifiesto P02/GX contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF03 | FIXED_MANIFEST / P03 | Validar manifiesto P03/HC contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF04 | FIXED_MANIFEST / P04 | Validar manifiesto P04/HF contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF05 | FIXED_MANIFEST / P05 | Validar manifiesto P05/IC contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF06 | FIXED_MANIFEST / P06 | Validar manifiesto P06/UQ contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF07 | FIXED_MANIFEST / P07 | Validar manifiesto P07/RV contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF08 | FIXED_MANIFEST / P08 | Validar manifiesto P08/NA contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF09 | FIXED_MANIFEST / P09 | Validar manifiesto P09/FN contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF10 | FIXED_MANIFEST / P10 | Validar manifiesto P10/CE contra fuente/pins mediante datos sellados y fixture de invocación; no importar su runner. | Módulo/IDs/grupos/targets/inventario/multiplicidad fijos, argv worker distinto de declaración del runner, estado NOT_RUN de campaña funcional. |
| PF11 | LIFECYCLE / SYNTHETIC_COMPONENT_ONLY | Inicio/fin y resultado exactos en suite sintética de varios grupos | Una fila por test, grupos partición exacta y comando padre registrado; no inferir end desde PASS agregado. |
| PF12 | LIFECYCLE / SYNTHETIC_COMPONENT_ONLY | FAIL/error/skip/expectedFailure/unexpectedSuccess/subTest en suite sintética | Preservar cada resultado y denominadores; nunca llenar successful por ausencia de excepción. |
| PF13 | LIFECYCLE / SYNTHETIC_COMPONENT_ONLY | Caso crea varios escenarios/Stores | Preservar IDs reales del dueño y ordinales con relación muchos-a-muchos, sin contar más tests. |
| PF14 | LIFECYCLE / SYNTHETIC_COMPONENT_ONLY | Caso sin Store o frontera integrada | Capture/frame ID separado; N/A motivado por manifiesto y oráculo unitario, sin UUID de Store inventado. |
| PF15 | LIFECYCLE / SYNTHETIC_COMPONENT_ONLY | Contexto no termina o falta callback de resultado | INCOMPLETE/NOT_RUN sin PASS heredado; cleanup propio y estado final inválido del capturador. |
| PF16 | LIFECYCLE / SYNTHETIC_COMPONENT_ONLY | Unittest delega/nida callbacks o assertion helpers | Depth/control de duplicados preserva resultado/cuenta; métricas de assertions no son tests nuevos. |
| PF17 | OBSERVER / SYNTHETIC_COMPONENT_ONLY | Wrapper observa función que retorna objeto sintético | Original llamado una vez, mismos args/identidad del retorno; metadata sólo de retorno ya producido. |
| PF18 | OBSERVER / SYNTHETIC_COMPONENT_ONLY | Función observada lanza excepción sintética | Misma excepción y traceback semántico para caller; registrar código saneado sin transformar resultado. |
| PF19 | OBSERVER / SYNTHETIC_COMPONENT_ONLY | Observer falla o rebasa presupuesto al registrar | No relanzar dentro de producto; captura INVALID y terminar ordenadamente al límite entre tests, sin afirmar campaña completa. |
| PF20 | OBSERVER / SYNTHETIC_COMPONENT_ONLY | Instalación/restauración de wrappers bajo error/skip/timeout | Restaurar objetos exactos del proceso propio, sin modificar ficheros o instalar hooks globales persistentes. |
| PF21 | OBSERVER / SYNTHETIC_COMPONENT_ONLY | Assertion exitosa y negativa/context manager | Distinguir declaración expected-exception de observación de salida; adaptador no soportado queda BLOCKED, sin cambiar identidad/semántica. |
| PF22 | OBSERVER / SYNTHETIC_COMPONENT_ONLY | Argumento/resultado grande o tipo no serializable | Digest streaming completo acotado o falta explícita; no repr ni truncado o acceso a propiedades para fabricar un oráculo. |
| PF23 | OBSERVER / SYNTHETIC_COMPONENT_ONLY | Observar snapshot/perform frente a ejecutar lectura nueva | Cero llamadas extra; no snapshot/perform/lookup/execute añadido por capturador, ni recuperación que cambie el caso. |
| PF24 | OBSERVER / SYNTHETIC_COMPONENT_ONLY | Hijo spawn no instrumentado por callbacks del padre | Sólo raw/gates ya emitidos enlazables; no atribuir al hijo metadata del padre como medición propia. |
| PF25 | PROVENANCE / SYNTHETIC_COMPONENT_ONLY | argv worker real vs context.argv literal del runner/demos | Separar invocación observada, entrypoint y declaración del runner; demo no se eleva a comando de campaña. |
| PF26 | PROVENANCE / SYNTHETIC_COMPONENT_ONLY | Entorno de parent/worker difiere o falta build/flags/kernel | Registrar valores por proceso cuando constan; herencia explícita o BLOCKED para campo requerido, sin completar historia. |
| PF27 | PROVENANCE / SYNTHETIC_COMPONENT_ONLY | Grupo comparte invocación padre | Referencia al mismo contexto; target/versiones propios sin inventar proceso/CLI por grupo. |
| PF28 | PROVENANCE / SYNTHETIC_COMPONENT_ONLY | Captura nueva intenta rellenar I34/I36/I64 | Identidad nueva y referencias históricas inmutables; rechazar reescritura o sustitución de stdout/IDs/entorno anteriores. |
| PF29 | PROVENANCE / SYNTHETIC_COMPONENT_ONLY | Operandos esperados/observados de assertion vs source | Declaración de source distinta de evaluación del predicado; hashes/resultado propios no prueban frontera durable por sí solos. |
| PF30 | BINDING / SYNTHETIC_COMPONENT_ONLY | Test ID observado distinto del manifiesto | STOP/INVALID_SCOPE; no actualizar pin automáticamente para lograr PASS. |
| PF31 | BINDING / SYNTHETIC_COMPONENT_ONLY | Metadata point/operation anidada en raw fresco | Schema/puntero/evento/rol precisos; preservar secuencia, sin asumir toda etiqueta como corte físico. |
| PF32 | BINDING / SYNTHETIC_COMPONENT_ONLY | Punteros rotos, caso equivocado o modo/rol/Store incompatible | BLOCKED/INVALID_BINDING con diagnóstico saneado, sin evidencia prestada de otra variante. |
| PF33 | BINDING / SYNTHETIC_COMPONENT_ONLY | Método generado por factory | ID observado ligado a factory/argumentos/expansión y source hash como derivación; no exigir definición AST individual inexistente. |
| PF34 | BINDING / SYNTHETIC_COMPONENT_ONLY | Agregación test→escenarios→grupo con hijo incompleto | Propagar carencias aplicables y N/A revisado; tag local COMPLETE no cierra obligación. |
| PF35 | BINDING / SYNTHETIC_COMPONENT_ONLY | Inventario original del runner vs del capturador | Dos ámbitos ligados por hash, sin alegar que discovery histórico incluyó módulos nuevos. |
| PF36 | INTEGRITY / SYNTHETIC_COMPONENT_ONLY | Bytes/config/contrato ejecutable cambian pre/post | STALE_INPUTS o INVALID_CAPTURE, nunca nuevo contexto sobre bytes viejos. |
| PF37 | INTEGRITY / SYNTHETIC_COMPONENT_ONLY | Namespace pertinente añade/retira archivo | Diferencia de conjunto además de hashes; no unión global sustituyendo reglas específicas. |
| PF38 | INTEGRITY / SYNTHETIC_COMPONENT_ONLY | Cambio únicamente documental o versión declarada sin hash | Separar delta documental y expectativa; no renovar autoridad/ejecución con etiqueta de versión. |
| PF39 | INTEGRITY / SYNTHETIC_COMPONENT_ONLY | JSON duplicado/NaN/profundidad/strings y enteros booleanos | Rechazo estricto previo a agregación; output sin texto privado de error. |
| PF40 | INTEGRITY / SYNTHETIC_COMPONENT_ONLY | Raw/contexto/sidecar/manifest parcial o hash distinto | Conservar las partes disponibles como incompletas; sin artefacto final completo o PASS operativo. |
| PF41 | BOUNDS / SYNTHETIC_COMPONENT_ONLY | Raw original o sidecar superan12MiB | No truncar ni aumentar límite; captura inválida y propuesta de ajuste concreto antes de ejecutar otra ampliación. |
| PF42 | BOUNDS / SYNTHETIC_COMPONENT_ONLY | Eventos por test/campaña o metadata/operandos excedidos | INVALID_CAPTURE al registrar, sin cambiar la llamada original; detener en frontera segura tras limpieza. |
| PF43 | BOUNDS / SYNTHETIC_COMPONENT_ONLY | Timeout/EOF/salida worker anómala con hijo propio | Registrar fallo, terminar/esperar sólo descendientes propios con prueba de ownership; no SIGKILL de aceptación de dominio. |
| PF44 | BOUNDS / SYNTHETIC_COMPONENT_ONLY | Resultado completo de runner con sidecar inválido | Conservar raw funcional como hecho separado; captura no se etiqueta completa ni suficiente. |
| PF45 | SAFETY / SYNTHETIC_COMPONENT_ONLY | Path/URL/comando/scope fuera del catálogo cerrado | Rechazar antes de abrir o lanzar; cero shell, red, proveedores, SQL/Java/Docker. |
| PF46 | SAFETY / SYNTHETIC_COMPONENT_ONLY | Symlink/FIFO/directorio/archivo existente o cambio de inode | Sin seguir symlinks ni overwrite; nuevas raíces/archivos propios con sentinel y metadatos de ownership. |
| PF47 | SAFETY / SYNTHETIC_COMPONENT_ONLY | Fixtures negativos y sentinel ajeno hermano | Restaurar temporal propio y comprobar hermano intacto; ninguna inspección/limpieza de dev/run_data/D4. |
| PF48 | SAFETY / SYNTHETIC_COMPONENT_ONLY | stdout/stderr/payload/paths privados en diagnóstico | Emitir sólo metadatos públicos, códigos y hashes; nada de repr/traceback/variables de entorno completas. |
| PF49 | SAFETY / SYNTHETIC_COMPONENT_ONLY | Modo plan/componentes intenta cargar runner funcional | Guard/no import en I70; tests con módulos sintéticos; catálogo vivo sólo en fase autorizada I71. |
| PF50 | SAFETY / SYNTHETIC_COMPONENT_ONLY | Worker vivo recibe orden de cleanup no correlacionada | Rechazar pid/grupo/sentinel no propios, registrar recursos pendientes y bloquear aceptación. |
| PF51 | ACCOUNTING / SYNTHETIC_COMPONENT_ONLY | 692 ocurrencias futuras mezcladas con1294 históricas | Campañas e IDs por invocación; repeticiones no se suman como pruebas nuevas ni reemplazo del pasado. |
| PF52 | ACCOUNTING / SYNTHETIC_COMPONENT_ONLY | Captura de assertions/gates/Stores contada como tests | Métricas separadas; resultado sólo de callbacks/runner y manifiesto exactos. |
| PF53 | ACCOUNTING / SYNTHETIC_COMPONENT_ONLY | Controles tratados como campañas/efectos de dominio | N/A explícito donde procede, no pruebas de recuperación ni200% cobertura por variantes. |
| PF54 | ACCOUNTING / SYNTHETIC_COMPONENT_ONLY | TestResults usan Recorded con overrides/super y prioridades | Suite sintética que reproduce delegación comprueba semántica original, orden y restore, sin modificar runner anterior. |
| PF55 | REPORT / SYNTHETIC_COMPONENT_ONLY | Sidecar completo por campos pero oráculo no ligado a misma secuencia | Sufficiency REVIEW_PENDING o INCOMPLETE, no promover UI por presencia de claves. |
| PF56 | REPORT / SYNTHETIC_COMPONENT_ONLY | Falta relevante o N/A mal motivado | No degradar obligatorio a opcional para obtener COMPLETE; reportar puertas pendientes. |
| PF57 | REPORT / SYNTHETIC_COMPONENT_ONLY | Todos los componentes PF60 pasan sin campañas funcionales | I70 valida capturador, P01–P10 NOT_RUN; tres partes PARTIAL y agregado81/3. |
| PF58 | REPORT / SYNTHETIC_COMPONENT_ONLY | Todos los registros prospectivos futuros coinciden | Sólo TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW; D5/GI globales abiertos y publicación separada. |
| PF59 | REPORT / SYNTHETIC_COMPONENT_ONLY | Integridad de cierre D1–D4/hito local y registro/auditor I38/I67 | Hashes anteriores intactos; no SQL/real ni ejecutar auditores como efecto secundario. |
| PF60 | REPORT / SYNTHETIC_COMPONENT_ONLY | Inputs/código/raw de ejecución de desarrollo se confunden con definitivo | Sellar únicamente campaña completa estable con inputs pre/post y contexto; desarrollos no suman casos. |

CP01–CP14 I68 se traducen en contexto de invocación/grupo, lifecycle, observadores semánticamente pasivos, normalización con punteros, agregación transitiva, presupuestos y preservación histórica. Los PF no son692 regresiones ni escenarios de persistencia nuevos. P0, agregado81/3, D5 global/G01–G07/GI globales abiertos.
