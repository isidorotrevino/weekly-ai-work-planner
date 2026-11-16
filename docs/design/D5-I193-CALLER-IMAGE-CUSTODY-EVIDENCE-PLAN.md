# I193 — Plan concreto de evidencia, con recibo de claim diferido

Fecha: 2026-11-16, Europe/Madrid. Base:
`24b1ce69e404add2eea97f061f377699eab1b85c`.

**I193 prepara un plan de doce paquetes CE01–CE12 para obtener y revisar la
evidencia de caller, imagen y custodia de PGO181 candidato 02.** Cada paquete
fija dossier, evidencias, roles, dependencias y criterio de aceptación. El
cierre previo al lanzamiento no depende de un recibo de claim: éste queda
diferido hasta eventos reales autorizados por separado. Toda la evidencia
actual sigue pendiente, sin admisión de I122/PJC115-R2, F179-01 o D5 cerrados.

## Ruta de revisión

1. Leer el [plan CE01–CE12](../validation/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json).
2. Contrastar el [checklist completo](../validation/D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json):
   ocho familias, dieciséis reglas K01–K16 y siete gates globales.
3. Revisar la [preparación](../validation/D5-I193-preparation-review.json),
   el [auditor](../validation/D5-I193-audit.py) y el
   [sello documental](../validation/D5-I193-integrity.json).

Se preservan I191/I192, perfil/protocolo 02 y todos los formatos/flags previos.
Sólo se publica el plan y su verificación documental. No se crean los doce
dossiers futuros, registros positivos, autoridad, actores/keys, imágenes,
servicios, claims o canales; no se contacta a proveedores o personas.

## Doce entregables y orden de trabajo

| Paquete | Dossier candidato / evidencia requerida | Revisión propuesta, sin personas asignadas |
| --- | --- | --- |
| CE01 SCOPE | Pins, roles, scope, permisos y decisiones negativas que se conservan | R06/R08 |
| CE02 ANCHOR | Origen externo ya aceptado de anclas, autoridad, keys/purpose/epoch y freshness | R01/R02/R08 |
| CE03 ROSTER | Identidad humana canónica, aliases/competencia/nombramientos y preparadores; intake provisional | R06/R08 |
| CE04 IMAGE | Seis fuentes reales, imagen/runtime distintos, mapeo, build/cierre completo y entrada inmutable | R01/R06/R08 |
| CE05 CALLER | Principal software, responsable humano, imagen/dominio/constructor y procedencia exclusiva | R01/R02/R06/R08 |
| CE06 PLATFORM | Ocho garantías, clock/UTC/monotonic, ledger atómico global y rollback/reinicio | R02/R03/R06/R08 |
| CE07 RESOURCES | Evidencia completa E01–E05 y compatibilidad efectiva de todo el nuevo source/runtime/caller | R03/R06/R08 |
| CE08 FREEZE | Autores y registros antecedentes finales, hashes, caps, epoch y autenticación previa a C | R01/R02/R03/R06/R08 |
| CE09 C | Proyección exacta de C y registro de aceptación sólo de custodia | R01/R02/R03/R06/R08 |
| CE10 BUNDLE | Cinco registros/hashes, tres aprobaciones genuinas y mapping externo único vigente | R01/R02/R06/R08 |
| CE11 PRELAUNCH | Revisión separada de siete familias previas y de todos los gates, con handoff explícito | R06/R08 |
| CE12 RECEIPT | Recibo privado de claim/construcción reales, sólo tras autorización y admisión futuras | R01/R02/R06/R08 |

Los paths exactos de dossiers futuros están en candidate_dossier_path. Son
wrappers documentales de revisión, no aliases de runtime o nuevos miembros de
los 494 pins. Cada uno debe registrar fuente/proveedor/custodia, scope, cuerpo
disponible, bytes/hashes conocidos, revisiones y hechos ausentes/rechazados.
Un dossier negativo puede decir missing; un registro I191 supuestamente aceptado
no puede usar null, ceros o hashes adivinados para esos hechos.

El productor de evidencia/preparador documental se distingue del revisor.
Ninguna persona queda asignada; ninguno de los roles listados se convierte en
autor o aceptante por aparecer en la tabla. Deben existir nombramientos y
competencia genuinos con las ocho exclusiones S01 y las adicionales de custodia.
El asistente que prepara este plan no suministra independencia de actor/
organización, autoridad externa o una aceptación competente.

## Intake provisional y congelación final

CE03 recoge identidades y evidencia de contribución existente. No declara
un actor_registry final completo antes de conocer a los autores reales de las
pruebas que se reunirán/revisarán en CE04–CE07. CE08 debe completar y congelar
ese scope y después reconciliar imagen, caller, plataforma y sus hashes en
orden antecedente. Las garantías deben estar realmente aceptadas antes de C:
no se toman prestadas de firmas de bundle aún no emitidas.

El checklist identifica explícitamente el paso que finaliza cada familia:
CE02 anclas, CE08 actores/imagen/caller/plataforma, CE09 aceptación, CE10 bundle
y CE12 receipt. Un intake anterior no acepta la familia por sí solo. También
exige todos los prerrequisitos y evidencia reales, además de schema/codec/cap.

Nuevo contribuyente, alias, fuente/imagen/runtime, proof body, scope, policy,
key o epoch invalida los hashes/revisiones dependientes. Se vuelve a CE03–CE10
según el impacto y se repite CE11; no se transfiere aceptación automáticamente.
Esta actualización de candidatos no aplica un capture_inputs rebind actual.

