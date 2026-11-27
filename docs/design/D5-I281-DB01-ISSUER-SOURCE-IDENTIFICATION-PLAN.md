# I281 — Plan para identificar al emisor DB01 y obtener su fuente

**Queda preparado un plan concreto de identificación y obtención de fuente, sin ejecutarlo externamente. Se mantiene la no admisión.** DB01 sigue sin emisor o cuerpo de autoridad acreditado, SD01 activo y la entrega sin habilitar. El primer aporte necesario es contexto del proyecto/organización y una referencia o custodio legítimo de registros preexistentes; no se pide nombrar a alguien para llenar el hueco.

Fecha: 2026-11-27, Europe/Madrid. Base: `62d008954cc95b6ceb1e48e71e731567035d53c5`.

El [plan estructurado](../validation/D5-I281-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN.json), `PGE251-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN-CANDIDATE-01`, conserva el [gap I279](D5-I279-DB01-ISSUER-UNIDENTIFIED-GAP.md), [su revisión I280](D5-I280-I279-DB01-GAP-REVIEW.md) y DB01/I277 exactos. Los identificadores IP/SR organizan tareas y clases de fuente, sin nuevo lote A09, retorno o fase de aceptación prelaunch. Ningún candidato se convierte en emisor por estar en una lista.

## Primer dato humano y resultado buscado

Una persona con conocimiento legítimo del proyecto puede aportar **contexto de organización/proyecto y un registro ya existente o la función de su custodio**, con provenance y base propia de acceso. No necesita que DB01 esté previamente aceptado para proponer una pista no verificada o suministrar legítimamente un documento disponible. Una pista no concede autoridad ni acepta el contenido.

La aportación mínima debería precisar:

- Qué proyecto/organización es titular del contexto de la entrega documental RQ01/RT01.
- Qué registro preexistente de mandato/gobernanza/appointment/delegación existe, o qué función legítima lo custodia.
- Dónde puede aportarse/leerse el cuerpo ya existente bajo autoridad propia.
- Qué cláusula o relación podría acreditar facultad de contacto documental, más allá de acceso a Git o un título.
- Qué gaps, ámbito/vigencia/provenance y facultades faltan para cualquier consulta adicional.

Si no se dispone de ello, se conserva el gap concreto. La salida buscada es un humano canónico respaldado por una cadena de autoridad disponible, con facultad para autorizar **este contacto documental exacto**, no un nombre plausible, un maintainer inferido o una declaración nueva que se presente como prueba retroactiva.

## Pistas locales comprobadas, sin emisor verificado

Se leyeron estáticamente siete fuentes versionadas: README, LICENSE, NOTICE, CONTRIBUTING, SECURITY, introducción/continuidad de docs/README y el checker de publicación. Se registran sus hashes y el alcance de lectura; no se ejecutaron instrucciones de desarrollo, producto o componentes contenidas en ellas.

| Observación limitada | Utilidad y límite |
|---|---|
| README sitúa gobernanza/operaciones D6 como trabajo futuro | Contexto del prototipo; no prueba que una autoridad no exista fuera de esos párrafos |
| NOTICE atribuye material a contribuidores colectivamente | Pista de procedencia, sin humano canónico o facultad DB01 individual |
| CONTRIBUTING menciona aprobación del maintainer y derechos de contribuidores | Funciones de proyecto; no identifica o delega por sí sola la entrega RQ01/RT01 |
| SECURITY delimita publicación/reporting y no configura correo dedicado | No se selecciona un canal, persona o permiso de contacto |
| LICENSE contiene texto general de licencia | Permiso de software no equivale a identidad humana o delegación DB01 de contacto documental |
| Remoto Git con cuenta `isidorotrevino` | Identificador de cuenta para navegación futura autorizada; no se verificó que sea persona, emisor o autoridad, ni se consultó el servicio |
| Sin CODEOWNERS/GOVERNANCE/MAINTAINERS en los paths versionados seleccionados | Cribado finito de nombres en este commit, sin búsqueda exhaustiva o inexistencia global |

Las fuentes locales son pistas y contexto público, no un expediente genuino de autoridad. No se atribuye facultad a titulares de copyright, usuario del chat, cuenta Git, maintainer o asistente por esos rótulos. Identidad canónica y facultad requieren sus cuerpos propios.

## Ocho pasos con salidas y paradas

