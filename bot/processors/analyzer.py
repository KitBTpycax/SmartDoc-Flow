import re
from google import genai
from config import GEMINI_API_KEY

# Єдиний екземпляр клієнта
client = genai.Client(api_key=GEMINI_API_KEY.strip(" '\"\t\r\n")) if GEMINI_API_KEY else None

def search_in_text(text: str, query: str) -> list[str]:
    results = []
    # Якщо у тексті немає маркерів сторінок, загортаємо все як Сторінку 1
    if "--- Сторінка " not in text:
        text = f"--- Сторінка 1 ---\n{text}"

    pages = text.split("--- Сторінка ")
    for page_block in pages:
        if not page_block.strip():
            continue
        lines = page_block.split("\n")
        page_num = lines[0].split(" ---")[0]
        page_text = "\n".join(lines[1:])
        
        if re.search(re.escape(query), page_text, re.IGNORECASE):
            matches = [line.strip() for line in page_text.split("\n") if query.lower() in line.lower()]
            results.append(f"📌 Сторінка {page_num}:\n" + "\n".join(matches[:3]))
    return results

def summarize_text_sync(text: str) -> str:
    if not client:
        return "Помилка: Не вказано GEMINI_API_KEY у файлі .env"
    
    # Сповіщення про скорочення занадто великого тексту
    warning_prefix = ""
    max_chars = 8000
    if len(text) > max_chars:
        warning_prefix = "⚠️ Текст занадто великий, для аналізу взято перші 8000 символів.\n\n"
        text = text[:max_chars]
        
    prompt = f"Зроби стислий конспект (TL;DR) наступного тексту українською мовою з виділенням головних тез:\n\n{text}"
    
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        return warning_prefix + (response.text or "Не вдалося згенерувати конспект.")
    except Exception as e:
        return f"Помилка при виклику Gemini API: {e}"