# D5 I6 — resultados de coexistencia SQL V30

Fecha: 2026-10-21. **PASS acotado; D5 abierto.**
[Alcance aprobado A13](../design/D5-I6-V30-COMPATIBILITY.md) ·
[Resumen portátil y hashes](D5-I6-results.json).

| Campaña nueva | Comando desde la raíz | Resultado |
|---|---|---|
| D5/V30 | `python3 -m testing.D5.run_v30_lab` | 41 pruebas: 21 I4 + 15 I5 + 5 nuevas T01–T05; 0 fallos/errores |
| Python local | `python3 -m unittest discover -s testing/D5 -v` | 51 pruebas, 0 fallos/errores |
| D2 independiente | `bash testing/D2/run-docker-audit.sh` | 157 pruebas, 0 fallos/errores/omisiones |

PostgreSQL 16.15 sobre imagen local `postgres:16-bookworm`; el resumen JSON registra
imagen y hashes ejecutados. El target D5 fue una base nueva con V1–V30 aplicadas
antes de V31/V32, con transacción por archivo. Ninguna migración o código de
producto necesitó cambios. El harness D2 mantuvo su target y fixtures propios;
sus 157 pruebas no se atribuyen al target V30 ni a la matriz D4.

## Observaciones nuevas

- Funciones public/D2/D3/D4 conservaron definición, propietario, ACL y configuración
  entre V30, la adición D5 y el final de la campaña. Se conservaron los triggers
  de aplicación no internos; el alcance exacto y digest están en el resumen.
- El readset D3 vigente incluyó presencia D4 y excluyó fuentes/revisiones y D5.
  Un ciclo completo de registro, ingesta, comparación, revisión y simulación
  conservó el digest de d3.state_body y las tablas protegidas no fuente.
- La instantánea protegida incluyó controles no vacíos: cuenta física, worker
  OFFLINE, recurso/catálogo deshabilitados y perfil/época D3. No se fabricaron
  heartbeat, presencia activa ni evidencias de ejecución.
- Escritor, lector y reviewer recibieron SQLSTATE 42501 al intentar usar entradas
  D3/D4 presentes: capture, enqueue, dispatch, transport, ejecución, presencia y
  registro de pruebas de árbol. Ninguno obtuvo autoridad efectiva de esas funciones.
- D5 completó su ciclo mientras otra sesión mantenía d3.lock_state. La sesión
  bloqueadora continuaba esperando al terminar el ciclo.
- Una captura D3 y una lectura D4 completaron mientras otra sesión mantenía el
  mutex D5. No hubo publicación de planes, entrega a workers ni ejecución.
- Se repitieron bajo V30 los casos I4/I5 de CAS, concurrencia, replay histórico,
  límites, aborto antes del commit, reinicio real, revisión y flujo CLI.
- Al terminar se comprobaron **cero tareas y cero operaciones** en esta base D5.
  El contenedor y su volumen anónimo se eliminaron; no quedaron contenedores D5.

Los logs y resultados brutos quedan privados en
`work/d5/postgres/d5-pg-*/v30-results.json`; D2 conserva su evidencia aparte en
`work/docker-audit/`. Ninguna fuente privada, credencial o log bruto se publica.

## Conservación y límites

Se verifican los hashes de cierre D3/D4, su documento canónico y las entradas
registradas en I4/I5. Se comprueban enlaces locales, formato y publicación. Los
informes anteriores siguen reflejando sus targets históricos y permanecen intactos.

I6 valida coexistencia SQL D5/V30 con controles inactivos y capturas de fixture.
No ejecuta la matriz HTTPS/procesos D4, efectos externos, planificación de tareas
reales o DDL concurrente arbitrario. Su PASS no cierra D5, no amplía D6 y no autoriza
aplicación operativa, proveedores reales, promoción ni despliegue.
