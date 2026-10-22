# D5 I23 — contrato integrado G01–G07 para revisión

Fecha: 2026-10-22. **PREPARADO PARA REVISIÓN; contrato aún no aprobado.**
D5 global abierto. No añade SQL, conectores ejecutables ni pruebas de integración.
[Hito local aceptado](D5-LOCAL-SYNTHETIC-approved.md) ·
[Auditoría de alcance](D5-I21-SCOPE-AUDIT.md) ·
[Matriz propuesta](D5-I23-GLOBAL-INTEGRATION-REVIEW.md) ·
[Comprobaciones documentales](../validation/D5-I23-design-review.json).

English: proposed integrated contract for the remaining global D5 work. The user
selected deterministic extraction, D2 ownership, separate observed source profiles,
text-only Drive inputs and blocking Plane writes until atomic conditions are proven.
The integrated contract still requires review. No real services, credentials,
activation, migration promotion, deployment or implicit D6 work.

## Autoridad y decisiones

| ID | Decisión | Estado |
|---|---|---|
| A53 | Continuar G01–G07, conservando límites y contratos aprobados | Solicitud expresa |
| A54 | Extracción determinista de elementos explícitos, perfil por formato y procedencia; sin inferir épicas/dependencias ausentes | Elegida expresamente |
| A55 | D2 conserva contenido aprobado; Plane recibe proyección y una edición remota de campos sincronizados bloquea hasta revisión | Elegida expresamente |
| A56 | Perfiles separados para registro y checklist observados; muestras y routing Gentle-AI faltantes separados, sin declarar G01 completo | Elegida expresamente |
| A57 | Drive: Markdown/texto y Google Docs exportado a texto; conservar bytes/revisión observada/formato. PDF/DOCX fuera del primer perfil | Elegida expresamente |
| A58 | Bloquear escrituras remotas Plane hasta demostrar condición atómica; diseñar proyección, conciliación y pruebas simuladas sin rebajar D2 | Elegida expresamente |

A53 inicia el diseño de continuidad; no autoriza conectar servicios reales ni
alterar D1–D4. El hito local I1–I20 aceptado en A52 no cambia su perímetro. Las
interfaces siguientes son propuestas: aprobarlas y validar fixtures no demostraría
por sí solo G01–G07 completos.

## Descubrimiento comprobado en este corte

La ruta local autorizada conserva las tres muestras históricas. Una comprobación
actual de bytes/hash confirma que plan narrativo y checklist coinciden con I1;
el registro tabular ha cambiado. No se reejecutó su parser ni se atribuyen conteos
nuevos de filas. Los hashes/paths privados quedan fuera de esta documentación.

La inspección acotada localizó pruebas de selección de modelos y conformance
LiteLLM; sus nombres/AST y referencias no acreditan el script de routing Gentle-AI
ni una gramática completa de sus planes. No se ejecutó código de ese checkout,
leyeron credenciales ni contactaron sus servicios. Una declaración de imagen
Plane indica `v1.4.2`: es configuración declarada, no versión desplegada comprobada.
La release del producto no equivale al número de versión de su API.

## Flujo y contratos comunes propuestos

Captura → artefacto reconstruible → extracción por perfil → propuesta revisable →
aplicación D2 explícita → proyección Plane aprobada → conciliación y recibo.
Cada frontera conserva identidad, versión, hash y autoridad. Leer, capturar,
extraer o seleccionar referencia nunca aprueba la siguiente frontera.

- Fuente: registro explícito proyecto/documento, namespace externo, ámbito de
  conector y perfil/versiones. UUID internos estables; nunca nombre, ruta, línea,
  fecha o similitud como identidad persistente de tarea.
- Observación: bytes exactos y SHA-256, formato/MIME/exportación, localizadores,
  revisión declarada/observada, grado de procedencia y diagnósticos. Un mismo hash
  de bytes no colapsa metadatos de observación distintos ni autentica el origen.
- Propuesta: IDs explícitos, tipo REQUIREMENT/EPIC/TASK, texto/proyección permitida,
  vínculos explícitos, revisión/snapshot completos, versiones esperadas, razones
  y hash del manifiesto cerrado. No comandos, secretos ni instrucciones ejecutables.
