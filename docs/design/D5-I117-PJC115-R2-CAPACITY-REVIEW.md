# I117 — dictamen de capacidad y alternativa PJC115-R2

Fecha: 2026-11-10, Europe/Madrid. **PJC115 no queda habilitada.** CP02 tiene
un contraejemplo permitido por las fuentes para su representación original.
Se prepara PJC115-R2 como diseño reversible y revisable, sin aplicarlo. Su
representación conserva todos los testigos y cabe en los mismos candidatos
numéricos I115. CP03 global y CP07 exacto siguen abiertos; no existe todavía
certificado de capacidad conjunta. D5 permanece abierto e IR03 NOT_READY.

[Contraejemplo CP02](../validation/D5-I117-CP02-source-counterexample.json),
[diseño R2 y celdas CP05](../validation/D5-I117-PJC115-R2-design.json),
[operandos CP03](../validation/D5-I117-operand-envelope-progress.json),
[Reader CP07](../validation/D5-I117-reader-capacity-design.json),
[auditoría documental](../validation/D5-I117-audit.py) y
[sello](../validation/D5-I117-integrity.json).

## Dictamen por obligación

| Obligación | Resultado I117 | Qué falta para admisión |
|---|---|---|
| CP02 filas | ORIGINAL_REJECTED_FOR_UNIVERSAL_SOURCE_SCOPE; R2_DESIGN_FITS | Implementación y validación separadas de la representación R2 |
| CP03 operandos | DR37_LARGE_CAPTURE_ARGUMENT_BOUNDED; GLOBAL_OPEN | Cerrar todos los operandos originales y auxiliares por familia/raíz |
| CP05 sidecar | DECLARED_R2_NUMERIC_CELLS_BOUNDED | Vincular el esquema exacto futuro y satisfacer CP03/CP07 |
| CP07 Reader | CLOSED_MANIFEST_AND_READ_INEQUALITY_PREPARED; EXACT_OPEN | Archivos, hashes, grafo de lecturas y autoridad futura reales |

La resolución negativa de CP02 impide habilitar PJC115 sin cambios. No se puede
convertir una propuesta R2 ni una desigualdad condicional en un PASS de las
cuatro obligaciones. CP01/04/06 conservan sus alcances y dependencias I116;
CP08/09 no están autorizadas. JC01–JC20 y NW01–NW10 siguen NOT_RUN.

## CP02: un caso permitido excede el formato original

DR37 contiene 4 labs de límites reducidos, 13 de bounds, 2 de presupuestos de
bytes y 1 final SOURCE_BUDGET: 20 labs en el contexto raíz, sin subTest. La
partición por role/subcase I116 permite como máximo 20 Store y 20 fachadas por
grupo; no se divide un total por subtests sin revisar los cuerpos.

Cada lab crea un directorio físico distinto. Ninguna comprobación global exige
que los UUID run_id/client_id de labs diferentes sean únicos. UUID4 obtiene
aleatoriedad y fija bits de versión; no guarda un conjunto de identidades
anteriores. Una cota universal no puede sustituir esa ausencia por una
probabilidad de colisión pequeña. El caso de fuente toma los mismos UUID
válidos para esos dos campos en las 20 labs y comandos distintos; no ejecuta
UUID4, no modifica su implementación ni produce una captura.

Cada Client tiene su Store. Los Store conservan autoridad de construcción y
retorno; las fachadas, retorno. Client.perform llama a snapshot antes de la
mutación, también en la última captura rechazada por SOURCE_BUDGET. Los objetos
retenidos por el recorder sobreviven al cierre de directorios anteriores y
comparten frame, subcase, thread, role e identidad de grupo.

La forma mínima de 40 objetos distintos, con O1…O40 ordenados léxicamente,
20 Store con ambas autoridades y 20 fachadas con retorno, mide **4123 bytes**.
Incluso con claves de contexto mínimas supera row4096 en **27 bytes**. El
contraejemplo es una cota inferior de esa forma permitida, no una afirmación de
que esos identificadores exactos se asignen en P01. Puede fallar una inserción
anterior; no se atribuye un primer fallo concreto. Tampoco se ha demostrado
que la ruta habitual de UUID distintos desborde, ni medido un exceso real.

## R2: representación sin pérdida y cobro explícito

