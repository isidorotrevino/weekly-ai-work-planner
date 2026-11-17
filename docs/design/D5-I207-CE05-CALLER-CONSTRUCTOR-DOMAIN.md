# I207 — CE05 preparado sin caller, constructor o dominio reales

CE05 (CALLER-CONSTRUCTOR-DOMAIN) queda **preparado como dossier documental de
procedencia faltante**, sin principal, solicitante, backend, constructor, dominio,
endpoints o enrollment seleccionados o aceptados. No se crea un caller_identity
ni una capacidad de ejecución. PGO181 candidato 02/PJC115-R2 mantienen la no
admisión, D5 abierto e IR03 `NOT_READY`.

Fecha del cliente: 2026-11-17, Europe/Madrid. Base publicada I206:
`49f7152be801d69a4c960567ba6f1a4d8b311d8b`. La fecha documental no prueba reloj,
currentness o capacidad de una plataforma.

## Entrega y dependencia pendiente

[CE05 candidato](../validation/D5-I193-CE05-CALLER-CONSTRUCTOR-DOMAIN-CANDIDATE.json)
ocupa la ruta exacta de `/steps/4` de I193. Conserva tres requisitos de evidencia,
dos checks, frontera de autorización y K02/K06/K07/K08/K09/K15. La checklist asigna
caller_identity a CE05/CE08 y su finalización a CE08. El wrapper tiene schema
propio; no es una instancia positiva I191 rellena con valores nulos.

CE04 quedó confirmado documentalmente como baseline en I206, sin imagen/runtime
o aceptación reales. Su dependencia competente sigue insatisfecha, junto con
las anteriores CE01–CE03. La petición I207 permite documentar esos faltantes;
no autoriza seleccionar infraestructura, enrolar personas/principales o ejecutar
constructor, procesos o componentes para suplirlos.

El inventario fija 15 documentos por hash/tamaño: I193/checklist, I191/pack,
CE01/CE03/CE04/I206, I122 y las referencias I192/perfil02/protocolo/output/transporte.
Los 832 pins se contrastan con Git y disco; esos hashes documentales no son
prueba de origen de un caller, endpoint, dominio o proceso real.

## Obligaciones por consumidor

| Obligación | Consumidor | Alcance, actualmente faltante |
| --- | --- | --- |
| CC01 | CE05 | Principal software auténtico, humano solicitante responsable, identidad canónica y enrollment real |
| CC02 | CE05 | Relaciones actor/imagen/caller/dominio/constructor previamente autenticadas, sin exigir hashes finales/C/bundle futuros |
| CC03 | CE05 | Mecanismo existente concreto de constructor/loader/privilegios/aislamiento y primera entrada inmutable |
| CC04 | CE05 | Procedencia y custodia exclusivas de endpoints heredados I189, dos pipes y seis operandos |
| CC05 | CE05 | Prueba de por qué fd/PID/UID/env/module/cwd/hash o mutación/inyección no pueden seleccionar al caller/imagen aceptados |
| CC06 | CE05 | Política bootstrap-custody-only, sin ejecución por appointment, frame, READY o firma |
| CC07 | CE06 diferido | Garantías completas de plataforma, reloj/currentness y dominio global de un uso |
| CC08 | CE07 diferido | Composición completa de recursos/costes por intento, backend/custodia/crypto/IO/900 s |
| CC09 | CE08 diferido | Freeze final de caller después de actor/image, con autores y antecedentes completos antes de C |
| CC10 | CE09 diferido | Proyección exacta de C, solicitante, constantes/tiempo/clock y relaciones entre registros |
| CC11 | CE10 diferido | Un único mapping actual autenticado por epoch/digest C hacia bundle/caller/image/domain/ledger |
| CC12 | CE12 diferido | Claim y construcción protegida reales sólo tras root/Q/admisión completa y autorización explícita separada |

Las doce filas siguen `MISSING_NOT_EVALUATED`, sin proveedor, localizador,
nombramiento, cuerpo/hash/tamaño o aceptación reales y sin permiso de contacto.
Seis son baseline CE05 y seis pertenecen a fases posteriores. No se exige en CE05
un C, mapping/bundle, registro final o worker futuros; tampoco se aceptan
implícitamente sus pruebas desde este baseline. Los otros dossiers no se crean.

## Identidad, capacidad y permiso

El principal software caller y el humano solicitante responsable son claims
distintos. Las identidades de rol, preparador, autor, solicitante y custodios deben
resolverse mediante la misma autoridad genuina; nombres, strings, claves o roles
no prueban personas distintas. Un humano designado no concede por sí solo la
capacidad funcional de ejecutar o construir un worker.

