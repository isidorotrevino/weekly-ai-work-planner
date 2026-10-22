# D5 I28 — resultados de conciliación Plane sintética

Fecha: 2026-10-22. Base publicada: `2655940`.
[Laboratorio](../design/D5-I28-PLANE-RECONCILIATION-LAB.md) ·
[Contrato aprobado I27](../design/D5-I27-PLANE-RECONCILIATION-DESIGN.md) ·
[Informe verificable](D5-I28-results.json).
**PASS de modelo en memoria; D5 global y G01–G07 abiertos.**

D5-A67 aprueba I27 y autoriza PC01–PC32 con fixtures sintéticas en memoria.
No se conecta Plane, Google, CLI/modelos ni credenciales; sin HTTP, SQL, Docker,
efectos persistentes D2, activación, promoción, despliegue o D6.

## Campaña ejecutada

`python3 -m testing.D5.run_plane_lab`, Linux/Python **3.14.4**, biblioteca estándar:

| Grupo | Tests distintos | Fallos / errores / omisiones |
|---|---:|---|
| I28 conciliación PC01–PC32 | 41 | 0 / 0 / 0 |
| I26 captura incremental | 30 | 0 / 0 / 0 |
| I24 integración offline | 35 | 0 / 0 / 0 |
| Python local anterior | 51 | 0 / 0 / 0 |
| Total de esta campaña | **157** | **0 / 0 / 0** |

Las 32 filas PC no se suman como tests adicionales. El JSON mapea las 41 pruebas
nuevas a esas filas y registra los 157 IDs distintos. Las 116 regresiones se
reejecutaron en esta campaña; no son números copiados de I26. No se reejecutaron
SQL/D2/D3/D4 ni se suman sus campañas históricas.

`python3 -m testing.D5.demo_plane_reconciliation` ejecuta el flujo de ejemplo y
emite estados/contadores sin payload/ID remoto: UNKNOWN inicial, conciliación
EFFECT_CONFIRMED con STALE_LOCAL, UPDATE aprobado al mismo objeto y replay que
preserva una edición remota posterior. Dos escrituras de fixture y una consulta;
cero solicitudes remotas reales. No hay artefactos persistidos por la demo.

## Observaciones

- PC01–PC11: identidad explícita y clave estable, unicidad atómica y por binding,
  creación con respuesta perdida, cero resultados eventual/fuerte, duplicados,
  coincidencia sin prueba y recibo exacto. UNKNOWN bloquea nuevos paquetes; un
  conflicto de identidad sigue bloqueando aunque una consulta posterior pruebe
  el efecto o observe otra edición remota.
- PC10: dos emisores locales compiten con el primero detenido en vuelo; solo uno
  consume ticket. Dos hilos llaman al doble sobre la misma clave y obtienen el
  mismo ID. Dos conciliadores pasan una barrera y solo uno publica por CAS.
  Una consulta mientras el envío está en vuelo provoca CONFLICT_LEDGER en la
  publicación; la siguiente consulta recupera el efecto sin repetirlo.
- PC12–PC22: invalidación por D2/revisión/binding/capacidad, corrupción de hash,
  revocación en vuelo y conciliación histórica. Los callbacks de envío/consulta
  editan estado local desde otro hilo sin retener lock de dominio. UPDATE nuevo
  requiere revisión propia y base remota; edición anterior/durante/ABA bloquea
  CAS, conservando campos ajenos.
- PC23–PC30: timeout, cuerpo inválido, ACK local y 429 ambiguo quedan UNKNOWN;
  UPDATE perdido tampoco permite otro paquete de escritura hasta conciliar.
  Rechazo concluyente no crea efecto; retry explícito consume presupuesto y tick
  válido. Delay inválido, versiones obsoletas y límites bloquean. Desaparición
  remota no recrea ni borra D2. No se simula una restauración durable del ledger.
- PC31–PC32: shapes/tipos/UUID/modo/límites cerrados y salida saneada. Se alcanzan
  64 bindings y 128 comandos, y se rechaza el siguiente. Texto UTF-8 válido puede
  exceder 64 KiB del manifiesto y se rechaza sin truncar. Hay además una prueba de
  presupuesto reducido; no se presenta como campaña de rendimiento.

Se iniciaron **ocho hilos nuevos propios**, todos terminados. I28 no crea raíces
de datos o hijos de proceso. La **regresión I26** creó 33 raíces temporales propias,
las eliminó todas y dejó cero hijos vivos de siete iniciados: tres normales y
cuatro SIGKILL controlados. Esta recuperación pertenece a la captura I26, no al
ledger en memoria I28. Los sentinels ajenos de esa prueba siguen siendo fixtures;
no se inspeccionan ni borran dev/run_data/D4 reales.

## Preservación y alcance

Solo se amplían el índice documental y la guía D5 entre archivos anteriores.
Se verifican todos los demás archivos de la base, 245 entradas de cierre D3/D4,
canónico D4 y 560 entradas de campañas D5 I4–I20. I21–I27 y la aceptación local
conservan bytes y se comprueban sus inputs contra el commit correspondiente si
sus índices/guías han evolucionado. El informe nuevo contiene hashes propios.
Enlaces, diff y patrones de publicación comprobados; estos patrones no son una
garantía universal de ausencia de secretos/defectos.

GI15–GI17 obtienen evidencia acotada de **modelo sintético**: 25/35 S con evidencia,
diez S y siete R pendientes. No se atribuye conformance Plane, unicidad real,
condición atómica remota, permisos, reinicio del ledger o cierre G03/D5. Tampoco
GI38/GI39/GI40 generales se consideran completos por probar estas fronteras.
El hito D5-LOCAL-SYNTHETIC-I1-I20 conserva su aceptación/perímetro exactos.
