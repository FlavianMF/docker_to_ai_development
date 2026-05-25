# Engineering Notes - Hermes Docker

## Log de Aprendizados e Traps

### 2026-05-25: Inicialização do Padrão Agêntico
- **Problema**: O projeto carecia de documentação estruturada para persistência de memória agêntica entre sessões.
- **Solução**: Implementado o [[Padrão de Documentação Agêntica Local]].
- **Trap**: Bind mounts no Windows (via WSL2) podem ter latência em volumes grandes do Obsidian. Monitorar performance de I/O.

## Decisões Recorrentes
- Sempre usar `git checkout -b` para novas features, seguindo a [[Skill - Fluxo de Trabalho de Feature Branch]].
