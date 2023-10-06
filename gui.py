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
from humanfriendly import format_timespan

class Konawall(wx.adv.TaskBarIcon):
    def __init__(self, file_logger):
        # Prevents it from closing before it has done any work on macOS
        if wx.Platform == "__WXMAC__":
            self.hidden_frame = wx.Frame(None)
            self.hidden_frame.Hide()

        self.wallpaper_rotation_counter = 0 
        self.file_logger = file_logger
        self.loaded_before = False

        # Call the super function, make sure that the type is the statusitem for macOS
        wx.adv.TaskBarIcon.__init__(self, wx.adv.TBI_CUSTOM_STATUSITEM)

        # Detect environment and timer settings
        self.environment = detect_environment()
        self.toggle_wallpaper_rotation_item = None
        self.wallpaper_rotation_timer = wx.Timer(self, wx.ID_ANY)

        # Reload (actually load) the config and modules.
        self.reload()
        self.load_modules()

        # Start the timer to run every second
        self.wallpaper_rotation_timer.Start(1000)

        # Set up the taskbar icon, menu, bindings, ...
        icon = self.generate_icon()
        self.SetIcon(icon, "Konawall")
        self.create_menu()
        self.create_bindings()

        # Run the first time, manually
        self.run(None)

    # wxPython requires a wx.Bitmap, so we generate one from a PIL.Image
    def generate_icon(self):
        width = 128
        height = 128

        # Missing texture style, magenta and black checkerboard
        image = Image.new('RGB', (width, height), (0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.rectangle((0, 0, width//2, height//2), fill=(255, 0, 255))
        dc.rectangle((width//2, height//2, width, height), fill=(255, 0, 255))
        if "wxMSW" in wx.PlatformInfo:
            image = image.Scale(16, 16)
        elif "wxGTK" in wx.PlatformInfo:
            image = image.Scale(22, 22)

        # Write image to temporary file
        temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image.save(temp.name)

        # Convert to wxPython icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(temp.name))
        return icon 

    def toggle_wallpaper_rotation_status(self):
        return f"{'Dis' if self.rotate else 'En'}able Timer"

    # Load in our source and environment handlers
    def load_modules(self):
        import_dir(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "sources"))
        kv_print("Loaded source handlers", ", ".join(source_handlers), level="debug")
        import_dir(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "environments"))
        kv_print("Loaded environment handlers", ", ".join(environment_handlers), level="debug")
    
    # Load a TOML file's key-value pairs into our class
    def read_config(self):
        if os.path.isfile("config.toml"):
            # If the config file exists, load it as a dictionary into the config variable.
            with open("config.toml", "rb") as f:
                config = tomllib.load(f)
            # for every key-value pair in the config variable , set the corresponding attribute of our class to it
            for k, v in config.items():
                kv_print(f"Loaded {k}", v)
                setattr(self, k, v)
        else:
            # If there is no config file, get complainy.
            dialog = wx.MessageDialog(
                None,
                "No config file found, using defaults.",
                "Konawall",
                wx.OK|wx.ICON_INFORMATION
            )
            dialog.ShowModal()
            dialog.Destroy()
            # Set some arbitrary defaults
            self.rotate = True
            self.interval = 10*60
            self.tags = ["rating:s"]
            self.logging = {}
            self.logging["file"] = "INFO"

    # Create the menu
    def create_menu(self):
        # Make it easier to define menu items
        def create_menu_item(menu, label, func, help="", kind=wx.ITEM_NORMAL):
            item = wx.MenuItem(menu, wx.ID_ANY, label)
            menu.Bind(wx.EVT_MENU, func, id=item.GetId())
            menu.Append(item)
            return item
        def create_separator(menu):
            item = wx.MenuItem(menu, id=wx.ID_SEPARATOR, kind=wx.ITEM_SEPARATOR)
            menu.Append(item)
            return item
        
        # Create our Menu object
        self.menu = wx.Menu()

        # Time remaining for automatic wallpaper rotation
        self.wallpaper_rotation_status = wx.MenuItem(self.menu, -1, "Time remaining")
        self.wallpaper_rotation_status.Enable(False)
        self.menu.Append(self.wallpaper_rotation_status)

        create_separator(self.menu)

        # Change wallpapers
        create_menu_item(
            self.menu,
            "Rotate Wallpapers",
            self.run,
            "Fetch new wallpapers and set them as your wallpapers"
        )

        # Toggle automatic wallpaper rotation
        self.toggle_wallpaper_rotation_item = create_menu_item(
            self.menu,
            self.toggle_wallpaper_rotation_status(),
            self.toggle_wallpaper_rotation,
            "Toggle the automatic wallpaper rotation timer"
        )

        create_separator(self.menu)

        # Interactive config editing
        create_menu_item(
            self.menu,
            "Edit Config",
            self.edit_config,
            "Interactively edit the config file"
        )
        # Exit
        create_menu_item(
            self.menu,
            "Exit",
            self.Destroy,
            "Quit the application"
        )

    # Interactively edit the config file
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

    # Reload the application
    def reload(self):
        kv_print(f"{'Rel' if self.loaded_before else 'L'}oading config from", "config.toml")
        self.read_config()
        
        # Handle finding the log level
        if "file" in self.logging:
            file_log_level = getattr(logging, self.logging["file"])
        else:
            file_log_level = logging.INFO
        self.file_logger.setLevel(file_log_level)

        if self.loaded_before == True:
            # If we're reloading, we need to make sure the timer and menu item reflect our current state.
            self.respect_wallpaper_rotation_toggle()
        
        # Finished loading
        self.loaded_before = True
    

    # Set whether to rotate wallpapers automatically or not
    def toggle_wallpaper_rotation(self, event):
        self.rotate = not self.rotate 
        self.respect_wallpaper_rotation_toggle()

    # Update the timer and the menu item to reflect our current state
    def respect_wallpaper_rotation_toggle(self): 
        if self.rotate and not self.wallpaper_rotation_timer.IsRunning():
            self.wallpaper_rotation_timer.Start(1000)
        elif not self.rotate and self.wallpaper_rotation_timer.IsRunning():
            self.wallpaper_rotation_timer.Stop()
            # Set the time left counter to show that it is disabled
            self.wallpaper_rotation_status.SetItemLabel(f"Automatic wallpaper rotation disabled")
        
        # Update the menu item for the toggle
        self.toggle_wallpaper_rotation_item.SetItemLabel(self.toggle_wallpaper_rotation_status())

    # Update wallpaper rotation time left counter
    def respect_wallpaper_rotation_status(self):
        self.wallpaper_rotation_status.SetItemLabel(f"{format_timespan(self.interval - self.wallpaper_rotation_counter)} remaining")

    # Perform the purpose of the application; get new wallpaper media and set 'em.
    def run(self, event):
        displays = screeninfo.get_monitors()
        count = len(displays)
        files = source_handlers[self.source](count, self.tags)
        set_environment_wallpapers(self.environment, files, displays)

    # For macOS
    def CreatePopupMenu(self):
        self.PopupMenu(self.menu)

    # For everybody else who has bindable events
    def show_menu(self, event):
        self.PopupMenu(self.menu)
    
    # Every second, check if the wallpaper rotation timer has ticked over
    def handle_timer_tick(self, event):
        if self.wallpaper_rotation_counter >= self.interval:
            # If it has, run the fetch and set mechanism
            self.run(None)
            self.wallpaper_rotation_counter = 0
        else:
            self.wallpaper_rotation_counter += 1
        # Update the time left counter
        self.respect_wallpaper_rotation_status()

    # Bind application events
    def create_bindings(self):
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.run)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self.show_menu)

        # Implement the wallpaper rotation timer
        self.Bind(wx.EVT_TIMER, self.handle_timer_tick, self.wallpaper_rotation_timer)

def main():
    file_logger = logging.FileHandler("app.log", mode="a")
    #console_logger = logging.StreamHandler()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            #console_logger,
            file_logger,
        ]
    )
    app = wx.App(redirect=False)
    app.SetExitOnFrameDelete(False)
    Konawall(file_logger)
    app.MainLoop()

if __name__ == "__main__":
    main()