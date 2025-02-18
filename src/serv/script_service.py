# src/application/script_service.py
import logging
from src.domain.entities import Repository
from src.infra.process_manager import ProcessManager
from src.serv.container_service import ContainerService

logger = logging.getLogger(__name__)

class ScriptService:
    """
    DiscordBot(Presentation)에서 전달받은 명령을 처리하는 Service 계층.
    Domain의 엔티티(Repository 등)와 Infrastructure(예: ProcessManager)를 사용.
    """
    def __init__(self):
        self.pm = ProcessManager(exec_repo_path="executive-repository")
        self.containerService = ContainerService()
        # 실제로는 repo 목록을 DB나 config에서 읽어올 수도 있음
        self.repos = {
            "repo1": Repository("repo1"),
            "repo2": Repository("repo2"),
        }

    def get_repo_list(self):
        return list(self.repos.keys())

    def start_repo(self, repo_name, extra_arg=None):
        repo = self._get_repo(repo_name)
        # Domain 로직: 예외가 발생하면 Discord 쪽에서 에러 메시지를 보여줄 수 있음
        repo.start()

        # Infrastructure 호출로 실제 프로세스 시작
        self.pm.start_repo_process(repo.name, extra_arg)

    def stop_repo(self, repo_name):
        repo = self._get_repo(repo_name)
        repo.stop()
        self.pm.stop_repo_process(repo.name)

    def restart_repo(self, repo_name):
        # stop -> start 시퀀스 또는 Domain 규칙대로
        self.stop_repo(repo_name)
        self.start_repo(repo_name)

    def kill_repo(self, repo_name):
        logger.info(f"Killing repo {repo_name} forcibly")
        # pm.stop_repo_process(repo_name) + repo.state = "stopped" or "error"
        # ...
    
    def status_repo(self, repo_name):
        """
        repo_name에 해당하는 레포의 현재 상태를 반환.
        예: "running", "stopped", "error" 등
        """
        repo = self._get_repo(repo_name)
        return repo.get_status()
    
    def _get_repo(self, repo_name):
        if repo_name not in self.repos:
            raise ValueError(f"Repo '{repo_name}' not found.")
        return self.repos[repo_name]

    # 예시: log, system, git, container 관련 메서드
    def get_all_logs(self):
        logger.info("get_all_logs called - not implemented")
        return "some logs"

    def get_today_logs(self):
        logger.info("get_today_logs called - not implemented")
        return "today's logs"

    def restart_system(self, alert=False):
        logger.info(f"restart_system called with alert={alert}")
        # infra layer를 또 호출할 수도 있음

    def get_cpu_usage(self):
        # ...
        return "CPU usage"

    def get_temp(self):
        # ...
        return "Temperature"

    def git_fetch_all(self):
        # ...
        logger.info("git_fetch_all called")

    def git_fetch_repo(self, repo_name):
        # ...
        logger.info(f"git_fetch_repo({repo_name})")

    def list_containers(self):
        return self.containerService.list_containers()

    def container_start(self, cont_name):
        return self.containerService.start_container(cont_name)

    def container_stop(self, cont_name):
        return self.containerService.stop_container(cont_name)

    def container_restart(self, cont_name):
        self.containerService.stop_container(cont_name)
        self.containerService.start_container(cont_name)
