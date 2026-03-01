import json
import logging
import os
from pathlib import Path

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

APP_DIR = Path(os.path.expanduser("~")) / ".pyvariety"
CONFIG_FILE = APP_DIR / "config.json"
CACHE_DIR = APP_DIR / "cache"

DEFAULT_CONFIG = {
    "interval_minutes": 15,
    "sources": ["unsplash", "wallhaven", "reddit", "local"],
    "local_paths": [
        str(Path.home() / "Pictures" / "Wallpapers"),
        str(Path.home() / "OneDrive" / "Pictures" / "WALLPAPERS")
    ],
    "filters": {
        "blur": False,
        "blur_radius": 5,
        "grayscale": False,
        "color_overlay": None  # e.g., [255, 0, 0, 50] for red tint
    },
    "features": {
        "show_clock": False,
        "show_quote": False,
        "pause_on_fullscreen": True
    },
    "unsplash_query": "dark,movie stills,landscape",
    "wallhaven_query": "dark wallpapers,anime,Miles Morales,movie stills",
    "wallhaven_api_key": "",
    "reddit_subreddits": ["EarthPorn", "wallpaper", "Amoledbackgrounds", "MoviePosterPorn"],
    "autostart": False
}

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
            # Merge with default to ensure new keys exist
            merged_config = {**DEFAULT_CONFIG, **config}
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
