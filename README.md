# Hermes Docker Setup

Hermes agent inside Docker container for autonomous development.

## Features

- **Hermes Agent**: Autonomous CLI agent.
- **Google Gemini CLI**: Pre-installed for advanced AI orchestration.
- **Ollama Integration**: Run local LLMs (Hermes-3) via Docker Compose.
- **NVIDIA NIM Support**: Ready for cloud-based inference.
- **Docker-in-Docker**: Agent can spawn its own tool-use containers.
- **Global Knowledge**: Obsidian vault mounted at `/knowledge` for direct updates.
- **OAuth Ready**: Port 8080 exposed for Google/Gemini authentication flows.
- **Automated Connection**: Hermes container waits for and connects to Ollama automatically.

## Prerequisites

- Docker and Docker Compose installed.

## Getting Started (Multi-Container with Ollama)

1. **Prepare Environment**:

   ```bash
   cp .env.example .env
   # Add your NVIDIA_API_KEY if using NIM, or leave as is for local only.
   ```

2. **Start Services**:

   ```bash
   docker compose up -d
   ```

3. **Pull Local Model**:
   Execute this inside the Ollama container to download the model:

   ```bash
   docker exec -it ollama ollama pull hermes3
   ```

   _(Use `hermes3:3b` for faster downloads on low-spec hardware)_

   **Recommended Models:**
   - **Light** (Fast, low RAM < 4GB):
     - `hermes3:3b` (Optimized for agents)
     - `phi3:latest` (Microsoft, very fast)
   - **Medium** (Balanced, 8GB+ RAM):
     - `hermes3:8b` (Recommended default)
     - `llama3.1:8b` (Meta, high quality)
   - **Large** (Slow/GPU needed, 32GB+ RAM):
     - `hermes3:70b` (State of the art)
     - `qwen2.5:72b` (Excellent reasoning)

4. **Start Hermes Agent**:

   ```bash
   docker exec -it hermes-agent hermes
   ```

   **Or use Gemini CLI**:

   ```bash
   docker exec -it hermes-agent gemini
   ```

## Setup Inside Container

On your first run, you may need to configure the provider:

```bash
hermes setup
```

- For Ollama: Select `Ollama` provider. The host `http://ollama:11434` is set automatically.
- For NVIDIA: Select `OpenAI` compatible and use `https://integrate.api.nvidia.com/v1`.

## Workspace

The `./workspace` directory on your host is mounted to `/workspace` in the container. Your code and projects should live there for persistence.

## Single Container Run (Cloud Only)

If you don't want to run local Ollama:

```bash
docker build -t hermes-docker .
docker run -it \
  --env-file .env \
  -v $(pwd)/workspace:/workspace \
  -v /var/run/docker.sock:/var/run/docker.sock \
  hermes-docker
```

## Documentation

See `docs/index.md` for the full Map of Concepts and detailed guides.

## Multi-Instance Management (Working on multiple projects)

You can run isolated instances for different projects by using different project names and workspace paths:

1. **Create a project folder** (optional, you can also just use different `.env` files):
   ```bash
   mkdir -p projects/my-new-app
   ```

2. **Run with a specific project name and workspace**:
   ```bash
   COMPOSE_PROJECT_NAME=my-new-app \
   HERMES_CONTAINER_NAME=hermes-my-new-app \
   WORKSPACE_PATH=./projects/my-new-app \
   OAUTH_PORT=8081 \
   docker compose up -d
   ```

3. **Access the specific instance**:
   ```bash
   docker exec -it hermes-my-new-app hermes
   ```

Each instance will have its own:
- Isolated container and network.
- Dedicated workspace directory.
- Separate port for OAuth if needed.
- Shared Ollama instance (unless you also rename the ollama service).
