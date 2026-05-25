# PRD - Hermes-Lazy-Gate (HLG)

## 1. Visão Geral
O **Hermes-Lazy-Gate (HLG)** é um orquestrador de containers "Agent-First" inspirado no `lazygit`. Ele fornece uma interface (CLI/TUI/API) para gerenciar ambientes de desenvolvimento agênticos, focando em persistência de estado, rastreabilidade de ferramentas e integração profunda com o Vault do Obsidian.

## 2. Objetivos
- **Isolamento Multitenant**: Subir múltiplos ambientes de desenvolvimento (containers) totalmente isolados para diferentes projetos ou tarefas, evitando conflitos de dependências entre agentes.
- **Eficiência**: Permitir que agentes e humanos controlem containers com comandos de alto nível (ex: `hlg create project-alpha --template python`).
- **Contexto Otimizado**: Expor para o agente exatamente o que está instalado e onde estão os volumes, via arquivos de metadados auto-gerados.
- **Sincronização**: Manter o status dos containers refletido no Vault Global do Obsidian.

## 3. Requisitos Funcionais (HLG-F)
1. **Dynamic Instantiation**: Criar, destruir e pausar instâncias de desenvolvimento rapidamente via comandos simples.
2. **Environment Isolation**: Cada instância possui seu próprio workspace e runtime, mas compartilha o acesso (ReadOnly ou RW) ao Vault de Conhecimento.
3. **Template Engine**: Blueprints para diferentes tipos de desenvolvimento (Web, Data Science, System Eng).
4. **Tool-Registry**: Registro de "Toolchains" (ex: Node, Python, Rust, Ruby) que podem ser injetadas dinamicamente.
5. **Path-Manager**: Mapeamento dinâmico de volumes entre Host e Containers específicos.

## 4. Requisitos Não-Funcionais
1. **Interface**: CLI rápida para agentes; TUI para humanos (estilo `lazydocker` / `lazygit`).
2. **Performance**: Uso de imagens base otimizadas (Alpine/Debian-Slim).
3. **Extensibilidade**: Plugins para novos backends (K8s local, Podman).

## 5. User Stories
- **Como Flavian**: Quero ver todos os meus ambientes de agentes ativos em uma única tela e saber quais ferramentas estão em cada um.
- **Como Agente**: Quero consultar o HLG para saber se tenho permissão de rodar `npm install` ou se devo solicitar a criação de um novo container.

---
*Status: Draft (Fase A)*
