# D5 I47 — matriz de revisión de suficiencia y delta

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base: `585c5e91c2072e656f7296fd2f04af3f1fc7d1c1`.
[Contrato](D5-I47-SUFFICIENCY-DELTA-DESIGN.md) · [Selección A](D5-I47-NEXT-CUT-SCOPE.md) · [Sello y candidatos completos](../validation/D5-I47-design-review.json).

**40 UI, 84 subcláusulas, 14 SR y 12 DC: REVIEW_NOT_EXECUTED. Cero nuevos dictámenes o tests.**
Los dictámenes de la columna «I40 histórico» solo reproducen el snapshot I40; no son resultados de I47. Los candidatos se extraen de objetivos UI parciales declarados por HC/HF/IC y de sus IDs registrados: no acreditan subcláusulas. La ausencia de candidatos nuevos no acredita ausencia de soporte histórico ni que nada haya cambiado.

## Plan por UI

| UI | GI / modo original | I40 histórico | Subcláusulas | Candidatos declarados HC/HF/IC | Foco documental previsto |
|---|---|---|---:|---|---|
| UI01 | GI33 / M | PARTIAL | 2 | I42: 1, I44: 1, I46: 1 | Contrastar inventario, comando y vínculo escenario/campaña; distinguir código/config embebida de versiones externas no registradas. |
| UI02 | GI33 / M | SUPPORTS_BOUNDED | 2 | I42: 1, I44: 1, I46: 1 | Comprobar invalidación por cambio y por input nuevo; explicar I34 histórico MATCH con discovery actual STALE. |
| UI03 | GI33 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 0, I46: 0 | Seguir pins de perfil/política/observación y generaciones en T; en R declarar ausencia de EVALUATION sin equivalencia ficticia. |
| UI04 | GI33 / M | PARTIAL | 2 | I42: 1, I44: 1, I46: 1 | Desglosar escenario/frontera/oráculo/resultado; detectar mapa completo con caso parcial o detalle empírico ausente. |
| UI05 | GI33 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 0, I46: 0 | Seguir bytes/IDs/procedencia entre captura I26 y T; distinguir captura JSON propia R y Docs OBSERVED_EXPORT pendiente. |
| UI06 | GI33 / M | SUPPORTS_BOUNDED | 2 | I42: 1, I44: 0, I46: 0 | Delimitar API de fixture y capacidad real; no elevar CAS/cierre de ticket o versión declarada a capacidad Plane. |
| UI07 | GI33 / M | SUPPORTS_BOUNDED | 2 | I42: 1, I44: 0, I46: 0 | Contrastar documentos emisores con los actuales; separar cambios de índices de cambios ejecutables y raw ausente. |
| UI08 | GI34 / M | SUPPORTS_BOUNDED | 2 | I42: 1, I44: 1, I46: 1 | Enumerar preservación pública de cierres/A52 y sus límites D1/D2; no inferir inspección de dev/D4 operativo. |
| UI09 | GI34 / M | PARTIAL | 2 | I42: 1, I44: 1, I46: 1 | Identificar targets/comandos/versiones de cada grupo efectivamente registrados; ausencias quedan NOT_RECORDED. |
| UI10 | GI34 / M | SUPPORTS_BOUNDED | 2 | I42: 1, I44: 1, I46: 1 | Verificar IDs distintos y campañas separadas; intersección de 281 no suma 602 y casos/subcasos no añaden tests. |
| UI11 | GI34 / M | SUPPORTS_BOUNDED | 2 | I42: 1, I44: 1, I46: 1 | Separar nuevos/regresiones ejecutadas y referencias históricas por hash; SQL/Java no reejecutados. |
| UI12 | GI34 / M | SUPPORTS_BOUNDED | 2 | I42: 2, I44: 2, I46: 2 | Identificar recursos de T/R y regresiones; no atribuir persistencia al modelo volátil por recuperación I26. |
| UI13 | GI38 / M | SUPPORTS_BOUNDED | 3 | I42: 0, I44: 0, I46: 0 | Localizar fallo antes/después de importación I26 a T y oráculo exacto; no confundir cursor capturado con fuente aceptada. |
| UI14 | GI38 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 0, I46: 0 | Leer negativos de captura/perfil/hash/ámbito y comprobar bloqueo de efectos y ausencia de reparación silenciosa. |
| UI15 | GI38 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 24, I46: 0 | Contrastar SOURCE/EVALUATION/EFFECT/PROJECTION T y SOURCE/BATCH/PROJECTION R; autoridad de revisión independiente. |
| UI16 | GI38 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 2, I46: 0 | Verificar commit local y recibo juntos, fallos antes/después y replay histórico sin restauración o doble efecto. |
| UI17 | GI38 / M | PARTIAL | 2 | I42: 0, I44: 2, I46: 0 | Examinar corte entre efecto local, binding y proyección; fase pendiente durable sin recibo final ficticio. |
| UI18 | GI38 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 6, I46: 0 | Verificar guardas antes del ISSUE y ticket UNKNOWN durable antes de REMOTE; distinguir NOT_SENT de efecto posible. |
| UI19 | GI38 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 6, I46: 0 | Seguir respuesta perdida y conciliación explícita con ticket/identidad/hash; prueba independiente de efecto único. |
| UI20 | GI38 / M | PARTIAL | 3 | I42: 0, I44: 0, I46: 0 | Leer lookup vacío/múltiple/incompatible y 429; acreditar incertidumbre persistente y retry solo con no efecto concluyente. |
| UI21 | GI38 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 38, I46: 2 | Contrastar command_id/request_hash, replay histórico y conflicto de payload; ningún rebobinado tras cambios posteriores. |
| UI22 | GI38 / F | PARTIAL | 2 | I42: 0, I44: 38, I46: 0 | Expandir cada frontera y rol a puntos antes/después de crash/reinicio; no aceptar contador SIGKILL como cobertura completa. |
| UI23 | GI38 / F | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 38, I46: 0 | Verificar COMMIT_UNKNOWN/fsync, bloqueo de handle y reopen; ACK o excepción no prueban rollback o éxito. |
| UI24 | GI38 / F | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 0, I46: 0 | Leer corrupción/cadena/schema/huérfanos y reloj persistido; no génesis, fallback o frescura comercial inventada. |
| UI25 | GI38 / R | SUPPORTS_BOUNDED | 3 | I42: 0, I44: 34, I46: 0 | Seguir lote R íntegro, recibo y generación exactos hasta TASK seleccionada y proyección; sin atomicidad remota distribuida. |
| UI26 | GI39 / M | PARTIAL | 2 | I42: 0, I44: 0, I46: 0 | Contrastar fuente/selección/revisiones antes de efecto, incluidos cambios ABA; copia vieja no conserva autoridad. |
| UI27 | GI39 / M | PARTIAL | 2 | I42: 0, I44: 0, I46: 0 | Examinar perfil/política/observación T y revocación/ABA; declarar diferencias de R sin forzar contrato Markdown. |
| UI28 | GI39 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 0, I46: 0 | Leer caducidad y horizonte con generación igual y reloj lógico persistido; no permiso operacional o renovación al reiniciar. |
| UI29 | GI39 / M | SUPPORTS_BOUNDED | 2 | I42: 0, I44: 0, I46: 0 | Contrastar dueño del snapshot local T/R frente a paquete preparado; justificar sustitución de objetos volátiles I28. |
| UI30 | GI39 / M | PARTIAL | 2 | I42: 6, I44: 0, I46: 0 | Leer cambio/revocación durante envío y conciliación; conservar efecto histórico, STALE y UNKNOWN según frontera. |
| UI31 | GI39 / M | PARTIAL | 2 | I42: 8, I44: 0, I46: 28 | Examinar cambio remoto y ABA frente a UPDATE/CAS; campos ajenos y base exacta, sin GET seguido de escritura incondicional. |
| UI32 | GI39 / M | PARTIAL | 2 | I42: 14, I44: 0, I46: 28 | Identificar ordenaciones forzadas por barreras y resultados CAS; distinguir carrera real de interleaving secuencial. |
| UI33 | GI39 / F | PARTIAL | 2 | I42: 13, I44: 0, I46: 24 | Verificar procesos sobre mismo estado, lock/CAS/revisiones/intentos; incluir oráculo independiente y resultados perdedores. |
| UI34 | GI39 / R | PARTIAL | 3 | I42: 10, I44: 0, I46: 14 | Contrastar cambios locales/relacionales y nuevo lote no-op frente a snapshot R; incertidumbre previa bloquea nuevo envío. |
| UI35 | GI40 / M | SUPPORTS_BOUNDED | 2 | I42: 1, I44: 1, I46: 1 | Separar declaraciones de cero actividad, guardas estáticas y observaciones; no elegibilidad como ejecución o reserva. |
| UI36 | GI40 / M | SUPPORTS_BOUNDED | 2 | I42: 1, I44: 1, I46: 1 | Comprobar alcance de lectura/comandos/salida saneada; cero proveedores reales no equivale a revisión exhaustiva de seguridad. |
| UI37 | GI40 / M | SUPPORTS_BOUNDED | 2 | I42: 1, I44: 1, I46: 1 | Leer creación/terminación de hilos y ownership de raíces/sentinels; regresiones y recursos nuevos separados. |
| UI38 | GI40 / F | SUPPORTS_BOUNDED | 2 | I42: 2, I44: 1, I46: 1 | Contrastar tabla de hijos/exitcodes/raíces y limpieza selectiva con harness; no inferir estado operativo dev/D4. |
| UI39 | GI40 / M | SUPPORTS_BOUNDED | 2 | I42: 2, I44: 2, I46: 2 | Enumerar límites realmente ejercitados y presupuestos reducidos; no capacidad simultánea máxima o benchmark. |
| UI40 | GI40 / M | SUPPORTS_BOUNDED | 2 | I42: 2, I44: 2, I46: 2 | Contrastar resumen, casos no ejecutados, aplicabilidad, raw ausente y bloqueos; conservar D5/G01–G07 abiertos. |

