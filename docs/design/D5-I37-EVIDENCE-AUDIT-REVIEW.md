# D5 I37 — matriz de auditoría GI33/GI34

Fecha: **2026-10-23**, Europe/Madrid.
[Contrato](D5-I37-EVIDENCE-AUDIT-DESIGN.md) ·
[Decisión de alcance](D5-I37-NEXT-CUT-SCOPE.md).
**EA01–EA36: DESIGN_NOT_EXECUTED; cero pruebas nuevas ejecutadas.**

English: proposed auditor acceptance matrix; fixture mutations exercise the
auditor, not the historical TASK/relational campaigns or SQL targets.

| ID | Criterio | Entrada o variación | Oráculo exigido |
|---|---|---|---|
| EA01 | GI33 | Registro fijo y campaña válida | Commit completo/path/hash/schema/target anclados; dimensiones separadas; no aceptación global o autoridad operacional |
| EA02 | GI33 | Bytes históricos alterados | MISMATCH aunque el JSON interno y sus hashes sean autoconsistentes; no actualizar registro para aprobar |
| EA03 | GI33 | Commit/blob ausente o repositorio incompleto | UNAVAILABLE/UNDETERMINED, salida no exitosa; sin HEAD alternativo, fetch, checkout o red |
| EA04 | GI33 | Input runtime actual modificado | Histórico intacto, recorded_files_now CHANGED y applicability STALE; path/hash/código saneados |
| EA05 | GI33 | Input actual eliminado | MISSING y discovery REMOVED cuando corresponda; sin fallback a histórico como archivo actual |
| EA06 | GI33 | Nuevo .py/fixture/contrato en namespace | ADDED y STALE aunque todos los hashes previos coincidan; incluir no tracked; parametrizar reglas I34/I36 |
| EA07 | GI33 | Cambio documental aislado | Hallazgo documental separado; runtime no se invalida automáticamente; informe histórico no se reescribe |
| EA08 | GI33 | Nuevos paths exactos del auditor fuera de discovery | No alteran conjunto I34/I36; inputs propios sí inventariados; nueva entrada dentro de discovery no se excluye por ser auditoría |
| EA09 | GI33 | Runner o regla de selección cambiados | Hash detectado y STALE; no importar o ejecutar runner para aprender reglas nuevas |
| EA10 | GI33 | Python/plataforma distintos o ausentes | DIFFERENT→STALE, ausente→UNDETERMINED; versión declarada no acredita fsync/API/CLI/proveedor real |
| EA11 | GI33 | Perfil/schema/config/capacidad sin referencia | NOT_RECORDED explícito; sin valor inventado, import o equivalencia de API externa; bytes embebidos ligados a inputs |
| EA12 | GI34 | PASS/grupos/cuentas consistentes | Grupos partición exacta, nuevos/regresión coherentes; status funcional legado conservado sin llamarlo resultado de auditoría |
| EA13 | GI34 | Duplicados, IDs vacíos, grupos solapados o cuentas booleanas | INCONSISTENT/INVALID según schema; no deduplicar para ocultar exceso o error |
| EA14 | GI34 | Failures/errors/skips o status incompatibles | Contradicción detectada; resultado histórico no PASS no genera pruebas exitosas ficticias |
| EA15 | GI33/GI34 | DF/DR ausente, desconocido, vacío o ID no PASS | Cobertura declarada inconsistente; comprobar exactamente 48 DF y 40 DR por adapter |
| EA16 | GI33/GI34 | Mismo test cubre varias filas | Referencia permitida, cuenta de IDs distintos estable; número de filas no incrementa pruebas |
| EA17 | GI33/GI34 | Mapas UI base/expansión I34 y R I36 | UI01–UI40 inventariadas con modalidad, mapa o pendiente; UI25/UI34 R no atribuidas a T; UI sin mapa no recibe PASS implícito |
| EA18 | GI33/GI34 | Suma de campañas y subcasos | 281 y 321 se muestran por campaña con intersección; nunca 602 nuevas, ni raíces/procesos/oráculos como tests |
| EA19 | GI34 | Cierres D3/D4 y A52 válidos | Verificar campos de hashes admitidos, canónicos/evidencia/referencias y targets; HISTORICAL_NOT_RERUN separado de Python |
| EA20 | GI34 | Falta/cambio en input o target histórico | Hallazgo exacto en su dimensión/target; no reejecutar SQL ni equiparar D1/D2/V30/dev por nombres |
| EA21 | GI34 | D1/D2 sin manifiesto homogéneo o referencia ausente | Límite explícito NOT_RECORDED; no crear cierres, marcar reapertura o afirmar inventario exhaustivo |
| EA22 | GI33 | I34/I36 sin salida bruta anclada | raw_binding NOT_RECORDED visible; no leer /tmp, reconstruir raw o confundir reejecución con original |
| EA23 | GI33/GI34 | Paquete sintético con raw/registrado concordantes | MATCH solo para campos comunes/normalizaciones enumeradas; enriquecimiento documental permitido no altera runtime |
| EA24 | GI33/GI34 | Raw contradice registrado o añade campo desconocido | MISMATCH/INVALID; no ignorar divergencia; orden de claves irrelevante, duplicados rechazados antes de comparar |
| EA25 | GI33 | JSON duplicado/truncado/no finito/schema incorrecto | INVALID y exit 2, sin volcar valores o traceback privado; campos extras no se aceptan silenciosamente |
| EA26 | GI33/GI40 | Path absoluto/traversal/URL/controles/privado | Rechazo antes de lectura; sin abrir .env, corpus, dev/run_data/D4 operativo o enlaces arbitrarios |
| EA27 | GI33/GI40 | Symlink intermedio/final, FIFO o dispositivo | INVALID antes de leer destino o bloquear en FIFO; también modos Git no regulares; sin seguir enlaces |
| EA28 | GI33 | Mutación durante hash o discovery | UNSTABLE_SNAPSHOT/UNDETERMINED; controles coordinados por harness, sin sleeps como oráculo ni mezcla de reintentos |
| EA29 | GI33/GI40 | Límites de archivos/bytes/paths/IDs/mapas/JSON | Bloqueo explícito antes de exceso; presupuestos reducidos etiquetados, no prueba de todos los máximos |
| EA30 | GI40 | Git excede tiempo/presupuesto o devuelve error | Salida no exitosa saneada, hijo propio terminado/esperado; no stderr arbitrario o conclusión parcial confirmada |
| EA31 | GI33/GI40 | Datos inválidos con marcadores sensibles | Salida no contiene valores fuente/credenciales/home/temporales; solo paths públicos/códigos/hashes/versiones/cuentas permitidos |
| EA32 | GI40 | Auditoría sobre checkout quieto | Bytes Git/index/config/archivos de entrada conservados; sin escritura/cache/limpieza o ejecución de módulos de campaña |
| EA33 | GI40 | Fixtures negativas y fallos del harness | Solo temporales/hijos propios limpiados/terminados; sentinel hermano intacto; cero operaciones/red/consumo/reservas/activación |
| EA34 | GI33/GI34 | Combinaciones de estados y exits | Precedencia INVALID>STALE>UNDETERMINED>CURRENT_RECORDED_SCOPE; exits 2/1/0 coherentes; raw legado ausente visible sin falsear ejecución |
| EA35 | GI33/GI34/GI40 | Auditoría del repositorio real de lectura | Informe de hallazgos esperado independiente, I34 no forzado a CURRENT ante ampliación I36; 78+7 I36 verificados si bytes siguen iguales; sin campaña T/R/SQL nueva |
| EA36 | GI33/GI34/GI40 | Informe propio final y exclusiones | Inputs/herramienta/registro/tests/resultados propios ligados, mapa EA a IDs ejecutados y regresiones separadas; REVIEW_PENDING, P0/D1–D4/A52/D5/G01–G07 preservados |