- Revisión: aceptación/rechazo del manifiesto íntegro por autoridad separada;
  cambio de texto, referencia, perfil, destino o versión invalida sus pins. Revisión
  de extracción, efecto D2 y proyección externa no son autorizaciones transferibles.
- Recibo: command_id, request_hash, ámbito, outcome y versiones antes/después;
  mismo comando/contenido recupera el efecto histórico, contenido distinto entra
  en conflicto. Un replay no restaura estado ni crea autorización vigente nueva.

Son contratos conceptuales; esta propuesta no declara un esquema JSON/SQL
implementado. Cualquier ampliación de persistencia exige diseño/matriz y aprobación
antes de SQL nuevo, sin modificar propuestas históricas selladas.

## G01 — formatos y routing

Mantener perfiles versionados independientes y registrar las muestras positivas,
negativas y fronterizas que justifican cada uno. Lo desconocido o ambiguo produce
BLOCKED con bytes conservados; no se repara, normaliza o interpreta silenciosamente.
El registro de ocho columnas tiene documento+ID; los UUID de candidatos checklist
I1, ligados a revisión/línea, **no** son identidad estable entre revisiones.
Una checklist sin ID persistente requiere correspondencia explícita revisada o
permanece solo como preview; no se adopta por título o posición.

El routing de proveedor debe ser un contrato separado de extracción, ligado a
versión y capacidades admitidas. La fuente no puede imponer comandos, modelos,
cuotas, prioridades, permisos o fallback. Un script existente solo puede reutilizarse
tras identificar su versión e interfaz y revisar sus efectos; encontrar una prueba
LiteLLM no satisface esa identificación. A56 mantiene separados el registro y la
checklist: se reutilizan los perfiles observados sin presentarlos como Gentle-AI
universal. El plan narrativo conserva captura/preview; su semántica no se inventa.

## G02 — captura incremental Drive

El ámbito del conector debe fijar cuenta/drive, corpus y allowlist; cambiarlo
invalida el cursor anterior y exige reconciliación explícita. El diseño separa
cursor de captura, referencia de revisión D5 y aplicación D2: avanzarlos no es
la misma operación.

Propuesta de recuperación: obtener ancla del feed antes del inventario inicial,
recorrer páginas, capturar y deduplicar hechos, y reproducir desde el ancla. No
promete un snapshot global de Drive ni todas las revisiones intermedias. Confirmar
un cursor solo tras conservar durablemente cada evento de su página, sus bytes o
un diagnóstico terminal explícito y recuperable. Fallo transitorio no pierde la
página. Una fuente en cuarentena no se convierte en referencia elegible por avanzar
el feed. Pérdida de acceso, removals o archivo ausente nunca borran/cierran D2.

Distinguir bytes de blob de bytes exportados. Guardar revisión/token y metadatos
observados antes/después, MIME/exportador y hash exacto; si cambian, bloquear y
reintentar bajo presupuesto. Igualdad de metadatos no prueba captura atómica.
Una exportación sin vínculo acreditado a una revisión concreta conserva grado
OBSERVED_EXPORT; no se etiqueta como contenido inmutable de esa revisión.
Selección/aplicación exige revisar ese grado; el parser no lo eleva por sí solo.
A57 limita el primer contrato a Markdown/texto y Google Docs exportado a texto
plano, con el MIME y versión del exportador/perfil registrados. PDF/DOCX y otros
formatos quedan fuera. Los límites locales siguen explícitos, sin truncar al máximo
admitido por la API. Texto exportado sin estructura reconocida conserva preview: no
se interpreta como Markdown por su extensión o por contener frases de requisitos.

## G03 — proyección y conciliación Plane

D2 es autoridad del contenido aprobado (A55). El binding explícito debe fijar
instancia, workspace/proyecto, tipo, UUID interno, ID remoto y versión/API/capacidades
verificadas. No adoptar work items por nombre ni convertir un estado remoto en
READY/DONE o prueba de ejecución. Definir una whitelist de campos proyectados;
los campos ajenos se preservan. No equiparar automáticamente epic D2 con module,
parent o tipo Epic de una edición Plane.

