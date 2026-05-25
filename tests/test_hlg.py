import os
import json
import pytest
from unittest.mock import MagicMock, patch
from hlg import HLGApp, STATE_FILE, WORKSPACE_BASE

@pytest.fixture
def mock_app(mocker):
    # Mock Textual App methods to avoid UI initialization issues
    mocker.patch("hlg.App.__init__", return_value=None)
    mocker.patch("hlg.HLGApp.update_env_list")
    mocker.patch("hlg.HLGApp.notify")
    app = HLGApp()
    app.state = {"environments": {}}
    return app

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
    mock_update = mocker.patch.object(mock_app, "update_env_list")
    
    mock_app.action_refresh()
    
    assert mock_app.state["environments"]["refreshed"] == "data"
    mock_update.assert_called_once()

def test_on_list_view_highlighted(mock_app, mocker):
    # Mock the widget query
    mock_details = MagicMock()
    mock_app.query_one = MagicMock(return_value=mock_details)
    
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
