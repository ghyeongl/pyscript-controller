# Script_Management

Python code for managing repositories in remote computers.
add this to systemd service to make restart-safe code executive.

to do update and stop repositories command by discord bot,
make discord bot account and add token.txt manually to remotely control your scripts.

make Repositories folder and put your repository in there.
this code will automatically find main.py script and execute it.

```python
# repo1/main.py
import time
import random
from pyscript_controller.lib import signal_interface as si

def main_logic():
    si.log("Repo1 main logic started")
    for i in range(5):
        si.log(f"Doing some work... step {i}")
        if random.random() < 0.3:
            si.warn("Something might be off here!")
        time.sleep(2)
    si.log("Repo1 main logic completed")

if __name__ == "__main__":
    main_logic()

```