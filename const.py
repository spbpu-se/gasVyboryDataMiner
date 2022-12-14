from subprocess import run
from time import sleep

# Path and name to the script you are trying to start
file_path = "main.py 01.05.2022 01.01.2023"

restart_timer = 2


def start_script():
    try:
        # Make sure 'python' command is available
        run("python " + file_path, check=True, shell=True)
    except Exception:
        # Script crashed, lets restart it!
        handle_crash()


def handle_crash():
    sleep(restart_timer)  # Restarts the script after 2 seconds
    start_script()


start_script()
