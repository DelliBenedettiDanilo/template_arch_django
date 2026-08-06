FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt

# 1. Copiamo l'entrypoint nella root (/app/entrypoint.sh)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 2. Copiamo il codice di project in una sottocartella dedicata (/app/project)
COPY ./project /app/project

# Creiamo le directory di destinazione dei volumi static/media qui, così Docker
# le inizializza con l'ownership corretta al primo mount del volume nominato
# (altrimenti verrebbero create vuote e di proprietà di root, non scrivibili
# dall'utente non-root "django" durante collectstatic).
RUN mkdir -p /app/staticfiles /app/mediafiles && \
    useradd -m -u 1000 django && \
    chown -R django:django /app

USER django

EXPOSE 8000

# L'entrypoint è al sicuro nella root
ENTRYPOINT ["/app/entrypoint.sh"]

# CMD in shell form per permettere l'espansione delle env var a runtime
# (numero di worker/thread/timeout regolabili da .env.prod senza rebuild)
CMD gunicorn config.wsgi:application --chdir /app/project \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-30} \
    --graceful-timeout 30 \
    --worker-tmp-dir /dev/shm \
    --access-logfile - --error-logfile -