El caller debe vincular realmente actor registry, imagen, dominio protegido y
constructor exacto, con evidencia de enrollment/aceptación previa auténtica.
Los hashes finales se congelan en CE08; se conservan como hechos ausentes, no se
rellenan desde un bundle futuro. Sus firmas posteriores pueden fijar el binding,
pero no ser la única autenticación anticipada de esos hechos anteriores.

`BOOTSTRAP_CUSTODY_ONLY_FULL_ROOT_AND_SEPARATE_REQUEST_REQUIRED` es el literal de
política del schema; no se emite como permiso real en esta preparación. C/I,
READY, un fd/PID/UID, fstat, módulo, nombre de padre o firma no autorizan imports
funcionales, capture, claim o spawn. El registro documental no es el mecanismo
concreto de constructor/loader/privilegios/aislamiento que exige K07.

No se leen ni proponen valores de PID/UID/fd/cwd/env reales como prueba. Tampoco
se selecciona un constructor/backend/caller para completar la tabla. Su origen,
inmutabilidad y aislamiento frente a shadowing, tracing, mutación de memoria,
reemplazo de imagen o inyección de descriptores siguen requiriendo evidencia
concreta auténtica, no sólo flags o hashes.

## Transporte I189 preservado como requisito

Se conservan el contrato/gramática I189 por hash y sus reglas completas, sin
crear streams ni ejecutar máquinas de protocolo:

- Dos pipes explícitos: DOWN lleva C/Q/I/L y UP lleva A, con extremos exclusivos,
  EOF y cierre de duplicados según el contrato. No hay pipe bootstrap nuevo.
- Seis operandos worker: P01, sidecar_fd, ready_fd, release_fd, directory_fd y
  lease. Cuatro descriptores distintos y >2, tipo/modo/origen correctos, stdout
  raw, fingerprints de OWNER/lease y sesión/grupo propios requieren prueba real;
  los números o nombres por sí solos no establecen origen ni capacidad.
- Los descriptores internos de runtime/spawn también requieren cierre/ownership/
  costes exactos. No se asumen gratuitos ni expuestos a código funcional. No se
  añade helper, proceso, fd, argv, archivo/lookup de confianza o atestación implícitos.
- El worker correlacionado nace en el dominio protegido aceptado. No recibe un
  mapping, recibo o confianza nuevos en frame/argv/canal añadido; valida C/Q/root
  independientemente antes de READY y conserva W_RELEASED como frontera funcional.

Si un backend real necesita ampliar esos mecanismos, la ruta sin cambios se
rechaza o requiere una revisión versionada de contratos/grafo/bounds/costes.
I207 no añade medios de transporte, cambia cuotas ni configura plataforma.

## C, mapping y construcción se mantienen en sus fases

K08 se conserva íntegro: `C.runtime_requester_id` debe igualar al
`caller.accountable_requester_actor_id` auténtico; `platform.domain_id` debe
igualar a `caller.protection_domain_id`; hashes, roles/keys, epochs, validez,
source/runtime/profile/resource y constantes literales deben coincidir. La
proyección/digest C reales pertenecen a CE09, después del freeze CE08. Ningún
C/Q o hash propio de C/bundle/receipt/root futuro se incorpora al caller schema.

K09 exige en CE10 exactamente un mapping actual autenticado para
`(configuration_epoch, SHA256(JCS(C)))` hacia un bundle/caller/image/domain/ledger.
Conflicto, rollback o estado obsoleto/desconocido rechazan. No se consulta ni crea
ese mapping aquí; el futuro bundle no autentica retrospectivamente el caller.
El caller debe resolverlo antes de P_ROOT_CHECK bajo custodia real y congelar
C/Q y estado admitido del constructor según I191.

CE12 permanece diferido y no autorizado. Sólo con los prerrequisitos reales de
I193 puede producirse un claim atómico y construcción protegida: root/Q/final
E06/payload, admisión completa y autorización separada preceden a la acción; el
claim/construcción real es requisito del recibo, no prerrequisito de sí mismo.
No hay claim, worker, reserva de paths o comando listo para ejecutarse. Fallos o
consumo parcial no permiten reutilizar la invocación según I189; no se prueba
replay ni se emite un recibo CLAIMED desde planes.