Cada conjunto candidato se resuelve íntegramente en el sello: campaña/caso/test ID/raw/mapa y recorrido. Antes de valorar una cláusula se localizará el oráculo efectivo y el campo/índice del raw, o se conservará NOT_RECORDED. No usar el conteo de candidatos como medida de suficiencia.

## Inventario original de subcláusulas

Los 84 IDs y textos se conservan de I40. Estado de lectura nuevo: REVIEW_NOT_EXECUTED en todas las filas; tipo de delta aún no asignado.

| ID | Obligación parcial I40 | I40 histórico | Controles de delta previstos |
|---|---|---|---|
| UI01.1 | Bytes de código/config/harness/perfil/esquema | SUPPORTS_BOUNDED | DC01, DC11, DC12 |
| UI01.2 | Entorno/comando/run_id y resultado por escenario | PARTIAL | DC01, DC11, DC12 |
| UI02.1 | Cambio de bytes/config o incorporación pertinente | SUPPORTS_BOUNDED | DC01, DC12 |
| UI02.2 | Historia conservada y aplicabilidad separada | SUPPORTS_BOUNDED | DC01, DC12 |
| UI03.1 | Perfil/política/observación y revisiones propias | SUPPORTS_BOUNDED | DC01, DC12 |
| UI03.2 | Versión o fecha no reemplaza generación/hash | SUPPORTS_BOUNDED | DC01, DC12 |
| UI04.1 | Relación completa escenario/frontera/inputs/oráculo/resultado | PARTIAL | DC01, DC09, DC12 |
| UI04.2 | Faltante/incompatible no produce PASS heredado | SUPPORTS_BOUNDED | DC01, DC09, DC12 |
| UI05.1 | Bytes/evento/commit I26 alcanzables | SUPPORTS_BOUNDED | DC01, DC02, DC12 |
| UI05.2 | Cursor no acepta y OBSERVED_EXPORT no se eleva | SUPPORTS_BOUNDED | DC01, DC02, DC12 |
| UI06.1 | API de fixture frente a código y capacidades reales | SUPPORTS_BOUNDED | DC01, DC02, DC11, DC12 |
| UI06.2 | Versión declarada no es atestación | SUPPORTS_BOUNDED | DC01, DC02, DC11, DC12 |
| UI07.1 | Cambio de índice explicado aparte | SUPPORTS_BOUNDED | DC01, DC11, DC12 |
| UI07.2 | Historia íntegra y aplicabilidad ejecutable | SUPPORTS_BOUNDED | DC01, DC11, DC12 |
| UI08.1 | Cierres/A52 y entradas públicas preservados | SUPPORTS_BOUNDED | DC10, DC12 |
| UI08.2 | Cambios documentales permitidos identificados | SUPPORTS_BOUNDED | DC10, DC12 |
| UI09.1 | Grupos y targets separados | SUPPORTS_BOUNDED | DC10, DC12 |
| UI09.2 | Comandos/versiones propios para todos los grupos | PARTIAL | DC10, DC12 |
| UI10.1 | IDs distintos dentro de campaña | SUPPORTS_BOUNDED | DC10, DC12 |
| UI10.2 | No sumar ejecuciones previas y subcasos | SUPPORTS_BOUNDED | DC10, DC12 |
| UI11.1 | Nuevos, regresiones y verificaciones históricas | SUPPORTS_BOUNDED | DC10, DC12 |
| UI11.2 | SQL/D2–D4 no ejecutados visibles | SUPPORTS_BOUNDED | DC10, DC12 |
| UI12.1 | Recursos nuevos frente a regresiones | SUPPORTS_BOUNDED | DC10, DC12 |
| UI12.2 | Recuperación I26 no es persistencia de objetos volátiles | SUPPORTS_BOUNDED | DC10, DC12 |
| UI13.1 | A confirmado, C reiniciado sin aceptación automática | SUPPORTS_BOUNDED | DC02, DC11, DC12 |
| UI13.2 | Fallos antes/después de importación y repetición | SUPPORTS_BOUNDED | DC02, DC11, DC12 |
| UI13.3 | Cursor/captura frente a referencia aceptada | SUPPORTS_BOUNDED | DC02, DC11, DC12 |
| UI14.1 | Perfil/ámbito/pin/hash incompatibles | SUPPORTS_BOUNDED | DC02, DC11, DC12 |
| UI14.2 | Sin reparación o elección silenciosa | SUPPORTS_BOUNDED | DC02, DC11, DC12 |
| UI15.1 | Revisiones independientes y pins exactos | SUPPORTS_BOUNDED | DC02, DC05, DC11, DC12 |
| UI15.2 | Revocación/reemplazo no transferibles | SUPPORTS_BOUNDED | DC02, DC05, DC11, DC12 |
| UI16.1 | Efecto y evidencia local juntos o ninguno | SUPPORTS_BOUNDED | DC05, DC06, DC09, DC11, DC12 |
| UI16.2 | Respuesta perdida y replay sin duplicado/rewind | SUPPORTS_BOUNDED | DC05, DC06, DC09, DC11, DC12 |
| UI17.1 | Estado intermedio local sin binding/proyección/envío | SUPPORTS_BOUNDED | DC06, DC09, DC11, DC12 |
| UI17.2 | Caída abrupta precisamente entre F3 y F4 | NOT_ESTABLISHED | DC06, DC09, DC11, DC12 |
| UI18.1 | Guardas antes de ISSUE y ticket durable antes de entrega | SUPPORTS_BOUNDED | DC03, DC06, DC07, DC08, DC11, DC12 |
| UI18.2 | Intento posible conserva UNKNOWN y no retry ciego | SUPPORTS_BOUNDED | DC03, DC06, DC07, DC08, DC11, DC12 |
| UI19.1 | Respuesta perdida y prueba correlacionada | SUPPORTS_BOUNDED | DC03, DC06, DC07, DC08, DC09, DC11, DC12 |
| UI19.2 | Un efecto sin restaurar payload viejo | SUPPORTS_BOUNDED | DC03, DC06, DC07, DC08, DC09, DC11, DC12 |
| UI20.1 | Lookup vacío conserva incertidumbre | SUPPORTS_BOUNDED | DC03, DC08, DC11, DC12 |
| UI20.2 | Prueba incompatible mantiene conflicto | SUPPORTS_BOUNDED | DC03, DC08, DC11, DC12 |
| UI20.3 | Múltiples coincidencias y 429 ambiguo específicos en T/R | PARTIAL | DC03, DC08, DC11, DC12 |
| UI21.1 | Mismo comando/hash histórico | SUPPORTS_BOUNDED | DC03, DC05, DC06, DC07, DC08, DC09, DC11, DC12 |
| UI21.2 | Replay tras cambios no restaura cabezas/datos | SUPPORTS_BOUNDED | DC03, DC05, DC06, DC07, DC08, DC09, DC11, DC12 |
| UI22.1 | Procesos nuevos y fallos antes/después de commits seleccionados | SUPPORTS_BOUNDED | DC05, DC06, DC09, DC11, DC12 |
| UI22.2 | Cada frontera sin excepciones y toda parametrización empírica | PARTIAL | DC05, DC06, DC09, DC11, DC12 |
| UI23.1 | Commit incierto bloquea handle hasta reapertura validada/fsync | SUPPORTS_BOUNDED | DC05, DC06, DC09, DC11, DC12 |
| UI23.2 | ACK/excepción no deciden efecto o rollback | SUPPORTS_BOUNDED | DC05, DC06, DC09, DC11, DC12 |
| UI24.1 | Corrupción/schema incompleto bloquea sin reconstruir | SUPPORTS_BOUNDED | DC11, DC12 |
| UI24.2 | Reloj no reinicia frescura | SUPPORTS_BOUNDED | DC11, DC12 |
| UI25.1 | Lote íntegro, tipos, campos y relaciones explícitas | SUPPORTS_BOUNDED | DC02, DC05, DC06, DC11, DC12 |
| UI25.2 | Selección TASK desde recibo/generación exactos | SUPPORTS_BOUNDED | DC02, DC05, DC06, DC11, DC12 |
| UI25.3 | Proyección permitida y resultado remoto parcial | SUPPORTS_BOUNDED | DC02, DC05, DC06, DC11, DC12 |
| UI26.1 | Origen/selección/revisión antes del efecto invalidan copia | SUPPORTS_BOUNDED | DC11, DC12 |
| UI26.2 | Origen cambiante concurrente con efecto en proceso | PARTIAL | DC11, DC12 |
| UI27.1 | Perfil/política/observación/revocación/ABA invalida | SUPPORTS_BOUNDED | DC11, DC12 |
| UI27.2 | Cambios durante confirmación durable | PARTIAL | DC11, DC12 |
| UI28.1 | Caducidad/horizonte con generación igual | SUPPORTS_BOUNDED | DC11, DC12 |
| UI28.2 | Sin capacidad, frescura o permiso operacional | SUPPORTS_BOUNDED | DC11, DC12 |
| UI29.1 | Snapshot del dueño local obsoleto antes de envío | SUPPORTS_BOUNDED | DC02, DC11, DC12 |
| UI29.2 | Relación con el contrato original | SUPPORTS_BOUNDED | DC02, DC11, DC12 |
| UI30.1 | Revocación antes/después de ISSUE preserva hecho y STALE | SUPPORTS_BOUNDED | DC03, DC09, DC11, DC12 |
| UI30.2 | Revocación o edición intercalada realmente durante llamada remota | PARTIAL | DC03, DC09, DC11, DC12 |
| UI31.1 | Edición remota previa, ABA y conservación de campos ajenos | SUPPORTS_BOUNDED | DC04, DC07, DC08, DC09, DC11, DC12 |
| UI31.2 | Edición durante UPDATE compitiendo en REMOTE | PARTIAL | DC04, DC07, DC08, DC09, DC11, DC12 |
| UI32.1 | Paquetes/efecto/revisión y execute/cierre con procesos | SUPPORTS_BOUNDED | DC03, DC04, DC07, DC08, DC09, DC11, DC12 |
| UI32.2 | Respuesta frente a conciliación/revisión con barreras propias | NOT_ESTABLISHED | DC03, DC04, DC07, DC08, DC09, DC11, DC12 |
| UI33.1 | Mismo estado durable: CAS y lock recuperado tras muerte | SUPPORTS_BOUNDED | DC03, DC04, DC07, DC08, DC09, DC11, DC12 |
| UI33.2 | Dos tickets CREATE/ISSUE simultáneos sin duplicar intento | PARTIAL | DC03, DC04, DC07, DC08, DC09, DC11, DC12 |
| UI34.1 | Cambio de entidad/relación/no-op invalida lote/snapshot entero | SUPPORTS_BOUNDED | DC02, DC03, DC04, DC07, DC08, DC09, DC11, DC12 |
| UI34.2 | Ticket previo incierto sobrevive a lote nuevo | SUPPORTS_BOUNDED | DC02, DC03, DC04, DC07, DC08, DC09, DC11, DC12 |
| UI34.3 | Concurrencia de toda variación relacional con entrega | PARTIAL | DC02, DC03, DC04, DC07, DC08, DC09, DC11, DC12 |
| UI35.1 | Cero ejecución/consumo/reservas dentro del alcance autorizado | SUPPORTS_BOUNDED | DC10, DC12 |
| UI35.2 | Separación de intentos de fixture | SUPPORTS_BOUNDED | DC10, DC12 |
| UI36.1 | Ausencia de red/SDK/CLI real en recorridos inspeccionados | SUPPORTS_BOUNDED | DC10, DC12 |
| UI36.2 | Salida pública saneada | SUPPORTS_BOUNDED | DC10, DC12 |
| UI37.1 | Recursos e hilos propios y de regresión terminados | SUPPORTS_BOUNDED | DC10, DC12 |
| UI37.2 | Limpieza solo de raíz propia y sentinel | SUPPORTS_BOUNDED | DC10, DC12 |
| UI38.1 | Hijos de caída/reinicio y raíces de CLIENT/REMOTE propios | SUPPORTS_BOUNDED | DC09, DC10, DC12 |
| UI38.2 | Dev/D4 intactos dentro del alcance comprobado | SUPPORTS_BOUNDED | DC09, DC10, DC12 |
| UI39.1 | Límites y headroom bloquean antes de emisión/efecto | SUPPORTS_BOUNDED | DC01, DC10, DC11, DC12 |
| UI39.2 | No presentar presupuestos reducidos como tamaño completo | SUPPORTS_BOUNDED | DC01, DC10, DC11, DC12 |
| UI40.1 | Informe distingue lo ejecutado/no ejecutado y aplicabilidad | SUPPORTS_BOUNDED | DC01, DC10, DC11, DC12 |
| UI40.2 | Conservación de pendientes globales y A52 | SUPPORTS_BOUNDED | DC01, DC10, DC11, DC12 |

