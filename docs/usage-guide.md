# Usage Guide

## Gemini CLI & Hermes
Both tools are pre-installed.
- **Hermes**: `hermes`
- **Gemini CLI**: `gemini`

## HLG TUI (Hermes-Lazy-Gate)
O comando `python3 hlg.py` lança uma interface interativa (TUI) para gerenciar instâncias.

### Atalhos Principais
- `a`: **Spawn** - Cria um novo ambiente.
- `u`: **Config** - Atualiza o caminho ou as portas de um ambiente existente.
- `d`: **Kill** - Remove o ambiente e os containers associados.
- `s`: **Stop** - Para o container sem remover.
- `e`: **Shell** - Abre um terminal dentro do container (suporta TMUX).
- `p`: **Prune** - Limpa containers e imagens órfãs.
- `h`: **Ajuda** - Abre o guia de comandos interativo.

### Configuração de Portas
Ao criar ou editar um ambiente, você pode definir as portas:
- **Porta OAuth**: Usada para autenticação do [[Gemini CLI]]. (Padrão: 8080+)
- **Porta Ollama**: Usada para comunicação com o modelo local. (Padrão: 11434+)
- **Mapeamento de Portas Extras**: Permite adicionar múltiplos pares `Host:Container` para serviços customizados.

#### Dicas de Navegação (Modal)
- **Enter**: Salta para o próximo campo do formulário.
- **TAB**: Utilizado apenas para **Autocomplete** no campo de Caminho.
- **Ctrl+S**: Salva as alterações de qualquer lugar do modal.
- **Ctrl+O**: Abre o seletor visual de arquivos `Yazi`.

## Persistence
- **Workspace**: Mapped via `WORKSPACE_PATH`.
- **Global Knowledge**: Your Obsidian vault is mounted at `/knowledge` inside the container.
- **Gemini Config**: Persisted in `gemini_data` volume across all instances.
- **Ollama**: Shared across instances via the internal network.
