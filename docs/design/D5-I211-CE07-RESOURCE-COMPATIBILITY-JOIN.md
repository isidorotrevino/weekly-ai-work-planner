# I211 — CE07: join de recursos y compatibilidad pendiente

CE07 queda preparado como dossier documental negativo para PGO181 candidato 02. No aporta una prueba de recursos ni habilita PJC115-R2: E01–E05 siguen abiertas, E06 continúa sin ejecutar, D5 permanece abierto e IR03 `NOT_READY`. La preparación no acepta las premisas reales pendientes de CE04, CE05 y CE06.

La unidad reúne [el dossier CE07](../validation/D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json), [la revisión de preparación](../validation/D5-I211-preparation-review.json), [el auditor documental](../validation/D5-I211-audit.py) y [su sello](../validation/D5-I211-integrity.json). La referencia normativa es [I193, CE07](../validation/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json); se conservan literalmente sus cuatro evidencias requeridas, tres comprobaciones, siete reglas y frontera de autorización.

## Qué debe revisar el siguiente lector

| Join | Evidencia necesaria y estado actual |
| --- | --- |
| E01 | Cierre efectivo exacto de fuentes, runtime, loader, caller, ledger y crypto; identidad y compatibilidad atestadas. Falta el sucesor real. |
| E02 | Once propietarios de heap con vida, transitorios, originales/hijos, marcos, native/GC, allocator y solapamiento de procesos; capacidad disponible atestada. Las cotas completas y la capacidad son desconocidas. |
| E03 | Trabajo, CPU y tiempo completos por actividad, proceso y fase en unidades compatibles; no convertir bytes, visitas o conteos en segundos. Faltan las derivaciones. |
| E04 | Servicio real de CPU, reloj, IO, bloqueo, scheduling, hijos y observación, compatible con la misma clausura. La política o un hash no prueban esas garantías. |
| E05 | Éxito justificado dentro de ventanas ordenadas 60/750/60 más reserva candidata 30, sin transferirla. Los 900 segundos son un objetivo candidato, no una garantía ni un resultado medido. |

Cada obligación y cada uno de los veinte criterios de I131 conservan su referencia y descripción histórica, junto a campos separados de evidencia del sucesor, todavía ausentes. Los veinte outputs históricos de I132 existen y se fijan por hash; el `output_created=false` guardado en aquel plan sigue siendo un dato histórico. Ninguno se transfiere automáticamente como prueba aceptada del sucesor.

La fuente PFC126-03 enumera diez actividades con treinta valores superiores requeridos de trabajo/CPU/wall, y P06 contiene veinte vectores proceso/fase. Eso no acredita treinta grupos distintos del sucesor ni satisface por sí mismo la expresión «all30 work groups» de CE07: se conserva íntegra y queda pendiente el inventario completo o una correspondencia revisada, sin inventar identificadores ni reducir la obligación.

Los 179 casos de operandos, 321 raíces, 12 grupos y 30 sitios atómicos son alcance heredado que requiere requalificación exacta. Tampoco los diez tests de componentes, CP03 heredado, el código de atomicidad escrito, los índices tipados o los anchos de placeholders sustituyen evidencia completa de nuevas rutas de custodia, bootstrap, salida y fallo. Los componentes siguen `NOT_RUN`.

## Costes y frontera temporal

El join exige ambos ledgers Reader de coordinador y worker y la composición global. Incluye lectura y copia, lookup/registry, parseo/hash, identidad y crypto, freshness/revocación, consultas y durabilidad del ledger, intentos de frame, recibos, dos escrituras de salida, native/GC, hijos, observación y cleanup. Los hechos de enrollment/build offline no hacen gratuita su verificación por intento. Las cotas de cuerpos, rutas, Reader, contexto/launch y bundle siguen siendo límites de diseño condicionados, no una prueba de heap, CPU o admisión.

Se conserva la reparación de `wait_worker`: Tworker termina al retornar exactamente `True` en tW; Tpost cubre el retorno normal de `launch` después de `finally`, validación y escritura final en tF. No se sustituye tW por la salida física del worker. Sin derivaciones compatibles de trabajo/servicio/latencia no se demuestra éxito en 900 segundos. Los sumandos desconocidos siguen `null`; no se suman como cero ni se transfiere reserva o capacidad.

## Pruebas previas y fases posteriores

CE07 exige evidencia BASIS/índices genuina y aceptada en el scope final de fuentes, imagen y runtime. No existen aquí esos cuerpos, sus premisas aceptadas ni decisiones competentes R03/R06 y R08 separado. Los cuatro destinos B01–B04 de I177 siguen ausentes: el dossier los vincula sin ejecutar sus productores ni emitir metadatos positivos. Las rutas de cualificación y validación final de I177 requieren autorización separada; no se ejecutan ni se convierten en una dependencia circular del propio root final.

CE08 conserva el freeze final; CE09, la proyección exacta de C; CE10, mapping/bundle únicos. CE07 no exige un C, root, mapping o recibo futuro como prueba antecedente de sí mismo. CE11 no depende del recibo CE12. La construcción del claim real antes del recibo pertenece a CE12, tras admisión y autorización separadas, con todos los prerrequisitos externos del plan. Preparar esta frontera no satisface ninguno de esos gates.

Las tres plazas R03/R06/R08 siguen sin persona ni appointment aceptado. Se conservan las ocho exclusiones S01 y la separación de custodia. La reconstrucción por el mismo asistente aporta comprobación metodológica; no es revisión independiente de actores ni aceptación competente.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I211-audit.py`.

Resultado requerido: `PASS_STATIC_SOURCE_ONLY_RESOURCE_EVIDENCE_MISSING`. Ese estado valida los documentos y la preservación, **no es un PASS de recursos o cualificación**. El auditor contrasta 852 pins con blobs del commit base I210 `4c4e634da477ea3fd441dc5809f5d4bd4c5bdd38`, reconstruye documentalmente I210 sin invocar sus mains de publicación y conserva 544 archivos publicados. Comprueba doce mutaciones negativas únicamente en memoria y el delta exacto de cinco archivos.

CE07 no existía en el commit base. Durante la reconstrucción histórica se proyecta sólo la consulta `Path.exists` de su ruta exacta como ausente; los blobs no se alteran ni se omiten controles. La consulta se restaura tanto en éxito como ante excepción. Fuera de ese replay se exige CE07 presente, CE01–CE06 presentes y los cinco dossiers CE08–CE12 ausentes. Los guards históricos anidados se conservan intactos.

El harness de runtime es N/A: no se importan, compilan ni ejecutan producto o componentes, ni se hacen probes, crypto/codec real, claims, clocks, benchmarks, procesos o contactos externos. No cambian cuotas, reservas, contratos activos, destinos, bindings o autoridades. No se crea ningún registro positivo I191 ni firma, actor, clave o PASS ficticio.

Una unidad documental con commit y push autorizados; supera 400 líneas por sus matrices, pins y comprobaciones de preservación. Reversión exacta: retirar sólo este documento y los cuatro archivos I211/CE07 enlazados arriba. La publicación no implica aceptación, ejecución o cierre. El siguiente trabajo puede revisar este dossier; toda evidencia real y sus decisiones competentes siguen pendientes.
