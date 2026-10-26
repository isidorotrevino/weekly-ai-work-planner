# I79 — binding tardío y diagnóstico acotado

[Contrato I78](../../docs/design/D5-I78-LATE-BINDING-DESIGN.md), [matriz LB64](../../docs/design/D5-I78-LATE-BINDING-REVIEW.md). Sólo stdlib y capturadores puros I70/I73/I76 sin modificar sus fuentes o registros. No importar módulos de pruebas/laboratorios PG64/AT80.

- `python3 -B -m testing.prospective_capture_late.run_late_lab`: LB64 con clases, módulos, suites y procesos sintéticos nuevos; wrapper externo de 300 segundos.
- `python3 -B -m testing.prospective_capture_late.capture`: plan NOT_RUN_I80_AUTHORIZATION_REQUIRED.
- `--capture P01`: necesita autorización humana posterior I80 y manifiesto fijo `docs/validation/D5-I80-capture-authorization.json`; aprobar I79 sólo habilita componentes sintéticos.

Autoridad futura schema `d5.late-capture-authority.v1`, claves exactas schema/phase/scopes/registry_sha256/capture_inputs; fase I80_EXPLICITLY_APPROVED, scopes=[P01]. Pins del perfil/registro/evidencia validada I79 y dependencias I69–I78, incluido seal I79 y todos sus artifacts. Coherencia de archivos no equivale a autorización humana o atestación independiente. No crear el manifiesto en I79. Destino exclusivo futuro `docs/validation/D5-I80-P01/` y copia fija hermana `D5-I80-P01-launch.json`, sin overwrite de I71/I74/I77.

El resolver empieza sólo con builtin dict y liga las dos excepciones desde módulos ya cargados al primer ID/helper/rol permitido, después del helper original. Sin imports o discovery extra, rebind, comparación/isinstance adicionales o exigencia global de clases en finish. Identidad/fuente/tipo exactos se comprueban antes/después y al finalizar; ausencia/cambio invalida fuera del stream y detiene entre tests preservando el original. Reader acumulado compartido para inputs y bindings. Los scopes/encoding I75 permanecen exactos: 29 snapshot Drive, DI28 negativo, cinco operandos, tres clases, siete políticas anteriores y321 IDs/12 grupos.

Diagnóstico cerrado `d5.worker-diagnostic.v1` de hasta4096 bytes dentro del sidecar existente de12MiB. Primera fase/código de fallo por allowlist, sin mensaje, traceback, rutas, payloads o keys. Sidecar normal `d5.late-sidecar.v1`; fallo previo a escritura final `d5.late-worker-failure.v1` con sólo schema y diagnóstico FAILED. Un único JSON por sidefd, sin canal/archivo/cuota adicionales ni append/overwrite tras escritura parcial. No se escribe antes de validar autoridad/capacidad. El padre correlaciona lease/PID/PGID y run_id si existe; conserva error de artifact aparte. COMPLETED/OK no prueba PASS funcional o suficiencia. Un diagnóstico ausente no se reconstruye desde AST.

Topes I72/I75 intactos:131072 eventos/campaña,2048/test,4KiB/evento,32 páginas de2MiB y64MiB acumulados; raw/índice/contexto/launcher≤12MiB, paquete≤112MiB+4KiB y37 miembros contando launcher.900s externos futuros y límites menores intactos. No capacidad funcional probada por LB64. Path HMAC sólo comparable dentro de captura y sin recomputación independiente; excepción es TYPE_AND_ARGS_PROJECTION_NOT_FULL_EXCEPTION_OBJECT.

I77 conservado sin confirmar retrospectivamente su error interno. I71/I74 bloqueados y P02–P10 pendientes de suficiencia. P0,81/3 y D5 global/H07/G01–G07/GI abiertos; D1–D4 cerrados e hito local I1–I20 aceptado intactos. Sin publicación.
