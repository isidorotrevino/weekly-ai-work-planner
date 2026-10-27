# Handoff — continuar D5 después del diseño I84

Fecha: **2026-10-27**, Europe/Madrid. I83 implementado/validado sólo en componentes; **I84 es diseño preparado, no implementación**. P0; **83 SUPPORTS_BOUNDED /1 PARTIAL** (UI04.1). D5 global/H07/G01–G07 siguen abiertos.

## Inicio de la sesión nueva

1. Leer instrucciones locales y verificar Git/HEAD/árbol. Conservar cambios ajenos; no resetear ni asumir que este documento describe un HEAD posterior.
2. Leer [contrato I84](docs/design/D5-I84-PARENTAL-CAPTURE-DESIGN.md), [matriz PR01–PR96](docs/design/D5-I84-PARENTAL-CAPTURE-REVIEW.md), [JSON declarativo](docs/validation/D5-I84-design-review.json) e [integridad I84](docs/validation/D5-I84-integrity.json).
3. Leer [resultado I83](docs/validation/D5-I83-results.md), [JSON por caso](docs/validation/D5-I83-results.json), [raw CT96](docs/validation/D5-I83-tests-raw.json), [integridad](docs/validation/D5-I83-integrity.json) y [laboratorio](docs/design/D5-I83-CAUSAL-CAPTURE-LAB.md). No reejecutar CT96 o campañas por leer este handoff.
4. Para el origen de obligaciones, consultar [contrato I82](docs/design/D5-I82-CAUSAL-CAPTURE-DESIGN.md), [inventario118/esquemas](docs/validation/D5-I82-design-review.json) y [dictamen I81](docs/validation/D5-I81-results.md).
5. Presentar opciones para **aprobar I84 y autorizar I85** o ajustar sólo el diseño. La autorización vigente no incluye implementar I85 ni ejecutar PR96/P01. La próxima implementación necesita esa decisión concreta; no repetir el diseño como si no estuviera hecho.

## Git y publicación efectiva

Repositorio: `https://github.com/isidorotrevino/weekly-ai-work-planner`, rama `main`.

| Corte | SHA completo | Estado |
|---|---|---|
| I52, antigua punta publicada | `ce44158ebaa603d61c266fe106b0dfc068ff2c80` | Base remota anterior a la publicación actual |
| I82, diseño de captura causal | `63c9cd2ca460f57a2337cbb00b10bb51a9cb9a88` | Incluido en el push actual |
| I83, perfil causal/CT96 | `ed25961a401eb50de49102b9f1bd70495690a02d` | Incluido en el push actual |
| I84, diseño parental/PR96 | `ded2228bf4d9bb7dbf315281a340cad5730651d9` | **Publicado y verificado mediante ls-remote el 2026-10-27** |

El usuario primero eligió mantener todo local. Su petición posterior fue: «continúa, cuando termines haz git commit y push y luego crea un handoff para seguir en una sesión nueva». Esa petición sustituyó la preferencia de no publicar **para lo realizado y este handoff**. Se publicó sin force el rango de32 commits `ce44158..ded2228`; el remoto confirmó el SHA completo de I84. No hubo implementación ni campaña nueva.

Este handoff se crea después de ese push y se guarda/publica en un commit posterior. El SHA de su propio commit se consulta con `git log` para evitar una referencia autorreferente; verificar HEAD remoto al entrar. [Integridad del handoff](docs/validation/D5-I84-handoff-integrity.json) conserva su digest y la verificación del push de I84. No es autorización abierta para publicar futuros cambios I85/I86. Los textos históricos «sólo I52 publicado» o «sin autorización de publicación» describen sus bases anteriores y permanecen byte a byte.

```bash
git status --short --branch
git log -5 --oneline
git log -1 --format='%H %s' -- HANDOFF-D5-I84.md
git ls-remote origin refs/heads/main
```

No crear un chat nuevo automáticamente: se pidió un documento para continuar en otra sesión.

## Límites que deben conservarse

- D1–D4 cerrados y [D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado](docs/design/D5-LOCAL-SYNTHETIC-approved.md), sin alterar código, SQL, targets, manifiestos, evidencia o cierres. Histórico30/35 sin promoción.
- Agregado83/1; UI04.1 PARTIAL; UI01.2/UI09.2 mantienen soporte acotado I81. D5 global/H07/G01–G07 y GI33/GI34/GI38/GI39/GI40 globales OPEN. No crear cierre global por PASS aislados.
- P0: sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6. La publicación Git expresamente autorizada no concede operaciones de producto/proveedor.
- No inferir persistencia, recuperación integrada, independencia de oráculo o fsync nativo desde hashes, etiquetas, exit0 o suites sintéticas.
- No inspeccionar/limpiar dev/run_data/D4/Compose o recursos ajenos. Sólo cleanup de recursos propios del alcance autorizado.
- Contrato/matriz → autorización concreta de implementación/componentes → evidencia → autorización funcional separada → revisión de suficiencia. Publicación también separada. Decisiones en español con opciones, sin volver a pedir permisos ya concedidos para el mismo acto.

