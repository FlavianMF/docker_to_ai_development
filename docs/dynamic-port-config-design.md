# Design Doc - Dynamic Port Configuration

## 1. Contexto & Motivação
O [[hermes-docker]] permite rodar múltiplas instâncias agênticas. Atualmente, o [[HLG]] (Hermes Launch Group) seleciona portas automaticamente a partir da 8080 (OAuth) e 11434 (Ollama). No entanto, usuários avançados precisam de controle granular sobre quais portas são expostas para evitar conflitos com outros serviços locais ou para seguir padrões de rede específicos.

## 2. Escopo
- **Manual Port Selection**: Permitir que o usuário digite as portas desejadas durante o spawn de um novo ambiente.
- **Extra Ports Support**: Adição dinâmica de múltiplos mapeamentos `Host:Container`.
- **Dynamic Updates**: Permitir a alteração das portas de um ambiente existente (requer restart do container).
- **UX Optimization**: Navegação entre campos via `Enter` e salvamento via `Ctrl+S`, mantendo `TAB` para autocomplete.

## 3. Arquitetura Proposta

### 3.1 Interface do Usuário (TUI)
- **Unified Modal**: Substituir o fluxo de múltiplos modais por um único `EnvConfigModal` com seção de portas rolável.

### 3.2 Orquestração (`ResourceManager` & `spawn_logic`)
- **Docker Override**: Uso de arquivos `docker-compose.override.yml` por instância para injetar portas extras sem modificar a base.
- **Port Discovery**: Fallback automático para portas livres se os campos forem deixados em branco.

### 3.3 Persistência
- O arquivo [[.hlg_state.json]] armazena `oauth_port`, `ollama_port` e a lista `extra_ports`.

## 4. Estratégia de Verificação

### 4.1 Casos de Teste
- **TC-PORT-01**: Criar ambiente com portas manuais (ex: 9000 e 12000) e verificar se o `docker ps` reflete essas portas.
- **TC-PORT-02**: Tentar criar ambiente com porta já em uso e receber aviso/erro.
- **TC-PORT-03**: Atualizar porta de um ambiente ativo e verificar se o container é reiniciado com a nova porta.

## 5. Rastreabilidade
- Requisito originado em: [[PRD#Requisitos Funcionais]]
- Implementação: [[hlg.py]]
