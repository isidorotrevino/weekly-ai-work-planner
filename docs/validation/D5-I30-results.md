# D5 I30 — resultados de relaciones y lotes sintéticos

Fecha: 2026-10-22. Base publicada: `ca7efea`.
[Laboratorio](../design/D5-I30-RELATIONAL-BATCH-LAB.md) ·
[Contrato aprobado I29](../design/D5-I29-RELATIONAL-BATCH-DESIGN.md) ·
[Informe verificable](D5-I30-results.json).
**PASS de modelo en memoria; D5 global y G01–G07 abiertos.**

D5-A71 aprueba I29 y autoriza RB01–RB34 con fixtures en memoria, conservando A68–A70.
Sin SQL, HTTP, credenciales/proveedores reales, efectos persistentes D2, activación,
promoción, despliegue o D6. No se modifica código/configuración/evidencia históricos.

## Campaña ejecutada

`python3 -m testing.D5.run_batch_lab`, Linux/Python **3.14.4**, biblioteca estándar:

| Grupo | Tests distintos | Fallos / errores / omisiones |
|---|---:|---|
| I30 relaciones/lotes RB01–RB34 | 38 | 0 / 0 / 0 |
| I28 conciliación Plane de fixture | 41 | 0 / 0 / 0 |
| I26 captura incremental de fixture | 30 | 0 / 0 / 0 |
| I24 integración offline | 35 | 0 / 0 / 0 |
| Python local anterior | 51 | 0 / 0 / 0 |
| Total de esta campaña | **195** | **0 / 0 / 0** |

Las 34 filas de matriz no se suman como tests adicionales. El JSON mapea los 38
nuevos a esas filas e identifica los 195 IDs distintos. Las 157 regresiones se
reejecutaron ahora; no son números copiados de I28. No se reejecutaron SQL/D2/D3/D4.
El elapsed es una observación de campaña, no benchmark.

`python3 -m testing.D5.demo_relational_batch` confirma un lote tipado de tres
entidades y dos vínculos, simula respuesta perdida y recupera el mismo recibo
mediante replay. Hay una sola data_generation aplicada y un comando confirmado.
La salida saneada evita texto fuente/destinos; cero solicitudes remotas reales.

## Resultados observados

- RB01–RB12: bytes/hash/localizadores exactos, UUID/claves explícitos y endpoints
  de solo lectura, tipos/proyectos y coherencia del grafo final completo. No se
  ignora una relación preexistente inválida fuera del paquete. Uniones repetidas
  retienen evidencia, TASK_EPIC no reasigna, todos los self-loops bloquean y los
  ciclos HARD existentes/nuevos se detectan. Los tipos no HARD se conservan.
  Una ausencia posterior no elimina entidades ni relaciones.
- RB13–RB19: creación, actualización y relaciones se confirman juntas. Identidades,
  claves o tipos incompatibles y una relación final inválida impiden todo efecto.
  Edición local previa no se convierte en base de origen; cambios posteriores o
  ABA invalidan la generación. Guardas de estado/trabajo de entidades y tareas
  relacionadas bloquean mediante flags sintéticos, sin insertar operaciones.
- RB20–RB23: fuente y lote tienen aprobaciones separadas. Revocación/reemplazo,
  incluso después de construir el candidato y antes del CAS, bloquea. Aprobar no
  modifica el hash del manifiesto ni su generación de datos. Dos hilos compiten
  desde candidatos aprobados con barrera: solo uno confirma y el otro devuelve
  CONFLICT_DATA; existe una sola entidad/recibo del ganador, sin prefijo del perdedor.
- RB24–RB28: fallos en candidate_ready/before_publish conservan toda la raíz.
  Una excepción after_publish pierde respuesta, conserva efectos/recibo juntos y
  permite recuperación exacta por comando/hash sin duplicar. Replay histórico no
  restaura texto ni rebobina cabeza. Texto/asignación de épica incrementan una vez
  row_version; no-op la conserva, con procedencia/cabeza D5 avanzadas una vez.
- RB29–RB34: description de EPIC y claims/instrucciones siguen siendo evidencia.
  Shapes/JSON/tipos/IDs/modo/límites bloquean sin reparación. Otro modelo volátil
  no hereda recibos ni autoridad y no acredita reinicio de proceso del batch.

Se alcanzaron realmente **32 elementos y 64 declaraciones por paquete**, **128
entidades**, **256 relaciones** y **128 comandos confirmados**; el siguiente se
rechaza. Replay confirmado sigue recuperable al alcanzar el límite de comandos.
Fuente >2 MiB, texto de 8.193 caracteres y un manifiesto real >4 MiB se rechazan
sin truncar. El último usa 22 elementos con campos válidos de 8.192 caracteres
multibyte y fuente inferior a 2 MiB. No se atribuyen estos casos a una prueba con
presupuestos reducidos ni se extrapolan a rendimiento de producto.

Los **dos hilos nuevos propios** terminan; I30 no crea raíces de datos o hijos de
proceso. Las regresiones conservan sus **ocho hilos I28 terminados**, **33 raíces
I26 eliminadas** y **cero hijos propios vivos** de siete iniciados: tres normales
y cuatro SIGKILL controlados. Recuperación filesystem/hijos pertenece a I26;
no al batch en memoria I30. Dev/run_data/D4 reales no se inspeccionan ni borran.

## Preservación y límites

Entre archivos anteriores solo se amplían índice y guía D5. Se contrastan todos
los demás archivos de la base, 245 entradas de cierres D3/D4, canónico D4 y 560
entradas de campañas D5 I4–I20. I21–I29 y aceptación local mantienen sus bytes;
sus inputs documentales se contrastan con el commit correspondiente cuando los
índices/guías han evolucionado. Se comprueban enlaces, diff y patrones de
publicación; estos patrones no son una garantía universal de ausencia de defectos.

GI28/GI29 obtienen evidencia de **modelo sintético**: 27/35 S con evidencia acotada,
ocho S y siete R pendientes. No se acredita SQL/D2/V30 completo, capacidades o
dependencias cross-project, grooming real suficiente, persistencia/reinicio del
batch, aislamiento de un caller hostil o efecto de proveedor. GI30 y los criterios
integrados GI38/GI39/GI40 siguen pendientes. G01–G07 siguen abiertos y el hito
D5-LOCAL-SYNTHETIC-I1-I20 conserva su aceptación/perímetro exactos.
