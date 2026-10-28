# I98 — matriz de llamadas y composición pendiente

Fecha: 2026-10-28. [Matriz con anclas y condiciones](../validation/D5-I98-parental-helper-costs.json).
Las fórmulas siguientes describen retorno exitoso de fuente original en frame
T/R causal activo, objetos ya creados y sin hooks/callbacks que añadan trabajo.
No son un certificado de todas las rutas de P01 ni nuevas observaciones runtime.

P=Client.perform, U=Store.transact, S=retornos snapshot observados (incluidos
los snapshots de Store), D=advance Drive. En este alcance **E=P+U+S+D**.
El causal de Client.perform se publica dentro de CALL_RETURN mediante
publish=False: sumar otro CAUSAL_TERMINAL duplicaría el coste. Store.transact
sí publica su terminal propio. Las aserciones, resultados y lifecycle se suman
fuera de esta matriz.

| Método/rama | P | U | S | D | Eventos |
|---|---:|---:|---:|---:|---:|
| Client.perform |1|1|2|0|4|
| Client.prepare_projection |1|1|6|0|8|
| Client.dispatch deliver=False |1|1|4|0|6|
| Client.dispatch deliver=True |2|3|8|0|13|
| Client.reconcile close=False |2|2|8|0|12|
| Client.reconcile close=True |2|3|6|0|11|
| Remote.execute |0|1|0|0|1|
| Remote.lookup |0|0|2|0|2|
| Remote.edit |0|1|2|0|3|
| Client.summary |0|0|4|0|4|
| durable_support.capture |0|0|1|1|2|

La facade Remote R hereda execute/lookup/edit de la facade T, manteniendo
reductor/schema R. No se convierte un resultado Remote en un recibo Store ni
se reconstruye cid desde esta cuenta. Los bucles sends de prepare_projection
y summary no llaman estos boundaries dentro de su iteración: su coste de
bytes/CPU sigue pendiente aunque el número de retornos snapshot sea fijo.

Para reconcile con proof_hook hay que sumar el vector del callback realmente
enlazado; no se le asigna0 por defecto. Los hooks de Store y las excepciones
originales exigen ramas propias. Un fallo previo al retorno puede cambiar
eventos, metadatos o missing: no hereda automáticamente el contrato de éxito.
El código dentro del hijo no se añade al padre; los eventos de protocolo
parental sí deben contarse por su fuente y acción.

## Objetos creados por factories y fresh

Una invocación exitosa de new_lab/fresh T crea2 Store,1 Client,1 Remote y1
FixtureStore. La R crea2 Store,1 Client y1 Remote. Son conteos de esas clases,
no de todos los objetos Python, ni de referencias/grupos. ready/prepare usan
los objetos del lab; no crean otro Store dentro de sus cuerpos.

Falta contar las invocaciones externas de lab/fresh/constructores directos y
sus contextos. Varias instancias físicas del mismo Store lógico deben conservar
todos los witnesses; el límite61 por fila I97 no permite fusionarlas. Un cambio
de subcase/thread puede crear otro grupo aunque comparta identidad lógica.

## Obligaciones que todavía impiden una cuota global

- Expandir por raíz las llamadas directas a perform/transact, dispatch/reconcile,
  snapshots y self.error(fn), con las rutas de excepción originales.
- Resolver lab.fresh(), constructores, oráculos independent/state/entities,
  callbacks, aserciones/subtests y lifecycle; contar protocolos parentales e hijos.
- Componer owners, objetos fuertes, contextos, grupos, autoridades y los30 sitios
  de cargo activos.30.146 sólo limita el subconjunto especificado de los helpers.
- Acotar bytes de filas/tablas/valores y eventos por test/campaña de321/12.
  E_helper≤19.218 no prueba E_P01≤131072 ni2048 por test.

Los Reader I96 siguen condicionados a su calendario pinneado. Hace falta revisar
su cuenta al proponer otro contrato/perfil. Ninguna cuota cambia ahora. Después
de una propuesta completa se necesitarán decisiones de implementación/componentes,
captura funcional, IR03, suficiencia global y publicación según su alcance.

Se preservan I83–I97 y todos los cambios previos. No se ejecuta otra campaña,
no se repite I92 y no se infiere compatibilidad P01 desde I95/CB32. D5/H07 y
G01–G07 siguen abiertos; P0,83/1, UI04.1 parcial, D1–D4 e I1–I20/A52 conservados.
Sin operaciones reales ni D6.
