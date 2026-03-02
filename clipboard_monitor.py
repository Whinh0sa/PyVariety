import ctypes
import logging
import threading
import time
import os
import requests
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ClipboardMonitor:
    def __init__(self, config, set_wallpaper_callback):
        self.config = config
        self.set_wallpaper_callback = set_wallpaper_callback
        self.running = False
        self._thread = None
        self.last_clipboard = ""
        
    def _get_clipboard_text(self) -> str:
        """Reads text from Windows clipboard natively via ctypes."""
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        try:
            if not user32.OpenClipboard(0):
                return ""
            
            CF_UNICODETEXT = 13
            if user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                handle = user32.GetClipboardData(CF_UNICODETEXT)
                if handle:
                    locked = kernel32.GlobalLock(handle)
                    if locked:
                        text = ctypes.c_wchar_p(locked).value
                        kernel32.GlobalUnlock(handle)
                        return text or ""
        except Exception as e:
            # Clipboard errors are common (e.g., currently locked by another app)
            pass
        finally:
            user32.CloseClipboard()
        return ""

    def _download_and_set(self, url: str):
        logger.info(f"Clipboard Monitor detected valid image URL: {url}")
        
        fetch_folder_str = self.config.get("fetch_folder", str(Path.home() / "Pictures" / "PyVariety_Fetched"))
        fetch_folder = Path(fetch_folder_str)
        fetch_folder.mkdir(parents=True, exist_ok=True)
        
        try:
            resp = requests.get(url, stream=True, timeout=10)
            if resp.status_code == 200:
                filename = f"clipboard_{int(time.time())}.jpg"
                filepath = fetch_folder / filename
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
                        
                logger.info(f"Successfully downloaded clipboard image to {filepath}")
                self.set_wallpaper_callback(str(filepath.absolute()))
        except Exception as e:
            logger.error(f"Failed to download clipboard image {url}: {e}")

    def _loop(self):
        while self.running:
            try:
                clip_config = self.config.get("clipboard", {})
                if not clip_config.get("enabled", False):
                    time.sleep(2)
                    continue
                    
                text = self._get_clipboard_text().strip()
                if text and text != self.last_clipboard:
                    self.last_clipboard = text
                    
                    # Validate URL
                    if text.startswith("http://") or text.startswith("https://"):
                        try:
                            parsed = urlparse(text)
                            host = parsed.netloc.lower()
                            if host.startswith("www."):
                                host = host[4:]
                            
                            allowed_hosts = [h.lower() for h in clip_config.get("hosts", [])]
                            
                            if host in allowed_hosts or any(host.endswith("." + h) for h in allowed_hosts):
                                # Ensure it points to an image
                                if text.lower().split('?')[0].endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                                    threading.Thread(target=self._download_and_set, args=(text,), daemon=True).start()
                        except Exception:
                            pass
            except Exception as e:
                pass
            time.sleep(1.5)

    def start(self):
        if self.running: return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("Clipboard Monitor thread started.")
        
    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
            
    def update_config(self, config):
        self.config = config
