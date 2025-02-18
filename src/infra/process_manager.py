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
        logger.info("[ProcessManager] Scanning for main.py in: %s", self.exec_repo_path)
        pattern = os.path.join(self.exec_repo_path, "*", "main.py")
        main_files = glob.glob(pattern)
        
        for mf in main_files:
            repo_name = os.path.basename(os.path.dirname(mf))
            logger.info(f"[ProcessManager] Launching {repo_name} from {mf}")
            p = subprocess.Popen(["python", mf], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append((repo_name, p))
        
        asyncio.ensure_future(self._collect_logs())
    
    def stop_all(self):
        logger.info("[ProcessManager] Stopping all processes...")
        for repo_name, proc in self.processes:
            if proc.poll() is None:  # 아직 종료 안 됨
                proc.terminate()
        self.processes.clear()

    async def _collect_logs(self):
        while True:
            for repo_name, proc in list(self.processes):
                if proc.poll() is not None:
                    self.processes.remove((repo_name, proc))
                    logger.info(f"[ProcessManager] {repo_name} exited with code {proc.returncode}")
                else:
                    pass
            await asyncio.sleep(2)
    
    def send_signal(self, repo_name, signal_type):
        for rn, proc in self.processes:
            if rn == repo_name:
                if signal_type == "STOP":
                    proc.terminate()
                    logger.info(f"[ProcessManager] Sent STOP to {repo_name}")
                break

    def start_repo_process(self, repo_name, extra_arg=None):
        main_script = os.path.join(self.exec_repo_path, repo_name, "main.py")
        cmd = ["python", main_script]
        if extra_arg:
            cmd.append(extra_arg)

        logger.info(f"[ProcessManager] Starting repo '{repo_name}' with command: {cmd}")
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.processes.append((repo_name, p))
        logger.info(f"[ProcessManager] '{repo_name}' pid={p.pid} started.")

    def stop_repo_process(self, repo_name):
        for i, (rn, proc) in enumerate(self.processes):
            if rn == repo_name and proc.poll() is None:
                proc.terminate()
                logger.info(f"[ProcessManager] '{repo_name}' (pid={proc.pid}) terminated.")
                self.processes.pop(i)
                return
        logger.warning(f"[ProcessManager] '{repo_name}' not found or already stopped.")
