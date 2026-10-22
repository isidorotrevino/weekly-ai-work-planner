# D5 I27 — contrato de conciliación Plane sintética

Fecha: 2026-10-22. **PREPARADO PARA REVISIÓN; sin implementación nueva.**
Cobertura propuesta: GI15/GI16/GI17 de [I23](D5-I23-GLOBAL-INTEGRATION-DESIGN.md).
[Matriz PC01–PC32](D5-I27-PLANE-RECONCILIATION-REVIEW.md) ·
[Comprobaciones documentales](../validation/D5-I27-design-review.json).
D5 global y G01–G07 siguen abiertos; el
[hito aceptado I1–I20](D5-LOCAL-SYNTHETIC-approved.md) conserva su perímetro.

English: proposed in-memory synthetic Plane creation/reconciliation protocol with
stable correlation, immutable reviewed payloads, bounded explicit retries and
historical effect recovery independent of current approval. No HTTP, real Plane
capability claim, filesystem recovery, SQL, D2 writes, activation or deployment.

## Decisiones y alcance propuesto

| ID | Decisión expresa | Consecuencia |
|---|---|---|
| A64 | Priorizar conciliación sintética Plane GI15–GI17 | Contrato y matriz para revisión antes de implementar |
| A65 | Clave estable por binding explícito de instancia/proyecto/tarea D2; todos los intentos comparten clave y el doble exige unicidad atómica | Ni paquete nuevo ni cambio de texto autorizan otra creación para la misma identidad |
| A66 | Con D2 cambiado o aprobación revocada, permitir solo conciliación histórica | Registrar efecto observado y conflicto de vigencia; sin actualizar, compensar o reenviar automáticamente |

A64–A66 no aprueban todavía este contrato completo ni su implementación. Se propone
un módulo y doble nuevos, aislados de `offline.py` e `incremental_fixture.py`, con
biblioteca estándar Python, memoria volátil, reloj lógico y barreras de prueba.
Solo fixtures públicas sintéticas. No HTTP/SDK/CLI, SQL, Docker, filesystem de
capturas, procesos hijos, selección de referencia D5 o efecto persistente D2.

I24 solo modifica un destino preexistente explícito y no crea ni concilia envíos
inciertos. Este contrato añade **creación de una proyección TASK de fixture** y
actualización condicional de un destino ya ligado por este protocolo. No adopta
objetos encontrados por título o similitud ni traduce estados Plane a ejecución.
Requisitos/épicas, relaciones, lotes, perfiles nuevos y cuotas quedan fuera.

## Identidad, capacidades y manifiesto

Binding cerrado/versionado: modo SYNTHETIC_ONLY, binding_id UUID, proyecto y tarea
D2 UUID explícitos, instancia `SYNTHETIC_PLANE`, workspace/proyecto remotos UUID,
versión de política y ficha de capacidades de fixture. El registro local impone
unicidad de tarea por ámbito y de destino remoto; cambiar binding_id no permite
sortearla. No aceptar URL, tokens, configuración `.env` o nombres para descubrir
un destino. Un cambio de ámbito no reutiliza clave ni adopta automáticamente.

La clave de creación es el hash canónico de schema + instancia + workspace/proyecto
remotos + proyecto/tarea D2. El binding fija esa tupla y su clave: no depende del
texto, fecha, intento ni revisión del paquete. No es una credencial. El doble
aplica unicidad **atómica** sobre ella, conservando relación con ID remoto, hash
original de creación y recibo del efecto. La capacidad se declara en un fixture
cerrado como demostración del modelo, nunca como capacidad probada de Plane.
Falta/cambio de versión o ausencia de capacidad exigida bloquea envío.

Manifiesto inmutable/hash: schema/modo, operación CREATE o UPDATE, binding y clave,
snapshot TASK completo y versión D2 sintética, whitelist `{name, description}`,
proyección/hash, ficha/versiones de capacidades y política, y para UPDATE destino,
versión remota de campos sincronizados y hash base. Solo se revisa el manifiesto
completo mediante decisión propia ACCEPT/REJECT con versión y razón; una revisión
de fuente, aplicación D2 o publicación Git no sirve como aprobación remota.

