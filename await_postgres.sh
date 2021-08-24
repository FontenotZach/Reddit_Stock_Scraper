#!/bin/sh
# Wait for postgres to start and begin accepting connections
set -e

until PGPASSWORD=$SQL_PASSWORD psql -h "$SQL_HOST" -d "$SQL_DB" -U "$SQL_USER" -c '\q'; do
    >&2 echo "Postgres unavailable, sleeping"
    sleep 1
done

>&2 echo "Postgres is up, running \"$@\"."
exec "$@"
