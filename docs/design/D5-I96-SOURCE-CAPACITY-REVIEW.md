# I96 — capacidad por fuente: MRO y Reader de evidencia acotados

Fecha:2026-10-27, Europe/Madrid. **DOCUMENTARY_MRO_AND_READER_ENVELOPES_RESOLVED_FULL_CAPACITY_UNRESOLVED**.
La petición «continúa» se aplica a la revisión documental pendiente después de
I95. Cero implementación/cuotas/campañas nuevas, imports de producto/runners o
publicación. I95 mantiene CB32 PASS sólo sintético; I86/I89/I92 inválidos.

[Inventario completo](../validation/D5-I96-source-capacity-review.json) ·
[Calendario de Reader](../validation/D5-I96-reader-envelope.json) ·
[30 obligaciones de carga](D5-I96-REFERENCE-OBLIGATIONS.md).

## Herencia resuelta y corrección del catálogo anterior

Recorder efectivo: selectors.Recorder → selectors.BaseRecorder → late.Recorder →
typed.Recorder → prospective_capture.Recorder. Estado: DomainState → ParentalState →
CausalState. Las bases y los aliases de imports están verificados por AST/hash,
sin importar esos módulos. **typed.Recorder hereda de c.Recorder original**:
no incluye paged.Recorder, aunque haya módulos/helpers históricos pinneados.

El catálogo I94 etiquetó paged.Recorder.owner:146 como posiblemente alcanzable.
Esa etiqueta era incorrecta para este MRO: se corrige aquí, sin tocar I94/I95.
Los seis sitios de paged.Recorder quedan inactivos; link/message de CausalState
están sobreescritos sin delegación super: dos más. Resultado: **38 candidatos,
8 inactivos,30 activos/condicionales**. Esto corrige el análisis de fuente; no
reduce retrospectivamente16393 de I92 ni cambia ninguna regla ejecutable.

BaseRecorder.start crea contexto para **todos los321 frames**, y su emit añade
contexto/membresías de TEST_RESULT sin exigir causal_enabled. El guard118 aplica
a otros boundaries: no sirve para contar sólo118 roots/resultados. Se preservan
los321 bindings de12 grupos y se amplió documentalmente cada uno por self.helpers
y raíces lifecycle locales. Son 156 posiciones de bucle distintas
en ese alcance: aún no es cierre de imports/despacho de objetos o concurrencia.

## Cinco términos que ya tienen cota por fuente

- Inicialización LateBindings:1 builtin.dict, cargado una vez en este worker.
- prepare:como máximo2 bindings tardíos adicionales, por transición BOUND y
  allowlist de3 clases. Las comprobaciones posteriores de hashes no son gratuitas:
  su multiplicidad de lecturas se analiza por separado.
- finish del recorder:carga manifiesto de páginas una vez, entre1 y32 en una
  captura completa. No son32 cargas por cada frame.
- Registro directo DI07:como máximo1 pareja por selector/frame, más sus cargas
  de G key/objetos/protocolo en otros términos. No confundir esta cota con13 o
  con todo el coste del protocolo.
- stop completo:321 unidades constantes **más** Σowner_context_refs por frame;
  la cardinalidad variable sigue pendiente.

No se calcula una nueva cuota con estas constantes: R=Σ(qᵢ×Nᵢ) conserva todos los
otros símbolos abiertos. No se extrapola13/321 ni se deduplica identidad física.

## Reader de evidencia: cota conjunta normal cerrada por fuente

launch lee raw/sidecar una vez. typed.validate_pages recorre páginas una vez;
selectors.validate_pages las recorre otra vez para la causalidad. packet.finish
relee raw/sidecar/páginas ya registrados. El chequeo final de paquete lee OWNER
si aún no estaba en ese Reader. Contexto y launcher hermano se escriben después:
**no los lee ese Reader de evidencia en esta ruta normal**.

Por tanto, **reads=2(raw+sidecar)+3·páginas+36**. Con12+12MiB y64MiB de páginas:
**251,658,276 bytes =240MiB+36**, frente a256MiB; margen
**16,777,180 bytes**. Únicos:
**92,274,724 bytes =88MiB+36**, frente a128MiB. Esto resuelve la condición
conjunta de bytes de **ese Reader en la ruta normal pinneada**. I94 sólo había
mostrado que tres escaneos de todo el paquete serían excesivos; no había afirmado
que fueran el calendario real. La ruta real no escanea contexto/launcher allí.

No es una medición nueva ni prueba de compatibilidad, RAM, cleanup, fsync o
persistencia. Quedan fuera otros Readers, lecturas directas fd/stdlib y rutas
parciales/error no certificadas en este cálculo. Un perfil futuro que cambie el
calendario necesitará otra cuenta; no se puede atribuir esta cota a cualquier
paquete por tamaño o hash.

## Reader de inputs: envolvente estática y cierre de checks tardíos

Cada proceso launcher/worker tiene su propio Reader de inputs; no se suman como
si fueran uno ni se reinician dentro de cada uno. Una autoridad I92 contiene292
pins/63.070.664 bytes. Su validación además relee registro, raw/sello I91 y sus
artefactos. Se expandió ese calendario por archivo sin llamar a authority():
**65,612,121 bytes por pasada**, más runner inputs de998408 bytes por pasada.
Las dos pasadas de autoridad y dos del runner dan una base conocida de
**133,221,058 bytes** por ámbito que recorra esas rutas, antes de registry,
target bindings y checks tardíos. No es el total runtime ni un inventario futuro.

