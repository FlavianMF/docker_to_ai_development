#!/usr/bin/env python3
import os
import subprocess
import json
import socket
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListItem, ListView, Label, Input, TabbedContent, TabPane, DataTable
from textual.containers import Container, Horizontal, Vertical
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
    def get_containers():
        try:
            cmd = ["docker", "ps", "-a", "--filter", "name=hlg_", "--format", "{{json .}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [json.loads(line) for line in result.stdout.splitlines() if line]
        except:
            return []

    @staticmethod
    def get_images():
        try:
            cmd = ["docker", "images", "--filter", "reference=hermes_docker*", "--format", "{{json .}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [json.loads(line) for line in result.stdout.splitlines() if line]
        except:
            return []

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
    def prune():
        try:
            subprocess.run(["docker", "container", "prune", "-f"], check=True)
            subprocess.run(["docker", "image", "prune", "-f"], check=True)
            return True
        except:
            return False

class SpawnModal(Screen):
    """Modal para criar um novo ambiente."""
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Digite o nome do novo ambiente:"),
            Input(placeholder="projeto-alpha", id="env_name"),
            Label("Pressione ENTER para criar ou ESC para cancelar"),
            id="modal_container"
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)

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
        width: 40;
        height: 10;
        border: thick $primary;
        background: $surface;
        align: center middle;
        padding: 1;
        content-align: center middle;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Sair", show=True),
        Binding("a", "add_env", "Adicionar", show=True),
        Binding("d", "delete_env", "Deletar", show=True),
        Binding("r", "refresh", "Atualizar", show=True),
        Binding("p", "prune", "Prune", show=True),
        Binding("tab", "switch_focus", "Tab: Entrar/Sair", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.state = self._load_state()
        self.resource_manager = ResourceManager()

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

    def update_docker_views(self):
        # Update Container Table
        try:
            c_table = self.query_one("#container_table")
            # Salvar cursor atual se possível
            c_table.clear(columns=True)
            c_table.add_columns("ID", "NOME", "STATUS", "PORTAS")
            c_table.cursor_type = "row"
            containers = self.resource_manager.get_containers()
            for c in containers:
                c_table.add_row(c.get("ID", ""), c.get("Names", ""), c.get("Status", ""), c.get("Ports", ""))
        except Exception as e:
            # Em testes, query_one pode falhar se o app não estiver rodando
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
            images = self.resource_manager.get_images()
            for i in images:
                i_table.add_row(i.get("ID", ""), i.get("Repository", ""), i.get("Tag", ""), i.get("Size", ""))
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
        def check_name(name: str | None) -> None:
            if name:
                self.spawn_logic(name)
        self.push_screen(SpawnModal(), check_name)

    def spawn_logic(self, name: str):
        project_path = os.path.join(WORKSPACE_BASE, name)
        gemini_data = os.path.join(project_path, ".gemini_data")
        ollama_data = os.path.join(project_path, ".ollama_data")
        
        for p in [project_path, gemini_data, ollama_data]:
            os.makedirs(p, exist_ok=True)

        oauth_port = self._get_free_port(8080)
        ollama_port = self._get_free_port(11434)

        env_vars = {
            **os.environ,
            "COMPOSE_PROJECT_NAME": f"hlg_{name}",
            "HERMES_CONTAINER_NAME": f"hermes_{name}",
            "OLLAMA_CONTAINER_NAME": f"ollama_{name}",
            "WORKSPACE_PATH": project_path,
            "GEMINI_DATA_PATH": gemini_data,
            "OLLAMA_DATA_VOLUME": ollama_data,
            "OAUTH_PORT": str(oauth_port),
            "OLLAMA_PORT": str(ollama_port),
            "OBSIDIAN_VAULT_PATH": VAULT_PATH
        }

        try:
            subprocess.run(["docker", "compose", "up", "-d"], env=env_vars, check=True, cwd=BASE_DIR)
            self.state["environments"][name] = {
                "path": project_path,
                "oauth_port": oauth_port,
                "ollama_port": ollama_port,
                "status": "active"
            }
            self._save_state()
            self.update_env_list()
            self.notify(f"Ambiente '{name}' criado com sucesso!")
        except Exception as e:
            self.notify(f"Erro: {e}", severity="error")

    def action_delete_env(self) -> None:
        list_view = self.query_one("#env_list", ListView)
        if list_view.index is not None:
            item = list_view.children[list_view.index]
            name = item.name
            self.kill_logic(name)

    def kill_logic(self, name: str):
        env_vars = {**os.environ, "COMPOSE_PROJECT_NAME": f"hlg_{name}"}
        try:
            subprocess.run(["docker", "compose", "down"], env=env_vars, cwd=BASE_DIR)
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
            details = f"""
[bold cyan]Ambiente:[/bold cyan] {name}
[bold green]Status:[/bold green] RUNNING
[bold blue]OAuth Port:[/bold blue] {data['oauth_port']}
[bold blue]Ollama Port:[/bold blue] {data['ollama_port']}
[bold gray]Workspace:[/bold gray] {data['path']}

[yellow]Atalhos:[/yellow]
'd' - Encerrar este ambiente
'a' - Criar novo ambiente
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
