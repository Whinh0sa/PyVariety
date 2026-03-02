import datetime
import logging
import textwrap
import math
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont, ImageColor

from fetcher import fetch_daily_quote

logger = logging.getLogger(__name__)

def hex_to_rgba(hex_color, opacity_percent):
    if not hex_color:
        return (0, 0, 0, 0)
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        a = int((opacity_percent / 100.0) * 255)
        return (r, g, b, a)
    return (0, 0, 0, 0)

def process_image(image_path: str, config: dict, output_path: str) -> str:
    effects = config.get("effects", {})
    quotes = config.get("quotes", {})
    clock = config.get("clock", {})

    needs_processing = not effects.get("keep_original", True) or \
                       quotes.get("enabled", False) or \
                       clock.get("enabled", False)

    if not needs_processing and effects.get("keep_original", True):
        # We might still need to process if clock/quotes are on.
        # Wait, if keep_original is true and others are false, just return.
        if not quotes.get("enabled", False) and not clock.get("enabled", False):
            return image_path

    try:
        with Image.open(image_path).convert("RGBA") as img:
            
            # Effects
            if effects.get("grayscale"):
                img = ImageOps.grayscale(img).convert("RGBA")

            if effects.get("heavy_blur"):
                img = img.filter(ImageFilter.GaussianBlur(15))
            elif effects.get("soft_blur"):
                img = img.filter(ImageFilter.GaussianBlur(5))

            if effects.get("pixellate"):
                # Downscale then upscale nearest neighbor
                w, h = img.size
                img = img.resize((w // 10, h // 10), Image.Resampling.NEAREST)
                img = img.resize((w, h), Image.Resampling.NEAREST)

            if effects.get("oil_painting"):
                img = img.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.5)

            if effects.get("pointillism"):
                # Posterize/quantize representation
                img = img.quantize(colors=32).convert("RGBA")

            width, height = img.size
            draw = ImageDraw.Draw(img)

            def get_font(name, size):
                if not name: name = "segoeui.ttf"
                if not name.endswith(".ttf"): name += ".ttf"
                try:
                    return ImageFont.truetype(name, size)
                except IOError:
                    try:
                        return ImageFont.truetype("arial.ttf", size)
                    except IOError:
                        return ImageFont.load_default()

            # Clock
            if clock.get("enabled", False):
                clock_font = get_font(clock.get("clock_font_name"), clock.get("clock_font_size", 70))
                date_font = get_font(clock.get("date_font_name"), clock.get("date_font_size", 30))
                
                time_str = datetime.datetime.now().strftime("%I:%M %p")
                date_str = datetime.datetime.now().strftime("%A, %B %d")
                
                x, y = 100, height - 300
                
                # Draw Box? Variety UI doesn't specify a box for clock, just font. We'll add text shadow.
                # Outline
                for adj_x, adj_y in [(-2,-2), (2,-2), (-2,2), (2,2)]:
                    draw.text((x + adj_x, y + adj_y), time_str, font=clock_font, fill=(0, 0, 0, 180))
                    draw.text((x + adj_x, y + 100 + adj_y), date_str, font=date_font, fill=(0, 0, 0, 180))
                
                draw.text((x, y), time_str, font=clock_font, fill=(255, 255, 255, 255))
                draw.text((x, y + 100), date_str, font=date_font, fill=(255, 255, 255, 255))

            # Quotes
            if quotes.get("enabled", False):
                quote = fetch_daily_quote()
                if quote:
                    font = get_font(quotes.get("font_name"), quotes.get("font_size", 30))
                    text_color = ImageColor.getrgb(quotes.get("text_color", "#FFFFFF"))
                    
                    # Layout
                    pos_x = quotes.get("pos_x", 50)
                    pos_y = quotes.get("pos_y", 50)
                    q_width_pct = quotes.get("width", 50)
                    
                    # Calculate wrap width in characters roughly (assuming average Char is size/2 px)
                    box_pixel_width = int(width * (q_width_pct / 100.0))
                    char_width = quotes.get("font_size", 30) * 0.5
                    wrap_chars = max(10, int(box_pixel_width / char_width))
                    
                    lines = []
                    for raw_line in quote.split('\n'):
                        lines.extend(textwrap.wrap(raw_line, width=wrap_chars))
                        
                    # Calculate block height
                    left, top, right, bottom = draw.textbbox((0, 0), "A", font=font)
                    line_height = (bottom - top) + 10
                    total_text_height = len(lines) * line_height
                    
                    # Calculate start X, Y
                    if pos_x < 10: start_x = 50
                    elif pos_x > 90: start_x = width - box_pixel_width - 50
                    else: start_x = int((width - box_pixel_width) * (pos_x / 100.0))
                    
                    if pos_y < 10: start_y = 50
                    elif pos_y > 90: start_y = height - total_text_height - 50
                    else: start_y = int((height - total_text_height) * (pos_y / 100.0))
                    
                    # Draw Backdrop
                    bg_color = hex_to_rgba(quotes.get("bg_color", "#000000"), quotes.get("bg_opacity", 50))
                    if bg_color[3] > 0:
                        padding = 20
                        box_coords = [start_x - padding, start_y - padding, start_x + box_pixel_width + padding, start_y + total_text_height + padding]
                        overlay = Image.new("RGBA", img.size, (0,0,0,0))
                        ImageDraw.Draw(overlay).rectangle(box_coords, fill=bg_color)
                        img = Image.alpha_composite(img, overlay)
                        draw = ImageDraw.Draw(img) # Refresh draw context

                    y_offset = start_y
                    shadow = quotes.get("shadow", True)
                    
                    for line in lines:
                        # Re-evaluate line width for centering
                        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
                        line_pixel_width = right - left
                        
                        # Justify center within the box
                        lx = start_x + (box_pixel_width - line_pixel_width) // 2
                        
                        if shadow:
                            draw.text((lx + 2, y_offset + 2), line, font=font, fill=(0, 0, 0, 150))
                            
                        draw.text((lx, y_offset), line, font=font, fill=text_color)
                        y_offset += line_height

            final_img = img.convert("RGB")
            final_img.save(output_path, "JPEG", quality=95)
            logger.info(f"Processed image saved to {output_path}")
            return output_path

    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        return image_path
