# I88 — laboratorio de witnesses de dominio

Fecha: 2026-10-27, Europe/Madrid; HEAD base 7ff4748. La respuesta expresa **A** del
usuario posterior a la presentación de I87 aprueba su diseño y autoriza sólo el
perfil/registro nuevos y DW01–DW24 sintéticos bajo 300 s externos. No autoriza
captura I89 ni publicaciones. I87 e I86 conservan su estado/evidencia históricos.

Se crea `testing/prospective_capture_domains` con cinco archivos y el registro
`D5-DOMAIN-CAPTURE-REGISTRY.json`. Los esquemas exactos de grupo, retained-oracle,
call, link y cabecera observada quedan fijados en el registro antes de DW24.
El normal es d5.domain-sidecar.v1; el fallo d5.domain-worker-failure.v1. La base
parental se copia desde fuente pinneada; helpers puros previos se reutilizan por
sus imports existentes, sin cambiar sus globals, fuentes, funciones o registros.

Los grupos tienen la clave completa de contexto y run/store/role, con witnesses
ordenados sin duplicados y autoridades cerradas. No se fusionan objetos, estados
o heads. El mismo objeto no cambia de identidad; otro frame/subcaso/hilo no hereda
el grupo. El oráculo retiene el conjunto completo de witnesses conocidos hasta su
terminal original. El lector exige evidencia previa de cada uno por construcción
o snapshot observado, no sólo una fila declarada por el writer. Construcción no
prueba head, estado o independencia. Un enlace de recibo requiere además igualdad
de command/request/seq y head/commit observados; múltiples llamadas compatibles
bloquean la unicidad exigida, sin elegir la primera ni descartar las restantes.

DW05 reproduce el rechazo del selector heredado copiado ante dos objetos nuevos
de la misma identidad; DW12 ejercita un recorder completo con reapertura y oráculo
sintéticos. Las pruebas del lector incluyen pertenencias sin evidencia, huérfanos,
duplicados, ciclos y contexto incompatible. DW23 usa un productor spawn nuevo y
el protocolo parental estilo DI07, sin ejecutar el DI07 histórico. El poll/join de
las pruebas pertenece a su propio harness sintético, no a nuevos observers de dominio.

Se conservan las cuotas I87 exactas; no CALL_START extra, muestreo, truncado o reset
de contadores para caber. Las tablas y cabeceras viven en el mismo sidecar. El Reader
de preservación acumula inputs antes/después y fuente por caso; se distingue de las
lecturas unitarias/stdlib y no representa el futuro scope runtime. Los pins
funcionales futuros se medirán de nuevo antes de una decisión I89.

El máximo resultado es componente validado pendiente de compatibilidad P01 y
suficiencia. Cualquier incompatibilidad de API/oráculo/presupuesto se conserva y se
presenta antes de ampliar o repetir. I89 requiere otra decisión expresa, autoridad
y destino exclusivos; no se crean durante I88. No reejecutar CT96/PR96/DF03/P01,
P02–P10, I38/I67, SQL/Java/Docker o suites históricas por este incremento.

P0;83/1,UI04.1 parcial; D1–D4 cerrados, I1–I20/A52 aceptado,30/35 sin promoción,
D5 global/H07/G01–G07/GI globales abiertos. Sin inferir persistencia/recuperación
integrada desde PASS aislados; sin proveedores/credenciales/corpus reales,
consumo/reservas, activación, promoción, despliegue o D6. Sin commit/push.
