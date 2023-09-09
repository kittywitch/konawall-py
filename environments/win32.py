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
    logging.info("Initialized for a Windows environment")

"""
This sets wallpapers on Windows.

:param files: A list of files to set as wallpapers
"""
@add_environment("win32_setter")
def set_wallpapers(files: list, displays: list):
    if len(files) > 1:
        logging.info("Several monitors detected, going the hard route")
        file = combine_to_viewport(displays, files)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, file, 0)
    else:
        logging.info("Detected only one monitor, setting wallpaper simply")
        ctypes.windll.user32.SystemParametersInfoW(20, 0, files[0] , 0)