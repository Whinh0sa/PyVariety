# PyVariety (Windows Wallpaper Manager)

PyVariety is a highly-capable, open-source Python application for Windows that replicates and innovates upon the iconic Linux `Variety` wallpaper manager. It acts as an autonomous background daemon, fetching high-quality curated wallpapers from around the web while remaining extremely lightweight on system resources.

## Features

- **Multi-Source Fetching**: Pulls ultra high-quality images dynamically from Unsplash, Wallhaven, Reddit, NASA APOD, and localized offline folders. Runs Fisher-Yates shuffle algorithms to ensure non-repeating sequences.
- **Desktop Text Overlays**: Dynamically renders a Minimalist Digital Clock and fetches Daily Motivational Quotes (via ZenQuotes API), cleanly wrapped and drawn directly onto the wallpaper using `Pillow`.
- **Performance-Conscious Pausing**: Never impacts your gameplay! Automatically utilizes Windows `ctypes` OS hooks to detect when you are running a video game or fullscreen application, instantly pausing all processing to drop its CPU footprint to 0%.
- **Modern Control GUI**: Written with `CustomTkinter`, accessible seamlessly via a background system tray icon, making API integrations and filters completely interactive (no `json` files required).
- **Aesthetic Filters**: Includes native on-the-fly Image manipulation (Blur, Grayscale, Color Overlays).
- **Auto-Start Integration**: Injects into the Windows Registry to automatically launch silently on boot.

## Installation & Running

Download the pre-compiled standalone executable from the Releases page, or build it yourself:

\`\`\`powershell
git clone https://github.com/Whinh0sa/pyvariety.git
cd pyvariety
pip install -r requirements.txt
python main.py
\`\`\`

You can compile the executable yourself using the included script:
\`\`\`powershell
.\build.ps1
\`\`\`

## Configuration
PyVariety builds its configuration file locally at `~/.pyvariety/config.json`.
You can customize search queries (e.g. Anime, Cyberpunk, Dark Wallpapers) directly through the System Tray UI Settings menu.
