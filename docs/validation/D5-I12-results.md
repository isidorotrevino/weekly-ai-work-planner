# D5 I12 — resultado del laboratorio de reaparición

Fecha: 2026-10-21. **PASS acotado; D5 abierto.**
[Implementación y autorización A29](../design/D5-I12-REAPPEARANCE-LAB.md) ·
[Resumen portátil y hashes](D5-I12-results.json).

| Campaña nueva | Comando | Resultado |
|---|---|---|
| V30 + V31–V35, base nueva | `python3 -m testing.D5.run_reappearance_lab` | 126 pruebas: 21 I4 + 15 I5 + 5 I6 + 27 I8 + 28 I10 + 30 R01–R30; cero fallos/errores |
| Python local | `python3 -m unittest discover -s testing/D5 -v` | 51 pruebas; cero fallos/errores |
| D2 independiente | `bash testing/D2/run-docker-audit.sh` | 157 pruebas; cero fallos/errores/omisiones |

PostgreSQL 16.15, imagen local sin red ni puertos publicados. El JSON registra
imagen, hashes de entrada y nombres completos de los casos aprobados. Los métodos
RP01–RP30 corresponden a la matriz R01–R30. D2 mantuvo su target histórico propio;
sus resultados no se atribuyen a V30 o a la campaña HTTPS/procesos D4.

## Matriz R01–R30 ejecutada

| Caso | Evidencia observada — PASS |
|---|---|
| R01 | Destinos creados por I8 e I10; preparación/replay sin mutar tablas protegidas y prueba/version explícitas |
| R02 | Scope/intención incorrectos y task_key local distinto rechazados sin adopción |
| R03 | Declaración SAME_SOURCE_ENTITY y razón válidas; distinta, no confirmada, vacía o solo blancos rechazadas |
| R04 | Observación, ACCEPT, simulación o ausencia no materializada insuficientes; sin tarea nueva |
| R05 | Recibos/IDs ajenos y cadena de fixture incoherente no acreditan ausencia; fixture revertida |
| R06 | Otro efecto de ausencia avanza cabeza; prueba anterior falla aunque conserve el mismo estado de fuente |
| R07 | Before histórico distinto de la base aplicada no la sustituye; PATCH usa la base/proyección reales |
| R08 | «Antes» nuevo con otra fila modificada y posición distinta admitido; ambas observaciones fijadas |
| R09 | CHANGED/UNCHANGED, fila ausente en ambos lados o captura bloqueante no son reaparición |
| R10 | Sin ACCEPT I5 o con pins obsoletos/ABA se bloquea; preparación nueva fija revisión vigente |
| R11 | Cambio de referencia y vuelta a la misma observación causan conflicto por versión |
| R12 | ID >5.000 caracteres, Unicode/Markdown/pipe/tachado y fila completa conservados |
| R13 | Título inválido bloqueado; descripción vacía/guion literal; DONE/approved no cambia BACKLOG |
| R14 | PATCH solo title/description y row_version +1, conservando todos los demás campos locales |
| R15 | Enlace de evidencia conserva exactamente la fila de tarea y avanza la base/cabeza propia |
| R16 | Edición local conservada por ausencia y con/sin incremento de versión bloquea, incluso al preparar de nuevo |
| R17 | Urgencia cambiada después de preparar causa CAS completo; cambio de clave invalida identidad |
| R18 | BLOCKED, operación y entrada CANCELLED de planificación bloquean; fixtures negativas revertidas |
| R19 | Hash alterado, campos extra o mutación de manifiesto rechazados; no transferir aceptación |
| R20 | Revisión propia ausente o revocada/reaceptada invalida paquete antiguo; versión nueva permite otro paquete |
| R21 | Lista/hash explícitos; vacío, duplicados, exceso de filas, dos propuestas por intención o mezcla I8 rechazados |
| R22 | Replay histórico, ALREADY_APPLIED y command_id global entre variantes no restauran campos locales |
| R23 | Dos paquetes concurrentes producen un ganador; carrera con cambio de referencia serializa o entra en conflicto |
| R24 | Paquete mixto inválido, terminación del backend y fallo después de mutaciones revierten tarea, vínculos, cabeza/base, auditoría y recibo |
| R25 | Commit con respuesta descartada, reinicio y recuperación por recibo/CLI sin repetir PATCH |
| R26 | Enlace idéntico reutilizado tras comprobación; localizador/revisión exactos y procedencia inmutable |
| R27 | Revocar revisión histórica de ausencia no borra el efecto; otro ciclo exige nueva prueba/version; replay no restaura estado anterior |
| R28 | Continúa I5/I8 con PATCH, enlace y ausencia; I8 antiguo sigue bloqueando ADDED materializado e I10 exige v0 |
| R29 | Sesiones reales prueban orden de locks; roles sin DML/helper/autoridad D3; READ COMMITTED exigido; PATCH cambia digest D3 y conserva plan publicado |
| R30 | Reaparición no crea tarea; BACKLOG eligible con cero operaciones/entregas/outbox/intentos/reservas y catálogo anterior intacto |

R23/R29 observaron esperas y resultados entre sesiones reales. R24 termina un
backend con transacción abierta e inyecta un fallo tras actualizar tareas, vínculos,
cabezas y auditoría, antes de confirmar el hecho de aplicación; toda la transacción,
incluidos trigger/función temporal de fixture, se revierte. R25 reinicia PostgreSQL
tras commit sin usar su respuesta y recupera el mismo resultado. No son solo mocks.

Las fixtures negativas de operación nunca se ejecutan y se revierten conforme a A18.
La entrada de planificación CANCELLED prueba que también se bloquea historial.
Los planes publicados son fixtures del propietario, sin d3.publish, despacho o
outbox. No se reejecuta la matriz HTTPS/procesos D4 ni se atribuye a estas pruebas.

## Conservación, limpieza y límites

El resumen JSON registra 75 tareas sintéticas BACKLOG de fixture y comprueba
cero operaciones, entregas, outbox, intentos, reservas y reservas de plan al terminar.
La aplicación de reaparición conserva el número de tareas; sus fixtures de origen
se crean antes mediante I8/I10. El contenedor y su volumen propios se eliminaron,
sin tocar datos dev/D4. Los logs/resultados brutos permanecen privados en
`work/d5/postgres/d5-pg-*/reappearance-results.json`, con D2 en `work/docker-audit/`.

Coinciden las definiciones, propietarios, ACL/config de funciones D5 anteriores a
V35 y el catálogo de funciones/triggers de aplicación public/D2/D3/D4 respecto a V30.
Se conservaron 245 entradas de cierre D3/D4, el documento canónico D4 y las
20/27/47/51/55 entradas de ejecución I4/I5/I6/I8/I10. I11 sigue como contrato
histórico; A29 autoriza esta implementación. Se verifican enlaces, formato e
higiene de publicación antes del commit. No se publica corpus privado ni logs brutos.

La reconstrucción del parser sigue siendo frontera del adaptador confiable;
SQL privilegiado no autentica fuente ni identidad de entidad. SAME_SOURCE_ENTITY
y etiquetas de revisor son afirmaciones, no identidad autenticada D6. Se valida
concurrencia acotada, no escalabilidad o DDL arbitrario del administrador.

D5 sigue abierto. Adopción, ID reutilizado para otra entidad, resolución local,
cambio de perfil/política, múltiples orígenes y formato Gentle-AI/routing conservan
sus pendientes. Sin proveedores/credenciales reales, activación, promoción,
despliegue o ampliación de D6.
