import pytest
from unittest.mock import patch, MagicMock
import logging
from src.serv.script_service import ScriptService

@pytest.fixture
def script_service():
    return ScriptService(exec_repo_path="executive-repository")

@patch("os.listdir")
@patch("os.path.isdir")
def test_load_local_repos(mock_isdir, mock_listdir):
    """
    - executive-repository 폴더 안에 ['repo1', 'repo2', 'somefile.txt']
    - repo1, repo2는 디렉터리, somefile.txt는 파일
    -> repos = { 'repo1': Repository('repo1'), 'repo2': ... }
    """
    def isdir_side_effect(path):
        if path == "executive-repository":
            return True
        elif path == "executive-repository/repo1":
            return True
        elif path == "executive-repository/repo2":
            return True
        elif path == "executive-repository/somefile.txt":
            return False
        return False

    mock_isdir.side_effect = isdir_side_effect
    mock_listdir.return_value = ["repo1", "repo2", "somefile.txt"]

    service = ScriptService(exec_repo_path="executive-repository")
    assert service.get_repo_list() == ["repo1", "repo2"]

@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
def test_git_fetch_repo_success(mock_isdir, mock_run, script_service, caplog):
    mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="fetch success")

    with caplog.at_level(logging.INFO):
        result_msg = script_service.git_fetch_repo("repo1")

    assert "Fetched repo repo1 successfully." in result_msg
    mock_run.assert_called_once_with(["git", "fetch", "origin"], cwd="executive-repository/repo1", capture_output=True, text=True)

@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
def test_git_fetch_repo_fail(mock_isdir, mock_run, script_service, caplog):
    mock_run.return_value = MagicMock(returncode=1, stderr="some git error", stdout="")

    with caplog.at_level(logging.INFO):
        with pytest.raises(RuntimeError) as excinfo:
            script_service.git_fetch_repo("repo1")

    assert "git fetch failed for repo1: some git error" in str(excinfo.value)
    mock_run.assert_called_once_with(["git", "fetch", "origin"], cwd="executive-repository/repo1", capture_output=True, text=True)

@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
def test_git_fetch_repo_fail(mock_isdir, mock_run, script_service, caplog):
    mock_run.return_value = MagicMock(returncode=1, stderr="some git error", stdout="")

    with caplog.at_level(logging.INFO):
        with pytest.raises(RuntimeError) as excinfo:
            script_service.git_fetch_repo("repo1")
        assert "git fetch failed: some git error" in str(excinfo.value)
        assert any("git fetch failed: some git error" in rec.message for rec in caplog.records)

@patch("subprocess.run")
@patch("os.path.isdir", return_value=False)
def test_git_fetch_repo_no_such_dir(mock_isdir, mock_run, script_service, caplog):
    with caplog.at_level(logging.INFO):
        with pytest.raises(ValueError) as excinfo:
            script_service.git_fetch_repo("unknown")
        assert "Repo 'unknown' not found" in str(excinfo.value)
    mock_run.assert_not_called()

@patch("os.listdir")
@patch("os.path.isdir")
def test_list_local_repos(mock_isdir, mock_listdir, script_service):
    """
    - executive-repository 폴더 내부에 'repoA', 'test-repo' 폴더가 있다고 가정
    - repoA/.git 은 있음
    - test-repo/.git 은 없음
    """
    def isdir_side_effect(path):
        if path == "executive-repository":
            return True
        if path == "executive-repository/repoA":
            return True
        if path == "executive-repository/test-repo":
            return True
        if path == "executive-repository/repoA/.git":
            return True
        if path == "executive-repository/test-repo/.git":
            return False
        return False

    mock_isdir.side_effect = isdir_side_effect
    mock_listdir.return_value = ["repoA", "test-repo"]

    repos = script_service.list_local_repos()
    assert repos == ["repoA"]  # test-repo는 .git이 없으므로 제외

@patch("src.serv.script_service.ScriptService.list_local_repos")
@patch("subprocess.run")
def test_git_fetch_all_success(mock_run, mock_list, script_service):
    """
    list_local_repos -> ['repoA', 'repoB']
    각 repo에 대해 git fetch origin main
    """
    mock_list.return_value = ["repoA", "repoB"]
    mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")

    msg = script_service.git_fetch_all()
    assert msg == "Fetched all local repos successfully."
    assert mock_run.call_count == 2

