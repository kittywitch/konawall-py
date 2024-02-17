import sys
import os
import logging
from konawall.custom_errors import UnsupportedPlatform
from konawall.module_loader import environment_handlers

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
        "plasma": "kde",
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
        return os.environ.get("XDG_CURRENT_DESKTOP").lower()

def detect_environment():
    if sys.platform == "linux":
        environment = detect_linux_environment()
        logging.debug(f"Detected environment is {environment} running on Linux")
    else:
        environment = sys.platform
        logging.debug(f"Detected environment is {environment}")
    return environment

"""
    This sets wallpapers on any platform, as long as it is supported.
"""
def set_environment_wallpapers(environment: str, files: list, displays: list):
    if f"{environment}_setter" in environment_handlers:
        environment_handlers[f"{environment}_setter"](files, displays)
        logging.debug("Wallpapers set!")
    else:
        UnsupportedPlatform(f"Environment {environment} is not supported, sorry!")
