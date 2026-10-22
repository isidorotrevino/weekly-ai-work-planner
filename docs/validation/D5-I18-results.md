# D5 I18 — resultado de resolución local de reaparición

Fecha: 2026-10-22. **PASS acotado; D5 abierto.**
[Implementación y autorización A44](../design/D5-I18-LOCAL-REAPPEARANCE-LAB.md) ·
[Resumen portátil y hashes](D5-I18-results.json).

| Campaña nueva | Comando | Resultado |
|---|---|---|
| V30 + V31–V38, base nueva | `python3 -m testing.D5.run_local_reappearance_lab` | 228 pruebas: 21 I4 + 15 I5 + 5 I6 + 27 I8 + 28 I10 + 30 I12 + 32 I14 + 34 I16 + 36 LR01–LR36; cero fallos/errores |
| Python local | `python3 -m unittest discover -s testing/D5 -v` | 51 pruebas; cero fallos/errores |
| D2 independiente | `bash testing/D2/run-docker-audit.sh` | 157 pruebas; cero fallos/errores/omisiones |

PostgreSQL 16.15 (Debian 16.15-1.pgdg12+2), imagen local sin red ni puertos publicados.
El JSON registra imagen, hashes de entrada, tiempo y nombres completos de casos.
Los métodos LR01–LR36 corresponden a la matriz I17. D2 conserva su target histórico;
no se atribuyen esos resultados a V30 ni a campañas HTTPS/procesos D4.

## Matriz LR01–LR36 ejecutada

| Caso | Evidencia observada — PASS |
|---|---|
| LR01 | Destinos I8/I10/I16 y efecto I14 previo; preparación/replay sin escritura protegida y B/L/S separados |
| LR02 | Ámbito/UUID/clave/perfil/política o destino no materializado rechazados; adaptador exige prueba materializada |
| LR03 | L=B rechaza variante local; I12 ordinario sigue funcionando con revisión propia |
| LR04 | Divergencia antes/durante/después de ausencia, con/sin row_version; snapshot actual completo y target histórico conservado |
| LR05 | Observación/ACCEPT/simulación sin aplicación y cadena/recibo CONFLICT incoherentes no prueban ausencia |
| LR06 | Ausencia aplicada a otra versión no sustituye la prueba vigente ni gana por fecha |
| LR07 | Before histórico distinto de última base aplicada: B y base reales se preservan desde cabeza |
| LR08 | Otro snapshot ausente actual permitido reconstruyendo y fijando ambas observaciones |
| LR09 | Solo ADDED no bloqueante con before nulo/after presente; duplicados en antes/después bloquean |
| LR10 | Declaración SAME_SOURCE_ENTITY obligatoria para USE_SOURCE/KEEP_LOCAL; reutilización/no confirmación rechazadas |
| LR11 | Razones de identidad y resolución independientes: blancos Unicode, controles, exceso/tipos inválidos bloqueados |
| LR12 | ACCEPT I5 separado y vigente; revocación/reaceptación invalida pin anterior |
| LR13 | Referencia exacta/versionada; ABA no recupera vigencia |
| LR14 | Revisión propia conjunta obligatoria; no valen dominios I12/I14 ni aceptación de otro manifiesto |
| LR15 | Inmutabilidad, reconstrucción de fuente/prueba y resultado completo; force/texto manual rechazados |
| LR16 | Rechazo y revisión conjunta revocada/reaceptada invalidan paquetes antiguos |
| LR17 | ID largo, Unicode/Markdown/pipes, tachado/anotación y procedencia íntegros |
| LR18 | Proyección inválida bloquea incluso KEEP_LOCAL; NULL local y Objective vacío/guion literales, claims inertes |
| LR19 | USE_SOURCE cambia solo title/description y row_version una vez; prueba/razones presentes en recibo |
| LR20 | S=L con USE_SOURCE: trigger negativo detecta cualquier UPDATE; enlace conserva tarea completa |
| LR21 | KEEP_LOCAL con S igual/distinto de L/B: trigger negativo sin UPDATE; cabeza +1 con projection=S |
| LR22 | S=B y L distinto permiten ambas elecciones completas, sin mezcla |
| LR23 | Edición posterior sin versión, campos ajenos, convergencia y ABA observable bloquean snapshot obsoleto |
| LR24 | Estado, operación y planificación histórica CANCELLED bloquean ambas elecciones; fixtures revertidas |
| LR25 | Lista explícita ordenada, límites/duplicados/única intención; dominios I8/I10/I12/I14/I16 separados |
| LR26 | Paquetes en sesiones reales: un ganador y un conflicto; nueva ausencia invalida cabeza anterior |
| LR27 | Referencia/revisión concurrentes con espera real y validación vigente tras desbloqueo |
| LR28 | Paquete mixto inválido, aborto y fallo tardío revierten tarea/vínculo/cabeza/hecho/auditoría y éxito |
| LR29 | Replay histórico, contenido distinto y ALREADY_APPLIED no restauran texto posterior |
| LR30 | Respuesta perdida, reinicio, recuperación CLI y JSON duplicado rechazado |
| LR31 | Procedencia exacta reutilizada/append-only, ámbito de lectura correcto y tarea local divergente conservada |
| LR32 | USE_SOURCE/convergencia continúan por I8; KEEP_LOCAL divergente exige I14 en cambio posterior, sin override permanente |
| LR33 | Nuevo ciclo exige nueva prueba/version/revisión; revocar revisión histórica no deshace ausencia aplicada |
| LR34 | Rechazos I8/I12/I14 anteriores y funciones históricas intactos |
| LR35 | Roles mínimos/READ COMMITTED/locks cruzados y captura D3; PATCH cambia digest y plan publicado permanece inmutable |
| LR36 | Cero tareas nuevas por resolución, BACKLOG conservado, catálogo y ausencia de activación |