@patch("src.serv.script_service.ScriptService.list_local_repos")
@patch("subprocess.run")
def test_git_fetch_all_fail(mock_run, mock_list, script_service):
    """
    한 레포에서 fetch 실패 -> RuntimeError
    """
    mock_list.return_value = ["repoA", "repoB"]
    def side_effect(cmd, cwd, capture_output, text):
        if cwd.endswith("repoA"):
            return MagicMock(returncode=0)
        else:
            return MagicMock(returncode=1, stderr="fatal: couldn't find remote ref main")
    mock_run.side_effect = side_effect

    with pytest.raises(RuntimeError) as exc:
        script_service.git_fetch_all()
    assert "fatal: couldn't find remote ref main" in str(exc.value)
    assert mock_run.call_count == 2

@patch("os.path.isdir")
@patch("subprocess.run")
def test_git_fetch_repo_main_success(mock_run, mock_isdir, script_service):
    mock_isdir.return_value = True
    mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
    msg = script_service.git_fetch_repo_main("repoA")
    assert "Fetched repo 'repoA' (branch main) successfully." in msg

@patch("os.path.isdir")
@patch("subprocess.run")
def test_git_fetch_repo_main_not_exist(mock_run, mock_isdir, script_service):
    mock_isdir.side_effect = [False]
    with pytest.raises(ValueError) as excinfo:
        script_service.git_fetch_repo_main("unknown")
    assert "Directory 'executive-repository/unknown' does not exist" in str(excinfo.value)
    mock_run.assert_not_called()

@patch("os.path.isdir")
@patch("subprocess.run")
def test_git_fetch_repo_main_fail(mock_run, mock_isdir, script_service):
    mock_isdir.return_value = True
    mock_run.return_value = MagicMock(returncode=128, stderr="fatal: couldn't find remote ref main")
    with pytest.raises(RuntimeError) as excinfo:
        script_service.git_fetch_repo_main("test-repo")
    assert "couldn't find remote ref main" in str(excinfo.value)

@patch("subprocess.run")
def test_git_clone_success(mock_run, script_service, caplog):
    mock_run.return_value = MagicMock(returncode=0, stdout="clone success", stderr="")
    
    with caplog.at_level(logging.INFO):
        msg = script_service.git_clone("git@github.com:ghyeongl/budget-calc-discord-bot.git")
    
    assert "Cloned repo from git@github.com:ghyeongl/budget-calc-discord-bot.git." in msg
    mock_run.assert_called_once_with(
        ["git", "clone", "git@github.com:ghyeongl/budget-calc-discord-bot.git"],
        cwd="executive-repository",
        capture_output=True,
        text=True
    )
    assert any("Cloned repo from git@github.com:ghyeongl/budget-calc-discord-bot.git." 
               in rec.message for rec in caplog.records)

@patch("subprocess.run")
def test_git_clone_fail(mock_run, script_service, caplog):
    mock_run.return_value = MagicMock(returncode=128, stdout="", stderr="Permission denied")

    with caplog.at_level(logging.INFO):
        with pytest.raises(RuntimeError) as excinfo:
            script_service.git_clone("git@github.com:ghyeongl/budget-calc-discord-bot.git")
        assert "git clone failed for git@github.com:ghyeongl/budget-calc-discord-bot.git: Permission denied" in str(excinfo.value)
    mock_run.assert_called_once()
    assert any("git clone failed for git@github.com:ghyeongl/budget-calc-discord-bot.git" in rec.message 
               for rec in caplog.records)

@patch("os.path.isdir", return_value=True)
@patch("os.listdir", return_value=["repo1"])
def test_status_repo_exists(mock_listdir, mock_isdir, script_service):
    status = script_service.status_repo("repo1")
    assert status == "stopped"

@patch("os.path.isdir", return_value=True)
@patch("os.listdir", return_value=["repo1"])
def test_start_then_status(mock_listdir, mock_isdir, script_service):
    script_service.start_repo("repo1")
    status = script_service.status_repo("repo1")
    assert status == "running"

def test_status_repo_not_exists():
    service = ScriptService()
    with pytest.raises(ValueError) as exc:
        service.status_repo("nonexistent")
    assert "not found" in str(exc.value)
