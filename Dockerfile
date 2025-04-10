FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

COPY conf ./conf

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ffmpeg \
    bash \
    curl \
    jq \
    libpq-dev \
    git \
    tzdata \
    expect \
    gcc \
    python3-dev \
    build-essential \
    portaudio19-dev \
    && curl -s https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash -s -- -a 

RUN expect tools/yc_init.expect \
    && ln -s /root/yandex-cloud/bin/yc /usr/local/bin/yc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
