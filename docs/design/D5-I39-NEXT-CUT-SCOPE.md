# D5 I39 — siguiente corte tras I38

Fecha: **2026-10-23**, Europe/Madrid. **A seleccionado; diseño preparado para revisión**.
Base: `a956daf33681838f10bfb1c9c6c4a35722be0e77`.
[I38](D5-I38-EVIDENCE-AUDIT-LAB.md) ·
[Resultados](../validation/D5-I38-results.md) ·
[Obligaciones UI01–UI40](D5-I33-INTEGRATED-EVIDENCE-REVIEW.md) ·
[Criterios GI](D5-I23-GLOBAL-INTEGRATION-REVIEW.md).

English: proposed next-cut scope after the evidence auditor. Current integrity
and read-only audit verified; no test rerun, new implementation or global acceptance.

## Estado comprobado y autorizaciones

El usuario pide «continúa». Se revisan pendientes y se prepara una elección de
alcance; no se interpreta como permiso de publicar. P0 continúa para I32, handoff
y posteriores. D1–D4 cerrados y A52/D5-LOCAL-SYNTHETIC-I1-I20 aceptado conservan
alcance y evidencia. D5 global, G01–G07 y los siete criterios reales permanecen
abiertos. No sumar PASS aislados para inferir persistencia o recuperación integrada.

Git está limpio al iniciar, main ocho commits por delante de la referencia local
origin/main. No se consultó de nuevo el remoto; ese tracking no acredita su estado
actual. Se añade únicamente este documento de alcance, pendiente de selección.

Los siete hashes propios de campaña y dos documentales I38 coinciden con los
archivos actuales. El hash de su salida bruta coincide con el sellado separado;
sus 36 IDs PASS distintos y las referencias EA01–EA36 son coherentes. Esto es
integridad documental, **no reejecución de las 36 pruebas**.

La auditoría actual de lectura vuelve a producir FINDINGS/exit 1 con nueve
hallazgos esperados. Once entradas históricas MATCH; I34 STALE por ampliación
del discovery, I36 CURRENT_RECORDED_SCOPE, raw_binding NOT_RECORDED para ambas.
Los cambios documentales se mantienen separados. No reconstruir raw histórico,
rebaselinar informes, equiparar targets o revocar hitos aceptados por esos hallazgos.

## Pendiente que orienta la recomendación

| Criterio | Evidencia acotada disponible | Revisión aún pendiente |
|---|---|---|
| GI33 | Inventarios T/R y auditor fijo I38, hashes/mapas/contexto | Relación semántica entre obligación, frontera, caso y evidencia; límites del contexto y raw histórico ausente |
| GI34 | Grupos/targets y preservación pública; intersección de 281 IDs | Alcance exacto de preservación y regresiones; no convertir hashes o suites acumulativas en ejecución nueva |
| GI38 | Campañas T/R durables, crash/reinicio y conciliación explícita | Comprobar cada frontera y parametrización exigida leyendo código/pruebas; no asumir cobertura porque haya mapa |
| GI39 | CAS, revocación/ABA y carreras T/R de fixture | Identificar los conflictos efectivamente ejercitados y las exclusiones; no atribuir capacidades reales |
| GI40 | Recursos/limpieza y declaraciones de cero actividad por campaña | Separar oráculos medidos de declaraciones y límites de cada campaña; no extrapolar a dev o proveedores |

Los mapas cubren referencias en cuarenta filas UI, no una aceptación automática
de cuarenta obligaciones. Docs y los criterios reales siguen pendientes. La
falta de raw histórico debe registrarse y evaluarse con límites explícitos, sin
fabricarlo ni convertir la lectura de código en una nueva ejecución empírica.

## Opciones de alcance material

El usuario eligió **A**, preparar la revisión conjunta de suficiencia. El
[contrato I39](D5-I39-SUFFICIENCY-REVIEW-DESIGN.md) y la
[matriz de revisión](D5-I39-SUFFICIENCY-REVIEW-MATRIX.md) concretan esa elección.
La revisión semántica propuesta todavía no está ejecutada ni autorizada.
Las opciones siguientes conservan el planteamiento original.

**A — Recomendada:** preparar contrato y matriz para revisión conjunta de suficiencia
de GI33/GI34/GI38/GI39/GI40. Fijar por obligación: código/prueba/campaña/commit,
frontera y parametrización, oráculo, evidencia registrada, limitación y pendiente.
Distinguir cobertura declarada, comprobada por lectura y ejecución registrada.
El resultado propuesto sería una revisión documental con hallazgos y recomendaciones,
sin cerrar automáticamente criterios o brechas, ampliar A52 o escribir código T/R.

**B — Alternativa:** preparar contrato y matriz para ampliar el auditor a paquetes
futuros con raw anclado y enriquecimiento documental explícito, usando I38 como
primer paquete existente. Fijar identidad, campos comunes/añadidos, referencias
de confianza e invalidación antes de implementar. No reconstruir raw I34/I36 ni
atribuir a esta ampliación la revisión semántica pendiente de GI38/GI39.

La elección autoriza preparar contrato y matriz; la ejecución de esa revisión o
la implementación del auditor ampliado se concretará después para aprobación.
Publicación sigue siendo decisión independiente sobre SHA y alcance exactos;
no hay push/PR autorizado ni nueva solicitud que sustituya P0.

Sin proveedores/credenciales reales, corpus privado, consumo/reservas, operaciones,
activación, promoción, despliegue ni D6. Sin lectura/limpieza de dev/run_data/D4
operativo; conservar código, evidencia y documentos históricos.
