# Hermes Docker Setup

Hermes agent inside Docker container for dev.

## Build
```bash
docker build -t hermes-docker .
```

## Run
Must pass API keys via env.
```bash
docker run -it \
  -v $(pwd)/workspace:/workspace \
  -e OPENROUTER_API_KEY=your_key \
  hermes-docker
```

## Setup Inside Container
Run once:
```bash
hermes setup
```
