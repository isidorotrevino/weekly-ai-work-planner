# Experimento acotado de D3 v0.2

Estado vigente: [D3 aprobado y cerrado como MVP conservador 1.0](../../docs/design/D3-approved.md) por «si, cierra D3». Las notas anteriores de cierre pendiente son históricas; no hay despliegue aprobado.
Ejecutar desde la raíz con Python 3.9+ y base de zonas IANA disponible:

```bash
python3 testing/D3/validate_design.py
```

El programa termina con error ante una discrepancia y emite un resumen JSON portable con hashes de entrada. Para actualizar intencionadamente el resumen de esta revisión:

```bash
python3 testing/D3/validate_design.py > docs/validation/D3-v0.2-results.json
```

Contrasta aritmética de cuentas/vectores, delta de retry, enlaces entre planes sin compromiso adicional, préstamos con deuda consumida, hipótesis de reparto unitario, herencia en un DAG pequeño, límites de la vía contra inanición y cambio horario civil. La revisión v0.2 añade oráculos de confianza/caducidad, intervalos de exclusión, tolerancia del recurso, heartbeat, triaje de incidentes y reconstrucción de servicio/vías. Usa 100 permutaciones deterministas en una comprobación; no son 100 pruebas adicionales.

Es un experimento de diseño sin dependencias de aplicación. No implementa scheduler, estimador, SemVer, workers ni publicación; no prueba guardas reales de SQL, checkpoints, concurrencia o rendimiento. El comportamiento completo por escenarios, incluido lo pendiente, figura en [D3 v0.2](../../docs/design/D3-capacity-scheduler-draft.md). No requiere repetir D2 y no altera su evidencia histórica. Ningún resultado aprueba parámetros ni cierra D3.

El resumen D3-v0.1-results.json se conserva como registro histórico de 23 comprobaciones sobre sus hashes anteriores; el script vigente reproduce v0.2 y genera un resumen separado. Las elecciones de política y el inicio de implementación están aprobados tras la revisión adicional exigida por 8B. El [núcleo Java inicial](../../scheduler-core/README.md) tiene pruebas JUnit separadas; este script conserva su alcance aritmético. Las metas numéricas de rendimiento se aplazan por 6B.

## Integración PostgreSQL I2/I3/coordinación

`bash testing/D3/run-postgres-tests.sh` ejecuta el núcleo, I2 sobre V12 e I3 sobre V13 y el coordinador sobre V14 en PostgreSQL desechable y después la regresión D2 sin cambios. `python3 scripts/summarize-d3-postgres.py > docs/validation/D3-OPTIMIZATION-results.json` exporta el resumen del último audit completo exitoso, con verificación de frescura y hashes. Alcance y requisitos: [scheduler-postgres](../../scheduler-postgres/README.md).

La [revisión integrada](../../docs/design/D3-REVIEW.md) añade aceptación V15 y cuatro mediciones del núcleo, con presupuestos locales de seguridad de 5 s y 30 s y sin SLA. Las plantillas anteriores se conservan.
