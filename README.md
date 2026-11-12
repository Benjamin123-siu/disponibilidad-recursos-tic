# Disponibilidad de recursos TIC

Proyecto individual ISI601 - Taller de Diseño de Sistemas.

Objetivo: diseñar y construir una API sencilla para consultar la disponibilidad de recursos tecnológicos de un colegio. La arquitectura planificada contará con API Gateway, balanceador, dos instancias de aplicación y PostgreSQL con base primaria y réplica de lectura.

## Estado

Fase 2 en desarrollo. La base PostgreSQL primaria está operativa.

## Documentación

- [Problemática elegida](docs/fase1/PROBLEMA.md)

- [Evidencias de la Fase 2](docs/fase2/EVIDENCIAS.md)

## Levantar la primaria

En la raíz del clon, crea un archivo local `.env` con una línea `POSTGRES_PASSWORD=tu_clave`. Reemplaza el ejemplo por una contraseña propia antes del primer arranque. Git excluye ese archivo.

Ejecuta `docker compose up -d --wait primaria`. Los datos quedan guardados en el volumen `primaria_datos`.
