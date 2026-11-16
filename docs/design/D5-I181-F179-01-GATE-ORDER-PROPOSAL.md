# I181 — Propuesta versionada para separar base previa y CP07 completo

Fecha: 2026-11-16, Europe/Madrid. Base:
`49644701b654c55c468272f2e721f153f126e37a`.

**PGO181-SPLIT-ROOT-01 propone resolver F179-01 mediante dos afirmaciones
distintas y un orden verificable:** una base antecedente aceptada, sin afirmar
CP07 completo, y una raíz final emitida después de los componentes y bindings
reales. CP07 completo se evalúa sólo al validar esa raíz y todo el bundle.
No se reduce el significado del gate actual. Es un protocolo sucesor propuesto,
sin adoptar ni implementar; no resuelve materialmente F179-01 ni habilita
admisión, E06, rebind o ejecución.

## Ruta de revisión

1. Leer la [propuesta](../validation/D5-I181-F179-01-GATE-ORDER-PROPOSAL.json):
   cuatro etapas de afirmación, DAG, raíz final y presupuesto de diseño.
2. Contrastar el alcance del certificado base frente a las condiciones completas
   de admisión final, sin equipararlos.
3. Revisar el cobro de la raíz al mismo Reader y las pruebas nuevas necesarias.
4. Consultar la [preparación](../validation/D5-I181-preparation-review.json),
   el [auditor](../validation/D5-I181-audit.py) y el [sello](../validation/D5-I181-integrity.json).

## Decisión propuesta

El parser I122 exige SOURCE_CAPACITY_VERIFIED y CP07=true en un certificado
que precede por hashes al manifest y a los componentes. F179-01 deja abierta
la frontera legítima de esa afirmación. Si significa que ya existe y está
aceptada la evidencia final que depende de él, el orden de bytes no permite
justificarla con un run futuro.

Se propone una versión incompatible y explícita, con nombres nuevos. El
certificado predecesor **no contiene el antiguo campo CP07_exact_admission_resolved**
ni usa SOURCE_CAPACITY_VERIFIED. Afirma sólo evidencia que ya puede ser verdad
antes de los consumidores. El CP07 completo conserva sus exigencias en la
decisión final: componentes reales, fuente/contrato/manifest, hashes, permisos,
trust/validez, recursos e inputs finales exactos. No desaparece ningún requisito.

| Etapa nueva | Afirmación permitida | Lo que no afirma |
| --- | --- | --- |
| BASIS: d5.prp181-source-basis.v3 | Base de CP03, E01–E05 y atomicidad antecedente realmente aceptada para las fuentes exactas | CP07 completo, E06 final o permiso de captura |
| FINAL_COMPONENTS: familia v3 | Run final real, review y sello con manifest/fuentes/runtime exactos | Cierre de recursos o autorización de captura por un PASS aislado |
| PAYLOAD: d5.prp181-authority-payload.v3 | Datos y scope de emisor con los 494 pins reales | Permiso runtime por la mera presencia del payload |
| FULL_ADMISSION: d5.prp181-final-admission-root.v3 | Cierre observado y emisión competente después de todos los cuerpos anteriores | Hashes futuros, certificado predictivo o éxito de ejecución futura |

El parser actual no soporta esta separación: seguiría rechazando el nuevo
estado/schema y exigiendo su gate antiguo. No es un rebind directo de PRP173,
una excepción al código existente o una nueva definición aplicada al certificado
actual. La adopción exige código y schemas nuevos en otro alcance revisado.
Aquí no se escriben esas fuentes o cuerpos runtime.

## Orden que elimina la dependencia semántica hacia el futuro

El modelo fija quince nodos de evidencia, datos y decisión. Sus dependencias
incluyen prerrequisitos semánticos/protocolo, además de hashes. El orden es:

