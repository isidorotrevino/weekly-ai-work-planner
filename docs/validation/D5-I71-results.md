# I71 — captura prospectiva: nueve alcances registrados, P01 bloqueado

[Contrato I69](../design/D5-I69-PROSPECTIVE-CAPTURE-DESIGN.md) · [Componente I70](D5-I70-results.md) · [Autorización](D5-I71-capture-authorization.json) · [Resultados y hashes](D5-I71-results.json) · [Integridad](D5-I71-integrity.json).

Base local `1d419fcffdcd598df301e9b9910c150ed0f23d38`. La selección A autoriza P01–P10 separados y exige detener el alcance afectado ante incompatibilidad. Se intentaron las diez campañas, en serie, con el capturador y registro I70 intactos. No hubo reintentos ni ampliación de presupuesto.

| Alcance | Ejecutadas/previstas | Raw funcional | Captura | Eventos |
|---|---:|---|---|---:|
| P01 Python | 77/321 | PASS | BLOQUEADA | 16384 |
| P02 GX | 90/90 | PASS | Pendiente de suficiencia | 9785 |
| P03 HC | 24/24 | PASS | Pendiente de suficiencia | 1773 |
| P04 HF | 40/40 | PASS | Pendiente de suficiencia | 2148 |
| P05 IC | 30/30 | PASS | Pendiente de suficiencia | 2753 |
| P06 UQ | 24/24 | PASS | Pendiente de suficiencia | 1736 |
| P07 RV | 20/20 | PASS | Pendiente de suficiencia | 2194 |
| P08 NA | 36/36 | PASS | Pendiente de suficiencia | 2440 |
| P09 FN | 64/64 | PASS | Pendiente de suficiencia | 4300 |
| P10 CE | 43/43 | PASS | Pendiente de suficiencia | 4431 |

448 ocurrencias ejecutadas de 692 previstas: 371 pertenecen a nueve capturas completas y 77 a P01 parcial. Quedan 244 sin ejecutar. No son pruebas distintas adicionales. P02–P10 conservan388 filas originales de escenario; esto no constituye una revisión de suficiencia ni cierre.

## Bloqueo P01

El límite acumulado de16.384 eventos se agotó durante DR29. La suite terminó entre tests con77 resultados PASS (48 T y29 R), sin fallos funcionales reportados. El raw PASS sólo describe esas77 ocurrencias. El sidecar es INVALID_CAPTURE por EVENT_CAMPAIGN_BUDGET, INCOMPLETE_TEST_SET e INVALID_TEST_COUNT. Falta un TEST_END en el stream agotado; no se trata como completo. El máximo observado por test fue1.317 frente al límite2.048.

Siete frames tienen DOMAIN_IDENTITY_NOT_RECORDED: DF01, DF02, DF07, DF43, DF48, DR01 yDR02. Los controles de inventario requieren revisar aplicabilidad; los casos de dominio requieren una referencia realmente observada. No se fabrican identidades a partir del PASS, del frame del capturador o de una expectativa. Los IDs exactos están en el JSON.

Se conservan raw, sidecar, contexto, OWNER y salida del launcher de cada alcance. Los hashes de inputs antes/después coinciden; los observadores se restauraron y el launcher confirmó OWN_GROUP_GONE en las diez sesiones. Cada runner reportó su limpieza de fixture. Esta comprobación se limita a esos recursos y no es un inventario del equipo.

## Ajuste concreto propuesto, aún sin autorizar

Preparar I72: contrato y matriz para captura P01 con almacenamiento por páginas acotadas, techo acumulado explícito calculado desde los datos registrados y guardas de tiempo/tamaño. Revisar la aplicabilidad de los siete frames por test, separando controles sin Store de la evidencia de dominio exigida. Preservar este intento y diseñar un nuevo destino para una futura captura. No truncar, muestrear o reducir observadores para obtener un PASS; no sustituir oráculos funcionales.

Este informe no autoriza modificar el capturador, sus pins o presupuestos, ni reejecutar P01. Una implementación y una nueva campaña requerirán autorización posterior al contrato y matriz.

P0 y agregado81/3 intactos; UI01.2/UI04.1/UI09.2 siguen PARTIAL. D1–D4 cerrados y el hito D5-LOCAL-SYNTHETIC-I1-I20 aceptado se conservan. D5 global, H07, G01–G07 y GI33/GI34/GI38/GI39/GI40 globales siguen abiertos. Los PASS aislados no demuestran persistencia o recuperación integrada. Sin proveedores/credenciales reales, consumo/reservas, activación, promoción, despliegue ni D6. Sin publicación ni acceso de red.
