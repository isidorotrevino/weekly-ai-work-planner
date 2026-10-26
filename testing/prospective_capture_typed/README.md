# I76 — perfil tipado de captura P01

[Contrato I75](../../docs/design/D5-I75-TYPED-ADAPTER-DESIGN.md) y [matriz AT80](../../docs/design/D5-I75-TYPED-ADAPTER-REVIEW.md). Sólo stdlib y capturadores puros I70/I73, sin modificar sus fuentes ni registros.

- `python3 -B -m testing.prospective_capture_typed.run_typed_lab`: AT80 con clases, suites y procesos sintéticos nuevos; wrapper externo de 300 segundos.
- `python3 -B -m testing.prospective_capture_typed.capture`: plan sin ejecución funcional.
- `--capture P01`: exige autorización humana posterior I77 y manifiesto fijo `docs/validation/D5-I77-capture-authorization.json`. I76 no autoriza crearlo ni ejecutar Python321.

El futuro manifiesto tiene schema `d5.typed-capture-authority.v1`, claves exactas `schema/phase/scopes/registry_sha256/capture_inputs`, fase `I77_EXPLICITLY_APPROVED` y scopes `["P01"]`. Incluye pins de componentes, registro y evidencia I69–I76, con todos los artifacts del seal I76. Esta puerta verifica coherencia; no acredita autorización humana por sí sola. Destinos exclusivos `docs/validation/D5-I77-P01/` y copia hermana `D5-I77-P01-launch.json`, sin overwrite de I71/I74.

29 IDs admiten identidad Drive observada del retorno snapshot, separada de Store. DI28 sólo admite declaración UUID tras construcción normal del fixture en el padre, sin head. Cinco IDs/helpers/roles admiten Path exactos, clases e instancias exactas de las dos excepciones permitidas. La proyección TYPE_AND_ARGS_PROJECTION_NOT_FULL_EXCEPTION_OBJECT no representa el objeto completo. No se reevalúan comparaciones ni oráculos.

Path usa sólo conversión léxica stdlib verificada y HMAC-SHA256 con clave efímera por captura, sin publicar clave/ruta ni pasarla a hijos. Comparación sólo dentro de esa captura; el lector verifica formato y enlaces, sin recomputar rutas ocultas. Builtins conservan el digest original I70 byte por byte. Fuentes de clases y binding stdlib pinneados; ninguna clase de producto se importa en AT80.

Topes I72 intactos: 131072 eventos/campaña, 2048/test, 4KiB/evento; 32 páginas de 2MiB y 64MiB acumulados; raw/índice/contexto/launcher de 12MiB cada uno, paquete de 112MiB+4KiB; operandos de 16MiB. 900 segundos futuros, sin ampliar límites menores existentes. No capacidad funcional probada con Python321; AT80 no reejecuta PG64.

P0, 81/3 y UI01.2/UI04.1/UI09.2 parciales. I74 permanece BLOCKED, P02–P10 pendientes de suficiencia. D1–D4 cerrados e hito I1–I20 aceptado intactos; D5 global/H07/G01–G07 y GI globales abiertos. Sin publicación.
