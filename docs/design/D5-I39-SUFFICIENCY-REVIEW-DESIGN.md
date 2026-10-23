# D5 I39 — contrato de revisión conjunta de suficiencia

Fecha: **2026-10-23**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base: `a956daf33681838f10bfb1c9c6c4a35722be0e77`.
[Decisión A](D5-I39-NEXT-CUT-SCOPE.md) ·
[Matriz propuesta](D5-I39-SUFFICIENCY-REVIEW-MATRIX.md) ·
[Criterios GI](D5-I23-GLOBAL-INTEGRATION-REVIEW.md) ·
[Obligaciones UI](D5-I33-INTEGRATED-EVIDENCE-REVIEW.md).

English: proposed documentary sufficiency review of bounded T/R and auditor
evidence. Declared coverage, static inspection and recorded execution remain
separate. No new runtime, code changes, criterion closure or global acceptance.

## Autoridad y objetivo

El usuario seleccionó A para preparar una revisión conjunta de GI33/GI34/GI38/
GI39/GI40. Esa selección autoriza **este contrato y matriz**, no ejecutar aún la
revisión semántica ni implementar correcciones. Las comprobaciones de integridad
de preparación no son dictámenes de suficiencia.

P0 conserva I32, handoff y posteriores sin publicar. D1–D4 cerrados y A52/
D5-LOCAL-SYNTHETIC-I1-I20 aceptado mantienen perímetro, targets y evidencia.
D5 global, G01–G07 y los cinco criterios siguen abiertos para revisión global.
Los siete criterios reales GI06/12/18/24/30/36/42 y Docs continúan pendientes.
No convertir por esta revisión el 30/35 previo en 35/35 ni crear D5-approved/
D5-CLOSURE globales. Publicación y aceptación necesitan decisiones independientes.

El objetivo futuro es responder, por subobligación: qué afirma el contrato, qué
comprueba una prueba, qué observó una campaña registrada, qué autoridad/recorrido
abarca y qué falta. Un mapa válido, un nombre de test o una cuenta PASS no responde
por sí solo esas preguntas. No se deduce durabilidad integrada de regresiones
aisladas ni se atribuye al auditor la recuperación de T/R.

## Corpus y referencias de lectura

| Grupo | Referencia histórica fija | Uso futuro |
|---|---|---|
| Obligaciones globales I23 | Base I38; documentos históricos intactos | Texto GI33/GI34/GI38/GI39/GI40 y exclusiones reales |
| UI y T durable I33 | `41582827c3a91425bd143021435cadfa7ebbf5a1` | UI01–UI40, contrato durable y DF01–DF48 |
| T I34 | `6a9932acec47f422249c94bc55bf83dc9a38b80b` | Código, harness, tests, runner e informe registrado |
| R I35/I36 | Diseño `aee8b212ab766cc89483013045ebb3bad8ebf168`; implementación `af31fd7f4d70c23ad84ac5b8258c05aba029a58a` | DR01–DR40, UI25/UI34, código/harness/campaña R |
| Auditor I37/I38 | Diseño `4eb9de6119bd6fe709981692282153c358040531`; implementación base I38 | EA01–EA36, registro fijo, código y raw/resultado propios |
| Cierres y A52 | Referencias del registro I38, incluyendo origen de inputs A52 | Preservación pública y targets históricos; sin auditoría exhaustiva nueva de D1–D4 |

Los inputs de diseño se sellan en un JSON separado. Al ejecutar la revisión se
verificarán otra vez hashes/commits y se registrará el snapshot efectivamente leído.
Fuente actual distinta del snapshot elegido exige hallazgo de aplicabilidad; no
usar líneas actuales para describir sin advertencia un test histórico distinto.
Para discrepancias documentales conocidas, leer el documento en su commit emisor
y explicar el cambio actual, conservando ambos hechos. Sin fetch o fallback a otro
commit por ausencia de objetos.

El corpus comprende código de kernel/T/R/planner, harness/test/runner y auditor;
regresiones públicas I24/I26/I28/I30/I32 y parsers solo según referencias relevantes
de la cadena. No afirmar revisión exhaustiva de sus 233 tests. No importar o
ejecutar módulos. La inspección de funciones/AST y hashes no ejecuta escenarios.
SQL/Java/documentación de D1–D4 solo para referencias públicas y targets declarados,
sin SQL/Java/Docker, migraciones o laboratorio operativo.

