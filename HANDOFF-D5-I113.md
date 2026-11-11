# Handoff — continuar hacia el cierre de D5 después de I113

Fecha: **2026-11-10**, Europe/Madrid. Petición humana: «crea un handoff y sigamos trabajando en una nueva sesión, queremos cerrar D5».

**Punto de partida:** las cotas documentales de eventos cubren321 pruebas/12 grupos y dan **E_global<=30129**, frente a131072. Frames de raíz<=321 frente a4096. Son envolventes condicionales por fuente, **sin nueva ejecución ni certificado conjunto de capacidad**. Referencias/bytes siguen pendientes y no existe captura P01 completa válida. D5/H07/G01–G07 siguen OPEN.

## Arranque de la sesión nueva

1. Usar este mismo proyecto y checkout local: `/home/chololo/Documents/Codex/weekly-ai-work-planner`. Buscar instrucciones locales, verificar Git/HEAD/árbol y conservar cambios ajenos. No reset, clean, stash, checkout o worktree que pierda documentos no rastreados.
2. Verificar [integridad de este handoff](docs/validation/D5-I113-handoff-integrity.json), los13 documentos locales I111–I113 y los sellos anteriores. El handoff y su sello son dos adiciones locales posteriores; no pertenecen al commit publicado.
3. Leer [I113: cota global de eventos](docs/design/D5-I113-GLOBAL-EVENT-SOURCE-ENVELOPE.md), [desglose Drive y tramos exteriores](docs/validation/D5-I113-drive-global-event-bounds.json), [registro321/321](docs/validation/D5-I113-global-event-bound-coverage.json) e [integridad I113](docs/validation/D5-I113-integrity.json).
4. Para la siguiente tarea, leer [contrato de capacidad I94](docs/design/D5-I94-CAPACITY-CONTRACT-DESIGN.md), [revisión I94](docs/design/D5-I94-CAPACITY-CONTRACT-REVIEW.md), [MRO/charging I96](docs/validation/D5-I96-source-capacity-review.json), [Reader I96](docs/validation/D5-I96-reader-envelope.json), [cota inferior R I97](docs/validation/D5-I97-reference-lower-bound.json) y [otros recursos I97](docs/validation/D5-I97-resource-bounds.json).
5. Leer [estado funcional y24 recursos I108](docs/validation/D5-I108-global-capacity-functional-readiness.json), [resultados de captura I92](docs/validation/D5-I92-results.json), [componente de capacidad I95](docs/validation/D5-I95-results.json) y [hoja de ruta/obligaciones globales](docs/design/D5-AFTER-I86-CLOSURE-ROADMAP.md).
6. **Continuar trabajando en referencias y bytes.** No volver a empezar el recuento321/321 como si estuviera pendiente. Si aparece un error de aplicabilidad o de una cota, documentar la corrección en un corte nuevo, conservando sellos históricos.

El handoff I84 anterior es histórico: sus propuestas I85/I86 ya fueron decididas y ejecutadas en los alcances siguientes. No volver a presentar I84 como próxima decisión ni usar la autorización consumida I92 para otra captura. La instrucción antigua de no crear chat automáticamente se refería a aquel traslado; la petición actual sí solicita continuar en una sesión nueva.

## Git y archivos que deben viajar juntos

Repositorio: `https://github.com/isidorotrevino/weekly-ai-work-planner`, rama `main`.

| SHA | Alcance | Publicación comprobada |
|---|---|---|
| `b22bc4d9189896c12f35c648cf47a93937b76b58` |146 archivos I85–I103|Push/ls-remote verificados en la sesión anterior|
| **`50c49678568bae2abeefbe5fec0285f26c628283`** |31 documentos I104–I110|Push origin/main y SHA remoto verificados al realizarse; HEAD local comprobado al crear este handoff|

[Contexto de publicación I111](docs/validation/D5-I111-prior-publication-context.json) conserva hashes,31 archivos/1369545 bytes y la petición «haz git commit y push y sigue». **No se ha consultado de nuevo el remoto el2026-11-10**: no presentar la comprobación histórica como verificación de red actual.

Al crear este handoff, no hay cambios tracked ni staged; hay13 archivos no rastreados I111–I113:3 diseños Markdown,3 registros de cobertura,3 sellos,3 revisiones y1 contexto de publicación. El sello del handoff enumera rutas/hash exactos. Se añaden después este Markdown y su sello, para un total esperado15 no rastreados. No hay código de producto nuevo.

La publicación anterior está completa. Esta petición no ejecuta otro commit/push; conservar todo local para continuar. Los flags históricos `publication_authorized=false` no se reescriben: el contexto posterior registra la autorización efectiva de cada publicación. La siguiente sesión debe usar **el checkout local**, porque un worktree nuevo no copiaría estos archivos.