## SR01–SR14 conservados

Los controles SR no son tests. El sello conserva su baseline I40 separado del plan nuevo.

| SR | GI | Foco | Controles de delta |
|---|---|---|---|
| SR01 | GI33/GI34 | Autoridad, versiones y continuidad | DC02, DC07, DC08, DC12 |
| SR02 | GI33 | Inventario y aplicabilidad | DC01, DC12 |
| SR03 | GI33 | Fuerza y trazabilidad de evidencia | DC01, DC11, DC12 |
| SR04 | GI33/GI34/GI38/GI39/GI40 | Exhaustividad por cláusula y recorrido | DC02, DC11, DC12 |
| SR05 | GI33/GI38/GI39 | Escenario y oráculo | DC03, DC04, DC05, DC06, DC07, DC08, DC09 |
| SR06 | GI38 | Fronteras y puntos de fallo | DC05, DC06, DC09 |
| SR07 | GI38/GI39 | Incertidumbre y recuperación | DC03, DC06, DC08 |
| SR08 | GI39 | Ordenaciones concurrentes y ABA | DC03, DC04, DC07, DC09 |
| SR09 | GI38/GI39 | Autoridad R y transacciones | DC02, DC06, DC08 |
| SR10 | GI33/GI40 | Elegibilidad y autoridad operacional | DC01, DC02, DC11 |
| SR11 | GI34 | Targets y contabilidad | DC10 |
| SR12 | GI34/GI40 | Recursos y preservación pública | DC10 |
| SR13 | GI33/GI40 | Límites, privacidad y contexto | DC01, DC09, DC10, DC11 |
| SR14 | GI33/GI34/GI38/GI39/GI40 | Dictamen y decisiones posteriores | DC12 |

