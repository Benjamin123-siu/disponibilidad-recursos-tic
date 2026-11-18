INSERT INTO recursos (nombre, cantidad_disponible)
VALUES
    ('Tablet', 20),
    ('Notebook', 10),
    ('Proyector', 5)
ON CONFLICT (nombre) DO NOTHING;