R en T/R y en las modalidades UI significa recorrido relacional de fixture; no
equivale a la etiqueta R de los siete criterios que exigen evidencia real.

## Unidad de revisión y registro exigido

Cubrir todas las **40 filas UI** y los **14 controles SR** de la matriz. Cada UI
se desglosa en todas sus cláusulas sustantivas, oráculos y cuantificadores: por
ejemplo, «antes/después», «cada frontera», «sin duplicar» y «sin perder conflictos»
no son una sola casilla satisfecha con un caso feliz. Las SR son controles de
revisión documental, no tests adicionales o sustitutos de las UI.

Cada entrada contendrá como mínimo:

- ID UI/SR, GI, texto original o referencia exacta y subcláusula identificada;
  modalidad M/F/R original y autoridad T/R/auditor/histórico efectivamente evaluada.
- Caso DF/DR/EA, test ID, función/harness/oráculo y path/commit/línea o símbolo;
  señalar qué se inspeccionó y qué falta. Los candidatos de los mapas son solo
  puntos de entrada; buscar el oráculo real y las dependencias relevantes.
- Frontera y rol, operación, punto de fallo/CAS, secuencia y parametrización
  exigida frente a la presente; temporización, proceso nuevo y lector independiente.
- Referencia de campaña/campo/índice de observación cuando existe, hashes y grupo/
  target; separar el PASS registrado de una prueba nueva. No inventar el contenido
  de un subcaso porque un método figure como PASS.
- Resultado de lectura, fuerza de evidencia, limitación, contradicción y pendiente
  concreto. Toda referencia debe resolverse o conservar el hueco explícito.

Para cada frontera se identificará dueño del estado, identidad/generación/hash,
revisión exigida y fuente de la prueba del antes/después. Atomicidad local BATCH
no implica atomicidad de múltiples proyecciones remotas. Las capacidades del
doble de ticket/CAS/unicidad no se transfieren a Plane real. La procedencia I26
de T y la captura JSON propia de R no se intercambian; R no inventa EVALUATION
Markdown o persistencia I32.

## Estados y reglas de inferencia

Registrar tres ejes independientes por subcláusula:

| Eje | Valores | Qué permite afirmar |
|---|---|---|
| Cobertura declarada | MAPPED / UNMAPPED / EXCLUDED | Existencia de referencia/limitación en contrato e informe |
| Lectura semántica | SUPPORTS_BOUNDED / PARTIAL / NOT_ESTABLISHED / CONTRADICTED / NOT_REVIEWED | Relación entre código, escenario y oráculo, solo en alcance descrito |
| Evidencia de ejecución | REGISTERED_PASS / REGISTERED_NONPASS / NOT_RECORDED / NOT_RUN | Lo que la campaña y sus campos efectivamente registran |

Añadir siempre `raw_binding`, integridad histórica y aplicabilidad actual como
metadatos separados, no como esos tres estados. Conservar la matriz T/R por
recorrido; fuera de un recorrido = EXCLUDED con motivo, no SUPPORTS_BOUNDED.
Una exclusión local no elimina la obligación original al resumir el criterio.

SUPPORTS_BOUNDED exige identificar implementación y oráculo de todas las partes
de esa subcláusula, sin contradicción detectada en el alcance inspeccionado.
No equivale a prueba de corrección universal, ejecución reciente o cierre GI.
PARTIAL identifica exactamente la parte sustentada y la restante. Una prueba
no encontrada o una observación insuficiente produce NOT_ESTABLISHED, nunca PASS
por analogía; una divergencia observable entre obligación y comportamiento
esperado/probado produce CONTRADICTED con evidencia, sin parche automático.

I34 e I36 carecen de raw histórico anclado: NOT_RECORDED no elimina sus informes
registrados ni los equipara al raw propio de I38. Puede constatarse REGISTERED_PASS
para un test identificado en el informe, con esa limitación de trazabilidad. Si
un dictamen exige un detalle de ejecución no registrado, ese detalle permanece
NOT_RECORDED aunque la lectura muestre que el test podría ejercitarlo. No buscar
raw en /tmp ni reconstruirlo, ni atribuir a una reejecución la identidad original.

