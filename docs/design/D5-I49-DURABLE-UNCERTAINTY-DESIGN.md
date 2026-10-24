# D5 I49 — contrato de incertidumbre durable

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_REVIEW**.
Base Git: `540fa16841855e5c1a995a2c999334f7fdc7d774`.
[Selección y alternativas históricas](D5-I49-NEXT-CUT-SCOPE.md) ·
[Matriz UQ01–UQ24 y MG01–MG03](D5-I49-DURABLE-UNCERTAINTY-REVIEW.md) ·
[Sello de diseño y fuentes](../validation/D5-I49-design-review.json) ·
[Revisión I48](../validation/D5-I48-results.md).

## Autoridad y propósito

El usuario eligió **A**: preparar contrato y matriz para H07/UI20.3/GI38. El
borrador de opciones y su sello se conservan íntegros como historia de preparación;
su AWAITING_SCOPE_SELECTION describe aquel momento, no la selección A posterior
registrada aquí. Esta elección no autoriza implementación, campañas, cambios de
modelo ni publicación. El corte futuro propuesto es I50, tras aprobar este alcance.

Objetivo: precisar el soporte que puede obtenerse sin alterar la API durable y
hacer visible el límite que subsiste frente a múltiples coincidencias/429 ambiguo.
UI20.3 permanece **PARTIAL** y H07 abierto. No se emitirán dictámenes nuevos hasta
revisar evidencia futura; ni siquiera UQ01–UQ24 PASS cerraría automáticamente la
parte de colecciones o semántica HTTP ausente.

## Contratos actuales y correspondencia

I28 volátil usa PlaneFixture.query(key,ticket): matches y proof separados, con
DUPLICATES/FOREIGN. Su execute usa AMBIGUOUS_429 como resultado UNKNOWN sintético
antes del efecto; no demuestra ambos desenlaces de un 429 real. PC08, PC23 y PC26
son referencias históricas, no pruebas durables transferibles ni tests nuevos.

T Remote.lookup(ticket,M) devuelve una prueba o None; valida request_hash si existe.
R reutiliza esa fachada pública sobre Store/reducer/schema R propios. No hay lista
de matches, status HTTP, cabeceras ni política de selección/adopción. proof_ok T/R
exige un dict cerrado correlacionado con ticket, M, K, run/store, payload y código.
Lista o envelope ajeno se rechaza como prueba incompatible, sin semántica de
multiplicidad válida. No se modifican reducers para aceptar esos formatos.

Client.dispatch emite ISSUE durable antes de execute. DurableError/OSError se
convierte en proof=None y RESULT; Client.reconcile registra QUERY, consulta,
convierte esas excepciones en None y registra RESULT. proof_hook opera después
de la consulta y fuera del try de transporte; no se usará para simular una
excepción capturada de execute/lookup. No se intercepta Store ni se inyecta estado
CLIENT/REMOTE directamente. Tampoco se convertirá un dict status=UNKNOWN/429
inválido en una respuesta HTTP acreditada.

Las categorías del contrato son NATIVE (API existente), INJECTABLE_NEGATIVE
(wrapper/hook local de fallo o formato inválido), CONTROL y MODEL_GAP (capacidad
no expresable fielmente). Se registran por separado del estado del test y del
soporte semántico de una obligación. Un negativo de schema no completa MG01;
un OSError no completa MG02.

## Alcance futuro propuesto

Solo nuevos archivos en testing/durable_uncertainty/ y nuevos documentos/raw I50.
Producto, harness históricos, registro fijo I38, handoff y evidencia anterior
permanecen intactos. Reutilizar setups T y R existentes, oráculo independiente y
propiedad de recursos revisados; no fabricar una segunda fuente de autoridad.

