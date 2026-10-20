# Propuesta de coordinación D3

V14 se aplica después de V13 mediante esta quinta ubicación explícita, solo en bases sintéticas desechables. V1–V13 se conservan. No promueve migraciones ni crea LOGIN o permisos de despliegue.

Añade solicitudes, eventos inmutables, intentos, historial, recibos propios de outbox y reloj de barrido persistente. El bookkeeping se excluye del snapshot físico: revisión causal y lease cercan la publicación. Ninguna función arranca temporizadores ni llama a workers o proveedores.

[Contrato, validación y límites](../docs/design/D3-COORDINATOR.md).
