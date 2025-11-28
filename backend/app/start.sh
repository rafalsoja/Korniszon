#!/bin/sh
CERT=/app/certs/server.crt
KEY=/app/certs/server.key

if [ ! -f "$CERT" ] || [ ! -f "$KEY" ]; then
  echo "Generating certificate..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout $KEY -out $CERT \
    -subj "/CN=localhost"
  mkdir -p /app/data
  cp $CERT /app/data/server.crt
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 \
    --ssl-keyfile=$KEY --ssl-certfile=$CERT