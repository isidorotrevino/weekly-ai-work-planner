# I134 — revisión documental de P01 RESOURCE-SCOPE

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`096935f4d3087ab62c9d8f6de0217810c7dc7cba`.

**P01 es conforme al ámbito fuente declarado, sin defectos documentales
bloqueantes encontrados.** La revisión no acredita independencia de actor: este
mismo asistente preparó I133. Se realiza una recomputación separada desde Git,
pero no se fabrica una aprobación de un tercero, firma de operador o aceptación
independiente. La no admisión de I122/PJC115-R2 se mantiene y E01–E05 no cierran.
P01, la candidata 03 y el plan I132 conservan sus bytes.

[Revisión de P01](../validation/D5-I134-P01-documentary-review.json) ·
[Reconstrucción de fuentes](../validation/D5-I134-P01-source-reconstruction.json) ·
[P01 revisado](../validation/D5-PFC126-03-RESOURCE-SCOPE.json) ·
[Auditoría](../validation/D5-I134-audit.py) ·
[Integridad](../validation/D5-I134-integrity.json).

## Método y resultado

No se toma PASS del auditor I133 como una aprobación independiente. Se leen los
blobs Git del commit de preparación declarado en P01 (`9268d2f…`) y se comprueba
que sus 120 input pins existen y coinciden, por SHA256, con P01 y con el working
tree. Se comprueba también el blob de P01 publicado en I133 (`096935f…`). Git se
usa para leer metadata/objetos, nunca para ejecutar esos blobs o cambiar fuentes.

Desde esas fuentes históricas se materializa el registro JSON, se reconstruye
el conjunto estático de imports locales del observador y se indexan los símbolos
léxicos de las definiciones. No se importan módulos, construyen factories o
instancias de test, ni se ejecuta discovery, runner, producto o componentes.

| Comprobación | Resultado |
| --- | --- |
| S01 schema/identidad | Ruta/schema P01 y ocho campos específicos del plan correctos; candidata/hash vinculados |
| S02 bytes/commit | 120 pins coinciden con Git de preparación y working tree; P01 publicado coincide |
| S03 fuentes originales | 79 inputs registrados, 71 Python; 33 registros de import/32 fuentes únicas preservados |
| S04 raíces/bindings | 321 IDs, 12 grupos y 321 símbolos léxicos/intervalos AST/factory_args coinciden |
| S05 separación de fuentes | 8 imports locales del observador; 3 archivos runtime, 2 componentes NOT_RUN y README diferenciados |
| S06 runtime/plataforma | Referencia no atestada, pendiente P02/P03, sin garantía añadida |
| S07 procesos/métricas | Heap worker y otros procesos/stack/RSS separados; tiempo incluye contribuciones pertinentes |
| S08 tiempo/éxito | tW exacto True y calificación posterior conservados, sin timestamp o garantía nueva |
| S09 presupuestos/políticas | 11/12 GiB, reservas 832 MiB/30 s y 24 cuotas intactos; transferencias 0 |
| S10 aplicabilidad/fallos | Precondiciones fuente I115/I124 y rechazo acotado explícitos; no runtime PASS nuevo |
| S11 proveniencia | Productor identificado; aceptación de actor independiente sigue pendiente |
| S12 no admisión/efectos | Otros 19 paquetes sin output, E06 NOT_RUN, certificado/autoridad/inputs intactos |

S01–S10/S12 son conformidad documental del ámbito. S11 conserva una limitación
expresa, no oculta ni resuelta atribuyéndose otra identidad. El resultado es una
revisión técnica concluida y favorable para el ámbito declarado, **no** cierre
de la condición de aceptación independiente del plan ni de recursos.

## Qué prueba el contraste de bindings

Los 321 bindings se reconstruyen sobre 12 archivos fuente del árbol de preparación.
Se comprueba el símbolo léxico declarado además del intervalo y hash AST, y se
conservan los factory_args particulares de cada ID. El resumen registra el hash
de la secuencia reconstruida y los conteos por archivo, sin fusionar raíces que
comparten una definición/factory. Se reconcilia el hash de IDs ordenados y el
reparto completo de grupos.

