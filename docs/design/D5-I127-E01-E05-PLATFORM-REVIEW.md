# I127 — revisión de E01–E05 de PFC126 para I122

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`42d69b558b615aae95fd226596775c752f5143f9`.

**Se revisan las cinco obligaciones; ninguna obtiene cierre de recursos.** E01
recibe una referencia local más precisa, E02 contrasta las11 partidas, E03/E04
separan trabajo y servicio, y E05 confirma la aritmética pero identifica una
frontera temporal que conviene aclarar. PFC126-CANDIDATE-01 queda byte a byte
intacto, como propuesta no atestada. Se conserva IMPLEMENTED_NOT_ADMITTED,
PJC115-R2 sin habilitar, D5/H07 abiertos e IR03 NOT_READY.

[Revisión E01–E05](../validation/D5-I127-E01-E05-review.json) ·
[Referencia local](../validation/D5-I127-runtime-reference-manifest.json) ·
[Auditoría](../validation/D5-I127-audit.py) ·
[Integridad](../validation/D5-I127-integrity.json).

| Obligación | Evidencia que sí se revisa | Resultado |
| --- | --- | --- |
| E01 identidad/correspondencia | Intérprete,12 archivos stdlib y5 nombres de extensión | Referencia parcial; sin atestación completa |
| E02 heap/capacidad |11 presupuestos y cuatro subcotas heredadas | Ajuste completo no demostrado |
| E03 trabajo/WCET | F/S, clone y mapa de fases/procesos | Núcleo acotado; trabajo total sin prueba |
| E04 servicio/latencias | Campos y reparto600/90/60 de PFC126 | Sin servicio o latencia atestados |
| E05 éxito<=900 | Sumas y fronteras fuente | Aritmética válida; aclaración de frontera y prueba temporal pendientes |

## E01 — qué identifica el manifiesto local

Se leen archivos y metadata del intérprete con helpers estándar, sin importar
producto/candidata/componentes. El binario local sigue teniendo SHA256
`52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41`, coincidente
con I126. Se añaden referencias de json,threading,subprocess,multiprocessing,io y
hashlib:12 archivos .py, con path/tamaño/hash. Se leen también dos candidatos
externos .so de _hashlib/_multiprocessing. Los nombres _json/_struct/
_posixsubprocess figuran como builtin del intérprete; no encontrar un .so para
ellos **no** significa que falte la implementación.

Son referencias de archivos, no una prueba de los módulos efectivamente
cargados. Un archivo io.py puede coexistir con una implementación frozen; tampoco
se certifica el cierre de dependencias nativas a partir de dos .so. La etiqueta
uname del kernel no es un pin de su imagen/configuración ni una garantía CPU.
No se usa ldd, no se carga una extensión candidata para descubrirla y no se
miden memoria, rendimiento o servicio.

Faltan el cierre de ejecución real, correspondencia fuente/binario, libc y
allocator, kernel/configuración, dominio de servicio y una atestación con
responsable y validez. El manifiesto no rellena retroactivamente los null de
PFC126 ni concede environment_manifest_verified. Su comprobación local opcional
relee hashes; no ejecuta los archivos inspeccionados.

## E02 — presupuesto frente a prueba

Los11 presupuestos suman correctamente10432MiB solicitados por propietario,
832MiB de reserva y1024MiB de overhead:11GiB solicitado/12GiB comprometido. Son
presupuestos candidatos, no demanda medida, disponibilidad, reserva operativa o
nuevas cuotas. Todas las proof_upper_bytes completas siguen siendo null.

| Partida con información parcial | Presupuesto | Subcota/modelo heredado | Lectura correcta |
| --- | ---: | ---: | --- |
| H04 clones/memo | 6442450944 B | 23096917808804736 B | El modelo condicional no demuestra ajuste |
| H08 Reader | 536870912 B | 532675582 B | Quedan4195330 B hasta el presupuesto, sin prueba de headers/mapas |
| H09 páginas | 201326592 B | 134217728 B | Payload no equivale a memoria completa |
| H10 raw | 134217728 B | 62914560 B | Falta capacidad/copias/árboles, no sólo texto |

El gran mayorante H04 es un sobreconteo condicionado de almacenamiento acumulado;
no es una necesidad real ni prueba de inviabilidad. Las otras subcotas no
acreditan sus propietarios completos aunque queden por debajo del presupuesto.
H01/H02/H03/H05/H06/H07/H11 tampoco reciben una cota completa nueva.

Para cerrar E02 hay que asignar y acotar todos los objetos/temporales/vidas,
originales y nativos, definir el dominio de heap comprometido/allocator,
justificar los prefixes de rechazo y comparar con capacidad atestada. Se puede
sobrecontar aliases, pero no omitir objetos, fusionar witnesses ni usar la
reserva832 como sustituto de una prueba. Los otros procesos tienen cuentas
separadas si se pretende afirmar capacidad total del host.

## E03 y E04 — mapa de costes y servicio

Se preservan F<=52018, S<=1759,53778 generaciones y17164544043094 visitas al
clonador de I124. No se convierten en instrucciones o segundos. El mapa fuente
separa contribuciones que una prueba futura debe incluir:

