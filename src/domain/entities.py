# src/domain/entities.py

class Repository:
    def __init__(self, name, state="stopped"):
        self.name = name
        self.state = state  # "stopped", "running", etc.

    def start(self):
        if self.state == "running":
            raise ValueError(f"Repo '{self.name}' is already running.")
        self.state = "running"

    def stop(self):
        if self.state == "stopped":
            raise ValueError(f"Repo '{self.name}' is already stopped.")
        self.state = "stopped"

    def get_status(self):
        return self.state
