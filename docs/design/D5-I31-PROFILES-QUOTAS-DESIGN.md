# D5 I31 — contrato de perfiles y cuotas sintéticas

Fecha: 2026-10-22. **PREPARADO PARA REVISIÓN; sin implementación nueva.**
Cobertura propuesta: GI04/GI20/GI22 de [I23](D5-I23-GLOBAL-INTEGRATION-DESIGN.md).
[Matriz PQ01–PQ34](D5-I31-PROFILES-QUOTAS-REVIEW.md) ·
[Comprobaciones documentales](../validation/D5-I31-design-review.json).
**G01–G07 y D5 global abiertos; hito aceptado I1–I20 sin ampliación.**

English: proposed in-memory versioned extraction/eligibility fixtures. Profile or
policy changes require fresh capture, preview and review, without converting old
mappings. All required quota dimensions/windows must belong to one explicit
physical account/scope; immutable observations, adapter versions and revocation
are bound to reviewed manifests. No quota consumption, reservations or D3 changes.

## Decisiones y perímetro

| ID | Decisión expresa | Consecuencia |
|---|---|---|
| A72 | Priorizar diseño de perfiles y cuotas GI04/GI20/GI22 | Contrato y matriz antes de implementar |
| A73 | Cambio de versión de perfil/política exige captura/preview y revisión propias; conservar correspondencias y bloquear reutilización automática | Sin conversión de correspondencias en este corte |
| A74 | Todas las observaciones necesarias vigentes de la misma cuenta/ámbito; sin sumar ventanas/cuentas; cualquier cambio/revocación exige nueva evaluación y revisión | Sin renovación compatible bajo aprobación anterior |

A72–A74 no aprueban todavía el contrato completo ni autorizan implementar. Propuesta:
módulo/harness Python nuevo en memoria, biblioteca estándar, reloj lógico monótono
y concurrencia controlada en hilos. Parsers/dobles/contratos I1–I30 permanecen
intactos. Solo fixtures públicas sintéticas; sin HTTP, SDK/CLI, SQL, Docker,
filesystem de datos nuevo, procesos hijos o proveedores/credenciales reales.
Las regresiones I26 conservarían sus requisitos y recursos propios separados.

Este corte añade manifiestos y guardas de **modelo**, sin conectar o cambiar D3.
Un resultado elegible no publica planes, consume cuota, reserva capacidad, reclama
leases ni activa tareas. No se introduce un proveedor o formato Gentle-AI real.
La [aprobación D3](D3-approved.md) conserva cuentas físicas por recurso/dimensión/
ventana, reservas compartidas, mappings congelados, reparto 70/20/10 y retries por
delta; sus APIs y campañas no cambian. No se acredita capacidad comercial real.

## Perfil, política y captura

Descriptor cerrado/versionado de fixture: profile_id, profile_version,
extraction_policy_version, decoder_id y hash/versión del contrato del decoder.
Un registro explícito admite solo decoders locales previamente conocidos; no
acepta rutas ejecutables, imports, comandos, URL ni instrucciones del documento.
El primer laboratorio propondrá versiones sintéticas envolviendo un parser ya
existente, conservando su semántica. Una etiqueta v2 de fixture no afirma un
formato comercial nuevo ni autoriza modificar el parser histórico.

Captura fija proyecto/documento/revisión declarados, bytes exactos/hash, descriptor
completo y política seleccionada por versión CAS. Su identidad combina esos datos:
los mismos bytes bajo otro perfil/política producen **otra captura y manifiesto**,
aunque su content_sha256 coincida. Lo desconocido conserva bytes acotados con
BLOCKED y no produce propuesta elegible. Una checklist sin identidad estable sigue
solo en preview; no se adopta por posición/título. No ampliar los formatos I23.

Capturar/preview no revisa. SOURCE_ACCEPT propio fija hash de captura/preview,
descriptor, política y versión de revisión. Cambiar el perfil seleccionado o la
política invalida paquetes preparados para ese ámbito, aunque el resultado textual
fuera idéntico. Volver después a la etiqueta anterior no restaura aprobaciones:
la generación monótona registra también ABA y revocaciones.

