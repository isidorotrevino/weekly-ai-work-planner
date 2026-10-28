# I91 — selectores nullable con contexto cerrado

La decisión A aprueba el diseño I90 e implementa sólo este perfil nuevo y NS01–NS12
sintéticos bajo 300 s externos. Los documentos I90 conservan sus flags históricos.
El registro es `docs/validation/D5-SELECTOR-CAPTURE-REGISTRY.json`.

NP00_STRICT sigue siendo el valor por defecto. NP01_T_REMOTE_PROOF y
NP02_R_REMOTE_PROOF admiten `retry_tick=null` sólo en la prueba pública exacta de
13 claves, familia, identidad REMOTE y operación EXECUTE/CLOSE observadas, o en
resultado remoto CP07/CP13 registrado. El null presente permanece diferente de
la ausencia; ningún otro entero gana nulabilidad. Las proyecciones versionadas
llevan metadata_policy_ref o selector_policy_ref y el lector revalida contexto.

Se heredan los límites, grupos/witnesses I88, quince políticas parentales y
observadores existentes. No hay nuevas llamadas, lecturas de dominio, procesos o
canales auxiliares. El resultado remoto del hijo no contiene recibo Store:
command_id/receipt permanecen ausentes y CHILD_LOCAL_NOT_OBSERVED. No se infiere
UUID5 ni se reemplazan cabeceras obligatorias.

NS12 usa clases y datos sintéticos nuevos, recorder/reader completos T y R y
rechazos de contexto, esquema, tipo, rango y manipulación. Sólo reutiliza helpers
puros; no importa ni reejecuta suites/producto/runners históricos. El reader
documental de preservación tiene ámbito propio acumulado y no representa todas
las lecturas OS/stdlib ni una prueba de capacidad runtime.

I92 P01 completo321/12 necesita autorización posterior, pins/destino nuevos y
límite externo900s, sin reintentos automáticos ni publicación. Este componente no
crea autoridad, destino o launcher de I92. Ante incompatibilidad se conserva y
presenta antes de ampliar o repetir. IR03 y publicación requieren decisiones
separadas. PASS sintéticos no demuestran persistencia/recuperación integrada,
fsync nativo, UI04.1 ni cierre D5.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL (UI04.1). D1–D4 cerrados e hito local I1–I20
aceptado; D5/H07/G01–G07/GI globales OPEN. Sin proveedores/credenciales/corpus
reales, consumo/reservas, activación, promoción, despliegue o D6.
