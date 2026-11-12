# I132 — plan concreto de evidencia E01–E05 para PFC126-CANDIDATE-03

Fecha: 2026-11-12, Europe/Madrid. Base publicada:
`fa91f107c56535b850ee3d86e16882756924e5eb`.

**Se prepara un plan de20 paquetes y20 entregables futuros; no se produce ni se
da por válida su evidencia.** El plan mantiene fija la candidata03/I122, los
presupuestos y las cuotas, sin asignar reservas ni ejecutar producto/componentes.
La ruta propuesta combina pruebas estáticas completas y documentación atestada
preexistente del runtime/plataforma, o un WCET estático sustentado. Si ese soporte
no existe, el resultado correcto seguirá siendo no admisión.

[Plan con paquetes, campos y dependencias](../validation/D5-I132-E01-E05-evidence-plan.json) ·
[Checklist de cierre](../validation/D5-I132-closure-checklist.json) ·
[Auditoría](../validation/D5-I132-audit.py) ·
[Integridad](../validation/D5-I132-integrity.json).

## Orden de trabajo y entregables

Los nombres siguientes son destinos futuros bajo docs/validation, no archivos
creados ni fixtures PASS. Cada paquete del JSON fija responsable por función,
revisor independiente, inputs, método, campos obligatorios, aceptación y rechazo.
Las personas aún no están asignadas; no se ha contactado a terceros o reservado
capacidad. Un rol designado en el plan no sustituye la atestación correspondiente.

| Orden | Paquete | Entregable futuro, prefijo D5-PFC126-03- |
| --- | --- | --- |
| S0 | P01 | RESOURCE-SCOPE.json:fuentes, métricas, procesos y marcadores exactos |
| S1 | P02 | E01-RUNTIME-IDENTITY.json:cierre/proveniencia runtime y correspondencia |
| S1, tras P02 | P03 | E04-PLATFORM-ENVELOPE.json:capacidad y servicio/latencias atestados |
| S2 | P04-H01…H11 | Once E02-Hxx.json, una prueba completa por propietario |
| S2 | P06 | E03-WORK-GROUPS.json:trabajo/WCET de los diez grupos y procesos |
| S3 | P05 | E02-HEAP-ROLLUP.json:suma/fit y capacidad, tras las once pruebas |
| S3 | P07 | E03-E04-COMPATIBILITY.json:trabajo/servicio/unidades/latencias compatibles |
| S4 | P08 | E05-PHASE-BOUNDS.json:teorema de éxito cualificado extremo a extremo |
| S5 | P09 | RESOURCE-BUNDLE-BINDING-REVIEW.json:proveniencia/pins e impacto de rebind |
| S5, tras P09 | P10 | E01-E05-CLOSURE-REVIEW.json:dictamen independiente por obligación |

P02 y P03 se priorizan antes de prometer cierre de cálculos costosos. P03 debe
aportar garantías que no dependan de afirmar de antemano el tiempo del programa;
P07 comprueba después que el trabajo real cumple sus supuestos de carga,
interferencia y proceso. No hay un ciclo «el programa termina porque el proveedor
lo garantiza si el programa ya termina».

Cada artefacto futuro necesita schema y tipo de evidencia, hashes reales del
contrato/fuentes/runtime/plataforma, productor/revisor identificables y validez,
ámbito/métrica/unidades/supuestos y una derivación completa. Una cota numérica
ha de estar derivada, no copiada del presupuesto. No se aceptan plantillas con
firmas, timestamps, valores o hashes ilustrativos como pruebas reales.

## Primer punto de decisión: evidencia externa

P02 corresponde al custodio de imagen/build/runtime. Debe aportar un cierre
completo de implementación realmente seleccionada —incluidos frozen/builtin,
extensiones, dependencias nativas, libc/allocator y kernel/configuración— y
correspondencia fuente/binario justificable. Se pueden revisar documentos de
release/build firmados existentes; el plan no ordena construir o ejecutar un
runtime para rellenarlos. El manifiesto histórico I127 es sólo un input parcial.

