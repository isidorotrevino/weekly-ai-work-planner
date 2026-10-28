# I87 — matriz propuesta DW01–DW24

Todos **NOT_RUN**. [Contrato](D5-I87-DOMAIN-WITNESS-DESIGN.md).
I88 propuesto: sólo componentes nuevos sintéticos, 300 s externos. Sin P01,
DF03 histórico, CT96/PR96 u otras suites antiguas. Los casos documentales verifican
historia; los casos de comportamiento usan llamadas reales de clases sintéticas.

| Caso | Disparador | Resultado exigido |
|---|---|---|
| DW01 | Lectura de I85/I86 y sus pins | Componentes PASS e intento inválido conservados; sin nueva autoridad funcional |
| DW02 | Intento de reutilizar autoridad/destino I86 | Rechazar antes de imports o escrituras funcionales |
| DW03 | Un solo Store sintético | Resolver identidad con witness único y object_ref original |
| DW04 | Sin witness compatible | Missing explícito; no fabricar grupo desde source/head solo |
| DW05 | Dos Store sintéticos reabiertos con mismo run/store/role | Reproducir rechazo del selector heredado por duplicidad y comprobar grupo nuevo con ambos witnesses |
| DW06 | Store y fachada con la misma identidad observada | Conservar objetos/autoridades separados; no doble crédito de oráculo |
| DW07 | Igual store_id, run distinto | Grupos separados y enlace cruzado rechazado |
| DW08 | Igual run/store, roles distintos | Grupos separados; no elegir ni homogeneizar roles |
| DW09 | Cambio de frame/subcaso/hilo | Sin herencia de witnesses; enlace incompatible bloqueado |
| DW10 | Identidad mutada en el mismo objeto | Conflicto latcheado, sin rebind |
| DW11 | Construcción sin snapshot/recibo | NOT_HEAD; no cabeza/estado u oráculo independiente inferidos |
| DW12 | Independent sintético retorna oráculo exacto | Una llamada, mismo retorno, resumen/digest/grupo ligados al contexto |
| DW13 | Comando/recibo/oráculo compatibles | Enlace sólo por campos observados y grupo/witnesses acreditados |
| DW14 | Recibo incompatible aunque grupo coincida | Conflicto/missing; grupo no sustituye command/request/seq/head |
| DW15 | Varios witnesses equivalentes y exigencia de objeto único | Conservar conjunto; unicidad requerida permanece sin resolver |
| DW16 | after_data/state y hashes Store/Drive/I70 | Dominios separados, sin igualdad ficticia o recomputación de cid |
| DW17 | Witness/grupo huérfano, duplicado o ciclo | Lector rechaza recorriendo refs locales acotadas |
| DW18 | Grupo no acreditado por declaraciones/cabeceras | Rechazar incluso con etiqueta/hash coherente |
| DW19 | Conjunto supera refs/fila/sidecar | Bloquear sin truncar, muestrear o resetear contadores |
| DW20 | Topes heredados y Reader antes/después/autoridad | Límites exactos acumulados; incompatibilidad conserva fallo |
| DW21 | Retorno/excepción original y error del observer | Una llamada, misma instancia, latch, cleanup y parada entre tests |
| DW22 | Instalación/restauración y canales | Punteros propios restaurados; ningún actor/IO/medición extra de dominio |
| DW23 | Políticas parentales y cadena DI07 en componentes nuevos | Conservar recibos/ausencias/autoridades; sin promover PR96 a P01 |
| DW24 | Transición tras DW24 | Como máximo componente validado; I89/IR03/publicación/aceptación global siguen separados |
