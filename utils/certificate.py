import io
import datetime
from PIL import Image, ImageDraw, ImageFont

def generate_certificate(name: str, plantation_date: str, tree_count: int = 1) -> bytes:
    # Set landscape dimensions (Width x Height)
    width, height = 1200, 850
    
    # Base background (Light off-white)
    image = Image.new("RGB", (width, height), "#F7F9F8")
    draw = ImageDraw.Draw(image)
    
    # Draw double green border
    green_color = "#0B6E38"
    draw.rectangle([30, 30, width - 30, height - 30], outline=green_color, width=4)
    draw.rectangle([40, 40, width - 40, height - 40], outline=green_color, width=2)
    
    # Header Banner
    draw.rectangle([80, 80, width - 80, 150], fill=green_color)
    
    # Fonts loading (Fallback to default if custom fonts are missing)
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 38)
        subtitle_font = ImageFont.truetype("arial.ttf", 26)
        name_font = ImageFont.truetype("georgiab.ttf", 44)
        body_font = ImageFont.truetype("arial.ttf", 20)
        bold_body_font = ImageFont.truetype("arialbd.ttf", 20)
    except IOError:
        title_font = subtitle_font = name_font = body_font = bold_body_font = ImageFont.load_default()

    # Title Text inside green banner
    draw.text((width / 2, 115), "CERTIFICATE OF PARTICIPATION", fill="white", font=title_font, anchor="mm")
    
    # Subtitle
    draw.text((width / 2, 210), "This is to certify that", fill="#333333", font=subtitle_font, anchor="mm")
    
    # Name
    draw.text((width / 2, 290), name.title(), fill="#111111", font=name_font, anchor="mm")
    
    # Name Underline
    draw.line([(width / 2 - 250, 325), (width / 2 + 250, 325)], fill=green_color, width=2)
    
    # Body Description
    formatted_date = str(plantation_date)
    msg1 = f"has successfully contributed to the environment by planting {tree_count} tree(s)"
    msg2 = f"on {formatted_date} as part of the Greenificate Tree Plantation Initiative."
    msg3 = "We appreciate your commitment to the planet, and your effort in fostering a"
    msg4 = "greener, healthier future for generations to come."

    draw.text((width / 2, 380), msg1, fill="#444444", font=body_font, anchor="mm")
    draw.text((width / 2, 415), msg2, fill="#444444", font=bold_body_font, anchor="mm")
    draw.text((width / 2, 470), msg3, fill="#555555", font=body_font, anchor="mm")
    draw.text((width / 2, 500), msg4, fill="#555555", font=body_font, anchor="mm")
    
    # Footer - Issued By
    draw.text((120, 680), "Issued by:", fill="#333333", font=bold_body_font)
    draw.text((120, 715), "Greenificate Tree Plantation Initiative", fill=green_color, font=bold_body_font)
    draw.text((120, 745), "District Administration Jammu", fill="#666666", font=body_font)
    
    # Output to Byte Stream
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()