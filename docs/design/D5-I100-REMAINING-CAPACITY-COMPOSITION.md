# I100 — composición parcial por raíz y siguiente obligación

Fecha: 2026-10-28. [Tabla de88 raíces con partes separadas](../validation/D5-I100-transitive-error-review.json).
No hay ejecución nueva ni certificado de admisión.

ready/prepare y self.error son partes disjuntas: los helpers de preparación no
llaman self.error, y self.plan R no llama prepare. Sus argumentos y callbacks se
han asignado a cada parte. Se pueden sumar sus cotas sin duplicar esas llamadas:

`E_partes_cubiertas ≤19.218 +1.985 =21.203`.

**No es E_P01_max.** Los eventos de las llamadas directas restantes, aserciones,
contextos, protocolos, factories y lifecycle aún deben añadirse; además faltan
otros grupos de las321 raíces. Se conserva cada parte por método DF/DR para
evitar sumar dos veces un perform interno al expandir un método externo.

El mayor subtotal cubierto por raíz es DR23:24 prepare×66 eventos≤1584; allí
no hay self.error. El límite2048/test es una condición que debe verificarse,
no una cota de demanda que permita dar por pagados los eventos restantes.
2048−1584=464 sólo sería una asignación suficiente al resto si se demuestra
que esa parte tiene cota≤464. No es margen observado ni autoriza una captura.

El siguiente bloque documental es expandir las llamadas directas de DR23:
phase por valor de kind, before/after independent, kill_at, reprocess,
fresh/replay y aserciones/subtests originales. Después se extiende el mismo
cómputo al resto de raíces, conservando rutas de excepción y cardinalidades
de datos. Los hijos mantienen su ámbito: sus métodos internos no son eventos
parentales; start/receive/finish y mensajes parentales sí requieren cuenta.

Quedan abiertos también los owners/objetos fuertes, grupos/contextos/autoridades,
los30 sitios de referencia y bytes de valores/filas/tablas. El máximo de61
witnesses por fila I97 sólo limita un factor. Una cota parcial de eventos no
justifica cuotas de refs o bytes, ni compatibilidad funcional P01.

Hace falta componer321 tests/12 grupos y todas las24 cuotas, revisando el
calendario Reader del contrato/perfil que se proponga. No se cambia el actual.
Implementación/componentes, captura funcional completa, IR03, suficiencia global
y publicación conservan las decisiones separadas correspondientes.

Git y evidencias I83–I99 preservados. Sin repetir I92, providers/credenciales/
corpus reales, consumo/reservas, activación, promoción, despliegue ni D6.
P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial; D1–D4 cerrados e I1–I20/A52
aceptado. D5/H07 y G01–G07, GI33/34/38/39/40 globales abiertos.
