import json
import logging
import os
import random
import time
from pathlib import Path
from typing import List, Optional
import requests

from config import CACHE_DIR

logger = logging.getLogger(__name__)

def fisher_yates_shuffle(items: List) -> List:
    """Implementation of Fisher-Yates (Knuth) Shuffle algorithm. Returns a new shuffled list."""
    shuffled = items.copy()
    n = len(shuffled)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled

class Playlist:
    """Manages the queue of images to ensure non-repeating sequences."""
    def __init__(self):
        self.queue: List[str] = []
        
    def populate(self, items: List[str]):
        """Populates and shuffles the queue using Fisher-Yates."""
        self.queue = fisher_yates_shuffle(items)
        
    def next_image(self) -> Optional[str]:
        if not self.queue:
            return None
        return self.queue.pop(0)
    
    def is_empty(self) -> bool:
        return len(self.queue) == 0

class Fetcher:
    """Fetches images from multiple sources based on config."""
    def __init__(self, config: dict):
        self.config = config
        self.sources = config.get("sources", [])
        self.playlist = Playlist()
        
    def get_next_wallpaper(self) -> Optional[str]:
        """Returns the absolute path to the next wallpaper image."""
        if self.playlist.is_empty():
            self.refresh_playlist()
            
        return self.playlist.next_image()

    def refresh_playlist(self):
        """Fetches images from all active sources to rebuild the playlist."""
        images = []
        
        if "local" in self.sources:
            images.extend(self.fetch_local_images())
            
        # Due to API constraints, we might just fetch one external image and append to front/back,
        # or cache some items. In PyVariety, fetching external APIs directly on rotation
        # happens when the cache runs out.
        
        if "unsplash" in self.sources:
            path = self.fetch_unsplash()
            if path:
                images.append(path)
                
        if "wallhaven" in self.sources:
            path = self.fetch_wallhaven()
            if path:
                images.append(path)
                
        if "reddit" in self.sources:
            path = self.fetch_reddit()
            if path:
                images.append(path)
                
        if "apod" in self.sources:
            path = self.fetch_apod()
            if path:
                images.append(path)
                
        # If APIs crashed or returned nothing, heavily rely on local + previously cached images
        if not images:
            logger.warning("No new images found from sources. Falling back to entire local cache folder.")
            images.extend(self._get_all_cached_images())
                
        # Shuffle immediately
        self.playlist.populate(images)

    def _get_all_cached_images(self) -> List[str]:
        """Returns all previously downloaded images from the cache dir."""
        images = []
        if CACHE_DIR.exists():
            for file in CACHE_DIR.rglob("*"):
                if file.is_file() and file.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"} and not file.name.startswith("processed_"):
                    images.append(str(file.absolute()))
        return images

    def fetch_local_images(self) -> List[str]:
        """Scans local directories for images."""
        extensions = {".jpg", ".jpeg", ".png", ".bmp"}
        images = []
        dirs = self.config.get("local_paths", [])
        
        for directory in dirs:
            path = Path(directory)
            if not path.exists():
                continue
            
            for file in path.rglob("*"):
                if file.is_file() and file.suffix.lower() in extensions and not file.name.startswith("processed_"):
                    images.append(str(file.absolute()))
                    
        return images

    def fetch_unsplash(self) -> Optional[str]:
        """Downloads a random Unsplash image."""
        query = self.config.get("unsplash_query", "landscape,nature")
        url = f"https://source.unsplash.com/random/1920x1080/?{query}"
        return self.download_image(url, "unsplash")
        
    def fetch_wallhaven(self) -> Optional[str]:
        """Downloads a random high-quality Wallhaven image."""
        query = self.config.get("wallhaven_query", "nature")
        api_key = self.config.get("wallhaven_api_key", "")
        
        # categories: 100 (General), 010 (Anime), 001 (People) - '110' is general+anime
        # purity: 100 (SFW)
        url = f"https://wallhaven.cc/api/v1/search?q={query}&categories=110&purity=100&sorting=random&resolutions=1920x1080"
        if api_key:
            url += f"&apikey={api_key}"
            
        try:
            # Wallhaven limits random queries severely. We use a 5s timeout.
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("data") and len(data["data"]) > 0:
                    img_url = data["data"][0].get("path")
                    if img_url:
                        return self.download_image(img_url, "wallhaven")
            elif resp.status_code == 429:
                logger.warning("Wallhaven API hit rate limit (429).")
        except requests.exceptions.Timeout:
            logger.warning("Wallhaven API timed out.")
        except Exception as e:
            logger.error(f"Error fetching from Wallhaven: {e}")
        return None

    def fetch_reddit(self) -> Optional[str]:
        """Downloads a top native image from configured subreddits."""
        subreddits = self.config.get("reddit_subreddits", ["EarthPorn", "wallpaper"])
        if not subreddits:
            return None
            
        subreddit = random.choice(subreddits)
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
        
        try:
            # Reddit requires a custom User-Agent to prevent 429 Too Many Requests errors
            headers = {'User-Agent': 'windows:pyvariety:v1.1 (by /u/pyvariety_bot)'}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                posts = data.get("data", {}).get("children", [])
                
                # Filter for direct image links over a certain resolution
                valid_images = []
                for p in posts:
                    post_data = p.get("data", {})
                    url = post_data.get("url", "")
                    domain = post_data.get("domain", "")
                    if domain == "i.redd.it" and url.endswith(('jpg', 'jpeg', 'png')):
                        # Extra filter to ensure we don't grab tiny images if preview data exists
                        preview = post_data.get("preview", {})
                        if preview and preview.get("images"):
                            source = preview["images"][0].get("source", {})
                            if source.get("width", 0) >= 1920:
                                valid_images.append(url)
                        else:
                            # Fallback if no preview
                            valid_images.append(url)
                            
                if valid_images:
                    img_url = random.choice(valid_images)
                    return self.download_image(img_url, "reddit")
                    
        except Exception as e:
            logger.error(f"Error fetching from Reddit r/{subreddit}: {e}")
        return None
        
    def fetch_apod(self) -> Optional[str]:
        """Downloads the NASA Astronomy Picture of the Day."""
        try:
            url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                img_url = data.get("hdurl", data.get("url"))
                if img_url and img_url.endswith(('jpg', 'jpeg', 'png')):
                    return self.download_image(img_url, "apod")
        except Exception as e:
            logger.error(f"Error fetching APOD: {e}")
        return None

    def download_image(self, url: str, prefix: str) -> Optional[str]:
        """Downloads an image and caches it locally."""
        try:
            # Use 5s connect timeout and 10s read timeout
            resp = requests.get(url, stream=True, timeout=(5, 10))
            if resp.status_code == 200:
                filename = f"{prefix}_{int(time.time())}.jpg"
                filepath = CACHE_DIR / filename
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
                return str(filepath.absolute())
            else:
                logger.warning(f"Download {url} failed with status: {resp.status_code}")
        except requests.exceptions.Timeout:
            logger.warning(f"Download timed out for {url}")
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
        return None

def fetch_daily_quote() -> str:
    """Fetches a daily motivational quote from ZenQuotes."""
    try:
        resp = requests.get("https://zenquotes.io/api/random", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 0:
                q = data[0].get("q")
                a = data[0].get("a")
                if q and a:
                    return f'"{q}"\n- {a}'
    except Exception as e:
        logger.error(f"Failed to fetch quote: {e}")
    return ""
