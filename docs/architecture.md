# Architecture Decision Log (ADR) - Hermes Docker

## Stack Tecnológica
- **Orquestração**: `docker-compose` com variáveis de ambiente dinâmicas.
- **Base Image**: Custom `Dockerfile` com [[Gemini CLI]] e dependências de runtime.
- **Rede**: Bridge network com exposição de porta OAuth (8080 default).
- **Storage**: Bind mounts para `/knowledge` (Vault) e volumes para persistência.

## Decisões de Design
1. **Vault Mount**: Decidido montar o Vault em modo leitura/escrita para permitir que agentes atuem como [[Skill - Graph-Gardener|Graph-Gardeners]].
2. **Dynamic Naming**: Uso de prefixos para evitar colisões em ambientes de [[Orquestração Híbrida de Agentes]].
3. **DooD**: Implementado para permitir que o agente gerencie outros containers de ferramentas.
