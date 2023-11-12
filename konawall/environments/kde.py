import subprocess
from konawall.module_loader import add_environment

"""
This sets the wallpaper on KDE.
"""
@add_environment("kde_setter")
def set_wallpapers(files: list, displays: list):
    for file in files:
        kde_script = f"""
        for (const desktop of desktops()) {{
            desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"]
            desktop.writeConfig("Image", "{file}")
        }}
        """
        subprocess.run(["qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", kde_script])