import logging
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

logger = logging.getLogger(__name__)

def create_icon_image():
    """Generates a simple colorful placeholder icon for the system tray."""
    width, height = 64, 64
    image = Image.new('RGB', (width, height), (30, 30, 30))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, width - 16, height - 16), fill=(0, 150, 255))
    dc.ellipse((24, 24, width - 24, height - 24), fill=(255, 100, 100))
    return image

class TrayIcon:
    def __init__(self, rotate_action, pause_action, resume_action, settings_action, quit_action, is_paused=False):
        """
        :param rotate_action: Callback string to trigger immediate wallpaper change.
        :param pause_action: Callback string to pause rotation.
        :param resume_action: Callback string to resume rotation.
        :param settings_action: Callback string to open settings or config.
        :param quit_action: Callback to hard exit the application thread.
        """
        self.rotate_action = rotate_action
        self.pause_action = pause_action
        self.resume_action = resume_action
        self.settings_action = settings_action
        self.quit_action = quit_action
        self.is_paused = is_paused
        self.icon = None

    def _on_change_now(self, icon, item):
        logger.info("Tray Action: Change Now clicked.")
        self.rotate_action()

    def _on_toggle_pause(self, icon, item):
        self.is_paused = not self.is_paused
        if self.is_paused:
            logger.info("Tray Action: Pause clicked.")
            self.pause_action()
        else:
            logger.info("Tray Action: Resume clicked.")
            self.resume_action()
            
        # Re-render menu to update Pause/Resume label
        self.icon.update_menu()

    def _on_settings(self, icon, item):
        logger.info("Tray Action: Settings clicked.")
        self.settings_action()

    def _on_quit(self, icon, item):
        logger.info("Tray Action: Quit clicked.")
        icon.stop()
        if hasattr(self, 'quit_action'):
            self.quit_action()

    def _get_menu_items(self):
        """Dynamic menu items to handle pause state toggling."""
        pause_label = "Resume Rotation" if self.is_paused else "Pause Rotation"
        
        return pystray.Menu(
            item('Change Now', self._on_change_now, default=True),
            pystray.Menu.SEPARATOR,
            item(pause_label, self._on_toggle_pause),
            item('Open Settings', self._on_settings),
            pystray.Menu.SEPARATOR,
            item('Quit', self._on_quit)
        )

    def run(self):
        """Starts the blocking system tray loop."""
        self.icon = pystray.Icon(
            "PyVariety", 
            create_icon_image(), 
            "PyVariety Wallpaper Manager",
            menu=self._get_menu_items()
        )
        self.icon.run()
