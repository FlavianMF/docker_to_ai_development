# Architecture - Hermes-Lazy-Gate (HLG)

## 1. Componentes
- **Core (Python)**: CLI principal que gerencia o ciclo de vida dos containers.
- **Namespacing**: Uso de `COMPOSE_PROJECT_NAME` para isolar ambientes.
- **Shared Knowledge**: O Vault do Obsidian é montado em Read-Only (ou RW) em todos os containers.
- **Isolated Workspace**: Cada container tem sua própria pasta em `workspace/`.

## 2. Fluxo de Operação
1. O usuário executa `hlg spawn <environment-name>`.
2. O HLG cria uma nova pasta de projeto isolada (se não existir) e gera um `docker-compose.yml` único usando um namespace (Project Name) exclusivo.
3. O HLG monta o Vault Global (`/knowledge`) e o workspace local do projeto.
4. O container sobe com o agente pronto para agir apenas naquele escopo.
5. O status da instância é registrado no Obsidian.

## 3. Modelo de Isolamento
Cada ambiente é tratado como uma unidade de trabalho independente:
- **Rede**: Isolada por padrão, com portas dinâmicas para evitar colisões (ex: porta 8080 para projeto A, 8081 para projeto B).
- **Volumes**: Workspace local exclusivo + Vault compartilhado.
- **Lifecycle**: `hlg list` mostra todos os ambientes ativos; `hlg kill <env>` remove a instância sem afetar as outras.

## 4. Integração com Gemini CLI
O HLG servirá como uma ferramenta (Skill) para o Gemini CLI, permitindo que ele gerencie sua própria infraestrutura.

## 5. Otimizações de Performance e UX (Update 2026-05-25)
- **Image Singleton**: Todas as instâncias herdam de uma única imagem base (`hermes-agent:latest`), eliminando builds redundantes e economizando espaço em disco.
- **Resource Monitoring**: Integração nativa com `docker stats` para visualização de CPU/MEM/NET por container.
- **Sequential Spawn**: Fluxo de criação unificado via [[EnvConfigModal]] para maior controle (Nome -> Caminho -> Portas).
- **Dynamic Port Allocation**: Suporte a seleção manual de portas OAuth e Ollama por instância, com fallback para busca automática de portas livres no host.
- **Visual Navigation**: Integração com `Yazi` (`Ctrl+O`) e Autocomplete (`TAB`) para seleção cirúrgica de diretórios de workspace.
