# Product Requirements Document (PRD) - Hermes Docker

## Visão Geral
O [[hermes-docker]] é uma infraestrutura de [[Ambiente de Desenvolvimento de Agentes em Containers|agentes em containers]] otimizada para o [[Método Karpathy]]. Ele permite a execução de instâncias isoladas do [[Gemini CLI]] com acesso direto ao conhecimento do [[Flavian Fernandes]].

## Requisitos Funcionais
1. **Multi-Instância**: Suporte a múltiplos containers via `COMPOSE_PROJECT_NAME`.
2. **Acesso ao Vault**: Montagem do Obsidian Vault em `/knowledge`.
3. **Persistência**: Volumes Docker para dados do Gemini CLI e histórico.
4. **Segurança**: Configuração de [[Fluxo de Autenticação OAuth em Containers|OAuth]] e portas dinâmicas.

## Requisitos Não-Funcionais
1. **Performance**: [[Otimização de Recursos para LLMs em CPU|Otimização de CPU/RAM]].
2. **Isolamento**: Uso de [[Docker-out-of-Docker (DooD)]] onde aplicável.
3. **Rastreabilidade**: Documentação [[densos|densamente linkada]].
