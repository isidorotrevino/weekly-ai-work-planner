# D3 I2 — persistencia y publicación transaccional

> Estado posterior: **D3 aprobado y cerrado el 2026-10-19** por «si, cierra D3», con el [MVP conservador 1.0](D3-approved.md). Las referencias a D3 abierto en este documento describen la entrega anterior a esa aprobación. No hay promoción ni despliegue aprobado.
Fecha: 2026-10-19. Incremento JDBC/SQL implementado y validado sobre datos sintéticos. Diseño D3 v0.2 e I1–I3 autorizados; **D3 abierto, sin cierre ni despliegue aprobado**.

## Resultado

El módulo [scheduler-postgres](../../scheduler-postgres/README.md) conecta el núcleo Java con una captura SQL inmutable. La propuesta [V12](../../migrations-d3-proposed/V12__planning_snapshot_and_publication.sql) añade exclusivamente objetos d3. No modifica V1–V11 ni sus funciones. La separación de carpetas impide que la auditoría histórica D2 cambie de target por descubrimiento automático.

| Contrato | Comportamiento implementado |
|---|---|
| Metadata | Perfil/época explícitos; estimaciones y calendarios inmutables con heads CAS; clasificación de incidentes; atribución legada de vía solo administrativa |
| Snapshot | Copia MVCC consistente, hash PostgreSQL `jsonb::text`, orden estable y UTC; incluye filas/conjuntos completos de dominio, capacidad, ejecución, evidencia, planes y metadata |
| Adaptador | Records del núcleo desde el capture, elegibilidad/integración por funciones D2 y compatibilidad JSONB exacta de worker/recurso; reutiliza V11 para versiones |
| Equidad | Muestras persistentes con caducidad acotada, intervalos elegibles y cierre por inicio de intento; vía/gasto derivados de reservas; épocas con motivo sin borrar hechos físicos |
| Publicación | Head global CAS, comprobación de huella fresca y guardas sensibles al reloj, snapshot/hijos congelados, sucesor explícito y outbox en una transacción |
| Capacidad | Delta de TOP_UP y vectores completos comprobados de nuevo; disponible físico compartido entre planes; publicar no crea RESERVE ni BORROW |
| Roles | API de lectura/publicación separada de configuración y contabilidad; PUBLIC sin permisos d3; prueba con rol NOLOGIN sin DML ni acceso directo a CLAIM/recalibración |

## Concurrencia y orden

El cálculo no conserva una transacción abierta. `capture` mantiene el mutex global D2 solo durante la copia y confirmación del capture. La función STABLE que construye el cuerpo comparte el snapshot de su sentencia; el token persiste dicho cuerpo para todas las lecturas posteriores del adaptador.

La publicación exige READ COMMITTED: adquiere 742001 (publicación), después 742002 (D2), antes de locks de filas. Toma locks SHARE de relaciones no protegidas por esos mutex para impedir cambios de conjuntos mientras valida. Las tablas con triggers de mutex —planes/hijos, grafos y mappings— se excluyen de esos locks SHARE para no invertir el orden con sus locks de tabla previos al trigger. Sus escrituras siguen serializadas por las guardas existentes. El propietario capaz de alterar DDL queda fuera del modelo runtime, igual que en D2.

Después de esperar, la función vuelve a leer el cuerpo completo y lo compara con el hash guardado. No usa el máximo del diario ni depende de que un escritor incremente row_version. Inserciones/borrados y cambios concurrentes de prioridad, cuentas, evidencia y configuración invalidan la propuesta. Además vuelve a comprobar heartbeat, ventanas, estimaciones y aprobación con el reloj actual, aunque ninguna fila haya cambiado.

Dos publicadores del mismo predecesor no pueden confirmar ambos. Primero se publica el sucesor, después se marca el anterior SUPERSEDED y se actualiza el head, dentro del mismo commit; conserva el contrato D2 que exige sucesor PUBLISHED explícito. Un rollback revierte también hijos, recibo y outbox. El head D3 no adopta silenciosamente planes legados publicados.

## Validación registrada

[Resultados portables I2](../validation/D3-I2-results.json), con hashes de entradas y versiones observadas. Los grupos permanecen separados:

- Núcleo Java: 62 pruebas I1, incluida igualdad del resultado completo ante permutaciones.
- Integración I2: 33 pruebas con PostgreSQL 16, instalación V1–V12, upgrade V11→V12 con reserva previa, JDBC real y rol restringido.
- Regresión D2: 157 pruebas históricas en bases V1–V11, con 29.829 vectores SemVer dentro de una prueba; sin modificar su harness ni evidencia original.

La integración cubre publicaciones rivales; espera observable en pg_locks ante CLAIM/recalibración/invalidación; escritor sin mutex; invalidación HARD real; cambios de conjuntos; replay/conflicto de comandos; rollback completo; reloj sin mutaciones; zonas horarias distintas; snapshots congelados; no duplicación del diario al enlazar reservas en planes sucesivos; conservación de consumo de vía al cambiar época; límites temporales de observación; recibos contradictorios; y excepción P4 solo por consumidor de mayor prioridad activo, no pausado.

Las llamadas D2 CLAIM de estos casos son operaciones SQL sintéticas, sin proceso externo. La suite D2 aislada prueba V1–V11; no se presenta como si sus 157 casos se hubieran vuelto a ejecutar sobre V12. Las interacciones V12 con ejecución se cubren por los casos I2 indicados.

## Alcance pendiente

**Estado al entregar I2 (histórico): I3 autorizado y pendiente.** Ahora se ha entregado el [prototipo I3](D3-I3-DISPATCH.md). El alcance previsto era: despachador ligado al plan vigente, mapping+CLAIM atómicos, guardas de ventana en TOP_UP y atribución de vía de nuevas reservas, renovación/fencing y verificación sin bypass. El núcleo conserva `reviewOnly`; la publicación es una intención, no una autorización para ejecutar.

Todavía no hay aplicación Spring Boot, consumidor de eventos ni temporizadores activos. `observe_eligibility` debe invocarse al procesar cambios/barridos; registra muestras acotadas y no inventa historia continua de cambios no observados. La precisión y entrega del circuito de eventos se validarán al implementar su coordinador. No hay cuotas/proveedores, checkpoints reales o integraciones comerciales probados, ni objetivos numéricos de rendimiento vigentes.

Los hashes completos son conservadores: incluso cambios ajenos al candidato pueden exigir recalcular, y su coste crece con la historia. La biblioteca devuelve conflictos SQL; la coordinación de hasta dos recálculos usa la política I1 y queda para el servicio de solicitudes. Permisos de LOGIN, archivado/retención y despliegue pertenecen a D6.
