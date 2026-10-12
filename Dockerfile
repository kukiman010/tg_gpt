FROM python:3.10-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Moscow \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

WORKDIR /app
COPY conf ./conf

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq-dev \
    tzdata \
    gcc \
    python3-dev \
    build-essential \
    portaudio19-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
