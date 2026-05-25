import os
import json
import pytest
from unittest.mock import MagicMock, patch
from hlg import HLGApp, STATE_FILE, WORKSPACE_BASE, ResourceManager

@pytest.fixture
def mock_app(mocker):
    # Mock Textual App methods to avoid UI initialization issues
    mocker.patch("hlg.App.__init__", return_value=None)
    # mocker.patch("hlg.HLGApp.update_env_list") # Don't mock here if we want to test it
    # mocker.patch("hlg.HLGApp.update_docker_views") # Don't mock here if we want to test it
    mocker.patch("hlg.HLGApp.notify")
    app = HLGApp()
    app.state = {"environments": {}}
    # Initialize resource_manager manually since __init__ is mocked
    app.resource_manager = ResourceManager()
    return app

def test_resource_manager_get_containers(mocker):
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.stdout = '{"ID": "123", "Names": "hlg_test", "Status": "Up", "Ports": "80"}\n'
    
    containers = ResourceManager.get_containers()
    assert len(containers) == 1
    assert containers[0]["ID"] == "123"
    # Search for the string in the command list
    assert any("name=hlg_" in arg for arg in mock_run.call_args[0][0])

def test_resource_manager_get_images(mocker):
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.stdout = '{"ID": "img1", "Repository": "hermes_docker", "Tag": "latest", "Size": "100MB"}\n'
    
    images = ResourceManager.get_images()
    assert len(images) == 1
    assert images[0]["ID"] == "img1"

def test_resource_manager_prune(mocker):
    mock_run = mocker.patch("subprocess.run")
    
    success = ResourceManager.prune()
    assert success is True
    assert mock_run.call_count == 2 # container prune and image prune

def test_update_docker_views(mock_app, mocker):
    # Mock tables and widgets
    mock_c_table = MagicMock()
    mock_i_table = MagicMock()
    mock_usage = MagicMock()
    
    # Mock the query_one method of the app
    def mock_query(q):
        if q == "#container_table": return mock_c_table
        if q == "#image_table": return mock_i_table
        if q == "#disk_usage_details": return mock_usage
        return MagicMock()
    
    mocker.patch.object(mock_app, "query_one", side_effect=mock_query)
    
    mocker.patch.object(mock_app.resource_manager, "get_containers", return_value=[{"ID": "c1"}])
    mocker.patch.object(mock_app.resource_manager, "get_images", return_value=[{"ID": "i1"}])
    mocker.patch.object(mock_app.resource_manager, "get_disk_usage", return_value={"Containers": "10"})
    
    # Explicitly call update_docker_views (the real one)
    HLGApp.update_docker_views(mock_app)
    
    assert mock_c_table.add_row.called
    assert mock_i_table.add_row.called
    assert mock_usage.update.called

def test_action_prune(mock_app, mocker):
    # Ensure update_docker_views is mocked for this test to avoid complexity
    mocker.patch.object(mock_app, "update_docker_views")
    mock_prune = mocker.patch.object(mock_app.resource_manager, "prune", return_value=True)
    
    mock_app.action_prune()
    
    mock_prune.assert_called_once()
    mock_app.update_docker_views.assert_called_once()
    mock_app.notify.assert_called_with("Limpeza (Prune) concluída com sucesso!")

def test_action_stop_env(mock_app, mocker):
    mock_stop = mocker.patch.object(mock_app.resource_manager, "stop_container", return_value=True)
    mocker.patch.object(mock_app, "update_docker_views")
    
    # Setup selected item
    mock_list = MagicMock()
    mock_list.index = 0
    mock_item = MagicMock()
    mock_item.name = "test-env"
    mock_list.children = [mock_item]
    mocker.patch.object(mock_app, "query_one", return_value=mock_list)
    
    mock_app.action_stop_env()
    
    mock_stop.assert_called_with("hermes_test-env")
    mock_app.notify.assert_called_with("Ambiente 'test-env' parado.")

def test_action_shell_env_tmux(mock_app, mocker):
    mocker.patch.dict(os.environ, {"TMUX": "/tmp/tmux"})
    mock_run = mocker.patch("subprocess.run")
    
    # Setup selected item
    mock_list = MagicMock()
    mock_list.index = 0
    mock_item = MagicMock()
    mock_item.name = "test-env"
    mock_list.children = [mock_item]
    mocker.patch.object(mock_app, "query_one", return_value=mock_list)
    
    mock_app.action_shell_env()
    
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "tmux" in args
    assert "new-window" in args
    assert "docker exec -it hermes_test-env /bin/bash" in args

