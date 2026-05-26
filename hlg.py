#!/usr/bin/env python3
import os
import subprocess
import json
import socket
import glob
import tempfile
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListItem, ListView, Label, Input, TabbedContent, TabPane, DataTable, Button
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.binding import Binding
from textual import on

# Configurações Base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_BASE = os.path.join(BASE_DIR, "workspace")
VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "/mnt/c/Users/saoflfer/Documents/obsidian/flv_fit_vault")
STATE_FILE = os.path.join(BASE_DIR, ".hlg_state.json")

class ResourceManager:
    """Gerenciador de recursos Docker (Containers e Imagens)."""
    @staticmethod
    def get_containers(all=False):
        try:
            cmd = ["docker", "ps", "-a", "--format", "{{json .}}"]
            if not all:
                cmd += ["--filter", "name=hlg_"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [json.loads(line) for line in result.stdout.splitlines() if line]
        except:
            return []

    @staticmethod
    def get_images(all=False):
        try:
            cmd = ["docker", "images", "--format", "{{json .}}"]
            if not all:
                cmd += ["--filter", "reference=hermes_docker*"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [json.loads(line) for line in result.stdout.splitlines() if line]
        except:
            return []

    @staticmethod
    def get_container_stats():
        """Retorna estatísticas de uso de recursos dos containers ativos."""
        try:
            cmd = ["docker", "stats", "--no-stream", "--format", "{{json .}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            stats = {}
            for line in result.stdout.splitlines():
                if line:
                    data = json.loads(line)
                    # Usar Name ou ID como chave
                    stats[data.get("Name", data.get("ID"))] = data
            return stats
        except:
            return {}

    @staticmethod
    def get_disk_usage():
        try:
            cmd = ["docker", "system", "df", "--format", "{{json .}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            # Retorna apenas o primeiro (resumo)
            for line in result.stdout.splitlines():
                if line: return json.loads(line)
        except:
            return {}

    @staticmethod
    def stop_container(name_or_id):
        try:
            subprocess.run(["docker", "stop", name_or_id], check=True)
            return True
        except:
            return False

    @staticmethod
    def prune():
        try:
            subprocess.run(["docker", "container", "prune", "-f"], check=True)
            subprocess.run(["docker", "image", "prune", "-f"], check=True)
            return True
        except:
            return False

class EnvConfigModal(Screen):
    """Modal unificado para configuração de ambiente (Nome, Path, Portas Dinâmicas)."""
    def __init__(self, name="", path="", oauth_port="", ollama_port="", extra_ports=None, is_update=False):
        super().__init__()
        self.env_name = name
        self.env_path = path if path else (os.path.join(WORKSPACE_BASE, name) if name else WORKSPACE_BASE)
        self.oauth_port = str(oauth_port) if oauth_port else ""
        self.ollama_port = str(ollama_port) if ollama_port else ""
        self.extra_ports = extra_ports if extra_ports else []
        self.is_update = is_update

    def compose(self) -> ComposeResult:
        with Vertical(id="modal_container"):
            yield Label(f"[bold]{'Configurar' if self.is_update else 'Novo'} Ambiente[/bold]", id="modal_title")
            
            yield Label("Nome:", classes="field_label")
            yield Input(value=self.env_name, placeholder="projeto-alpha", id="env_name", disabled=self.is_update)
            
            yield Label("Caminho:", classes="field_label")
            yield Input(value=self.env_path, placeholder="Caminho do projeto", id="env_path")
            yield Label("[dim]TAB: Autocomplete | Ctrl+O: Yazi | Enter: Próximo[/dim]", classes="help_text")
            
            with Horizontal(id="port_container"):
                with Vertical():
                    yield Label("Porta OAuth:", classes="field_label")
                    yield Input(value=self.oauth_port, placeholder="Auto (8080+)", id="oauth_port")
                with Vertical():
                    yield Label("Porta Ollama:", classes="field_label")
                    yield Input(value=self.ollama_port, placeholder="Auto (11434+)", id="ollama_port")
            yield Label("[dim]Deixe em branco para auto-seleção[/dim]", classes="help_text")

            yield Label("[bold]Mapeamento de Portas Extras (Host:Container)[/bold]", id="extra_ports_title")
            with ScrollableContainer(id="extra_ports_list"):
                for i, port in enumerate(self.extra_ports):
                    yield self._create_port_row(i, port.get("host"), port.get("container"))
            
            yield Button("＋ Adicionar Porta", id="add_port", variant="default")

            yield Label("[dim]Enter: Navegar | Ctrl+S: Salvar | ESC: Cancelar[/dim]", id="global_help")
            
            with Horizontal(id="button_container"):
                yield Button("Cancelar", variant="error", id="cancel")
                yield Button("Salvar", variant="primary", id="save")

    def _create_port_row(self, index, host="", container=""):
        row_id = f"port_row_{index}"
        return Horizontal(
            Input(value=str(host), placeholder="Host", classes="port_input host_port"),
            Label(":"),
            Input(value=str(container), placeholder="Cont.", classes="port_input container_port"),
            Button("🗑", classes="remove_port", variant="error"),
            id=row_id,
            classes="extra_port_row"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            self._submit()
        elif event.button.id == "add_port":
            container = self.query_one("#extra_ports_list")
            new_index = len(container.children)
            container.mount(self._create_port_row(new_index))
            # Foca no novo input de host
            container.children[-1].query_one(".host_port").focus()
        elif "remove_port" in event.button.classes:
            event.button.parent.remove()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Navegação via ENTER: move foco para o próximo widget."""
        self.focus_next()

    def _submit(self):
        name = self.query_one("#env_name", Input).value.strip()
        path = self.query_one("#env_path", Input).value.strip()
        oauth = self.query_one("#oauth_port", Input).value.strip()
        ollama = self.query_one("#ollama_port", Input).value.strip()
        
        extra_ports = []
        for row in self.query(".extra_port_row"):
            h = row.query_one(".host_port", Input).value.strip()
            c = row.query_one(".container_port", Input).value.strip()
            if h and c:
                extra_ports.append({"host": h, "container": c})
        
        if not name:
            self.app.notify("Nome é obrigatório", severity="error")
            return
        
        self.dismiss({
            "name": name,
            "path": path,
            "oauth_port": oauth,
            "ollama_port": ollama,
            "extra_ports": extra_ports
        })

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "ctrl+s":
            self._submit()
            event.prevent_default()
            event.stop()
        elif event.key == "tab":
            if self.focused and self.focused.id == "env_path":
                self._handle_autocomplete()
                event.prevent_default()
                event.stop()
        elif event.key == "ctrl+o":
            if self.focused and self.focused.id == "env_path":
                self._handle_yazi()
                event.prevent_default()
                event.stop()

    def _handle_yazi(self):
        """Lança o Yazi para selecionar um diretório."""
        input_widget = self.query_one("#env_path", Input)
        current_val = input_widget.value or WORKSPACE_BASE
        
        start_dir = current_val if os.path.isdir(current_val) else os.path.dirname(current_val)
        if not os.path.exists(start_dir):
            start_dir = WORKSPACE_BASE

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            cmd = ["yazi", start_dir, f"--chooser-file={tmp_path}"]
            with self.app.suspend():
                subprocess.run(cmd)
            
            if os.path.exists(tmp_path):
                with open(tmp_path, "r") as f:
                    selected = f.read().strip()
                    if selected:
                        input_widget.value = selected
                        input_widget.cursor_position = len(selected)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _handle_autocomplete(self):
        input_widget = self.query_one("#env_path", Input)
        current = input_widget.value
        if not current:
            return
        
        path = os.path.expanduser(current)
        matches = glob.glob(path + "*")
        
        if not matches:
            return
            
        if len(matches) == 1:
            match = matches[0]
            if os.path.isdir(match) and not match.endswith("/"):
                match += "/"
            input_widget.value = match
            input_widget.cursor_position = len(match)
        else:
            common = os.path.commonprefix(matches)
            if common:
                input_widget.value = common
                input_widget.cursor_position = len(common)

class HLGApp(App):
    CSS = """
    #main_container {
        layout: horizontal;
    }
    #sidebar {
        width: 30%;
        border-right: heavy gray;
        background: $panel;
    }
    #content {
        width: 70%;
        padding: 1;
    }
    .env_item {
        padding: 1;
    }
    #modal_container {
        width: 65;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }
    #modal_title {
        text-align: center;
        margin-bottom: 1;
    }
    .field_label {
        margin-top: 1;
        text-style: bold;
    }
    .help_text {
        color: $text-disabled;
        text-style: italic;
        margin-bottom: 1;
    }
    #port_container {
        height: 5;
        margin-top: 1;
    }
    #port_container Vertical {
        width: 50%;
        padding: 0 1;
    }
    #extra_ports_title {
        margin-top: 2;
        border-bottom: solid $primary;
    }
    #extra_ports_list {
        height: 8;
        border: solid $panel;
        margin-top: 1;
        padding: 1;
    }
    .extra_port_row {
        height: 3;
        margin-bottom: 1;
    }
    .port_input {
        width: 35%;
    }
    .remove_port {
        width: 10%;
        margin-left: 1;
    }
    #add_port {
        margin-top: 1;
        width: 100%;
    }
    #global_help {
        text-align: center;
        margin-top: 1;
        color: $accent;
    }
    #button_container {
        height: 3;
        align: center middle;
        margin-top: 2;
    }
    #button_container Button {
        margin: 0 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Sair", show=True),
        Binding("a", "add_env", "Spawn", show=True),
        Binding("u", "edit_env", "Config", show=True),
        Binding("d", "delete_env", "Kill", show=True),
        Binding("s", "stop_env", "Stop", show=True),
        Binding("e", "shell_env", "Shell", show=True),
        Binding("r", "refresh", "Atualizar", show=True),
        Binding("p", "prune", "Prune", show=True),
        Binding("v", "toggle_view", "Alternar Tudo/HLG", show=True),
        Binding("tab", "switch_focus", "Tab: Entrar/Sair", show=True),
        Binding("h", "help", "Ajuda", show=True),
    ]

    def action_help(self) -> None:
        """Exibe modal com instruções de uso."""
        help_text = """
    [bold cyan]COMANDOS DO HLG[/bold cyan]

    [bold yellow]Navegação Geral:[/bold yellow]
    - [bold]TAB[/bold]: Alterna foco entre Menu e Conteúdo
    - [bold]v[/bold]: Alterna visualização de recursos (Apenas HLG ou Sistema Todo)
    - [bold]r[/bold]: Atualiza dados da tela

    [bold yellow]Gerenciamento de Ambientes:[/bold yellow]
    - [bold]a[/bold]: [Spawn] Cria novo ambiente de agente
    - [bold]u[/bold]: [Config] Edita ambiente (Caminho, Portas, Portas Extras)
    - [bold]d[/bold]: [Kill] Remove ambiente e apaga containers
    - [bold]s[/bold]: [Stop] Para os containers do ambiente
    - [bold]e[/bold]: [Shell] Entra no terminal do container (Bash)

    [bold yellow]Configuração (Modal):[/bold yellow]
    - [bold]Enter[/bold]: Pula para o próximo campo
    - [bold]TAB[/bold]: Autocomplete de caminhos (no campo Caminho)
    - [bold]Ctrl+O[/bold]: Abre seletor de pastas Yazi (no campo Caminho)
    - [bold]Ctrl+S[/bold]: Salva as configurações
    - [bold]ESC[/bold]: Cancela e fecha o modal

    [bold yellow]Limpeza:[/bold yellow]
    - [bold]p[/bold]: [Prune] Remove containers e imagens órfãs do sistema
        """
        self.push_screen(Screen(id="help_screen"), lambda _: None)
        self.query_one("#help_screen").mount(
            Vertical(
                Static(help_text),
                Button("Fechar", variant="primary", id="close_help"),
                id="modal_container"
            )
        )

    @on(Button.Pressed, "#close_help")
    def on_close_help(self) -> None:
        self.pop_screen()

    def __init__(self):
        super().__init__()
        self.state = self._load_state()
        self.resource_manager = ResourceManager()
        self.show_all_resources = False

    def action_switch_focus(self) -> None:
        """Alterna o foco entre a barra de abas e o conteúdo."""
        tabs = self.query_one(TabbedContent)
        if self.focused == tabs:
            self._focus_active_content()
        else:
            tabs.focus()

    def _focus_active_content(self) -> None:
        tabs = self.query_one(TabbedContent)
        active_pane = tabs.get_pane(tabs.active)
        if active_pane.id == "ambientes_pane":
            self.query_one("#env_list").focus()
        elif active_pane.id == "containers_pane":
            self.query_one("#container_table").focus()
        elif active_pane.id == "imagens_pane":
            self.query_one("#image_table").focus()

    def _load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"environments": {}}

    def _save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=4)

    def _get_free_port(self, start=8080):
        port = start
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0:
                    return port
            port += 1

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Ambientes", id="ambientes_pane"):
                yield Container(
                    Vertical(
                        Label("[bold]AMBIENTES[/bold]", id="sidebar_title"),
                        ListView(id="env_list"),
                        id="sidebar"
                    ),
                    Vertical(
                        Static("Selecione um ambiente para ver detalhes", id="env_details"),
                        id="content"
                    ),
                    id="main_container"
                )
            with TabPane("Containers", id="containers_pane"):
                yield DataTable(id="container_table")
            with TabPane("Imagens", id="imagens_pane"):
                yield DataTable(id="image_table")
            with TabPane("Recursos", id="recursos_pane"):
                yield Vertical(
                    Static("Resumo de Uso de Disco", id="resource_title"),
                    Static(id="disk_usage_details"),
                    id="resource_container"
                )
        yield Footer()

    def on_mount(self) -> None:
        self.update_env_list()
        self.update_docker_views()
        self.query_one(TabbedContent).focus()

    @on(TabbedContent.TabActivated)
    def on_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Mantém o foco na barra de abas ao trocar lateralmente."""
        self.query_one(TabbedContent).focus()

    def action_toggle_view(self) -> None:
        """Alterna entre mostrar apenas recursos HLG ou todos os recursos do sistema."""
        self.show_all_resources = not self.show_all_resources
        mode = "TUDO" if self.show_all_resources else "HLG-ONLY"
        self.notify(f"Modo de visualização: {mode}")
        self.update_docker_views()

    def update_docker_views(self):
        # Update Container Table
        try:
            c_table = self.query_one("#container_table")
            c_table.clear(columns=True)
            c_table.add_columns("ID", "NOME", "STATUS", "CPU %", "MEM", "NET I/O")
            c_table.cursor_type = "row"
            
            containers = self.resource_manager.get_containers(all=self.show_all_resources)
            stats = self.resource_manager.get_container_stats()
            
            for c in containers:
                name = c.get("Names", "")
                # Tenta buscar stats pelo nome ou ID
                s = stats.get(name, stats.get(c.get("ID", "")))
                
                cpu = s.get("CPUPerc", "N/A") if s else "N/A"
                mem = s.get("MemUsage", "N/A") if s else "N/A"
                net = s.get("NetIO", "N/A") if s else "N/A"
                
                # Destaca containers HLG se estiver no modo "Tudo"
                display_name = name
                if self.show_all_resources and name.startswith("hlg_"):
                    display_name = f"[bold green]{name}[/bold green]"
                elif self.show_all_resources and name.startswith("hermes_"):
                    display_name = f"[bold cyan]{name}[/bold cyan]"

                c_table.add_row(
                    c.get("ID", ""), 
                    display_name, 
                    c.get("Status", ""),
                    cpu,
                    mem,
                    net
                )
        except Exception as e:
            if "PYTEST_CURRENT_TEST" not in os.environ:
                pass
            else:
                raise e

        # Update Image Table
        try:
            i_table = self.query_one("#image_table")
            i_table.clear(columns=True)
            i_table.add_columns("ID", "REPOSITÓRIO", "TAG", "TAMANHO")
            i_table.cursor_type = "row"
            images = self.resource_manager.get_images(all=self.show_all_resources)
            for i in images:
                repo = i.get("Repository", "")
                display_repo = repo
                if self.show_all_resources and (repo.startswith("hermes_") or "hermes" in repo):
                    display_repo = f"[bold cyan]{repo}[/bold cyan]"
                
                i_table.add_row(i.get("ID", ""), display_repo, i.get("Tag", ""), i.get("Size", ""))
        except Exception as e:
            if "PYTEST_CURRENT_TEST" not in os.environ:
                pass
            else:
                raise e

        # Update Disk Usage
        try:
            usage = self.resource_manager.get_disk_usage()
            if usage:
                details = f"""
