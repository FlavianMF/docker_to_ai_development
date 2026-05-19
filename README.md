# Hermes Docker Setup

Hermes agent inside Docker container for dev.

## Build
```bash
docker build -t hermes-docker .
```

## Run
1. Copy `.env.example` to `.env` and add keys.
2. Run with env file:
```bash
docker run -it \
  --env-file .env \
  -v $(pwd)/workspace:/workspace \
  hermes-docker
```

## Setup Inside Container
Run once:
```bash
hermes setup
```
