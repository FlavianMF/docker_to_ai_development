# Design Doc - HLG Resource Management & Visibility

## 1. Background & Motivation
O **Hermes-Lazy-Gate (HLG)** atualmente foca no spawn de novos ambientes, mas carece de visibilidade sobre o estado real dos recursos Docker subjacentes (containers órfãos, imagens acumuladas, uso de disco). Para operar como um orquestrador "Agent-First" eficiente, ele precisa gerenciar o ciclo de vida completo, incluindo a limpeza de recursos para evitar exaustão de disco no host.

## 2. Scope & Impact
### Funcionalidades Planejadas:
- **Global Visibility**: Listagem de todos os containers (Up/Exited) e Imagens (Used/Dangling).
- **Resource Monitoring**: Exibição do uso de disco por containers e volumes.
- **Garbage Collection**: Comandos para apagar containers parados e imagens sem uso.
- **Smart Pruning**: Sugestão de ambientes antigos (não acessados há X dias) para deleção.

## 3. Proposed Architecture

### 3.1 Data Flow
- **Discovery Layer**: Integração direta com a API do Docker (via `docker inspect` ou `docker stats`) para obter dados em tempo real, independente do arquivo `.hlg_state.json`.
- **Logic Layer**: Novo módulo `ResourceManager` responsável por filtrar e correlacionar containers com ambientes do HLG.
- **UI Layer (TUI)**:
    - **Tab 'Containers'**: Lista detalhada com Status, Portas e ID.
    - **Tab 'Images'**: Lista de imagens, Tags e Tamanho.
    - **Dash 'Resources'**: Resumo de uso de disco.

### 3.2 UI/UX Extensions (Textual)
- Implementação de um `TabbedContent` no `HLGApp`.
- Adição de `Binding` para atalhos de limpeza (ex: `p` para prune).

## 4. Cases de Teste (Strategy)

### 4.1 Testes de Visibilidade (Read-Only)
- **TC-VIS-01**: Validar listagem de containers retornando estados 'running' e 'exited' via mock do Docker CLI.
- **TC-VIS-02**: Validar correlação de imagens com containers ativos (não permitir apagar imagens em uso).
- **TC-VIS-03**: Verificar cálculo de tamanho total de disco (parsing do `docker system df`).

### 4.2 Testes de Gerenciamento de Recursos (Mutação)
- **TC-RES-01**: Simular `hlg prune` e verificar se containers parados são removidos do estado e do host.
- **TC-RES-02**: Validar remoção de imagens "dangling" (tag `<none>`).
- **TC-RES-03**: Testar proteção contra deleção de ambientes marcados como "Persistentes".

### 4.3 Testes de UX/TUI
- **TC-UI-01**: Verificar se a troca de tabs (`Environments` vs `Resources`) mantém o estado de seleção.
- **TC-UI-02**: Validar diálogos de confirmação (Modals) antes de ações destrutivas (`docker rm -f`).

## 5. Migration & Documentation
- Atualizar `HLG_architecture.md` com o novo `ResourceManager`.
- Atualizar `usage-guide.md` com os novos atalhos de limpeza.
- Plano de implementação detalhado em `resource-management-implementation.md`.
