# D5 I4 — revisión del diseño de persistencia

Fecha: 2026-10-21. Estado: **diseño preparado para revisión; implementación y
ejecución pendientes**. [Contrato técnico](D5-PERSISTENCE-DESIGN.md).

## Qué se propone aprobar después

El siguiente incremento podría implementar un laboratorio PostgreSQL desechable,
exclusivo de D5, con fixtures sintéticas y un adaptador local que reconstruya las
previsualizaciones antes del ingreso. No integraría el entorno de desarrollo ni
el laboratorio D4, no importaría el corpus privado y no promovería migraciones.
Esta propuesta de siguiente paso todavía no autoriza ejecutarlo.

Las decisiones expresas D5-A06/A07/A08 ya fijan reutilizar SourceDocument y
SourceRevision, añadir observaciones D5, seleccionar referencias con versión
esperada y conservar los bytes limitados en PostgreSQL dentro de la misma
transacción que la observación y el recibo.

El contrato concreta además estas reglas para revisión:

- Registro explícito de proyecto existente, documento y namespace/clave lógica;
  solo fuentes nuevas administradas por D5 en el primer laboratorio.
- Contenido de hasta 2 MiB y artefacto de hasta 32 MiB; deduplicación de contenido
  por documento, observaciones distintas por comando y hechos append-only.
- Cabeza por documento/perfil, inicialmente vacía, versión monotónica; ingerir
  nunca la selecciona. Una referencia de diagnóstico BLOCKED sigue BLOCKED.
- Mutex propio de D5 para el primer laboratorio; recibos históricos y replay
  exacto. Una respuesta antigua no acredita el estado actual de la cabeza.
- D2 conserva sus contratos y punteros; el escritor D5 no obtiene autoridad para
  ejecutar, planificar ni modificar tareas.

## Matriz de aceptación del futuro laboratorio

**Son pruebas requeridas, no resultados ejecutados en este corte.** Cada grupo
deberá tener evidencia propia, comprobaciones del estado confirmado y casos de
rechazo, sin reutilizar los conteos de pruebas de entregas anteriores.

| Grupo | Casos mínimos | Resultado que deberá demostrarse |
|---|---|---|
| P01 Identidad | Registro nuevo; repetición; proyecto inexistente; UUID/clave ya usados; documento histórico; cambio ajeno de URI/tipo/head | Identidad exacta o conflicto; ninguna adopción, reasignación o reparación implícita |
| P02 Ámbito | Artefacto de otro documento/proyecto; observación de otro perfil; FKs directas inválidas | Rechazo sin enlaces cruzados ni hechos parciales |
| P03 Bytes | Límites exactos y exceso; digest incorrecto; base64 distinto; metadatos incompatibles; JSON duplicado o perfil adulterado | Verificación del adaptador y guardas SQL separadas; recuperación de bytes exactos |
| P04 Deduplicación | Mismo contenido con etiquetas/perfiles nuevos; mismo artefacto con dos comandos; mismo contenido en documentos distintos | Revisiones, artefactos y observaciones según la tabla del contrato, sin falsas nuevas capturas |
| P05 Selección | Ingesta sin seleccionar; CAS inicial; nueva selección de la misma observación; referencia BLOCKED | Solo SELECT_REFERENCE mueve cabeza y versión; no cambia elegibilidad |
| P06 Concurrencia | Dos INGEST iguales con comandos distintos; dos SELECT con la misma versión; secuencia A→B→A | Una revisión/dos observaciones; un CAS ganador; versión antigua siempre rechazada |
| P07 Recibos | Replay exacto; mismo ID con otros blobs/acción/versión; replay de éxito tras otra selección; replay de conflicto | No duplicación ni sobrescritura; recibo histórico distinto de lectura actual |
| P08 Recuperación | Aborto antes del commit; commit con respuesta perdida; reinicio de la base conservando datos del laboratorio | Atomicidad y recuperación por READ_COMMAND; ninguna inferencia de éxito por timeout |
| P09 Permisos | Roles lector/escritor; DML/UPDATE/DELETE/TRUNCATE; funciones D2/D3/D4; objetos temporales que oculten nombres | Acceso mínimo, hechos inmutables y entradas propietarias con resolución de nombres fija |
| P10 Aislamiento | Estado D2 antes/después; outbox/tareas/bindings/punteros; bootstrap D4 y Compose dev; manifiestos históricos | Solo nuevas fuentes/revisiones y hechos D5 autorizados; ninguna activación ni cambio de entradas selladas |

P06 exige sesiones SQL realmente concurrentes; una llamada secuencial no demuestra
concurrencia. P08 exige observar estado tras reconexión y no solo una excepción
del cliente. P03 debe distinguir la reconstrucción semántica del parser de los
controles relacionales y de bytes en SQL. Ninguna prueba acredita autenticidad,
frescura o aprobación de una fuente real.

## Validación de este corte documental

Se revisa la compatibilidad contra los contratos existentes V1/V5/V7/V10 y las
fronteras D3/D4. Se comprueban publicación, enlaces locales, formato del diff e
integridad de los hashes registrados en los manifiestos de cierre D3/D4.
Resultado: comprobación de publicación correcta sobre 317 archivos de texto;
245 entradas de hash de rutas/evidencias correctas, más el hash explícito del
documento canónico D4; enlaces locales de los tres documentos y diff correctos.
Estas comprobaciones documentales no validan un DDL ni el aislamiento PostgreSQL.
No se ejecutan migraciones, servicios, baterías SQL ni nuevas pruebas de ingesta.
Los resultados I1–I3 y sus artefactos conservan su carácter histórico.

La decisión pendiente es autorizar por separado la implementación y ejecución
del laboratorio sintético descrito, o ajustar primero este contrato. D5 permanece
abierto; no se inicia D6 ni se reabren D1–D4.
