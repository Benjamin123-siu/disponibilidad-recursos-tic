
CREATE TABLE IF NOT EXISTS recursos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    cantidad_disponible INTEGER NOT NULL DEFAULT 0
        CHECK (cantidad_disponible >= 0)
);

CREATE TABLE IF NOT EXISTS movimientos (
    id SERIAL PRIMARY KEY,
    recurso_id INTEGER NOT NULL REFERENCES recursos(id),
    tipo VARCHAR(20) NOT NULL
        CHECK (tipo IN ('entrega', 'devolucion')),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