Antes de escribir se exige versión/hash D2 todavía vigente, aprobación del payload,
base remota conocida y condición remota atómica. Una edición remota en campos
sincronizados abre conflicto aun siendo D2 autoridad; no se sobrescribe bajo la
misma aprobación. GET+PATCH no es CAS y una verificación posterior no recupera una
edición ya perdida. Si esa capacidad no está acreditada, la escritura queda
bloqueada (A58). No se diseña ni se incorpora una pasarela/patch del lado Plane
como parte implícita de este contrato. La prueba simulada de CAS sirve para probar
el bloqueo y las precondiciones; no acredita esa capacidad en un servidor real.

Crear también necesita correlación estable y unicidad/deduplicación acreditadas.
Timeout/respuesta perdida tras un envío produce UNKNOWN: consultar por correlación
estable y conciliar antes de reintentar. Cero resultados de una lectura eventual
no prueba que no se creó; múltiples resultados bloquean. Sin capacidad demostrada
no hay retry ciego ni claim exactly-once. ACK local no acredita efecto externo.
No efectuar llamadas de red mientras se sostienen locks SQL de dominio.

## G04 — adaptadores y cuotas

Proponer una ficha por proveedor/release: capacidades, modo de autorización,
ámbito, límites de concurrencia, dimensiones/unidades, ventanas observadas,
frescura, procedencia y códigos de indisponibilidad. Mantener desconocido, cero,
ilimitado declarado y observación caducada como estados distintos. Solo usar
cuota válida acreditada; desconocida/caducada bloquea elegibilidad sin crear
capacidad ni sumar proveedores/unidades.

Los dobles sintéticos prueban el contrato, no permisos unattended, límites reales,
latencias o autenticación del proveedor. Reutilizar guardas/cuentas/reservas D3 y
protocolo D4; no activar workers u operaciones para validar este diseño. No habrá
fallback automático de pago, login real, token en Context Pack o sondeo de cuentas.
La validación empírica de CLI/proveedor sigue bloqueada por el límite vigente y
requiere autorización propia; no se obtiene desde documentación de APIs.

## G05 — requisitos, épicas y grooming explícito

A54 admite solo elementos declarados e identificables; no extraer requisitos de
narrativa libre ni fabricar épicas para cubrir el dominio. Un documento puede
proponer tareas sin requisito/épica. Vínculos y dependencias solo desde referencias
explícitas, resueltas por UUID/clave registradas, con proyecto/tipo compatible y
validación de ciclos/guardas D2; los claims Status/Verified siguen inertes.

Propuesta de whitelist: requisito → requirement_key/title/description, inicialmente
DRAFT; épica → epic_key/title, inicialmente BACKLOG; tarea → task_key/title/description,
inicialmente BACKLOG. El modelo D2 vigente no ofrece description en epics: conservar
texto adicional como evidencia D5, sin inventar columna. V10 aporta row_version de
épica; las condiciones se contrastan con V30, no solo con V1 aislada.

Antes de aplicar, exigir correspondencia explícita, manifiesto/revisión propios,
CAS del destino completo y coherencia de relaciones. No promover estados por la
palabra «groomed», planificar, asignar operadores, crear operaciones ni eludir
guardas de edición local I14/I18/I20. El criterio mínimo de grooming será completitud
estructural/procedencia y resolución explícita de referencias; la suficiencia de
negocio y cualquier transición de workflow requieren aceptación separada.

## G06/G07 — aceptación y secuencia de validación

1. Revisar este contrato y la matriz con A54–A58 incorporadas. Mantener G01–G07
   abiertos; una aprobación de diseño no es aceptación de capacidades implementadas.
2. Proponer un primer corte implementable offline: envelopes/perfiles, propuestas
   explícitas y dobles de Drive/Plane/cuota, sin SQL ni servicios reales. Su aprobación
   será una decisión nueva sobre un alcance concreto.
3. Si se autoriza persistencia después, laboratorio sintético nuevo separado de
   dev/D4 y del hito local aceptado; regresiones propias y evidencia por inputs.
