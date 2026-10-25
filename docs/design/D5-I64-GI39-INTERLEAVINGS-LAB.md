# D5 I64 — laboratorio de intercalados finitos GI39

Fecha: **2026-10-25**, Europe/Madrid. Base I63 `3934e51`.
[Contrato](D5-I63-GI39-INTERLEAVINGS-DESIGN.md) · [GX90](D5-I63-GI39-INTERLEAVINGS-REVIEW.md) · [Harness](../../testing/gi39_interleavings/README.md).

La selección A posterior a I63 aprueba implementar/validar GX90 y nueve regresiones independientes. Los flags de preparación de I63 permanecen como historia. No autoriza publicación ni cierre de UI26.2/UI27.2/UI34.3 o GI39/D5.

24 carreras locales APPLY/APPLY_BATCH distinguen mutación antes de lock y commit antes de mutación; diez carreras R previas a ISSUE verifican STALE_SELECTION tras separar CONFLICT_HEAD. En COMMIT_FIRST, el contender observa el lock mediante probe y pierde E vieja; una mutación nueva explícita usa HEAD fresca. T puede publicar BIND auxiliar al probar después la preparación de proyección, pero no prepara/acepta PROJECTION ni emite send bajo pins viejos. R prueba SELECT_TASKS por el recibo BATCH original sin reselección implícita.

44 casos intercalan mutación CLIENT dentro de Remote.execute real (CREATE/before_object y UPDATE/after_head para cada mutación). Ocho casos CREATE/after_head pierden P al volver al wrapper y requieren consulta explícita. Se conserva efecto histórico y vigencia STALE, sin rollback o segundo intento. Las generaciones ABA se observan en cada paso, aunque el valor final vuelva a A. No se llama ABA a REVOKE_OBSERVATION.

La preparación pública conserva I26/pin/bytes y revisiones T; registra B observacional antes de EVALUATION. R parte de lote de siete entidades, TASK0 seleccionada por cid/request exactos y relaciones explícitas. UPDATE aplica nueva fuente/base mediante la vía pública coherente aprobada en I61, con CREATE v1 y edición foreign v2 como preparación, efecto objetivo v3. Nunca se modifica producto o estado persistido directamente para sortear validaciones.

El raw liga actores, comandos/args/request/expected, M/send/ticket, READY/PREPARED/probe/ACK, recibos y firmas de generación/selección/data_hash, P/entidad/base/foreign y rechazos sin recibo. Lector de archivos y CLIENT/REMOTE públicos spawn concuerdan pasivamente. La persistencia observada tras actores con salida0 no se etiqueta como SIGKILL o recuperación integrada general.

Cuatro controles validan gates/releases/probe/EOF/salida normal/timeout, ownership y presupuestos/inventario/raw. El harness y RECORDS son propios; reutiliza helpers pinneados sin modificarlos. Las selecciones de desarrollo no se suman como tests adicionales de aceptación. Nueve regresiones usan runners históricos intactos y contextos/inputs separados, sin afirmar que descubren el directorio GX.

Presupuestos y límites I63 intactos: 4 hijos,20s espera,120s/caso,900s/campaña,256 eventos/caso,16KiB/evento,12MiB/raw. Sin nuevas fronteras crash/fsync, casos nativos, grooming real, auditor I38, SQL/Java/Docker o red. D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos; I62 conserva agregado78/6 y UI22.2 acotada T/R v1. H07, GI globales y D5 global/G01–G07 abiertos, sin promoción30/35→35/35. Los siete reales/humanos conservan puertas propias. P0: sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue o D6; sin inspección/limpieza operativa dev/run_data/D4. Sólo limpieza de raíces propias. Sin push.
