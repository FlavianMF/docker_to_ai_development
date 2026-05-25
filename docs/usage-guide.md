# Usage Guide

## Gemini CLI & Hermes
Both tools are pre-installed.
- **Hermes**: `hermes`
- **Gemini CLI**: `gemini`

## Multi-Instance Support
To work on multiple projects simultaneously without interference:

### Using Project Names
Run Docker Compose with a unique project name, container name, and workspace path:

```bash
COMPOSE_PROJECT_NAME=my-project \
HERMES_CONTAINER_NAME=hermes-my-project \
WORKSPACE_PATH=./path/to/project \
OAUTH_PORT=8081 \
docker compose up -d
```

### Key Variables
- `COMPOSE_PROJECT_NAME`: Isolates the Docker stack.
- `HERMES_CONTAINER_NAME`: Ensures unique container identity.
- `WORKSPACE_PATH`: Maps specific project files.
- `OAUTH_PORT`: Prevents port collisions for OAuth callbacks.

## Persistence
- **Workspace**: Mapped via `WORKSPACE_PATH`.
- **Global Knowledge**: Your Obsidian vault is mounted at `/knowledge` inside the container.
- **Gemini Config**: Persisted in `gemini_data` volume across all instances.
- **Ollama**: Shared across instances via the internal network.
