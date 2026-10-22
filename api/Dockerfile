# JP Security SAS — servicio de contacto (solo biblioteca estándar)
FROM python:3.12-alpine

LABEL org.opencontainers.image.title="JP Security SAS API" \
      org.opencontainers.image.description="Recibe el formulario de contacto, lo guarda y lo reenvía por correo" \
      org.opencontainers.image.source="https://github.com/pel-matiasvaldivia/jpsecutirysas" \
      org.opencontainers.image.licenses="UNLICENSED"

# Usuario sin privilegios; /data queda a su nombre para que el volumen
# nombrado herede el propietario correcto al crearse.
RUN adduser -D -u 10001 app && mkdir -p /data && chown app:app /data

COPY server.py /app/server.py

USER app
WORKDIR /app
VOLUME ["/data"]
EXPOSE 8080

ENV PORT=8080 \
    DATA_FILE=/data/consultas.jsonl \
    PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/api/healthz || exit 1

CMD ["python3", "-I", "/app/server.py"]