## Estrategia de validación propuesta

Usar pequeños repositorios Git locales creados por el harness, paquetes sintéticos
con oráculos construidos explícitamente y mutaciones independientes del auditor.
No tomar la propia salida del auditor como expected. Parametrizar paths, campos,
presupuestos y adapters; publicar subcasos cubiertos sin sumarlos como nuevos tests.
Los casos de carrera/timeout usan sincronización y procesos locales propios.

EA19/EA20 verifican preservación por hash y metadatos; no ejecutan SQL/Java ni
modifican D1–D4. EA35 lee solo entradas públicas permitidas del checkout actual y
no hace que una campaña histórica parezca ejecutada ahora. Esperar hallazgos por
ampliaciones posteriores es un éxito de detección, no un permiso para rebaselinar.

La implementación futura registrará por campaña los estados esperados y observados,
tests propios realmente ejecutados, inputs y recursos/limpieza. Ninguna fila
acredita por sí misma suficiencia global de GI33/GI34 o recuperación integrada.

## Decisión pendiente

**A:** aprobar contrato I37 y autorizar implementación/validación del auditor,
registro fijo y EA01–EA36, con lectura local y sin reejecutar campañas funcionales.
**B:** aprobar solo el diseño, sin implementar. **C:** pedir ajustes al contrato.
P0 y todas las exclusiones permanecen; publicar exige SHA concreto por separado.
