import ctypes
import logging
import threading
import time
import schedule

from config import config

logger = logging.getLogger(__name__)

class WallpaperScheduler:
    def __init__(self, action_func, interval_amount: int, interval_unit: str):
        """
        Initializes the background scheduler.
        :param action_func: The function to call when rotating wallpapers.
        :param interval_amount: How often to rotate.
        :param interval_unit: Unit of time ('minutes', 'hours', 'days').
        """
        self.action_func = action_func
        self.interval_amount = interval_amount
        self.interval_unit = interval_unit
        self.running = False
        self.paused = False
        self._thread = None
        
        # Pull performance toggle
        self.pause_on_fullscreen = config.get("pause_on_fullscreen", True)
        
        # Initial schedule setup
        self._setup_schedule()

    def _setup_schedule(self):
        schedule.clear()
        amount = self.interval_amount
        unit = self.interval_unit.lower()
        
        if unit == 'minutes' or unit == 'minute':
            schedule.every(amount).minutes.do(self._job)
        elif unit == 'hours' or unit == 'hour':
            schedule.every(amount).hours.do(self._job)
        elif unit == 'days' or unit == 'day':
            schedule.every(amount).days.do(self._job)
        else:
            # Fallback
            schedule.every(amount).minutes.do(self._job)

    def _job(self):
        if self.paused:
            logger.info("Scheduler triggered, but rotation is user-paused.")
            return
            
        if self.pause_on_fullscreen and self._is_fullscreen():
            logger.info("Fullscreen application detected. Postponing rotation to save resources.")
            return
            
        logger.info("Scheduler triggered wallpaper rotation.")
        self.action_func()

    def set_interval(self, amount: int, unit: str):
        """Update the rotation interval without restarting the daemon."""
        self.interval_amount = amount
        self.interval_unit = unit
        self._setup_schedule()
        logger.info(f"Scheduler interval updated to {amount} {unit}.")

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
