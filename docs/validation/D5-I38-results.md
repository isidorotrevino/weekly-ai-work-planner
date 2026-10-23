# D5 I38 — resultados de auditoría de evidencia

Fecha: **2026-10-23**, Europe/Madrid. **PASS: 36 pruebas nuevas del auditor**.
[Implementación/autoridad](../design/D5-I38-EVIDENCE-AUDIT-LAB.md) ·
[Registro fijo](D5-EVIDENCE-REGISTRY.json) · [Salida bruta](D5-I38-raw.json) ·
[Sellado documental](D5-I38-results.json).

English: 36 auditor tests passed; historical T/R and SQL campaigns were not rerun.
Read-only CLI returned expected findings, not global acceptance or publication.

## Autorización y ejecución

A aprueba el contrato I37 `4eb9de6119bd6fe709981692282153c358040531` e implementar/validar el auditor,
registro fijo y EA01–EA36. P0 sigue vigente. Linux/Python 3.14.4.
Comando de la campaña final, desde raíz:

```bash
python3 -B -m testing.evidence_audit.run_audit_lab
```

La salida bruta se conserva sin enriquecimiento posterior. El runner no guarda
archivos por sí mismo; se capturó stdout en el archivo enlazado. Siete inputs
propios tienen hashes antes/después idénticos. El sellado documental es separado
y no se interpreta como parte de la salida original del runner.

| Medida | Campaña final |
|---|---:|
| Pruebas distintas EA01–EA36 | 36 |
| Fallos / errores / omisiones | 0 / 0 / 0 |
| Regresiones T/R o SQL ejecutadas | 0 |
| Subtests registrados, no tests adicionales | 33 |
| Ámbitos temporales propios / restantes | 36 / 0 |
| Subprocesos propios / vivos | 718 / 0 |
| Git / Python propios | 716 / 2 |

Los procesos Git incluyen creación/commit de repositorios sintéticos por el harness
además de lecturas del auditor. Los dos Python son el hijo de timeout controlado
(terminado por SIGKILL) y el CLI real (exit 1 esperado). Los códigos finales son
715 con 0, uno con -9, uno con 1 y uno Git con 128 por objeto histórico inexistente
intencional. El escritor coordinado de EA28 termina y se comprueba en su prueba.
Todos los recursos son propios; sentinels hermanos intactos. No inspección o
limpieza de dev/run_data/D4 operativo. No sumar campañas de desarrollo previas.

## Auditoría actual y límites de inferencia

CLI `python3 -B scripts/audit-d5-evidence.py`: **FINDINGS, exit 1 esperado**, nueve
hallazgos, once entradas históricas con integridad MATCH. Se detectan seis archivos
R añadidos al discovery de I34, sus dos índices documentales cambiados y un índice
documental cambiado respecto de A52. El auditor no modifica ni rebaselina nada.

| Entrada | Resultado acotado |
|---|---|
| I34 | Históricamente íntegro; STALE para el discovery actual ampliado |
| I36 | CURRENT_RECORDED_SCOPE, contexto declarado coincidente; 78 inputs y siete documentales coinciden, además del JSON anclado |
| I34/I36 raw_binding | NOT_RECORDED en ambas campañas; no raw histórico reconstruido |
| D3/D4/A52 | Referencias públicas históricas verificadas, grupos/targets conservados; HISTORICAL_NOT_RERUN |
| UI01–UI40 | Inventario con mapas declarados y modalidad, suficiencia REVIEW_PENDING |

I34 e I36 comparten 281 IDs; no son 602 pruebas nuevas. Las 36 del auditor tampoco
se suman a los 321 históricos como campaña funcional integrada. Los cierres D1–D4
y la aceptación local A52/I1–I20 permanecen intactos. La preservación D1/D2 tiene
el límite de las referencias existentes explícitas; no inventario exhaustivo.
El registro contiene 296 paths únicos de dependencias públicas, con commits y hashes;
no una prueba de ejecución, de representatividad o de APIs reales.

Los presupuestos reducidos de EA29/EA30 se identifican; no todos los máximos a
capacidad completa ni benchmark. Lectura exige checkout quieto: no snapshot atómico
contra escritor hostil/ABA ni atestación de filesystem/host. Registro y herramienta
son raíces de confianza revisables, sin firma. Hash/escaneo no es garantía exhaustiva.

## Preservación y exclusiones

No se modifican archivos previamente tracked: kernel, parsers, T/R, runners,
contratos/reportes históricos e índices conservan sus bytes. Comprobaciones
documentales de enlaces, hashes propios/I37/I36, diferencias Git y escaneo de
publicación se registran en el JSON separado. No se repiten tests por estas
comprobaciones documentales ni se publica nada.

Cero proveedores/credenciales reales, red remota, SQL/Docker/Java funcional,
operaciones/intentos operativos, consumo/reservas o activación. Sin promoción,
despliegue ni D6. GI33/GI34 reciben evidencia del auditor acotado; GI40 solo la de
sus recursos. **D5 global, G01–G07 y la revisión global de cinco criterios siguen
abiertos; siete criterios reales y Docs pendientes.** No deducir recuperación
integrada de PASS aislados ni elevar automáticamente 30/35 a 35/35. La publicación
requiere autorización independiente de un SHA concreto.
