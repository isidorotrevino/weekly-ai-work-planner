# I100 — self.error: coste transitivo por expresión resuelto

Fecha: 2026-10-28, Europe/Madrid. Revisión documental autorizada por «continúa».
**Los92 callsites de self.error quedan acotados por fuente en eventos, incluidos
fn, argumentos y receptores: E_error≤1.985.** No se ejecutó producto, callback,
test o campaña. No se cambió implementación, cuota, perfil o autoridad.

[Censo con costes](../validation/D5-I100-transitive-error-review.json) ·
[Cierre de funciones](../validation/D5-I100-source-function-closure.json) ·
[Composición restante](D5-I100-REMAINING-CAPACITY-COMPOSITION.md).

## Descomposición completa de estas expresiones

| Parte del self.error revisado | Cota superior de eventos |
|---|---:|
| Cuerpos fn:27 expresiones distintas,92 callsites |1221|
| Contexto esperado:≤330 invocaciones×2 |660|
| fresh evaluado como receptor:≤45×2 Store construidos |90|
| self.state evaluado en otros argumentos:≤14 oráculos |14|
| Total de las expresiones self.error revisadas |1985|

La multiplicidad conservadora procede de I99: se suman alternativas mutuamente
excluyentes para sobreestimar. Cada fila identifica posición línea/columna,
tipo/binding del fn, coste por invocación y contribución ponderada. No se mezcla
el fresh previo al contexto con el cuerpo de snapshot. No quedan expresiones
fn sin clasificar dentro de esos92 callsites; esto no resuelve todas las
llamadas directas ni los with assertRaises escritos fuera de self.error.

## Contratos aplicados al fn, incluyendo prefijos de fallo

| fn resuelto por fuente | Eventos como máximo por invocación |
|---|---:|
| Client.perform/review/capture/import_event |4|
| Client.snapshot; Store.snapshot directo |2;1|
| Client.dispatch; Client.reconcile |13;12|
| Remote.execute |1|
| self.plan R |24|
| Reductores/planner/validadores revisados; _pin/create/close especificados |0 observados|

Los tipos no se deducen sólo del nombre: c se enlaza a lab.client/fresh, r a
Remote en DF19, st al Store explícito DF07, t al TClient importado en DR35,
y t_manifest a remote_manifest T en DR22. Se conservan los schemas de cada uno.
Las cotas de Client/Remote incorporan prefijos de excepción de I99; no exigen
convertir un fallo en retorno exitoso ni aplicar7 refs a un comando rechazado.
Los hooks locales revisados añaden0 boundaries; callbacks distintos quedan fuera.

Para los reductores/planners y builders se revisó un cierre nominal/importado
sobreaproximado de **88 funciones en10 archivos**. Incluye validators q.validate_*
pasados a checked(fn,value), parse de registro importado localmente y funciones
anidadas incluidas en sus cuerpos. No contiene llamadas a los observers, creación
de sus clases ni eval/exec/getattr/__import__. Condición: builtins de fixture
cerrados y stdlib sin sustituciones; no es un analizador general de Python.

_pin utiliza FixtureStore.inspect, cuyos _locked/_load no llaman los boundaries
snapshot/advance/transact. Store.create de DF07 usa genesis/_publish con hook=None;
ALREADY_EXISTS puede abortar antes. close realiza sus lecturas/cleanup sin un
observer de close. **Cero eventos observados conserva todo ese trabajo real**:
no prueba límites de bytes, CPU, memoria, referencias ni ausencia de efectos.
Esta revisión no ejecutó ninguno de esos métodos.

## Argumentos y oráculos

Además del receptor fn, se inventariaron todas las llamadas en pattern/args/kwargs.
Son builders/encoding/hash/UUID/deepcopy de datos cerrados y14 self.state por
la sobreestimación de ramas. self.state llama independent una vez. Su wrapper
emite1 CAUSAL_TERMINAL; las nuevas filas de oráculo y enlaces se cargan en refs
y sidecar, no como eventos extra. Sus bytes y fanout siguen pendientes.

Un self.error aceptado no prueba que el observador pueda proyectar la excepción
ni sustituye campos ausentes. Los negativos conservan los requisitos I99 y los
missing originales; no se crea una exención N/A.

I97 conserva R≥19.037>16.384. I98/I99 no se reescriben. D5/H07/G01–G07 y
GI33/34/38/39/40 globales siguen abiertos; P0,83/1 y UI04.1 parcial, D1–D4 e
I1–I20/A52 conservados. Sin operaciones reales, publicación ni D6.
