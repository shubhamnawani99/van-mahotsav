import os
import random
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

REG_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansDevanagari-Regular.ttf")
BOLD_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansDevanagari-Bold.ttf")

# System fallbacks if local fonts directory is missing fonts
if not os.path.exists(REG_FONT_PATH):
    REG_FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"

if not os.path.exists(BOLD_FONT_PATH):
    BOLD_FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
    if not os.path.exists(BOLD_FONT_PATH):
        BOLD_FONT_PATH = REG_FONT_PATH  # Fallback to regular if bold doesn't exist


class CertificatePDF(FPDF):
    def footer(self):
        self.set_y(-20)
        self.set_font("NotoHindi", style="", size=9)
        self.set_text_color(68, 68, 68)
        self.cell(0, 10, "paalna.jammu.nic.in", align="L")
        self.cell(0, 10, f"Page {self.page_no()}", align="R")


def generate_paalna_certificate(
    student_name: str, student_class: str, school_name: str, 
    tree_name: str, species: str, planted_on: str, 
    height_cm: str, location: str, teacher_name: str, holiday_guardian: str
) -> bytes:
    
    pdf = CertificatePDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Register Noto Sans Devanagari Regular and Bold fonts
    pdf.add_font("NotoHindi", style="", fname=REG_FONT_PATH)
    pdf.add_font("NotoHindi", style="B", fname=BOLD_FONT_PATH)
    pdf.add_font("NotoHindi", style="I", fname=REG_FONT_PATH)
    pdf.add_font("NotoHindi", style="BI", fname=BOLD_FONT_PATH)
    
    pdf.set_font("NotoHindi", style="", size=10)
    
    # Enable HarfBuzz Devanagari Shaping natively inside FPDF2
    # Fixes 'कि', half-letters, and halants
    pdf.set_text_shaping(True)

    # 1. Outer Double Green Border
    pdf.set_draw_color(11, 110, 56) # #0B6E38
    pdf.set_line_width(1)
    pdf.rect(7, 7, 196, 283)
    pdf.set_line_width(0.3)
    pdf.rect(9, 9, 192, 279)

    # 2. Header Section
    pdf.set_text_color(11, 110, 56)
    pdf.set_font("NotoHindi", style="B", size=14)
    pdf.cell(0, 7, "जिला प्रशासन जम्मू / DISTRICT ADMINISTRATION JAMMU", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "पालना / PAALNA", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_text_color(217, 83, 79) # Crimson Motto
    pdf.set_font("NotoHindi", style="B", size=11)
    pdf.cell(0, 6, "पेड़ लगाओ नहीं – पेड़ पालो।", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 6, "DON'T PLANT A TREE. RAISE ONE.", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(3)
    pdf.set_text_color(11, 110, 56)
    pdf.set_font("NotoHindi", style="B", size=12)
    pdf.cell(0, 6, "वृक्ष गोद-ग्रहण प्रमाण-पत्र / CERTIFICATE OF TREE ADOPTION", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Serial Number
    serial_no = f"PAALNA/2026/{random.randint(1000, 9999)}"
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
    pdf.multi_cell(0, 5, cert_text, align="L")
    pdf.ln(4)

    # 4. Metadata Grid (Table)
    tree_id = f"TREE-{random.randint(10000, 99999)}"
    grid_data = [
        ["वृक्ष का नाम / Tree's Name", tree_name, "वृक्ष क्रमांक / Tree ID", tree_id],
        ["प्रजाति / Species", species, "रोपण तिथि / Planted On", planted_on],
        ["ऊँचाई सें.मी. / Height (cms.)", f"{height_cm} cm", "स्थान / Location", location]
    ]
    
    with pdf.table(col_widths=(50, 50, 50, 50), line_height=6, text_align="LEFT") as table:
        for row in grid_data:
            r = table.row()
            for cell in row:
                r.cell(cell)

    pdf.ln(4)

    # 5. The Pledge Block
    pledge_text = (
        "शपथ / THE PLEDGE\n"
        "यह पेड़ मेरा है। मैं इसे रोज़ देखने जाऊँगा/जाऊँगी, पानी दूंगा/दूँगी, और इसे बड़ा होते हुए देखूँगा / देखूँगा। "
        "जब तक मैं इस विद्यालय में हूँ, यह पेड़ अकेला नहीं रहेगा।\n"
        "This tree is mine. I will visit it, water it, and watch it grow. For as long as I am at this school, this tree will not stand alone."
    )
    pdf.set_fill_color(253, 251, 247)
    pdf.multi_cell(0, 5, pledge_text, border=1, fill=True, align="L")
    pdf.ln(4)

    # 6. 12-Month Growth Record Table
    pdf.set_font("NotoHindi", style="B", size=10)
    pdf.set_text_color(11, 110, 56)
    pdf.cell(0, 5, "बारह-महीनों की बही / 12-MONTH GROWTH RECORD", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("NotoHindi", style="", size=8)
    pdf.set_text_color(88, 88, 88)
    pdf.cell(0, 4, "FILLED IN BY THE ADOPTER, ONCE A MONTH", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("NotoHindi", style="", size=9)
    pdf.set_text_color(0, 0, 0)
    with pdf.table(col_widths=(35, 40, 35, 80), line_height=5, text_align="CENTER") as table:
        header = table.row()
        header.cell("माह / MONTH")
        header.cell("ऊँचाई सें.मी. / HEIGHT CM")
        header.cell("जीवित ? / ALIVE?")
        header.cell("संरक्षक के हस्ताक्षर / GUARDIAN'S SIGNATURE")
        
        for i in range(12):
            r = table.row()
            r.cell(f"Month {i+1}")
            r.cell("")
            r.cell("")
            r.cell("")

    pdf.ln(6)

    # 7. Signatures Block
    sig_data = [
        [f"गोद लेने वाला विद्यार्थी\nAdopter student\n{student_name.title()}", 
         f"सह-संरक्षक शिक्षक\nCo-guardian teacher\n{teacher_name.title()}", 
         f"अवकाश संरक्षक\nHoliday guardian\n{holiday_guardian.title()}"],
        ["\nप्रधानाचार्य\n\nHead of School", "", "\nउपायुक्त, जम्मू\n\nDeputy Commissioner, Jammu"]
    ]
    
    with pdf.table(col_widths=(63, 64, 63), line_height=5, text_align="CENTER", borders_layout="NONE") as table:
        for row in sig_data:
            r = table.row()
            for cell in row:
                r.cell(cell)

    pdf.ln(4)
    pdf.set_font("NotoHindi", style="B", size=10)
    pdf.set_text_color(11, 110, 56)
    pdf.cell(0, 5, "हर पेड़ का एक नाम, हर नाम का एक ज़िम्मेदार", align="C")

    return bytes(pdf.output())