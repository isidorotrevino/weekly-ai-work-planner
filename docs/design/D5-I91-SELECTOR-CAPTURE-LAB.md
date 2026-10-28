# I91 — autoridad y laboratorio de componentes NS12

La respuesta expresa A aprueba I90 y autoriza I91: perfil y registro nuevos,
NS01–NS12 sintéticos bajo límite externo300s. No incluye I92 funcional ni
publicación. La autorización se registra aquí sin reescribir el diseño histórico
I90, los sellos I88/I89, sus retornos ausentes ni la evidencia anterior.

Implementación: `testing/prospective_capture_selectors/` y
`docs/validation/D5-SELECTOR-CAPTURE-REGISTRY.json`. Herencia exacta de cuotas,
grupos/witnesses I88 y contrato parental. Los únicos cambios semánticos son las
políticas NP00/NP01/NP02 y las proyecciones versionadas/contextuales I90.

La matriz NS01–NS12 de I90 se verifica con datos/clases nuevos: reproducción del
rechazo heredado; recorder/reader completos T y R; límites de tipos/rangos;
ausencia/null y forma exacta; otros enteros estrictos; contextos incompatibles;
cabeceras/enlaces originales; protocolos CP07/CP13 sin inventar recibo; rechazo de
política forjada; identidad/diagnóstico/salida parcial/restauración/cleanup;
transición sin autoridad I92. No ejecuta pruebas históricas o producto.

Una ejecución externa300s; sin ampliación automática. Los resultados conservan
raw, hashes antes/después, fuentes por caso, contexto externo y sello. Cualquier
incompatibilidad se preserva y presenta antes de ampliar/repetir. Las raíces de
prueba son propias con control hermano; ningún recurso operativo se inspecciona.

I92 sigue NOT_RUN: una eventual captura P01 completa321 tests/12 grupos necesitará
decisión separada sobre pins, presupuesto acumulado y destino exclusivo, externa
900s, sin reintentos ni publicación. No se crean aquí autoridad, destino ni
launcher. El PASS de componentes no prueba compatibilidad/capacidad funcional,
persistencia, recuperación integrada, independencia o fsync nativo. IR03,
suficiencia UI04.1 y publicación se deciden después de evidencia nueva completa.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL(UI04.1); D1–D4 cerrados e I1–I20/A52 aceptado.
D5 global/H07/G01–G07/GI33/34/38/39/40 OPEN; histórico30/35 sin promoción. Sin
proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción,
despliegue, nuevos SQL/Java/Docker o D6. Sin commit/push.
