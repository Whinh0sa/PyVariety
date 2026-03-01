import ctypes
import logging
import os
import platform
import sys
import winreg

logger = logging.getLogger(__name__)

# Constants for SystemParametersInfo
SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02

def set_wallpaper(image_path: str, style: str = "Fill") -> bool:
    """
    Sets the Windows desktop wallpaper and updates the registry to ensure persistence.
    
    :param image_path: Absolute path to the image file.
    :param style: "Center", "Tile", "Stretch", "Fit", "Fill", or "Span".
    :return: True if successful, False otherwise.
    """
    if platform.system() != "Windows":
        logger.error("OS is not Windows. Cannot set wallpaper via ctypes.")
        return False

    try:
        # Define wallpaper styling constants
        # style values: 0 = Center, 1 = Tile, 2 = Stretch, 6 = Fit, 10 = Fill, 22 = Span
        style_map = {
            "Center": ("0", "0"),
            "Tile": ("0", "1"),
            "Stretch": ("2", "0"),
            "Fit": ("6", "0"),
            "Fill": ("10", "0"),
            "Span": ("22", "0")
        }
        
        wallpaper_style, tile_wallpaper = style_map.get(style, ("10", "0"))

        # 1. Update the registry so it persists across reboots
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            r"Control Panel\Desktop", 
            0, 
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(registry_key, "WallpaperStyle", 0, winreg.REG_SZ, wallpaper_style)
        winreg.SetValueEx(registry_key, "TileWallpaper", 0, winreg.REG_SZ, tile_wallpaper)
        winreg.CloseKey(registry_key)
        
        # 2. Call SystemParametersInfoW to change the background immediately
        # ctypes.c_wchar_p specifies a wide-character string (necessary for Windows APIs)
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 
            0, 
            image_path, 
            SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
        )
        
        if result:
            logger.info(f"Successfully set wallpaper to {image_path}")
            return True
        else:
            logger.error("SystemParametersInfoW call failed.")
            return False

    except Exception as e:
        logger.error(f"Error setting wallpaper: {e}")
        return False

def toggle_autostart(enable: bool = True):
    """
    Adds or removes PyVariety from Windows Startup by modifying the Registry.
    We check if we are running as a compiled .exe to get the correct path.
    """
    if platform.system() != "Windows":
        return
        
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_path = sys.executable
        else:
            # Running as a normal python script (fallback)
            app_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "PyVariety"
        
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            key_path, 
            0, 
            winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
        )

        if enable:
            winreg.SetValueEx(registry_key, app_name, 0, winreg.REG_SZ, app_path)
            logger.info(f"Added PyVariety to startup registry ({app_path})")
        else:
            try:
                winreg.DeleteValue(registry_key, app_name)
                logger.info("Removed PyVariety from startup registry.")
            except FileNotFoundError:
                pass # Already removed
                
        winreg.CloseKey(registry_key)
    except Exception as e:
        logger.error(f"Could not toggle autostart in registry: {e}")

