# I125 — heap completo y alcance real de los900 segundos

Fecha: 2026-11-11, Europe/Madrid. Base:
`50c49678568bae2abeefbe5fec0285f26c628283`.

**La evidencia disponible no permite cerrar la cota completa de heap ni justificar
la terminación exitosa en900 segundos. PJC115-R2 no queda habilitada.** I125 deja
un dictamen verificable de no admisión por falta de prueba, no una cifra inventada
ni una afirmación de que I122 sea físicamente inviable. El certificado I122 sigue
IMPLEMENTED_NOT_ADMITTED y no se modifica. F/S y las vidas de I124 se conservan.

La restricción de no ejecución se respeta. Un contrato estático ya existente de
runtime/plataforma podría aportar parte de la evidencia sin ejecutar producto,
pero no aparece en los inputs revisados. El usuario confirmó: «No; dejar
dictamen de no admisión». Se registra su respuesta y se mantiene la no admisión;
no queda pendiente una respuesta sobre la ruta del contrato. Esta confirmación
no autoriza ejecutar producto/componentes ni aplicar cuotas.

## Qué significa heap completo

La afirmación mínima a justificar sería el pico de asignaciones dinámicas Python
y nativas del worker I122, incluidos runtime, originales y observador. Se debe
indicar si se habla de bytes solicitados o de heap comprometido del allocator.
La segunda métrica añade arenas, retención y fragmentación. Ninguna equivale por
sí sola a RSS: stacks nativos y otros mappings tienen cuentas distintas.
Coordinador e hijos necesitarían cuentas por proceso si se afirmase capacidad
conjunta del host. La falta de cota del propio worker ya impide aquella admisión;
no se amplía aquí la solicitud a una exigencia de certificar RSS.

El JSON de cobertura enumera11 propietarios de memoria. No admite que un término
sin prueba valga0 ni que un tamaño serializado se presente como heap:

| Propietario | Qué falta para una cota completa |
| --- | --- |
| Runtime/imports/extensiones nativas | Asignaciones iniciales y vivas, fuera de FIELDS |
| Originales retenidos y fixtures | Estado privado completo; ser opaco evita copia, no elimina memoria |
| Observer persistente y hojas | profile/entry/specs, callbacks/parches, locks/Condition, weakrefs, escalares |
| Contenedores/memo del clonador | I124 es un modelo upstream condicional, sin atestación binaria completa |
| Marcos/generadores/tracebacks | Tamaño de cada objeto y asignaciones auxiliares; vidas ya sobrecontadas |
| Proyección/digest/operaciones de fase | sorted, registros temporales, filas nuevas y buffers |
| JSON/Unicode/árboles decodificados | Coexistencia de árboles, texto y bytes, más temporales de codecs |
| Reader/PhaseBytes | Headers, mapas, listados, datos parseados y payload de lecturas |
| Páginas | Listas/headers, concatenaciones y temporales además de los payloads |
| Tee/StringIO/raw | Capacidad interna, snapshots, texto y árbol del raw que se mantienen a la vez |
| Dominio de asignación | Modelo del allocator y métrica exacta, sin sumar o confundir RSS |

Se precisan tres subcotas documentales, sin atribuirles cobertura total:

- Reader: chunks leídos más cuerpos unidos tienen hasta
  `2*266337791 = 532675582` bytes de **payload** en el grafo exitoso worker I122.
  Contar todo el calendario sobrecuenta retenciones; PhaseBytes comparte los
  cuerpos. No incluye headers, árboles JSON ni listados del filesystem.
- Páginas: cuerpos y chunks históricos distintos<=134217728 bytes de payload,
  incluido el memo anterior a flush. Permanecen adicionales objetos/temporales.
- Raw: para una representación Unicode de hasta4 bytes por code point y una
  copia UTF8, `5*12582912 = 62914560` bytes de payload. Esto no acota la capacidad
  de StringIO, todas sus copias ni el árbol JSON resultante.

No se suman esas cifras para presentar un heap completo. I124 conserva además
su modelo parcial de builtins de23096917808804736 bytes globales: sigue siendo
un mayorante condicional muy holgado, no un pico real, una necesidad de memoria
ni una cota atestada del proceso completo. La identidad SHA del intérprete no
atestigua por sí sola las asignaciones del runtime, libs nativas o allocator.

Los guards no subsanan esta falta: BoundedOutput.write codifica antes de comprobar
raw_bytes; PageSink.append codifica antes de comprobar event_bytes; encode forma
json.dumps y luego bytes; finish forma/codifica salidas antes de comprobar su
longitud. digest_value puede ordenar claves antes del cargo de sus elementos.
Las formas fuente cerradas de CP03/CP05 ayudan a limitar esas entradas, pero un
check posterior no es por sí mismo un límite preventivo de asignación.

