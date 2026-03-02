import customtkinter as ctk
import logging
from config import config, save_config
from setter import toggle_autostart

logger = logging.getLogger(__name__)

class PyVarietyGUI(ctk.CTk):
    def __init__(self, on_close_callback=None):
        super().__init__()
        
        self.on_close_callback = on_close_callback
        self.title("Variety Preferences")
        self.geometry("900x700")
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_general = self.tabview.add("General")
        self.tab_wallpaper = self.tabview.add("Wallpaper")
        self.tab_quotes = self.tabview.add("Quotes")
        self.tab_clock = self.tabview.add("Clock")
        self.tab_downloading = self.tabview.add("Downloading")
        
        self.create_general_tab()
        self.create_wallpaper_tab()
        self.create_quotes_tab()
        self.create_clock_tab()
        self.create_downloading_tab()
        
        # Save Button at bottom absolute
        self.save_button = ctk.CTkButton(self, text="Close and Save", command=self.save_and_close)
        self.save_button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="e")
        
        self.load_current_settings()

    def create_general_tab(self):
        # Auto start & interval
        fr_top = ctk.CTkFrame(self.tab_general, fg_color="transparent")
        fr_top.pack(fill="x", padx=10, pady=10)
        
        self.var_autostart = ctk.BooleanVar()
        ctk.CTkCheckBox(fr_top, text="Start Variety when the computer starts", variable=self.var_autostart).pack(anchor="w", pady=5)
        
        self.var_pause_fs = ctk.BooleanVar()
        ctk.CTkCheckBox(fr_top, text="Pause rotation on fullscreen app (Performance mode)", variable=self.var_pause_fs).pack(anchor="w", pady=5)
        
        fr_interval = ctk.CTkFrame(fr_top, fg_color="transparent")
        fr_interval.pack(anchor="w", pady=5)
        ctk.CTkLabel(fr_interval, text="Change wallpaper every").pack(side="left", padx=(0,10))
        self.interval_entry = ctk.CTkEntry(fr_interval, width=50)
        self.interval_entry.pack(side="left")
        self.interval_unit_var = ctk.StringVar(value="minutes")
        ctk.CTkOptionMenu(fr_interval, values=["minutes", "hours", "days"], variable=self.interval_unit_var, width=100).pack(side="left", padx=10)
        
        # Images Sources
        fr_src = ctk.CTkFrame(self.tab_general)
        fr_src.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(fr_src, text="Images", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.var_unsplash = ctk.BooleanVar()
        self.var_wallhaven = ctk.BooleanVar()
        self.var_reddit = ctk.BooleanVar()
        self.var_local = ctk.BooleanVar()
        self.var_bing = ctk.BooleanVar()
        self.var_natgeo = ctk.BooleanVar()
        
        ctk.CTkCheckBox(fr_src, text="Unsplash High-Res Search", variable=self.var_unsplash).pack(anchor="w", padx=20, pady=2)
        ctk.CTkCheckBox(fr_src, text="Wallhaven (Anime/General/Nature)", variable=self.var_wallhaven).pack(anchor="w", padx=20, pady=2)
        ctk.CTkCheckBox(fr_src, text="Reddit /r/EarthPorn & Wallpapers", variable=self.var_reddit).pack(anchor="w", padx=20, pady=2)
        ctk.CTkCheckBox(fr_src, text="Bing Photo of the Day", variable=self.var_bing).pack(anchor="w", padx=20, pady=2)
        ctk.CTkCheckBox(fr_src, text="NatGeo Photo Proxy", variable=self.var_natgeo).pack(anchor="w", padx=20, pady=2)
        ctk.CTkCheckBox(fr_src, text="Local Folders", variable=self.var_local).pack(anchor="w", padx=20, pady=2)
        
        # Local Paths
        fr_local = ctk.CTkFrame(self.tab_general, fg_color="transparent")
        fr_local.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(fr_local, text="Local Directory Path:").pack(side="left", padx=10)
        self.local_dir_entry = ctk.CTkEntry(fr_local, width=300)
        self.local_dir_entry.pack(side="left")

        # Favorites
        fr_fav = ctk.CTkFrame(self.tab_general, fg_color="transparent")
        fr_fav.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(fr_fav, text="Copy favorite wallpapers to:").pack(side="left", padx=10)
        self.fav_dir_entry = ctk.CTkEntry(fr_fav, width=300)
        self.fav_dir_entry.pack(side="left")

    def create_wallpaper_tab(self):
        ctk.CTkLabel(self.tab_wallpaper, text="Effects", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,5))
        ctk.CTkLabel(self.tab_wallpaper, text="Apply advanced visual filters to images:", text_color="gray").pack(anchor="w", padx=10, pady=(0,10))
        
        self.var_grayscale = ctk.BooleanVar()
        self.var_heavy_blur = ctk.BooleanVar()
        self.var_soft_blur = ctk.BooleanVar()
        self.var_oil = ctk.BooleanVar()
        self.var_pointillism = ctk.BooleanVar()
        self.var_pixellate = ctk.BooleanVar()
        
        grid_fr = ctk.CTkFrame(self.tab_wallpaper, fg_color="transparent")
        grid_fr.pack(fill="x", padx=10)
        
        ctk.CTkCheckBox(grid_fr, text="Grayscale", variable=self.var_grayscale).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(grid_fr, text="Heavy blur", variable=self.var_heavy_blur).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(grid_fr, text="Soft blur", variable=self.var_soft_blur).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(grid_fr, text="Oil painting", variable=self.var_oil).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(grid_fr, text="Pointillism", variable=self.var_pointillism).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkCheckBox(grid_fr, text="Pixellate", variable=self.var_pixellate).grid(row=1, column=2, padx=10, pady=10, sticky="w")

    def create_quotes_tab(self):
        self.var_quote_env = ctk.BooleanVar()
        ctk.CTkCheckBox(self.tab_quotes, text="Show random wise quotes on the desktop", variable=self.var_quote_env).pack(anchor="w", padx=10, pady=10)
        
        fr_app = ctk.CTkFrame(self.tab_quotes)
        fr_app.pack(fill="x", padx=10, anchor="w")
        
        # Appearance
        ctk.CTkLabel(fr_app, text="Appearance", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(fr_app, text="Text color (Hex):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.quote_color_entry = ctk.CTkEntry(fr_app, width=100)
        self.quote_color_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(fr_app, text="Font size:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.quote_font_entry = ctk.CTkEntry(fr_app, width=60)
        self.quote_font_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")
        
        self.var_quote_shadow = ctk.BooleanVar()
        ctk.CTkCheckBox(fr_app, text="Draw a text shadow", variable=self.var_quote_shadow).grid(row=1, column=4, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(fr_app, text="Backdrop color:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.quote_bg_entry = ctk.CTkEntry(fr_app, width=100)
        self.quote_bg_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(fr_app, text="Opacity (%):").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.quote_bg_op_entry = ctk.CTkEntry(fr_app, width=60)
        self.quote_bg_op_entry.grid(row=2, column=3, padx=10, pady=5, sticky="w")

        # Placement
        fr_place = ctk.CTkFrame(self.tab_quotes)
        fr_place.pack(fill="x", padx=10, pady=10, anchor="w")
        ctk.CTkLabel(fr_place, text="Placement", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(fr_place, text="Horizontal position:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.quote_x_slider = ctk.CTkSlider(fr_place, from_=0, to=100)
        self.quote_x_slider.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(fr_place, text="Vertical position:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.quote_y_slider = ctk.CTkSlider(fr_place, from_=0, to=100)
        self.quote_y_slider.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(fr_place, text="Quotes area width (%):").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.quote_w_slider = ctk.CTkSlider(fr_place, from_=10, to=100)
        self.quote_w_slider.grid(row=1, column=3, padx=10, pady=5, sticky="w")

    def create_clock_tab(self):
        self.var_clock_env = ctk.BooleanVar()
        ctk.CTkCheckBox(self.tab_clock, text="Show a nice digital clock on the desktop", variable=self.var_clock_env).pack(anchor="w", padx=10, pady=10)
        
        fr_app = ctk.CTkFrame(self.tab_clock)
        fr_app.pack(fill="x", padx=10, anchor="w")
        
        ctk.CTkLabel(fr_app, text="Appearance", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(fr_app, text="Clock font size:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.clock_size_entry = ctk.CTkEntry(fr_app, width=60)
        self.clock_size_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(fr_app, text="Date font size:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.date_size_entry = ctk.CTkEntry(fr_app, width=60)
        self.date_size_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    def create_downloading_tab(self):
        fr_fetch = ctk.CTkFrame(self.tab_downloading, fg_color="transparent")
        fr_fetch.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(fr_fetch, text="Fetch Folder", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(fr_fetch, text="Save manually downloaded wallpapers to:", text_color="gray").pack(anchor="w", pady=(0,5))
        self.fetch_dir_entry = ctk.CTkEntry(fr_fetch, width=400)
        self.fetch_dir_entry.pack(anchor="w")
        
        fr_clip = ctk.CTkFrame(self.tab_downloading, fg_color="transparent")
        fr_clip.pack(fill="x", padx=10, pady=20)
        ctk.CTkLabel(fr_clip, text="Clipboard monitoring", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.var_clipboard = ctk.BooleanVar()
        ctk.CTkCheckBox(fr_clip, text="Monitor clipboard for image URLs and fetch them", variable=self.var_clipboard).pack(anchor="w", pady=5)
        ctk.CTkLabel(fr_clip, text="Valid hosts: wallhaven.cc, imgur.com, reddit.com", text_color="gray").pack(anchor="w", padx=25)

    def load_current_settings(self):
        c = config
        
        # General
        self.var_autostart.set(c.get("autostart", False))
        self.var_pause_fs.set(c.get("pause_on_fullscreen", True))
        
        self.interval_entry.insert(0, str(c.get("interval_amount", 5)))
        self.interval_unit_var.set(c.get("interval_unit", "minutes"))
        
        srcs = c.get("sources", [])
        self.var_unsplash.set("unsplash" in srcs)
        self.var_wallhaven.set("wallhaven" in srcs)
        self.var_reddit.set("reddit" in srcs)
        self.var_local.set("local" in srcs)
        self.var_bing.set("bing" in srcs)
        self.var_natgeo.set("natgeo" in srcs)
        
        self.local_dir_entry.insert(0, c.get("local_paths", [""])[0] if c.get("local_paths") else "")
        self.fav_dir_entry.insert(0, c.get("favorites_folder", ""))
        
        # Wallpaper
        eff = c.get("effects", {})
        self.var_grayscale.set(eff.get("grayscale", False))
        self.var_heavy_blur.set(eff.get("heavy_blur", False))
        self.var_soft_blur.set(eff.get("soft_blur", False))
        self.var_oil.set(eff.get("oil_painting", False))
        self.var_pointillism.set(eff.get("pointillism", False))
        self.var_pixellate.set(eff.get("pixellate", False))
        
        # Quotes
        q = c.get("quotes", {})
        self.var_quote_env.set(q.get("enabled", False))
        self.quote_color_entry.insert(0, q.get("text_color", "#FFFFFF"))
        self.quote_font_entry.insert(0, str(q.get("font_size", 30)))
        self.var_quote_shadow.set(q.get("shadow", True))
        self.quote_bg_entry.insert(0, q.get("bg_color", "#000000"))
        self.quote_bg_op_entry.insert(0, str(q.get("bg_opacity", 50)))
        self.quote_x_slider.set(q.get("pos_x", 50))
        self.quote_y_slider.set(q.get("pos_y", 50))
        self.quote_w_slider.set(q.get("width", 50))
        
        # Clock
        clk = c.get("clock", {})
        self.var_clock_env.set(clk.get("enabled", False))
        self.clock_size_entry.insert(0, str(clk.get("clock_font_size", 70)))
        self.date_size_entry.insert(0, str(clk.get("date_font_size", 30)))
        
        # Downloading
        self.fetch_dir_entry.insert(0, c.get("fetch_folder", ""))
        clip = c.get("clipboard", {})
        self.var_clipboard.set(clip.get("enabled", False))

    def save_and_close(self):
        c = config
        
        c["autostart"] = self.var_autostart.get()
        c["pause_on_fullscreen"] = self.var_pause_fs.get()
        toggle_autostart(c["autostart"])
        
        amt = self.interval_entry.get()
        if amt.isdigit():
            c["interval_amount"] = int(amt)
        c["interval_unit"] = self.interval_unit_var.get()
        
        ns = []
        if self.var_unsplash.get(): ns.append("unsplash")
        if self.var_wallhaven.get(): ns.append("wallhaven")
        if self.var_reddit.get(): ns.append("reddit")
        if self.var_local.get(): ns.append("local")
        if self.var_bing.get(): ns.append("bing")
        if self.var_natgeo.get(): ns.append("natgeo")
        c["sources"] = ns
        
        ldir = self.local_dir_entry.get().strip()
        if ldir: c["local_paths"] = [ldir]
        
        fdir = self.fav_dir_entry.get().strip()
        if fdir: c["favorites_folder"] = fdir
        
        c["effects"]["grayscale"] = self.var_grayscale.get()
        c["effects"]["heavy_blur"] = self.var_heavy_blur.get()
        c["effects"]["soft_blur"] = self.var_soft_blur.get()
        c["effects"]["oil_painting"] = self.var_oil.get()
        c["effects"]["pointillism"] = self.var_pointillism.get()
        c["effects"]["pixellate"] = self.var_pixellate.get()
        
        c["quotes"]["enabled"] = self.var_quote_env.get()
        c["quotes"]["text_color"] = self.quote_color_entry.get().strip()
        fz = self.quote_font_entry.get()
        if fz.isdigit(): c["quotes"]["font_size"] = int(fz)
        c["quotes"]["shadow"] = self.var_quote_shadow.get()
        c["quotes"]["bg_color"] = self.quote_bg_entry.get().strip()
        op = self.quote_bg_op_entry.get()
        if op.isdigit(): c["quotes"]["bg_opacity"] = int(op)
        c["quotes"]["pos_x"] = int(self.quote_x_slider.get())
        c["quotes"]["pos_y"] = int(self.quote_y_slider.get())
        c["quotes"]["width"] = int(self.quote_w_slider.get())
        
        c["clock"]["enabled"] = self.var_clock_env.get()
        cs = self.clock_size_entry.get()
        if cs.isdigit(): c["clock"]["clock_font_size"] = int(cs)
        ds = self.date_size_entry.get()
        if ds.isdigit(): c["clock"]["date_font_size"] = int(ds)
        
        fetdir = self.fetch_dir_entry.get().strip()
        if fetdir: c["fetch_folder"] = fetdir
        c["clipboard"]["enabled"] = self.var_clipboard.get()
        
        save_config(c)
        logger.info("GUI TabView settings saved.")
        
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

def open_gui(on_close_callback=None):
    app = PyVarietyGUI(on_close_callback)
    app.mainloop()

if __name__ == "__main__":
    open_gui()
