# I116 — revisión por fuente de las siete obligaciones PJC115

Fecha:2026-11-10, Europe/Madrid. **PJC115 todavía no está habilitada.**
Se acotan las proyecciones, el raw y varias filas originales, y se acota
el esquema normal de contexto/launcher con dependencia del input scope.
CP02 y CP05 son parciales; CP03 sigue abierto y CP07 requiere fuentes futuras inexistentes.
No sería correcto declarar resueltas las siete obligaciones ni pedir ahora
autorización de implementación sobre un certificado conjunto inexistente.

[Proyecciones, filas y88 raíces T/R](../validation/D5-I116-projection-row-envelopes.json) ·
[Raw y contexto](../validation/D5-I116-raw-context-envelopes.json) ·
[Estados, correcciones y addendum R1](../validation/D5-I116-PJC115-gate-review.json) ·
[Auditoría documental](../validation/D5-I116-audit.py) ·
[Sello](../validation/D5-I116-integrity.json).

HEAD permanece50c49678568bae2abeefbe5fec0285f26c628283. Se conservan los26
archivos locales anteriores, incluidos I111–I115/handoff/sellos, sin cambios
tracked o staged. Sólo se añade documentación y su auditoría. No se importó ni
ejecutó producto/runner, componentes o campañas; no se aplicaron cuotas ni hubo
commit/push. La lectura de metadatos descriptivos stdlib del host no es captura
funcional ni autoridad para otro entorno.

## Resultado por obligación

| Puerta | Resultado I116 | Conclusión y límite |
|---|---|---|
| CP01 eventos causales | RESOLVED_SOURCE_PROJECTION_SHAPES_CONDITIONAL_CP03 | Proyecciones completas acotadas; falta éxito de operandos |
| CP02 filas | PARTIAL_GROUP_ROW_SOURCE_UPPER_ABOVE_LIMIT | Varias filas caben; grupo4224 no certifica4096 |
| CP03 operandos | OPEN_FULL_OPERAND_SOURCE_CLOSURE | Resuelta sólo la subfamilia ORACLES; faltan árboles y auxiliares |
| CP04 raw | RESOLVED_ORIGINAL_NORMAL_RAW_ENVELOPE | Cota1667028 bytes para el runner original completo PASS |
| CP05 sidecar | PARTIAL_AGGREGATE_ALLOWANCES_AND_FUTURE_METADATA | Formas refinadas; agregado y propagación de límites pendientes |
| CP06 contexto/launcher | RESOLVED_NORMAL_SCHEMA_ENVELOPE_CONDITIONAL_CP07 | Cada uno<=11649032 bytes bajo esquema y paths revisados |
| CP07 Reader futuro | OPEN_FUTURE_FILES_HASHES_AND_READ_SCHEDULE_ABSENT | No hay hashes/calendario exactos de archivos inexistentes |

Los calificadores son parte del resultado: ninguna dependencia se sustituye por
PASS ni por0. CP08/09 permanecen NOT_AUTHORIZED; JC01–JC20, NOT_RUN.

## CP01 y CP02: tamaño por forma, sin suponer UUID únicos

I115 permite refs O de hasta5 caracteres y claves causales de hasta6:5190
owners y37651 altas Q19. No se obtiene su longitud imponiendo refs442305.
Cada grupo separa role y subcase. Se revisan las88 raíces T/R y sus bindings.

Para raíces de hasta18 Store constructors, todos pueden asignarse a un
mismo role. Las construcciones mayores restantes son pares client/remote o
están repartidas por objetos unittest subtest distintos. Los seis casos de
desglose propio quedan en el JSON: DF11, DF12, DR23, DR27, DF20 y DR37.
La auditoría AST halló en DR37 los4+13 labs iniciales, dos de byte-budget y\nuno final SOURCE_BUDGET:20 por role, todos en contexto raíz;
DR24 puede acumular18 por role en el contexto raíz. No se divide un total por
subtests sin revisar sus cuerpos.

