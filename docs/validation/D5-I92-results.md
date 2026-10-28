# I92 — captura P01 bloqueada por presupuesto global de referencias

La respuesta expresa **A** autorizó una captura sintética P01 completa321/12,
una ejecución bajo900s externos, sin reintento automático ni publicación. Se creó
una autoridad I92 nueva con los292 pins preparados y destinos exclusivos.
No se reutilizaron autoridades ni paquetes I86/I89. HEAD sigue
`7ff47485109306f90ecc4eebc6a6b3f6ec597d99`, sin cambios tracked, commit o push.

**BLOCKED_WORKER_FAILURE / INVALID_CAPTURE** tras **13/321 tests,1/12 grupos**
en **65,50s externos** (64,292s del runner). Los trece DF01–DF13 figuran PASS en
raw, cero fallos/errores/skips del runner; **308 tests no observados**. Ese PASS
parcial no es P01 completo ni evidencia aceptada. Primer diagnóstico:
**REFERENCE_BUDGET**, fase ENTRYPOINT. No hubo repetición.

[Autoridad](D5-I92-capture-authorization.json) ·
[Raw](D5-I92-P01/runner-raw.json) · [Sidecar](D5-I92-P01/sidecar.json) ·
[Contexto](D5-I92-P01/context.json) · [Medición externa](D5-I92-external-context.json) ·
[Resultados detallados](D5-I92-results.json) · [Integridad](D5-I92-integrity.json).

## Qué conserva el expediente

6882 eventos en cuatro páginas,7.582.675 bytes, máximo1317 eventos/frame;
99 oráculos retenidos,143 grupos de dominio,1366 enlaces y118 protocolos.
El contador compartido conserva **16393**, frente al techo **16384**. El código
heredado incrementa antes de comprobar el límite; intentos posteriores pueden
seguir incrementando. El exceso de9 no es una nueva tolerancia. El diagnóstico
prueba el fallo de presupuesto; no identifica unívocamente el primer wrapper o
la secuencia exacta de asignaciones que lo produjo.

DF01–DF12 conservan missing=[]; DF13 tiene PENDING_CHILD_EXIT y falta TEST_END.
El runner registra su PASS, pero la instrumentación no retuvo una observación de
salida para el último protocolo. No se completa usando cleanup o evidencia antigua.
Los hashes de páginas coinciden; el launcher conserva
NOT_ACCEPTED_INCOMPLETE_CAPTURE, sin validación causal completa aceptada.

Se observan seis proyecciones NP01_T_REMOTE_PROOF con null explícito en
recibos/oráculos del padre. El paquete inválido no permite promoverlas a aceptación
funcional; no demuestra NP02 R, CP07/CP13 nullable o compatibilidad321/12.
No reapareció COMMAND_HEADER_INVALID en errors; eso no certifica todas las rutas.

## Cleanup e integridad

Observadores restaurados. El runner registra142 raíces T creadas/retiradas,
118 hijos de dominio sintético asentados y cero vivos; los -9 corresponden a
terminaciones de los escenarios originales. Cero hilos vivos. El launcher registra
OWN_GROUP_GONE. Estas observaciones no reparan PENDING_CHILD_EXIT ni prueban
persistencia/recuperación integrada o fsync nativo. Sólo recursos propios.

Los292 pins/63.070.664 bytes coinciden después. Sellos I83–I91 y propuesta I91,
con todos sus artefactos, permanecen byte a byte. No se ejecutaron otras campañas,
P02–P10, I38/I67, suites de componentes, SQL/D2/D3/D4, Java o Docker.

## Próxima decisión

La captura queda conservada e inválida; no se amplía cuota, reinicia contador,
descarta evidencia, divide/reanuda P01 ni repite automáticamente. El requisito de
referencias es global, aun si las páginas tienen espacio. El prefijo13/321 no
permite calcular por extrapolación una cuota suficiente para toda la campaña.
La evaluación documental de capacidad I93 prepara las opciones antes de cualquier
cambio de contrato/perfil, componente o nueva captura. IR03 sigue NOT_READY:
necesita una captura nueva completa y válida y una decisión de revisión separada.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1). D1–D4 cerrados, I1–I20/A52 aceptado,
30/35 sin promoción; D5 global/H07/G01–G07/GI33/34/38/39/40 OPEN. Sin proveedores,
credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue o
D6. Publicación y aceptación global requieren decisiones propias.