P03 corresponde a una autoridad capaz de sostener capacidad y servicio del
entorno declarado. Necesita disponibilidad de heap solicitado/comprometido,
identidad y validez del dominio de procesos/clock, CPU/WCET y cotas de scheduling,
locks, IO, finalización de hijos y observación. Debe explicitar interferencias,
señales/reintentos y límites de carga que hagan finitas esas garantías.

**Si no hay material suficiente en P02/P03, se registra el bloqueo de evidencia
y E01/E04/E05 afectadas siguen abiertas.** No se infiere rate de W/budget, no se
sustituye servicio por frecuencia o número de cores y no se ejecutan benchmarks.
No se inventa una garantía por disponer de un watchdog o una cuota ordinaria.
El plan no garantiza que un operador pueda proporcionar esas pruebas.

## E02:once pruebas, sin reducir heap a bytes serializados

P04-H01…H11 se preparan por análisis estático sobre el runtime fijado en P02;
P05 integra sus resultados con la capacidad de P03. Sus objetivos son los
presupuestos actuales, no límites nuevos aplicados:

| Propietario | MiB candidatos | Contenido indispensable de su prueba |
| --- | ---: | --- |
| H01 runtime/imports | 256 | Asignaciones iniciales/vivas Python y nativas |
| H02 originales | 2048 | Estado privado completo y retención, incluidos objetos opacos |
| H03 observer persistente | 512 | Raíces fuera de FIELDS, callbacks/parches, locks y hojas |
| H04 clones/memo | 6144 | Tamaños ABI y vidas/reachability, retornos escapados, IO, rechazos/tracebacks |
| H05 marcos/generadores | 128 | Allocaciones dinámicas y multiplicidad, separadas del stack/RSS |
| H06 proyección/digest | 256 | sorted, registros/fila nueva y todos los temporales |
| H07 codecs/árboles | 256 | Unicode/bytes, fragmentos, parse y coexistencia de raíces |
| H08 Reader | 512 | Payload, headers/mapas/listados y PhaseBytes completos |
| H09 páginas | 192 | Cuerpos/chunks, memo histórico, listas y concat/encode |
| H10 raw/StringIO | 128 | Capacidad/snapshots/copias y árboles coexistentes |
| H11 allocator | 1024 | Overhead de arenas/retención/fragmentación en métrica declarada |

H04 necesita un argumento de vidas/asignaciones suficientemente preciso; el
antiguo mayorante acumulado de23PB no prueba ajuste a6GiB. No se reemplaza por33
generaciones ni GC inmediato sin demostrarlo. No se cambia I122 para acomodar
la prueba dentro de este plan. Los subbounds de payload H08/H09/H10 tampoco
cierran sus propietarios completos.

P05 exige que cada upper completo quepa en su partida, suma solicitada más
reserva832MiB<=11GiB, H11<=1GiB y comprometido<=12GiB, con capacidad atestada.
Se permite sobrecontar, no omitir o fusionar witnesses. No se asigna reserva:
x_i,y_i,z_i continúan0. Si una prueba completa no cabe o no puede obtenerse,
se emite dictamen negativo/insuficiente, sin ampliar presupuesto,900 o cuotas.
Cualquier cambio de fuente/contrato necesitaría otro alcance explícito.

## E03/E04:prueba de trabajo y compatibilidad, no multiplicación de cuotas

P06 cubre C01–C10 por proceso y ventana. Incluye trabajo del worker antes de
READY y el que pueda avanzar tras leer RELEASE antes del cierre tR del padre;
puede partirlo por intervalo o sobrecontarlo justificadamente. Incluye originales,
metadata, noncopy/nativo, JSON/hash/sort/GC/destrucción, IO y el finally completo
hasta tF. La lista de campos obliga a no convertir en0 los30 upper ausentes.

