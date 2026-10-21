# D5 I6 — coexistencia SQL sobre V30

Fecha: 2026-10-21. **Validación sintética completada; D5 abierto.**
[I5: comparación/revisión/simulación](D5-I5-REVIEW-SIMULATION.md) ·
[Uso](../../testing/D5/README.md#i6--coexistencia-sql-sobre-v30) ·
[Evidencia nueva](../validation/D5-I6-results.md).

## D5-A13 — alcance autorizado

El usuario eligió: «A: validar D5 sobre V30 en un laboratorio nuevo, con regresiones
y evidencia propias; sin tocar D4 ni escribir tareas D2 (recomendada)».
Se mantienen las exclusiones de proveedores/credenciales reales, promoción,
despliegue, activación y D6. Esta entrega añade un runner y pruebas, sin cambiar
SQL V1–V32, adaptadores, parsers, runners anteriores o contratos D1–D4.

## Target y preparación

El [runner I6](../../testing/D5/run_v30_lab.py) crea una base vacía exclusiva en un
contenedor PostgreSQL sin red ni puertos, usando la imagen local
`postgres:16-bookworm`. Aplica V1–V30 en orden, una transacción por archivo, y solo
entonces V31 y V32. No es el target anterior V11+V31+V32 ni una promoción Flyway.
El orden y hashes de los 32 archivos se registran en la evidencia propia.

Se conservan el volumen anónimo y los permisos sintéticos del laboratorio D5 para
comprobar reinicio y recuperación. Al salir se elimina exclusivamente ese contenedor
y se comprueba la desaparición de su volumen. No monta `run_data`, checkouts
privados o configuración D4/dev, ni arranca procesos de workers/control plane.

El propietario prepara controles sintéticos no vacíos: worker OFFLINE, recurso
deshabilitado con provider SYNTHETIC, cuenta física sin reservas, catálogo D4
deshabilitado y perfil/época D3 creado mediante su entrada configure existente.
No hay heartbeat, presencia activa, entrega, prueba de proceso, tarea u operación.
Estos controles pertenecen al fixture; no se presentan como actividad real.

## Matriz implementada

El runner reutiliza las 21 pruebas PostgreSQL I4 y las 15 I5, sin modificar sus
casos. En este target amplía la instantánea de estado protegido a las tablas de
public/D2/D3/D4. Las revisiones fuente nuevas son el efecto autorizado de ingesta;
ninguna simulación escribe tareas o requisitos. Añade:

| Caso | Comprobación |
|---|---|
| T01 | Definiciones/propietarios/ACL/config de funciones y triggers de aplicación V30 conservados; readset D3 vigente incluye presencia D4 y excluye fuentes/D5 |
| T02 | Registro de fuente, ingesta, comparación, revisión y simulación completos; tablas protegidas y digest de d3.state_body idénticos antes/después |
| T03 | Funciones D3/D4 presentes denegadas con SQLSTATE 42501 a escritor/lector/reviewer; ninguna autoridad efectiva de esas funciones; propietario D5 sin uso de schemas D2/D3/D4 |
| T04 | Flujo D5 termina mientras otra sesión mantiene d3.lock_state y sigue esperando; no necesita los mutex de publicación/ejecución D3/D2 |
| T05 | Captura D3 y lectura de presencia D4 terminan mientras otra sesión mantiene el mutex D5 |

T04/T05 comprueban que la sesión bloqueadora sigue viva al terminar la operación
observada. El timeout es una guarda del test, no una promesa de rendimiento.
T05 crea una captura/recibo D3 de fixture, sin publicar planes ni ejecutar tareas.
La lectura D4 devuelve ausencia de presencia; no fabrica una señal de proceso.

La comparación de catálogo se limita a funciones existentes de public/D2/D3/D4
(definición, propietario, ACL y configuración) y triggers no internos. Las tablas
nuevas D5 y sus triggers FK internos son aditivos. Se mantienen los permisos
mínimos al propietario D5 previstos en V31 sobre las tablas públicas de fuentes;
no se afirma identidad de todo el catálogo PostgreSQL ni de esos grants nuevos.

## Resultado y límites

41 pruebas PostgreSQL pasan: 36 de regresión D5 y cinco de integración. Las pruebas
incluyen concurrencia, CAS, replay, aborto antes del commit, reinicio real y flujo
CLI bajo V30. La campaña confirma cero filas en tasks y operations al terminar.
La regresión D2 independiente y las comprobaciones de conservación se registran
en el informe nuevo, sin sustituir evidencias anteriores.

Esta entrega cierra el hueco de coexistencia SQL probado en I4/I5. La matriz
HTTPS/procesos de D4 conserva su evidencia histórica; I6 no ejecuta ni revalida sus
30 escenarios completos, efectos externos o verificación de procesos activos.
Tampoco prueba escalabilidad o coexistencia con DDL arbitrario del propietario.

Siguen pendientes el formato Gentle-AI/routing completo, el contrato de aplicación
operativa/mapeo a D2, las integraciones previstas en D1 y los criterios de cierre
D5. La aplicación real y proveedores requieren decisiones posteriores. D1–D4
permanecen cerrados y D6 no se inicia.
