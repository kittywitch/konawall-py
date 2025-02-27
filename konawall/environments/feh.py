import subprocess
import dbus
import time
from konawall.module_loader import add_environment

@add_environment("feh_setter")
def set_wallpapers(files: list, displays: list):
    command = ["feh", "--bg-fill"] + files
    subprocess.run(command)
