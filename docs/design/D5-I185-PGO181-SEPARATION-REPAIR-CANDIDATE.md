# I185 — Candidato 02 conserva las ocho exclusiones de S01

Fecha: 2026-11-16, Europe/Madrid. Base:
`a5c48bb713fb220d6b983176c3c1af75819d792f`.

**I185 prepara la reparación documental de F183-01 en un candidato 02 nuevo.**
Expresa las ocho exclusiones de S01 y vincula la lista completa de preparadores
con procedencia auténtica al contexto y al core firmado. Conserva la separación
adicional respecto al autor de fuentes y entre claves. No modifica I183/I184,
adopta S01, nombra personas o concede admisión. La reparación candidata necesita
revisión separada; F179-01 y D5 siguen abiertos e I122/PJC115-R2 sin admisión.

## Ruta de revisión

1. Leer el [perfil candidato 02](../validation/D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json):
   bootstrap.inherited_S01_actor_exclusions y documentary_preparer_binding.
2. Contrastar el [paquete de schemas 02](../validation/D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json):
   trust_context.documentary_preparers y el compromiso en role_acceptance_scope.
3. Revisar la [preparación](../validation/D5-I185-preparation-review.json),
   el [auditor](../validation/D5-I185-audit.py) y el
   [sello documental](../validation/D5-I185-integrity.json).

Los nuevos ids de paquete/perfil terminan en candidate:02/CANDIDATE-02.
Las familias v3 siguen siendo propuestas no instaladas. No se reclama
compatibilidad con cuerpos de confianza/raíz del candidato 01 ni fallback.
Los consumidores futuros tendrían que seleccionar exactamente el nuevo paquete,
perfil y sus digests; ninguno de ellos se instala ahora.

## Ocho exclusiones, sin sustituir preparador por autor de fuentes

La matriz de [S01/I179](../validation/D5-I179-S01-ROLES-SCOPE-GATES.json)
se traslada de forma explícita a ocho registros verificables, sin eliminar ni
reinterpretar sus restricciones. DOCUMENTARY_PREPARER se expande a **todos**
los preparadores de la lista auténtica, no sólo al primer elemento.

| Rol | Debe diferir de |
| --- | --- |
| R03, recursos | Cada preparador documental |
| R06, admisión/Reader | Cada preparador documental |
| R08, aceptación separada | Cada preparador documental |
| R05, revisión de componentes | R04, custodia de componentes |
| R08 | R03 |
| R08 | R04 |
| R08 | R06 |
| R08 | R07, emisión |

Se conservan además R08 ≠ source_author_id y clave del emisor ≠ clave del
aceptante. El autor de fuentes puede coincidir realmente con un preparador,
pero esa relación debe acreditarse; no se presume. Si coincide, se aplican
ambos conjuntos de restricciones. No se exige que todos los roles sean
mutuamente distintos: se comprueban exactamente las exclusiones heredadas y
las adicionales conservadas.

## Identidad, procedencia y compromisos exactos

El contexto añade documentary_preparers, una lista obligatoria de 1–16 objetos
cerrados con actor_id, provenance_record_id y provenance_record_sha256.
Debe estar ordenada por actor_id canónico, sin duplicados y completa para el
scope de preparación documental aceptado. No se pueden omitir contribuyentes
para superar una exclusión o un límite de bytes. Si hacen falta más de 16,
se rechaza o revisa el diseño; no se amplían cuotas ni se recorta la lista.

Cada registro debe remitir a custodia auténtica aceptada que vincule actor,
contribución/scope y los digests exactos del paquete/perfil 02. Los roles,
autores y preparadores se comparan bajo la misma resolución de identidad
aceptada. Dos strings o claves distintas no prueban que sean personas distintas;
aliases, identidad ambigua, scope incompleto o procedencia no aceptada rechazan.
Un record_id o digest aislado tampoco acredita la existencia de esa custodia.

El contexto completo, incluidos todos los registros de procedencia, entra en
signed_core.trust_context_sha256. Además,
role_acceptance_scope.documentary_preparers_sha256 compromete SHA-256 de JCS
de la lista exacta ordenada. Ambas firmas de rol cubren ese mismo core con
ambos compromisos. R06 y el aceptante separado R08 deben contrastar
procedencia y completitud auténticas antes de emitir/admitir.

Son condiciones de un contrato futuro. No se crea una lista real, custodia,
nombramiento, clave, firma, solicitud, raíz o cuerpo PASS. El mismo asistente
preparó los candidatos anteriores y éste; la auditoría no aporta independencia
de actor/organización ni aceptación competente.

## Delta acotado y presupuesto conservado

