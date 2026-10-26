# D5 I72 — matriz PG01–PG64

[Contrato](D5-I72-PAGED-CAPTURE-DESIGN.md) · [Políticas y pins](../validation/D5-I72-design-review.json) · [Integridad](../validation/D5-I72-integrity.json).

**Diseño solamente.** Los64 casos propuestos serían componentes sintéticos I73; ninguno ha sido implementado o ejecutado en I72. I74/Python321 requiere autorización posterior separada.

| ID | Familia | Estímulo | Oráculo exigido |
|---|---|---|---|
| PG01 | AUTHORITY | Ausencia de autorización futura I74 | Bloquear antes de importar runner/producto o crear worker; aprobar I73 sólo habilita componentes sintéticos. |
| PG02 | AUTHORITY | Pins I69–I72 o código/registro alterados | STALE_AUTHORITY/STALE_INPUTS sin aprender hashes nuevos durante captura. |
| PG03 | AUTHORITY | Scope distinto de P01 o argv/path arbitrario | Rechazar; P02–P10 y sus registros I71 permanecen sellados. |
| PG04 | AUTHORITY | IDs, grupos o multiplicidades distintos | No completar por conteo parcial ni PASS del runner; exigir conjunto Python321 original. |
| PG05 | AUTHORITY | Discovery añade/elimina fuente o cambia documento pertinente | Comparar conjuntos y bytes pre/post; separar delta documental sin aceptarlo automáticamente. |
| PG06 | AUTHORITY | Registro I70 o raw I71 reescrito | Rechazar preservación; perfil paginado tiene registro nuevo y destino fijo nuevo. |
| PG07 | AUTHORITY | Import del capturador o modo plan | Sólo stdlib/ayudantes I70 explícitos; cero imports históricos y cero campañas. |
| PG08 | AUTHORITY | Mismo código y manifest bajo control del caller | Declarar puerta de coherencia; no atestación independiente ni autorización humana por archivo. |
| PG09 | PAGES | Evento que cabe exactamente en página | Aceptar sólo si el documento JSON completo con envelope cabe en 2MiB. |
| PG10 | PAGES | Evento siguiente rebasa página | Cerrar página no vacía y abrir índice consecutivo; no dividir/truncar evento ni test. |
| PG11 | PAGES | Evento individual rebasa4KiB | INVALID_CAPTURE; conservar oráculo/retorno original, parar entre tests. |
| PG12 | PAGES | Página número33 o bytes acumulados >64MiB | Bloquear incluso con menos de131072 eventos; nunca resetear acumulado al rotar. |
| PG13 | PAGES | Eventos de campaña131072 y131073 | Aceptar el primero sólo si otros topes caben; rechazar el excedente, no ocultarlo. |
| PG14 | PAGES | Eventos de test2048 y2049 cruzando páginas | Contador por test continuo; página nueva no reinicia límite. |
| PG15 | PAGES | Página vacía, duplicada, índice ausente o fuera de orden | Rechazar manifest; cero eventos sólo admite pages=[] en paquete incompleto. |
| PG16 | PAGES | Hash/bytes/first/last/count/header discrepantes | INVALID_PACKET_BINDING; no aceptar página por nombre o posición aproximada. |
| PG17 | STREAMING | Secuencia global densa entre páginas | Validar sin huecos/repetición, capture_run_id único y page_index correlacionado. |
| PG18 | STREAMING | Test cruza múltiples páginas | Frame usa rango global semiabierto y conteo; validador enlaza todos sus eventos. |
| PG19 | STREAMING | Muchos tests en una página | Conservar test_frame_id exacto; no asignar por cercanía al último resultado. |
| PG20 | STREAMING | Evento sin frame antes/después del lifecycle | Tipar fuera de test; nunca regalarlo a un frame vecino ni sustituir identidad de dominio. |
| PG21 | STREAMING | Validación de paquete al máximo permitido | Leer una página acotada cada vez y contabilizar bytes leídos; sin reconstruir lista global. |
| PG22 | STREAMING | Buffer del recorder durante suite larga | Una página más resúmenes acotados por test; no retener todos los eventos ni slices globales. |
| PG23 | STREAMING | Fallo escritura/flush/cierre o disco lleno simulado | Latch de invalidez independiente del stream; no pasar excepción instrumental al producto. |
| PG24 | STREAMING | Completitud calculada con un hijo/evento ausente | Propagar INCOMPLETE a test/grupo/campaña; digest/manifest correcto no reemplaza hijo. |
| PG25 | SEMANTICS | Wrapper retorna objeto/lanza excepción original | Una llamada original, mismos args y misma identidad; no llamadas extra de snapshot/perform. |
| PG26 | SEMANTICS | Assertions delegadas y subTest fallido | Depth evita duplicación semántica; callbacks y resultado funcional se conservan. |
| PG27 | SEMANTICS | assertRaises declarado pero __exit__ no observado | Distinguir expectativa de salida real; no inferir excepción desde PASS. |
| PG28 | SEMANTICS | Operando/retorno de tipo no soportado | NOT_RECORDED y propagación; sin repr, propiedades ni digest ficticio. |
| PG29 | SEMANTICS | Registro cambia tras stopTest | RECORD_MUTATED_AFTER_TEST; páginas históricas no se reparan para casar. |
| PG30 | SEMANTICS | Binding de método generado y alias DF/DR | Conservar fuente/factory/args y hash sellados; no crear AST inexistente. |
| PG31 | SEMANTICS | Raw funcional PASS parcial por stop instrumental | INVALID_TEST_COUNT/INCOMPLETE_TEST_SET; no denominarlo Python321 completo. |
| PG32 | SEMANTICS | Restauración tras éxito/fallo/budget | Restaurar objetos exactos anteriores, incluso constructor; sustitución ajena detectada invalida. |
| PG33 | APPLICABILITY | DF01 sin Store | N/A sólo identidad de dominio; exige lifecycle/assertions/inventario realmente observados. |
| PG34 | APPLICABILITY | DF02 sin Store | N/A sólo dominio; no reabrir D3/D4 ni rellenar historia ausente. |
| PG35 | APPLICABILITY | DF48 sin Store | N/A sólo dominio; cobertura declarada no equivale a escenarios ejecutados. |
| PG36 | APPLICABILITY | DR01 sin Store | N/A sólo dominio; fuente y manifiesto sellados de inventario relacional. |
| PG37 | APPLICABILITY | DR02 sin Store | N/A sólo dominio; conserva carácter documental del control. |
| PG38 | APPLICABILITY | DF07 con construcción declarada pero snapshot rechazado | Exigir evento de constructor exitoso del padre; no HEAD_VERIFIED, no observación instrumental del hijo. |
| PG39 | APPLICABILITY | DF43 con construcción declarada y limpieza rechazada | Exigir identidad observada de construcción y assertions; no inventario saneado ni durabilidad por PASS. |
| PG40 | APPLICABILITY | Cualquier otro ID sin identidad requerida | INCOMPLETE; sin nuevas excepciones N/A aprendidas del resultado ni reglas por prefijo/grupo. |
| PG41 | CONSTRUCTOR | Store.__init__ público con firma/fuente exactas | Binding AST/hash y inspect de función/firma; no alias ad hoc ni imports en fase componente. |
| PG42 | CONSTRUCTOR | Retorno normal del constructor sintético | Observar args run_id/store_id/role ya ligados tras original; retorno None preservado. |
| PG43 | CONSTRUCTOR | Constructor lanza antes de completar | Conservar excepción; registrar fallo sin aceptar identidades como constructor validado. |
| PG44 | CONSTRUCTOR | IDs inválidos, rol inesperado o tipo custom | No coerción/str/repr/getattr de payload; metadata inválida no altera excepción/retorno original. |
| PG45 | CONSTRUCTOR | Dos Stores o mismos IDs con objetos distintos | Referencias de objeto y declaraciones separadas; UUID repetido no prueba mismo Store ni mismo head. |
| PG46 | CONSTRUCTOR | Snapshot posterior de identidad diferente | Conservar ambas autoridades y marcar conflicto, sin sobrescribir declaración para aparentar consistencia. |
| PG47 | CONSTRUCTOR | Proceso hijo spawn sin wrapper propio | No atribuir callback padre al hijo; sólo protocolo existente y autoridad explícita de su metadata. |
| PG48 | CONSTRUCTOR | Constructor observado fuera de un frame o reutilizado | No enlazar por proximidad ni dejar que declaración satisfaga política HEAD donde se exige head observado. |
| PG49 | BOUNDS | Raw original supera12MiB | No truncar ni ampliar; conservar lo producido con estado inválido. |
| PG50 | BOUNDS | Sidecar/index o contexto supera12MiB | Bloquear; páginas no son permiso para crecimiento de frames/links/contexto sin techo. |
| PG51 | BOUNDS | Operandos16MiB, profundidad32 y strings4096 | Mantener topes I69, sin payload crudo ni escapes que eludan cómputo de bytes. |
| PG52 | BOUNDS | Frames4096 o referencias16384 excedidos | Rechazar exceso; enlaces por rango no consumen un puntero persistente por evento. |
| PG53 | BOUNDS | Inputbudget128MiB únicos/256MiB lectura o4096paths | Mantener inputscope separado y bloquear; no gastar contador de evidencia para saltar inputbudget. |
| PG54 | BOUNDS | Paquete >112MiB+4KiB o lectura de evidencia >256MiB | Contar raw/index/context/launch/pages/OWNER y repeticiones de lectura; no presupuesto por página reiniciable. |
| PG55 | BOUNDS | Tiempo900s o espera20s excedidos | Límite menor de runner/hijo/hook domina; no alterar alarmas/límites kernel ni añadir actores. |
| PG56 | BOUNDS | Presupuesto agotado durante stopTest/finalización | Estado inválido fuera del stream con código acotado; no añadir TEST_END ficticio ni cerrar el criterio. |
| PG57 | OWNERSHIP | Destino D5-I74-P01 existente | Rechazar sin overwrite; no reutilizar D5-I71-P01 ni borrar evidencia. |
| PG58 | OWNERSHIP | Componente symlink/FIFO/dispositivo o rename ajeno | Rechazar con identidad de fichero comprobada; no seguir links de manifest no confiables. |
| PG59 | OWNERSHIP | Página no listada o path/manifiesto con traversal | Conjunto cerrado exacto; sólo event-0001.json…event-0032.json bajo root propio. |
| PG60 | OWNERSHIP | READY/RELEASE con nonce/pid/pgid/fds incorrectos | No liberar worker ni tocar proceso ajeno; correlación proviene del Popen propio. |
| PG61 | OWNERSHIP | Timeout y recursos no confirmados terminados | Parada sólo grupo propio; registrar BLOCKED y pendientes, nunca cero por inferencia. |
| PG62 | OWNERSHIP | Sibling ajeno, dev/run_data/D4 operativo | Intactos y no inspeccionados; limpieza sólo temporales nuevos con owner/sentinel comprobados. |
| PG63 | OWNERSHIP | Resultados de suite sintética I73 usados como campaña | COMPONENT_ONLY; cero ocurrencias Python321 y cero import de runner/producto histórico. |
| PG64 | OWNERSHIP | Paquete íntegro y todos los tests PASS | Como máximo TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW; 81/3 y globales abiertos hasta revisión separada. |

