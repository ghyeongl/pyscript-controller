# process_manager.py
import os
import subprocess
import glob
import asyncio
import logging

logger = logging.getLogger(__name__)

class ProcessManager:
    def __init__(self, exec_repo_path):
        self.exec_repo_path = exec_repo_path
        self.processes = []  # (repo_name, Popen_object)
    
    def start_all(self):
        """
        executive-repository 폴더 내의 모든 subfolder에서 main.py를 찾아서 실행
        """
        logger.info("[ProcessManager] Scanning for main.py in: %s", self.exec_repo_path)
        pattern = os.path.join(self.exec_repo_path, "*", "main.py")
        main_files = glob.glob(pattern)
        
        for mf in main_files:
            repo_name = os.path.basename(os.path.dirname(mf))
            logger.info(f"[ProcessManager] Launching {repo_name}")
            
            # Popen으로 실행(파이썬 버전에 맞춰 변경 가능)
            p = subprocess.Popen(["python", mf], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append((repo_name, p))
        
        # 로그 수집용 Task를 돌릴 수도 있음 (asyncio)
        asyncio.ensure_future(self._collect_logs())
    
    def stop_all(self):
        logger.info("[ProcessManager] Stopping all processes...")
        for repo_name, proc in self.processes:
            if proc.poll() is None:  # 아직 종료 안 됨
                proc.terminate()
        self.processes.clear()

    async def _collect_logs(self):
        """
        각 프로세스의 stdout/stderr를 비동기로 읽어와
        DiscordBot 등에 전달할 수 있게 하는 예시
        """
        while True:
            for repo_name, proc in list(self.processes):
                if proc.poll() is not None:
                    # 이미 종료됨
                    self.processes.remove((repo_name, proc))
                    logger.info(f"[ProcessManager] {repo_name} exited with code {proc.returncode}")
                else:
                    # 아직 동작 중이면 로그 처리
                    # 주의: non-blocking I/O 처리를 위해서는 asyncio subprocess 또는 다른 기법 필요
                    pass
            await asyncio.sleep(2)
    
    def send_signal(self, repo_name, signal_type):
        """
        특정 레포에 'STOP' 등 신호를 보낸다고 가정
        - 실제 구현은 IPC 방식을 정해서 메시지를 전달
        """
        for rn, proc in self.processes:
            if rn == repo_name:
                if signal_type == "STOP":
                    proc.terminate()
                    logger.info(f"[ProcessManager] Sent STOP to {repo_name}")
                break

    def start_repo_process(self, repo_name, extra_arg=None):
        """
        실제로 {repo_name}/main.py를 서브프로세스로 실행하여
        레포를 '시작'한다고 가정.
        """
        # 1) main.py 위치 찾기
        main_script = os.path.join(self.exec_repo_path, repo_name, "main.py")

        # 2) 실행할 커맨드 구성
        cmd = ["python", main_script]
        if extra_arg:
            cmd.append(extra_arg)

        logger.info(f"[ProcessManager] Starting repo '{repo_name}' with command: {cmd}")

        # 3) 서브프로세스 실행
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 4) 관리 리스트에 추가
        self.processes.append((repo_name, p))
        logger.info(f"[ProcessManager] '{repo_name}' pid={p.pid} started.")

    def stop_repo_process(self, repo_name):
        """
        해당 레포 프로세스를 찾아 중지. (단순 terminate 예시)
        """
        for i, (rn, proc) in enumerate(self.processes):
            if rn == repo_name and proc.poll() is None:
                proc.terminate()
                logger.info(f"[ProcessManager] '{repo_name}' (pid={proc.pid}) terminated.")
                self.processes.pop(i)
                return

        logger.warning(f"[ProcessManager] '{repo_name}' not found or already stopped.")
