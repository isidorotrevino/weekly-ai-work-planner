# D5 I68 — revisión documental GI33/GI34

Fecha: **2026-10-26**, Europe/Madrid. Base I67 `6aee6c5cfe0c50ac9f0b8b2d5078bbc6ee4d1458`. **DOCUMENTARY_REVIEW_COMPLETE_WITH_OPEN_CRITERIA**.
[Matriz y pendientes](D5-I68-matrix.md) · [Referencias estructuradas](D5-I68-results.json) · [Integridad](D5-I68-integrity.json) · [Contrato I66](../design/D5-I66-TRACEABILITY-DESIGN.md) · [Resultado I67](D5-I67-results.md).

## Dictamen

**UI01.2, UI04.1 y UI09.2 siguen PARTIAL; agregado81 SUPPORTS_BOUNDED /3 PARTIAL sin cambios.** GI33/GI34 mantienen PARTIAL en su evaluación de evidencia. El trazador I67 aporta procedencia, integridad y un inventario ejecutable de carencias dentro de doce entradas, pero no produce el contexto histórico que no fue capturado. Sus48 PASS prueban el auditor en el perímetro TT48; el FINDINGS de la lectura real es esperado. Nada de ello cierra estas obligaciones o convierte los1294 registros leídos en tests nuevos.

Se reevalúan sólo las tres partes dirigidas. Las otras81 partes heredan I65, incluidos los límites físicos T/R v1 I62, CREATE nativo I56 y los intercalados finitos I65. GI38/GI39/GI40 conservan su soporte acotado previo, todos los GI globales y D5/G01–G07 OPEN, closure=false. No promoción histórica30/35→35/35.

## Qué permite conservar I67

Los sellos I65/I66/I67, los354 inputs pre/post de la campaña de auditoría y las doce referencias históricas preservan bytes y trazabilidad declarada. Se mantienen44 ocurrencias de grupo,1294 de test y388 filas de escenario, incluidas las múltiples variantes de13 casos. Los602 registros I34/I36 y692 I64 se conservan por campaña, sin sumar repetición como prueba nueva. El contexto de invocación padre basta para identificar el mismo comando en varios grupos cuando hay referencia explícita; no exige fingir una llamada CLI independiente por grupo.

Veintiún grupos I64 tienen ese comando padre registrado; los23 grupos I34/I36 carecen de comando de campaña observado. demo_command sigue siendo demo. I34/I36 conservan MATCH histórico y CHANGED actual por ampliación del namespace pertinente, sin reescribir los inventarios para volverlos vigentes. Las tres campañas acumulativas I34/I36/Python321 muestran entorno incompleto en distintas dimensiones; kernel de Python321 I64 no consta. No se sustituye por el contexto del auditor ni se convierte el hash de source en prueba de ejecución. test_postgres_adapter conserva target MOCKED_QUERY_NO_DB, sin SQL V30 ni Postgres real.

UI01.2 recibe contexto/run_id donde constan, pero923 ocurrencias de test de I34/I36/Python321 no tienen scenario_refs de I67. Puede haber oráculos o identidades compartidos en esos informes: la ausencia del enlace por test impide atribuirlos automáticamente, y no se declara que toda esa evidencia bruta sea inexistente. Crear un UUID del expediente no reemplaza el run_id del dueño. UI09.2 retiene versiones declaradas y hashes por ámbito, sin certificar versiones/capacidades de proveedores fuera de P0.

## Hallazgos de granularidad y evidencia recuperable

La inspección documental del raw distingue ausencia en la cabecera de ausencia absoluta. **Los191 escenarios de HC/HF/IC/UQ/RV/NA contienen etiquetas point en eventos y189 contienen operation.** El JSON I68 conserva un ejemplo y cantidad por fila, sin modificar esos raws o el trazador. Por tanto, el FINDINGS de I67 no justifica recapturar esos191 escenarios sólo para rellenar una clave superior. Hace falta un adapter con schema/roles/punteros y controles revisados para normalizar lo existente, o revisión documental causal específica.