| Paso / dependencia | Acción futura condicionada y función responsable, sin persona asignada | Salida y parada |
|---|---|---|
| IP01 — Inicio | Persona con conocimiento legítimo aporta contexto, registro/custodio y base de acceso propios | Referencias disponibles o gap de contexto; no inferir emisor de Git/licencia ni contactar desconocidos |
| IP02 — Tras IP01 | Custodio/operador legítimo forma lista finita de fuentes ya aportadas/autorizadas, priorizando SR01–SR04 | Fuente/localización/disponibilidad/provenance y facultad esperada; fuente privada/externa sin base de acceso detiene esa ruta |
| IP03 — Tras IP02 | Elegir material existente legítimamente aportado o preparar una indagación exacta para autoridad independiente separada | Material disponible o propuesta de acceso/consulta aún no aprobada; sin base propia, parar ruta externa y pedir referencia existente aportada localmente |
| IP04 — Tras IP03 | Reviewer competente separa claims de candidatos de identidad/rol/facultad verificados | Vínculo candidato-fuente y dudas, sin nombramiento/flag positivo; alias ambiguo, servicio o nombre sin soporte sigue no verificado |
| IP05 — Tras IP04 | Custodio autorizado aporta cuerpos completos preexistentes y antecedentes de autoridad/delegación | Inventario/cadena/cláusulas/scope/vigencia/provenance o gap; cuerpo parcial, autoafirmación o cadena ausente no satisface DB01 |
| IP06 — Tras IP05 | Actor competente/elegible bajo autoridad propia revisa humano/aliases/competencia/appointment/facultad/scope/currentness/independencia | Review genuina razonada con cuerpos/referencias; desconocido o incompatible conserva aplazado/rechazado según decisión real |
| IP07 — Tras IP06 | Actor de decisión propio reconcilia DB01 y cambios/dependientes A01–A08 | Resolución limitada DB01 o gap explícito; invalidar/revisar afectados, sin transferencia automática o grant |
| IP08 — Tras IP07 | Volver a la frontera I277 existente con actores elegibles/autorizados | DB02–DB12 y decisión exacta siguen exigidos; ningún envío/aceptación/ejecución o cierre por este plan |

Los ocho pasos permanecen `performed=false/completed=false`. La lectura estática limitada de esta sesión es una observación documental separada, sin presentar la búsqueda externa/obtención/review genuina como realizadas. No hay operador, custodio, reviewer, emisor, canal o calendario designados.

## Fuentes a priorizar y cómo romper el círculo sin autoautorizar

| Ruta | Fuente existente que se buscaría, si se aporta o autoriza legítimamente | Quién podría aportarla por función, sin nombramiento |
|---|---|---|
| SR01 | Decisión/mandato/gobernanza de proyecto, appointment o delegación del scope | Humano con conocimiento legítimo o custodio autorizado de esos registros |
| SR02 | Delegación organizativa de owner/maintainer con facultad de contacto documental | Custodio legítimo de gobernanza/registros; no cuenta Git inferida |
| SR03 | Directorio/identidad/rol y appointments aplicables | Custodio existente de identidad/organización con acceso legítimo; pertenencia o título solos no prueban facultad |
| SR04 | Antecedentes independientes de la cadena y evidencia de currentness/revocación | Fuente/custodio legítimo bajo autoridad propia, con cuerpos disponibles y ámbito |

**Material ya disponible:** puede proponerse como pista o aportarse genuinamente bajo provenance propia, sin exigir DB01 aceptado antes de considerar ese material. **Consulta externa o contacto necesario:** exige una base independiente propia de acceso/indagación y un alcance exacto de fuente/actor/canal/finalidad/datos/costes/permiso antes de actuar; no se toma prestado DB01 ausente o el grant de entrega I277. **Sin esa base:** se detiene la ruta externa y se pide una referencia existente legítimamente suministrada. Este plan no autoriza la consulta, envío, discovery/fetch, lectura privada o servicio de verificación.

No se confecciona una autoridad retrospectiva para completar la cadena. Si se descubriera que hace falta establecer gobernanza nueva, sería trabajo prospectivo separado bajo autorización y revisión propias; no se realiza aquí ni se usa un documento recién emitido como prueba automática de una autoridad anterior. Falta de fuente no prueba inexistencia global o inviabilidad.

## Qué debe traer el expediente y qué permitiría concluir

Se mantienen los cinco grupos de reentrada I279: humano canónico/aliases; cuerpo disponible de autoridad/delegación auténtica independiente con locator/bytes/digest/autor/provider/custodia y antecedentes; facultad/acciones permitidas-denegadas/scope exactos; vigencia/currentness/revocación/provenance; review competente propia. Los cuerpos y referencias deben estar completos, con cláusulas de soporte identificadas y desconocidos explícitos. Preservar claims/digests no autentica autoridad o currentness; una firma o fecha del host no basta.

Candidato, fuente disponible, fuente verificada y decisión genuina son estados distintos. Los registros de candidatos están vacíos y el inventario completo desconocido, sin humano/aliases/cuerpo de autoridad o review aportados. Catorce exclusiones/preparadores del scope real se conservan; W02 aporta criterios sin aceptación previa/roster final/CE10 o separación general R01/R02 nuevos. No se ejecutan codec/crypto, firma/keygen, enrollment, pruebas/probes de plataforma/reloj/ledger o configuración para llenar el expediente.

