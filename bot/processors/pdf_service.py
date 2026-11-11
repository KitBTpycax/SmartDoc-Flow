import io
import pymupdf as fitz
from pypdf import PdfReader
import pytesseract
from PIL import Image
from config import TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def extract_text_from_pdf(pdf_path: str) -> str:
    # 1. Спроба текстової екстракції через pypdf
    extracted_text = []
    try:
        reader = PdfReader(pdf_path)
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                extracted_text.append(f"--- Сторінка {idx} ---\n{text.strip()}")
    except Exception:
        pass

    full_text = "\n\n".join(extracted_text)

    # 2. Якщо текст розпізнано і його довжина достатня — повертаємо результат
    if len(full_text.strip()) >= 50:
        return full_text

    # 3. Fallback: Якщо це скан-PDF (тексту немає або мало), проганяємо сторінки через OCR
    ocr_text = []
    with fitz.open(pdf_path) as doc:
        for idx, page in enumerate(doc, start=1):
            pix = page.get_pixmap(dpi=150)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            
            # Обробка Tesseract
            page_text = pytesseract.image_to_string(img, lang="ukr+eng").strip()
            if page_text:
                ocr_text.append(f"--- Сторінка {idx} ---\n{page_text}")
    
    return "\n\n".join(ocr_text) if ocr_text else "Не вдалося витягти текст із PDF-документа."
