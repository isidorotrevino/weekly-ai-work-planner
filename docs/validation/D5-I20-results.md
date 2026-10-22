# D5 I20 — resultado de resolución local aislada

Fecha: 2026-10-22. **PASS acotado; D5 abierto.**
[Implementación y autorización A49](../design/D5-I20-ISOLATED-LOCAL-EDIT-LAB.md) ·
[Resumen portátil y hashes](D5-I20-results.json).

| Campaña nueva | Comando | Resultado |
|---|---|---|
| V30 + V31–V39, base nueva | `python3 -m testing.D5.run_isolated_local_edit_lab` | 264 pruebas: 21 I4 + 15 I5 + 5 I6 + 27 I8 + 28 I10 + 30 I12 + 32 I14 + 34 I16 + 36 I18 + 36 IL01–IL36; cero fallos/errores |
| Python local | `python3 -m unittest discover -s testing/D5 -v` | 51 pruebas; cero fallos/errores |
| D2 independiente | `bash testing/D2/run-docker-audit.sh` | 157 pruebas; cero fallos/errores/omisiones |

PostgreSQL 16.15 (Debian 16.15-1.pgdg12+2), imagen local sin red ni puertos publicados.
El JSON registra imagen, hashes, tiempo y nombres completos de los casos. IL01–IL36
corresponden a I19. D2 conserva su target histórico; no se atribuyen esos resultados
a V30 o a la campaña HTTPS/procesos D4.

## Matriz IL01–IL36 ejecutada

| Caso | Evidencia observada — PASS |
|---|---|
| IL01 | Destinos I8/I10/I12/I14/I16/I18 con prueba presente; preparar/replay sin escritura protegida ni avance de cabeza |
| IL02 | Ámbito/UUID/clave y destino no materializado bloqueados; ninguna adopción/reinicialización |
| IL03 | L=B con/sin row_version y convergencia posterior bloquean; no confirmación automática |
| IL04 | Snapshot actual completo, adopción divergente y ediciones con/sin versión; NULL local conservado |
| IL05 | Preparar/revisar/aplicar no crean comparaciones, review_items o decisiones I5; revisión propia real |
| IL06 | Cambios de estado, verificación, componentes, bloqueos, tachado o anotación bloquean aunque Item/Objective coincidan |
| IL07 | Otros bytes/posiciones con semántica igual: nueva revisión/localizador reales y fuente B conservada |
| IL08 | Ausencia aplicada vigente bloquea ambas elecciones con referencia presente antigua; prueba anterior falla por versión |
| IL09 | IDs de prueba ajenos, versión/cadena y recibo CONFLICT incoherente no acreditan presencia; fixtures revertidas |
| IL10 | Adopción v1 y reaparición válida, encadenamiento iterativo de resoluciones; revocar revisión histórica no deshace efecto |
| IL11 | Fila ausente, duplicados/ambigüedad ajenos y perfil incorrecto bloquean snapshot |
| IL12 | Referencia y versión exactas; ABA no devuelve vigencia a paquete antiguo |
| IL13 | Hashes de bytes/preview/fila y payload alterado rechazados; sin éxito ni procedencia falsa |
| IL14 | ID largo, Unicode/Markdown/pipes, tachado y anotación íntegros/literales |
| IL15 | Proyecciones inválidas bloquean; NULL local y Objective vacío/guion se conservan como tales |
| IL16 | Razón inválida, opción MERGE, force y texto manual rechazados por entrada cerrada |
| IL17 | Revisión propia completa requerida; aceptación de otra propuesta o dominio no se transfiere |
| IL18 | REJECT y revocación/reaceptación invalidan pins anteriores |
| IL19 | Manifiesto inmutable y reconstrucción comprueban fuente/base, prueba, snapshot y elección |
| IL20 | USE_SOURCE cambia solo title/description y row_version una vez; épica, urgencia, fecha, diferimientos y dependencia conservados |
| IL21 | KEEP_LOCAL no hace UPDATE: trigger negativo y snapshot completo; row_version intacta |
| IL22 | Ambas elecciones avanzan cabeza una vez conservando base, digest y projection exactamente |
| IL23 | KEEP_LOCAL sin escritura de tarea invalida otros paquetes aislados y paquetes I8/I14 sobre versión anterior |
| IL24 | Ediciones sin versión, campos ajenos y ABA observable invalidan snapshot completo |
| IL25 | Estado, operación y planificación histórica CANCELLED bloquean preparar/aplicar ambas elecciones; rollback obligatorio |
| IL26 | Límites, duplicados, única intención y snapshot/perfil; varias observaciones rechazadas y dominio I8 separado |
| IL27 | Sesiones reales entre paquetes aislados y entre ausencia I8/resolución aislada: un avance y un conflicto |
| IL28 | Revisión/referencia concurrentes se serializan y se validan tras espera real |
| IL29 | Paquete mixto inválido, aborto y fallo tardío revierten tarea/vínculo/cabeza/hecho/auditoría y recibo de éxito |
| IL30 | Replay histórico, command_id global y ALREADY_APPLIED no restauran texto/base/versiones posteriores |
| IL31 | Respuesta perdida, reinicio y CLI recuperan mismo recibo; JSON duplicado rechazado |
| IL32 | Vínculo exacto reutilizado, procedencia append-only y localizador incoherente rechazado; lectura por ámbito |
| IL33 | Continuidad I8 tras USE_SOURCE; nueva resolución aislada y resolución I14 ante cambio real tras KEEP_LOCAL |
| IL34 | Nueva ausencia/reaparición conserva I8/I12/I18 y prueba nueva/versionada, sin relajar entradas antiguas |
| IL35 | Roles/DML/READ COMMITTED, locks cruzados y captura D3 observados; PATCH cambia digest y plan publicado es inmutable |
| IL36 | Número de tareas conservado por resolución, BACKLOG, ausencia de activación y catálogo histórico intacto |