## DC01–DC12 específicos

Estos doce controles hacen explícitas las comprobaciones del contrato; no añaden cláusulas originales, tests o dictámenes.

| DC | Foco | Registro previsto |
|---|---|---|
| DC01 | Inventario/contexto | Discovery real, pre/post, dependencias/contexto suficientes frente a hashes idénticos. |
| DC02 | Autoridad/procedencia | T I26 y R SOURCE/BATCH/TASK; sin equivalencia ficticia I32/I28 o criterios reales. |
| DC03 | HC ledger/revocación | HEAD frente a ledger, revisión perdedora, conciliación explícita e historia/STALENESS. |
| DC04 | HC EDIT/UPDATE/ABA | Versión fijada, ambas ramas, HEAD/entidad/recibo y controles ABA seriales. |
| DC05 | HF fronteras/fsync | Seis operaciones/stages, puntos reales, huérfanos/temporales y OSError frente a SIGKILL/energía. |
| DC06 | HF hueco/UNKNOWN | After_head APPLY, BIND/generación, primera reconcile desde UNKNOWN y P observada frente a lookup pendiente. |
| DC07 | IC conflicto/historia | Precedencia COMMAND_CONFLICT/HEAD/BINDING y recibo viejo sin rebobinado. |
| DC08 | IC ticket/autoridad | IC17–20 ticket emitido; IC21–24 extra no emitido, sin adopción/reconcile o conclusión integrada. |
| DC09 | Barreras/oráculos | READY/lock/probe/ACK/retornos, lector independiente y límites de reapertura. |
| DC10 | Conteos/recursos | Campañas/IDs/intersecciones, controles T/R, timeout negativo/OSError/SIGKILL y recursos propios. |
| DC11 | Residuales | H02/H03/H07, cuantificadores/modes/scopes no cubiertos y H04/H05 históricos. |
| DC12 | Dictamen/continuidad | Delta razonado por parte frente a I40; cinco GI y D5/G01–G07 abiertos. |

## Restricciones de interpretación

Conservar declaración, semántica y ejecución como ejes separados. Todo cambio o conservación de valoración debe tener razón y referencias resolubles. Revisar generadores/bindings de tests dinámicos por lectura/AST; no importarlos para descubrir tests. No sumar ejecuciones repetidas de HC/HF/Python, actores, filas, probes, OSError o SIGKILL como tests nuevos.

IC21–IC24 son solo negativos REMOTE con ticket extra no emitido: no conciliación/adopción o conclusión integrada. CREATE no acredita UPDATE/CLOSE; revisión perdedora no revoca; lectura pasiva no prueba caída; recibo histórico no concede ejecución o rebobinado. Raw histórico ausente/contextos no aplicables mantienen sus límites.

P0, D1–D4 cerrados, hito local aceptado y D5 global/G01–G07 abiertos se conservan. Revisión futura documental I48 pendiente de aprobar: solo documentos nuevos y checks de lectura/Git/JSON/AST/hashes, sin código o campañas.
