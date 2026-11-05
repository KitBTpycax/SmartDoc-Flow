import re
from google import genai
from config import GEMINI_API_KEY

def search_in_text(text: str, query: str) -> list[str]:
    results = []
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
    if not GEMINI_API_KEY:
        return "Помилка: Не вказано GEMINI_API_KEY у файлі .env"
    
    clean_key = GEMINI_API_KEY.strip(" '\"\t\r\n")
    client = genai.Client(api_key=clean_key)
    clean_text = text.encode("utf-8", errors="ignore").decode("utf-8")
    prompt = f"Зроби стислий конспект (TL;DR) наступного тексту українською мовою з виділенням головних тез:\n\n{clean_text[:8000]}"
    
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Помилка при виклику Gemini API: {e}"