El mapa de I38 inventaría cuarenta UI: aún no prueba suficiencia semántica. El
estado I34 STALE por inputs R nuevos se conserva junto con integridad histórica;
no vuelve falsos sus hechos históricos ni autoriza citarlos como campaña actual.
I36 CURRENT_RECORDED_SCOPE se limita a bytes/contexto registrados, no garantiza
calidad de oráculos, representatividad, capacidad de APIs o evidencia empírica real.

Las obligaciones originales que mencionan objetos volátiles/I28 se contrastarán
con la autoridad nueva aprobada T/R. Explicar la correspondencia y diferencias
mediante contrato aprobado y código. No exigir restaurar privados por fidelidad
literal ni declarar equivalencia funcional completa sin evidencia. Una sustitución
no justificada deja PARTIAL/NOT_ESTABLISHED y pide una decisión de alcance posterior.

## Cobertura de fallos, concurrencia y auditoría

GI38 requiere tabla por frontera/operación/rol/punto antes-después, estado y
recibo, respuesta perdida y recuperación explícita. Contrastar procesos spawn,
señales, exitcodes, HEAD/hashes, lectores independientes y persistencia de
UNKNOWN/CONFLICT. Un solo SIGKILL o un contador de procesos no cubre toda la tabla.
No inferir energía/disco fallido, NFS/Windows o aislamiento contra caller hostil.

GI39 requiere ordenaciones concretas y resultados aceptables: cambios fuente/
selección/perfil/local/relaciones/remoto, ABA/revocación, expected_head/CAS y
respuestas concurrentes. Diferenciar interleaving controlado de carrera entre
procesos, identificando barreras/Event/pipes y oráculo. No exigir o anunciar un
orden que el código de la prueba no fuerza. Fechas no eligen ganador.

GI40 diferencia declaraciones cero, comprobaciones estáticas, oráculos de pruebas
y observaciones finales de recursos. No presentar escaneo como prueba exhaustiva
de ausencia de secretos/operaciones. La limpieza propia no demuestra estado actual
de dev/D4: no inspeccionarlos para intentar acreditarlo. Registrar qué evidencia
de preservación pública existe y dónde termina su alcance.

## Entregables y validación de la revisión futura

Se propone emitir I40 como **revisión documental**, con informe legible, tabla
estructurada completa UI/subcláusulas/SR, resumen de cinco GI, hallazgos y referencias
de inputs. Cada resumen GI enumerará soporte acotado, lagunas, limitaciones y
próximo trabajo propuesto, manteniendo `global_review=OPEN` y `closure=false`.
No un único PASS que esconda subcláusulas parciales.

La validación documental comprobará IDs completos, referencias resolubles,
hashes/commits, estados válidos, ningún hueco rellenado por suma de tests y
coherencia resumen→subcláusulas. Los 281 tests compartidos I34/I36 no se cuentan dos
veces; 321 históricos y 36 del auditor permanecen en campañas distintas. Los
controles SR y filas UI no añaden tests ejecutados. No reejecutar DF/DR/EA o SQL.

La lectura/auditoría fija de integridad puede volver a ejecutarse con salida
saneada, separada de tests y de dictámenes semánticos. No cambiar el auditor o
su registro para incorporar I40; esa ampliación sería otro alcance. No guardar
capturas privadas, copiar texto de inspect/manifiestos de laboratorio ni abrir
estado temporal ajeno. Referencias públicas únicamente y errores saneados.

Solo se escribirán documentos/resultados nuevos I40; código, tests, runners,
registro I38, cierres e informes históricos quedan intactos. Si aparece un defecto,
registrar reproducción conceptual y alcance de corrección propuesto; no repararlo
o ejecutar un laboratorio bajo esta autorización documental. Sin pruebas nuevas,
cuentas/credenciales reales, consumo/reservas, activación, promoción, despliegue o D6.

## Decisión concreta pendiente

**A:** aprobar I39 y autorizar ejecutar la revisión documental I40 de las 40 UI,
sus subcláusulas y SR01–SR14, por lectura de código/pruebas/evidencia T/R/I38 y
comprobaciones de integridad; sin código nuevo, reejecución de tests o cierres.
**B:** aprobar solo el diseño, sin ejecutar la revisión. **C:** ajustar contrato/matriz.
P0 se conserva en todas las opciones; publicar requiere SHA concreto por separado.
