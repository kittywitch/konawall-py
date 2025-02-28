#!/usr/bin/env python
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
import importlib.metadata
from konawall.environment import set_environment_wallpapers, detect_environment
from konawall.module_loader import import_dir, environment_handlers, source_handlers
from konawall.custom_print import kv_print
from humanfriendly import format_timespan

class Konawall(wx.adv.TaskBarIcon):
    def __init__(self, version, file_logger, log_path):
        super().__init__()
        # Prevents it from closing before it has done any work on macOS
        if wx.Platform == "__WXMAC__" or wx.Platform == "__WXGTK__":
            self.hidden_frame = wx.Frame(None)
            self.hidden_frame.Hide()

        self.log_path = log_path
        self.config = {}
        self.wallpaper_rotation_counter = 0 
        self.file_logger = file_logger
        self.version = version
        self.title_string = f"Konawall - {version}"
        self.description_string = "A hopefully cross-platform service for fetching wallpapers and setting them."
        self.loaded_before = False
        self.current = []

        print(self.IsAvailable())
        print(self.IsOk())
        # Call the super function, make sure that the type is the statusitem for macOS
        wx.adv.TaskBarIcon.__init__(self, wx.adv.TBI_CUSTOM_STATUSITEM)

        # Detect environment and timer settings
        self.environment = detect_environment()
        self.toggle_wallpaper_rotation_menu_item = None
        self.wallpaper_rotation_timer = wx.Timer(self, wx.ID_ANY)

        # Reload (actually load) the config and modules.
        if wx.Platform == "__WXGTK__":
            from xdg_base_dirs import xdg_config_home
            self.config_path = os.path.join(xdg_config_home(), "konawall")
        if wx.Platform == "__WXMAC__":
            config_path_string = "~/Library/Application Support/konawall/"
            self.config_path = os.path.expanduser(config_path_string)
        elif wx.Platform == "__WXMSW__":
            config_path_string = "%APPDATA%\\konawall"
            self.config_path = os.path.expandvars(config_path_string)
        else:
            try:
                from xdg_base_dirs import xdg_config_home
                self.config_path = os.path.join(xdg_config_home(), "konawall")
            except:
                self.config_path = os.path.join(os.path.expanduser("~"), ".config", "konawall")
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)
        self.config_path = os.path.join(self.config_path, "config.toml")
        self.reload_config()
        self.import_modules()

        # Start the timer to run every second
        self.wallpaper_rotation_timer.Start(1000)

        # Set up the taskbar icon, menu, bindings, ...
        icon = self.generate_icon()
        self.SetIcon(icon, self.title_string)
        if self.environment in ["hyprland", "gnome"]:
            import pystray
            def setup(self):
                self.visible = True
            self.external_icon = pystray.Icon("Konawall - {version}", icon=self.generate_icon_bitmap(), menu=pystray.Menu(
                pystray.MenuItem("Rotate", self.rotate_wallpapers),
                pystray.MenuItem("Open URL for image", self.open_url),
                pystray.MenuItem("Open log", self.open_log),
                pystray.MenuItem("Toggle Rotation", self.toggle_timed_wallpaper_rotation, checked=lambda item: self.rotate),
                pystray.MenuItem("Quit",  self.close_program_menu_item)
            ))
            self.external_icon.run_detached(setup)
        self.hidden_frame.SetIcon(icon)
        self.create_menu()
        self.create_bindings()

        # Run the first time, manually
        self.rotate_wallpapers(None)

    def open_url(self, evt=None):
        for post in self.current:
            subprocess.call(["xdg-open", post["show_url"])

    def open_log(self, evt=None):
        subprocess.call(["xdg-open", self.log_path])

    # wxPython requires a wx.Bitmap, so we generate one from a PIL.Image
    def generate_icon_bitmap(self):
        width = 128
        height = 128

        # Missing texture style, magenta and black checkerboard
        image = Image.open(os.path.join(os.path.dirname(__file__), 'icon.png'))
        if "wxMSW" in wx.PlatformInfo:
            image = image.resize((16, 16))
        elif "wxGTK" in wx.PlatformInfo:
            image = image.resize((22, 22))
        return image

    def generate_icon(self):
        image = self.generate_icon_bitmap()
        # Write image to temporary file
        temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image.save(temp.name)

        # Convert to wxPython icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(temp.name))
        return icon

    def toggle_timed_wallpaper_rotation_status(self):
        return f"{'Dis' if self.rotate else 'En'}able Timer"

    # Load in our source and environment handlers
    def import_modules(self):
        import_dir(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "sources"))
        kv_print("Loaded source handlers", ", ".join(source_handlers), level="debug")
        import_dir(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "environments"))
        kv_print("Loaded environment handlers", ", ".join(environment_handlers), level="debug")
    
    # Load a TOML file's key-value pairs into our class
    def load_config(self):
        if os.path.isfile(self.config_path):
            # If the config file exists, load it as a dictionary into the config variable.
            with open(self.config_path, "rb") as f:
                config = tomllib.load(f)
                self.config = config
            # for every key-value pair in the config variable , set the corresponding attribute of our class to it
            for k, v in config.items():
                kv_print(f"Loaded {k}", v)
                setattr(self, k, v)
        else:
            # If there is no config file, get complainy.
            dialog = wx.MessageDialog(
                None,
                f"No config file found at {self.config_path}, using defaults.",
                self.title_string,
                wx.OK|wx.ICON_INFORMATION
            )
            dialog.ShowModal()
            dialog.Destroy()
            # Set some arbitrary defaults
            self.rotate = True
            self.source = "konachan"
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
        def create_info_item(menu, label, help=""):
            item = wx.MenuItem(menu, wx.ID_ANY, label)
            if wx.Platform == "__WXGTK__":
                menu.Bind(wx.EVT_MENU, (lambda x: x), id=item.GetId())
            else:
                item.Enable(False)
            menu.Append(item)
            return item
        def create_separator(menu):
            item = wx.MenuItem(menu, id=wx.ID_SEPARATOR, kind=wx.ITEM_SEPARATOR)
            menu.Append(item)
            return item
        
        # Create our Menu object
        self.menu = wx.Menu()

        # Program header
        self.header_menu_item = create_menu_item(
            self.menu,
            self.title_string,
            lambda event: self.create_message_dialog(f"{self.description_string}\n\nIf you need help with this, I'm @floofywitch on Discord and Telegram. ^^;"),
            self.description_string,
        )

        create_separator(self.menu)

        self.current_interval_menu_item = create_info_item(self.menu, f"Interval: {format_timespan(self.interval)}")

        # Time remaining for automatic wallpaper rotation
        self.timed_wallpaper_rotation_status_menu_item = create_info_item(self.menu, "Automatic wallpaper rotation disabled")

        create_separator(self.menu)

        # Change wallpapers
        create_menu_item(
            self.menu,
            "Rotate Wallpapers",
            self.rotate_wallpapers,
            "Fetch new wallpapers and set them as your wallpapers"
        )
        
        # Toggle automatic wallpaper rotation
        self.toggle_wallpaper_rotation_menu_item = create_menu_item(
            self.menu,
            self.toggle_timed_wallpaper_rotation_status(),
            self.toggle_timed_wallpaper_rotation,
            "Toggle the automatic wallpaper rotation timer"
        )

        create_separator(self.menu)
        create_menu_item(
            self.menu,
            "Open wallpaper URLs",
            self.open_url,
            "Open wallpaper URLs via xdg-open"
        )
        
        create_menu_item(
            self.menu,
            "Open log",
            self.open_log,
            "Open konawall log in editor"
        )

        create_separator(self.menu)

        # Interactive config editing
        create_menu_item(
            self.menu,
            "Edit Config",
            self.edit_config_menu_item,
            "Interactively edit the config file"
        )
        create_menu_item(
            self.menu,
            "Reload Config",
            self.reload_config_menu_item,
            "Reload the config file from disk"
        )
        create_separator(self.menu)
        # Exit
        create_menu_item(
            self.menu,
            "Exit",
            self.close_program_menu_item,
            "Quit the application"
        )

    def close_program_menu_item(self, event):
        wx.Exit()
    
    # Interactively edit the config file
    def edit_config_menu_item(self, event):
        kv_print("User is editing", self.config_path)
        # Check if we're on Windows, if so use Notepad
        if sys.platform == "win32":
           # I don't even know how to detect the default editor on Windows
           subprocess.call(f"notepad.exe {self.config_path}", shell=True)
        else:
            # Open config file in default editor
            subprocess.call(f"{os.environ['SHELL']} {os.environ['EDITOR']} {self.config_path}", shell=True)
        # When file is done being edited, reload config
        kv_print("User has edited", self.config_path)
        self.reload_config()

    # Reload the application
    def reload_config(self):
        kv_print(f"{'Rel' if self.loaded_before else 'L'}oading config from", self.config_path)
        self.load_config()
        
        # Handle finding the log level
        if "file" in self.logging:
            file_log_level = getattr(logging, self.logging["file"])
        else:
            file_log_level = logging.INFO
        self.file_logger.setLevel(file_log_level)

        if self.loaded_before == True:
            # If we're reloading, we need to make sure the timer and menu item reflect our current state.
            self.respect_timed_wallpaper_rotation_toggle()
            self.respect_current_interval_status()
            self.create_message_dialog("Config reloaded.")
        
        # Finished loading
        self.loaded_before = True
    
    def reload_config_menu_item(self, event):
        self.reload_config()


    def create_message_dialog(self, message):
        dialog = wx.MessageDialog(
            None,
            message,
            self.title_string,
            wx.OK|wx.ICON_INFORMATION
        )
        # Set the icon of the dialog to the same as the taskbar icon
        dialog.ShowModal()
        dialog.Destroy()
 
    
    # Update the menu item of the current interval display to read correctly
    def respect_current_interval_status(self):
        if self.IsAvailable:
            self.current_interval_menu_item.SetItemLabel(f"Rotation interval: {format_timespan(self.interval)}")

    # Set whether to rotate wallpapers automatically or not
    def toggle_timed_wallpaper_rotation(self, event):
        self.rotate = not self.rotate
        self.respect_timed_wallpaper_rotation_toggle()
    
    # Update the timer and the menu item to reflect our current state
    def respect_timed_wallpaper_rotation_toggle(self): 
        if self.rotate and not self.wallpaper_rotation_timer.IsRunning():
            self.wallpaper_rotation_timer.Start(1000)
        elif not self.rotate and self.wallpaper_rotation_timer.IsRunning():
            self.wallpaper_rotation_timer.Stop()
            # Set the time left counter to show that it is disabled
            if self.IsAvailable:
                self.current_interval_menu_item.SetItemLabel(f"Automatic wallpaper rotation disabled")
        
        # Update the menu item for the toggle
        if self.IsAvailable:
            self.toggle_wallpaper_rotation_menu_item.SetItemLabel(self.toggle_timed_wallpaper_rotation_status())

    # Update wallpaper rotation time left counter
    def respect_timed_wallpaper_rotation_status(self):
        if self.IsAvailable:
            self.timed_wallpaper_rotation_status_menu_item.SetItemLabel(f"Next rotation: {format_timespan(self.interval - self.wallpaper_rotation_counter)} remaining")

    # Perform the purpose of the application; get new wallpaper media and set 'em.
    def rotate_wallpapers(self, event):
        displays = screeninfo.get_monitors()
        count = len(displays)
        files, self.current = source_handlers[self.source](count, self.tags, self.config)
        set_environment_wallpapers(self.environment, files, displays)

    # For macOS
    def CreatePopupMenu(self):
        self.PopupMenu(self.menu)

    # For everybody else who has bindable events
    def show_popup_menu(self, event):
        self.PopupMenu(self.menu)
    
    # Every second, check if the wallpaper rotation timer has ticked over
    def handle_timer_tick(self, event):
        if self.wallpaper_rotation_counter >= self.interval:
            # If it has, run the fetch and set mechanism
            self.rotate_wallpapers(None)
            self.wallpaper_rotation_counter = 0
        else:
            self.wallpaper_rotation_counter += 1
        # Update the time left counter
        self.respect_timed_wallpaper_rotation_status()

    # When the user clicks on the taskbar icon or menu item, run the fetch and set mechanism
    # then reset the wallpaper rotation timer
    def handle_manual_wallpaper_rotation(self, event):
        self.rotate_wallpapers(None)
        self.wallpaper_rotation_counter = 0

    # Bind application events
    def create_bindings(self):
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.handle_manual_wallpaper_rotation)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self.show_popup_menu)

        # Implement the wallpaper rotation timer
        self.Bind(wx.EVT_TIMER, self.handle_timer_tick, self.wallpaper_rotation_timer)

def main():
    try:
        version = f'v{importlib.metadata.version("konawall-py")}'
    except:
        version = "testing version"

    if wx.Platform == "__WXGTK__":
        from xdg_base_dirs import xdg_data_home
        log_path = os.path.join(xdg_data_home(), "konawall") 
    if wx.Platform == "__WXMAC__":
        log_path_string = "~/Library/Application Support/konawall"
        log_path = os.path.expanduser(log_path_string)
    elif wx.Platform == "__WXMSW__":
        log_path_string = "%APPDATA%\\konawall"
        log_path = os.path.expandvars(log_path_string)
    else:
        try:
            from xdg_base_dirs import xdg_data_home
            log_path = os.path.join(xdg_data_home(), "konawall") 
        except:
            log_path = os.path.join(os.path.expanduser("~"), ".config", "konawall")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_path = os.path.join(log_path, "konawall.log")
    file_logger = logging.FileHandler(log_path, mode="a")
    console_logger = logging.StreamHandler()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            console_logger,
            file_logger,
        ]
    )
    app = wx.App(redirect=False)
    app.SetExitOnFrameDelete(False)
    Konawall(version, file_logger, log_path)
    app.MainLoop()

if __name__ == "__main__":
    main()