def test_action_shell_env_direct(mock_app, mocker):
    # Ensure TMUX is NOT in environment
    mocker.patch.dict(os.environ, {}, clear=True)
    mock_run = mocker.patch("subprocess.run")
    # Mock suspend as a context manager
    mock_suspend = mocker.patch.object(mock_app, "suspend")
    mock_suspend.return_value.__enter__ = MagicMock()
    mock_suspend.return_value.__exit__ = MagicMock()
    
    # Setup selected item
    mock_list = MagicMock()
    mock_list.index = 0
    mock_item = MagicMock()
    mock_item.name = "test-env"
    mock_list.children = [mock_item]
    mocker.patch.object(mock_app, "query_one", return_value=mock_list)
    
    mock_app.action_shell_env()
    
    # Verify suspend was used
    mock_suspend.assert_called_once()
    # Verify direct docker exec call
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "docker" == args[0]
    assert "exec" == args[1]
    assert "-it" == args[2]
    assert "hermes_test-env" == args[3]

def test_get_free_port(mock_app, mocker):
    mock_socket = mocker.patch("socket.socket")
    # Mock connect_ex to return 0 (busy) then 1 (free)
    mock_socket.return_value.__enter__.return_value.connect_ex.side_effect = [0, 1]
    
    port = mock_app._get_free_port(8080)
    assert port == 8081

def test_load_state(tmp_path, mocker):
    state_file = tmp_path / ".hlg_state.json"
    mocker.patch("hlg.STATE_FILE", str(state_file))
    
    initial_state = {"environments": {"test": {"port": 8080}}}
    with open(state_file, "w") as f:
        json.dump(initial_state, f)
        
    mocker.patch("hlg.App.__init__", return_value=None)
    app = HLGApp()
    state = app._load_state()
    assert state == initial_state

def test_save_state(tmp_path, mocker):
    state_file = tmp_path / ".hlg_state.json"
    mocker.patch("hlg.STATE_FILE", str(state_file))
    
    mocker.patch("hlg.App.__init__", return_value=None)
    app = HLGApp()
    app.state = {"environments": {"test": "data"}}
    app._save_state()
    
    with open(state_file, "r") as f:
        saved_state = json.load(f)
    assert saved_state == app.state

def test_spawn_logic(mock_app, mocker):
    mocker.patch("os.makedirs")
    mock_run = mocker.patch("subprocess.run")
    mock_get_port = mocker.patch.object(mock_app, "_get_free_port", side_effect=[8080, 11434])
    mock_save = mocker.patch.object(mock_app, "_save_state")
    mocker.patch.object(mock_app, "update_env_list")
    
    mock_app.spawn_logic("new-env")
    
    # Check directory creation
    assert os.makedirs.call_count >= 3
    
    # Check subprocess call
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == ["docker", "compose", "up", "-d"]
    assert kwargs["env"]["COMPOSE_PROJECT_NAME"] == "hlg_new-env"
    
    # Check state update
    assert "new-env" in mock_app.state["environments"]
    assert mock_app.state["environments"]["new-env"]["oauth_port"] == 8080

def test_kill_logic(mock_app, mocker):
    mock_run = mocker.patch("subprocess.run")
    mock_save = mocker.patch.object(mock_app, "_save_state")
    mocker.patch.object(mock_app, "update_env_list")
    
    mock_app.state["environments"]["to-kill"] = {"path": "/tmp/test"}
    
    mock_app.kill_logic("to-kill")
    
    # Check subprocess call
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == ["docker", "compose", "down"]
    assert kwargs["env"]["COMPOSE_PROJECT_NAME"] == "hlg_to-kill"
    
    # Check state removal
    assert "to-kill" not in mock_app.state["environments"]

def test_refresh_logic(mock_app, mocker):
    mock_load = mocker.patch.object(mock_app, "_load_state", return_value={"environments": {"refreshed": "data"}})
    mocker.patch.object(mock_app, "update_env_list")
    mocker.patch.object(mock_app, "update_docker_views")
    
    mock_app.action_refresh()
    
    assert mock_app.state["environments"]["refreshed"] == "data"
    mock_app.update_env_list.assert_called_once()

def test_on_list_view_highlighted(mock_app, mocker):
    # Mock the widget query
    mock_details = MagicMock()
    mocker.patch.object(mock_app, "query_one", return_value=mock_details)
    
    # Mock the event
    mock_event = MagicMock()
    mock_event.item.name = "test-env"
    mock_app.state["environments"]["test-env"] = {
        "oauth_port": 8080,
        "ollama_port": 11434,
        "path": "/path/to/test"
    }
    
    mock_app.on_list_view_highlighted(mock_event)
    
    # Verify that update was called on the details widget
    mock_details.update.assert_called_once()
    content = mock_details.update.call_args[0][0]
    assert "test-env" in content
    assert "8080" in content
