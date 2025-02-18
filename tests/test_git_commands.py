import pytest
from unittest.mock import patch, MagicMock
from src.serv.script_service import ScriptService

@pytest.fixture
def script_service():
    return ScriptService(exec_repo_path="executive-repository")

@patch("subprocess.run")
def test_git_fetch_repo(mock_run, script_service):
    with patch("os.path.isdir", return_value=True):
        mock_run.return_value = MagicMock(returncode=0, stdout="fetch success", stderr="")
        
        script_service.git_fetch_repo("repo1")
        mock_run.assert_called_once_with(
            ["git", "fetch", "origin"],
            cwd="executive-repository/repo1",
            capture_output=True,
            text=True
        )

@patch("subprocess.run")
def test_git_fetch_repo_not_exist(mock_run, script_service):
    with patch("os.path.isdir", return_value=False):
        with pytest.raises(ValueError) as exc:
            script_service.git_fetch_repo("unknown")
        assert "does not exist" in str(exc.value)
    mock_run.assert_not_called()

@patch("subprocess.run")
def test_git_clone_success(mock_run, script_service):
    mock_run.return_value = MagicMock(returncode=0, stdout="clone success", stderr="")
    script_service.git_clone("git@github.com:ghyeongl/budget-calc-discord-bot.git")

    mock_run.assert_called_once_with(
        ["git", "clone", "git@github.com:ghyeongl/budget-calc-discord-bot.git"],
        cwd="executive-repository",
        capture_output=True,
        text=True
    )

@patch("subprocess.run")
def test_git_clone_fail(mock_run, script_service):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="clone error")
    with pytest.raises(RuntimeError) as exc:
        script_service.git_clone("git@github.com:ghyeongl/budget-calc-discord-bot.git")
    assert "git clone failed" in str(exc.value)
