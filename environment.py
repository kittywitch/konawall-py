import sys
import os
import logging
from custom_errors import UnsupportedPlatform
from module_loader import environment_handlers

"""
This detects the DE/WM from the Linux environment because it's not provided by the platform
"""
def detect_linux_environment():
    if os.environ.get("SWAYSOCK"):
        return "sway"
    return_unmodified_if_these = [
        # TODO: implement
        "gnome", # dconf
        "cinnamon", # dconf
        "mate", # dconf
        "deepin", # dconf
        "xfce4", # xfconf
        "lxde", # pcmanfm
        "kde", # qdbus
    ]
    modified_mapping = {
        "fluxbox": "feh",
        "blackbox": "feh",
        "openbox": "feh",
        "i3": "feh",
        "ubuntustudio": "kde",
        "ubuntu": "gnome",
        "lubuntu": "lxde",
        "xubuntu": "xfce4",
        "kubuntu": "kde",
        "ubuntugnome": "gnome",
    }
    desktop_session = os.environ.get("DESKTOP_SESSION")
    if desktop_session in return_unmodified_if_these:
        return desktop_session
    elif desktop_session in modified_mapping:
        return modified_mapping[desktop_session]
    else:
        UnsupportedPlatform(f"Desktop session {desktop_session} is not supported, sorry!")

def detect_environment():
    if sys.platform == "linux":
        environment = detect_linux_environment()
        logging.info(f"Detected environment is {environment} running on Linux")
    else:
        environment = sys.platform
        logging.info(f"Detected environment is {environment}")
    return environment

"""
    This sets wallpapers on any platform, as long as it is supported.
"""
def set_environment_wallpapers(environment: str, files: list):
    if environment in environment_handlers:
        environment_handlers[f"{environment}_setter"](files)
        logging.info("Wallpapers set!")
    else:
        UnsupportedPlatform(f"Environment {environment} is not supported, sorry!")