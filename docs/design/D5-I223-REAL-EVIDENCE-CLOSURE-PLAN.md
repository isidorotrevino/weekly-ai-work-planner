# I223 — plan para cerrar evidencia prelaunch y E01–E05

El plan define **13 paquetes de evidencia real**, con entregables, dependencias, proveedor por clase de autoridad, revisores por rol, condiciones de salida y rechazo. Cubre los **30 gates de prelaunch y los 20 criterios de E01–E05**. No cierra ninguno ahora: faltan personas/appointments, seis fuentes sucesoras, runtime/imagen/plataforma, garantías y pruebas completas. Se mantiene la no admisión, D5 abierto e IR03 `NOT_READY`.

No son trece iteraciones documentales automáticas. El próximo avance útil requiere material genuino y decisiones competentes, no más estados PASS de documentos vacíos. El [plan detallado](../validation/D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json) contiene los contratos de cada paquete y las matrices de cobertura. [La revisión de preparación](../validation/D5-I223-preparation-review.json) y [el sello](../validation/D5-I223-integrity.json) fijan esta unidad. Fecha: 24 de noviembre de 2026.

## Resultado objetivo y frontera

El objetivo es obtener, en el mismo scope efectivo, evidencia suficiente y aceptación primaria/separada para siete familias, dieciséis reglas y siete gates globales, junto a cinco dictámenes completos de recursos. El recibo CE12 queda fuera de esos 30 targets. La ruta final E06/payload/Q/root/admisión/claim sigue diferida, sin ejecución ni comandos actuales.

Un eventual dictamen positivo de recursos/custodia **no es liberación del producto**, no modifica automáticamente el certificado I122, flags, `capture_inputs`, autoridad, destino o cuotas y no cierra D5. Las operaciones necesarias para producir/validar evidencia —si no existe ya con provenance y autoridad genuinas— requieren autorización específica separada. Este plan sólo autoriza su propia elaboración, auditoría documental y publicación.

## Ruta de entregables

| Paquete y dependencias | Entrega concreta | Proveedor / revisión prevista |
| --- | --- | --- |
| **W01 — scope y autoridad** | Scope lógico exacto, políticas/caps/guards/fases conservados y ledger de permisos por acción. Sin hashes futuros o helpers ocultos. | Maintainer/autoridad real todavía sin designar; R06 y R08 separado. |
| **W02 — humanos y anchors**, tras W01 | Identidades canónicas, aliases, competencia, appointments, autores/preparadores/requester, claves por propósito y registry externo auténtico vigente. | Autoridad de identidad/anchors y humanos genuinos; R06/R08, sin autoenrollment. |
| **W03 — fuentes/imagen/runtime**, tras W01–W02 | Seis fuentes reales, digests/mapping, imagen/build/toolchain y clausura interpreter/loader/stdlib/frozen/native/crypto; políticas I191 implementadas. | Custodio R01/autor de fuentes, con R06/R08. Fuentes ausentes requieren material genuino o autorización separada de implementación/cualificación. |
| **W04 — caller/plataforma/servicio**, tras W02–W03 | Constructor/dominio y ocho garantías, capacidad de memoria y servicio CPU/IO/scheduler/locks/hijos/observación, reloj y mecanismo global durable one-use. | R02 y operador con autoridad real; R03/R06/R08 revisan garantías completas. |
| **W05 — requalificación**, tras W03–W04 | Alcance 179 casos/321 raíces/12 grupos/30 sitios, nuevas rutas custodia/bootstrap/output/fallo, atomicidad y cuerpos BASIS/índices genuinos; inventario de todo coste. | Autor de pruebas; R03/R05/R06 y R08. Cualquier cualificación con componentes necesita autorización propia; E06 final no es prueba previa ficticia. |
| **W06 — heap**, tras W03–W05 | Once derivaciones H01–H11 de bytes/vida/pico/native/allocator/GC/solapamiento y rollup requested/committed con capacidad independiente. | Autores de memoria e integrador separados de R03/R08. |
| **W07 — trabajo/servicio**, tras W03–W05 | Clausura de trabajo/CPU/wall y compatibilidad, actividades/procesos/fases completos, ambos Reader y costes nuevos; correspondencia revisada de «all30 work groups». | Autores de análisis estático/WCET/servicio; R03/R06/R08. |
| **W08 — éxito en 900 s**, tras W04–W07 | Prueba de fases t0/tR/tW/tF, servicio/latencia/éxito y `finally` completos dentro de presupuestos candidatos conservados. | Autor de prueba temporal y garante de servicio, separados de R03/R06/R08. |
| **W09 — aceptación conjunta**, tras W02–W08 | Revisión exacta de los 20 criterios y cinco obligaciones, BASIS/índices/atomicidad/scope aceptados con cuerpos/autores/supuestos genuinos y decisiones independientes. | R03/R06 y R08 separado; sin auto-revisión o transferencia histórica. |
| **W10 — freeze final**, tras W02–W09 | Registro completo con todos los autores reales, seguido de imagen/caller/plataforma; bytes/caps/epoch/vigencias y reconciliación con scope de W09. | Custodios/autoridad y R01/R02/R03/R06/R08. Si cambia algo relevante, invalida y vuelve a revisar dependientes. |
| **W11 — C/acceptance**, tras W09–W10 | Proyección exacta de 14 tipos compartidos, valores/digest/constantes, contención de vigencia y cinco evidencias previas. Acceptance sólo de custodia, sin firma propia. | Custodios de hechos; R01/R02/R03/R06 y R08. Sin body positivo rellenado con placeholders. |
| **W12 — bundle/mapping**, tras W02/W04/W10/W11 | Cinco registros, tres aprobaciones sobre core íntegro con dominios+NUL, caps reales y mapping único global epoch/C → bundle/caller/image/domain/ledger. | Autoridad externa y custodios; R01/R02/R06/R08 con evidencia genuina de verificación. No firma/provisioning/crypto/servicio autorizado por este plan. |
| **W13 — decisión de 30 gates**, tras W01–W12 | Checklist con evidencia/decisión por fila, aceptación separada y handoff de ruta final pendiente. Rechazados/faltantes visibles y estado activo sin promoción automática. | R06 y R08 separados de autores, con competencia/appointments genuinos. |

