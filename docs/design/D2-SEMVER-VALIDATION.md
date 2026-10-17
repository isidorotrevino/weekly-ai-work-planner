# D2 — validación pendiente de SemVer

Estado: requisito de cierre aprobado (D2-A05); gramática de rangos aprobada (D2-A06). D2 permanece abierto. Este documento especifica trabajo pendiente; no afirma que esté implementado ni probado.

## Alcance normativo y propuesta

Las versiones deberán cumplir [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html): tres componentes numéricos sin ceros iniciales, identificadores prerelease y metadatos de build. El orden compara números y luego prereleases; una versión estable supera a sus prereleases y los metadatos de build no afectan a la precedencia.

SemVer no proporciona una gramática de rangos. Se aprueba la documentada por [npm/node-semver](https://github.com/npm/node-semver#ranges): comparadores, intersecciones, uniones `||`, rangos con guion, parciales/comodines, tilde y caret. La admisión de prereleases será explícita según las reglas del rango. Esta elección fue aprobada por el usuario en D2-A06.

No se exige usar Node en producción. La implementación Java/PostgreSQL y cualquier dependencia se elegirán a partir del contrato aprobado, revisando licencia, mantenimiento y resultados de conformidad. La gramática normativa y su versión deberán quedar fijadas; una actualización de librería no cambiará silenciosamente decisiones de admisión.

## Cambios necesarios en el prototipo

1. Inventariar `d2.compatible`, sus llamadas de admisión y finalización, y la persistencia de versiones y restricciones. No reemplazar únicamente la comprobación inicial: todas las guardas deberán coincidir.
2. Distinguir entradas inválidas de versiones válidas que no satisfacen el rango. Ambas bloquean la dependencia; conservar una razón comprensible en la capa de resolución.
3. Conservar el texto original, la identidad exacta de la versión y el contrato/hash verificado. Igual precedencia no autoriza reutilizar evidencia de otro artefacto o build.
4. Definir límites de tamaño y coste de análisis con errores explícitos. No truncar ni convertir valores fuera de rango; no afirmar soporte ilimitado si se usan enteros de tamaño fijo.
5. Revisar los datos existentes antes de promover una migración. Las restricciones previas deben interpretarse igual o generar una discrepancia visible para revisión.
6. Añadir una propuesta de migración y pruebas de contrato sin alterar las migraciones históricas. No promoverla a la línea aprobada ni iniciar la aplicación completa por esta tarea.

## Matriz que deberá ejecutarse

| Grupo | Casos y resultado a comprobar |
|---|---|
| Sintaxis | Versiones estables, prereleases y builds válidos; rechazo de identificadores vacíos, ceros iniciales prohibidos, caracteres inválidos y versiones incompletas |
| Orden | Comparación numérica, orden de identificadores prerelease y estable posterior; builds con igual precedencia |
| Rangos básicos | Exactos y comparadores; intersección, unión y límites abiertos/cerrados |
| Rangos abreviados | Parciales, comodines, guiones, caret con major cero y tilde; expansión en límites inferiores/superiores |
| Prereleases | Admisión explícita y exclusión por defecto; cambios de núcleo numérico y comparación entre candidatos |
| Errores y coste | Restricciones malformadas, números grandes y entradas largas; rechazo determinista sin desbordamientos ni admisión accidental |
| Integración SQL | HARD bloquea si no satisface el rango; MOCKABLE conserva su regla de finalización; CLAIM y VERIFY coinciden |
| Identidad y evidencia | Builds de igual precedencia conservan versión, entorno, hash y generación de evidencia exactos |
| Regresión | Subconjunto ya admitido, invalidación y concurrencia; ninguna pérdida de garantías previas |

Las filas de rangos se rigen por D2-A06. Se requieren resultados esperados independientes del código bajo prueba y pruebas a través de los entrypoints SQL, además de los casos del parser. La ejecución completa debe conservar el informe anterior y publicar un nuevo resumen con conteos y limitaciones reales.

## Puerta de cierre

A05 seguirá pendiente de validación hasta que el contrato completo acordado tenga evidencia ejecutable satisfactoria. Las **147 pruebas existentes** validan el prototipo anterior, no esta ampliación. Resolver este requisito tampoco cierra D2: continúan las demás decisiones del [registro](D2-DECISIONS.md) y la aprobación final expresa del usuario.
