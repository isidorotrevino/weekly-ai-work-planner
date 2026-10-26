# D5 I67 — laboratorio de trazabilidad GI33/GI34

Fecha: **2026-10-26**. [Contrato I66](D5-I66-TRACEABILITY-DESIGN.md) · [TT48](D5-I66-TRACEABILITY-REVIEW.md).

La selección A aprueba I66 y autoriza implementar trazador de lectura, registro fijo y pruebas de auditoría TT48. No reejecuta campañas funcionales ni modifica producto, auditor I38, registro anterior, handoff o evidencia previa. P0 vigente, agregado81/3 y criterios globales abiertos.

El script nuevo adapta las doce entradas selladas en I66, liga Git/blob/hashes, inputs y contexto específico de cada runner y conserva44 grupos y388 escenarios. Los602 registros legados y692 ocurrencias I64 no son pruebas nuevas. La lectura real genera FINDINGS esperados por metadata ausente y cambios de aplicabilidad legada; TT48 valida esa respuesta sin convertirla en fallo funcional histórico ni aceptación de suficiencia.

Las primitivas de lectura segura/Git se adaptan del código GPL existente de I38 como texto revisado; no se importa ni ejecuta su módulo y sus archivos quedan intactos. Cache por identidad evita releer cada raw/input por test; comprobación final vuelve a leer/hash y compara conjuntos. Se respeta256MiB acumulado/128MiB único,16MiB por archivo y12MiB de salida; no se truncó ni aumentó presupuesto. Los hijos permitidos son Git local con límites y espera de terminación; no procesos de laboratorio ni señales de inyección.

Los fixtures negativos viven en temporales propios; no se recorre entorno operativo. Source AST identifica métodos explícitos y aliases DF/DR conocidos sin ejecutarlos. Los métodos generados por factories sin definición AST individual conservan METHOD_AST_NOT_RECORDED. Las fronteras/operaciones ausentes permanecen tipadas; campos complejos de dominio sólo se referencian por puntero y hash, sin payload en la salida.

La validación consta de TT48 y una invocación CLI real de lectura separada, con argv/entorno actuales del auditor, hash del raw, exit y entradas pre/post. Ninguna ejecución de auditoría es regresión Python321/HC/HF/IC/UQ/RV/NA/FN/CE/GX ni prueba de persistencia o recuperación integrada. I67 sólo puede quedar AUDIT_VALIDATED_PENDING_SUFFICIENCY_REVIEW; UI01.2/UI04.1/UI09.2 siguen PARTIAL hasta revisión específica. D1–D4 cerrados y hito local aceptado intactos; D5 global/G01–G07/GI globales y H07 abiertos, sin proveedores/credenciales, consumo/reservas, activación, promoción, despliegue, D6 o publicación.