## Estado exacto de I83

Nuevo namespace [prospective_capture_causal](testing/prospective_capture_causal/README.md) y [registro fijo](docs/validation/D5-CAUSAL-CAPTURE-REGISTRY.json). CT01–CT96: **96/96 PASS** en la ejecución final sellada, wrapper externo300s;19 raíces propias y sentinels verificados/retirados; cuatro procesos sintéticos terminaron0,0,2,2. Cero imports de producto/runners históricos, campañas funcionales o suites antiguas. No reejecución de PF60/PG64/AT80/LB64. No se afirmó compatibilidad funcional P01.

I83 retiene resúmenes públicos de oráculos T/R con digest I70 y sidecar_pointer propio, separado de raw_pointer. Proyecta comandos/recibos, observa subcasos y protocolos parentales registrados; conserva límites y diagnóstico previos. Ledger mantiene primera fase/código y allowlist I78; error causal desconocido se sanitiza en diagnóstico, sin texto libre. Una escritura JSON; no reparar salida parcial.

Sus497 inputs quedaron preservados; el lector documental acumuló113.830.203 bytes únicos/235.352.502 leídos, dentro de128/256MiB. El sello I84 verificó503 inputs preservados,12 artifacts I83 y ausencia de cambios previos. Estos son ámbitos documentales; no convertir toda esa historia en inputs ejecutados por un worker futuro.

## Lo que diseña I84

Cuatro documentos nuevos, estado PREPARED_FOR_REVIEW. **PR01–PR96 siguen NOT_RUN**.37 anclas de repositorio, cinco bindings stdlib por AST, quince políticas de acción CP01–CP15, trece puntos de fuente. Ningún nuevo perfil/registro ejecutable ni autoridad/destino de captura creado.

### Registro directo DI07

`testing/D5/test_incremental_capture.py` crea su Process/Pipe directamente en `test_DI07_fresh_process_recovers_state_from_disk`, con target `child_snapshot`. No pasa por start/spawn registrados en I83. Es una carencia por fuente, no un fallo runtime nuevo observado. I83 conserva UNREGISTERED_CHILD_PROTOCOL_REQUIRED para ese caso.

La propuesta nueva observa **BaseContext.Pipe y BaseProcess.start** sólo en el frame/subcaso/hilo DI07 exacto y sobre tipos/fuentes/identidades pinneados. Fuera de ese selector se delega sin inspección. Pipe se observa después del retorno; pareja por objetos exactos. Antes de start se permite leer mínimamente `_target/_args/_kwargs/_popen` del SpawnProcess exacto: `_args` tuple len4; sólo índices1(run_id) y3(endpoint child); ignorar0(root) y2(scope), sin publicar, copiar, hashear ni abrirlos. Leer TestCase.lab y lab.run_id exactos para cotejo; nunca lab.root/scope.

El child endpoint debe coincidir por is con una pareja única del mismo contexto, target exactamente la función ya cargada y run_id coherente. start borra sus campos de argumentos al retornar: se conserva sólo vista mínima transitoria previa; registro exitoso después de retorno original None y Popen/pid ya producidos. No rebind/selección por orden/PID/fd/tiempo, ni actors/canales auxiliares. Máximo una pareja/start para el selector de fuente. Misma llamada, retorno/excepción y cleanup originales; fallo de instrumentación latcheado, parada entre tests.

Cadena propuesta: frame/input → subcaso → pareja → endpoint/target/start → conexión parental → snapshot del hijo → assertEqual/outcome originales, por digest de retorno completo y contexto compatible. Snapshot del padre es OWN_FIXTURE_SNAPSHOT; recibido del hijo es CHILD_PROTOCOL_RETURN. No wrappers dentro del hijo ni nuevo snapshot/oráculo. DI07 no requiere cid de comando para su snapshot; el avance previo del padre no presta su cid al hijo. Join/finish sólo leen escalar ya producido; pending no significa0 y el observer no hace poll/wait/is_alive/kill.

### Cabeceras de hijos y ausencias que deben permanecer

