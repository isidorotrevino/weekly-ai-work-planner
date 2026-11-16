# I184 — I183 requiere completar la separación de roles

Fecha: 2026-11-16, Europe/Madrid. Base:
`ecd63ca9b6eb716031e2e30957f2c909f89f99df`.

**La revisión encuentra un defecto documental bloqueante: F183-01.** El perfil
candidato de I183 no expresa cinco exclusiones de identidad de S01. La estructura
de sus schemas y conjuntos de bindings es consistente en las comprobaciones
realizadas, pero el contrato de confianza requiere revisión antes de aceptarlo.
PGO181-SPLIT-ROOT-01 sigue sin adoptar ni implementar, F179-01 abierto e
I122/PJC115-R2 sin admisión. D5 continúa abierto.

## Ruta de revisión

1. Leer [F183-01 y el dictamen](../validation/D5-I184-I183-documentary-review.json).
2. Contrastar la [reconstrucción de schemas y relaciones de roles](../validation/D5-I184-I183-source-reconstruction.json).
3. Revisar el [auditor](../validation/D5-I184-audit.py) y el
   [sello documental](../validation/D5-I184-integrity.json).

Se preservan los seis archivos I183. Esta revisión no reescribe la propuesta,
la matriz S01 ni schemas/flags activos. El mismo asistente preparó I183 y
realiza esta reconstrucción metodológicamente separada: no hay independencia
de actor u organización, aceptación separada o nombramiento competente.

## F183-01 — Faltan exclusiones explícitas de S01

La [matriz I179](../validation/D5-I179-S01-ROLES-SCOPE-GATES.json), en
`/role_authority_validity_matrix`, exige ocho relaciones de separación entre
actores. El [perfil I183](../validation/D5-I183-PGO181-TRUST-PROFILE-CANDIDATE.json),
en `/bootstrap/separation`, declara cuatro relaciones de actores y otra de claves.
Tres relaciones de actores conservan exclusiones de S01; la cuarta separa al
aceptante del autor de fuentes. No identifica a ese autor con el preparador
documental ni incorpora exactamente las restantes exclusiones.

| Exclusión de S01 no expresada | Consecuencia de especificación |
| --- | --- |
| R03 ≠ DOCUMENTARY_PREPARER | No queda explícitamente prohibida la autorrevisión de recursos |
| R06 ≠ DOCUMENTARY_PREPARER | No queda explícitamente prohibida la autorrevisión de admisión/Reader |
| R08 ≠ DOCUMENTARY_PREPARER | La separación respecto al autor de fuentes no cubre necesariamente al preparador documental |
| R08 ≠ R03 | El aceptante separado podría coincidir con el revisor primario de recursos bajo los predicados escritos |
| R08 ≠ R06 | El aceptante separado podría coincidir con el revisor primario de admisión bajo esos predicados |

El schema de trust_context tiene `source_author_id`, pero carece de una
identidad de preparador documental o de una correspondencia auténtica que
permita aplicar todas esas restricciones. Dos claves distintas tampoco
acreditan separación respecto a los revisores primarios.

La reconstrucción forma cinco contramodelos simbólicos, uno por exclusión:
unificar los dos símbolos de cada fila aún permite satisfacer todas las
desigualdades de actores escritas en I183. No genera nombres, claves, contextos,
firmas o evidencia. No comprueba firmas ni ejecuta una admisión.

El alcance del hallazgo es exactitud del contrato: la cláusula general de que
los ocho roles estén genuinamente asignados/aceptados podría apoyarse en una
custodia externa más fuerte, pero no importa de forma inequívoca y verificable
las cinco exclusiones omitidas. Los contramodelos satisfacen la lista explícita;
no demuestran conformidad con toda posible política externa ni un bypass del
protocolo completo. Tampoco se afirma que exista una colisión real: todos los
nombramientos siguen pendientes.

Se requiere otro candidato versionado que conserve las ocho exclusiones,
vincule la identidad/procedencia auténtica del preparador y añada sus casos
negativos; o una adjudicación competente explícita de una política distinta.
No se puede asumir que preparador y autor de fuentes sean la misma persona.
Debe mantenerse la separación de claves y actualizar los digests del paquete/
perfil revisados. F183-01 queda abierto; no se aplica reparación en I184.

## Aspectos del contrato confirmados

| Área | Resultado y límite |
| --- | --- |
| Estructura | 17 familias, 32 definiciones, referencias locales acíclicas y discriminadores distintos |
| Bindings | 480 históricos y seis fuentes; BASIS 489, manifest nueve, payload 494; conjuntos recompuestos desde Git |
| Orden | BASIS/índice excluyen descendientes finales; payload excluye raíz y sí mismo; CP07 conserva nueve condiciones finales |
| Raíz | Core fija antecedentes, contexto/solicitud/perfil e invocación; excluye firmas, hash propio y resultado futuro |
| Firma | Dos dominios de rol sobre el mismo core; el perfil distingue sus restricciones locales de los requisitos del RFC |
| Confianza | Origen externo auténtico, custodia y aceptación real exigidos; no quedan establecidos por un key_id o archivo |
| Reader | 496 rutas y aritmética condicionada 266.693.693 bytes; cuotas intactas y fit real sin demostrar |