Cada fachada Client/Remote crea un Store propio. Un grupo retiene como máximo
20 Store y20 fachadas. Se permite incluso que distintas labs generen los mismos
UUID: no se usa la probabilidad de UUID4 como prueba de capacidad. Los Store
conservan construcción y retorno; las fachadas sólo retorno. La forma mayorante
del grupo codifica **4224 bytes**, superior al techo4096. Esta cota suelta no\ndemuestra un exceso real, pero tampoco acredita capacidad.

Los resultados seleccionados de los reducers originales retienen como máximo
cuatro metadatos escalares: NP01/02 conserva run_id/store_id/ticket/retry_tick;
los otros resultados seleccionan como máximo dos. Se revisan las asignaciones
result de ambos client_reduce y ledger_transition, y p/old de remote_reduce.
Arrays/payloads no se insertan en metadatos; conservan sus digests y evidencia
original donde corresponde. El modelo usa cuatro claves de17 caracteres y
valores ASCII de64, aunque la combinación sea mayor que las formas reales.

Los diccionarios literales de revisión incluyen evento/causal row, input_ref,
request, receipt, commit, head, retained_refs y witnesses. No llaman a helpers
ni validadores de producto. Sus tamaños conservadores incluyen:

- Independent3538 bytes; Store.transact2697; Client.perform1361;
  Drive.advance1756; start/receive/finish1320; variante negativa1397.
- Grupo4224; protocolo3767; retained1293; subcase2555; link663;
  registro DI07688 bytes.

Las variantes de excepción son menores que el techo causal uniforme3538.
Un protocolo consume como máximo READY y un resultado terminal, con dos
observaciones de exit; se conserva cada una. Los hooks sin barrier pausan tras
READY hasta kill. El barrier raw_mutate alcanza before_lock una vez; Drive
prepared reanuda una operación. No se instrumenta el hijo. Subcase cuenta los
25 result_refs máximos por raíz y los escapes de8 parámetros de128 caracteres.

CP01 no presupone event_bytes4096, ni las cotas de filas usan row4096 para\nlimitar su cuenta. CP02 conserva abierto el ajuste de grupo tras corregir\nla omisión de los tres últimos labs DR37 en la cuenta preliminar de I116.
Conservan bindings y formas escalares válidas: **no prueban que cada digest o
operando vaya a tener éxito**. Con3538 para las categorías causales y los
techos pequeños I115, las cuentas retenidas dan **29 páginas/58774619 bytes**.
Se conservan E<=30129 y321 frames, sin rehacer eventos como tarea pendiente.

## CP03: una parte cerrada; el árbol completo sigue pendiente

String4096 pertenece a strict_json sobre árboles de archivos JSON. digest_value
no lo impone a toda cadena de operando: cuenta bytes codificados y profundidad.
Confundir esos ámbitos impondría una regla nueva. Se conserva string4096 donde
existe, sin eliminar comprobaciones.

Para ORACLES se deriva mediante aritmética del encoding I70 un mayorante de595
bytes cargados por registro y **593221 bytes** para los997 elementos, depth<=2.
La forma mayorante incluye campos T/R, ambos hashes de head/commit y contadores.
Los prefijos sólo reducen el consumo. El JSON conserva cuerpo, bytes JSON y
suma con digest. Esto acota los guards de registros/listas, no estados de Store.

Siguen pendientes aserciones, estados/snapshots/receipts, requests originales
y canónicos, receipt/result originales, valores de protocolo, hashes del estado
independiente y proyecciones tipadas con auxiliares. Una proyección3538 no limita
su entrada. No se inventa16MiB a partir del techo32MiB del fixture o de un guard.

## CP04 y CP06: raw, mapas y metadatos

El censo AST del report verifica todos sus campos. El mayorante conserva997
oráculos,717 crashes, tres listas de718 exits,321 IDs y40 casos; sobreestima
cada uno de los12 grupos con los321 IDs. Incluye79 inputs originales y hashes,
indentación2, sort_keys de salida, newline y margen de representación float.
Resultado: **1667028<12582912 bytes**. Python/plataforma coinciden con los pins
stdlib. Source content y tracebacks no son campos del report completo PASS.
No se generó raw de producto ni se utilizó un prefijo inválido.

