FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN useradd -u 8888 appuser && chown -R appuser:appuser /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

COPY --chown=appuser:appuser scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]