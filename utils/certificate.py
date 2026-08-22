import os
import io
from PIL import Image, ImageOps
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

REG_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansDevanagari-Regular.ttf")
BOLD_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansDevanagari-Bold.ttf")

if not os.path.exists(REG_FONT_PATH):
    REG_FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"

if not os.path.exists(BOLD_FONT_PATH):
    BOLD_FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
    if not os.path.exists(BOLD_FONT_PATH):
        BOLD_FONT_PATH = REG_FONT_PATH


class CertificatePDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("NotoHindi", style="", size=9)
        self.set_text_color(68, 68, 68)

def generate_paalna_certificate(
    student_name: str, student_class: str, school_name: str, 
    tree_name: str, species: str, planted_on: str, 
    height_cm: str, location: str, teacher_name: str, holiday_guardian: str,
    submission_id: int = 1, photo_bytes: bytes = None
) -> bytes:
    
    pdf = CertificatePDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.add_font("NotoHindi", style="", fname=REG_FONT_PATH)
    pdf.add_font("NotoHindi", style="B", fname=BOLD_FONT_PATH)
    pdf.add_font("NotoHindi", style="I", fname=REG_FONT_PATH)
    pdf.add_font("NotoHindi", style="BI", fname=BOLD_FONT_PATH)
    
    pdf.set_font("NotoHindi", style="", size=10)
    pdf.set_text_shaping(True)

    # 1. Outer Double Green Border
    pdf.set_draw_color(11, 110, 56) # #0B6E38
    pdf.set_line_width(1)
    pdf.rect(7, 7, 196, 283)
    pdf.set_line_width(0.3)
    pdf.rect(9, 9, 192, 279)

    # 2. Header Section
    pdf.set_text_color(11, 110, 56)
    pdf.set_font("NotoHindi", style="B", size=16)
    pdf.cell(0, 7, "जिला प्रशासन जम्मू / DISTRICT ADMINISTRATION JAMMU", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "पालना / PAALNA", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_text_color(217, 83, 79)
    pdf.set_font("NotoHindi", style="B", size=14)
    pdf.cell(0, 6, "पेड़ लगाओ नहीं – पेड़ पालो।", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 6, "DON'T PLANT A TREE. RAISE ONE.", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(2)
    pdf.set_text_color(11, 110, 56)
    pdf.set_font("NotoHindi", style="B", size=12)
    pdf.cell(0, 6, "वृक्ष गोद-ग्रहण प्रमाण-पत्र / CERTIFICATE OF TREE ADOPTION", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Sequential Serial Number (e.g. PAALNA/2026/00001)
    formatted_id = f"{submission_id:05d}"
    serial_no = f"PAALNA/2026/{formatted_id}"
    pdf.set_font("NotoHindi", style="", size=9)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 5, f"क्रमांक / NO. {serial_no}", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # 3. Adopter Certification Clause
    cert_text = (
        f"प्रमाणित किया जाता है कि {student_name.title()} (कक्षा: {student_class}), "
        f"{school_name} ने नीचे दर्ज वृक्ष को गोद लिया है। आज से इसकी देखभाल की ज़िम्मेदारी इनकी है।\n"
        f"This certifies that the student named above has adopted the tree recorded below. From today, its care is in their hands."
    )
    pdf.set_font("NotoHindi", style="", size=10)
    pdf.multi_cell(0, 6.5, cert_text, align="L")
    pdf.ln(3)

    # 4. Metadata Grid (Table)
    tree_id = f"TREE-{formatted_id}"
    grid_data = [
        ["वृक्ष का नाम / Tree's Name", tree_name, "वृक्ष क्रमांक / Tree ID", tree_id],
        ["प्रजाति / Species", species, "रोपण तिथि / Planted On", planted_on],
        ["ऊँचाई सें.मी. / Height (cms.)", f"{height_cm} cm", "स्थान / Location", location]
    ]
    
    with pdf.table(col_widths=(50, 50, 50, 50), line_height=6.5, text_align="LEFT") as table:
        for row in grid_data:
            r = table.row()
            for cell in row:
                r.cell(cell)

    pdf.ln(3)

    # 5. The Pledge Block
    pledge_text = (
        "शपथ / THE PLEDGE\n"
        "यह पेड़ मेरा है। मैं इसे रोज़ देखने जाऊँगा/जाऊँगी, पानी दूंगा/दूँगी, और इसे बड़ा होते हुए देखूँगा / देखूँगा। "
        "जब तक मैं इस विद्यालय में हूँ, यह पेड़ अकेला नहीं रहेगा।\n"
        "This tree is mine. I will visit it, water it, and watch it grow. For as long as I am at this school, this tree will not stand alone."
    )
    pdf.set_fill_color(253, 251, 247)
    pdf.multi_cell(0, 5.5, pledge_text, border=1, fill=True, align="L")
    pdf.ln(3)

    # 6. Expanded 12-Month Growth Record Table with Full-Height Centered Image
    pdf.set_font("NotoHindi", style="B", size=10)
    pdf.set_text_color(11, 110, 56)
    pdf.cell(0, 5, "बारह-महीनों की बही / 12-MONTH GROWTH RECORD", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("NotoHindi", style="", size=8)
    pdf.set_text_color(88, 88, 88)
    pdf.cell(0, 4, "FILLED IN BY THE ADOPTER, ONCE A MONTH", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Save starting Y position for the grid
    start_y = pdf.get_y()
    
    # Expanded Row Height Parameters
    header_h = 8.0
    row_h = 10.0  # Increased for ample space to write height details
    img_box_h = header_h + (6 * row_h)  # Total table height = 68mm
    
    # Left Side: X = 10 to 78 (Width: 68mm)
    # Center Image Box: X = 78 to 132 (Width: 54mm)
    # Right Side: X = 132 to 200 (Width: 68mm)
    img_box_x = 78
    img_box_w = 54
    
    # Draw Table Headers
    pdf.set_font("NotoHindi", style="B", size=6.5)
    pdf.set_text_color(0, 0, 0)
    
    # Left Column Headers (Months 1-6)
    pdf.set_xy(10, start_y)
    pdf.cell(14, header_h, "Month", border=1, align="C")
    pdf.cell(15, header_h, "Height (cm)", border=1, align="C")
    pdf.cell(15, header_h, "Alive (Y/N)", border=1, align="C")
    pdf.cell(24, header_h, "Guardian's Sign", border=1, align="C")

    # Right Column Headers (Months 7-12)
    pdf.set_xy(132, start_y)
    pdf.cell(14, header_h, "Month", border=1, align="C")
    pdf.cell(15, header_h, "Height (cm)", border=1, align="C")
    pdf.cell(15, header_h, "Alive (Y/N)", border=1, align="C")
    pdf.cell(24, header_h, "Guardian's Sign", border=1, align="C")

    # Draw 6 Rows (Left: M1-M6 | Right: M7-M12)
    pdf.set_font("NotoHindi", style="", size=8)
    for i in range(6):
        curr_y = start_y + header_h + (i * row_h)
        
        # Left Side: Month i+1
        pdf.set_xy(10, curr_y)
        pdf.cell(14, row_h, f"M-{i+1}", border=1, align="C")
        pdf.cell(15, row_h, "", border=1)
        pdf.cell(15, row_h, "", border=1)
        pdf.cell(24, row_h, "", border=1)

        # Right Side: Month i+7
        pdf.set_xy(132, curr_y)
        pdf.cell(14, row_h, f"M-{i+7}", border=1, align="C")
        pdf.cell(15, row_h, "", border=1)
        pdf.cell(15, row_h, "", border=1)
        pdf.cell(24, row_h, "", border=1)

    # Process & Crop Image to span full width and height of middle table space
    if photo_bytes:
        try:
            im = Image.open(io.BytesIO(photo_bytes))
            # Crop image dynamically to match exact aspect ratio of middle column (54 x 68)
            target_pixel_w = 540
            target_pixel_h = int(540 * (img_box_h / img_box_w))
            im_cropped = ImageOps.fit(im, (target_pixel_w, target_pixel_h), centering=(0.5, 0.5))
            
            img_buf = io.BytesIO()
            im_cropped.save(img_buf, format="JPEG", quality=85)
            img_buf.seek(0)

            # Draw image spanning whole width and height of the middle section
            pdf.image(img_buf, x=img_box_x, y=start_y, w=img_box_w, h=img_box_h)
        except Exception:
            pass

    # Draw outer green border box around middle image area
    pdf.set_draw_color(11, 110, 56)
    pdf.rect(img_box_x, start_y, img_box_w, img_box_h)

    # Move cursor below the growth grid table
    pdf.set_xy(10, start_y + img_box_h + 4)

    pdf.set_font("NotoHindi", style="B", size=9.5)
    
    # 7. Signatures Block
    sig_data = [
        ["\n\n"],
        [f"{student_name.title()}\nगोद लेने वाला विद्यार्थी, Adopter student", 
         f"{teacher_name.title()}\nसह-संरक्षक शिक्षक, Co-guardian teacher", 
         f"{holiday_guardian.title()}\nअवकाश संरक्षक, Holiday guardian"],
        ["\n\n\n"],
    ]

    with pdf.table(col_widths=(63, 64, 63), line_height=4, text_align="CENTER", borders_layout="NONE") as table:
        for row in sig_data:
            r = table.row()
            for cell in row:
                r.cell(cell)

    pdf.set_font("NotoHindi", style="B", size=10)

    sig_data = [
        ["अनुराग आर्य, आई.एफ.एस. / Anurag Arya, IFS\nमंडलीय वन अधिकारी / Divisional Forest Officer", 
         "डॉ. राकेश मिन्हास, आई.ए.एस / Dr. Rakesh Minhas, IAS\nउपायुक्त, जम्मू / Deputy Commissioner, Jammu"]
    ]
    with pdf.table(col_widths=(95, 95), line_height=4, text_align="CENTER", borders_layout="NONE") as table:
        for row in sig_data:
            r = table.row()
            for cell in row:
                r.cell(cell)

    # 8. Bottom Tagline
    pdf.set_auto_page_break(auto=False)
    pdf.set_y(278)
    pdf.set_font("NotoHindi", style="B", size=11)
    pdf.set_text_color(11, 110, 56)
    pdf.cell(0, 5, "हर पेड़ का एक नाम, हर नाम का एक ज़िम्मेदार", align="C")

    return bytes(pdf.output())