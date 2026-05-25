# Hermes Docker Setup

A professional-grade containerized environment for autonomous development using **Hermes Agent** and **Google Gemini CLI**. This setup provides a safe, isolated, and scalable "sandbox" for AI agents to interact with code, manage infrastructure, and maintain a global knowledge base.

## 🚀 Key Features

- **Agentic Orchestration**: Pre-installed **Hermes Agent** and **Google Gemini CLI**.
- **Multi-Instance Architecture**: Spin up isolated environments for different projects using a single configuration.
- **Global Knowledge Integration**: Native mount for **Obsidian Vaults** at `/knowledge` for real-time synchronization of engineering notes.
- **Ollama Integration**: Automated connection to local LLMs (Hermes-3, Llama-3.1, etc.).
- **Docker-in-Docker (DooD)**: Enables agents to spawn and manage their own tool-use containers.
- **OAuth Ready**: Dedicated port (8080) and persistence for Google/Gemini authentication flows.

## 🛠️ Prerequisites

- Docker and Docker Compose.
- (Optional) NVIDIA GPU for hardware acceleration.

## 🏁 Getting Started

### 1. Initialize Environment
```bash
cp .env.example .env
# Edit .env to set your OBSIDIAN_VAULT_PATH and other keys
```

### 2. Launch Services
```bash
docker compose up -d
```

### 3. Initialize Models (Local Ollama)
```bash
docker exec -it ollama ollama pull hermes3:8b
```

### 4. Enter the Agent Environment
```bash
# To use Hermes Agent
docker exec -it hermes-agent hermes

# To use Gemini CLI
docker exec -it hermes-agent gemini
```

---

## 📂 Multi-Instance Management

Work on multiple projects simultaneously without interference. Each instance gets its own workspace and identity while sharing the core LLM backbone.

### Spawning a new instance:
```bash
COMPOSE_PROJECT_NAME=my-web-app \
HERMES_CONTAINER_NAME=hermes-web-app \
WORKSPACE_PATH=./projects/web-app \
OAUTH_PORT=8081 \
docker compose up -d
```

### Resource Isolation:
- **`COMPOSE_PROJECT_NAME`**: Isolates network and service stacks.
- **`WORKSPACE_PATH`**: Mounts a specific local folder to `/workspace`.
- **`OAUTH_PORT`**: Unique port for Gemini CLI authentication callbacks.

---

## 🧠 Knowledge Base Integration

Your Obsidian vault is automatically mounted to `/knowledge` inside the container. This allows the agent to:
1.  Read engineering standards and architectural patterns.
2.  Update project documentation and permanent notes.
3.  Maintain a "Global Brain" across multiple development tasks.

---

## ⚙️ Setup & Configuration

Inside the container, initialize your preferred AI provider:
```bash
hermes setup
```
- **Local (Ollama)**: Use `http://ollama:11434`.
- **Cloud (NVIDIA NIM)**: Use `https://integrate.api.nvidia.com/v1` with your API key.

## 📖 Documentation
Detailed guides are available in the `docs/` directory:
- [[usage-guide|Usage & Multi-Instance Guide]]
- [[ollama-setup|Local LLM Setup]]
- [[oauth-setup|OAuth & Remote Access]]
- [[docker-in-docker|Docker-in-Docker Architecture]]

---
*Created for autonomous engineering workflows.*
