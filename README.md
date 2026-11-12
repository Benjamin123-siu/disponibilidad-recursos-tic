# Disponibilidad de recursos TIC

Proyecto individual ISI601 - Taller de Diseño de Sistemas.

Objetivo: diseñar y construir una API sencilla para consultar la disponibilidad de recursos tecnológicos de un colegio. La arquitectura planificada contará con API Gateway, balanceador, dos instancias de aplicación y PostgreSQL con base primaria y réplica de lectura.

## Estado

Fase 2 en desarrollo. La primaria PostgreSQL transmite cambios a una réplica de solo lectura.

## Documentación

- [Problemática elegida](docs/fase1/PROBLEMA.md)

- [Evidencias de la Fase 2](docs/fase2/EVIDENCIAS.md)

## Levantar la primaria

Antes de iniciar Docker Compose, crea un archivo `.env` en la raíz del proyecto. Define `POSTGRES_PASSWORD` y `REPLICATION_PASSWORD` con contraseñas distintas, y `KONG_API_KEY` con una clave hexadecimal aleatoria de 64 caracteres. Escribe cada variable en una línea con el formato `NOMBRE=valor`. Git excluye este archivo.

Ejecuta `docker compose up -d --wait primaria`. Los datos quedan guardados en el volumen `primaria_datos`.

Para iniciar ambas bases, ejecuta `docker compose up -d --wait replica`. El servicio configurar-replicacion prepara el usuario de replicación y termina. En el primer arranque la réplica toma una copia de la primaria. En los siguientes reutiliza su volumen.

### Cambiar la contraseña de una primaria existente

PostgreSQL usa `POSTGRES_PASSWORD` para crear el usuario administrador en el primer arranque. Si la base ya contiene datos, sigue estos pasos desde la raíz del proyecto.

1. Abre una sesión con `docker compose exec primaria psql -U postgres -d recursos_tic`.
2. En el indicador `recursos_tic=#`, ejecuta `\password postgres`. Escribe la nueva contraseña dos veces y sal con `\q`.
3. Abre el archivo local `.env`, actualiza solo `POSTGRES_PASSWORD` con la misma contraseña y guarda el archivo.
4. Comprueba que Compose puede conectarse con el valor guardado:

   ```sh
   docker compose run --rm --no-deps -T --entrypoint psql configurar-replicacion -X -w -h primaria -U postgres -d recursos_tic -c "SELECT current_user;"
   ```

   La consulta debe devolver `postgres`.

## Probar el balanceador interno

Ejecuta `docker compose up -d --wait balanceador`. Desde ese contenedor, `docker compose exec -T balanceador curl -fsSi http://127.0.0.1/health` consulta el balanceador. La cabecera `X-Instance` identifica cuál de los dos servicios de prueba respondió.

## Entrada local mediante Kong

Ejecuta `docker compose up -d --wait`. Kong publica el puerto 8000 en 127.0.0.1. La ruta GET /health requiere la clave en la cabecera apikey. El balanceador y las bases se comunican por la red de Docker.