Una etiqueta point puede ser final, SPAWN, before_passive u otro hito lógico; no es por sí sola una frontera física con identidad/efecto acreditados. Los READY/gates y los oráculos mantienen el alcance de sus revisiones previas; esta revisión de metadata no reevalúa todas las garantías causales. NA35/NA36 (filas46/47 del raw NA) no tienen operation en sus eventos: son controles de evidencia, y un futuro contrato podrá justificar N/A si procede, sin inventar operación o nuevo efecto nativo.

HF tiene30 e IC24 referencias de método sin definición AST individual, porque sus métodos proceden de factories. Las funciones early_test/fsync_test y client_test/remote_test están disponibles con hashes/anclas; un binding ID→factory/argumentos puede revisarse como derivación de fuente. No hace falta ejecutar factories para reconstruir una historia ni llamar ausencia total de código a METHOD_AST_NOT_RECORDED.

Otra limitación es que la clasificación por test en I67 es local: **317 tests figuran COMPLETE_RECORDED_SCOPE, pero120 enlazan escenarios clasificados INCOMPLETE**. El código calcula la fila de test por existencia de scenario_refs, comando y método; luego calcula los faltantes de cada escenario por separado. No propaga la clasificación del hijo ni la metadata de entorno a aquella fila. Esto se registra como límite del agregado, sin invalidar los hechos históricos ni corregir código bajo una autorización documental. No usar ese tag local como puerta de suficiencia transitiva. Los197 escenarios GX/FN/CE con clasificación técnica completa tampoco certifican el conjunto de UI04 o la ejecución real de proveedor.

## Pendientes de captura nueva y normalización

CP01–CP14 fijan requisitos para un contrato futuro, no una implementación aprobada: nueva invocación/contexto/raw con identidad propia; manifest por grupo con target/versiones y referencia al padre; lifecycle por test/escenario, run/Stores/comandos y frontera/oráculo/resultado enlazados; N/A de controles motivado; fallos/skips/NOT_RUN conservados; inventarios específicos pre/post; límites y preservación de P0. La captura nueva debe cubrir los datos realmente ausentes en el perímetro finito que se acuerde, distinguiendo valores medidos en el nuevo run de expectativas de fuente.

CP05/CP08/CP12 son aprovechamiento y normalización de evidencia existente, no orden de reejecutar campañas. CP13 exige que una futura agregación considere escenarios hijos y metadata aplicable antes de afirmar completitud de test/grupo. CP11 conserva irreversible en este corte la carencia histórica: una campaña nueva puede aportar evidencia prospectiva para el alcance aprobado, nunca completar stdout/argv/kernel/run_id de I34/I36/I64 retrospectivamente. Elegir qué campañas, variantes, observers o wrappers cubrirá aquella captura requiere contrato y matriz antes de implementar; no se fija aquí un presupuesto o ejecución nueva.

La mera presencia de todos los campos no prueba la cadena causal ni persistencia integrada. La revisión posterior de la futura evidencia seguirá separada de tests del capturador/auditor, publicación y cierre global. Las siete puertas reales/humanas conservan su requisito propio.

## Verificación y continuidad

I68 usa lectura de JSON, fuentes/AST, documentos, hashes y Git; **cero imports o ejecución de producto, harness, trazador I67, auditor I38, discovery, campañas funcionales, SQL/Java/Docker o red**. Los TT48 y la CLI leídos siguen siendo ejecuciones históricas I67. Se contrastan sellos/inputs,44 grupos,388 escenarios/punteros,120 diferencias de granularidad y14 pendientes. Sólo se añaden cuatro documentos I68. La revisión de higiene completa conserva los avisos de tamaño y su umbral temporal12MiB sin tocar el checker; no autoriza publicación.

D1–D4 cerrados y D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. H07, D5 global/G01–G07 y GI33/GI34/GI38/GI39/GI40 abiertos, closure=false. GI06/GI12/GI18/GI24/GI30/GI36/GI42 reales/humanos no se trasladan a D6. P0 vigente: sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6; sin inspección/limpieza operativa dev/run_data/D4. Publicado sólo hasta I52; I53–I68 locales, sin push ni nueva lectura remota. Contrato de captura/normalización y publicación de SHA concreto son decisiones posteriores distintas.
