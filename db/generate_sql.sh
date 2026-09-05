#!/usr/bin/env bash

# Regenere le SQL depuis le .dbml et l'applique a la base Postgres (via Docker).
# Usage: ./generate_sql.sh [chemin/vers/schema.dbml]


set -euo pipefail

DBML_FILE="${1:-db/schema.dbml}"
OUT_DIR="$(dirname "$DBML_FILE")"
SQL_FILE="$OUT_DIR/schema.sql"
ENV_FILE=".env"
 
if [ ! -f "$ENV_FILE" ]; then
    echo "Erreur: fichier .env introuvable" 
    exit 1
fi
 
# Parametres de connexion lus depuis .env 
set -a
source "$ENV_FILE"
set +a
DB_USER="$POSTGRES_USER"
DB_NAME="$POSTGRES_DB"
DB_CONTAINER="waterpolo_db"
 

if [[ ! -f "$DBML_FILE" ]]; then
	echo "Erreur: fichier introuvable $DBML_FILE"
	exit 1
fi

if ! command -v dbml2sql &> /dev/null ; then
	echo "Erreur: dbml2sql introuvable"
	exit 1
fi

dbml2sql "$DBML_FILE" --postgres -o "$SQL_FILE"

if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}" ; then
	echo "  Conteneur non demarre"
    docker compose -f ./docker.yml up -d
    until docker exec "$DB_CONTAINER" pg_isready -U "$DB_USER" &> /dev/null; do
        sleep 1
    done
fi

# On repart de zero pour l'instant (phase de conception) : on drop et recree le schema public.
# ATTENTION: ceci efface toutes les donnees existantes.

docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$SQL_FILE"
 
echo ""
echo "Termine."
echo "  SQL genere : $SQL_FILE"
echo "  Base       : postgresql://${DB_USER}@localhost:5432/${DB_NAME}"
