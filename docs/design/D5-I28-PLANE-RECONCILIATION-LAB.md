# D5 I28 — laboratorio de conciliación Plane sintética

Fecha: 2026-10-22. Implementa [I27](D5-I27-PLANE-RECONCILIATION-DESIGN.md) y
[PC01–PC32](D5-I27-PLANE-RECONCILIATION-REVIEW.md), solo para GI15/GI16/GI17
como modelo en memoria. [Resultados propios](../validation/D5-I28-results.md).
**D5 global y G01–G07 abiertos; el hito aceptado I1–I20 permanece separado.**

English: isolated volatile Plane fixture and reviewed command ledger, with atomic
creation-key uniqueness, conditional updates, bounded explicit retries and
historical reconciliation after lost responses. No real Plane client/capability
proof, durable restart, SQL, persistent D2 changes, activation or deployment.

## Autoridad y ejecución

D5-A67: el usuario aprueba I27 y autoriza implementar/validar PC01–PC32 con fixtures
sintéticas en memoria, conservando A64–A66, sin HTTP, persistencia D2, activación,
promoción, despliegue ni D6. I27 publicado y verificado en `main`:
`26559404a7b8853973ab9c29e021a542710fae4a`.

Desde la raíz, Python 3 con biblioteca estándar:

```bash
python3 -m testing.D5.demo_plane_reconciliation
python3 -m unittest discover -s testing/D5 -p test_plane_reconciliation.py -v
python3 -m testing.D5.run_plane_lab
```

La demo crea solo objetos en memoria y emite estados/contadores saneados. Ejercita
CREATE con respuesta perdida, cambio local, conciliación histórica obsoleta,
UPDATE aprobado y replay que conserva una edición remota posterior. No recibe
URL, rutas, credenciales o configuración de servicio. Todo estado desaparece al
salir; el stdout es evidencia de fixture, no acuse real de un proveedor.

La suite nueva usa hilos propios, reloj lógico y barreras/Event de prueba; no
crea carpetas de datos, hijos de proceso, red, SQL o Docker. El runner completo
**también reejecuta I26**: esa regresión conserva sus requisitos Linux/fsync/flock,
crea/elimina sus raíces temporales y sus propios hijos de fallo controlado. No
atribuir su recuperación filesystem a I28. El runner emite JSON y no guarda
informe por sí mismo; la redirección de stdout es decisión del operador.

## APIs y datos

[`plane_fixture.py`](../../source_ingest/plane_fixture.py) es nuevo y no cambia
`offline.py`, parsers ni el almacén/harness de captura I26.

| Entrada | Función y frontera |
|---|---|
| `binding`, `task`, `capabilities` | Construyen fixtures cerradas; validación al registrar/usar. TASK/BACKLOG sintética, IDs y proyectos explícitos |
| `PlaneFixture` | Doble en memoria: unicidad atómica por clave, recibos por ticket, versión monótona de campos proyectados y cambios controlados del harness |
| `ReconciliationLab.bind` | Registro explícito de binding/tarea; una tarea no recibe otra identidad cambiando binding_id |
| `prepare` / `manifest` | Manifiesto inmutable direccionado por hash; inspection privada incluye texto completo de fixture |
| `review` | ACCEPT/REJECT propios con razón y CAS de versión, separados de cualquier revisión D5 previa |
| `dispatch` | Un intento explícito; registra/consume ticket bajo lock corto, suelta lock para llamar al doble y publica resultado bajo CAS |
| `reconcile` | Una consulta explícita por identidad/ticket/hash; no contiene payload de escritura y exige versión local esperada |
| `command` | Vista saneada del recibo histórico, estado actual, vigencia derivada y conflicto; nunca reenvía |
| `inspect_command` | Copia privada del ledger y eventos; no autoridad de publicación ni mutación del modelo |
| `summary` | Contadores y límites de autoridad: sin efectos reales, D2 persistente o cierre |

CREATE usa la clave estable de la tupla instancia/workspace/proyecto remoto y
proyecto/tarea D2. No incluye texto, paquete, fecha o comando. El doble impone
unicidad bajo lock; repetir el payload original recupera ID/recibo sin restaurar
campos editados después. Otro payload no crea un segundo destino. La API local
exige conciliar antes de cualquier nuevo envío incierto del mismo binding.

UPDATE requiere destino ligado por este protocolo, manifiesto/revisión nuevos,
versión y hash base remotos. La versión aumenta con cada edición de campos
sincronizados, incluso A→B→A; los campos ajenos se preservan. No existe adopción
por nombre, traducción de workflow remoto, requisitos/épicas/relaciones o batch.

## Incertidumbre, vigencia y conflictos