El ledger separado registra command_id + request_hash, paquete/review_version,
intentos, ticket de envío, respuesta/observaciones, recibo y versiones CAS locales.
El mismo command_id con otro request falla; replay devuelve hechos históricos y
nunca vuelve a enviar. Otra identidad de comando no evade una creación incierta
o confirmada para esa clave. Preparar/revisar no envía ni reserva capacidad D3.

## Protocolo y fronteras

1. Preparar y revisar fija bytes/hash de payload y versiones. Antes de enviar se
   revalidan binding, snapshot D2, aprobación y capacidades bajo lock local corto.
   Se registra intento PREPARED y se consume una sola vez el ticket DISPATCHED;
   solo un emisor puede consumirlo. Otro emisor concilia o recibe conflicto.
2. Se libera el lock antes de invocar el doble. El intento ya DISPATCHED se trata
   como potencialmente enviado aunque se pierda control antes de la llamada.
   Nunca se conserva un lock de dominio durante una llamada al proveedor/doble.
3. El doble crea atómicamente por clave o actualiza con precondición atómica sobre
   versión **monótona de campos sincronizados** y hash base. Un ciclo A→B→A cambia
   versión y bloquea el UPDATE antiguo. Campos ajenos se preservan; no se reemplaza
   el objeto completo. GET+PATCH sin condición no es una alternativa permitida.
4. Se publica respuesta/observación bajo CAS de ledger. Después del envío se
   revalida también D2/revisión: revocar durante la llamada no deshace el efecto
   remoto. Se conserva ese hecho con vigencia obsoleta, nunca se afirma rollback.
5. Una acción de conciliación explícita consulta exclusivamente identidad/ticket/
   clave fijados; no contiene payload de actualización. Se registran observaciones
   vinculadas al intento. Dos conciliadores usan CAS; uno confirma y el otro relee
   o recibe conflicto sin duplicar recibo. No se selecciona evidencia por fecha.

Crear con la misma clave y payload original recupera el mismo ID/recibo, aunque
posteriormente hayan cambiado sus campos. Otro payload no puede crear un segundo
objeto: devuelve conflicto de clave/contenido. Encontrar un ID por clave no basta
para probar que el payload del intento se aplicó: se exige recibo/hash de creación
o actualización del ticket. Un elemento modificado después se conserva tal como
está; su lectura actual no autoriza a restaurar el payload aprobado antiguo.

## Resultado remoto y vigencia son ejes distintos

| Evidencia del intento | Resultado remoto | Acción permitida |
|---|---|---|
| Aún sin envío | NOT_SENT | Envío solo tras todas las guardas y aprobación vigente |
| Enviado sin respuesta concluyente, timeout o respuesta inválida | UNKNOWN | Solo conciliación; ningún retry de escritura por observar cero resultados |
| Un efecto exacto probado por identidad, ticket y hash | EFFECT_CONFIRMED | Recibo histórico; comprobar por separado vigencia y estado remoto actual |
| Rechazo concluyente de no efecto por el doble | REJECTED_NO_EFFECT | Nuevo intento explícito acotado, solo con guardas vigentes |
| Múltiples coincidencias, identidad/hash incompatibles | CONFLICT | Bloqueo y evidencia; sin escoger primera/última ni crear/adoptar otro destino |

Vigencia se deriva de versiones actuales: CURRENT o STALE_LOCAL / STALE_REVIEW /
STALE_BINDING / STALE_CAPABILITY (pueden coexistir). CONFIRMED + STALE no se
convierte en éxito vigente ni en ausencia de efecto. A66 permite conciliar el
intento histórico aunque cambie D2 o se revoque ACCEPT; esa lectura no consume una
nueva autorización de escritura. El recibo original sigue inmutable y las nuevas
observaciones de conflicto se añaden al ledger.

