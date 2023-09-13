sudo apt-get install libpq-dev python3-dev
pip install telebot
pip install openai
pip install psycopg2


для yandexapi
git clone https://github.com/yandex-cloud/cloudapi
sudo apt-get install grpcurl
sudo apt update && sudo apt install jq
# sudo apt-get install portaudio19-dev
# pip install grpcio-tools PyAudio
# pip install pydub


TODO:
* добавить логирование ошибок 
* Добавить лизенцию на проект 
* Добавить распознование языка (можно брать из tg) так же нужна смена языков интерфейса и текстов в боте
+- Добавить распознование голосовых сообщений (нужно еще реализовать разбор от 30 сек, ну и перейти на v3 api)
* Добавить генерацию голосовых сообщений
* Добавить возмодность генерировать IAM-токен раз в час
* Добавить возможность собирать метрики и статистику (может пригодиться telegram-stats-bot)
* Добавить тесты
* Добавить Возможность премиума
* 
