# Design Doc - Dynamic Port Configuration

## 1. Contexto & Motivação
O [[hermes-docker]] permite rodar múltiplas instâncias agênticas. Atualmente, o [[HLG]] (Hermes Launch Group) seleciona portas automaticamente a partir da 8080 (OAuth) e 11434 (Ollama). No entanto, usuários avançados precisam de controle granular sobre quais portas são expostas para evitar conflitos com outros serviços locais ou para seguir padrões de rede específicos.

## 2. Escopo
- **Manual Port Selection**: Permitir que o usuário digite as portas desejadas durante o spawn de um novo ambiente.
- **Dynamic Updates**: Permitir a alteração das portas de um ambiente existente (requer restart do container).
- **Port Validation**: Verificar se a porta escolhida já está em uso no host antes de aplicar.

## 3. Arquitetura Proposta

### 3.1 Interface do Usuário (TUI)
- **Unified Modal**: Substituir o fluxo de múltiplos modais por um único `EnvConfigModal` contendo:
    - Nome do Ambiente
    - Caminho do Workspace
    - Porta OAuth (Padrão: Auto-selecionada)
    - Porta Ollama (Padrão: Auto-selecionada)

### 3.2 Lógica de Negócio (`HLGApp`)
- `spawn_logic`: Receberá os valores do modal. Se os campos de porta estiverem vazios, manterá a lógica de `_get_free_port`.
- `update_logic`: Nova ação para reconfigurar um ambiente existente, atualizando o arquivo `.hlg_state.json` e reiniciando os containers com as novas variáveis de ambiente.

### 3.3 Persistência
- O arquivo [[.hlg_state.json]] já armazena `oauth_port` e `ollama_port`. Nenhuma mudança de schema estrutural é necessária, apenas a exposição para edição.

## 4. Estratégia de Verificação

### 4.1 Casos de Teste
- **TC-PORT-01**: Criar ambiente com portas manuais (ex: 9000 e 12000) e verificar se o `docker ps` reflete essas portas.
- **TC-PORT-02**: Tentar criar ambiente com porta já em uso e receber aviso/erro.
- **TC-PORT-03**: Atualizar porta de um ambiente ativo e verificar se o container é reiniciado com a nova porta.

## 5. Rastreabilidade
- Requisito originado em: [[PRD#Requisitos Funcionais]]
- Implementação: [[hlg.py]]
