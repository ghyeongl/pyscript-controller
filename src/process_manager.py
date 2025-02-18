# process_manager.py
import os
import subprocess
import glob
import asyncio

class ProcessManager:
    def __init__(self, exec_repo_path):
        self.exec_repo_path = exec_repo_path
        self.processes = []  # (repo_name, Popen_object)
    
    def start_all(self):
        """
        executive-repository 폴더 내의 모든 subfolder에서 main.py를 찾아서 실행
        """
        print("[ProcessManager] Scanning for main.py in:", self.exec_repo_path)
        pattern = os.path.join(self.exec_repo_path, "*", "main.py")
        main_files = glob.glob(pattern)
        
        for mf in main_files:
            repo_name = os.path.basename(os.path.dirname(mf))
            print(f"[ProcessManager] Launching {repo_name}")
            
            # Popen으로 실행(파이썬 버전에 맞춰 변경 가능)
            p = subprocess.Popen(["python", mf], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append((repo_name, p))
        
        # 로그 수집용 Task를 돌릴 수도 있음 (asyncio)
        asyncio.ensure_future(self._collect_logs())
    
    def stop_all(self):
        print("[ProcessManager] Stopping all processes...")
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
                    print(f"[ProcessManager] {repo_name} exited with code {proc.returncode}")
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
                    print(f"[ProcessManager] Sent STOP to {repo_name}")
                break
