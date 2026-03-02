import json
import logging
import os
import collections.abc
from pathlib import Path

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

APP_DIR = Path(os.path.expanduser("~")) / ".pyvariety"
CONFIG_FILE = APP_DIR / "config.json"
CACHE_DIR = APP_DIR / "cache"

DEFAULT_CONFIG = {
    "interval_amount": 5,
    "interval_unit": "minutes",
    "sources": ["unsplash", "wallhaven", "reddit", "local"],
    "local_paths": [
        str(Path.home() / "Pictures" / "Wallpapers"),
        str(Path.home() / "OneDrive" / "Pictures" / "WALLPAPERS")
    ],
    "favorites_folder": str(Path.home() / "Pictures" / "PyVariety_Favorites"),
    "fetch_folder": str(Path.home() / "Pictures" / "PyVariety_Fetched"),
    "effects": {
        "keep_original": True,
        "grayscale": False,
        "heavy_blur": False,
        "soft_blur": False,
        "oil_painting": False,
        "pointillism": False,
        "pixellate": False
    },
    "quotes": {
        "enabled": False,
        "change_interval_amount": 5,
        "change_interval_unit": "minutes",
        "text_color": "#FFFFFF",
        "font_name": "Arial",
        "font_size": 30,
        "shadow": True,
        "bg_color": "#000000",
        "bg_opacity": 50,
        "pos_x": 50,
        "pos_y": 50,
        "width": 50
    },
    "clock": {
        "enabled": False,
        "clock_font_name": "Arial",
        "clock_font_size": 70,
        "date_font_name": "Arial",
        "date_font_size": 30
    },
    "clipboard": {
        "enabled": False,
        "hosts": ["wallhaven.cc", "imgur.com", "reddit.com", "deviantart.com"]
    },
    "wallhaven_api_key": "",
    "reddit_subreddits": ["EarthPorn", "wallpaper", "Amoledbackgrounds", "MoviePosterPorn"],
    "autostart": False,
    "pause_on_fullscreen": True
}

def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def ensure_app_dirs():
    """Ensure that application directories exist."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    """Load configuration from JSON file or create a default one."""
    ensure_app_dirs()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Use deep update to ensure nested dictionaries like effects/quotes aren't overwritten shallowly
            import copy
            merged_config = copy.deepcopy(DEFAULT_CONFIG)
            merged_config = deep_update(merged_config, config)
            # Migration for old interval setting
            if "interval_minutes" in config and "interval_amount" not in config:
                merged_config["interval_amount"] = config["interval_minutes"]
                merged_config["interval_unit"] = "minutes"
            return merged_config
    except Exception as e:
        logger.error(f"Error loading config, using defaults: {e}")
        return DEFAULT_CONFIG

def save_config(config: dict):
    """Save configuration to JSON file."""
    ensure_app_dirs()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")

# Global config instance load
config = load_config()
