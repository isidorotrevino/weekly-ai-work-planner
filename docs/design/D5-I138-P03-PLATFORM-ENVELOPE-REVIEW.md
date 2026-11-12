# I138 — revisión de P03 PLATFORM-ENVELOPE

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`3b34ca56606cd759bbcd1398f5aa9d276a473365`.

**Se confirma el dictamen de evidencia insuficiente de P03.** No se encuentran
defectos bloqueantes en la representación documental del expediente negativo.
Sus siete campos siguen sin permitir aceptar disponibilidad de capacidad,
servicio o latencias del objetivo. E04/E05 permanecen abiertas y se mantiene
la no admisión de PFC126-CANDIDATE-03/I122/PJC115-R2. P03 conserva sus bytes.

[Revisión documental](../validation/D5-I138-P03-documentary-review.json) ·
[Reconstrucción desde Git](../validation/D5-I138-P03-source-reconstruction.json) ·
[P03 revisado](../validation/D5-PFC126-03-E04-PLATFORM-ENVELOPE.json) ·
[Auditoría](../validation/D5-I138-audit.py) ·
[Integridad](../validation/D5-I138-integrity.json).

## Método y resultado del contraste

Se lee el blob P03 publicado en I137 y sus 130 inputs desde el commit de
preparación declarado (`8566fb3…`). Sus SHA256 coinciden con el expediente y los
bytes actuales. Se recompone cada una de las once proyecciones JSON: ruta, pin,
puntero, valor y hash canónico. Ninguna referencia o respuesta histórica de I125
se transforma en una atestación nueva del operador.

Se indexan los símbolos léxicos de las fuentes fijadas en esos blobs. Los 41
registros de anclas coinciden en símbolo, expresión aplicable, intervalo,
columna cuando está declarada y hash AST. Se contrastan también las cuatro
anclas de t0/tR/tW/tF. Se conservan las anotaciones históricas repetidas: 41
registros no significan 41 mediciones independientes ni cotas de recursos.
No se fusionan o descuentan obligaciones por compartir una definición fuente.

Se inspecciona por AST la llamada process.wait con timeout, el retorno True y la
ruta TimeoutExpired/False del helper fijado; el coordinador declara una llamada
wait_worker y el retorno normal final de launch. Son propiedades de fuente,
sin ejecutar caminos, imports, discovery, producto, componentes o sondeos.
La calificación de éxito y el reloj real siguen sin probarse.

## Disposición por campo del plan

| Campo P03 | Disposición I138 |
| --- | --- |
| platform_runtime_pin_set_and_validity | Insuficiente: plataforma/runtime/configuración/dominio/validez no atestados; P02 no aceptado como identidad |
| available_worker_requested_and_committed_heap | Insuficiente: disponibilidad y correspondencia de métrica no acreditadas; 11/12 GiB siguen siendo presupuestos |
| coordinator_child_resource_and_interference_scope | Insuficiente: ámbito P01 correcto, sin mapeo completo, capacidad conjunta o aislamiento/interferencia acreditados |
| compatible_CPU_service_unit_rate_latency_or_WCET_assumptions | Insuficiente: no hay servicio inferior compatible ni entorno WCET exacto justificado; ruta sin seleccionar |
| bounded_scheduler_locks_IO_child_completion_observation_delays | Insuficiente: ocho uppers ausentes; requisitos de proceso/actividad sin prueba de cobertura finita |
| admissible_signal_retry_interference_and_load_assumptions | Insuficiente: límites/supuestos y enforcement de señales, reintentos y carga no atestados |
| clock_monotonicity_domain_and_latency_accounting | Insuficiente: definiciones contractuales preservadas, reloj/dominio/compatibilidad reales sin evidencia |

Se comprueban los 35 valores desconocidos principales, ocho uppers de demora y
siete campos de autoridad explícitos: 50 valores null ya presentes en P03.
Es un inventario de campos contrastados, no de todos los hechos faltantes ni
50 obligaciones independientes. No se sustituyen por cero, listas vacías,
identidades del helper actual o garantías ilustrativas.

## Capacidad y servicio conservan sus límites

La definición de heap solicitado/comprometido coincide con P01. Se distinguen
worker, coordinador e hijos, con recursos separados y contribuciones temporales
pertinentes. No se acredita capacidad RAM/RSS conjunta o disponible, ni se
confunden bytes serializados, cuotas ordinarias o presupuestos con disponibilidad.

