import subprocess
import dbus
from konawall.module_loader import add_environment

@add_environment("hyprland_setter")
def set_wallpapers(files: list, displays: list):
    #[Monitor(x=0, y=0, width=1920, height=1080, width_mm=280, height_mm=160, name='eDP-1', is_primary=False), Monitor(x=1920, y=0, width=3840, height=2160, width_mm=600, height_mm=340, name='DP-3', is_primary=False)]
    try:
        subprocess.Popen(["killall", "swaybg"])
        time.sleep(0.005)
    except Exception as e:
        print(e)
    for i in range(len(displays)):
        display_name = displays[i].name
        command = ["swww", "img", "-o", display_name, files[i]]
        subprocess.run(command)
