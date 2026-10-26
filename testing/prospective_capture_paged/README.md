# I73 — captura prospectiva paginada P01

[Contrato I72](../../docs/design/D5-I72-PAGED-CAPTURE-DESIGN.md), políticas exactas y PG01–PG64. Sólo stdlib y helpers puros I70 pinneados; cargar estos módulos no importa producto/runners históricos.

- `python3 -B -m testing.prospective_capture_paged.run_paged_lab`: PG64 con suites, Stores y procesos sintéticos nuevos. No Python321 ni P02–P10.
- `python3 -B -m testing.prospective_capture_paged.capture`: plan cerrado sin ejecución funcional.
- `--capture P01` requiere autorización humana **posterior I74** y `docs/validation/D5-I74-capture-authorization.json`. Aprobar I73 no autoriza crear ese archivo ni ejecutar P01. No se crea en I73.

Schema futuro `d5.paged-capture-authority.v1`, claves exactas `schema/phase/scopes/registry_sha256/capture_inputs`, fase `I74_EXPLICITLY_APPROVED`, scopes exactamente `["P01"]`. Requiere pins de componentes/registro y evidencia I69–I73; el seal I73 y todas sus artifacts deben estar incluidos. Es una puerta de coherencia, no atestación independiente o autorización humana por controlar código/manifest.

Destino exclusivo futuro `docs/validation/D5-I74-P01/` y copia fija hermana `D5-I74-P01-launch.json`, sin overwrite. OWNER, READY/RELEASE con PID/PGID/canales/directorio correlacionados. El worker sólo recibe descriptores y scope fijo, no módulos o paths arbitrarios. Los descendientes ajenos o no confirmados bloquean la captura.

131.072 eventos/campaña, 2.048/test, 4KiB/evento; hasta32 páginas JSON de2MiB y64MiB acumulados. Raw/índice/contexto/copia launcher ≤12MiB cada uno; paquete ≤112MiB+4KiB.900s externos, límites menores del runner/hijo/hook intactos. Inputs y lectura de evidencia tienen contadores separados y acumulativos. No capacidad probada para las244 ocurrencias que I71 no alcanzó.

Sólo página actual y resúmenes acotados, rangos de frame globales y secuencias densas; verificación de hashes/bytes/envelopes/lifecycle y conjunto exacto. Constructor observado tras retorno normal: argumentos run_id/store_id/role, tipados como declaración del padre, nunca head durable o medición del hijo. N/A de dominio sólo para cinco controles; DF07/DF43 siguen negativos de dominio y exigen esa declaración. Los demás tests conservan requisitos anteriores.

PG64 incluye productores/procesos propios sintéticos, controles de límite real131072, instrumentación/restauración y rechazo de metadata incompleta. No demuestra compatibilidad funcional con Python321. Conservar I71 bloqueado y P02–P10 pendientes de suficiencia. P0 y81/3; D5 global/G01–G07/GI globales abiertos. Sin publicación.
