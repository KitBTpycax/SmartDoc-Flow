import pytesseract

# Вказуємо шлях до встановленого Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from PIL import Image, ImageEnhance, ImageFilter

def preprocess_image(image_path: str) -> Image.Image:
    img = Image.open(image_path).convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(2.0)

def perform_ocr(image_path: str, lang: str = "ukr+eng") -> str:
    processed_img = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_img, lang=lang)
    return text.strip()

def images_to_pdf(image_paths: list[str], output_pdf_path: str) -> str:
    images = [Image.open(p).convert("RGB") for p in image_paths]
    if images:
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
    return output_pdf_path