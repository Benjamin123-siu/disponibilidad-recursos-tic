# Pruebas de falla — Fase 3 

## Objetivo
Validar el comportamiento de resiliencia, consistencia y recuperación del sistema (`Kong` -> `balanceador` NGINX -> `instancia-1` / `instancia-2` en Flask -> `primaria` / `replica` en PostgreSQL 16) frente a tres escenarios de falla.


## Experimento 1: Detención de una instancia de aplicación (`instancia-2`)

### Procedimiento
1. Detener el contenedor `instancia-2` mediante `docker compose stop instancia-2`.
2. Enviar cuatro peticiones `GET /api/v1/recursos` a través de Kong (`http://127.0.0.1:8000`) con la cabecera `apikey` y revisar `HTTP`, `X-DB` y `X-Instance`.

### Resultado
* El contenedor `disponibilidad-recursos-tic-instancia-2-1` pasó a estado `Stopped`
* Todas las peticiones respondieron `HTTP/1.1 200 OK`, con `X-DB: replica` y `X-Instance: instancia-1`

### Evidencia
![Experimento 1: Detención de instancia-2](Evidencias/Detencion%20Instancia%202%20prueba_TEST1.png) 



## Experimento 2: Corte / bloqueo de replicación y caída de la réplica

### Parte 1 — Lectura desactualizada al bloquear la replicación
1. Consultar el estado inicial de `GET /api/v1/recursos/1` (`Tablet` con `cantidad_disponible: 15`)
2. Bloquear el rol `replicador` (`ALTER ROLE replicador NOLOGIN;`) y terminar la sesión activa de replicación (`SELECT pg_terminate_backend(pid) FROM pg_stat_replication;`) en `primaria`
3. Registrar una entrega de `1` unidad en `POST /api/v1/movimientos`: responde `HTTP/1.1 201 CREATED` (`X-DB: primary`, `X-Instance: instancia-2`), actualizando la primaria a `cantidad_disponible: 14` (`movimiento_id: 4`)
4. Consultar `GET /api/v1/recursos/1`: responde `HTTP/1.1 200 OK` (`X-DB: replica`, `X-Instance: instancia-1`), pero muestra `cantidad_disponible: 15` (lectura desactualizada mientras la réplica no recibe cambios)
5. Rehabilitar el rol `replicador` (`ALTER ROLE replicador LOGIN;`) y volver a consultar `GET /api/v1/recursos/1`: la réplica se sincroniza y devuelve `cantidad_disponible: 14`

### Parte 2 — Caída total de la réplica (`503 Service Unavailable`)
1. Detener `replica` con `docker compose stop replica` y solicitar `GET /api/v1/recursos` vía Kong
2. La aplicación responde `HTTP/1.1 503 SERVICE UNAVAILABLE` con `{"error":"No se pudieron consultar los recursos"}` y `X-Instance: instancia-1`, sin redirigir lecturas a la primaria
3. Al ejecutar `docker compose up -d --wait replica`, la réplica vuelve a quedar `Healthy`

### Evidencias
* Antes del corte: ![Antes de la caída](Evidencias/Comprobacion%20de%20cantidad%20de%20recursos%20antes%20de%20la%20caida_TEST2.png)
* Escritura en primaria sin replicador: ![Movimiento en primaria sin replicador](Evidencias/Movimiento%20registrado%20en%20bd%20primaria%20sin%20replicador_TEST2.png)
* Lectura desactualizada en réplica: ![Consulta a réplica desactualizada](Evidencias/Consulta%20hacia%20bd%20replica_TEST2.png)
* Sincronización tras reactivar replicador: ![Actualización de réplica](Evidencias/actualizacion%20de%20bd%20replica_TEST2.png)
* Respuesta `503` y recuperación de réplica: ![Réplica caída y recuperada](Evidencias/Que%20pasa%20al%20estar%20caida%20la%20r%C3%A9plica%20y%20consultar%20datos_TEST2.png)



## Experimento 3: Caída de `primaria`, promoción de `replica` y medición de RPO / RTO

### Procedimiento y resultados
1. **Estado previo:** antes de matar la primaria, se registraban `total_movimientos: 4` y `ultimo_id: 4`
2. **Falla de `primaria`:** se registró `T_INICIO=$(date +%s)` y se ejecutó `docker compose kill primaria` (`primaria-1 Killed`). Un `POST /api/v1/movimientos` durante la caída devolvió `HTTP/1.1 503 SERVICE UNAVAILABLE` con `{"error":"No se pudo registrar el movimiento"}` (`X-Instance: instancia-2`)
3. **Promoción y reconexión:** se promovió la réplica mediante `SELECT pg_promote();` (`t`) y se recrearon `instancia-1` e `instancia-2` apuntando `DB_PRIMARY_URL` a `replica`
4. **Recuperación:** el `POST /api/v1/movimientos` volvió a responder `201 CREATED` (`cantidad_disponible: 13`, `movimiento_id: 37`) y el `GET /api/v1/recursos/1` respondió `200 OK` (`X-DB: replica`, `X-Instance: instancia-1`, `cantidad_disponible: 13`)
5. **Limpieza:** se eliminó `/tmp/override-failover.yml` y se restauró el entorno limpio con `docker compose down -v && docker compose up -d --wait`

### Medición de RPO y RTO
* **RPO:** **0 movimientos perdidos** respecto al último registro replicado (`ultimo_id: 4` antes de matar la primaria, sin pérdida de datos ya transmitidos por replicación)
* **RTO:** **~111 segundos** (~1 min 51 s entre la falla registrada a las `12:27:27 GMT` y la comprobación de escritura/lectura recuperada a las `12:29:18 GMT`, incluyendo la promoción manual y recreación de las instancias)

### Evidencias
* Estado previo: ![Estado previo](Evidencias/Revision%20ultimo%20movimiento%20antes%20de%20matar%20bd%20primaria_TEST3.png)
* Kill de primaria: ![Kill primaria](Evidencias/Matamos%20bd%20primaria_TEST3.png)
* Error `503` al escribir: ![Sin escritura en primaria](Evidencias/No%20se%20registran%20movimientos%20en%20la%20bd%20primaria_TEST3.png)
* Promoción de réplica: ![Promoción réplica](Evidencias/Se%20promueve%20la%20bd%20replica_TEST3.png)
* Lectura y escritura recuperadas: ![Lectura y escritura recuperadas](Evidencias/Se%20comprueba%20lectura%20y%20escritura%20nuevamente_TEST3.png)
* Restauración del entorno: ![Entorno restaurado](Evidencias/recuperar%20el%20entorno_TEST3.png)