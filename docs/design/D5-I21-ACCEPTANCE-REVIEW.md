# D5 I21 — revisión de alcance y aceptación pendiente

Fecha: 2026-10-22. Autoridad: D5-A50, auditoría documental sin SQL ni cierre.
[Auditoría y trazabilidad](D5-I21-SCOPE-AUDIT.md) ·
[Inventario verificable](../validation/D5-I21-audit.json).

English: review proposal, not a closure approval. Recorded I20 runtime results and
I21 documentary checks are separate. A bounded local milestone could be accepted
explicitly while the broader D5 integration deliverable remains open.

## Perímetro candidato, todavía sin aceptación formal

Laboratorio local sintético de ingestión, revisión y correspondencias hacia tareas
BACKLOG, con clientes Python/CLI y PostgreSQL desechable V30 + propuestas V31–V39.
Los perfiles admitidos son los definidos en I1–I3; la proyección mínima es
Item→title y Objective→description. No se interpreta el resto de la fila como
instrucciones de ejecución, aprobación, verificación, dependencias o estado D2.

El flujo cubre comparación/simulación, aplicación revisada, bootstrap, reaparición,
adopción elegible y resolución origen/local presente, reaparecida o aislada.
El laboratorio SQL está restringido a contenedores propios etiquetados, sin red ni
puertos; no está integrado en el Compose dev persistente. La reproducción
registrada corresponde al entorno Linux/Python/Docker documentado por los runners;
no acredita otros sistemas, producción o comportamiento de terceros.

Quedan fuera activación, operaciones, integración real, credenciales, promoción y
despliegue. La fixture negativa transitoria de operación autorizada en A18 se
revierte obligatoriamente: no implica operación ejecutada ni excepción al
perímetro final sin operaciones.

## Matriz documental de revisión

«Respaldado» significa evidencia registrada y trazada; no ejecución nueva ni
aceptación humana. La clasificación completa L/G/E está en la auditoría.

| ID | Criterio propuesto | Resultado de la auditoría | Base |
|---|---|---|---|
| C01 | Declarar un hito local separado de D5 global | **Pendiente de decisión expresa** | A50 no autoriza cierre; G01–G07 siguen visibles |
| C02 | Identidad, bytes/hash y perfiles explícitos sin normalización silenciosa | Respaldado dentro de los perfiles existentes | L01–L03; I1–I5, regresiones I20 |
| C03 | Revisión por fila/manifiesto, CAS, replay y atomicidad | Respaldado dentro de variantes implementadas | L04/L09; I5–I20 |
| C04 | Tareas propias BACKLOG, proyección mínima y ausencia sin borrar/cerrar | Respaldado; no pipeline de grooming completo | L05; I8/I10, G05 pendiente |
| C05 | Identidad reaparecida y edición local requieren sus pruebas/revisiones | Respaldado; ID reutilizado permanece bloqueado | L06/L07; I12/I14/I18/I20 |
| C06 | Adopción explícita conserva toda la tarea y rechaza trabajo/procedencia previos | Respaldado dentro de A35–A40 | L08; I16, E02 fuera |
| C07 | Contadores operativos finales cero y limpieza propia | Registrado en I20; no ejecución I21 | L11; 259 tareas sintéticas, cero operaciones/outbox/entregas/intentos/reservas |
| C08 | Regresión y separación de targets, sin sumar campañas solapadas | Registrado en I20 | 264 SQL, 51 locales, 157 D2 independiente; todas sin fallos/errores |
| C09 | Preservar contratos, manifests e informes históricos D1–D4 y D5 | Comprobado por hashes actuales | Inventario I21 y verificaciones de entradas anteriores; sin reescritura histórica |
| C10 | Entrada bilingüe coherente y guía reproducible del laboratorio | README actualizados; enlaces comprobados | README principales, guía I20 y testing/D5; no producto integrado en dev |
| C11 | Distinguir extensiones locales opcionales de obligaciones globales | Propuesta trazada, pendiente de conformidad | E01–E07 frente a G01–G07; no cambia D1 ni mueve brechas a D6 |
| C12 | Aprobar aceptación o cierre con evidencia y límites explícitos | **No concedido por esta auditoría** | Sin D5-approved ni D5-CLOSURE nuevos; publicar no equivale a aprobar |

No se identifica un fallo de pruebas abierto en el informe I20. Esta revisión no
es una revisión exhaustiva de seguridad/código ni prueba que no existan defectos.
Los rechazos de IDs reutilizados, adopciones no elegibles y cambios de perfil no
son incumplimientos de los contratos que los excluyen.

## Qué impide afirmar D5 completo

- G01/G05: falta acordar el contrato completo Gentle-AI/routing y la aceptación de
  requisitos/épicas/grooming. Los ocho campos tabulares y las tareas BACKLOG no lo sustituyen.
- G02/G03: faltan contratos y validación de Drive/Plane, incluida revisión remota,
  conflicto, idempotencia y conciliación externa.
- G04/G07: no se han validado adaptadores/CLI, cuotas comerciales o ciclo integrado
  reales; las pruebas sintéticas no acreditan esos efectos.
- G06/C01/C12: falta una decisión integrada de perímetro y aceptación. Es posible
  reconocer un hito parcial sin declarar cerrado el entregable D5 global.

Nada de esta lista autoriza conectores reales, autenticación o ejecución de trabajo.
D6 conserva sus obligaciones operativas separadas. Sheets/Monday sigue opcional.

## Comprobaciones de I21 y cómo reproducirlas

El [JSON propio](../validation/D5-I21-audit.json) registra hashes relativos de las
fuentes consultadas, informes anteriores y entradas ejecutables verificadas,
además de los conteos de comprobaciones. No contiene corpus privado ni logs brutos.
Los archivos de salida I21 se excluyen de su propio inventario para evitar ciclos.

Para comprobar sus entradas desde la raíz del repositorio:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
report = json.loads(Path('docs/validation/D5-I21-audit.json').read_text())
for path, digest in report['inputs'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
print('Audit inputs match:', len(report['inputs']))
PY
python3 scripts/check-publication.py
git diff --check
```

Las verificaciones históricas adicionales contrastan las entradas SHA-256 de los
manifiestos D3/D4, el documento canónico D4 y los informes D5 I4–I20; sus conteos
están en el JSON. No se reejecutan SQL, parser, D2/D4 ni Docker en I21. El chequeo
de publicación detecta los patrones configurados, no garantiza ausencia de todos
los secretos posibles. Los hashes vinculan contenido con resultados registrados;
no recrean esas ejecuciones ni autentican a sus autores.

## Decisiones siguientes con opciones

1. **Aceptar la clasificación y preparar la aceptación de un hito local acotado
   (recomendada).** Elaborar un documento concreto de aceptación del laboratorio,
   con límites, evidencias y continuidad G01–G07; mantener D5 global abierto.
   Preparar ese documento no equivale a aprobarlo ni autoriza SQL nuevo.
2. **Priorizar el contrato Gentle-AI/routing de D5 global.** Acordar primero qué
   muestras sin secretos y scripts existentes revisar, y preparar contrato/matriz;
   no implementar conectores ni usar proveedores reales en este paso.
3. **Ajustar el perímetro candidato.** Indicar qué caso de E01–E07 se considera
   necesario y por qué; diseñar requisitos y aceptación antes de ampliar código.

La publicación de I21 requiere autorización del commit concreto. Cualquier
aceptación posterior debe precisar si reconoce solo el hito local; no se deduce
cierre de D5 global de una aprobación documental o de publicación.
