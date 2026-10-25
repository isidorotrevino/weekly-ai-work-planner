# I61 — evidencia causal CE43

Harness sintético local del contrato [I60](../../docs/design/D5-I60-CAUSAL-CELLS-DESIGN.md), con el ajuste de preparación T UPDATE autorizado expresamente en I61 y registrado en el [laboratorio](../../docs/design/D5-I61-CAUSAL-CELLS-LAB.md).

Ejecutar desde la raíz, sin optimización:

```sh
python3 -B -m testing.causal_frontier_cells.run_causal_cells_lab
```

CE01–CE39 corresponden uno a uno a las 39 celdas calificadas I59. CE40–CE43 son controles, sin caídas positivas. El runner captura stdout JSON real; cada escenario conserva identidad, gate, hashes/HEAD/recibos, lector independiente, APIs públicas CLIENT/REMOTE spawn pasivas y continuación explícita. No infiere recuperación de la suma de PASS.

Se reutilizan helpers públicos pinneados HF/FN para propiedad/procesos y observación; RECORDS es propio. No se modifican helpers anteriores, producto, fixtures, schemas, hooks o registro I38. El runner declara sus entradas efectivas completas con hashes pre/post, incluidos I60 y todos sus inputs. No incluye sus propios resultados/raw en un ciclo.

UPDATE prepara CREATE v1 y edición pública de foreign a v2, y exige efecto objetivo v2→v3 con payload distinto y foreign preservado. T actualiza fuente/base mediante una segunda captura I26, EVALUATION/EFFECT revisados y APPLY públicos; R usa segundo SOURCE/BATCH y selección por su recibo exacto. CLOSE publica tombstone sobre manifiesto CREATE. El hijo deriva modo y petición real; no acepta P del padre como autoridad.

Ocho regresiones se ejecutan y sellan por separado: Python321, HC24, HF40, IC30, UQ24, RV20, NA36 y FN64. Sus runners históricos conservan inventarios propios; no se afirma que descubran este directorio nuevo. Sus repeticiones no son pruebas CE adicionales.

Límites CE: cuatro hijos vivos, espera20s, caso120s, campaña900s, 256 eventos/caso, 16KiB/evento, raw12MiB. Sólo raíces propias; timeout negativo separado de SIGKILL positivo; cero hijos/hilos/raíces pendientes. Sin OSError nuevo, energía/host/disco/NFS/Windows, ampliación nativa, auditor, SQL, proveedor/credenciales reales, consumo/reservas, activación, promoción, despliegue o D6. UI22.2, H07, GI y D5 global conservan su estado abierto hasta revisión propia. Este comando no publica.
