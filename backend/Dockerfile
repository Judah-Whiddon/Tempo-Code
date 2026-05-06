# TempoCode backend — FastAPI on Python 3.12 slim.
# Same image runs the API and the one-shot seed job (compose overrides the command).

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# psycopg2-binary ships pre-built wheels — no apt-get build deps needed.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Bind to 0.0.0.0 so the container is reachable from the host port mapping.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
