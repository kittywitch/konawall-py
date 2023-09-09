import wx 
import wx.adv
import tempfile
from PIL import Image, ImageDraw
import os
import sys
import logging
import screeninfo
import tomllib
import subprocess
from environment import set_environment_wallpapers, detect_environment
from module_loader import import_dir, environment_handlers, source_handlers
from custom_print import kv_print

def create_icon():
    width = 128
    height = 128
    # Missing texture
    image = Image.new('RGB', (width, height), (0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, 0, width//2, height//2), fill=(255, 0, 255))
    dc.rectangle((width//2, height//2, width, height), fill=(255, 0, 255))
    # Write image to temporary file
    temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    image.save(temp.name)
    icon = wx.Icon()
    icon.CopyFromBitmap(wx.Bitmap(temp.name))
    return icon


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item

class Konawall(wx.adv.TaskBarIcon):
    def __init__(self, file_logger, console_logger):
        self.file_logger = file_logger
        self.console_logger = console_logger
        self.loaded = False
        wx.adv.TaskBarIcon.__init__(self)
        # Pre-setup initialization
        self.environment = detect_environment()
        self.automatic_item = None
        self.automatic_timer = wx.Timer(self, wx.ID_ANY)
        # Reload (actually load) the config
        self.reload()
        self.load_modules()

        self.automatic_timer.Start(self.seconds * 1000)
        # Set up the taskbar icon  
        self.SetIcon(create_icon(), "Konawall")
        self.create_menu()
        self.create_bindings()

    def automatic_item_state(self):
        if self.automatic:
            return "Disable Automatic"
        else:
            return "Enable Automatic"

    def load_modules(self):
        import_dir(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "sources"))
        kv_print("Loaded source handlers", ", ".join(source_handlers), level="debug")
        import_dir(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "environments"))
        kv_print("Loaded environment handlers", ", ".join(environment_handlers), level="debug")
    
    def read_config(self):
        # check if config file exists
        if os.path.isfile("config.toml"):
            with open("config.toml", "rb") as f:
                config = tomllib.load(f)
            for k, v in config.items():
                kv_print(f"Loaded {k}", v)
                setattr(self, k, v)
        else:
            dialog = wx.MessageDialog(
                None,
                "No config file found, using defaults.",
                "Konawall",
                wx.OK|wx.ICON_INFORMATION
            )
            dialog.ShowModal()
            dialog.Destroy()
            self.automatic = True
            self.seconds = 10*60
            self.tags = ["rating:s"]

    def create_menu(self):
        self.menu = wx.Menu()
        create_menu_item(self.menu, "Run", self.run)
        self.automatic_item = create_menu_item(self.menu, self.automatic_item_state(), self.toggle_automatic)
        create_menu_item(self.menu, "Edit Config", self.edit_config)
        self.menu.Append(wx.ID_EXIT, "Exit")

    def edit_config(self, event):
        kv_print("User is editing", "config.toml")
        # Check if we're on Windows, if so use Notepad
        if sys.platform == "win32":
           # I don't even know how to detect the default editor on Windows
           subprocess.call("notepad.exe config.toml")
        else:
            # Open config file in default editor
            subprocess.call(f"{os.environ['EDITOR']} config.toml")
        # When file is done being edited, reload config
        kv_print("User has edited", "config.toml")
        self.reload()

    def reload(self):
        if self.loaded: 
            kv_print("Reloading config from", "config.toml")
        else:
            kv_print("Loading config from", "config.toml")
        self.read_config()
        # Handle finding the log level
        if "file" in self.logging:
            file_log_level = getattr(logging, self.logging["file"])
        else:
            file_log_level = logging.INFO
        self.file_logger.setLevel(file_log_level)
        if "console" in self.logging:
            console_log_level = getattr(logging, self.logging["console"])
        else:
            console_log_level = logging.INFO
        self.console_logger.setLevel(console_log_level)
        # Finished loading
        self.loaded = True

        # Handle the automatic timer
        if self.automatic and self.automatic_timer.IsRunning():
            self.automatic_timer.Stop()
            self.automatic_timer.Start(self.seconds * 1000)
            self.menu.SetLabel(self.automatic_item.Id, self.automatic_item_state())
        elif not self.automatic and self.automatic_timer.IsRunning():
            self.automatic_timer.Stop()
            self.menu.SetLabel(self.automatic_item.Id, self.automatic_item_state())
     
    def toggle_automatic(self, event):
        self.automatic = not self.automatic
        if self.automatic:
            self.automatic_timer.Start(self.seconds * 1000)
        else:
            self.automatic_timer.Stop()
        self.menu.SetLabel(self.automatic_item.Id, self.automatic_item_state())

    def show_menu(self, event):
        self.PopupMenu(self.menu)

    def run(self, event):
        displays = screeninfo.get_monitors()
        count = len(displays)
        files = source_handlers[self.source](count, self.tags)
        set_environment_wallpapers(self.environment, files, displays)

    def create_bindings(self):
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.run)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self.show_menu)
        self.Bind(wx.EVT_TIMER, self.run, self.automatic_timer)

if __name__ == "__main__":
    file_logger = logging.FileHandler("app.log", mode="a")
    console_logger = logging.StreamHandler()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            console_logger,
            file_logger,
        ]
    )
    app = wx.App(False)
    Konawall(file_logger, console_logger)
    app.MainLoop()