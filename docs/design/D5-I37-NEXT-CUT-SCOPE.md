# D5 I37 — siguiente corte tras I36

Fecha: **2026-10-23**, Europe/Madrid. **A seleccionado; diseño preparado para revisión.**
Base revisada: `af31fd7f4d70c23ad84ac5b8258c05aba029a58a`.
[Implementación I36](D5-I36-DURABLE-RELATIONAL-LAB.md) ·
[Resultados I36](../validation/D5-I36-results.md) ·
[Criterios globales](D5-I23-GLOBAL-INTEGRATION-REVIEW.md).

English: proposed next-cut scope after bounded durable T/R evidence. Integrity
checks only, no new runtime campaign, implementation authorization or global acceptance.

## Continuidad y comprobación actual

«Continúa» autoriza revisar pendientes y preparar una decisión. P0 sigue vigente:
sin publicación de I32, handoff o incrementos posteriores. D1–D4 cerrados y el
hito D5-LOCAL-SYNTHETIC-I1-I20 aceptado conservan alcance y evidencia. D5 global,
G01–G07 y los siete criterios que requieren evidencia real permanecen abiertos.

Al iniciar, main está limpio y seis commits por delante de la referencia local
origin/main. No se ha consultado el remoto de nuevo; el tracking local no acredita
su estado actual.

La comprobación de archivos actuales verifica los **78 hashes de inputs de campaña
y siete documentales** del JSON I36. Los 321 IDs PASS registrados son distintos;
los conteos separan 40 pruebas R nuevas y 281 regresiones. Las 40 filas DR y los
dos mapas UI25/UI34 no contienen referencias vacías o ajenas a esos PASS. Esto
verifica integridad y coherencia de referencias, **no reejecuta pruebas ni demuestra
por sí solo suficiencia semántica de cobertura**. El informe histórico queda intacto.

T y R tienen autoridades durables propias y evidencia acotada de recuperación;
I24/I28/I30/I32 no adquieren persistencia por aparecer como regresiones. Los
resultados I36 mantienen GI33/GI34/GI38/GI39/GI40 en
`BOUNDED_T_AND_R_EVIDENCE_GLOBAL_REVIEW_PENDING`. No convertir 30/35 en 35/35 por
sumar informes, casos, subcasos o regresiones de campañas sucesivas.

## Opciones para decidir antes de diseñar e implementar

El usuario eligió **A** para preparar el
[contrato I37](D5-I37-EVIDENCE-AUDIT-DESIGN.md) y la
[matriz EA01–EA36](D5-I37-EVIDENCE-AUDIT-REVIEW.md).
La elección no autoriza todavía implementar o ejecutar esa auditoría.
Las opciones siguientes conservan el planteamiento de la decisión.

**A — Recomendada: auditoría ejecutable de inventario y aplicabilidad GI33/GI34.**
Preparar contrato y matriz de un verificador local de evidencia: identidad de
campaña, inputs/targets/versiones, mapas de pruebas y contabilidad; distinguir
integridad histórica, aplicabilidad actual, cobertura declarada y suficiencia
pendiente de revisión. Cambios de código/configuración/perfil/target invalidan
la aplicabilidad pertinente sin borrar ni corregir retrospectivamente resultados.
Contemplar archivos nuevos no inventariados, datos ausentes, mapas incompletos,
duplicados y discrepancias entre informe registrado y salida bruta del runner.
Separar Python ejecutado de SQL/D1–D4 preservados; hashes no equivalen a reejecución.
Fijar oráculos negativos y reglas de lectura segura antes de crear la herramienta.
No ampliar recorridos T/R ni hacer depender la auditoría de scripts previos en /tmp.

**B — Alternativa: revisión documental conjunta de los cinco criterios pendientes.**
Preparar contrato y matriz de suficiencia: afirmación, frontera, campaña/prueba,
limitación y pendiente por GI33/GI34/GI38/GI39/GI40. Diferenciar cobertura de fixture
T/R de Docs y capacidades reales pendientes. No crear herramienta ni nueva
integración; el resultado sería una revisión propuesta, no aceptación global.

Elegir A o B autoriza preparar su contrato/matriz para revisión. Implementación
o ejecución nueva requieren después aprobación del diseño y alcance concreto.
En ambas opciones, las observaciones de cero actividad y limpieza de una campaña
se conservan como evidencia de ese alcance; no acreditan otros entornos.

## Publicación: decisión independiente

No se ejecuta push ni se crea PR. La publicación limitada a I32 correspondería al
origen exacto `7b64d87ef45b4973a5ea80dc676f1bd2eca220f7`; incluir también el handoff
alcanzaría `79c696a66f85923173650f271995c69569b50b0d`. Publicar hasta I36 alcanzaría
`af31fd7f4d70c23ad84ac5b8258c05aba029a58a` e incluiría los seis commits locales
posteriores a I31. Son alternativas para una autorización futura, no acciones
autorizadas. Antes de cualquier publicación se comprobarán remoto, ascendencia y
diff del SHA concreto; una autorización limitada nunca permite push de todo HEAD.

Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue ni D6. No inspeccionar o limpiar dev/run_data/D4.
