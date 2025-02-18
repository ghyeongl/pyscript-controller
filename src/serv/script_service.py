# src/application/script_service.py
import logging
import subprocess
import os
from src.domain.entities import Repository
from src.infra.process_manager import ProcessManager
from src.serv.container_service import ContainerService

logger = logging.getLogger(__name__)

class ScriptService:
    """
    DiscordBot(Presentation)에서 전달받은 명령을 처리하는 Service 계층.
    Domain의 엔티티(Repository 등)와 Infrastructure(예: ProcessManager)를 사용.
    """
    def __init__(self, exec_repo_path="executive-repository"):
        self.pm = ProcessManager(exec_repo_path=exec_repo_path)
        self.containerService = ContainerService()
        self.exec_repo_path = exec_repo_path
        self.repos = self._load_local_repos()

    def _load_local_repos(self):
        if not os.path.isdir(self.exec_repo_path):
            logger.warning(f"{self.exec_repo_path} does not exist or is not a directory.")
            return {}

        repo_dict = {}
        for entry in os.listdir(self.exec_repo_path):
            path = os.path.join(self.exec_repo_path, entry)
            if os.path.isdir(path):
                repo_dict[entry] = Repository(entry)
        logger.info(f"Found local repos: {list(repo_dict.keys())}")
        return repo_dict

    def get_repo_list(self):
        return list(self.repos.keys())

    def _get_repo(self, repo_name):
        if repo_name not in self.repos:
            logger.error(f"Repo '{repo_name}' does not exist in {self.exec_repo_path}.")
            raise ValueError(f"Repo '{repo_name}' does not exist in {self.exec_repo_path}.")
        return self.repos[repo_name]

    def list_local_repos(self):
        """
        .git 폴더가 있는 디렉토리만 '진짜 Git 레포'라고 간주
        """
        valid_repos = []
        for repo_name in self.repos.keys():
            git_path = os.path.join(self.exec_repo_path, repo_name, ".git")
            if os.path.isdir(git_path):
                valid_repos.append(repo_name)
        return valid_repos

    def start_repo(self, repo_name, extra_arg=None):
        repo = self._get_repo(repo_name)
        repo.start()
        self.pm.start_repo_process(repo.name, extra_arg)

    def stop_repo(self, repo_name):
        repo = self._get_repo(repo_name)
        repo.stop()
        self.pm.stop_repo_process(repo.name)

    def restart_repo(self, repo_name):
        self.stop_repo(repo_name)
        self.start_repo(repo_name)

    def kill_repo(self, repo_name):
        logger.info(f"Killing repo {repo_name} forcibly")

    def status_repo(self, repo_name):
        repo = self._get_repo(repo_name)
        return repo.get_status()

    def get_all_logs(self):
        logger.info("get_all_logs called - not implemented")
        return "some logs"

    def get_today_logs(self):
        logger.info("get_today_logs called - not implemented")
        return "today's logs"

    def restart_system(self, alert=False):
        logger.info(f"restart_system called with alert={alert}")

    def get_cpu_usage(self):
        return "CPU usage"

    def get_temp(self):
        return "Temperature"

    def git_fetch_all(self):
        repos = self.list_local_repos()
        if not repos:
            logger.warning("No local repos found in exec_repo_path.")
            return "No local repos found."

        logger.info(f"Found local repos: {repos}. Now fetching origin.")
        for repo_name in repos:
            self.git_fetch_repo(repo_name)
        return "Fetched all local repos successfully."

    def git_fetch_repo(self, repo_name):
        self._get_repo(repo_name)
        repo_path = os.path.join(self.exec_repo_path, repo_name)
        if not os.path.isdir(repo_path):
            raise ValueError(f"Folder '{repo_path}' does not exist.")

        cmd = ["git", "fetch", "origin"]
        logger.info(f"Fetching repo '{repo_name}': {cmd} (cwd={repo_path})")
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = f"git fetch failed for {repo_name}: {result.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        msg = f"Fetched repo {repo_name} successfully."
        logger.info(msg)
        return msg

    def git_fetch_repo_main(self, repo_name):
        self._get_repo(repo_name)  # 레포 존재 여부 확인
        repo_path = os.path.join(self.exec_repo_path, repo_name)
        if not os.path.isdir(repo_path):
            raise ValueError(f"Directory '{repo_path}' does not exist")

        cmd = ["git", "fetch", "origin", "main"]
        logger.info(f"Fetching main branch for '{repo_name}': {cmd} (cwd={repo_path})")
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = f"git fetch main failed for {repo_name}: {result.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        msg = f"Fetched repo '{repo_name}' (branch main) successfully."
        logger.info(msg)
        return msg

    def git_clone(self, url):
        logger.info(f"Cloning from {url} into {self.exec_repo_path}")
        result = subprocess.run(["git", "clone", url],
                                cwd=self.exec_repo_path,
                                capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = f"git clone failed for {url}: {result.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        msg = f"Cloned repo from {url}."
        logger.info(msg)  # <= 테스트에서 여기 로그를 찾는다
        return msg

    def list_containers(self):
        return self.containerService.list_containers()

    def container_start(self, cont_name):
        return self.containerService.start_container(cont_name)

    def container_stop(self, cont_name):
        return self.containerService.stop_container(cont_name)

    def container_restart(self, cont_name):
        self.containerService.stop_container(cont_name)
        self.containerService.start_container(cont_name)