Esto confirma la expectativa de fuente, no que un loader/runtime la haya
seleccionado al ejecutar. Tampoco transforma el inventario causal 118 en toda
la campaña 321. Los modos 88 T/R, 30 Drive y 203 sólo aserciones/contextos permanecen
separados. Los imports locales son un superconjunto AST; no reemplazan el cierre
real loaded/frozen/builtin/extensiones, que corresponde a P02.

## Métricas y límites correctamente delimitados

P01 incluye originales opacos, observador y runtime en el heap dinámico del
worker. Coordinador/hijos tienen cuentas separadas y no se declaran cubiertos
por sus 11/12 GiB. Las contribuciones temporales relevantes de esos procesos sí
permanecen dentro del ámbito extremo a extremo y los grupos C01–C10.

Solicitado, comprometido de allocator y stack/RSS no se identifican entre sí.
La correspondencia del backend exacto aún tiene que probarse en P02/H11;
P01 no la da por conocida. Las cotas completas/capacidad disponible permanecen
null. Los presupuestos y reservas candidatos no se llaman demanda, memoria
libre o servicio disponible. Los originales no desaparecen por ser opacos.

Se mantienen los marcadores del coordinador y la ruta de éxito cualificada:

```
t0 <= tR <= tW <= tF
Tpre=tR-t0; Tworker=tW-tR; Tpost=tF-tW
```

tW es el retorno exacto True de la llamada única wait_worker; validaciones
posteriores no lo mueven. False/excepción o un fallo de salida/paquete/finally
no establecen la afirmación de éxito. No se promete <=900 para cualquier cleanup
fallido. P01 conserva la necesidad de cubrir trabajo antes de tR y finalización
hasta tF; la definición no constituye una cota numérica ni atesta el reloj.

## Disposición de la revisión

No se requiere cambiar P01 para que represente su ámbito fuente declarado.
La aceptación independiente no se registra como obtenida: la revisión actual
explicita mismo asistente/recomputación separada y no inventa un revisor humano,
otro agente o autoridad operadora. Los campos históricos de I133 quedan intactos;
I134 registra su juicio y límites en documentos separados.

P02/P03 y los demás paquetes no se inician ni se producen. E01–E05 permanecen
abiertas, E06 continúa separado, pendiente y NOT_RUN. No se emite
SOURCE_CAPACITY_VERIFIED ni se actualizan autoridad/destino, capture_inputs,
cuotas, reservas o certificado IMPLEMENTED_NOT_ADMITTED. Git no convierte esta
revisión en admisión operativa o permiso de ejecución.

## Verificación y publicación

`python3 docs/validation/D5-I134-audit.py` recompone los datos desde blobs Git,
verifica hashes/AST/símbolos, registro/grupos, métricas, marcadores y no admisión.
No ejecuta el auditor histórico para hacerle pasar supuestos de snapshot que ya
no corresponden al working tree actual. Sus archivos/sellos permanecen íntegros.
PASS_STATIC_SOURCE_ONLY significa consistencia del contraste y del dictamen,
no prueba de runtime, independencia de actor o recursos.

Se conservan 148 archivos previamente publicados. El auditor funciona antes de
stage y después del commit. Se hace commit y push de todos los cambios I134,
verificando el resultado real en Git sin self hashes. Sólo se usan helpers
estándar y Git; no se ejecutan producto/componentes o escenarios, ni se prueban
latencias, memoria o scheduling.

P0 conserva 83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1); D1–D4 e I1–I20/A52 aceptados.
D5/H07 y brechas/obligaciones reales pendientes; IR03 NOT_READY. I86/I89/I92
INVALID_CAPTURE sin reanudación/mezcla. Sin proveedores/credenciales, consumo,
reservas operativas, activación, promoción, despliegue o D6. No se inspecciona ni
limpia dev/run_data/D4.
