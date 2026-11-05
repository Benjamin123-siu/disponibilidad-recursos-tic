**Requisitos y estimación de carga**
**Proyecto:** Disponibilidad de recursos TIC
**Asignatura:** ISI601 – Taller de Diseño de Sistemas
**Fase:** 1 – Diseño
**Avance:** Jueves 5 de noviembre de 2026

# Requisitos Funcionales:
1. Consultar Recursos: Los profesores pueden ver el listado junto con la disponibilidad de los recursos dentro de la pagina web
2. Consultar 1 Recurso: Se puede revisar la disponibilidad de un recurso en especifico
3. Registrar Entrega: El encargado TIC puede registrar la entrega de 1 o más unidades de un recurso desde un programa en Python
4. Registrar Devolución: El encargado TIC puede registrar la devolución de las unidades de un recurso
5. Actualizar Disponibilidad: Al registrar una entrega o devolución el sistema actualiza la cantidad disponible
6. Evitar Cantidades Negativas: No se permite entregar una cantidad superior a la disponible, siempre se valida el dato 
7. Consultar Movimientos: El encargado puede consultar los movimientos registrados de cada recurso

La aplicación web y el programa administrativo en Python consumirán la misma API. Se mantendrán dos entidades principales: Recurso y Movimiento.

# Requisitos No Funcionales:
1. Tiempo de respuesta de lectura: El 95% de las consultas responderá en menos de 500ms en la carga estimada
2. Tiempo de respuesta de escritura: El 95% de las entregas y devoluciones se registra en menos de 1 segundo en la carga estimada
3. Disponibilidad: Al menos un 99% durante el horario de uso del colegio 
4. RPO: Ante una falla grave, perder como máximo 1 minuto de cambios recientes
5. RTO: Recuperar la capacidad de registrar movimientos en un máximo de 15 minutos
6. Escalabilidad: Atender hasta 10 colegios con 2 instancias de la aplicación y un balanceador
7. Consistencia: Las escrituras se validan contra la base primaria. La consulta desde la réplica puede mostrar brevemente datos anteriores

# Estimación de carga
1 colegio: 40 profesores
Consultas por profesor: 12 al día 
Entregas y devoluciones: 20 movimientos por día 
Horario de uso: 8 Horas diarias (Durante el periodo de clases)
Escala objetivo: 10 colegios de tamaño similar
Hora punta: Se estima una carga 5 veces mayor que el promedio durante el horario de uso
Año escolar: Aprox 200 dias de actividad

# Cálculos de lecturas y escrituras
**Un Colegio**
Lecturas al día: 40 profesores x 12 consultas = 480 lecturas por día
Escrituras al día: 20 movimientos por día
Relación: 480/20 = 24 escrituras por día 

**10 Colegios**
Lecturas al día: 480 x 10 = 4800 lecturas al día
Escrituras al día: 20 x 10 = 200 escrituras al día

**Promedio por segundo en horario de uso**
Lecturas: 4800/28800(8horas transformado a seg) = 0,167 lecturas por segundo
Escrituras: 200/28800 = 0,0069 escrituras por segundo 

**Hora punta estimada (5veces el promedio)**
Lecturas: 0,167 x 5 = 0,833 lecturas por segundo
Escrituras: 0,0069 x 5 = 0,0347 escrituras por segundo 

Estas cifras son promedios de referencia para dimensionar el sistema; las peticiones reales llegan de manera irregular y pueden concentrarse en segundos específicos.

# Estimación a 5 años
Se considera que cada movimiento registrado ocupa aproximadamente 250 bytes como supuesto inicial (incluidos sus campos y una estimación sencilla de espacio por registro)

Movimientos anuales: 200 movimientos al día x 200 días al año = 40000 movimientos al año
Movimientos en 5 años: 40000 x 5 = 200000 movimientos 
Espacio para movimientos: 200000 x 250 bytes = 50000000 bytes 
Recursos: Se estiman 20 tipos de recursos por colegio x 10 colegios = 200 registros, con un tamaño muy pequeño frente al historial de movimientos
Considerando espacio adicional para índices y crecimiento, se reserva un margen de 3 veces: aproximadamente 150 MB

Esta es una estimación de datos de la aplicación, no incluye las copias de seguridad ni el almacenamiento adicional necesario para mantener la réplica completa. La réplica tendrá su propia copia de los datos

# Resumen 
El sistema propuesto tiene más lecturas que escrituras (24:1), por lo que es razonable usar una réplica de lectura. La aplicación web y el programa administrativo justifican una entrada común mediante API Gateway. El balanceador y las dos instancias permiten distribuir solicitudes y mantener el servicio de aplicación ante la caída de una instancia.