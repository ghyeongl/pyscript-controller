import pytest
from src.serv.script_service import ScriptService

def test_status_repo_exists():
    service = ScriptService()
    # 기본 repo1, repo2가 "stopped" 상태라고 가정
    status = service.status_repo("repo1")
    assert status == "stopped"

def test_status_repo_not_exists():
    service = ScriptService()
    with pytest.raises(ValueError) as exc:
        service.status_repo("nonexistent")
    assert "not found" in str(exc.value)

def test_start_then_status():
    service = ScriptService()
    service.start_repo("repo1")  
    # start_repo()가 실행되면 state가 "running"이 되었다고 가정
    status = service.status_repo("repo1")
    assert status == "running"
