[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

## Добро пожаловать в проект!

проверить работу можно в [телеграме][tg]

Ниже приведено руководство по установке и настройке необходимых пакетов для проекта:

## Установка зависимостей

Python >= 3.8.* && <= 3.10.0*

Выполните следующую команду, чтобы установить необходимые зависимости:

```shell
sudo apt-get install libpq-dev python3-dev

pip install --no-cache-dir -r requirements.txt
```

## Yandex API

Для использования Yandex API выполните следующие действия:

1. Создание профиля

   Следовать этой [инструкции][df3]

2. Клонирование репозитория:

   ```shell
   git clone https://github.com/yandex-cloud/cloudapi
   ```

3. Установка grpcurl:

   ```shell
   sudo apt-get install grpcurl
   ```

4. Обновление пакетов и установка jq:

   ```shell
   sudo apt update && sudo apt install jq
   ```

   Опционально:

   - Установка portaudio19-dev:

     ```shell
     sudo apt-get install portaudio19-dev
     ```

## Sber API

Для использования Sber API выполните следующие действия:
1. Скачать российский сертификат с [сайта госуслуг][df1]:

2. Переместить скаченый сертификат

После скачивания сертификата переместите его в нужную папку, используя команду:

```bash
sudo cp ./russian_trusted_root_ca_pem.crt /usr/local/share/ca-certificates/
```

3. Обновление сертификатов

Выполните обновление системных сертификатов командой:

```bash
sudo update-ca-certificates
```

4. Получение авторизационных данных

Для получения данных авторизации перейдите на [сайт разработчиков][df2] Сбер:

Создайте учетную запись и следуйте инструкциям для получения необходимых данных авторизации (API ключа и токена).
Внесите в файл conf/sber_config.ini полученные данные


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

- [ ] Добавить возможность собирать метрики и статистику (может пригодиться telegram-stats-bot)
- [ ] Добавить тесты
- [ ] Добавить возможность премиума
- [ ] Добавить возможность фидбека при ошибке
- [ ] Добавлять фотографии в контекст переписка
- [ ] Привести структуру проекта в порядок 
- [ ] Добавить возможность отправлять ссылки для выжемки текста
- [ ] Диспетчер нагрузки для базы
- [ ] Сделать миниап с ссылкой на поиск через гпт
- [ ] Ошибка. дублируется заголовок сообщения при отправке файла
- [ ] Добавить команду выключения
- [ ] Так же при update environment нужно блокировать и обновлять список моделей.
- [ ] Добавить в default_data переменную чата поддержки по умолчанию, а то сейчас поддержка хардкодиться в файлах переводов
- [ +/- ] Добавить возможность поиска в интеренете (пока частично реализовано для openai и Claude)
- [ ] Ссылка на источник
https://community.openai.com/t/how-to-enable-web-search-results-with-chatgpt-api/318118/2
- [ ] Добавить выбор голоса для yndex tts
- [ ] Добавить в меню пункт добавления think
- [ ] Добавить в меню пункт добавления locate
- [ ] Задать такую переменную как tire для моделей openai, так же нужно запрашивать tire аккаунта при старте и update_env
- [ ] 




[df1]: <https://www.gosuslugi.ru/crt>
[df2]: <https://developers.sber.ru/docs/ru/gigachat/api/authorization>
[df3]: <https://cloud.yandex.ru/docs/cli/quickstart#linux_1>
[tg]:  <https://t.me/kukimanGptBot>
