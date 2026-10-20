# D4 I9 — resolución concluyente y checkpoint desde reconciliación

Fecha: 2026-10-20. Estado: decisiones A/A/B aprobadas (A17–A19); implementación y validación acotada completadas; D4 abierto.
La petición del usuario autoriza ampliar el trabajo a contradicciones y continuidad
 desde RECONCILING. Las respuestas expresas aprueban la ruta sellada y amplían el alcance a v1 y recuperación terminal.
V1–V25 y los informes existentes se conservan.

## Fronteras existentes

V9 mantiene lease, reserva y exclusión al expirar; EXPIRE entra en RECONCILING.
UNKNOWN puede llevar a BLOCKED_APPROVAL. V13 exige identidad exacta incluso en
recuperación y bloquea liberación/retry si hay hechos contradictorios.
V24/V25 admiten checkpoints solo RUNNING con lease viva y pruebas APPLIED/ABSENT;
multi_effects_safe rechaza cualquier UNKNOWN o discrepancia histórica. Por ello
una nueva prueba concluyente no basta por sí sola: falta una relación explícita
entre hechos anteriores y resolución, y una guarda que revise esa relación.
No se deben retirar esas guardas globalmente ni fabricar ABSENT para habilitar CLAIM.

## Propuesta común

Una resolución es un hecho append-only, no UPDATE/DELETE de recibos. Identifica
operación, intento, generación, intención cerrada v2 y contexto/política; referencia
el conjunto completo ordenado/hash de recibos históricos y el cierre durable del
único receptor, su identidad/diario y secuencia final. El verificador independiente
comprueba parada actual del grupo y consulta directamente ese cierre. Ni worker ni
driver pueden declarar autoridad, saldos o estado final por su cuenta.

El ingreso debe usar command_id idempotente y CAS del conjunto observado; un recibo
nuevo, cambio de cabeza/contexto/política o prueba incompleta invalida la admisión.
La exclusión y los compromisos siguen retenidos mientras falta prueba concluyente.
Ningún grant se renueva y el receptor cerrado no vuelve a abrir la generación.
La resolución no equivale a aceptación final del producto.

Contabilidad: calcular solo el delta APPLIED aún no liquidado por paso/cuenta, desde
costes congelados y procedencia de checkpoints anteriores. No duplicar CONSUME ni
compensar efectos; no liberar más que el compromiso pendiente real. Mantener reserva,
mapping y vector original, 70/20/10, límite D2 de intentos y TOP_UP completo.
La elegibilidad de continuación debe incorporar resolución/cabeza al readset,
snapshot/publicación/CLAIM y revalidar dependencias, prioridad y ventanas.

## Decisiones materiales

1. Autoridad: A recomendada, cierre concluyente del mismo receptor/diario y resultados
   monotónicos. UNKNOWN y ABSENT históricos pueden quedar explicados por APPLIED
   probado; un APPLIED previo nunca se convierte en ABSENT. Hash distinto, pérdida
   de diario o receptor que niega un APPLIED previo siguen bloqueados. B: admitir
   invalidación de un APPLIED por arbitraje externo, que requiere otra autoridad y
   contrato de revocación de evidencia; no existe hoy en el laboratorio.
2. Ciclo de vida: A recomendada, entrada nueva RECONCILING→CANCELLED exclusivamente
   por checkpoint de recuperación sellado; aceptar BLOCKED_APPROVAL solo mediante
   resolución explícita que retorna primero a RECONCILING, sin liberar allí. Reutilizar
   después autorización y rearme expresos A08/A12, mismo contador y nueva generación.
   B: RECONCILING→READY directo autorizado, con admisión nueva distinta de la existente.
   No habilitar cancelación ordinaria ni rearmar automáticamente en ninguna opción.
3. Alcance: A recomendada, manifiestos v2 lineales multicuentas, prefijo APPLIED y
   sufijo ABSENT no vacío; v1 y caso completamente APPLIED conservan recuperación
   existente/bloqueo y se documentan fuera de este incremento. B: incluir también
   v1 y resolución completamente APPLIED con aceptación final independiente, que
   amplía adaptadores, liquidación terminal y matriz de upgrade.

## Plan de validación original y resultado posterior

SQL: upgrade V25 vivo sin mutación de hechos, roles, JSON cerrado, CAS, replay,
recibo nuevo tras resolución, APPLIED incompatible, UNKNOWN/pérdida de diario,
parada/cierre ausentes, doble consumo, doble autorización, intentos agotados,
cuenta vencida/déficit, snapshot obsoleto y fencing de generación vieja.
Compose: expiración real D2, proceso observado/parado por canal independiente,
contradicciones conservadas, resolución autoritativa, checkpoint de recuperación,
continuación explícita del sufijo en misma operación/reserva y consumo final exacto.
Añadir negativo de evidencia inconcluyente; regresión S14/S15 y suites afectadas.
No se cuentan escenarios por estar enumerados; registrar resultados y limitaciones
propios, sin promoción, credenciales reales ni cierre D4.

## Mapa de integración que no cambia las decisiones pendientes

| Punto | Cambio necesario si se aprueba la ruta sellada |
|---|---|
| SQL propuesto posterior a V25 | Tablas de resolución/procedencia append-only, comandos idempotentes y entradas limitadas; ningún cambio de bytes V1–V25 |
| `multi_effects_safe` | Conservar el rechazo histórico por defecto; admitir solo recibos cubiertos exactamente por una resolución vigente, sin ignorar hechos posteriores |
| Evaluación/commit | Ruta específica sin exigir lease viva; sí exige lease exacta retenida, estado reconciliable, prueba independiente y cierre irrevocable. Nunca reutilizar una bandera para saltar la guarda RUNNING de V25 |
| `multi_heads`/`multi_head_settled` | Checkpoint de recuperación conserva cadena, contabilidad, intención y vinculación exacta al intento; no permite forks |
| `multi_authorize`/`multi_safe` | Revalidar resolución y conjunto de recibos actual en autorización y CLAIM; no confiar solo en que alguna resolución existió |
| Snapshot/readset/CAS | Incluir resoluciones y enlaces; cambios posteriores a captura invalidan publicación y despacho |
| Verificador | Parada por observador host, bytes observados y cierre firmado consultado al receptor, mismos hashes y generación; sin credenciales del worker ni SQL libre en driver |
| Compose | Escenario propio con expiración real de 60 s, parada demostrada, conservación de contradicciones y continuación explícita; negativos separados y limpieza por proyecto |

Un recibo nuevo después de sellar no se considera explicado por proximidad temporal.
La prueba de resolución cubre IDs y contenido exactos; su vigencia se recalcula.
APPLIED de hash desconocido/incompatible no se puede borrar mediante una declaración
humana o un booleano del verificador. La identidad del diario no puede depender
únicamente de un número de secuencia que otro diario nuevo pudiera repetir.

El cálculo debe distinguir consumo previamente liquidado, consumo nuevo comprobado
y compromiso pendiente real. Si el journal no permite demostrar la procedencia
exacta por paso/cuenta, mantener bloqueo; no ajustar saldos para que coincidan.
En particular no tratar CALLBACK perdido y CALLBACK comprometido como el mismo
estado contable. La ampliación no autoriza corregir journals históricos.

Respuestas recibidas: A17=A, A18=A, A19=B. Las alternativas se conservan como
historia de revisión, no como preguntas pendientes. No hay aprobación de cierre.

Resultado posterior: [I9 validado](D4-I9-RECONCILIATION-LAB.md) registra el alcance
ejecutado y sus límites. La enumeración del plan original no acredita cobertura
Compose de todos los negativos; prevalece el informe de resultados final.
