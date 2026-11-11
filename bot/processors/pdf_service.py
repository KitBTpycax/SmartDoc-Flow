import io
import pymupdf as fitz
import pytesseract
from PIL import Image
from config import TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Посторінковий аналіз PDF-документа:
    1. Для кожної сторінки спочатку перевіряється наявність вбудованого тексту.
    2. Якщо сторінка не містить тексту (або менше 20 символів) —
       ТІЛЬКИ ця сторінка рендериться з DPI=300 та передається в Tesseract OCR.
    3. Результати текстових і відсканованих сторінок об'єднуються зі збереженням структури сторінок.
    """
    result_pages = []

    with fitz.open(pdf_path) as doc:
        if doc.is_encrypted:
            raise RuntimeError("PDF-документ захищено паролем.")

        total_pages = len(doc)
        if total_pages == 0:
            raise RuntimeError("PDF-документ порожній і не містить сторінок.")

        for idx, page in enumerate(doc, start=1):
            page_text = (page.get_text() or "").strip()

            # Якщо сторінка містить достатньо тексту — використовуємо його без виклику OCR
            if len(page_text) >= 20:
                result_pages.append(f"--- Сторінка {idx} ---\n{page_text}")
                continue

            # Якщо сторінка не містить тексту (сканована) — виконуємо OCR ТІЛЬКИ для цієї сторінки
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            ocr_text = pytesseract.image_to_string(img, lang="ukr+eng", config="--dpi 300").strip()
            final_text = ocr_text if ocr_text else page_text

            if final_text:
                result_pages.append(f"--- Сторінка {idx} ---\n{final_text}")

    if not result_pages:
        raise RuntimeError("Не вдалося витягти або розпізнати текст із PDF-документа.")

    return "\n\n".join(result_pages)
