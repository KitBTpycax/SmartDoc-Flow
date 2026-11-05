from pypdf import PdfReader, PdfWriter

def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = []
    for idx, page in enumerate(reader.pages, start=1):
        content = page.extract_text() or ""
        text.append(f"--- Сторінка {idx} ---\n{content}")
    return "\n\n".join(text)

def merge_pdfs(pdf_paths: list[str], output_path: str) -> str:
    writer = PdfWriter()
    for path in pdf_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
    return output_path

def split_pdf(pdf_path: str, start_page: int, end_page: int, output_path: str) -> str:
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for idx in range(start_page - 1, min(end_page, len(reader.pages))):
        writer.add_page(reader.pages[idx])
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
    return output_path