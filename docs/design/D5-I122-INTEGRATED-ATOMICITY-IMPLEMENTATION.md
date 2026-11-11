# I122 — reparación integrada de atomicidad, escrita sin ejecución

Fecha: 2026-11-11 (Europe/Madrid). Base:
`50c49678568bae2abeefbe5fec0285f26c628283`.

**Se implementa una candidata nueva, I122-CANDIDATE-01, con rutas integradas
para los30 sitios lógicos.** Está en `testing/prospective_capture_joint_i122/`.
No se limita a otra revisión de los fallos: contiene el motor de transacciones,
el Recorder y los bindings conectados al worker, más diez componentes
sintéticos futuros escritos. No se importaron, compilaron ni ejecutaron esos
módulos. Los componentes están NOT_RUN.

La habilitación integral no se declara: el certificado nuevo permanece
IMPLEMENTED_NOT_ADMITTED. Falta validar comportamiento y recursos transitorios,
en particular el coste de copiar metadatos por fase. D5/H07 y brechas globales
siguen abiertos; IR03 NOT_READY. El rechazo I121 sigue describiendo los bytes
anteriores, que se conservan íntegros junto con los otros76 archivos de partida.

## Código conectado y propiedad de publicación

El punto final de binding de capture.py instala Recorder/LateBindings de
atomic.build. El worker importa este namespace y esos exports; no selecciona
silenciosamente el Recorder anterior. Los helpers crudos heredados siguen
presentes como implementación de las operaciones de metadatos, pero se invocan
sobre el estado privado de la fase. Las fuentes activas y las candidatas selladas
I119/I120/I121 no se sobrescriben.

El motor prepara un draft con contenedores builtin exactos. Un memo temporal
común preserva alias de frames/active/causal.frame y record_links/record_refs.
Los originales de record_refs, las listas de record_baselines, los valores de
oracle_guards y las listas de causal_sources permanecen opacos: mantienen su
identidad real para las comprobaciones de mutación. No se usa deepcopy ni se
invocan hooks de copia de objetos de producto. Tampoco se fusionan objetos con
identidades lógicas iguales.

Bajo un único _state_lock, compartido con _ref_lock y _emit_lock, la operación
completa modifica sólo ese draft. Se ejecutan los guards de cargos, filas,
eventos y páginas. invalid() dentro del draft deja un rechazo persistente aunque
el helper heredado haya capturado la excepción. Antes de _publish se comprueban
ese rechazo y el contador entero exacto, no negativo y no decreciente dentro de
la cuota original propuesta. Una fase rechazada no publica sus tablas, contador,
membresías ni cola de páginas. Sólo se permite registrar diagnóstico/poison en
el observador vivo.

La publicación se concentra en _publish, que sustituye el conjunto fijo de campos
y los datos causales bajo el mismo lock. No hay presupuesto por hilo, release,
reset ni índice persistente nuevo de deduplicación. El memo de alias es temporal
y no convierte dos objetos físicos distintos en uno.

Las páginas se codifican y verifican en el draft, incluida la rotación. Después
de publicar y liberar el lock, _atomic crea/escribe/cierra los archivos. Hay un
guard explícito de no posesión del lock antes de esa E/S. Un fallo físico
posterior invalida permanentemente la captura; no se afirma rollback de archivos
ni se permite reintento/reparación para obtener un sidecar aceptado. El contador
de E/S pendiente se drena con Condition.wait, que libera el lock durante la
espera. La finalización sella la entrada de nuevas fases antes de formar el
sidecar.

## Integración de los30 sitios

El JSON de implementación fija hashes de las seis fuentes y el AST/intervalo
actual de cada fase de la matriz. Se conservan los30 sitios lógicos originales,
aunque varios cargos ya estén agregados por la normalización R2.