Los estados NOT_SENT/UNKNOWN/EFFECT_CONFIRMED/REJECTED_NO_EFFECT/CONFLICT se
mantienen separados de CURRENT/STALE_LOCAL/STALE_REVIEW/STALE_BINDING/
STALE_CAPABILITY. Cambiar o revocar durante una llamada no revierte un efecto.
Se permite conciliar el envío histórico A66; el recibo confirmado sigue ligado
al hash/ticket exactos y no autoriza otra escritura. Replay no restaura texto.

La fixture separa resultado eventual vacío, coincidencia sin prueba y recibo
exacto. Cero resultados —incluso lectura fuerte con intento aún en vuelo— no
prueba ausencia. Múltiples resultados, identidad/prueba incompatible, destino
compartido o desaparecido dejan un bloqueo de identidad persistente. Una consulta
posterior puede acreditar un hecho histórico, pero no borra ese bloqueo ni el
historial de observaciones. No se proporciona resolución/adopción automática de
esos conflictos en este corte. Una edición remota legítima exige paquete UPDATE
nuevo con base/revisión explícitas; nunca se reusa la aprobación anterior.

La publicación de respuesta y conciliación compiten por CAS local. Si una consulta
confirma otro estado mientras el envío está en vuelo, la publicación puede devolver
CONFLICT_LEDGER; el efecto remoto no se presume perdido. Otra consulta explícita
recupera el ticket exacto. Los contadores consumen las consultas realizadas aunque
pierdan CAS. No hay locks de dominio durante callbacks de envío/consulta.

Timeout, cuerpo inválido, ACK local y 429 ambiguo conservan UNKNOWN. Solo la rama
atómica de fixture con garantía de no efecto devuelve REJECTED_NO_EFFECT. No se
infieren estas garantías de códigos HTTP reales. Reintentar exige acción expresa,
misma clave/payload, guardas aún vigentes, presupuesto y, para 429 concluyente,
tick mínimo válido. Falta/dato inválido bloquea. Un conflicto de precondición o
clave no admite retry del paquete; requiere revisión/base nuevas donde proceda.

Hay un comando por manifiesto, con intentos acotados por paquete; otro command_id
no reinicia presupuesto. Tres intentos, seis consultas por comando, 64 bindings,
128 comandos, manifiesto ≤64 KiB y campos de texto ≤8.192 caracteres. Los límites
son de fixture. Reloj lógico monótono del harness; sin sleeps, polling, daemon,
retry automático, truncamiento, cuota/reserva D3 nueva o fallback de pago.

## Evidencia y límites

41 tests nuevos cubren las 32 filas de matriz, más 116 regresiones Python
identificadas: 157 distintos, cero fallos/errores/omisiones. Se ejercitan carreras
reales en hilos para ticket local, creación atómica en el doble y CAS de consultas;
otra prueba publica una consulta mientras el envío está en vuelo. Los callbacks
permiten editar D2 de fixture desde otro hilo durante envío y consulta para
comprobar que el lock local se liberó. Los ocho hilos propios terminan.

Se alcanzan realmente los límites de 64 bindings y 128 comandos; se bloquea el
siguiente sin truncar. Tres intentos y seis consultas se agotan en fixtures.
El límite de bytes se ejercita con texto UTF-8 multibyte válido; existe además
una prueba de presupuesto reducido para un rechazo temprano. No es benchmark.

El ledger es volátil: el doble rechaza adjuntar un segundo lab sobre el mismo
objeto vivo para evitar fingir restauración de autoridad. Perder ambos objetos
no deja prueba durable ni forma de recuperar un servicio externo. No se prueba
reinicio/pérdida de proceso I28, energía/disco, HTTP, autenticación, aislamiento
ante caller Python hostil o capacidades reales de Plane. Los hooks y mutaciones
privadas son controles del harness confiable, no instrucciones de documentos.

Errores/vistas/recibos publicados evitan texto crudo de fixture. `manifest`,
`read` e inspecciones privadas sí contienen texto: no son salida de publicación.
La ficha sintética de unicidad/condición no acredita GI18; A58 sigue bloqueando
escrituras remotas hasta probar capacidades en la versión/edición objetivo.

Con I28, 25 de 35 criterios sintéticos tienen evidencia acotada (22 anteriores y
GI15–GI17 nuevos). Quedan diez S y siete R pendientes. GI38/GI39/GI40 generales
y todas las brechas G01–G07 siguen abiertos. No se reescriben hashes/manifiestos
ni se reejecutan SQL/D2/D3/D4; la evidencia de esas campañas permanece histórica.
Sin proveedores reales, promoción, despliegue ni D6.
