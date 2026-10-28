# I94 — matriz sintética propuesta y puertas de revisión

**PREPARED_FOR_REVIEW**,32 casos **NOT_RUN**; no son resultados.
La aprobación documental I93 no autoriza implementar ni ejecutar esta matriz.

| Caso | Disparador | Oráculo esperado | Estado |
|---|---|---|---|
| CB01 | Prior seals and candidate source pins | Mismatch rejects; I86/I89/I92 and I93 remain unchanged. | NOT_RUN |
| CB02 | Registry compares every quota | Missing/extra/renamed quota or stale hash rejects; no fallback default. | NOT_RUN |
| CB03 | Atomic charge reaches exact shared refs limit | Last allowed allocation commits once; retained count equals limit. | NOT_RUN |
| CB04 | Charge of one beyond refs | Reject before counter or evidence/table mutation; preserved count does not exceed cap. | NOT_RUN |
| CB05 | Variable charge 1+len(witnesses) crossing cap | Whole allocation preflight rejects; no partially added witness/link/key. | NOT_RUN |
| CB06 | Invalid charge types/values | bool/float/string/negative/overflow and nonbuiltin values reject without coercion. | NOT_RUN |
| CB07 | Several threads consume one ledger | One global atomic budget; no duplicate reservation, races or per-thread reset. | NOT_RUN |
| CB08 | Frame/table/page changes | Same global counter and quota; switching context never resets. | NOT_RUN |
| CB09 | Source graph has overridden charging methods | Count actual pinned MRO; inactive parent copies are not added by syntactic counting. | NOT_RUN |
| CB10 | Certificate absent/unknown multiplicity | Full-P01 capacity status NOT_ESTABLISHED; worker release not authorized. | NOT_RUN |
| CB11 | Certificate pins or321/12 inventory differ | Reject before runner import; no subset or sum of older packets. | NOT_RUN |
| CB12 | Certificate numeric candidate only clears I92 prefix | Reject as unsupported basis; no extrapolation of13/321. | NOT_RUN |
| CB13 | Events at exact per-test limit and one more | All events retained to boundary; next callback invalidates, no sample/drop. | NOT_RUN |
| CB14 | Events exact campaign limit and one more | Global event ceiling independent of reference budget. | NOT_RUN |
| CB15 | Row/event encoded4096 and4097 bytes | Exact byte check; UTF8/escaping included, no truncation. | NOT_RUN |
| CB16 | Page exact2MiB, rollover and32-page boundary | Headers/commas included; exceeding pages or64MiB fails without overwrite. | NOT_RUN |
| CB17 | Raw/sidecar/context/launcher exact12MiB and one more | Four independent checks, plus combined package budget. | NOT_RUN |
| CB18 | Package37 members and112MiB+4KiB exact/one over | Launcher counted once; OWNER and page names validated, no hidden extra member. | NOT_RUN |
| CB19 | Reader unique/read limits exact and one over | Single accumulated Reader across before/after/authority/finish; no reset. | NOT_RUN |
| CB20 | Maximum package scanned three times | Admission rejects predicted overread even if each independent byte cap fits. | NOT_RUN |
| CB21 | Operand source and auxiliaries exceed16MiB | Reject even when emitted digest/projection is small. | NOT_RUN |
| CB22 | Depth32/string4096/frames4096 boundaries | No quota bypass through subcases, encoding or alternate tables. | NOT_RUN |
| CB23 | Pinned source loops have local literal bounds | Tag local bounds only; never infer full call closure or runtime count. | NOT_RUN |
| CB24 | Data-driven iteration, recursive helper or external branch | Unknown propagates; do not replace with0, N/A or observed prefix count. | NOT_RUN |
| CB25 | Witness identity and contextual source sets | Retain all object refs, role/family/context and authorities; no merging physical state. | NOT_RUN |
| CB26 | Repeated pointers in distinct evidence structures | Charge real materialization; do not erase charges by string interning/dedup labels. | NOT_RUN |
| CB27 | Resource error on original wrapper return/exception | Original call/return/exception identity preserved; latch and stop between tests. | NOT_RUN |
| CB28 | First diagnostic then later budget/finalization errors | First phase/code stable and allowlisted; no free-text traceback/objects. | NOT_RUN |
| CB29 | Partial normal/failure-envelope write | One attempt only; no JSON repair/retry or second envelope. | NOT_RUN |
| CB30 | Observer changed/cleanup/restore | Identity checked; restore originals, own roots only, sibling preserved, no new product cleanup. | NOT_RUN |
| CB31 | Resource certificate is valid but semantic evidence missing | No budget waiver for receipt/oracle/link/pending child/null policy requirements. | NOT_RUN |
| CB32 | Planning lab ends | Only synthetic planner components; no capture authority/destination, IR03 or publication. | NOT_RUN |

La ejecución propuesta I95 es sólo componente sintético externo300s, sin importar
producto/runners/tests históricos ni reejecutar NS12/DW24/PR96/CT96, P01–P10,
I38/I67, SQL/Java/Docker. Cada caso debe ligar fuente/hash antes/después, raw_pointer
y oráculo; raíces nuevas con OWNER y hermano conservado, cleanup propio. No se
inician procesos de dominio; la concurrencia de CB07 usa sólo hilos sintéticos
propios y sincronización determinista, siempre terminados dentro del laboratorio.

Criterio de salida:32/32 PASS sólo validaría los componentes del planificador y
la carga atómica bajo datos sintéticos, incluidos certificados UNKNOWN rechazados.
No valida321/12, aplica cuotas ni crea captura. Certificado numérico, perfil de
captura nuevo y sus componentes requieren revisión posterior antes de pedir una
captura I96 o posterior. IR03, publicación y aceptación global son separadas.

Opciones: A, aprobar I94 y autorizar **sólo I95 CB32 sintético bajo300s**, defaults
actuales, sin perfil/campaña funcional; B, ajustar únicamente el diseño. El bloqueo
de capacidad numérica permanece explícito en ambas opciones. P0;83/1, UI04.1
parcial, D1–D4 cerrados e I1–I20 aceptado; D5/H07/G01–G07/GI globales OPEN.
