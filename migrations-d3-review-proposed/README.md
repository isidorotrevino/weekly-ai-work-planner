# Corrección de revisión D3

V15 es una propuesta nueva, aplicada únicamente a bases sintéticas con una sexta ubicación explícita. Conserva V1–V14 y sus evidencias. No promueve migraciones ni concede permisos de despliegue.

Sustituye la función D3 que clasifica eventos: STATE_CHANGED a REOPENED de un incidente actualmente crítico y abierto tiene tratamiento inmediato y rompe protección, igual que la señal REPLAN_REQUIRED. D2 no siempre emite esa segunda señal al reabrir sin cambiar severidad.

Para reaperturas críticas ya recibidas por V14 en un lote abierto, añade un evento explícito `V15_REOPENING_CORRECTION`, adelanta el lote y aumenta su revisión. Conserva el evento/recibo original y todos los hechos físicos. No reinterpreta silenciosamente la historia ni ejecuta un worker.

Las pruebas comparan el comportamiento V14 y V15, verifican la conservación del outbox y prueban flujos completos sobre V15. [Revisión y límites](../docs/design/D3-REVIEW.md).