El diff del schema tiene siete rutas de cambio: id, título, id del perfil,
propiedad/lista required de documentary_preparers y propiedad/lista required
del nuevo compromiso en role_acceptance_scope. Se conservan 17 familias y
32 definiciones; las nuevas entradas usan un objeto cerrado inline.

El resto de los schemas queda idéntico al candidato 01. Se conservan los
480 históricos, seis fuentes, BASIS 489, manifest nueve y payload 494; el orden
antecedente, las nueve condiciones de CP07 y las exclusiones de autopin/futuro.
No se cambian criptografía, límites numéricos, caps de cuerpos, dominio de firma,
scopes o presupuestos de I183. Sólo C08/C09 se amplían para exigir el nuevo
binding y las exclusiones; las demás reglas semánticas permanecen intactas.

El contexto sigue limitado a 8.192 bytes y la raíz a 8.192. La comprobación
estructural en memoria con 16 entradas de longitudes máximas produce 6.905
bytes de contexto y 2.794 de raíz para esos placeholders. No acredita identidades,
procedencia, firmas o un upper universal de todo el protocolo. Schema, cap,
orden/unicidad, exclusiones e identidad real deben cumplirse conjuntamente.

La custodia/procedencia se exige a inputs auténticos acotados del caller;
no se introducen archivos, helpers o red gratuitos. Todo parsing, copia,
resolución, comparación, verificación y coste nativo pertenece a E01–E05 y las
ventanas launch/worker/finish. Si la implementación necesita otros cuerpos o
transcripts, hay que demostrar sus cotas y revisar grafo/IO. Sus hashes no
permiten ocultar trabajo o sustituir la evidencia.

Se mantienen 496 rutas y 266.693.693 bytes como aritmética de diseño condicionada;
las fuentes sucesoras y el techo fresco 4.852.460 siguen sin demostrar.
No se acredita fit Reader, heap, CPU o el objetivo de 900 segundos.

## Verificación y límite del cierre

`python3 docs/validation/D5-I185-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Verifica 717 pins contra Git y preserva 409 archivos publicados. Reproduce el
dictamen I184 y comprueba que sus archivos y el candidato 01 siguen intactos.
Reconstruye las ocho exclusiones desde S01 y las contrasta con las reglas 02.

Los casos simbólicos comprueban las ocho colisiones heredadas, las cinco de
I184, tres conflictos con un segundo preparador y la separación adicional del
autor de fuentes. También confirman que una coincidencia real autor/preparador
no concede waivers y que no se prohíben coincidencias ajenas a la matriz.
Las comprobaciones de forma rechazan campos obligatorios ausentes, listas
vacías/de 17 entradas, procedencia incompleta, campos extra e ids 01 en los
nuevos cuerpos de confianza/raíz. No son actores reales ni ejecuciones del
protocolo, del guard o de criptografía.

La brecha exacta de F183-01 queda reparada **en el candidato 02 preparado**.
No se reescribe el hallazgo histórico ni se declara su aceptación independiente:
se requiere revisión separada del nuevo contrato, procedencia y compatibilidad.
El PASS documental no establece identidad, independencia real, custodia o
seguridad de un programa, ni cierra recursos o admisión.

Siguen pendientes adopción competente de S01/PGO181, implementación y
biblioteca exactas, schemas completos de contexto/launch, requalification de
179 casos/321 raíces/12 grupos/30 sitios y E01–E05, cotas reales, E06 final,
solicitudes/contexto/custodia auténticos, payload/raíz/firmas y decisiones
separadas de admisión/ejecución. I185 no resuelve materialmente F179-01.

## Unidad y publicación

La unidad son los seis archivos de work_unit.rollback_files: este documento,
paquete 02, perfil 02, preparación, auditor y sello. Rollback limitado a esos
archivos. El diff supera 400 líneas por los contratos completos y evidencia
trazable; se informa el exceso. Runtime harness N/A: preparación documental
sin implementación o ejecución runtime. Auditoría antes de stage y tras commit,
commit/push solicitados y verificación de remoto/árbol limpio. Publicar no adopta.

E01–E05 abiertos, E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07/correlación
false y cuatro bindings I175 pendientes. Sin SOURCE_CAPACITY_VERIFIED,
rebind, autoridad/destino nuevos, propuesta/captura habilitadas o D5/H07
cerrados; IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e
I1–I20/A52 intactos; brechas globales/reales pendientes. I86/I89/I92
INVALID_CAPTURE no se reanudan ni mezclan.

Sin ejecutar/importar/compilar producto o componentes, tests, discovery,
benchmarks, firmas o calendarios runtime ni medir plataforma. Sin cambiar
fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o inputs;
sin inspeccionar ni limpiar dev/run_data/D4. Sin personas/aceptaciones,
claves, firmas o evidencia positiva emitidas; sin proveedores, credenciales,
consumo, activación, promoción, despliegue o D6.
