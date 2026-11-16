# I192 — Contrato de identidad/custodia confirmado documentalmente

Fecha: 2026-11-16, Europe/Madrid. Base:
`e7d8444a620b9c81bd216da3c89a224fea666da6`.

**La revisión no encuentra nuevos defectos documentales bloqueantes en I191.**
Confirma sus ocho familias de índices tipados, la separación de identidades,
la cobertura de C por las aprobaciones y el orden acíclico de evidencia.
Bajo los caps de sus registros, el bundle tiene upper de 221.644 bytes.
No se acreditan identidades, imagen, custodia o capacidad reales; PGO181 02
sigue sin adoptar ni implementar, I122/PJC115-R2 sin admisión, F179-01 y D5 abiertos.

## Ruta de revisión

1. Leer el [dictamen](../validation/D5-I192-I191-documentary-review.json).
2. Contrastar la [reconstrucción de schemas, cobertura y cotas](../validation/D5-I192-I191-source-reconstruction.json).
3. Revisar el [auditor](../validation/D5-I192-audit.py) y el
   [sello documental](../validation/D5-I192-integrity.json).

Se preservan los seis archivos I191 y todos los contratos anteriores. El
mismo asistente preparó I191 y hace esta reconstrucción metodológicamente
separada: no existe independencia de actor/organización, aceptación competente,
nombramiento o autoridad de custodia real. No se crea un registro positivo,
caller, imagen, ledger, ancla, clave, firma o contexto de ejecución.

## Frontera de confianza e identidades

El contrato no admite que el bundle, C o un archivo de repositorio elijan su
propia ancla. Exige selección externa ya aceptada de digest/epoch/purpose/
clave/persona y freshness. Una firma, key_id o un registry auto-firmado no
sustituyen ese antecedente. La configuración y su autoridad siguen sin aportar.

El actor humano responsable y el principal software caller son identidades
distintas. Todos los roles/preparadores/solicitante/autor/firmantes se resuelven
mediante la misma autoridad aceptada, con aliases y competencia reales. Las
formas del schema no prueban que dos strings, claves o cuentas sean personas
distintas. Incompletitud o ambigüedad debe rechazar, no convertirse en un nuevo
alias aceptado para evadir una exclusión.

Se conservan las ocho exclusiones S01, la relación con autor de fuentes y la
separación de claves del perfil 02. Las aprobaciones nuevas de custodia exigen
además que R08 difiera de R01 y R02 tanto en persona como en clave. R01/R02
pueden coincidir si existe competencia genuina para ambos roles y dos dominios
de aprobación separados. La revisión no aplica esa política a actores reales.

## Imagen, caller y proyección de C

| Área | Resultado y límite |
| --- | --- |
| Imagen | Seis rutas exactas y evidencia de mapeo/build/cierre; no equivale a una imagen construida o medida |
| Runtime | runtime_sha256 conserva su significado completo; image_bytes_sha256 no lo sustituye |
| Caller/plataforma | Deben concordar persona responsable, imagen, dominio y constructor; fds/PID/UID no acreditan custodia |
| Proyección C | 14 campos comparten tipos exactos con perfil 02; C hash compromete el cuerpo completo y sus relaciones |
| Mapping externo | Un único bundle/caller/imagen/dominio/ledger vigente por epoch/C hash, sin añadir un campo a C/Q |
| Worker | Procedencia intrínseca del constructor protegido; no se introduce un nuevo canal o receipt enviado al hijo |

C conserva sus constantes de repositorio/root_path/offline_key_status. El
clock se deriva conservadoramente de evidencia de plataforma y su validez
queda dentro de los registros aceptados. Hashes de C, scopes, runtime/fuentes,
roles y keys deben concordar con los cuerpos reales y sus appointments.
La igualdad de tipos no verifica esas relaciones o la verdad de la evidencia.

El manifest y el core fijan los digests exactos de política/schema I191, junto
a los pins anteriores. No permiten negociar una política desde un bundle
recibido ni incrustar en la imagen su propio hash futuro. La custodia externa
selecciona la identidad esperada de imagen; el mapeo real y la inmutabilidad
desde el primer código siguen pendientes.

Si el backend necesita más transporte/fds/archivos/helpers/argv para establecer
esa procedencia, debe rechazar la ruta sin cambios o someter otra versión a
revisión con sus recursos. Los records no proporcionan ese backend por el hecho
de nombrarlo; tampoco un appointment humano concede ejecución funcional.

## Firmas y orden de evidencia

El core contiene los cinco registros actor/imagen/caller/plataforma/aceptación
y exactamente sus cinco hashes. El registro de aceptación está dentro del
core y contiene el digest de C. Las tres aprobaciones R01/R02/R08 cubren ese
mismo core bajo dominios distintos y claves de propósito externo aceptado.
Las keys de C no se convierten automáticamente en anclas de custodia.

**acceptance_record no tiene una firma individual en su schema.** Su cobertura
firmada procede de las aprobaciones del bundle, que incluyen ese registro y
su C digest. Las referencias de I191 a la aceptación firmada se leen bajo
esa estructura explícita; no se supone una firma independiente anterior que
no existe en el formato.

El contrato exige hechos de actor/imagen/caller/plataforma genuinamente
autenticados antes de C y de aceptar sus recursos antecedentes. No los toma
prestados de un bundle futuro. Las aprobaciones posteriores cierran su vínculo,
no hacen verdad una inscripción o prueba no realizada.