1. Fuentes sucesoras y contrato; evidencia completa de recursos y base de
   atomicidad, realmente aceptadas. Si hacen falta componentes calificadores,
   se obtienen por una autorización futura separada y no se llaman E06 final.
2. Índice sólo de antecedentes; registry y certificado BASIS. Ninguno referencia
   raw/review/seal finales, payload o raíz posteriores.
3. Manifest final; componentes reales; revisión y sello. Los consumidores
   tardíos no se pinnean hacia atrás en el manifest.
4. Payload de autoridad completo, sin autopin ni raíz final en su mapa.
5. Raíz final que fija payload, fuente base, manifest y componente trio reales,
   scope de aceptación, validez y compromiso del conjunto de antecedentes.
6. Consumidor runtime verifica raíz y todos los predicados antes de admitir.

El auditor comprueba que el certificado BASIS y el índice no tienen nodos
finales entre sus antecesores y que la raíz sí depende de toda la cadena real.
Incluye como contraste un pequeño ciclo hipotético certificado→sello→manifest→
certificado, sólo bajo la interpretación pendiente que exige evidencia propia
posterior. No afirma que el DAG negativo I175 tenga ese ciclo ni que todo
protocolo alternativo sea imposible.

La base de atomicidad exige evidencia antecedente aceptada, no implementación
escrita, un contador de diez tests o una predicción. E06 final se exige aparte.
Los nueve predicados de CP07 final incluyen recursos completos, componentes
reales, pins/freshness, confianza/validez, separación de aceptación, cuotas
inalteradas y solicitud runtime explícita. No se permite un certificado
emitido como verificado a cuenta de una validación aún no realizada.

## Raíz final sin ciclo ni lectura gratuita

La ruta propuesta es D5-PRP181-FINAL-ADMISSION-ROOT.json; no existe ahora. Es
un punto de arranque confiable del nuevo protocolo, no miembro del mapa de la
autoridad o de los bindings del certificado. Ningún predecesor la pinnea.

La firma se define sobre un signed_core canónico; excluye el campo firma,
el hash del propio archivo y resultados de ejecución futuros. El core fija
hashes anteriores reales, scope/validez y perfil de verificación. Firmante,
perfil y claves permanecen sin elegir o crear. Se requiere confianza de un
caller/runtime aceptado, sin confiar en un key_id autopropuesto por el archivo.

La raíz se lee físicamente en BEFORE y AFTER y se vuelve a leer en finish,
con el **mismo Input Reader**. PhaseBytes incluye sus bytes declarados sin
fingir lectura fresca. La unión es raíz + payload + sus 494 miembros: 496
rutas. La excepción de descubrimiento no es un Reader nuevo, reset, quota
extra o snapshot gratis. Si una key/helper requiere otros archivos, deben
aparecer y cobrarse en el grafo revisado; este presupuesto no los oculta.

La verificación debe fallar cerrada ante ausencia, firma no confiable,
expiración, scope/hash incorrecto o inestabilidad. Debe preceder a reservar
rutas de captura y a READY/RELEASE/import funcional del worker. Su trabajo
queda dentro de launch t0..tR y las ventanas reales del worker, con todos los
costes de firma, parsing, IO, memoria, GC y nativo contabilizados.

El digest de raíz debe ligarse a invocación y READY/RELEASE del coordinador y
worker para no aceptar raíces distintas. Sólo los outputs posteriores de
captura registran la raíz usada: no crean un pin hacia atrás. Los mensajes y
schemas de evidencia requieren versiones nuevas y prueba de sus límites.

## Presupuesto numérico de diseño, sin prueba de fit heredada

Se propone reservar hasta 262.144 bytes para seis fuentes sucesoras en un
namespace separado aún inexistente. Las seis actuales suman 217.934; no se
sobrescriben ni se asume que su prueba cubra código nuevo. Los 480 inputs
históricos se conservan con sus 86.765.083 bytes exactos.

