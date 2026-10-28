# I99 — coste de excepciones parentales y self.error

Fecha: 2026-10-28, Europe/Madrid. Revisión documental por «continúa».
**Las rutas negativas no heredan el coste de retorno exitoso.** No se ejecutó
producto, test, callback ni campaña; no se creó perfil, cuota o autoridad.

[Censo y árboles](../validation/D5-I99-parental-error-review.json) ·
[Ramas por fuente](../validation/D5-I99-parental-exception-costs.json) ·
[Composición pendiente](D5-I99-CALLBACK-AND-COMPOSITION-REGISTER.md).

## Censo acotado de self.error

Se revisaron92 callsites estáticos:42 T y50 R. La expansión de los88 métodos
DF/DR, con bucles literales y suma conservadora de alternativas/handlers/finally,
da **como máximo107 invocaciones T y223 R:330**. El exceso deliberado de ramas
mutuamente excluyentes no se presenta como cantidad exacta de una ejecución.
No hay bucle desconocido que alcance self.error en este cierre revisado. Esto
no incluye todos los with assertRaises directos de P01 ni callbacks desconocidos.

El helper error de ambas clases evalúa primero sus argumentos, entra en
assertRaisesRegex, invoca fn una vez y sale del contexto original. En una
excepción esperada aceptada hay **2 eventos de contexto**:
EXPECTED_EXCEPTION_DECLARED y EXPECTED_EXCEPTION_EXIT_OBSERVED. La fuente
stdlib de __exit__, inspeccionada sin ejecutar tests, coincide por hash con el
pin del registro: verifica tipo/regex sin añadir otra aserción observada en PASS.
Por tanto, el andamiaje de esos self.error aporta **como máximo660 eventos**.
El coste de fn y sus argumentos se suma aparte; no es0 por defecto.

Por ejemplo, lab.fresh().snapshot construye los objetos de fresh al evaluar el
receptor, antes de entrar al contexto. El JSON registra esa contribución separada;
no se debe omitirla ni cargarla otra vez como si snapshot construyera el Store.
Las cotas de660 y de I98 no demuestran un total global de eventos.

## Prefijos de excepción observables

Condición: fuentes/MRO/selectores actuales, frame causal T/R, wrappers abiertos
correctamente, excepción original y proyección válida. Se excluyen aquí owners,
contextos, objetos fuertes, aserciones y construcción externa.

| Ruta | Eventos locales | C keys | Q35 de retorno | L/Q37 anidado |
|---|---:|---:|---:|---:|
| perform falla en snapshot antes de transact |3|1|0|0|
| perform obtiene snapshot y falla transact |4|2|0|0|
| Client.snapshot falla en Store.snapshot |2|0|0|0|
| Store.snapshot directo falla |1|0|0|0|
| Remote.execute raíz falla transact |1|1|0|0|

En perform, el causal terminal del caller sigue dentro de CALL_EXCEPTION mediante
publish=False. Store.transact emite CAUSAL_TERMINAL con excepción. DomainState
añade los2 slots Q35 sólo cuando exception is None. El except de wrap_boundary
relanza antes del código de link: **no añade L ni los2 extremos Q37** de ese
enlace anidado. Los C ya abiertos sí siguen cargados y conservan sus terminales.

Así, las7 unidades del subconjunto de un comando anidado exitoso pasan a2 si
falla transact, o1 si falla el snapshot antes del Store. No es el coste completo
de referencias del fallo. I97 sólo usó comandos exitosos requeridos por una
captura completa válida: su piso19.037 sigue intacto.

Los prefijos de dispatch rechazado en ISSUE y reconcile rechazado en QUERY
aportan como máximo6 eventos cada uno, bajo estas condiciones. self.plan R,
usado como fn de varios self.error, tiene como máximo6 perform/24 eventos;
con los2 del contexto,≤26, sin argumentos ni constructores externos. Sus rutas
transitivas deben seguir asociadas al callsite y a la excepción real.

## Un negativo esperado no valida el observador

El selector negativo de Store.transact sólo interviene si construir request
falla con un input_failure permitido para ese test. Entonces exige además que
el código de excepción original pertenezca exactamente a exception_codes.
El regex que satisface self.error no sustituye ese cotejo ni aporta recibo/cid.
El digest inicial de Client.perform no tiene ese mismo fallback. Un fallo de
instrumentación sigue invalidando la captura aunque unittest acepte la excepción.
No se crea una dispensa N/A por llamar negativo al test.

I83–I98 y sus sellos permanecen intactos. P0;83 SUPPORTS_BOUNDED/1 PARTIAL,
UI04.1 parcial; D1–D4 cerrados e I1–I20/A52 aceptado. D5/H07/G01–G07 y
GI33/34/38/39/40 globales abiertos. Sin operaciones reales, publicación ni D6.
