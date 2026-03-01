import datetime
import logging
import textwrap
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont

from fetcher import fetch_daily_quote

logger = logging.getLogger(__name__)

def process_image(image_path: str, config: dict, output_path: str) -> str:
    """
    Applies configured filters to the image.
    If no filters apply, returns the original image_path.
    If filters apply, saves a new image and returns the path.

    Filters from config dict:
      - blur: bool
      - blur_radius: int
      - grayscale: bool
      - color_overlay: tuple (R, G, B, A) or list
    """
    filters = config.get("filters", {})
    features = config.get("features", {})
    show_clock = features.get("show_clock", False)
    show_quote = features.get("show_quote", False)

    needs_processing = any([
        filters.get("blur"), 
        filters.get("grayscale"), 
        filters.get("color_overlay") is not None,
        show_clock,
        show_quote
    ])

    if not needs_processing:
        # No processing required, keep original path
        return image_path

    try:
        with Image.open(image_path).convert("RGBA") as img:
            
            # 1. Grayscale
            if filters.get("grayscale"):
                img = ImageOps.grayscale(img).convert("RGBA")

            # 2. Blur
            if filters.get("blur"):
                radius = filters.get("blur_radius", 5)
                img = img.filter(ImageFilter.GaussianBlur(radius))

            # 3. Color Overlay
            overlay_color = filters.get("color_overlay")
            if overlay_color and len(overlay_color) == 4:
                overlay = Image.new("RGBA", img.size, tuple(overlay_color))
                img = Image.alpha_composite(img, overlay)

            # 4. Text Overlays
            if show_clock or show_quote:
                draw = ImageDraw.Draw(img)
                width, height = img.size
                
                # Try to load a generic Windows font, fallback to default
                try:
                    font_large = ImageFont.truetype("segoeuil.ttf", 140)
                    font_small = ImageFont.truetype("segoeui.ttf", 40)
                except IOError:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()

                # Draw Clock Bottom Left
                if show_clock:
                    time_str = datetime.datetime.now().strftime("%I:%M %p")
                    x, y = 100, height - 250
                    # Draw thick outline for readability
                    for adj_x, adj_y in [(-3,-3), (3,-3), (-3,3), (3,3), (0,4), (0,-4), (4,0), (-4,0)]:
                        draw.text((x + adj_x, y + adj_y), time_str, font=font_large, fill=(0, 0, 0, 180))
                    draw.text((x, y), time_str, font=font_large, fill=(255, 255, 255, 255))
                    
                # Draw Quote Bottom Center, safely wrapped
                if show_quote:
                    quote = fetch_daily_quote()
                    if quote:
                        # Wrap long quotes so they don't clip off the edges dynamically
                        # 60 characters is a safe bounds for most monitor fonts
                        lines = [line for raw_line in quote.split('\n') for line in textwrap.wrap(raw_line, width=50)]
                        
                        # Calculate starting Y to keep it nicely positioned above the clock vertically
                        y_offset = height - 200 - (len(lines) * 45)
                        
                        for line in lines:
                            # Dynamically measure width to purely center it horizontally
                            left, top, right, bottom = draw.textbbox((0, 0), line, font=font_small)
                            line_width = right - left
                            x = (width - line_width) // 2
                            
                            # Draw thick outline
                            for adj_x, adj_y in [(-2,-2), (2,-2), (-2,2), (2,2), (0,3), (0,-3), (3,0), (-3,0)]:
                                draw.text((x + adj_x, y_offset + adj_y), line, font=font_small, fill=(0, 0, 0, 200))
                            draw.text((x, y_offset), line, font=font_small, fill=(255, 255, 255, 255))
                            y_offset += 45

            # Convert to RGB to save as JPEG/PNG correctly without alpha layer issues
            final_img = img.convert("RGB")
            
            final_img.save(output_path, "JPEG", quality=95)
            logger.info(f"Processed image saved to {output_path}")
            return output_path

    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        return image_path
