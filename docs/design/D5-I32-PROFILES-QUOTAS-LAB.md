# D5 I32 — laboratorio de perfiles y cuotas sintéticas

Fecha: 2026-10-22. Implementa [I31](D5-I31-PROFILES-QUOTAS-DESIGN.md) y
[PQ01–PQ34](D5-I31-PROFILES-QUOTAS-REVIEW.md), solo GI04/GI20/GI22 como modelo
en memoria. [Resultados propios](../validation/D5-I32-results.md).
**G01–G07 y D5 global abiertos; hito aceptado I1–I20 sin ampliación.**

English: isolated volatile versioned extraction and quota-evaluation fixtures.
Exact profile/policy/account/adapter/observation generations are bound to separate
reviews. All required dimensions/windows must be valid for one explicit account;
no conversion, quota consumption, reservation, real-provider authority or D3 change.

## Autoridad y ejecución

D5-A75: el usuario aprueba I31 y autoriza implementar/validar PQ01–PQ34 con fixtures
en memoria y parsers existentes sin cambios; sin SQL, HTTP, cambios D3, efectos
D2, consumo/reservas, activación, promoción, despliegue ni D6. I31 publicado y
verificado en `main`: `8e90a87cce7edbefc6c854a73ff1f60a20ae8485`.

Desde la raíz, Python 3 con biblioteca estándar:

```bash
python3 -m testing.D5.demo_profiles_quotas
python3 -m unittest discover -s testing/D5 -p test_profiles_quotas.py -v
python3 -m testing.D5.run_eligibility_lab
```

La demo construye un registro tabular sintético en memoria, exige revisiones
SOURCE y EVALUATION propias y evalúa dos dimensiones. Tras caducidad, el mismo
comando devuelve un recibo **histórico**, mientras otro comando revalida y devuelve
BLOCKED. Se imprimen estados/contadores sin contenido fuente o datos de cuenta.
No recibe rutas, URL, `.env`, credenciales o argumentos de proveedor; todo estado
se pierde al salir. Un resultado SIMULATED_ELIGIBLE no autoriza ejecución.

La suite nueva usa tres hilos propios, barreras/Event y reloj lógico. No crea
raíces de datos ni hijos de proceso. El runner completo también ejecuta las
regresiones I24/I26/I28/I30 y Python anterior: **I26** mantiene requisitos Linux/
fsync/flock, carpetas temporales marcadas e hijos/SIGKILL propios. Su recuperación
filesystem no se atribuye a I32. El runner emite JSON a stdout; no guarda informe.

## Perfiles, fuente y correspondencias

[`eligibility_fixture.py`](../../source_ingest/eligibility_fixture.py) es nuevo y
no modifica parsers ni módulos anteriores. Los descriptores cerrados llevan
profile_id/version, extraction_policy_version y decoder_id/contrato versionado.
El hash del contrato del decoder identifica una interfaz declarada de fixture;
no es una firma ni un hash del código ejecutable. El informe registra por separado
los hashes reales de los archivos usados en esta campaña.

La lista cerrada de decoders admite `task-register.v1`, `task-register-compat.v1`
y `markdown-structure.v1` mediante `build_observation` existente. Las versiones
sintéticas del descriptor envuelven el mismo parser sin atribuir un formato
Gentle-AI nuevo. Unknown/rutas/comandos de decoder no se ejecutan: los bytes
acotados se conservan con BLOCKED. Checklist sigue preview sin identidad estable.

Captura conserva bytes/base64/hash, descriptor y generación de selección explícita
por proyecto/documento. Bytes idénticos bajo otro descriptor/política tienen el
mismo content_sha256 pero otra captura y preview_sha256: este último incluye el
contexto versionado. La proyección interna puede coincidir sin compartir revisión.
Cambiar/revocar/restaurar selección avanza generación; no revive paquetes antiguos.
SOURCE_ACCEPT fija exactamente esa captura y generación. Un perfil o revisión
obsoletos bloquean antes de preparar o confirmar una evaluación.

`record_mapping_fixture` conserva correspondencias históricas de prueba sin crear
entidades D2. `check_mapping_fixture` comprueba identidad completa y bloquea
reutilización entre perfiles aunque coincidan documento+ID o UUID. Las fixtures de
correspondencias permanecen inmutables. No hay conversión, adopción o aplicación
de tareas; las inspecciones privadas no otorgan autoridad al llamante.

## Cuentas, políticas y observaciones

Un binding identifica cuenta física de proveedor **de fixture**, recurso,
proveedor/instancia y proyecto, con un adaptador explícito. Recurso/cuenta no pueden
registrarse dos veces bajo otro binding para multiplicar saldo. Este primer corte
rechaza esos alias; no descubre ni une cuentas por nombre. Una cuenta de proveedor
no es una cuenta D3 multidimensional: los ledgers D3 por recurso/dimensión/ventana,
sus mappings congelados y reparto/reservas permanecen intactos.

La política activa del proyecto tiene descriptor inmutable por policy_id/version,
selección CAS y generación. Sus restricciones completas fijan dimensión, unidad,
window_id, intervalo `[window_start,window_end)`, coste entero positivo y horizonte
positivo. Los intervalos son parte de la identidad exacta de ventana. El caller
no aporta un subconjunto de costes a `prepare_evaluation`; la fuente tampoco
puede sustituir política, proveedor, permisos o fallback. Duplicados bloquean.

