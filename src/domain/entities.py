# src/domain/entities.py

class Repository:
    def __init__(self, name, state="stopped"):
        self.name = name
        self.state = state  # e.g. "running", "stopped", "error"

    def start(self):
        if self.state == "running":
            raise ValueError(f"Repo '{self.name}' is already running.")
        self.state = "running"

    def stop(self):
        if self.state == "stopped":
            raise ValueError(f"Repo '{self.name}' is already stopped.")
        self.state = "stopped"

    def get_status(self):
        """현재 저장된 state를 반환."""
        return self.state

    def can_start(self):
        return self.state in ("stopped", "error")

    # etc...