## Políticas finitas de los siete frames

| Caso | Clasificación propuesta | Razón y límite |
|---|---|---|
| DF01 | NO_STORE_CONTROL / NOT_APPLICABLE_WITH_REASON | Inventario y detección de staleness; no instancia Store. |
| DF02 | NO_STORE_CONTROL / NOT_APPLICABLE_WITH_REASON | Lectura de sellos D3/D4 e hito local; no instancia Store. |
| DF48 | NO_STORE_CONTROL / NOT_APPLICABLE_WITH_REASON | Contabilidad de grupos y mapa de cobertura; no instancia Store. |
| DR01 | NO_STORE_CONTROL / NOT_APPLICABLE_WITH_REASON | Inventario relacional y aplicabilidad; no instancia Store. |
| DR02 | NO_STORE_CONTROL / NOT_APPLICABLE_WITH_REASON | Sellos históricos y no cierre D5; no instancia Store. |
| DF07 | NEGATIVE_DOMAIN / OBSERVED_CONSTRUCTION_DECLARATION_REQUIRED | Inicialización incompleta y rechazo de snapshot/create; identidad declarada en constructor padre no equivale a head ni observación del hijo. |
| DF43 | NEGATIVE_DOMAIN / OBSERVED_CONSTRUCTION_DECLARATION_REQUIRED | Rechazo de limpieza ante marker/symlink y preservación del sentinel; identidad declarada no acredita persistencia. |

La política aplica sólo a una futura captura P01; no cambia los siete frames incompletos I71. Los demás IDs mantienen sus requisitos anteriores. Presupuestos:131.072 eventos/campaña,2.048/test,32 páginas de2MiB,64MiB acumulados; guardas independientes. Raw/índice/contexto/launcher≤12MiB cada uno; paquete≤112MiB+4KiB.900s externos y límites menores intactos. Ningún tope garantiza que toda Python321 quepa.

P0, agregado81/3, partes PARTIAL, D5 global/G01–G07 y GI globales abiertos. Sin publicación ni cierre automático.