Los generadores usados en `/tmp` eran scratch y **ya no están disponibles**. No depender de ellos ni regenerar paquetes sellados para continuar. Los JSON conservan términos, anclas, inventarios AST, cuerpos/hash stdlib y desglose suficiente para revisar las cuentas.

## Evidencia y decisiones ya realizadas

- I83/CT96 es evidencia sellada de componentes, no compatibilidad funcional P01. I84 fue el diseño parental DI07 y15 políticas; la aprobación posterior permitió I85/PR96,96/96 PASS sólo componentes.
- I86: una captura P01 autorizada, **INVALID_CAPTURE tras3/321** por identidades/enlaces. I88/DW24 validó24 componentes de dominio. I89: otra captura autorizada, **INVALID_CAPTURE tras8/321**, por `COMMAND_HEADER_INVALID`/retry_tick nullable.
- I91/NS12 validó12 componentes de selectores contextuales. I92: una captura autorizada, **INVALID_CAPTURE tras13/321**,1/12 grupos, por `REFERENCE_BUDGET`; contador retenido16393 frente a16384. No se conoce el primer wrapper/asignación fallidos.13 raw PASS no acreditan P01 ni el frame final completo.
- I93/I94 prepararon diseño de capacidad y revisión numérica justificada; I95/CB32 validó32 componentes independientes, **sin adaptar el perfil funcional original** y con capacidad P01 `NOT_ESTABLISHED`.
- I96–I113 fueron revisión documental/AST de fuentes y evidencia existente, sin importar producto/runners ni ejecutar suites/campañas. I86/I89/I92 no se suman, reanudan, fusionan o reconstruyen. **IR03 sigue NOT_READY**.

## Cotas actuales y advertencias de composición

[I111](docs/design/D5-I111-OFFLINE-GLOBAL-EVENT-BOUNDS.md) alcanzó174/321 y28471 eventos; [I112](docs/design/D5-I112-VOLATILE-RACE-GLOBAL-EVENT-BOUNDS.md)291/321 y29565; I113 añadió30 Drive y564 para **30129**. Los321 IDs son distintos. El registro acumulado enlaza la revisión que justifica cada raíz; no sumar otra vez helpers I98/I100 ni prefijos anteriores.

Las cotas son para la ruta original completa PASS con observación válida y fuentes/bindings/MRO exactos, sin nuevos hooks/importers/tipos. No predicen que el perfil actual logre observar esa ruta. I113 acota discovery/cola de runner/finalización por0 eventos adicionales **bajo esas condiciones**; esas fases siguen gastando referencias, bytes, IO, CPU y Reader. Los constructores/snapshots Drive se sobreestiman expresamente donde corresponde. No contar los Store del hijo como observers del padre: no se instrumentan hijos.

**Unidades:** `events_campaign=131072`, `events_test=2048`, `refs=16384`, `frames=4096`. Las alusiones antiguas I105–I107 a16384 al comparar subtotales de eventos fueron aclaradas en I108; no son la cuota global de eventos. Los321 frames no acotan subcasos/contextos/owners/grupos/referencias. Los bytes no se deducen del mero número de eventos.

MRO correcto: selectors.Recorder → selectors.BaseRecorder → late.Recorder → typed.Recorder → prospective_capture.Recorder. **paged.Recorder no pertenece a ese MRO**. State: DomainState → ParentalState → CausalState. I96 localiza38 sitios de charging,30 activos/condicionales y8 inactivos; no sumar las copias inactivas.

I97 mantiene **R>=19037>16384** para la representación original. Es una cota inferior conservadora, no cuota suficiente ni reconstrucción de I92. La explicación de la exclusión de DF26/DR29 fue corregida en I98: no era Try; el extractor rechazaba el loop por Return en bad anidado. Los archivos sellados I97 permanecen intactos y la cota inferior sigue válida.

I96 proporciona calendarios Reader normales originales, con exclusiones: no garantizan el alcance de autoridades/perfiles futuros. No convertir inputs documentales en runtime ejecutado, no unir presupuestos Reader distintos ni resetear antes/después/autoridad. Mantener bytes/filas/eventos4096,32 páginas de2MiB/64MiB,12MiB raw/sidecar/contexto/launcher,37 miembros/112MiB+4KiB,valor16MiB,Reader128MiB únicos/256MiB leídos por ámbito,depth32,string4096,20s espera/900s campaña. No aplicar cambios al contrato actual.

## Próximo trabajo concreto

