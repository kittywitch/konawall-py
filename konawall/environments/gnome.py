import subprocess
from konawall.module_loader import add_environment
from konawall.imager import combine_to_viewport

@add_environment("gnome_setter")
def set_wallpapers(files: list, displays: list):
    file = combine_to_viewport(displays, files)
    command = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{file.name}"]
    command = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", f"file://{file.name}"]
    subprocess.run(command)