El subconjunto ASCII/enteros seguros y sus rechazos léxicos se distinguen de
JCS general. Schema, codificación/caps y verdad semántica son capas diferentes:
una estructura válida no prueba recursos o procedencia. Las anchuras ficticias
de preparación no son upper bounds de todas las instancias; cada cuerpo real
debe respetar también su cap. La evidencia completa del índice no puede
truncarse para caber ni introducir lecturas ocultas.

[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) respalda las reglas generales
de JCS; la restricción ASCII/enteros es local. [RFC 8032 §5.1.7](https://www.rfc-editor.org/rfc/rfc8032)
admite la ecuación sin cofactor como comprobación suficiente. La exclusión de
identidades/subgrupos y los dominios adicionales son elecciones explícitas
del candidato. Esta revisión documental no prueba su implementación, seguridad,
compatibilidad de biblioteca o resistencia a ataques.

Los schemas siguen [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-validation).
La revisión comprueba su estructura y las relaciones indicadas; no ejecuta un
validador runtime del producto ni acredita conformidad completa del estándar.
La igualdad entre cuerpos, aceptación real de evidencia y autorización del
caller siguen siendo obligaciones semánticas externas al schema.

## Readiness que continúa pendiente

Faltan implementación exacta y calificación de custodia, identidad/roles,
reloj/epoch/revocación/replay, guard y biblioteca criptográfica; los schemas
completos de contexto/launch que contendrían capture_binding; pruebas de todo
el flujo INVOKE/READY/RELEASE y sus excepciones. El fragmento de binding y las
reglas escritas no son un formato completo o control de flujo implementado.

También quedan la requalification de los 179 casos, 321 raíces/12 grupos y
30 sitios; E01–E05 completos con IO/heap/CPU/nativo/crypto y objetivo 900;
cotas reales de fuentes/cuerpos/fresh reads/outputs; solicitudes auténticas,
evidencia antecedente y E06 final reales; payload/raíz/firmas y decisiones
competentes separadas. La configuración de confianza, aprobaciones y
transcripts externos precisan procedencia y cotas reales antes de su uso.

I184 no adopta S01, resuelve F179-01, habilita la propuesta o establece un trust
anchor. Un dictamen sobre la forma del contrato no convierte los antecedentes
en aceptados ni entrega autorización de ejecución.

## Verificación y publicación

`python3 docs/validation/D5-I184-audit.py`: PASS_STATIC_SOURCE_ONLY esperado.
Contrasta 712 pins con Git, preserva 404 archivos publicados, recompone las
relaciones y confirma la reproducción de la preparación I183 usando sólo sus
funciones documentales. El PASS acredita la integridad/reproducción de esta
revisión, **incluido su hallazgo bloqueante**; no acepta el candidato.

La unidad consta de cinco archivos: este documento, dictamen, reconstrucción,
auditor y sello; la lista exacta está en work_unit.rollback_files. El diff
supera 400 líneas por evidencia trazable y auditoría; se informa el exceso.
Runtime harness N/A: revisión documental sin implementación runtime ni
producto/componentes/criptografía ejecutados. Rollback limitado a esos cinco
archivos. Auditoría antes de stage y tras commit, push solicitado y verificación
de remoto/árbol limpio. La publicación no adopta ni concede autoridad.

E01–E05 abiertos, E06 NOT_RUN; I122 IMPLEMENTED_NOT_ADMITTED, CP07/correlación
false, cuatro bindings I175 pendientes. Sin SOURCE_CAPACITY_VERIFIED, rebind,
autoridad/destino nuevos, captura/propuesta habilitadas o D5/H07 cerrados;
IR03 NOT_READY. P0 83 SUPPORTS_BOUNDED/1 PARTIAL UI04.1, D1–D4 e I1–I20/A52
intactos; brechas globales/reales pendientes. I86/I89/I92 INVALID_CAPTURE no
se reanudan ni mezclan.

Sin ejecutar/importar/compilar producto o componentes, tests, discovery,
benchmarks, firmas o calendarios runtime; sin mediciones de plataforma. Sin
cambiar fuentes, schemas/contratos activos, cuotas, presupuestos, reservas o
inputs; sin inspeccionar ni limpiar dev/run_data/D4. Sin nombres/aceptaciones,
claves, firmas, root/payload reales o PASS emitidos; sin proveedores,
credenciales, consumo, activación, promoción, despliegue o D6.
