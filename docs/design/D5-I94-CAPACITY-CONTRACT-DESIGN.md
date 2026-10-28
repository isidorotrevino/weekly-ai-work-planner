# I94 — contrato de capacidad y carga atómica propuestos

Fecha:2026-10-27, Europe/Madrid. **PREPARED_FOR_REVIEW_NUMERIC_CAPTURE_CERTIFICATE_UNRESOLVED**.
La respuesta A a I93 autoriza este diseño documental y propuestas justificadas;
no aplica cuotas, implementa código, ejecuta componentes/capturas ni publica.
[Evaluación y matriz](../validation/D5-I94-design-review.json) ·
[Auditoría AST](../validation/D5-I94-source-capacity-audit.json) ·
[Revisión CB01–CB32](D5-I94-CAPACITY-CONTRACT-REVIEW.md).

## Resultado de diseño

Se recomienda ALT03: certificado versionado de capacidad y reserva atómica del
presupuesto global. **No hay todavía una cifra nueva justificable para refs**.
La capacidad completa321/12 sigue NOT_ESTABLISHED. Esto es una puerta bloqueante
explícita: aprobar el diseño no aprobaría una captura o ampliación numérica.
ALT02 (multiplicar cuotas o extrapolar13/321) se rechaza. ALT01 (representación
sin pérdida con16384) y ALT04 (streaming/interning) requieren prueba de cómputo;
no se presentan como soluciones ya viables.

La auditoría leyó/parseó 71 fuentes pinneadas del runner,321 bindings de
test/12 grupos y118 entradas causales (48 T,40 R,30 DRIVE), sin importarlas ni
ejecutarlas. Identificó 25 métodos con 38 sitios candidatos de carga,
y 493 bucles sintácticos. El JSON separa límites locales literales de
iteración dependiente de datos/control. Ningún conteo sintáctico se presenta como
multiplicidad transitiva o evidencia runtime. Los métodos sobreescritos se
identifican para no sumar copias inactivas como si se ejecutaran.

## Envolvente por fuente y condiciones conjuntas

Para referencias se define **R=Σ(qᵢ×Nᵢ)** sobre sitios activos del MRO pinneado.
qᵢ es1,2,len(owner_context_refs)+1,1+len(witnesses), etc., según cada sitio real;
Nᵢ es su multiplicidad por las321 identidades y rutas originales. Incluye owners,
identidades, declaraciones, miembros del frame, keys, contextos/subcasos/hilos,
retained records, enlaces, grupos/witnesses, mensajes/exit y registros DI07,
bindings tardíos, fuentes y manifiesto de páginas. Dos estructuras que retienen
un puntero cuentan aunque la cadena se interne; no se deduce una reducción de
cuota por ahorrar bytes. R no se evalúa sustituyendo incógnitas por0 o por I92.

**No existe Nᵢ completo certificado**: los bucles locales no resuelven helpers,
ramas, datos de fixture, callbacks y concurrencia. Las anclas I82 y métodos de
carga existentes permiten localizar ese trabajo sin atribuir la primera carga
fallida de I92, que no fue retenida. El diseño exige que el certificado declare
cada desconocido y bloquee la afirmación de capacidad hasta resolverlo.

Para eventos, E=Σeₜ. Las321 cuotas por test permiten657408 eventos, pero el techo
global es131072. No es una contradicción: son límites conjuntos; cumplir cada
límite local no garantiza completar toda la campaña.131072×4096 permite512MiB de
payload, mientras las páginas permiten64MiB, con headers/comas adicionales.
La envolvente de una captura aceptable requiere ambas condiciones a la vez.

Raw/sidecar/contexto/launcher de12MiB cada uno,64MiB de páginas y OWNER36 bytes
suman **112MiB+36 bytes**, frente a112MiB+4096: margen4060 bytes a máximos
individuales. El launcher hermano se cuenta exactamente una vez; son32 páginas+
raw+sidecar+contexto+OWNER+launcher=37 miembros. No añadir archivos al paquete
para resolver capacidad. El presupuesto de Reader exige su propio calendario:
tres escaneos de ese máximo suman352321644 bytes y superan256MiB, aun cuando el
paquete cumpla tamaño. No se afirma que el reader actual haga exactamente esos
tres escaneos; se demuestra que los máximos independientes no bastan para probar
viabilidad conjunta. Hay que pinnear las lecturas reales, incluida finish.

La futura autoridad/contrato/registro/código/sello y verificaciones antes/después
consumirán Reader128MiB únicos/256MiB leídos por ámbito, sin resets. Los292 pins
actuales y el preflight I91 no certifican el alcance futuro, ni convierten574
inputs documentales en runtime ejecutado. Operand16MiB incluye original y
representaciones/hashes auxiliares; salida pequeña no dispensa la entrada.

## Comparación completa de cuotas

Todas las cifras están en bytes, unidades o segundos según su clave. No hay
cambios aplicados. La propuesta numérica de refs queda bloqueada por certificado.

