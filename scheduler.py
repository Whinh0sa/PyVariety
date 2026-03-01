import ctypes
import logging
import threading
import time
import schedule

from config import config

logger = logging.getLogger(__name__)

class WallpaperScheduler:
    def __init__(self, action_func, interval_minutes: int):
        """
        Initializes the background scheduler.
        :param action_func: The function to call when rotating wallpapers.
        :param interval_minutes: How often to rotate.
        """
        self.action_func = action_func
        self.interval_minutes = interval_minutes
        self.running = False
        self.paused = False
        self._thread = None
        
        # Pull performance toggle
        self.pause_on_fullscreen = config.get("features", {}).get("pause_on_fullscreen", True)
        
        # Initial schedule setup
        self._setup_schedule()

    def _setup_schedule(self):
        schedule.clear()
        schedule.every(self.interval_minutes).minutes.do(self._job)

    def _job(self):
        if self.paused:
            logger.info("Scheduler triggered, but rotation is user-paused.")
            return
            
        if self.pause_on_fullscreen and self._is_fullscreen():
            logger.info("Fullscreen application detected. Postponing rotation to save resources.")
            return
            
        logger.info("Scheduler triggered wallpaper rotation.")
        self.action_func()

    def set_interval(self, minutes: int):
        """Update the rotation interval without restarting the daemon."""
        self.interval_minutes = minutes
        self._setup_schedule()
        logger.info(f"Scheduler interval updated to {minutes} minutes.")

    def start(self):
        """Start the background daemon thread."""
        if self.running:
            return
            
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler thread started.")

    def _run_loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def _is_fullscreen(self) -> bool:
        """Detects if the foreground window is fullscreen using ctypes."""
        try:
            user32 = ctypes.windll.user32
            
            # Get screen resolution
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            # Get foreground window
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False
                
            # Get window bounds
            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.pointer(rect))
            
            w_width = rect.right - rect.left
            w_height = rect.bottom - rect.top
            
            # If the foreground window dimensions match the screen exactly
            if w_width >= screen_width and w_height >= screen_height:
                # Extra check to ensure we aren't confusing the desktop worker (Progman)
                # with a true fullscreen app like a game/video.
                cwbuf = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, cwbuf, 256)
                if cwbuf.value in ("WorkerW", "Progman"):
                    return False
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error checking fullscreen status: {e}")
            return False

    def stop(self):
        """Stop the background daemon thread."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("Scheduler thread stopped.")

    def pause(self):
        """Pause rotations."""
        self.paused = True
        logger.info("Wallpaper rotation paused.")

    def resume(self):
        """Resume rotations."""
        self.paused = False
        logger.info("Wallpaper rotation resumed.")