CE06 conserva la plataforma completa, CE07 recursos y CE08 los autores/registros
finales. Todo lookup/frescura/identidad/verificación, copias/clock/registry/receipt
y trabajo nativo/IO necesario por intento permanece dentro de t0/fases/global
E01–E05. Enrollment previo o llamar algo offline no vuelve gratuito el trabajo.
No se demuestra heap, CPU/IO, servicio o los 900 segundos.

## Límites de evidencia y preservación

`actual_caller_state` deja ausentes principal, solicitante, registros actor/image,
dominio, constructor/mecanismo, enrollment, endpoints/descriptores/peer, entrada
inmutable, aceptación previa, epoch/validez, caller body/hash/tamaño, C/Q, mapping,
aprobaciones, claim/receipt, reloj/ledger y recursos. Sus flags de selección,
enrollment, creación, verificación, freeze o permiso funcional son falsos.
Los cuatro fragmentos de schema —caller_identity, identity, evidence_reference,
validity— son exactos. El caller record cerrado tiene 13 campos y cap candidato
8.192 bytes; no es el cap del wrapper ni prueba de ajuste. Codec/hash/schema/cripto
reales sobre un cuerpo final siguen sin ejecutar y pertenecen a CE08.

R01/R02/R06/R08 están sin personas, nombramientos, competencia, claves/vigencias
o aceptación. El mismo asistente/chat prepara el dossier, sin independencia
personal u organizativa acreditada. Ningún artefacto o publicación sustituye
aceptación competente o evidencia externa genuina.

Permanecen ocho exclusiones S01, cuatro separaciones extra, nueve condiciones
CP07, candidatos numéricos y cuatro acciones documentales/14 clases denegadas.
I122 sigue `IMPLEMENTED_NOT_ADMITTED`, CP03 verdadero sólo en su alcance heredado,
CP07 falso, atomicidad correlacionada no verificada y componentes `NOT_RUN`.
E01–E05 abiertos, cero obligaciones cerradas; E06 separado y sin ejecutar,
F179-01/S01 sin aceptación. Fuentes sucesoras, ocho cuerpos I191 y los otros siete
dossiers siguen ausentes. No cambian cuota, reserva, presupuesto, schema activo,
Reader, capture_inputs, binding, autoridad/root o destino.

## Verificación histórica y publicación

Crear CE05 no reescribe los registros históricos de ausencia. La auditoría prueba
con `git ls-tree` que esta ruta exacta estaba ausente en la base I206 y sólo
proyecta esa consulta de presencia durante la reproducción documental heredada
I206. Los guards CE04/CE03/CE02/CE01 originales siguen anidados sin cambiar bytes;
`finally` restaura el método. Fuera del replay se exige el CE05 real, sus hashes,
CE01–CE04 preservados y los otros siete slots ausentes. No se ejecutan los `main`
de publicación históricos ni producto/componentes.

```sh
python3 docs/validation/D5-I207-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_CALLER_CONSTRUCTOR_DOMAIN_MISSING`.
[La preparación reproducible](../validation/D5-I207-preparation-review.json)
comprueba diez contraejemplos sólo en memoria: adelantar mapping o freeze a CE05;
exigir C final en baseline; aceptar una aserción fd/UID como capacidad;
autorizar por appointment/bootstrap; añadir un pipe; tomar confianza previa del
bundle futuro; aceptar CE05 desde documentación; confundir humano/software; o
permitir ejecución funcional. No son tests de componentes.
[El sello](../validation/D5-I207-integrity.json) preserva 524 archivos publicados
y fija los otros cuatro artefactos de la unidad. Harness runtime: N/A, dossier
sin seleccionar/enrolar backend, construir endpoints/procesos/claim o ejecutar
build/import/probes/producto/componentes/cripto/codec.

Unidad única superior a 400 líneas por pins, matrices y preservación; se declara
el exceso sin recortar evidencia. Commit/push publica para revisión estos cinco
archivos y limita la reversión a ellos:

- `docs/design/D5-I207-CE05-CALLER-CONSTRUCTOR-DOMAIN.md`
- `docs/validation/D5-I193-CE05-CALLER-CONSTRUCTOR-DOMAIN-CANDIDATE.json`
- `docs/validation/D5-I207-preparation-review.json`
- `docs/validation/D5-I207-audit.py`
- `docs/validation/D5-I207-integrity.json`

El siguiente alcance posible es revisar este dossier CE05 y las fronteras de
identidad/capacidad, transporte y fases diferidas. Evidencias y decisiones reales
permanecen pendientes, sin habilitar producto ni cerrar D5.
