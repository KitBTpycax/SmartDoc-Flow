import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_formatted_docx(text: str, output_path: str) -> str:
    doc = Document()
    
    # Налаштування полів сторінки
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.6)

    lines = text.split("\n")
    for line in lines:
        line_str = line.strip()
        
        # Пропускаємо технічні маркери сторінок та порожні рядки
        if not line_str or line_str.startswith("--- Сторінка"):
            continue

        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(4)

        # Перевірка на заголовок (Тема, нумерований пункт або заголовок)
        if re.match(r'^(Тема|\d+\.|\#+)', line_str, re.IGNORECASE):
            clean_title = re.sub(r'^\#+\s*', '', line_str)
            run = p.add_run(clean_title)
            run.font.name = "Arial"
            run.font.size = Pt(13)
            run.bold = True
            run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)  # Темно-синій колір
            p.paragraph_format.space_before = Pt(8)
        else:
            run = p.add_run(line_str)
            run.font.name = "Calibri"
            run.font.size = Pt(11)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.save(output_path)
    return output_path