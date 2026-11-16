# I177 — Plan de cuatro bindings preparado; ninguna ejecución autorizada

Fecha: 2026-11-16, Europe/Madrid. Base:
`49a160ffe78e31ac6eff277db62157bfe44561b3`.

I177 prepara un plan concreto para resolver los cuatro cuerpos pendientes de
I175: raw, resultado, sello de componentes y autoridad. **No resuelve sus hashes
con datos inventados ni crea esos archivos.** Define ocho pasos, roles,
dependencias, schemas, custodia, criterios de aceptación y causas de parada.
La no admisión se mantiene: E01–E05 abiertos, E06 NOT_RUN y D5 sin cerrar.

## Ruta de revisión

1. Leer el [plan](../validation/D5-I177-FOUR-BINDINGS-EVIDENCE-PLAN.json),
   especialmente semantic_order, las ocho tareas y el plan B01–B04.
2. Contrastar schemas y condiciones con las seis anclas AST del runner,
   componentes y parser, sin ejecutarlos.
3. Revisar la [readiness documental](../validation/D5-I177-readiness-review.json),
   el [auditor](../validation/D5-I177-audit.py) y el [sello](../validation/D5-I177-integrity.json).

El grafo I175 y la revisión I176 conservan sus bytes, 495 rutas, 491 bindings
reales y cuatro pendientes. Las copias candidatas y el descriptor de autoridad
no se modifican. Las personas, firmas, aceptación y autorizaciones futuras
siguen sin asignar u obtener; los roles del plan no son nombramientos reales.

## Entregable por binding

| Binding | Productor y dependencia | Cuerpo que permitiría fijar el SHA | Máximo PRP173 |
| --- | --- | --- | ---: |
| B01 raw | Custodio autorizado; freeze final S03 | Stdout real e inmutable de componentes, con proveniencia y salida aceptables | 512 B |
| B02 resultado | Revisor independiente; B01 y manifest final | Revisión component-only que fija los SHA reales de raw y manifest | 768 B |
| B03 sello | Packager y revisor de hashes; B01/B02/manifest | artifacts exactos raw/resultado/manifest y copia del mapa de nueve fuentes | 2.048 B |
| B04 autoridad | Autoridad de admisión y revisor separado; cadena completa | Registry SHA y los 494 capture_inputs reales, sin autopin | 65.536 B |

Los cuatro SHA continúan null. Esos máximos son condiciones de serialización
ya propuestas, sin cambiar cuotas de producto. Una longitud conocida no
determina el hash de un cuerpo que aún no existe.

## Ocho pasos y evidencias de salida

| Paso | Trabajo futuro previsto | Salida y condición para avanzar |
| --- | --- | --- |
| S01 | Nombrar custodios/revisores, fijar scope y semántica de gates | Decisión atribuida: qué evidencia hace verdadero cada gate y qué autorización cubre cada acción |
| S02 | Obtener base calificadora si no existe evidencia aceptada exacta | Evidencia real o decisión justificada sobre evidencia previa; no sustituye E06 del manifest final |
| S03 | Aceptar recursos y congelar sucesor/registry/certificado/manifest | Scope, hashes y gates verdaderos por evidencia anterior, sin anticipar resultados futuros |
| S04 | Validación final de componentes, sólo con autorización explícita | B01 real, logs y proveniencia fuente/runtime/manifest antes y después |
| S05 | Revisar B01 y el freeze final | B02 sólo si la evidencia cumple y un revisor acepta componentes únicamente |
| S06 | Sellar cuerpos inmutables | B03 con hashes exactos, mapa de nueve fuentes y sin ciclos |
| S07 | Emitir autoridad sólo mediante decisión separada | B04 completo en staging autorizado, sin instalarlo en la ruta activa |
| S08 | Validar grafo, bytes, roles, límites y bindings finales | Ledger de 495 hashes reales, cero pendientes; rebind/captura siguen siendo decisiones separadas |

Todos los pasos están PLANNED_NOT_STARTED, con ejecución actual no autorizada
y sin artefactos producidos. El plan está listo para revisión documental,
no para ejecución. No fija plazos o garantías de éxito/recursos.

## El orden de hashes no basta para verificar un certificado

El DAG I175 evita ciclos de bytes, pero un certificado no puede declarar
atomicidad o CP07 verificados basándose en un run final aún no realizado.
S01 exige aclarar ese alcance y la evidencia anterior que lo justifica.
No se habilitan flags porque metadata y source_revision coincidan.

Si no existe una base aceptada exacta, S02 prevé una evidencia calificadora
por una vía separada y expresamente autorizada sobre el candidato negativo
congelado. Sólo evidencia real y revisión competente podrían justificar
posteriormente los gates de fuente. S03 exige además E01–E05 aceptados y el
protocolo de empaquetado revisado. Un resultado calificador no se transfiere
automáticamente al manifest final.

Después del freeze final, S04 exige su propia autorización y validación sobre
esos bytes y scope. El permiso para calificar no implica permiso para validar
de nuevo. Una decisión futura podría cubrir scopes explícitos, pero este
plan no concede ninguno. Si la definición de un gate exige evidencia posterior
que depende de su propio certificado, se para: hace falta una separación de
evidencia/protocolo revisada en otro alcance, sin reparación de fuentes/schema
autorizada aquí. No se rompe el ciclo semántico inventando un PASS.

