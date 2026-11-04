# I105 — historia, limpieza y salida pública: siete cotas de eventos

Fecha: 2026-10-28, Europe/Madrid. Continuación documental local de I104.
**40 de 88 raíces T/R tienen ahora una cota completa de eventos por fuente**.
No se importó el producto/runner ni se ejecutaron tests, hijos o campañas.

[Desglose, anclas y prueba del bucle](../validation/D5-I105-history-cleanup-event-bounds.json) ·
[Registro acumulado](../validation/D5-I105-event-bound-coverage.json) ·
[Revisión anterior I104](D5-I104-PARENTAL-PROTOCOL-EVENT-BOUNDS.md).

| Raíz | Máximo de eventos, condicionado por fuente |
|---|---:|
| DF01 | 7 |
| DF41 | 109 |
| DF42 | 91 |
| DF43 | 11 |
| DF45 | 249 |
| DF47 | 101 |
| DF48 | 8 |

Son envolventes de una ruta original completa PASS con observación válida,
fuentes/bindings pinneados y sin callbacks nuevos. No son resultados de pruebas.
El subtotal nuevo es 576; el acumulado de 40 raíces es 18274. Este último
**no es una cota global**, ni una cota inferior: exceder 16384 con una suma de
cotas superiores parciales no prueba que los eventos reales excedan ese límite.
Tampoco se suma a los helpers de I100, pues se solapan.

## DF45: acotar el while sin usar el presupuesto como premisa

El guard lee snapshot antes de cada vuelta y continúa mientras head.seq < 23.
Store._load valida el génesis con seq=0 y sus transiciones; _next suma uno
por commit nuevo. Client.perform usa por defecto expected con el head actual.
Un recibo previo procede de una operación cuyo expected.seq es menor que la
secuencia actual. Reutilizar ese cid cambia el hash de petición y produce
COMMAND_CONFLICT; no permite replay aceptado sin avance. Una excepción inesperada
abandona la ruta completa PASS que estamos acotando. Esta raíz no tiene writer
concurrente ni hook nuevo.

Por tanto, partiendo sólo de seq>=0, hay como máximo 23 CLOCK aceptados y 24
lecturas de condición. Se cargan 92 eventos por los cuerpos y 48 por las
condiciones, además de setup, dispatch, rechazo HISTORY_HEADROOM, RESULT y
oráculos/aserciones finales: total <=249. No se afirma el número exacto de
vueltas; no se usa events_test=2048 ni commits=25 para justificar terminación.
No se ejecutó CLOCK ni se accedió a stores durante esta revisión.

## Limpieza y métodos públicos

DF41 conserva los dos patch de socket/Popen y sus AssertionError. En la ruta
PASS no se activan sus efectos. summary tiene cuatro snapshots observados y
el test seis comprobaciones de contadores, una de activación y una de entities.
Los ceros del test no constituyen una medición nueva de consumo o actividad.

DF42 incluye ready, start/receive/finish y las dos aserciones de fresh_process,
además de tres comprobaciones del caller. close y sus cleanup mantienen todas
sus lecturas, verificaciones de ownership y borrado; no llaman a otros observers.
La iteración sobre CHILDREN usa is_alive, cuyo cuerpo stdlib revisado en I104
no llama join. No se está acotando su coste de CPU/IPC ni comprobando procesos
reales. DF43 conserva dos contextos esperados, dos aserciones del sentinel y
las restauraciones en finally; no se ha tocado ningún marker o symlink real.

DF47 cuenta dos independent, las tres fronteras y dos aserciones internas de
fresh_process, más cinco aserciones del caller. dumps y la comparación de salida
siguen haciendo su trabajo; sus tamaños se revisarán como recursos separados.
No se deduce privacidad global, persistencia o recuperación integrada.

## Helpers de inventario y cobertura

DF01 tiene cuatro aserciones. applicability lee/hash los paths recibidos, sin
llamar Store ni observers; durante I105 sólo se inspeccionó su AST. DF48 tiene
cinco aserciones: distinct_groups recibe tres literales, dos distintos, y coverage
genera 48 entradas con range(1,49). Se revisó el import local de run_durable_lab:
imports/definiciones y guard __main__, sin invocar main. La cota conserva la
precondición de módulos fixture/support ya cargados por el descubrimiento P01
y bindings stdlib originales. No se ejecutó el runner para validar esta cuenta.

## Pendiente y estado conservado

Quedan 48 raíces T/R y 233 tests de otras familias. DF46 y DR36 siguen pendientes:
requieren revisar transitivamente las clases históricas y la cardinalidad de
observaciones/provenance. No se asignan cero eventos a callees desconocidos.
Faltan cotas globales de eventos, referencias y bytes, y la composición de las
24 cuotas. I97 mantiene la cota inferior de referencias R>=19037>16384.
No se propone cuota, perfil o certificado de capacidad nuevo.

Git HEAD permanece b22bc4d9189896c12f35c648cf47a93937b76b58. Los cinco archivos
locales I104 y sus hashes se conservaron. I105 sólo añade estos documentos y su
sello; no forma parte del push anterior I85–I103 y no se publica en este corte.

P0; 83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial; D1–D4 cerrados e I1–I20/A52
aceptado. D5/H07/G01–G07 y GI33/34/38/39/40 globales abiertos. I83/CT96 es evidencia
de componentes, no compatibilidad funcional P01. Captura funcional, IR03,
suficiencia global y publicación requieren sus decisiones separadas.
Sin proveedores/credenciales/corpus reales, consumo/reservas, activación,
promoción, despliegue ni D6. No se inspeccionaron ni limpiaron dev/run_data/D4.
