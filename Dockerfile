# Dockerfile for Hermes Agent

FROM ubuntu:22.04

# Avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
  curl \
  git \
  build-essential \
  python3 \
  python3-pip \
  ca-certificates \
  python3-dotenv \
  lsb-release \
  gnupg \
  && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (to talk to host Docker)
RUN install -m 0755 -d /etc/apt/keyrings \
  && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
  && chmod a+r /etc/apt/keyrings/docker.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
  && apt-get update && apt-get install -y docker-ce-cli

# Install Node.js (for MCP)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs

# Install Google Gemini CLI
RUN npm install -g @google/gemini-cli

# Install Hermes Agent
RUN curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Workspace
WORKDIR /workspace

# Copy and set entrypoint
# COPY entrypoint.sh /usr/local/bin/
# RUN chmod +x /usr/local/bin/entrypoint.sh

# ENTRYPOINT ["entrypoint.sh"]

# Keep container alive
CMD ["bash"]