El recorrido DFS separado recompone 16 nodos de evidencia sin ciclos. Los
antecedentes y C no dependen de aceptación/bundle/Q/raíz/claim/receipt posteriores.
El claim depende de raíz completa, Q y mapping actual; el receipt sucede al
claim. No hay autopin de bundle/imagen o pin retrospectivo desde antecedentes.
Este grafo de prerrequisitos no prueba hechos físicos o emisiones reales.

La decisión de aceptación tiene alcance IDENTITY_IMAGE_CUSTODY_ONLY. No cierra
E01–E05, certifica capacidad o concede captura. El receipt es custodia privada
del caller, sin campos nuevos en I187 o frames I189 y sin autoridad propia.

## Cotas serializadas bajo condiciones explícitas

El schema define índices con referencias a evidencia, no todos los cuerpos de
prueba. Las cotas conservadoras de forma se calculan con literales exactos,
cardinalidades máximas, longitud decimal segura y hasta dos bytes por carácter
ASCII variable para cubrir escapes. Los máximos sin aplicar caps separados son:

| Familia | Upper conservador de schema | Cap obligatorio |
| --- | ---: | ---: |
| Anclas | 35.252 | 65.536 |
| Actores | 213.612 | 98.304 |
| Imagen | 129.700 | 98.304 |
| Caller | 1.933 | 8.192 |
| Plataforma | 5.940 | 16.384 |
| Aceptación | 13.879 | 16.384 |
| Bundle | 368.348 | 262.144 |
| Receipt | 2.702 | 8.192 |

Un upper conservador por encima de un cap no demuestra inviabilidad real.
Muestra que ese cálculo de forma aislado no basta para certificar fit.
I191 exige además codec, cap de cada registro y condiciones semánticas; no
permite truncar aliases, autores, dependencias o prueba para que quepan.

Al componer el bundle con los cinco registros **ya sujetos a sus caps**,
actores e imagen quedan limitados a 98.304 cada uno y se conservan los
uppers menores de caller/plataforma/aceptación. Incluyendo el wrapper, hashes,
policy pins y las tres aprobaciones, el upper es **221.644 bytes**, con
**40.500** de margen a 262.144. La representación canónica anidada de cada
registro tiene los mismos bytes que la usada para su hash/cap independiente.

La premisa requiere comprobar los caps reales de los registros anidados.
Los placeholders de preparación no acreditan una evidencia completa que quepa.
Tampoco esa suma incluye todos los cuerpos referenciados o prueba transitorios
de memoria, CPU, IO, firmas, métricas de imagen, latencia o los 900 segundos.
Ningún coste operativo se vuelve gratuito por ser custodia externa/offline.

## Vigencia, one-use y trabajo pendiente

La unicidad del mapping epoch/C, los snapshots vigentes, revocación conocida,
clock con error aceptado y namespace global de claim entre callers/dominios/
reinicios son obligaciones explícitas. No implican revocación instantánea
universal o durabilidad real por una declaración. Falta de freshness,
rollback, ambigüedad o claim incierto rechazan/gastan la invocación, sin retry.

La inspección confirma que perfil 02, ocho exclusiones, nueve condiciones CP07,
C/Q/I/A/L, dos pipes, seis argumentos y salida I187 permanecen intactos.
Las 496 rutas/266.693.693 Reader y todos los presupuestos siguen condicionados;
no se añade capacidad disponible o una aceptación de recursos.

Siguen pendientes revisión/adopción competentes, autoridades/actores/keys/caller/
imagen y backend reales, evidencia completa fuente-runtime-imagen/dependencias/
plataforma/clock/one-use; implementación autorizada y requalification 179/321/12/30,
E01–E05/global/phase/heap/CPU/IO/Reader/900; E06 final real, C/Q/payload/raíz/firmas
y decisiones separadas de admisión/ejecución. El dictamen no resuelve F179-01,
acepta S01 o cierra D5.

## Verificación y publicación

`python3 docs/validation/D5-I192-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Verifica 756 pins contra Git y preserva 448 archivos publicados. Reproduce
sólo herramientas documentales de I191 y recompone schemas/DFS/cobertura/
proyección/cotas por separado. No ejecuta resolvedor de identidad, crypto,
build de imagen, caller/ledger/backend, canal o producto/componentes. El PASS
no es identidad, confianza, independencia o capacidad runtime verificadas.

La unidad consta de cinco archivos de work_unit.rollback_files: documento,
dictamen, reconstrucción, auditor y sello. Rollback limitado a ellos. El diff
supera 400 líneas por evidencia trazable y auditoría; se informa el exceso.
Runtime harness N/A: revisión documental sin cambio runtime. Auditoría antes
de stage y tras commit, commit/push solicitados y comprobación remoto/árbol
limpio. Publicar no adopta, inscribe identidades o concede autoridad.

F183-01 conserva reparación documental. E01–E05 abiertos, E06 NOT_RUN; I122
IMPLEMENTED_NOT_ADMITTED, CP07/correlación false y cuatro bindings I175 pendientes.
Sin SOURCE_CAPACITY_VERIFIED, rebind, autoridad/destino nuevos, propuesta/captura
habilitadas o D5/H07 cerrados; IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL
UI04.1, D1–D4 e I1–I20/A52 intactos; brechas globales/reales pendientes.
I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

Sin ejecutar/importar/compilar producto/componentes, tests, discovery,
benchmarks, criptografía o calendarios runtime ni medir plataforma. Sin cambiar
fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o inputs;
sin inspeccionar ni limpiar dev/run_data/D4. Sin identidades, imagen, servicios,
anclas, claves, firmas, autoridad o evidencia positiva reales creados; sin
proveedores, credenciales, consumo, activación, promoción, despliegue o D6.
