# I99 — callbacks revisados y composición restante

Fecha: 2026-10-28. [Definiciones, bindings y hashes](../validation/D5-I99-parental-error-review.json).
Revisión AST/lectura stdlib; cero ejecución de callbacks/producto/tests/campañas.

## Ocho callbacks parentales con coste de boundaries resuelto

Se localizaron los8 bindings explícitos hook/client_hook/remote_hook/proof_hook
de las dos suites:6 hooks de OSError controlado y2 mutadores de proof.

| Familia y método | Callback | Efecto original |
|---|---|---|
| T DF11 | fault; recovery_fault | OSError en directory_fsync o recovery_fsync |
| T DF19 | fault | OSError en directory_fsync |
| T DF26 | bad | Mutar un campo del proof y retornar el mismo dict |
| R DR24 | fault; recovery | OSError en directory_fsync o recovery_fsync |
| R DR27 | fault | OSError en directory_fsync |
| R DR29 | bad | Mutar un campo del proof y retornar el mismo dict |

Sus cuerpos sólo realizan comparación, dict mutation/retorno, uid/endswith o
crean/lanzan OSError. uid está enlazado a la función pinneada de soporte, que
usa UUID stdlib. **Añaden0 invocaciones a los boundaries observados y0 eventos
de aserción por invocación.** Esto no significa trabajo0: pueden cambiar datos,
resultados y la ruta de excepción del caller. Tampoco autoriza ese valor para
callbacks futuros/desconocidos. La multiplicidad de llamadas al hook y el coste
de CPU/valores siguen perteneciendo a sus rutas originales.

La etiqueta directory_fsync/recovery_fsync del punto de fuente no prueba fsync
nativo ni recuperación integrada. Se conservan la excepción/estado que realmente
produzca cada ejecución; no hay una ejecución nueva en esta revisión.

## Argumentos y receptores de self.error

El censo incluye hasta45 invocaciones fresh escritas dentro de fn, antes
de entrar en error; a2 Store construidos/eventos de construcción por fresh,
su contribución local es≤90 eventos. Es una sobreestimación por ramas
y bucles del censo. No incluye c=lab.fresh escrito en otra sentencia ni otros
constructores/cleanup. Las expresiones restantes también se evalúan antes:
state/independent, funciones de encoding o builders no se vuelven gratuitas.

Los92 fn están registrados con expresión, patrón y multiplicidad superior.
Su presencia en un inventario no demuestra cobertura runtime. Para cerrar su
coste transitivo hay que distinguir métodos Client/Remote/Store, self.plan,
reductores/planners puros y facades históricas por fuente y binding, conservando
las rutas rechazadas. No aplicar la matriz de éxito a todo fn por su nombre.

## Lo que falta para una propuesta ejecutable

- Completar el censo de métodos directos y fn, con tipos/bindings y cardinalidades
  de datos; expandir factories/fresh, oráculos y protocolos parentales.
- Incorporar aserciones/subtests y lifecycle de los321 tests/12 grupos, incluidos
  contextos esperados que no pasan por self.error.
- Componer los30 sitios de cargo, grupos/objetos/witnesses y bytes de tablas,
  filas y valores. R≥19.037 prueba insuficiencia del techo actual; aún falta R_max.
- Revisar conjuntamente las24 cuotas y el calendario Reader del perfil que se
  proponga. No crear una cifra suficiente por sumar cotas de subconjuntos.

El siguiente paso documental es resolver por fuente los fn y las llamadas
directas restantes. Después, una implementación/componentes y una captura P01
completa necesitarán las decisiones correspondientes; IR03, suficiencia global
y publicación siguen separados. No se repite I92 ni se cambia el perfil actual.

P0,83/1 y UI04.1 parcial conservados. D1–D4 e I1–I20/A52 intactos. D5/H07 y
G01–G07, GI33/34/38/39/40 globales abiertos. Sin proveedores/credenciales/corpus
reales, consumo/reservas, activación, promoción, despliegue ni D6.
