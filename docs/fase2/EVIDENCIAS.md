# Evidencias de Fase 2

## Primaria PostgreSQL · 12 de noviembre de 2026

Desde la raíz del repositorio:

```sh
docker compose up -d --wait primaria
docker compose exec -T primaria psql -X -U postgres -d recursos_tic -c "SELECT current_database(), current_setting('server_version') AS version, pg_is_in_recovery() AS en_recuperacion;"
```

Compose creó el volumen primaria_datos y la red del proyecto. El contenedor primaria-1 alcanzó el estado Healthy. La consulta devolvió:

| Base | Versión | En recuperación |
| --- | --- | --- |
| recursos_tic | 16.15 (Debian 16.15-1.pgdg13+2) | f |

El valor f indica que el servidor está fuera de recuperación, como corresponde a la primaria.

## Réplica streaming · 12 de noviembre de 2026

Desde la raíz del repositorio:

```sh
docker compose up -d --wait replica
docker compose exec -T primaria psql -U postgres -d recursos_tic -c "SELECT application_name, state FROM pg_stat_replication;"
docker compose exec -T replica psql -U postgres -d recursos_tic -c "SELECT pg_is_in_recovery() AS es_replica, current_setting('transaction_read_only') AS solo_lectura;"
```

| Comprobación | Resultado observado |
| --- | --- |
| Conexiones antes de levantar la réplica | 0 filas |
| Conexiones después | replica / streaming |
| Recuperación y solo lectura en la réplica | t / on |

## Distribución de solicitudes con NGINX · 12 de noviembre de 2026

Desde la raíz del repositorio, levantar el balanceador y sus dos servicios de prueba. En CMD, ejecutar cuatro consultas consecutivas:

```cmd
docker compose up -d --wait balanceador
for /L %i in (1,1,4) do @docker compose exec -T balanceador curl -fsSi http://127.0.0.1/health
```

| Solicitud | Respuesta HTTP | Cabecera X-Instance |
| --- | --- | --- |
| 1 | 200 OK | instancia-1 |
| 2 | 200 OK | instancia-2 |
| 3 | 200 OK | instancia-1 |
| 4 | 200 OK | instancia-2 |

Las cuatro solicitudes entraron por el mismo balanceador. Cada instancia agregó su nombre a la respuesta. El orden inicial puede variar al repetir la prueba.

## Kong como única entrada · 12 de noviembre de 2026

Pruebas desde Windows contra http://127.0.0.1:8000:

| Método y ruta | Cabecera apikey | Resultado observado |
| --- | --- | --- |
| GET /health | Ausente | 401 |
| GET /health | Incorrecta | 401 |
| GET /health (dos solicitudes) | Válida | 200 en ambas, X-Instance alternó entre instancia-1 e instancia-2 |
| GET /otra | Válida | 404 |

Repetir desde PowerShell en la raíz del repo:

```powershell
$clave = ((Get-Content .env | Where-Object { $_ -like 'KONG_API_KEY=*' }) -split '=',2)[1]
curl.exe -i http://127.0.0.1:8000/health
curl.exe -i -H "apikey: incorrecta" http://127.0.0.1:8000/health
1..2 | ForEach-Object { curl.exe -i -H "apikey: $clave" http://127.0.0.1:8000/health }
curl.exe -i -H "apikey: $clave" http://127.0.0.1:8000/otra
docker compose ps
```

En la lista de puertos, solo Kong mostró un puerto publicado en Windows: 127.0.0.1:8000. La API administrativa de Kong está deshabilitada.
