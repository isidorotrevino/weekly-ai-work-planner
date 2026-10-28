# I97 — cotas parciales y recursos pendientes

Fecha: 2026-10-28. Análisis de fuente y aritmética stdlib sobre esquemas; cero
ejecución de producto o campañas. [Datos y esqueletos JSON](../validation/D5-I97-resource-bounds.json).
Complementa I96 sin alterar sus fuentes ni sus sellos.

## Fanout de testigos acotado por la fila aceptada

El grupo d5.domain-witness-group.v1 contiene cuatro UUID de36 caracteres,
contexto y lista de witnesses. Usando refs mínimas de2 caracteres y CLIENT
(igual longitud que REMOTE), el esqueleto vacío mide333 bytes JSON compacto.
Un witness con object_ref y la autoridad permitida más corta,
OBSERVED_PARENT_RETURN, mide60. Por tanto, para n testigos:

`bytes ≥333 +60n +max(0,n−1)`.

Con61:4053; con62:4114, superior al límite4096. Una fila aceptada tiene así
**a lo sumo61 witnesses**. Usar refs repetidas en el esqueleto mínimo sólo
reduce la longitud: no afirma que61 sea alcanzable con identidades distintas.
Refs reales más largas y autoridades adicionales aumentan el tamaño.

Q34/Q36/Q38 cargan1+witnesses: peso≤62. Un link con dominio carga además L y2
extremos:≤65 en total; sin dominio son3. Sigue sin cota superior la cantidad
de grupos, objetos y links. Esta acotación de un factor no resuelve R global.

## Cinco contribuciones adicionales fijas

Condicionadas a captura completa válida y al lifecycle pinneado:

| Sitio | Cargos totales | Ruta |
|---|---:|---|
| Q12 |2| FixtureStore de setUp DI28 y fixture del cuerpo |
| Q13 |2| Membresías de esas mismas dos construcciones |
| Q27 |2| assertEqual de snapshot y exitcode DI07 |
| Q28 |1| TEST_RESULT raíz DI07, sin subtests |
| Q29 |2| command.snapshot y expected.snapshot DI07 |

message usa assertTrue. Genesis, advance y cleanup de esos fixtures no llaman
snapshot ni añaden constructores parentales. child_snapshot ejecuta en el hijo
y no añade observaciones parentales. No se equiparan estas nueve unidades con
todo el coste de DI07/DI28: el resto sigue en los demás sitios activos.

## Pisos de eventos y sidecar; valores aún sin envolvente suficiente

Los2582 comandos obligatorios de la cota mínima producen al menos4 eventos
cada uno: Store.snapshot y Client.snapshot CALL_RETURN, Store.transact
CAUSAL_TERMINAL y Client.perform CALL_RETURN. Con3 eventos por cada frame:
**eventos≥11.291**. Estar por debajo de131072 no prueba suficiencia de campaña
ni del límite2048/test; faltan cotas superiores de todos los eventos.

También hay al menos2582 links SAME_THREAD_NESTED_CALL. Un cuerpo mínimo de
fila mide318 bytes: **al menos821.076 bytes sólo en esos cuerpos**. No incluye
claves del mapa, delimitadores ni otras filas/tablas. No permite concluir que
el sidecar completo cabe en12MiB.

Los máximos de commit/objeto de fixture de32MiB no certifican operand_bytes de
16MiB del observador, que contabiliza representaciones/auxiliares de encoding
y hashes. Tampoco demuestran un valor real sobredimensionado: falta acotar los
valores efectivamente observados del workload. No se propone truncamiento,
muestreo, pérdida de evidencia ni cambio del significado de un retorno.

Las envolventes Reader I96 siguen condicionadas al calendario y fuentes del
perfil original. Ninguna medición ni perfil nuevo procede de este documento.

## Pendiente antes de preparar otra captura

SC01: cotas superiores de multiplicidades de los30 sitios activos, con
lifecycle/callbacks. SC02: grupos, objetos, contextos y autoridades; fanout61
acota sólo un factor. SC04: eventos/test/campaña, bytes de filas/tablas y valores
completos. SC05: proponer contrato/perfil/cuotas numéricas sólo con esa cuenta;
la decisión de implementación/componentes y la funcional permanecen separadas.

El siguiente trabajo documental es descomponer helpers parentales T/R por
categoría de comando y por objetos/contextos, preservando ramas desconocidas.
No se autoriza aquí otra captura ni repetir I92. IR03, suficiencia global y
publicación conservan decisiones propias. I95/CB32 sigue evidencia sintética
de componentes, no compatibilidad P01.

P0;83/1 y UI04.1 parcial. D1–D4 e I1–I20/A52 conservados. D5/H07/G01–G07 y
GI33/34/38/39/40 globales abiertos. Sin operaciones reales ni D6.
