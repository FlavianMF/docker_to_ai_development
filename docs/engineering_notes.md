# Engineering Notes - Hermes Docker

## Log de Aprendizados e Traps

### 2026-05-25: Inicialização do Padrão Agêntico
- **Problema**: O projeto carecia de documentação estruturada para persistência de memória agêntica entre sessões.
- **Solução**: Implementado o [[Padrão de Documentação Agêntica Local]].
- **Trap**: Bind mounts no Windows (via WSL2) podem ter latência em volumes grandes do Obsidian. Monitorar performance de I/O.

### 2026-05-25: Suíte de Testes e Correções no HLG
- **Problema**: O `hlg.py` tinha um bug na chamada do `subprocess.run` (docker compose) e caminhos de Vault hardcoded.
- **Solução**: 
    - Corrigido o comando `docker compose` para ser passado como lista de argumentos individuais.
    - Tornado o `VAULT_PATH` configurável via variável de ambiente `OBSIDIAN_VAULT_PATH`.
    - Implementada suíte de testes unitários com 7 casos cobrindo o core logic (Spawn, Kill, State, Ports).
- **Trap**: Testar aplicações TUI (Textual) requer mockar o `App` base para evitar que o loop de eventos bloqueie os testes unitários.

### 2026-05-25: Integração Docker TUI e Estatísticas de Recursos
- **Problema**: A TUI do HLG mostrava apenas containers com prefixo `hlg_` e não exibia consumo de recursos (CPU/MEM).
- **Solução**: 
    - Implementada integração com `docker stats` no `ResourceManager`.
    - Adicionada coluna de CPU %, MEM e NET I/O na `DataTable` de containers.
    - Implementado toggle de visualização ('v') para alternar entre "HLG-Only" e "Tudo" (All system resources).
    - Expandida a suíte de testes de 7 para 17 casos, validando a filtragem e o merge de dados de estatísticas.
- **Trap**: `docker stats --no-stream` pode ser lento em sistemas com muitos containers ativos. O merge de dados é feito via Name/ID para garantir precisão.

## Decisões Recorrentes
- Sempre usar `git checkout -b` para novas features, seguindo a [[Skill - Fluxo de Trabalho de Feature Branch]].
