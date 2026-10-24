# D5 I52 — preparación de revisión CP01/CP05

Fecha: **2026-10-24**, Europe/Madrid. **PREPARED_FOR_SUFFICIENCY_REVIEW**.
[Plan I51](../design/D5-I51-CLOSURE-PLAN.md) ·
[Matriz de cierre](../design/D5-I51-CLOSURE-MATRIX.md) ·
[Campos/fuentes/casos](D5-I52-CP01-CP05-preparation.json).

Selección A sobre I51 autoriza preparar este expediente documental junto con
RV20, sin modificar automáticamente las valoraciones UI/GI de I48. Este documento
no cuenta como test, campaña SQL o aceptación global. Las ejecuciones IC nuevas
citadas pertenecen a la regresión IC30 separada de I52, no a CP05 como suite nueva.

## CP01 — datos disponibles y lo pendiente

- I32 conserva 84 hashes verificados contra su commit original 7b64d87. Los índices
  docs/README.md y testing/D5/README.md cambiaron después: integridad histórica no
  implica inventario completo actualmente aplicable. No se reconstruye el raw
  original I34/I36, que sigue NOT_RECORDED.
- D3 y D4 conservan manifiestos de cierre, versión, grupos y hashes de evidencia
  pública. A52 conserva su aceptación independiente y distingue D2 histórico de
  D5 V30. El catálogo JSON liga cada referencia con su hash y campo de origen.
- D4-I12 registra clean_target=30, comando propio y versiones por grupo/caso;
  eso no convierte las regresiones históricas D2/D3 a evidencia V30. I20 declara
  su entorno V1–V30 y propuestas V31–V39 por separado de D2 independiente.
- Si target/comando/versiones no está en el root del informe leído, se marca
  NOT_RECORDED_AT_REPORT_ROOT; no significa que falte en todos sus anexos. D1/D2
  aún no tienen inventario autónomo exhaustivo en esta preparación. Hay referencias
  preservadas en los otros manifiestos, sin reabrir sus cierres ni ejecutar SQL.

Antes de valorar UI01.2/UI04.1/UI09.2: acordar el conjunto explícito de targets y
resolver comandos/versiones en sus anexos públicos, separar historia conservada
de las campañas actuales por raw/contexto, y determinar qué límite histórico es
aceptable sin falsear ni eliminar obligación. No basta volver a ejecutar una suite
actual y etiquetarla como el stdout perdido de la campaña original.

## CP05 — correspondencia normativa pendiente de decisión

UI33 original pide dos procesos sobre estado durable, sin perder revisiones/recibos
ni duplicar intento; requiere contrato F para CAS/locks/crash. DF37 añade CREATE
repetido/tickets concurrentes con misma creation_key, índice único, prueba estable
por ticket/hash y reinicio sin duplicación. La descomposición I40 UI33.2 habla de
dos tickets CREATE/ISSUE simultáneos sin duplicar intento. I48 conserva PARTIAL
porque no se probó el ciclo de dos tickets distintos efectivamente autorizados.

La frase «dos tickets distintos efectivamente autorizados» no es literal del UI33
original, pero no se elimina sin revisar también DF37 y el contrato durable F.
La revisión debe distinguir un requisito legítimo de ciclo integrado frente a una
interpretación que exija emitir dos intentos donde la guarda de negocio prohíbe
el segundo. Se prepara esa cuestión; no se resuelve por un recuento de PASS.

La regresión IC30 I52 vuelve a observar las familias contractuales ya conocidas:
C1 idempotencia de la misma petición; C2 propuestas cid/send/ticket distintos con
un único ISSUE y rechazo de HEAD, luego BINDING_UNRESOLVED con HEAD fresca;
C3 mismo send/ticket con cid distinto; C4 misma cid con request incompatible;
R1 doble entrega del ticket emitido; R2 ticket extra nunca emitido sólo en REMOTE,
sin reconcile/adopción y sin atribución integrada. Los punteros exactos, actores,
órdenes y procedencia están en el JSON de preparación y el raw IC nuevo.

Propuesta para la revisión siguiente: resolver por separado «competición de
propuestas que no duplica emisión», «replay/entrega del ticket emitido» y «unicidad
de dominio frente a tickets distintos negativos», declarando qué obligación exige
una misma secuencia integrada. No declarar éxito de una emisión que nunca ocurrió,
no fabricar un ticket autorizado ni deducir integración de sumar esos casos.

UI33.2, las otras partes parciales y los cinco GI conservan sus valoraciones I48.
D5 global/G01–G07 abiertos; A52 y D1–D4 intactos. Sin publicación, proveedor/
credenciales/corpus real, consumo/reservas, activación, promoción, despliegue o D6.
