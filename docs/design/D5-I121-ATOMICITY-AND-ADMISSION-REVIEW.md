# I121 — atomicidad de los30 sitios y decisión de admisión PJC115-R2

Fecha: 2026-11-11 (Europe/Madrid). Base:
`50c49678568bae2abeefbe5fec0285f26c628283`.

**Decisión concreta para los bytes actuales: NO_ADMITIR.** La revisión cubre los
30 sitios lógicos, pero la atomicidad correlacionada **no queda resuelta**. Se
identifican publicaciones parciales en la candidata I119-CANDIDATE-02. No se
habilita PJC115-R2, ni se sustituye esa propiedad por la corrección del contador
individual. D5/H07 y brechas globales siguen abiertos; IR03 NOT_READY.

I121 no ha implementado una transacción integrada ni ejecutado producto o
componentes. Se entregan el examen por sitio, doce contraejemplos abstractos,
el protocolo de corrección requerido, la decisión de admisión y su auditoría.
La decisión de rechazo queda resuelta; el objetivo positivo de habilitación
sigue pendiente. Los70 archivos de partida permanecen idénticos, incluidas las
fuentes candidatas y las cuatro sustituciones no aplicadas de I120.

## La condición que debe cumplirse

I115 exige reservar cada cambio correlacionado de owner/grupo/witness/autoridad/
tabla/frame/evento/página antes de publicar contador o estructura. Exige un
único presupuesto compartido, sin descuentos, resets ni presupuesto por hilo;
ningún lock durante llamada original, E/S, espera o cleanup. I117 añade las
cuatro unidades por witness normalizado, sin eliminar sus unidades originales.

El guard de Recorder.reference comprueba el nuevo entero antes de escribirlo,
y CausalState.ref protege charge+counter con _ref_lock. DomainState.declaration
prevalida el grupo/registro normalizado antes de publicar esos dos contenedores.
Son hechos locales correctos. No abarcan las mutaciones que los rodean.

El JSON `D5-I121-atomicity-review.json` conserva30 filas con source/symbol,
intervalo, hash del AST actual y peso I115. Q30–Q33 ya no son cuatro llamadas
físicas independientes: sus partes están agregadas en `units`, y parte de W/Y
de Q19 se trasladó a ese cargo. La matriz sigue los30 sitios **lógicos** de la
prueba, sin sumar dos veces su implementación normalizada. Los ocho sitios
históricos inactivos siguen inactivos.

## Hallazgos decisivos

Los siguientes son trazados aritméticos sobre estados abstractos en el borde
del presupuesto L=442305, sin modificar la cuota ni ejecutar la candidata.
No se afirma que esos estados se alcancen durante el P01 fijo exitoso, cuya
cota fuente333109 se conserva. Una cota positiva inferior a L no demuestra la
propiedad de rechazo atómico que también debe cumplir la implementación.

| Cambio correlacionado | Orden actual | Publicación parcial posible |
| --- | --- | --- |
| Drive Q08/Q09 | charge1; identity; charge2 | identity sin observation/member |
| Constructor Q10/Q11, fixture Q12/Q13 | charge1; declaration; charge1 | declaration sin membership de frame |
| Owner/objeto Q07/Q20 | weak owner/frame; strong-association charge | owner sin asociación fuerte correlacionada |
| Contexto Q19 | refT/publicar thread; refS | thread/counter sin subcase |
| Grupo Q30–Q33 | super.declaration; validar grupo/registro; charge(units) | domains ya modificado antes de reservar el agregado |
| TEST_RESULT Q28/Q24 | parent_outcome; result-ref charge | outcome sin result_refs/evento |
| Retained Q34/Q19 | super.retain publica; cargo group+witness | retained/guard sin normalización completa |
| Link Q19/Q37/Q38 | refL; dos pointers; grupo+witness | counter/cargos sin fila link completa |
| Pipe Q25 | insertar registration; charge1; añadir pairs | registration visible antes de su propio cargo |
| Cierre Q35/Q36 y link obligatorio | cerrar fila/stack/evento; crear link | terminal sin link correlacionado |
| Stop Q14/Q15 | publicar record_links; cargo agregado del frame | enlaces previos a finalización rechazada |
| Finish Q16 | close/flush; reference(len(manifest)) | página física/manifest previos al cargo rechazado |

Ejemplo especialmente directo: ParentalState.pipe_return contiene en este
orden `self.tables['parental_registrations'][key]=row`, `self.charge()` y
`self.pairs.append(...)`. Con cero unidades libres tras el prefijo, el cargo
rechaza después de publicar registration. El chequeo de tamaño previo no evita
ese fallo de correlación.

Otro ejemplo: con owner y contexto ya existentes, una declaración nueva llama
a super.declaration, que escribe `domains`. El agregado normalizado cuesta9
unidades (identity1 + grupo/W2 + witness6). Con8 libres, el guard rechaza antes
de los grupos/records, pero domains ya cambió. La protección local de I119 no
es una prueba de atomicidad de la declaración completa.

Q17 permite un cargo por binding antes de rows/state, pero ejecuta Reader.check
antes y después: no puede encerrarse todo el método en un lock de ledger.
Q18 publica el callback on_reference antes del cargo inicial. Q23/Q26 añaden
observaciones y después verifican row_budget. Q27/Q29 retienen metadatos en
fases distintas de la aceptación del evento. Q33 tiene preflight local correcto
para la autoridad adicional; aun así, sus dependencias de contexto/domain
impiden certificar la operación completa con ese hecho aislado.

No se atribuye a todos los sitios un contraejemplo de la misma clase. La matriz
distingue guard primitivo correcto, preflight local correcto y correlación no
certificable. Los doce trazados no son capturas, tests, evidencia de consumo ni
una afirmación nueva de INVALID_CAPTURE funcional.

