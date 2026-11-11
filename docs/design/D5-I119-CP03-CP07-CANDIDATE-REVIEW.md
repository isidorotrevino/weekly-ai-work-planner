# I119 — PJC115-R2: operandos y candidata vinculada

Fecha: 2026-11-10 (Europe/Madrid). Base: `50c49678568bae2abeefbe5fec0285f26c628283`.

**Resultado: avance parcial, propuesta todavía NO habilitada.** CP03 global sigue
abierto. CP07 tiene fuentes candidatas, vinculaciones actuales y cota numérica
concretas; la admisión exacta futura sigue pendiente. D5/H07 y las brechas globales
permanecen abiertos; IR03 `NOT_READY`.

El usuario autorizó expresamente «Sí, crear fuentes candidatas sin ejecutar».
I119 crea cinco fuentes en `testing/prospective_capture_joint`, un contrato,
registro, certificado borrador y manifiesto de componentes. No se importaron,
compilaron ni ejecutaron esas fuentes. Los diez componentes son un plan
`NOT_RUN`. Las únicas verificaciones nuevas son documentales: AST, hashes,
JSON y aritmética simbólica con biblioteca estándar.

## CP03: qué se ha acotado

`D(x)` representa los bytes cargados por el digest I70; `J(x)` la serialización
original indicada. Son presupuestos independientes por llamada. Los modelos
conservan copias completas: estado, resultados, procedencia, before/after y,
cuando la aserción lo exige, la cadena independiente completa. No se descuentan
alias ni se deducen tamaños de originales a partir de un digest o fila pequeña.
Las cotas pertenecen al programa original fijo y las fuentes selladas, no a
entradas arbitrarias futuras.

| Familia / operación | Cota de bytes |
| --- | ---: |
| Recibo Store: D(whole)+D(result) | 40.514 |
| Snapshot Drive: D(snapshot) | 3.158.549 |
| Recibo Drive: D(receipt) | 445 |
| Estado remoto: D(state)+J_UTF8(state) | 10.917.045 |
| Estado cliente T: D(state)+J_UTF8(state) | 12.773.503 |
| Estado cliente R: D(state)+J_UTF8(state) | 9.783.694 |
| Petición Store: D(args)+D(op)+J_UTF8(op) | 13.762.309 |
| Petición Drive normal: digest+JSON+newline | 496.959 |
| Aserción DF44 con retorno independiente completo | 14.890.036 |
| Proyección tipada de tupla(path,SHA), Linux y stdlib fijados | 12.915 |
| SQL simulado observado por AdapterBoundary | 1.400.742 |

El máximo positivo revisado es 14.890.036, margen 1.887.180 frente a 16.777.216.
Esto **no es una prueba global de todos los operandos**. El JSON de operandos
incluye las formas simbólicas completas, tamaños, premisas y fuentes.

La prueba distingue puntos antes confundibles: recibos R con arrays completos
(created32, participants128, declared_relations64); entidades remotas con dos
textos Unicode8192; UUID5 que puede repetir identidades sin reducir objetos;
base64 DATA de 197 bytes/264 caracteres; logs T con cuentas globales de append;
Drive con hasta1024 continuaciones; cadenas DF44 de19/20 commits y remoto DF47
genesis1. Una cadena completa no se sustituye por su último estado.

Se mantiene DI24: la petición sobredimensionada rechazada origina el resultado
seleccionado `NOT_RECORDED/OPERAND_BUDGET`, con hash nulo, descrito en I118.
No se convierte esa rama negativa en un digest íntegro ni en una prueba nueva
de `INVALID_CAPTURE`. Las excepciones esperadas conservan el tratamiento
original que no digiere argumentos de la función rechazada.

Las dos familias de paths se acotan a partir del `mkdir` nativo exitoso de
save_preview, PATH_MAX4096 de Linux, sufijo SHA+.json y codificación
surrogatepass; no se presume que un path privado mida512 bytes. Se preservan
las cinco autorizaciones tipadas originales y los límites I118 de excepción383
y clase189. La lista tipada permitida tiene un path y la tupla tiene dos items.

El censo AST resuelve los321 métodos originales y sus helpers locales. Para24
roots se añadieron pruebas de slots concretos: LocalPreview17, AdapterBoundary3
y ReportBoundary4. El reporte no se digiere entero en sus aserciones: se
observan strings/flags, changed_fields y un set de tres claves. El adaptador
usa Mock y `LabClient.__new__`, sin SQL ni Docker nuevos.

### Pendiente real de CP03

| Grupo original | Roots que todavía requieren prueba de footprint por slot |
| --- | ---: |
| test_plane_reconciliation | 41 |
| test_profiles_quotas | 38 |
| test_relational_batch | 38 |
| test_offline_integration | 35 |
| test_register_comparison | 16 |
| test_register_compat | 11 |
| Total | 179 |

El censo lexical no prueba los valores. Se registran tres hipótesis de bosques
finitos como **NOT_ADMITTED**, con `premises_verified=false`: que una cuenta
propuesta quepa no demuestra sus premisas. Falta derivar por productor y slot
los nodos, strings escapados, base64/hex, copias anidadas, cardinalidad de sets,
tipos y profundidad. No se declara CP03 resuelto por una cota supuesta.

## Fuentes candidatas y modificaciones explícitas

La revisión `I119-CANDIDATE-02` deriva de la implementación de selectores
original, que permanece intacta. Materializa grupos v2 y registros Y v1 sin
fusionar objetos físicos O; mantiene los O completos en retained/call/link. Cada
nuevo witness conserva sus unidades originales y añade cuatro. No hay índice
global adicional ni descuentos o resets. Conserva la cota de diseño I117:
333.109 referencias y sidecar30.996.862 bytes; los cuatro números propuestos por
I115 son defaults sin aplicar en un namespace separado.