Veinticuatro métodos explícitos UQ01–UQ24, doce familias × T/R. Diez familias son
CREATE/PROJECTION con una TASK seleccionada; dos son controles de laboratorio.
No UPDATE/CLOSE, nuevas carreras, SIGKILL, perfil/cuenta/origen, UI33.2 o variaciones
relacionales UI34.3. Las familias de fallo son seriales y deterministas. La caída
positiva ya tiene evidencia HF; este corte usa reapertura, sin atribuirle una
nueva caída. Se reportará qué oráculos repiten evidencia histórica.

Wrapper local a cada nuevo worker sustituye temporalmente la referencia execute
o lookup de esa instancia, nunca código de producto/clase global. Registrar
execute_wrapper_calls, execute_real_calls, lookup_wrapper_calls, lookup_real_calls
y fase del fallo, con restauración en finally o descarte de la instancia al salir.
Una excepción antes de la llamada real y otra después de su retorno se distinguen
por contadores y estado REMOTE. Después del efecto se captura hash de P sólo
como observación, sin pasarla al CLIENT que perdió la respuesta.

## Estado, versiones y oráculos

Cada familia comienza con raíz propia, proyección revisada actual y ningún send.
T conserva captura I26 y SOURCE/EVALUATION/EFFECT; R usa SOURCE/BATCH, recibo y
selección TASK exactos. Registrar los hashes/revisiones que respaldan la proyección.
No elevar R a EVALUATION Markdown o I32 ni usar ticket no emitido.

ISSUE inicia UNKNOWN/ledger1/queries0 con send pendiente. QUERY incrementa queries
y añade pending de consulta, sin incrementar ledger. RESULT(None) incrementa
ledger, elimina sólo el pendiente identificado: con query_id elimina la consulta
y conserva send; con query_id=None elimina send. Por ello dispatch con respuesta
perdida puede dejar UNKNOWN sin pending send. UNKNOWN y un intento registrado
siguen bloqueando emisión/retry; no exigir un pending inexistente ni interpretar
su ausencia como no efecto. La matriz fija cada ledger/queries esperado.

En UQ11–UQ16, la consulta posterior de P correcta lleva ledger a 3 y queries a 2;
permanece CONFLICT/hard_conflict y no se adopta P en sends.proof.

RESULT con prueba incompatible fija CONFLICT/hard_conflict, incrementa ledger
y retira pendientes del send. Una P correcta posterior no elimina hard_conflict
ni habilita emisión, aunque el registro de observación conserve P. Distinguir
sends.proof, resultado del comando y evento OBSERVED; no afirmar que P se adoptó.

Comparar HEAD/seq/hash, cadena alcanzable, recibos/cid/request_sha256, estado local,
sends/attempts/ledger/queries/pending, prueba/código/retry_tick y REMOTE
entities/tickets/keys/versions/payload/foreign. Un efecto CREATE confirmado tiene
entidad única versión1, prueba vinculada al ticket emitido y payload/hash exactos;
lookup/reconcile nunca escribe REMOTE. Capturar antes/después de cada paso,
rechazo, CLOCK, lector y conciliación explícita. Un rechazo de retry conserva
HEAD/recibos/attempts; CLOCK es una operación local con su propio recibo y no se
oculta en ese contraste. No inferir oráculo de exitcode o PASS padre.

En UQ17/18 el RATE_LIMIT es prueba concluyente NO_EFFECT con retry_tick=5. Antes
del tick, rechazo sin nueva emisión; tras CLOCK 5, únicamente la llamada explícita
retry=True puede emitir ticket nuevo y producir efecto. Comparar con un send
UNKNOWN de raíz distinta que sigue BINDING_UNRESOLVED incluso después de CLOCK 5.
En UQ19/20 retry_tick=None conserva RETRY_NOT_ELIGIBLE tras CLOCK. Son controles
sintéticos de elegibilidad; no consumo ni reservas o retry de proveedor.

## Reapertura, evidencia y controles