LateBindings.check relee fuentes según clases ya BOUND:32708·N_plane+
27464·N_eligibility bytes, más primeras lecturas de binding. prepare/check/projector
pueden comprobar varias veces el mismo operand; los N no se deducen de2 clases
ni del número de tests. Quedan **135,214,398 bytes** como máximo
optimista antes de las otras lecturas: no es margen disponible demostrado.
Se resolvió después el calendario estático restante:registry completo
22,791,067 bytes; targets≤272,631; once bindings causales≤127,101;
primeras cargas tardías≤60,172. Así, la envolvente del worker queda
**R_worker≤156,472,029+32708·N_plane+27464·N_eligibility**, y cumplir el Reader
requiere que la suma real quede≤268435456. Quedan **111,963,427 bytes**
para checks repetidos tras esas cotas estáticas; los N siguen desconocidos.
El launcher sin esos checks tardíos queda acotado por156,012,125 bytes
en esta ruta. La unión de nombres de inputs del perfil actual tiene293 paths,
**63,104,330 bytes únicos**, bajo128MiB; no incluye las lecturas directas fuera
de ese Reader ni autoriza el inventario de un perfil futuro. No se descuenta una
relectura por compartir nombre: cada pasada sigue cargando bytes. El JSON expande
cada read por función/motivo, incluidos anchors que repiten el mismo archivo.

Los métodos actuales launch/main no llaman inputs.finish(); el finish del
preflight documental I91 era otro ámbito. Si un perfil nuevo añade finish, debe
cargarlo expresamente. No se eliminan checks ni se resetea el Reader para caber.

### Cierre por fuente del término de checks

La revisión posterior de los cinco scopes tipados encontró **9 llamadas directas**
al helper seleccionado:5 assertEqual en el caso de guardado LocalPreview,1
assertNotEqual en el de revisión,1 assertIsInstance en cada uno de los dos PC10
y1 en PQ26. Están fuera de bucles/callbacks anidados; sus cierres self.helper y
lifecycle locales no añaden llamadas a ese helper. Con2 operandos por llamada:
**≤18 invocaciones de operand tipado**. El guard depth0 impide contar otra vez
las aserciones internas de unittest. No se cuenta todo assertEqual de321 tests:
la rama tipada exige test_id y helper exactos de esos cinco scopes.

Cada operand puede provocar como máximo4 checks:2 en prepare y2 en observe;
class_row/instance_row sólo recorren bindings ya retenidos y no llaman check.
Se añade1 check en finish. Por tanto, **N_plane≤73 y N_eligibility≤73**. Se asume
conservadoramente que ambas clases ya estén BOUND en todos esos checks, aunque
algunas rutas usan digest builtin y otras ocurren antes de los bindings.
Las primeras lecturas para bindear ya se incluyeron aparte en la base estática.

Checks repetidos≤**4,392,556 bytes**; worker completo en esta ruta de fuente:
**≤160,864,585 bytes**, bajo256MiB, margen **107,570,871 bytes**.
Esto cierra la envolvente de bytes del Reader de inputs para el perfil pinneado;
no es una ejecución ni prueba de que P01 alcance321/12, cumpla referencias/eventos
o satisfaga sus predicados. Los9 callsites y anclas de ambos extremos están en
el JSON. Una modificación futura de scopes, helper, callback o perfil invalida
la aplicación automática de esta cota. Las ecuaciones anteriores conservan la
secuencia de revisión: los N que allí estaban pendientes se acotan aquí por fuente.

## Recuento estructural de I92, sin reconstruir su fallo

Se recorrieron las páginas ya selladas, sin reejecutar ni validar como completa
la captura. Las estructuras visibles dan una demanda de carga por el modelo de
fuente de **16388**; el contador retenido es16393. La diferencia5 es **aritmética**,
no una traza de asignaciones omitidas ni identificación del primer wrapper.
Un expediente inválido puede contener mutaciones parciales y cargos fallidos:
no se llama a este recuento «cargas comprometidas» ni se completa su historia.
El JSON desglosa cada término y pointer/campo. No se extrapola al resto de308 tests.

## Estado y siguiente obligación concreta

Los calendarios de ambos Readers y el MRO están acotados por fuente en este alcance;
**capacidad P01 completa NOT_ESTABLISHED**, refs16384 y todas las24 cuotas intactas.
Siguen SC01/SC02/SC04: multiplicidades de30 sitios, fanout por contexto y
demás cuotas conjuntas; SC03 se acota para el perfil actual y debe revisarse
si cambian código, autoridad o calendario; SC05 reserva la decisión numérica/perfil nuevo.
No existe certificado numérico, perfil nuevo de captura ni autoridad/destino
funcional. Este expediente usa I96 como revisión documental, no como campaña:
una captura posterior tendrá otra numeración/destino tras decisiones separadas.

El cierre global requiere además conservar las42 obligaciones normativas I23 y
sus siete filas reales/humanas, ya separadas en la ruta de cierre posterior a I86.
Las exclusiones P0 actuales no permiten sustituirlas por estos componentes. No
se mueve ningún requisito a D6 ni se presenta el avance sintético como cierre.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL(UI04.1). D1–D4 cerrados e I1–I20/A52 aceptado,
30/35 sin promoción; D5/H07/G01–G07/GI33/34/38/39/40 OPEN. Sin proveedores,
credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue,
SQL/Java/Docker nuevos o D6. Evidencia anterior/Git intactos; sin commit/push.
