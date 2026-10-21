# D5 I5 — resultados de comparación, revisión y simulación

Fecha: 2026-10-21. **PASS acotado; D5 abierto.**
[Contrato y decisiones A10–A12](../design/D5-I5-REVIEW-SIMULATION.md)
· [Resultados portátiles y hashes](D5-I5-results.json).

| Campaña nueva | Comando desde la raíz | Resultado |
|---|---|---|
| Python local | `python3 -m unittest discover -s testing/D5 -v` | 51 pruebas: 47 de regresión y 4 nuevas, sin fallos/errores |
| PostgreSQL I5 | `python3 -m testing.D5.run_review_lab` | 36 pruebas: 21 I4 sobre el target nuevo y 15 R01–R15; sin fallos/errores |
| D2 independiente | `bash testing/D2/run-docker-audit.sh` | 157 pruebas, sin fallos/errores/omisiones |

PostgreSQL 16.15, imagen local `postgres:16-bookworm`; identificador y entradas
exactas en el resumen JSON. Esta campaña usa V1–V11 + V31 + V32 exclusivamente en
su base D5 desechable. No es una cadena Flyway promovida ni una integración sobre
V30. I4 conserva su runner, propuesta SQL, informe y hashes ejecutados.

## Cobertura nueva observada

| Casos | Evidencia |
|---|---|
| R01–R04 | Recuperación/reconstrucción de capturas SQL sin archivos locales originales; deduplicación del informe; comparación consigo misma; anotaciones y filas completas; BLOCKED y ámbitos incompatibles |
| R05 | Hash/ámbito incoherentes rechazados; semántica falsa insertada por escritor SQL directo confiable detectada al reconstruir el informe, antes de revisar |
| R06–R09 | Decisiones por fila y cambio completo; CAS, rechazo posterior, reaceptación, pins obsoletos, referencia vacía, cambio de referencia y A→B→A; replay histórico sin restaurar cabezas |
| R10 | Dos decisiones realmente esperando el mutex: una gana y otra da conflicto. Simulación concurrente con rechazo: resultado consistente con el orden confirmado; no aplica una decisión ya reemplazada |
| R11 | Sesiones terminadas después de escribir y antes del commit, tanto decisión como simulación; rollback íntegro; retry y recuperación tras reinicio real |
| R12 | Simulación de añadido/cambio/ausencia; KEEP_EXISTING_NO_DELETE; tablas públicas/D2 y referencia de fuente idénticas antes/después |
| R13 | Separación escritor/reviewer/lector, helpers privados, hechos inmutables, rechazo de envelope ampliado y pins duplicados |
| R14 | ID de origen con más de 5.000 caracteres conservado y revisado sin truncamiento ni error de tamaño de índice |
| R15 | CLI compare → export → row → decide → simulate; bytes exportados verificados; código 2 para decisión obsoleta |

Se observaron cuatro barreras de concurrencia con dos sesiones realmente esperando
el mutex: dos de regresión I4 y dos de revisión/simulación. Un conflicto de una
lista mixta aceptada/rechazada no genera simulación parcial. El resultado exitoso
lleva simulation_only=true, writes_d2=false y activation_allowed=false.

La ejecución final eliminó su contenedor y comprobó que su volumen anónimo ya no
existía. Los logs y reportes brutos se conservan solo en
`work/d5/postgres/d5-pg-*/review-results.json`; la regresión D2 mantiene su propio
directorio ignorado. Los temporales de comparación/exportación de los casos se
eliminaron. No se leyó ni importó el corpus privado.

## Límites y conservación

La reconstrucción del comparador corresponde al adaptador confiable, no a SQL.
R05 demuestra esa frontera y no se presenta como validación independiente del
parser en PostgreSQL. Las etiquetas del revisor son declarativas, sin firma ni
autenticación D6. ACCEPT no autoriza trabajo ni cambia estados de tareas.

El punto 1 queda implementado sobre PostgreSQL. El punto 2 llega hasta revisión
persistida y simulación, según la opción A aprobada; la aplicación operativa real
sigue pendiente. No hay importación de tareas/requisitos, proveedores reales,
credenciales reales, promoción, despliegue ni ampliación D6.

Se comprueban aparte manifiestos y hashes D3/D4, hashes de entradas I4 y enlaces
locales, formato del diff y revisión de publicación. Los resultados I1–I4 y los
cierres D1–D4 permanecen intactos; no se sustituyen por esta campaña.