Las filas normalizadas preflightan tamaño y coste antes de publicar su cambio;
contador y referencia comparten lock. Se serializa la emisión a PageSink con
otro lock. **Esto no demuestra la atomicidad correlacionada de los30 sitios**:
owner/context/frame/event/page heredados siguen pendientes de revisión y de
componentes futuros. El certificado exige esa propiedad y actualmente la niega.

Se detectó además un problema independiente del layout: BaseRecorder.emit
intentaba capturar parámetros subTest de unitarios fuera del inventario causal
118 (por ejemplo `size`, `file`, `label`), rechazados por su esquema cerrado.
La candidata restringe esa anotación causal al inventario118. Se conservan
aserciones, operandos originales, resultados y test_frame_id de321 roots. Esta
ampliación explícita del diseño I117 está en el contrato; no es un cambio
silencioso ni una omisión de assertions.

MemberReader y SideWriter emplean caps explícitos (sidecar34MiB, página2MiB,
resto revisado), incluido el parser. InputReader conserva file16MiB,
unique128MiB y read256MiB. Las fuentes activas y sus cuotas no se modifican.

## CP07: vinculación actual y presupuesto concreto

Registro:478 inputs previos (477 heredados + documento CP03), cinco fuentes
candidatas y contrato. Certificado:485 bindings, sin su propio hash.
Manifiesto de componentes:8 bindings (cinco fuentes, registro, contrato,
certificado). La unión conocida tiene487 archivos y87.651.290 bytes.

La futura autoridad tendrá exactamente490 capture_inputs: esos487 más los tres
outputs de componentes aún ausentes. La autoridad es el archivo491 de la unión
leída; no se incluye a sí misma en capture_inputs. No se crean autoridad,
destino ni outputs de componentes.

El nuevo protocolo versionado lee una vez la unión en BEFORE y genera una vista
explícita PhaseBytes para cruces puros. Targets y LateBindings siguen usando el
mismo Reader físico. AFTER relee físicamente la unión, y finish la verifica una
tercera vez sobre el mismo ledger. No se presenta una consulta a PhaseBytes como
lectura fresca, ni se reinicia el Reader.

Los cuatro metadatos futuros tienen esquemas cerrados y JSON minificado, con un
newline opcional. Sus hashes se modelan por anchura64, **no por valor conocido**.
Las cotas incluyen autoridad54.618, raw327, review417 y seal1.390 bytes: total
56.752. Source bindings del seal son exactamente los8 del manifiesto. Hay
comprobaciones de revisión, hash y tipos antes de cualquier import del runner.

```
U_known = 87.651.290
F_future <= 56.752
worker <= 3*(U_known+F_future)+4.852.460 = 267.976.586
límite InputReader = 268.435.456
margen = 458.870 bytes
```

El término4.852.460 hereda la cota I96 de targets/late. `worker.targets` y
`BaseRecorder.bind_causal_target` mantienen AST idéntico; LateBindings conserva
la implementación heredada. Los nuevos cruces consumen PhaseBytes: X adicional
fresco es0. Las comprobaciones stdlib directas mantienen su ámbito heredado;
no se afirman inexistentes ni se disfrazan de lecturas gratuitas de Reader.
Launcher necesita como máximo las tres pasadas de la unión. El certificado usa
la cota conservadora U<=87.700.000 y F<=70.000: total268.162.460, también cabe.
El top metadata model mide482.509 frente a524.288, con una clave de autoridad
extra conservadora y los32 manifiestos de página; no añade campos de salida.

El grafo de hashes es acíclico: fuentes/prueba → contrato/registro → certificado
→ manifiesto → futuros raw/review/seal → autoridad final. El informe de binding
y sello I119 son consumidores documentales externos a ese conjunto runtime;
introducirlos en capture_inputs exige recalcular la prueba. Ningún self-hash ni
hash futuro se sustituye por un valor ficticio válido para la admisión.

**CP07 de fuentes actuales y capacidad numérica: verificado documentalmente.**
**CP07 de admisión completa: pendiente** de hashes reales y evidencia aceptada
futuros. El certificado conserva `DRAFT_NOT_ADMITTED`, CP03 false, CP07 de
admisión false, atomicidad false y `proposal_enabled=false`. El worker exige
`SOURCE_CAPACITY_VERIFIED` y los tres gates true antes de READY/RELEASE/import.

## Verificación y continuidad

`python3 docs/validation/D5-I119-audit.py` es una auditoría documental de solo
lectura. Recalcula tamaños simbólicos, hashes y presupuesto; inspecciona AST
sin importar componentes ni producto; comprueba borradores, ausencias y el
sello. PASS significa coherencia documental, nunca PASS funcional ni CP03
global. Los45 archivos no versionados previos y los477 inputs heredados se
preservan byte a byte. Ningún archivo versionado/staged cambia.

Para habilitar PJC115-R2 faltan la prueba de los179 roots, revisión completa de
atomicidad correlacionada y la evidencia de componentes/admisión bajo su
alcance propio. No se solicita ni presume una ejecución funcional. Los paquetes
I86/I89/I92 siguen INVALID_CAPTURE; no se reanudan ni combinan.

P0 conserva83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1), D1–D4 e I1–I20/A52 conservan
su aceptación. D5/H07/G01–G07 y GI globales siguen abiertos; las obligaciones
humanas/reales GI06/12/18/24/30/36/42 siguen pendientes. Sin proveedores reales,
credenciales, consumo, reservas, activación, promoción, despliegue ni D6. No se
inspecciona ni limpia dev/run_data/D4. Sin producto, cuotas activas, commit o push.