Correspondencias anteriores se conservan como evidencia inmutable de su namespace
original. No se reinterpretan al seleccionar el nuevo perfil ni se vinculan UUID
existentes por igualdad de documento+ID o título. El modelo puede consultar fixtures
de correspondencias para demostrar el bloqueo de reutilización; no crea, adopta,
convierte o aplica tareas. Una conversión futura exige contrato/decisión propios.
Replay histórico devuelve su recibo/artefacto anterior sin reactivar la selección
revocada ni actualizar correspondencias.

## Cuenta física, ámbito y política de evaluación

Registro explícito de fixture: physical_account_id UUID, resource_id UUID,
provider_id e instancia de fixture, ámbito/proyecto autorizado y adaptador con
adapter_id/release/hash. Un recurso físico no se registra como dos cuentas para
multiplicar capacidad; alias del mismo recurso deben resolver a la misma cuenta
canónica o bloquear por conflicto. No descubrir cuentas por nombre o credenciales.

physical_account_id es la identidad de cuenta de proveedor **de fixture**, no una
cuenta D3 multidimensional nueva. Las cuentas D3 conservan su clave separada por
recurso/dimensión/ventana. Exigir el mismo proveedor/cuenta exterior no permite
agrupar los saldos de esas cuentas ni modificar sus mappings/reservas.
Cambiar proveedor/recurso/ámbito exige binding explícito nuevo, nunca hereda cuotas.

La política de demanda es una ficha cerrada/versionada del harness: capability,
lista de restricciones necesarias `(dimension, unit, window_id, cost)` y horizonte
lógico requerido, entero positivo. Cada cost es entero positivo; no hay conversión de unidades,
redondeo de floats o demanda que pueda rebajar restricciones por texto fuente.
El manifiesto debe incluir **todas** las restricciones de la política activa.
Duplicados o una lista vacía bloquean, no se suman ni se elige el subconjunto más
favorable. Una configuración desconocida conserva bloqueo.

La clave de observación incluye cuenta/recurso/proveedor/ámbito, dimensión, unidad
exacta e identidad/intervalo de ventana. Dos ventanas de la misma dimensión son
restricciones distintas, no bolsas acumulables. Todas deben satisfacerse a la vez
para la misma cuenta y política. Una ventana futura o una observación de otra
cuenta no cubren una restricción actual, aunque sus cantidades fueran mayores.
No se suman proveedores, cuentas, dimensiones, unidades o ventanas.

## Observaciones, frescura y revocación

Cada observación es inmutable, con observation_id UUID, clave de ámbito completa,
adapter_id/release/hash que la produjo, número de revisión registrado, procedencia
SYNTHETIC_ONLY, state, remaining, observed_at, expires_at y ventana `[start,end)`.
No admite secretos o cuerpos de error crudos. Estados KNOWN, UNKNOWN,
UNLIMITED_DECLARED y REVOKED son distintos; solo KNOWN válido puede habilitar.
remaining es entero no negativo: cero bloquea coste positivo, nunca es ilimitado.

Publicar/revocar una observación requiere generación esperada de su cuenta. El
registro guarda historial y una selección explícita por clave; ninguna fecha,
observed_at más alto o último elemento de una lista decide cuál manda. Un nuevo
ID con el mismo contenido también avanza la generación e invalida la evaluación
anterior de esa cuenta, conforme A74. No sobrescribir hechos ni restaurarlos por
replay. Cambiar/revocar adaptador, capacidad o permiso de fixture también avanza
esa generación. Restaurar valores no restaura versiones.

Para cada restricción se exige coincidencia exacta de cuenta/ámbito/adapter y
unidad/ventana, permiso SYNTHETIC_GRANTED y capability conocida/online; además:

- `observed_at <= now < expires_at`, sin heredar frescura de otra observación;
- `window_start <= now < window_end`, con intervalo válido y horizonte cubierto
  hasta `now + required_horizon` por ventana y caducidad;
- `remaining >= cost`, con todas las restricciones requeridas presentes y KNOWN.

Son ticks e intervalos de fixture, no datos del reloj de Google/Plane/proveedor.
El horizonte viene de la política explícita y no sustituye el lease/renovación D3.
Al avanzar el reloj se revalida frescura aunque no cambie la generación de cuenta.
Un reset/rollover no mueve reservas existentes, no renueva saldo y no crea capacidad.
Observación de ventana nueva exige selección y evaluación nuevas; no rellena la
anterior ni concede capacidad al reintentar. Ni lectura ni revisión descuentan
saldo o producen reservas, incluso cuando dos lectores resultan elegibles.

