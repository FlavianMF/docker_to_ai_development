#!/bin/bash
set -e

# Default Ollama host if not set
export OLLAMA_HOST=${OLLAMA_HOST:-"http://ollama:11434"}

echo "Configuring Hermes to use Ollama at: $OLLAMA_HOST"

# Check if ollama is reachable
until curl -s "$OLLAMA_HOST/api/tags" > /dev/null; do
  echo "Waiting for Ollama to be ready..."
  sleep 2
done

echo "Ollama is ready."

# Execute the passed command or bash
exec "$@"