- Tpre no es sólo preparación del coordinador: incluye validaciones y lecturas
  del worker antes de READY, además de Popen/canales/handshake.
- Tworker incluye originales, metadata, proyecciones, codecs, GC/destrucción,
  nativo, servicio de hijos y las lecturas/escrituras finales del worker.
- Tpost incluye after/finish del coordinador, validación/parse/agregación y el
  finally: listado/comprobación del paquete, contexto/launch, cierres y retorno.

Los266337791 bytes del Reader worker no son una cota de CPU ni de IO de todos
los procesos. Las mismas rutinas usadas por ambos procesos necesitan una cuenta
por proceso/fase. El trabajo ajeno a clone no puede tomar valor0 por omisión.

E04 permanece sin unidad/rate/latency probados y sin evidencia de servicio. El
reparto600CPU/90IO-hijos/60scheduling es una propuesta, no una reserva o una
curva inferior de servicio. Identidad de CPU, frecuencia o número de cores no
sustituyen las garantías de ejecución/interferencia/latencia necesarias. Se
requiere un WCET sustentado o trabajo completo y servicio compatible; W/budget
es una exigencia de la prueba, no evidencia de disponer del servicio.

## E05 — hallazgo F127-01: frontera observada, no exit físico

La aritmética60+750+60+30=900 y600+90+60=750 es correcta. No justifica por sí sola
los upper de fase, que permanecen null. Además, PFC126 llama a sus fronteras
RELEASE escrito/cerrado, salida real del worker y retorno final.

El orden fuente del coordinador es: escribir RELEASE/newline, cerrar el fd,
llamar wait_worker y continuar validaciones. El worker puede leer la línea y
progresar antes del cierre del fd del coordinador. El siguiente interleaving
es un **modelo lógico no ejecutado**, no una traza observada:

1. El coordinador escribe RELEASE y queda sin servicio antes de cerrar el fd.
2. El worker recibe la línea, prosigue y podría salir antes de ese cierre.
3. El coordinador reanuda, cierra el fd y wait_worker observa una salida previa.

Sin una garantía de orden adicional, el exit físico no es una frontera
necesariamente posterior al cierre de RELEASE. También hay latencia entre exit
y la observación del coordinador. Para una futura revisión del contrato se
propone definir marcadores ordenados en el propio coordinador:

```
t0 = entrada en launch
tR = cierre de RELEASE completo
tW = retorno True de wait_worker, timestamp en ese retorno
tF = retorno real de launch después de finally

t0 <= tR <= tW <= tF
Tpre=tR-t0; Tworker=tW-tR; Tpost=tF-tW
```

La aceptación posterior de exitcode/captura determina si esa ejecución cumple
la condición de éxito; no desplaza tW al momento de aquella validación. El
intervalo exit físico→tW queda cargado explícitamente a la espera/servicio del
coordinador, en lugar de desaparecer o crear fronteras ambiguas.

Esto es una propuesta de aclaración, **no** una modificación de PFC126, del código
ni del timer. wait_worker900 sigue siendo un watchdog local, sin garantía de
terminación o éxito extremo a extremo. E05 exige resolver los marcadores en una
revisión del contrato y cerrar E03/E04, además de cotas por fase y uso explícito
de la reserva30. No se puede absorber una fase sin cota dentro de esa reserva.

## Dictamen y publicación

E01–E05 quedan revisadas, con evidencia parcial y criterios de aceptación
explícitos. Ninguna queda cerrada; no se emite SOURCE_CAPACITY_VERIFIED. E06 no
se revisa ni ejecuta aquí: continúa separado y pendiente, componentes NOT_RUN.
No se crean autoridad/destino/captura ni se incorporan estos archivos a los
capture_inputs de I122. Cualquier incorporación futura exigirá rebind y revisar
el calendario Reader sobre bytes finales.

La auditoría usa AST, JSON, hashes, identidades de referencia y aritmética.
PASS_STATIC_SOURCE_ONLY significa consistencia documental, no PASS de
plataforma, componentes, memoria o tiempo. El modo --check-local-reference sólo
relee los archivos locales del manifiesto; el modo normal puede verificar la
instantánea histórica sin exigir que otra máquina tenga aquellos mismos paths.
Se conservan los113 archivos de I111–I126 publicados y los inputs anteriores.
El auditor funciona antes de stage y después del commit de I127. No se reescriben
los auditores históricos para cambiar sus supuestos de snapshot.

Se hace commit y push de todos los cambios de I127 conforme a la instrucción
expresa; Git publica documentos/fuentes, no concede admisión operativa. Los
resultados de publicación se comprueban en Git sin hashes circulares.

P0 conserva83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
D5/H07 y brechas globales/obligaciones reales pendientes; IR03 NOT_READY.
I86/I89/I92 INVALID_CAPTURE sin reanudación/mezcla. Sin producto/componentes,
cuotas, proveedores/credenciales, consumo/reservas operativas, activación,
promoción, despliegue o D6. No se inspecciona ni limpia dev/run_data/D4.
