Добро пожаловать в проект!

Ниже приведено руководство по установке и настройке необходимых пакетов для проекта:

## Установка зависимостей

Выполните следующую команду, чтобы установить необходимые зависимости:

```shell
sudo apt-get install libpq-dev python3-dev
pip install telebot
pip install openai
pip install psycopg2
```

## Yandex API

Для использования Yandex API выполните следующие действия:

1. Клонирование репозитория:

   ```shell
   git clone https://github.com/yandex-cloud/cloudapi
   ```

2. Установка grpcurl:

   ```shell
   sudo apt-get install grpcurl
   ```

3. Обновление пакетов и установка jq:

   ```shell
   sudo apt update && sudo apt install jq
   ```

   Опционально:

   - Установка portaudio19-dev:

     ```shell
     sudo apt-get install portaudio19-dev
     ```

   - Установка дополнительных пакетов для голосовых сообщений:

     ```shell
     pip install grpcio-tools PyAudio
     pip install pydub
     ```

## Настройка базы данных

Пожалуйста, обратите внимание, что база данных должна работать только в кодировке UTF-8.

Выполните следующие шаги, чтобы настроить базу данных:

1. Установка кодировки UTF-8 для базы данных:

   ```sql
   UPDATE pg_database SET datistemplate = FALSE WHERE datname = 'tg_base';
   DROP DATABASE tg_base;
   CREATE DATABASE tg_base WITH owner=postgres ENCODING = 'UTF-8' lc_collate = 'en_US.utf8' lc_ctype = 'en_US.utf8' template template0;
   UPDATE pg_database SET datistemplate = TRUE WHERE datname = 'tg_base';
   ```

2. Установка кодировки UTF-8 для клиента:

   ```sql
   SET client_encoding = 'UTF8';
   ```

## TODO

- [+] Добавить логирование ошибок 
- [ ] Добавить лицензию на проект 
- [ ] Добавить распознавание языка (можно брать из tg) также нужна смена языков интерфейса и текстов в боте
- [+] Добавить распознавание голосовых сообщений (нужно еще реализовать разбор от 30 сек, ну и перейти на v3 api)
- [+] Добавить генерацию голосовых сообщений v3
- [+] Добавить возможность генерировать IAM-токен раз в час
- [ ] Добавить возможность собирать метрики и статистику (может пригодиться telegram-stats-bot)
- [ ] Добавить тесты
- [ ] Добавить возможность премиума
- [ ] Решить проблему с ограничениями token size для chatgpt
- [ ] Добавить возможность фидбека при ошибка
- [ ] сделать AiApi для того, что бы можно было работать с разными нейронками (например gigachat or yandexGpt)
- [ ] Сделать функцию, которая будет задавать промт
- [ ] показывать количество на историю переписки
- [ ] 
- [ ] 