Ruta crítica por dependencias, **sin promesa temporal**:

`W01 → W02 → W03 → W04 → W05 → {W06 y W07 en paralelo} → W08 → W09 → W10 → W11 → W12 → W13`.

Toda persona, clave, appointment y proveedor concreto permanece sin asignar. Los nombres de roles no prueban identidad o independencia. Se conservan las ocho exclusiones S01, source-author/root-key y separación adicional R08 respecto de R01/R02; no se impone una separación general nueva entre R01 y R02.

## Primeras decisiones y material necesario

1. **W01–W02:** presentar un scope aceptable y una autoridad real; aportar humanos canónicos, competencia, appointments, autores y aceptantes independientes, con anchors y provenance auténticos. No se contacta ni designa a nadie desde esta unidad.
2. **W03:** aportar las seis fuentes y una imagen/runtime efectivas con equivalencia y provenance. Hoy las seis rutas están ausentes. Sin artefactos genuinos, una implementación/build/cualificación exige una solicitud separada y acotada; no se crean aquí.
3. **W04:** aportar un contrato de plataforma respaldado por autoridad capaz de garantizar capacidad/servicio/reloj/atomicidad y sus pruebas exactas. Si no puede sostenerlo, se mantiene no admisión; un documento candidato no proporciona las garantías.

Cada paquete debe entregar un inventario inmutable de cuerpos disponibles con hashes/bytes reales, autores/provider/custodia, scope/source/runtime/imagen/epoch/políticas, derivaciones/unidades/supuestos y registros de revisión primaria/separada. Valores desconocidos siguen desconocidos. No se inventa un formato positivo nuevo ni se añaden miembros al runtime graph. Los outputs históricos de I132 existen como dossiers negativos: se fijan por hash y se requalifican, no se reescriben o transfieren automáticamente.

## Cómo se cierran los 30 gates

El JSON contiene una fila por gate original con requisito literal, paquetes productores, sus entregables requeridos, decisión final W13 y criterios de cierre/rechazo. La cobertura es exacta: siete familias + dieciséis reglas + siete globals; excluye el recibo diferido.

| Familias | Paquetes principales de evidencia |
| --- | --- |
| Anchor registry | W02 |
| Actor registry / image / caller / platform | W02–W04 y W10, con join de recursos W09 para plataforma. |
| Acceptance | W09–W11 |
| Custody bundle | W02/W11/W12 |

