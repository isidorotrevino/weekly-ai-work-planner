# D5 I33-F — matriz durable de fallos y reinicio

Fecha: **2026-10-23**, Europe/Madrid. [Contrato F](D5-I33-DURABLE-INTEGRATION-DESIGN.md).
**48 casos DESIGN_NOT_EXECUTED; implementación y ejecución no autorizadas.**

English: design matrix only. New durable fixture state, independently persistent
remote double and explicit settle-or-close are proposed, not implemented capabilities.

Cada DF debe registrar IDs de tests efectivamente ejecutados, configuración/hash,
rol del proceso, punto alcanzado, exitcode, snapshots/digests y resultado esperado.
C significa CLIENT, P doble REMOTE, A captura I26. SIGKILL solo a hijo propio tras
señal por pipe. I/O incierto se inyecta como fallo controlado distinto del SIGKILL.
No sleeps para resolver carreras, fixtures sintéticas y reloj explícito. Abrir nuevo
objeto en el mismo proceso no cuenta como reinicio; los casos de reinicio usan otro
proceso sin memoria heredada del cliente. El harness puede conservar controles y
oráculos de prueba, nunca usarlos para reconstruir autoridad perdida.

| ID | GI / UI relacionados | Proceso/punto o entrada | Oráculo exigido |
|---|---|---|---|
| DF01 | GI33 / UI01–UI07 | Inventario y cambio de input | Código/config/esquema/capabilities/parser/árbol real ligados a campaña; input cambiado marca STALE_INPUTS; histórico intacto |
| DF02 | GI34 / UI08–UI12 | Preservación y contabilidad | Cierres/aceptación/targets/hashes intactos; nuevos, regresiones y hashes históricos separados; UI+DF no duplican tests |
| DF03 | GI38 / UI13 | A confirmado, C aún sin importación; reiniciar C | Mismo pin/bytes/ámbito/grado, sin aceptación automática; A no se modifica |
| DF04 | GI38 / UI14 | Importar commit no alcanzable, hash/evento/ámbito distinto | Bloqueo antes de fuente/efecto; no elegir otra captura por fecha |
| DF05 | GI38 / UI14 | Perfil desconocido/ambigüedad/checklist o Docs | Preview/bloqueo, cero efecto; no interpretar envelope relacional como registro |
| DF06 | GI38 / UI15 | SOURCE/EVALUATION/EFFECT/PROJECTION | Revisiones durable nuevas independientes; falta/revocación de una no se reemplaza con ACCEPT de otra |
| DF07 | GI38 / UI22–UI24 | Creación interrumpida antes de HEAD | INITIALIZATION_INCOMPLETE al abrir; no génesis automática ni adopción por ruta |
| DF08 | GI38 / UI23 | C kill antes de escribir objeto F1/F2 | HEAD previo íntegro; ningún comando/manifest/revisión parcial |
| DF09 | GI38 / UI23 | C kill tras objeto durable antes de HEAD | Huérfano ignorado; reapertura no lo promueve ni acepta fuente |
| DF10 | GI38 / UI23 | C kill con HEAD temporal previo a replace | HEAD anterior; temporal no es autoridad ni recibo |
| DF11 | GI38 / UI23 | C replace completado, fsync directorio falla | COMMIT_UNKNOWN; no llamadas P hasta recuperación validada/fsync; fallo persistente no confirma |
| DF12 | GI38 / UI21–UI23 | C kill tras fsync HEAD antes de respuesta | Proceso nuevo recupera mismo recibo histórico; otro request bajo command_id bloquea |
| DF13 | GI38 / UI16/UI22 | C kill antes/después de commit F3 | Entidad+mapping+base+procedencia+recibo todos o ninguno; replay no reaplica |
| DF14 | GI38 / UI17/UI22 | C kill entre F3 y F4 | Efecto local único y fase pendiente, cero efecto P hasta revisión PROJECTION |
| DF15 | GI38 / UI18/UI23 | C intento F5 con objeto huérfano/HEAD previo | No emitir ticket no confirmado; P vacío; recibo local no prueba efecto remoto |
| DF16 | GI38 / UI18/UI22 | C kill tras F5 confirmado antes de llamada P | Reinicio lista UNKNOWN; no autoenvío; lookup vacío mantiene UNKNOWN |
| DF17 | GI38 / UI19/UI22 | P kill antes de su commit de efecto F6 | C UNKNOWN; P reabre íntegro sin efecto; cierre explícito puede concluir NO_EFFECT |
| DF18 | GI38 / UI19/UI23 | P objeto durable, sin replace HEAD | Huérfano P no prueba efecto; settle_or_close tras reabrir confirma cierre desde cabeza válida |
| DF19 | GI38 / UI19/UI23 | P replace con fsync incierto | No prueba concluyente hasta reabrir/fsync; C UNKNOWN; no retry por excepción |
| DF20 | GI38 / UI19/UI22 | P efecto+ticket fsync, respuesta perdida y C muerto | Proceso C nuevo concilia prueba exacta de P superviviente; un efecto, sin reenvío |
| DF21 | GI38 / UI19/UI23 | C recibe prueba, kill antes de commit F7 | P conserva prueba; C UNKNOWN; otra consulta explícita recupera mismo efecto |
| DF22 | GI38 / UI21–UI23 | C F7 fsync, respuesta al operador perdida | Replay histórico conserva recibo; cambio posterior local/remoto no restaura payload viejo |
| DF23 | GI38 / UI20/UI24 | Ticket ausente / lookup vacío / eventual vacío | UNKNOWN estable; ninguna espera ni lectura cero acredita no efecto |
| DF24 | GI38 / UI22 | settle_or_close ticket ausente y llegada tardía | Tombstone durable CLOSED_NO_EFFECT; execute tardío rechaza sin efecto, incluso tras reiniciar P |
| DF25 | GI39 / UI32/UI33 | execute y settle_or_close desde dos procesos | Bajo lock P gana efecto o cierre, nunca ambos; prueba terminal estable y un solo destino |
| DF26 | GI38 / UI20 | Prueba ticket/hash/key/store_id equivocada o múltiples identidades | CONFLICT persistente; no adoptar primer/último resultado ni borrar conflicto con otro paquete |
| DF27 | GI38 / UI20/UI21 | Rechazo concluyente/429 conocido, retry explícito | Nuevo ticket, mismo paquete/clave/payload, tres intentos máximos; tick mínimo válido y guardas actuales |
| DF28 | GI38 / UI20 | Timeout/429 ambiguo o intento previo aún UNKNOWN | Ningún retry ni nuevo envío del binding, aun con command_id/manifest nuevo |
| DF29 | GI38 / UI24 | HEAD inválido/objeto alcanzable ausente/cadena rota | CORRUPT/RECOVERY_REQUIRED; no fallback a padre ni génesis; evidencia conservada |
| DF30 | GI38 / UI24 | Marca/role/store_id/schema extra/JSON duplicado/symlink | Apertura bloqueada; no migración automática ni lectura de rutas externas |
| DF31 | GI38 / UI24 | Reiniciar C con tick persistido, luego avanzar explícitamente | Tick no retrocede; caducidad durante parada solo se representa por avance; bloquea evaluación/efecto/envío al cruzar límite |
| DF32 | GI39 / UI26/UI27 | Selección de origen/perfil/política/revisión A→B→A | Generaciones/revisiones exactas impiden revivir manifest; mapping histórico intacto |
| DF33 | GI39 / UI27/UI28 | Cuenta/observación/revocación/horizonte | Todas restricciones vigentes de cuenta única; no sumas ni conversiones; nuevo hecho o reloj invalida sin consumo/reserva |
| DF34 | GI39 / UI29 | Edición de TASK/campo ajeno tras preparar F4 | C dueño detecta snapshot obsoleto antes F5; ningún envío bajo copia vieja |
| DF35 | GI39 / UI30 | Revocar antes F5 vs después de su emisión durable | Antes bloquea; después permite hecho en vuelo y registra STALE, sin fingir rollback ni nueva autorización de recuperación |
| DF36 | GI39 / UI31 | Editar P entre preparación y CAS, incluido ABA | UPDATE rechaza base/version/hash obsoletos y conserva campos ajenos; nuevo paquete/revisión exigidos |
| DF37 | GI39 / UI31/UI33 | CREATE repetido/tickets concurrentes misma creation_key | Índice único durable, sin adopción; mismo ticket devuelve prueba, hash distinto bloquea; reinicio no duplica destino |
| DF38 | GI39 / UI32/UI33 | Dos C con mismo expected_head, incluso revisión vs efecto | Una transición confirma; otra CONFLICT_HEAD sin rebase; ninguna revisión/recibo perdido |
| DF39 | GI39 / UI32/UI33 | Respuesta F7 vs consulta/concurrencia de revisión | Ledger CAS impide sobrescritura; prueba perdida por CAS exige consulta explícita; preserva STALE/conflicto |
| DF40 | GI39 / UI33 | Kill del dueño de flock, otro escritor preparado | Lock se libera por muerte; segundo valida HEAD nuevo; timeout no concede propiedad ni permite saltar CAS |
| DF41 | GI40 / UI35/UI36 | Auditoría de recorrido completo y negativos | Cero HTTP/SQL/SDK/CLI reales, operaciones/intentos operativos, consumo/reservas/activación; tickets P contados solo como fixture |
| DF42 | GI40 / UI37/UI38 | Kill/reinicio C y P, cierre del harness | Todos hijos/hilos propios terminados, exitcodes identificados; tres raíces propias eliminadas, sentinel hermano intacto |
| DF43 | GI40 / UI38 | Marca incoherente/symlink al limpiar | No borrado por heurística; residuo reportado; sin tocar dev/D4/evidencia ajena |
| DF44 | GI40 / UI39 | Límites de conteo/bytes/historia/disco lógico | Siguiente entrada bloquea sin truncar ni efecto parcial; tamaños completos y presupuesto reducido se informan separados |
| DF45 | GI40 / UI39 | Capacidad restante con intentos/consultas pendientes | Headroom por todos los resultados pendientes protegido frente a otro escritor; no emitir sin sitio para resultado; error físico → UNKNOWN |
| DF46 | GI33/GI38 / UI04/UI15 | Comparación controlada con modelos I24/I28/I32 | Misma identidad/proyección/guardas/revisiones/cuota/replay en casos declarados; divergencias durables/cierre ticket explícitas, sin afirmar paridad completa |
| DF47 | GI40 / UI36/UI40 | Errores/recibos/reporte y reapertura | Sin texto fuente, cuerpos privados ni paths en salida; historical separado de CURRENT/STALE; reopen no envía/consulta/cierra solo |
| DF48 | GI34/GI40 / UI11/UI40 | Informe de campaña y exclusiones | Mapa UI/DF→tests reales, regresiones propias sin sumas históricas; R/Docs y siete R reales pendientes; G01–G07 abiertos |

