import ctypes
import logging
import os
import sys
import threading
from pathlib import Path

from config import config, CONFIG_FILE, load_config
from fetcher import Fetcher
from processor import process_image
from setter import set_wallpaper
from scheduler import WallpaperScheduler
from tray import TrayIcon
from clipboard_monitor import ClipboardMonitor
import gui

logger = logging.getLogger(__name__)

class PyVarietyApp:
    def __init__(self):
        self.config = config
        self.fetcher = Fetcher(self.config)
        
        # Initialize the background scheduler
        self.scheduler = WallpaperScheduler(
            action_func=self.change_wallpaper,
            interval_amount=self.config.get("interval_amount", 5),
            interval_unit=self.config.get("interval_unit", "minutes")
        )
        
        # Track active wallpaper to prevent redundant processing if re-triggered
        self.current_wallpaper = None
        
        # Initialize Clipboard Monitor
        self.clipboard_monitor = ClipboardMonitor(self.config, self.set_specific_wallpaper)

    def _get_active_wallpaper_path(self):
        """Returns the currently active processed wallpaper or None."""
        if hasattr(self.fetcher.playlist, 'current') and self.fetcher.playlist.current:
            return self.fetcher.playlist.current
        return None

    def _handle_login_screen_copy(self, final_path):
        """Mirrors the active processed image to a public login directory if enabled."""
        import shutil
        cust = self.config.get("customize", {})
        if cust.get("login_screen_support", False):
            target_dir = cust.get("login_screen_folder", "")
            if target_dir:
                try:
                    os.makedirs(target_dir, exist_ok=True)
                    # We always overwrite the same file name so LightDM/Lockscreen can target a static path statically
                    target_path = os.path.join(target_dir, "variety_login_bg.jpg")
                    shutil.copy2(final_path, target_path)
                    logger.info(f"Mirrored active wallpaper to login screen directory: {target_dir}")
                except Exception as e:
                    logger.error(f"Failed to copy to login screen folder: {e}")

    def set_specific_wallpaper(self, filepath: str):
        """Processes and sets a specific image file instead of pulling from the playlist."""
        logger.info(f"Setting specific wallpaper from: {filepath}")
        if not os.path.exists(filepath):
            return
            
        processed_path = os.path.join(
            os.path.dirname(filepath), 
            "processed_" + os.path.basename(filepath)
        )
        
        final_path = process_image(filepath, self.config, processed_path)
        success = set_wallpaper(final_path)
        if success:
            self.current_wallpaper = final_path
            self._handle_login_screen_copy(final_path)
            logger.info("Specific wallpaper set successfully.")
            if hasattr(self, 'tray') and self.tray and self.tray.icon:
                self.tray.icon.update_menu()
                
    def change_wallpaper(self):
        """Core logic to fetch, process, and set a new wallpaper."""
        logger.info("Initiating wallpaper change sequence...")
        
        # 1. Fetch
        image_path = self.fetcher.get_next_wallpaper()
        if not image_path:
            logger.warning("Fetcher could not find any wallpapers!")
            return

        # 2. Process (Apply filters)
        processed_path = os.path.join(
            os.path.dirname(image_path), 
            "processed_" + os.path.basename(image_path)
        )
        
        # Only process if we need to
        final_path = process_image(image_path, self.config, processed_path)
        
        # 3. Set Wallpaper
        success = set_wallpaper(final_path)
        if success:
            self.current_wallpaper = final_path
            self._handle_login_screen_copy(final_path)
            logger.info("Wallpaper update sequence complete.")
            if self.tray and self.tray.icon:
                self.tray.icon.update_menu()
        else:
            logger.error("Failed to set wallpaper.")

    def previous_wallpaper(self):
        """Rewinds the playlist to the previous wallpaper."""
        logger.info("Reverting to previous wallpaper...")
        img_path = self.fetcher.playlist.previous_image()
        if img_path:
            processed_path = os.path.join(os.path.dirname(img_path), "processed_" + os.path.basename(img_path))
            final_path = process_image(img_path, self.config, processed_path)
            if final_path:
                set_wallpaper(final_path)
                self.current_wallpaper = final_path
                self._handle_login_screen_copy(final_path)
                if self.tray and self.tray.icon:
                    self.tray.icon.update_menu()
                    
    def favorite_wallpaper(self):
        """Copies the current active wallpaper to the configured Favorites folder."""
        import shutil
        active_path = self._get_active_wallpaper_path()
        if not active_path or not os.path.exists(active_path):
            logger.warning("No active wallpaper found to favorite.")
            return
            
        fav_folder = Path(self.config.get("favorites_folder", str(Path.home() / "Pictures" / "PyVariety_Favorites")))
        fav_folder.mkdir(parents=True, exist_ok=True)
        
        try:
            filename = os.path.basename(active_path)
            if filename.startswith("processed_"):
                filename = filename.replace("processed_", "", 1)
            
            target_path = fav_folder / filename
            shutil.copy2(active_path, target_path)
            logger.info(f"Favorited wallpaper to {target_path}")
        except Exception as e:
            logger.error(f"Failed to favorite wallpaper: {e}")

    def trash_wallpaper(self):
        """Deletes the current wallpaper from disk and skips to the next one."""
        active_path = self._get_active_wallpaper_path()
        if not active_path or not os.path.exists(active_path):
            logger.warning("No active wallpaper found to trash.")
            return
            
        try:
            os.remove(active_path)
            logger.info(f"Trashed wallpaper: {active_path}")
            
            processed_path = os.path.join(os.path.dirname(active_path), f"processed_{os.path.basename(active_path)}")
            if os.path.exists(processed_path):
                os.remove(processed_path)
                
            self.change_wallpaper()
        except Exception as e:
            logger.error(f"Failed to trash wallpaper: {e}")

    def open_settings(self):
        """Launch the CustomTkinter GUI."""
        def on_gui_close():
            # Refresh config dynamically after GUI save
            from config import load_config
            self.config = load_config()
            self.scheduler.set_interval(
                self.config.get("interval_amount", 5),
                self.config.get("interval_unit", "minutes")
            )
            self.fetcher = Fetcher(self.config)
            logger.info("Config dynamically reloaded from GUI.")
            
        # Pystray blocks the thread it runs on. CustomTkinter strictly requires running on the Main Thread.
        # We need to run pystray in a background thread OR spawn the GUI in a new process/thread.
        # We start tkinter on a new thread properly by isolating it if possible, but ctk complains.
        # Safest way: Run pystray in a daemon thread, let main.py stay alive with a while loop,
        # but since tray is running, we can trigger an event or launch CTK safely if we dispatch it.
        # ACTUALLY: CustomTkinter must run on the main thread.
        # So we use a threading Event to signal the main loop to open the GUI.
        logger.info("Signaling main thread to open Settings GUI.")
        self.gui_event.set()

    def run(self):
        """Start the application and block on the tray icon loop or GUI loop."""
        logger.info("Starting PyVariety...")
        
        # Do an initial fetch & set immediately on startup
        threading.Thread(target=self.change_wallpaper, daemon=True).start()
        
        # Start background scheduling daemon
        self.scheduler.start()
        
        # Start clipboard daemon
        self.clipboard_monitor.start()
        
        # Event to signal main thread to open GUI
        self.gui_event = threading.Event()
        
        # Initialize system tray UI
        self.tray = TrayIcon(
            rotate_action=self.change_wallpaper,
            previous_action=self.previous_wallpaper,
            favorite_action=self.favorite_wallpaper,
            trash_action=self.trash_wallpaper,
            pause_action=self.scheduler.pause,
            resume_action=self.scheduler.resume,
            settings_action=self.open_settings,
            quit_action=self.quit_app,
            app_ref=self,
            is_paused=False
        )
        
        # Run Tray on a background thread!
        tray_thread = threading.Thread(target=self.tray.run, daemon=True)
        tray_thread.start()
        
        try:
            # Main thread loop
            while True:
                # Wait for the tray thread to signal a GUI open
                # Use a timeout so we can still catch KeyboardInterrupts
                if self.gui_event.wait(timeout=1.0):
                    self.gui_event.clear()
                    logger.info("Main thread launching CustomTkinter GUI.")
                    # Launch GUI. This will block the main thread until the window closes.
                    self.open_settings_blocking()
        except KeyboardInterrupt:
            logger.info("Received exit signal.")
            self.quit_app()

    def quit_app(self):
        """Gracefully shuts down all threads and loops."""
        logger.info("Shutting down PyVariety...")
        self.scheduler.stop()
        self.clipboard_monitor.stop()
        if hasattr(self, 'tray') and self.tray and self.tray.icon:
            self.tray.icon.stop()
            
        # Hard exit to bypass tkinter mainloop lock if it's hanging
        os._exit(0)

    def open_settings_blocking(self):
        def on_gui_close():
            from config import load_config
            self.config = load_config()
            self.scheduler.set_interval(
                self.config.get("interval_amount", 5),
                self.config.get("interval_unit", "minutes")
            )
            self.fetcher = Fetcher(self.config)
            logger.info("Config dynamically reloaded from GUI.")
            
        gui.open_gui(on_close_callback=on_gui_close)

mutex = None
def enforce_single_instance():
    """Ensures only one instance of PyVariety runs at a time securely using a Kernel32 Mutex."""
    global mutex
    mutex_name = "PyVariety_SingleInstance_Mutex_Active"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()
    if last_error == 183: # ERROR_ALREADY_EXISTS
        logger.error("PyVariety is already running. Exiting redundant instance.")
        sys.exit(0)

if __name__ == "__main__":
    enforce_single_instance()
    app = PyVarietyApp()
    app.run()
