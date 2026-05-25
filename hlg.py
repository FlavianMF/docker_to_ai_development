#!/usr/bin/env python3
import os
import subprocess
import json
import socket
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListItem, ListView, Label, Input
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.binding import Binding
from textual import on

# Configurações Base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_BASE = os.path.join(BASE_DIR, "workspace")
VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "/mnt/c/Users/saoflfer/Documents/obsidian/flv_fit_vault")
STATE_FILE = os.path.join(BASE_DIR, ".hlg_state.json")

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
        Binding("q", "quit", "Sair"),
        Binding("a", "add_env", "Adicionar (Spawn)"),
        Binding("d", "delete_env", "Deletar (Kill)"),
        Binding("r", "refresh", "Atualizar"),
    ]

    def __init__(self):
        super().__init__()
        self.state = self._load_state()

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
        yield Footer()

    def on_mount(self) -> None:
        self.update_env_list()

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

if __name__ == "__main__":
    app = HLGApp()
    app.run()
