#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )/"

VERSION="0.2"

FILE_DB="tg_base.sql"

KEY="$1"
DB_NAME="$2"
DB_LOGIN="postgres"
DB_PASS="$3"
DB_HOST="$4"
DB_PORT="5432"


command -v psql >/dev/null 2>&1 || { echo >&2 "Требуется psql, но он не установлен. Прекращение работы."; exit 1; }

drop()
{
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_LOGIN -c "DROP DATABASE IF EXISTS $DB_NAME;"
}

create()
{
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_LOGIN -c "CREATE DATABASE $DB_NAME;"
}

install_db()
{
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_LOGIN -d $DB_NAME -f "$DIR$FILE_DB"
}


install_all()
{
    echo "Терминирование активных сессий для базы данных $DB_NAME..."
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_LOGIN -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = '$DB_NAME';" > /dev/null

    echo "Удаление существующей базы данных..."
    drop

    echo "Создание новой базы данных..."
    create

    echo "Инициализация базы данных из SQL файла..."
    install_db

    echo "Инициализация завершена."
}

info()
{
    echo "Скрипт для инициализации базы данных TG_GPT"
    echo "Версия скрипта: $VERSION"
    echo ""
    echo "-h                Показать помощь"
    echo "-b                Переустановка базы данных"
    echo ""
    echo "Пример использования:"
    echo "sudo bash ./create_db.sh -b \"имя_базы_данных\" \"пароль\" \"хост\""
    exit 0
}



if [ "$KEY" == "-h" ]; then
    info
elif [ "$KEY" == "-b" ]; then
    if [ -z "$DB_NAME" ] || [ -z "$DB_PASS" ] || [ -z "$DB_HOST" ]; then
        echo "Не все необходимые параметры были переданы."
        info
    fi
    install_all
else 
    echo "Неверные аргументы"
    info
fi
