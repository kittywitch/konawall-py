import subprocess
import dbus
import time
from konawall.module_loader import add_environment

@add_environment("niri_setter")
def set_wallpapers(files: list, displays: list):
    for i in range(len(displays)):
        display_name = displays[i].name
        command = ["swww", "img", "-o", display_name, files[i]]
        subprocess.run(command)
