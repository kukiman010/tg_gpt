FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow

RUN apt-get update && apt-get install -y apt-transport-https

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


# Сделайте python3 основным интерпретатором
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

RUN curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash -s -- -a

COPY conf /app/conf
COPY . .

RUN bash -c "source ~/.bashrc"
RUN expect tools/yc_init.expect

# Установите pip для python3.10
RUN python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


CMD ["bash"]
   


