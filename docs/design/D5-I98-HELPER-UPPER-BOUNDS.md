# I98 — cotas superiores de los helpers parentales de preparación

Fecha: 2026-10-28, Europe/Madrid. Revisión documental autorizada por «continúa».
**La contribución de ready/prepare queda acotada; la capacidad global sigue abierta.**
No se ejecutaron helpers, producto, tests ni campañas; no se cambió implementación,
perfil o cuota. Los datos son deducciones de fuente condicionadas, no mediciones.

[Árboles y anclas](../validation/D5-I98-helper-upper-review.json) ·
[Contratos de coste](../validation/D5-I98-parental-helper-costs.json) ·
[Composición pendiente](D5-I98-CAPACITY-COMPOSITION.md).

## Invocaciones y contribución acotada

Se expandieron los48 DF y40 DR hacia ready/prepare, incluidos phase_args,
commit_crashes, remote_crashes y phase. Los bucles que alcanzan esos helpers
son tuplas/listas/ranges literales o phases, tuple local. No se encontró un
bucle de cardinalidad desconocida que alcance estas dos invocaciones en el
cierre revisado. Se verificó ausencia de rebinds/usos como callbacks de esos
helpers. El cierre general de objetos/imports/callbacks de P01 aún no está cerrado.

| Contribución cubierta | Invocaciones como máximo | Client.perform por invocación como máximo | Client.perform total como máximo | Eventos como máximo |
|---|---:|---:|---:|---:|
| T: ready |144|18|2592|11232|
| R: prepare, fuente P01 de2 TASKs |121|14|1694|7986|
| Sólo estos helpers |265| |4286|19218|

Se suman ramas/handlers/finally y se conserva código posterior a return/break
para sobreestimar; no se presupone una rama favorable. Un loop desconocido que
alcance el helper bloquea el extractor, nunca se trata como0. Los árboles
de los88 métodos conservan líneas y multiplicaciones. Una fila0 sólo significa
que este cierre no invoca ready/prepare, no que ese test no tenga otros costes.

## Coste interno de cada helper

Para ready, a=apply y p=projection, ambos0/1:

`P=14+a+3ap; E=4P+4ap+2`.

El prefijo obligatorio aporta14 comandos. APPLY añade1; BIND,
PREPARE_PROJECTION y REVIEW PROJECTION añaden3 si ambos flags están activos.
Cada perform genera2 snapshots, su CALL_RETURN y el terminal Store:4 eventos.
prepare_projection añade4 snapshots externos al perform. capture añade1
snapshot Drive y1 terminal advance. Así, las ramas completas aportan58,
62 o78 eventos, con14,15 o18 comandos. inspect/_pin recorren bytes sin llamar
snapshot/perform/transact adicionales; ese trabajo no desaparece del presupuesto
de valores/tiempo por no añadir estos eventos.

Para prepare, a=apply, s=select, z=project y m=TASKs seleccionados:

`P=6+a+as+3aszm; E=4P+2a+4aszm`.

El snapshot explícito después de APPLY añade2 retornos observados. Por cada
TASK, BIND/PREPARE_PROJECTION/REVIEW añaden3 comandos y la preparación de
proyección añade4 snapshots. Con m=2, las ramas de preparación aportan24,
30,34 o66 eventos, con6,7,8 o14 comandos.

La procedencia de m=2 se revisó en cada callsite: normalmente prepare invoca
source() con tasks=2; los únicos raw/targets explícitos son source(description=desc)
en DR07 y source() en DR36, este último con project=False. No hay tasks= distinto
en los source calls de esta suite. No se deduce m del tamaño observado de I92.
Para un uso genérico exitoso, SELECT_TASKS valida unicidad y selected≤16 antes
del bucle; entonces P≤56 y E≤290. Esa cota genérica no se aplica como si cada
invocación P01 seleccionara16 tareas.

## Referencias: una parte más puede componerse

Para la parte Client.perform/Store.transact/enlace anidado:7 cargos por comando
(dos C, una L, dos slots Q35 y dos extremos Q37). ready añade una C del advance
Drive. Por tanto, **sólo ese subconjunto** está acotado por:

`144×(7×18+1)+121×(7×14)=30.146`.

No es una cota superior de R. Excluye incluso contextos/owners/grupos de esas
mismas llamadas, además de todas las llamadas externas. Tampoco es una nueva
cuota recomendada. I97 conserva su piso R≥19.037 y el techo16384 sigue insuficiente.

## Corrección de una explicación I97

I97 atribuyó la exclusión de DF26/DR29 del piso a Try omitidos. Es incorrecto:
no hay Try en esos métodos. Su extractor inferior descartó el bucle porque
ast.walk encontraba un Return **dentro de la función bad anidada**. Esa decisión
conservadora sólo reducía el piso; R≥19.037 sigue válido. I98 incluye los7 pasos
de cada bucle al acotar invocaciones. Se conserva I97 byte a byte, junto con
su sello, y se registra esta corrección explícita en el JSON.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial. D1–D4 cerrados e I1–I20/A52
aceptado. D5/H07/G01–G07 y GI33/34/38/39/40 globales abiertos. Sin proveedores,
credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue,
D6 ni publicación. Esta cuenta no prueba persistencia o recuperación integrada.