| Sitios | Integración escrita |
| --- | --- |
| Q07–Q09 | owner, identidad Drive, observation, pending flags y membresías se preparan en el mismo draft; fallo no expone prefijos |
| Q10–Q11 | Un constructor wrapper llama una sola vez al original; después agrupa owner, declaration, membership, contexto, dominio y evento |
| Q12–Q13 | El wrapper de fixture agrupa toda su metadata posterior al retorno original |
| Q14–Q15 | _close_frame/_stop_fields agrupan records, guards, cierre y TEST_END; test.id y result.stop quedan fuera |
| Q16 | Cada página se reserva en Pages.flush antes de publicar manifest o comenzar E/S, incluida la rotación |
| Q17–Q18 | Las lecturas de source bindings son frescas y externas al lock; filas/estados/cargo se publican juntos; callback inicial sólo tras reserva exitosa |
| Q19–Q20 | CausalProxy lleva las operaciones mutantes al draft; sus callbacks charge/owner/emit/invalid apuntan al Recorder privado |
| Q23–Q26 | Exit, result refs, Pipe/registration, mensajes y comprobaciones de fila están dentro de sus fases completas |
| Q27–Q29 | Retenciones parentales, resultado/aserción y evento correspondiente se agrupan; snapshot original queda fuera |
| Q30–Q33 | domains, contexto, owner, grupo, registro Y y autoridad se modifican sólo en el draft, incluido el prefijo super.declaration |
| Q34–Q38 | POSTRETURN contiene retained/guards, grupos, witnesses, links obligatorios, cierre de stack y terminal/evento juntos |

Los métodos selected/check_retained/protocol_for/witnesses son lecturas puras
revisadas: no reservan contexto ni cargos ni hacen E/S. Su proxy devuelve un
snapshot de lectura; no expone un contenedor mutable vivo. Las otras operaciones
pasan por _atomic. Los argumentos que ya son metadatos se remapean mediante el
memo; las entradas originales no se copian como si fueran metadata.

### Cargos que debían adelantarse

La reparación no conserva dos reservas tardías que permitirían publicar datos
antes de pagar su referencia:

- **Q15:** cada nueva membresía de owner en owner_context_refs se carga en la
  fase de owner. En stop sólo queda el marcador +1. La suma de incrementos de
  membresías equivale al tamaño final de esas listas; no se paga dos veces ni
  se descuenta al cerrar el frame.
- **Q16:** cada append a manifest paga una unidad en el plan de flush, antes de
  manifest/cola/E/S. Finish sólo prepara la última página y sella; no vuelve a
  cobrar len(manifest). La suma por páginas es exactamente aquel len final.

Las unidades normalizadas originales2+adicionales4 por witness y la autoridad
adicional1 se conservan. La cota333109 se mantiene como premisa de transferencia
del total persistente de la captura completa; no es un conteo nuevo ejecutado
ni una aprobación de los nuevos recursos transitorios.

## Originales, fallos y límites de la afirmación

PRECALL y POSTRETURN/EXCEPTION son fases distintas, separadas por la llamada
original sin lock. Una fila pendiente de PRECALL no se convierte en terminal
parcial si falla POSTRETURN. El original se llama una vez y conserva su identidad
de retorno/excepción; un fallo del observador no sustituye la excepción original.
Constructor, snapshot/perform y boundaries tienen wrappers explícitos para ello.
Las llamadas de unittest, entropy/clock del inicio/cierre y checks Reader también
quedan fuera de las fases. Los checks frescos de bindings tienen un guard que
rechaza su ejecución bajo posesión del lock.

La propiedad revisada cubre rechazo por presupuesto y validación determinista
antes de publicar la fase. No es un protocolo de recuperación frente a muerte
del intérprete, ni una transacción de filesystem, ni evidencia de ejecución
exitosa. La E/S posterior a commit usa poison/fail-closed. No se concede PASS de
componentes a partir del código o del análisis AST.

