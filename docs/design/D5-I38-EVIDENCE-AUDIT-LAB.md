# D5 I38 — auditoría ejecutable GI33/GI34

Fecha: **2026-10-23**, Europe/Madrid.
[Contrato I37](D5-I37-EVIDENCE-AUDIT-DESIGN.md) ·
[EA01–EA36](D5-I37-EVIDENCE-AUDIT-REVIEW.md) ·
[Uso](../../testing/evidence_audit/README.md) ·
[Resultados](../validation/D5-I38-results.md) ·
[Registro fijo](../validation/D5-EVIDENCE-REGISTRY.json).

English: local read-only evidence audit, with a separate synthetic auditor test
campaign. No T/R or SQL rerun, historical report rewriting or global acceptance.

## Autoridad y alcance implementado

El usuario aprobó **I37 y la implementación/validación del auditor, registro fijo
y EA01–EA36, solo lectura local y sin reejecutar T/R o SQL**, mediante respuesta A.
Contrato aprobado: `4eb9de6119bd6fe709981692282153c358040531`. I37 conserva su estado
documental histórico PREPARED_FOR_REVIEW; este documento registra la decisión posterior.

P0 continúa para I32, handoff y posteriores. El commit local no concede publicación.
D1–D4 cerrados y A52/D5-LOCAL-SYNTHETIC-I1-I20 aceptado mantienen alcance, targets
y evidencia. D5 global y G01–G07 abiertos; cinco criterios integrados en revisión
global y siete criterios reales pendientes. Sin proveedores/credenciales reales,
consumo/reservas, operaciones, activación, promoción, despliegue o D6.

## Implementación y reproducción

[`audit-d5-evidence.py`](../../scripts/audit-d5-evidence.py) usa únicamente biblioteca
estándar y Git local de lectura. Sin argumentos, red, import de módulos T/R, caches,
escrituras, reparación o limpieza. Cargas de blobs regulares por lotes, hashes
SHA-256, inventarios del commit y actuales con reglas fijas, metadatos de contexto,
cuentas/grupos/mapas y oráculos de coherencia separados. El registro fija once
entradas y 296 paths únicos de dependencias públicas; no inventario universal.

I34/I36 y contratos I33/I35 quedan anclados a sus commits. Los documentos D3/D4/A52
se anclan a I36. Los inputs emitidos con A52 se comprueban en el commit original
de aceptación `148c656` completo en el registro: es donde coinciden sus hashes,
incluido el índice documental antiguo. No alterar hashes para hacerlos actuales.
D1/D2 se preservan mediante referencias públicas explícitas existentes, no mediante
manifiestos de cierre nuevos o una supuesta reejecución.

Desde raíz, Linux/Python/Git locales y checkout quieto:

```bash
python3 -B scripts/audit-d5-evidence.py
python3 -B -m unittest discover -s testing/evidence_audit -v
python3 -B -m testing.evidence_audit.run_audit_lab
```

El primer comando devuelve **exit 1/FINDINGS esperado** por cambios pertinentes
desde I34; esto no significa que sus pruebas históricas fallen. El runner de
auditoría registra como PASS la detección esperada y sus pruebas propias. No
descubre `testing/D5` ni ejecuta las 321 pruebas históricas o SQL/Java/Docker.

Las pruebas del auditor usan repositorios y paquetes sintéticos propios, mutaciones
independientes, cuentas conocidas, sentinels hermanos, coordinación de un escritor
y timeout de un hijo Python propio. Los procesos Git de fixture crean commits
solo en esos temporales; el auditor de producto solo invoca comandos Git de lectura.
El harness registra sus recursos/exitcodes sin publicar paths temporales.

## Hallazgos y lectura correcta

I34 conserva integridad histórica, pero **seis inputs R de I36 amplían su discovery**:
dos módulos y cuatro archivos de campaña. Por tanto, STALE para el alcance actual.
Sus dos índices documentales también cambiaron. En A52 cambió un índice documental;
la aceptación local y sus bytes históricos se conservan. Son nueve hallazgos
explícitos, sin rebaselinar informes o reabrir hitos aceptados.

I36 coincide con su alcance registrado y contexto declarado al validar esta campaña:
CURRENT_RECORDED_SCOPE, no nueva ejecución ni aplicabilidad a APIs/targets reales.
Ambas campañas tienen **raw_binding NOT_RECORDED**: no existe salida bruta histórica
anclada en este registro y no se reconstruye. El comparador explícito de paquetes
brutos/registrados se ejercita con fixtures sintéticas, sin atribuirles identidad
histórica. El registro y código son raíces de confianza revisables, no firmas.

UI01–UI40 quedan inventariadas con origen/campaña/modalidad y mapas declarados.
Que haya referencias en cuarenta filas no acredita suficiencia de cuarenta
obligaciones. Los 281 IDs compartidos entre I34 e I36 se muestran como intersección;
no se convierten 281+321 en 602 pruebas nuevas ni se suman los tests del auditor.
Se conservan REVIEW_PENDING, Docs pendiente y ausencia de evidencia real.

## Límites y preservación

Límites de archivos/bytes/IDs/mapas/JSON/salida/Git y tiempo; pruebas con presupuestos
reducidos identificadas, sin benchmark o prueba simultánea de todos los máximos.
Paths cerrados, sin traversal, privados, enlaces, FIFO/dispositivos o fallback de
historia. Git no hereda trazas/configuraciones de entorno, no permite protocolos y
termina/espera hijos propios al fallar. Un cambio detectado durante la lectura
produce UNSTABLE_SNAPSHOT/UNDETERMINED, sin mezclar reintentos.

No snapshot atómico frente a escritor hostil/ABA, atestación de host/filesystem,
certeza de ejecución histórica por hashes o equivalencia de API/perfil externo.
La herramienta no recorre ni borra dev/run_data/D4 operativo o corpus privado.
Los únicos blobs D4 leídos son públicos y explícitos en el registro/cierre.

Kernel, parsers, laboratorios/runners T/R, reportes históricos y documentos previos
permanecen intactos. Los archivos de auditoría están fuera de su discovery y tienen
inventario propio. Los resultados se conservan con salida bruta propia y SHA,
separados del sellado documental para evitar hashes autorreferentes.

GI33/GI34 reciben evidencia de este alcance, GI40 auditoría de sus recursos. No
deducir persistencia o recuperación integrada de los PASS aislados. No crear
D5-approved/D5-CLOSURE global ni convertir 30/35 previo en 35/35 automáticamente.
La publicación exige autorización independiente del SHA concreto.
