# D4 — alcance sintético aprobado y cerrado

Versión 1.0. Fecha de aprobación: 2026-10-20, Europe/Madrid.
Estado: **APPROVED_CLOSED_SYNTHETIC**.

El usuario aprobó expresamente el cierre con **«A: aprobar cierre de D4 sintético»**,
como respuesta a la revisión final de 638 pruebas positivas y 1.085 comprobaciones
en 30 escenarios V30. Esta aprobación cierra el alcance sintético documentado,
conserva sus límites y no autoriza promoción de migraciones ni despliegue.

Este documento y el [manifiesto de cierre](../validation/D4-CLOSURE.json) establecen
el estado vigente. Las [decisiones A01–A24](D4-DECISIONS.md), la
[tabla de aceptación](D4-I12-ACCEPTANCE-REVIEW.md) y el
[informe I12](../validation/D4-I12-INTEGRATED-results.json) delimitan lo aprobado.
Los informes anteriores conservan su estado al emitirse, incluidos los campos
«D4 abierto» y «aprobación pendiente»; no se reescriben como si la aprobación
hubiera precedido a las pruebas.

## Alcance aceptado

- Workers Java 21 de fixtures confiables, HTTPS/mTLS con CA efímera, catálogo
  autorizado y sesiones/incarnaciones durables con secuencia monotónica.
- Integración con D2/D3: cuentas físicas, reservas entre planes, reparto 70/20/10,
  dependencias, prioridad por camino bloqueante, límites de intentos y fencing.
- Supervisor de subprocesos, renovación acotada, parada acreditada de forma
  independiente, receptor sintético con diario y cierre durable, grants ligados
  a lease y generación. La presencia no libera reservas ni acredita parada.
- Verificador Java independiente de archivos, objetos Git y restauración local;
  ingreso de hechos, aceptación, liquidación y rearme con autoridades separadas.
- Checkpoints v1/v2 y cadena lineal multicuentas con costes exactos congelados,
  continuidad en la misma operación/reserva/contador, TOP_UP al vector original
  y autorización/rearme explícitos.
- Reconciliación monotónica del mismo receptor, recuperación parcial o terminal,
  ausencia sin progreso, revisiones append-only con delta cero y cuarentena
  separada tras hechos nuevos, conservando terminales, PASS y consumo históricos.
- Polling acotado, pausa tras checkpoint o incertidumbre y recuperación explícita
  tras reinicios. Laboratorio Compose separado de las baterías SQL históricas.

## Evidencia del cierre

La campaña final I12 registra **638 pruebas distintas**: 281 D4, 175 D3,
157 D2 y 25 Python. El grupo adicional repite cinco pruebas que no se suman de
nuevo. Las suites históricas conservan sus targets; no se presentan como pruebas
V30. La matriz Compose S01–S30 sí se ejecutó completa sobre V30 y registró
**1.085 comprobaciones**, sin fallos ni omisiones finales.

El informe identifica fuentes, imágenes, versiones, snapshots y pilotos excluidos.
Su limpieza documenta cero contenedores, redes y volúmenes restantes en los 30
proyectos finales y los 14 proyectos piloto. El manifiesto liga por SHA-256 las
161 entradas ejecutables verificadas y conserva los hashes históricos y de D3.
Este registro de aprobación modifica documentación y metadatos; no afirma una
nueva ejecución de las campañas.

## Límites conservados

Fixtures confiables y receptor sintético; no aislamiento de código hostil ni
atestación de máquinas físicas. Git construye y verifica objetos en un repositorio
privado del verificador desde una base confiable y archivos observados: no importa
`.git`/bundles del worker ni acredita su historial arbitrario. SHA-1 identifica
objetos Git; SHA-256 verifica contenido. La observación repetida de archivos bajo
parada/exclusión no es un snapshot atómico frente a escritores concurrentes.

La restauración solo afecta archivos locales; no deshace APPLIED ni consumo.
Hashes incompatibles, revocación de APPLIED, costes variables, diario perdido,
varios receptores o ejecuciones heredadas sin procedencia concluyente permanecen
bloqueados. No se declara arbitraje universal, exactly-once externo ni SLA.

D1, D2 y D3 conservan su cierre y evidencia. Las migraciones propuestas permanecen
en sus ubicaciones actuales, sin promoción. Proveedores, credenciales y cuotas
reales, operación física y despliegue quedan fuera. Este cierre no inicia D5/D6.

## Referencia de repositorio

Base de la sesión: `90061785d084ea2107b5605bdd0d38f731445090`.
El cierre y los incrementos I11/I12 se publicaron en `origin/main` el 2026-10-21:
`dc8e542b28c55fafd8ec155e2b8ebf7e8aa80f94`. El manifiesto registra esa referencia en
`repository_reference.published_D4_commit`; las fuentes ejecutables y los informes
conservan sus hashes originales. La anotación de publicación es posterior al commit
de cierre para evitar una referencia circular.
No quedan pendientes de aprobación ni técnicos identificados dentro de este
alcance sintético aceptado; ampliaciones requieren su propio alcance y validación.