## Corrección requerida, todavía sin implementación integrada

El protocolo de reparación queda definido para que pueda revisarse una fuente
concreta contra la misma condición:

1. Observar una sola vez el retorno/excepción original fuera de locks; preservar
   su identidad. Separar PRECALL y POSTRETURN cuando la instrumentación necesita
   una fila pendiente durante la llamada original.
2. Preparar un plan puro de **todos** los cambios correlacionados de esa fase:
   owners, contexto, filas, membresías, links, evento y rollover/finalización de
   página. No publicar un prefijo mientras se calcula el resto.
3. Validar filas/eventos completos y todos los límites deterministas; calcular
   el delta entero total, incluidas unidades originales y4 adicionales por
   witness. No añadir un índice persistente gratuito ni descontar copias O.
4. Bajo un único lock de metadatos/ledger, revalidar identidades/versiones,
   comprobar el delta completo antes de la primera mutación y publicar el
   agregado de estructuras y contador. Dos hilos no deben reservar desde la
   misma lectura previa sin esa revalidación.
5. Liberar el lock antes de llamadas originales, checks Reader, E/S, esperas y
   cleanup. La publicación física de páginas exige su plan validado antes de
   crear/escribir. Un fallo de E/S posterior debe invalidar la captura: no se
   promete rollback de un archivo parcialmente escrito ni captura aceptada.
6. Conservar primer diagnóstico allowlisted, restauración de observadores,
   parada entre tests y escritura única. Sin reparación/replay ni omisiones.

Reordenar sólo `self.charge()`, envolver métodos completos en un lock o revertir
únicamente grupos normalizados no implementa ese protocolo. Tampoco lo hace
un snapshot superficial que pierda aliases o copie los originales retenidos,
porque destruiría las garantías de identidad/mutación. La nueva implementación
debe acreditar los30 sitios y volver a calcular cargos/bytes/lecturas si añade
estado. Este informe no marca ese trabajo como realizado.

## Admisión: condiciones evaluadas, sin UNKNOWN convertido en PASS

`D5-I121-admission-decision.json` fija los hashes de los cinco fuentes y los
cuatro metadatos actuales, y los de las cuatro sustituciones I120. La decisión
aplica a esos bytes exactos:

- CP03 fuente sigue resuelto en I120,179/179, máximo conjunto positivo14890036.
  El certificado actual todavía tiene CP03=false; CP03=true sólo existe en su
  sustitución I120 no aplicada. No se intercambian ambas versiones.
- Atomicidad correlacionada: rechazada por el orden de publicación actual.
- Ambos certificados siguen DRAFT_NOT_ADMITTED y atomicity=false. El worker
  exige SOURCE_CAPACITY_VERIFIED y los gates verdaderos antes de importar el
  runner; no se cambia esa comprobación.
- El manifiesto contiene10 componentes NOT_RUN. No existen raw, review ni seal
  nuevos aceptados. I121 prohíbe ejecutarlos; AST, nombres y trazados de papel
  no sustituyen sus resultados ni sus hashes reales.
- La nueva autoridad JOINT_EXPLICITLY_APPROVED está ausente. No se crea ni se
  reutiliza ninguna autoridad de I86/I89/I92. El launcher llama a authority
  antes de reservar paths de captura, y el worker antes de READY/RELEASE/import.

Por ello no puede concederse una admisión de captura válida con el estado
actual. La ausencia de componentes está impuesta por el alcance de I121; la
falta de atomicidad es además un defecto de fuente que no se arregla con una
aprobación o con ejecutar los tests. No se pide ejecutar nada para disimularlo.

## Capacidad: el margen I120 no es transferible sin recalcular

La propuesta I120 sigue sin cambios: lectura superior268387721 frente a
268435456, margen47735, para sus488 archivos conocidos y cuatro metadatos
futuros. Los documentos I121 son consumidores documentales externos y no se
agregan silenciosamente a capture_inputs.

Si se añadiera **sólo** el informe completo de atomicidad (23939 bytes) como
nuevo input de aquel plan, manteniendo los demás cuerpos, sus tres pasadas
costarían71817 bytes. La nueva lectura sería **al menos268459538**, exceso
mínimo24082, incluso antes de crecer la autoridad y los bindings. Es una
hipótesis de crecimiento, no una medida ni un exceso actual aplicado.

La fuente corregida y sus pruebas necesitarán un nuevo plan exacto. Puede
revisarse una representación documental más compacta o un calendario fuente
más preciso, preservando evidencia y frescura; no se propone elevar cuotas ni
asumir que nuevas lecturas son gratuitas. No se expide un certificado numérico
positivo para una implementación que todavía no existe.

## Verificación y continuidad

`python3 docs/validation/D5-I121-audit.py` es una auditoría documental de lectura:
verifica los30 anclajes AST, el orden decisivo de mutaciones/cargos, la aritmética
de los doce trazados abstractos, los pins, las ausencias y el sello. No importa
ni compila candidata/producto, ni ejecuta componentes. PASS significa que el
informe de rechazo y sus evidencias son coherentes, **no** atomicidad verificada.

I120 se conserva íntegro. Las cotas positivas de referencias y operandos no se
retiran ni se convierten en prueba de saturación funcional. P0 permanece83
SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 conservan aceptación.
D5/H07/G01–G07 y GI globales siguen abiertos; las obligaciones humanas/reales
GI06/12/18/24/30/36/42 siguen pendientes. IR03 NOT_READY.

Sin producto ni componentes, cuotas, commit/push, autoridad, destino, consumo,
reservas operativas, activación, promoción, despliegue ni D6. No se inspecciona
ni limpia dev/run_data/D4. I86/I89/I92 permanecen INVALID_CAPTURE y no se
reanudan ni combinan.
