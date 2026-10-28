# I90 — política cerrada para retry_tick nullable

Fecha: 2026-10-27, Europe/Madrid. **PREPARED_FOR_REVIEW, DESIGN_ONLY**.
[Intento I89](../validation/D5-I89-results.md) ·
[Matriz NS01–NS12](D5-I90-NULLABLE-SELECTOR-REVIEW.md) ·
[Pins y contrato estructurado](../validation/D5-I90-design-review.json).

I89 consumió su autorización de una captura P01 sin reintentos. Esta preparación
presenta el ajuste antes de ampliar/repetir; no implementa I91 ni autoriza I92.
I86/I88/I89 y toda la historia permanecen byte a byte.

## Hallazgo y alcance

La fuente T/R permite retry_tick=None en pruebas remotas de EXECUTE. El selector
heredado exige int exacto 0..1023 para todo retry_tick seleccionado. I89 registra
COMMAND_HEADER_INVALID y una llamada sin terminal C1087 en la fase RESULT de DF08;
no retiene el retorno que falló. Esa incompatibilidad por fuente debe reproducirse
con clases y datos sintéticos nuevos, sin reconstruir valores ausentes de I89 ni
convertir el raw PASS de 8 tests en una captura completa.

Se propone **sólo** permitir None observado para el campo retry_tick de las formas
remotas cerradas T/R, con contexto acreditado. No permitir None para todos los
enteros ni para un campo sólo porque se llame retry_tick. Mantener el rango int
0..1023 y rechazar bool, float, strings y oversize según las cuotas vigentes.
No interpretar null como cero, infinito, cuota, tiempo observado o prueba de retry.

## Políticas nuevas propuestas

- **NP00_STRICT**: comportamiento previo. retry_tick, si es selector admisible,
  requiere int exacto; no hay excepción nullable por defecto.
- **NP01_T_REMOTE_PROOF**: schema original d5.durable-remote-proof.v1.
- **NP02_R_REMOTE_PROOF**: schema original d5.relational-remote-proof.v1.

NP01/NP02 exigen dict builtin con exactamente las trece claves de fuente:
`schema,run_id,store_id,ticket,request_hash,creation_key,manifest_hash,status,
remote_id,applied_version,payload_hash,retry_tick,code`. La excepción sólo afecta a
retry_tick; el resto conserva sus tipos/alfabetos/formas y guardas de fuente ya
permitidas. Un proof de forma desconocida no enseña una política nueva al collector.

La selección debe provenir del contexto original ya observado y pinneado:

1. Para recibo Store del padre, llamada Store.transact EXECUTE/CLOSE, dominio
   REMOTE y familia T/R del frame; run/store de la prueba coinciden con el grupo/
   witness acreditado. No seleccionar sólo por un schema declarado en el payload.
2. Para el último recibo de un oráculo remoto original, head/rol/familia y operación
   retenidos compatibles, sin nueva llamada a independent ni lectura de dominio.
3. Para resultado remoto de hijo, política CP07/CP13 registrada y run/store
   compatibles con la identidad remota del protocolo parental original. Sigue
   REMOTE_RESULT_WITHOUT_STORE_RECEIPT: receipt y command_id siguen ausentes.

Si el contexto requerido no existe o es ambiguo, no activar la excepción. Ningún
scope CLIENT, Drive, control sin Store, mensaje desconocido o policy sólo textual
puede obtenerla. Una llamada/retorno observado mantiene su autoridad; source,
ParentIntentID, send_id, ticket, ACK/READY/exit0 no se convierten en command_id.

## Representación y lector

Distinguir **clave presente con None** de **clave ausente**. Bajo NP01/NP02 se
retiene retry_tick:null observado; no se inserta un null por ausencia. No eliminar
el campo, truncar, coercionar, recomputar o rellenar con valores de otro retorno.
Un proof al que falta la clave no satisface la forma exacta requerida.

El registro nuevo fijaría los tres NP y sus contextos, anclas, tipos y claves antes
de ejecutar NS12. Se versionaría la proyección Store a
`d5.scoped-store-receipt-projection.v1`, añadiendo metadata_policy_ref al conjunto
cerrado de campos, con result_digest completo del retorno original y metadata
permitida. Las políticas base usarían NP00_STRICT. El header normalizado de hijo
pasaría a `d5.scoped-child-header-observation.v1`, con selector_policy_ref; los
campos previos y las quince políticas CP01–CP15 conservarían sus obligaciones.

El lector exige referencias NP cerradas y contexto/familia/rol/run/store/acción
compatibles ya presentes en llamadas, grupos y protocolos. No acepta un null sólo
por etiqueta o hash. La representación no retiene el proof completo como payload
ni crea un oráculo independiente. El enlace comando/recibo/oráculo conserva
command/request/seq y commit/head; after_data_sha256 no es oracle.state_sha256.
Los grupos de witnesses I88 y las ausencias de identidad permanecen sin relajación.

Los errores y enlaces huérfanos C1087 de I89 permanecen en su expediente inválido:
no limpiar stacks, reparentar eventos, filtrar missing o reparar sidecars históricos.
Los negativos futuros conservan su primer error/diagnóstico y cleanup originales;
ninguna excepción nullable justifica omitir otros fallos.

## Archivos, cuotas y transición

I91 propuesto: nuevo namespace `testing/prospective_capture_selectors`, cinco
archivos, registro `D5-SELECTOR-CAPTURE-REGISTRY.json`, normal
`d5.selector-sidecar.v1` y fallo `d5.selector-worker-failure.v1`. No se crean en I90.
Base I88 por fuente pinneada/helpers puros, sin mutar fuentes, globals, funciones
o registros anteriores. No nuevos observers, actores, llamadas o canales: sólo
proyección/lector contextual de campos ya permitidos.

Cuotas heredadas exactas: 131072 eventos/campaña,2048/test,4096 bytes/fila/evento;
32 páginas de 2 MiB/64 MiB;12 MiB/canal,37 miembros/112 MiB+4 KiB;4096 frames,
16384 refs,depth32,string4096,16 MiB/valor con auxiliares; Reader128/256 MiB por
ámbito acumulado antes/después/autoridad. Sin CALL_START adicional, muestreo,
truncado, nuevos contadores paralelos o resets. El tamaño observado I89 no demuestra
capacidad para la campaña completa; si falla un límite, detener y presentar ajuste.

1. Si se aprueba I90, autorizar **I91 sólo NS01–NS12 sintéticos bajo 300 s externos**.
   Reproducir la incompatibilidad y comprobar la política nueva con datos propios;
   no importar producto, ejecutar DF08 o repetir P01/CT96/PR96/DW24/suites históricas.
2. Tras I91 válido, preparar y presentar pins/presupuesto y destino nuevos para
   **I92**, P01 completo 321/12 bajo 900 s. Requiere otra decisión expresa; no crear
   su autoridad/destino ahora ni reutilizar I89. No reanudar sólo los 313 pendientes.
3. Sólo un paquete completo válido permite revisar IR03 después. La suficiencia,
   publicación y aceptación global son separadas; ningún PASS cierra D5 por sí solo.

P0,83 SUPPORTS_BOUNDED/1 PARTIAL,UI04.1 parcial; D1–D4 cerrados e hito I1–I20/A52
aceptado,30/35 sin promoción; D5 global/H07/G01–G07/GI globales abiertos. Sin
proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción,
despliegue, SQL/Java/Docker nuevos o D6. Sin inspección/limpieza dev/run_data/D4.
