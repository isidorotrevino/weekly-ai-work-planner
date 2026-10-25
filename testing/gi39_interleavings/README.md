# I64 — intercalados finitos GI39 / GX90

Implementa el [contrato I63](../../docs/design/D5-I63-GI39-INTERLEAVINGS-DESIGN.md) y su [matriz](../../docs/design/D5-I63-GI39-INTERLEAVINGS-REVIEW.md) mediante APIs públicas T/R y hooks existentes. No cambia producto, Store, fixtures o helpers anteriores.

```sh
python3 -B -m testing.gi39_interleavings.run_gi39_interleavings_lab
```

GX01–GX86 son casos de dominio sobre 22 mutaciones; GX87–GX90 son controles. Dos actores spawn fuerzan MUTATION_FIRST/COMMIT_FIRST mediante before_lock/before_object, o mutan CLIENT mientras una llamada Remote.execute real retiene REMOTE. Se distinguen CONFLICT_HEAD y rechazo semántico con HEAD fresca. El probe observa lock retenido, sin afirmar que el contender ya ejecutó flock bloqueante.

Las mutaciones usan SOURCE/revisiones propias, ABA de perfil/política/observación/adapter T y diez cambios relacionales R. Observación B se registra antes de EVALUATION. R usa siete entidades explícitas, selección TASK0 por recibo BATCH y aristas nuevas sin ciclos. UPDATE usa preparación pública de fuente/base coherentes y entidad remota v2→v3, preservando foreign. No se reconstruye autoridad por escritura directa.

Ocho casos pierden la respuesta después del commit remoto real; UNKNOWN/2/0 STALE sólo pasa a confirmado /3/1 mediante reconcile explícita. Nuevos lectores de archivos y APIs públicas spawn son pasivos, execute=lookup=0. No son nuevas pruebas SIGKILL/H02 ni prueba de recuperación integrada por suma de PASS.

Cada runner histórico se ejecuta por separado con inventario/raw/contexto propios: Python321, HC24, HF40, IC30, UQ24, RV20, NA36, FN64 y CE43. El runner GX incluye sus módulos, reutilizados, contrato/matriz/sello I63 y dependencias, con hashes pre/post. Sus resultados/raw propios quedan fuera de ese inventario para evitar ciclos.

Presupuestos propios: 4 hijos vivos, espera20s, caso120s, campaña900s,256 eventos/caso,16KiB/evento,raw12MiB. Kills de timeout negativos separados; cero raíces/hijos/hilos propios pendientes. Sólo limpieza propia con sentinels. Sin fsync/OSError nuevo, nativo nuevo, red/proveedor/credenciales reales, SQL/Java/Docker/auditor I38, consumo/reservas, activación, promoción, despliegue o D6. D5 global/G01–G07 y criterios globales abiertos. No publica.
