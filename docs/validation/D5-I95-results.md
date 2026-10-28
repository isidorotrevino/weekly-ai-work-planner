# I95 — planificador y guard validados sólo en componentes

La respuesta expresa **A** aprueba I94 y autoriza únicamente I95 CB01–CB32
sintéticos bajo300s externos con límites actuales. Los documentos/sellos I94
conservan flags históricos. No se autoriza captura funcional, ampliación numérica
ni publicación. HEAD base `7ff47485109306f90ecc4eebc6a6b3f6ec597d99` intacto.

**32/32 PASS en0,21s externos** (0,132s internos), una ejecución, cero fallos,
errores o skips. Ocho hilos sintéticos propios terminados; ocho raíces propias
verificadas/retiradas y controles hermanos conservados. Cero procesos de dominio,
imports de producto/perfiles/tests/runners históricos o campañas funcionales.

[Raw CB32](D5-I95-tests-raw.json) · [Contexto externo](D5-I95-context.json) ·
[Resultados por caso](D5-I95-results.json) · [Integridad](D5-I95-integrity.json) ·
[Manifiesto](D5-CAPACITY-PLANNER-MANIFEST.json) ·
[Decisión y laboratorio](../design/D5-I95-CAPACITY-PLANNER-LAB.md).

El namespace nuevo prospective_capture_capacity contiene sólo planificador,
guard y laboratorio sintético. **No hay perfil de captura, worker o launcher**.
Las24 cuotas siguen exactas, refs16384. La reserva comprueba el bloque completo
antes de mutar contador/tablas/eventos del modelo; rechazar no deja un fragmento
nuevo. Ocho hilos compartieron un ledger:64 reservas únicas comprometidas y64
rechazos. Ni frame, tabla, hilo o página resetea el presupuesto. Dos punteros
iguales retenidos en campos diferentes se cuentan sin deduplicarlos por etiqueta.

Se verificaron retorno/excepción originales por identidad, sin mantener el lock
al ejecutar original/observer; primer diagnóstico, allowlist I78 copiada por valor,
sanitización de código desconocido, binding cambiado/restaurado y una salida
parcial real de12 bytes que no se reparó ni reintentó. El diagnóstico del nuevo
componente tiene scope/schema sintético y no modifica el canal del worker.

Los límites128/256MiB,112MiB y131072 eventos se verifican mediante descriptores de
planificación; no representan archivos o campañas funcionales de ese tamaño.
Se combinan con filas codificadas4096/4097 bytes, UTF8, página planificada exacta
2MiB con header/comas, transacciones retenidas y Reader real de archivos propios
con sublímites menores. El paquete válido a máximos individuales suma112MiB+36,
con4060 bytes de margen frente al contador global, probado por separado. Tres
escaneos máximos se rechazan por el Reader acumulado. No se recorta evidencia.

El certificado ausente/con UNKNOWN sigue NOT_ESTABLISHED. El modelo sintético
con cotas conocidas sólo alcanza CAPACITY_ESTABLISHED_SYNTHETIC_MODEL_ONLY y
nunca autoriza release. El coste mínimo del guard no sustituye el cómputo completo
de cada sitio P01. La herencia estática soportada es de una base y las cotas AST
locales no certifican multiplicidades transitivas. Un presupuesto favorable no
sana PENDING_CHILD_EXIT, oráculo/recibo ausentes ni políticas nullable/contexto.

**El P01 original sigue NOT_ESTABLISHED; no existe certificado numérico nuevo**.
No se conectó el guard a los wrappers antiguos ni se validó un retrofit de su
atomicidad. I86/I89/I92 permanecen inválidos, sin suma/reanudación ni repetición.
Una revisión numérica y perfil/registro de captura nuevos, componentes de ese
perfil y otra captura requerirán decisiones posteriores. IR03 sigue NOT_READY;
publicación y aceptación global separadas.

Se preservaron195 inputs del Reader documental:19.455.449 bytes únicos y
40.202.254 leídos bajo128/256MiB. Este ámbito incluye manifiesto, fuentes, sellos,
hashes por caso y finish; no representa todas las lecturas unitarias/stdlib/OS.
Todos los untracked previos y sellos I83–I94 permanecen byte a byte; árbol tracked
sin cambios, sin commit/push. El resultado está sellado como
CAPACITY_PLANNER_COMPONENT_VALIDATED_ORIGINAL_P01_NOT_ESTABLISHED.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL(UI04.1). D1–D4 cerrados e I1–I20/A52 aceptado,
30/35 sin promoción. D5 global/H07/G01–G07/GI33/34/38/39/40 OPEN. Sin proveedores,
credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue,
SQL/Java/Docker nuevos o D6. CB32 PASS no prueba persistencia/recuperación integrada,
independencia, fsync nativo o suficiencia funcional.
