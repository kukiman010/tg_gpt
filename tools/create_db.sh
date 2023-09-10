#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )/"

VERSION="0.1"
FILE_DB="tg_base.sql"
KEY="$1"

DB_NAME="$2"
DB_LOGIN="postgres"
DB_PASS="$3"
DB_HOST="$4"
DB_PORT="5432"


drop()
{
    DB_PASS=$DB_PASS $POSSQL_DIR"psql" -h $DB_HOST -p $DB_PORT -U $DB_LOGIN -c "DROP DATABASE $DB_NAME;"
}

create()
{
    DB_PASS=$DB_PASS $POSSQL_DIR"psql" -h $DB_HOST -p $DB_PORT -U $DB_LOGIN -c "CREATE DATABASE $DB_NAME;"
}

install_db()
{
    DB_PASS=$DB_PASS $POSSQL_DIR"psql" -h $DB_HOST -p $DB_PORT -U $DB_LOGIN -d $DB_NAME < $DIR$FILE_DB
}


install_all()
{
    DB_PASS=$DB_PASS $POSSQL_DIR"psql" -h $DB_HOST -p $DB_PORT -U $DB_LOGIN -c "SELECT pg_terminate_backend (pid) from pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = '$DB_NAME';" > /dev/null
    
    drop
    create
    install_db
}

info()
{
    echo "Make database for TG_GPT"
    echo "Version sripts: $VERSION"
    echo ""
    echo "-h                Help"
    echo "-b                Reinstalling the database"
    echo ""
    echo "Example:"
    echo "sudo bash ./create_db.sh -b \"tg_base\" \"postgres\" \"127.0.0.1\""


    exit 0

}



if [ "$KEY" == "-h" ]; then
    info
elif [ "$KEY" == "-b" ]; then
    install_all
else 
    echo "Not valid args"
fi
