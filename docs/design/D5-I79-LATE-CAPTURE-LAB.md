# I79 — laboratorio de binding tardío y diagnóstico

Autoridad: selección A posterior a I78, aprobar contrato e implementar perfil/registro fijo y validar LB01–LB64 sólo sintéticos. Excluye producto/runners históricos, PG64/AT80, campañas funcionales y publicación. Base local `d6d52172a877f1892437becf50a08960f0bb3883`.

[Contrato](D5-I78-LATE-BINDING-DESIGN.md) · [Matriz](D5-I78-LATE-BINDING-REVIEW.md) · [Componentes](../../testing/prospective_capture_late/README.md).

Comando `python3 -B -m testing.prospective_capture_late.run_late_lab`, bajo subprocess externo con timeout de300s. Raw por caso, contexto público/versiones/comando, anclas AST y hashes pre/post en archivos nuevos I79. Reutilizar sólo módulos puros de captura; no importar pruebas/laboratorios antiguos.

Clases y módulos sintéticos se inyectan mediante lookup privado del fixture de prueba, sin cargar módulos de producto. Probar carga inicial/tardía, no uso, ausencia al primer rol, sustitución/export/source y contador acumulado. Preservar llamada original única, proyecciones I75, fallos/subtests y restauración. Writer y lector de diagnósticos prueban allowlist, fase/código inicial, rechazo de extras/tipos/correlación, escritura parcial sin reparación y separación de resultado funcional/metadata/transporte.

Productores sintéticos en grupos nuevos ejercitan el main real del nuevo worker y launcher con dependencias inyectadas: éxito, fallo TARGETS antes de raw, módulo sintético disponible sólo dentro de entrypoint y autoridad rechazada antes de confiar en canales. No es P01, no ejecuta un runner histórico ni valida retrospectivamente el error I77. Un proceso sintético propio adicional prueba timeout, guardas de lease y retirada confirmada. Temporales con OWNER/sentinel propio y sibling preservado; no tocar ámbitos operativos o privados.

Cuotas anteriores intactas, incluido ensayo real de131072 eventos sintéticos y rechazo del siguiente,2048/test, rotación de páginas, lectura acumulada y tamaño del paquete. El diagnóstico usa únicamente el sidecar existente. Validación sintética no garantiza compatibilidad, capacidad o tiempo de una futura captura completa P01.

Plan NOT_RUN_I80_AUTHORIZATION_REQUIRED; ningún manifiesto/destino/copia I80 en checkout. Autoridades sintéticas sólo en temporales retirados. I80 requeriría autorización humana separada para P01 completo321/12 en destino nuevo, deteniéndose y presentando cualquier incompatibilidad, sin ampliar topes ni sumar resultados históricos.

P0,81/3, UI01.2/UI04.1/UI09.2 PARTIAL; D1–D4 cerrados e hito D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/H07/G01–G07 y GI33/GI34/GI38/GI39/GI40 globales abiertos, histórico30/35 sin promoción. Sin inferir persistencia o recuperación integrada de PASS aislados, proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6. Sólo I52 publicado; publicación separada, sin acceso remoto.