Cada regla K01–K16 y gate G01–G07 tiene su propia asociación en la matriz, incluida la autenticación previa, ausencia de self-bootstrap, source/image/runtime exactos, constructor, C, mapping global, approvals, epoch/currentness, mecanismo one-use, costes y caps. **W13 no acepta un gate hasta que exista evidencia suficiente para ese requisito exacto**, con revisores competentes y R08 separado. Una firma, schema, hash de documento o estado de paquete no basta.

Las 69 plantillas de referencia de CE11 siguen siendo sólo declaraciones tipadas, no cuerpos únicos ni un inventario real completo. El cierre requiere registrar cada referencia real faltante/aportada/rechazada, sus bytes/scope/autor/provider/custodia y decisión. El recibo CE12, claim/spawn y la finalización de la ruta E06/payload/Q/root/admisión no se agregan como precondiciones de CE11.

## Cómo se cierran E01–E05

| Obligación | Evidencia y paquetes para la decisión W09 |
| --- | --- |
| **E01** | W01/W03/W04/W05: entorno y clausura completos, source-to-binary/runtime/imagen/loader/native y plataforma/servicio auténticos, compatibles y vigentes. Referencias históricas no bastan. |
| **E02** | W04/W06: once owners completos, todos los picos/vidas/native/GC/allocator/solapamientos, rollup y capacidad realmente disponible. Sin términos desconocidos igualados a cero. |
| **E03** | W03/W05/W07: trabajo y CPU completos de fuente/observador/runtime por actividad/proceso/fase, con unidades compatibles o WCET justificado. Conteos/bytes no equivalen a segundos. |
| **E04** | W04/W07/W08: servicio real de CPU/procesos/reloj/IO/scheduling/locks/hijos/observación con demoras acotadas o WCET justificado, compatible con el trabajo. |
| **E05** | W04–W08: éxito normal end-to-end bajo ventanas ordenadas y reserva conservada; no watchdog/deadline/elapsed como sustituto. |

La matriz de criterios conserva los veinte IDs y requisitos históricos I131, revalidando su aplicabilidad al sucesor. Las nueve consistencias documentales y una referencia histórica no se promocionan a pruebas de recursos; las evidencias completas ausentes siguen sin aportar. La matriz de memoria detalla H01–H11; la de trabajo, diez actividades con treinta valores work/CPU/wall aún desconocidos. Los veinte vectores históricos proceso/fase y esos treinta valores no satisfacen por sí solos el literal «all30 work groups»: W07 debe aportar inventario/correspondencia revisada completa.

Se conservan como candidatos 11 GiB requested, 12 GiB committed, overhead allocator 1 GiB y reserva requested 832 MiB sin asignar. No se aplican ni transfieren reservas. Debe justificarse la composición de todo el scope y demostrar ajuste bajo presupuestos efectivos revisados y capacidad independiente, no suponerla por existir presupuesto. Heap serializado/RSS/getsizeof parcial no reemplazan ese análisis.

Para tiempo se conservan 60/750/60 más 30 segundos de reserva candidata. `tW` es el retorno exacto `True` de `wait_worker`, no salida física ni validación posterior; `True` tampoco prueba éxito de captura. W08 debe cubrir worker previo a tR, exit-to-wait-return y `finally`/validaciones/doble escritura hasta tF. Los costes de ambos Reader, lookup/freshness/identidad/crypto/measurement/copias/registry/recibo/native/IO permanecen dentro de fases y join global. No hay cota real ni garantía de 900 segundos ahora.

## Evitar dependencia circular y evidencia caducada

W02 es intake auténtico provisional, no cierre anticipado de autores. Antes de aceptar recursos en W09 deben conocerse/autenticarse todos los autores reales de W05–W08, sus cuerpos completos y los hechos baseline actor/imagen/caller/plataforma. W10 sigue al join CE07, pero no suministra su única autenticación prevista. El freeze posterior sólo puede conservar esa aceptación si coincide el scope/factos/autores relevante.

Si cambian autores, cuerpos, source/runtime/imagen, dominio/recurso, epoch/clave/política, se detiene la progresión, se invalidan candidatos/revisiones afectados y se repite lo necesario antes de avanzar. Esa vuelta por invalidación no es una dependencia que permita aceptar con evidencia futura. Ni bundle, root, E06 final o recibo pueden ser la única autenticación antecedente. Se mantienen clock/currentness y validez genuinos en cada frontera, sin cache/TOFU o revocación instantánea supuesta.

## Ocho decisiones de parada

