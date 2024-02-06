import subprocess
import dbus
from konawall.module_loader import add_environment

# https://powersnail.com/2023/set-plasma-wallpaper/

SCRIPT_GET_DESKTOPS = """
function getDesktops() {
    return desktops()
        .filter(d => d.screen != -1)
        .sort((a, b) => screenGeometry(a.screen).left - screenGeometry(b.screen).left);
}
"""

SCRIPT_SET_WALLPAPER = """
function setWallpaper(desktop, path) {
    desktop.wallpaperPlugin = "org.kde.image"
    desktop.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General")
    desktop.writeConfig("Image", path)
}
"""

SCRIPT_ALL = f"""
{SCRIPT_GET_DESKTOPS}
{SCRIPT_SET_WALLPAPER}
const imageList = IMAGE_LIST;
getDesktops().forEach((desktop, i) => setWallpaper(desktop, imageList[i % imageList.length]));
"""


SCRIPT_ONE = f"""
{SCRIPT_GET_DESKTOPS}
{SCRIPT_SET_WALLPAPER}
setWallpaper(getDesktops()[DESKTOP_ID], IMAGE);
"""
"""
This sets the wallpaper on KDE.
"""

def quote(s):
    return "'" + s + "'"

def plasma_dbus():
    bus = dbus.SessionBus()
    plasma = dbus.Interface(
        bus.get_object("org.kde.plasmashell", "/PlasmaShell"), dbus_interface="org.kde.PlasmaShell"
    )
    return plasma


@add_environment("kde_setter")
def set_wallpapers(files: list, displays: list):
    image_list_string = "[" + ",".join(quote(p) for p in files) + "]"
    script = SCRIPT_ALL.replace("IMAGE_LIST", image_list_string)
    plasma_dbus().evaluateScript(script)