El ensayo inicial tuvo tres casos fallidos por fixtures: representar I14 sin un
cambio previo real, pedir un hash que no figura en el recibo de ingesta y reutilizar
una prueba de cabeza obsoleta antes de probar fuente inválida. Corregidas las
fixtures, pasaron nueve casos corregidos/reforzados en otra base y dos casos
complementarios de carrera/conservación. Esta campaña completa se ejecutó después
con código congelado; no se cuentan resultados parciales como evidencia aprobada.
No se relajó V39 para aceptar esas fixtures incorrectas.

IL05 compara contadores I5 antes/después: no basta declarar «sin comparación».
IL08 selecciona explícitamente un snapshot presente anterior tras ausencia aplicada:
ni S=B ni un recibo presente antiguo permiten avanzar esa cabeza. IL09 contrasta
cadena real y fixture negativa incoherente revertida. IL10 verifica nuevos efectos
sin requerir vigente la revisión histórica ya aplicada; la revisión nueva sí lo es.

IL21 instala un trigger negativo en transacción revertida y confirma luego el
efecto real, comparando toda la fila. IL22 comprueba base/digest/proyección exactos,
además de incremento único. IL23 no fabrica un paquete I18 sobre cabeza presente:
I18 parte de ausencia y la variante aislada la bloquea (IL08); versiones obsoletas
de reaparición siguen inválidas según sus regresiones y el ciclo IL34.

IL27/IL28/IL35 usan sesiones simultáneas y espera observada. La carrera I8 usa una
ausencia válida que puede ganar; entonces la variante aislada sigue bloqueada.
IL29 verifica rollback salvo el recibo de conflicto de negocio esperado; aborto o
error estructural no deja éxito. IL31 pierde respuesta confirmada y reinicia antes
de recuperar. Operaciones/planes CANCELLED negativos solo existen en transacciones
con rollback, nunca ejecutados y sin entregas/reservas persistentes. Plan publicado
de fixture no implica d3.publish ni despacho. PATCH cambia digest de tarea D3;
no se promete invariancia global del readset ante efectos de evidencia o cambios ajenos.

## Conservación, limpieza y límites

Final: 259 tareas BACKLOG sintéticas de fixtures/regresiones, cero operaciones,
entregas, outbox, intentos, reservas y reservas de plan. V39 no crea tareas.
Contenedor y volumen propio eliminados sin tocar dev/D4. Logs privados en
`work/d5/postgres/d5-pg-*/isolated-local-edit-results.json`; D2 en `work/docker-audit/`.
No se publican corpus privado, credenciales o logs brutos.

Cuerpos, propietarios, ACL/config de funciones D5 anteriores a V39 y funciones/
triggers public/D2/D3/D4 respecto a V30 se conservan. Coinciden 245 entradas de
cierre D3/D4, documento canónico D4 y 20/27/47/51/55/60/66/72/78 entradas históricas
I4/I5/I6/I8/I10/I12/I14/I16/I18. I19 conserva su estado documental histórico; A49
autoriza esta implementación. 84 hashes nuevos identifican entradas ejecutadas,
incluidos contrato/matriz. Los 392 archivos históricos inventariados y los cuatro
archivos de código congelado coinciden tras ejecutar.
Se comprobaron 142 enlaces locales y formato sin incidencias; el scanner de
publicación revisó 401 archivos de texto sin detectar patrones configurados.
Se revisó el diff; el scanner no sustituye esa revisión.

Semántica de parser según adaptador confiable; etiquetas/razones sintéticas sin
autenticación D6. Se valida concurrencia/recuperación acotada, no escalabilidad,
DDL arbitrario del administrador ni ABA externo sin huella observable.

D5 conserva pendientes IDs reutilizados/transferencias, adopción con trabajo o
procedencia previos, perfil/política, múltiples orígenes y Gentle-AI/routing completo.
Sin proveedores/credenciales reales, activación, promoción, despliegue o ampliación D6.
