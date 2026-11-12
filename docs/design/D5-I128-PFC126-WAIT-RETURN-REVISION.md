# I128 — revisión de PFC126: frontera en el retorno de wait_worker

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`918d40229d8b35f5af40feda6419754dcc0fba34`.

**PFC126-CANDIDATE-02 resuelve F127-01 en el contrato candidato.** Sustituye la
salida física del worker por el retorno exacto True de wait_worker observado
por el coordinador. No acredita tiempos, servicio o heap: E05 sigue abierta,
E01–E04 conservan sus faltas de prueba y no cambia la no admisión de I122.
PFC126-CANDIDATE-01 y la revisión I127 quedan íntegros como antecedentes.

[Contrato revisado](../validation/D5-I128-PLATFORM-CONTRACT-CANDIDATE.json) ·
[Resolución de F127-01](../validation/D5-I128-F127-01-resolution.json) ·
[Auditoría](../validation/D5-I128-audit.py) ·
[Integridad](../validation/D5-I128-integrity.json).

## Modificación normativa

La revisión2 añade marcadores definidos en un único dominio monotónico del
coordinador. Son definiciones para una prueba futura: no se instrumenta código,
no se recogen timestamps y la garantía del reloj sigue pendiente de atestación.

| Marcador | Evento definido |
| --- | --- |
| t0 | Entrada de la invocación launch, antes de su primera instrucción |
| tR | Retorno normal de os.close(release_write), tras escribir RELEASE/newline |
| tW | Retorno de la llamada única wait_worker(process), con resultado exacto True |
| tF | Retorno normal real de launch al caller, después de finally y sus escrituras/cierres |

El resultado de la captura se valida independientemente después de tW. Esa
validación determina si la ejecución es elegible como éxito, pero **no mueve
el timestamp tW**. Tampoco se usa como tW una espera de cleanup posterior, el
exit físico, raw.elapsed_seconds o una fecha del filesystem.

Las ventanas quedan definidas así:

```
t0 <= tR <= tW <= tF
Tpre    = tR - t0       presupuesto candidato60s
Tworker = tW - tR       presupuesto candidato750s
Tpost   = tF - tW       presupuesto candidato60s
reserva explícita      30s
```

El orden del programa fuente sitúa el cierre de RELEASE antes de la llamada a
wait_worker, y su retorno antes de las validaciones y el retorno tras finally.
Con el reloj monotónico requerido por contrato, los tres intervalos son no
negativos y cubren el total sin hueco:

`(tR-t0)+(tW-tR)+(tF-tW)=tF-t0`.

Este argumento resuelve la definición de la partición. Para demostrar<=900
siguen faltando cotas verificadas<=60/750/60 y el tratamiento de la reserva30,
además de trabajo y servicio compatibles. Una igualdad de sumas no suministra
las cotas que faltan.

## Por qué ya no importa cuándo sale físicamente el worker

Si el worker sale antes de que el coordinador cierre RELEASE, el retorno True
de la espera sigue ocurriendo después de ese cierre. Tworker no se vuelve
negativo. Si sale después, la demora entre su salida y la reanudación/retorno
de la espera permanece dentro de Tworker. Se carga explícitamente al servicio
de scheduling/observación; no se descuenta ni desaparece entre ventanas.

Los anclajes fijan la llamada única de launch y el helper activo heredado
`typed.wait_worker`: True se devuelve tras completar process.wait; timeout
produce False. El retorno True confirma terminación observada, **no** exitcode0,
raw PASS, validez de paquete o éxito final de launch.

La resolución documenta cinco rutas lógicas, sin ejecutarlas ni simularlas:

- Exit físico previo a tR: se usa tW posterior observado por el coordinador.
- Exit posterior a tR: la latencia hasta tW cuenta en Tworker.
- False o excepción: no hay tW cualificado para la afirmación de éxito.
- True seguido de exit no normal o fallo de paquete/finalización: la calificación
  independiente de éxito falla, sin admisión temporal.
- True y éxito posterior validado: tW queda fijo en el retorno original y tF en
  el retorno real tras finally; las duraciones aún necesitan prueba.

False no se transforma en True por un reap/cleanup posterior ni por un estado de
captura que después parezca normal. La llamada actual no guarda un nuevo campo
de medición; el contrato exige evidencia del retorno al justificar esta ruta.
Un marcador ausente no se sustituye por0. La comprobación de éxito debe incluir
las condiciones vigentes de salida/autoridad/inputs/paquete/captura y finalizar
sin errores. El estado pendiente de revisión de suficiencia no cierra D5.

No se afirma que todas las rutas de fallo/cleanup terminen en900. Se preserva la
semántica original del watchdog/cleanup. El process.wait(900) actual continúa
siendo un timeout local, no una garantía extrema a extremo.

## Qué permanece sin cambios

Se conserva exactamente el heap candidato11GiB solicitado/12GiB comprometido,
las11 partidas, la reserva832MiB y el overhead1GiB. No se cambian los presupuestos
60/750/60+30 ni el reparto600CPU/90IO-hijos/60scheduling; se aclara que este último
incluye la observación del retorno de espera. No se aplica ningún presupuesto.
Las24 cuotas de producto y las fuentes I122 siguen byte a byte idénticas.

También se conservan los estados no atestados del runtime, todas las cotas de
heap/fase null, la curva de servicio sin rate/latency y los entregables MISSING.
El texto de E05 se actualiza para exigir las ventanas ordenadas nuevas; su
obligación de prueba no se marca completada.

| Elemento | Estado I128 |
| --- | --- |
| F127-01 | Resuelto en PFC126-CANDIDATE-02, sólo como definición normativa |
| F127-02 | Evidencia de costes/reservas todavía pendiente |
| E01–E04 | Abiertas; resultados I127 preservados |
| E05 | Frontera resuelta; trabajo, servicio y cotas temporales pendientes |
| E06 | Separada, pendiente; componentes NOT_RUN |
| Certificado I122 | IMPLEMENTED_NOT_ADMITTED, sin cambios |

No se emite SOURCE_CAPACITY_VERIFIED, no se habilita PJC115-R2/captura, no se
crean autoridad/destino o reservas y no se cambian los capture_inputs. Una futura
incorporación de esta revisión a la admisión real necesitaría rebind completo y
revisión Reader sobre bytes finales. La aceptación del candidato no se sustituye
por la instrucción de publicar documentos en Git.

## Verificación y publicación

`python3 docs/validation/D5-I128-audit.py` comprueba hashes, AST, orden de eventos,
partición simbólica, diferencias permitidas frente a PFC126-CANDIDATE-01, flags
de no admisión y conservación de118 archivos previamente publicados. No invoca
wait_worker, launch, procesos de producto ni rutas lógicas: sólo lee fuentes y
documentos, con Git como helper de metadata.
PASS_STATIC_SOURCE_ONLY es consistencia de la revisión, no PASS de ejecución,
plataforma o tiempo. El auditor funciona antes de stage y después del commit.

Se hace commit y push de todos los cambios conforme a la instrucción I128. Los
snapshots históricos no se reescriben; el éxito Git se verifica por separado y
no se confunde con admisión de producto, captura o despliegue.

P0 conserva83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
D5/H07, brechas globales y obligaciones reales pendientes; IR03 NOT_READY.
I86/I89/I92 INVALID_CAPTURE sin reanudación/mezcla. Sin ejecución de producto o
componentes, cambios de cuotas, proveedores/credenciales, consumo, reservas
operativas, activación, promoción, despliegue o D6. No se inspecciona ni limpia
dev/run_data/D4.
