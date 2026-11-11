import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from config import TESSERACT_CMD

# Вказуємо шлях до встановленого Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def preprocess_image(image_path: str) -> Image.Image:
    img = Image.open(image_path).convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(2.0)

def perform_ocr(image_path: str, lang: str = "ukr+eng") -> str:
    processed_img = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_img, lang=lang, config="--dpi 300")
    text_clean = text.strip()
    if not text_clean:
        raise RuntimeError("Текст на зображенні не знайдено.")
    return f"--- Сторінка 1 ---\n{text_clean}"

def images_to_pdf(image_paths: list[str], output_pdf_path: str) -> str:
    images = [Image.open(p).convert("RGB") for p in image_paths]
    if images:
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:], resolution=300.0)
    return output_pdf_path
