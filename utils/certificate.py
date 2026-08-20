import os
import io
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

def get_font(font_name: str, size: int):
    """Case-insensitive local font loader with Linux system fallback."""
    # 1. Search fonts/ directory (case-insensitive)
    if os.path.exists(FONTS_DIR):
        for file in os.listdir(FONTS_DIR):
            if file.lower() == font_name.lower():
                return ImageFont.truetype(os.path.join(FONTS_DIR, file), size)

    # 2. Linux System Fonts Fallback (Streamlit Cloud Debian Environment)
    system_font_paths = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if "bd" in font_name.lower() or "georgia" in font_name.lower() else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    ]
    for sys_path in system_font_paths:
        if os.path.exists(sys_path):
            return ImageFont.truetype(sys_path, size)

    # 3. Last-resort default PIL font
    return ImageFont.load_default()

def generate_certificate(name: str, plantation_date: str, tree_count: int = 1) -> bytes:
    bg_path = os.path.join(BASE_DIR, "certificate_bg.png")
    green_color = "#0B6E38"
    
    # 1. Load Background Image or Fallback to Blank Canvas
    if os.path.exists(bg_path):
        image = Image.open(bg_path).convert("RGB")
    else:
        image = Image.new("RGB", (1200, 850), "#F7F9F8")

    draw = ImageDraw.Draw(image)
    width, height = image.size

    # 2. Draw Double Green Border
    draw.rectangle([30, 30, width - 30, height - 30], outline=green_color, width=4)
    draw.rectangle([40, 40, width - 40, height - 40], outline=green_color, width=2)

    # 3. Load Fonts safely from the fonts/ folder
    title_font = get_font("ARIALBD.ttf", 38)
    subtitle_font = get_font("ARIAL.ttf", 26)
    name_font = get_font("GEORGIAB.ttf", 44)
    body_font = get_font("ARIAL.ttf", 20)
    bold_body_font = get_font("ARIALBD.ttf", 20)

    # 4. Draw Header Banner & Title
    draw.rectangle([80, 80, width - 80, 150], fill=green_color)
    draw.text((width / 2, 115), "CERTIFICATE OF PARTICIPATION", fill="white", font=title_font, anchor="mm")
    
    # 5. Draw Subtitle
    draw.text((width / 2, 210), "This is to certify that", fill="#333333", font=subtitle_font, anchor="mm")
    
    # 6. Draw Name & Name Underline
    draw.text((width / 2, 290), name.title(), fill="#111111", font=name_font, anchor="mm")
    draw.line([(width / 2 - 250, 325), (width / 2 + 250, 325)], fill=green_color, width=2)
    
    # 7. Draw Complete Body Description
    formatted_date = str(plantation_date)
    msg1 = f"has successfully contributed to the environment by planting {tree_count} tree(s)"
    msg2 = f"on {formatted_date} as part of the Greenificate Tree Plantation Initiative."
    msg3 = "We appreciate your commitment to the planet, and your effort in fostering a"
    msg4 = "greener, healthier future for generations to come."

    draw.text((width / 2, 380), msg1, fill="#444444", font=body_font, anchor="mm")
    draw.text((width / 2, 415), msg2, fill="#444444", font=bold_body_font, anchor="mm")
    draw.text((width / 2, 470), msg3, fill="#555555", font=body_font, anchor="mm")
    draw.text((width / 2, 500), msg4, fill="#555555", font=body_font, anchor="mm")
    
    # 8. Draw Footer Details
    draw.text((120, 680), "Issued by:", fill="#333333", font=bold_body_font)
    draw.text((120, 715), "Greenificate Tree Plantation Initiative", fill=green_color, font=bold_body_font)
    draw.text((120, 745), "District Administration Jammu", fill="#666666", font=body_font)

    # 9. Output to Bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()