El siguiente corte libre es **I114**, si no existe al arrancar; comprobar antes de crear archivos.

1. Resolver por fuente `R=Σ(q_i*N_i)` para los30 sitios activos I96: owners/identidades/declaraciones, membresías de frame, refs de claves/contextos/subcasos/hilos, enlaces/retained oracles, grupos/witnesses, mensajes/exit/DI07, late bindings y páginas. Empezar por sitios fijos/acotables desde321 frames y los términos source ya retenidos; no suponer desconocidos=0 ni inferir multiplicidad transitiva del número de loops.
2. Conservar todos los punteros/cargas semánticas. Dos estructuras que retienen el mismo puntero siguen siendo dos referencias; interning/compresión de JSON no las elimina. No resets, muestreo, truncado, deduplicación de evidencia ni omisión de witnesses/autoridad para caber.
3. Acotar tamaños de valores/operandos, filas, eventos, tablas, páginas, raw/sidecar/contexto/launcher y paquete; componer conjuntamente las24 cuotas y calendarios Reader. Una cota superior suelta puede superar un techo sin demostrar exceso real; no convertirla en medición. No usar el prefijo13/321 como extrapolación.
4. Si los recursos están resueltos, preparar **propuesta concreta y revisable** de contrato/perfil/namespace/registro nuevos, cuotas justificadas, charging atómico y matriz sintética NOT_RUN. Mantener desconocidos/bloqueos explícitos. No implementar sólo porque se terminó el diseño.
5. Después, obtener las decisiones separadas requeridas para implementación/componentes y una captura funcional nueva con pins/destino nuevos,321 tests/12 grupos,900s externos, sin reintentos ni publicación implícita. No reutilizar I92. Antes de pedir autorización, terminar la propuesta/documentos que permitan revisar el alcance concreto.
6. Sólo tras captura completa válida procede proponer revisión IR03, suficiencia global y eventual publicación/aceptación global con sus decisiones propias. No anunciar cierre por haber resuelto capacidad o por PASS de componentes.

## Perímetro de cierre que no puede cambiarse tácitamente

Conservar **P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial**. D1–D4 cerrados, hito local I1–I20/A52 aceptado, histórico30/35 sin promoción. D5 global/H07/G01–G07 y GI33/34/38/39/40 siguen abiertos. No degradar obligaciones para fabricar cierre ni trasladarlas a D6.

Las obligaciones **GI06/GI12/GI18/GI24/GI30/GI36/GI42** conservan sus requisitos de versiones/corpus/entorno/evidencia real o revisión/aceptación humana en la hoja de ruta. Las restricciones actuales **no autorizan** esos accesos reales: cuando el trabajo sintético/documental esté suficientemente preparado, presentar las decisiones concretas pendientes, sin tratar los fixtures como sustitutos. No se puede declarar D5 global cerrado aceptando otro hito parcial.

Sin proveedores, credenciales o corpus reales; sin consumo/reservas, activación, promoción, despliegue, SQL/Java/Docker nuevos ni D6. Sin inspección/limpieza operativa de `dev/run_data/D4`. No deducir persistencia, recuperación integrada o fsync nativo de PASS aislados, hashes o exit0. Publicaciones futuras y captura funcional nueva requieren decisiones propias. No pedir otra vez aprobación de actos ya consumados; sólo de nuevos alcances concretos cuando estén preparados.

## Prompt de continuidad

> Lee HANDOFF-D5-I113.md y sus documentos enlazados. Verifica Git/HEAD y conserva los archivos locales I111–I113, este handoff, sus sellos y cambios ajenos. Continúa hacia cerrar D5 con el trabajo autorizado de referencias y bytes/capacidad conjunta: I113 ya acota por fuente321/321 tests y E_global<=30129/131072; no es evidencia funcional ni certificado completo. R>=19037>16384 sigue bloqueando la representación original; resolver los30 sitios activos I96 y los recursos restantes sin inventar cuotas, omitir evidencia o ejecutar producto/runners. I86/I89/I92 siguen INVALID_CAPTURE; IR03 NOT_READY. No implementar perfiles, cambiar cuotas, ejecutar componentes/capturas ni publicar sin sus decisiones concretas separadas. Conserva P0,83/1, UI04.1 parcial, D1–D4 cerrados, I1–I20/A52 aceptado y D5/H07/G01–G07/GI globales abiertos. Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue, D6 o inspección/limpieza operativa dev/run_data/D4. Las7 obligaciones reales/humanas no se sustituyen por fixtures. Progresa autónomamente en el análisis pendiente y prepara propuestas revisables antes de pedir nuevas autorizaciones. Responde en español.
