import os
import ctypes
import logging
from imager import combine_to_viewport
from module_loader import add_environment

"""
Pre-setting on Windows
"""
@add_environment("win32_init")
def init():
    os.system("color")
    logging.debug("Initialized for a Windows environment")

"""
This sets wallpapers on Windows.

:param files: A list of files to set as wallpapers
"""
@add_environment("win32_setter")
def set_wallpapers(files: list, displays: list):
    import winreg
    if len(files) > 1:
        logging.debug("Several monitors detected, going the hard route")
        desktop = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, winreg.KEY_ALL_ACCESS)
        wallpaper_style = winreg.SetValueEx(desktop, "WallpaperStyle", 0, winreg.REG_SZ, "5")
        desktop.Close()
        file = combine_to_viewport(displays, files)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, file, 0)
    else:
        logging.debug("Detected only one monitor, setting wallpaper simply")
        desktop = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, winreg.KEY_ALL_ACCESS)
        wallpaper_style = winreg.SetValueEx(desktop, "WallpaperStyle", 0, winreg.REG_SZ, "3")
        desktop.Close()
        ctypes.windll.user32.SystemParametersInfoW(20, 0, files[0] , 0)