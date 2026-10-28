# I87 — propuesta de witnesses de dominio después del bloqueo I86

Fecha: 2026-10-27, Europe/Madrid. **PREPARED_FOR_REVIEW, DESIGN_ONLY**.
[Resultado I86](../validation/D5-I86-results.md) ·
[Matriz DW01–DW24](D5-I87-DOMAIN-WITNESS-REVIEW.md) ·
[Contrato estructurado y pins](../validation/D5-I87-design-review.json).

La petición de avanzar hacia el cierre permite preparar este ajuste concreto.
No aprueba todavía su implementación I88 ni una nueva campaña I89. I86 ya consumió
su autorización de un intento: se conserva inválido e inmutable. Ninguna fase
reutiliza su autoridad/destino o sus tres PASS para completar otra captura.

## Problema comprobado y prueba necesaria

I86 registra ORACLE_DOMAIN_IDENTITY_MISSING en DF03 y se detiene tras tres tests.
El selector de dominio heredado exige un único objeto para un run/store/role.
DF03 reabre el Store y el sidecar conserva objetos distintos de la misma identidad.
La fuente permite ese conflicto; el conjunto interno de candidatos no fue retenido.
DW05 debe reproducirlo sintéticamente, sin ejecutar DF03 ni reconstruir su memoria.
La corrección no consiste en tomar el primero/último, elegir por proximidad o
eliminar el error. Unicidad de objeto y unicidad de dominio son obligaciones distintas.

## Identidad de dominio y objetos testigo

Se propone un grupo explícito con clave observada exacta:
`capture_run_id, test_frame_id, subcase_ref, thread_ref, run_id, store_id, role`.
Cada witness conserva su object_ref original y autoridad: construcción NOT_HEAD,
retorno de snapshot observado o cabecera de llamada/recibo observada. No se fusionan
objetos, retornos, versiones, heads, recibos o estados. El grupo representa sólo
identidad de dominio compartida, sin certificar contenido actual ni igualdad de
estado entre instancias. Store T y R no se unen por texto, hash o cuenta; Drive
mantiene su política propia y no se homologa con Store.

Cero witnesses compatibles deja missing. Varios witnesses con la misma clave se
conservan completos como conjunto. Roles/runs/contextos distintos no se unen;
mutación de identidad de un mismo objeto o datos contradictorios bloquean.
Una obligación que requiere objeto/llamada único sigue exigiéndolo: el grupo no
resuelve esa ambigüedad. No se crean referencias por orden de lista, PID/fd,
tiempo, nombres parecidos o UUID nuevo que sustituya identidad de dominio.

## Observación, oráculo y enlaces

Se reutilizan las mismas llamadas/retornos permitidos por I82/I84. No se añade
import/discovery, snapshot/independent, lectura del dominio, descriptor, canal,
actor, hook, barrera, señal o medición. No se lee root/scope. Los fallos se latchean,
conservando el original y su cleanup y deteniéndose entre tests.

El wrapper de independent sólo retiene el resumen público y cabecera del retorno
ya producido. Lo liga al grupo por run/store/role y contexto exactos; conserva el
conjunto de witnesses compatibles, sin decir qué instancia física leyó el oráculo.
Las declaraciones de construcción nunca dan head/estado ni independencia adicional.
Una fuente esperada no se convierte en observación. El oráculo sigue siendo el
retorno del harness, no una segunda lectura del collector.

El enlace comando→recibo→oráculo exige además command_id/request_sha256/seq y
commit/head compatibles realmente observados, en el mismo contexto, con witnesses
específicos conservados. Pertenecer al grupo no basta. Si varios comandos/recibos
satisfacen el vínculo y la obligación exige unicidad, sigue missing.
`after_data_sha256` no se compara con `oracle.state_sha256`. Los namespaces
Store/Drive/I70 y las ausencias de los quince parsers parentales quedan intactos.

## Esquemas y lector propuestos

Nuevo namespace `testing/prospective_capture_domains`, cinco archivos habituales,
registro `D5-DOMAIN-CAPTURE-REGISTRY.json`. No se crea ninguno en I87.
Normal `d5.domain-sidecar.v1`, fallo `d5.domain-worker-failure.v1`. Tablas previas
conservadas más `domain_witness_groups`, dentro del mismo sidecar.

`d5.domain-witness-group.v1` usa exactamente las claves:
`schema, group_ref, capture_run_id, test_frame_id, subcase_ref, thread_ref,
run_id, store_id, role, witnesses`.
Cada witness usa exactamente `object_ref, authorities`; authorities es un conjunto
serializado ordenado de los literales ya admitidos, sin datos libres ni autoridad
inferida. El grupo no contiene payload, paths de dominio, state ni head sintetizado.

El registro I88 versionaría los esquemas causales/retained-oracle/link que necesitan
el nuevo group_ref y el conjunto witness_refs, conservando object_ref del productor
observado y todas las comprobaciones previas. Debe fijar sus claves exactas antes
de ejecutar DW24; no aprender schemas de mensajes desconocidos. El lector recorre
todas las referencias locales, pertenencia y contexto; rechaza huérfanos, duplicados,
ciclos, grupos incompatibles y pertenencias no acreditadas por las declaraciones o
cabeceras ya retenidas. Un grupo construido por el writer no se acepta sólo por etiqueta.

El conjunto completo consume las cuotas compartidas: 16384 refs, 4096 frames,
profundidad 32, strings 4096, 4096 bytes/fila/evento y 16 MiB/valor incluyendo
representaciones auxiliares. Grupo demasiado grande bloquea: no truncar, muestrear,
repartir semántica para eludir el tope ni borrar witnesses antiguos. Se conservan
131072 eventos/campaña, 2048/test, 32 páginas de 2 MiB/64 MiB acumulados,
12 MiB por canal, 37 miembros/112 MiB+4 KiB e inputs/evidencia 128/256 MiB por
ámbito acumulado antes/después/autoridad. Sin resets ni aumento de límites.

## Secuencia de decisión

1. **Aprobar I87 y autorizar I88**, si se elige: sólo perfil/registro nuevos y
   DW01–DW24 con clases/módulos/procesos sintéticos nuevos, bajo 300 s externos.
   Incluir reproducción del selector heredado con cero/uno/múltiples witnesses y
   nueva resolución positiva/negativa. No ejecutar DF03, P01 o suites históricas.
2. Si I88 es válido, presentar pins, presupuesto y un destino nuevo para **I89**.
   La captura P01 completa 321/12 bajo 900 s requiere otra decisión expresa.
   No crear ahora su autoridad/destino ni autorizar reintentos parciales.
3. Sólo un paquete completo nuevo permite la revisión IR03 posterior. No cierra
   por sí solo UI04.1, H07, GI o D5. La publicación y aceptación global son separadas.

I83/I84/I85/I86 quedan byte a byte. PR96 sigue siendo componente validado, I86
captura inválida y DW24 NOT_RUN. P0,83/1,UI04.1 parcial; D1–D4 cerrados, I1–I20/A52
aceptado, 30/35 sin promoción y D5 global/H07/G01–G07/GI globales abiertos.
Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción,
despliegue, SQL/Java/Docker nuevos ni D6; sin inspección/limpieza operativa dev/D4.
