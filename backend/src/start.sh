#!/bin/sh
CERT=/app/data/certs/server.crt
KEY=/app/data/certs/server.key

mkdir -p /app/data/certs
mkdir -p /app/data/logs

if [ ! -f "$CERT" ] || [ ! -f "$KEY" ]; then
  echo "Generating certificate..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout $KEY -out $CERT \
    -subj "/CN=localhost"
fi

echo "Running tests..."
uv run pytest tests/ -v --tb=short
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
  echo "Tests failed! Exit code: $TEST_EXIT_CODE"
  exit $TEST_EXIT_CODE
fi

if [ "$RUN_TESTS_ONLY" = "1" ]; then
  echo "Tests passed! Exiting..."
  exit 0
fi

echo "Tests passed! Starting app..."
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 \
    --ssl-keyfile=$KEY --ssl-certfile=$CERT
