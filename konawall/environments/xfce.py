import subprocess
from konawall.module_loader import add_environment
from konawall.imager import combine_to_viewport

@add_environment("xfce_setter")
def set_wallpapers(files: list, displays: list):
    file = combine_to_viewport(displays, files)
    command_for_last_image = ["xfconf-query", "--channel", "xfce4-desktop", "--list"]
    workspaces_command = subprocess.run(command_for_last_image, capture_output=True)
    workspaces_command_lines = workspaces_command.stdout.decode("utf-8").strip().split("\n")
    workspaces_command_wallpapers = [conf for conf in workspaces_command_lines if "last-image" in conf]
    set_command_base = ["xfconf-query", "-c", "xfce4-desktop", "-s", file.name, "-p"]
    for workspace_config in workspaces_command_wallpapers:
        set_command = set_command_base + [workspace_config]
        set_style_command = ["xfconf-query", "-c", "xfce4-desktop", "-s", "5", "-p"] + [workspace_config.replace("last-image", "image-style")]
        subprocess.run(set_style_command)
        subprocess.run(set_command)
