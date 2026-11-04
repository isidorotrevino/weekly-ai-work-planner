# I108 — composición global y preparación de evidencia funcional

Fecha: 2026-10-28, Europe/Madrid. **Las88 raíces T/R ya tienen cotas completas
de eventos por fuente**. Quedan233 tests de otras10 familias y la composición
de recursos/callbacks para321/12. No se ejecutó ninguna campaña ni se importó
producto/runner. Esta cuenta no es un resultado funcional.

[Desglose de las27 raíces nuevas](../validation/D5-I108-final-T-R-event-bounds.json) ·
[Registro88/88](../validation/D5-I108-event-bound-coverage.json) ·
[24 recursos y evidencia funcional revisada](../validation/D5-I108-global-capacity-functional-readiness.json).

## Composición de eventos y unidades

Las27 cotas nuevas suman5979; las88 T/R suman **27679**. Su máximo local
es1951, menor que2048. Son cotas superiores de
la ruta original completa PASS con observación válida y fuentes/bindings
pinneados; no predicen que una captura vaya a completar esa ruta.

**events_campaign=131072; refs=16384.** Las alusiones de I105–I107 a superar
16384 con sumas de cotas de eventos no son comparaciones de admisión aplicables.
Los números y sellos históricos se conservan; esta aclaración separa unidades.
La desigualdad global a resolver es:

`E_global <= 27679 + U_other233 + U_campaign_callbacks`

Quedan **103393 eventos de margen aritmético condicional** para los
últimos dos términos, todavía desconocidos. No se sustituyen por0 ni se deduce
capacidad del mero límite2048/test. No sumar aquí I100/helpers solapados.
La cota inferior independiente de referencias sigue **R>=19037>16384(I97)**:
la representación original no cabe; falta una cota superior justificable para
proponer un contrato nuevo o demostrar otra representación sin pérdida.

## Raíces terminadas en este corte

| Raíz | Máximo de eventos condicionado por fuente |
|---|---:|
| DF02 | 191 |
| DF03 | 31 |
| DF04 | 97 |
| DF05 | 60 |
| DF06 | 91 |
| DF07 | 18 |
| DF14 | 78 |
| DF15 | 181 |
| DF16 | 112 |
| DF17 | 382 |
| DF18 | 382 |
| DF19 | 355 |
| DF20 | 872 |
| DF29 | 261 |
| DF30 | 349 |
| DF31 | 93 |
| DF32 | 429 |
| DF33 | 493 |
| DF34 | 106 |
| DF35 | 211 |
| DF36 | 159 |
| DR01 | 7 |
| DR02 | 263 |
| DR34 | 203 |
| DR35 | 373 |
| DR39 | 99 |
| DR40 | 83 |

remote_crashes tiene3 modos de118 eventos cada uno más25 del único UPDATE:
379 por helper, incluidos3 resultados subTest, sin lifecycle de raíz duplicado.
DF20 llama ese helper dos veces y añade su escenario final. Las dos ramas
published conservan los mismos máximos de oráculos/contextos; close=True se
sobreestima por12. No se cuentan eventos de Store del hijo otra vez en el padre.
DF19 incluye el Store del Remote nuevo y el hook fault fuente sin observers extra.

DF02/DR02 sólo necesitan cardinalidades de manifiestos documentales: D3=25,
D4=161 e I34=73. No se han recorrido sus targets ni inspeccionado estado
operativo D4. DF05 conserva3 subTest; import_event/_pin inválidos en DF04 no
llegan a perform, según los cuerpos revisados. DR01/40 importan helpers de
cobertura/inventario sin main; no se han invocado durante I108.

## Matriz global de24 recursos

El registro JSON conserva todas las cuotas actuales y su estado. Resolver
los eventos no resuelve referencias, owners/contextos/grupos, operandos,
bytes de filas/eventos/tablas/páginas ni tamaño de raw/sidecar/contexto/launcher.
Los Reader normales originales de I96 mantienen cotas condicionales de
92274724 bytes únicos y251658276 leídos para evidencia, con sus exclusiones;
no certifican el Reader de una futura autoridad/perfil nuevos. Los techos
900/20s son parámetros de corte, no demostraciones de tiempo de finalización.
No se crea certificado numérico, perfil, cuota o autoridad de captura nuevos.

## Evidencia funcional existente y siguiente puerta

| Intento sellado | Tests observados de321 | Resultado de captura |
|---|---:|---|
| I86 | 3 | INVALID_CAPTURE |
| I89 | 8 | INVALID_CAPTURE |
| I92 | 13 | INVALID_CAPTURE |

Se comprobaron sus hashes de paquete. Los prefijos no se suman, reanudan o
fusionan; raw PASS en esos prefijos no prueba321/12. I92 conserva su fallo
REFERENCE_BUDGET y la autorización de una sola ejecución ya consumida. El
componente CB32 de I95 sigue validado sólo como componente; no crea perfil
funcional ni establece capacidad del P01 original. **IR03 sigue NOT_READY**.

La petición actual autoriza continuar este trabajo de cotas y evidencia.
Antes de una captura nueva hay que cerrar el análisis de recursos, preparar
una propuesta concreta de contrato/perfil y decidir implementación/componentes
y ejecución en sus puertas separadas. Aún no hay una propuesta numérica completa
aprobable; no se solicita permiso para un perfil o destino inexistentes ni se
lanza otra campaña que conserva una insuficiencia conocida de referencias.
La siguiente captura, si se decide después, necesitará pins y destino nuevos,
321/12, límite externo900s, sin reintentos ni publicación; IR03/suficiencia
global y publicación conservarán decisiones posteriores propias.

## Conservación

Git HEAD b22bc4d9189896c12f35c648cf47a93937b76b58 y18 documentos locales
I104–I107 se conservan. I108 queda local, sin commit/push. P0;83 SUPPORTS_BOUNDED/
1 PARTIAL, UI04.1 parcial; D1–D4 cerrados e I1–I20/A52 aceptado. D5/H07/G01–G07
y GI33/34/38/39/40 globales abiertos. I83/CT96 continúa como evidencia de
componentes. No se deduce persistencia o recuperación integrada de PASS aislados.
Sin proveedores/credenciales/corpus reales, consumo/reservas, activación,
promoción, despliegue ni D6. No se limpia estado operativo dev/run_data/D4.
