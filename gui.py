import customtkinter as ctk
import logging
from config import config, save_config
from setter import toggle_autostart

logger = logging.getLogger(__name__)

class PyVarietyGUI(ctk.CTk):
    def __init__(self, on_close_callback=None):
        super().__init__()
        
        self.on_close_callback = on_close_callback
        self.title("PyVariety Settings")
        self.geometry("600x750")
        
        # Configure grid for resizing
        self.grid_columnconfigure(0, weight=1)
        
        # Glassmorphism aesthetic / Modern look
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.create_widgets()
        self.load_current_settings()

    def create_widgets(self):
        # --- Title Block ---
        self.title_label = ctk.CTkLabel(self, text="PyVariety Configuration", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")
        
        # --- General Settings Frame ---
        self.general_frame = ctk.CTkFrame(self, corner_radius=10)
        self.general_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.interval_label = ctk.CTkLabel(self.general_frame, text="Rotation Interval (Minutes):")
        self.interval_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.interval_entry = ctk.CTkEntry(self.general_frame, width=100)
        self.interval_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # --- Active Sources Frame ---
        self.sources_frame = ctk.CTkFrame(self, corner_radius=10)
        self.sources_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.sources_label = ctk.CTkLabel(self.sources_frame, text="Active Sources:", font=ctk.CTkFont(weight="bold"))
        self.sources_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.var_unsplash = ctk.BooleanVar()
        self.var_wallhaven = ctk.BooleanVar()
        self.var_reddit = ctk.BooleanVar()
        self.var_local = ctk.BooleanVar()
        self.var_bing = ctk.BooleanVar()
        self.var_natgeo = ctk.BooleanVar()
        
        self.cb_unsplash = ctk.CTkCheckBox(self.sources_frame, text="Unsplash", variable=self.var_unsplash)
        self.cb_unsplash.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.cb_wallhaven = ctk.CTkCheckBox(self.sources_frame, text="Wallhaven", variable=self.var_wallhaven)
        self.cb_wallhaven.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.cb_reddit = ctk.CTkCheckBox(self.sources_frame, text="Reddit", variable=self.var_reddit)
        self.cb_reddit.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.cb_local = ctk.CTkCheckBox(self.sources_frame, text="Local Directory", variable=self.var_local)
        self.cb_local.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.cb_bing = ctk.CTkCheckBox(self.sources_frame, text="Bing POTD", variable=self.var_bing)
        self.cb_bing.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.cb_natgeo = ctk.CTkCheckBox(self.sources_frame, text="NatGeo POTD Proxy", variable=self.var_natgeo)
        self.cb_natgeo.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        
        # --- Advanced Settings Frame ---
        self.adv_frame = ctk.CTkFrame(self, corner_radius=10)
        self.adv_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.adv_label = ctk.CTkLabel(self.adv_frame, text="Advanced source configs:", font=ctk.CTkFont(weight="bold"))
        self.adv_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.local_dir_label = ctk.CTkLabel(self.adv_frame, text="Local Directory Path:")
        self.local_dir_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.local_dir_entry = ctk.CTkEntry(self.adv_frame, width=300)
        self.local_dir_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.fav_dir_label = ctk.CTkLabel(self.adv_frame, text="Favorites Save Target:")
        self.fav_dir_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.fav_dir_entry = ctk.CTkEntry(self.adv_frame, width=300)
        self.fav_dir_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # --- OS Integrations ---
        self.os_frame = ctk.CTkFrame(self, corner_radius=10)
        self.os_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.os_label = ctk.CTkLabel(self.os_frame, text="OS Integrations:", font=ctk.CTkFont(weight="bold"))
        self.os_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.var_autostart = ctk.BooleanVar()
        self.cb_autostart = ctk.CTkCheckBox(self.os_frame, text="Start with Windows", variable=self.var_autostart)
        self.cb_autostart.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.var_pause_fs = ctk.BooleanVar()
        self.cb_pause_fs = ctk.CTkCheckBox(self.os_frame, text="Pause rotation if Game/Fullscreen app is running (Performance Mode)", variable=self.var_pause_fs)
        self.cb_pause_fs.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # --- Overlays Frame ---
        self.overlay_frame = ctk.CTkFrame(self, corner_radius=10)
        self.overlay_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        
        self.overlay_label = ctk.CTkLabel(self.overlay_frame, text="Desktop Overlays:", font=ctk.CTkFont(weight="bold"))
        self.overlay_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.var_clock = ctk.BooleanVar()
        self.cb_clock = ctk.CTkCheckBox(self.overlay_frame, text="Show Digital Clock", variable=self.var_clock)
        self.cb_clock.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.var_quote = ctk.BooleanVar()
        self.cb_quote = ctk.CTkCheckBox(self.overlay_frame, text="Show Daily Motivational Quote", variable=self.var_quote)
        self.cb_quote.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # --- Save Button ---
        self.save_button = ctk.CTkButton(self, text="Save Settings & Close", command=self.save_and_close)
        self.save_button.grid(row=6, column=0, padx=20, pady=20, sticky="e")

    def load_current_settings(self):
        # Interval
        self.interval_entry.insert(0, str(config.get("interval_minutes", 15)))
        
        # Sources
        active_sources = config.get("sources", [])
        self.var_unsplash.set("unsplash" in active_sources)
        self.var_wallhaven.set("wallhaven" in active_sources)
        self.var_reddit.set("reddit" in active_sources)
        self.var_local.set("local" in active_sources)
        self.var_bing.set("bing" in active_sources)
        self.var_natgeo.set("natgeo" in active_sources)
        
        # Advanced
        local_paths = config.get("local_paths", [])
        if local_paths:
            self.local_dir_entry.insert(0, local_paths[0])
            
        self.fav_dir_entry.insert(0, config.get("favorites_folder", ""))
            
        # OS Integration (Check registry indirectly by seeing if we flagged it in config, 
        # or checking the actual registry. For simplicity, we track intention in config)
        self.var_autostart.set(config.get("autostart", False))
        
        # v1.3 Features
        features = config.get("features", {})
        self.var_pause_fs.set(features.get("pause_on_fullscreen", True))
        self.var_clock.set(features.get("show_clock", False))
        self.var_quote.set(features.get("show_quote", False))

    def save_and_close(self):
        new_interval = self.interval_entry.get()
        if new_interval.isdigit():
            config["interval_minutes"] = int(new_interval)
            
        new_sources = []
        if self.var_unsplash.get(): new_sources.append("unsplash")
        if self.var_wallhaven.get(): new_sources.append("wallhaven")
        if self.var_reddit.get(): new_sources.append("reddit")
        if self.var_local.get(): new_sources.append("local")
        if self.var_bing.get(): new_sources.append("bing")
        if self.var_natgeo.get(): new_sources.append("natgeo")
        config["sources"] = new_sources
        
        new_local = self.local_dir_entry.get().strip()
        if new_local:
            config["local_paths"] = [new_local]
            
        new_fav = self.fav_dir_entry.get().strip()
        if new_fav:
            config["favorites_folder"] = new_fav
            
        # OS Int
        autostart_enabled = self.var_autostart.get()
        config["autostart"] = autostart_enabled
        toggle_autostart(autostart_enabled)
        
        # v1.3 Features
        if "features" not in config:
            config["features"] = {}
        config["features"]["pause_on_fullscreen"] = self.var_pause_fs.get()
        config["features"]["show_clock"] = self.var_clock.get()
        config["features"]["show_quote"] = self.var_quote.get()
            
        save_config(config)
        logger.info("GUI settings saved.")
        
        if self.on_close_callback:
            self.on_close_callback()
            
        self.destroy()

def open_gui(on_close_callback=None):
    app = PyVarietyGUI(on_close_callback)
    app.mainloop()

if __name__ == "__main__":
    open_gui()
