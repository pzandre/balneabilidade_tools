FROM python:3.13-slim AS build-stage

WORKDIR /app

RUN groupadd -r balneabilidade && useradd -r -g balneabilidade balneabilidade

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.13-slim AS runner-stage

RUN groupadd -r balneabilidade && useradd -r -g balneabilidade balneabilidade

WORKDIR /app

COPY --from=build-stage /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build-stage /app /app

RUN chown -R balneabilidade:balneabilidade /app && \
    chmod -R 755 /app

USER balneabilidade

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]