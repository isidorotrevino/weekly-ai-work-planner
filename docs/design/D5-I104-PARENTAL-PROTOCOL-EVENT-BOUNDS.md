# I104 — protocolos, carreras y reconciliación:21 raíces más acotadas

Fecha: 2026-10-28, Europe/Madrid. Trabajo documental después de la publicación
Git autorizada. **33 de88 raíces T/R tienen ahora cotas completas de eventos**;
las21 nuevas están por debajo de2048/test. No se ejecutó campaña ni helper.

[Desglose y anclas](../validation/D5-I104-parental-protocol-event-bounds.json) ·
[Registro acumulado](../validation/D5-I104-event-bound-coverage.json) ·
[Publicación anterior verificada](../validation/D5-I104-prior-publication-context.json).

## Cotas nuevas

| Raíz | Eventos como máximo |
|---|---:|
|DF21|116|
|DF22|119|
|DF23|121|
|DF24|110|
|DF25|103|
|DF26|815|
|DF27|160|
|DF28|146|
|DF37|96|
|DF38|77|
|DF39|115|
|DF40|105|
|DR25|100|
|DR26|123|
|DR28|183|
|DR29|731|
|DR30|319|
|DR31|54|
|DR32|110|
|DR33|141|
|DR38|99|

El subtotal de las21 es3943; con las12 anteriores,17698. Son rutas completas
de PASS original, con observación válida y excepciones esperadas conservadas,
no resultados runtime. Los vectores sobreestiman dispatch/reconcile rechazados
con sus cotas generales; close=True puede usar12 aunque su ruta conocida tenga11.
No se infiere una nueva cuota de referencias o bytes de estos máximos de eventos.

## Cardinalidades de las carreras y liberación del lock

DF25/DR28 crean2 start sobre una tuple de2 modos. DF38 usa args list de2
elementos y DR31 una tuple de2 manifests: en cada bloque hay2 receive y2 finish,
con sus aserciones originales. Los ERROR de conflicto son mensajes de protocolo
esperados, no eventos de métodos del Store del hijo dentro del padre. No se
reconstruyen cid ni recibos ausentes a partir del resultado de la carrera.

DF40/DR38 tienen2 start,3 receive (READY del owner, READY del waiter y resultado
del waiter) y2 finish explícitos. Sus finally recorren2 pares; se añaden hasta
2 finish más como sobreestimación, sin asumir gratis la limpieza. El cierre
por proceso fresco añade start/receive/finish y2 aserciones, más la aserción del
caller. DR38 incluye también2 contextos de error de close y2 aserciones finales.
Las lecturas/cleanup originales de close permanecen; close no tiene observer.

Se inspeccionó is_alive de stdlib por fuente/hash coincidente con el registro:
usa _popen.poll, sin llamar BaseProcess.join. Las comprobaciones de estado y
barrier no añaden esos eventos observados; conservan su coste de CPU/IPC y su
semántica original. No se ejecutó ningún proceso, barrier o comprobación real
de recursos durante esta revisión documental.

## Mutaciones, reintentos y métodos compuestos

DF26/DR29 recorren exactamente7 campos, sin subTest. bad modifica/retorna el
proof, con0 boundaries adicionales según I99; cada vuelta incluye lab/setup,
dispatch, Remote.execute, dos reconcile y oráculos/aserciones. Se cuentan sus
Return dentro de la función anidada sin cortar el bucle exterior (corrección I98).

DF27/DR30 conservan sus2 reintentos literales y todos los self.error. DF28 tiene
2 casos de binding más el rechazo final. DR30 además crea otro lab y realiza
6 reconcile antes de los rechazos de query/binding. Los argumentos/receptores
fresh se cargan antes del contexto de error, como estableció I100.

phase_args_result de DF22 no llama ready otra vez: son dispatch sin entrega,
state y Remote.execute. No se duplica el setup. Las ediciones Remote de
DF22/DF37/DR33 y summary de DR32 incluyen los snapshots que les corresponden.
El causal de Client.perform ya está en su outcome; no añadir otro terminal.
exit_observations/message conservan referencias y filas sin crear eventos nuevos.

## Git publicado y trabajo actual

El usuario autorizó «haz commit y push en git, sigue con tareas de D5». Se
publicaron146 archivos pendientes I85–I103 en **b22bc4d9189896c12f35c648cf47a93937b76b58**,
origin/main, después de verificar hashes y24 sellos. El push tuvo éxito y
ls-remote confirmó el mismo SHA; el árbol quedó limpio. Los flags históricos
publication_authorized=false permanecen en los sellos originales de sus cortes.
El contexto nuevo registra la decisión posterior, sin reescribir la historia.

I104 es la continuación documental local, fuera de aquel commit. No se infiere
autorización para campañas, perfil/cuotas, IR03 o publicación futura de I104.

## Pendiente para D5

Quedan55 raíces T/R y otros233 tests hasta321/12. Estos33 roots son disjuntos;
no sumar17698 a los subtotales globales de helpers I100 porque se solapan.
Faltan owners/objetos/grupos/contextos/autoridades,30 sitios de referencias y
bytes de valores/tablas/eventos. I97 mantiene R≥19037>16384. Hace falta revisar
conjuntamente las24 cuotas y Reader antes de proponer un contrato/perfil nuevo.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial; D1–D4 cerrados e I1–I20/A52
aceptado. D5/H07/G01–G07 y GI33/34/38/39/40 globales abiertos. Sin proveedores/
credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue
ni D6. No se deduce persistencia, recuperación integrada o fsync nativo de
estas cuentas o de PASS aislados.