## Expansión requerida de failpoints

DF08–DF12 parametrizan el protocolo de commit común para importación, SOURCE,
EVALUATION, EFFECT, PROJECTION, emisión de intento, consumo de consulta y F7.
DF17–DF20 parametrizan CREATE, UPDATE y cierre de ticket en REMOTE; DF13 cubre
especialmente la atomicidad del efecto local. Debe registrarse cada combinación
que realmente corra; un DF PASS parcial no da por ejecutadas las demás. Los casos
con presupuesto reducido se etiquetan como tales, sin afirmar límite completo.

La implementación autorizada futura deberá probar estado antes/después mediante
lector independiente del escritor: parseo de archivos, hashes/cadena/HEAD y conteos
exactos, no solo llamadas al mismo método que produjo el resultado. Controlar
barreras antes de CAS/replace/envío y después de fsync, sin assertions sobre timing.
Una caída C conserva P/A; los tests que pierdan también P deben declararlo como
corrupción/pérdida y esperar bloqueo, no éxito de recuperación.

## Cobertura y puerta

Los **33 UI de base** se reinterpretan en el modelo durable nuevo, sin alterar sus
obligaciones de identidad, evidencia y auditoría; UI16 ya no se limita a memoria.
**UI22–UI24/UI33/UI38** se desglosan aquí. **UI25/UI34 (R)** no se ejecutan. DF no
confiere aprobación a UI, no se suma a su cuenta como tests por defecto ni cambia
el estado 30/35 previo. GI38/GI39 integrados globales continúan pendientes por
alcance R/otras exclusiones; GI40 se evaluará sobre recursos y campaña autorizados.

El contrato F queda preparado para revisión de diseño y alcance T durable.
Aprobar solo diseño no inicia implementación; publicación requiere SHA autorizado
independiente. Sin proveedores/credenciales reales, consumo/reservas, activación,
promoción, despliegue ni D6. No se deduce recuperación integrada de PASS aislados.
