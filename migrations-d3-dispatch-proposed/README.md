# Propuesta aditiva D3 I3

V13 se aplica después de V12 usando esta cuarta ubicación explícita. Solo está validada en PostgreSQL desechable; no promueve migraciones ni concede permisos de despliegue. V1–V12 y la evidencia histórica se conservan.

Añade el historial inmutable `d3.dispatches` y las APIs del control plane `d3.dispatch`/`d3.execution`. Extiende la lista de relaciones del snapshot mediante una función nueva conservando la original I2. PUBLIC no recibe permisos. Los roles NOLOGIN del harness son exclusivamente sintéticos.

Contratos y límites: [I3: despacho protegido](../docs/design/D3-I3-DISPATCH.md).