4. Validación real por integración solo con autorización separada, entorno/versiones
   identificados y capacidades demostradas; nunca sustituida por mock PASS.
5. Aceptación global D5 solo con decisión expresa, requisitos/limitaciones revisados
   y evidencia integrada suficiente; no se deduce de terminar esta lista documental.

La matriz distingue DESIGN_NOT_EXECUTED, evidencia sintética y validación real
pendiente. Un fallo o una capacidad desconocida conserva bloqueo visible. D6 retiene
hosting, identidades/permisos productivos, retención, promoción y despliegue.

## Primer incremento offline propuesto para autorización separada

Alcance concreto: reutilizar los parsers locales existentes sin cambiar sus
perfiles; añadir envelopes/validadores de contrato, propuestas tipadas y dobles en
memoria de captura, Plane y cuota. Fixtures públicas exclusivamente sintéticas.
Un flujo de demostración une captura de fixture, extracción o candidato tipado
explícito, revisión simulada, efecto D2 **en memoria** y proyección Plane simulada.
Un doble con CAS permite pruebas negativas/positivas; la configuración remota real
permanece bloqueada por A58. No hay cliente HTTP, SQL, Docker, daemon o llamadas CLI
a proveedores; no se reutilizan credenciales ni configuración del checkout privado.

Cobertura propuesta de este primer corte: GI01/GI02/GI03/GI05/GI10/GI13/GI14,
GI19/GI21/GI23/GI25/GI26/GI27/GI31/GI32/GI35/GI37/GI41, **18 criterios S**.
Los tests deberán contrastar resultados y ausencia de efectos reales; su número
final puede superar 18. No se promete durabilidad/reinicio o concurrencia SQL en
un doble en memoria. Los otros 17 criterios S y los siete R quedan pendientes.
No se denominará a este corte implementación completa de Drive, Plane o grooming.

Los candidatos REQUIREMENT/EPIC del doble tendrán un contrato tipado explícito de
fixture, identificado como tal. No introducen marcadores nuevos en documentos
privados ni fingen que el registro/checklist real declara esos tipos. El registro
produce candidatos TASK; checklist sin identidad estable permanece preview; el
contrato de correspondencia/importación persistente adicional queda para otro corte.

Aprobar este contrato no autoriza por sí solo el incremento: la decisión debe
mencionar expresamente ese alcance offline. Tampoco autoriza GI06/12/18/24/30/36/42
reales, SQL nuevo, aplicación D2 persistente o cierre de ninguna brecha global.

## Fuentes primarias consultadas el 2026-10-22

La documentación pública es referencia de diseño; no acredita la instancia local.

- [Drive: retrieve changes](https://developers.google.com/workspace/drive/api/guides/manage-changes): el feed usa tokens y paginación; no equivale a historial completo de snapshots.
- [Drive: changes.list](https://developers.google.com/workspace/drive/api/reference/rest/v3/changes/list): removals pueden indicar borrado o pérdida de acceso; no deben convertirse en borrado D2.
- [Drive: files](https://developers.google.com/workspace/drive/api/reference/rest/v3/files): headRevisionId está limitado a contenido binario; version no es hash de exportación.
- [Drive: download/export](https://developers.google.com/workspace/drive/api/guides/manage-downloads): descargar blobs y exportar documentos son operaciones distintas; sus límites no sustituyen los locales.
- [Drive: revisions](https://developers.google.com/workspace/drive/api/guides/manage-revisions): la lista puede omitir revisiones antiguas; no prometer reconstrucción íntegra posterior.
- [Plane: introducción API v1](https://developers.plane.so/api-reference/introduction) y [API v2](https://developers.plane.so/api-reference/v2/introduction): existen contratos de versiones diferentes; no asumir compatibilidad con la release declarada.
- [Plane: actualizar work item](https://developers.plane.so/api-reference/issue/update-issue-detail): la página revisada describe PATCH/correlación, pero no acredita aquí una precondición atómica If-Match. No se concluye que ninguna versión la soporte: falta verificar la objetivo.
