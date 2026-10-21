# D5 I4 — resultados de persistencia sintética

Fecha: 2026-10-21. **PASS acotado; D5 abierto.**
[Implementación y autorización A09](../design/D5-I4-PERSISTENCE-LAB.md)
· [Resumen portátil con casos y hashes](D5-I4-results.json).

| Campaña nueva | Comando desde la raíz | Resultado |
|---|---|---|
| Parser/comparación/adaptador local | `python3 -m unittest discover -s testing/D5 -v` | 47 pruebas, 0 fallos/errores; 44 existentes y 3 nuevas de frontera del adaptador |
| PostgreSQL D5 aislado | `python3 -m testing.D5.run_postgres_lab` | 21 pruebas P01–P10, 0 fallos/errores |
| Regresión D2 intacta | `bash testing/D2/run-docker-audit.sh` | 157 pruebas, 0 fallos/errores/omisiones |

La ejecución final D5 usa PostgreSQL 16.15 y la imagen local
`postgres:16-bookworm`; el identificador de imagen y hashes de entradas están en
el resumen JSON. Los resultados brutos, logs y recibos son privados bajo
`work/d5/postgres/`; la regresión D2 tiene su propio directorio en
`work/docker-audit/`. No se incorporan fuente privada, snapshots reales o logs a Git.

## Comportamientos observados

- Registro de fuentes nuevas, colisiones de clave/UUID, rechazo de adopción de
  documentos históricos y bloqueo por cambios externos de identidad o head.
- Ámbito documento/proyecto/perfil; FK compuesta que rechaza una observación
  adjunta a otra cabeza; envelope cerrado, claves duplicadas y tipos inválidos.
- Bytes fuente exactos de 2 MiB aceptados y exceso rechazado por SQL y adaptador.
  Almacenamiento de artefacto de 32 MiB aceptado y exceso rechazado en transacciones
  del propietario con rollback. No es una prueba de parser de padding arbitrario.
- Hashes, bytes base64, metadatos y reconstrucción del parser; un artefacto con
  semántica adulterada no llega a SQL mediante el adaptador. SQL no es un segundo
  parser ni una atestación de afirmaciones del documento.
- Deduplicación de contenido entre etiquetas/perfiles del mismo documento,
  separación entre documentos y nuevas recepciones para comandos nuevos.
- Ingesta sin selección, selección explícita y diagnóstico BLOCKED que conserva
  su bloqueo; seleccionar otra vez con nuevo comando incrementa versión.
- Dos sesiones de ingesta esperando simultáneamente el mutex: una revisión y dos
  observaciones. Dos selecciones esperando ese mutex con versión 0: un éxito y
  un conflicto. Ambas barreras registraron dos sesiones realmente bloqueadas.
- Secuencia A→B→A, CAS obsoleto, agotamiento bigint y replay histórico sin mover
  cabeza. Cambiar request/acción de un comando no reemplaza su recibo.
- Sesión terminada tras escribir ingesta y antes del commit: ningún hecho parcial;
  sesión terminada tras selección: cabeza/recibo/selección sin cambios. Retry
  exacto posterior funciona en ambos casos.
- Resultado confirmado descartado, reinicio real de PostgreSQL conservando su
  volumen, recuperación por recibo y bytes exactos. No se simula una partición de
  red ni se confunde un resultado histórico con la referencia actual.
- Lector/escritor sin DML directo ni autoridad D2, hechos inmutables y funciones
  D5 sin EXECUTE público. Tablas temporales no redirigen las lecturas propietarias.
- Flujo CLI real register → ingest → reference → select → receipt, incluyendo
  código 2 para selección obsoleta. Estado público y D2, salvo nuevas revisiones
  permitidas, idéntico antes/después; ningún head D2 se mueve.

El runner final eliminó su contenedor y comprobó la desaparición de su volumen
anónimo. No usó red, puertos, `run_data`, Docker Compose o datos reales. Los pilotos
iniciales también tuvieron limpieza exclusiva; sus diagnósticos permanecen privados.
Las correcciones de bootstrap, permisos REFERENCES y sintaxis de la propuesta se
validaron después en campañas nuevas; no se reetiquetan intentos fallidos como PASS.

## Conservación y alcance

Se verifican por separado los hashes de cierre D3/D4 y el diff de entradas
históricas. No se reescriben manifiestos ni informes I1–I3. La nueva propuesta V31
solo se ha aplicado en bases desechables construidas sobre V1–V11. No hay
integración ejecutada D5/V30, promoción Flyway, importación de tareas, activación,
proveedores o credenciales reales, despliegue ni D6.
