# I107 — transiciones y rechazos relacionales:19 raíces adicionales

Fecha: 2026-10-28, Europe/Madrid. Continuación documental local de I106.
**61 de88 raíces T/R tienen cotas completas de eventos por fuente; quedan27**.
Las19 nuevas están por debajo de2048/test bajo la ruta original completa PASS,
fuentes/bindings pinneados y observación válida. No son resultados runtime.
No se importó el producto/runner ni se ejecutaron tests, hijos o campañas.

[Desglose, macros, sintaxis y anclas](../validation/D5-I107-relational-transition-event-bounds.json) ·
[Registro acumulado](../validation/D5-I107-event-bound-coverage.json) ·
[Cardinalidades históricas I106](D5-I106-HISTORICAL-COMPARISON-EVENT-BOUNDS.md).

| Raíz | Máximo de eventos condicionado por fuente |
|---|---:|
| DR03 | 16 |
| DR04 | 61 |
| DR05 | 54 |
| DR06 | 126 |
| DR07 | 185 |
| DR08 | 101 |
| DR09 | 127 |
| DR10 | 155 |
| DR11 | 210 |
| DR12 | 267 |
| DR13 | 90 |
| DR15 | 108 |
| DR16 | 55 |
| DR17 | 63 |
| DR18 | 110 |
| DR19 | 294 |
| DR20 | 365 |
| DR21 | 100 |
| DR22 | 123 |

El subtotal nuevo es2610; las61 raíces suman21700. Son cotas superiores
parciales de raíces disjuntas, no una cota inferior o global de eventos. Rebasar
16384 con su suma no prueba exceso real. No se suman a I100/helpers solapados.

## Setup, planes rechazados y argumentos

prepare completo conserva66 eventos, apply=False24, project=False34 y
select=False30, según I98. plan tiene hasta6 perform,24 eventos. Un plan
rechazado se sobreestima con24 más2 del contexto esperado, aunque no llegue al
review final. Los perform rechazados se acotan por4 más2 de contexto y los
dispatch rechazados por13 más2. No se traslada la contribución de referencias
del perform exitoso a una excepción ni se crea recibo/cid ausente.

capture/select_source/review sólo agregan su perform bajo entradas builtin;
summary incluye4 snapshots y Remote.edit incluye2 snapshots más transact.
Los cuerpos de reducers/planners/parsers y remote_manifest reutilizan la
closure nominal I100 con bindings cerrados. No se les asigna cero trabajo,
CPU o bytes. Cada método compuesto se cuenta una vez, con sus llamadas internas
en su vector. lab cierra los anteriores y conserva sus cleanups; close no añade
observers según la revisión de lifecycle previa.

## Bucles y ramas que cambian la cuenta

DR04 tiene4 casos en una list literal, luego dos rechazos más en otro lab.
DR06/08/11 usan3 casos; DR07 tiene2 variantes de descripción. DR10 recorre
4 tipos:1 HARD rechazado,3 no HARD con apply y oráculo; después un SELF_LOOP
independiente. DR12 tiene3 IDs más ACTIVE fuera del loop. DR17 tiene3 IDs
más el rechazo de receipt fuera del loop. Ninguno usa subTest.

DR19 conserva3 setups y sus rechazos; el caso no-op incluye plan y apply,
mientras los otros2 hacen una mutación cada uno. DR20 conserva3 modos y,
fuera de ese loop, otro setup/ISSUE/revocación/Remote.execute/reconcile/summary.
No se multiplica ese último escenario por3 ni se omiten las lecturas de summary.

En DR15 los bucles recorren4 claves de mappings y4 de entity_provenance.
source/planners conservan las cuatro identidades y sus endpoints tras el
segundo apply (I106); no se usa la comparación final como premisa. El bucle
cuenta claves, no las2 filas de cada clave. La tercera fuente tiene2 elementos,
conserva endpoints y se compara su source_base; no añade otro bucle de provenance.

DR16 incluye2 construcciones Store al crear fresh antes del replay. Sus4 eventos
de perform son una sobreestimación también para el retorno histórico. DR22
incluye las4 observaciones de oráculo,5 aserciones explícitas, el contexto de
remote_manifest y las2 entregas; Remote.edit conserva su coste de lectura.
Nada de ello acredita recuperación integrada o compatibilidad funcional P01.

## Estado y siguiente revisión

Quedan27 raíces T/R y233 tests de otras familias hasta321/12, además de cotas
globales de referencias, bytes, owners, grupos/contextos y composición de24
cuotas/Reader. R>=19037>16384(I97) sigue siendo una cota inferior independiente
de referencias. No se crea perfil, cuota, certificado ni autoridad de captura.

Git HEAD b22bc4d9189896c12f35c648cf47a93937b76b58 y los14 archivos locales
I104–I106 se conservan. I107 sólo añade documentación local, sin commit/push.
P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial; D1–D4 cerrados e I1–I20/A52
aceptado. D5/H07/G01–G07 y GI33/34/38/39/40 globales abiertos. I83/CT96 continúa
como evidencia de componentes; no se deduce persistencia/recuperación integrada
de PASS aislados. Captura funcional, IR03/suficiencia global y publicación
requieren sus decisiones separadas. Sin proveedores/credenciales/corpus reales,
consumo/reservas, activación, promoción, despliegue ni D6. No se inspecciona ni
limpia estado operativo dev/run_data/D4.
