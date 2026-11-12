# I137 — preparación de P03 PLATFORM-ENVELOPE

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`8566fb37220722879f3ec98de296787b6224b162`.

**P03 queda preparado como expediente de bloqueo por evidencia externa
insuficiente.** No se aporta un contrato autenticado de disponibilidad, servicio
o latencias para el objetivo exacto. Se aplica el rechazo y early stop de I132:
E04/E05 siguen abiertas, sin prometer cierre de heap o de los 900 segundos.
PFC126-CANDIDATE-03/I122/PJC115-R2 mantienen la no admisión.

[P03](../validation/D5-PFC126-03-E04-PLATFORM-ENVELOPE.json) ·
[Revisión de preparación](../validation/D5-I137-P03-preparation-review.json) ·
[Auditoría](../validation/D5-I137-audit.py) ·
[Integridad](../validation/D5-I137-integrity.json).

## Ámbito y dependencias

Se utiliza el destino y schema P03 del plan I132, con sus siete campos específicos,
aceptación/rechazo y roles requeridos. Se fijan 130 inputs por SHA256 y se
contrastan con blobs Git de la base publicada y bytes actuales. Once proyecciones
JSON incluyen valor observado, puntero, hash del archivo y hash canónico del valor.
Vinculan los registros de candidata03, P01, P02/I136 e I125, sin tratar una
referencia documental o respuesta histórica como atestación nueva del operador.

P01 tiene conformidad técnica del ámbito fuente, con aceptación independiente
pendiente. P02 sigue rechazado como prueba de identidad runtime según I136.
Preparar un expediente negativo P03 no satisface ni omite esas dependencias.
No se inicia el trabajo de cierre posterior condicionado a ellas.

El productor es el asistente de este chat, sin autoridad de plataforma/servicio.
Custodio/autoridad, firma/confianza, hash de material firmado, validez y revisor
independiente permanecen null. El trabajo se limita a los
inputs vinculados, sin afirmar ausencia global de documentación, contactar a
terceros, acceder a cuentas externas o inspeccionar la plataforma actual.

## Siete campos evaluados

| Campo del plan | Disposición y material pendiente |
| --- | --- |
| platform_runtime_pin_set_and_validity | Sin objetivo/plataforma/configuración/dominio/validez acreditados; requiere material autenticado compatible con P02 aceptado |
| available_worker_requested_and_committed_heap | Disponibilidad de heap solicitado y comprometido desconocida; requiere evidencia de capacidad real en la métrica y ventana declaradas |
| coordinator_child_resource_and_interference_scope | Ámbito P01 preservado, sin mapeo completo de recursos, aislamiento o interferencia; requiere cobertura del conjunto de procesos |
| compatible_CPU_service_unit_rate_latency_or_WCET_assumptions | Sin servicio inferior compatible ni entorno WCET estático justificado; requiere unidades, dominio, carga, latencia y validez explícitos |
| bounded_scheduler_locks_IO_child_completion_observation_delays | Ocho clases de demora sin cotas verificadas; requiere cobertura finita y atribución de todas las esperas relevantes |
| admissible_signal_retry_interference_and_load_assumptions | Señales/reintentos/backoff, competencia, concurrencia/arribos e IO sin supuestos acreditados; requiere límites y su justificación/enforcement |
| clock_monotonicity_domain_and_latency_accounting | Definición contractual conservada, implementación/dominio y compatibilidad real sin atestar; requiere evidencia de reloj y contabilidad temporal |

Los siete campos son INSUFFICIENT_FOR_ACCEPTANCE. El registro enumera 35 valores
null en sus registros principales, además de ocho uppers de demora ausentes y
los datos de autoridad no aportados. El número 35 no pretende contar todos los
hechos faltantes. No se sustituye información desconocida por cero, un manifiesto
vacío, el runtime del helper o valores ilustrativos de una firma.

## Memoria disponible y recursos de procesos

Los 11 GiB solicitados y 12 GiB comprometidos son presupuestos candidatos del
worker. Se conserva la definición P01 de heap solicitado/comprometido y su
correspondencia de backend pendiente. No se equiparan con RSS, bytes serializados,
memoria libre del host, cuota ordinaria o capacidad garantizada disponible.

Coordinador e hijos mantienen cuentas separadas; sus recursos y la interferencia
con el worker no se omiten de una eventual afirmación conjunta. No se acredita
capacidad agregada RAM/RSS ni aislamiento. Las once cotas completas de propietarios
siguen null, igual que demanda completa y capacidad disponible. El resultado de
fit es NOT_EVALUABLE_NO_DEMAND_OR_AVAILABILITY_PROOF: no se prueba ajuste ni
inviabilidad por la falta de evidencia o por un mayorante parcial demasiado holgado.