| Clave | Actual | Propuesta por defecto | Estado |
|---|---:|---:|---|
| event_bytes | 4096 | 4096 | UNCHANGED |
| events_test | 2048 | 2048 | UNCHANGED |
| events_campaign | 131072 | 131072 | UNCHANGED |
| page_bytes | 2097152 | 2097152 | UNCHANGED |
| pages | 32 | 32 | UNCHANGED |
| event_pages_total_bytes | 67108864 | 67108864 | UNCHANGED |
| raw_bytes | 12582912 | 12582912 | UNCHANGED |
| index_sidecar_bytes | 12582912 | 12582912 | UNCHANGED |
| context_bytes | 12582912 | 12582912 | UNCHANGED |
| launch_bytes | 12582912 | 12582912 | UNCHANGED |
| package_bytes | 117444608 | 117444608 | UNCHANGED |
| evidence_unique_bytes | 134217728 | 134217728 | UNCHANGED |
| evidence_read_bytes | 268435456 | 268435456 | UNCHANGED |
| operand_bytes | 16777216 | 16777216 | UNCHANGED |
| frames | 4096 | 4096 | UNCHANGED |
| refs | 16384 | sin cifra aprobable; certificado pendiente | CONDITIONAL_NUMERIC_REVISION_UNRESOLVED |
| depth | 32 | 32 | UNCHANGED |
| string | 4096 | 4096 | UNCHANGED |
| input_paths | 4096 | 4096 | UNCHANGED |
| input_file_bytes | 16777216 | 16777216 | UNCHANGED |
| input_unique_bytes | 134217728 | 134217728 | UNCHANGED |
| input_read_bytes | 268435456 | 268435456 | UNCHANGED |
| wait_seconds | 20 | 20 | UNCHANGED |
| campaign_seconds | 900 | 900 | UNCHANGED |

Filas/eventos siguen4096 bytes y el diagnóstico4096 bytes allowlisted. Las32
páginas mantienen2MiB,64MiB acumulados y nombres existentes. No cambiará P0 ni
se obtendrá autoridad funcional de un certificado de recursos.

## Reserva atómica y fallo

La futura operación debe validar un entero exacto no negativo y reservar toda la
carga bajo un único lock global **antes** de incrementar contador o mutar tablas.
Si n>limit-used, ni contador ni nuevo fragmento cambian. Concurrencia, frame,
tabla y página comparten ese presupuesto: no hay reset ni contador alternativo.
El lock sólo protege la instrumentación y nunca se mantiene durante una llamada
original, I/O de dominio, espera o cleanup; no altera las barreras del test.
La comprobación previa de referencia **sola no basta** si owner/key/group ya se
mutó: la unidad de reserva debe cubrir el conjunto de cambios correlacionados,
su row/event/operand budget y publicación. Las asignaciones ya comprometidas no
se descuentan al cerrar un frame ni se reutilizan como identidades nuevas.

El método original se llama una sola vez; se conserva retorno/excepción por
identidad. El primer error se latchea y se detiene entre tests, con cleanup y
restauración originales. Una escritura JSON; no reparar salida parcial. El
canal4096 bytes conserva primera fase/código cerrado, sin texto libre, objetos,
stacktrace o rutas. Un resumen fijo de recursos sólo puede ir inline en contexto
normal dentro de cuotas, sin actor/canal/observación de dominio adicionales.
No se modifica ni reinterpreta el16393 sellado de I92.

Reader valida cuotas y evidencia por separado: source/certificate/pins y counts;
además, contexto, membresía, recibos, request/command/seq/head, oráculos y todas
las autoridades/missing. Un buen presupuesto no sana PENDING_CHILD_EXIT ni
REMOTE_RESULT_WITHOUT_STORE_RECEIPT, ni inventa UUID5/cid. NP00/NP01/NP02 y las
quince políticas parentales se conservan. Debe prevalecer el fallo si no se puede
publicar el conjunto completo sin pérdida, incluso con límites nuevos.

## Componentes futuros y decisiones posteriores

**I95 propuesto** es sólo planificador de certificado y guard de carga atómica
con datos/clases sintéticos nuevos, **CB01–CB32 NOT_RUN**, externo300s. Namespace
`testing/prospective_capture_capacity/`: capacity.py,test_capacity.py,
run_capacity_lab.py,README.md; manifiesto documental nuevo
`docs/validation/D5-CAPACITY-PLANNER-MANIFEST.json`. **Nada de ello existe ahora**.
Mantendría16384 como default; no crearía perfil/registro de captura de producto.
Puede verificar fórmulas/negativos sintéticos y UNKNOWN, pero no rellenar Nᵢ ni
certificar que el P01 original cabe sin la evidencia de fuente correspondiente.

Implementar/ejecutar I95 requiere aprobación separada. Incluso con CB32 PASS,
una captura I96 o posterior seguiría bloqueada: certificado numérico revisado,
diseño de perfil/registro nuevos, componentes de ese perfil, pins/presupuesto y
autoridad/destino nuevos necesitarían decisiones posteriores. No se asignan
ahora paths de captura ni se crea launcher.321/12 una vez bajo900s externos,
sin reanudación/suma de paquetes ni reintentos automáticos. Ante incompatibilidad,
conservar y presentar antes de ampliar/repetir. IR03 y publicación separados.

## Estado conservado

I86/I89/I92 inválidos y sellados; I92:13/321 raw PASS no es captura completa.
Sellos I83–I93 y Git conservados, sin commit/push. Nuevo diseño y revisión no son
pruebas ejecutadas, ni prueba de persistencia/recuperación integrada, fsync nativo
o suficiencia UI04.1. P0;83 SUPPORTS_BOUNDED/1 PARTIAL; D1–D4 cerrados,
I1–I20/A52 aceptado,30/35 sin promoción. D5/H07/G01–G07 y GI33/34/38/39/40 OPEN.
Sin proveedores/credenciales/corpus reales, consumo/reservas, activación,
promoción, despliegue, nuevos SQL/Java/Docker o D6.
