# I67 — trazabilidad de evidencia local

Contrato: [I66](../../docs/design/D5-I66-TRACEABILITY-DESIGN.md), TT01–TT48.

- `python3 -B scripts/trace-d5-evidence.py`: lectura fija; FINDINGS/exit1 es esperado por carencias históricas.
- `python3 -B -m testing.evidence_trace.run_trace_lab`: sólo tests del auditor; no ejecuta campañas de producto.

Registro cerrado: doce entradas I34/I36/I64, targets por grupo, variantes de escenario preservadas. Los pins no se regeneran al usar el programa. No argumentos CLI de raíz, URL, paths o comandos. La API Python de raíz/registro reducidos es para fixtures propios; no crea atestación independiente.

El resultado funcional histórico, sus bytes, la vigencia actual y los huecos de trazabilidad son dimensiones separadas. Contexto padre no es medición independiente por escenario. I34/I36 no adquieren stdout, comando o run_id inventados. No importa ni ejecuta I38 o componentes históricos. Mantiene agregado81/3 y cierre global pendiente.