El ensayo inicial tuvo cuatro casos fallidos por fixtures del harness: ausencia no
materializada rechazada ya por adaptador, reutilización del ámbito de una fixture y
limpieza de triggers temporales al terminar su sesión. Se corrigieron las fixtures
y pasaron los cuatro casos en otra base nueva. La campaña completa publicada aquí
se ejecutó después, con código congelado; no se cuentan resultados parciales como
aprobados. V38 y el adaptador no necesitaron relajar el contrato por esos ajustes.

LR20/LR21 instalan un trigger negativo dentro de una transacción revertida y luego
confirman el efecto sin ese trigger; en ambos pasos la tarea queda idéntica.
LR26/LR27/LR35 observan sesiones simultáneas y espera, no solo llamadas secuenciales.
LR28 prueba rollback completo salvo el recibo de conflicto de negocio esperado;
aborto/error estructural no deja éxito. LR30 recupera el recibo tras reinicio.

Las operaciones y planificación CANCELLED negativas solo existen dentro de
transacciones con rollback obligatorio, nunca se ejecutan ni dejan entregas/reservas.
Planes publicados son fixtures de propietario sin despacho, d3.publish o outbox.
LR35 detecta cambio del digest de tarea tras PATCH; no promete invariancia global
del readset para enlaces/evidencia o cambios concurrentes ajenos.

## Conservación, limpieza y límites

La campaña finaliza con 206 tareas BACKLOG sintéticas de fixture y cero operaciones,
entregas, outbox, intentos, reservas y reservas de plan. La resolución no crea tareas;
las filas nuevas de la campaña proceden de fixtures o regresiones de importación
previas. Se eliminó el contenedor y su volumen propio sin tocar dev/D4. Brutos
privados en `work/d5/postgres/d5-pg-*/local-reappearance-results.json`, D2 en
`work/docker-audit/`. No se publican fuentes privadas, credenciales ni logs brutos.

Se conservan cuerpos, propietarios, ACL/config de funciones D5 anteriores a V38 y
funciones/triggers public/D2/D3/D4 respecto a V30. Coinciden 245 entradas de cierre
D3/D4, documento canónico D4 y las 20/27/47/51/55/60/66/72 entradas históricas
I4/I5/I6/I8/I10/I12/I14/I16. I17 conserva su estado documental histórico y A44
autoriza esta implementación. Los 78 hashes nuevos corresponden a los archivos
ejecutados, incluidos contrato/matriz. Los 383 archivos históricos capturados y
los cuatro archivos de código congelado coinciden tras la ejecución.
Se comprobaron 136 enlaces locales y formato sin incidencias; el scanner de
publicación revisó 392 archivos de texto sin detectar patrones configurados.
Se revisó el diff; el scanner no sustituye esa revisión.

La semántica de parser depende del adaptador confiable; razones/etiquetas son
claims sintéticos, no identidad autenticada D6. Concurrencia/recuperación acotadas,
sin pruebas de escalabilidad ni protección frente a DDL arbitrario de administrador
o ABA externo sin huella observable.

D5 sigue abierto: resolución local sin cambio revisable del origen, IDs reutilizados
para otra entidad, transferencias, adopción con procedencia/trabajo previos,
perfil/política, múltiples orígenes y Gentle-AI/routing completo conservan pendientes.
Sin proveedores/credenciales reales, activación, promoción, despliegue ni ampliación D6.