Los hechos de enrollment/build pueden ser anteriores a un intento. Los
snapshots firmados, C/bundle/keys vigentes deben satisfacer el lifetime máximo
3.600 y el clock/freshness del perfil 02. Se refrescan cuando la evidencia
esté completa; caché o estado del plan no renuevan un registro caducado.
Cualquier cambio de C exige recomponer sus consumidores reales posteriores,
sin sustituir la raíz de un intento o reutilizar un claim.

## Frontera previa al lanzamiento y recibo tardío

CE11 depende de CE01–CE10 y revisa siete familias de identidad/custodia.
**No depende de CE12**, de crear un claim o de arrancar un worker para probar
retrospectivamente que sus antecedentes eran aceptables. El auditor comprueba
el DAG y rechaza el ciclo artificial CE11↔CE12.

CE12 requiere, fuera de la autorización de este plan: autorización explícita
separada, E06 final/payload reales, Q y raíz finales confiables, admisión
completa y claim/construcción protegida efectivamente realizados. Sólo entonces
podría existir un receipt que diga CLAIMED. Mientras no existan esos hechos,
el slot es DEFERRED_NOT_AUTHORIZED, sin hash o estado positivo fabricado.
No hay comando de ejecución listo ni instrucción para gastar una invocación.

La recepción de evidencia existente no autoriza nuevas inscripciones, firmas,
validaciones crypto/runtime, builds, probes, mediciones, campañas o contactos.
Si hacen falta para obtener hechos no disponibles, su alcance debe autorizarse
por separado. Esta tarea no los ejecuta ni los concede por estar en el plan.
Un proveedor o reviewer listado no recibe ningún mensaje automático.

## Criterios que no se pueden sustituir

- Anclas y autoridad deben venir de aceptación externa; un registry auto-firmado,
  nombre, fd/PID, key_id o digest no crean confianza.
- Se requieren las seis fuentes/imágenes/runtime reales y cuerpos de prueba
  completos, no sólo índices o declaraciones. Las fuentes sucesoras no existen
  ahora; no se construyen o ejecutan para rellenar un dossier.
- CE07 exige el scope completo 179/321/12/30 y E01–E05 con todo el trabajo de
  caller/registro/crypto/clocks/frames/readers/copias/fallos/dual write dentro de
  fases. CP03 heredado, diez tests, deadlines, schemas o placeholders no prueban
  esa nueva capacidad/compatibilidad o los 900 segundos.
- El mapping epoch/C es único/vigente y el one-use es global/restart-safe. Una
  suposición de servicio o un receipt planeado no sustituyen la evidencia.
- Todos los límites actuales se conservan. Scope demasiado grande o backend
  que necesite nuevos inputs/canales/helpers exige rechazo o diseño/revisión
  separado dentro de las restricciones, sin ocultar trabajo o cambiar cuotas.

CE10 exige los caps de cada registro real además del bundle 262.144. La cota
condicional 221.644/margen 40.500 de I192 sólo compone índices que ya cumplen
esos caps; no acota todos los proofs referenciados, transitorios o el servicio.
No se recortan autores/aliases/dependencias para caber ni se emiten firmas,
PASS o SOURCE_CAPACITY_VERIFIED a cuenta de hechos futuros.

## Checklist y estado presente

El checklist enlaza cada familia con su schema/pointer/campos obligatorios,
cap, paquetes productores y paso final; cada regla K01–K16 con los paquetes que
la verifican. Los siete gates globales cubren independencia, autenticación
antecedente, scope/recursos, mapping/one-use, receipt tardío, autorización y
prohibición de promoción desde forma/plan a evidencia verdadera.

Todos los pasos salvo el receipt son PLANNED_EVIDENCE_MISSING_NOT_ACCEPTED;
el receipt está diferido. Las 31 entradas de checklist están pendientes o
diferidas: cero familias/reglas/gates aceptados, cero dossiers creados, cero
personas/appointments asignados y cero evidencia externa aceptada. Preparar
este plan no significa completar uno de los paquetes futuros.

E01–E05 siguen abiertos, E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07/
correlación false, cuatro bindings I175 pendientes. F183-01 conserva reparación
documental/ocho exclusiones; S01 no está aceptado y F179-01 no se resuelve.
Sin SOURCE_CAPACITY_VERIFIED, rebind, autoridad/destino nuevos, propuesta o
captura habilitadas o D5/H07 cerrados; IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/
1 PARTIAL UI04.1, D1–D4 e I1–I20/A52 intactos; brechas globales/reales
pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

## Verificación y publicación

`python3 docs/validation/D5-I193-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Verifica 761 pins contra Git, preserva 453 archivos publicados y comprueba
orden, cobertura completa de ocho familias/dieciséis reglas, 31 gates pendientes,
freeze antes de C y frontera CE11/CE12 sin ciclo. Sólo reproduce herramientas
Git/JSON/grafos documentales; no ejecuta producto/componentes, claims, crypto,
imágenes, callers o canales. El PASS acredita el plan, no sus hechos futuros.

La unidad son los seis archivos de work_unit.rollback_files: documento,
plan, checklist, preparación, auditor y sello. Rollback limitado a ellos.
El diff supera 400 líneas por especificación/evidencia trazables; se informa
el exceso. Runtime harness N/A: sólo planificación documental. Auditoría antes
de stage y tras commit, commit/push solicitados y comprobación remoto/árbol
limpio. Publicar no adopta, inscribe identidades, acepta recursos o concede autoridad.

Sin ejecutar/importar/compilar producto/componentes, tests, discovery,
benchmarks, criptografía o calendarios runtime ni medir plataforma. Sin cambiar
fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o inputs;
sin inspeccionar ni limpiar dev/run_data/D4. Sin identidades/imágenes/servicios/
ledger/claims/firmas/autoridad o evidencia positiva reales creados; sin
proveedores, credenciales, consumo, activación, promoción, despliegue o D6.