[bold]Tipo[/bold] | [bold]Total[/bold] | [bold]Ativos[/bold] | [bold]Tamanho[/bold] | [bold]Reclamável[/bold]
Containers: {usage.get('Containers', '')}
Imagens: {usage.get('Images', '')}
Volumes: {usage.get('Volumes', '')}
                """
                details_widget = self.query_one("#disk_usage_details")
                details_widget.update(details)
        except Exception as e:
            if "PYTEST_CURRENT_TEST" not in os.environ:
                pass
            else:
                raise e

    def update_env_list(self):
        list_view = self.query_one("#env_list", ListView)
        list_view.clear()
        for name in self.state["environments"].keys():
            list_view.append(ListItem(Label(f"● {name}"), name=name))

    def action_add_env(self) -> None:
        def handle_config(config: dict | None) -> None:
            if config:
                self.spawn_logic(
                    config["name"], 
                    config["path"], 
                    config["oauth_port"], 
                    config["ollama_port"],
                    config["extra_ports"]
                )
        self.push_screen(EnvConfigModal(), handle_config)

    def action_edit_env(self) -> None:
        """Abre modal para atualizar a configuração de um ambiente existente."""
        list_view = self.query_one("#env_list", ListView)
        if list_view.index is not None:
            item = list_view.children[list_view.index]
            name = item.name
            env = self.state["environments"][name]
            
            def handle_config(config: dict | None) -> None:
                if config:
                    self.spawn_logic(
                        name, 
                        config["path"], 
                        config["oauth_port"], 
                        config["ollama_port"],
                        config["extra_ports"]
                    )
            
            self.push_screen(
                EnvConfigModal(
                    name=name, 
                    path=env["path"], 
                    oauth_port=env["oauth_port"], 
                    ollama_port=env["ollama_port"],
                    extra_ports=env.get("extra_ports", []),
                    is_update=True
                ), 
                handle_config
            )

    def action_stop_env(self) -> None:
        """Pausa o container do ambiente selecionado."""
        list_view = self.query_one("#env_list", ListView)
        if list_view.index is not None:
            item = list_view.children[list_view.index]
            name = item.name
            if self.resource_manager.stop_container(f"hermes_{name}"):
                self.notify(f"Ambiente '{name}' parado.")
                self.update_docker_views()
            else:
                self.notify(f"Erro ao parar '{name}'.", severity="error")

    def action_shell_env(self) -> None:
        """Abre o shell do container (Bash) em uma nova aba do TMUX ou direto no terminal."""
        list_view = self.query_one("#env_list", ListView)
        if list_view.index is not None:
            item = list_view.children[list_view.index]
            name = item.name
            container_name = f"hermes_{name}"
            
            # Verifica se está no TMUX
            if "TMUX" in os.environ:
                bash_cmd = f"docker exec -it {container_name} /bin/bash"
                try:
                    # Cria nova janela no tmux e roda o comando
                    subprocess.run(["tmux", "new-window", "-n", f"shell-{name}", bash_cmd], check=True)
                    self.notify(f"Shell aberto para '{name}' no TMUX.")
                except Exception as e:
                    self.notify(f"Erro TMUX: {e}", severity="error")
            else:
                # Fallback: Entra direto no docker suspendendo a TUI temporariamente
                self.notify("Entrando no container... (Saindo da TUI)")
                with self.suspend():
                    subprocess.run(["docker", "exec", "-it", container_name, "/bin/bash"])

    def spawn_logic(self, name: str, custom_path: str | None = None, oauth_port: str = "", ollama_port: str = "", extra_ports: list = None):
        project_path = custom_path if custom_path else os.path.join(WORKSPACE_BASE, name)
        gemini_data = os.path.join(project_path, ".gemini_data")
        ollama_data = os.path.join(project_path, ".ollama_data")
        extra_ports = extra_ports if extra_ports else []
        
        for p in [project_path, gemini_data, ollama_data]:
            os.makedirs(p, exist_ok=True)

        # Lógica de Portas: Manual ou Auto-discovery
        try:
            o_port = int(oauth_port) if oauth_port else self._get_free_port(8080)
            l_port = int(ollama_port) if ollama_port else self._get_free_port(11434)
        except ValueError:
            self.notify("Portas devem ser números válidos", severity="error")
            return

        # Gera docker-compose.override.yml com portas extras
        override_file = os.path.join(project_path, "docker-compose.override.yml")
        with open(override_file, "w") as f:
            f.write("services:\n  hermes:\n    ports:\n")
            for p in extra_ports:
                f.write(f"      - \"{p['host']}:{p['container']}\"\n")

        env_vars = {
            **os.environ,
            "COMPOSE_PROJECT_NAME": f"hlg_{name}",
            "HERMES_CONTAINER_NAME": f"hermes_{name}",
            "OLLAMA_CONTAINER_NAME": f"ollama_{name}",
            "WORKSPACE_PATH": project_path,
            "GEMINI_DATA_PATH": gemini_data,
            "OLLAMA_DATA_VOLUME": ollama_data,
            "OAUTH_PORT": str(o_port),
            "OLLAMA_PORT": str(l_port),
            "OBSIDIAN_VAULT_PATH": VAULT_PATH
        }

        try:
            cmd = [
                "docker", "compose", 
                "-f", os.path.join(BASE_DIR, "docker-compose.yml"),
                "-f", override_file,
                "up", "-d"
            ]
            subprocess.run(cmd, env=env_vars, check=True, cwd=BASE_DIR)
            self.state["environments"][name] = {
                "path": project_path,
                "oauth_port": o_port,
                "ollama_port": l_port,
                "extra_ports": extra_ports,
                "status": "active"
            }
            self._save_state()
            self.update_env_list()
            self.notify(f"Ambiente '{name}' configurado (OAuth: {o_port}).")
        except Exception as e:
            self.notify(f"Erro: {e}", severity="error")

    def action_delete_env(self) -> None:
        list_view = self.query_one("#env_list", ListView)
        if list_view.index is not None:
            item = list_view.children[list_view.index]
            name = item.name
            self.kill_logic(name)

    def kill_logic(self, name: str):
        env = self.state["environments"].get(name, {})
        project_path = env.get("path", BASE_DIR)
        override_file = os.path.join(project_path, "docker-compose.override.yml")
        
        env_vars = {**os.environ, "COMPOSE_PROJECT_NAME": f"hlg_{name}"}
        try:
            cmd = ["docker", "compose", "-f", os.path.join(BASE_DIR, "docker-compose.yml")]
            if os.path.exists(override_file):
                cmd += ["-f", override_file]
            cmd += ["down"]
            
            subprocess.run(cmd, env=env_vars, cwd=BASE_DIR)
            del self.state["environments"][name]
            self._save_state()
            self.update_env_list()
            self.notify(f"Ambiente '{name}' removido.")
        except Exception as e:
            self.notify(f"Erro ao encerrar: {e}", severity="error")

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item:
            name = event.item.name
            data = self.state["environments"][name]
            
            # Formata portas extras
            extra_ports_list = data.get("extra_ports", [])
            extra_ports_str = ""
            if extra_ports_list:
                extra_ports_str = "\n[bold blue]Portas Extras:[/bold blue]"
                for p in extra_ports_list:
                    extra_ports_str += f"\n  - {p['host']} -> {p['container']}"

            details = f"""
[bold cyan]Ambiente:[/bold cyan] {name}
[bold green]Status:[/bold green] RUNNING
[bold blue]OAuth Port:[/bold blue] {data['oauth_port']}
[bold blue]Ollama Port:[/bold blue] {data['ollama_port']}{extra_ports_str}
[bold gray]Workspace:[/bold gray] {data['path']}

[yellow]Atalhos:[/yellow]
'd' - Encerrar este ambiente
'a' - Criar novo ambiente
'u' - Configurar (Portas/Path)
'q' - Sair
            """
            self.query_one("#env_details", Static).update(details)

    def action_refresh(self) -> None:
        self.state = self._load_state()
        self.update_env_list()
        self.update_docker_views()
        self.notify("Dados atualizados!")

    def action_prune(self) -> None:
        if self.resource_manager.prune():
            self.update_docker_views()
            self.notify("Limpeza (Prune) concluída com sucesso!")
        else:
            self.notify("Falha ao executar limpeza.", severity="error")

if __name__ == "__main__":
    app = HLGApp()
    app.run()
