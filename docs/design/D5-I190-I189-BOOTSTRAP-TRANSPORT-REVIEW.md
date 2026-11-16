# I190 — Contrato bootstrap/transporte confirmado documentalmente

Fecha: 2026-11-16, Europe/Madrid. Base:
`400f99d70b0a52d55737b4c7aa343ff16321d9b7`.

**La revisión no encuentra nuevos defectos documentales bloqueantes en I189.**
Confirma la frontera de confianza declarada, el orden C/Q/I → A/EOF → L/EOF,
la conservación de bindings y las cotas del transporte bajo sus precondiciones.
No acredita una imagen/caller reales, custodia, seguridad o progreso de código.
PGO181 candidato 02 sigue sin adoptar ni implementar; I122/PJC115-R2 sin
admisión, F179-01 y D5 abiertos.

## Ruta de revisión

1. Leer el [dictamen](../validation/D5-I190-I189-documentary-review.json).
2. Contrastar la [reconstrucción de orden y cotas](../validation/D5-I190-I189-source-reconstruction.json).
3. Revisar el [auditor](../validation/D5-I190-audit.py) y el
   [sello documental](../validation/D5-I190-integrity.json).

Se preservan los seis archivos I189, el perfil/protocolo 02 y la salida I187.
El mismo asistente preparó I189 y realiza esta reconstrucción metodológicamente
separada. No hay independencia de actor/organización, nombramiento o aceptación
competente. La revisión no crea fuentes, imagen, procesos worker, canales de
protocolo, claves, firmas o evidencia de captura.

## Confianza antes de usar bytes del repositorio

El contrato exige caller aceptado, entrada de imagen confiable y mapeo exacto
fuente-runtime/loader/stdlib/nativo inmutable desde el arranque. Si no se puede
acreditar, rechaza antes de ejecutar código mutable del repositorio. No propone
autenticar después un módulo ya ejecutado desde cwd o mecanismos de shadowing.

La procedencia de C/Q depende de la capacidad de creación del proceso y de la
custodia exclusiva de endpoints. Ni fstat, fd, PID, key_id, argv o un digest
constituyen esa confianza por sí solos. El worker vuelve a validar contexto,
solicitud y evidencia real de raíz antes de READY. El contrato distingue esa
obligación de una implementación o prueba de la plataforma: ambas faltan.

La imagen elegida no se suministra. R01/R02 y revisores competentes deben
acreditar runtime/fuentes/custodia, ausencia de inyección/duplicación/tracing
hostil, loader y reloj/epoch/one-use reales. Estas precondiciones son límites
de la propuesta, no garantías del equipo actual o una autorización de despliegue.

## Ownership, secuencia y EOF

| Paso | Condición revisada |
| --- | --- |
| Antes de paths/spawn | Caller, raíz completa y claim one-use aceptados |
| C/Q/I hacia worker | Lectura concurrente; no esperar down EOF tras I |
| READY/A | Sólo tras validación completa del worker; cerrar writer up |
| Padre | Validar A y EOF, luego recheck vivo antes de escribir L |
| RELEASE/L | Cerrar writer down; worker exige L y EOF |
| Import funcional | Sólo después del recheck final del worker y permiso separado |

Se mantienen dos pipes explícitas y los seis operandos observados por I187.
Los extremos opuestos/duplicados se cierran, el raw/sidecar/directorio tienen
roles distintos, owner/lease/identidades son verificados y no se delegan canales
a descendientes funcionales. El runtime/spawn interno necesita sus propias
pruebas de fds/cierre/recursos; no se considera gratuito.

Las obligaciones de espera no introducen un ciclo de canal en el orden nominal:
el worker consume C/Q/I mientras el padre escribe; produce/cierra A antes de
esperar L; el padre consume A/EOF antes de L y cierra down sin esperar el fin
funcional. El worker no pide otro reply antes del import.

Esto revisa 12 estados locales del padre y 11 del worker, no el producto de
estados concurrentes o todos los interleavings. No prueba ausencia real de
deadlock, fairness, servicio del kernel, retorno de librerías o comportamiento
de excepciones. El orden real del emisor exige fuentes y custodia correctas;
los bytes recibidos no prueban por sí solos la cronología de escritura remota.

## Framing y cotas, incluidos rechazos

Se confirman cinco cuerpos de schemas 02 existentes con un LF único, sin
wrappers, tag, negociación o longitud extra. El estado selecciona el schema;
EOF parcial, formato/mismatch/roles/tiempo erróneos o bytes extra rechazan.
La lectura propuesta de un byte no sobrelee el siguiente frame; el writer
avanza exactamente por el progreso observado, sin repetir prefijos.

| Frame | Cap con LF | Longitud exacta si el control cumple schema |
| --- | ---: | ---: |
| C, contexto | 8.193 | Se mantiene el cap |
| Q, solicitud | 2.049 | Se mantiene el cap |
| I, INVOKE | 512 | 409 |
| A, READY | 512 | 403 |
| L, RELEASE | 512 | 407 |

Los controles tienen sólo literales y digests hex de longitud fija. Por ello,
sus cuerpos canónicos miden exactamente 408/402/406 bytes y sus frames
409/403/407. Manteniendo los caps de C/Q, un stream conforme queda acotado a
11.461 bytes. La envolvente publicada de cinco caps sigue en **11.778**.