Contexto y launcher tienen cuatro materializaciones: mapas runner y
capture_inputs antes/después. Cada mapa<=4096 paths ASCII públicos de512
caracteres y hashes64; se sobreestima cada entrada con583 bytes y contenedor.
El resto del esquema normal se acota con2MiB: se conservan todos los campos y
se rellenan strings a4096 caracteres con escapes de6 bytes e integers32 dígitos.
El modelo resultante cabe en2MiB.

    context_or_launcher <= 4*(4096*583+2)+2097152 = 11649032 < 12582912

No se descuentan mapas iguales por interning. CP07 deberá demostrar el scope
futuro y la forma revisada; campos nuevos o rutas de error exigen su cuenta.
No se usa el techo12MiB de contexto para deducir que su contenido cabe.

## CP05 y CP07: correcciones concretas; todavía no habilitan

PJC115 debe explicitar dos puntos de propagación:

1. evidence_reader sólo sustituye unique_bytes/read_bytes. Reader.read conserva
   **file_bytes16MiB**. read_sidecar llama strict_json sin límite específico y
   SideWriter lo llama antes de escribir. Un sidecar en(16MiB,34MiB] puede cumplir
   el candidato y aun así ser rechazado. Es una incompatibilidad de admisión,
   **no prueba ni medida de exceso real del sidecar P01**.
2. SideWriter.write captura el default **12MiB** al definirse. Cambiar un número
   en un registro futuro no actualiza ese default. Hay que propagar el límite
   explícitamente a todos los puntos, además de las comprobaciones finales.

El addendum **PJC115-R1** propone límites de miembro existentes en un único
Reader de evidencia y file_bytes=index_sidecar_bytes para el parser del
sidecar, manteniendo depth32/string4096. Input Reader queda separado en16MiB.
OWNER36, raw12MiB, páginas2MiB y contexto/launcher12MiB conservan sus techos.
Sin quota key nueva, reset, Reader alternativo o cambio aplicado. Failure
envelope4096. JC21–JC23 **NOT_RUN** cubren16/34MiB, default12MiB y rechazo de
premisas pendientes.

Aún deben justificarse las12 allowances agregadas de sidecar y los metadatos
futuros:35474392 sigue siendo un plan condicional. El certificado permanecería
externo al paquete37, con path/hash; sus bytes y lecturas consumen input Reader.

El namespace, registro, contrato, certificado y autoridad futuros no existen.
No se pueden sellar sus hashes ni certificar el calendario exacto antes de
prepararlos bajo la decisión de implementación correspondiente. Se retiene la
fórmula por ámbito y multiplicidad: antes/después/autoridad/finish y checks late.
**Desconocido no significa0**; el margen histórico I96 de107570871 bytes no es
una cota de nuevas lecturas.

No se pide permiso mientras faltan CP02/CP03/CP05/CP07. El pendiente está localizado
por etapas en el JSON; el siguiente corte libre será I117 si no existe.
Cifras candidatas I115 y contratos vigentes intactos. R>=19037>16384 sigue
bloqueando la representación original;442305 no es certificado conjunto ni
cifra aplicada.

I86/I89/I92 INVALID_CAPTURE, sin suma/reanudación/reparación; IR03 NOT_READY.
P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial; D1–D4 cerrados e I1–I20/A52
aceptado. D5/H07/G01–G07/GI globales abiertos. GI06/12/18/24/30/36/42 requieren
evidencias reales o decisiones humanas propias. Sin proveedores/credenciales/
corpus reales, consumo/reservas, activación, promoción, despliegue, SQL/Java/Docker
nuevos, D6 ni inspección/limpieza operativa dev/run_data/D4. No se infiere
persistencia/recuperación integrada de PASS aislados.