La aritmética candidata concuerda: 10 propietarios solicitados más reserva
832 MiB suman 11 GiB; H11 de 1 GiB lleva a 12 GiB comprometidos. Los objetivos
60/750/60 más reserva de 30 suman 900; 600/90/60 suman los 750 de Tworker.
Estas igualdades no prueban demanda, capacidad, servicio, slack o ajuste.
Transferencias y asignaciones siguen cero. La falta de evidencia tampoco
prueba inviabilidad: se confirma NOT_EVALUABLE_NO_DEMAND_OR_AVAILABILITY_PROOF.

P03 mantiene la distinción CPU-time/wall-time y no deriva una tasa a partir de
trabajo/budget, frecuencia, cores, cuotas o watchdog. La ruta servicio/WCET no
se selecciona sin evidencia compatible y justificada para el dominio exacto.
Los requisitos pendientes de señales/reintentos/backoff, carga/arribos e IO no
se asumen nulos, finitos o satisfechos por defecto.

Las ocho filas de demora tienen unidades wall_seconds, proceso y actividades
candidatas, con uppers null y sin evidencia verificada. Las filas pueden
solaparse y C10 abarca fases; el enlace a IDs de actividad no demuestra cobertura
exhaustiva, partición disjunta ni compatibilidad P06/P07/P08. Se preservan las
reglas contra omisión, resta de solapamientos sin prueba y doble crédito.

El trabajo que avance tras recibir RELEASE antes del cierre tR sigue cubierto
por la obligación Tpre. La salida física del worker no sustituye tW: su
observación/dispatch/reap hasta el retorno exacto True queda dentro de Tworker.
Tpost incluye validaciones y finally hasta el retorno normal tF. Los chequeos
posteriores califican el éxito sin mover tW. No se promete plazo para todo fallo
o cleanup, ni se toma process.wait900/wait20 como prueba de éxito completo.
No se recogen timestamps ni se acredita el reloj de plataforma.

## Aceptación y efectos

Los 14 controles respaldan la coherencia documental del dictamen negativo.
No se requiere cambiar P03 para expresarlo. Los 16 criterios E01/E02/E04/E05
conservan clasificación y permanecen sin cerrar. Se confirma la regla de rechazo
P03 y early stop de I132, sin iniciar los 17 outputs posteriores aún ausentes.
E01–E05 siguen abiertas y E06 separado, pendiente, NOT_RUN y sin autorización.

Este mismo asistente preparó I137. La recomputación separada no atesta
independencia de actor/organización, autoridad de plataforma, competencia de un
custodio, firma/confianza o aceptación independiente. P01 independiente sigue
pendiente y P02 sigue insuficiente como identidad runtime; la revisión de P03
no satisface ni omite esas dependencias. La conformidad del expediente negativo
no lo convierte en un contrato válido de capacidad y servicio.

Se mantienen los bytes de P03, candidata03, plan I132, P01/P02 y fuentes. Sin
cambios de cuotas/presupuestos/reservas, certificado IMPLEMENTED_NOT_ADMITTED,
capture_inputs o autoridad/destino; sin SOURCE_CAPACITY_VERIFIED o captura
habilitada. D5/H07 abiertos e IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1
PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados sin cambios. Brechas/obligaciones
reales pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar/mezclar. Sin
proveedores, credenciales, consumo, reservas operativas, activación, promoción,
despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.

## Verificación y publicación

`python3 docs/validation/D5-I138-audit.py` reproduce el contraste de blobs,
proyecciones, símbolos/AST, campos desconocidos, aritmética y no admisión.
Conserva 168 archivos publicados y los inputs heredados. Los cinco archivos
nuevos son documento, revisión, reconstrucción, auditor y sello I138. No se
invocan los auditores históricos con sus supuestos antiguos de working tree.

PASS_STATIC_SOURCE_ONLY valida la revisión documental, no capacidad, servicio,
identidad, independencia, fit o tiempo. Sólo se ejecutan helpers documentales
estándar/Git. El auditor funciona antes del stage y después del commit. Se hace
commit y push de todos los cambios I138 y se verifica remoto efectivo/árbol limpio.
