#!/bin/sh
set -eu

if [ ! -s "$PGDATA/PG_VERSION" ]; then
    copia=$(mktemp -d /var/lib/postgresql/data/copia.XXXXXX)
    trap 'rm -rf "$copia"' EXIT
    pg_basebackup --dbname="host=primaria user=replicador application_name=replica" \
        --pgdata="$copia" --write-recovery-conf --wal-method=stream --no-password
    mv "$copia" "$PGDATA"
    trap - EXIT
fi

exec postgres -D "$PGDATA"
