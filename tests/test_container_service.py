import pytest
from unittest.mock import patch, MagicMock
from src.serv.container_service import ContainerService

@patch("subprocess.check_output")
def test_list_containers(mock_check_output):
    """
    docker ps -a --format "{{.Names}}" 명령이 실행되고,
    반환된 목록을 파싱하는지 검증
    """
    service = ContainerService()

    # 가짜 출력: b"cont1\ncont2\n"
    mock_check_output.return_value = b"cont1\ncont2\n"

    containers = service.list_containers()
    assert containers == ["cont1", "cont2"]

    # subprocess.check_output가 이렇게 호출되었는지 확인
    mock_check_output.assert_called_once_with(["docker", "ps", "-a", "--format", "{{.Names}}"])


@patch("subprocess.run")
@patch("subprocess.check_output")
def test_start_container(mock_check_output, mock_run):
    """
    docker ps -a -> cont1, cont2
    docker start cont1
    """
    service = ContainerService()

    # list_containers() 호출 시 "cont1"만 있다고 가정
    mock_check_output.return_value = b"cont1\n"

    service.start_container("cont1")

    # 먼저 list_containers()가 불려서 docker ps -a 확인
    mock_check_output.assert_called_once_with(["docker", "ps", "-a", "--format", "{{.Names}}"])

    # 이후 docker start cont1
    mock_run.assert_called_once_with(["docker", "start", "cont1"], check=True)


@patch("subprocess.run")
@patch("subprocess.check_output")
def test_start_container_not_exists(mock_check_output, mock_run):
    """
    컨테이너 목록에 없는 이름 start 시도
    """
    service = ContainerService()
    mock_check_output.return_value = b"cont1\ncont2\n"

    with pytest.raises(ValueError) as exc:
        service.start_container("unknown")
    
    # docker start는 절대 불리지 않아야 함
    mock_run.assert_not_called()
    assert "Container 'unknown' does not exist." in str(exc.value)


@patch("subprocess.run")
@patch("subprocess.check_output")
def test_stop_container(mock_check_output, mock_run):
    """
    docker ps -a -> cont1, cont2
    docker stop cont2
    """
    service = ContainerService()
    mock_check_output.return_value = b"cont1\ncont2\n"

    service.stop_container("cont2")

    # list_containers()는 1번 호출
    mock_check_output.assert_called_once_with(["docker", "ps", "-a", "--format", "{{.Names}}"])
    # docker stop cont2 실행
    mock_run.assert_called_once_with(["docker", "stop", "cont2"], check=True)