Sólo material genuino suficiente y decisión competente propia permiten considerar DB01 resuelto en su ámbito. No equivale a aprobar DB02–DB12, entregar el handoff, nominar EA01/R06/R08, aceptar RT01/A01 o habilitar RQ02. Mensaje/seis archivos/extracto y límites I277 permanecen intactos. Todo cambio de autor/body/source/runtime/scope/epoch/key/policy/validez invalida afectados antes de avanzar, sin transferencia automática de pruebas/aprobaciones/aceptaciones o rebind activo.

## Custodia, publicación y no admisión

CONTRIBUTING/SECURITY exigen separar fixtures de datos reales y no publicar credenciales, adjuntos privados, conversaciones o logs no revisados. El plan publica sólo metadata/pistas ya versionadas y descripciones, sin cuerpos privados, identidades canónicas verificadas o material entrante. Una fuente genuina futura debe tener custodia/acceso propios y alcance de publicación revisado: no se incorpora automáticamente al Git, ni se elige backend o input Reader nuevo.

La comprobación global `python3 scripts/check-publication.py` devuelve **exit 1 con 37 avisos preexistentes**: dos localizaciones antiguas con rutas personales y 35 archivos históricos grandes. No se copian valores coincidentes; no se modifican archivos congelados para ocultarlos. El auditor I281 exige el mismo baseline de localizaciones/categorías y cero patrones configurados en sus cinco archivos nuevos. Esto no es un PASS global ni un scanner exhaustivo de secretos/autoridad; se revisa además el diff preparado.

Ambos Readers/costes globales/caps/guards/outputs/cuotas/reservas siguen intactos, sin inputs ocultos o trabajo offline gratis. CE12/recibo privado sigue diferido/no autorizado, sin eventos finales E06/Q/root/claim/spawn/recibo como nuevas condiciones entrada/prelaunch; se conservan prerrequisitos, claim no es su propia precondición y no hay retry gratuito. No se alteran bindings activos/autoridad/destinos/certificado.

I122 permanece IMPLEMENTED_NOT_ADMITTED, CP07 falso, atomicidad correlacionada sin verificar, componentes/E06 NOT_RUN, PJC115-R2 sin habilitar, D5/H07 abiertos e IR03 NOT_READY. A01–A08, treinta gates y E01–E05 pendientes. SD01 activo, DB01 sin satisfacer, DB02–DB12 pendientes, RQ01 sin enviar y RQ02 sin habilitar; cero búsquedas externas/contactos/fuentes genuinas obtenidas o grants/aceptaciones creados.

## Comprobación y publicación

Se fijan 1210 entradas contra blobs del commit base, incluidos siete documentos locales; se preservan 895 archivos publicados. La [comprobación enfocada](../validation/D5-I281-documentary-check.json) verifica cuatro rutas, ocho pasos no ejecutados, cinco campos de primer aporte, reentrada exacta y treinta mutaciones rechazadas, sin repetir auditorías históricas. El [sello](../validation/D5-I281-integrity.json) cubre los cuatro artefactos propios distintos del sello.

```text
python3 docs/validation/D5-I281-audit.py
PASS_STATIC_SOURCE_ONLY_DB01_IDENTIFICATION_PLAN_PREPARED_UNVERIFIED_LEADS_ONLY_GENUINE_ISSUER_SOURCE_MISSING_NOT_ADMITTED
publication_hygiene: global_exit=1, baseline_unchanged=37, new_I281_findings=0
```

Harness de runtime: **N/A**; sólo JSON/Git/hashes/pointers, lectura estática local, higiene de publicación stdlib y mutaciones documentales propias. Sin importar, compilar o ejecutar producto/componentes, discovery/tests/build/benchmark/E06, codec positivo de protocolo/crypto, firma/keygen/enrollment, contactos, provisión/configuración o probes de plataforma/reloj/CPU/IO/ledger/procesos/endpoints/replay/crash/restart. Sin inspección/limpieza de dev/run_data/D4 o reanudación de I86/I89/I92.

Unidad documental única con exceso de 400 líneas declarado por plan, fuentes/pins, baseline de publicación, comprobaciones y preservación; sin PR solicitado. Rollback limitado a retirar exactamente:

- `docs/design/D5-I281-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN.md`
- `docs/validation/D5-I281-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN.json`
- `docs/validation/D5-I281-documentary-check.json`
- `docs/validation/D5-I281-audit.py`
- `docs/validation/D5-I281-integrity.json`

Commit y push publican el plan revisable. No identifican/acreditan al emisor por sí mismos, ejecutan consultas/contactos, obtienen cuerpos genuinos o conceden la entrega.