## Manifiesto, revisión y revalidación

Se proponen tres registros separados: SOURCE, EVALUATION y recibos de consulta.
Una evaluación fija captura/preview y SOURCE_ACCEPT exactos, binding de cuenta,
perfil/política/generaciones, adaptador/capacidades/permisos, vector completo de
costes y todos los IDs/hashes/selecciones de observación. Conserva el tick evaluado
y los diagnósticos por restricción, sin presentar el resultado como cuota real.
No contiene un comando de ejecución ni una reserva D3.

La evaluación completa obtiene revisión EVALUATION propia con CAS de versión y
razón. No se reutilizan aprobaciones de fuente, lotes I30, proyección Plane,
publicación Git o aceptación local A52. Un resultado bloqueado no se convierte en
elegible por ACCEPT: revalidación aplica las mismas guardas a los hechos actuales.
Aprobar tampoco cambia el hash del manifiesto o la generación de hechos evaluados;
la revisión tiene versión separada para evitar un ciclo de hash/aprobación.

`validate_evaluation` hace una lectura consistente: fija snapshot/generaciones,
reconstruye la evaluación, y bajo lock corto revalida versiones de hechos, perfil,
políticas y revisiones exigidas. Si cambia cualquier hecho de la cuenta, adaptador,
selección relevante o perfil/política, devuelve STALE/CONFLICT; no sustituye IDs ni
renueva timestamps bajo aprobación vieja. Se requiere otro manifiesto/evaluación y
otra revisión. Una edición durante el cálculo se reproduce con barrera de fixture.

Un reloj posterior dentro de los intervalos puede validar una aprobación vigente;
cruzar expires_at, window_end o perder cobertura de horizonte bloquea aunque la
cuenta no haya cambiado. Confirmar una consulta guarda recibo con request_hash,
manifest/review_version, generaciones y tick/resultado, **sin cambiar hechos de
cuota**. Un replay confirmado devuelve el resultado histórico etiquetado como tal;
no prueba elegibilidad actual, no revalida ni activa. Un comando nuevo exige
validación actual. Mismo command_id con otro request bloquea, nunca reemplaza.

Observaciones, perfil/política y revisiones tienen generaciones/versiones separadas
de la colección de recibos. Registrar un recibo o aprobar una evaluación no crea
saldo ni invalida por sí mismo los hechos que acaba de revisar. La publicación de
un cambio concurrente sí invalida; no hay vencedor por fecha. Llamadas al exterior,
locks SQL, retries automáticos, fallbacks y reservas quedan fuera.

## Laboratorio propuesto y aceptación

Límites propuestos: 16 perfiles/versiones registrados, 16 bindings de cuenta,
16 restricciones por política, 128 observaciones inmutables y 128 recibos por
laboratorio; fuente ≤2 MiB con límites existentes, manifiesto ≤1 MiB y etiquetas
≤256 caracteres. Exceso bloquea sin truncar, sumar cuotas o renovar presupuestos
por command_id nuevo. No son límites comerciales. Reloj entero monótono del
harness; sin sleeps, daemon o sondeo real. Los hechos y la evidencia son volátiles.

Si se autoriza implementar, la campaña deberá cubrir PQ01–PQ34, con evidencia
propia de versiones, identidad, cuentas/ventanas, revocación y concurrencia. Se
identificarán aparte las regresiones I24/I26/I28/I30 y la limpieza de sus recursos;
el filesystem/reinicio I26 no se atribuirá a este modelo en memoria. No reescribir
historia, manifiestos o evidencias ni reejecutar SQL por una edición documental.

GI04/GI20/GI22 recibirían solo evidencia de modelo. GI06/GI24 reales y los criterios
integrados GI33/GI34/GI38/GI39/GI40 siguen pendientes, así como G01–G07 globales.
El hito aceptado I1–I20 no se amplía. Puerta propuesta: aprobar I31 y autorizar
implementar/validar PQ01–PQ34 en memoria, sin SQL, HTTP, efectos D2, consumo/reservas,
activación, promoción, despliegue o D6. Publicar el diseño no autoriza implementarlo.
