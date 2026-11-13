# Disponibilidad de recursos TIC

Proyecto individual ISI601 - Taller de Diseño de Sistemas.

Objetivo: diseñar y construir una API sencilla para consultar la disponibilidad de recursos tecnológicos de un colegio. La arquitectura planificada contará con API Gateway, balanceador, dos instancias de aplicación y PostgreSQL con base primaria y réplica de lectura.

## Estado

Fase 2 en desarrollo. La primaria PostgreSQL transmite cambios a una réplica de solo lectura.

## Documentación

- [Problemática elegida](docs/fase1/PROBLEMA.md)

- [Evidencias de la Fase 2](docs/fase2/EVIDENCIAS.md)

## Configuración inicial (solo la primera vez)

Si ya tienes el archivo `.env` configurado, pasa a **Levantar la arquitectura completa**.

Si acabas de clonar el repositorio, crea un archivo llamado `.env` en la misma carpeta que `compose.yaml`. Escribe una variable por línea con el formato `NOMBRE=valor`.

| Variable | Para qué se usa |
| --- | --- |
| `POSTGRES_PASSWORD` | Contraseña del usuario `postgres` de la primaria. |
| `REPLICATION_PASSWORD` | Contraseña que usa el usuario `replicador` para conectar la réplica a la primaria. |
| `KONG_API_KEY` | Clave que Kong comprueba al recibir una solicitud. Usa una clave hexadecimal aleatoria de 64 caracteres. |

Elige contraseñas distintas para los dos usuarios de PostgreSQL. Git excluye el archivo `.env` para mantener las credenciales fuera del repositorio.

## Levantar la arquitectura completa

Abre Docker Desktop y espera a que indique `Engine running`. Desde la raíz del proyecto, ejecuta:

```sh
docker compose up -d --wait
```

Este comando levanta Kong, el balanceador NGINX, las dos instancias de prueba y las dos bases de datos. El servicio `configurar-replicacion` prepara el usuario de replicación y termina. Es normal que aparezca como `Exited` después de completar su tarea.

## Levantar solo las bases de datos

Para iniciar únicamente la primaria, ejecuta:

```sh
docker compose up -d --wait primaria
```

La primaria guarda sus datos en el volumen `primaria_datos`. Para iniciar la primaria y la réplica juntas, ejecuta:

```sh
docker compose up -d --wait replica
```

En el primer arranque, la réplica toma una copia de la primaria. En los siguientes, reutiliza su volumen y continúa recibiendo los cambios.

### Cambiar la contraseña de una primaria existente

1. Con la primaria encendida, abre una sesión en PostgreSQL:

   ```sh
   docker compose exec primaria psql -U postgres -d recursos_tic
   ```

2. Cuando aparezca `recursos_tic=#`, ejecuta `\password postgres`. Escribe la nueva contraseña dos veces y sal con `\q`.
3. Abre tu `.env`, cambia el valor de `POSTGRES_PASSWORD` por esa misma contraseña y guarda el archivo.
4. Comprueba que Docker Compose puede conectarse con la contraseña guardada:

   ```sh
   docker compose run --rm --no-deps -T --entrypoint psql configurar-replicacion -X -w -h primaria -U postgres -d recursos_tic -c "SELECT current_user;"
   ```

   Si la conexión funciona, la consulta devuelve `postgres`.

## Probar el balanceador interno

Si ya levantaste la arquitectura completa, puedes hacer la prueba directamente. Para iniciar solo NGINX y las dos instancias, ejecuta `docker compose up -d --wait balanceador`.

Ejecuta esta consulta varias veces:

```sh
docker compose exec -T balanceador curl -fsSi http://127.0.0.1/health
```

La consulta se ejecuta dentro del contenedor del balanceador. La cabecera `X-Instance` indica qué servicio respondió en cada solicitud: `instancia-1` o `instancia-2`.

## Acceder desde el PC mediante Kong

Con la arquitectura completa en ejecución, Kong recibe las solicitudes del PC en `http://127.0.0.1:8000/health`. Para consultar esta ruta, envía una solicitud `GET` con la cabecera `apikey` y el valor de `KONG_API_KEY` guardado en tu `.env`.

| Solicitud | Resultado esperado |
| --- | --- |
| Con la clave válida | `200 OK` y la cabecera `X-Instance` con el nombre de la instancia que respondió. |
| Sin clave o con una clave incorrecta | `401 Unauthorized`. |