P07 une ese trabajo con el servicio o WCET de P03. Debe comprobar misma
plataforma/runtime/procesos, unidades compatibles y supuestos de carga; además,
atribuir correctamente cada latencia. CPU acumulada y tiempo wall pueden
diferir; no se restan solapamientos sin prueba. Una latencia ya incluida puede
sobrecontarse conservadoramente, pero no omitirse o usarse como dos créditos de
presupuesto. El600CPU/90IO-hijos/60scheduling debe tener cobertura completa y
fit sustentado dentro de750, además de cotas completas de Tpre/Tpost.

Si el servicio no admite las unidades del trabajo o el entorno no limita
esperas/reintentos, P07 no cierra E03/E04. No se mide producto o componentes para
resolver ese bloqueo dentro de este plan.

## E05:teorema estático sobre marcadores cualificados

P08 consume P05/P06/P07 y las identidades/reloj de P02/P03. Prueba la ruta de
éxito definida en I128, sin inventar timestamps ni instalar instrumentación:

```
t0 <= tR <= tW <= tF
Tpre=tR-t0<=60; Tworker=tW-tR<=750; Tpost=tF-tW<=60
60+750+60+30=900, con reserva contada una sola vez
```

tW es el retorno exacto True de wait_worker; validaciones posteriores califican
el éxito sin moverlo. False/excepción, salida/paquete inválidos o finally fallido
no producen la afirmación de éxito. El plan no promete<=900 para todo cleanup de
fallo, ni omite por ello el heap de los prefixes de rechazo aplicables. Una
partición correcta, un raw elapsed o process.wait900 no sustituyen cotas de fase.

## Packaging y dictamen independiente

P09 comprueba los artefactos reales, su autoridad/validez y todos sus hashes y
schemas, sin ciclos de self pin. Las referencias externas de binarios/atestaciones
no se copian al Reader ni se llaman lecturas frescas por omisión. Si se proponen
como inputs de una admisión futura, se debe definir el grafo exacto, calcular
bytes reales por Reader y verificar todos los límites individuales/acumulados
sin reset, descuento ni cambio de cuotas. No se presupone3*N si cambia el grafo.
P09 sólo evalúa compatibilidad: no ejecuta rebind, autoridad o worker.

P10 reevalúa los20 criterios I131 y clasifica cada obligación con sus artefactos
y supuestos completos. La checklist vincula cada E01–E05 a paquetes y criterios;
no permite cerrar por la existencia de este plan o por aprobar coherencia
aritmética. Un dictamen honesto de evidencia insuficiente es un endpoint válido.

Incluso si en el futuro E01–E05 se verificasen, **E06/componentes/CP07 y la
admisión operativa seguirían separados**. P10 no concede permiso de ejecución,
no fabrica PASS de componentes y no sustituye la autoridad/certificado real.
En I132 ninguna obligación se cierra; todos los20 entregables siguen sin crear.

## Verificación y publicación I132

Sólo se crean el plan, checklist, documento, auditor y sello I132. La auditoría
comprueba DAG/orden,20 destinos futuros únicos que no existen, once tareas de
heap, cobertura de los20 criterios, aceptación/rechazo, pins y no admisión.
Conserva138 archivos previamente publicados y funciona antes/después del commit.
PASS_STATIC_SOURCE_ONLY no es una prueba de recursos; no se importa ni ejecuta
producto/componentes o escenarios. Se hace commit y push de todos los cambios
I132 autorizados; el resultado real se verifica en Git, sin hashes circulares.

Candidata03, código, cuotas, reservas, certificado IMPLEMENTED_NOT_ADMITTED,
capture_inputs y autoridad/destino permanecen intactos. PJC115-R2 no habilitada;
D5/H07 abiertos e IR03 NOT_READY. P0 conserva83 SUPPORTS_BOUNDED/1 PARTIAL
(UI04.1); D1–D4 e I1–I20/A52 aceptados. Brechas y obligaciones reales pendientes;
I86/I89/I92 INVALID_CAPTURE sin reanudar/mezclar. Sin proveedores/credenciales,
consumo/reservas operativas, activación, promoción, despliegue o D6. No se
inspecciona ni limpia dev/run_data/D4.
