# signal_interface.py

"""
각 레포 main.py가 import해서 사용하는 공용 인터페이스 예시
'컨트롤러' 쪽에 로그나 메세지를 보낼 수 있는 스텁 함수들
실제로는 IPC나 소켓을 통해 ProcessManager/DiscordBot에 전달되도록 구현 가능
"""

def log(message: str):
    print(f"[REPO-LOG] {message}")

def warn(message: str):
    print(f"[REPO-WARN] {message}")

def send_event(event_type: str, data: dict):
    print(f"[REPO-EVENT] type={event_type}, data={data}")
