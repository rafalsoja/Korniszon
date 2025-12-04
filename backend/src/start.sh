#!/bin/sh
CERT=/app/data/certs/server.crt
KEY=/app/data/certs/server.key

if [ ! -f "$CERT" ] || [ ! -f "$KEY" ]; then
  echo "Generating certificate..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout $KEY -out $CERT \
    -subj "/CN=localhost"
fi

uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 \
    --ssl-keyfile=$KEY --ssl-certfile=$CERT