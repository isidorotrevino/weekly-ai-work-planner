# I186 — Reparación documental F183-01 confirmada en candidato 02

Fecha: 2026-11-16, Europe/Madrid. Base:
`df98c54ea86b885c8768b44f34cc467c230c6456`.

**La revisión confirma que el candidato 02 de I185 resuelve la brecha documental
F183-01 y conserva las ocho exclusiones de S01.** No encuentra nuevos defectos
documentales bloqueantes en esta reparación. El alcance es el contrato candidato:
no acredita identidades/independencia reales, custodia, adopción o implementación.
I122/PJC115-R2 sigue sin admisión; F179-01 y D5 permanecen abiertos.

## Ruta de revisión y alcance

1. Leer el [dictamen y disposición F183-01](../validation/D5-I186-I185-documentary-review.json).
2. Contrastar la [reconstrucción](../validation/D5-I186-I185-source-reconstruction.json):
   ocho relaciones, su expansión y el delta exacto del schema.
3. Revisar el [auditor](../validation/D5-I186-audit.py) y el
   [sello documental](../validation/D5-I186-integrity.json).

La revisión preserva los seis archivos I185 y el hallazgo histórico I184.
Declara la brecha reparada en candidato 02; no modifica el registro histórico
ni convierte su estado en una aceptación competente independiente. El mismo
asistente preparó I183/I185 y hace esta reconstrucción metodológicamente
separada. No existe independencia de actor/organización ni nombramiento real.

## Ocho exclusiones conservadas

Se recompone la matriz de [S01/I179](../validation/D5-I179-S01-ROLES-SCOPE-GATES.json)
y se contrasta con los registros tipados y las expresiones explícitas del
[perfil candidato 02](../validation/D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json).
Las ocho relaciones coinciden exactamente:

| Rol | Debe diferir de |
| --- | --- |
| R03 | Cada preparador documental |
| R06 | Cada preparador documental |
| R08 | Cada preparador documental |
| R05 | R04 |
| R08 | R03 |
| R08 | R04 |
| R08 | R06 |
| R08 | R07 |

Se mantienen además R08 ≠ autor de fuentes y clave del emisor ≠ clave del
aceptante. Preparador y autor no se presumen iguales; si realmente coinciden,
se aplican ambos conjuntos de restricciones. El contrato no introduce una
prohibición de coincidencia general entre todos los roles.

La comprobación separada expande DOCUMENTARY_PREPARER sobre todas las posiciones
para cada longitud permitida, de 1 a 16. Compara el conjunto resultante de
restricciones con S01 y evalúa 2.480 casos simbólicos de fusión de un par de
identidades manteniendo las restantes distintas. Se rechazan exactamente las
coincidencias prohibidas y se conservan las no prohibidas por estas relaciones.
Los cinco contramodelos originales de I184 quedan rechazados por el contrato 02.

Esto examina relaciones matemáticas entre símbolos, no personas o ejecuciones.
No es una enumeración de todos los estados runtime ni prueba de un resolvedor
de aliases. La igualdad exacta de conjuntos respalda la equivalencia de las
conjunciones de exclusión para el dominio declarado; su aplicación real sigue
requiriendo identidad canónica auténtica y código correcto.

## Preparadores y procedencia realmente incluidos en el contrato

El [schema 02](../validation/D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json) exige una
lista no vacía de hasta 16 registros cerrados con actor_id, provenance_record_id
y provenance_record_sha256. Las reglas semánticas exigen orden, unicidad,
completitud del scope y procedencia auténtica aceptada, sin omitir preparadores
para caber en una cota o evitar una exclusión.

Todos los roles, preparadores y autor de fuentes usan la misma resolución de
identidad aceptada. Los aliases de un actor deben resolver a un único actor
canónico; datos ambiguos, incompletos o no aceptados rechazan. Dos nombres,
record IDs, hashes o claves diferentes no acreditan dos personas distintas.
La procedencia debe vincular actor, contribución/scope y paquete/perfil exactos.

La revisión distingue tres obligaciones:

- El schema comprueba la forma y cardinalidad de los registros.
- Las reglas semánticas exigen orden, unicidad, completitud, identidad/custodia
  auténticas y las exclusiones universales.
- La implementación y los revisores competentes deberán demostrar y verificar
  que esas obligaciones se cumplen para actores y cuerpos reales.