Se conserva la aritmética documental, sin asignaciones:

```
10938744832 + 872415232 = 11811160064 bytes solicitados
11811160064 + 1073741824 = 12884901888 bytes comprometidos
60 + 750 + 60 + 30 = 900 segundos
600 + 90 + 60 = 750 segundos candidatos de Tworker
```

La reserva de 832 MiB, H11 de 1 GiB y reserva temporal de 30 segundos no acreditan
capacidad/servicio o slack. Sus transferencias siguen cero y sus reglas de
conservación íntegramente preservadas. Las cuotas numéricas no se aplican ni
modifican. P04/P05 deben aportar las pruebas de demanda/fit, si se satisfacen sus
dependencias; la existencia de P03 no las produce.

## Servicio, latencias y reloj

P03 deja sin seleccionar la ruta de prueba: servicio inferior compatible o WCET
estático exacto justificado. No se calcula tasa deseada a partir de trabajo/budget,
frecuencia/cores, límites ordinarios o watchdog. Una tasa por tiempo CPU y una
tasa por tiempo wall tienen dominios diferentes: cualquier conversión exige
justificar servicio denegado, esperas, paralelismo y carga. La suma CPU de varios
procesos no se convierte automáticamente en duración wall.

Las ocho clases pendientes de demora cubren dispatch/servicio denegado,
locks/bloqueo, filesystem/pipes/streams, hijos/reap, salida física hasta retorno
exacto True, startup/READY/RELEASE, finalización/validación/publicación y
señales/reintentos/backoff/interferencia. Cada fila tiene proceso, actividades
C01–C10 pertinentes, unidad wall_seconds y upper null. Son requisitos de cobertura,
sin afirmar que constituyan categorías disjuntas ni sumar latencias inventadas.

Se preservan los marcadores y reglas de la candidata03:

- Trabajo del worker e hijos que avance tras recibir RELEASE y antes del cierre
  tR del coordinador debe quedar cubierto por Tpre o un sobreconteo justificado.
- La salida física no define tW: dispatch/observación/reap hasta el retorno exacto
  True de wait_worker pertenece a Tworker, incluso con worker ya terminado.
- Tpost comprende validación y finally completo hasta el retorno normal tF;
  chequeos posteriores no mueven tW. El éxito sigue cualificado, sin promesa de
  plazo para todos los caminos de fallo/cleanup.

No se restan solapamientos sin prueba ni se usa una demora como doble crédito
de presupuesto. Los 600/90/60 son objetivos candidatos, no garantías de CPU,
IO/hijos o scheduler. El watchdog de process.wait y wait20 no sustituyen la prueba
completa de éxito. El reloj monótono requerido no aporta implementación, unidad,
tasa, resolución o validez atestadas. No se recogen timestamps ni datos actuales.

P06 tendría que aportar trabajo completo, P07 compatibilidad de unidades,
servicio/supuestos y atribución, y P08 las cotas de fase. Esta preparación no los
inicia ni promete resolverlos con los conteos fuente existentes.

## Disposición y verificación

Los 16 criterios heredados de E01/E02/E04/E05 conservan su clasificación sin
cierre. E01–E05 siguen abiertas, E06 separado, pendiente, NOT_RUN y sin permiso
de ejecución. Los otros 17 outputs del plan siguen ausentes. No se producen
SOURCE_CAPACITY_VERIFIED, autoridad/destino, rebind o habilitación de captura.

Se conservan candidata03, plan I132, P01/P02 y fuentes, certificado
IMPLEMENTED_NOT_ADMITTED, capture_inputs, presupuestos, cuotas y reservas.
D5/H07 abiertos e IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL
(UI04.1); D1–D4 e I1–I20/A52 aceptados sin cambios. Brechas/obligaciones reales
pendientes; I86/I89/I92 INVALID_CAPTURE sin reanudar/mezclar. Sin proveedores,
credenciales, consumo, reservas operativas, activación, promoción, despliegue o
D6. No se inspecciona ni limpia dev/run_data/D4.

`python3 docs/validation/D5-I137-audit.py` verifica JSON, hashes/blobs, siete
campos, once proyecciones, 41 anclas AST, aritmética y dictamen negativo.
Conserva 163 archivos publicados y los inputs heredados. PASS_STATIC_SOURCE_ONLY
valida la preparación documental, no capacidad, servicio, identidad, fit o tiempo.
Sólo se ejecutan helpers documentales estándar/Git; no producto, componentes,
imports de objetivo, builds, escenarios, benchmarks o sondeos de plataforma.
El auditor funciona antes del stage y después del commit. Se hace commit y push
de los cinco archivos I137 y se verifica la referencia remota y el árbol limpio.