La reconstrucción considera también el primer slot rechazado. En ese slot
se permiten cap de body más un byte de LF/overflow; los controles previos
válidos tienen longitud exacta. Los sondeos terminales leen como máximo un
byte inesperado antes de rechazar:

| Primer rechazo o sondeo | Upper de bytes consumidos entre receptores |
| --- | ---: |
| C | 8.193 |
| Q tras C | 10.242 |
| I tras C/Q | 10.754 |
| A tras C/Q/I | 11.163 |
| Byte extra tras A válido | 11.055 |
| L tras A/EOF válido | **11.566** |
| Byte extra tras L válido | 11.462 |

La cota de prefijos sigue dentro de 11.778 para estos casos del receptor
fail-stop declarado. No es un límite a todo lo que un emisor arbitrario no
conforme pueda ofrecer/dejar encolado, ni al tráfico externo a la custodia
aceptada. No se implementa o ejecuta un parser de streams, una pipe, un worker
o un calendario para obtener esos números.

La aritmética nominal de I189 permanece: 11.266 bytes down, 512 up, 23.556
contando transferencias de lectura/escritura y 23.558 llamadas de progreso
byte a byte más dos lecturas EOF. Los retries/readiness tienen su contador
separado global de 65.536 por endpoint, 131.072 entre ambos. Esas cifras no
son un conteo de syscalls real ni una prueba de CPU/heap/IO global.

## Plazos, one-use y fallos

Los dos plazos de 20 segundos tienen orígenes explícitos distintos y no se
reinician por frame/byte/retry. No se comparan relojes entre procesos. Los
checks de deadline/counter son una política de rechazo; no preemptan por sí
mismos spawn, crypto, librerías, syscalls o descheduling. Sus cotas de servicio,
reloj y coste dentro de launch/worker/finish continúan pendientes.

El padre reclama one-use antes de paths/spawn y un intento fallido queda
gastado. El worker es el hijo correlacionado del mismo claim, no una segunda
solicitud o un segundo consumo. La custodia restart-safe y la unicidad real
siguen sin implementarse. No se autoriza un retry con otra raíz o un rebind.

Se preserva el primer fallo auténtico cuando el sidecar/owner es confiable,
sin error frames nuevos, datos funcionales o READY/RELEASE inventados. Sin
canal/owner aceptados no se escribe allí; se cierran y paran sólo recursos de
propiedad demostrada. Si faltan pruebas de grupo desaparecido o de outputs
completos, sigue bloqueado. La compatibilidad I187 usa los recibos I/A/L y los
digests C/Q existentes, sin cambiar schemas o fingir un transcript grabado.

## Alcance heredado y pendientes

Perfil 02, reparación documental F183-01/ocho exclusiones S01, nueve condiciones
CP07 y caps numéricos permanecen intactos. Tampoco cambian las seis fuentes
propuestas, las 496 rutas o la aritmética Reader condicionada 266.693.693.
Todos los lectores de ambos procesos, parsing/copia, clocks/poll/crypto,
descriptores internos, startup/cleanup y dos escrituras necesitan join global
E01–E05 y pruebas reales de fase/heap/CPU/IO/900. No hay un servicio o fit
Reader nuevo acreditado por la gramática.

Siguen pendientes revisión/adopción competentes, caller e imagen exactos,
implementación autorizada de loader/guard/transporte/excepciones/output,
mapeo fuente-imagen y requalification de 179/321/12/30; evidencia antecedente y
E06 final reales, contexto/requests/payload/raíces/firmas y decisiones separadas
de admisión/ejecución. El dictamen sólo confirma el contrato bajo sus
precondiciones; no cierra F179-01 o D5 ni habilita captura.

## Verificación y publicación

`python3 docs/validation/D5-I190-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Contrasta 745 pins contra Git, preserva 437 archivos publicados y reproduce
sólo herramientas documentales de I189. Recompone cadenas/guards y deriva
longitudes de controles/prefijos por separado, sin crear canales de protocolo
o ejecutar producto/componentes/criptografía. El PASS no es aceptación
independiente ni una prueba de seguridad/progreso runtime.

La unidad son los cinco archivos de work_unit.rollback_files: documento,
dictamen, reconstrucción, auditor y sello. Rollback limitado a ellos. El diff
supera 400 líneas por evidencia trazable y auditoría; se informa el exceso.
Runtime harness N/A: revisión documental sin cambio runtime. Auditoría antes
de stage y tras commit, commit/push solicitados y comprobación remoto/árbol
limpio. Publicar no adopta ni concede autoridad.

E01–E05 abiertos, E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07/correlación
false y cuatro bindings I175 pendientes. Sin SOURCE_CAPACITY_VERIFIED, rebind,
autoridad/destino nuevos, propuesta/captura habilitadas o D5/H07 cerrados;
IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e I1–I20/A52
intactos; brechas globales/reales pendientes. I86/I89/I92 INVALID_CAPTURE no
se reanudan ni mezclan.

Sin ejecutar/importar/compilar producto/componentes, tests, discovery,
benchmarks, criptografía o calendarios runtime ni medir plataforma. Sin cambiar
fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o inputs;
sin inspeccionar ni limpiar dev/run_data/D4. Sin imagen/caller, procesos o
canales de protocolo, claves, firmas, autoridad o evidencia positiva reales
creados; sin proveedores, credenciales, consumo, activación, promoción,
despliegue o D6.
