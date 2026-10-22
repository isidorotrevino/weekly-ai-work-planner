# D5 I26 — resultados de captura incremental sintética

Fecha: 2026-10-22. Base publicada: `e66a42c`.
[Implementación](../design/D5-I26-DRIVE-INCREMENTAL-LAB.md) ·
[Contrato I25](../design/D5-I25-DRIVE-INCREMENTAL-DESIGN.md) ·
[Informe verificable](D5-I26-results.json).
**PASS sintético filesystem/procesos; G01–G07 y D5 global abiertos.**

D5-A63 aprueba I25 y autoriza DI01–DI28 con fixtures públicas sintéticas y carpeta
temporal propia. Se añaden almacén/harness/tests; no Google/HTTP, SQL, Docker,
credenciales, referencia D5 seleccionada, aplicación D2, activación o D6.
No se relee corpus privado ni se modifica código, parsers o fixtures históricos.

## Ejecución y separación de campañas

`python3 -m testing.D5.run_incremental_lab`, Linux/Python **3.14.4**, biblioteca estándar:

| Grupo actual | Pruebas | Fallos / errores / omisiones |
|---|---:|---|
| I26 DI01–DI28 (algunos casos con más de un test) | 30 | 0 / 0 / 0 |
| I24 offline | 35 | 0 / 0 / 0 |
| Python local anterior | 51 | 0 / 0 / 0 |
| Total distinto de esta campaña | **116** | **0 / 0 / 0** |

Las 28 filas de matriz **no** se suman a los 116 tests. Los IDs de los 30 tests
nuevos se mapean a esas filas en el JSON. Las 86 regresiones se ejecutaron ahora;
no son números copiados de un resultado anterior. No se reejecutaron SQL/D2/D3/D4
ni se suman sus campañas históricas a I26. El elapsed es observación de campaña,
no benchmark ni garantía de rendimiento.

## Fallos, recuperación y limpieza observados

- DI01–DI07: ámbito explícito y ancla antes de inventario; páginas/fases/tokens,
  repetición lógica con ocurrencias conservadas, poll vacío y lectura de estado
  desde otro proceso. Sin snapshot global ni historial completo de revisiones.
- DI08/DI09: bytes/diagnósticos/recibo/cursor en un solo commit; evento transitorio
  posterior no confirma un prefijo. Exportación Docs conserva OBSERVED_EXPORT al
  reabrir, sin selección automática de referencia.
- DI10–DI13: cuatro hijos propios terminados con SIGKILL antes de objeto, después
  de objeto, antes de reemplazo de head y después de confirmarlo. Se conserva head
  anterior o se recupera recibo exacto; huérfanos/temporales no se promueven por fecha.
- DI13 adicional: fallo de fsync tras reemplazo devuelve UNKNOWN_COMMIT. Mientras
  falla fsync de recuperación no se devuelve confirmación; al restablecerlo se
  recupera el recibo alcanzable sin nueva aplicación.
- DI14: dos escritores reales del harness preparan sobre la misma cabeza y esperan
  una barrera antes de competir. Solo uno confirma; el otro devuelve conflicto.
  command_id con request distinto no reemplaza el recibo; replay no regresa cursor.
- DI15–DI21: diagnósticos recuperables de allowlist/MIME/tamaño/removal/acceso,
  captura bloqueada y posterior disponibilidad; fuente cambiante/global auth/scope
  bloquean. Un flag caller-terminal no permite saltar errores; nunca se borra/cierra D2.
- DI22–DI28: ámbito incompatible, envelope/JSON inválido, presupuestos, ciclos de
  tokens, head/objeto/parent/scope/bytes corruptos, enlaces/propietario incorrectos
  y limpieza selectiva. No se repara automáticamente ni se elige un objeto mayor.

Se crearon **33 raíces marcadas** del laboratorio y se comprobaron **33 eliminadas**.
Se iniciaron siete hijos explícitos de fixture: tres terminaron normalmente y
cuatro con código `-9` en fallos controlados; **cero hijos propios vivos** al final.
Sentinels hermanos de prueba sobrevivieron, incluidas rutas de enlace adversas.
Son fixtures de entornos ajenos, no inspecciones de dev/run_data/D4 reales.
El harness solo mata/espera los procesos que creó y limpia sus raíces originales.

Se verifican los límites configurados de 16 eventos/página, JSON 32 MiB y 1.024
commits. La prueba de agotamiento usa también un presupuesto reducido del mismo
mecanismo; no se atribuye una campaña de escala con 1.024 commits llenos. No hay
truncamiento parcial para avanzar cursor. Los tokens son opacos y no se simula
una caducidad temporal que el contrato público no establece.

## Preservación, evidencia y límites

Entre archivos anteriores solo se amplían el índice documental y la guía D5.
Se contrastan hashes de todos los demás archivos de la base, 245 entradas D3/D4,
documento canónico D4 y 560 entradas de campañas D5 I4–I20. Las revisiones
posteriores conservan sus bytes y se contrastan con su commit cuando sus índices
documentales han evolucionado. El informe nuevo registra inputs/entorno/mapa de
casos y limpieza; no sustituye manifiestos de cierre o informes históricos.

Se comprueban enlaces, `git diff --check` y los patrones de publicación. Los logs,
paths temporales, PIDs y capturas completas no entran en el informe versionado.
Capturas/inspect sí contienen bytes íntegros y son privados durante el laboratorio.
El chequeo de publicación no es detector universal de secretos o defectos.

Hay evidencia sintética nueva para GI07/GI08/GI09/GI11 y regresión de los 18
criterios modelados I24: **22 de los 35 criterios S tienen evidencia acotada**.
Los 13 S restantes y los siete R no se ejecutan por este corte. GI38/GI39/GI40
siguen pendientes como criterios integrados generales, aunque se prueben fallos y
limpieza de la frontera de captura. No se declara completa ninguna brecha global.

No se acredita energía/disco/NFS/Windows, resistencia a rollback hostil, firma del
proveedor, permisos de una cuenta real o integración Google. La marca y los hashes
no aíslan a un propietario/caller Python hostil. Sin promoción, despliegue ni D6;
el hito I1–I20 conserva su aceptación/perímetro exactos.