La primera implementación copia el grafo retenido de metadatos para cada fase.
Eso añade memoria temporal y coste de CPU. Los originales opacos no se duplican,
pero el memo, el draft y las páginas en E/S pendientes **no están cubiertos sólo
por la cota del sidecar o por peak_page_buffer_bytes**, cuyo significado anterior
se conserva. Antes de habilitar PJC115-R2 deben acotarse/validarse estos recursos
y el tiempo de campaña, u optimizarse la copia conservando la misma propiedad.
Los diez componentes escritos comprueban el núcleo y casos de integración; no
se atribuye a NOT_RUN cobertura experimental de toda la campaña.

## Registro sin pérdida y bindings nuevos

El registro nuevo es un envelope cerrado d5.joint-inherited-registry.v1. Hereda
la base de selectores fijada por SHA y aplica exactamente los overrides
permitidos. checked_registry materializa el mismo objeto lógico completo y
conserva los validators heredados. Los arrays de inventario, tests, contextos y
listas O no se recortan. La base ya está en PhaseBytes; materializar no añade
lecturas físicas ni presenta esa vista como una lectura fresca.

El registro físico ocupa57521 bytes; materializado y serializado compacto
ocuparía806944. La reducción permite incorporar atomic.py y la prueba de fuente
sin elevar cuotas. Contrato/registro/certificado/manifiesto nuevos tienen paths
I122 propios. El certificado vincula488 fuentes/documentos finales; el manifiesto
vincula9 entradas (seis fuentes + contrato + registro + certificado). No se
incluyen self hashes ni hashes de autoridad futura.

| Calendario propuesto, sin ejecutar | Valor |
| --- | ---: |
| Inputs conocidos | 490 |
| Bytes U conocidos | 87.104.500 |
| Metadatos futuros canónicos F, por anchura | 57.277 |
| capture_inputs futuros / unión con autoridad | 493 / 494 |
| Worker: 3*(U+F)+4.852.460 | 266.337.791 bytes |
| Límite read_bytes sin cambios | 268.435.456 bytes |
| Margen de lectura | **2.097.665 bytes** |
| Top metadata model / allowance | 483.286 / 524.288 bytes |

Es una cota de **bytes de archivos del Reader**, no un certificado completo de
memoria/CPU. Se preservan las tres pasadas físicas y los checks frescos heredados;
el draft usa object.__new__ y nunca reinicializa Projector/Reader por fase. Los
metadatos futuros son modelos de anchura, no evidencia real PASS. No existen
raw/review/seal ni autoridad nuevos. El worker sigue exigiendo
SOURCE_CAPACITY_VERIFIED y todos los gates antes de importar el runner.

## Verificación y estado final

`python3 docs/validation/D5-I122-audit.py` sólo lee AST, JSON, hashes y tamaños.
Comprueba los anclajes30/30, el punto de publicación posterior a guards, E/S
fuera de la sección crítica, el traslado Q15/Q16, forwarding de originales,
nombres libres, pins y expansión sin pérdida del registro, calendario Reader,
cuotas idénticas y conservación de los76 archivos previos. No ejecuta producto,
candidata ni componentes; PASS_STATIC_SOURCE_ONLY no es validación runtime.

Estado: **reparación integrada escrita**, componentes10 NOT_RUN, atomicidad
runtime no validada, capacidad transitoria pendiente, PJC115-R2 no admitida para
captura. CP03 de I120 se conserva como prueba de los operandos originales; no se
convierte en prueba del nuevo coste de clonación.

P0 permanece83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1). D1–D4 e I1–I20/A52 conservan
aceptación. D5/H07/G01–G07 y GI globales siguen abiertos; obligaciones
humanas/reales GI06/12/18/24/30/36/42 pendientes. IR03 NOT_READY. I86/I89/I92 siguen
INVALID_CAPTURE, sin reanudación ni combinación. Sin producto ni componentes,
cuotas activas, commit/push, autoridad/destino, consumo, reservas operativas,
activación, promoción, despliegue ni D6. No se inspecciona ni limpia dev/run_data/D4.