Cualquier CREATE o UPDATE incierto bloquea nuevas escrituras del mismo binding,
aunque se prepare otro paquete/comando; se permiten solo lecturas y conciliación.
Crear un paquete nuevo no elimina UNKNOWN anterior. Primero se concilia. Si se
confirma creación previa, se conserva el destino y cualquier cambio requiere
**nuevo UPDATE revisado**, nueva base remota y capacidades/guardas vigentes. Si el
remoto fue editado, esa diferencia exige revisión explícita y base nueva; D2
sigue siendo autoridad, pero no concede una sobrescritura bajo aprobación vieja.
Un destino borrado/desaparecido no se recrea por silencio ni por GET vacío.

## Lecturas, errores y presupuesto

La fixture distingue búsqueda eventual (cero/uno/múltiples) y recibo concluyente
por ticket/clave. Cero resultados eventuales, incluso repetidos, deja UNKNOWN;
ninguna espera temporal prueba ausencia. Una coincidencia sin evidencia exacta
produce diagnóstico incierto o conflicto, nunca confirmación por similitud.
Tampoco una lectura fuerte vacía permite reenviar mientras el ticket pueda seguir
en vuelo. Este primer contrato no añade una operación remota de cancelación ni
una prueba de no efecto basada únicamente en ausencia.

Timeout, desconexión simulada, error sin garantía de no efecto o respuesta parcial
tras envío → UNKNOWN. El doble solo puede emitir REJECTED_NO_EFFECT si su rama
atómica acredita que no produjo efecto. Un 429 de fixture permite retry únicamente
con esa garantía; un 429 ambiguo queda UNKNOWN. Denegación o precondición rechazada
son negativas concluyentes solo bajo el contrato cerrado del doble. No se infieren
estas garantías de códigos HTTP reales. ACK local solo acredita registro local.

Propuesta acotada: tres intentos de escritura por paquete aprobado, seis consultas
de conciliación por comando, máximo 64 bindings y 128 comandos por ejecución,
manifiesto ≤64 KiB y texto ≤8.192 caracteres por campo. Límites del laboratorio,
no cuotas Plane. Cada llamada hace como máximo un intento o una consulta; no
polling, sleeps, daemon, retry automático, truncamiento o fallback de pago.

Retry explícito tras REJECTED_NO_EFFECT consume presupuesto, conserva clave y
payload, crea otro attempt_id y vuelve a comprobar todas las versiones. Un 429
con retry_after válido fija un tick mínimo del reloj lógico confiable del harness;
antes de ese tick bloquea. Falta/valor inválido bloquea retry hasta nueva decisión
revisada, sin interpretar cero como ilimitado. Cambiar texto exige nuevo paquete;
no se renueva presupuesto fabricando comandos para el mismo paquete. No existen
reservas/cuotas de proveedores D3 nuevas.

## Recuperación propuesta y límites

El ledger en memoria permite simular pérdida de **respuesta** y concurrencia entre
hilos/barreras del mismo proceso. Tras perder toda la memoria no existe prueba
durable para recuperar, enviar o conciliar: queda fuera del contrato, sin afirmar
recuperación entre procesos. Una futura persistencia del outbox, antes de HTTP,
requerirá diseño y autorización propios; no se reutiliza el almacén de captura
I26 como ledger de envíos ni se mezclan sus hashes/cursor con este protocolo.

Los hooks de fallo son controles del harness confiable, nunca instrucciones de
fuente o campos arbitrarios de payload. Errores/recibos públicos contienen códigos,
IDs sintéticos y hashes permitidos; no cuerpos remotos crudos, texto fuente,
URLs/credenciales ni trazas. La inspección privada de fixtures contiene su texto.
El modelo no aísla a un caller Python hostil ni acredita permisos reales.

GI15–GI17 recibirían solo evidencia acotada de modelo si se aprueba e implementa.
No acreditarían GI18 real, GI38/GI39/GI40 integrados, G03 completo o cierre D5.
Se conservarán I24/I26 y las campañas/hashes históricos sin reescribirlos. No hay
migración, promoción, despliegue ni D6. Aprobar/publicar I27 tampoco equivale a
implementar: la puerta propuesta es aprobar contrato y autorizar PC01–PC32 en
memoria, con regresiones Python identificadas por separado y evidencia nueva.
