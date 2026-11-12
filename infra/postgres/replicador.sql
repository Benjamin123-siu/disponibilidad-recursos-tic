\getenv clave REPLICATION_PASSWORD
BEGIN;
SELECT 'CREATE ROLE replicador' WHERE NOT EXISTS (
    SELECT FROM pg_roles WHERE rolname = 'replicador'
) \gexec
ALTER ROLE replicador WITH LOGIN REPLICATION PASSWORD :'clave';
COMMIT;
