#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
while ! pg_isready -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -t 1; do
  sleep 2
done

# Execute regular start script
exec ./start.sh