Cada observación es un hecho inmutable por UUID con scope completo, descriptor de
adaptador, revisión, ventana, estado, remaining y observed_at/expires_at. Publicar
exige generación esperada; el mismo ID/bytes recupera el hecho sin reselect ni
restauración. Otro contenido bajo el mismo ID bloquea. Nuevo ID, aun con valores
idénticos, avanza generación. Elegir observación es otra operación CAS explícita;
ningún observed_at o orden de lista gana por fecha. Revocación conserva el hecho
y registra un marcador que invalida la cuenta; replay no lo elimina.

Todas las restricciones deben encontrar observación seleccionada de la misma
cuenta/scope y release/hash de adaptador. No se suman cuentas, proveedores,
dimensiones, unidades o ventanas ni se convierten unidades. Solo KNOWN válido,
permiso SYNTHETIC_GRANTED, capability admitida y online pueden habilitar. Cero
remaining bloquea coste positivo; UNKNOWN/UNLIMITED_DECLARED/REVOKED son distintos.

Se exige observed_at ≤ now < expires_at, ventana activa semiabierta y cobertura
hasta now + horizonte tanto por caducidad como por fin de ventana. La igualdad del
horizonte con el límite cubre el intervalo; pasar ese límite bloquea. El horizonte
es una política de fixture y no cambia el lease D3. Un rollover no rellena ventanas
anteriores, remapea reservas ni concede saldo a un retry. Ni observación, lectura,
revisión o resultado positivo consume cuota o crea reservas.

## Revisión, revalidación y replay

`prepare_evaluation` fija captura/preview y SOURCE_ACCEPT, perfil/generación,
binding y generación de cuenta, adaptador/capacidades/permisos, política/generación,
vector completo y IDs/hashes de las observaciones seleccionadas. Guarda evaluación
y tick originales. El manifiesto canónico es inmutable y obtiene revisión
EVALUATION separada. Aceptar un manifiesto bloqueado no lo vuelve elegible.

`validate_evaluation` verifica el manifiesto y su reconstrucción, toma una lectura
consistente y, antes de confirmar el recibo bajo lock, comprueba otra vez hechos,
selecciones, política y revisiones exactas. Los hooks confiables de prueba están
fuera del lock. Cambio/revocación o restauración ABA exige otro manifiesto y nueva
revisión, incluso si los valores vuelven a coincidir. Registrar otro hecho en la
misma cuenta invalida el paquete aun si no se seleccionó todavía.

El reloj se reevalúa al confirmar: puede cruzar caducidad/perder horizonte sin
modificar generación de cuenta. Cada comando nuevo recibe resultado actual de
fixture. Los recibos no cambian hechos o generaciones, de modo que lectores
concurrentes pueden resultar positivos sin afirmar que han reservado capacidad.
Una aprobación reemplazada, incluso por otro ACCEPT, no sustituye su versión previa.

Replay/read_command devuelve el recibo anterior con `historical=true`; un recibo
fresco tiene `historical=false`. Ambos llevan `grants_execution_authority=false`,
activation/fallback false y consumo/reservas cero. El request hash fija manifiesto
y versión de revisión; el mismo command_id con otro request bloquea. Un fallo
simulado después de confirmar se recupera solo como lectura histórica. No se
atribuye autoridad actual a un resultado positivo antiguo.

## Evidencia, límites y continuidad

38 tests nuevos cubren PQ01–PQ34, más 195 regresiones identificadas: **233 tests
distintos**, cero fallos/errores/omisiones. Se crean y terminan tres hilos nuevos;
las regresiones terminan sus diez hilos, eliminan 33 raíces I26 y dejan cero hijos
propios vivos de siete iniciados. No se reejecutan SQL/D2/D3/D4 ni se suman sus
campañas históricas como pruebas nuevas.

Límites: 16 perfiles/versiones, 16 bindings, 16 restricciones por política, 128
observaciones inmutables y 128 recibos. Se alcanzan esos conteos realmente y se
rechaza el siguiente; el replay de un recibo confirmado sigue disponible al límite.
Fuente >2 MiB y etiqueta de 257 caracteres se rechazan sin truncar. El manifiesto
configura 1 MiB; **su rama de rechazo se prueba con un presupuesto reducido**, no
con una campaña de manifiestos completos >1 MiB. No es benchmark de capacidad.

Las inspecciones de captura/manifiesto/hechos contienen bytes y datos completos
de fixture y son privadas; recibos/runner/demo evitan texto crudo y cuerpos de
error. No hay garantía frente a caller Python hostil ni prueba de permisos,
cuotas reales, HTTP, SQL, reservas D3 o recuperación durable del proceso. Todo
estado es volátil y otro laboratorio no hereda aprobaciones/recibos.

GI04/GI20/GI22 reciben solo evidencia acotada de modelo: **30/35 S con evidencia**,
cinco S y siete R pendientes. GI06/GI24 reales y GI33/GI34/GI38/GI39/GI40 integrados
siguen pendientes; ninguna brecha G01–G07 se cierra. El hito I1–I20 no se amplía.
Sin promoción, despliegue ni D6.
