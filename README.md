sudo apt-get install libpq-dev python3-dev
pip install telebot
pip install openai
pip install psycopg2


для работы yandexapi
<!-- git clone https://github.com/yandex-cloud/cloudapi
sudo apt-get install grpcurl
sudo apt update && sudo apt install jq
# sudo apt-get install portaudio19-dev
# pip install grpcio-tools PyAudio
# pip install pydub -->

<!-- // install  go
wget https://go.dev/dl/go1.21.1.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.21.1.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin -->

curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
exec -l $SHELL
https://oauth.yandex.ru/authorize?response_type=token&client_id=1a6990aa636648e9b2ef855fa7bec2fb
restart terminal 
yc init 


//intal grpcurl
wget https://github.com/fullstorydev/grpcurl/releases/download/v1.8.7/grpcurl_1.8.7_linux_x86_32.tar.gz
tar -xf grpcurl_1.8.7_linux_x86_32.tar.gz 
sudo cp ./grpcurl /usr/bin/


TODO:
* добавить логирование ошибок 
* Добавить лизенцию на проект 
* Добавить распознование языка (можно брать из tg) так же нужна смена языков интерфейса и текстов в боте
+- Добавить распознование голосовых сообщений (нужно еще реализовать разбор от 30 сек, ну и перейти на v3 api)
+ Добавить генерацию голосовых сообщений v3
* Добавить возмодность генерировать IAM-токен раз в час
* Добавить возможность собирать метрики и статистику (может пригодиться telegram-stats-bot)
* Добавить тесты
* Добавить Возможность премиума
* Добавить проверку подключения к БД
* 
