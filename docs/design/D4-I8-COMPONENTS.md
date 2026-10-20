# D4 I8.1 — componentes de generalización y verificación

Fecha: 2026-10-20. A13–A15 aprobadas en [revisión I8](D4-I8-GENERALIZATION-REVIEW.md).
**D4 abierto. Primer corte de componentes; integración SQL/HTTPS/Compose pendiente.**
No se afirma que V23 admita ahora varios checkpoints o cuentas. Sus guardas siguen
rechazándolo. La propuesta V24 aún no existe como migración ejecutable.

## Cálculo multidimensional y cadena lineal

`worker-runtime/.../CheckpointAccounting.java` es un cálculo puro de propuestas.
Admite hasta 32 pasos y 8 cuentas con costes exactos, dimensión, ventana y vector
original. Rechaza IDs duplicados, costes incompletos, negativos o superiores al
vector original, y produce hashes deterministas del manifiesto y la liquidación.
No asigna generaciones, no escribe journal, no autoriza continuidad ni evidencia.

Cada invocación recibe de la futura frontera de confianza el manifiesto congelado,
identidad D2, cabeza vigente, contador real de intentos, journal y cierre ya
verificado. Esos objetos Java no demuestran por sí solos que haya una firma,
lease viva, prueba de parada o autorización: el adaptador debe comprobarlas y
volver a leer estado/journal bajo los locks antes de efectuar una transacción.
Una llamada directa desde datos del worker sería un uso inválido del componente.

La cabeza debe coincidir con el hash del padre exacto. El sucesor conserva
operación/recurso/worker, tiene otro intento y la siguiente generación real D2.
El contador de entrada procede de D2; no se crea otro contador de autoridad.
Un checkpoint sin progreso, terminal, con padre antiguo, cambios de manifiesto o
sin presupuesto para continuar se rechaza. Todos los pasos APPLIED heredados
conservan intento, generación y hash originales. El cierre nuevo debe describir
exactamente el sufijo autorizado: prefijo APPLIED nuevo seguido de ABSENT, nunca
UNKNOWN ni APPLIED después de ABSENT. La aceptación final exige completar todos.

El consumo anterior del journal debe coincidir, por cuenta, con los pasos
heredados. El cálculo obtiene acumulado, delta CONSUME y remanente RELEASE; verifica
el vector completo antes de devolverlo. Cada intento debe tener comprometido el
vector original completo y todas sus ventanas vigentes. Un resultado es solo una
propuesta inmutable; no certifica que SQL la haya aplicado atómicamente.

| Paso | Cuenta A: tokens | Cuenta B: peticiones |
|---|---:|---:|
| 1 | 4 | 1 |
| 2 | 3 | 2 |
| 3 | 3 | 3 |
| Vector original | 10 | 6 |

La prueba compone dos checkpoints y tres intentos: deltas (4,1), (3,2), (3,3),
consumo final (10,6). Otra prueba usa el receptor durable real del componente,
aplica un paso por generación, cierra y reabre el diario después de cada paso.
Los sellos anteriores permanecen idénticos y el prefijo conserva su generación.
No ejecuta D2 CLAIM ni liquida una reserva SQL: eso pertenece a la campaña posterior.

## Artefactos, Git y restauración local

`testing/D4/verifiers.py` es un componente local Python, separado del servicio
Java HTTPS. No registra PASS ni tiene SQL. El manifiesto esperado y la base Git
proceden de política confiable, nunca del candidato. Devuelve método, hash del
manifiesto, número de archivos y bytes observados; no devuelve aceptación.

El verificador de archivos compara el conjunto completo, tamaño, SHA-256 y modo
(ejecutable o no). Usa descriptores relativos y apertura sin seguir symlinks;
rechaza rutas ambiguas, .git, archivos extra/faltantes, directorios extra, enlaces
simbólicos/duros y dispositivos/FIFO. Límite: 64 archivos, 64 KiB por archivo y
4 MiB total. Detecta cambios durante la lectura; requiere además observación de
parada/frescura independiente para que un escritor posterior no invalide el estado.
No promete una instantánea atómica frente a escritores concurrentes.

Git trabaja únicamente en un repositorio bare nuevo controlado por el verificador
para fixtures. No importa directorios .git, bundles ni configuración del worker.
Exige OIDs completos de commits, ancestralidad de la base aprobada y árbol completo
con hashes SHA-256 de blobs y modos 100644/100755. Rechaza symlinks/submódulos,
configuración cambiada, alternates, grafts, shallow y replace. Sin red, shell,
hooks, filtros ni ejecución de archivos candidatos. Cada comando tiene timeout
de cinco segundos y salida limitada a 2 MiB. Los OIDs SHA-1 de esta fixture son
identificadores Git; la comprobación de contenido usa SHA-256 y no eleva el OID a
prueba de aceptación. No se implementa aún importación segura de objetos candidatos.

La restauración local vuelve a comprobar el árbol completo contra el manifiesto
anterior. No ejecuta `git reset`, scripts ni compensaciones. No toca recibos APPLIED,
consumo o fencing. Este componente observa el resultado restaurado: la preparación
de la fixture realiza la escritura y la futura integración debe aportar parada,
identidad, frescura y política. No acredita ausencia de efectos externos.

## Reproducción y evidencia

```bash
python3 -m unittest discover -s testing/D4 -p test_verifiers.py -v
D4_OFFLINE=1 D4_TESTS=CheckpointAccountingTest,ProcessRuntimeTest,CheckpointStoreTest,PollingStoreTest bash testing/D4/run-delivery-tests.sh
```

El segundo comando usa imágenes y caché locales; se pueden fijar D4_PG_IMAGE y
D4_MAVEN_IMAGE por digest como registra la [evidencia I8.1](../validation/D4-I8-COMPONENTS-results.json).
El harness Docker copia fuentes y conserva los targets e informes anteriores.
Resultado final: 26 pruebas de contabilidad/cadena, 25 verificadores locales,
55 de regresión D4 y 332 históricas D3/D2, sin fallos, errores ni omisiones.
Las pruebas locales Git no se denominan Compose ni sustituyen D2/D3.

## Pendiente ya autorizado

1. V24 propuesta con manifiesto v2 congelado antes de primer CLAIM, historia/cabeza
   sin ramas, autorizaciones/enlaces consumidos una vez y liquidación multicuentas
   atómica. Preservar v1, locks y guardas de lease/UNKNOWN.
2. Incorporar cabeza/pruebas v2 a observación, snapshot/readset, CAS y despacho;
   revalidar mapping, pools, cuentas, dependencias y prioridad por camino bloqueante.
3. Adaptar grants, fixture/cursor, callbacks vectoriales y verificador independiente;
   enlazar los resultados locales con identidad/frescura/parada/cierres sin confiar
   en hashes declarados por el worker. Persistir procedencia antes de admitir PASS.
4. Campaña Compose de tres pasos, dos cuentas, dos checkpoints y tres intentos;
   verificar reserva única, TOP_UP (10,6) en cada continuación, consumo final (10,6),
   rearme A12 en cada pausa, fencing, negativos y upgrade vivo.

Estos pendientes no requieren volver a consultar A13–A15. No se habilitan por un
booleano de prueba ni quitando UNIQUE o la guarda de una cuenta en V19. D4 no se
cierra y no se promueven migraciones ni despliegan servicios.

Integración posterior: [I8.2](D4-I8-INTEGRATION.md) implementa el puente SQL/HTTPS
y la campaña Compose acotada. Los límites y resultados anteriores de I8.1 son históricos.