Se propone namespace nuevo y sidecar d5.joint-sidecar.v2. El grupo v2 mantiene
contexto e identidad y sustituye witnesses por witness_record_refs. La tabla
inline domain_witness_records contiene un registro v1 por par (grupo, objeto
físico), con witness_ref Y, group_ref W, object_ref O y todas sus authorities.
La lista conserva el orden canónico por object_ref; no se ordena por Y.

El diseño exige pertenencia única, ausencia de huérfanos y duplicados, igualdad
entre clave y witness_ref, group_ref correcto y validación de cada autoridad
contra los eventos originales. No combina objetos, identidades o grupos. Los
witness_refs de filas causales, retained y links siguen siendo listas completas
de O físicos. La reconstrucción literal del ejemplo produce exactamente los
bytes originales. Es una comprobación de JSON inerte, no del componente.

Cada alta de testigo conserva los cargos anteriores y añade **4 unidades**:
clave/contador Y, self witness_ref, group_ref y referencia del grupo. Añadir
una autoridad a un testigo existente cuesta la unidad original y no crea otro
Y. Reserva atómica antes de publicar la mutación; sin resets, descuentos,
liberaciones ni índices secundarios sin cobrar. La búsqueda sigue siendo
lineal. No se mantiene un lock del ledger durante llamadas originales o I/O.

La partición por role/subcase I116 reduce W a min(W,40) para las copias de
witnesses por retained. Sobre las 321 raíces I115:

    ahorro = Σ 4 * I_t * max(0, W_t - 40) = 146336
    altas adicionales = 4 * J = 4 * 9285 = 37140
    R2 <= 442305 - 146336 + 37140 = 333109 referencias

El candidato refs442305 queda intacto, con margen109196. El contador causal
puede llegar a 37651+9285=46936, seis caracteres con prefijo. Owners5190
requieren cinco. El mayorante de grupo R2 es **714 bytes** y el registro
individual **212 bytes**; ambos caben en row4096 sin cambiarlo. Los códigos,
lectores y validadores v2 no existen ni se han aprobado aquí. No se reinterpretan
sidecars antiguos ni se reparan capturas inválidas.

## CP03: argumento grande de DR37, sin convertirlo en cota global

La llamada final usa b'x'*(2097152+1), 2097153 bytes. Su base64 ASCII tiene
2796204 caracteres. Client.capture original no es el método observado;
Client.perform y Store.transact sí lo son. Se cuentan simbólicamente markers
I70, claves, delimitadores y auxiliares, sin crear el payload ni llamar al codec
o al producto. La expectativa seq1023 es conservadora frente al head inicial.

| Operando/auxiliar | Mayorante de bytes |
|---|---:|
| Digest del wrapper perform | 2796269 |
| Digest de args | 2796236 |
| Digest de op | 2796401 |
| JSON canónico de op | 2796358 |
| Suma del helper request de Store | 8388995 |

Cada operación observadora mantiene su presupuesto independiente de16777216.
No se suman ledgers de wrapper y Store ni se cobra como observado el argumento
raw de capture. Profundidad<=3. String4096 se aplica a árboles strict_json
persistidos/leídos; no es un límite universal de cadenas internas del digest.

Este argumento concreto cabe. No prueba que sea el mayor de toda la campaña.
Siguen pendientes árboles de assertion/estado/snapshot, otros requests y sus
auxiliares originales/decodificados/canónicos, receipts/resultados/protocolos
y estados independientes. Se conserva la cota ORACLES I116; ninguna familia
pendiente se sustituye por cero o por su digest proyectado.

## CP05: celdas estructurales del esquema R2 declarado

El JSON fija las 13 celdas y sus mayorantes literales, incluyendo delimitadores
y entradas de mapa. Grupos: G*600 + J*10 + J*300. Protocolos:
718*2048 + 934*2304 + 1438*128. El mensaje mayorante independiente ocupa2294
bytes con delimitador; incluye tags NP02 largos y cuatro selectores SHA64.
El protocolo completo ocupa3672, con READY, resultado terminal y dos exits.
Action y requested_kind se acotan por el catálogo ASCII de las fuentes originales,
no por cadenas arbitrarias con escapes. Se incluyen expresamente las dos
fixture declarations DI28 (512 bytes) y los seis objetos DI07 (12288).

