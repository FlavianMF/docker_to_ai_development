# Docker-in-Docker (DooD) Setup

## Goal
Allow Hermes Agent to spawn and manage containers for sandboxed tool execution.

## Implementation
- **Docker CLI**: Installed in container.
- **Socket Mounting**: Map host `/var/run/docker.sock` to container.

## Why DooD not DinD
"Docker-out-of-Docker" (DooD) uses host engine. Faster, less overhead, shares images with host.

## Usage in Hermes
In `hermes setup`, select `Docker` as terminal backend. Agent will use the mounted socket to create sandboxes.
