
import os
import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request 

app = Flask(__name__)

INSTANCIA = os.getenv("INSTANCE_ID", "sin-definir")


@app.get("/health")
def health():
    respuesta = jsonify({
        "status": "ok",
        "instance_id": INSTANCIA
    })

    respuesta.headers["X-Instance"] = INSTANCIA
    return respuesta, 200


@app.get("/api/v1/recursos")
def obtener_recursos():
    try:
        # Conexión a la base de datos réplica
        with psycopg.connect(
            os.environ["DB_REPLICA_URL"],
            connect_timeout=5
        ) as conexion:

            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    "SELECT id, nombre, cantidad_disponible "
                    "FROM recursos ORDER BY id"
                )
                recursos = cursor.fetchall()

        respuesta = jsonify(recursos)

        respuesta.headers["X-Instance"] = INSTANCIA
        respuesta.headers["X-DB"] = "replica"

        return respuesta, 200

    except (psycopg.Error, KeyError):
        respuesta = jsonify({
            "error": "No se pudieron consultar los recursos"
        })
        respuesta.headers["X-Instance"] = INSTANCIA
        return respuesta, 503


@app.post("/api/v1/movimientos")
def registrar_movimiento():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "Se requiere un JSON valido"}), 400

    recurso_id = datos.get("recurso_id")
    tipo = datos.get("tipo")
    cantidad = datos.get("cantidad")

    if (type(recurso_id) is not int or recurso_id <= 0
            or tipo not in ("entrega", "devolucion")
            or type(cantidad) is not int or cantidad <= 0):
        return jsonify({"error": "Datos invalidos"}), 400

    try:
        with psycopg.connect(
            os.environ["DB_PRIMARY_URL"],
            connect_timeout=5
        ) as conexion:

            with conexion.cursor(row_factory=dict_row) as cursor:
                # Bloqueamos el recurso durante el movimiento
                cursor.execute(
                    "SELECT cantidad_disponible FROM recursos "
                    "WHERE id = %s FOR UPDATE",
                    (recurso_id,)
                )
                recurso = cursor.fetchone()

                if recurso is None:
                    return jsonify({"error": "Recurso no encontrado"}), 404

                disponible = recurso["cantidad_disponible"]

                if tipo == "entrega" and cantidad > disponible:
                    return jsonify({
                        "error": "Cantidad insuficiente"
                    }), 409

                if tipo == "devolucion":
                    cursor.execute(
                        "SELECT COALESCE(SUM("
                        "CASE WHEN tipo = 'entrega' THEN cantidad "
                        "ELSE -cantidad END), 0) AS pendientes "
                        "FROM movimientos WHERE recurso_id = %s",
                        (recurso_id,)
                    )
                    pendientes = cursor.fetchone()["pendientes"]

                    if cantidad > pendientes:
                        return jsonify({
                            "error": "Devolucion superior a lo prestado"
                        }), 409

                cambio = -cantidad if tipo == "entrega" else cantidad

                cursor.execute(
                    "UPDATE recursos "
                    "SET cantidad_disponible = cantidad_disponible + %s "
                    "WHERE id = %s RETURNING cantidad_disponible",
                    (cambio, recurso_id)
                )
                nueva_cantidad = cursor.fetchone()["cantidad_disponible"]

                cursor.execute(
                    "INSERT INTO movimientos (recurso_id, tipo, cantidad) "
                    "VALUES (%s, %s, %s) RETURNING id",
                    (recurso_id, tipo, cantidad)
                )
                movimiento_id = cursor.fetchone()["id"]

        respuesta = jsonify({
            "mensaje": "Movimiento registrado",
            "movimiento_id": movimiento_id,
            "cantidad_disponible": nueva_cantidad
        })
        respuesta.headers["X-Instance"] = INSTANCIA
        respuesta.headers["X-DB"] = "primary"

        return respuesta, 201

    except (psycopg.Error, KeyError):
        respuesta = jsonify({
            "error": "No se pudo registrar el movimiento"
        })
        respuesta.headers["X-Instance"] = INSTANCIA
        return respuesta, 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