El censo top incluye todos los campos existentes, la tabla nueva, 32 manifiestos
de página, 12 grupos, mapas runner y hasta484 pins antes/después. Los strings
dinámicos de entorno se rellenan hasta4096 con escapes de seis bytes; el basename
a255. Mide481815 frente a524288. Las tablas/frames vacías de este modelo se
cobran por sus celdas separadas. No se admite un capacity_summary nuevo sin
revisar la cota; un certificado futuro sólo aparece como input con path/hash.
Los SHA de anchura futura son placeholders, nunca pins verificados.

**Sidecar R2 <=30996862 bytes**, frente al candidato35651584 (34 MiB),
margen4654722. Con el tag de metadatos más largo, el techo causal uniforme
se amplía a3546: **29 páginas /58870179 bytes**, todavía bajo64 MiB.
Eventos<=30129 y frames321 se conservan. No se modifica I116 ni se rehace
la cota de eventos como obligación pendiente. Los candidatos package140513280
y evidence_read297799680 siguen siendo los de I115; no se han aplicado.

La conclusión numérica vale para estas formas y este manifiesto cerrado. La
implementación debe vincularlos exactamente y demostrar el éxito de operandos.
También debe resolver IC01/02 I116: pasar explícitamente el límite de miembro
sidecar por Reader.finish, parser, writer y launcher, en el mismo ledger de
evidencia. Input Reader conserva file16 MiB. No usar defaults heredados de
16/12 MiB ni introducir una cuota nueva para ocultar la incompatibilidad.

## CP07: manifiesto cerrado y contrato de lectura propuesto

La unión documental verificada contiene464 paths y84080766 bytes; el archivo
máximo mide9755833. No es un paquete de inputs funcionales admitido. Heredar
sin cambios las repeticiones antiguas da una cota286898223 frente a268435456;
es insuficiente para certificar, sin demostrar un exceso medido.

Se propone un protocolo versionado: BEFORE lee una vez todos los inputs y
valida registros/contratos contra ese snapshot explícito e inmutable; DURING
conserva las comprobaciones frescas de binding/clases; AFTER relee todo; FINISH
revalida todo por tercera vez con el mismo Reader y ledger. No llama a lecturas
anidadas antiguas como si fueran gratuitas. Es un cambio explícito del protocolo
de lectura, que requiere revisión propia de frescura; no se afirma equivalencia
bit a bit con el parser anidado anterior ni se cambian perfiles históricos.

El recheck fijo heredado es160864585-156012125=4852460. Base:

    3 * 84080766 + 4852460 = 257094758
    3*S + X <= 11340698
    84080766 + S <= 134217728

S incluye todos los bytes nuevos; X todas las nuevas lecturas adicionales al
calendario fijo. Ambos siguen desconocidos. Sólo si X=0 se demuestra por fuente,
S podría llegar a3780232. No se asume X=0. Cada archivo sigue<=16 MiB y cada
path público<=512 caracteres.

El manifiesto reserva7 archivos I117,12 nombres futuros fijos y1 autoridad sin
path asignado:484 paths como máximo. El JSON enumera los nombres. Los archivos
futuros, sus hashes, autoridad/destino y grafo exacto no existen; no se inventan.
Cualquier dependencia transitiva adicional obliga a revisar el manifiesto, top
y lecturas antes de admisión. Deben probarse fallos por cambios antes/durante/
después, symlinks/aliases y exceso de presupuesto sin resets ni otro Reader.

## Entrega y conservación

Se añaden únicamente estos siete archivos documentales y de auditoría I117.
HEAD50c49678568bae2abeefbe5fec0285f26c628283 y los32 archivos locales previos
se conservan. La auditoría comprueba hashes, formas JSON, AST y aritmética;
no importa ni ejecuta producto, runner, componentes o campañas. No se aplican
cuotas, no hay commit/push ni autoridad de captura/destino, credenciales,
proveedores reales, consumo, reservas, activación, promoción, despliegue o D6.
No se inspecciona ni limpia dev/run_data/D4.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL y UI04.1 siguen iguales. D1–D4 cerrados;
I1–I20/A52 aceptados. D5/H07/G01–G07 y GI globales abiertos. Las siete obligaciones
humanas/reales GI06/12/18/24/30/36/42 siguen pendientes. I86/I89/I92 continúan
INVALID_CAPTURE, sin reanudación ni mezcla. La siguiente evidencia necesaria es
la prueba global CP03 y la vinculación exacta CP07; el diseño R2 por sí solo
no autoriza implementación, ejecución ni cierre.