Las24 cuotas propuestas no contienen heap_bytes, presupuesto de memoria de
worker ni un modelo de allocator. No se añade ni cambia una cuota para llenar
ese hueco. Tampoco se afirma que el heap real sea infinito: lo que falta es una
prueba numérica completa y su comparación con una capacidad declarada.

## Qué limita exactamente900

La ruta activa conserva wait_worker=late.wait_worker, que llega a
`typed.wait_worker`. Este ejecuta `process.wait(timeout=900)` y devuelveFalse
cuando vence el timeout. No mide process_time, ciclos ni CPU consumida.

El orden real de launch es:

1. Lecturas/validación inicial, planificación, creación de canales/proceso y
   READY/RELEASE: fuera de process.wait.
2. wait_worker: ventana de espera del coordinador con argumento900 segundos.
   Dentro de esa espera el worker realiza sus checks posteriores a RELEASE,
   import, suite/observación, finish y escritura final.
3. stop_owned, lecturas frescas after/finish y checks: fuera de esa ventana.
4. Lectura/parse/validación del paquete, agregación y publicación del contexto:
   también fuera de esa ventana.

Por tanto, ni siquiera una finalización del worker observada antes del timeout
prueba que **todo el flujo** haya durado<=900. Si la solicitud se refiere sólo a
la ventana del worker, sigue faltando probar terminación exitosa dentro de ella.
El wait20 del handshake/Condition tampoco certifica progreso o éxito.

La CPU del proceso, su tiempo transcurrido y el tiempo extremo a extremo son
tres métricas diferentes. Los17164544043094 pasos de clone de I124 no tienen
una conversión WCET sustentada a ninguna de ellas; además falta trabajo ajeno a
clone. Dividir la cota por900 fija una exigencia, no demuestra un servicio.

La revisión incluye un contramodelo **puramente lógico, no ejecutado**: las
mismas fuentes y cantidades de trabajo, coordinador activo y worker sin servicio
de CPU durante901 segundos tras RELEASE. No hay en los inputs una garantía de
plataforma que excluya ese calendario. El timeout puede detenerlo sin una captura
completa. Esto refuta la inferencia «trabajo finito + timeout => éxito antes de900»;
no predice que el host actual vaya a fallar ni representa una prueba sintética.
No se durmió, pausó, lanzó o señalizó ningún proceso para construirlo.

Optimizar copias podría reducir trabajo, pero no reemplazaría el contrato de
servicio temporal. Una medición futura tampoco sería automáticamente un WCET;
no se ejecuta producto, componente o benchmark ni se inventan frecuencias mínimas.

## Dictamen concreto

El expediente I125 hace explícitos ocho predicados necesarios: cota completa de
heap, métrica/capacidad, modelo de runtime, trabajo de la ventana reclamada,
servicio CPU/latencias, terminación exitosa<=900, componentes y CP07 real.
**Ninguno obtiene un PASS nuevo en I125.** La decisión documental es
DO_NOT_ISSUE_SOURCE_CAPACITY_VERIFIED. Es falta de evidencia, no una autorización
pendiente que se resuelva confirmando una ejecución ya prohibida.

Para cambiar el dictamen harían falta un contrato estático concreto de
runtime/plataforma y una prueba completa de asignaciones/trabajo vinculada a
las fuentes; además siguen siendo necesarias las evidencias separadas de
componentes y CP07. No se vuelve a abrir el conteo F52018/S1759 ni la envolvente
de53778 generaciones resueltos por I124.

La cota completa de heap y los segundos permanecen **null/no probados**, nunca0.
No se produce certificado SOURCE_CAPACITY_VERIFIED, autoridad/destino, captura
ni modificación del registro. Los archivos I125 tampoco se incorporan a los
inputs I122; el calendario Reader y sus pins conservan su ámbito anterior.

## Verificación y conservación

`python3 docs/validation/D5-I125-audit.py` sólo comprueba JSON, AST, hashes,
orden de llamadas, aritmética de subcotas y flags. PASS_STATIC_SOURCE_ONLY es
consistencia del dictamen, no prueba de recursos. Conserva102 archivos previos,
los bytes de la candidata, cuotas, certificado y evidencias anteriores. No
importa, compila ni ejecuta producto, candidata o componentes.

P0 sigue83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 conservan
aceptación. D5/H07/G01–G07 y GI globales abiertos; GI06/12/18/24/30/36/42 reales
pendientes; IR03 NOT_READY. I86/I89/I92 INVALID_CAPTURE sin reanudación ni mezcla.
Sin proveedores/credenciales, consumo, reservas, activación, promoción,
despliegue, D6 ni commit/push. No se inspecciona ni limpia dev/run_data/D4.