- mutate/raw_mutate/reconcile T/R: recibo Store original, con su cabecera/flags/selectores cerrados.
- advance Drive: recibo Drive original y commit_sha256; no equiparar version/head con seq/Store T/R.
- dispatch T/R: forma exacta send_id/ticket/receipt; proyectar recibo anidado **LAST_PUBLIC_RECEIPT_ONLY**, no todos los comandos internos. Sin búsqueda recursiva de claves.
- remote T/R devuelve resultado sin cabecera Store: REMOTE_RESULT_WITHOUT_STORE_RECEIPT y missing si se exige esa cabecera. No recomputar UUID5 desde fuente/ticket para suplir cid.
- snapshot T/R es summary de su schema; snapshot Drive tiene su schema propio. No convertirlos en oráculo independiente por etiqueta.
- initialize T devuelve None: GENESIS_NO_COMMAND_RECEIPT no prueba fsync/publicación desde exit0.
- cid explícito parental es REQUESTED_PARENT_COMMAND_ID/intención. Sólo recibo realmente emitido da ACTUAL_PROTOCOL_RECEIPT. ParentIntentID, send_id, ticket, READY/ACK/exit0 no son cid; ausencia CHILD_LOCAL_NOT_OBSERVED permanece. Ninguna política dispensa campos obligatorios con N/A genérico.

Puntos de fuente: los nueve I83 más after_issue,after_remote,after_query,before_result de Client T/R. Son EXPECTED_SOURCE_POINT, no gates medidos dentro del hijo. Negativo previo a publicar requiere protocolo real y oráculo no-efecto compatible; after_object no prueba ausencia de objetos huérfanos, prepared concurrente o puntos compuestos no garantizan no-efecto. after_data_sha256 del recibo se calcula antes de insertar el propio recibo y **no es** oracle.state_sha256.

### Perfil, límites y transición propuestos

I85 propuesto: nuevo namespace `testing/prospective_capture_parental` con cinco archivos, registro `D5-PARENTAL-CAPTURE-REGISTRY.json`, schemas parental-sidecar/parental-worker-failure. Tablas dentro del mismo sidecar; parental_registrations y header de mensaje/políticas versionados en JSON. No cambiar fuentes/globals/funciones/registros I70/I73/I76/I79/I83 ni producto/fixtures/hooks/runners. Helpers puros pueden reutilizarse por hash; no importar tests/labs antiguos. La regla DI07 I83 sólo se sustituye en perfil nuevo tras cadena completa; no filtrar otros missing/errores.

I85 sólo PR96 sintético bajo300s externos, **si se autoriza posteriormente**. No CT96 ni pruebas antiguas, P01/P02–P10, I38/I67, SQL/Java/Docker o producto/runners históricos. Cualquier incompatibilidad se conserva y se presenta antes de ampliar/repetir. PR96 no garantiza que una campaña321/12 quepa o resuelva UI04.1.

Todos los límites anteriores exactos:131072 eventos/campaña,2048/test,4096 bytes/evento/fila;32x2MiB páginas/64MiB acumulados;12MiB raw/sidecar/contexto/launcher,37 miembros y112MiB+4KiB;4096 frames,16384 refs,depth32,string4096,16MiB/valor contando hashes/encoding auxiliares. Reader128MiB únicos/256MiB leídos por ámbito, acumulado antes/después/autoridad sin resets. No CALL_START extra, muestreo o pérdida de evidencia para caber. Diagnóstico I78 cerrado4096 bytes, canal existente y primera fase/código conservados.

Base runtime específica propuesta:58.670.898 bytes conocidos, más contrato/registro/código/evidencia/sello nuevos que deberán medirse de nuevo. No unir automáticamente los503 históricos documentales al runtime ni llamarlos ejecutados.

**Numeración:** I84 ahora es este diseño. Los paths de antigua captura I84 de I83 siguen ausentes y su plan histórico no se reescribe. Tras I85 validado, I86 requeriría autorización nueva `D5-I86-capture-authorization.json`, schema d5.parental-capture-authority.v1, fase I86_EXPLICITLY_APPROVED, scopes=[P01], pins exactos y destino exclusivo nuevo `D5-I86-P01/`, launcher hermano `D5-I86-P01-launch.json`. No se crean ahora ni durante I85. Captura completa321/12, sin reanudar sólo DI07 o sumar paquetes anteriores; revisión IR03 posterior separada, sin cierre automático.

## Prompt listo para la sesión nueva

> Lee HANDOFF-D5-I84.md y sus documentos enlazados. Verifica Git y conserva los cambios ajenos. I84 es sólo diseño preparado: contrato parental DI07, quince políticas de hijos y PR01–PR96 NOT_RUN. I83/CT96 es evidencia de componentes sellada, no compatibilidad funcional P01. Conserva P0,83/1, UI04.1 parcial, D1–D4 cerrados, hito local I1–I20 aceptado y D5 global/H07/G01–G07 abiertos. Presenta opciones para aprobar I84 y autorizar I85 sólo con perfil/registro nuevos y PR96 sintético bajo300s, o ajustar sólo documentación. No implementes ni ejecutes campañas sin esa autorización. I86 funcional y publicaciones futuras requieren decisiones separadas. No deduzcas persistencia/recuperación integrada de PASS aislados. Sin proveedores/credenciales reales, consumo/reservas, activación, promoción, despliegue ni D6. Responde en español.