| Partida de diseño | Bytes |
| --- | ---: |
| 480 inputs históricos | 86.765.083 |
| Seis fuentes sucesoras, máximo conjunto propuesto | 262.144 |
| Nueve cuerpos variables equivalentes a PRP173, máximo conjunto | 244.992 |
| Raíz final adicional, máximo propuesto | 8.192 |
| Upper único de diseño | 87.280.411 |
| Tres pasadas más techo fresco de diseño 4.852.460 | **266.693.693** |
| Límite de lectura intacto | 268.435.456 |
| Margen numérico condicionado | **1.741.763** |

Las 496 rutas y esos máximos son compatibles numéricamente con file16MiB,
unique128MiB, read256MiB y 4096 paths. Son condiciones de diseño inferiores a
las cuotas existentes, no cambios de producto, capacidad reservada o enforcement.

El techo fresco 4.852.460 **debe demostrarse otra vez** para el código nuevo:
no se hereda automáticamente. Tampoco están materializados los schemas,
las fuentes, firma o cuerpos finales. Por ello successor_Reader_fit_verified
sigue false. Si hacen falta más fuentes/keys/lecturas, crecen los cuerpos o
cambian listings, se revisa el grafo/cota o se rechaza; no se aumenta cuota.

El scope de 321 raíces/12 grupos, operandos, treinta sitios, runtime/nativo,
heap, CPU/servicio y fases necesita requalification para el sucesor. Los
outputs y handshake nuevos no heredan el modelo parcial de metadata anterior.
Todo trabajo criptográfico y de root debe entrar en E01–E05 y los presupuestos
de fase; no se extrae del objetivo 900 moviéndolo fuera de launch.

## Adopción y estado actual

La propuesta requiere nombres y aceptación competente de custodios, revisores
de recursos/protocolo y aceptación separada; especificación exacta de schemas,
trust y guard; implementación autorizada en otro alcance; requalification
completa; evidencia real de componentes y emisión final. Sólo después cabe
decidir un rebind/ejecución de captura separado. No se conceden esos permisos.

I181 entrega una solución lógica candidata para la frontera de F179-01,
no su adopción ni cierre material. S01 sigue sin aceptar; ocho asignaciones y
los cuatro bindings I175 siguen pendientes. No se crea certificado positivo,
firma, root, payload de autoridad, componente PASS o namespace nuevo.

E01–E05 abiertos, E06 NOT_RUN; certificados actuales IMPLEMENTED_NOT_ADMITTED,
CP07/correlación false. D5/H07 de cierre abiertos e IR03 NOT_READY; sin
SOURCE_CAPACITY_VERIFIED, gate actualizado o propuesta/captura habilitadas.
P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1; D1–D4 e I1–I20/A52 intactos;
brechas globales y reales pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan.

`python3 docs/validation/D5-I181-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Comprueba 696 pins históricos contra Git, predicados
fuente, DAG/contraejemplo, orden de afirmaciones y presupuesto aritmético.
Preserva 388 archivos publicados e inputs heredados. No ejecuta el protocolo,
producto, componentes o un calendario ni prueba recursos con una simulación.

Unidad de cinco archivos: propuesta, preparación, este documento, auditor y
sello. Rollback limitado a los cinco archivos enumerados en work_unit. El diff
supera 400 líneas por la especificación trazable y auditor autocontenido;
el exceso queda informado. Runtime harness N/A: propuesta documental sin
cambio runtime. Auditoría antes del stage y tras commit, push autorizado y
comprobación de remoto/árbol limpio. Publicar no adopta, admite o autoriza.

Sin ejecutar/importar/compilar producto/componentes, tests, benchmarks,
introspección o mediciones. Sin cambiar código, schemas/contratos activos,
cuotas, reservas, presupuestos o inputs; sin inspeccionar ni limpiar
dev/run_data/D4. Sin proveedores, credenciales, consumo, activación, promoción,
despliegue o D6.
