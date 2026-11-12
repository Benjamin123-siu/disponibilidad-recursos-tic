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
