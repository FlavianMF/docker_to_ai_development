# Ollama Local LLM Setup

## Architecture: Multi-Container
Better approach: separate containers.
1. **Ollama Container**: Standard `ollama/ollama` image. Handles model weights and inference.
2. **Hermes Container**: Custom image with Hermes Agent CLI. Connects to Ollama via internal network.

## Benefits
- Isolation: Models don't bloat the agent image.
- Persistence: Ollama data volumes managed separately.
- Scalability: Can swap Ollama for other backends easily.

## Automation
Hermes container uses `entrypoint.sh` to:
1. Wait for Ollama service.
2. Set `OLLAMA_HOST`.
3. Ensure connectivity before starting.

## Usage
1. `docker compose up -d`
2. `docker exec -it ollama ollama run hermes3` (Pull model)

### Llama Runner Error (Exit Code -1)
If you see "llama runner process has terminated with exit code -1", it usually means **Out of Memory (OOM)** or **AVX/Hardware incompatibility**.

**Fixes**:
1. **Try a smaller model**:
   ```bash
   docker exec -it ollama ollama run hermes3:3b
   ```
2. **Increase Docker Resources**: Ensure Docker has at least 8GB RAM assigned.
3. **CPU-only mode**: If you don't have an NVIDIA GPU, ensure you aren't trying to force GPU drivers.
3. `docker exec -it hermes-agent hermes` (Start agent)

## WSL2 & Windows Browser Access
To complete Google OAuth or access the agent from Windows:
1. **Localhost**: Try `http://localhost:8080` in Chrome/Edge. WSL2 usually maps this automatically.
2. **WSL IP**: If localhost fails, find your WSL IP in terminal:
   ```bash
   ip addr show eth0 | grep inet
   ```
   Use `http://<WSL_IP>:8080`.
3. **Firewall**: Ensure Windows Firewall allows traffic on port 8080 for Docker Desktop.
