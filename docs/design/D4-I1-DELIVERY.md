# D4 I1 — entrega durable sobre los contratos D3

Fecha: 2026-10-19. **Incremento de persistencia implementado y validado con Docker.
D4 abierto; vertical HTTPS/procesos todavía pendiente.**

## Resultado y frontera

[V16 propuesta](../../migrations-d4-proposed/V16__durable_worker_delivery.sql) añade
un catálogo autorizado de workers, recibos, entregas y ACK inmutables. Reutiliza
mapping/CLAIM/lease/reserva/generación reales D3/D2 y no altera V1–V15.

| Entrada del control plane | Garantía comprobada |
|---|---|
| `d4.deliver(cid, principal_worker, req)` | Solo recurso del worker autorizado; CLAIM y entrega/recibo atómicos. Recupera una entrega confirmada tras respuesta perdida, también con nuevo comando de polling, sin duplicar intento/reserva |
| `d4.ack(...)` | Confirma recepción de entrega propia; ni START ni renovación ni liberación. Repeticiones no duplican ACK |
| `d4.current_assignment(principal_worker)` | Recupera asignación propia con estado y vencimiento actuales. El resultado es informativo, nunca autorización de spawn/efecto |
| `d4.worker_execution(...)` | Solo START/HEARTBEAT/CALLBACK; reconstruye identidad desde dispatch persistido. No admite VERIFY, evidencia, contabilidad libre ni cambio de generación en payload |

`principal_worker` debe proceder del adaptador mTLS de confianza. El rol que tiene
EXECUTE es el control plane; no se entrega SQL al worker. Las pruebas JDBC llaman
este límite con principales sintéticos: **no demuestran autenticación mTLS**.
El catálogo es autorización de acceso; no es un nuevo catálogo de cuota ni una
autoalta de capacidades. Su sincronización con presencia/certificados sigue en I2.

Mismo ID, principal y JSONB completo devuelve recibo; otro contenido/principal
produce conflicto. Revocación del catálogo se comprueba incluso antes de replay.
El lock de la fila del catálogo conserva autorización durante el comando. Orden
global 742001→742002, transacciones READ COMMITTED, sin llamadas externas bajo locks.

Todos los resultados de comandos llevan `receipt_only=true`. Un replay START puede
mostrar éxito histórico con lease vencida: no la renueva ni autoriza otro proceso.
El futuro supervisor/receptor debe comprobar autoridad vigente; V16 no emite grants.

El upgrade mantiene intentos V15 y diario sin adoptarlos silenciosamente como
entregas D4. Una operación ya RUNNING conserva lease/compromiso y bloquea otro
CLAIM. La adaptación de una ejecución anterior exige reconciliación independiente.

## Reproducción y evidencia

Desde la raíz, con imágenes y caché Maven ya preparadas:

```bash
D4_OFFLINE=1 bash testing/D4/run-delivery-tests.sh
```

`D4_MAVEN_CACHE`, `D4_PG_IMAGE` y `D4_MAVEN_IMAGE` permiten fijar caché e imágenes.
Sin `D4_OFFLINE=1`, un contenedor de bootstrap sin credenciales/DB puede descargar
dependencias y compilar; después las pruebas se ejecutan offline en red interna.
Imágenes siempre locales con `--pull never`; bootstrap ausente no se oculta.
Se admiten referencias por digest; se registran IDs/digests realmente observados.

El runner copia fuentes a `work/d4/<run-id>/source`, añade el módulo de pruebas
solo al reactor copiado y preserva targets/informes D3 originales. Usa PostgreSQL
desechable con SCRAM, secreto sintético local privado y cero puertos publicados.
No cambia autenticación histórica D2 ni crea credenciales reales. Recoge logs y
elimina únicamente sus dos contenedores y su red; tmpfs elimina la DB de esta
batería de persistencia. Este harness **no prueba reinicios con volúmenes durables**.

[Resultados portables](../validation/D4-I1-results.json): 14 pruebas D4, cero
fallos/errores/omisiones. Instala V1–V16 y prueba upgrade V15→V16 con plan, intento
RUNNING, reserva/diario/lease conservados, dos conexiones, rollback, ownership,
permisos mínimos de un rol NOLOGIN sintético, callback y consumo únicos, identidad
deshabilitada, replay antiguo y rechazo de bypass D2/D3. Un caso adelanta la lease
por SQL para verificar persistencia: no se presenta como expiración real de proceso.

La regresión exigida por CONTRIBUTING ejecutó el harness D2 sin cambios: 157 pruebas,
incluido su corpus SemVer dentro de una prueba; V1–V11 en sus bases históricas,
no 157 pruebas sobre V16. Se fijaron las imágenes por digest observado. Los informes
de cierre D2/D3 permanecen intactos; no se repitió toda la batería D3 en este incremento.

## Lo siguiente

Actualización posterior: [I2](D4-I2-HTTPS.md) ya entrega Spring Boot/HTTPS/mTLS y
LOGIN mínimo sintético. La lista siguiente conserva lo que estaba pendiente al
entregar I1; supervisor/receptor/Compose siguen pendientes.

Adaptador Spring Boot/HTTPS y mTLS, bootstrap con LOGIN de laboratorio mínimos,
polling y presencia, supervisor de procesos, receptor/grants/cierre durable,
verificador independiente, Compose y campaña D4-S01–S04 siguen pendientes.
Las 14 pruebas actuales son persistencia, no esas cuatro pruebas end-to-end.

Las decisiones A05/A06/A07 concretan la [propuesta de continuidad con efectos
parciales](D4-CHECKPOINT-CONTINUATION.md). Aún no se cambia el retry D3 ni se habilita
CANCELLED→READY. UNKNOWN y contradicciones siguen bloqueados, conforme A04.
No hay promoción de migraciones, despliegue, proveedor real ni aprobación de cierre D4.
