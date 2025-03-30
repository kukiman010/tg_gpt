FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow

RUN apt-get update && apt-get install -y apt-transport-https ffmpeg

RUN apt-get install -y --no-install-recommends \
   python3.10 \
   python3-pip \
   bash \
   curl \
   jq \
   libpq-dev \
   git \
   tzdata \
   expect 

RUN apt-get update && apt-get install -y gcc  \
   python3-dev \
   build-essential \
   portaudio19-dev \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY conf /app/conf
COPY . .

# установка yc cli
RUN curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash -s -- -a
RUN expect tools/yc_init.expect
RUN ln -s /root/yandex-cloud/bin/yc /usr/local/bin/yc

# Сделайте python3 основным интерпретатором
RUN ln -s /usr/bin/python3 /usr/bin/python

# Установите pip для python3.10
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# CMD ["bash"]
CMD ["python3", "main.py"]
# CMD bash -c "source ~/.bashrc && python3 main.py"



