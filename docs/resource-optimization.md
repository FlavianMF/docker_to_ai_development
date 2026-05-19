# Resource Optimization & CPU Setup

## Setting Docker RAM Limits

### Linux (Docker Engine)
Limits are typically set per container in `docker-compose.yml` or globally via systemd, but Docker on Linux uses all available host RAM by default.

### macOS / Windows (Docker Desktop)
1. Open **Settings** (gear icon).
2. Go to **Resources** > **Advanced**.
3. Adjust the **Memory** slider (Recommend **8GB** minimum for 8B models, **16GB** preferred).
4. Click **Apply & Restart**.

---

## CPU-Only Optimization

Since no NVIDIA GPU is available, use these strategies to improve speed:

### 1. Use Smaller Models
8B models are heavy on CPU. **3B** models are significantly faster and more responsive.
```bash
docker exec -it ollama ollama run hermes3:3b
```

### 2. Docker Compose Optimization
Ensure no GPU drivers are being requested which might cause overhead or errors. (The current compose is already safe as GPU is commented out).

### 3. Threading
Ollama auto-detects CPU threads. To verify or force:
- In `hermes` container, the agent handles the logic, but the heavy lifting is in `ollama`.
- Ollama will use all available cores by default. Ensure Docker has access to all CPU cores in **Settings > Resources**.

### 4. Memory Swap
If you are low on physical RAM, ensure **Swap** is enabled in Docker Desktop resources to prevent `exit code -1` (OOM) crashes.