| Punto | Si falta o falla | Resultado obligatorio |
| --- | --- | --- |
| SD01, W01 | Scope/autoridad/roles competentes reales. | Detener progreso positivo, sin auto-nominación/contacto. |
| SD02, W03 | Fuentes/imagen/runtime/loader reales y cualificados. | Exigir material genuino o autorización separada; sin hashes predictivos. |
| SD03, W04 | Garantías completas de capacidad/servicio/reloj/atomicidad. | E01/E04 y dependientes abiertos; sin promesa o probe oculto. |
| SD04, W06 | Owner/native/allocator/overlap completo y ajuste probado. | No admisión de recursos; sin reserva/cuota ampliada o unknown=0. |
| SD05, W08 | Trabajo/servicio/latencia y éxito justificado en 900. | No admisión temporal; presupuesto o watchdog no son prueba. |
| SD06, W10 | Cambia algún hecho relevante del scope aceptado. | Invalidar y requalificar/revisar dependientes antes de aceptar. |
| SD07, W12 | Aprobaciones/anchors/mapping/caps/referencias/freshness. | No admisión de custodia; no firmar/provisionar/probar para llenar el plan sin autoridad propia. |
| SD08, W13 | Algún gate/obligación/reviewer sigue incompleto. | Dictamen negativo veraz; sin agregado positivo parcial, D5 abierto. |

No demostrar una cota no prueba automáticamente inviabilidad o unboundedness. No se cambia una cuota para forzar ajuste. El plan no ofrece fecha de cierre sin proveedores, artefactos y pruebas reales; registrar decisiones negativas es un resultado válido y obligatorio.

## Permisos y estado actual

Este trabajo no autoriza implementar/build/import/ejecutar/cualificar producto o componentes, medir/probar plataforma/reloj/ledger, firmar/generar claves/verificar crypto operativo, contactar actores/proveedores/revisores, enrollment/provisioning/configuración o cambiar `capture_inputs`, root, autoridad, destino, cuota o reserva. Cada operación futura necesaria exige su propia autoridad exacta, alcance y prueba de costes; la evidencia externa existente sólo puede considerarse con provenance autorizada genuina.

El handoff final mantiene los cuatro prerrequisitos anteriores al claim y el claim/construcción reales antes del recibo. Claim no es su propia precondición, debe seguir a admisión completa y preceder paths/spawn, y el recibo permanece privado y `DEFERRED_NOT_AUTHORIZED`. Esas acciones están fuera del cierre prelaunch y no se ejecutan aquí.

**Estado después de I223: 13 paquetes planificados, 30 gates pendientes, cinco obligaciones abiertas y cero pruebas o aceptaciones reales aportadas por esta unidad.** I122 mantiene `IMPLEMENTED_NOT_ADMITTED`, CP03 sólo en su scope heredado, CP07/atomicidad correlacionada sin verificar y componentes `NOT_RUN`; no se emite `SOURCE_CAPACITY_VERIFIED`. No cambian cuotas, reservas, presupuesto, bindings, autoridad/destino ni D5.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I223-audit.py`.

Resultado requerido: `PASS_STATIC_SOURCE_ONLY_REAL_EVIDENCE_CLOSURE_PLAN_NOT_ADMITTED`. Comprueba 912 pins contra blobs del commit base I222 `643a5f290e4dfdc1a937727d01515c0a5778febf`, preserva 604 archivos publicados y exige cinco archivos nuevos. Verifica cobertura exacta de gates/criterios, propietarios/actividades, DAG/ramas, frontera de autoridad y doce mutaciones negativas en memoria. Reproduce la reconstrucción/revisión documental I222 sin invocar mains históricos de publicación ni añadir un nuevo guard de presencia histórico. No es un PASS de recursos/prelaunch real.

Harness runtime: N/A; sólo documentos/Git/hash, matrices y grafos. No se ejecutan producto/componentes, codecs/crypto positivos, probes, clocks/ledger, procesos, claims o servicios. No se crean paquetes positivos de evidencia, se contactan terceros o reservan recursos.

Una unidad con commit y push autorizados; se declara el exceso de 400 líneas por los contratos de paquetes, matrices, pins y preservación. Reversión exacta: retirar este documento, `D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json`, `D5-I223-preparation-review.json`, `D5-I223-audit.py` y `D5-I223-integrity.json`. Publicar prepara un plan concreto; no acepta pruebas ni libera ejecución o admisión.
