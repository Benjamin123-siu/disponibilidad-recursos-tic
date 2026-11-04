# Problemática: Consulta de disponibilidad de recursos TIC

## 1. Descripción del problema

En un colegio, los profesores necesitan saber si hay recursos tecnológicos disponibles, como notebooks, tablets y proyectores. Si esta información se consulta de manera informal, pueden solicitar un equipo que ya está prestado o perder tiempo preguntando al encargado.

Se propone un sistema sencillo que permita consultar la cantidad disponible de cada recurso. El encargado TIC podrá registrar cuándo se entrega o devuelve un equipo, para mantener el inventario actualizado.

## 2. ¿Quiénes lo usarán?

- **Profesores:** consultarán la disponibilidad desde una página web.
- **Encargado TIC o sistema administrativo:** consultará los datos desde un pequeño programa externo en Python y registrará entregas y devoluciones mediante la API.

Así existirán al menos dos tipos de clientes que consumen la misma API: una aplicación web y un programa externo.

## 3. ¿Por qué hay más lecturas que escrituras?

Es habitual que los profesores consulten varias veces la disponibilidad, mientras que el inventario solo cambia cuando se entrega o devuelve un equipo.

**Supuestos iniciales para un colegio:**

- 40 profesores.
- 12 consultas por profesor al día: 40 × 12 = **480 lecturas diarias**.
- 20 entregas o devoluciones al día: **20 escrituras diarias**.
- Relación lectura/escritura: 480 ÷ 20 = **24 a 1**.


## 4. ¿Cómo podría crecer?

El diseño partirá pensando en un colegio y tendrá como objetivo poder atender a **10 colegios** con un uso similar:

- Aproximadamente **400 profesores**.
- Aproximadamente **4.800 lecturas diarias**.
- Aproximadamente **200 escrituras diarias**.

Las dos instancias de la aplicación y el balanceador permitirán repartir las solicitudes y seguir respondiendo si una instancia deja de funcionar. Estos valores son una meta de diseño y se comprobarán en las siguientes fases.

## 5. ¿Qué dato es importante proteger?

El dato más importante es la **cantidad disponible de cada recurso**. Si se pierde una entrega o devolución, el sistema podría mostrar una cantidad incorrecta.

Como objetivos iniciales, se propone:

- **RPO:** perder como máximo 1 minuto de actualizaciones ante una falla grave.
- **RTO:** recuperar la capacidad de registrar cambios en un máximo de 15 minutos.
- **Lecturas:** se acepta un atraso breve de la réplica, pero antes de registrar un préstamo o devolución se verificará el valor actualizado en la base primaria.

Son objetivos de diseño; no se consideran garantizados hasta que se pruebe el sistema.

## 6. Alcance pequeño del proyecto

Para mantener el trabajo realizable, se usarán solamente **2 entidades**:

1. **Recurso:** nombre y cantidad disponible de tablets, notebooks, proyectores, etc.
2. **Movimiento:** registro de entrega o devolución, asociado al recurso.

**Endpoints principales planificados:**

- `GET /api/v1/recursos`: consultar recursos (lectura desde réplica).
- `GET /api/v1/recursos/:id`: consultar un recurso (lectura desde réplica).
- `POST /api/v1/movimientos`: registrar una entrega o devolución (escritura en primaria).
- `GET /health`: comprobar el estado de cada instancia.

**Limites**

El proyecto no incluirá autenticación de profesores, reservas anticipadas ni notificaciones, para concentrarse en la arquitectura solicitada.
