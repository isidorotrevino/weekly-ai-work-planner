# D5 I38 — auditor de evidencia local

Implementación del [contrato I37](../../docs/design/D5-I37-EVIDENCE-AUDIT-DESIGN.md)
y [matriz EA01–EA36](../../docs/design/D5-I37-EVIDENCE-AUDIT-REVIEW.md).
Python estándar, Linux, Git local y checkout quieto con los objetos históricos.
Sin instalación de dependencias, proveedores o credenciales.

Desde raíz:

```bash
python3 -B scripts/audit-d5-evidence.py
python3 -B -m unittest discover -s testing/evidence_audit -v
python3 -B -m testing.evidence_audit.run_audit_lab
```

El auditor solo lee los documentos y namespaces públicos permitidos. No acepta
argumentos, escribe archivos, importa módulos T/R, ejecuta sus pruebas o SQL,
consulta red ni repara registros. Imprime JSON saneado; no seguir enlaces ni
apuntar a corpus privado. No usarlo como permiso de ejecución o publicación.

Exit **0** significa coherencia del alcance registrado, no nueva ejecución ni
aceptación. Exit **1** señala cambios, ausencia de información necesaria o
aplicabilidad obsoleta/indeterminada. Exit **2** señala formato/lectura inválidos.
En la base I36 se espera exit **1**: I34 conserva integridad histórica, pero seis
inputs relacionales nuevos amplían su discovery y los índices documentales cambiaron.
I36 puede resultar CURRENT_RECORDED_SCOPE conservando raw_binding NOT_RECORDED.
Las salidas brutas históricas I34/I36 no se reconstruyen; la revisión global sigue
pendiente. El registro y la herramienta son raíces de confianza revisables, sin firma.

Las pruebas de este directorio crean únicamente repositorios/paquetes sintéticos
propios, incluyendo negativos y un hijo de timeout controlado. También leen el
registro y entradas públicas del checkout real. El runner solo carga estas 36
pruebas, registra recursos y hashes propios y comprueba el exit esperado del CLI;
no descubre `testing/D5`. Su PASS puede coexistir con FINDINGS/exit 1 del auditor.
No sumar sus tests a los 321 históricos o considerar reejecutadas regresiones.

Los presupuestos reducidos se etiquetan; no es benchmark ni prueba de todos los
máximos simultáneos. Cero acciones reales, consumo/reservas, activación, promoción,
despliegue o D6. D1–D4 cerrados y A52/I1–I20 sin ampliación; D5 global/G01–G07 abiertos.
P0 continúa: no publicar sin autorización independiente del SHA concreto.