Cada caso sustantivo tendrá lector de archivos independiente y CLIENT fresco en
spawn después del punto observado: lectura pasiva no consulta, no ejecuta, no
concilia ni cambia HEAD/estado. Las consultas de continuación son acciones
explícitas con contadores propios. Nunca inferir integración desde la suma de
PASS aislados: registrar una misma identidad/run/store/ticket a través de cada
secuencia integrada afirmada y sus observaciones anteriores/posteriores.

Raw nuevo I50 con esquema propio: ID/caso/path/rol/operación/modo/stage/fase/ronda,
run/store/cid/request, wrapper y llamadas reales, hash y clasificación del valor
observado, error controlado, HEAD/oráculos y punteros exactos. Para listas/envelopes
registrar tipo y cardinalidad como entrada inválida, no matches nativos. Para
OSError usar LOSS_BEFORE_REAL_CALL o LOSS_AFTER_REAL_COMMIT, jamás HTTP_429.
La tabla de representabilidad MG01–MG03 tendrá resultado NO_NATIVE_MODEL, no PASS.
MG03 describe una capacidad que sólo se consideraría en otro contrato: no añade
una obligación de selección/adopción a UI20.3 ni exige implementarla.

Runner rechazará optimize!=0 y comprobará contexto Python/build/platform/debug,
comando, hashes de entradas antes/después y conjunto descubierto. Discovery incluirá
source_ingest/*.py, testing/D5/*.py y fixtures/*.md, helpers HC reutilizados,
archivos nuevos, README y este contrato/matriz/sello, I48 y sus referencias de
preparación pertinentes. El informe expondrá reglas y lista completa. Hash igual
no demuestra por sí solo suficiencia de la lista ni de la semántica.

Guardas de lab: máximo cuatro hijos vivos, espera20s/caso120s/campaña900s,
256 eventos/caso,16KiB/evento,8MiB/raw; límites de dominio heredados. Fallar por
mapa incompleto/IDs duplicados/skips/timeouts/residuos. Ningún timeout negativo
cuenta como caída positiva. Inode/marker/sentinel/link se restauran antes de
cerrar sólo raíz propia; cero hilos/hijos/raíces propias restantes. No inspección
de dev/run_data/D4 ni certificación del host, energía/disco/NFS/Windows.

Si se aprueba I50, conservar campaña UQ24 propia y regresiones Python321, HC24,
HF40 e IC30 por separado, con raw/contexto/hash/inputs efectivo pre/post y
recursos propios. No sumar repeticiones/intersecciones como tests nuevos. No SQL,
Java, Docker, auditor ni cierres D1–D4 reejecutados. Ninguna de esas campañas se
ha ejecutado al preparar I49.

## Entregables, aceptación y decisión

Futuro I50: nuevo harness, README, raw UQ, raws/contextos de regresión separados,
results.md/results.json y correspondencia por UQ/UI/MG. Fuente/método/puntero/raw
resolubles; resultados declarados/semánticos/ejecución separados, MG no evaluado
como test. UI20.3/H07 y límites históricos I34/I36 no se completan por el conteo.
Si una expectativa contradice código, registrar y parar esa ampliación: no
cambiar producto ni reducir el oráculo sin una nueva decisión material.

**A — Aprobar este I49 y autorizar I50:** implementar/validar exclusivamente el
nuevo harness UQ01–UQ24 y regresiones separadas descritas, sin alterar API/modelo.
**B — Aprobar sólo diseño:** conservar implementación/pruebas pendientes.
**C — Ajustar contrato/matriz:** concretar el cambio antes de ejecutar.
La aprobación de A no acepta equivalencia de abstracción con 429/multicoincidencias
ni cierra UI20.3; una ampliación MODEL_GAP necesita contrato/decisión independientes.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado se conservan. D5 global,
G01–G07 y revisión global GI33/GI34/GI38/GI39/GI40 abiertos, cierre=false. P0 sigue:
I32, handoff y posteriores sin publicación. Sin proveedor/credenciales reales,
corpus privado, consumo/reservas, activación, promoción, despliegue ni D6.