No se atribuye al JSON Schema por sí solo una comprobación de aliases,
independencia de personas, orden/completitud de contribuyentes o verdad de la
custodia. Los placeholders usados en la preparación sólo prueban forma/anchura.

El digest del contexto completo incluye toda la lista y sus referencias de
procedencia. El core exige también el digest explícito de esa lista exacta en
role_acceptance_scope; ambas firmas de rol cubren ambos compromisos en el mismo
core. La verificación de procedencia y completitud se exige a R06 y al aceptante
separado R08. No se ha firmado o verificado criptográficamente un cuerpo real.

## Delta, compatibilidad y costes

Se confirman las siete rutas de cambio del schema respecto a I183: id, título,
id del perfil y las propiedades/required de la lista y de su compromiso.
El resto del schema queda idéntico. Se preservan 17 familias, 32 definiciones,
480 históricos, seis fuentes, BASIS 489, manifest nueve y payload 494.
Los nuevos campos obligatorios e id/digests 02 exigen seleccionar explícitamente
el nuevo perfil; no existe fallback al perfil 01 ni un consumidor instalado.

Los cambios mantienen las nueve condiciones de CP07, el orden antecedente,
los dominios/contrato criptográfico y los límites/caps de I183. No añaden
fuentes, helpers, claves, schemas o lecturas de archivos al bundle runtime.
Cualquier necesidad real adicional debe acotarse y revisar grafo/IO. El parsing,
resolución, copia, comparación, firma y trabajo nativo siguen dentro de E01–E05
y de las ventanas launch/worker/finish.

Continúan 496 rutas y 266.693.693 bytes como aritmética condicionada, no fit
Reader real. La lista no puede truncarse si excede 16 o el contexto 8.192 bytes.
Las nuevas obligaciones de custodia, las cotas de fuentes/cuerpos/fresh reads,
heap/CPU y el objetivo 900 segundos requieren pruebas propias.

## Disposición y pendientes

F183-01 queda **resuelto como brecha documental del candidato 02** en este
dictamen. No se declara aceptación independiente, adopción de S01/PGO181,
independencia real o cierre de admisión. El hallazgo I184 y la preparación I185
permanecen intactos como registros históricos. No se nombran custodios,
preparadores, firmantes o revisores reales.

Siguen pendientes el caller/identidad/custodia/reloj/replay concretos, biblioteca
y guard exactos; schemas completos de contexto/launch; requalification de
179 casos/321 raíces/12 grupos/30 sitios y E01–E05; evidencia antecedente y
E06 final reales; solicitudes/contexto auténticos, payload/raíz/firmas y
aceptación/decisiones separadas. La reparación del contrato no sustituye esas
obligaciones ni resuelve materialmente F179-01.

## Verificación y publicación

`python3 docs/validation/D5-I186-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Contrasta 723 pins con Git y preserva 415 archivos publicados. Reproduce sólo
funciones documentales de la preparación y recompone por separado el delta,
las relaciones y su alcance. No ejecuta el producto, componentes, guard,
criptografía o un calendario de lecturas. El PASS confirma la revisión y sus
límites; no es evidencia de capacidad, seguridad o permiso runtime.

La unidad contiene cinco archivos: este documento, dictamen, reconstrucción,
auditor y sello; work_unit.rollback_files enumera el rollback exacto. El diff
supera 400 líneas por evidencia trazable y comprobaciones autocontenidas; se
informa el exceso. Runtime harness N/A: revisión documental sin cambio runtime.
Auditoría antes de stage y tras commit; commit/push solicitados y comprobación
de remoto/árbol limpio. Publicar no adopta ni concede autoridad.

E01–E05 abiertos, E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07/correlación
false y cuatro bindings I175 pendientes. Sin SOURCE_CAPACITY_VERIFIED, rebind,
autoridad/destino nuevos, propuesta/captura habilitadas o D5/H07 cerrados;
IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e I1–I20/A52
intactos; brechas globales/reales pendientes. I86/I89/I92 INVALID_CAPTURE no
se reanudan ni mezclan.

Sin ejecutar/importar/compilar producto o componentes, tests, discovery,
benchmarks, firmas o calendarios runtime ni medir plataforma. Sin cambiar
fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o inputs;
sin inspeccionar ni limpiar dev/run_data/D4. Sin nombres/aceptaciones reales,
claves, firmas, root/payload o evidencia positiva emitidos; sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6.
