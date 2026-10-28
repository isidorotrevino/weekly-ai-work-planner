# I96 — sitios activos y obligaciones de cómputo

Revisión documental, no resultados de campañas. Los IDs Q conservan la posición
del catálogo I94; los ocho sitios excluidos se mantienen en el JSON con multiplicidad cero en este MRO.
No se renombran punteros ni se borran cargas para hacer caber P01.

| Sitio | Fuente/clase/método:línea | Carga | Cota/multiplicidad |
|---|---|---|---|
| Q07 | prospective_capture_typed.Recorder.owner:260 | `1` | NOT_YET_CERTIFIED |
| Q08 | prospective_capture_typed.Recorder.owner:270 | `1` | NOT_YET_CERTIFIED |
| Q09 | prospective_capture_typed.Recorder.owner:271 | `2` | NOT_YET_CERTIFIED |
| Q10 | prospective_capture_typed.Recorder.constructor:293 | `1` | NOT_YET_CERTIFIED |
| Q11 | prospective_capture_typed.Recorder.constructor:295 | `1` | NOT_YET_CERTIFIED |
| Q12 | prospective_capture_typed.Recorder.fixture_constructor:314 | `1` | NOT_YET_CERTIFIED |
| Q13 | prospective_capture_typed.Recorder.fixture_constructor:315 | `1` | NOT_YET_CERTIFIED |
| Q14 | prospective_capture_typed.Recorder.stop:400 | `1` | NOT_YET_CERTIFIED |
| Q15 | prospective_capture_typed.Recorder.stop:422 | `len(f['owner_context_refs']) + 1` | 321_PLUS_SUM_FRAME_OWNER_MEMBERSHIPS |
| Q16 | prospective_capture_typed.Recorder.finish:439 | `len(self.events.manifest)` | ONE_FINALIZATION_WITH_MANIFEST_LENGTH |
| Q17 | prospective_capture_late.LateBindings.prepare:143 | `1` | AT_MOST_TWO_ADDITIONAL_CLASS_BINDINGS |
| Q18 | prospective_capture_late.Recorder.__init__:152 | `len(self.projector.bindings.rows)` | ONE_INITIAL_BUILTINS_DICT_BINDING |
| Q19 | prospective_capture_selectors.CausalState.ref:414 | `1` | NOT_YET_CERTIFIED |
| Q20 | prospective_capture_selectors.CausalState.object_ref:419 | `1` | NOT_YET_CERTIFIED |
| Q23 | prospective_capture_selectors.CausalState.exit:528 | `1` | NOT_YET_CERTIFIED |
| Q24 | prospective_capture_selectors.BaseRecorder.emit:551 | `1` | NOT_YET_CERTIFIED |
| Q25 | prospective_capture_selectors.ParentalState.pipe_return:979 | `1` | AT_MOST_ONE_DI07_PAIR |
| Q26 | prospective_capture_selectors.ParentalState.message:1027 | `1` | NOT_YET_CERTIFIED |
| Q27 | prospective_capture_selectors.Recorder.emit:1066 | `1` | NOT_YET_CERTIFIED |
| Q28 | prospective_capture_selectors.Recorder.emit:1067 | `1` | NOT_YET_CERTIFIED |
| Q29 | prospective_capture_selectors.Recorder.wrap_return:1078 | `1` | NOT_YET_CERTIFIED |
| Q30 | prospective_capture_selectors.DomainState.declaration:1208 | `1` | NOT_YET_CERTIFIED |
| Q31 | prospective_capture_selectors.DomainState.declaration:1212 | `1` | NOT_YET_CERTIFIED |
| Q32 | prospective_capture_selectors.DomainState.declaration:1217 | `2` | NOT_YET_CERTIFIED |
| Q33 | prospective_capture_selectors.DomainState.declaration:1219 | `1` | NOT_YET_CERTIFIED |
| Q34 | prospective_capture_selectors.DomainState.retain:1242 | `1 + len(witnesses)` | NOT_YET_CERTIFIED |
| Q35 | prospective_capture_selectors.DomainState.close_call:1248 | `2` | NOT_YET_CERTIFIED |
| Q36 | prospective_capture_selectors.DomainState.close_call:1250 | `1 + len(witnesses)` | NOT_YET_CERTIFIED |
| Q37 | prospective_capture_selectors.DomainState.link:1253 | `2` | NOT_YET_CERTIFIED |
| Q38 | prospective_capture_selectors.DomainState.link:1261 | `1 + len(witnesses)` | NOT_YET_CERTIFIED |

Cota completa **R=Σ(qᵢ×Nᵢ)**: los términos de owners, declaraciones/membresías,
record bindings, keys, objetos causales, exits, mensajes y fanout de witnesses
siguen abiertos. Los cinco hechos fijos no permiten rellenar los demás términos.
La fuente de cada sitio y todos los321 bindings/closures están en el JSON I96.
Los cierres self.helper son sintácticos, no un certificado de despacho transitivo.

SC01: multiplicidades parentales y lifecycle/callbacks de los30 sitios. SC02:
objetos por contexto y fanout conservando cada witness/autoridad. SC03: calendario del Reader de inputs y bindings tardíos acotado por fuente
para el perfil actual (worker≤160864585 bytes; debe revisarse si cambia el perfil). SC04: eventos, filas/tablas y valores del
P01 original. SC05: cualquier cuota numérica/perfil nuevo necesita decisión propia.

La siguiente revisión documental debe resolver esos símbolos por helper/ruta con
anclas y distinción padre/hijo. No cargar al padre llamadas internas no observadas
del worker hijo, ni omitir callbacks/cleanup originales del padre. Un conteo de
sitios AST o bucles locales no mide llamadas ni permite aceptar UNKNOWN como0.
No hace falta ni está autorizada otra campaña para esta revisión de fuentes.
