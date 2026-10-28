# I90 — matriz NS01–NS12 propuesta

**12 NOT_RUN**. [Contrato](D5-I90-NULLABLE-SELECTOR-DESIGN.md).
I91 requeriría aprobación: sólo módulos/clases/datos/procesos sintéticos nuevos,
300 s externos. Ningún caso ejecuta el DF08 histórico ni una campaña funcional.

| Caso | Disparador | Oráculo exigido |
|---|---|---|
| NS01 | Prueba sintética nueva con retry_tick=None y selector heredado | Reproducir COMMAND_HEADER_INVALID; preservar I88/I89 y no reconstruir su retorno |
| NS02 | NP01 T, prueba remota exacta y contexto REMOTE EXECUTE/CLOSE compatible | Retener null observado, digest original y metadata_policy_ref; mismo retorno/una llamada |
| NS03 | NP02 R, prueba remota exacta y contexto compatible | Mantener schema/familia R y null; no convertir a T ni aceptar alias por nombre |
| NS04 | Valores int0/int1023/bool/float/string/int1024 | Primeros válidos bajo política; tipos/rango restantes rechazados sin coerción |
| NS05 | retry_tick ausente, None presente o schema/forma desconocidos | Distinguir ausencia/null; no insertar campo ni aprender policy de payload |
| NS06 | None en seq/version/ledger_version u otro entero sin excepción | Rechazar; NP no vuelve nullable todo el catálogo |
| NS07 | Rol CLIENT/Drive, acción/familia/run/store incompatibles o contexto ausente | No activar NP01/NP02 sólo por etiqueta; missing/conflicto cerrado |
| NS08 | Recibo Store original con cid/request/seq/flags | Preservar cabecera y vínculo; metadata nullable no sustituye campos obligatorios |
| NS09 | Resultado remoto de hijo CP07/CP13 sin recibo Store | Null proyectado sólo con política/contexto; receipt/command_id permanecen ausentes, sin UUID5 inferido |
| NS10 | Reader recibe policy_ref forjado, claves extra o contexto cruzado | Rechazar incluso con hashes coherentes; conservar grupos/witnesses y reglas de enlaces I88 |
| NS11 | Error del observer, excepción original, salida parcial, cuotas/restauración | Misma llamada/retorno/excepción; latch y primer diagnóstico, cleanup original; una escritura y límites compartidos intactos |
| NS12 | Final de componente y transición | Como máximo componente validado; I92 funcional, IR03, publicación y aceptación global pendientes de decisiones separadas |
