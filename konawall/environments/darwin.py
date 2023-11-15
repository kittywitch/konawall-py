import subprocess
from konawall.module_loader import add_environment

"""
This sets wallpapers on Darwin.

:param files: A list of files to set as wallpapers
"""
@add_environment("darwin_setter")
def set_wallpapers(files: list, displays: list):
    for i, file in enumerate(files):
        # Run osascript to set the wallpaper for each monitor
        command = f'tell application "System Events" to set picture of desktop {i-1} to "{file}"'
        subprocess.run(["osascript", "-e", command])