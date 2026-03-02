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
        self.tab_filtering = self.tabview.add("Filtering")
        self.tab_customize = self.tabview.add("Customize")
        self.tab_tips = self.tabview.add("Tips")
        self.tab_changelog = self.tabview.add("Changelog")
        self.tab_donate = self.tabview.add("Donate")
        
        self.create_general_tab()
        self.create_wallpaper_tab()
        self.create_quotes_tab()
        self.create_clock_tab()
        self.create_downloading_tab()
        self.create_filtering_tab()
        self.create_customize_tab()
        self.create_tips_tab()
        self.create_changelog_tab()
        self.create_donate_tab()
        
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

    def create_filtering_tab(self):
        ctk.CTkLabel(self.tab_filtering, text="When possible use images that:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=10)
        
        fr_size = ctk.CTkFrame(self.tab_filtering, fg_color="transparent")
        fr_size.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(fr_size, text="Size", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.var_landscape = ctk.BooleanVar()
        ctk.CTkCheckBox(fr_size, text="Have landscape orientation", variable=self.var_landscape).pack(anchor="w", padx=20, pady=5)
        
        fr_min = ctk.CTkFrame(fr_size, fg_color="transparent")
        fr_min.pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(fr_min, text="Are big at least").pack(side="left")
        self.min_size_entry = ctk.CTkEntry(fr_min, width=50)
        self.min_size_entry.pack(side="left", padx=10)
        ctk.CTkLabel(fr_min, text="% of the screen resolution", text_color="gray").pack(side="left")
        
        fr_color = ctk.CTkFrame(self.tab_filtering, fg_color="transparent")
        fr_color.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(fr_color, text="Color", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        fr_clrt = ctk.CTkFrame(fr_color, fg_color="transparent")
        fr_clrt.pack(anchor="w", padx=20, pady=5)
        self.var_enable_clr = ctk.BooleanVar()
        self.cb_enable_clr = ctk.CTkCheckBox(fr_clrt, text="Are dark or light:", variable=self.var_enable_clr)
        self.cb_enable_clr.pack(side="left")
        self.color_type_var = ctk.StringVar(value="Dark")
        ctk.CTkOptionMenu(fr_clrt, values=["Dark", "Light"], variable=self.color_type_var, width=80).pack(side="left", padx=10)
        
        fr_spec = ctk.CTkFrame(fr_color, fg_color="transparent")
        fr_spec.pack(anchor="w", padx=20, pady=5)
        self.var_enable_spec = ctk.BooleanVar()
        self.cb_enable_spec = ctk.CTkCheckBox(fr_spec, text="Contain this color:", variable=self.var_enable_spec)
        self.cb_enable_spec.pack(side="left")
        self.color_spec_entry = ctk.CTkEntry(fr_spec, width=80)
        self.color_spec_entry.pack(side="left", padx=10)
        ctk.CTkLabel(fr_spec, text="(Hex code logic filtering)", text_color="gray").pack(side="left")

        fr_rate = ctk.CTkFrame(self.tab_filtering, fg_color="transparent")
        fr_rate.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(fr_rate, text="Rating", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        fr_rat_cb = ctk.CTkFrame(fr_rate, fg_color="transparent")
        fr_rat_cb.pack(anchor="w", padx=20, pady=5)
        self.var_enable_rat = ctk.BooleanVar()
        self.cb_enable_rat = ctk.CTkCheckBox(fr_rat_cb, text="Have rating at least:", variable=self.var_enable_rat)
        self.cb_enable_rat.pack(side="left")
        self.rating_var = ctk.StringVar(value="4")
        ctk.CTkOptionMenu(fr_rat_cb, values=["1", "2", "3", "4", "5"], variable=self.rating_var, width=60).pack(side="left", padx=10)

    def create_customize_tab(self):
        fr_ind = ctk.CTkFrame(self.tab_customize, fg_color="transparent")
        fr_ind.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(fr_ind, text="Indicator Icon", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        fr_ico = ctk.CTkFrame(fr_ind, fg_color="transparent")
        fr_ico.pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(fr_ico, text="Indicator icon:").pack(side="left", padx=(0,10))
        self.icon_var = ctk.StringVar(value="Dark")
        ctk.CTkOptionMenu(fr_ico, values=["Dark", "Light"], variable=self.icon_var, width=100).pack(side="left")
        
        ctk.CTkLabel(fr_ind, text="When the icon is hidden, Variety can be controlled from the command line.", text_color="gray").pack(anchor="w", padx=10)
        
        fr_log = ctk.CTkFrame(self.tab_customize, fg_color="transparent")
        fr_log.pack(fill="x", padx=10, pady=20)
        ctk.CTkLabel(fr_log, text="Login Screen Support", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.var_login = ctk.BooleanVar()
        ctk.CTkCheckBox(fr_log, text="Make sure the wallpapers set by Variety will be used on the login screen", variable=self.var_login).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(fr_log, text="Privacy warning: This copies the wallpaper image to a separate active lock folder.", text_color="gray", justify="left").pack(anchor="w", padx=35)
        
        fr_log_dir = ctk.CTkFrame(fr_log, fg_color="transparent")
        fr_log_dir.pack(anchor="w", padx=35, pady=5)
        ctk.CTkLabel(fr_log_dir, text="Copy wallpaper image files to this folder:").pack(side="left", padx=(0,10))
        self.login_dir_entry = ctk.CTkEntry(fr_log_dir, width=250)
        self.login_dir_entry.pack(side="left")

    def create_tips_tab(self):
        textbox = ctk.CTkTextbox(self.tab_tips, wrap="word", width=840, height=450, fg_color="transparent")
        textbox.pack(padx=20, pady=20, fill="both", expand=True)
        tips = (
            "Tips and tricks\n\n"
            "You can change the wallpaper back and forth by scrolling the mouse wheel on top of the indicator icon.\n\n"
            "You can drop image links or files on the launcher icon to download them and use them as wallpapers. For quicker downloading "
            "from a specific site, you can also use clipboard monitoring (see 'Downloading' tab).\n\n"
            "Applying a heavy blurring filter is a great way to get abstract-looking and unobtrusive, yet colorful wallpapers.\n\n"
            "Variety's indicator icon is themeable - if you choose the 'Light' option for the icon, Variety will first check if "
            "the current theme has an icon named 'variety-indicator'."
        )
        textbox.insert("0.0", tips)
        textbox.configure(state="disabled")

    def create_changelog_tab(self):
        textbox = ctk.CTkTextbox(self.tab_changelog, wrap="word", width=840, height=450, fg_color="transparent")
        textbox.pack(padx=20, pady=20, fill="both", expand=True)
        log = (
            "Recent changes\n\n"
            "v1.9 Absolute Parity\n"
            "- Added complete Filtering, Customize, Tips, Changelog, and Donate tabs.\n"
            "- Added advanced image analytics to guarantee Landscape-only rotation.\n"
            "- Added light/dark palette extraction using Pillow.\n"
            "- Synchronized the Windows LightDM equivalent for login screen wallpaper mirroring.\n\n"
            "v1.8 Ultimate Parity\n"
            "- Refactored GUI into CustomTkinter TabViews.\n"
            "- Built robust pixel math filters (Pointillism, Pixellation, Oil Painting).\n"
            "- Native Windows ctypes background hook for clipboard scraping.\n"
            "- Massive Quotes Engine overlay logic rework.\n"
        )
        textbox.insert("0.0", log)
        textbox.configure(state="disabled")

    def create_donate_tab(self):
        textbox = ctk.CTkTextbox(self.tab_donate, wrap="word", width=840, height=450, fg_color="transparent")
        textbox.pack(padx=20, pady=20, fill="both", expand=True)
        don = (
            "Donate to Variety\n\n"
            "I am developing Variety in my spare time, which usually means the late hours after my kids go to bed. "
            "Any amount you donate will be appreciated. It will show me Variety is valued by you - the users - and "
            "will motivate me to continue working actively on it.\n\n"
            "Thank you,\nPeter Levi\nPatrick\n\n"
            "Donate via PayPal: [Disabled in Windows Port]\n\n"
            "To donate in Bitcoin, please send to this wallet: 1EHtkck9pw2Ry4NP6Es8rAXWEeADLdkqcP"
        )
        textbox.insert("0.0", don)
        textbox.configure(state="disabled")

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
        
        # Filtering
        filt = c.get("filtering", {})
        self.var_landscape.set(filt.get("landscape_only", True))
        self.min_size_entry.insert(0, str(filt.get("min_screen_size_pct", 80)))
        ctype = filt.get("color_type", "None")
        self.var_enable_clr.set(ctype != "None")
        self.color_type_var.set(ctype if ctype != "None" else "Dark")
        self.var_enable_spec.set(bool(filt.get("specific_color", "")))
        self.color_spec_entry.insert(0, filt.get("specific_color", ""))
        self.var_enable_rat.set(filt.get("min_exif_rating", 0) > 0)
        self.rating_var.set(str(filt.get("min_exif_rating", 4) if filt.get("min_exif_rating", 0) > 0 else 4))
        
        # Customize
        cust = c.get("customize", {})
        self.icon_var.set(cust.get("indicator_icon", "Dark"))
        self.var_login.set(cust.get("login_screen_support", False))
        self.login_dir_entry.insert(0, cust.get("login_screen_folder", ""))

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
        
        # Filtering
        c["filtering"]["landscape_only"] = self.var_landscape.get()
        msp = self.min_size_entry.get()
        if msp.isdigit(): c["filtering"]["min_screen_size_pct"] = int(msp)
        if self.var_enable_clr.get():
            c["filtering"]["color_type"] = self.color_type_var.get()
        else:
            c["filtering"]["color_type"] = "None"
        
        if self.var_enable_spec.get():
            c["filtering"]["specific_color"] = self.color_spec_entry.get().strip()
        else:
            c["filtering"]["specific_color"] = ""
            
        if self.var_enable_rat.get():
            c["filtering"]["min_exif_rating"] = int(self.rating_var.get())
        else:
            c["filtering"]["min_exif_rating"] = 0
            
        # Customize
        c["customize"]["indicator_icon"] = self.icon_var.get()
        c["customize"]["login_screen_support"] = self.var_login.get()
        ldir = self.login_dir_entry.get().strip()
        if ldir: c["customize"]["login_screen_folder"] = ldir
        
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