## Runner, manifest y proveniencia

La fuente run_joint_lab.py exige --components-only, ejecuta diez componentes
sintéticos e imprime un raw por stdout. No escribe los cuatro archivos finales,
no produce resultado/sello ni contiene una lectura/fijación explícita del manifest. Por tanto, ni el comando
ni un stdout PASS vinculan por sí solos el run al manifest final.

El plan conserva una referencia textual al módulo y argumentos existentes.
El intérprete real deberá ser el ejecutable absoluto y SHA aceptados para el
scope, aún desconocidos; python3 en esa referencia no certifica el runtime.
**El comando no se ejecuta en I177.**

La custodia futura debe congelar raíz aislada/versionada y registrar comando,
cwd, runtime efectivo y cierre transitivo de fuentes, los nueve bindings del
manifest y diez IDs de test, antes y después. No basta con seis nombres I122,
un contador de módulos o una referencia histórica I127. Stdout, stderr, exit y
proveniencia se conservan inmutables en staging, sin sobrescribir resultados
históricos o escribir en rutas activas del repositorio.

Para B01 se exige la salida real del runner con schema cerrado, exit cero,
PASS verdadero, diez tests, cero errores/fallos, forbidden_imports vacío,
product_or_runner_imported false, functional_campaigns_executed cero y
closure/D5 false. elapsed_milliseconds debe ser el entero real 0..300000 y
new_module_count el entero real 0..9223372036854775807. No se simulan valores,
se convierte una auditoría AST en tiempo medido ni se altera FAIL a PASS.
Un fallo conserva su evidencia y bloquea la cadena; no hay retries o reparaciones
automáticos que oculten el resultado.

B02 fija SHA de los bytes reales de B01 y del manifest final aceptado. Su
decisión ACCEPTED_COMPONENTS_ONLY requiere revisión atribuida, sin cerrar
recursos o captura. B03 copia exactamente las nueve fuentes y hashea raw,
resultado y manifest. El manifest mantiene los tres hashes de consumidores
tardíos null intencionadamente para no formar ciclos con resultado/sello.

## Autoridad y validación final

B04 necesita E01–E05 aceptados, gates de fuente verdaderos, cadena E06 real,
identidad/validez/confianza de autoridad y una decisión explícita de emisión.
Sólo entonces corresponderían schema d5.joint-capture-authority.v2, fase
JOINT_EXPLICITLY_APPROVED y scope P01. Sus 494 pins deben ser exactos y reales;
AUTH queda fuera de su propio mapa.

El descriptor NOT_AUTHORIZED de I175 no se copia ni promueve a autoridad.
Tampoco se reutilizan autoridades I71/I77/I86/I89/I92 o INVALID_CAPTURE. Resolver
los hashes en staging no instala rebind ni lanza una captura. La instalación
y ejecución reales requieren decisiones separadas que este plan no suministra.

S08 recalcula los nueve cuerpos variables, cuotas Reader intactas, listings,
lecturas frescas, metadata/contexto/launcher/paquete, hashes y orden de bytes y
prerrequisitos semánticos. No hereda sin más el upper 266.402.939 del candidato
negativo ni trata el modelo parcial 483.562 como output final. El envelope
general PRP173 266.536.487 continúa condicionado, no garantizado para cualquier
sucesor. Si cualquier cuerpo o hipótesis falla, se mantiene la no admisión.

## Preservación y publicación

No se resuelve materialmente ningún binding en I177. E01–E05 abiertos, E06
NOT_RUN, certificado IMPLEMENTED_NOT_ADMITTED; sin SOURCE_CAPACITY_VERIFIED,
gate actualizado, propuesta/captura habilitadas o autoridad/destino nuevos.
D5/H07 de cierre abiertos; IR03 NOT_READY. P0 conserva 83 SUPPORTS_BOUNDED/
1 PARTIAL UI04.1; D1–D4 e I1–I20/A52 intactos; brechas globales y reales
pendientes. I86/I89/I92 INVALID_CAPTURE no se reanudan ni mezclan.

`python3 docs/validation/D5-I177-audit.py`: resultado esperado
PASS_STATIC_SOURCE_ONLY. Contrasta 675 pins contra Git, seis anclas AST, schemas,
diez IDs, cuatro bindings y ocho pasos ordenados con condiciones/rechazos.
Preserva 368 archivos publicados e inputs heredados. No importa, compila,
ejecuta o descubre tests/componentes ni invoca el runner o parser del producto.

Unidad de cinco archivos: plan, readiness, este documento, auditor y sello.
Rollback limitado a esos cinco archivos enumerados en work_unit. El diff supera
400 líneas por el plan trazable y auditor autocontenido; el exceso queda informado.
Runtime harness N/A: trabajo documental sin cambio runtime. Auditoría antes del
stage y tras commit, push autorizado y comprobación de remoto/árbol limpio.
Publicar no autoriza, admite ni resuelve hashes de evidencia ausente.

Sólo Git/JSON/AST documental. Sin ejecutar producto/componentes, tests,
benchmarks, schedule, introspección o mediciones; sin modificar fuentes,
contratos, cuotas, reservas o inputs vigentes. Sin inspeccionar ni limpiar
dev/run_data/D4; sin proveedores, credenciales, consumo, activación, promoción,
despliegue o D6.
